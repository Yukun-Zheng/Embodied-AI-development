# Embodied AI Development

> **《具身智能：从物理世界到通用机器人》**  
> *Embodied Intelligence: From the Physical World to General-Purpose Robots*

本仓库用于长期编写一部系统、可验证、可运行、持续更新的具身智能教材。目标不是做“论文列表”或“VLA 模型百科”，而是从第一性原理出发，把数学、物理、机器人学、控制、感知、状态估计、规划、学习、基础模型、世界模型、人形机器人、仿真、数据、系统工程与研究方法统一到同一个闭环框架中。

## 1. 核心问题

本书围绕一个问题展开：

> **一个智能体如何依靠身体，在真实或物理可信的世界中，通过感知、建模、决策、控制、学习与持续交互，形成可泛化、可迁移、可改进的智能？**

全书统一采用如下信息闭环：

```text
Physical World
    ↓
Sensors / Proprioception / Interaction
    ↓
Observation
    ↓
State / Representation / Belief
    ↓
Prediction / World Model
    ↓
Goal / Reasoning / Planning
    ↓
Policy / Controller
    ↓
Action / Torque / Command
    ↓
Robot Body
    ↓
Physical World
    ↺
```

因此，本书不会把“具身智能”简化为 `Transformer + Robot`，也不会从某个热门 VLA 模型直接开始。读者会先理解身体、坐标系、运动学、动力学、闭环控制和部分可观测性，再逐步进入 imitation learning、reinforcement learning、Diffusion Policy、VLA、world model、whole-body intelligence、cross-embodiment 与 continual learning。

## 2. 教材目标

目标读者可以从“会线性代数、概率、Python，但不熟悉机器人学”出发，最终达到：

- 能从物理和数学层面理解机器人状态、动作、约束和反馈；
- 能推导并实现 FK、IK、Jacobian、动力学与基础控制器；
- 能理解相机、深度、点云、触觉、本体感觉等输入如何进入策略；
- 能理解 BC、DAgger、RL、ACT、Diffusion Policy、Flow Matching、Autoregressive Action 等路线；
- 能系统理解 VLM → VLA → generalist robot policy 的技术演化；
- 能分析 world model、active perception、memory、reasoning 与 planning；
- 能独立使用 MuJoCo、SAPIEN、Isaac Sim / Isaac Lab 等平台构建实验；
- 能区分“模型性能提高”和“真正获得更强物理智能”；
- 能阅读、复现、批判前沿论文，并提出可证伪的新研究问题。

## 3. 本书不是怎样的书

本书不是：

- 热门模型排行榜；
- 只有概念、没有公式和代码的综述；
- 只有公式、没有真实系统数据流的经典机器人学教材替代品；
- 只会复现 benchmark 的教程；
- 把机器人当成 LLM 的输出设备；
- 把仿真中的 reward hacking 当成真正的智能；
- 把所有问题都归结为扩大 Transformer。

## 4. 每章统一结构

原则上，每个核心章节均包含九层：

1. **现实问题**：真实机器人到底遇到什么问题？
2. **物理直觉**：在公式之前建立正确直觉。
3. **系统与数据流**：明确模块、输入输出、shape、时间尺度和坐标系。
4. **数学形式化**：给出假设、定义、推导和边界条件。
5. **算法**：伪代码、复杂度、训练与推理过程。
6. **代码**：从最小实现到真实框架。
7. **实验**：可运行、可复现、可观察失败模式。
8. **论文谱系**：解释问题如何一步步演化，而不是简单列 paper。
9. **研究问题**：指出目前仍然不知道什么，以及怎样证伪新想法。

## 5. 仓库结构

```text
Embodied-AI-development/
├── README.md
├── BOOK_PLAN.md
├── AUTHORING_GUIDE.md
├── book/
│   ├── TOC.md
│   └── 00-preface/
│       └── 00-why-embodied-intelligence.md
├── figures/          # 原创图、数据流图、坐标系图、算法图
├── math/             # 长推导、符号表、数学补充
├── papers/           # 论文谱系与阅读笔记
├── labs/             # 教材实验
├── code/             # 最小实现与配套代码
├── simulations/      # MuJoCo / SAPIEN / Isaac Lab 等
├── datasets/         # 数据格式、转换与说明，不直接存大数据
├── benchmarks/       # benchmark 协议与统一评测
└── references/       # 参考文献与来源管理
```

目录会随教材发展扩充，但不会为了“看起来完整”而提前制造大量空目录。

## 6. 表达原则

本书优先采用“机制与数据流”表达方式。例如，在讲控制时，优先画清：

```text
Desired End-Effector Pose
    ↓
Inverse Kinematics / Operational-Space Target
    ↓
Joint / Task-Space Controller
    ↓
Torque / Position / Velocity Command
    ↓
Robot Dynamics
    ↓
Sensor Feedback
    ↺
```

在讲学习策略时，必须明确：

- observation 到底是什么；
- action 到底控制什么；
- observation/action frequency；
- history/window 长度；
- action horizon；
- 坐标系；
- tensor shape；
- policy 是 open-loop 还是 closed-loop；
- 真机中谁负责低层控制；
- 失败究竟发生在 perception、prediction、planning、control 还是 system latency。

## 7. 数学原则

数学不是附录装饰，而是全书核心语言。包括但不限于：

- 线性代数与矩阵分析；
- 概率论、贝叶斯推断与随机过程；
- 优化；
- 微分方程；
- SO(3)、SE(3) 与 Lie 群 / Lie 代数；
- 刚体运动学与动力学；
- 最优控制；
- 动态规划；
- 信息论；
- 图模型与图论；
- 几何、拓扑及其在具身表示中的适用边界；
- 表示学习与生成建模的数学基础。

所有公式尽可能回答三个问题：**它从哪里来？它在物理系统里表示什么？它在代码里对应哪一个张量或变量？**

## 8. 实验原则

实验不是正文的附件。教材实验遵循：

```text
Toy system
→ controlled simulation
→ realistic simulation
→ robot-learning benchmark
→ real robot when feasible
```

每个实验必须记录：环境、随机种子、数据、依赖、硬件假设、评价指标、失败样例和可复现命令。

## 9. 时效性与证据

具身智能变化快，因此：

- 基础数学、物理、机器人学章节追求稳定；
- 前沿模型章节明确版本与日期；
- 论文结论尽量回到原论文、项目页、官方代码或官方技术报告；
- 不把宣传口径直接写成技术结论；
- 对尚无一致证据的观点明确标注“假说 / 争议 / 尚未证实”；
- 每个重要技术结论尽量给出可追溯来源。

## 10. 当前版本

当前处于 **v0.1 — Foundation / Architecture of the Book** 阶段。

第一阶段任务：

1. 锁定教材全局知识图谱与章节依赖；
2. 建立数学符号、图示、引用、代码和实验规范；
3. 完成 Part 0–III：具身智能观、数学基础、物理与机器人学、感知；
4. 同时搭建最小实验链，确保教材不是“只写不跑”。

完整目录见 [`book/TOC.md`](book/TOC.md)。  
写作与证据规范见 [`AUTHORING_GUIDE.md`](AUTHORING_GUIDE.md)。  
全书工程路线见 [`BOOK_PLAN.md`](BOOK_PLAN.md)。

---

**长期目标：让读者从第一性原理出发，最终能够独立理解、实现、质疑并推进具身智能。**
