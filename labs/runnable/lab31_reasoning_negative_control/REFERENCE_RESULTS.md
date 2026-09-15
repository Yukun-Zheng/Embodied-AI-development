# Lab 31 — CI-Verified Reference Observation

> These values come from the deterministic GitHub Actions **quick/smoke configuration**. They are mechanism checks in a symbolic executable world, not claims that a particular LLM/VLM/VLA reasons correctly on a real robot.

## CI configuration

The permanent `Executable textbook regression` evaluates **300 shared episodes per condition**. Each episode varies the required key, key location, target package, target bin and whether the cabinet is locked.

All plan-based controls use the same executable operator vocabulary and matched mean plan length. Plans are replayed through the true transition function; success is never assigned by the planner itself.

## Runner observations

| condition | real success | locked success | mean action validity | success in planner's own model |
|---|---:|---:|---:|---:|
| `correct_plan` | **1.000** | **1.000** | **1.000** | **1.000** |
| `no_plan` | 0.190 | 0.000 | 0.291 | — |
| `random_plan` | 0.000 | 0.000 | 0.271 | — |
| `fluent_wrong_plan` | 0.190 | 0.000 | **0.705** | **1.000** |
| `shuffled_binding` | 0.000 | 0.000 | 0.527 | — |

The overall `0.190` success of `no_plan` and `fluent_wrong_plan` comes from the easy episodes in which the cabinet starts unlocked. The CI analyzer separately verifies that those controls succeed on unlocked episodes while both fail on locked episodes.

## What the numbers establish

### 1. A real planning horizon exists

On locked episodes:

\[
S_{correct}=1.000,
\qquad
S_{no\ plan}=0.000.
\]

The myopic baseline can solve easy unlocked episodes but cannot discover the prerequisite chain

```text
required key
→ unlock
→ open
→ retrieve package
→ deliver to requested bin
```

Therefore the gain is not merely task difficulty or motor syntax: it appears specifically when multi-step dependency reasoning is required.

Across all 300 episodes, the causal-planning gain is

\[
1.000-0.190=\mathbf{0.810}.
\]

### 2. Internal coherence is not physical correctness

`fluent_wrong_plan` uses the same BFS algorithm as `correct_plan`, but under a coherent false causal model that swaps which key unlocks the cabinet.

Inside that wrong model:

\[
S_{internal}=1.000.
\]

When the exact same plans are executed in the true world:

\[
S_{real}=0.190,
\]

with locked-episode success equal to zero. The resulting reality gap is

\[
\Delta_{model\rightarrow world}
=1.000-0.190
=\mathbf{0.810}.
\]

This is the executable analogue of a fluent explanation that is fully self-consistent but causally wrong.

### 3. The wrong plan is not just random garbage

Mean action validity is:

\[
V_{fluent\ wrong}=0.705,
\qquad
V_{random}=0.271.
\]

So the wrong-model plan is more executable by

\[
0.705-0.271=\mathbf{0.434}.
\]

It preserves much more local structure than a random permutation, yet still fails the latent causal dependency. This separates **local plausibility / executability** from **global causal correctness**.

### 4. Ordering matters

`random_plan` reuses the correct plan's action multiset but permutes the order. Its success is **0.000**.

Because action vocabulary and plan length are controlled, the failure isolates temporal/prerequisite structure rather than planner output size.

### 5. Entity binding matters

`shuffled_binding` preserves the plan skeleton and navigation ordering while swapping key, package and bin referents. Its success is also **0.000**.

Thus an embodied reasoning trace cannot be evaluated only at the level of abstract verbs or subgoal shape; the symbols must stay grounded to the correct physical entities.

## CI mechanism assertions

The permanent runner verifies all of the following:

```text
correct executable plan succeeds
+ locked dependency defeats no-plan control
+ easy unlocked episodes do not require reasoning
+ fluent-wrong plan is internally coherent
+ fluent-wrong plan fails in the true locked world
+ fluent-wrong actions are much more valid than random actions
+ random ordering fails
+ shuffled entity binding fails
+ plan output budget is matched
+ correct order and binding are jointly necessary
```

The smoke test first checks raw metrics and artifacts, then invokes the independent analyzer. The analyzer therefore cannot pass solely by restating its own outputs.

## Scientific scope

The supported claim is deliberately narrow:

> A reasoning module earns behavioral credit only when the causal model, ordering and entity bindings represented by its intermediate plan survive execution in the true environment. Internal coherence, linguistic fluency or local action validity alone are insufficient.

The experiment does **not** establish that symbolic BFS is a preferred robot-reasoning architecture, nor that current language models do or do not possess physical reasoning. It provides a falsifiable evaluation pattern that can be lifted into simulator and real-robot systems.

## Reproduce

```bash
python labs/runnable/lab31_reasoning_negative_control/run.py \
  --quick \
  --output /tmp/lab31

python labs/runnable/lab31_reasoning_negative_control/analyze.py \
  /tmp/lab31/condition_metrics.csv \
  --output-dir /tmp/lab31
```

Inspect `steps.csv`, `episodes.csv` and `plans.jsonl` to trace exactly where an apparently coherent plan stops matching the true world.

If the transition model, episode distribution, planner, operator set or control construction changes, regenerate the analysis rather than copying these numbers forward.
