# Part 4　优化、动态系统与最优决策

## 4.1 机器人问题几乎都可以写成优化

\[
\min_x f(x)
\quad\text{s.t.}\quad h(x)=0,\ g(x)\le0.
\]

\(x\) 可以是 joint configuration、trajectory、controller gain、network parameter、甚至 morphology。

关键不是“会调用 optimizer”，而是知道 objective 与 constraint 分别编码什么物理意义。

## 4.2 Lagrangian

等式约束：

\[
\mathcal L(x,\lambda)=f(x)+\lambda^Th(x).
\]

一阶必要条件把 constrained optimum 转成 stationarity。Lagrange multiplier 还可解释成约束影子价格/constraint force。

## 4.3 KKT

不等式约束引入 \(\mu\ge0\)：

- stationarity；
- primal feasibility；
- dual feasibility；
- complementary slackness：\(\mu_i g_i(x)=0\)。

Contact、whole-body QP、MPC 都会遇到这套结构。

## 4.4 Convexity

若 \(f\) convex、feasible set convex，任何 local optimum 都是 global optimum。机器人碰撞、rotations、contact、neural network 多数非凸，因此常见策略是：

- convex relaxation；
- sequential convex optimization；
- local linearization；
- multi-start / sampling。

## 4.5 Gradient Descent

\[
\theta_{k+1}=\theta_k-\eta\nabla L(\theta_k).
\]

Learning rate 决定离散 optimization dynamics。过大震荡，过小慢。Momentum/Adam 改善 conditioning，但不能修复错误 objective 或数据。

## 4.6 Dynamic System

\[
\dot x=f(x,u),\qquad y=h(x).
\]

State 的定义要求：给定当前 \(x\) 和未来输入，就足以预测未来。机器人学中的“状态”和神经网络任意 feature 不能随意等同。

## 4.7 Equilibrium 与 Linearization

平衡点 \(x^*\)：

\[
f(x^*,u^*)=0.
\]

在附近：

\[
\delta\dot x=A\delta x+B\delta u,
\quad A=\frac{\partial f}{\partial x}.
\]

线性控制理论因此可以局部应用于非线性机器人。

## 4.8 Lyapunov Stability

若存在 \(V(x)>0\)、\(\dot V(x)<0\)，可证明平衡点稳定/渐近稳定。

Lyapunov 的价值是提供**轨迹级保证**，不同于经验 rollout 成功率。

## 4.9 Optimal Control

\[
\min_{u_{0:T-1}}\sum_{t=0}^{T-1}\ell(x_t,u_t)+\ell_T(x_T)
\]

subject to

\[
x_{t+1}=f(x_t,u_t).
\]

这里明确把 dynamics 作为 constraint。Trajectory optimization、LQR、MPC、RL 都可以放到这个统一框架中理解。

## 4.10 Dynamic Programming

Bellman principle：一个最优轨迹的后半段，从其中任一 state 开始仍应是该剩余问题的最优轨迹。

\[
V_t(s)=\min_a\left[c(s,a)+\mathbb E V_{t+1}(s')\right].
\]

这正是 RL value function 的祖先。

## 4.11 LQR

线性 dynamics + quadratic cost：

\[
x_{t+1}=Ax_t+Bu_t,
\]

\[
J=\sum x_t^TQx_t+u_t^TRu_t.
\]

Riccati recursion 给出最优线性反馈 \(u=-Kx\)。它展示了 model + future cost 如何自动形成 feedback gain。

## 4.12 iLQR / DDP

在 nominal trajectory 周围对 dynamics 线性化、cost 二次化，反向计算局部 value，再前向 rollout 更新轨迹。它们连接 nonlinear control、trajectory optimization 与 local feedback。

## 4.13 MPC

每个时刻重新解有限时域最优控制，只执行第一段：

```text
estimate state
→ optimize future
→ execute first control
→ observe again
→ repeat
```

现代 action-chunk policy 的 receding-horizon execution 与 MPC 在系统思想上相通。

## 4.14 Pontryagin Minimum Principle

Hamiltonian：

\[
\mathcal H=\ell(x,u)+\lambda^Tf(x,u).
\]

最优轨迹满足 state equation、costate equation 与 Hamiltonian 对 control 的最优条件。即使工程中使用数值 solver，PMP 提供连续最优控制的重要理论骨架。

## 4.15 Optimal Transport / Flow

Flow matching 学习

\[
\frac{dx}{dt}=v_\theta(x,t,c)
\]

将简单 base distribution 搬运到复杂 target distribution。现代 VLA 用它生成连续 action chunk，本质上把“动作生成”写成概率流 ODE。

## 最小实验

用 double integrator \(x=[p,v]\) 比较：手工 PD、LQR、MPC。加入 control bound 与 obstacle 后观察：为什么 LQR 解析最优性失效，而 constrained MPC 仍能显式处理约束。
<!-- CHAPTER-ENRICHMENT-P04:START -->
## 4.16 Model Mismatch：最优解只对所写问题最优

优化器返回的 \(x^*\) 只对**当前 objective、constraint 与 dynamics model**有意义：

\[
x^*=\arg\min_x f_{\hat\theta}(x)\quad\text{s.t.}\quad g_{\hat\theta}(x)\le0.
\]

如果真实系统参数是 \(\theta\neq\hat\theta\)，则 solver 数值收敛并不保证真实闭环最优。机器人里最典型的是：friction、payload、delay、contact mode 或 actuator saturation 被错误建模。

因此必须把两种误差分开：

```text
optimization error: 没有把已定义的问题解好
modeling error:      把错误的问题解得非常好
```

## 4.17 常见失败

### Objective hacking

一个 reward/cost 可以被 policy 以设计者没预期的方式满足。仿真 reward 上升不代表真实任务语义改善。

### Constraint 只在 nominal trajectory 成立

trajectory optimizer 在预测模型中满足 collision/force bound，但 tracking error 与 model mismatch 会让真实轨迹越界。需要 margin、robust constraint 或 feedback correction。

### Open-loop optimality 冒充 feedback robustness

一次求出的长 horizon trajectory 可能在 nominal model 上最优，但 disturbance 后没有 recovery。必须比较 open-loop plan 与 receding-horizon / feedback execution。

### 非凸 solver 的“成功”依赖 initialization

同一 target 不同 initial guess 得到不同 local optimum。只汇报最好结果会隐藏 basin-of-attraction 问题。

### Learned optimizer 改变了问题而不自知

神经网络可能 amortize 求解，但如果训练数据隐式改变 constraint distribution，不能只比较 wall-clock time 就宣称“替代了优化”。

## 4.18 研究问题

1. Learned policy、MPC 与 trajectory optimization 在相同 model/data/compute budget 下，性能差异究竟来自哪里？
2. Foundation policy 的 action expert 是否可以解释为 amortized optimizer；若可以，它隐式优化的 objective 是什么？
3. 对 contact-rich manipulation，robust MPC、online system identification 与 experience-based policy adaptation 应怎样分工？
4. 如何设计 benchmark，把 optimizer failure、model mismatch 与 controller tracking failure 分开记录？
5. Flow-matching action generator 的 ODE integration error 在什么条件下会真正影响 physical control，而不是仅影响离线 likelihood？
<!-- CHAPTER-ENRICHMENT-P04:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 04`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-04)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
