# Embodied Intelligence Labs

教材实验系统分成四层，不再把“Lab 描述”“执行环境”“实验规范”和“可运行代码”混在一个文件里。

```text
40 Labs + 3 Capstones
        ↓
Execution Matrix
M / S / R execution tier
        ↓
Runnable implementation
config → run → raw logs → failures → summary
        ↓
Unified Experiment Protocol
controls → CI → failure analysis → falsification
```

## 1. Curriculum

[`LABS.md`](LABS.md) 定义 **40 个渐进 Lab + 3 个 Capstone**，回答：

> 应该研究什么问题？

覆盖数学/机器人学、感知、robot learning、VLA、world model、continual learning、humanoid、whole-body 与真实系统工程。

## 2. Execution Matrix

[`EXECUTION_MATRIX.md`](EXECUTION_MATRIX.md) 为每个 Lab 指定：

- **M — Mechanism / CPU**：最小可证伪机制实验；
- **S — Simulator**：物理 simulator / benchmark；
- **R — Real System**：ROS 2 / 真机 / 真实传感器。

它回答：

> 这个实验最小应该在哪一层运行，何时值得 scale up？

## 3. Runnable Labs

[`runnable/README.md`](runnable/README.md) 定义统一可执行 harness。

当前第一份 reference implementation：

- [`Lab 22 — Asynchronous Policy Execution`](runnable/lab22_async_execution/README.md)

其 CPU mechanism test 已进入长期 executable regression；后续 simulator adapter 将继续复用同一 run schema。

## 4. Experiment Protocol

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

## 5. Evidence flow

所有正式实验应尽量形成同一证据链：

```text
Question
→ falsifiable hypothesis
→ controlled intervention
→ raw per-step logs
→ failure events
→ summary metrics + uncertainty
→ negative control
→ interpretation
→ next experiment
```

最终目标不是把 40 个实验都“跑通”，而是让读者能够从一个物理/算法 claim 出发，构造足以支持或推翻它的实验。
