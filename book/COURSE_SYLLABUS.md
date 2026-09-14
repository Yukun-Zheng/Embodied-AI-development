# 36-Week Systematic Embodied Intelligence Curriculum
## 从“会深度学习”到“能独立做具身智能研究”

> 这不是按论文热度排的 reading list，而是一条强依赖路径。每周同时推进四层：**概念 → 数学 → 代码 → 实验/研究判断**。

推荐强度：每周 10–15 小时。若是全职集中学习，可以把 36 周压缩到 12–18 周；如果同时上课/做科研，则按 36 周或更长周期推进。

---

# 每周固定工作流

```text
Day 1–2  读 Chapter + Derivation
Day 3    手算 / minimal code
Day 4–5  Lab / simulator experiment
Day 6    读 2–4 个 primary sources
Day 7    写 failure notes + research question
```

每周至少留下五个 artifact：

```text
1. 一页机制图
2. 一页公式推导
3. 一个可运行脚本
4. 一张实验图/表
5. 一个可证伪问题
```

---

# Phase A　建立具身智能世界观（Week 1–2）

## Week 1 — 什么是具身智能

读：Part 0。

掌握：

- feedback loop；
- body/environment coupling；
- partial observability；
- latency；
- affordance；
- physical intelligence。

实验：open-loop vs closed-loop toy agent。

验收：能从 `sensor → state → policy → controller → actuator → world` 完整画出一台真实机器人的信息流。

## Week 2 — 1948–2026 技术史

读：Part 1 + `references/TIMELINE.md`。

目标：知道今天 VLA / World Model / Humanoid 每个词分别从哪些旧问题发展而来。

任务：任选一个 2026 系统，画“它继承了哪些 1980–2024 技术”的谱系图。

---

# Phase B　数学与动态系统（Week 3–6）

## Week 3 — Linear Algebra for Robotics

Part 2 前半。

手算：

- basis / coordinate change；
- rank / null space；
- SVD；
- least squares。

代码：`planar_arm.py` 中 Jacobian / pseudoinverse。

## Week 4 — Calculus / ODE / Numerics

Part 2 后半。

手算：Jacobian / Hessian / Taylor linearization。

实验：不同 Euler/RK step size 对动态系统稳定性的影响。

## Week 5 — Probability / Information / Uncertainty

Part 3。

重点：Bayes、entropy、mutual information、calibration。

代码：`kalman_filter.py`。

## Week 6 — Optimization / Optimal Control / Geometry / Causality

Part 4–5。

手算：LQR、KKT、Lie group 基础、intervention。

输出：写一页“prediction ≠ causality ≠ control”。

---

# Phase C　经典机器人学核心（Week 7–12）

## Week 7 — Robot Body / Mechatronics

Part 6。

必须搞清：motor、gear、encoder、position/velocity/torque control、CAN/EtherCAT、URDF/MJCF/USD。

作业：从一个真实 robot description 自动生成 kinematic tree。

## Week 8 — SO(3) / SE(3)

Part 7 + D4/D5。

代码：`se3.py`。

验收：随机 rotation round-trip test 全通过；能解释 left/right composition。

## Week 9 — FK / IK / Jacobian

Part 8 + D1/D2/D3/D6。

代码：`planar_arm.py`。

验收：自己写 analytical FK、numerical IK、DLS、null-space objective。

## Week 10 — Dynamics / Contact / Grasp

Part 9。

手推：2-link Euler–Lagrange。

实验：接触任务记录 force/slip/pose error 三条同步曲线。

## Week 11 — Feedback / Impedance / MPC / WBC

Part 10。

代码：`control.py`。

实验：free-space vs contact，比较 position control 与 impedance。

## Week 12 — Motion Planning / TAMP / Belief Planning

Part 11。

实现：A* + RRT/RRT*。

研究题：构造一个 learned policy 和 classical planner 必须合作才能稳定完成的任务。

---

# Phase D　感知、状态与主动信息获取（Week 13–16）

## Week 13 — Sensors / Calibration / Time

Part 12。

必须掌握：intrinsic/extrinsic、RGB-D、IMU、encoder、F/T、tactile、timestamp。

实验：人为注入 10–100 ms observation/action misalignment。

## Week 14 — 2D / 3D / 4D Representation

Part 13–14。

比较：CNN/ViT/self-supervised、point cloud/TSDF/NeRF/3DGS/object-centric representation。

核心问题：什么表示真正服务 action？

## Week 15 — State Estimation / SLAM / Belief

Part 15。

实现：Kalman/EKF。

输出：画出 `observation → belief → decision`，而不是只画 perception network。

## Week 16 — Tactile + Active Perception

Part 16–17。

代码：`active_perception.py`。

实验：random camera motion vs information-gain NBV；slow vision + fast tactile residual。

---

# Phase E　Robot Learning Core（Week 17–21）

## Week 17 — 为机器人重新学 ML

Part 18。

重点：closed-loop distribution shift、sequence model、generative objective。

实验：同一个双峰 action toy 比 regression / diffusion / flow。

## Week 18 — Imitation Learning

Part 19。

代码：`bc_dagger.py`。

任务：自己制造 covariate shift，然后用 DAgger 修复。

## Week 19 — Reinforcement Learning

Part 20。

实现/复现：PPO + SAC。

必须同时看 sample efficiency、wall-clock、seed variance。

## Week 20 — Offline → Online Experience Learning

Part 20 + 29 预读。

比较：

```text
BC
BC + more demonstrations
BC + offline RL
BC + online RL
```

统一真实 interaction budget。

