# Lab 34 — CI Reference Results

> Frozen from GitHub Actions run **34973816714**, job **104396373475**, commit `e51dac719fd66430540d1180b0cc87c72fdac4ce`.
>
> These are deterministic M-layer mechanism results for the reference config. They are **not** a claim that the same ranking must hold unchanged in every simulator or real-robot curriculum.

## Reference configuration

All strategies receive the same total budget:

- 9 task difficulties;
- 2 shared warmup rounds per task;
- **180 total practice steps**;
- identical competence and learning-gain dynamics;
- only the curriculum-selection rule changes.

## Strategy results

| Strategy | Final average success | Learning-curve AUC | Final skill | Mean selected learnability | Mean frontier distance | Mastered tasks |
|---|---:|---:|---:|---:|---:|---:|
| `learning_progress` | **0.965** | **0.652** | 1.054 | **0.901** | **0.045** | **8** |
| `fixed_curriculum` | 0.935 | 0.546 | 0.992 | 0.685 | 0.099 | 8 |
| `uniform` | 0.728 | 0.365 | 0.759 | 0.344 | 0.268 | 5 |
| `hardest_first` | 0.058 | 0.057 | 0.096 | ~0.000 | 0.854 | 0 |
| `shuffled_progress` | 0.058 | 0.057 | 0.096 | ~0.000 | 0.854 | 0 |

## What the controls establish

### 1. Same task counts do not imply the same curriculum

`uniform` and `fixed_curriculum` allocate the same total number of practices to every task, but differ only in ordering. Their AUCs separate strongly:

\[
0.546 - 0.365 = 0.181.
\]

So total task coverage alone does not explain learning efficiency.

### 2. Hardest-first is not equivalent to learning at the frontier

After warmup, `hardest_first` repeatedly chooses a task whose success probability and learnability are effectively zero. It finishes with final average success **0.058**, despite spending the same 180-step budget.

The mechanism distinction is:

```text
hard task
≠
currently learnable task
```

### 3. Correct progress-to-task binding is causal

`shuffled_progress` preserves the measured progress magnitudes but reverses their task identity before selection. It collapses from

\[
0.965 \rightarrow 0.058
\]

in final average success and from

\[
0.652 \rightarrow 0.057
\]

in learning-curve AUC.

Thus the useful signal is not merely “a progress number exists”; the progress estimate must be attached to the **correct practice goal**.

### 4. Learning-progress scheduling tracks the competence frontier

The adaptive scheduler selects tasks with mean frontier learnability **0.901** and mean difficulty-to-skill distance **0.045**, while ultimately mastering **8/9** tasks.

This is the intended mechanism:

```text
measure progress
→ locate current learnable frontier
→ allocate practice there
→ move frontier outward
```

## Scientific interpretation

The reference result supports a narrow mechanism claim:

> Under a fixed practice budget and this controlled skill model, a scheduler that correctly binds measured learning progress to task identity allocates practice more sample-efficiently than matched uniform, fixed-order, hardest-first, and shuffled-binding controls.

It does **not** establish that a scalar learning-progress heuristic is sufficient for real embodied curriculum generation. A simulator/robot extension must still test noisy progress estimates, multidimensional task difficulty, task interference, catastrophic forgetting, reset costs, safety constraints, and nonstationary embodiment dynamics.
