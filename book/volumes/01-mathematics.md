# Volume I　数学与计算语言

> 本卷不是“高数复习”。目标是建立后续机器人学、控制、概率估计、强化学习、生成式策略和 world model 共用的数学语言。每个对象都回答：它在机器人系统里代表什么？

---

# Part 2　线性代数、微积分与数值计算

## 2.1 向量、矩阵与张量：先看 shape

机器人程序里最常见的错误不是公式错，而是对象语义错。约定：

- 关节位置：\(q\in\mathbb R^n\)；
- 末端位置：\(p\in\mathbb R^3\)；
- RGB 图像：\(I\in\mathbb R^{H\times W\times 3}\)；
- 点云：\(P\in\mathbb R^{N\times 3}\)；
- 一个 batch 的 action chunk：\(A\in\mathbb R^{B\times H_a\times d_a}\)。

学习任何公式前先写出 shape，是本书的硬规则。

矩阵 \(A\in\mathbb R^{m\times n}\) 最重要的理解是“线性映射”而不只是二维数字表：

\[
y=Ax,\qquad x\in\mathbb R^n,\ y\in\mathbb R^m.
\]

坐标系变化、Jacobian、camera projection、attention projection 都是线性映射与非线性组合。

## 2.2 基、坐标与 Change of Basis

几何向量本身与坐标表示不同。若 \(v\) 是同一物理向量，在两个基下有坐标 \([v]_A,[v]_B\)，则

\[
[v]_B=P_{BA}[v]_A.
\]

机器人学里“world frame 下的速度”和“body frame 下的速度”就是这种区别。混淆物理量与坐标表达会产生极难发现的 bug。

## 2.3 Rank、Null Space 与冗余

对 \(A\in\mathbb R^{m\times n}\)：

- \(\mathrm{rank}(A)\) 表示可独立产生多少输出方向；
- \(\ker(A)=\{x:Ax=0\}\) 是 null space。

若机械臂 Jacobian \(J\in\mathbb R^{6\times n}\)，满足

\[
V=J(q)\dot q,
\]

那么任何 \(\dot q_N\in\ker(J)\) 都不会改变末端瞬时 twist。这就是冗余机器人能“末端不动而内部调姿”的数学基础。

## 2.4 Least Squares、Pseudoinverse 与 SVD

当 \(Ax=b\) 无精确解时，最小二乘寻找

\[
x^*=\arg\min_x\|Ax-b\|_2^2.
\]

若条件合适，

\[
x^*=A^+b,
\]

其中 \(A^+\) 是 Moore–Penrose pseudoinverse。SVD

\[
A=U\Sigma V^\top
\]

不仅用于数值求逆，还直接揭示奇异方向。机械臂接近 singularity 时，Jacobian 某个奇异值 \(\sigma_i\to0\)，于是为了产生某个末端速度可能需要极大的关节速度。

Damped Least Squares：

\[
\dot q=J^\top(JJ^\top+\lambda^2I)^{-1}V_d
\]

通过 \(\lambda\) 抑制奇异附近的爆炸。

## 2.5 Eigenvalue 与稳定性

线性离散系统

\[
x_{t+1}=Ax_t
\]

若所有特征值满足 \(|\lambda_i|<1\)，原点渐近稳定。连续系统

\[
\dot x=Ax
\]

则要求特征值实部为负。

这为控制、优化和训练动力学提供统一直觉：特征值描述不同方向上扰动被放大还是衰减。

## 2.6 微分、Gradient、Jacobian、Hessian

标量函数 \(f:\mathbb R^n\to\mathbb R\) 的梯度：

\[
\nabla f=\begin{bmatrix}\partial f/\partial x_1&\cdots&\partial f/\partial x_n\end{bmatrix}^\top.
\]

向量函数 \(f:\mathbb R^n\to\mathbb R^m\) 的 Jacobian：

\[
J_{ij}=\frac{\partial f_i}{\partial x_j}.
\]

Hessian \(H=\nabla^2f\) 则描述局部曲率。机器人运动学中的 Jacobian 与神经网络自动微分里的 Jacobian 是同一种数学对象，只是语义不同。

## 2.7 Chain Rule 与计算图

若 \(y=f(g(x))\)：

\[
\frac{\partial y}{\partial x}
=\frac{\partial y}{\partial g}\frac{\partial g}{\partial x}.
\]

