# MuJoCo Simulator Layer

`labs/simulators/mujoco/` is the first physics-engine backend for the textbook's **S-layer** experiments.

Its role is not to replace transparent M-layer mechanism tests. It asks a second question:

> Does a mechanism that survives analytical / toy falsification still hold when state transitions are produced by an independent rigid-body physics engine?

## Current CI-verified S-layer experiments

### Lab 04 — Numerical IK

[`LAB04.md`](LAB04.md) · [`CI reference`](LAB04_REFERENCE_RESULTS.md)

```text
MuJoCo qpos / qvel
→ site_xpos + mj_jacSite
→ DLS Cartesian control
→ torque-limited actuators
→ mj_step
```

Mechanism controls:

- correct Cartesian frame vs deliberate frame mismatch;
- near-singular Jacobian;
- undamped pseudoinverse vs damped least squares.

Reference highlights on MuJoCo 3.13.0:

- correct DLS: task-space error `0.4707 → ~0`;
- frame mismatch: final error `0.4285`;
- near-singular `σ_min = 0.001846`;
- pseudoinverse joint-speed norm `54.185 rad/s` vs DLS `0.074 rad/s`.

### Lab 05 — Rigid-Body Dynamics

[`LAB05.md`](LAB05.md) · [`CI reference`](LAB05_REFERENCE_RESULTS.md)

```text
MuJoCo q / qdot / applied force
→ M(q) + bias + passive force
→ reconstructed qddot
→ engine qacc comparison
```

Mechanism controls:

- matched engine dynamics;
- `0.6 M` inertia mismatch;
- omitted passive damping.

Reference highlights on MuJoCo 3.13.0:

- matched relative RMSE `4.439e-16`;
- wrong-mass relative RMSE `0.667`;
- omit-passive relative RMSE `0.137`;
- mass-matrix symmetry error `0`;
- minimum observed inertia eigenvalue `0.003684`;
- rigid-body residual `2.256e-15`.

### Lab 06 — Feedback Control

[`LAB06.md`](LAB06.md) · [`CI reference`](LAB06_REFERENCE_RESULTS.md)

```text
MuJoCo qpos / qvel
→ PD feedback
→ actuator saturation
→ external force pulse
→ mj_step
→ recovery
```

Mechanism controls:

- no feedback;
- correct-sign PD;
- wrong-sign positive feedback.

Reference highlights on MuJoCo 3.13.0:

- no-feedback final error `2.6647`;
- PD final error `0.0010`;
- disturbance-end error `0.0619 → 0.0010` final;
- wrong-sign controller saturation fraction `0.999`.

Together, Labs 04–06 form the first complete S-layer foundation:

```text
kinematics / Jacobian
→ rigid-body dynamics
→ closed-loop feedback
```

## Install

```bash
python -m pip install -r labs/simulators/mujoco/requirements.txt
```

No renderer is required for hosted CI; these tests use headless physics only.

## Run

```bash
python labs/simulators/mujoco/lab04_smoke.py
python labs/simulators/mujoco/lab05_smoke.py
python labs/simulators/mujoco/smoke.py
```

## Evidence contract

Every lightweight MuJoCo experiment should preserve the same evidence discipline as `labs/runnable/`:

```text
raw simulator state
+ action / controller command
+ physical transition
+ negative control
+ failure event
+ summary metrics
+ deterministic smoke relation
```

Exact engine-version-specific floating-point coordinates should not become textbook claims unless the exact value itself is scientifically material. Prefer robust mechanism relations.

## Next extensions

The 04/05/06 foundation is now stable enough to move beyond isolated primitives. Priorities are:

1. feed matched vs mismatched Lab 05 dynamics into the **same computed-torque / MPC controller**;
2. add contact-rich manipulation rather than only free-space joints;
3. connect the S-layer contract to RoboTwin for Lab 25 / 37 and Capstone 1;
4. connect Isaac Lab for locomotion / humanoid tasks;
5. keep hosted CI limited to lightweight headless physics and adapter dry-runs.
