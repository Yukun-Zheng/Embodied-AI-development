# Lab 38 — CI-Verified Reference Observation

> These observations come from GitHub Actions `Executable textbook regression` run **34958983747**, job **104347763376**, at commit `24f7d05f38e3fe687a160b3e5e1487eaf293a029`.

## CI configuration

The deterministic mechanism test contains two suites.

### Normal collaboration suite

```text
robots = 2 heterogeneous agents
jobs = 12 alternating precision / haul jobs
work per job = 2.0
horizon = 18 steps

dexter:  precision 1.00, haul 0.35
carrier: precision 0.35, haul 1.00
```

The task board is shared and authoritative. The communication intervention affects the robots' **availability heartbeat**, which is exactly the state the coordinator needs to know whether a robot is free for a new assignment.

### Single-agent failure suite

```text
jobs = 8
horizon = 20 steps
carrier failure step = 5
failure detection = held fixed across both controls
```

The comparison therefore isolates whether interrupted work is released and reallocated after the detected failure.

## GitHub-runner observations

| condition | completion | makespan | duplicate / blocked | stale-idle | capability mismatch | heartbeat delivery | interrupted recovery |
|---|---:|---:|---:|---:|---:|---:|---:|
| `independent_no_comm` | **0.750** (9/12) | 18 | **9 / 18** | 0 | 0 | 0.000 | — |
| `coordinated_fresh` | **1.000** (12/12) | **12** | 0 / 0 | 0 | 0 | 1.000 | — |
| `coordinated_delayed` | **1.000** (12/12) | **14** | 0 / 0 | **6** | 0 | 1.000 | — |
| `coordinated_dropout` | **0.750** (9/12) | 18 | 0 / 0 | **17** | 0 | **0.250** | — |
| `shuffled_capability_map` | **0.500** (6/12) | 18 | 0 / 0 | 0 | **6** | 1.000 | — |
| `failure_no_reallocation` | **0.875** (7/8) | 20 | 0 / 0 | 0 | 0 | — | **0** |
| `failure_reallocation` | **1.000** (8/8) | **17** | 0 / 0 | 0 | 0 | — | **1** |

The deterministic smoke test additionally hard-asserts:

```text
coordinated_delayed assignment_rejections = 2
failure_reallocation reallocation_count = 1
failure_reallocation recovery_latency = 6 steps
```

## What the observations establish

### 1. Heterogeneous collaboration is more than “two robots are present”

Without claim/status communication, both idle robots repeatedly choose the same highest-priority incomplete job. Exclusive ownership means one robot works while the other is blocked. The result is:

\[
9/12 \quad \text{vs.} \quad 12/12
\]

for independent versus fresh coordinated execution.

The improvement is produced by real work-state transitions and ownership conflicts, not by a hand-written condition-specific success table.

### 2. Communication delay can first cost time before it costs eventual success

A two-step heartbeat delay preserves 12/12 completion, but makespan increases from 12 to 14. The delayed run also produces six steps where a physically idle robot is left unused because the coordinator still believes it is busy.

Two stale assignment rejections occur when an old `idle` heartbeat arrives after the robot has already accepted a newer assignment. This exposes a timestamp/order problem that a scalar “network latency” penalty would hide.

Therefore:

\[
\text{same eventual success}
\not\Rightarrow
\text{same collaboration quality}.
\]

### 3. Severe communication loss changes the physical outcome

When only one in four heartbeat attempts is transmitted, the delivery ratio is 0.25, stale-idle time grows to 17 steps, and completion drops to 9/12.

This separates a mild freshness cost from a regime in which communication failure changes task completion itself.

### 4. Correct capability metadata is causally necessary

`shuffled_capability_map` preserves:

- the same scheduler;
- the same jobs;
- the same fresh heartbeat channel;
- heartbeat delivery ratio 1.0;
- the same two physical robots.

Only the capability descriptions are swapped. The coordinator therefore issues six capability-mismatched assignments and completion falls to 6/12.

The collaboration gain cannot be explained by centralization or communication bandwidth alone.

### 5. Failure detection is not the same as failure recovery

Both failure controls receive the same detected `carrier` failure at step 5 while a haul job is partially complete.

Without reallocation, ownership remains stuck on the failed robot and final completion is 7/8. With release/reallocation, the survivor finishes the interrupted work after six steps and the system reaches 8/8.

Thus:

\[
\text{failure detected}
\neq
\text{interrupted work recovered}.
\]

## CI mechanism assertions

The permanent regression verifies:

```text
fresh capability-aware coordination completes the full normal queue
+ fresh coordination beats independent/no-communication execution
+ no-communication creates duplicate claims and blocked work
+ delayed heartbeat increases stale state and makespan
+ severe dropout degrades completion
+ shuffled capability metadata degrades allocation under matched communication
+ failure detection is held constant across the recovery controls
+ explicit reallocation recovers the interrupted job
+ no-reallocation leaves interrupted work stuck
+ raw step logs / failures / manifests are emitted before analysis
```

The same executable job also re-ran all previously published runnable mechanism labs successfully, so adding Lab 38 did not break the existing reference set.

## Scientific scope

The supported claim is narrow:

> In this deterministic heterogeneous shared-work system, collaboration gains require both correct capability information and sufficiently fresh coordination state; after a detected robot failure, explicit release/reallocation of interrupted work is causally necessary for full recovery.

This experiment does **not** claim to reproduce full ROS 2 DDS behavior, decentralized consensus, collision avoidance, language negotiation, or human–multi-robot teaming. Simulator and real-system extensions should preserve these same negative controls while replacing the toy work dynamics and heartbeat channel with realistic robot motion, networking and task execution.

## Reproduce

```bash
python labs/runnable/lab38_multi_robot_collaboration/run.py \
  --output /tmp/lab38

python labs/runnable/lab38_multi_robot_collaboration/analyze.py \
  /tmp/lab38/condition_metrics.csv \
  --output-dir /tmp/lab38
```
