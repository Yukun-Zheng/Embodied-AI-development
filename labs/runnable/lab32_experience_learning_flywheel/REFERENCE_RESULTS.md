# Lab 32 — CI Reference Results

> Frozen from GitHub Actions run **34975371236**, job **104401636954**, commit `dcd2200a2b6ac4f52790936a8697245e6fcc9387`.
>
> These are deterministic M-layer mechanism results for the reference config. They isolate experience-selection and update semantics; they are **not** a claim that a table policy is a sufficient model of real robot online learning.

## Reference configuration

- 12 new-task contexts;
- 8 old-task contexts;
- base policy correct on all 8 old contexts;
- base policy correct on only 4/12 new contexts;
- 4 autonomous learning rounds;
- 2 rollouts per new context per round;
- correction budget: 2 new experience records per round.

Thus every update condition except `no_update` receives exactly **8 new-task experience records**.

## Results

| Condition | Final new success | New-task gain | Learning-curve AUC | Final old success | Old-task regression | New examples | Selection precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| `no_update` | 0.333 | 0.000 | 0.333 | 1.000 | 0.000 | 0 | 0.000 |
| `targeted_failure_mining` | **1.000** | **0.667** | **0.667** | **1.000** | **0.000** | **8** | **1.000** |
| `random_new_data` | 0.667 | 0.333 | 0.500 | 1.000 | 0.000 | **8** | 0.500 |
| `success_only_data` | 0.333 | 0.000 | 0.333 | 1.000 | 0.000 | **8** | 0.000 |
| `shuffled_corrections` | 0.333 | 0.000 | 0.333 | 1.000 | 0.000 | **8** | **1.000** |
| `targeted_reset_no_replay` | **1.000** | **0.667** | **0.667** | **0.000** | **1.000** | **8** | **1.000** |

## What the controls establish

### 1. More autonomous data is not the mechanism

`targeted_failure_mining` and `random_new_data` consume the same eight new experience records, but final new-task success differs:

\[
1.000 - 0.667 = 0.333.
\]

The targeted condition also has higher learning-curve AUC:

\[
0.667 - 0.500 = 0.167.
\]

So the gain is not explained by new-data volume alone.

### 2. Success-only experience does not cover missing failure states

`success_only_data` spends the same eight-example budget but remains at the initial **0.333** new-task success. Replaying states the policy already solves does not repair unseen failure modes in this controlled system.

### 3. Finding the right failure state is not enough

`shuffled_corrections` has failure-selection precision **1.000**: every selected context is genuinely failing. Yet its corrective labels are attached to the wrong contexts, and final new-task success remains **0.333**.

Therefore the flywheel requires both:

```text
correct failure state
+
correct corrective semantics
```

### 4. New capability can hide catastrophic old-task regression

`targeted_reset_no_replay` reaches the same perfect new-task success as targeted incremental learning:

\[
1.000.
\]

But old-task success falls from **1.000 → 0.000**. A report that only shows the new-task number would incorrectly call both updates equally successful.

### 5. Failure mining improves marginal value per new example

The targeted method gains **0.667** success over eight examples, while equal-volume random data gains **0.333**. In this reference system the marginal capability gain per new record is therefore approximately doubled.

## Scientific interpretation

The reference result supports a narrow causal claim:

> Under a matched new-experience budget, selecting currently failing states, attaching semantically correct corrections, and preserving prior competence are separately necessary for an effective experience-learning flywheel.

A simulator/real extension must replace the table policy with learned policies and add noisy failure detection, ambiguous corrections, representation drift, optimizer interference, trajectory-level credit assignment, replay/storage cost, and real old-task regression suites.
