# Lab 33 — CI-Verified Reference Observation

> These values come from the deterministic GitHub Actions **quick/smoke configuration**. They are mechanism checks for a fixed-capacity toy continual learner, not benchmark claims about a real robot, dataset, replay system, or lifelong-learning algorithm.

## Fixed-capacity sequential experiment

The permanent `Executable textbook regression` trains the same shared network sequentially on

\[
A\rightarrow B\rightarrow C
\]

with three independent task directions in a 3-D input and only a 2-D shared representation bottleneck. Task-specific heads remove label-semantic conflict, so the main competition is shared representation capacity.

The CI quick run produced:

| method | final average accuracy | average old-task forgetting | mean current-task plasticity | BWT | extra method memory |
|---|---:|---:|---:|---:|---:|
| `naive_finetune` | 0.813 | 0.179 | **0.932** | -0.178 | 0 B |
| `replay` | 0.809 | **0.012** | 0.817 | **-0.012** | 9000 B |
| `quadratic_anchor` | **0.817** | 0.048 | 0.849 | -0.048 | **24 B** |
| `replay_shuffled_labels` | 0.697 | 0.381 | 0.951 | -0.381 | 9000 B |

All four methods keep the same network parameter count; the reported memory column contains only method-specific replay or anchor state.

## What the numbers establish

### 1. Naive sequential fine-tuning really forgets

`naive_finetune` reaches the highest clean plasticity among the non-corrupted methods, but average old-task forgetting is 0.179 and mean BWT is -0.178.

The experiment therefore creates a real stability–plasticity stress test rather than a sequence of tasks that the bottleneck can all retain for free.

### 2. Correct replay buys stability, not a free lunch

Correct replay reduces average forgetting from

\[
0.179\rightarrow0.012,
\]

roughly a 15× reduction, while BWT moves from -0.178 to -0.012.

But plasticity falls from 0.932 to 0.817. Under fixed representational capacity, preserving old task directions consumes capacity that could otherwise adapt fully to the current task.

So the scientific statement is not

\[
\text{replay}=\text{strictly better}.
\]

It is

\[
\text{replay shifts the stability–plasticity operating point}.
\]

### 3. Regularization exposes a different point on the same frontier

`quadratic_anchor` uses only 24 B of anchor state in this toy model. It reduces forgetting to 0.048 while retaining plasticity 0.849.

That makes it more memory-efficient than raw replay here, but less stable than replay. The result is useful because it turns continual learning into an explicit multi-objective comparison:

\[
(\text{retention},\text{plasticity},\text{memory},\text{compute}).
\]

### 4. Replay content is causally necessary

`replay_shuffled_labels` uses the **same 9000 B replay budget** and the same replay update structure as correct replay, but its old labels are deterministically corrupted.

Its average forgetting rises to 0.381 and final average accuracy falls to 0.697, substantially worse than naive fine-tuning.

This negative control rules out the explanation that replay works merely because it performs more optimization steps or stores more data. The retained information must be semantically correct.

### 5. Parameter growth is not hiding the result

The CI analyzer verifies

\[
\Delta N_{parameter}=0
\]

for every method. Stability gains therefore cannot be explained by adding task-specific adapters, expanding the trunk, or silently allocating new model capacity.

## CI mechanism assertions

The runner verified all of the following:

```text
naive forgetting exists
+ correct replay reduces forgetting
+ replay has a plasticity cost under fixed capacity
+ quadratic anchoring trades plasticity for stability
+ corrupted replay destroys retention
+ parameter count stays fixed
+ method-specific memory cost is explicit
```

These are mechanism assertions, not leaderboard claims.

## Scientific scope

The experiment supports a narrow statement:

> Under a deliberately capacity-limited shared representation, continual learning is a Pareto problem rather than a single final-accuracy problem. Retention mechanisms can reduce forgetting, but they consume memory and/or plasticity; replay succeeds only when the stored old-task information is correct.

It does **not** establish that replay or quadratic anchoring is optimal for large neural networks, robot policies, non-stationary embodiment changes, or real-world lifelong learning.

## Reproduce

```bash
python labs/runnable/lab33_continual_learning/run.py \
  --quick \
  --output /tmp/lab33

python labs/runnable/lab33_continual_learning/analyze.py \
  /tmp/lab33/method_metrics.csv \
  --output-dir /tmp/lab33
```

Each method also writes `performance_matrix.csv` and `probe_matrix.csv`, so stage-by-stage forgetting and forward-transfer probes can be reanalyzed without relying on the summary table.

`analysis.json` is the machine-readable source for the permanent CI assertions. If task directions, bottleneck dimension, replay budget, regularization strength, or optimization schedule change, regenerate the analysis rather than copying these numbers forward.
