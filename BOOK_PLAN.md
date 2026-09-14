# BOOK PLAN — 《具身智能：从物理世界到通用机器人》

## 0. 项目定位

这不是一部“机器人算法百科”，也不是一部“VLA 综述”。它的组织原则是：

> **从一个智能体如何进入物理世界、形成闭环、从交互中学习，再到跨任务、跨场景、跨本体的通用智能。**

全书以 `World ↔ Body ↔ Sensors ↔ State ↔ Prediction ↔ Decision ↔ Control ↔ Action` 为主轴，把传统机器人学与现代机器学习真正接起来。

---

## 1. 全书知识图谱

```text
Mathematics
├─ Linear Algebra
├─ Probability / Statistics
├─ Optimization
├─ Differential Equations
├─ Geometry / Lie Groups
├─ Information Theory
└─ Dynamical Systems
        ↓
Physics & Robotics
├─ Rigid-body motion
├─ Kinematics
├─ Dynamics
├─ Contact
└─ Actuation
        ↓
Perception & State
├─ Vision
├─ Depth / Point Cloud
├─ Tactile / Force
├─ Proprioception
├─ State Estimation
└─ Representation
        ↓
Decision & Control
├─ Feedback Control
├─ Optimal Control
├─ Motion Planning
├─ MPC
└─ Whole-body Control
        ↓
Robot Learning
├─ Imitation Learning
├─ Reinforcement Learning
├─ Offline RL
├─ Representation Learning
└─ Generative Policies
        ↓
Foundation Embodied Intelligence
├─ VLM
├─ VLA
├─ World Models
├─ Embodied Reasoning
├─ Active Perception
├─ Memory
└─ Planning
        ↓
General-Purpose Robots
├─ Manipulation
├─ Bimanual
├─ Dexterous Hands
├─ Locomotion
├─ Humanoids
├─ Multi-Robot
├─ Cross-Embodiment
└─ Continual / Developmental Learning
```

---

## 2. 读者能力路线

### Level A — 能看懂机器人在干什么

读者应能回答：

- 世界坐标系、机器人基座坐标系、末端坐标系分别是什么；
- 一个 joint state、pose、twist、wrench 各自表示什么；
- camera observation 如何变成 policy 输入；
- policy 输出的是 torque、joint position、joint velocity 还是 Cartesian delta；
- 真机闭环频率、模型推理频率和低层控制频率为何不同。

### Level B — 能从头实现基础机器人算法

读者应能实现并验证：

- FK / IK；
- Jacobian；
- trajectory generation；
- PID / impedance / operational-space control；
- Kalman filter；
- sampling-based planning；
- BC / DAgger / PPO；
- Transformer / diffusion / flow based robot policy。

### Level C — 能理解现代具身模型

读者应能从系统层解释：

- VLM 与 VLA 的差异；
- action tokenization 与 continuous action generation；
- observation history 与 action chunking；
- Diffusion Policy、ACT、flow matching policy 各自的归纳偏置；
- world model 到底预测什么；
- active perception 为什么不是简单“多移动相机”；
- whole-body policy 如何与低层控制器配合。

### Level D — 能做研究

最终应能：

- 区分研究问题与 benchmark engineering；
- 从 failure mode 逆推模型假设；
- 设计对照组和负对照；
- 判断性能来自数据、架构、训练策略还是评价协议；
- 形成可证伪假说；
- 独立复现、批判和扩展最新工作。

---

## 3. 全书四条平行主线

### 主线 A：物理与控制

回答“机器人身体为什么会这样动”。

`Rigid Body → Kinematics → Dynamics → Contact → Feedback → Optimal Control → Whole-Body Control`

### 主线 B：感知与世界表示

回答“机器人到底知道世界中的什么”。

`Sensor → Geometry → State Estimation → Representation → Uncertainty → World Model`

### 主线 C：学习与智能

回答“机器人怎样通过数据和交互获得行为”。

`Supervised Learning → Imitation → RL → Generative Policy → Foundation Model → Continual Learning`

### 主线 D：系统与实验

回答“论文里的模型怎样真正变成一个工作的机器人系统”。

`Data → Simulator → Training → Deployment → Real-time System → Evaluation → Failure Analysis`

四条线在每一阶段都要交叉，而不是写成互不相干的课程笔记。

---

## 4. 教材工程标准

### 4.1 理论层

每个核心概念至少回答：

1. 为什么需要它；
2. 它建立在哪些假设上；
3. 数学对象是什么；
4. 对应真实机器人系统中的什么量；
5. 在代码里是哪一个变量 / tensor；
6. 哪些情况下会失效。

### 4.2 图示层

优先原创以下图形：

- 数据流图；
- 坐标系图；
- tensor shape 图；
- 时间轴图；
- feedback loop 图；
- architecture 图；
- paper genealogy 图；
- failure mode 图；
- benchmark protocol 图。

### 4.3 代码层

同一个主题通常分三层代码：

```text
minimal/      # 最小数学实现，便于学习
reference/    # 与论文或标准实现对齐
system/       # 接入真实仿真/机器人系统
```

### 4.4 实验层

每个实验必须给出：

- hypothesis；
- independent variable；
- dependent variable；
- controls；
- seeds；
- metrics；
- expected failure modes；
- reproducibility instructions。

---

## 5. 版本路线

### v0.1 — Book Architecture

- 完成全书目录；
- 建立作者规范；
- 完成序章；
- 建立符号体系；
- 建立第一批基础实验。

### v0.2 — Mathematical & Robotics Foundations

- 数学卷；
- 刚体运动；
- 运动学；
- 动力学；
- 控制基础。

### v0.3 — Perception, State, Planning

- 视觉 / 深度 / 点云 / 触觉；
- 状态估计；
- mapping；
- planning；
- MPC。

### v0.4 — Robot Learning Core

- imitation learning；
- RL；
- offline learning；
- representation learning；
- generative policies。

### v0.5 — Foundation Models for Robotics

- VLM；
- VLA；
- robot foundation models；
- world models；
- reasoning / memory / planning。

### v0.6 — Manipulation, Humanoids, Cross-Embodiment

- bimanual；
- dexterity；
- locomotion；
- whole-body；
- cross-embodiment。

### v0.7 — Systems, Simulation, Data and Evaluation

- Isaac Lab / MuJoCo / SAPIEN；
- robot data engineering；
- deployment；
- benchmarks；
- sim2real；
- safety。

### v0.8 — Research Edition

- 论文谱系补全；
- 大量 reproduction case study；
- failure analysis；
- research methodology。

### v1.0 — Complete First Edition

目标不是“所有章节都有文字”，而是：

- 核心概念闭环；
- 关键实验可运行；
- 主要论断可追溯；
- 章节依赖稳定；
- 前沿部分注明时间版本；
- 从初学者到研究者具有连续学习路径。

---

## 6. 长期扩展

v1.0 之后仍持续维护：

- 新的 VLA / world model / humanoid 系统；
- 新 benchmark；
- 新型 action representation；
- 新型感知与触觉；
- 新型 robot morphology；
- continual / developmental learning；
- post-Transformer embodied architectures；
- 数学上更统一的物理智能理论。

因此，本仓库应被视为一部 **living textbook**，而不是一次性出版物。
