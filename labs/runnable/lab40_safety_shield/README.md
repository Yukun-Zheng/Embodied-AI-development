# Lab 40 — Watchdog / Safety Shield

> **Question:** does a robot safety layer actually keep the physical system inside its safety envelope after latency and braking dynamics, or does it merely fire a Boolean rule after the situation is already unrecoverable?

This runnable Lab turns the final systems/safety exercise into a closed-loop mechanism test:

```text
model + sensors
→ timestamps / freshness
→ proposed command
→ safety monitor
→ reject / safe-stop / ask-human
→ finite braking dynamics
→ physical state
→ safety violation or safe outcome
→ audit log
```

The core scientific principle is:

> **A safety rule is not validated because it triggered. It is validated only if the physical plant remains safe after the intervention, while normal-task availability stays acceptable.**

## Physical plant

A 1-D robot axis follows a target under damped acceleration dynamics. The nominal policy is a PD controller:

\[
a_\pi = k_p(x^*-x)-k_d\dot x.
\]

The policy command is bounded, but the robot still has inertia. A safe stop therefore takes non-zero time and distance.

For positive motion, the idealized stopping distance is

\[
d_{stop}=\frac{v^2}{2a_{brake}}.
\]

The predictive shield adds reaction-distance and safety margins before deciding whether the remaining joint/human separation is sufficient.

## Fault scenarios

Every condition receives the same deterministic episode schedule. Five scenarios are evaluated separately.

### `normal`

No fault. This measures mission completion and false intervention rate.

### `model_timeout`

At a fixed fault time the model heartbeat stops. Without a watchdog the system holds the last acceleration command, which creates a runaway trajectory.

### `stale_camera`

The human begins approaching while the camera stream freezes. The last measured human pose initially appears safe, so geometry-only rules continue acting on stale information.

### `unsafe_joint_target`

The model begins proposing a target outside the allowed joint envelope. A valid shield should reject the target and route the event to human review before execution.

### `human_proximity`

The camera remains fresh while a human approaches the moving robot. A purely reactive threshold fires too late; a predictive shield must account for stopping distance and closing motion.

## Conditions

### 1. `no_shield`

Executes the model command directly. This establishes that the injected faults are physically consequential rather than cosmetic metadata changes.

### 2. `static_rules`

Uses three common static checks:

- reject a target outside the configured joint-target envelope;
- stop when current joint position reaches a reactive threshold;
- stop when the currently measured human separation crosses a reactive threshold.

It intentionally ignores heartbeat/camera freshness and does not plan braking distance. It can catch an obviously invalid target but should fail on several dynamic faults.

### 3. `predictive_no_freshness`

Adds stopping-distance reasoning for joint/human hazards, but deliberately ignores timestamp freshness.

This is the key negative control for stale sensing:

\[
\text{good geometric prediction} + \text{stale state}
\not\Rightarrow
\text{safe behavior}.
\]

### 4. `predictive_shield`

Combines:

- target rejection;
- model heartbeat age;
- camera age;
- predictive joint stopping distance;
- predictive human separation;
- finite braking dynamics.

Responses are explicit:

| fault | response |
|---|---|
| model timeout | `safe_stop` |
| stale camera | `safe_stop` |
| unsafe target | `reject_and_ask_human` |
| human proximity | `safe_stop` |

### 5. `overconservative_shield`

Uses the same predictive mechanisms but shrinks the allowed target envelope. It should remain physically safe while rejecting some valid normal goals.

This prevents the invalid conclusion:

```text
more emergency stops
=
better safety system
```

A deployment-quality safety layer must report both safety and availability.

## Safety envelope

The experiment defines two hard physical constraints:

### Joint envelope

\[
|x| \le x_{hard}.
\]

Crossing the limit is logged as `hard_joint_violation`.

### Human separation

\[
d_{human} \ge d_{min}.
\]

Crossing the separation limit is logged as `human_collision`.

