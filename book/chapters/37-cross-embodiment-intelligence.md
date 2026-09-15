# Part 37　Cross-Embodiment Intelligence

## 37.1 Embodiment 到底包含什么

Embodiment 不是 robot name。

可写成：

\[
e=(G_{body},S,A,D,C),
\]

其中：

- \(G_{body}\)：身体拓扑；
- \(S\)：sensor configuration；
- \(A\)：actuator/action interface；
- \(D\)：dynamics；
- \(C\)：control constraints。

跨本体学习就是在这些量变化时保持能力。

---

## 37.2 Morphology

身体可表示为 graph：

\[
G=(V,E).
\]

节点属性：

- link geometry；
- mass；
- joint type；
- actuator；
- sensor。

边表示 kinematic connection。

这比固定长度 joint vector 更自然。

---

## 37.3 Sensor Configuration

两个机器人即使手臂相似，也可能拥有：

- 不同 camera 数量；
- 不同视角；
- tactile / no tactile；
- 不同 proprioception。

因此跨本体不仅是 action adaptation，也是 observation adaptation。

---

## 37.4 Action Topology

不同机器人：

\[
\mathcal A_i\neq\mathcal A_j.
\]

例如：

- 7-DoF arm；
- 6-DoF arm；
- bimanual；
- humanoid whole-body。

简单 padding 到同一维度不会自动产生 semantic alignment。

---

## 37.5 Embodiment Descriptor / Token

最简单方式是 robot ID embedding：

\[
z_e=Embedding(id).
\]

但对 unseen robot 无法泛化。

更结构化方式：

\[
z_e=f(G_{body},limits,sensors,kinematics).
\]

才能让模型根据身体属性组合推理。

---

## 37.6 Morphology-Conditioned Policy

\[
\pi(a\mid o,g,e).
\]

训练时随机不同 embodiment，模型学习：

> 在这个身体上，怎样实现相同任务 effect？

真正 test 应包含未见 morphology，而不是只在训练机器人之间切换。

---

## 37.7 Robot-Agnostic Representation

共享表示应尽量描述任务而非关节：

- object state；
- end-effector effect；
- contact relation；
- subgoal；
- spatial relation。

例如：

\[
\text{move cup from A to B}
\]

对机械臂、人形都成立。

---

## 37.8 Universal Action Representation

候选 universal action：

### End-effector delta

跨不同 arm 容易，但不适合 locomotion。

### Keypoint target

对 hand/body 结构更灵活，但需要低层 retargeter。

### Object-centric effect

最抽象，但需要 planning/controller 转换。

### Latent skill

可学习，但语义难解释。

没有单一表示在所有 embodiment 上最优。

---

## 37.9 Skill Space / Latent Action Space

共享 latent：

\[
z_{skill}\sim\pi_H(o,g),
\]

每个机器人 decoder：

\[
a^{(i)}=D_i(z_{skill},s^{(i)}).
\]

这把“任务语义”和“身体执行”分开。

缺点是 decoder 可能成为隐藏的 robot-specific policy，导致所谓 universal core 实际并不 universal。

---

## 37.10 Cross-Robot Transfer

迁移可以发生在：

- perception；
- representation；
- skill；
- policy；
- motion prior；
- world model。

必须明确论文声称的是哪一级。

一个共享 visual encoder 不能被称为完整 cross-embodiment control。

---

## 37.11 Zero / Few-Shot Embodiment Transfer

真正严格的 zero-shot：

\[
D_{new\ embodiment}=\varnothing.
\]

few-shot 则必须报告：

- 数据条数/小时；
- 是否需要 teleop；
- 调哪些参数；
- 是否任务也新。

2026 的 Gemini Robotics On-Device 2 等公开系统把 few-hour adaptation 作为重要能力，但科学比较需要统一适配预算。

---

## 37.12 Motion Transfer

共享 high-level motion：

\[
M^*=\arg\min_M \mathcal L_{effect}+\lambda\mathcal L_{feasible}(e).
\]

不同 robot 对同一 effect 可以采用完全不同 motion。

所以 motion transfer 不应该追求 joint trajectory 相似，而应该追求 effect equivalence。

---

## 37.13 新身体的 Calibration / Adaptation

接入新 robot 的实际流程包括：

```text
robot description
→ sensor calibration
→ action normalization
→ workspace discovery
→ low-level controller validation
→ policy adaptation
→ safety validation
```

任何“plug-and-play cross embodiment”如果跳过这些工程步骤，都需要非常谨慎解读。

---

## 37.14 “一个 Checkpoint 控不同机器人”意味着什么

可能有三种不同情况：

1. backbone 相同，但每机器人有 head；
2. checkpoint 相同，但输入包含 robot ID / adapter；
3. 真正结构化理解 morphology 并直接适配。

这三种 generality 层级完全不同。

---

## 37.15 Cross-Embodiment 的真正上限

最强检验不是：

> “在 5 台训练过的机器人上都成功。”

而是：

- unseen kinematic chain；
- unseen sensor configuration；
- unseen actuator range；
- unseen body scale；
- same task effect；
- minimal adaptation。

如果能做到，才接近真正 body-general intelligence。

---

## 最小实验

训练 3 种 arm morphology，测试第 4 种未见 arm：

比较：

- robot ID；
- padded joint state；
- morphology graph；
- object-centric skill + embodiment decoder。

测 zero-shot 与 10/50/100 demonstrations few-shot curve。

---

## 本章结论

Cross-embodiment 的核心不是“支持很多机器人型号”，而是学习**任务中与身体无关的规律**，再利用具体 morphology、sensor 和 dynamics 把这些规律实例化为可执行行为。真正的跨本体能力必须在 unseen body 上被检验。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 37`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-37)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
