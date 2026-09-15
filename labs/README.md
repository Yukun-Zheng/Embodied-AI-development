# Embodied Intelligence Labs

教材实验系统不再把“Lab 描述”“机制验证”“物理 simulator”“实验规范”和“真实系统”混在一个文件里，而是明确采用 **M → S → R** 的证据升级链。

```text
40 Labs + 3 Capstones
        ↓
Execution Matrix
M / S / R execution tier
        ↓
M-layer runnable mechanism labs
        ↓
S-layer physics simulator labs
        ↓
R-layer real-system validation
        ↓
Unified Experiment Protocol
```

## 1. Curriculum

[`LABS.md`](LABS.md) 定义 **40 个渐进 Lab + 3 个 Capstone**，回答：

> 应该研究什么问题？

覆盖数学/机器人学、感知、robot learning、VLA、world model、experience learning、continual learning、curriculum、humanoid、whole-body、多机器人与真实系统工程。

## 2. Execution Matrix

[`EXECUTION_MATRIX.md`](EXECUTION_MATRIX.md) 为每个 Lab 指定：

- **M — Mechanism / CPU**：最小可证伪机制实验；
- **S — Simulator**：独立物理 simulator / benchmark；
- **R — Real System**：ROS 2 / 真机 / 真实传感器。

它回答：

> 这个实验最小应该在哪一层运行，何时值得 scale up？

当前更细的 S-layer 路线见 [`simulators/SIMULATOR_MATRIX.md`](simulators/SIMULATOR_MATRIX.md)。

## 3. M-Layer Runnable Labs

[`runnable/README.md`](runnable/README.md) 定义统一的机制实验 harness：

```text
config
→ deterministic intervention
→ raw logs
→ failures
→ summary
→ independent analyzer
→ CI smoke
```

当前已有 **14 个 CI-verified M-layer reference labs**，覆盖主动感知、触觉、多速率执行、VLA 视觉因果性、跨本体、记忆、world model、reasoning、experience learning、continual learning、curriculum、双臂、多机器人和 safety shield。

这些实验的核心价值是先回答：

> claim 的机制在最小系统里是否真实存在，而且是否经得住负对照？

## 4. S-Layer Physics Simulators

[`simulators/README.md`](simulators/README.md) 是 Phase 2 入口。

首个后端是 [`simulators/mujoco/`](simulators/mujoco/README.md)。当前已经在 GitHub-hosted CI 上用 **MuJoCo 3.13.0** 实际验证：

- Lab 04 Numerical IK / Jacobian / DLS；
- Lab 05 Rigid-Body Dynamics；
- Lab 06 Feedback Control。

三者构成第一条 S-layer 基础链：

```text
kinematics / Jacobian
→ rigid-body dynamics
→ feedback control
```

下一步不是继续堆孤立 simulator demo，而是做**跨层因果实验**：把 Lab 05 的 dynamics mismatch 注入 Lab 06 的 model-based controller，测模型误差如何变成 tracking / saturation / recovery error；随后进入 RoboTwin / Isaac Lab adapters。

## 5. Experiment Protocol

[`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) 定义：

- hypothesis；
- system contract；
- controls；
- seeds；
- confidence intervals；
- latency；
- failure taxonomy；
- world-model / VLA / continual / cross-embodiment protocol；
- safety gate；
- publication table。

它回答：

> 一个训练 run 什么时候才算科学实验？

## 6. Evidence flow

所有正式实验应尽量形成同一证据链：

```text
Question
→ falsifiable hypothesis
→ M-layer controlled intervention
→ S-layer independent physics check
→ R-layer system validation
→ raw per-step logs
→ failure events
→ uncertainty / confidence interval
→ negative control
→ interpretation
→ next experiment
```

最终目标不是把 40 个实验都“跑通”，而是让读者能够从一个物理/算法 claim 出发，构造足以支持或推翻它的完整证据链。
