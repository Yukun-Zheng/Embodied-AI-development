# Embodied AI Failure Atlas

> A robot “failed” is not a diagnosis. This atlas decomposes failure across sensing, state, representation, planning, action generation, temporal execution, control, contact, hardware, data and evaluation.

The top-level causal chain is:

```text
world
→ sensing
→ synchronization / calibration
→ representation / state
→ reasoning / planning
→ action generation
→ temporal executor
→ controller / safety
→ actuator / contact
→ world
```

A visible task failure can originate anywhere along this chain.

---

# 1. How to use the atlas

For every failed episode, record:

```text
primary failure category
secondary contributing category
first time failure became detectable
first time failure became irreversible
model confidence / uncertainty
human intervention
recovery attempt
final outcome
```

Do not label based only on the final symptom.

Example:

```text
final symptom: gripper misses object
possible roots:
- camera calibration drift
- stale observation
- wrong object grounding
- pose estimation bias
- action-frame bug
- IK singularity
- controller lag
```

---

# 2. Sensor / calibration failures

## F-S01 — Camera intrinsics mismatch

**Symptom:** depth/back-projection or pixel-to-ray geometry is systematically wrong.

**Diagnosis:** reproject calibration target; compare pixel residual.

**Negative control:** use synthetic perfect intrinsics.

## F-S02 — Camera extrinsics drift

**Symptom:** consistent Cartesian offset that changes when camera mount moves.

**Diagnosis:** independently re-estimate `T_base_camera`.

## F-S03 — Wrong transform direction

**Symptom:** object pose appears mirrored/inverted or moves opposite robot motion.

Common mistake:

\[
T_{AB}\neq T_{BA}.
\]

## F-S04 — Quaternion convention mismatch

`[w,x,y,z]` vs `[x,y,z,w]`.

**Symptom:** orientation commands are catastrophically wrong while translation works.

## F-S05 — Left/right-handed coordinate mismatch

**Symptom:** one axis changes sign unexpectedly across simulator/robot stack.

## F-S06 — Depth scale error

mm vs m or sensor-specific scaling.

**Symptom:** reconstructed geometry is uniformly too large/small.

## F-S07 — IMU bias / drift

**Symptom:** base orientation/velocity slowly diverges despite static robot.

## F-S08 — Encoder zero-offset error

**Symptom:** FK and real arm disagree even under static pose.

## F-S09 — Force/Torque sensor bias

**Symptom:** false contact or incorrect force-control equilibrium.

## F-S10 — Tactile preload drift

**Symptom:** contact classifier changes with time/temperature without actual contact change.

---

# 3. Time / synchronization failures

## F-T01 — Camera/state timestamp misalignment

**Symptom:** image shows pre-motion state while proprioception is post-motion.

## F-T02 — Action timestamp ambiguity

Does `a_t` cause transition from `s_t→s_{t+1}` or correspond to already-executing command?

Wrong convention teaches incorrect dynamics.

## F-T03 — Variable network latency

Mean latency may be acceptable while p99 causes intermittent catastrophic stale actions.

## F-T04 — Sensor-clock drift

Independent devices slowly desynchronize over long episodes.

## F-T05 — Queue lag

Policy predicts new actions but old queue continues executing.

## F-T06 — Inference overrun

\[
\tau_{inference}>\Delta t_{policy}.
\]

The model acts on increasingly stale state.

## F-T07 — Chunk boundary discontinuity

Adjacent action chunks disagree, producing jerk/contact loss.

## F-T08 — Wrong action horizon alignment

Training labels use one horizon; deployment executes another.

---

# 4. Visual perception / grounding failures

## F-V01 — Object identity confusion

Semantically similar objects are swapped.

## F-V02 — Instance grounding failure

Correct category, wrong instance.

## F-V03 — Occlusion failure

Policy acts as if hidden geometry were known.

## F-V04 — Reflection / transparency failure

