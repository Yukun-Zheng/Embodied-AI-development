# MuJoCo Simulator Layer

`labs/simulators/mujoco/` is the first physics-engine backend for the textbook's **S-layer** experiments.

Its role is not to replace transparent M-layer mechanism tests. It asks a second question:

> Does a mechanism that survives analytical / toy falsification still hold when state transitions are produced by an independent rigid-body physics engine?

## Current S-layer experiments

### Lab 04 — Numerical IK

[`LAB04.md`](LAB04.md)

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

The first CI-frozen S-layer reference used **MuJoCo 3.13.0**.

## Install

```bash
python -m pip install -r labs/simulators/mujoco/requirements.txt
```

No renderer is required for hosted CI; these tests use headless physics only.

## Run

```bash
python labs/simulators/mujoco/lab04_smoke.py
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

1. freeze Lab 04 after CI validation;
2. Lab 05 dynamics / model-mismatch comparison;
3. Lab 06 impedance / computed-torque extension;
4. multi-joint/contact-rich manipulation;
5. locomotion after the control/dynamics foundation is stable.
