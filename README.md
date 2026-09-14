# Embodied AI Development

# 《具身智能：从物理世界到通用机器人》
### *Embodied Intelligence: From Physical Principles to General-Purpose Robots*

> **v1.0 Complete Manuscript**  
> **Knowledge frontier frozen at 2026-09-14**

这是一个从第一性原理系统学习具身智能的开放教材工程。它不把具身智能等同于 `Transformer + Robot`，也不以热门模型排行榜组织知识，而是把**数学、物理、机器人学、控制、感知、状态估计、规划、模仿学习、强化学习、生成式策略、VLA、World Model、主动感知、触觉、双臂、人形、跨本体、持续学习、仿真、数据工程、系统部署、评测、安全与研究方法**放进同一个物理闭环。

核心问题只有一个：

> **一个智能体如何依靠身体，在真实或物理可信的世界中，通过感知、建模、预测、决策、控制、记忆、学习与持续交互，形成可泛化、可迁移、可恢复、可持续发展的智能？**

---

## Start Here

- **[教材阅读入口](book/README.md)** — 11 卷正文、阅读路线与学习层级
- **[完整总目录](book/TOC.md)** — Part 0–50 + Appendix A–Z
- **[40 个 Labs + 3 个 Capstones](labs/LABS.md)** — 从 Jacobian 到 VLA / World Model / Humanoid
- **[A–Z 附录](book/APPENDICES.md)** — 公式、系统、平台、论文/模型 Atlas、Checklists
- **[中英术语表](book/GLOSSARY.md)**
- **[统一参考文献与 Source Map](references/REFERENCES.md)** — 经典基础到 2026-09-14
- **[写作与证据规范](AUTHORING_GUIDE.md)**
- **[全书工程设计](BOOK_PLAN.md)**

---

# 全书正文

| Volume | 主题 | 文件 |
|---|---|---|
| 0 | 导论：具身智能定义与技术史 | [Volume 0](book/volumes/00-introduction.md) |
| I | 数学与计算语言 | [Volume I](book/volumes/01-mathematics.md) |
| II | 身体、SE(3)、运动学、动力学、控制、规划 | [Volume II](book/volumes/02-robotics-foundations.md) |
| III | 感知、3D/4D、状态估计、触觉、主动感知 | [Volume III](book/volumes/03-perception-state.md) |
| IV | Imitation / RL / Generative Robot Policy | [Volume IV](book/volumes/04-robot-learning.md) |
| V | VLM → VLA → Robot Foundation Models | [Volume V](book/volumes/05-foundation-models.md) |
| VI | Reasoning、Memory、Experience、World Models | [Volume VI](book/volumes/06-reasoning-world-models.md) |
| VII | Manipulation、Bimanual、Dexterity、Navigation、Humanoid、Multi-Robot | [Volume VII](book/volumes/07-capabilities-humanoids.md) |
| VIII | Cross-Embodiment、Continual、Developmental、Self-Evolving Intelligence | [Volume VIII](book/volumes/08-cross-embodiment-developmental.md) |
| IX | Simulation、Synthetic Data、Robot Data、真实系统部署 | [Volume IX](book/volumes/09-simulation-data-systems.md) |
| X | Benchmark、Reliability、Physical/Agentic Safety | [Volume X](book/volumes/10-evaluation-safety.md) |
| XI | Research Method、数学化具身智能、Post-Transformer、Open Problems | [Volume XI](book/volumes/11-research-frontiers.md) |

---

# 全书统一闭环

```text
                    ┌──────────── Memory / Experience ────────────┐
                    │                                              │
Physical World → Sensors → Observation → State / Belief / Representation
      ↑                                      │
      │                                      ↓
      │                            Prediction / World Model
      │                                      ↓
      │                           Reasoning / Planning / Policy
      │                                      ↓
      │                              Action Representation
      │                                      ↓
      │                        IK / WBC / Controller / Safety
      │                                      ↓
      └────── Body / Actuator ← Physical Action ←─────────────────┘
                                             │
                                      Evaluation / Failure
                                             │
                                      Learning / Development
                                             ↺
```

本书所有技术都必须能回答自己在这张图中的位置。模型名字会变化，但闭环中的信息、物理和时间关系不会因为热点改变。

---

# 为什么这本书从经典机器人学开始

如果只学 VLA，读者可能知道 π、GR00T、Gemini Robotics，却不知道：

\[
q,\ \dot q,\ \tau,\ SE(3),\ J(q),\ M(q),\ \text{impedance},\ \text{contact},\ \text{latency}
\]

究竟如何决定一条 action 能不能在现实中执行。

因此教材坚持：

```text
Mathematics
→ Physical Body
→ Geometry / Kinematics / Dynamics
→ Feedback Control / Planning
→ Perception / State Estimation
→ Robot Learning
→ Foundation Models
→ World Models / Reasoning / Memory
→ Whole-Body / Cross-Embodiment
→ Continual Development
→ Reliable Real Systems
```

