# Part 40　Physics Simulation 与 Robot Learning Platform

## 40.1 为什么机器人研究离不开 Simulation

真实机器人实验昂贵、慢、危险且难以复现。

仿真提供：

- fast reset；
- parallel rollout；
- exact state；
- controlled intervention；
- safe failure。

但仿真不是现实：

\[
P_{sim}(s'\mid s,a)\neq P_{real}(s'\mid s,a).
\]

所以它既是研究工具，也是 bias source。

---

## 40.2 Physics Engine 的数值基础

物理引擎每个 time step 近似求：

\[
M(q)\ddot q+C(q,\dot q)+g(q)=\tau+J^T\lambda.
\]

然后处理：

- collision detection；
- contact constraints；
- friction；
- integration。

不同 solver 对 contact-rich task 可能产生明显差异。

---

## 40.3 MuJoCo

MuJoCo 适合：

- rigid-body dynamics；
- control；
- RL；
- fast CPU/GPU-compatible workflows。

它强调稳定、可控的 articulated dynamics。

适合把算法问题和视觉渲染复杂度分开研究。

---

## 40.4 SAPIEN

SAPIEN 强调机器人操作、视觉、3D 场景和高质量交互 simulation。

在 manipulation benchmark 中常用于：

- RGB-D；
- point cloud；
- articulated objects；
- photorealistic rendering。

使用时必须记录 renderer、physics version 和 asset version。

---

## 40.5 Isaac Sim

Isaac Sim 建立在 USD / Omniverse 生态上，提供：

- RTX sensor rendering；
- articulated robot；
- synthetic data；
- large scene；
- GPU simulation integration。

它更像大型 robotics simulation platform，而不只是 physics engine。

---

## 40.6 Isaac Lab

Isaac Lab 在 Isaac Sim 上构建 robot learning workflow：

- RL；
- imitation；
- manager-based environment；
- vectorized simulation；
- domain randomization；
- humanoid / manipulation tasks。

实验必须区分：

```text
Isaac Sim = simulator/platform
Isaac Lab = robot-learning framework built around it
```

---

## 40.7 ManiSkill

ManiSkill 提供标准化 manipulation tasks、SAPIEN-based simulation 和 robot learning pipeline。

适合：

- imitation；
- RL；
- visual manipulation；
- reproducible benchmark。

---

## 40.8 robosuite / MetaWorld

这类平台价值在于：

- task suite 小而标准；
- reset 简单；
- baseline 丰富。

适合算法 ablation，但不要把在有限 task family 上的提升等同于 open-world manipulation。

---

## 40.9 RLBench

RLBench 基于 CoppeliaSim，强调大量 language-described manipulation tasks。

它推动了 multi-task imitation 和 language-conditioned policy 研究。

需要警惕：task generator / camera placement 的 benchmark-specific shortcut。

---

## 40.10 RoboTwin / RoboTwin 2.0

RoboTwin 类平台强调双臂与多策略统一评测，并逐步覆盖更复杂的 manipulation data / policy pipeline。

对于研究者，平台最重要的价值不是“任务多”，而是能否：

- 固定 asset/version；
- 重复同一随机化；
- 输出完整 observation/action；
- 接不同 policy；
- 做公平 evaluation。

---

## 40.11 Habitat

Habitat 主要服务 embodied navigation / interactive embodied AI。

它让研究者在大规模 3D scene 中研究：

- navigation；
- exploration；
- embodied question answering。

---

## 40.12 BEHAVIOR / OmniGibson

这类平台把目标推进到 household activities：

- articulated objects；
- semantic scene；
- long-horizon tasks；
- household interaction。

更接近“机器人生活在环境里”，但 simulation complexity 也更高。

---

## 40.13 Humanoid / Whole-Body Simulation

humanoid simulation 必须处理：

- floating base；
- many contacts；
- high DoF；
- fall；
- actuator model。

一个 manipulator simulator 的稳定 contact 参数不一定适合 humanoid foot contact。

---

## 40.14 Asset、Material 与 Scene

仿真世界由三类东西组成：

```text
geometry
material/physics property
semantic/task metadata
```

asset quality 直接影响：

- collision mesh；
- inertia；
- friction；
- graspability。

漂亮 mesh 不代表物理参数正确。

---

## 40.15 USD / MJCF / URDF Import Pipeline

跨平台 import 可能丢失：

- joint limit；
- transmission；
- collision mesh；
- material；
- sensor；
- mimic joint。

因此 import 后必须做 robot doctor：

1. joint range；
2. FK；
3. gravity；
4. collision；
5. controller；
6. sensor。

---

## 40.16 Parallel Simulation

若有 \(N\) 个环境：

\[
\{E_1,\dots,E_N\},
\]

一次 policy inference 可 batch：

\[
A=\pi(O),\quad O\in\mathbb R^{N\times d}.
\]

这是现代 locomotion RL scaling 的基础。

---

## 40.17 GPU-Accelerated Simulation

GPU 可并行：

- physics；
- rendering；
- policy inference。

但 GPU 加速也引入：

- nondeterminism；
- memory pressure；
- renderer/driver dependency。

必须记录软件栈。

---

## 40.18 Determinism 与 Versioning

可复现实验至少固定：

- simulator version；
- asset commit；
- random seed；
- physics dt；
- substeps；
- solver params；
- renderer；
- robot controller。

否则“同一环境”实际上不是同一个实验。

---

## 40.19 Benchmark Platform 与研究问题错位

平台会诱导研究者解决“平台容易测的问题”。

例如：

- fixed camera；
- perfect reset；
- clean object segmentation；
- short episode。

真实世界未必拥有这些条件。

所以研究问题应先定义，再选 simulator；不要让 simulator 定义科学问题。

---

## 本章结论

Simulation 的价值是提供可控、可并行、可干预的物理实验室；风险是把 simulator artifacts 当世界规律。优秀的机器人研究必须同时理解算法和 simulator solver、asset、controller、version 的边界。
<!-- CHAPTER-ENRICHMENT-R3-P40:START -->
## 40.22 Platform / Simulation Failure Taxonomy

### Environment version drift

同名 task 在 asset、physics parameter、success detector 或 controller 更新后已不是同一个 benchmark。必须固定 commit 与 asset hash。

### Headless/render mismatch

GPU compute 正常不代表 Vulkan/RTX render path 正常；视觉任务可能悄悄退到 software renderer 或不同 camera pipeline。

### Physics-step / control-step confusion

sim 以 1 kHz physics、20 Hz policy、50 Hz controller 运行时，substep/decimation 配错会改变真实 dynamics。

### Reset leakage

reset 过程留下上一 episode state、cache、random seed 或 object pose pattern，造成异常高 success。

### Simulator-specific observation shortcut

segmentation ID、perfect state、deterministic lighting 等训练时可见信号，真机不存在。

## 40.23 最小实验：Platform Doctor + Cross-Simulator Slice

对同一最小 task 固定 policy/input-output convention，建立 doctor：

```text
GPU compute
renderer / camera
physics dt
control dt
asset hash
seed determinism
joint/action units
contact/friction sanity
trajectory logging
```

随后在两套 simulator 或两组 physics parameter 上执行相同 action sequence，比较 state/contact divergence。目标不是证明 simulator 一致，而是量化**哪些差异足以改变算法结论**。
<!-- CHAPTER-ENRICHMENT-R3-P40:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 40`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-40)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