The predictive shield does not wait until either inequality is violated. It compares available distance with stopping distance, reaction distance and safety margin.

## Measurements

Metrics are reported **per fault scenario** and by condition:

- physical violation rate;
- joint-limit violation rate;
- human-collision rate;
- intervention rate;
- ask-human rate;
- intervention time;
- normal mission-completion rate;
- normal false-intervention rate;
- final tracking error;
- maximum absolute joint position;
- minimum human separation;
- control energy.

The two headline axes are:

\[
\text{safety}=1-\text{fault violation rate},
\]

and

\[
\text{availability}=\text{normal completion rate}.
\]

They are reported separately rather than collapsed into a single score.

## Audit contract

Each condition uses the common runnable-Lab files plus an explicit safety audit stream:

```text
<run-dir>/
├── manifest.json
├── steps.csv
├── failures.jsonl
├── summary.json
├── episodes.csv
├── scenario_metrics.csv
└── audit_events.jsonl
```

`steps.csv` records at every control tick:

```text
model_alive / camera_alive
model_age / camera_age
policy target
raw policy acceleration
current robot state
true + measured human state
stopping distance
required human separation
shield latch / reason / response
executed braking command
next physical state
actual violation flags
```

`audit_events.jsonl` records two classes of auditable event independently:

1. first shield intervention (`safe_stop`, `reject_and_ask_human`);
2. first physical safety violation (`hard_joint_limit`, `human_collision`).

This distinction matters because an intervention may be too late and therefore coexist with a later physical violation.

## CI mechanism assertions

The deterministic regression requires all of the following:

```text
all injected faults are dangerous without a shield
+ static target rejection catches the obvious unsafe target
+ static rules still fail on timeout / stale camera / dynamic human approach
+ predictive braking beats reactive human thresholding
+ freshness check is necessary under stale camera
+ heartbeat watchdog prevents timeout runaway
+ complete predictive shield prevents all four injected physical violations
+ all fault classes trigger an auditable intervention
+ unsafe target routes to ask-human
+ predictive shield preserves normal completion with negligible false stops
+ overconservative shield remains safe but loses normal availability
```

If these relations stop holding, CI fails. The intended response is to inspect physical traces and audit events, not weaken the assertions.

## Failure taxonomy

Physical failures are logged only when the plant actually crosses a hard safety boundary:

- `hard_joint_violation`;
- `human_collision`.

Shield interventions are **not** failure events; they are audit events. This prevents a safety mechanism from looking worse merely because it successfully intervened.

## Reproduce

Quick deterministic CI configuration:

```bash
python labs/runnable/lab40_safety_shield/run.py \
  --quick \
  --output /tmp/lab40

python labs/runnable/lab40_safety_shield/analyze.py \
  /tmp/lab40/condition_metrics.csv \
  /tmp/lab40/scenario_metrics.csv \
  --output-dir /tmp/lab40
```

Full default episode count:

```bash
python labs/runnable/lab40_safety_shield/run.py \
  --output /tmp/lab40-full
```

## Falsification conditions

The safety claim should be rejected if:

- `predictive_shield` fires but the plant still violates a hard boundary;
- a freshness-blind controller handles stale sensing equally well;
- reactive human thresholding performs as well as stopping-distance prediction;
- timeout handling is no better than holding the last command;
- unsafe targets are executed before rejection;
- normal episodes suffer substantial false stops;
- safety is achieved only by refusing essentially all normal work;
- audit events cannot reconstruct why and when intervention occurred.

## Scientific scope

This is a CPU mechanism experiment, not a certification or a substitute for a real robot safety case. A production system also needs hardware e-stop paths, fail-safe actuators, independent safety-rated sensing, formal hazard analysis, redundancy, fault containment, human procedures and applicable standards.

Its purpose is narrower: to make **freshness, braking physics, command rejection, human escalation and availability** measurable experimental variables instead of treating “safety layer” as an architectural label.
