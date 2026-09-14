# Embodied AI Development

# 《具身智能：从物理世界到通用机器人》
### *Embodied Intelligence: From Physical Principles to General-Purpose Robots*

> **v1.0 Complete First-Edition Manuscript**  
> **Part 0–50 · 51 independent chapters · 12 volumes · frontier snapshot: 2026-09-14**

这是一个从第一性原理系统学习具身智能的开放教材工程。它不把具身智能等同于 `Transformer + Robot`，也不按热门模型排行榜组织知识，而是把**数学、物理、机器人学、控制、感知、状态估计、规划、模仿学习、强化学习、生成式策略、VLA、World Model、主动感知、触觉、双臂、人形、跨本体、持续学习、仿真、数据工程、系统部署、评测、安全与研究方法**放进同一个物理闭环。

核心问题只有一个：

> **一个智能体如何依靠身体，在真实或物理可信的世界中，通过感知、建模、预测、决策、控制、记忆、学习与持续交互，形成可泛化、可迁移、可恢复、可持续发展的智能？**

---

## Start Here

- **[51 章正式主稿索引](book/chapters/README.md)** — Part 0–50，推荐从这里进入完整教材
- **[教材总入口](book/README.md)** — 阅读路线、12 卷结构与版本说明
- **[冻结版完整目录](book/TOC.md)** — 细粒度知识树 + Appendix A–Z
- **[12 卷连续通读版](book/volumes/)** — 先看森林，再进入逐章主稿
- **[40 Labs + 3 Capstones](labs/LABS.md)** — 从 Jacobian 到 VLA / World Model / Humanoid
- **[A–Z 附录](book/APPENDICES.md)** — 公式、系统、平台、论文/模型 Atlas、Checklists
- **[中英术语表](book/GLOSSARY.md)**
- **[统一参考文献与 Source Map](references/REFERENCES.md)** — 经典基础到 2026-09-14
- **[写作与证据规范](AUTHORING_GUIDE.md)**
- **[全书工程设计](BOOK_PLAN.md)**

---

# 全书 12 个 Volume

| Volume | 主题 | 主线 |
|---|---|---|
| 0 | 导论与技术史 | 什么是具身智能，为什么物理闭环改变一切 |
| I | 数学与计算语言 | 线代、概率、优化、动态系统、几何、因果 |
| II | 机器人身体、几何、力学与控制 | 机电、SE(3)、运动学、动力学、控制、规划 |
| III | 感知、状态与世界表示 | 传感器、2D/3D/4D、SLAM、触觉、主动感知 |
| IV | Robot Learning | BC、DAgger、RL、Offline RL、Diffusion / Flow / AR Action |
| V | Robot Foundation Models | VLM → RT/Octo/OpenVLA → π/GR00T/Gemini/Helix |
| VI | VLA 之后 | Reasoning、Memory、Experience Learning、World Models |
| VII | 能力层 | Manipulation、Bimanual、Dexterity、Navigation、Humanoid、Multi-Robot |
| VIII | 长期发展 | Cross-Embodiment、Continual、Developmental、Self-Evolving Intelligence |
| IX | 基础设施与部署 | Simulation、Sim2Real、Robot Data、ROS/Real-Time System |
| X | Evaluation & Safety | Benchmark、Reliability、Physical/Agentic Safety |
| XI | 研究方法与下一代架构 | Mechanism Research、Post-Transformer、数学化具身智能、Open Problems |

卷级快速稿位于 [`book/volumes/`](book/volumes/)，逐 Part 深章位于 [`book/chapters/`](book/chapters/)。

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

# 为什么从经典机器人学开始

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

# 2026 前沿如何进入本书

截至 **2026-09-14**，主稿已经把以下问题纳入统一知识链：

- Diffusion / Flow Matching / autoregressive action / action tokenization；
- action chunking、Real-Time Action Chunking、asynchronous inference 与 latency；
- RT-1 / RT-2 / Open X-Embodiment / Octo / OpenVLA；
- π0 / FAST / π0.5 / π*0.6 / embodied memory / π0.7；
- GR00T N1 / N1.5 / N1.6；
- Gemini Robotics / Robotics 2 / On-Device 2；
- Figure Helix / Helix 02 与 human-video scaling；
- V-JEPA 2 / 2.1、action-conditioned predictive models；
- world foundation models / World Action Models / neural simulators；
- tactile foundation models 与 high-frequency tactile feedback；
- whole-body humanoid、loco-manipulation、multi-robot collaboration；
- cross-embodiment、continual / developmental learning；
- autonomous experience learning、self-evolving architecture；
- uncertainty、human intervention 与 reliable deployment。

它们作为**历史节点、案例和可检验机制**进入教材，而不是反过来用品牌名组织整本书。

---

# 每章统一学习标准

每个主题最终要达到四级：

1. **Concept** — 能解释问题为什么存在；
2. **Mathematics** — 能写出对象、方程、假设、shape；
3. **Implementation** — 能在最小环境中从头实现；
4. **Research** — 能设计 negative control、发现 failure、质疑 claim。

博士级掌握的目标是 L4。

读任何方法都应强制回答：

1. observation 是什么？单位、frame、shape 是什么？
2. action 最终控制什么物理量？
3. 中间 state / representation / memory 是什么？
4. policy、planner、controller 如何分工？
5. frequency / latency 是多少？
6. 训练数据来自哪里？
7. failure mode 是什么？
8. 什么负对照能推翻其机制解释？

---

# 实验体系

[`labs/LABS.md`](labs/LABS.md) 给出 **40 个渐进实验 + 3 个 Capstone**：

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

统一要求 raw logs、config、seed、failure cases、negative controls 和 reproducible figures。

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
│   ├── chapters/
│   │   ├── README.md
│   │   ├── 00-*.md
│   │   ├── ...
│   │   └── 50-*.md
│   └── volumes/
│       ├── 00-introduction.md
│       ├── ...
│       └── 11-research-frontiers.md
├── labs/
│   └── LABS.md
└── references/
    └── REFERENCES.md
```

---

# 版本状态

**v1.0 已完成全书第一版完整 manuscript。**

这里的“完成”表示：

- 知识骨架与 Part 0–50 已冻结；
- **51 个 Part 均已存在独立 Chapter 主稿**；
- 12 个 Volume 均有连续通读版；
- A–Z 附录、术语表、40 Labs + 3 Capstones、参考来源体系均已建立；
- 前沿时间截面统一为 2026-09-14。

它不表示教材停止发展。接下来的 v1.x 是**出版级增厚与验证**，不是继续补空白章节：

- 原创系统图、矩阵图、坐标系图、数据流图；
- 重点公式的逐步长推导与习题；
- Labs 的完整可执行代码与结果；
- BibTeX、逐段 citation、paper genealogy；
- 真机/仿真实验数据对教材判断的持续校正；
- 编辑、交叉引用、索引和出版排版。

---

**长期目标：让读者从第一性原理出发，最终能够独立理解、实现、质疑并推进具身智能。**