深度学习反向传播就是沿计算图反复使用 chain rule。机器人中 differentiable simulator、differentiable IK、trajectory optimization 也依赖同一机制。

## 2.8 Taylor 展开与局部线性化

在 \(x_0\) 附近：

\[
f(x)\approx f(x_0)+J_f(x_0)(x-x_0).
\]

二阶则加入

\[
\frac12(x-x_0)^\top H(x_0)(x-x_0).
\]

EKF、iLQR、DDP、局部 MPC 都大量使用“先把非线性系统在当前点附近线性化/二次化，再解易处理的问题”。

## 2.9 ODE 与状态演化

连续机器人系统常写成

\[
\dot x(t)=f(x(t),u(t)).
\]

例如 \(x=[q,\dot q]\)。控制器给出 \(u\)，动力学决定状态变化。数值模拟需要积分：

Euler：
\[
x_{k+1}=x_k+\Delta t f(x_k,u_k).
\]

Runge–Kutta 用多个中间斜率提高精度。\(\Delta t\) 不只是“仿真参数”：太大可能让接触、刚性弹簧、高增益控制数值发散。

## 2.10 离散时间与采样

真实控制器按固定或近似固定周期运行：

\[
x_{k+1}=f_d(x_k,u_k).
\]

连续控制律离散部署后稳定性可能改变。一个 1 kHz 设计的 torque controller 与 10 Hz VLA 不能被当成同一个时间尺度。

---

# Part 3　概率、统计、信息与不确定性

## 3.1 为什么机器人必须概率化

传感器有噪声、世界被遮挡、动作执行不精确、对象性质未知。因此同一观测往往对应多个可能世界。

随机变量 \(X\) 的概率分布 \(p(x)\) 表示不确定性；条件分布

\[
p(x\mid y)=\frac{p(y\mid x)p(x)}{p(y)}
\]

则是从证据更新 belief 的核心。

## 3.2 Expectation、Variance、Covariance

\[
\mathbb E[X]=\int xp(x)dx,
\qquad
\mathrm{Var}(X)=\mathbb E[(X-\mu)^2].
\]

多维状态的 covariance

\[
\Sigma=\mathbb E[(x-\mu)(x-\mu)^\top]
\]

不仅表示各维不确定程度，也表示误差方向间相关性。定位系统里“x 和 yaw 联动的不确定性”不能只看逐维方差。

## 3.3 Gaussian 与线性高斯世界

Gaussian

\[
\mathcal N(x;\mu,\Sigma)
\]

之所以在机器人学中常见，是因为线性变换后仍是 Gaussian，且只需均值和协方差。但真实接触、遮挡、数据关联常产生强多模态分布，不能强行用单峰 Gaussian 表示。

## 3.4 MLE 与 MAP

最大似然：

\[
\theta_{MLE}=\arg\max_\theta p(D\mid\theta).
\]

最大后验：

\[
\theta_{MAP}=\arg\max_\theta p(D\mid\theta)p(\theta).
\]

深度网络常见的交叉熵训练可视为特定概率模型下的 MLE；L2 正则可对应 Gaussian prior 的 MAP。

## 3.5 Bayes Filter

belief 更新分预测和校正：

\[
\bar b_t(x_t)=\int p(x_t\mid x_{t-1},u_{t-1})b_{t-1}(x_{t-1})dx_{t-1},
\]

\[
b_t(x_t)\propto p(z_t\mid x_t)\bar b_t(x_t).
\]

这两步几乎是所有状态估计器的共同祖先：动力学先预测，传感器再纠正。

## 3.6 Entropy、KL 与 Mutual Information

熵：

\[
H(X)=-\mathbb E[\log p(X)].
\]

KL divergence：

\[
D_{KL}(p\|q)=\mathbb E_p\left[\log\frac{p}{q}\right].
\]

互信息：

\[
I(X;Y)=H(X)-H(X\mid Y).
\]

主动感知可把候选视角 \(v\) 的价值写成预期信息增益：

\[
v^*=\arg\max_v I(S;O_v)-\lambda C(v).
\]

即“这个动作能减少多少任务相关不确定性，值得付多少运动代价”。

## 3.7 Epistemic 与 Aleatoric

**Aleatoric uncertainty** 来自不可消除的随机性，例如噪声或多种合理动作；**epistemic uncertainty** 来自模型不知道，理论上可通过更多数据降低。

安全机器人更关心后者：在 OOD 场景下模型应该知道自己不知道，从而请求人工、主动观察或进入安全状态。

