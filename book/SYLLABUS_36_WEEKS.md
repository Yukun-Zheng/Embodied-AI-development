# 36-Week Systematic Embodied Intelligence Curriculum

> Goal: move from mathematical foundations to independent embodied-intelligence research in roughly one academic year. The schedule assumes 8–12 focused hours per week outside experiments.

This syllabus maps directly to:

- `book/chapters/Part 0–50`;
- `book/EXERCISES.md`;
- `book/SOLUTION_SKETCHES.md`;
- `book/DERIVATIONS.md`;
- `code/minimal/`;
- `labs/LABS.md`;
- `case-studies/`;
- `references/READING_MAP.md`.

The weekly unit is not “read chapters”. Each week has four outputs:

```text
understand
→ derive
→ implement
→ falsify / critique
```

---

# Phase I — Mathematical and physical language
## Weeks 1–5

## Week 1 — What embodied intelligence actually is

Read:

- Part 0;
- Part 1.

Questions:

- Why is closed-loop interaction fundamentally different from static prediction?
- What does embodiment add beyond an output interface?
- Which historical ideas returned in modern foundation robotics?

Deliverables:

- draw the complete physical closed loop from memory;
- explain partial observability without using neural-network jargon;
- write a one-page history from cybernetics to VLA without listing model names only.

Research exercise:

> choose one modern “embodied” paper and identify which parts are genuinely embodied and which are ordinary multimodal prediction.

---

## Week 2 — Linear algebra for robot state and action

Read:

- Part 2;
- Derivations D1–D3.

Master:

- SVD;
- rank/null space;
- pseudoinverse;
- Jacobian intuition;
- least squares.

Implement:

- `code/minimal/planar_arm.py`.

Pass condition:

- derive DLS inverse kinematics by hand;
- explain null-space motion physically;
- numerically verify Jacobian with finite differences.

---

## Week 3 — Probability, uncertainty and information

Read:

- Part 3;
- Part 15 sections on Bayesian state estimation;
- Derivations D10–D12.

Master:

- conditional probability;
- Bayes rule;
- Gaussian fusion;
- entropy;
- mutual information;
- epistemic vs aleatoric uncertainty.

Implement:

- `kalman_filter.py`;
- `active_perception.py`.

Research task:

> construct an example where a visually confident model is epistemically uncertain about physical state.

---

## Week 4 — Optimization, dynamics and optimal decision

Read:

- Part 4;
- Part 10 preview.

Master:

- constrained optimization;
- KKT intuition;
- dynamic programming;
- Bellman principle;
- LQR;
- flow matching as transport.

Deliverable:

- derive scalar LQR;
- explain when gradient descent, dynamic programming and MPC solve fundamentally different problems.

---

## Week 5 — Geometry, manifolds, graphs and causality

Read:

- Part 5;
- Part 7 preview.

Master:

- manifold/tangent-space intuition;
- Lie-group motivation;
- relational graphs;
- causal intervention vs correlation.

Research exercise:

> design a robot-learning experiment where an observational predictor succeeds but an intervention test fails.

---

# Phase II — Classical robotics as the physical substrate
## Weeks 6–11

## Week 6 — Robot bodies and mechatronics

Read:

- Part 6;
- `references/HARDWARE_ATLAS.md`.

Master:

- DOF;
- actuation;
- transmission;
- position/velocity/torque interfaces;
- embedded compute;
- communication buses.

Deliverable:

> pick two robot platforms and explain why the same action vector would not imply the same physical transition.

---

## Week 7 — SO(3), SE(3) and coordinate frames

Read:

- Part 7;
- `book/NOTATION_AND_CONVENTIONS.md`;
- Derivations D4–D5.

Implement:

- `se3.py`.

Pass condition:

- compose camera→base→world transforms correctly;
- convert between axis-angle and rotation matrix;
- identify at least five common convention bugs.

---

