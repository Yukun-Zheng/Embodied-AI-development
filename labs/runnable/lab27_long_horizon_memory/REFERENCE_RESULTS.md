# Lab 27 — CI-Verified Reference Observation

> These observations come from the deterministic GitHub Actions **quick/smoke configuration** in `Executable textbook regression` run **34957421300**, job **104342722463**, at commit `6e2e21de0acd0ea9d02245f9f6d55fb51daa1a87`.

## CI configuration

The quick regression evaluates six memory conditions over three distractor horizons:

```text
conditions = 6
horizons = 4 / 10 / 16 distractor subtasks
episodes per horizon = 64 balanced mission bindings
decisions after distractors = 3
context window = 8 observations
task adaptation steps = 0
```

The 64 quick episodes enumerate the full mission space

\[
4\ \text{objects}\times4\ \text{gates}\times4\ \text{bins}=64,
\]

so the deterministic no-memory fallback has exact per-decision accuracy \(1/4\) and exact complete-task success \(1/64=0.015625\).

Across all conditions and horizons, the smoke test executes **1152 paired episodes**.

## CI runner observations

The GitHub runner printed the following aggregate results:

| condition | task success | query accuracy | avg retrieval cost | avg serialized memory |
|---|---:|---:|---:|---:|
| `no_memory` | **0.015625** | **0.250** | **0.0** | **0.0 B** |
| `frame_context` | **0.343750** | **0.500** | **23.0** | **792.3 B** |
| `episodic_log` | **1.000000** | **1.000** | **39.0** | **1326.3 B** |
| `semantic_memory` | **1.000000** | **1.000** | **3.0** | **88.0 B** |
| `shuffled_memory` | **0.000000** | **0.000** | **3.0** | **88.0 B** |
| `unrelated_memory` | **0.015625** | **0.250** | **3.0** | **58.0 B** |

For the **16-distractor** condition, the runner also reported:

```text
episodic serialized memory = 1845.5 B
semantic serialized memory =   88.0 B
```

The semantic and shuffled conditions both use three persistent fact slots. Their capacity and read interface are matched; only the stored binding content differs.

## Horizon separation

The permanent smoke test hard-asserts the following complete-task success pattern:

| condition | 4 distractors | 10 distractors | 16 distractors |
|---|---:|---:|---:|
| `no_memory` | 0.015625 | 0.015625 | 0.015625 |
| `frame_context` | **1.000000** | **0.015625** | **0.015625** |
| `episodic_log` | **1.000000** | **1.000000** | **1.000000** |
| `semantic_memory` | **1.000000** | **1.000000** | **1.000000** |
| `shuffled_memory` | **0.000000** | **0.000000** | **0.000000** |
| `unrelated_memory` | 0.015625 | 0.015625 | 0.015625 |

This is the central causal separation. The bounded 8-observation context succeeds while the initial mission card still lies inside its window, then collapses exactly to the balanced fallback once the cue is pushed outside that window. Persistent correct memory does not collapse.

## What the observations establish

### 1. More recent context is not automatically long-term memory

At four distractors, `frame_context` retains the mission card through all three later decisions and achieves perfect task success. At 10 and 16 distractors, the same fixed-capacity context no longer contains the cue and falls to \(1/64\).

Therefore:

\[
\text{larger recent context}
\neq
\text{persistent task state}.
\]

### 2. Persistent state solves the partial-observability gap

Both `episodic_log` and `semantic_memory` remain at 1.0 success across all three horizons. Later observations never reveal the missing object/gate/bin bindings, so their performance cannot be explained by current-frame information.

### 3. Correct memory content is causally necessary

`semantic_memory` and `shuffled_memory` have matched three-slot persistent capacity and the same one-read interface:

```text
semantic_memory  success = 1.0
shuffled_memory  success = 0.0
```

The difference is the binding value stored in memory. Extra persistent state or extra reads alone therefore do not explain the gain.

### 4. Unrelated persistent state is not useful memory

`unrelated_memory` also keeps three persistent facts, but they describe task-irrelevant state. It remains at the exact no-memory complete-task baseline of 0.015625.

Thus:

\[
\text{persistent storage}
\not\Rightarrow
\text{task-relevant memory}.
\]

### 5. Episodic and semantic memory can have the same behavioral result but different cost structure

Both correct persistent memories achieve perfect success, yet at the longest horizon the serialized state is approximately:

\[
1845.5\ \text{B} \quad \text{vs.} \quad 88.0\ \text{B}.
\]

The analyzer also requires semantic retrieval cost to remain horizon-invariant and below 20% of the long-horizon episodic scan cost, while episodic retrieval cost must grow by more than 2× from the short to the long horizon.

This does **not** claim that 88 bytes is a production memory-system cost. It establishes the mechanism distinction between retaining an entire trace and retaining the task-sufficient latent state.

## CI mechanism assertions

The permanent regression verifies:

```text
paired balanced missions
+ no hidden task-state leak into later observations
+ bounded context works only while cue is still in-window
+ episodic memory survives long gaps
+ semantic memory survives long gaps
+ shuffled capacity-matched memory collapses
+ unrelated persistent memory stays at chance
+ episodic retrieval cost grows with horizon
+ semantic retrieval/storage remains compact
+ raw steps / manifests / failures are emitted before analysis
```

The smoke test directly checks raw episode artifacts before invoking `analyze.py`, so the independent analyzer cannot self-certify a run that failed to emit the expected evidence.

## Scientific scope

The supported claim is narrow:

> In this partially observable long-horizon mechanism task, correct persistent task state is causally necessary once the relevant cue falls outside bounded recent context; persistent memory with shuffled or irrelevant content does not substitute for that state.

The experiment does **not** establish the superiority of a particular LLM/VLA memory product, database, retrieval embedding, or memory-token architecture. A simulator/VLA extension must preserve the same intervention structure while replacing the symbolic cue and choices with realistic visual/language observations and robot actions.

## Reproduce

```bash
python labs/runnable/lab27_long_horizon_memory/run.py \
  --quick \
  --output /tmp/lab27

python labs/runnable/lab27_long_horizon_memory/analyze.py \
  /tmp/lab27/episode_metrics.csv \
  --output-dir /tmp/lab27
```
