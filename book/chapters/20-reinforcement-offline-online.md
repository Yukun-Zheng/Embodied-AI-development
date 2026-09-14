# Part 20　强化学习、Offline RL 与交互学习

## 学习目标

掌握 MDP、value/Q/advantage、Bellman equation、policy gradient、actor–critic、PPO、SAC、model-based RL、offline RL、goal-conditioned/hierarchical RL、reward design、exploration 与 residual RL；更重要的是理解为什么真实机器人 RL 的核心问题不是“选哪个算法”，而是**怎样安全地产生高价值交互、怎样利用 demonstration prior、怎样把失败转成经验，以及怎样防止 online update 破坏已有能力**。

---

## 20.1 MDP

马尔可夫决策过程：

\[
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
\]

状态转移：

\[
s_{t+1}\sim P(\cdot\mid s_t,a_t).
\]

策略：

\[
a_t\sim\pi_\theta(\cdot\mid s_t).
\]

目标：

\[
J(\pi)=\mathbb E_\pi
\left[\sum_{t=0}^{\infty}\gamma^t r_t\right].
\]

机器人经常部分可观测，因此真正系统更接近 POMDP；RL 只是先从 state-known 版本理解 decision structure。

## 20.2 Return

从时刻 \(t\) 开始：

\[
G_t=\sum_{k=0}^{\infty}\gamma^k r_{t+k}.
\]

\(\gamma\) 不是“未来不重要”的哲学参数，也决定有效 horizon：

\[
H_{eff}\approx\frac1{1-\gamma}.
\]

\(\gamma=0.99\) 的有效范围约百步量级；control frequency 改变时，同一 \(\gamma\) 对真实时间 horizon 的含义也改变。

## 20.3 Value Function

\[
V^\pi(s)=\mathbb E_\pi[G_t\mid s_t=s].
\]

Action value：

\[
Q^\pi(s,a)=\mathbb E_\pi[G_t\mid s_t=s,a_t=a].
\]

Advantage：

\[
A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s).
\]

它回答：在这个 state 中，action 比 policy 平均水平好多少。

## 20.4 Bellman Equation

