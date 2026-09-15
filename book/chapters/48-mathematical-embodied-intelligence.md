# Part 48　数学化具身智能：从相关性到结构与规律

## 48.1 Physical Invariance

物理规律常对某些变换不变。

例如把整个实验平移：

\[
x_i' = x_i+c
\]

相对运动规律不应改变。

如果模型需要为每个绝对位置重新学习，就是浪费数据。

---

## 48.2 Equivariance

对变换 \(g\)：

\[
f(gx)=g f(x).
\]

SE(3)-equivariant representation 可让空间旋转/平移规律直接写进 architecture。

对 3D manipulation 特别重要。

---

## 48.3 Symmetry

机器人问题中存在：

- left/right symmetry；
- object permutation；
- rotational symmetry；
- identical fingers。

利用 symmetry 可以减少 hypothesis space。

---

## 48.4 Conservation Law

真实动力系统受：

- energy；
- momentum；
- angular momentum

等规律约束。

learned dynamics 若长期违反守恒，rollout 会漂移。

可以在 loss / architecture 中加入物理约束。

---

## 48.5 Constraint

机器人智能从来不是无约束函数拟合。

\[
g(x,u)=0,\quad h(x,u)\ge0.
\]

约束包括：

- kinematics；
- collision；
- contact；
- actuator limits；
- safety。

把约束显式化可大幅减少无效搜索空间。

---

## 48.6 Geometry-Aware Learning

位置、旋转、pose 不是普通 vector。

SO(3)/SE(3) 上学习应尊重 manifold geometry。

例如 rotation loss 应避免 Euler angle discontinuity。

---

## 48.7 Koopman Operator

非线性 dynamics：

\[
x_{t+1}=f(x_t)
\]

在 observable space 中可能近似线性：

\[
\psi(x_{t+1})\approx K\psi(x_t).
\]

Koopman 思想提供一种把复杂 dynamics 升维后线性化的途径。

对控制价值在于可以复用线性系统工具。

---

## 48.8 System Identification

从 interaction data 识别：

\[
\theta^*=\arg\min_\theta\sum_t\|x_{t+1}-f_\theta(x_t,u_t)\|^2.
\]

现代 foundation model 不应让 system ID 消失；相反，新 embodiment / payload / friction 的在线识别可能是泛化关键。

---

## 48.9 Causal Representation

希望 representation 拆出真正影响 transition 的因素：

\[
z=(mass,friction,joint\ type,goal,\dots).
\]

如果只是 correlational latent，很难在 intervention 下泛化。

---

## 48.10 Object / Relation / Mechanism Decomposition

把世界写成：

\[
World=Objects+Relations+Mechanisms.
\]

例如“抽屉”不是视觉类别，而是：

- handle object；
- prismatic joint；
- containment relation；
- friction mechanism。

这种 decomposition 更接近可迁移规律。

---

## 48.11 Compositionality

如果能力：

\[
C=Compose(M_1,M_2,\dots,M_k),
\]

模型可以用已知 mechanism 组合新行为。

组合泛化比 task memorization 更接近通用智能。

---

## 48.12 Mechanism Learning

目标不再是：

\[
(o_t,g)\rightarrow a_t
\]

而是学习局部机制：

\[
M_i:(state,action)\rightarrow effect.
\]

再由 planner/assembler 组合。

关键检验是机制能否跨对象、场景、embodiment 复用。

---

## 48.13 Hybrid Symbolic–Continuous System

物理任务同时包含：

### Discrete

- door open/closed；
- holding/not holding；
- skill stage。

### Continuous

- pose；
- velocity；
- force。

因此 hybrid system：

\[
(q,x),\quad q\text{ discrete},\ x\text{ continuous}
\]

可能比纯 token 或纯 vector 更自然。

---

## 48.14 Differentiable Physics

如果 simulator 可微：

\[
\frac{\partial x_T}{\partial u_{0:T-1}}
\]

可直接用于 trajectory optimization、system ID、policy learning。

但真实 contact 往往非平滑，可微近似必须谨慎。

---

## 48.15 Neural ODE / Continuous Dynamics

\[
\dot z=f_\theta(z,u,t).
\]

连续模型适合：

- irregular sampling；
- multi-rate sensors；
- physics-inspired dynamics。

但计算成本和 stiffness 仍是问题。

---

## 48.16 Physics-Informed / Physics-Constrained Learning

有三种强度：

### soft prior

把物理 residual 放 loss。

### hard constraint

architecture 天然满足约束。

### hybrid

known physics + learned residual：

\[
f=f_{physics}+f_{learned}.
\]

机器人中 hybrid 往往很实用，因为已知动力学不必重新从数据学。

---

## 48.17 从“拟合动作”到“学习规律”

纯行为拟合：

\[
\pi:o\mapsto a.
\]

更强目标：

\[
\{M_i\}=Discover(interaction),
\]

\[
plan=Compose(\{M_i\},goal,embodiment).
\]

如果成功，模型可以：

- 少数据适配；
- 跨 embodiment；
- 做 counterfactual；
- 解释失败。

这可能是从 foundation policy 走向更深 physical intelligence 的路线之一。

---

## 最小实验：规律还是记忆

训练模型见过：

- 多种物体；
- 多种视觉纹理；
- 少数几种 friction/mass 组合。

测试未见组合：

```text
seen appearance + unseen physics
unseen appearance + seen physics
unseen appearance + unseen physics
```

如果模型真正学习机制，它应对 physics factor 有结构化外推，而不是只跟视觉相似度走。

---

## 本章结论

数学介入具身智能的真正价值，不是让论文公式更多，而是把 **symmetry、geometry、constraint、dynamics、causality、mechanism 和 compositionality** 变成模型的结构，使系统从经验相关性逐步走向可迁移的物理规律。
<!-- CHAPTER-ENRICHMENT-R2-P48:START -->
## 48.21 数学化失败：公式多不等于机制清楚

### 把 notation 当 explanation

给每个模块写一个符号，并没有解释它为什么存在、满足什么 invariant、在什么条件下会失败。

### Optimization objective 与 scientific objective 不同

训练 loss 可下降，但研究真正关心的是 task success、identifiability、stability、transfer 或 causal mechanism。二者必须显式连接。

### 过度连续化

Contact、mode switch、tool change、memory write/delete 等含离散事件。强行用光滑 ODE 描述全部系统可能隐藏关键 hybrid dynamics。

### 不可辨识模型也能拟合数据

\[
P_{\theta_1}(O)=P_{\theta_2}(O)
\]

不代表两个模型在 intervention 下相同。纯 prediction loss 无法自动发现“真实规律”。

### 数学保证建立在错误假设上

Lyapunov、convexity、observability 等结论都依赖假设。机器人最危险的情况是 theorem 正确，而真实 deployment 不满足模型假设。

## 48.22 研究问题

1. 下一代具身架构最应该显式编码哪些 invariant：SE(3)、contact、conservation、causal locality、morphology graph 还是 time-scale separation？
2. 能否从 interaction 中自动发现新的 state variable / constraint，而不是预先固定网络宽度与 latent dimension？
3. 如何把 identifiability 变成 active exploration objective，让机器人主动做最能区分 competing mechanisms 的实验？
4. 结构生长/遗忘能否被写成优化之外的离散结构动力学，而不只是在固定网络上更新权重？
5. 什么数学对象最适合描述“不分训练和推理、持续与世界交互更新”的长期 physical agent？
<!-- CHAPTER-ENRICHMENT-R2-P48:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 48`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-48)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
