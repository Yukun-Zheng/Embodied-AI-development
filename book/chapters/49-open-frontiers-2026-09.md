# Part 49　开放问题：截至 2026-09 的真正前沿

> 时间截面：2026-09-14。本章故意不按公司或模型组织，而按尚未解决的科学问题组织。

## 49.1 Robust Open-World Generalization

今天的模型已经能在部分新对象、新指令上泛化，但真正 open world 要同时面对：

\[
OOD_{object}+OOD_{scene}+OOD_{task}+OOD_{physics}+OOD_{embodiment}.
\]

目前仍缺统一证据表明一个系统能在这些维度同时可靠泛化。

---

## 49.2 Long-Horizon Autonomy

瓶颈逐渐从“单个 skill 做不会”转向：

- memory；
- progress；
- recovery；
- task decomposition；
- repeated failure。

十分钟、小时级 autonomy 会成为比单动作 benchmark 更重要的测试。

---

## 49.3 Reliable Dexterity

灵巧手 demo 已快速进步，但可靠性仍受：

- tactile；
- contact model；
- finger calibration；
- high-frequency control；
- wear。

“能做一次”与“每天做一万次”之间仍有巨大鸿沟。

---

## 49.4 Contact-Rich Intelligence

视觉 foundation model 在自由空间运动上有优势，但接触仍是物理智能 hardest regime。

需要把：

- force；
- tactile；
- compliance；
- friction；
- contact mode

变成基础模型的一等公民。

---

## 49.5 Real-Time Foundation Policy

模型规模继续增加，而控制系统要求低 latency。

核心问题：

\[
\text{semantic capacity}\uparrow
\quad while\quad
T_{loop}\downarrow.
\]

multi-rate、async、distillation、on-device 都是路线，但还没有终极解。

---

## 49.6 Embodied Memory

2026 已出现明确 long/short-term memory 工作，但开放问题包括：

- what to store；
- cross-day memory；
- privacy；
- forgetting；
- memory corruption。

---

## 49.7 Learning from Experience

从 demonstration-only 走向 RL / deployment learning 已成为明确趋势。

仍缺：

- safe autonomous practice；
- automatic reward；
- low-cost reset；
- stable lifelong update。

---

## 49.8 Cross-Embodiment Transfer

真正挑战是未见 body。

如果每个新 robot 都需要数十小时 data + adapter，foundation model 仍不是 universal controller。

---

## 49.9 Whole-Body Intelligence

2026 whole-body VLA / humanoid control 快速推进。

开放问题：

- balance 与 semantics 如何统一；
- moving camera 下 perception；
- fall recovery；
- whole-body tactile；
- energy。

---

## 49.10 World Model that Actually Helps Control

最重要问题仍是：

> 有没有 world model 在严格控制变量下，持续显著提高真实机器人控制？

视频预测变强不等于此问题已经解决。

---

## 49.11 Active Perception

机器人模型大多仍默认 camera 给什么就看什么。

真正 embodied agent 应主动改变：

- viewpoint；
- touch；
- object configuration

以获取任务信息。

---

## 49.12 Data Efficiency

真实 robot-hours 是稀缺资源。

未来 scaling 不可能永远依赖同等比例扩大人工 teleop。

需要 human video、simulation、autonomous experience、better priors。

---

## 49.13 Autonomous Data Flywheel

真正 scalable flywheel：

```text
deploy
→ detect uncertainty/failure
→ autonomous practice
→ auto-evaluate
→ improve
```

今天很多流程仍需大量人工筛选。

---

## 49.14 Continual / Developmental Learning

机器人长期运行后是否会越用越强，而不是只积累日志？

这个问题尚未被 foundation model scaling 自动解决。

---

## 49.15 Structural Plasticity

模型能否根据新 mechanism 改变自身计算结构，而不是只更新 fixed tensor weights？

这是发展型智能最基础又最开放的问题之一。

---

## 49.16 Self-Evolving Architecture

“self-evolving”需要科学定义：

- autonomous growth；
- retention；
- transfer；
- resource efficiency；
- safety。

目前远未形成成熟范式。

---

## 49.17 Causal Physical Reasoning

模型是否知道：

> 因为摩擦变低，所以这个抓法会滑。

而不是只记住某纹理对应某动作。

需要 intervention-based benchmark。

---

## 49.18 Multi-Robot Intelligence

多机器人 foundation model 已有重要公开演示，但真正开放问题是：

- decentralized coordination；
- new partner generalization；
- heterogeneous embodiment；
- shared memory；
- emergent role allocation。

---

## 49.19 Safety under Continual Adaptation

静态模型 safety 已经困难，自我更新机器人更难。

必须保证：

\[
SafetyInvariant(\theta_t),\quad\forall t.
\]

如何证明仍是重大开放问题。

---

## 49.20 Sim-to-Real at Foundation-Model Scale

foundation model 训练同时混合 web、sim、real。

新的问题不再只是单 policy sim2real，而是：

> 不同数据源在大模型中怎样相互影响，synthetic bias 会不会被规模化放大？

---

## 49.21 Hardware–Intelligence Co-Design

未来身体可能不应只是固定平台。

需要共同设计：

- sensor；
- actuator；
- compliance；
- tactile skin；
- compute；
- learned policy。

好的 morphology 本身可以降低智能计算难度。

---

## 49.22 General-Purpose Humanoid 是终局吗

人形的优势：人类环境兼容。

但代价：

- high DoF；
- balance；
- energy；
- complexity。

某些任务中专用 morphology 可能永远更优。

所以“通用智能”不必等于“唯一通用身体”。

---

## 49.23 是否需要新的计算范式

如果未来仍有：

- fixed weights；
- fixed context；
- offline training；
- token-centric representation，

可能难以实现长期发展型 agent。

值得研究：

- persistent state；
- structural plasticity；
- mechanism-based computation；
- event-driven / continuous-time systems。

---

## 49.24 什么才算“理解了物理世界”

本书建议最低标准不是会回答物理题，而是：

1. 能在 intervention 下预测；
2. 能选择导致目标 effect 的动作；
3. 能把规律迁移到新对象/身体；
4. 能从预测错误中更新。

即：

\[
Understanding\Rightarrow Predict+Intervene+Transfer+Revise.
\]

---

## 49.25 距离真正通用智能还有什么

机器人需要同时做到：

- broad semantic understanding；
- accurate physical control；
- lifelong memory；
- autonomous learning；
- robust transfer；
- safe self-improvement。

2026 的系统已经分别触及这些能力，但尚未有公开证据表明它们被统一成一个长期自主、可靠、可持续学习的实体智能体。

---

## 本章结论

截至 2026-09，具身智能的主要矛盾正在从“能不能生成机器人动作”转向：**动作是否可靠、是否理解物理、是否能长期记忆和继续学习、是否跨身体迁移，以及能否在真实世界安全地持续存在。** 这些才是下一阶段值得长期追的问题。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 49`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-49)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
