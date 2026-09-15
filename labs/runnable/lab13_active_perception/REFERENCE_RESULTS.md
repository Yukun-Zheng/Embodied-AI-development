# Lab 13 — CI-Verified Reference Observation

> These numbers come from the deterministic GitHub Actions **quick/smoke configuration**. They are mechanism sanity checks, not benchmark claims about a real robot or visual active-perception system.

## Paired quick experiment

The permanent `Executable textbook regression` runs 240 paired episodes with four view-selection policies. Hidden targets and potential observations are paired across policies, so the comparison isolates the view-selection mechanism rather than random environment draws.

| policy | target-inference accuracy | final belief entropy | sensing movement | task utility |
|---|---:|---:|---:|---:|
| `fixed_center` | 0.654 | 0.7658 | 0.000 | 0.654 |
| `random_view` | 0.863 | 0.2656 | 6.350 | 0.672 |
| `info_gain` | **0.963** | **0.0998** | **2.354** | **0.892** |
| `info_gain_shuffled_geometry` | 0.792 | 0.4716 | 1.000 | 0.762 |

## What the numbers establish

### 1. The intermediate uncertainty variable changes

Compared with random view changes, task-aware information gain reduces mean final entropy from

\[
0.2656\rightarrow0.0998.
\]

Compared with the fixed center view, the reduction is

\[
0.7658\rightarrow0.0998.
\]

This verifies that the active mechanism actually changes the uncertainty variable it claims to optimize.

### 2. The uncertainty change survives to the task decision

Final target inference improves from

\[
0.863\rightarrow0.963
\]

against random view selection, and from

\[
0.654\rightarrow0.963
\]

against the fixed-view baseline.

Therefore the experiment does not stop at “entropy went down”; the information gain is task-relevant in this toy world.

### 3. The gain is not bought by more camera travel

The information-gain policy uses

\[
\frac{2.354}{6.350}\approx0.371
\]

of the random policy's sensing travel while achieving higher accuracy. This is why the experiment reports physical view-motion cost together with information quality.

### 4. Correct view geometry is causally required

`info_gain_shuffled_geometry` keeps the real observation process and Bayesian update intact, but corrupts only the mapping used to decide which physical view should be informative.

Its accuracy drops

\[
0.963\rightarrow0.792
\]

and final entropy rises

\[
0.0998\rightarrow0.4716.
\]

This negative control attacks the mechanism directly: the benefit is not merely “using an information-gain formula”; the policy must have the correct relationship between viewpoint and expected evidence.

## Reproduce

```bash
python labs/runnable/lab13_active_perception/run.py \
  --quick \
  --output /tmp/lab13

python labs/runnable/lab13_active_perception/analyze.py \
  /tmp/lab13/policy_metrics.csv \
  --output-dir /tmp/lab13
```

The generated `analysis.json` is the machine-readable source for the four CI mechanism assertions. If the environment geometry or configuration changes, regenerate the analysis rather than copying these numbers forward.
