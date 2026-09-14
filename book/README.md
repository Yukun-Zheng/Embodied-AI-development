# 《具身智能：从物理世界到通用机器人》
## Embodied Intelligence: From Physical Principles to General-Purpose Robots

**v1.0 complete first-edition manuscript · frontier frozen at 2026-09-14**

本书从数学、物理、机器人学与控制出发，一直推到 2026 年的机器人基础模型、VLA、world model、embodied memory、experience learning、whole-body humanoid、cross-embodiment、continual/developmental learning 与下一代架构。

它不是模型排行榜，也不是把 `Transformer + Robot` 当成具身智能的全部。全书始终围绕同一个闭环问题：

```text
Physical World
     ↓
Body / Morphology / Actuator
     ↓
Sensors
     ↓
Observation
     ↓
State / Belief / Representation
     ↓
Prediction / World Model / Memory
     ↓
Reasoning / Planning / Policy
     ↓
Action Representation
     ↓
Kinematics / WBC / Controller / Safety
     ↓
Physical Action
     ↓
World Changes
     ↓
Evaluation / Failure / Experience
     ↓
Learning / Consolidation / Development
     ↺
```

---

# 阅读入口

## 1. 正式主稿：Part 0–50

**推荐从这里读。**

- [51 章点击式主稿索引](./chapters/README.md)
- [冻结版完整细粒度目录 TOC](./TOC.md)

`book/chapters/` 已覆盖 **Part 0–50 共 51 个独立章节**。每章围绕现实问题、数学对象、系统数据流、代表机制、失败模式、最小实验与可证伪研究问题展开。

## 2. 卷级连续通读版

如果想先看完整知识主线，再进入逐章细节，可读：

- [Volume 0：导论与技术史](./volumes/00-introduction.md)
- [Volume I：数学与计算语言](./volumes/01-mathematics.md)
- [Volume II：机器人身体、几何、力学与控制](./volumes/02-robotics-foundations.md)
- [Volume III：感知、状态与世界表示](./volumes/03-perception-state.md)
- [Volume IV：Robot Learning](./volumes/04-robot-learning.md)
- [Volume V：Robot Foundation Models / VLA](./volumes/05-foundation-models.md)
- [Volume VI：Reasoning、Memory、Experience 与 World Models](./volumes/06-reasoning-world-models.md)
- [Volume VII：操作、导航、灵巧与人形](./volumes/07-capabilities-humanoids.md)
- [Volume VIII：持续学习、跨本体与发展型智能](./volumes/08-cross-embodiment-developmental.md)
- [Volume IX：仿真、数据基础设施与系统工程](./volumes/09-simulation-data-systems.md)
- [Volume X：评测、可靠性与安全](./volumes/10-evaluation-safety.md)
- [Volume XI：研究方法、理论前沿与下一代具身智能](./volumes/11-research-frontiers.md)

## 3. 配套学习层

- [17 张全书核心机制图](./FIGURES.md)
- [204 道 Part 0–50 章末题](./EXERCISES.md)
- [204 题解题要点与验收标准](./SOLUTION_SKETCHES.md)
- [Part 0–50 原始教材 / 论文 / 官方来源地图](../references/READING_MAP.md)
- [A–Z 附录](./APPENDICES.md)
- [中英术语表](./GLOSSARY.md)
- [40 Labs + 3 Capstones](../labs/LABS.md)
- [统一参考文献与来源地图](../references/REFERENCES.md)
- [作者规范与证据标准](../AUTHORING_GUIDE.md)

---

# 全书 12 个 Volume