## Week 8 — Forward/inverse kinematics and Jacobians

Read:

- Part 8.

Master:

- FK;
- PoE;
- Jacobian;
- singularity;
- numerical IK;
- redundancy.

Lab:

- solve multiple reachable/unreachable planar targets;
- visualize singular values of the Jacobian.

Research task:

> explain why a learned Cartesian action head can still fail because of kinematic singularity.

---

## Week 9 — Dynamics, contact and grasping

Read:

- Part 9;
- Derivation D7.

Master:

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J^T\lambda.
\]

Understand:

- constrained dynamics;
- friction cone;
- contact solver;
- force/form closure.

Deliverable:

> draw the chain from policy action to contact wrench and explain where simulator mismatch enters.

---

## Week 10 — Feedback, impedance, optimal and whole-body control

Read:

- Part 10;
- Derivations D8–D9/D27.

Implement:

- `control.py`.

Master:

- PID;
- impedance/admittance;
- operational-space control;
- LQR/MPC;
- WBC;
- CBF.

Pass condition:

> explain why a VLA cannot simply replace a 1 kHz stabilizing controller.

---

## Week 11 — Motion planning and task planning

Read:

- Part 11.

Master:

- configuration space;
- RRT/RRT*;
- trajectory optimization;
- TAMP;
- belief-space planning.

Research exercise:

> design a hybrid system where a language planner, geometric planner and learned policy each own different decisions.

---

# Phase III — Perception, state and active sensing
## Weeks 12–16

## Week 12 — Sensors, calibration and time

Read:

- Part 12.

Master:

- camera intrinsics/extrinsics;
- IMU;
- proprioception;
- FT/tactile;
- timestamps and synchronization.

Deliverable:

> produce a timing diagram for camera/policy/controller rates and show how stale observation creates control error.

---

## Week 13 — 2D vision representations

Read:

- Part 13.

Master:

- CNN/ViT;
- detection/segmentation/tracking;
- optical flow;
- SSL;
- task-relevant features.

Research exercise:

> propose a visual feature test that is predictive of manipulation success but not image classification accuracy.

---

## Week 14 — 3D/4D world representations

Read:

- Part 14.

Master:

- point cloud;
- voxel/TSDF;
- occupancy;
- NeRF/3DGS;
- object-centric representation;
- scene graphs.

Key question:

> which representations are merely renderable, and which are useful for physical decision-making?

---

## Week 15 — State estimation and SLAM

Read:

- Part 15.

Master:

- Bayes filter;
- EKF/UKF;
- particle filter;
- visual odometry;
- SLAM;
- uncertainty calibration.

Implementation:

- modify `kalman_filter.py` to introduce wrong noise assumptions and inspect consistency.

---

## Week 16 — Tactile and active perception

Read:

- Part 16;
- Part 17.

Master:

- contact sensing;
- visuo-tactile fusion;
- information gain;
- NBV;
- active touch.

Mini-project:

> construct a partially occluded manipulation toy task where moving the camera is more useful than taking an immediate manipulation action.

---

# Phase IV — Robot learning core
## Weeks 17–21

## Week 17 — ML for robots

Read:

- Part 18.

Focus:

- supervised generalization;
- sequence models;
- Transformer;
- generative modeling;
- why robot data violate i.i.d. assumptions.

Deliverable:

> draw train/test distribution shift caused by a policy changing its own future observations.

---

## Week 18 — Imitation learning

Read:

- Part 19;
- Case Study: ACT.

Implement:

- `bc_dagger.py`.

Master:

- BC;
- covariate shift;
- DAgger;
- action chunking;
- teleoperation;
- recovery data.

Pass condition:

> explain the exact causal chain from covariate shift to compounding error.

---

## Week 19 — Reinforcement and offline/online learning

Read:

- Part 20.

Master:

- Bellman equation;
- policy gradient;
- PPO;
- SAC;
- offline RL;
- goal-conditioned/hierarchical RL;
- safe exploration.