## Week 21 — Diffusion / Flow / AR Action

Part 21 + Case Study 02。

代码：`generative_actions.py`。

核心：mode coverage、action horizon、execution horizon、latency。

---

# Phase F　VLM → VLA（Week 22–25）

## Week 22 — Language / VLM / Grounding

Part 22。

读 CLIP、PaLM-E、SayCan。

实验：VLM 只负责 object/affordance grounding，经典 planner 负责可执行性。

## Week 23 — VLA Formation 2022–2024

Part 23 + `MODEL_ATLAS.md`。

读：Gato、RT-1/2、Open X、Octo、OpenVLA。

任务：对一个开放 VLA 逐 tensor 追 dataset → action output。

## Week 24 — VLA 2024–2026

Part 24。

比较：π、GR00T、Gemini Robotics、Helix。

不比较宣传数字；只填 10 个机制轴。

## Week 25 — VLA Internals / Data Scaling

Part 25–26 + Case Study 03。

重点：

- frozen vs joint training；
- action head；
- dataset mixture；
- embodiment conditioning；
- human video；
- latency/controller。

输出：做一次 `data gain vs architecture gain` factorial study。

---

# Phase G　VLA 之后（Week 26–29）

## Week 26 — Embodied Reasoning

Part 27。

做 wrong/shuffled reasoning negative control。

目标：证明 reasoning 是否真的改变 motor behavior。

## Week 27 — Memory

Part 28。

比较：context-only、RNN state、episodic retrieval、structured task memory。

任务 horizon 必须逐步增加。

## Week 28 — Learning from Experience

Part 29。

重点：autonomous practice、reset、failure replay、RL post-training。

输出：用 robot-hours 作为成本单位设计实验。

## Week 29 — World Models

Part 30–31 + Case Study 04。

代码：`world_model_mpc.py`。

必须做：random/shuffled/wrong-physics world-model negative control。

---

# Phase H　能力层：Manipulation → Humanoid（Week 30–32）

## Week 30 — Manipulation / Bimanual / Dexterity

Part 32–33。

实验：

- grasp verification；
- bimanual relative frame；
- slip/tactile feedback。

核心：contact 与 internal force。

## Week 31 — Navigation / Long-Horizon Embodiment

Part 34。

比较 reactive、RNN、semantic map、active exploration。

目标：把 memory/belief 从抽象模型放回移动机器人。

## Week 32 — Humanoid / Whole-Body / Multi-Robot

Part 35–36。

重点：floating base、centroidal dynamics、motion prior、loco-manipulation、multi-rate whole-body VLA、multi-agent coordination。

---

# Phase I　长期智能与真实系统（Week 33–34）

## Week 33 — Cross-Embodiment / Continual / Developmental

Part 37–39。

代码：`continual_metrics.py`。

实验必须测：

- unseen morphology；
- retention；
- forward transfer；
- resource growth；
- autonomy ratio。

## Week 34 — Simulation / Data / Deployment

Part 40–43。

选至少两个 simulator 复现实验。

做一次完整 robot rollout latency budget：

```text
sensor
→ preprocess
→ model
→ safety
→ controller
→ actuator
→ observe
```

---

# Phase J　从读论文到做研究（Week 35–36）

## Week 35 — Evaluation / Reliability / Safety

Part 44–45。

代码：`evaluation_stats.py`。

任务：把一个“成功率提高”的论文结果重写成：

- denominator；
- CI；
- OOD matrix；
- intervention rate；
- recovery rate；
- safety case。

## Week 36 — Independent Research Program

Part 46–50。

最终交付不是考试，而是一份完整研究提案：

```text
Grand Question
Hypothesis
Mechanism
Minimum Experiment
Positive Control
Negative Control
Kill Criterion
Scale-up Plan
Real-Robot Evaluation
Three-year Question Tree
```

最终答辩的最后一个问题固定是：

> **什么实验结果会让你承认自己的核心假设是错的？**

如果答不出来，就还没有形成真正的科研问题。

---

# 三次综合 Capstone

## Capstone A — Classical-to-Learned Manipulation

完成 Week 12 后：

```text
RGB-D
→ state estimation
→ motion planning / IK
→ impedance control
→ manipulation
```

然后替换 policy 层为 BC，比较 learned 与 classical 的 failure distribution。

## Capstone B — Foundation Robot Policy Autopsy

完成 Week 29 后：

选一个开放 VLA：

```text
clone code
→ reproduce
→ trace all tensors
→ profile latency
→ identify low-level controller
→ design negative control
→ write mechanism report
```

目标不是跑 demo，而是“把系统拆到不能再拆”。

## Capstone C — Falsifiable New Architecture

完成 Week 36：

必须提出一个新机制，并通过最小实验决定是否值得继续。

要求：

- 不能只换 backbone；
- 必须有明确 physical failure target；
- 必须有 negative control；
- 如果最小实验失败，立即放弃/修订，不靠规模掩盖。

---

# 学完之后你应该能做什么

不是“知道很多论文名字”，而是能：

1. 拿到陌生机器人系统，快速画出 body/sensor/action/control 链；
2. 拿到陌生论文，追踪完整 tensor / frame / frequency / data flow；
3. 手推关键机器人与学习公式；
4. 写最小可运行机制实验；
5. 区分 data gain、architecture gain、system gain；
6. 识别论文中的 hidden controller / hidden data / benchmark shortcut；
7. 设计 world model / reasoning / memory 的负对照；
8. 把 VLA 放回真实物理闭环，而不是把机器人当 LLM 外设；
9. 独立形成一个长期、可证伪的研究 program。
