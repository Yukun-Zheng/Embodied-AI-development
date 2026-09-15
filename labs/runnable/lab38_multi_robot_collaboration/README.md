# Lab 38 — Multi-Robot Collaboration

> **Question:** when two heterogeneous robots outperform independent execution, is the gain actually caused by capability-aware allocation and fresh coordination state, and can the system recover interrupted work after one robot fails?

This runnable lab is the CPU mechanism layer for [`Lab 38`](../../LABS.md). It uses a deterministic shared-work environment so the collaboration claim can be falsified before moving to multi-robot simulators or real ROS 2 systems.

## Hypotheses

The lab separates three claims that are often collapsed into one “multi-agent success” number:

1. **Heterogeneous allocation:** a coordinator that knows the real capability map should exploit complementary robots better than independent agents that repeatedly contend for the same work.
2. **Communication freshness:** coordination should degrade when robot availability heartbeats are delayed or dropped, even if the task board and scheduler are unchanged.
3. **Failure recovery:** after one robot fails, releasing and reallocating its partially completed job should recover more work than simply detecting the failure and leaving ownership stuck.

The mechanism chain is:

```text
heterogeneous physical capabilities
→ task allocation / ownership
→ robot-status communication
→ stale or fresh coordinator belief
→ real per-step work progress
→ completion / blocking / idle time
→ failure → release / reallocation → recovery
```

## Environment

Two robots share a deterministic work queue:

| robot | precision rate | haul rate |
|---|---:|---:|
| `dexter` | **1.00** | 0.35 |
| `carrier` | 0.35 | **1.00** |

Jobs alternate between `precision` and `haul` and each requires 2.0 work units. Only one robot can own a job at a time. Progress is a real state transition:

\[
w_{t+1}=\max(0,\;w_t-r_{robot,job}),
\]

and a job becomes complete only when remaining work reaches zero.

The normal suite uses 12 jobs and an 18-step horizon. The failure suite uses 8 jobs and a 20-step horizon.

## Normal collaboration conditions

| condition | changed mechanism | purpose |
|---|---|---|
| `independent_no_comm` | no peer claim/status communication | robots independently choose the same highest-priority incomplete job; exclusive ownership creates blocked duplicate work |
| `coordinated_fresh` | correct capability map + fresh heartbeats | reference coordinated execution |
| `coordinated_delayed` | same scheduler/capabilities, but heartbeat delivery delayed by 2 steps | isolates stale availability information |
| `coordinated_dropout` | same scheduler/capabilities, but only 1 in 4 heartbeat attempts transmitted | tests communication loss |
| `shuffled_capability_map` | fresh communication, but the two robots' capability descriptors are swapped | metadata-content negative control |

The task board itself is shared and authoritative in the coordinated conditions. Only robot availability is communicated. This is deliberate: the experiment isolates **status freshness** from task-discovery uncertainty.

### Why `shuffled_capability_map` is important

The shuffled condition preserves:

- the same jobs;
- the same scheduler;
- the same number of robots;
- the same communication channel;
- the same heartbeat delivery ratio;
- the same planning opportunity.

Only the capability semantics are wrong. If performance collapses, the result cannot be explained by “centralization” or extra communication alone.

## Independent no-communication control

Independent robots see the same incomplete-job priority list but cannot observe peer claims or ownership. Claims are simultaneous.

If both choose the same queued job, the robot with the better real capability wins ownership and the other robot loses that work step. While the winner continues the job, the idle peer can keep selecting the same still-incomplete job and remain blocked.

This is not a hand-written success table: contention changes which robot actually makes physical work progress at each step.

## Communication model

At the end of every coordinated step, each robot attempts to send a status heartbeat containing:

```text
agent id
idle / busy
active job
timestamp
```

The coordinator maintains a shadow state. Delayed or dropped heartbeats therefore create measurable:

- status age;
- idle time caused by a stale `busy` belief;
- stale assignment rejection when an old `idle` heartbeat arrives after a new assignment;
- communication messages and bytes.