Visual depth/segmentation becomes unreliable.

## F-V05 — Texture shortcut

Policy uses color/background instead of geometry.

**Negative control:** texture randomization with fixed geometry.

## F-V06 — Camera viewpoint shortcut

Model learns fixed scene-camera correlation.

## F-V07 — Poor small-object resolution

Semantic encoder loses tiny task-critical feature.

## F-V08 — Motion blur

Wrist/head camera movement corrupts action-critical features.

## F-V09 — Lighting shift

Policy representation changes despite invariant geometry.

## F-V10 — 2D semantic success, 3D geometric failure

Model recognizes object but estimates grasp/contact geometry poorly.

---

# 5. 3D / state-estimation failures

## F-E01 — Pose bias

Estimated object pose has stable systematic offset.

## F-E02 — Multimodal state collapsed to one estimate

Ambiguous observation is represented as overconfident single pose.

## F-E03 — Kalman inconsistency

Filter covariance becomes too small relative to actual estimation error.

## F-E04 — SLAM relocalization jump

Global pose discontinuity creates downstream command jump.

## F-E05 — Dynamic object treated as static map

World model/state estimator violates scene dynamics.

## F-E06 — Robot self-state delayed

Proprioceptive state is accurate but stale.

## F-E07 — Contact state unobserved

Vision-only policy cannot distinguish pre-contact/post-contact states.

## F-E08 — Hidden task state missing

Long task depends on prior event not present in current observation.

This is a memory problem, not necessarily a policy-capacity problem.

---

# 6. Representation failures

## F-R01 — Semantic overcompression

Feature preserves category but discards metric geometry.

## F-R02 — Geometry overfit

Representation works in one camera/frame arrangement only.

## F-R03 — Missing action-relevant variable

Example: friction/contact compliance absent from latent state.

## F-R04 — Entangled embodiment identity

Robot identity is encoded through incidental camera layout rather than explicit morphology.

## F-R05 — No uncertainty representation

Policy cannot distinguish “known wrong” from “unknown”.

## F-R06 — Temporal aliasing

Single-frame representation cannot distinguish opposite velocity states.

## F-R07 — Predictive representation ignores action

World-model feature predicts average temporal evolution but is insensitive to intervention.

**Negative control:** shuffle action and test prediction change.

---

# 7. Language / reasoning failures

## F-L01 — Instruction parsing error

Wrong task semantics.

## F-L02 — Correct semantics, impossible physics

Plan is linguistically valid but unreachable / unstable.

## F-L03 — Hallucinated object/state

Reasoner assumes an object/action outcome not observed.

## F-L04 — Wrong task decomposition

Subgoals are individually feasible but globally inconsistent.

## F-L05 — No progress tracking

Robot repeats already-completed step.

## F-L06 — Reasoning disconnected from motor policy

Language plan changes but motor action barely changes.

**Negative control:** inject wrong plan and measure causal effect.

## F-L07 — Overlong deliberation causes stale action

Reasoning improves semantics but destroys real-time relevance.

## F-L08 — Human clarification omitted

System guesses when uncertainty should trigger a question.

---

# 8. Planning failures

## F-P01 — Collision model mismatch

Planner uses geometry different from actual robot/scene.

## F-P02 — Planning in wrong frame

Target transformed incorrectly.

## F-P03 — Reachability ignored

High-level policy chooses goal outside kinematic workspace.

## F-P04 — Singular path

Trajectory passes through low-manipulability configuration.

## F-P05 — Dynamic obstacle treated as static

## F-P06 — Contact task treated as collision avoidance

Planner avoids the interaction needed to complete task.

## F-P07 — TAMP symbolic/geometric mismatch

Symbolic action is valid but no feasible geometric realization exists.

## F-P08 — World-model exploitation

Planner selects actions that exploit model error rather than real physics.

---

# 9. Action-representation failures

## F-A01 — Wrong action units