Research task:

> identify what new information RL provides beyond imitation in a precision manipulation task.

---

## Week 20 — Generative action policies

Read:

- Part 21;
- Case Study: Diffusion Policy;
- Derivations D15–D16.

Implement:

- `generative_actions.py`.

Compare:

- MSE regression;
- autoregressive action;
- diffusion;
- flow matching.

Key question:

> when is multimodality genuinely useful, and when is it merely uncertainty caused by bad state representation?

---

## Week 21 — Real-time policy execution

Focus from Part 21:

- action chunking;
- receding horizon;
- temporal ensembling;
- RTC;
- asynchronous inference;
- latency.

Deliverable:

> build a timing model where model latency exceeds action period and compare naive chunk execution with asynchronous replanning.

---

# Phase V — Foundation policies and VLA
## Weeks 22–26

## Week 22 — Language/VLM grounding

Read:

- Part 22.

Master:

- VLM pretraining;
- grounding;
- affordance;
- open vocabulary;
- language planning;
- internet vs embodied knowledge.

Research exercise:

> create a prompt/scene pair where a VLM answer is semantically correct but physically impossible for the robot.

---

## Week 23 — VLA formation: Gato to OpenVLA

Read:

- Part 23;
- `references/TIMELINE.md`;
- `references/MODEL_ATLAS.md`.

Trace:

```text
Gato
→ SayCan
→ PaLM-E
→ RT-1/RT-2
→ RT-X/Open X
→ Octo
→ OpenVLA
```

Do not memorize model names. For each model record:

- observation;
- action;
- data;
- temporal structure;
- controller;
- generalization claim.

---

## Week 24 — VLA 2024–2026

Read:

- Part 24;
- modern VLA Case Study.

Compare mechanism axes:

- discrete vs continuous action;
- flow/DiT/action expert;
- post-training;
- embodiment conditioning;
- on-device deployment;
- whole-body action.

Deliverable:

> fill the Model Atlas table yourself for π, GR00T, Gemini Robotics and Helix.

---

## Week 25 — VLA internal mechanism

Read:

- Part 25.

Trace tensor flow:

```text
vision
language
proprioception
→ fusion/backbone
→ action expert
→ chunk
→ executor
→ controller
```

Research exercise:

> design a negative control to test whether language representation is actually used during motor execution.

---

## Week 26 — Robot data scaling and cross-embodiment

Read:

- Part 26;
- `references/DATASET_ATLAS.md`.

Study:

- dataset mixture;
- human video;
- synthetic trajectories;
- embodiment encoding;
- canonical/latent action spaces.

Deliverable:

> design a matched-data experiment separating data scaling gain from architecture gain.

---

# Phase VI — Beyond reactive VLA
## Weeks 27–30

## Week 27 — Embodied reasoning and memory

Read:

- Part 27;
- Part 28.

Master:

- hierarchical reasoning;
- replanning;
- progress monitoring;
- episodic/semantic/spatial memory;
- retrieval.

Negative-control project:

> compare correct memory, random memory, shuffled memory and no memory.

---

## Week 28 — Learning from experience

Read:

- Part 29.

Study:

- RL post-training;
- autonomous data collection;
- failure mining;
- preference signals;
- test-time adaptation;
- online system identification.

Research question:

> what must remain fixed during online adaptation to preserve safety and scientific attribution?

---

## Week 29 — World models

Read:

- Part 30;
- World Model + MPC Case Study.

Implement:

- `world_model_mpc.py`.

Evaluate:

- prediction error;
- action sensitivity;
- counterfactuals;
- planning improvement.

Pass condition:

> demonstrate that a wrong world model degrades planning; otherwise the controller may not actually use the model.

---

## Week 30 — Generative world models / neural simulators

Read:

- Part 31.

Compare:

- video generation;
- latent action models;
- neural simulators;
- physical simulators.

Core question:

