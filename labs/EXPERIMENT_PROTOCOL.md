# Unified Experiment Protocol

> Every experiment in this repository should be readable as a scientific argument, not merely a training script.

# 1. The minimum scientific unit

Before any experiment starts, write the following block:

```text
Question:
Hypothesis:
Mechanism:
Independent variable:
Dependent variable:
Controls:
Positive control:
Negative control:
Primary metric:
Secondary metrics:
Failure criterion:
Scale-up criterion:
```

If these cannot be stated clearly, do not start expensive training.

---

# 2. Separate four sources of gain

Robot-learning results are often confounded by multiple changes.

At minimum separate:

\[
\text{performance gain}
= \text{data} + \text{architecture} + \text{training} + \text{system} + \text{interaction terms}.
\]

A recommended factorial matrix is:

| | old data | new data |
|---|---:|---:|
| old architecture | A | B |
| new architecture | C | D |

Then estimate:

- data gain: \(B-A\);
- architecture gain: \(C-A\);
- interaction: \(D-C-B+A\).

Extend the matrix when post-training or controller changes are also introduced.

---

# 3. Freeze the system contract

Before comparing methods, freeze:

```text
robot / embodiment
observation definition
action semantics
coordinate frame
low-level controller
action frequency
sensor frequency
latency pipeline
reset protocol
train/test split
metrics
```

A method comparison is invalid if one model gets a different controller or more favorable action semantics without explicit accounting.

---

# 4. Required experiment metadata

Every run must save:

- git commit;
- config;
- random seed;
- dataset version/hash;
- simulator version;
- robot asset version;
- model checkpoint identifier;
- hardware/GPU info;
- wall-clock start/end;
- dependency lockfile;
- calibration files for real robots;
- environment randomization parameters.

Recommended run ID:

```text
YYYYMMDD-HHMM_<project>_<method>_<seed>
```

---

# 5. Raw data first

Never save only final scalar metrics.

At minimum preserve:

```text
per-step observation summaries
per-step action
policy latency
controller status
success / progress
intervention markers
failure markers
termination reason
```

For real robots also preserve synchronized sensor logs when storage permits.

This allows later failure analysis without rerunning expensive trials.

---

# 6. Three levels of evaluation

## Level A — unit/mechanism test

Smallest environment possible.

Goal:

> verify that the proposed mechanism actually changes the intended intermediate variable.

Example: active perception should reduce uncertainty before testing task success.

## Level B — controlled benchmark

Multiple tasks/seeds with fixed protocol.

Goal:

> measure whether mechanism gain survives realistic complexity.

## Level C — external validity

New objects, scenes, embodiments, perturbations, or real robot.

Goal:

> test whether the explanation generalizes beyond the construction used to invent it.

---

# 7. Positive and negative controls

A **positive control** proves the metric can detect a known useful intervention.

A **negative control** attacks the proposed explanation.

Examples:

### memory

- correct retrieved episode;
- random episode;
- temporally shuffled episode;
- no memory.

### world model

- correct learned model;
- frozen random model;
- shuffled future;
- wrong dynamics.

### reasoning

- correct plan;
- removed plan;
- random plan;
- plausible but wrong plan.

### geometry

- correct frame;
- random frame rotation;
- corrupted depth;
- appearance-only baseline.

If a method survives the wrong control, the claimed mechanism may not actually be used.

---

# 8. Seed policy

Do not choose seed count after seeing variance.

Recommended workflow:

1. small pilot to estimate variance;
2. choose target confidence/effect size;
3. freeze seed count;
4. run all methods under same seeds where possible.

For simulation, paired seeds reduce variance.

For real robots, document unavoidable environment drift.

---

# 9. Confidence intervals

For continuous metrics report:

\[
\bar x \pm CI.
\]

For success rates report binomial confidence intervals, not only raw percentages.

A difference like `80% vs 85%` is not interpretable without number of trials.

Also report effect size when useful.

---

# 10. Generalization matrix

A strong robot policy should be evaluated by source of novelty.

| Axis | ID | OOD |
|---|---|---|
| object | seen | unseen instance/category |
| scene | seen | unseen room/layout |
| task | seen | new composition |
| language | seen wording | new paraphrase/goal |
| dynamics | nominal | changed mass/friction |
| embodiment | trained robot | unseen robot |

Do not collapse all OOD conditions into one score.

---

# 11. Long-horizon evaluation

A long task should not be measured only by final success.

Log subgoal sequence:

\[
g_1\rightarrow g_2\rightarrow\cdots\rightarrow g_K.
\]

Metrics:

- completed subgoals;
- time-to-failure;
- recovery count;
- human interventions;
- replanning count;
- accumulated error;
- final success.

This distinguishes catastrophic early failure from near-completion.

---

# 12. Real-time evaluation

