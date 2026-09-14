# Part 11　运动规划、任务规划与不确定决策

## 学习目标

读完本章，应能把“去哪里、怎么过去、先做什么、信息不够时先观察什么”区分成不同规划层次；理解 configuration space、A*/RRT、trajectory optimization、kinodynamic planning、TAMP、belief-space planning 与 receding-horizon replanning；知道 learned policy 和 classical planner 的边界怎样划分。

---

## 11.1 Planning 的基本对象

规划不是泛指“想一想”。它至少包含：

- **Path planning**：找一条几何可行路径；
- **Trajectory planning**：路径还带时间、速度、加速度；
- **Kinodynamic planning**：同时满足 dynamics；
- **Task planning**：决定离散动作顺序；
- **Planning under uncertainty**：belief 而非精确 state 上决策。

如果论文写“planning”却没有说明搜索的是哪个空间，就很难判断算法真正解决什么。

## 11.2 Configuration Space

机器人 configuration \(q\in\mathcal C\)。工作空间障碍映射成 configuration-space obstacle：

\[
\mathcal C_{obs}=\{q:\text{robot}(q)\cap\mathcal O\ne\emptyset\}.
\]

可行区域：

\[
\mathcal C_{free}=\mathcal C\setminus\mathcal C_{obs}.
\]

于是复杂机械臂 collision planning 被统一为：在高维 \(\mathcal C_{free}\) 中找连续曲线。

## 11.3 Collision Checking

给定 \(q\)，先 FK 得到所有 link pose，再判断：

- self-collision；
- robot–environment collision；
- attached object collision。

规划器往往绝大时间花在 collision checking，因此 collision geometry、broad-phase、distance field 与 caching 都影响系统性能。

## 11.4 Graph Search

Dijkstra：

