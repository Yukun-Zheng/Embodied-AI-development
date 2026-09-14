# Model × Data × Hardware × Benchmark Matrix

> **Purpose:** stop comparing robot models as if checkpoint name were the whole experimental system.
>
> Any empirical result actually comes from a tuple:
>
> \[
> R = F(M,D,E,C,B,P),
> \]
>
> where:
>
> - \(M\): model / architecture;
> - \(D\): training data;
> - \(E\): embodiment / hardware;
> - \(C\): controller / temporal executor;
> - \(B\): benchmark / evaluation distribution;
> - \(P\): protocol / reset / intervention / metric.
>
> A leaderboard that compares only \(M\) while the other five axes change is not an architecture comparison.

---

# 1. The six-layer experiment contract

```text
MODEL
  representation / action generator / memory / world model
        ↓
DATA
  demonstrations / robot fleet / human video / synthetic / experience
        ↓
EMBODIMENT
  arm / bimanual / mobile / humanoid / hand
        ↓
EXECUTION
  chunking / async / RTC / controller / WBC
        ↓
BENCHMARK
  task / object / scene / morphology distribution
        ↓
PROTOCOL
  reset / trial count / intervention / metric
```

Every result in the textbook should be mentally expanded to this stack.

---

# 2. Representative system matrix

The following is a **mechanism-oriented** summary. It is not a performance ranking.

| System | Action path | Typical data role | Embodiment scope | Temporal/runtime layer | Evaluation meaning |
|---|---|---|---|---|---|
| ACT | continuous action chunk | teleop demonstrations | especially bimanual tabletop | chunk + temporal aggregation/execution | fine-grained imitation under matched setup |
| Diffusion Policy | diffusion action trajectory | demonstrations | arm / manipulation | receding horizon | multimodal continuous action learning |
| OpenVLA | discrete action tokens | Open X / RLDS mixture | heterogeneous robot data but fixed action interfaces per data source | AR decode + external execution | open VLA / language-conditioned robot action |
| SmolVLA | flow action chunk | LeRobot datasets / robot corpora | multiple supported robots through preprocessing/config | queue / async / RTC | small/open VLA under full software stack |
| GR00T N1.7 | embodiment-conditioned flow/DiT action | heterogeneous robot / humanoid data | explicit embodiment-tagged robots | async / RTC / deployment runtime | cross-embodiment foundation policy stack |
| Gemini Robotics 2 | proprietary whole-body VLA stack | large internal multimodal/robot corpora | multiple robot types / whole body | hidden production runtime | official whole-body / reasoning capability evidence; limited source audit |
| Helix 02 | multi-rate humanoid policy | internal human/robot video and experience | Figure humanoid | slow semantic + fast visuomotor | whole-body humanoid execution |
| V-JEPA 2.1 AC | future latent prediction | video + DROID robot trajectories | action/state-conditioned prediction | no direct action executor by itself | predictive representation / latent dynamics |
| Cosmos family | generative world model | internet/synthetic/video/physical data | not one robot policy | simulator/generator runtime | synthetic data / world-generation capability |

The point is that each row occupies a different place in the embodied stack.

---

# 3. Action-space matrix

| Family | Model output | Physical meaning still needed downstream |
|---|---|---|
| action-token VLA | token sequence → decoded action vector | frame, scale, controller, rate |
| continuous flow/diffusion | action trajectory tensor | controller, execution horizon, rate |
| target-pose policy | Cartesian pose / delta | IK, collision, impedance/WBC |
| joint-target policy | joint pos/vel target | servo gains, limits, dynamics |
| torque policy | torque | actuator dynamics, safety |
| world model | predicted future state/latent | planner/evaluator must choose action |
| language planner | skill/subgoal | skill implementation and feasibility |

Two policies that both report “7-D action” may implement completely different physical interfaces.

---

# 4. Dataset × claim matrix