Radians vs degrees; meters vs centimeters.

## F-A02 — Absolute vs delta mismatch

## F-A03 — Base-frame vs end-effector-frame delta mismatch

## F-A04 — Rotation representation discontinuity

Euler-angle wrap or quaternion sign ambiguity.

## F-A05 — Gripper semantics mismatch

Binary open/close vs width vs effort.

## F-A06 — Action-token quantization saturation

Action lies outside representable/normalized range.

## F-A07 — Wrong action dimension order

Example: `[x,y,z,rx,ry,rz,g]` mismatch.

## F-A08 — Dataset-specific normalization mismatch

Correct normalized action decoded using wrong robot/dataset stats.

---

# 10. Generative-policy failures

## F-G01 — Mode averaging in regression

MSE policy predicts unsafe mean between two valid modes.

## F-G02 — Diffusion/flow under-sampling

Too few inference steps distort action distribution.

## F-G03 — Diffusion/flow over-sampling latency

Higher sample quality creates stale control.

## F-G04 — Chunk too long

Policy remains open-loop through perturbation.

## F-G05 — Chunk too short

Excess inference overhead and temporal incoherence.

## F-G06 — Multimodality caused by missing state

Generative action model compensates for partial observability rather than genuine strategy diversity.

## F-G07 — Action expert ignores language

Strong motor prior dominates conditioning.

## F-G08 — Action expert ignores proprioception

Visual shortcut works until robot initial state shifts.

---

# 11. VLA-specific failures

## F-VLA01 — VLM semantic prior not grounded to robot reachability

## F-VLA02 — Language dominates geometry

## F-VLA03 — Internet prior conflicts with robot embodiment

Human-like action semantics may not match robot capabilities.

## F-VLA04 — Embodiment tag acts as dataset ID only

Fails on unseen morphology.

## F-VLA05 — Backbone/action-head gradient interference

Motor fine-tuning damages semantic representation or vice versa.

## F-VLA06 — Wrong post-training distribution

Task specialization destroys general competence.

## F-VLA07 — Generalization claim is data overlap

## F-VLA08 — Action decoding correct, controller incompatible

Checkpoint is blamed for downstream system mismatch.

---

# 12. Temporal-executor failures

## F-X01 — Full chunk executes despite new obstacle

## F-X02 — Async inference returns out-of-date chunk

## F-X03 — RTC overlap index mismatch

Previous and new chunks are aligned to different physical times.

## F-X04 — RTC over-constrains prefix

Continuity preserved but necessary correction suppressed.

## F-X05 — RTC under-constrains prefix

Boundary jerk remains.

## F-X06 — Buffer underrun

Robot waits/stops because next action chunk is late.

## F-X07 — Buffer overrun / excessive backlog

Very stale commands remain queued.

---

# 13. Controller failures

## F-C01 — PID gains too aggressive

Oscillation / overshoot.

## F-C02 — Gains too soft

High-level target correct but robot never reaches it precisely.

## F-C03 — Impedance stiffness mismatch

Too stiff for contact; too soft for precision.

## F-C04 — IK instability

Pseudoinverse amplifies singular directions.

## F-C05 — Joint-limit violation

Task-space target feasible locally but not under joint constraints.

## F-C06 — WBC task-priority conflict

Balance and manipulation objectives fight.

## F-C07 — Safety clipping changes learned action

Policy assumes command that runtime shield silently truncates.

## F-C08 — Controller frequency mismatch

Target changes faster than servo can track.

---

# 14. Contact / manipulation failures

## F-M01 — Premature contact

## F-M02 — Missed contact

## F-M03 — Slip

## F-M04 — Excess force

## F-M05 — Insufficient normal force

## F-M06 — Friction-cone violation

## F-M07 — Grasp not force-closed

## F-M08 — Object pose changes after grasp

## F-M09 — Insertion jamming

## F-M10 — Deformable-object state not modeled