而不是：

```text
LLM → VLM → VLA → “懂机器人”
```

---

# v1.0 覆盖的 2026 前沿

截至 **2026-09-14**，教材框架已经纳入并统一讨论：

- action tokenization / Diffusion / Flow Matching / Real-Time Action Chunking；
- RT-1 / RT-2 / Open X-Embodiment / Octo / OpenVLA；
- π0 / FAST / π0.5 / π*0.6 / embodied memory / π0.7；
- GR00T N1 / N1.5 / N1.6；
- Gemini Robotics / 1.5 / Robotics 2 / On-Device 2；
- Figure Helix 与 human-video scaling；
- V-JEPA 2 / 2.1、action-conditioned predictive models；
- World Action Models、robot-factored world models、world-model executability；
- tactile foundation models 与 high-frequency tactile feedback；
- whole-body humanoid、loco-manipulation、multi-robot collaboration；
- cross-embodiment、continual / developmental learning；
- agentic robotics safety / uncertainty-driven intervention。

这些模型进入**知识框架**而不是反过来决定章节结构。

---

# 每个主题的学习标准

不是“读过”，而是达到四级：

1. **Concept** — 能解释问题为什么存在；
2. **Mathematics** — 能写出对象、方程、假设、shape；
3. **Implementation** — 能在最小环境从头实现；
4. **Research** — 能设计 negative control、发现 failure、质疑 claim。

全书最终目标是 L4。

---

# 实验体系

[`labs/LABS.md`](labs/LABS.md) 给出 40 个渐进实验与 3 个 Capstone：

```text
Jacobian / SE(3)
→ FK / IK / Dynamics / Control
→ Camera / State Estimation / Active Perception
→ BC / DAgger / PPO / ACT
→ Diffusion / Flow Policy
→ VLA
→ Memory / World Model
→ Cross-Embodiment / Continual Learning
→ Humanoid / Multi-Robot
→ Real-Time Deployment / Safety
→ Falsifiable New Architecture
```

实验统一要求 raw logs、config、seed、failure cases、negative controls 和 reproducible figures。

---

# 科学立场

本书反复坚持：

- **能生成动作 ≠ 理解物理世界。**
- **语言解释得通 ≠ reasoning 对行为有因果作用。**
- **视频生成得真实 ≠ world model 可用于控制。**
- **一个 checkpoint 控多个已见 robot ≠ 强 cross-embodiment。**
- **更多数据带来提升 ≠ 新架构本身有效。**
- **一次成功 demo ≠ reliable robot system。**
- **类脑比喻 ≠ 计算机制。**
- **Transformer 很强 ≠ 所有具身问题都应被 token 化。**

任何重要 claim 最终都应该变成可证伪实验。

---

# 仓库结构

```text
Embodied-AI-development/
├── README.md
├── BOOK_PLAN.md
├── AUTHORING_GUIDE.md
├── book/
│   ├── README.md
│   ├── TOC.md
│   ├── APPENDICES.md
│   ├── GLOSSARY.md
│   ├── volumes/
│   │   ├── 00-introduction.md
│   │   ├── 01-mathematics.md
│   │   ├── 02-robotics-foundations.md
│   │   ├── 03-perception-state.md
│   │   ├── 04-robot-learning.md
│   │   ├── 05-foundation-models.md
│   │   ├── 06-reasoning-world-models.md
│   │   ├── 07-capabilities-humanoids.md
│   │   ├── 08-cross-embodiment-developmental.md
│   │   ├── 09-simulation-data-systems.md
│   │   ├── 10-evaluation-safety.md
│   │   └── 11-research-frontiers.md
│   └── 00-preface/
├── labs/
│   └── LABS.md
└── references/
    └── REFERENCES.md
```

后续 `figures/`、`code/`、`simulations/`、`datasets/`、`benchmarks/` 会承载 v1.x 的图、代码与实际可执行实验，而不是制造空目录。

---

# 版本状态

**v1.0 已完成全书第一版完整 manuscript。**

这里的“完成”表示：知识骨架已经冻结、11 卷正文连续可读、Part 0–50 均有对应内容、A–Z 附录存在、实验体系与参考来源已经建立。

它不表示教材停止发展。接下来的 v1.x 主要是**深化而不是补空白**：

- 将重点 Part 扩成更长的独立 Chapter；
- 增加原创系统图、矩阵图、坐标系图和训练/推理数据流图；
- 为 40 Labs 补完整可执行代码；
- 增加 BibTeX、逐段 citation 与论文精读页；
- 用真实实验结果持续校正教材中的判断；
- 随前沿进展更新 Atlas，而不让主目录随热点漂移。

---

**长期目标：让读者从第一性原理出发，最终能够独立理解、实现、质疑并推进具身智能。**