| Data source | Strongest claims it can support | Claims it cannot support alone |
|---|---|---|
| single-robot demos | imitation / task generalization near one embodiment | cross-embodiment generality |
| multi-task same robot | task scaling | morphology transfer |
| Open X-style multi-robot mixture | heterogeneous data transfer | unseen-morphology zero-shot unless explicitly tested |
| human video | semantics / interaction prior / task structure | actuator-level control |
| motion capture | body motion prior | object-contact manipulation reliability |
| simulation expert | scalable state/action supervision | real contact fidelity |
| failure / intervention logs | recovery / safety / uncertainty | nominal competence by itself |
| online robot experience | deployment learning | stable retention unless evaluated |
| world-model-generated trajectories | synthetic coverage | real physical validity unless audited |

A model’s apparent generality is bounded by what its data distribution actually identifies.

---

# 5. Embodiment × research-question matrix

| Embodiment | Dominant physical issues | What a model comparison must control |
|---|---|---|
| fixed-base arm | reachability, Cartesian precision, contact | gripper, camera, controller |
| bimanual | relative pose, collision, coordination | synchronization, workspace, arm symmetry |
| dexterous hand | contact observability, high-dimensional action | tactile sensors, actuation coupling |
| mobile manipulator | base-arm coordination, moving viewpoint | navigation stack, base dynamics |
| quadruped | balance/contact switching | terrain, actuator torque, WBC |
| humanoid | floating base, balance, locomotion+manipulation | whole-body controller, fall policy, hand type |
| heterogeneous fleet | action/state mismatch | adaptation budget, embodiment descriptor |

Therefore “success on humanoid” is not a scalar extension of tabletop manipulation.

---

# 6. Benchmark × claim matrix

| Benchmark type | Good for | Weak evidence for |
|---|---|---|
| Push-T / toy 2D | mechanism isolation, action multimodality | foundation-model generality |
| MetaWorld | standardized manipulation RL | photorealistic visual robustness |
| RLBench | multi-task manipulation | true open-world real robotics |
| CALVIN | long-horizon compositional manipulation | embodiment transfer |
| LIBERO | lifelong/multi-task manipulation | whole-body control |
| ManiSkill | physics-rich simulation / scalable manipulation | real-world robustness by itself |
| RoboTwin | bimanual / multi-policy comparison in simulation | physical real-world validity alone |
| Habitat / ObjectNav | embodied navigation | dexterous manipulation |
| BEHAVIOR / OmniGibson | household long-horizon interaction | exact real-contact performance |
| real robot benchmark | physical validity | broad generalization unless distribution is sufficiently diverse |

A benchmark result should only support the axes it actually varies.

---

# 7. Controller confound matrix

Suppose two VLA methods produce the same end-effector delta.

Method A uses:

```text
IK + position servo
```

Method B uses:

```text
operational-space impedance
```

Then contact success difference is not purely model-level.

Control confounds include:

- IK solver;
- damping;
- trajectory interpolation;
- impedance gains;
- gripper force;
- WBC hierarchy;
- collision shield;
- action smoothing;
- safety clipping.

Report controller stack explicitly.

---

# 8. Temporal-execution confound matrix

Same checkpoint, different executor:

| Executor | Behavior |
|---|---|
| one-step closed loop | frequent replanning, high inference demand |
| full chunk open-loop | low compute, stale action risk |
| receding horizon k-step | compromise |
| temporal aggregation | overlaps predictions |
| async queue | inference/execution decoupled |
| RTC | continuous replacement conditioned on old chunk |

A “real-time VLA improvement” may come entirely from this layer.

Therefore define:

\[
\text{System}=(\pi_\theta, E_{temporal}, C_{low-level}).
\]

---

# 9. Model scaling vs data scaling vs hardware scaling

A modern robot result can improve because of:

\[
\Delta P
=
\Delta P_{model}
+
\Delta P_{data}
+
\Delta P_{hardware}
+
\Delta P_{runtime}
+
\Delta P_{protocol}
+
\text{interactions}.
\]