\[
g(n')=\min(g(n') , g(n)+c(n,n')).
\]

A*：

\[
f(n)=g(n)+h(n).
\]

若 heuristic \(h\) admissible，则 A* 可保持最优性。好的 heuristic 本质是用便宜估计缩小搜索。

## 11.5 PRM

Probabilistic Roadmap：

1. 在 \(\mathcal C_{free}\) 采样节点；
2. 连接局部可达邻居；
3. 构建 roadmap；
4. query 时将 start/goal 接入图并搜索。

适合同一环境多次 query。

## 11.6 RRT

Rapidly-exploring Random Tree 反复：sample → nearest → steer → collision check → add。由于 Voronoi bias，它会快速扩展到尚未探索的大区域。

RRT 擅长找到“某条路”，但不保证短。

## 11.7 RRT*

RRT* 加入 choose-parent / rewiring，在适当条件下：

\[
C_n\rightarrow C^*\quad(n\rightarrow\infty).
\]

即 asymptotically optimal。代价是更高计算。

## 11.8 Narrow Passage

Sampling-based planner 的经典困难是狭窄通道：可行区域体积很小，uniform sampling 很难命中。

这也是 learned sampler 有价值的位置：学习哪里值得采样，而不是直接替代完整 feasibility checking。

## 11.9 Path vs Trajectory

Path \(q(s)\) 只描述几何；trajectory \(q(t)\) 还要求：

\[
|\dot q|\le v_{max},
\qquad
|\ddot q|\le a_{max}.
\]

路径可行不等于机器人能按任意速度执行。

## 11.10 Trajectory Optimization

直接优化离散 trajectory：

\[
\min_{q_{0:T}}J(q_{0:T})
\]

例如：

\[
J=\lambda_sJ_{smooth}+\lambda_cJ_{collision}+\lambda_gJ_{goal}.
\]

CHOMP 使用 functional gradient；STOMP 通过 stochastic perturbation；TrajOpt 类方法使用 sequential convex optimization。

优点：轨迹平滑、易加 cost；缺点：非凸、依赖 initialization。

## 11.11 Kinodynamic Planning

高速 drone、vehicle、legged robot 不能任意连接两个 configuration，必须满足：

\[
\dot x=f(x,u).
\]

搜索节点在 state space，edge 是可执行 control rollout。所谓“几何可达”不再足够。

## 11.12 Motion Primitive

可以预先定义短时动力学可行 motion primitive：

\[
m_i:x\mapsto x'.
\]

规划器在 primitive graph 上搜索，比任意连续 control 搜索高效。现代 skill library / latent action 也可看作更学习化的 primitive。

## 11.13 Task Planning

任务层可能写成离散 operator：

```text
Pick(cup)
Open(drawer)
Place(cup, drawer)
```

每个 operator 有 precondition 与 effect。例如：

\[
\text{Pick}(o):
\quad pre: reachable(o)\land handempty,
\]

\[
 effect: holding(o)\land\neg handempty.
\]

符号 planner 擅长组合长时结构，却依赖 state abstraction 正确。

## 11.14 Task and Motion Planning

TAMP 连接离散 plan 与连续 feasibility：

```text
symbolic plan candidate
      ↓
choose grasp / pose / base location
      ↓
IK / collision / motion feasibility
      ↓
if fail → backtrack symbolic choices
```

这解决一个根本问题：语言上合理的任务步骤，几何上未必做得到。

## 11.15 Affordance 与 Planner

Learned affordance 可以缩小搜索：哪里可抓、哪里可推、哪个 base pose 更可操作。

但 affordance proposal 与 feasibility proof 不同。一个 high-score grasp 仍需 IK/collision/contact check。

## 11.16 Planning Under Uncertainty

如果 state 是 belief \(b_t\)，action 同时影响物理状态与未来信息：

\[
b_{t+1}=\tau(b_t,a_t,o_{t+1}).
\]

最优动作可能不是直接靠近目标，而是先“看一眼”以减少 uncertainty。

这就是 active perception 与 planning 的统一点。

## 11.17 Information-Gathering Action

候选动作可按：

\[
U(a)=\mathbb E[R\mid a]+\beta I(S;O'\mid a)-\lambda C(a)
\]

评分。第二项奖励未来 observation 带来的信息。

普通 shortest path 没有这一项，因此不会主动绕到更好的观察位置。

## 11.18 Receding-Horizon Planning

长 horizon 一次性 plan 很容易因世界变化失效。更实用：

1. plan 一段；
2. execute 一小段；
3. re-observe；
4. update state/belief；
5. replan。

这与 MPC、VLA action chunk 的共同思想都是**滚动闭环**。

## 11.19 Hierarchical Planning

不同时间尺度：

```text
minutes: task sequence
seconds: skill / waypoint
100 ms: motion / action chunk
1–10 ms: control
```

把所有决策压在同一个 Transformer frequency 上既浪费计算，也让 safety 难验证。

## 11.20 Learned Planner

学习可以进入规划多个位置：

- heuristic \(h_\theta\)；
- sampling distribution；
- cost / value；
- dynamics model；
- skill proposal；
- high-level task decomposition。

最稳健的思路通常不是“去掉 search”，而是让 learning 提供 search 的 prior，再保留在线 feasibility/replanning。

## 11.21 VLM / LLM Planner

语言模型擅长语义 decomposition：

```text
“整理桌面”
→ 找垃圾
→ 丢垃圾
→ 把杯子放托盘
→ 把书叠好
```

但它不知道实时 collision、grasp feasibility、force。高层语言 plan 必须经过 grounded executor / tool / world-state verification。

SayCan 的经典意义就在于把 language score 与可执行 affordance/value 分开。

## 11.22 VLA 与 Planning

VLA 可以把一部分 planning 隐进 policy：

\[
a_{t:t+H}=\pi(o_{\le t},g).
\]

但我们仍需问：

- horizon 多长？
- 中途状态变化会不会 replan？
- 是否显式检查 collision/safety？
- unseen long-horizon composition 靠什么完成？

“端到端”不是“没有 planning”，可能只是 planning structure 不可见。

## 11.23 Planner–Policy Hybrid

现实可扩展架构：

```text
Reasoner / task planner
          ↓ subgoal
Learned manipulation / navigation skill
          ↓ nominal trajectory/action
Motion planner / IK / WBC / safety
          ↓ executable command
Physical world
          ↑ feedback
```

高层负责组合，学习 skill 处理高维复杂 interaction，低层保证 feasibility。

## 11.24 常见失败

- planner 使用过期 map；
- symbolic precondition 与真实状态不一致；
- learned cost 在 OOD state 给错误低 cost；
- TAMP 组合 explosion；
- trajectory optimization 卡 local minimum；
- action chunk 太长，中途环境改变仍照旧执行；
- language planner 生成语义合理但物理不可执行 subgoal。

## 最小实验

构造一个桌面机械臂任务：同一 start/goal 有窄通道。比较 RRT、RRT*、trajectory optimization；再加入“遮挡导致障碍位置 uncertain”，让一种 planner 直接走最短路，另一种先移动相机减少 uncertainty。比较成功率、路径长度与 sensing cost。

## 研究问题

1. Foundation VLA 规模越来越大后，显式 motion planner 还应该保留在哪些场景？
2. 能否让 world model 提供 counterfactual rollout，同时由 classical constraints 保证 action 可执行？
3. 最优 task abstraction 应由人定义，还是从长期 experience 自动形成？