## F-M11 — Bimanual force fighting

Both arms command inconsistent object constraints.

## F-M12 — Handover timing mismatch

Receiver closes too early/late relative to giver release.

---

# 15. Humanoid / locomotion failures

## F-H01 — Balance loss during manipulation

## F-H02 — Foot contact schedule mismatch

## F-H03 — Base-state estimator drift

## F-H04 — Manipulation target outside dynamically stable region

## F-H05 — Loco-manipulation hierarchy conflict

Locomotion and arm policy optimize inconsistent goals.

## F-H06 — Head-camera motion destabilizes perception

## F-H07 — Fall recovery absent

One failure terminates entire long-horizon episode.

## F-H08 — Human motion prior physically infeasible for robot

Retargeted pose violates torque/contact limits.

---

# 16. Memory failures

## F-MEM01 — Relevant episode not stored

## F-MEM02 — Retrieval returns semantically similar but physically wrong memory

## F-MEM03 — Memory becomes stale after world change

## F-MEM04 — Too much memory causes latency/context dilution

## F-MEM05 — No forgetting / consolidation

Memory grows without bound.

## F-MEM06 — Memory causally unused

Correct vs random retrieval gives same motor behavior.

---

# 17. World-model failures

## F-W01 — One-step accurate, rollout unstable

## F-W02 — Pixel/video realism without action sensitivity

## F-W03 — Wrong contact dynamics

## F-W04 — Counterfactual extrapolation failure

## F-W05 — Uncertainty uncalibrated

## F-W06 — Planner exploits world-model artifacts

## F-W07 — World model not used by policy

**Negative control:** random/shuffled future produces same control performance.

## F-W08 — Camera motion confused with world motion

Particularly for wrist/head cameras without extrinsics.

---

# 18. Cross-embodiment failures

## F-XE01 — Wrong morphology descriptor

## F-XE02 — Joint topology mismatch hidden by padding

## F-XE03 — Same action semantics, different dynamics

## F-XE04 — Camera-layout shortcut mistaken for embodiment representation

## F-XE05 — Adapter works only inside seen robot family

## F-XE06 — Zero-shot claim actually uses target-robot normalization/calibration

## F-XE07 — Gripper/hand topology incompatible with shared action decoder

## F-XE08 — Adaptation budget omitted

“Few-shot” cannot be compared.

---

# 19. Continual / developmental failures

## F-CL01 — Catastrophic forgetting

## F-CL02 — Replay dominates new learning

## F-CL03 — New task improves by parameter growth only

No efficiency/generalization gain.

## F-CL04 — Plasticity destabilizes safety-critical behavior

## F-CL05 — Memory growth unbounded

## F-CL06 — Forward transfer absent

System accumulates tasks but learns each from scratch.

## F-CL07 — Self-generated curriculum collapses to easy tasks

## F-CL08 — “Self-evolution” equals extra fine-tuning

No autonomous capability acquisition or structural evidence.

---

# 20. Simulation / Sim-to-Real failures

## F-SIM01 — Visual domain gap

## F-SIM02 — Friction gap

## F-SIM03 — Contact solver artifact

## F-SIM04 — Actuator model gap

## F-SIM05 — Latency omitted in simulation

## F-SIM06 — Sensor noise too clean

## F-SIM07 — Reset distribution unrealistically narrow

## F-SIM08 — Domain randomization includes target test distribution

Inflated robustness.

## F-SIM09 — Simulator-specific reward exploitation

## F-SIM10 — Asset scale/inertia error

---

# 21. Data failures

## F-D01 — Wrong action/state alignment

## F-D02 — Duplicate trajectories

## F-D03 — Success-only bias

No recovery/failure coverage.

## F-D04 — Operator-style bias

## F-D05 — Dataset mixture imbalance

Large dataset overwhelms rare embodiment/task.

## F-D06 — Train/test object leakage

