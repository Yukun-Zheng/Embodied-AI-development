# Lab 34 — Self-Generated Curriculum

## 1. Hypothesis

A curriculum mechanism is useful only if it selects practice goals near the agent's **current learning frontier** rather than merely choosing tasks that are easy, difficult, diverse, or numerous.

This Lab tests the causal chain

```text
current competence
→ measured learning progress
→ practice-goal selection
→ learning gain
→ evolving competence frontier
→ final capability under a fixed practice budget
```

The important distinction is:

> **More practice and better task coverage are not enough. The scheduler must bind the right learning-progress signal to the right task.**

## 2. Minimal learning system

There are nine practice goals with increasing difficulty. A single latent skill variable supports all of them. Task success probability is

\[
p_i(s)=\sigma\!\left(\frac{s-d_i}{T}\right),
\]

where

- \(s\) is current skill,
- \(d_i\) is task difficulty,
- \(T\) controls the competence transition width.

Practice gain is largest near the current competence frontier:

\[
L_i = 4p_i(1-p_i),
\]

so already-mastered tasks and tasks far beyond current ability both produce little progress.

All strategies receive exactly the same total budget: **180 practice steps**, including the same two-round warmup over all tasks.

## 3. Compared curriculum strategies

### `learning_progress`

Measure recent change in per-task success probability and practice the task with the largest progress signal, breaking ties toward the current frontier.

### `uniform`

Round-robin over all tasks after warmup. This controls total task exposure without adaptive selection.

### `fixed_curriculum`

Use the **same final per-task practice counts as uniform**, but schedule them in easy-to-hard blocks. This isolates ordering from total coverage.

### `hardest_first`

Always practice the hardest task after warmup. This is a negative control for the claim that challenge alone is a curriculum.

### `shuffled_progress`

Preserve the measured progress values but reverse their task identities before selection. This is the strongest mechanism control: the progress signal still exists, but it is attached to the wrong practice goal.

## 4. What is logged

Every practice step records:

```text
strategy
selected task / difficulty
skill before / after
selected-task success probability
measured progress score
frontier learnability
frontier distance
average competence before / after
learning gain
```

Each strategy also emits the common runnable-lab contract:

```text
manifest.json
steps.csv
failures.jsonl
summary.json
```

The experiment-level outputs are:

```text
strategy_metrics.csv
selection_counts.csv
experiment_summary.json
analysis.json
ANALYSIS.md
```

## 5. Metrics

The Lab reports:

- final average success across the task pool;
- learning-curve AUC across the full 180-step budget;
- final latent skill;
- mean learnability of selected tasks after warmup;
- mean distance between selected difficulty and current skill;
- mean per-step learning gain;
- number of mastered tasks;
- hardest mastered difficulty;
- number of distinct post-warmup tasks practiced.

This avoids reducing curriculum quality to one final scalar.

## 6. Negative controls and falsification logic

The experiment is designed to falsify several weak curriculum claims.

### Same counts, different order

`uniform` and `fixed_curriculum` use the same total number of practice steps for every task. If their learning curves differ, the difference cannot be attributed to more data or more task coverage.

### Same progress magnitudes, wrong task identity

`learning_progress` and `shuffled_progress` preserve progress-score magnitudes, but shuffled progress assigns those scores to the wrong tasks. If performance collapses, the useful mechanism is not merely "having a progress signal"; correct **progress-to-task binding** is causally necessary.

### Hardest task is not automatically most useful

`hardest_first` tests whether maximizing task difficulty is equivalent to selecting the competence frontier. It should spend most practice where success and learning gain are near zero.

## 7. Run

From the repository root:

```bash
python labs/runnable/lab34_self_generated_curriculum/run.py \
  --quick \
  --output /tmp/lab34

python labs/runnable/lab34_self_generated_curriculum/analyze.py \
  /tmp/lab34/strategy_metrics.csv \
  /tmp/lab34/selection_counts.csv \
  --output-dir /tmp/lab34
```

Deterministic regression:

```bash
python labs/runnable/lab34_self_generated_curriculum/smoke.py
```

## 8. What would falsify the intended mechanism?

The Lab should be considered unsuccessful if any of the following occurs:

- learning-progress scheduling does not outperform the fixed curriculum under the same budget;
- fixed and uniform curricula become indistinguishable despite identical counts but different ordering;
- shuffled progress-to-task binding performs almost as well as correct binding;
- learning-progress scheduling spends most post-warmup updates on already-mastered or unreachable tasks;
- the curriculum only changes the final score but not sample efficiency / learning-curve AUC.

## 9. Extension path

The M-layer toy system should later be lifted into simulator tasks where task difficulty is not a scalar but a vector over:

```text
geometry
contact
occlusion
language ambiguity
horizon
reset difficulty
embodiment constraints
```

A simulator-level extension should keep the same causal controls: equal practice budget, matched task pool, fixed curriculum, hardest-first, and shuffled progress-to-task identity.
