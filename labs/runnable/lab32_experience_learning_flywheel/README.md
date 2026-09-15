# Lab 32 — Experience Learning Flywheel

## 1. Hypothesis

An embodied system does not improve merely because it accumulates more autonomous experience. The value of an experience-learning flywheel depends on **which states are mined, whether corrections are semantically correct, and whether the update preserves prior competence**.

This Lab turns the common slogan

```text
rollout → failure mining → correction → retrain
```

into a falsifiable chain:

```text
base policy
→ autonomous rollout
→ observed failure states
→ experience selection
→ corrective label
→ policy update
→ new-task gain
→ old-task regression audit
```

## 2. Controlled policy model

The policy is an auditable context-to-action table rather than a neural network. This is intentional: the experiment isolates data-selection and update semantics before adding representation or optimization confounders.

There are:

- **12 new-task contexts**;
- **8 old-task contexts**;
- the base policy is correct on all old contexts;
- the base policy is correct on only the first **4/12** new contexts;
- four learning rounds;
- two autonomous rollouts per new context per round;
- a fixed correction budget of **2 new experience records per round**.

Thus every matched update condition receives exactly

\[
4\times2=8
\]

new-task experience records.

## 3. Conditions

### `no_update`

Run autonomous rollouts but never write experience back. This is the zero-update baseline and is **not** part of the matched-data comparison.

### `targeted_failure_mining`

Select currently failing contexts and attach the correct action. This is the intended flywheel.

### `random_new_data`

Use the same eight labeled examples, but select contexts from a seeded fixed permutation of the entire new-task state set. Some budget is therefore spent on states that were already correct.

### `success_only_data`

Use the same eight examples only on already-successful contexts. This tests whether more on-policy data alone repairs unvisited failure modes.

### `shuffled_corrections`

Mine actual failure contexts, but swap their corrective action labels. The **state selection is correct** while correction semantics are wrong.

### `targeted_reset_no_replay`

Mine the same failure contexts and learn the new task, but rebuild without retaining the old-task mapping. This isolates old-task regression from new-task acquisition.

## 4. Fairness structure

The most important comparison is not `targeted` versus `no_update`. It is:

```text
targeted_failure_mining
vs
random_new_data
vs
success_only_data
vs
shuffled_corrections
vs
targeted_reset_no_replay
```

All five receive **8 new experience records**.

Therefore:

- targeted vs random isolates **state-selection value**;
- targeted vs success-only isolates **failure-state coverage**;
- targeted vs shuffled isolates **corrective-label semantics**;
- targeted vs reset/no-replay isolates **retention of prior competence**.

## 5. What is logged

Every autonomous rollout writes:

```text
round
task
context
prediction
target action
success / failure
```

Each round additionally records:

- new-task success before/after update;
- old-task success before/after update;
- number of failure contexts observed;
- examples added;
- selected failure examples;
- selection precision;
- correct/wrong labels written;
- cumulative new-data volume;
- cumulative uniquely corrected contexts.

The standard runnable-lab artifacts are emitted per condition:

```text
manifest.json
steps.csv
failures.jsonl
summary.json
```

and the experiment-level outputs are:

```text
condition_metrics.csv
round_metrics.csv
selection_events.csv
experiment_summary.json
analysis.json
ANALYSIS.md
```

## 6. Core metrics

For each condition the Lab reports:

\[
\text{new-task gain},
\quad
\text{learning-curve AUC},
\quad
\text{selection precision},
\quad
\frac{\Delta \text{success}}{\text{new examples}},
\quad
\text{old-task regression}.
\]

A method cannot hide old-task forgetting behind a new-task success number.

## 7. Run

From the repository root:

```bash
python labs/runnable/lab32_experience_learning_flywheel/run.py \
  --quick \
  --output /tmp/lab32

python labs/runnable/lab32_experience_learning_flywheel/analyze.py \
  /tmp/lab32/condition_metrics.csv \
  /tmp/lab32/round_metrics.csv \
  --output-dir /tmp/lab32
```

Deterministic regression:

```bash
python labs/runnable/lab32_experience_learning_flywheel/smoke.py
```

## 8. Falsification criteria

The intended mechanism should be rejected if any of the following happens:

- targeted failure mining does not beat equal-volume random new data;
- success-only data repairs the unseen failure states equally well;
- failure states with shuffled corrective labels improve as much as correct corrections;
- targeted learning only wins because it consumes more new experience;
- learning the new task silently destroys old-task competence without being reported;
- the flywheel increases dataset volume while new-task success remains flat.

## 9. Extension path

The table policy should later be replaced by real robot policies while retaining the same experimental controls:

```text
base policy checkpoint
→ autonomous simulator / real rollouts
→ failure taxonomy + uncertainty / novelty ranking
→ human or autonomous correction
→ matched-volume random experience control
→ update
→ old-task regression suite
```

A strong simulator/real extension must report not only final success but also intervention count, marginal value per new trajectory, failure-cluster coverage, replay/storage cost, and regression on previously solved tasks.
