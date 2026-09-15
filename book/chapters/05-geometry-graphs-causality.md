# Part 5　几何、流形、图与因果

## 学习目标

本章把四类经常被分别教授的对象放回同一个机器人问题：**几何约束告诉我们状态“在哪里”，图结构告诉我们变量“怎样连接”，因果结构告诉我们动作“改变了什么”，可辨识性告诉我们从数据究竟能推出多少。**

---

## 5.1 为什么欧氏向量不够

三维位置属于 \(\mathbb R^3\)，旋转却不是一个普通三维向量。旋转矩阵属于：

\[
SO(3)=\{R\in\mathbb R^{3\times3}:R^TR=I,\det R=1\}.
\]

它有约束、曲率和群结构。若直接对两个 rotation matrix 做普通线性插值，结果通常不再是合法 rotation。

机器人真正面对的是“混合状态空间”：位置、旋转、关节角、离散 contact mode、object graph、belief distribution 同时存在。把它们全部拍平成普通向量不代表结构消失，只代表模型被迫从数据重新学习这些结构。

## 5.2 Manifold

流形 \(\mathcal M\) 局部类似欧氏空间，但全局可能有复杂结构。每个点 \(x\) 有 tangent space \(T_x\mathcal M\)，可在其中表示局部速度/扰动。

机器人位姿优化的正确直觉是：state 在 manifold 上，increment 在 tangent space 中。

例如：

\[
R\in SO(3),\qquad \delta\theta\in T_RSO(3)\simeq\mathbb R^3.
\]

这解释了为什么优化器可以在三维局部坐标里更新旋转，但更新后必须通过 exponential map 回到合法群元素。

## 5.3 Lie Group

Lie group 同时是群和光滑流形。\(SO(3)\)、\(SE(3)\) 是最重要例子。

Group operation 对应 compose transform，identity 对应无变换，inverse 对应反向 transform。

这不是纯数学装饰。相机外参、末端位姿、base pose、object pose 都在不断做 composition / inverse。只要系统出现 frame chain，就已经在使用群结构。

## 5.4 Lie Algebra 与 Exp / Log

Lie algebra 是 identity 附近 tangent space。三维角速度向量映射为 skew matrix：

\[
\hat\omega=\begin{bmatrix}
0&-\omega_z&\omega_y\\
\omega_z&0&-\omega_x\\
-\omega_y&\omega_x&0
\end{bmatrix}.
\]

Exponential map 将局部速度积分回 group：

\[
R'=R\exp(\widehat{\delta\theta}).
\]

Log map 则把有限 rotation error 拉回局部向量：

\[
e_R=\log(R_d^{-1}R)^{\vee}.
\]

这里已经出现一个重要 convention：perturbation 左乘还是右乘？它决定 error 在 world frame 还是 body frame 表达。很多“优化发散”其实是这一步 convention 与 Jacobian 不一致。

## 5.5 Equivariance

若输入通过群作用 \(g\) 变化，输出按相应作用变化：

\[
f(gx)=\rho(g)f(x).
\]

这是一种“把物理对称性写进模型”的方法。对 3D manipulation，SE(3)-equivariant feature 可能比纯数据 augmentation 更 sample-efficient。

但 equivariance 不是越多越好。任务中存在 gravity、桌面法向、相机安装方向等**真实破缺的对称性**。若模型强制对这些因素也保持不变，反而会丢失控制需要的信息。

## 5.6 Graph：身体和世界天然是关系结构

图：

\[
G=(V,E).
\]

机器人身体本来就是 graph：link/joint 是 node/edge；场景也是 graph：对象与 spatial/contact relation 构成边；多机器人 communication 也形成 graph。

常见三类图：

```text
kinematic graph: link -- joint -- link
scene graph:     object -- relation/contact -- object
factor graph:    variable -- measurement factor -- variable
```

它们的 node/edge 语义不同，不能因为都叫 graph 就直接共用同一种 message passing。

