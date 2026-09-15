# Lab 14 — CI-Verified Reference Observation

> These values come from the deterministic GitHub Actions **quick/smoke configuration**. They are mechanism checks for a toy multi-rate contact loop, not benchmark claims about a real tactile sensor, gripper, object, or VLA.

## Paired quick experiment

The permanent `Executable textbook regression` runs 240 paired episodes. Each control mode receives the same slip-event phase and the same per-step tactile noise.

| mode | drop rate | p95 max slip | mean reaction latency | reaction detection |
|---|---:|---:|---:|---:|
| `slow_policy_only` | 0.529 | 4.020 mm | 69.1 ms | 0.621 |
| `fast_tactile_reflex` | **0.000** | **0.490 mm** | **2.6 ms** | **1.000** |
| `delayed_tactile_reflex` | 1.000 | 4.011 mm | 122.6 ms | 1.000 |

## What the numbers establish

### 1. A short contact event can be missed by the slow loop

The reference event lasts 140 ms while the high-level policy period is 200 ms:

\[
T_{event}=0.14\text{ s}<T_{slow}=0.20\text{ s}.
\]

The slow loop detects a reaction in only 62.1% of episodes and drops the object in 52.9% of episodes. This is a phase-of-sampling effect, not a claim that the high-level controller is incapable of increasing grip force when it happens to observe the event.

### 2. The fast residual changes both timing and physical outcome

The fast tactile loop reacts in about 2.6 ms on average, compared with 69.1 ms among slow-loop episodes that react. Its p95 slip displacement falls from 4.020 mm to 0.490 mm and the reference drop rate falls to zero.

The important causal chain is therefore:

```text
low-latency contact signal
→ earlier residual control
→ actuator force changes while recovery is still possible
→ less slip
→ fewer drops
```

not merely “tactile was added as another modality.”

### 3. High execution rate is not enough when information is stale

`delayed_tactile_reflex` still executes the correction path at 200 Hz, but its tactile signal is delayed by 120 ms. Its mean reaction latency becomes 122.6 ms, p95 slip returns to 4.011 mm, and all reference episodes drop.

This negative control separates two quantities that are often conflated:

\[
\text{controller update rate}
\neq
\text{fresh feedback rate}.
\]

A nominally fast loop cannot recover information that arrived too late.

## Scientific scope

The experiment supports a narrow systems statement:

> When a recoverable physical event evolves faster than the high-level policy cycle, a low-latency residual feedback path can materially change closed-loop outcome; stale sensing can destroy that benefit even if the residual function itself is executed at high frequency.

It does **not** establish that 200 Hz is a universal tactile frequency, that tactile is always superior to vision, or that a threshold reflex is sufficient for real dexterous manipulation.

## Reproduce

```bash
python labs/runnable/lab14_tactile_reflex/run.py \
  --quick \
  --output /tmp/lab14

python labs/runnable/lab14_tactile_reflex/analyze.py \
  /tmp/lab14/mode_metrics.csv \
  --output-dir /tmp/lab14
```

`analysis.json` is the machine-readable source for the CI assertions. If the event duration, actuator time constant, tactile delay, friction model, or controller parameters change, regenerate the analysis instead of copying these numbers forward.
