# Lab 25 — CI-Verified Reference Observation

> These observations come from the deterministic GitHub Actions **quick/smoke configuration**. The first full reference run passed in `Executable textbook regression` run **34965158350**, job **104367762414**, at commit `d72615351d0e25725933652cdaa884e47b1d5891`.

## CI configuration

The quick reference uses **160 paired scenes** under one fixed instruction. Every policy receives the same representation schema:

```text
fixed instruction
target image coordinate
camera yaw
target texture id
background id
irrelevant distractor coordinate
```

The observational/base distribution intentionally makes target appearance and distractor location predictive of the real target, so all four policies can achieve perfect base success for different reasons.

Each base scene is then paired with six one-factor interventions:

```text
target_position
texture_swap
background_swap
camera_angle
distractor_move
geometry_shuffle
```

The point is to measure **action and task sensitivity**, not merely whether a feature can be decoded from a representation.

## CI-verified reference observations

| policy | base | target position | position response gain | texture swap | camera angle | distractor move | geometry shuffle | base geometry probe RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `geometry_causal` | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** | **0.000e+00** |
| `appearance_shortcut` | **1.000** | **0.000** | **0.000** | **0.000** | **1.000** | **1.000** | **1.000** | **0.000e+00** |
| `camera_unaware` | **1.000** | **1.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.000** | **0.000e+00** |
| `distractor_shortcut` | **1.000** | **0.000** | **0.000** | **1.000** | **1.000** | **0.000** | **1.000** | **0.000e+00** |

The permanent analyzer additionally requires:

- `geometry_causal` to remain invariant to **background** swaps as well as texture swaps;
- appearance texture/background interventions to move shortcut actions by a nontrivial amount;
- camera intervention to move the camera-unaware action by a nontrivial amount;
- distractor intervention to move the distractor-shortcut action by a nontrivial amount;
- target-geometry corruption to strongly move the causal geometry action.

## What the observations establish

### 1. A normal benchmark can be maximally non-diagnostic

All four policies score **1.000** on the base distribution.

Yet their mechanisms are mutually incompatible:

```text
true target geometry
appearance shortcut
camera-frame misuse
irrelevant distractor shortcut
```

Therefore observational success alone cannot establish which visual variable caused the action.

### 2. Probe-decodable information is not evidence of policy use

The strongest counterexample is `appearance_shortcut`.

Its representation contains enough target geometry for the external geometry probe to achieve **0.000e+00 RMSE**. Nevertheless:

- moving the true target gives success **0.000**;
- the action response gain to true target displacement is **0.000**;
- corrupting the target-geometry token leaves shortcut success at **1.000**;
- changing appearance breaks the action.

Thus:

\[
\text{information decodable from } z
\not\Rightarrow
\text{policy causally uses that information}.
\]

### 3. Task-relevant visual sensitivity should follow the physical variable

For `geometry_causal`, moving the target gives:

\[
\frac{\Delta a}{\Delta x_{target}}=1.000,
\]

and task success remains **1.000**.

The same policy remains successful under texture, background, camera and distractor interventions because those interventions do not change the desired world target.

This separates desired sensitivity from desired invariance.

### 4. Geometry corruption is a stronger test than feature visualization

`geometry_causal` falls from base success **1.000** to **0.000** when the target-geometry token is replaced by geometry from a distant target bin.

The intervention therefore demonstrates that the geometry path is not merely present: changing it changes the action and downstream outcome.

By contrast, appearance and distractor shortcuts remain successful under the same geometry corruption because they do not read the corrupted target-geometry path.

### 5. Camera pose is part of visual action semantics

`camera_unaware` is perfect under the canonical camera but drops to **0.000** under camera yaw.

It still tracks target-position changes at the canonical camera with response gain **1.000**, so the failure is not lack of geometric sensitivity in general. The failure is specifically the missing frame transform between image coordinate and world action coordinate.

### 6. Irrelevant objects can become causal shortcuts

`distractor_shortcut` is perfect on the base distribution because distractor position is correlated with target position. It fails completely when only the target moves and also fails completely when only the irrelevant distractor moves.

The latter is especially diagnostic: the physical task target is unchanged, yet the action follows an irrelevant scene element.

## CI mechanism assertions

The permanent smoke test verifies:

```text
all policy variants match the observational base benchmark
+ target geometry is probe-decodable for every policy
+ correct geometry policy follows physical target displacement
+ correct geometry policy is invariant to appearance/background nuisance
+ correct geometry policy is camera-frame aware
+ correct geometry policy ignores distractor motion
+ geometry corruption breaks the causal geometry path
+ appearance shortcut ignores real target motion despite perfect geometry probe
+ texture/background swaps expose appearance dependence
+ camera yaw exposes frame misuse
+ distractor motion exposes irrelevant-object shortcut
+ raw manifests / steps / failures / summaries remain reconstructible
```

The independent analyzer recomputes these relations from `policy_metrics.csv` rather than trusting the prose interpretation.

## Scientific scope

The supported claim is narrow:

> In this controlled representation/action experiment, task-relevant visual information being linearly or analytically decodable from a representation is insufficient evidence that the action head uses it. Paired interventions on physical geometry, appearance, camera frame, distractors and the geometry path itself can separate causal visual use from observational shortcuts.

This is **not** a claim about any particular real VLA checkpoint. The simulator / real-image extension must apply the same intervention logic to actual images and actions: object translation, texture replacement, background compositing, camera-extrinsic perturbation, distractor insertion/removal and representation-path corruption, while measuring both action distribution and physical task success.

## Reproduce

```bash
python labs/runnable/lab25_visual_intervention/run.py \
  --quick \
  --output /tmp/lab25

python labs/runnable/lab25_visual_intervention/analyze.py \
  /tmp/lab25/policy_metrics.csv \
  --output-dir /tmp/lab25
```

The key audit target is the pair `appearance_shortcut` + geometry probe: if a future implementation can no longer maintain high probe quality while failing the target-position intervention, the intended information-availability-versus-policy-use counterexample has changed and CI should fail.