The delayed control is allowed to preserve eventual success. The claim is not “any latency causes failure”; the analyzer explicitly accepts the stronger pattern:

```text
fresh: all jobs complete quickly
→ delay: all jobs may still complete, but makespan grows
→ severe dropout: completion itself degrades
```

## Single-agent failure suite

The second suite injects a `carrier` failure at step 5 while it owns a partially completed haul job.

Both failure conditions receive the failure event at the same step. This holds detection constant and isolates only the recovery mechanism:

| condition | interrupted job ownership |
|---|---|
| `failure_no_reallocation` | remains assigned to failed robot and is stuck |
| `failure_reallocation` | remaining work is released back to the queue and can be completed by the survivor |

Thus the comparison does **not** confound failure detection latency with reallocation policy.

## Outputs

```text
<output>/
├── experiment_summary.json
├── condition_metrics.csv
├── job_metrics.csv
├── analysis.json              # after analyze.py
├── ANALYSIS.md                # after analyze.py
└── runs/
    └── <condition run>/
        ├── manifest.json
        ├── steps.csv
        ├── failures.jsonl
        └── summary.json
```

`steps.csv` records both real agent/job state and the coordinator shadow state, so communication staleness can be audited rather than inferred from a final score.

## Metrics

The normal suite reports:

- job completion rate;
- makespan / throughput;
- duplicate claims;
- blocked work steps;
- stale-idle steps;
- stale assignment rejections;
- capability-mismatch assignments;
- heartbeat delivery ratio;
- transmitted communication bytes;
- average status age.

The failure suite additionally reports:

- interrupted job id;
- reallocation count;
- interrupted-job recovery;
- recovery latency.

## Deterministic smoke reference

The smoke contract is intentionally specific enough to catch mechanism drift:

```text
coordinated_fresh:
    12 / 12 jobs, makespan 12

independent_no_comm:
    9 / 12 jobs
    9 duplicate claims
    18 blocked steps

coordinated_delayed:
    12 / 12 jobs
    makespan 14
    6 stale-idle steps
    2 stale assignment rejections

coordinated_dropout:
    9 / 12 jobs
    heartbeat transmission ratio 0.25
    17 stale-idle steps

shuffled_capability_map:
    6 / 12 jobs
    6 capability-mismatch assignments
    communication delivery remains 1.0

failure_no_reallocation:
    7 / 8 jobs
    interrupted work not recovered

failure_reallocation:
    8 / 8 jobs
    interrupted work recovered after 6 steps
```

These are deterministic consequences of the configured rates, queue, horizon, communication channel and failure time. The independent analyzer also checks broader relational claims rather than only these exact numbers.

## Run

```bash
python labs/runnable/lab38_multi_robot_collaboration/run.py \
  --output /tmp/lab38

python labs/runnable/lab38_multi_robot_collaboration/analyze.py \
  /tmp/lab38/condition_metrics.csv \
  --output-dir /tmp/lab38
```

## Permanent acceptance relations

The independent analyzer requires:

```text
fresh coordination finishes the full queue
+ fresh coordination beats independent/no-comm execution
+ no-comm execution exhibits duplicate claims and blocking
+ delayed status increases status age / makespan without needing to fail outright
+ severe dropout degrades completion
+ shuffled capability metadata degrades allocation under matched communication
+ failure reallocation recovers the interrupted job
+ the same failure without reallocation leaves interrupted work stuck
```

The smoke test checks raw metrics and per-condition artifacts before invoking `analyze.py`, so the analyzer cannot self-certify missing or malformed evidence.

## Scientific scope

The supported claim is narrow:

> In this deterministic heterogeneous work system, collaboration gains require both correct capability information and sufficiently fresh coordination state; after a detected robot failure, explicit release/reallocation of interrupted work is causally necessary for full recovery.

This lab does **not** claim to model language negotiation, decentralized consensus, collision avoidance, ROS 2 DDS in full detail, or human–multi-robot teaming. Those belong in simulator and real-system extensions that preserve the same negative controls and raw logging contract.
