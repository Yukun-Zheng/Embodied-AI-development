# 《具身智能：从物理世界到通用机器人》
## Embodied Intelligence: From Physical Principles to General-Purpose Robots

**v1.0 complete manuscript · frontier frozen at 2026-09-14**

这不是按热门模型堆砌的论文综述，而是一套从数学、物理与机器人学出发，一直通向 2026 年机器人基础模型、world model、人形、持续学习与下一代架构的系统教材。

---

# 阅读入口

- [完整目录 TOC](./TOC.md)
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
- [A–Z 附录](./APPENDICES.md)
- [中英术语表](./GLOSSARY.md)
- [40 Labs + 3 Capstones](../labs/LABS.md)
- [统一参考文献与来源地图](../references/REFERENCES.md)

---

# 全书知识主线

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

本书所有章节都应该能挂回这张闭环图。

---

# 三条阅读路线

## 路线 A：第一次系统学习具身智能

建议按顺序：

```text
Volume 0
→ I 数学
→ II 经典机器人学
→ III 感知/状态
→ IV Robot Learning
→ V VLA
→ VI World Model/Memory
→ VII 能力层
→ IX 系统工程
→ X Evaluation/Safety
→ VIII Continual/Cross-Embodiment
→ XI Research Frontier
```

不要从 π0 / Gemini Robotics 直接开始；否则会认识模型名字，却不知道 action 最后怎样穿过 IK、controller、actuator 与 contact 进入物理世界。

## 路线 B：已经会深度学习，转具身研究

重点补：

```text
Volume II → Volume III → Volume IV
```

然后读：

```text
Volume V → VI → IX → X → XI
```

这条路线专门纠正“VLM + action head = robotics”的知识断层。

## 路线 C：已经做机器人，希望进入 Foundation Model

可跳过熟悉的基础，但至少快速检查：

```text
Volume I flow matching / probability
Volume IV generative policy
Volume V VLA lineage + internals
Volume VI world model / memory / experience
Volume VIII cross-embodiment
Volume X eval / safety
Volume XI frontier
```

---

# 学习层级

每一部分建议达到四级：

### L1 — Concept
能用自己的话解释概念、为什么需要它。

### L2 — Mathematics
能写出核心状态、方程、假设与 shape。

### L3 — Implementation
能在最小环境中从头实现，而不是只调用框架。

### L4 — Research
能设计 negative control、找到失败边界、质疑论文 claim。

真正博士级掌握应达到 L4。

---

# 章节使用方法

读任何算法都强制回答：

1. 真实问题是什么？
2. 输入是什么？单位/frame/shape 是什么？
3. 输出是什么？
4. 中间状态表示什么？
5. 假设了什么？
6. action 怎样真正执行？
7. feedback 在哪里？
8. latency / frequency 是多少？
9. 失败模式是什么？
10. 如何用最小实验推翻其核心 claim？

这十问是本书统一学习模板。

---

# 实验配套

`labs/LABS.md` 提供：

- 40 个逐级实验；
- 从 Jacobian / SE(3) 到 VLA / World Model；
- 从 Push-T 到 humanoid / multi-robot；
- 统一 failure log / reproducibility 规范；
- 3 个最终 Capstone。

最终目标不是“完成教程”，而是能独立提出一个可证伪的新架构。

---

# 版本语义

本版正文的前沿时间截面为：

> **2026-09-14**

稳定知识（数学、机器人学、控制等）应尽量长期不变；动态技术（VLA / World Model / Humanoid / Safety）通过附录 Atlas 和参考文献持续更新。

**新模型默认不新增一级章节。** 它必须先回答自己属于哪条既有知识链；只有出现真正的新数学对象、系统接口或独立范式时，才调整全书骨架。

---

# 当前定位

v1.0 已经形成从头到尾连续可读的完整 manuscript，并配套实验、附录、术语和来源体系。

后续版本不是“继续补空白章节”，而主要做四类升级：

1. **Depth pass**：把重点 Part 扩成更长的独立 Chapter；
2. **Figure pass**：补原创系统图、矩阵图、数据流图；
3. **Code pass**：为 Labs 增加可执行代码；
4. **Evidence pass**：逐章扩充 BibTeX、实验结果、原始论文引用。

这意味着从 v1.0 开始，项目已经从“搭教材”进入“不断提高教材深度”的阶段。
