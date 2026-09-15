# Simulator-Layer Labs

`labs/simulators/` 是教材从 **M — mechanism** 进入 **S — physics simulator** 的第二层执行系统。

M 层回答：

> 一个机制在最小数学系统中是否存在、能否被负对照推翻？

S 层继续回答：

> 同一机制进入真实物理引擎、接触、actuator、sensor timing 与 simulator state 后是否仍成立？

## 统一原则

Simulator Lab 不允许只保留成功视频。它必须尽量复用 `labs/runnable/` 的证据契约：

```text
config / model asset
→ simulator state
→ observation / controller input
→ action / actuator command
→ physics step
→ raw trajectory
→ failure events
→ summary metrics
→ deterministic smoke assertion
```

轻量 simulator smoke 可以进入 GitHub-hosted CI；GPU renderer、大规模 parallel rollout、Isaac Lab / RoboTwin 重任务仍只在研究机器执行，并复用相同的 result schema。

## 当前后端

### MuJoCo

`mujoco/` 是第一个 S 层后端。首个 reference adapter 是 **Lab 06 Feedback Control**：

```text
qpos / qvel
→ PD controller
→ MuJoCo actuator ctrl
→ external disturbance
→ mj_step
→ recovery / stability metrics
```

后续优先扩展：

- Lab 04 Numerical IK；
- Lab 05 Rigid-Body Dynamics；
- Lab 06 impedance / computed torque；
- Lab 18 locomotion。

### RoboTwin

计划承接：Lab 17 / 22 / 25 / 26 / 37 与 Capstone 1。

### Isaac Lab

计划承接：Lab 18 / 26 / 35 / 36 与 Capstone 2。

## S 层不是 M 层的替代

机制实验与 simulator 实验应形成：

```text
M-layer falsification
        ↓
S-layer external-physics check
        ↓
R-layer real-system validation
```

若一个 claim 在 M 层已经被 falsify，不应该直接用更昂贵的 simulator / real-robot experiment 掩盖机制问题。