## 5.7 Message Passing

\[
m_i=\operatorname{AGG}_{j\in\mathcal N(i)}\psi(h_i,h_j,e_{ij}),
\]

\[
h_i'=\phi(h_i,m_i).
\]

Graph architecture 能自然适应 variable number of joints / objects，是 cross-embodiment 与 object-centric model 的重要候选。

但“能接受不同 node 数量”不等于自动理解不同 embodiment。还必须知道 edge type、joint axis、link geometry、actuation limits、node identity 与 action interface。

## 5.8 Factor Graph

概率后验常分解：

\[
p(X\mid Z)\propto\prod_k\phi_k(X_k,Z_k).
\]

取负 log 变成稀疏 nonlinear least squares。SLAM 中 pose、landmark、IMU、loop closure 都可作为变量与 factor。

图结构的价值不仅是可视化，而是揭示 Jacobian / Hessian 的 sparse block structure，使大规模优化可计算。

## 5.9 Causal Graph

结构因果模型：

\[
X_i=f_i(PA_i,U_i).
\]

相关性问 \(p(y\mid x)\)，干预问：

\[
p(y\mid do(x)).
\]

机器人最大的优势是能**真的 do(action)**，因此比纯互联网观察更适合收集因果数据。

一个最小 manipulation SCM 可以写成：

```text
object mass ─────┐
friction ────────┼→ object motion
robot action ────┤
contact mode ────┘

object color ─→ camera pixels
lighting ─────→ camera pixels
```

如果训练数据让 `color` 与 `mass` 共变，policy 很容易把视觉 shortcut 当成动力学规律。

## 5.10 Confounding

如果训练中红色物体总是轻，模型可能学到 color→required force 的伪相关。换成红色重物时失败。

解决不是简单“更多同分布数据”，而是主动打破 confounding：控制颜色、质量独立变化。

更一般地，机器人数据里的 confounder 可能是：

- operator identity 与任务难度；
- camera view 与 robot type；
- scene 与成功标签；
- controller version 与 model checkpoint；
- simulation asset 与 train/test split。

因此数据工程和因果实验设计不可分离。

## 5.11 Intervention

真正的 intervention 是主动改变一个变量，并尽量保持其他机制不变：

\[
do(A=a).
\]

例如固定同一个 object pose，改变 grasp force；固定同一个 action，改变 friction；固定 instruction，移动 irrelevant distractor。

这种实验比“看 attention map”更接近回答模型到底依赖什么。

## 5.12 Counterfactual

决策需要比较未执行动作：

> 如果刚才从另一侧抓，会不会滑？

形式上比较潜在结果 \(Y(a_1),Y(a_2)\)。World model 真正用于 planning，必须对 counterfactual action 有正确敏感性。

因此一个 video predictor 若只会产生“最可能未来”，却不能对不同 action 生成不同且正确的后果，它还不是足够的 control world model。

## 5.13 Identifiability

即使模型拟合所有 observation，也不一定唯一恢复真实 mechanism。多个 hidden causal model 可能产生相同 observational distribution。

因此“发现物理规律”的 claim 必须说明哪些 intervention 足以辨识机制。

可以把问题写成：

\[
P_{\theta_1}(O)=P_{\theta_2}(O)
\]

但

\[
P_{\theta_1}(Y\mid do(A=a))\neq P_{\theta_2}(Y\mid do(A=a)).
\]

只看 observational fit 无法区分 \(\theta_1,\theta_2\)，而 action intervention 可以。

## 5.14 几何与因果的结合

机器人很多 mechanism 同时具有 geometry 与 causality：抽屉的关节轴是几何 constraint，同时决定“沿什么方向施力才会开”。如果 representation 只识别语义“drawer”，却没有 axis/contact/effect，就很难跨柜子迁移。

类似地：

- door hinge axis 决定 admissible motion；
- support polygon 决定 humanoid balance feasibility；
- contact normal 决定可传递的 force direction；
- kinematic tree 决定一个 joint intervention 会影响哪些 links。