## 3.8 Calibration

若模型声称 80% 置信的一组事件实际约 80% 成功，我们称其 calibration 良好。单纯高 accuracy 并不保证 uncertainty 可用。真实系统中常要同时测 success、confidence、expected calibration error、risk-coverage curve。

## 3.9 Monte Carlo 与 Sampling

当积分不可解析时，用样本逼近：

\[
\mathbb E[f(X)]\approx \frac1N\sum_{i=1}^N f(x^{(i)}).
\]

Particle filter、trajectory sampling、diffusion sampling、model-based planning 都依赖 sampling 思想。

---

# Part 4　优化、动态系统与最优决策

## 4.1 统一问题形式

大量机器人问题都可写成

\[
\min_x f(x)
\quad\text{s.t.}\quad
h(x)=0,\ g(x)\le0.
\]

其中 \(x\) 可以是关节角、轨迹、控制序列、网络参数甚至机器人形态。

## 4.2 Lagrangian 与 KKT

等式约束：

\[
\mathcal L(x,\lambda)=f(x)+\lambda^\top h(x).
\]

加入不等式后，KKT 给出 stationarity、primal feasibility、dual feasibility、complementary slackness。IK、contact optimization、whole-body QP、MPC 都会遇到这些结构。

## 4.3 Convexity

凸问题的重要性在于局部最优等于全局最优。但机器人几何、碰撞、接触、深度网络几乎都非凸。因此“把问题变凸”或“局部线性化后反复求解”是工程常态。

## 4.4 Gradient Descent 与 Adam

\[
\theta_{k+1}=\theta_k-\eta\nabla_\theta L.
\]

Momentum 为梯度加入历史惯性；Adam 对一阶、二阶矩做自适应归一化。它们是训练工具，不是理论保证。机器人策略训练中，数据相关性、非平稳分布、reward scale 往往比 optimizer 名字更决定结果。

## 4.5 State-Space Dynamic System

\[
\dot x=f(x,u),\qquad y=h(x).
\]

状态 \(x\) 应足以预测未来；观测 \(y\) 是可测量量。这个区分贯穿 Kalman filter、control、MDP、world model。

## 4.6 Stability 与 Lyapunov

若存在函数 \(V(x)>0\)，且沿轨迹

\[
\dot V(x)<0,
\]

则可证明系统向目标收敛。Lyapunov 思想比“reward 变高”更强：它给出动力系统层面的稳定性证据。

## 4.7 Optimal Control

有限时域问题：

\[
\min_{u_{0:T-1}}\sum_{t=0}^{T-1}\ell(x_t,u_t)+\ell_T(x_T)
\]

subject to

\[
x_{t+1}=f(x_t,u_t).
\]

LQR 在 linear dynamics + quadratic cost 下有解析结构；iLQR/DDP 对非线性系统反复局部二次化；MPC 每个时刻重新求有限时域问题，只执行第一段动作，因此天然闭环。

## 4.8 Bellman Principle

定义 value：

