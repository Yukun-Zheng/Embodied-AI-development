# BOOK PLAN — 《具身智能：从物理世界到通用机器人》

> **Current status: v1.0 Complete Manuscript**  
> **Frontier cutoff: 2026-09-14**

## 0. 项目定位

这不是一部“机器人算法百科”，也不是一部“VLA 综述”。它的组织原则是：

> **从一个智能体如何进入物理世界、形成闭环、从交互中学习，再到跨任务、跨场景、跨本体和长期发展的通用物理智能。**

全书以

```text
World ↔ Body ↔ Sensors ↔ State ↔ Prediction ↔ Decision ↔ Control ↔ Action
                              ↕
                       Memory / Learning
```

为主轴，把经典机器人学与现代 foundation model 真正接起来。

---

# 1. v1.0 已完成的教材结构

正文已经形成 12 个 Volume 文件，对应总目录 Part 0–50：

```text
Volume 0   导论与技术史
Volume I   数学与计算语言
Volume II  身体、几何、运动学、动力学、控制、规划
Volume III 感知、3D/4D、状态估计、触觉、主动感知
Volume IV  Imitation / RL / Generative Robot Policy
Volume V   VLM → VLA → Robot Foundation Models
Volume VI  Reasoning / Memory / Experience / World Models
Volume VII Manipulation / Bimanual / Dexterity / Navigation / Humanoid
Volume VIII Cross-Embodiment / Continual / Developmental Intelligence
Volume IX  Simulation / Data / Systems / Deployment
Volume X   Evaluation / Reliability / Safety
Volume XI  Research Method / Mathematical Embodied AI / Open Frontiers
```

此外已经存在：

- 完整 `book/TOC.md`；
- `book/APPENDICES.md`：Appendix A–Z；
- `book/GLOSSARY.md`：中英术语统一；
- `labs/LABS.md`：40 个 Labs + 3 个 Capstones；
- `references/REFERENCES.md`：经典基础到 2026-09-14 的来源地图；
- `AUTHORING_GUIDE.md`：后续扩写的统一作者规范；
- `book/README.md`：正式阅读入口。

---

# 2. 全书知识图谱

```text
Mathematics
├─ Linear Algebra / Calculus
├─ Probability / Information
├─ Optimization
├─ Differential Equations
├─ Geometry / Lie Groups
├─ Dynamical Systems
└─ Causality
        ↓
Physics & Robotics
├─ Mechanism / Actuation
├─ Kinematics
├─ Dynamics / Contact
├─ Feedback / Optimal Control
└─ Planning / Whole-Body Control
        ↓
Perception & State
├─ RGB / Depth / 3D / 4D
├─ Proprioception / Force / Tactile
├─ State Estimation / SLAM
├─ Representation
├─ Uncertainty
└─ Active Perception
        ↓
Robot Learning
├─ Imitation
├─ Reinforcement Learning
├─ Offline / Online RL
├─ Action Chunking
├─ Diffusion / Flow / AR
└─ Experience Learning
        ↓
Foundation Physical Intelligence
├─ VLM / Grounding
├─ VLA
├─ Memory / Reasoning
├─ World Model / World Action Model
├─ Human-to-Robot
└─ Agentic Systems
        ↓
Capabilities
├─ Manipulation
├─ Bimanual / Dexterity
├─ Navigation / Mobile Manipulation
├─ Locomotion / Humanoid
├─ Whole-Body
└─ Multi-Robot / HRI
        ↓
Generality over a Lifetime
├─ Cross-Embodiment
├─ Continual Learning
├─ Developmental Robotics
├─ Structural Plasticity
└─ Self-Evolving Physical Intelligence
        ↓
Real Systems
├─ Simulation / Synthetic Data
├─ Sim-to-Real
├─ Data Engineering
├─ Real-Time Deployment
├─ Evaluation / Reliability
└─ Safety / Governance
```

---

# 3. 读者能力目标

## Level A — Concept