因此“物理规律”常常不是一条纯 scalar equation，而是**几何约束 + 图结构 + intervention response**的组合。

## 5.15 从 scene 到 action 的结构化数据流

```text
raw sensors
→ metric geometry / poses on SE(3)
→ object & body graph
→ state / relation variables
→ candidate intervention a
→ predicted causal effect
→ planner / policy chooses action
→ real outcome
→ update graph / belief / mechanism
```

一个 architecture 若声称“结构化物理推理”，至少要说明自己在哪一步显式表示了 geometry、relation 和 intervention，而不是只在最终语言解释里出现这些词。

## 5.16 常见失败

### 把坐标差当 manifold error

直接做 rotation matrix element MSE，可能优化出不在 \(SO(3)\) 上的中间结果；直接减 quaternion 又会遇到双覆盖符号问题。

### 左/右 perturbation 混用

error 在 body frame，Jacobian 却按 world frame 推导，solver 可能每一步都“方向差不多”，但就是无法收敛。

### Graph batching 后丢掉语义

只把不同 robot padding 成同样 node 数，而不编码 joint type/axis/limits，得到的是相同 shape，不是相同 embodiment semantics。

### 把相关性称为因果规律

若没有 intervention、environment change 或明确 identifiability assumptions，不能仅凭 prediction accuracy 声称“发现了物理机制”。

### 过度强制 equivariance

把 gravity direction、support surface 等任务相关 reference 也视为可随意旋转的 nuisance，会伤害实际控制。

## 最小实验

### 实验 A：几何

随机生成合法 \(R\in SO(3)\)，比较三种 update：矩阵直接加法、quaternion normalize、Lie-algebra exponential update。测 orthogonality error：

\[
\|R^TR-I\|_F.
\]

### 实验 B：图

构造 3-link 与 5-link kinematic graph，让同一 message-passing policy 接受 variable node count。然后打乱 joint-axis metadata，验证“图结构存在”本身不足以跨本体。

### 实验 C：因果

构造 object color 与 mass。在 training 中让它们高度相关，再在 test 打破相关。比较普通 policy 与显式利用 force feedback / active intervention 的 policy，观察 shortcut 如何形成并被打破。

## 研究问题

1. Cross-embodiment representation 应该显式编码 kinematic graph，还是让统一 policy 从 trajectories 中自行发现拓扑？
2. SE(3)-equivariance 的最佳边界在哪里：哪些变量应该 equivariant，哪些 reference frame 必须保留？
3. World model 的 latent dynamics 要满足什么 intervention test，才有资格被称为“物理机制”而非 sequence predictor？
4. 能否联合学习 object-centric graph、contact graph 与 causal mechanism，同时又保持 online inference 足够高效？
5. 对持续学习机器人，可辨识性是否应该成为 active exploration 的目标，而不仅是 prediction uncertainty？

## Source anchors / 原始来源

- Lynch & Park, *Modern Robotics*（Lie groups / rigid-body motions）: https://modernrobotics.northwestern.edu/
- Kschischang, Frey & Loeliger, “Factor Graphs and the Sum-Product Algorithm,” IEEE TIT 2001: https://doi.org/10.1109/18.910572
- Bronstein et al., “Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges”: https://arxiv.org/abs/2104.13478
- Judea Pearl, *Causality: Models, Reasoning, and Inference*: https://doi.org/10.1017/CBO9780511803161
- Peters, Janzing & Schölkopf, *Elements of Causal Inference*: https://mitpress.mit.edu/9780262037310/elements-of-causal-inference/

## 本章结论

几何回答“合法状态和变换是什么”，图回答“局部结构如何连接”，因果回答“主动改变一个变量会发生什么”。真正面向物理世界的表示学习，最终必须同时尊重这三类结构，并对**哪些机制可由现有数据辨识**保持明确边界。
