# Lab 26 — Cross-Embodiment Transfer

> **Question:** does a shared policy truly transfer across bodies, or does it merely support several robot identities and tensor formats that were already known during development?

This runnable Lab separates cross-embodiment claims into an executable physical chain:

```text
raw robot sensors
→ observation interface / units
→ canonical physical state
→ one shared canonical policy
→ morphology / dynamics adapter
→ hardware action semantics
→ embodiment-specific dynamics
→ closed-loop physical success
```

The central distinction is:

```text
multiple seen embodiments
≠
zero-shot transfer to an unseen morphology
```

## Physical task

Every embodiment controls the same 1-D point-mass reaching task:

\[
m_e\ddot x + c_e\dot x = F,
\]

where embodiment \(e\) changes mass \(m_e\), damping \(c_e\), sensor units, hardware action scale/sign and command limit.

The shared canonical policy is deliberately tiny and fixed:

\[
a_d = k_p(x^*-x)-k_d\dot x.
\]

It has only the two shared gains \((k_p,k_d)\). No condition receives a larger policy network or extra task-specific policy capacity.

## Embodiments and transfer split

| body | evaluation role | important variation |
|---|---|---|
| A | **seen** | nominal SI-like interface and light dynamics |
| B | **seen** | heavier body, different sensor scales, reversed hardware action sign |
| C | **held-out interpolation** | parameters between/near seen dynamics, new interface scales |
| D | **held-out extrapolation** | substantially heavier/more damped, reversed action sign, lower actuation scale |

A/B represent the common claim “one system supports multiple robots.” C/D are never used for task adaptation and are reported separately rather than averaged into the seen mixture.

The held-out robot is allowed to provide **robot metadata**—units, action convention and morphology parameters—because a new physical platform must expose its interface contract. It is *not* allowed to provide task success labels, rollout fine-tuning or new task demonstrations.

For every C/D result:

```text
adaptation_steps = 0
```

## Conditions

### 1. `raw_shared`

The shared controller receives raw sensor numbers as though every robot used the same SI units, then sends its force-like output directly as a hardware command.

This control tests the false equivalence:

\[
\text{same tensor shape} \Rightarrow \text{same physical semantics}.
\]

### 2. `canonical_interface_only`

Observation units and hardware action sign/scale are correctly canonicalized, but the controller uses one nominal body model for everyone.

This isolates **semantic interface alignment** from **morphology/dynamics alignment**.

### 3. `seen_robot_lookup`

A/B have exact robot-specific dynamics entries. The same shared canonical policy therefore supports both seen robots well.

C/D have no lookup entry and fall back to the nominal dynamics. This is the key negative control for the claim:

> “works on several known robot IDs” is not evidence of transfer to an unseen morphology.

### 4. `morphology_conditioned`

Uses the continuous morphology descriptor \((m_e,c_e)\) to map desired canonical acceleration into physical force:

\[
F_d = m_e a_d + c_e\dot x.
\]

The observation/action interface still performs only semantic conversion; the shared policy gains remain exactly the same. C/D receive no task adaptation.

### 5. `wrong_morphology_tag`

All sensor and action semantics are correct, but the body descriptor is deliberately swapped or replaced by the nominal body.

If morphology conditioning is causally used, this condition must degrade while the correct descriptor succeeds.

### 6. `wrong_action_semantics`

The state and morphology descriptor are both correct, but every robot is treated as if it used Robot A's hardware action sign/scale.

This isolates a hard systems fact: even a correct policy and correct body model can fail catastrophically when the actuator convention is wrong.

## Shared trial schedule

All conditions and all embodiments receive the same deterministic episode schedule:

- initial position;
- initial velocity;
- physical target position.

The target is kept a minimum distance from the start so the test cannot be passed by doing nothing.

This paired design prevents one condition from winning because it sampled easier goals.

## Measurements

The experiment reports **per embodiment**, **seen aggregate**, **held-out aggregate**, **held-out interpolation**, and **held-out extrapolation** metrics:

- success rate;
- final position error;
- final velocity error;
- integrated squared tracking error;
- force energy;
- actuator saturation fraction;
- maximum absolute physical position;
- adaptation steps.

It also runs deterministic interface round-trip probes:

\[
(x,\dot x)\to(q_{raw},\dot q_{raw})\to(x,\dot x)
\]

and

\[
F\to u_{hardware}\to F.
\]

These separate a calibration bug from a policy/morphology failure.

## Raw artifacts

Each condition writes:

```text
<run-dir>/
├── manifest.json
├── steps.csv
├── failures.jsonl
├── summary.json
├── episodes.csv
└── embodiment_metrics.csv
```

Each `steps.csv` row includes the complete physical/interface path:

```text
raw sensor
canonical estimate
descriptor used
desired acceleration
desired force
hardware command
actual physical force
acceleration
next state
tracking error
```

The experiment root writes:

```text
condition_metrics.csv
embodiment_metrics.csv
interface_checks.csv
experiment_manifest.json
analysis.json
ANALYSIS.md
```

## CI mechanism assertions

The deterministic smoke test requires all of the following to hold simultaneously:

```text
correct interface round trips are numerically exact
+ canonical semantics beat raw shared tensors
+ seen_robot_lookup succeeds on both seen robots
+ seen_robot_lookup still has a large held-out/extrapolation gap
+ C and D are reported separately
+ morphology_conditioned succeeds on held-out C/D with zero adaptation
+ continuous morphology conditioning beats seen-ID lookup on held-out bodies
+ wrong morphology metadata degrades transfer
+ wrong action sign/scale breaks the reversed-action robots
+ policy parameter count stays fixed
```

If one relation stops holding, the CI fails; the experiment should be diagnosed rather than the threshold silently weakened.

## Failure taxonomy

A failed episode is logged as `tracking_failure` together with:

- embodiment and split;
- condition;
- final position/velocity error;
- saturation fraction;
- adaptation budget.

Future simulator variants should extend this with collision/contact/controller failures rather than collapsing them into the same category.

## Reproduce

Quick deterministic CI configuration:

```bash
python labs/runnable/lab26_cross_embodiment/run.py \
  --quick \
  --output /tmp/lab26

python labs/runnable/lab26_cross_embodiment/analyze.py \
  /tmp/lab26/condition_metrics.csv \
  /tmp/lab26/embodiment_metrics.csv \
  /tmp/lab26/interface_checks.csv \
  --output-dir /tmp/lab26
```

Full default episode count:

```bash
python labs/runnable/lab26_cross_embodiment/run.py \
  --output /tmp/lab26-full
```

## Falsification conditions

The intended cross-embodiment interpretation should be rejected if:

- multi-seen lookup performs equally well on truly held-out extrapolation;
- correct morphology metadata does not improve held-out behavior;
- wrong morphology tags do not matter;
- wrong action semantics do not change behavior;
- C/D secretly receive task adaptation;
- success requires different policy gains/parameter counts for each body;
- results are reported only as one average that hides seen vs unseen bodies.

## Scientific scope

This CPU experiment is not evidence that a particular VLA has solved robot morphology generalization. It establishes a stricter evaluation decomposition:

```text
interface semantics
→ seen-body support
→ held-out interpolation
→ held-out extrapolation
→ adaptation budget
→ morphology intervention
→ physical closed-loop utility
```

A simulator/real-robot extension should preserve these axes while replacing the point mass with distinct manipulators or humanoid bodies and using a common task-space action contract.
