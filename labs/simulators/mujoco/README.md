# MuJoCo S-Layer — Lab 06 Feedback Control

This is the first **S-layer** experiment in the textbook. It lifts the M-layer feedback-control idea out of a hand-written toy integrator and into the MuJoCo physics engine.

## 1. Physics boundary

The adapter uses a 1-DOF slider with:

- MuJoCo rigid-body integration;
- a physical slider joint with damping and finite range;
- a motor actuator with command saturation;
- `qpos / qvel` as simulator state;
- an injected external body force;
- `mj_step` as the only state transition.

The closed loop is therefore

```text
MuJoCo qpos / qvel
→ controller
→ actuator ctrl
→ external disturbance
→ mj_step
→ new physical state
```

## 2. Conditions

### `no_feedback`

Actuator command is zero. The system cannot track the target and the injected force moves it away.

### `pd_feedback`

\[
u_t = K_p(q^*-q_t)-K_d\dot q_t.
\]

The controller must reach the target, absorb the same external disturbance, and recover.

### `wrong_sign_feedback`

The feedback signs are reversed. This is a controller-mechanism negative control: it should drive the actuator into saturation and push the slider toward its joint boundary rather than stabilizing the target.

## 3. Shared disturbance

All conditions receive the same force pulse:

```text
t = 0.80 s → 0.95 s
external force = -8 N
```

The actuator range is fixed to `[-20, 20]`, and the joint range is `[-2, 2]`.

## 4. Outputs

Every condition reuses the runnable-lab artifact contract:

```text
runs/<condition>/
├── manifest.json
├── steps.csv
├── failures.jsonl
└── summary.json
```

The experiment also writes:

```text
condition_metrics.csv
experiment_summary.json
```

Step-level logs include time, `q`, `qdot`, raw/saturated control, disturbance force and tracking error.

## 5. CI assertions

The headless MuJoCo smoke test checks only relations that should be robust across compatible MuJoCo 3.x versions:

- PD final error is small;
- PD late-window error is small after the disturbance;
- PD decisively beats no-feedback;
- correct-sign PD decisively beats wrong-sign feedback;
- wrong-sign feedback spends substantially more time saturated and reaches the joint-limit region;
- all physical quantities remain finite;
- raw simulator artifacts are emitted.

It does **not** freeze a single engine-version-specific final coordinate as a scientific claim.

## 6. Run

```bash
python -m pip install -r labs/simulators/mujoco/requirements.txt
python labs/simulators/mujoco/lab06_control.py --output /tmp/mujoco-lab06
python labs/simulators/mujoco/smoke.py
```

No renderer is required; the CI path runs physics only.

## 7. Why this is an S-layer result

The M-layer `code/minimal/control.py` establishes the feedback mechanism in a transparent numerical system. This MuJoCo adapter adds an independent simulator implementation of:

- state representation;
- actuator saturation;
- joint constraints;
- body force disturbance;
- engine integration.

Agreement between the two layers is stronger evidence than either alone, while still not constituting real-robot validation.

## 8. Next extensions

The same backend should next support:

1. Lab 04 Numerical IK on a multi-joint arm;
2. Lab 05 rigid-body dynamics comparison;
3. Lab 06 impedance / computed-torque variants;
4. contact-rich manipulation and locomotion experiments.
