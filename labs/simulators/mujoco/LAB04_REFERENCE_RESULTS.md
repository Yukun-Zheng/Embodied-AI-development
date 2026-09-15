# MuJoCo Lab 04 — S-Layer CI Reference Results

> Frozen from GitHub Actions run **34977564653**, job **104409104017**, commit `2ea7e2f47cee2962d4025163f7184467e0b49531`.
>
> GitHub runner used **MuJoCo 3.13.0**. These are simulator-layer results, not real-robot validation.

## Closed-loop tracking

Both conditions start from the same 3R arm state and the same Cartesian target. The only difference is the coordinate-frame interpretation of the Cartesian error.

| Condition | Initial error | Final error | Late mean error | Max actual joint-speed norm |
|---|---:|---:|---:|---:|
| `dls_correct` | **0.4707** | **≈0.0000** | **0.0001** | 3.570 |
| `frame_mismatch` | **0.4707** | **0.4285** | **0.5928** | 4.535 |

The S-layer controller uses MuJoCo `site_xpos` and `mj_jacSite` directly. No analytic FK/Jacobian is used inside this experiment.

## Near-singularity probe

The arm is placed at

\[
q=[0, 0.01, -0.01],
\]

close to a straight configuration.

MuJoCo's Cartesian Jacobian gives:

| Metric | Value |
|---|---:|
| smallest singular value \(\sigma_{\min}\) | **0.001846** |
| Jacobian condition number | **770.1** |
| undamped pseudoinverse \(\lVert\dot q\rVert\) | **54.185 rad/s** |
| DLS \(\lambda=0.05\) \(\lVert\dot q\rVert\) | **0.074 rad/s** |

Thus the same Cartesian request produces roughly

\[
\frac{54.185}{0.074}\approx 7.3\times 10^2
\]

times more joint-speed norm under the undamped pseudoinverse than under DLS.

## What the result establishes

### 1. The Jacobian/DLS chain survives the physics-engine boundary

The control path is

```text
MuJoCo qpos / qvel
→ site_xpos
→ mj_jacSite
→ Cartesian error
→ DLS
→ desired joint velocity
→ torque servo
→ actuator limits
→ mj_step
```

and converges from **0.4707** task-space error to essentially zero.

### 2. Coordinate-frame correctness is causal

The `frame_mismatch` controller remains numerically well-defined and uses the same model, target, DLS solver and actuator path. Rotating only the Cartesian error axes prevents convergence.

Therefore

> a stable-looking optimizer or IK solver does not rescue a broken frame contract.

### 3. Damping is a real numerical/physical regularizer

The near-singular probe does not rely on a hand-written Jacobian. MuJoCo itself reports a highly ill-conditioned Jacobian, and the pseudoinverse amplifies the requested Cartesian velocity into an impractical joint-speed command while DLS regularizes it.

## Evidence boundary

This result establishes a kinematic/control mechanism in rigid-body simulation. It does not yet test:

- camera-to-world calibration;
- real encoder noise;
- joint backlash;
- motor bandwidth identification;
- collision/contact constraints;
- real-robot singularity safety.

Those belong to later S- and R-layer experiments.