Measure the complete latency budget:

\[
\tau_{total}
=\tau_{sensor}+\tau_{pre}+\tau_{network}+\tau_{model}+\tau_{post}+\tau_{controller}.
\]

Also log jitter:

\[
J = std(\tau_{total}).
\]

A faster mean with large jitter can be worse for control.

Report:

- mean;
- median;
- p95/p99;
- missed deadlines;
- action age at execution.

---

# 13. Real-robot reset protocol

Reset procedure is part of the benchmark.

Document:

- initial object pose distribution;
- robot home configuration;
- camera/world calibration;
- operator intervention;
- whether failed trials are rerun;
- whether model sees reset actions.

Selective reset can bias results dramatically.

---

# 14. Human intervention protocol

If a human can intervene, intervention is a metric.

Record:

```text
intervention time
reason
human action
robot state
whether trial counted as success
```

Recommended metrics:

\[
IR=\frac{N_{intervention}}{N_{episode}}
\]

and

\[
TBI=\frac{\text{autonomous time}}{N_{intervention}+\epsilon}.
\]

---

# 15. Failure taxonomy protocol

Every failed episode gets one primary category and optional secondary causes.

Top-level categories:

```text
sensor / calibration
time synchronization
perception / grounding
state estimation
reasoning / planning
action generation
latency / executor
controller
contact / dynamics
hardware / safety
data / OOD
unknown
```

Track category frequencies before and after a method change.

A +5% aggregate improvement is scientifically useful only when we know which failures disappeared.

---

# 16. Mechanism evidence ladder

Claims should climb this ladder:

### E0 — performance correlation
Method scores higher.

### E1 — intermediate variable changes
Claimed mechanism is observable.

### E2 — intervention
Directly perturb mechanism and behavior changes predictably.

### E3 — counterfactual / negative control
Incorrect mechanism degrades performance.

### E4 — external validity
Same mechanism explains new tasks/scenes/robots.

Strong mechanism papers should target E2–E4.

---

# 17. World-model protocol

A world model should not be judged only by prediction quality.

Measure:

1. state/video prediction;
2. action sensitivity;
3. counterfactual correctness;
4. uncertainty calibration;
5. downstream planning improvement.

The decisive metric is:

\[
\Delta J = J_{policy+WM}-J_{policy-no-WM}.
\]

Run wrong-model controls to prove the policy uses it.

---

# 18. VLA protocol

For VLA evaluation, report separately:

- semantic instruction following;
- grounding;
- spatial precision;
- temporal execution;
- contact success;
- recovery;
- latency;
- unseen object/scene/task;
- embodiment transfer.

A single average task success rate hides too much.

---

# 19. Continual-learning protocol

After each task/domain \(k\), evaluate all previous tasks.

Construct matrix:

\[
R_{i,j}=\text{performance on task }j\text{ after learning }i.
\]

Then report:

- average accuracy/success;
- forgetting;
- forward transfer;
- backward transfer;
- memory/replay cost;
- parameter growth;
- adaptation samples/time.

For self-evolving architectures also report compute/structure growth.

---

# 20. Cross-embodiment protocol

Split transfer into:

1. seen robot, new task;
2. new robot in seen morphology family;
3. new morphology;
4. changed sensor layout;
5. changed action topology.

Measure adaptation budget:

\[
B=(N_{demo},N_{interaction},N_{gradient\ steps},T_{wall}).
\]

“Few-shot transfer” without a budget is underspecified.

---

# 21. Sim-to-real protocol

Evaluate gap by controlled decomposition:

- visual gap;
- dynamics gap;
- latency gap;
- sensor noise gap;
- contact gap;
- scene/task distribution gap.

Do not report only one real-world success number.

A useful experiment changes one gap source at a time.

---

# 22. Safety gate before scale-up

Before real-robot deployment, verify:

```text
joint limits
velocity limits
torque/force limits
workspace limits
self-collision
external collision
e-stop
watchdog
network timeout
uncertainty stop
human override
```

Learning performance never overrides physical safety constraints.

---

# 23. Publication table template

Every major result table should be reconstructible from raw runs.

Recommended columns:

```text
method
data version
checkpoint
seed/trial count
mean metric
CI
latency
intervention rate
failure distribution
compute budget
```

Avoid a table containing only final success rate.

---

# 24. Experiment report template

```text
# Experiment ID

## Question
## Hypothesis
## Mechanism
## System contract
## Data
## Methods
## Controls
## Metrics
## Seeds/trials
## Results
## Confidence intervals
## Failure analysis
## Negative-control result
## Unexpected observations
## Limitations
## Reproduction command
## Next experiment
```

---

# 25. Final rule

A training run is not automatically an experiment.

A scientific experiment must make it possible to answer:

> **what belief about the system changed because of this result, and what result would have falsified it?**
