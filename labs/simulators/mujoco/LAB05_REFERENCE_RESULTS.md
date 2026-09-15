# MuJoCo Lab 05 — S-Layer CI Reference Results

> Frozen from GitHub Actions run **34978602043**, job **104413984284**, commit `f28712c7eba839eeb09c5617f5e10d4251ec5536`.
>
> GitHub runner used **MuJoCo 3.13.0**. These are simulator-layer dynamics results, not real-robot validation.

## Dynamics identity under test

For five nontrivial 3R-arm states with different \(q\), \(\dot q\) and applied generalized force, the experiment reconstructs MuJoCo forward acceleration from

\[
M(q)\ddot q
=
\tau_{\mathrm{applied}}
+	au_{\mathrm{actuator}}
+	au_{\mathrm{passive}}
-h(q,\dot q).
\]

The dense joint-space mass matrix is expanded from MuJoCo's internal inertia representation and compared against engine `qacc`.

## CI results

| Model variant | RMSE | Relative RMSE | Max absolute acceleration error |
|---|---:|---:|---:|
| `matched` | **≈ 0** | **4.439e-16** | **≈ 0** |
| `wrong_mass_scale` (`0.6 M`) | **61.8839** | **0.66667** | **129.2707** |
| `omit_passive` | **12.6989** | **0.13680** | **31.8063** |

Structural checks for the matched engine model:

| Check | CI value |
|---|---:|
| max mass-matrix symmetry error | **0.000e+00** |
| minimum mass-matrix eigenvalue | **0.003684** |
| mean dynamics residual | **2.256e-15** |

## What the simulator result establishes

### 1. MuJoCo forward dynamics can be reconstructed at machine precision

The matched model reaches relative acceleration RMSE

\[
4.439\times 10^{-16},
\]

while the direct rigid-body residual is approximately

\[
2.256\times 10^{-15}.
\]

This verifies that the generalized-force bookkeeping used by the textbook is consistent with the engine at the tested unconstrained states.

### 2. Inertia mismatch has a large causal effect

Replacing the true mass matrix with

\[
\hat M = 0.6M
\]

while holding the same physical state and forces fixed increases relative acceleration error to **0.667**.

The failure mechanism is therefore explicit:

```text
same q / qdot / applied force
→ wrong inertia model
→ wrong acceleration prediction
→ downstream planning / control error
```

### 3. Passive dynamics are not a bookkeeping detail

Dropping joint damping / passive generalized force raises relative RMSE to **0.137**. This is substantially smaller than the 40% inertia error but still many orders of magnitude above the matched reconstruction.

Thus a dynamics model can have the correct rigid-body mass structure while still being materially wrong because actuator/passive terms are missing.

### 4. The tested mass matrix has the expected structure

Across the five probe states the expanded mass matrix is exactly symmetric at the recorded precision, and its smallest observed eigenvalue remains positive:

\[
\lambda_{\min}(M)=0.003684.
\]

This provides a concrete simulator-side check of the positive-definite joint-space inertia used throughout the dynamics chapters.

## Engineering note: MuJoCo 3.13 Python binding

The first two CI attempts exposed a binding-version issue rather than a physics issue:

- older bindings/documentation commonly expose the packed inertia as `qM` and use a C-like `mj_fullM(model, dst, packed)` call;
- the MuJoCo 3.13 Python wheel used by hosted CI exposes the current binding path as `mj_fullM(model, data, dst)`.

The textbook adapter supports both signatures so the scientific experiment is not accidentally tied to one Python wheel's field naming.

## Evidence boundary

This S-layer result establishes dynamics consistency and controlled model mismatch inside MuJoCo. It does not yet establish:

- identified real-robot inertial parameters;
- motor torque calibration;
- gearbox friction / backlash;
- contact-model fidelity;
- real sensor delays;
- sim-to-real controller robustness.

The next experiment should inject these same matched/mismatched models into a closed-loop computed-torque or MPC controller, measuring how acceleration-model error becomes tracking, energy, saturation or stability error.
