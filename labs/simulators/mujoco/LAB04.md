# MuJoCo S-Layer — Lab 04 Numerical IK

This experiment lifts the textbook's kinematics/Jacobian/Damped Least Squares chain into MuJoCo.

## 1. Physics and kinematics boundary

The simulator model is a 3R planar arm with three revolute joints and a MuJoCo end-effector site `ee`.

The closed loop is:

```text
MuJoCo qpos / qvel
→ site_xpos
→ mj_jacSite
→ Cartesian target error
→ Damped Least Squares
→ desired joint velocity
→ torque servo
→ actuator limits
→ mj_step
→ new arm configuration
```

No analytic forward kinematics or Jacobian is used inside the S-layer controller. MuJoCo is the source of truth for both end-effector position and Jacobian.

## 2. Main tracking conditions

### `dls_correct`

The Cartesian error is interpreted in the correct world-frame x/y axes and mapped through

\[
\dot q = J^\top\left(JJ^\top+\lambda^2I\right)^{-1}v,
\]

with \(\lambda=0.06\).

### `frame_mismatch`

Everything is held fixed except the Cartesian error is intentionally rotated by +90° before the DLS solve. This is a coordinate-frame negative control.

The purpose is to show that a numerically valid controller can still be physically wrong when the frame contract is wrong.

## 3. Near-singularity probe

A separate probe places the arm near a straight configuration:

```text
q = [0.0, 0.01, -0.01]
```

and requests a Cartesian velocity mostly along the poorly conditioned direction.

It compares:

- Moore–Penrose pseudoinverse;
- DLS with \(\lambda=0.05\).

The probe records singular values, Jacobian condition number and joint-velocity norm. This isolates regularization from the full closed-loop dynamics.

## 4. What is measured

Tracking rollouts log:

- end-effector x/y;
- target x/y;
- world-frame error;
- error actually passed to the solver;
- minimum Jacobian singular value;
- joint positions;
- actual and desired joint-velocity norm;
- torque norm;
- saturation events.

The singularity probe writes:

```text
singularity_probe.csv
```

with the exact MuJoCo Jacobian-derived pseudoinverse and DLS responses.

## 5. Falsification logic

The intended mechanism fails if:

- correct-frame DLS cannot reduce task-space error;
- the frame-mismatch controller performs almost as well;
- the chosen probe is not actually ill-conditioned;
- the pseudoinverse does not amplify the near-singular Cartesian request;
- DLS does not substantially reduce the required joint-velocity norm.

## 6. Run

```bash
python -m pip install -r labs/simulators/mujoco/requirements.txt
python labs/simulators/mujoco/lab04_ik.py --output /tmp/mujoco-lab04
python labs/simulators/mujoco/lab04_smoke.py
```

The CI path is headless and does not require a renderer.

## 7. Evidence boundary

This S-layer experiment validates the kinematics/Jacobian mechanism inside a rigid-body simulator. It does not yet validate camera calibration, actuator identification, real joint backlash, network latency or real-robot safety.