能解释：state / observation、pose / twist / wrench、action semantics、closed loop、partial observability、world model、VLA、embodiment 分别是什么。

## Level B — Mathematics

能推导和计算：

- SO(3) / SE(3)；
- FK / IK / Jacobian；
- rigid-body dynamics；
- Kalman / Bayes update；
- PID / impedance / LQR / MPC；
- Bellman equation；
- diffusion / flow action model 的基本数学。

## Level C — Implementation

能独立实现：

- 基础 perception / state estimation；
- planning / controller；
- BC / DAgger / PPO；
- ACT / Diffusion Policy / Flow Policy；
- 小型 VLA / world model；
- multi-rate deployment pipeline。

## Level D — Research

能：

- 从 failure mode 逆推假设；
- 区分 data gain / architecture gain；
- 设计 baseline / ablation / negative control；
- 检验 VLA 是否真正 generalize；
- 检验 world model 是否真正改善 control；
- 提出可证伪的新机制。

---

# 4. 教材工程标准

每个被进一步扩成独立 Chapter 的主题，至少包含：

1. 现实问题；
2. 物理直觉；
3. 系统图 / 数据流；
4. 数学形式化；
5. 算法；
6. tensor shape / frame / unit；
7. 最小代码；
8. 可运行实验；
9. failure modes；
10. 论文谱系；
11. negative controls；
12. open questions。

任何前沿模型 claim 必须区分：**论文/机构报告的结果** 与 **已经形成独立学术共识的结论**。

---

# 5. 版本定义

## v1.0 — Complete Manuscript（当前）

“完成”指：

- 全局知识依赖已经冻结；
- Part 0–50 都有正文覆盖；
- 从数学基础到 2026 前沿连续可读；
- A–Z 附录、术语、Labs 和参考来源齐备；
- 前沿部分有明确时间截面；
- 已没有依赖“以后再补某一整卷”才能成立的结构空洞。

**v1.0 不等于出版终稿，也不等于 40 个 Labs 已全部带可执行代码。** 当前 Labs 是完整实验设计与验收协议；代码化属于 v1.x 的下一层工程。

## v1.1 — Figure & Citation Pass

- 原创系统图；
- 坐标系图；
- matrix / tensor-shape 图；
- paper genealogy；
- 逐章更细 citation；
- BibTeX 数据库。

## v1.2 — Executable Lab Edition

- 为 40 Labs 增加代码；
- reproducible configs；
- automated tests；
- MuJoCo / SAPIEN / Isaac Lab 实验环境；
- benchmark adapters；
- CI 检查。

## v1.3 — Deep Chapter Pass

把核心 Part 拆成更长的独立 chapter，补：

- 完整推导；
- 逐行代码；
- case study；
- raw experiment results；
- exercises / solutions。

## v2.0 — Publication-Grade Edition

目标：

- 全书统一排版；
- 数百幅原创图；
- 可执行 companion code；
- 课程/习题/答案；
- PDF / website；
- 系统 bibliography；
- 外部技术审校。

---

# 6. 动态前沿维护规则

主目录不跟热点漂移。新模型默认进入：

- Appendix R：VLA / Foundation Model Atlas；
- Appendix S：World Model Atlas；
- Appendix T：Humanoid Atlas；
- Appendix U：Dexterity / Tactile Atlas；
- Appendix W：Open-Source Reproduction Index。

只有满足以下任一条件才改变一级知识结构：

1. 出现新的核心数学对象；
2. 出现新的系统接口；
3. 形成不可被现有章节自然容纳的独立计算范式；
4. 长期证据表明现有框架遗漏了一条基础能力链。

---

# 7. 长期质量目标

这套教材最终不是追求“页数最多”，而是追求四件事同时成立：

\[
\boxed{
\text{Mechanistic clarity}
+\text{Mathematical depth}
+\text{Executable evidence}
+\text{Frontier relevance}
}
\]

v1.0 解决完整性；v1.x 开始系统提高深度、图示、代码与证据密度。
