# Part 33　双臂、灵巧手与触觉智能

## 33.1 为什么双臂不是两个单臂

两个独立单臂策略：

\[
a_t^L=\pi_L(o_t),\quad a_t^R=\pi_R(o_t)
\]

无法自动保证：

- 相对位姿；
- cooperative force；
- collision avoidance；
- role coordination。

真正双臂策略必须建模 joint action：

\[
(a_t^L,a_t^R)\sim\pi(o_t,g).
\]

---

## 33.2 Relative Pose / Coordinated Frame

绝对位姿不是最自然的协调变量。

定义：

\[
T_{L\rightarrow R}=T_L^{-1}T_R.
\]

很多任务真正约束的是两手相对关系，例如：

- 拉紧布料；
- 搬箱子；
- handover；
- 双手装配。

---

## 33.3 Bimanual Constraint

共同持物时，对象形成闭链：

```text
left arm → object ← right arm
```

两臂不能独立随意运动。

约束可以写成：

\[
\phi(q_L,q_R)=0.
\]

控制必须满足：

\[
J_L\dot q_L-J_R\dot q_R=0
\]

或其任务定义变体。

---

## 33.4 Symmetric / Asymmetric Coordination

### Symmetric

两臂承担相似作用，例如抬大箱子。

### Asymmetric

一臂稳定、一臂操作，例如：

- 一手拿瓶、一手拧盖；
- 一手拉布、一手折叠。

学习系统需要动态分配角色，而不是固定“左臂辅助、右臂主操作”。

---

## 33.5 Leader–Follower Coordination

经典方式：

\[
x_F^{des}=f(x_L).
\]

优点是简单，缺点是 rigid role。

现代方法更希望根据任务状态切换 leader/follower，甚至不存在永久 leader。

---

## 33.6 Handover

handover 同时需要：

- 双臂/双机器人空间协调；
- grasp overlap；
- force transfer；
- release timing。

成功条件不是“两个手都碰到物体”，而是物体 support 从 A 平滑转移给 B。

---

## 33.7 Cooperative Manipulation

共同搬运时，对象 wrench：

\[
w=G_L f_L+G_R f_R.
\]

存在 internal force：两手施力互相抵消却不改变对象运动。

过大的 internal force 会损坏对象或造成不稳定。

---

## 33.8 Collision / Deadlock / Safety

双臂 action space 维度高，容易出现：

- self-collision；
- crossed arms；
- mutual blocking；
- deadlock。

安全约束应在 policy 之外仍有实时 monitor。

---

## 33.9 Dexterous Hand Kinematics

多指手拥有高 DOF：

\[
q_{hand}\in\mathbb R^n,\quad n\gg 2.
\]

优势：接触丰富；难点：

- high-dimensional action；
- tendon coupling；
- calibration；
- tactile sensing；
- sim2real。

---

## 33.10 Grasp Synergy

人手动作并不是每个关节完全独立。

可以用低维 synergy：

\[
q\approx \bar q+Wz,
\]

其中 \(z\) 维度远小于关节数。

这给 dexterous policy 提供一个重要思路：低维 latent action + 高频局部 residual。

---

## 33.11 In-Hand Manipulation

任务包括：

- rotate；
- regrasp；
- finger gaiting；
- object repositioning。

核心是接触集合持续变化。

视觉常看不到指内接触，所以 tactile/proprioception 非常重要。

---

## 33.12 Whole-Hand Contact

灵巧操作不是多个 fingertip 独立接触的简单和。

掌心、指腹、侧面都可能参与。

这要求表示：

\[
\mathcal C=\{(p_i,n_i,f_i)\}_{i=1}^m.
\]

接触图本身可能比 joint vector 更接近任务结构。

---

## 33.13 Visuo-Tactile Dexterity

视觉提供全局几何，触觉提供局部接触。

```text
vision: where / what
 tactile: whether contact / slip / force
```

融合可以多时间尺度：

- vision 10–30 Hz；
- tactile 100–1000 Hz；
- motor control 更高。

直接同步成单一 token sequence 可能浪费 tactile 高频信息。

---

## 33.14 Tactile Pretraining

触觉预训练可学习：

- contact embedding；
- slip；
- material；
- force proxy；
- deformation。

与视觉不同，触觉数据高度依赖 sensor geometry 和 material。

因此 tactile foundation model 需要面对严重的 sensor embodiment gap。

---

## 33.15 Predictive + Reactive Tactile Control

两层结构：

```text
slow predictive policy
→ target / action chunk
fast tactile reflex
→ residual correction
```

形式：

\[
a_t=a_t^{base}+\Delta a_t^{tactile}.
\]

它对应人类“计划动作 + 接触反射”的结构。

---

## 33.16 High-Frequency Tactile Residual Policy

高频 residual 特别适合：

- slip correction；
- insertion；
- grasp force regulation。

因为如果等一个 7 Hz VLM 重新推理，接触早已失效。

这再次说明 embodied intelligence 天然需要 multi-rate architecture。

---

## 33.17 Tactile Foundation Model

“Foundation”不能只看参数规模。真正应验证：

- cross-object；
- cross-task；
- cross-sensor；
- cross-hand；
- few-shot adaptation。

跨 tactile sensor 泛化比跨 camera 更困难，因为 sensor mechanics 本身改变 observation function。

---

## 33.18 Bimanual / Dexterous VLA

把 VLA 扩到双臂/灵巧手时，action dimension 急剧增长。

需要重新考虑：

- continuous vs token；
- chunk length；
- latency；
- relative frame；
- tactile input；
- hand-specific adapter。

2026 的 whole-body VLA 公开演示表明这一方向快速推进，但高维控制的独立可复现 benchmark 仍非常重要。

---

## 33.19 灵巧操作离人类水平还差什么

主要差距包括：

- tactile bandwidth；
- compliant mechanics；
- rich contact prior；
- long-term practice；
- fast reflex；
- hand morphology；
- recovery。

“会打一个结”不等于 general dexterity。

---

## 最小实验

在 zipper / insertion / in-hand rotation 上比较：

1. vision-only VLA；
2. vision+tactile 同频融合；
3. vision slow policy + tactile high-rate residual。

测 success、contact recovery、latency sensitivity。

---

## 本章结论

双臂与灵巧手把机器人从“轨迹生成”推向真正的**协调接触系统**。未来高水平 dexterity 很可能依赖：结构化双臂关系 + 多接触表示 + 高频触觉闭环，而不是单纯扩大视觉语言模型。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 33`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-33)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
