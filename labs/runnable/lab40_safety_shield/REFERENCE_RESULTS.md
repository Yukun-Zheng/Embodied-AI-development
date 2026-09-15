# Lab 40 — CI-Verified Reference Observation

> These observations come from the deterministic GitHub Actions **quick/smoke configuration**. The first full reference run passed in `Executable textbook regression` run **34951489494**, job **104323250776**. This is a mechanism test, not a certified robot safety case.

## CI configuration

The quick regression evaluates **60 paired episodes for each of five scenarios** under every shield condition:

```text
normal
model_timeout
stale_camera
unsafe_joint_target
human_proximity
```

The safety envelope is evaluated **after the physical braking dynamics**. A shield rule firing does not count as success if the simulated plant later crosses a hard joint boundary or human-separation boundary.

## CI-verified mechanism relations

The permanent regression hard-asserts the following observations.

| condition / scenario | CI-verified observation |
|---|---|
| `no_shield` / every injected fault | physical violation rate **> 0.95** |
| `static_rules` / unsafe target | violation rate **< 0.05**, intervention **> 0.95**, ask-human **> 0.95** |
| `static_rules` / model timeout | violation rate **> 0.90** |
| `static_rules` / stale camera | violation rate **> 0.90** |
| `static_rules` / human proximity | violation rate **> 0.90** |
| `predictive_no_freshness` / stale camera | violation rate **> 0.80** |
| `predictive_no_freshness` / human proximity | violation rate **< 0.05** |
| `predictive_shield` / all four faults | violation rate **< 0.05** and intervention rate **> 0.95** |
| `predictive_shield` / unsafe target | ask-human rate **> 0.95** |
| `predictive_shield` / normal | completion rate **> 0.95**, false intervention **< 0.05** |
| `overconservative_shield` / injected faults | aggregate fault violation rate **< 0.05** |
| `overconservative_shield` / normal | false intervention **> 0.20** and completion is **> 0.20 below** the predictive shield |

These are intentionally recorded as the relations that CI actually enforces rather than reconstructing missing log scalars from a local rerun.

## Audit observation

For the complete `predictive_shield`, the smoke test reads `audit_events.jsonl` and requires exactly **60 first interventions for each fault reason**:

```text
model_timeout                 60
stale_camera                  60
unsafe_joint_target           60
predictive_human_proximity    60
```

It also requires:

- **zero** `safety_violation` audit events for `predictive_shield`;
- all 60 unsafe-target events use response `reject_and_ask_human`;
- all 60 unsafe-target events set `ask_human=true`;
- `no_shield` retains explicit physical-violation audit evidence.

So the audit stream is not decorative logging: CI checks that every injected fault is classified by the intended mechanism.

## What the observations establish

### 1. The injected faults are physically consequential

All four fault classes produce violation rates above 0.95 when the policy command is executed without a shield. The experiment therefore does not claim safety gains on harmless metadata perturbations.

### 2. Static rejection is useful but insufficient

A static target-envelope rule correctly catches the deliberately unsafe target and routes it to human review. Yet the same static-rule system still violates the physical safety envelope on timeout, stale sensing and dynamic human approach.

This separates:

```text
invalid command rejection
from
closed-loop hazard anticipation
```

### 3. Braking physics matters

`predictive_no_freshness` reduces the dynamic human-proximity violation rate below 0.05, whereas the reactive static rule remains above 0.90.

The mechanism difference is stopping-distance reasoning:

\[
d_{stop}=\frac{v^2}{2a_{brake}},
\]

plus reaction and closing-motion margins. Waiting until the human is already inside a fixed reactive threshold is too late at the same physical speed.

### 4. Good prediction on stale state is still unsafe

The freshness-blind predictive condition still has stale-camera violation above 0.80. The complete predictive shield drives the same fault below 0.05 by treating camera age itself as a safety variable.

Thus:

\[
\text{predictive geometry} + \text{stale observation}
\not\Rightarrow
\text{safe behavior}.
\]

### 5. Heartbeat age is a control variable, not infrastructure trivia

The static-rule system has model-timeout violation above 0.90, while the complete predictive watchdog keeps the same fault below 0.05. Holding the last command after inference disappears is therefore an experimentally visible closed-loop failure mode.

### 6. Safety must be reported together with availability

The complete predictive shield is required to keep normal-task completion above 0.95 with false interventions below 0.05.

The deliberately overconservative shield is also physically safe on injected faults, but CI requires it to false-stop more than 20% of normal episodes and lose more than 20 percentage points of normal completion relative to the predictive shield.

This prevents a trivial always-stop policy from winning the safety evaluation.

## CI mechanism assertions

The permanent smoke test verifies:

```text
faults are dangerous without protection
+ unsafe targets are rejected before execution
+ target rejection alone is not enough
+ predictive stopping beats reactive distance thresholds
+ sensor freshness is causally necessary under stale camera
+ heartbeat watchdog prevents held-command runaway
+ complete shield prevents all four injected violation classes
+ every injected fault produces the intended audit reason
+ unsafe target routes to human review
+ normal availability remains high
+ overconservative safety exposes false-stop cost
```

The independent analyzer then recomputes the same mechanism claims from `condition_metrics.csv` and `scenario_metrics.csv`.

## Scientific scope

The supported claim is narrow:

> In this closed-loop mechanism experiment, safe behavior requires explicit command rejection, freshness monitoring and stopping-distance-aware intervention; safety must be judged after physical dynamics and reported together with normal-task availability.

The experiment does **not** constitute functional-safety certification. Real deployment requires hardware e-stop paths, safety-rated components, independent sensing, redundancy, fault-containment analysis, operational procedures and the applicable standards/regulatory process.

## Reproduce

```bash
python labs/runnable/lab40_safety_shield/run.py \
  --quick \
  --output /tmp/lab40

python labs/runnable/lab40_safety_shield/analyze.py \
  /tmp/lab40/condition_metrics.csv \
  /tmp/lab40/scenario_metrics.csv \
  --output-dir /tmp/lab40
```

Inspect `audit_events.jsonl` and `steps.csv` together whenever a rule fires but a physical violation still occurs; the distinction between **intervention** and **successful stopping** is the central point of the Lab.