## F-D07 — Scene leakage

## F-D08 — Task-template leakage

## F-D09 — Embodiment leakage

Claimed held-out robot is close variant present in training.

## F-D10 — Hidden internet-video leakage

Foundation model may have seen evaluation behavior.

---

# 22. Hardware failures

## F-HW01 — Motor saturation

## F-HW02 — Thermal throttling

## F-HW03 — Battery voltage drop changes actuator response

## F-HW04 — Gear backlash

## F-HW05 — Cable / tendon slack

## F-HW06 — Encoder packet loss

## F-HW07 — Network packet loss

## F-HW08 — Camera mount flex

Calibration changes under motion.

## F-HW09 — Gripper wear / friction change

## F-HW10 — Emergency stop / watchdog configuration error

---

# 23. Benchmark / evaluation failures

## F-B01 — Too few trials

Reported success rate has huge confidence interval.

## F-B02 — Cherry-picked videos

Demo quality is not evaluation.

## F-B03 — Failed trials silently rerun

## F-B04 — Human intervention counted inconsistently

## F-B05 — Reset protocol biased

## F-B06 — Baseline gets less data / compute

## F-B07 — Architecture gain confounded with data gain

## F-B08 — Benchmark overfitting through repeated test inspection

## F-B09 — Only average success reported

Failure type remains unknown.

## F-B10 — Latency ignored

Offline action accuracy does not imply deployable control.

---

# 24. Safety failures

## F-SAFE01 — No uncertainty-triggered stop

## F-SAFE02 — Safety monitor sees stale state

## F-SAFE03 — Human override latency too high

## F-SAFE04 — Collision shield conflicts with learned policy

## F-SAFE05 — Continual adaptation bypasses validated safety envelope

## F-SAFE06 — Unsafe language instruction reaches motor policy

## F-SAFE07 — Multi-robot safety assumes independent agents

## F-SAFE08 — Cyber/network command integrity failure

---

# 25. Root-cause debugging order

When a real robot fails, a useful order is:

```text
1. hardware health
2. timestamps / calibration / frames
3. raw sensor correctness
4. state estimator
5. action semantics / normalization
6. controller execution
7. model representation
8. planning / reasoning
9. learning/data hypothesis
```

Why start low-level?

Because a 3 cm extrinsic error can make an excellent VLA look “unintelligent”, and no amount of architecture analysis fixes the wrong transform.

---

# 26. Failure report template

```text
Episode ID:
Task:
Robot:
Checkpoint:
Controller:

Observed symptom:
First anomalous timestamp:
First irreversible timestamp:

Primary category:
Secondary category:
Evidence:

Sensor/calibration checks:
Frame checks:
Latency/action-age checks:
State-estimation checks:
Model outputs:
Controller outputs:
Safety events:

Negative control:
Reproduction rate:
Recovery attempted:

Root-cause confidence:
Fix:
Post-fix regression test:
```

---

# 27. Failure statistics

Let categories be \(c\in C\).

Failure fraction:

\[
p_c=\frac{N_c}{N_{failed}}.
\]

For method comparison, report change:

\[
\Delta p_c=p_c^{new}-p_c^{baseline}.
\]

A method that raises overall success by 5% but merely shifts failures from “grounding” to “unsafe contact” may not be an improvement.

Also track severity and recovery:

\[
Risk_c=p_c\cdot Severity_c,
\]

\[
RecoveryRate_c=\frac{N_{recovered,c}}{N_c}.
\]

---

# 28. The central research principle

A strong embodied-intelligence paper should not stop at:

> our success rate increased from 72% to 81%.

It should answer:

1. **Which failure classes decreased?**
2. **Which intermediate mechanism changed?**
3. **Which negative control breaks the gain?**
4. **Did any safety/reliability failure class increase?**
5. **Does the same causal explanation survive a new task/scene/robot?**

That turns benchmark improvement into scientific knowledge.
