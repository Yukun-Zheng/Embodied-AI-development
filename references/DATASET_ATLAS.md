# Robot Dataset Atlas

> Frontier snapshot: **2026-09-14**. This atlas is organized by **what supervision a dataset provides and what claims it can support**, not by popularity.

# 1. Why robot data are structurally different

A robot dataset is not merely a collection of images and labels. A useful episode usually couples:

```text
observation_t
+ proprioception_t
+ action_t
+ timestamp_t
+ calibration / frame metadata
+ task / language context
+ outcome / intervention / failure
```

The core object is therefore a temporally aligned interaction trajectory:

\[
\tau = \{(o_t, s_t, a_t, r_t, m_t)\}_{t=0}^{T}.
\]

Here \(m_t\) denotes metadata such as embodiment, camera calibration, controller mode, operator identity, reset condition and safety events.

A dataset can be large yet scientifically weak if any of the following are unknown:

- action semantics;
- control frequency;
- coordinate frame;
- low-level controller;
- success/failure protocol;
- duplicate or near-duplicate episodes;
- train/evaluation overlap;
- embodiment identity;
- intervention history.

---

# 2. Dataset dimensions

Every dataset in this book should be described along the same axes.

| Axis | Questions |
|---|---|
| Embodiment | single arm, bimanual, mobile manipulator, humanoid, hand? |
| Sensors | RGB, depth, point cloud, tactile, FT, proprioception? |
| Action | joint position, joint delta, Cartesian delta, torque, gripper? |
| Control | action rate, controller rate, low-level controller? |
| Demonstration source | teleoperation, kinesthetic, scripted, RL, autonomous? |
| Tasks | single-task, multi-task, open-world, long-horizon? |
| Outcome | success labels, dense rewards, progress, failures? |
| Language | task text, free-form instruction, narration? |
| Time | synchronized timestamps and known latency? |
| Geometry | camera intrinsics/extrinsics, robot/world frames? |
| Scale | episodes, transitions, hours, robots, sites? |
| Diversity | scenes, objects, users, embodiments, lighting, dynamics? |
| License / reproducibility | can the exact training corpus be reconstructed? |

---

# 3. Classical manipulation datasets

## 3.1 BridgeData / BridgeData V2

Representative use:

- multi-task imitation learning;
- visual generalization;
- pretraining for tabletop manipulation.

What it is useful for:

> testing whether a policy can benefit from heterogeneous real-robot demonstrations.

What it does **not** prove by itself:

- broad cross-embodiment transfer;
- whole-body control;
- reliable long-horizon autonomy;
- physical reasoning.

## 3.2 DROID

Important because data are collected across multiple environments and operators with a standardized hardware/data stack.

Research questions:

- scene diversity vs repeated task coverage;
- operator diversity;
- calibration consistency;
- generalization under real-world visual variation.

## 3.3 RoboNet and earlier multi-robot datasets

Historically important because they made cross-robot visual control and dynamics learning concrete research questions.

Their role in the textbook is historical and methodological: they expose the difficulty of combining trajectories from robots with incompatible action spaces.

---

# 4. Open X-Embodiment and dataset mixtures

Open X-Embodiment changed the unit of analysis from “one lab’s dataset” to a **mixture of heterogeneous robot corpora**.

A mixture introduces a new distribution:

\[
p(D)=\sum_k \alpha_k p(D_k).
\]

The mixture weights \(\alpha_k\) become part of the algorithm.

Important questions:

- does a large source dominate gradients?
- are action spaces normalized correctly?
- is the embodiment token informative enough?
- is improvement from diversity or simply more transitions?
- does transfer hold to unseen embodiments or only seen robot families?

A dataset mixture must therefore log not only total data size but per-source sampling statistics.

---

# 5. Human video and egocentric corpora

Human video differs from robot demonstration because actions are usually latent.

Observed:

\[
I_{1:T},\quad \text{possibly language / narration}.
\]

Missing:

\[
a_{1:T}^{robot}.
\]

This creates the human-to-robot grounding problem.

Useful supervision from video can include:

- object interaction order;
- hand-object contact cues;
- task semantics;
- affordance;
- long-horizon structure;
- motion priors.

But video alone does not provide actuator-level control labels.

Negative control:

> pretrain on appearance-matched videos with destroyed temporal order. If downstream performance is unchanged, claimed temporal/physical knowledge may not be used.

---

# 6. Failure and intervention data

Most robot corpora overrepresent successful demonstrations.

