# MuJoCo Lab 06 — S-Layer CI Reference Results

> Frozen from GitHub Actions run **34976737909**, job **104406246727**, commit `d282d0ec6fc4757cb5378d18a7f04bb50394530c`.
>
> GitHub runner installed **MuJoCo 3.13.0** and executed the physics engine headlessly. These are S-layer simulator results, **not real-robot validation**.

## Reference physics setup

- 1-DOF slider joint;
- mass = 1 kg;
- joint damping = 0.2;
- joint range = `[-2, 2]`;
- motor command range = `[-20, 20]`;
- MuJoCo timestep = 0.002 s;
- target position = 1.0;
- rollout duration = 2.5 s;
- shared external force pulse:
  - start = 0.80 s;
  - end = 0.95 s;
  - force = -8 N.

The only state transition is `mujoco.mj_step`.

## CI results

| Condition | Final error | Late mean error | Saturation fraction | Peak \(|q|\) |
|---|---:|---:|---:|---:|
| `no_feedback` | **2.6647** | **2.1998** | 0.000 | 1.663 |
| `pd_feedback` | **0.0010** | **0.0079** | 0.000 | 1.001 |
| `wrong_sign_feedback` | **3.0006** | **3.0006** | **0.999** | **2.062** |

For `pd_feedback`, the error immediately after the shared disturbance window was approximately **0.0619**, while final error recovered to **0.0010**.

## What the simulator result establishes

### 1. The M-layer feedback mechanism survives an independent physics engine

The PD controller does not merely solve a hand-written numerical toy. It receives MuJoCo `qpos / qvel`, writes an actuator command, experiences the same injected physical force, and recovers through MuJoCo integration.

### 2. Open loop and feedback are physically distinguishable

With no feedback, the system neither tracks the target nor rejects the disturbance:

\[
|e_T| = 2.6647.
\]

With PD feedback:

\[
|e_T| = 0.0010.
\]

The simulator therefore reproduces the qualitative closed-loop claim from the minimal control chapter without sharing its state-transition implementation.

### 3. Feedback sign is a causal mechanism, not a cosmetic parameter

Reversing the signs drives the motor into saturation for approximately **99.9%** of the rollout and pushes the joint into its finite-range boundary region.

The failure mode is therefore explicit:

```text
wrong error sign
→ positive feedback
→ actuator saturation
→ joint-limit region
→ large persistent tracking error
```

### 4. Recovery is measured after a real simulator disturbance

The PD controller sees a finite external body-force pulse. The error near disturbance end is much larger than the final error:

\[
0.0619 \rightarrow 0.0010,
\]

so the result is a recovery observation rather than only nominal set-point tracking.

## Evidence boundary

This result establishes only:

> a controlled feedback mechanism remains valid after crossing from the M-layer numerical implementation into MuJoCo rigid-body simulation.

It does **not** establish:

- real actuator fidelity;
- sensor latency / quantization;
- motor current or thermal limits;
- real friction / backlash;
- hardware safety;
- sim-to-real transfer.

Those belong to later S- and R-layer validation.
