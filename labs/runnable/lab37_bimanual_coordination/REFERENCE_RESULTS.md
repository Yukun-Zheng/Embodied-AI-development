# Lab 37 — CI-Verified Reference Observation

> These observations come from the deterministic GitHub Actions **quick/smoke configuration**. The first full reference run passed in `Executable textbook regression` run **34963834474**, job **104363495493**, at commit `571665234a54a8641a1ed311ae8200abdf933d95`.

## CI configuration

The quick reference uses **120 paired episodes**. Every condition sees the same episode-wise:

```text
left actuator gain
right actuator gain
target object center
short unilateral left-arm disturbance
shared spring-damper object dynamics
```

Only the control organization changes.

The physical success criterion requires all three:

```text
final object center reaches target
+ final arm separation returns near nominal
+ transient shared-object strain never crosses the limit
```

So the reference does not define bimanual success as “both endpoints eventually arrived.”

## CI-verified reference metrics

| condition | success | mean center RMSE | mean relative RMSE | mean peak strain | mean episode p95 internal force |
|---|---:|---:|---:|---:|---:|
| `independent_world` | **0.4333** (52/120) | **0.0493** | **0.0072** | **0.0277** | **1.005** |
| `midpoint_only` | **0.0417** (5/120) | **0.0425** | **0.0117** | **0.0420** | **1.586** |
| `relative_coordinated` | **0.9583** (115/120) | **0.0435** | **0.0037** | **0.0151** | **0.506** |
| `wrong_relative_sign` | **0.0000** (0/120) | **0.2307** | **0.6997** | **1.0711** | **58.836** |

The smoke test also verifies that the coordinated condition does not obtain its gain by receiving a much larger effort budget: its mean total effort must remain below **1.10×** the independent controller's.

## What the observations establish

### 1. Independent endpoint tracking is not sufficient

The two independent world-frame controllers eventually drive their endpoints close to the correct final positions, but only **52/120** episodes satisfy the transient shared-object strain constraint.

This is the core distinction:

```text
individual endpoint convergence
≠
shared-object coordination
```

Actuator heterogeneity and a one-sided disturbance create a differential mode that independent endpoint loops do not suppress as directly as an explicit relative-coordinate controller.

### 2. Midpoint tracking is a deliberately strong counterexample

`midpoint_only` has **lower center RMSE (0.0425)** than `independent_world` **(0.0493)**, yet its bimanual success collapses to **5/120** and its relative RMSE rises to **0.0117**.

Therefore a benchmark that reports only object-center trajectory error can rank a physically worse bimanual controller as better.

The missing variable is the shared constraint:

\[
r=x_R-x_L.
\]

### 3. Relative-coordinate feedback changes the physical outcome

The complete coordinated controller explicitly regulates common and differential modes:

\[
c=\frac{x_L+x_R}{2},
\qquad
r=x_R-x_L.
\]

Compared with independent world-frame tracking, CI observes:

- success: **0.433 → 0.958**;
- relative RMSE: **0.0072 → 0.0037**;
- mean peak strain: **0.0277 → 0.0151**;
- mean episode p95 internal force: **1.005 → 0.506**;
- center RMSE also improves slightly rather than being traded away.

Thus the coordination gain propagates through the intended intermediate variable—relative state—into a shared-object physical consequence.

### 4. The sign of the relative mechanism is causally necessary

`wrong_relative_sign` receives the same state variables and uses the same relative-control branch, but its differential correction reinforces rather than cancels separation error.

The result is intentionally catastrophic:

- success **0/120**;
- relative RMSE **0.6997**;
- mean peak strain **1.0711**;
- mean episode p95 internal force **58.836**.

This rules out the explanation that the gain comes merely from “adding another controller term.” The geometry/sign of the relative coordinate is part of the mechanism.

### 5. Internal load is a first-class bimanual metric

The spring-damper coupling produces an internal force

\[
F_{int}=k(r-r_0)+b(\dot x_R-\dot x_L).
\]

A controller can have acceptable center tracking while generating large internal load. CI therefore requires relative feedback to reduce both deformation and internal force, not only final task position error.

## CI mechanism assertions

The permanent smoke test verifies:

```text
paired actuator / disturbance trials are reused across conditions
+ coordinated shared-object success > 0.90
+ independent control exposes shared-object failures
+ coordination improves success by > 0.40
+ relative feedback reduces relative RMSE
+ relative feedback reduces peak strain
+ relative feedback reduces internal force
+ center tracking is not sacrificed
+ midpoint-only gives a center-good / relative-bad counterexample
+ wrong relative sign destroys coordination
+ coordinated gain is not explained by a much larger effort budget
+ raw manifests / steps / failures / summaries remain reconstructible
```

The independent analyzer recomputes these relations from `condition_metrics.csv` rather than trusting the prose interpretation.

## Scientific scope

The supported claim is narrow:

> In this paired compliant shared-object mechanism experiment, explicit relative-coordinate feedback is causally useful for suppressing differential deformation and internal load under actuator heterogeneity and unilateral disturbance; independent endpoint convergence or good midpoint tracking alone is insufficient evidence of bimanual coordination.

This is **not** a real-robot bimanual manipulation result. Simulator and hardware validation must add SE(3) relative pose, contact wrench, grasp geometry, object inertia, impedance/force control, saturation, collision, perception delay and safety constraints.

## Reproduce

```bash
python labs/runnable/lab37_bimanual_coordination/run.py \
  --quick \
  --output /tmp/lab37

python labs/runnable/lab37_bimanual_coordination/analyze.py \
  /tmp/lab37/condition_metrics.csv \
  --output-dir /tmp/lab37
```

Inspect `steps.csv` together with `failures.jsonl` when an episode ends near the target but still fails: the transient strain crossing is precisely the failure mode that final endpoint error alone would hide.