\[
V(s)=\min_a\left[c(s,a)+\gamma\mathbb E V(s')\right].
\]

它把长时决策拆成“当前一步 + 剩余最优问题”。强化学习的 Q-learning、actor-critic 与动态规划都源于此。

## 4.9 Pontryagin Minimum Principle

对连续控制，引入 costate \(\lambda\) 和 Hamiltonian：

\[
\mathcal H(x,u,\lambda)=\ell(x,u)+\lambda^\top f(x,u).
\]

最优控制满足状态、costate 和最小化 Hamiltonian 的必要条件。即使实际工程常用数值优化，PMP 提供理解轨迹优化的理论骨架。

## 4.10 Optimal Transport 与 Flow Matching

Optimal Transport 研究如何以最小代价把一个分布搬运到另一个分布。连续流可写为 ODE：

\[
\frac{dx}{dt}=v_\theta(x,t).
\]

Flow matching 直接学习速度场，使简单基分布随时间演化到目标分布。这为现代 VLA 中连续 action expert 提供了重要数学基础：机器人动作 chunk 不必逐 token 生成，而可通过学习的连续流从噪声/基分布变成条件动作轨迹。

---

# Part 5　几何、流形、图与因果

## 5.1 为什么旋转需要流形

三维位置可写 \(p\in\mathbb R^3\)，但旋转矩阵属于

\[
SO(3)=\{R\in\mathbb R^{3\times3}:R^\top R=I,\det R=1\}.
\]

它是嵌入高维欧氏空间的流形，不是任意九维矩阵。直接对旋转矩阵做普通线性平均会离开 \(SO(3)\)。

## 5.2 Manifold 与 Tangent Space

流形局部看起来像欧氏空间。切空间 \(T_x\mathcal M\) 提供在点 \(x\) 附近表示速度和小扰动的线性空间。机器人在 \(SE(3)\) 上优化位姿、在 \(SO(3)\) 上积分角速度，本质都依赖这个结构。

## 5.3 Lie Group / Lie Algebra

Lie group 同时有群结构和光滑流形结构。\(SO(3)\)、\(SE(3)\) 是机器人最重要的例子。Lie algebra 是单位元附近的切空间，用更易处理的线性对象表示局部运动：

\[
\hat\omega\in\mathfrak{so}(3),\qquad
R=\exp(\hat\omega\theta).
\]

这将在 Volume II 展开。

## 5.4 Graph 与关系结构

图 \(G=(V,E)\) 可表示机器人关节拓扑、物体关系、scene graph、多机器人通信网络。Graph Neural Network 的 message passing 一般写作

\[
h_i^{(l+1)}=\phi\left(h_i^{(l)},\operatorname{AGG}_{j\in\mathcal N(i)}\psi(h_i^{(l)},h_j^{(l)},e_{ij})\right).
\]

对 cross-embodiment，一个关键思想是把身体表示成图而非固定长度向量，使模型可接受不同关节数量与拓扑。

## 5.5 Factor Graph

SLAM 常把变量与测量因子写成 factor graph：

\[
p(X\mid Z)\propto\prod_k \phi_k(X_k,Z_k).
\]

优化负对数概率就得到稀疏 nonlinear least squares。这里体现了概率与优化的统一。

## 5.6 Causality

相关性模型学习 \(p(y\mid x)\)，因果问题问的是 intervention：

\[
p(y\mid do(x)).
\]

机器人天然可以干预世界，因此是研究因果的理想载体。但“能互动”不等于自动学到因果。若数据采集策略偏置、隐藏变量存在，模型仍可能只学习相关性。

## 5.7 Structural Causal Model

SCM 写为

\[
X_i=f_i(PA_i,U_i),
\]

其中 \(PA_i\) 是父变量，\(U_i\) 是外生噪声。机器人例子：抓取结果可能由抓取位姿、夹爪力、物体材质共同决定。若训练数据里“红色物体恰好总是轻”，模型可能错误把颜色当成因果变量。

## 5.8 Counterfactual

反事实问：“如果刚才换一个动作，会怎样？”

\[
Y_{a'}(u)
\]

这与 world model、offline policy evaluation、failure diagnosis 深度相关。真正强的物理智能应不仅预测观察到的轨迹，还能比较未执行动作的后果。

---

# 数学统一图

本卷中的对象可以压缩成一张图：

```text
Geometry / Lie groups ──→ pose, velocity, rigid motion
Linear algebra ─────────→ Jacobian, projection, representation
Calculus / ODE ─────────→ dynamics, gradients, integration
Probability ────────────→ belief, state estimation, uncertainty
Information theory ─────→ active perception, representation
Optimization ───────────→ IK, planning, control, training
Dynamic programming ────→ RL, planning, long-horizon decision
Graphs ─────────────────→ kinematic topology, scene relation
Causality ──────────────→ intervention, mechanism, counterfactual
Optimal transport/flow ─→ generative action models
```

## 必做推导

读者应能独立完成：

1. 从 normal equation 推导 least squares；
2. 用 SVD 解释 pseudoinverse；
3. 对二维两关节机械臂手算 Jacobian；
4. 推导一维 Kalman update；
5. 从 Bellman principle 写出有限时域动态规划；
6. 给出一个 Lyapunov function 并判断稳定性；
7. 写出一个简单 flow ODE 并数值积分；
8. 用一个三变量 SCM 区分 correlation 与 intervention。

## 推荐资料

- Strang, *Introduction to Linear Algebra*.
- Boyd & Vandenberghe, *Convex Optimization*.
- Bertsekas, *Dynamic Programming and Optimal Control*.
- Barfoot, *State Estimation for Robotics*.
- Thrun, Burgard & Fox, *Probabilistic Robotics*.
- Lynch & Park, *Modern Robotics*.
- Sutton & Barto, *Reinforcement Learning: An Introduction*.
