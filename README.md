# Embodied AI Development

# 《具身智能：从物理世界到通用机器人》
### *Embodied Intelligence: From Physical Principles to General-Purpose Robots*

> **v1.0 complete first-edition manuscript**  
> **Part 0–50 · 51 independent chapters · 12 volumes · frontier snapshot: 2026-09-14**

[![Minimal textbook code regression](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/minimal-code-regression.yml/badge.svg)](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/minimal-code-regression.yml)
[![Textbook QA](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/book-qa.yml/badge.svg)](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/book-qa.yml)
[![Website Build](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/site-build.yml/badge.svg)](https://github.com/Yukun-Zheng/Embodied-AI-development/actions/workflows/site-build.yml)

这是一个从第一性原理系统学习具身智能的开放教材工程。它不把具身智能等同于 `Transformer + Robot`，也不按热门模型排行榜组织知识，而是把**数学、物理、经典机器人学、控制、感知、状态估计、规划、模仿学习、强化学习、生成式策略、VLA、World Model、主动感知、触觉、双臂、人形、跨本体、持续学习、仿真、数据工程、系统部署、评测、安全与研究方法**放进同一个物理闭环。

核心问题只有一个：

> **一个智能体如何依靠身体，在真实或物理可信的世界中，通过感知、建模、预测、决策、控制、记忆、学习与持续交互，形成可泛化、可迁移、可恢复、可持续发展的智能？**

---

## Start Here

### 正文

- **[51 章正式主稿索引](book/chapters/README.md)** — Part 0–50，完整教材的唯一正文真源
- **[教材总入口](book/README.md)** — 阅读方式、12 卷结构与版本说明
- **[自动生成完整目录](book/TOC.md)** — 从 51 个 Chapter 的真实标题生成，避免目录漂移
- **[12 卷连续通读版](book/volumes/)** — 先建立全局框架，再进入逐 Part 深章
- **[36 周系统学习路线](book/SYLLABUS_36_WEEKS.md)** — 从基础到独立研究的一年课程
- **[知识依赖图](book/DEPENDENCY_GRAPH.md)** / **[概念索引](book/CONCEPT_INDEX.md)** — 支持跳读与按概念查找

### 数学、图、习题与实验

- **[30 组核心长推导](book/DERIVATIONS.md)** — shape → 公式 → 物理意义 → 代码变量
- **[204 道章末题](book/EXERCISES.md)** — 每个 Part: Concept / Math / Implementation / Research
- **[解题要点与验收标准](book/SOLUTION_SKETCHES.md)**
- **[18 张 canonical 核心机制图](figures/CORE_DIAGRAMS.md)** — 统一物理对象、数据流与时间尺度的视觉语言
- **[最小可执行代码](code/minimal/README.md)** — SE(3)、IK、控制、Kalman、DAgger、Diffusion/Flow、World Model+MPC 等
- **[40 Labs + 3 Capstones](labs/LABS.md)**
- **[统一实验协议](labs/EXPERIMENT_PROTOCOL.md)** — hypothesis、controls、seeds、raw logs、failure taxonomy、real-robot protocol

### 源码级学习

- **[7 篇 canonical Source-Level Case Studies](case-studies/README.md)**：
  - ACT / ALOHA
  - Diffusion Policy
  - OpenVLA
  - SmolVLA + LeRobot
  - GR00T N1.7
  - V-JEPA 2 / 2.1
  - World Model + Control
- **[Action Path Comparison](case-studies/ACTION_PATH_COMPARISON.md)** — discrete token / diffusion / flow / predictive latent 同轴比较
- **[Source-Code Atlas](references/SOURCE_CODE_ATLAS.md)** — 真实官方仓库、commit、训练入口、processor、loss、inference、deployment 的阅读地图

源码案例不做 paper summary，而是强制追踪：

```text
dataset
→ processor
→ tensor / shape
→ representation
→ loss
→ sampling / decoding
→ temporal executor
→ controller boundary
→ physical robot
```

### Research Atlas

- **[Model Atlas](references/MODEL_ATLAS.md)**
- **[Dataset Atlas](references/DATASET_ATLAS.md)**
- **[Robot / Hardware Atlas](references/HARDWARE_ATLAS.md)**
- **[Benchmark / Platform Atlas](references/BENCHMARK_ATLAS.md)**
- **[Failure Atlas](references/FAILURE_ATLAS.md)**
- **[Model × Data × Hardware × Benchmark Matrix](references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md)**
- **[1948–2026 技术时间线](references/TIMELINE.md)**
- **[逐 Part Reading Map](references/READING_MAP.md)**
- **[统一 References](references/REFERENCES.md)** / **[BibTeX](references/BIBLIOGRAPHY.bib)**
- **[A–Z 附录](book/APPENDICES.md)** / **[中英术语表](book/GLOSSARY.md)** / **[符号与约定](book/NOTATION_AND_CONVENTIONS.md)**

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
| IX | 基础设施与部署 | Simulation、Sim2Real、Robot Data、ROS / Real-Time System |
| X | Evaluation & Safety | Benchmark、Reliability、Physical / Agentic Safety |
| XI | 研究方法与下一代架构 | Mechanism Research、Post-Transformer、数学化具身智能、Open Problems |

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

本书所有技术都必须能回答自己在这张图中的位置。模型名字会变化，但闭环中的**物理量、坐标系、信息流、时间关系、控制接口与失败机制**不会因为热点改变。

---

# 为什么从经典机器人学开始

如果只学 VLA，读者可能知道 π、GR00T、Gemini Robotics，却不知道

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
- action chunking、Real-Time Chunking、asynchronous inference 与 latency；
- RT-1 / RT-2 / Open X-Embodiment / Octo / OpenVLA；
- π0 / FAST / π0.5 / π*0.6 / embodied memory / π0.7；
- **GR00T N1 / N1.5 / N1.6 / N1.7**；
- Gemini Robotics / Robotics 2 / On-Device 2；
- Figure Helix / Helix 02 与 human-video scaling；
- V-JEPA 2 / 2.1、action-conditioned predictive models；
- world foundation models / World Action Models / neural simulators；
- tactile foundation models 与 high-frequency tactile feedback；
- whole-body humanoid、loco-manipulation、multi-robot collaboration；
- cross-embodiment、continual / developmental learning；
- autonomous experience learning、self-evolving architecture；
- uncertainty、human intervention 与 reliable deployment。

GR00T N1.6 / N1.7 的日期按官方 GitHub release 校正为 **2026-04-15 / 2026-04-18**。N1.7 还进入了源码层：教材直接追踪 processor、embodiment tags、state/action projector、DiT、flow integration、RTC 与 deployment runtime。

这些系统作为**历史节点、案例和可检验机制**进入教材，而不是反过来用品牌名组织整本书。

---

# 每章统一学习标准

每个主题最终要达到四级：

1. **Concept** — 能解释问题为什么存在；
2. **Mathematics** — 能写出对象、方程、假设、shape；
3. **Implementation** — 能在最小环境中从头实现；
4. **Research** — 能设计 negative control、发现 failure、质疑 claim。

博士级掌握的目标是 L4。读任何方法都应强制回答：

1. observation 是什么？单位、frame、shape 是什么？
2. action 最终控制什么物理量？
3. 中间 state / representation / memory 是什么？
4. policy、planner、executor、controller 如何分工？
5. frequency / latency / horizon 是多少？
6. 训练数据来自哪里？
7. failure mode 是什么？
8. 什么负对照能推翻其机制解释？

---

# 实验与证据标准

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

统一要求 raw logs、config、seed、failure cases、negative controls、confidence interval 和 reproducible figures。模型结果必须展开成：

\[
\text{Model}\times\text{Data}\times\text{Embodiment}\times\text{Executor/Controller}\times\text{Benchmark}\times\text{Protocol}.
\]

否则不把一个 success rate 当成可迁移的科学结论。

---

# 出版与工程质量

教材源文件仍按科研工作流组织；正式 Web build 使用 **MkDocs Material + MathJax + Mermaid** 生成 disposable publication view：

```text
canonical manuscript
      ↓
scripts/prepare_site.py
      ↓
.site-src/ + chapter-driven .site-mkdocs.yml
      ↓
MkDocs / Material
      ↓
MathJax formulas + Mermaid diagrams + searchable navigation
```

网站左侧导航与 `book/TOC.md` 都从 51 个 Chapter 的真实标题派生，避免平行目录长期漂移。

当前自动回归覆盖三层：

- **Minimal code regression** — 最小数学/机器人代码；
- **Textbook QA** — Part 0–50 连续性、TOC、关键资产与本地 Markdown 链接；
- **Website Build** — publication staging、MathJax/Mermaid 构建、Part 0/24/50 与关键源码案例 smoke test。

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
├── mkdocs.yml
├── book/
│   ├── README.md
│   ├── TOC.md                  # chapter-driven generated TOC
│   ├── SYLLABUS_36_WEEKS.md
│   ├── CONCEPT_INDEX.md
│   ├── DEPENDENCY_GRAPH.md
│   ├── NOTATION_AND_CONVENTIONS.md
│   ├── DERIVATIONS.md
│   ├── EXERCISES.md
│   ├── SOLUTION_SKETCHES.md
│   ├── APPENDICES.md
│   ├── GLOSSARY.md
│   ├── chapters/               # Part 0–50 canonical manuscripts
│   └── volumes/                # 12 volume continuous reading views
├── figures/
│   └── CORE_DIAGRAMS.md
├── code/
│   └── minimal/
├── case-studies/               # 7 canonical source/mechanism deep dives
├── labs/
│   ├── LABS.md
│   └── EXPERIMENT_PROTOCOL.md
├── references/
│   ├── SOURCE_CODE_ATLAS.md
│   ├── MODEL_ATLAS.md
│   ├── DATASET_ATLAS.md
│   ├── HARDWARE_ATLAS.md
│   ├── BENCHMARK_ATLAS.md
│   ├── FAILURE_ATLAS.md
│   ├── MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md
│   ├── TIMELINE.md
│   ├── READING_MAP.md
│   ├── REFERENCES.md
│   └── BIBLIOGRAPHY.bib
├── scripts/                     # TOC / QA / publication generators
└── .github/workflows/           # code / book / website regressions
```

---

# 当前版本状态

- Part 0–50：**51 个独立 Chapter**；
- **12** 个 Volume 连续通读版；
- **204** 道章末题 + solution sketches；
- **30** 组核心长推导；
- **18** 张 canonical 核心机制图；
- **10** 个最小可执行脚本；
- **7** 篇 canonical 深度 Case Study + **1** 份 Action Path Comparison；
- Source-Code Atlas：ACT / Diffusion Policy / OpenVLA / LeRobot / GR00T N1.7 / V-JEPA 2/2.1；
- **40 Labs + 3 Capstones** + 统一实验协议；
- **36 周**系统课程；
- Notation / Concept Index / Dependency Graph；
- Model / Dataset / Hardware / Benchmark / Failure Atlas + cross-matrix；
- References / Reading Map / BibTeX / 1948–2026 Timeline；
- chapter-driven TOC + chapter-driven website navigation；
- minimal-code / textbook-QA / website-build 三层 CI；
- 统一前沿时间截面：**2026-09-14**。

v1.x 将继续重点推进：**逐章 primary-source citations、simulator-level executable labs、真实/仿真实验结果回填、更多源码级解剖、跨章交叉引用与出版编辑**。

---

**长期目标：让读者从第一性原理出发，最终能够独立理解、实现、质疑并推进具身智能。**
