# Lab 31 — Reasoning Negative Control

> **Question:** when a high-level planner appears to “reason”, does the plan actually carry correct causal structure into behavior, or is it merely plausible-looking intermediate text / action syntax?

This runnable Lab turns reasoning into an **executable mechanism**. A planner does not receive credit for producing a fluent explanation. It emits a sequence of high-level actions that is consumed by an executor and judged only by the true environment state transitions.

The minimal scientific chain is:

```text
world state + task goal
→ causal model
→ high-level plan
→ executable action sequence
→ prerequisite satisfaction / violation
→ environment transition
→ final task success
```

The core claim is deliberately narrow:

> A reasoning module is behaviorally useful only if the causal structure, ordering and entity bindings encoded in its plan survive execution in the true environment.

## Why this Lab is not a CoT benchmark

Natural-language plausibility is not the dependent variable here. A long explanation may be wrong; a short plan may be correct. Therefore this Lab does **not** score chain-of-thought length, lexical fluency or verbal confidence.

Instead, every planned step is converted into one of a small set of executable operators:

```text
move(location)
pickup(item)
drop(item)
unlock(key)
open(cabinet)
place(package, bin)
```

Those operators have explicit preconditions and effects. The environment, not the planner, decides whether they are valid.

## Environment

The toy workbench contains:

- a start location and junction;
- two supply locations;
- a cabinet;
- two goal bins;
- a red and blue key;
- a red and blue package;
- one-item carrying capacity.

Each episode deterministically randomizes from the run seed:

- which key opens the cabinet;
- which key is at which supply location;
- target package;
- target bin;
- whether the cabinet starts locked.

The target package begins inside the cabinet. If the cabinet is locked, success requires a genuine prerequisite chain:

```text
find required key
→ carry it to cabinet
→ unlock cabinet
→ open cabinet
→ release / manage inventory
→ pick target package
→ navigate to requested bin
→ place correct package
```

This creates a small but real planning horizon: going directly to the cabinet does not solve a locked episode.

## Conditions

### 1. `correct_plan`

Breadth-first search over the **true** causal transition model. It finds a shortest executable plan.

This is not an oracle success flag: the returned plan is still replayed step by step through the same environment transition function as every negative control.

### 2. `no_plan`

A myopic target-directed policy. It can exploit an already-unlocked cabinet, but it performs no prerequisite search. On a locked cabinet, retrieving a key does not improve its one-step task progress, so the policy keeps trying to approach/open the cabinet instead of solving the latent dependency.

This control asks whether multi-step causal planning adds value beyond reactive goal seeking.

### 3. `random_plan`

Takes the exact action multiset from the correct plan but deterministically shuffles the order.

This matches plan vocabulary and approximate compute/output budget while destroying temporal structure.

### 4. `fluent_wrong_plan`

Runs the **same BFS planner** under a coherent but false causal model in which the other key is assumed to open the cabinet.

Crucially, this plan is internally valid under its own model. The Lab separately executes it inside that false model and records `self_model_success_rate`.

It is then executed in the true world. Thus we can measure the gap

\[
\text{internal coherence} \;\not\Rightarrow\; \text{physical correctness}.
\]

This is the mechanism analogue of a fluent but causally wrong explanation.

### 5. `shuffled_binding`

Preserves the correct plan order and navigation structure but swaps key, package and bin bindings.

This attacks variable/entity binding without destroying all temporal structure.

## What is controlled

The plan-based controls share the same environment episodes and the same underlying correct plan length. `random_plan` and `shuffled_binding` are derived directly from that plan. The wrong-model planner uses the same search algorithm and symmetric environment model.

The analyzer explicitly checks that mean plan length is matched across plan-based conditions. Therefore a success difference cannot be attributed merely to a longer plan or more planner output.

## Measurements

Each condition reports:

- overall task success;
- success on locked episodes;
- success on easy unlocked episodes;
- action validity;
- invalid-action count;
- prerequisite / constraint violations;
- executed steps;
- final and maximum causal progress;
- plan length;
- planner node expansions;
- self-model success for model-based planners.

The important derived quantities include:

\[
\Delta_{reasoning}
=
S_{correct}-S_{no\ plan},
\]

and the wrong-model reality gap

\[
\Delta_{model\rightarrow world}
=
S_{wrong\ model\;internal}-S_{wrong\ plan\;real}.
\]

A useful reasoning module should create a large positive first gap while the second experiment demonstrates that internally coherent planning is insufficient when the causal model is wrong.

## Raw artifacts

Every condition uses the common runnable-Lab contract:

```text
<run-dir>/
├── manifest.json
├── steps.csv
├── failures.jsonl
├── summary.json
├── episodes.csv
└── plans.jsonl
```

`steps.csv` stores each executed operator together with:

- state before / after;
- action argument;
- validity;
- violation category;
- causal progress before / after;
- task bindings and lock state.

`plans.jsonl` stores the structured actions and a readable text rendering. The readable text is only an audit surface; it is never used as reward or as a success metric.

The experiment root also contains:

```text
condition_metrics.csv
experiment_manifest.json
analysis.json
ANALYSIS.md
```

## Failure taxonomy

Failures are mechanism-specific rather than collapsed into one `success=0` bucket:

| condition | failure category | interpretation |
|---|---|---|
| `correct_plan` | `unexpected_correct_plan_failure` | implementation/model consistency problem |
| `no_plan` | `missing_prerequisite_reasoning` | reactive policy cannot solve latent dependency |
| `random_plan` | `plan_order_failure` | correct operators with destroyed ordering |
| `fluent_wrong_plan` | `wrong_causal_model` | coherent planning under the wrong intervention model |
| `shuffled_binding` | `entity_binding_failure` | sequence structure preserved but referents are wrong |

## CI mechanism assertions

The deterministic smoke test does not merely check that the script exits. It requires:

```text
correct plan succeeds in the true world
+ locked episodes defeat the no-plan baseline
+ unlocked easy episodes remain solvable without reasoning
+ fluent-wrong plan succeeds inside its own wrong model
+ the same fluent-wrong plan fails on locked real-world episodes
+ fluent-wrong actions are substantially more valid than random-plan actions
+ random ordering fails
+ shuffled entity binding fails
+ plan length / output budget is matched
```

If any relation stops holding, CI fails and the experiment must be diagnosed rather than the claim silently preserved.

## Reproduce

Quick deterministic configuration:

```bash
python labs/runnable/lab31_reasoning_negative_control/run.py \
  --quick \
  --output /tmp/lab31

python labs/runnable/lab31_reasoning_negative_control/analyze.py \
  /tmp/lab31/condition_metrics.csv \
  --output-dir /tmp/lab31
```

Full default episode count:

```bash
python labs/runnable/lab31_reasoning_negative_control/run.py \
  --output /tmp/lab31-full
```

## Falsification conditions

This Lab should **not** support the reasoning claim if, for example:

- `correct_plan` does not outperform `no_plan` on locked episodes;
- `fluent_wrong_plan` works equally well in the true world;
- random order succeeds at comparable rates;
- entity-binding corruption does not matter;
- the purported reasoning gain disappears after matching plan budget;
- success comes from a hidden oracle shortcut rather than executing the plan.

## Scientific scope

This is a symbolic mechanism experiment, not evidence that a particular LLM, VLM or VLA reasons correctly. It establishes an evaluation pattern that can later be lifted into embodied systems:

```text
reasoning trace / plan
→ executable intermediate representation
→ causal intervention
→ physical behavior
→ negative controls
```

A future simulator or real-robot version should preserve this causal structure while replacing symbolic operators with perception-conditioned skills and real execution failures.
