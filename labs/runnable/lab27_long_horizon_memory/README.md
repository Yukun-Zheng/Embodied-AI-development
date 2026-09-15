# Lab 27 — Long-Horizon VLA + Memory

> **Question:** when a task-relevant binding disappears from the current observation, does persistent memory causally preserve the state needed for later embodied decisions, or does a larger recent-frame context merely postpone failure?

This runnable lab is the CPU mechanism layer for [`Lab 27`](../../LABS.md). It deliberately does **not** require an LLM/VLA checkpoint. The goal is to isolate the memory claim before adding language, vision models, retrieval systems, or simulator complexity.

## Hypothesis

A long-horizon robot policy should not receive credit for “having memory” merely because its input context is longer. In a partially observable task:

1. a bounded recent-frame context should work only while the original mission cue is still inside the window;
2. correct persistent episodic or semantic memory should preserve performance after that cue falls outside the window;
3. shuffled or unrelated persistent memory should not help;
4. a compact semantic state should be able to retain the necessary information with lower storage/retrieval cost than scanning a full episodic trace.

The falsifiable mechanism chain is:

```text
mission cue visible once
→ cue disappears from later observations
→ distractor subtasks increase temporal gap
→ memory write / retention mechanism
→ later memory-dependent physical choices
→ task success
```

## Environment

At the beginning of each episode the robot sees a one-shot mission card containing three bindings:

```text
target_object
access_gate
destination_bin
```

The robot then executes a sequence of irrelevant distractor subtasks. The quick CI sweep uses distractor horizons:

```text
4 / 10 / 16 distractor subtasks
```

followed by three decisions:

```text
pick target object
→ traverse access gate
→ place in destination bin
```

Thus the evaluated task lengths are **7 / 13 / 19 subtasks**, inside the 5–20-subtask range of the curriculum design.

Crucially, the later query observations expose the available choices but **never re-expose the original mission binding**. All conditions see exactly the same paired episodes and candidate action sets.

## Balanced quick protocol

The mission space contains four objects × four gates × four bins:

\[
4^3 = 64
\]

The deterministic quick configuration runs exactly **64 episodes per horizon per condition**, covering every binding combination once. Therefore the deterministic first-choice fallback has:

- per-decision accuracy = \(1/4\);
- complete three-decision task success = \(1/64 = 0.015625\).

This makes the chance baseline a property of the experiment design rather than a lucky random seed.

## Conditions

| condition | state available at decision time | purpose |
|---|---|---|
| `no_memory` | current query only | chance/fallback baseline |
| `frame_context` | last 8 raw observations | tests whether a bounded context is being mislabeled long-term memory |
| `episodic_log` | complete observation log + reverse retrieval | persistent trace with cost growing with horizon |
| `semantic_memory` | 3 compact mission facts | persistent task state with fixed-size retrieval |
| `shuffled_memory` | 3 persistent facts with every binding systematically shifted | capacity-matched negative control for memory **content correctness** |
| `unrelated_memory` | 3 persistent but task-irrelevant facts | negative control for “having persistent state” without useful information |

`semantic_memory` and `shuffled_memory` use the same number of persistent fact slots. The difference is information content, not capacity.

## Why the frame-context control matters

The recent context window is 8 observations. With four distractors, the one-shot mission card remains visible through all three later decisions. With 10 or 16 distractors it has already fallen out of the window before the first memory-dependent decision.

So the expected causal transition is:

```text
short horizon: frame context can solve the task
long horizon:  same context capacity loses the binding
persistent memory: binding survives
```

If frame context remained perfect after the cue left its window, the implementation would be leaking hidden task state.

## Why the shuffled-memory control matters

`shuffled_memory` preserves:

- the same three semantic keys;
- the same number of persistent slots;
- the same one-read retrieval interface;
- the same action candidates and action budget.

It changes only the stored binding value by a deterministic category-wise permutation. Therefore a collapse under shuffled memory attacks the **correctness of remembered content**, not memory size or extra compute.

## Outputs

```text
<output>/
├── experiment_summary.json
├── episode_metrics.csv
├── condition_metrics.csv
├── horizon_metrics.csv
├── analysis.json              # after analyze.py
├── ANALYSIS.md                # after analyze.py
└── runs/
    └── <condition run>/
        ├── manifest.json
        ├── steps.csv
        ├── failures.jsonl
        └── summary.json
```

`steps.csv` records the actual raw observation stream, memory size, retrieval source, selected action, expected action, and query correctness. A final success scalar is therefore not the only retained evidence.

## Metrics

The mechanism is evaluated with:

- complete task success;
- memory-dependent query accuracy;
- retrieval scan/read cost;
- persistent memory slots;
- approximate serialized memory bytes;
- performance by distractor horizon;
- explicit memory-dependent decision failures.

The cost metrics are intentionally simple mechanism proxies; they are **not** claims about production database latency or transformer KV-cache memory.

## Run

```bash
python labs/runnable/lab27_long_horizon_memory/run.py \
  --quick \
  --output /tmp/lab27

python labs/runnable/lab27_long_horizon_memory/analyze.py \
  /tmp/lab27/episode_metrics.csv \
  --output-dir /tmp/lab27
```

## Permanent smoke acceptance

The deterministic smoke test requires all of the following:

```text
episodic + semantic memory stay near-perfect at all horizons
+ bounded frame context is perfect only while cue remains in-window
+ no-memory stays at balanced chance
+ shuffled persistent memory collapses despite matched fact capacity
+ unrelated persistent memory does not improve chance behavior
+ semantic memory uses much less long-horizon storage/retrieval than episodic scan
+ episodic retrieval cost grows with horizon
+ semantic retrieval cost remains horizon-invariant
```

It also verifies raw artifacts **before** invoking the independent analyzer, so the analyzer cannot certify a run that failed to emit the expected evidence.

## Scientific scope

The supported claim is narrow:

> In this partially observable long-horizon mechanism task, correct persistent state is causally necessary once task-relevant information falls outside bounded recent context; persistent memory with shuffled or irrelevant content does not substitute for the missing state.

This lab does **not** establish that one particular VLA/LLM memory architecture is superior. The simulator/VLA extension should preserve the same causal controls while replacing symbolic observations/actions with real visual observations, language instructions, robot actions, and realistic memory-system costs.