For reliable systems we also need:

```text
near miss
failure
human intervention
recovery
aborted rollout
safety stop
```

A useful failure record contains:

- failure time;
- preceding observation window;
- attempted action;
- root-cause label if available;
- human intervention;
- recovery action;
- final outcome.

This enables:

- failure detection;
- recovery policy learning;
- uncertainty calibration;
- offline hard-example mining;
- safety analysis.

---

# 7. Synthetic robot data

Synthetic data sources include:

- scripted planner trajectories;
- privileged-state experts;
- RL experts;
- motion retargeting;
- procedural scenes;
- world-model-generated trajectories.

The key distinction is not “real vs synthetic”, but **which variables are trustworthy**.

For example:

| Signal | Simulation trust level |
|---|---|
| exact pose | high |
| segmentation | high |
| rigid geometry | often high |
| contact force | simulator-dependent |
| frictional micro-dynamics | weak-to-medium |
| tactile texture | often weak |
| camera realism | renderer-dependent |
| human clutter statistics | scene-generator-dependent |

Synthetic scale does not remove the reality gap.

---

# 8. Humanoid and whole-body data

Humanoid data require more metadata than arm datasets.

State may include:

\[
s_t = (q,\dot q,\text{base pose},\text{base velocity},\text{contacts},\text{IMU}).
\]

Important dataset families include:

- human motion capture;
- retargeted motion;
- teleoperated whole-body trajectories;
- locomotion RL rollouts;
- loco-manipulation demonstrations;
- interaction-rich humanoid data.

A motion dataset is not automatically a manipulation dataset. Hand/object contact and force feasibility matter.

---

# 9. Tactile datasets

Tactile learning introduces high-rate local signals.

Typical alignment problem:

```text
camera: 30 Hz
policy: 10–50 Hz
tactile: 100–1000+ Hz
motor control: 500–2000 Hz
```

Naively resampling everything to camera rate can destroy slip/contact information.

Dataset design must preserve:

- raw tactile timestamps;
- sensor geometry;
- preload/contact state;
- force/torque reference where possible;
- synchronized visual/proprioceptive context.

---

# 10. Dataset leakage taxonomy

Leakage is not only exact duplicate frames.

## L1 — frame duplicate
Same image appears in train and test.

## L2 — episode duplicate
Same trajectory or near-copy.

## L3 — object-instance leakage
Same exact object instance under minor visual changes.

## L4 — scene leakage
Same room/layout/reset configuration.

## L5 — task-template leakage
Evaluation is merely paraphrased training tasks.

## L6 — embodiment leakage
Claimed cross-robot test uses an embodiment family represented in training.

## L7 — human-video leakage
Internet pretraining contains evaluation demonstrations.

Any strong generalization claim should explicitly discuss these levels.

---

# 11. Dataset quality metrics

Scale is one axis, not the objective.

Useful statistics:

\[
N_{episode},\; N_{transition},\; H_{hours},\; N_{task},\; N_{object},\; N_{scene},\; N_{robot}.
\]

Also track:

- success/failure ratio;
- action entropy;
- state-space coverage;
- object/scene long-tail;
- operator distribution;
- intervention rate;
- temporal gap statistics;
- missing-data frequency.

A more informative notion is **effective diversity**, not raw size.

---

# 12. Data-mixture experiment template

To distinguish data gain from architecture gain, evaluate a matrix:

| | small corpus | full corpus | held-out robot |
|---|---:|---:|---:|
| baseline architecture | A | B | C |
| new architecture | D | E | F |

Then ask:

- \(B-A\): data scaling gain;
- \(D-A\): architecture gain at matched data;
- \(E-B\): architecture gain after scaling;
- \(F-C\): cross-embodiment gain.

---

# 13. Dataset card template

Every dataset page in this repository should eventually answer:

```text
Name:
Version/date:
Robot(s):
Sensor suite:
Action representation:
Controller:
Action frequency:
Episode count:
Hours:
Tasks:
Objects/scenes:
Success/failure labeling:
Human interventions:
Calibration metadata:
Train/test split protocol:
License:
Known leakage risks:
Known biases:
Best-supported claims:
Claims it cannot support:
```

---

# 14. Research principle

The central lesson is:

> **robot data are part of the model.**

Action semantics, controller, timestamps, embodiment and curation determine what relationship the policy can learn. A paper that changes dataset composition changes the effective learning problem even if the neural architecture is identical.