\[
V^\pi(s)=
\mathbb E_{a\sim\pi,s'\sim P}
[r(s,a)+\gamma V^\pi(s')].
\]

Optimal Bellman：

\[
Q^*(s,a)=
\mathbb E[r+\gamma\max_{a'}Q^*(s',a')].
\]

RL 大量算法只是用不同数据与 function approximation 逼近这些 fixed-point equation。

## 20.5 Q-Learning

Tabular update：

\[
Q(s,a)\leftarrow Q(s,a)+
\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)].
\]

Target 与当前 Q 都由同一估计产生会造成 instability，deep Q-learning 因此使用 target network、replay buffer 等机制。

连续高维 action 下 \(\max_a Q(s,a)\) 难求，actor–critic 更自然。

## 20.6 Policy Gradient

Policy gradient theorem：

\[
\nabla_\theta J
=\mathbb E_{s,a\sim\pi}
[\nabla_\theta\log\pi_\theta(a\mid s)Q^\pi(s,a)].
\]

用 baseline 不改变期望，却降低 variance：

\[
Q\rightarrow A=Q-V.
\]

机器人中 high-variance gradient 意味着需要更多 physical rollout，因此 sample efficiency 很重要。

## 20.7 Actor–Critic

Actor \(\pi_\theta\) 产生 action，critic \(V_\phi/Q_\phi\) 估计 future return。

```text
state
├─ actor → action → environment
└─ critic → value estimate
```

Critic 可以训练时看到 privileged state，而 actor 部署只看 proprioception/vision，这在 sim-to-real locomotion 很常见。

## 20.8 Generalized Advantage Estimation

TD residual：

\[
\delta_t=r_t+\gamma V(s_{t+1})-V(s_t).
\]

GAE：

\[
\hat A_t^{GAE}=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}.
\]

\(\lambda\) 在 bias 与 variance 之间折中。

## 20.9 PPO

Probability ratio：

\[
r_t(\theta)=
\frac{\pi_\theta(a_t\mid s_t)}
{\pi_{\theta_{old}}(a_t\mid s_t)}.
\]

Clipped objective：

\[
L^{clip}=\mathbb E
\left[
\min(r_tA_t,
\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t)
\right].
\]

PPO 通过限制每次 policy update 幅度获得实用稳定性，因此在 massive parallel locomotion 中极常见。

## 20.10 PPO 不等于“简单”

最终 locomotion performance 还严重依赖：

- reward；
- observation；
- action scaling；
- PD gain；
- reset；
- terrain curriculum；
- privileged critic；
- domain randomization。

如果只说“用了 PPO”，几乎没有解释能力来源。

## 20.11 SAC

Soft Actor-Critic 最大化：

\[
J=\mathbb E
\left[
\sum_t r_t+\alpha\mathcal H(\pi(\cdot\mid s_t))
\right].
\]

Soft Q target：

\[
y=r+\gamma
\mathbb E_{a'\sim\pi}
[Q_{target}(s',a')-\alpha\log\pi(a'\mid s')].
\]

Off-policy replay 提高数据复用，适合真实机器人样本昂贵场景。

## 20.12 On-Policy vs Off-Policy

**On-policy**：数据来自当前 policy，distribution matched，但每次更新后旧数据价值下降；

**Off-policy**：可以反复利用 replay / demonstration，样本高效，但 distribution mismatch 与 Q extrapolation 更难处理。

真实 robot RL 往往更青睐能复用旧数据的方法。

## 20.13 Reward Design

Reward 是算法真正优化的 objective：

\[
r_t=w_1r_{task}+w_2r_{smooth}+w_3r_{energy}+\cdots.
\]

如果任务“拿起杯子”只奖励高度，agent 把杯子撞飞也可能高分。

Reward hacking 不是模型“坏”，而是 objective 与真正意图错位。

## 20.14 Dense vs Sparse Reward

Sparse terminal success：语义对齐强，但 exploration 难；dense shaping：学习快，却可能产生 shortcut。

一个好方法是保留 task-grounded success 为核心，再用 potential-based shaping / curriculum 提供学习信号。

## 20.15 Exploration

随机 exploration 在真机高风险。可利用：

- demonstration initialization；
- simulation pretraining；
- uncertainty-guided exploration；
- safe action set；
- human supervision；
- goal curriculum；
- world-model imagination。

所以“真实机器人 RL”本质上是安全 data acquisition 问题。

## 20.16 Goal-Conditioned RL

\[
\pi(a\mid s,g),
\qquad r=r(s,g).
\]

同一个 trajectory 可 relabel 多个 goal，增强数据复用。

如果 goal 是 image/language/subgoal latent，就与现代 generalist policy 接轨。

## 20.17 Hindsight Experience Replay

如果 agent 没到原 goal \(g\)，但到了 \(g'=s_T\)，可把 trajectory relabel 成“成功达到 \(g'\)”：

\[
(s_t,a_t,s_{t+1},g')
\]

用于训练 goal-conditioned value/policy。

它把失败 episode 中仍然发生的有效行为转成 supervision。

## 20.18 Hierarchical RL

高层：

\[
z_k\sim\pi_H(z\mid s,g),
\]

低层：

\[
a_t\sim\pi_L(a\mid s,z_k).
\]

\(z\) 可以是 option、skill、subgoal、language instruction。

层级结构自然对应机器人多时间尺度：高层几秒更新，低层几十/几百 Hz。

## 20.19 Option

Option 包含：initiation set、intra-option policy、termination：

\[
o=(I_o,\pi_o,\beta_o).
\]

现代 skill-conditioned VLA 虽然不一定使用 option terminology，但仍在解决相同问题：如何抽象可重用 temporally extended behavior。

## 20.20 Model-Based RL

学习：

\[
\hat s_{t+1}=f_\phi(s_t,a_t)
\]

或 distribution / latent dynamics。

然后用：

- model predictive control；
- imagined rollout；
- synthetic data；
- value expansion。

优势是 data efficiency；风险是 model bias 随 horizon 复合。

## 20.21 Model Bias

若单步模型误差 \(\epsilon\)，长 horizon prediction error 可能快速增长：

\[
\|\hat s_H-s_H\|
\not\approx H\epsilon
\]

因为 dynamics nonlinear、distribution shift 会放大错误。

所以 model-based RL 不应无限 rollout imagined future。

## 20.22 Offline RL

只给固定 dataset \(D\)：

\[
D=\{(s,a,r,s')\}.
\]

目标是在不继续交互的情况下学更好 policy。

最大问题：dataset 外 action 的 Q value 缺少真实证据。

## 20.23 Extrapolation Error

Actor 可能选择 dataset 中从未出现的 action；critic 网络却因 function approximation 给它虚高 Q：

\[
a_{OOD}=\arg\max_a Q_\theta(s,a).
\]

然后 policy 专门利用 critic 的错误。

## 20.24 Conservative Q Learning

CQL 类思想：压低广泛 action 的 Q，同时保留 dataset action 的 value：

\[
L_{CQL}=L_{Bellman}
+\alpha
\left[
\log\sum_a e^{Q(s,a)}
-\mathbb E_{a\sim D}Q(s,a)
\right].
\]

核心是避免对数据外 action 过度乐观。

## 20.25 IQL / Advantage-Weighted Regression

另一类方法不显式优化数据外 action，而从 dataset 中选择 advantage 高的 behavior 进行加权 imitation：

\[
L_\pi=-\mathbb E_D
[w(s,a)\log\pi(a\mid s)].
\]

这与 foundation policy 的“用 reward 筛选/重加权已有 experience”很自然兼容。

## 20.26 Demonstration + RL

最实用机器人 recipe：

```text
human / planner demonstrations
       ↓
behavior pretraining
       ↓
autonomous rollout
       ↓
reward / correction
       ↓
offline or online RL
```

RL 不再从随机策略开始，而是围绕一个已经有 broad competence 的 policy 做 refinement。

## 20.27 Residual RL

已有稳定 controller \(a_{base}\)：

\[
a=a_{base}+\Delta a_\theta.
\]

让 RL 只学 contact residual / model mismatch，可以显著减少 search space 和安全风险。

这是“经典控制 + learning”比完全端到端更有结构的一种方式。

## 20.28 Curriculum Learning

任务难度 \(d\) 随能力增长：

\[
d_{t+1}=f(d_t,\text{success rate}).
\]

例如 terrain、object mass、initial pose disturbance 逐渐增加。

但手工 curriculum 也会把研究者先验写进系统，论文应报告这些设计。

## 20.29 Locomotion RL

成熟 pipeline：

```text
massively parallel simulation
→ privileged critic
→ proprioceptive actor
→ terrain curriculum
→ domain randomization
→ system identification
→ real deployment
```

成功来自完整系统，不是单一 PPO objective。

## 20.30 Dexterous RL

Dexterous hand action 高维、contact mode 多、reward sparse，因此常依赖 simulation + privileged state + curriculum + motion prior。

如果最终 real policy 只看 vision/tactile，需要 teacher–student / distillation 解决 privileged-information gap。

## 20.31 Real-World Online RL

真机 online RL 受：

- reset cost；
- wear；
- safety；
- wall-clock time；
- human monitoring。

因此每次 interaction 的 information value 比 simulation 更重要。

## 20.32 Foundation Policy + Online RL

2025–2026 的重要转变：先有 broad VLA prior，再用 autonomous experience 精调 precision、speed、reliability。

以 Physical Intelligence π*0.6 / 2026 online-RL 路线为代表，foundation policy 提供安全且较强的初始 behavior，RL 不再探索“什么是抓取”，而是优化“怎样更快更准地完成这个特殊任务”。

## 20.33 Experience Data Flywheel

\[
\pi_t\rightarrow D_t^{rollout}
\rightarrow\text{reward/failure/correction}
\rightarrow\pi_{t+1}.
\]

真正持续 RL 系统必须同时维护：

- new-task improvement；
- old-task regression；
- safety；
- data quality；
- rollback。

## 20.34 Safe Exploration

定义 safe set \(\mathcal C\)。策略 proposal 先经过 shield：

\[
a_{safe}=\Pi_{\mathcal C}(a_{RL}).
\]

探索被限制在可恢复/安全区域，再逐步扩展 boundary。

这比把碰撞 reward 设成 -1000 后任由机器人试撞更符合真机现实。

## 20.35 Sim-to-Real RL

Domain randomization：

\[
\phi\sim p(\phi),
\]

训练 policy 对 mass/friction/delay/terrain 变化鲁棒。

如果 randomization 太窄，real 不在 support；太宽，policy 保守且难学。最好结合 real system identification posterior。

## 20.36 RL 与 Imitation 的统一视角

Imitation 优化“像 expert”；RL 优化“得到高 return”。

现代系统经常：

\[
L=L_{BC}+\lambda L_{RL}+\beta L_{reg}.
\]

不要把二者视为互斥阵营。真正问题是不同 supervision 何时可信、覆盖什么 state。

## 常见失败

- reward 与真正任务目标错位；
- simulator reset/curriculum 泄露 privileged information；
- offline RL 在 OOD action 上 Q 爆高；
- online RL 新任务提升但旧任务退化；
- PPO baseline reward/config 调差，导致不公平；
- real RL 不统计 reset/human 时间，只报告 gradient steps；
- domain randomization 范围凭感觉设置；
- safety 只是负 reward，没有独立 hard guard。

## 最小实验

建立一个 manipulation task，数据包含 expert + imperfect trajectories。比较 BC、IQL/CQL-style offline RL、BC→online SAC/actor-critic、residual RL。统一 real/sim interaction budget，报告 success、samples、wall-clock、unsafe event、旧任务 regression。特别画 critic 对 dataset distance 与 Q overestimation 的关系。

## 研究问题

1. Foundation policy 的下一次能力增长更应该来自 RL、更多 demonstration、world-model planning，还是三者组合？
2. 如何让 online RL 在真实机器人上只探索“有信息且可恢复”的 state？
3. Reward verifier 本身若由 VLM 给出，它的误差会怎样被 RL 放大？