| Volume | 核心问题 |
|---|---|
| 0 | 什么是具身智能，它为什么与传统 AI 不同？ |
| I | 机器人世界需要哪些数学语言？ |
| II | 身体怎样运动、受力、控制与规划？ |
| III | 机器人怎样感知并维护世界状态？ |
| IV | 怎样从数据、示范和交互中学习动作？ |
| V | VLM 如何演化为 VLA / robotics foundation policy？ |
| VI | 机器人怎样推理、记忆、从经验继续学习并预测世界？ |
| VII | 操作、灵巧、导航与 whole-body humanoid 如何形成能力？ |
| VIII | 智能怎样跨身体、跨时间持续发展？ |
| IX | 仿真、数据和系统工程如何把算法变成真实机器人？ |
| X | 怎样科学评测，并让系统可靠、安全？ |
| XI | 怎样做严谨研究，以及下一代具身架构可能是什么？ |

---

# 三条阅读路线

## 路线 A：第一次系统学习具身智能

```text
Volume 0
→ I 数学
→ II 经典机器人学
→ III 感知/状态
→ IV Robot Learning
→ V VLA
→ VI World Model/Memory/Experience
→ VII 能力层
→ IX 系统工程
→ X Evaluation/Safety
→ VIII Continual/Cross-Embodiment
→ XI Research Frontier
```

不要从 π0、GR00T 或 Gemini Robotics 直接开始；否则很容易认识模型名字，却不知道 action 最终怎样穿过坐标变换、IK、controller、actuator 与 contact 进入物理世界。

## 路线 B：会深度学习，转具身研究

重点补：

```text
Volume II → III → IV
```

再读：

```text
Volume V → VI → IX → X → XI
```

## 路线 C：已有机器人基础，进入 Foundation Models

快速检查：

```text
Volume IV generative policy
→ V VLA lineage + internals
→ VI memory / experience / world model
→ VIII cross-embodiment
→ X eval / safety
→ XI frontier
```

---

# 每章统一学习标准

读任何方法都强制回答：

1. 真实问题是什么？
2. 输入是什么，单位 / frame / shape 是什么？
3. 输出是什么？
4. 中间状态表示什么？
5. 假设了什么？
6. action 怎样真正执行？
7. feedback 在哪里？
8. latency / frequency 是多少？
9. failure mode 是什么？
10. 什么最小实验能推翻核心 claim？

掌握层级分为：

```text
L1 Concept
→ L2 Mathematics
→ L3 Implementation
→ L4 Research / Falsification
```

博士级掌握的目标是 L4，而不是只会复述论文。

推荐每个 Part 完成一套四步闭环：

```text
读 Chapter
→ 追 READING_MAP 中 2–4 个原始来源
→ 做 EXERCISES 中 C/M/I/R 四题
→ 跑对应 Lab / negative control
```

---

# 当前完成度与版本语义

当前 `v1.0` 已包括：

- 完整知识骨架与冻结目录；
- Part 0–50 全部 51 个独立主章；
- 12 个 Volume 连续通读稿；
- 17 张可直接渲染的核心机制图；
- 204 道章末题 + 204 题解题要点；
- Part 0–50 原始来源阅读地图；
- A–Z 附录与术语表；
- 40 Labs + 3 Capstones；
- 2026-09-14 之前重要前沿的统一知识链。

这是一版**完整第一版 manuscript**，不是“最终出版物已经永远完成”。后续工作属于出版级增厚与验证：

1. **Derivation pass**：把高频公式扩成逐行、逐矩阵的长推导；
2. **Code/Lab pass**：把实验 protocol 扩成完整可执行实现；
3. **Evidence pass**：逐章 BibTeX、逐段 citation、复现实验结果；
4. **Figure pass 2**：把 Mermaid 机制图进一步做成出版级原创图；
5. **Editorial pass**：统一术语、交叉引用、索引与网站/出版排版。

因此下一阶段不是“补缺失章节”，而是把已经完整的第一版继续打磨成真正的大体量、图文并茂、实验可运行的长期教材。

---

# 时效性

前沿技术时间截面：

> **2026-09-14**

新模型默认进入既有 Part、案例或 Atlas。只有当它改变了“感知—状态—预测—决策—控制—学习”闭环中的基本数学对象或系统接口，才允许修改一级目录。