> what evidence is required before a visually realistic video model can be called a useful physical world model?

---

# Phase VII — Capabilities and embodiments
## Weeks 31–33

## Week 31 — Manipulation, bimanual and dexterity

Read:

- Part 32;
- Part 33.

Study:

- contact-rich manipulation;
- articulated/deformable objects;
- bimanual constraints;
- in-hand manipulation;
- tactile feedback.

Deliverable:

> build a failure taxonomy for a bimanual handover task.

---

## Week 32 — Navigation and humanoid whole-body intelligence

Read:

- Part 34;
- Part 35.

Study:

- navigation;
- VLN;
- balance;
- locomotion RL;
- retargeting;
- whole-body VLA;
- loco-manipulation.

Research exercise:

> identify which parts of a humanoid stack must run at high frequency independently of the foundation policy.

---

## Week 33 — HRI, multi-robot and cross-embodiment

Read:

- Part 36;
- Part 37.

Study:

- shared autonomy;
- intent inference;
- coordination/task allocation;
- heterogeneous robots;
- morphology-conditioned policies.

Deliverable:

> define a cross-embodiment adaptation budget and a held-out morphology test.

---

# Phase VIII — Long-term intelligence and research independence
## Weeks 34–36

## Week 34 — Continual, developmental and self-evolving systems

Read:

- Part 38;
- Part 39.

Implement:

- `continual_metrics.py`.

Measure:

- forgetting;
- forward transfer;
- parameter growth;
- memory cost;
- adaptation efficiency.

Research rule:

> never call a system self-evolving unless the capability gain is measurable under bounded resources and previously learned capability is tracked.

---

## Week 35 — Simulation, systems, evaluation and safety

Read:

- Parts 40–45;
- `references/BENCHMARK_ATLAS.md`;
- `references/FAILURE_ATLAS.md`;
- `labs/EXPERIMENT_PROTOCOL.md`.

Study:

- simulator choice;
- sim2real;
- data engineering;
- ROS/real-time deployment;
- benchmark science;
- uncertainty/safety.

Implement:

- `evaluation_stats.py`;
- run `code/minimal/run_all.py`.

Deliverable:

> produce a complete experiment report using the unified protocol.

---

## Week 36 — Research method and next architectures

Read:

- Part 46;
- Part 47;
- Part 48;
- Part 49;
- Part 50.

Complete one final research proposal containing:

```text
Question
Hypothesis
Mechanism
System diagram
Mathematical object
Minimal experiment
Positive control
Negative control
Failure criterion
Scale-up plan
Compute/data budget
Expected contribution if hypothesis is false
```

Final oral defense:

1. explain why the problem is not already solved by scaling data;
2. identify the dominant confounder;
3. state the result that would make you abandon the idea;
4. show how the experiment separates mechanism gain from system engineering.

---

# Final capstone options

Choose one.

## Capstone A — Foundation-policy mechanism study

Examples:

- does 3D representation actually improve physical interaction?
- is language causally used during motor execution?
- does action chunking trade precision for latency robustness?

## Capstone B — Predictive intelligence

Examples:

- when does a world model improve planning?
- active perception + world model;
- tactile predictive model for contact-rich control.

## Capstone C — Developmental embodied intelligence

Examples:

- continual skill acquisition under bounded parameter growth;
- morphology transfer;
- structural plasticity with measurable retention/forward transfer.

---

# Graduation criterion

Finishing the 36 weeks does **not** mean “I have read all chapters”.

You should be able to take an unfamiliar embodied-AI paper and, within one day:

1. reconstruct the complete physical/data flow;
2. identify tensor shapes, frames and frequencies;
3. locate the true algorithmic novelty;
4. distinguish architecture/data/system gains;
5. reproduce the minimal mechanism;
6. design a negative control;
7. predict at least three failure modes;
8. decide whether the result actually advances physical intelligence.

That is the standard for completing the course.