A useful ablation cube is:

```text
architecture × data scale × hardware/controller
```

At minimum test matched-data architecture comparison.

For whole-body systems also test matched-controller where feasible.

---

# 10. Cross-embodiment evaluation matrix

The phrase “cross-embodiment” should identify exactly which cell is tested.

| Train | Test | Difficulty |
|---|---|---|
| same robot | new task | task transfer |
| same morphology family | new robot instance | calibration/dynamics transfer |
| different arm geometry | new arm | kinematic/morphology transfer |
| gripper → dexterous hand | new action topology | strong morphology transfer |
| fixed arm → mobile manipulator | added base | topology + navigation |
| arm → humanoid | floating base + many new joints | extreme embodiment transfer |

Also report adaptation budget:

\[
B=(N_{demo},N_{interaction},N_{updates},T_{wall},P_{new}).
\]

Without \(B\), “few-shot” is not comparable.

---

# 11. Data overlap / leakage matrix

Generalization claims can be invalidated by multiple overlap levels:

```text
exact frame
same trajectory
same object instance
same room / scene
same task composition
same robot family
internet video containing evaluation behavior
```

For foundation models, hidden web/video pretraining makes perfect leakage audit difficult.

Therefore report evidence level rather than absolute claims of novelty.

---

# 12. Evidence × openness matrix

| Source state | What we can inspect |
|---|---|
| paper only | architecture / reported experiments |
| paper + checkpoint | inference behavior |
| code | processor/model/loss/runtime mechanism |
| code + data | training problem and distribution |
| code + data + benchmark | stronger reproduction |
| real hardware open | end-to-end system reproduction |
| independent multi-lab replication | strongest empirical evidence |

Open source does not guarantee correctness, but it dramatically improves **mechanism auditability**.

---

# 13. A normalized system card

Any modern robot model should eventually get a row/card with:

```text
Model:
Commit / checkpoint:
Training data:
Human-video data:
Synthetic data:
Online experience:
Robot embodiments:
Observation modalities:
State representation:
Memory:
Action representation:
Action horizon:
Generator:
Inference steps / token length:
Policy rate:
Temporal executor:
Low-level controller:
Benchmark:
Reset protocol:
Trials:
Human intervention:
Latency:
Evidence level:
Known failure modes:
```

This is the minimum unit for meaningful comparison.

---

# 14. Example: why OpenVLA vs GR00T N1.7 is not a clean architecture comparison

They differ in multiple axes:

```text
OpenVLA:
- action tokens
- different backbone/data era
- one-step action baseline path
- different embodiment interface

GR00T N1.7:
- continuous flow/DiT action chunk
- explicit embodiment tags
- action horizon
- async/RTC deployment support
- different data/robot stack
```

If GR00T scores higher on a benchmark, one cannot attribute gain solely to flow matching.

A clean experiment would transplant action heads under shared representation/data/controller.

---

# 15. Example: why V-JEPA 2.1 vs VLA is not a leaderboard comparison

V-JEPA action-conditioned predictor learns:

\[
(z_t,a_t,s_t)\rightarrow z_{t+1}.
\]

A VLA learns approximately:

\[
(o_t,l_t,s_t)\rightarrow a_t.
\]

One predicts world consequences; one chooses actions.

The meaningful comparison is not “success score A vs B”.

The meaningful system experiment is:

```text
VLA only
vs
VLA + predictive representation
vs
VLA + action-conditioned world model
```

with matched policy/data where possible.

---

# 16. The matrix suggests the real research frontier

Many 2026 systems already have strong components separately:

- semantic VLM;
- continuous action expert;
- real-time executor;
- predictive world representation;
- memory;
- whole-body controller.

The deeper question is now interface design:

```text
What is shared?
What is modular?
What runs at which rate?
What learns online?
What remains safety-critical and fixed?
```

A useful future architecture may therefore be judged less by parameter count and more by whether it provides a coherent, falsifiable answer to these interface questions.
