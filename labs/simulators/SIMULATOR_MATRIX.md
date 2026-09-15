# Simulator-Layer Execution Matrix

> Phase 2 的目标不是“把所有 toy 换成一个仿真器”，而是把已经在 M 层被 falsify/验证过的机制逐步送入独立物理后端，观察哪些结论能保留、哪些会被 contact、dynamics、timing、controller 或 embodiment 重新改写。

## 1. 状态定义

| 状态 | 含义 |
|---|---|
| **CI reference** | GitHub-hosted runner 实际安装后端并通过 deterministic physics smoke；有 frozen result |
| **adapter next** | 机制已在 M 层稳定，下一步应做 simulator adapter |
| **research machine** | 后端太重，不在 hosted CI 跑完整 rollout；只做 schema/import/dry-run |
| **real next** | S 层稳定后应进入 R 层真机验证 |

---

## 2. MuJoCo — 经典机器人学基础链

| Lab | 机制 | S-layer 状态 | CI reference | 下一步 |
|---|---|---|---|---|
| **04 Numerical IK** | `site_xpos → mj_jacSite → DLS → actuator → mj_step` | **CI reference** | [`LAB04_REFERENCE_RESULTS.md`](mujoco/LAB04_REFERENCE_RESULTS.md) | collision/joint-limit aware IK |
| **05 Rigid-Body Dynamics** | `M(q), bias, passive force → qacc` | **CI reference** | [`LAB05_REFERENCE_RESULTS.md`](mujoco/LAB05_REFERENCE_RESULTS.md) | model-mismatch → closed-loop controller |
| **06 Feedback Control** | `q/qdot → PD → force disturbance → recovery` | **CI reference** | [`LAB06_REFERENCE_RESULTS.md`](mujoco/LAB06_REFERENCE_RESULTS.md) | impedance / computed torque |
| 18 PPO Locomotion | policy → contact dynamics → gait | adapter next | — | MuJoCo/Isaac matched protocol |

The first S-layer foundation is therefore closed:

```text
Part 8 / Lab 04
kinematics + Jacobian
        ↓
Part 9 / Lab 05
rigid-body dynamics
        ↓
Part 10 / Lab 06
feedback control
```

All three references were executed on **MuJoCo 3.13.0** in GitHub Actions.

---

## 3. RoboTwin — Manipulation / VLA / Bimanual

| Lab | M-layer evidence | S-layer plan | Hosted CI |
|---|---|---|---|
| 17 ACT / Action Chunking | existing source case + minimal action latency | same task/action convention as Capstone 1 | adapter import/config only |
| 22 Async Execution | **CI M reference** | inject real simulator policy latency / action-age logging | dry-run only |
| 25 Visual Intervention | **CI M reference** | object pose / texture / background / camera / distractor intervention matrix | scene/config validation only |
| 26 Cross-Embodiment | **CI M reference** | held-out robot/action-interface variants | adapter dry-run only |
| 37 Bimanual Coordination | **CI M reference** | relative-frame control on shared-object tasks | adapter dry-run only |
| Capstone 1 | — | ACT + Diffusion/DP3 + Flow + VLA under matched protocol | heavy rollout on research machine |

RoboTwin 不应只输出 success。必须尽量复用 M 层已经固定的因果变量：

```text
visual reliance
latency / action age
relative-frame error
intervention type
failure taxonomy
```

---

## 4. Isaac Lab — Locomotion / Humanoid / Development

| Lab | M-layer evidence | S-layer plan | Hosted CI |
|---|---|---|---|
| 18 PPO Locomotion | RL foundations | reward / perturbation / gait diagnostics | import/config only |
| 26 Cross-Embodiment | **CI M reference** | different humanoid/robot morphology descriptors | import/config only |
| 35 Humanoid Retargeting | chapter + protocol | motion target + contacts + balance constraints | research machine |
| 36 Whole-Body Loco-Manipulation | chapter + protocol | hierarchical vs unified whole-body | research machine |
| Capstone 2 | Lab 32/33/34 M evidence | A→B→C + revisit + curriculum + continual updates | research machine |

Isaac Lab 的重点不是把 action dimension 变大，而是引入：

- floating-base dynamics；
- contacts；
- balance；
- multi-rate whole-body control；
- long-running curriculum / continual-update experiments。

---

## 5. M → S → R promotion gate

一个机制从 M 层晋升 S 层，应至少满足：

```text
M-layer hypothesis is explicit
+ matched negative control exists
+ simulator observation/action convention is documented
+ physical backend really produces the transition
+ raw state/action/force/time logs exist
+ mechanism relation survives or fails informatively
```

S 层晋升 R 层再增加：

```text
calibration manifest
+ timestamp / latency logging
+ actuator/controller boundary
+ safe reset / stop protocol
+ hardware limits
+ real failure audit
```

---

## 6. Current Phase 2 milestone

As of the current repository state:

- **14 M-layer runnable reference labs** are CI-verified;
- **3 MuJoCo S-layer reference experiments** are CI-verified:
  - Lab 04 Numerical IK;
  - Lab 05 Rigid-Body Dynamics;
  - Lab 06 Feedback Control;
- next priority is no longer another CPU toy;
- next high-value step is a **cross-layer experiment** where Lab 05 model mismatch is injected into the same closed-loop controller, followed by RoboTwin / Isaac Lab adapters.
