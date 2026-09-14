# Part-by-Part Reading Map

> **Snapshot: 2026-09-14**
>
> 标记：
>
> - **[F]** Foundation / textbook：稳定基础教材或经典资料；
> - **[P]** Paper：论文 / technical report；
> - **[O]** Official：快速变化的官方研究发布、项目页；
> - **[C]** Code：优先读源码；
> - **[S]** Survey / course：综述或课程。
>
> 原则：基础知识优先书/论文；2025–2026 快速变化的工业研究节点在稳定论文出现前，用带日期的官方来源，并与 independent reproduction 分开。

---

# Volume 0　导论与技术史

## Part 0　具身智能究竟是什么

- [F] Norbert Wiener, *Cybernetics*, 1948.
- [P] Rodney Brooks, “Intelligence without Representation,” 1991.
- [P] Ruzena Bajcsy, “Active Perception,” 1988.
- [S] Robotics / embodied intelligence historical surveys;重点比较 sense–plan–act、behavior-based、learning-based 闭环。

## Part 1　思想史与技术史

- [P] Brooks, “A Robust Layered Control System for a Mobile Robot,” 1986.
- [F] Thrun, Burgard & Fox, *Probabilistic Robotics*.
- [F] Lynch & Park, *Modern Robotics*.
- [P] Reed et al., Gato; Ahn et al., SayCan; RT / Open X / Octo / OpenVLA / π lineage.
- [O] `references/TIMELINE.md` 作为本书内部统一历史索引。

---

# Volume I　数学与计算语言

## Part 2　线性代数、微积分与数值计算

- [F] Gilbert Strang, *Linear Algebra and Learning from Data* / MIT 18.06.
- [F] Trefethen & Bau, *Numerical Linear Algebra*.
- [F] Lynch & Park, *Modern Robotics*, Jacobian / pseudoinverse sections.

## Part 3　概率、信息与不确定性

- [F] Murphy, *Probabilistic Machine Learning*.
- [F] Cover & Thomas, *Elements of Information Theory*.
- [F] Thrun et al., *Probabilistic Robotics*.

## Part 4　优化、动态系统与最优决策

- [F] Boyd & Vandenberghe, *Convex Optimization*.
- [F] Bertsekas, dynamic programming / optimal control texts.
- [F] Tedrake, *Underactuated Robotics* notes.
- [P] Lipman et al. / flow-matching literature for continuous transport objectives.

## Part 5　几何、图与因果

- [F] Barfoot, *State Estimation for Robotics* — Lie-group/state-estimation view.
- [F] Lynch & Park — SO(3), SE(3), twists.
- [F] Pearl, *Causality*; Peters et al., *Elements of Causal Inference*.

---

# Volume II　机器人身体、几何、力学与控制

## Part 6　机器人身体与机电系统

- [F] Craig, *Introduction to Robotics*.
- [F] Lynch & Park, mechanics/control chapters.
- [O] 具体 robot SDK / hardware manuals；结合 `references/HARDWARE_ATLAS.md`。

## Part 7　空间、旋转与刚体几何

- [F] Lynch & Park, Chapters 3–4.
- [F] Barfoot, Lie groups for robotics.
- [O] `book/NOTATION_AND_CONVENTIONS.md` 作为全书工程 convention。

## Part 8　机器人运动学

- [F] Lynch & Park, kinematics/Jacobian/IK.
- [F] Siciliano et al., *Robotics: Modelling, Planning and Control*.
- [C] `code/minimal/planar_arm.py` 与 `se3.py`。

## Part 9　动力学、接触与抓取

- [F] Featherstone, *Rigid Body Dynamics Algorithms*.
- [F] Mason, *Mechanics of Robotic Manipulation*.
- [F] Murray, Li & Sastry, *A Mathematical Introduction to Robotic Manipulation*.

## Part 10　反馈、最优与 Whole-Body Control

- [P] Khatib, Operational Space Formulation, 1987.
- [F] Tedrake, *Underactuated Robotics*.
- [F] Slotine & Li, nonlinear/control foundations.
- [P] Control Barrier Function literature for safety filters.
- [C] `code/minimal/control.py`.

## Part 11　运动规划与任务规划

- [F] LaValle, *Planning Algorithms*.
- [P] Kavraki et al., PRM; LaValle, RRT.
- [S] TAMP surveys; Garrett et al. task-and-motion-planning lineage.

---

# Volume III　感知、状态与世界表示

## Part 12　传感器、标定与时间

- [F] Szeliski, *Computer Vision: Algorithms and Applications*.
- [F] Hartley & Zisserman, *Multiple View Geometry*.
- [O] Camera / IMU / FT / tactile sensor calibration manuals.

## Part 13　二维视觉与表示

- [P] ViT, CLIP, DINO / DINOv2, MAE and modern self-supervised visual representation literature.
- [P] Ego-centric video representation literature.
- [S] Evaluate representation by downstream physical tasks, not classification alone.

## Part 14　三维/四维世界表示

- [F] Multiple-view geometry references.
- [P] NeRF; 3D Gaussian Splatting.
- [P] point-cloud / occupancy / object-centric representation literature.
- [P] robotics 3D policy lineage including DP3-style work.

## Part 15　状态估计与定位

- [F] Barfoot, *State Estimation for Robotics*.
- [F] Thrun et al., *Probabilistic Robotics*.
- [P] ORB-SLAM / factor-graph / VIO literature.
- [C] `code/minimal/kalman_filter.py`.

## Part 16　触觉与接触智能

- [P] GelSight / DIGIT tactile sensing lineage.
- [P] visuo-tactile representation and dexterous-control work.
- [P/O] 2025–2026 predictive/reactive tactile foundation-policy work;按明确 release 日期追踪。

## Part 17　主动感知

- [P] Bajcsy, Active Perception, 1988.
- [F] information theory / POMDP foundations.
- [P] next-best-view / active SLAM / active touch literature.
- [C] `code/minimal/active_perception.py`.

---

# Volume IV　Robot Learning

## Part 18　为机器人重新学习机器学习

- [F] Goodfellow et al., *Deep Learning*.
- [F] Sutton & Barto for sequential decision-making.
- [P] Transformer, ViT, diffusion, flow-matching foundational papers.
- [S] sequence/model-based robot-learning courses.

## Part 19　模仿学习

- [S] Argall et al., Robot Learning from Demonstration survey.
- [P] Ross, Gordon & Bagnell, DAgger, 2011.
- [P] Zhao et al., ACT/ALOHA, RSS 2023.
- [C] https://github.com/tonyzhaozh/act
- [C] `case-studies/ACT_SOURCE_WALKTHROUGH.md`.

## Part 20　强化学习、Offline RL 与交互学习

- [F] Sutton & Barto.
- [P] PPO; SAC.
- [P] CQL / IQL and offline-RL lineage.
- [P] model-based RL / TD-MPC2 lineage.

## Part 21　生成式动作模型与实时策略

- [P/C] Diffusion Policy: https://github.com/real-stanford/diffusion_policy
- [P] 3D Diffusion Policy / DP3 lineage.
- [P/O] π0 / flow-matching robot-policy lineage.
- [P/O] FAST action tokenizer.
- [O] Physical Intelligence, Real-Time Action Chunking.
- [C] LeRobot RTC / async inference implementation; see `references/SOURCE_CODE_ATLAS.md`.

---

# Volume V　Robot Foundation Models / VLA

## Part 22　语言、VLM 与 Physical Grounding

- [P] CLIP.
- [P] BLIP / BLIP-2 lineage.
- [P] LLaVA lineage.
- [P] PaLM-E.
- [P] SayCan.

## Part 23　VLA 的形成：2022–2024

- [P] Gato.
- [P] RT-1 / RT-2.
- [P] Open X-Embodiment / RT-X.
- [P/O] Octo: https://octo-models.github.io/
- [P/C] OpenVLA: https://github.com/openvla/openvla
- [P] RoboCat.

## Part 24　VLA 第二阶段：2024–2026

- [O] Physical Intelligence π0 / π0.5 / π*0.6 / π0.7: https://www.pi.website/
- [O] Physical Intelligence RTC: https://www.pi.website/research/real_time_chunking
- [O] NVIDIA GR00T N1.6 research page: https://research.nvidia.com/labs/gear/gr00t-n1_6/
- [O/C] **NVIDIA GR00T N1.7**: https://github.com/NVIDIA/Isaac-GR00T/releases/tag/n1.7-release
- [C] NVIDIA Isaac-GR00T: https://github.com/NVIDIA/Isaac-GR00T
- [O] Google DeepMind Gemini Robotics 2 official release.
- [O] Figure Helix / Helix 02.
- [C] Hugging Face LeRobot / SmolVLA: https://github.com/huggingface/lerobot
- [C] `references/SOURCE_CODE_ATLAS.md` for verified train/model/deployment paths.

> 日期勘误：官方 GitHub `n1.6-release` = 2026-04-15；`n1.7-release` = 2026-04-18。

## Part 25　VLA 内部机制

- [C] OpenVLA `vla-scripts/` + `prismatic/`.
- [C] LeRobot policy / processor / async stack.
- [C] GR00T N1.7 model / processor / embodiment tags / tests.
- [P/O] π0-family continuous-action-expert technical work.
- [O] Helix multi-rate architecture releases.

## Part 26　机器人数据、人类视频与 Cross-Embodiment

- [P] Open X-Embodiment.
- [P] DROID.
- [C/O] LeRobotDataset / RLDS ecosystem.
- [O/P] human-video-to-robot transfer work, 2025–2026.
- [O] `references/DATASET_ATLAS.md` for dataset contract and leakage taxonomy.

---

# Volume VI　Reasoning、Memory、Experience、World Models

## Part 27　Embodied Reasoning / Agentic Robotics

- [P] SayCan.
- [P] Inner Monologue.
- [P] VoxPoser.
- [O] Gemini Robotics embodied-reasoning lineage.

## Part 28　Embodied Memory

- [O] Physical Intelligence, long/short-term VLA memory, 2026.
- [F] POMDP / belief-state literature.
- [S] episodic / semantic / spatial memory literature for agents.

## Part 29　Learning from Experience

- [O] π*0.6.
- [O] Physical Intelligence efficient online RL / RL-token work, 2026.
- [P] RoboCat self-improvement lineage.
- [F] Sutton & Barto.

## Part 30　World Models 与 Predictive Intelligence

- [P] Ha & Schmidhuber, “World Models”.
- [P] PlaNet / Dreamer lineage.
- [P] TD-MPC / TD-MPC2 lineage.
- [P/C] Meta V-JEPA 2 / 2.1: https://github.com/facebookresearch/vjepa2
- [C] Key code paths in `references/SOURCE_CODE_ATLAS.md`.

## Part 31　生成式世界 / World Foundation Models

- [O] NVIDIA Cosmos.
- [O] Cosmos 3 official research release.
- [P/O] world-action / action-conditioned generative-model literature.
- [S] Evaluate by downstream planning/control, not video realism alone.

---

# Volume VII　操作、导航、灵巧与人形

## Part 32　Manipulation

- [F] Mason, *Mechanics of Robotic Manipulation*.
- [P] Dex-Net lineage.
- [P] Transporter Networks.
- [P] ACT / Diffusion Policy for modern visuomotor manipulation.

## Part 33　Bimanual / Dexterity / Tactile

- [P] ALOHA / ACT.
- [P] Dactyl / dexterous-hand RL lineage.
- [P] visuo-tactile / predictive-reactive tactile-control literature.

## Part 34　Navigation / Embodied Navigation

- [O/P] Habitat / Habitat 2.0.
- [P] Vision-and-Language Navigation lineage.
- [S] ObjectNav / PointNav literature.
- [O/P] BEHAVIOR / OmniGibson.

## Part 35　Humanoid / Whole-Body

- [P] DeepMimic.
- [P] AMP / motion-prior lineage.
- [P] legged-RL sim-to-real literature.
- [O] NVIDIA SONIC.
- [O/C] GR00T N1.7 for open modern humanoid-foundation stack.
- [O] Gemini Robotics 2; Helix 02.

## Part 36　Human–Robot / Multi-Robot

- [F/S] shared autonomy / HRI references.
- [F/S] multi-agent planning / CTDE literature.
- [O] 2026 multi-robot foundation-policy demonstrations should be read with explicit communication/control assumptions.

---

# Volume VIII　Cross-Embodiment、Continual、Developmental

## Part 37　Cross-Embodiment Intelligence

- [P] Open X-Embodiment / RT-X.
- [P/O] Octo / GR00T / modern embodiment-conditioned policy work.
- [C] `gr00t/data/embodiment_tags.py` as a concrete modern interface.
- [O] `references/HARDWARE_ATLAS.md` for morphology/action-topology comparison.

## Part 38　Continual / Lifelong / Developmental Learning

- [S] continual-learning surveys.
- [P] catastrophic-forgetting / replay / parameter-isolation lineage.
- [S] developmental robotics and intrinsic-motivation literature.
- [C] `code/minimal/continual_metrics.py`.

## Part 39　Self-Evolving Physical Intelligence

- [F] continual-learning foundations.
- [S] open-ended learning / developmental robotics literature.
- [O] current claims should be evaluated by retention, forward transfer, resource growth and safety—not metaphor.

---

# Volume IX　Simulation、Data、Deployment

## Part 40　Physics Simulation 与 Platforms

- [O] MuJoCo documentation.
- [O] SAPIEN / ManiSkill.
- [O] NVIDIA Isaac Sim / Isaac Lab.
- [O] RLBench / RoboTwin / Habitat / OmniGibson.
- [O] `references/BENCHMARK_ATLAS.md`.

## Part 41　Synthetic Data 与 Sim-to-Real

- [P] domain randomization lineage.
- [P] system identification / dynamics randomization literature.
- [O] modern synthetic-data / world-foundation-model systems.

## Part 42　Robot Data Engineering

- [C/O] LeRobotDataset.
- [P/O] RLDS / Open X data standardization.
- [O] `references/DATASET_ATLAS.md`.

## Part 43　机器人系统工程与部署

- [O] ROS 2 / TF / real-time documentation.
- [C] LeRobot `robots/`, `motors/`, `cameras/`, `async_inference/`.
- [C] GR00T `getting_started/real_world_deployment.md` and deployment scripts.
- [O] TensorRT / model-compilation docs for on-device deployment.

---

# Volume X　Evaluation、Reliability、Safety

## Part 44　Benchmarks 与 Evaluation Science

- [F] statistical inference / binomial confidence intervals.
- [O] CALVIN / LIBERO / ManiSkill / RLBench / RoboTwin protocols.
- [O] `references/BENCHMARK_ATLAS.md`.
- [C] `code/minimal/evaluation_stats.py`.

## Part 45　Reliability / Safety / Intervention

- [P] Control Barrier Function literature.
- [S] safe RL / runtime assurance literature.
- [O] human-intervention and physical-safety practices from real robot systems.
- [O] `references/FAILURE_ATLAS.md`.

---

# Volume XI　Research Method、Theory、Next Architecture

## Part 46　严谨的具身智能研究

- [F] scientific experimental-design / statistics references.
- [O] `labs/EXPERIMENT_PROTOCOL.md`.
- [O] `references/FAILURE_ATLAS.md`.
- [C] use source-level walkthroughs instead of architecture diagrams alone.

## Part 47　Transformer 的作用与边界

- [P] Transformer foundation paper.
- [P/S] state-space / recurrent / graph / continuous-time alternatives.
- [P] object-centric / equivariant / geometry-aware models.

## Part 48　数学化具身智能

- [P] Koopman/operator-learning lineage.
- [P] differentiable physics / neural ODE / physics-informed learning.
- [F] symmetry / equivariance / causal modeling foundations.

## Part 49　开放前沿

- Read by **problem axis**, not by model leaderboard:
  - open-world generalization;
  - whole-body;
  - memory;
  - experience learning;
  - world models;
  - cross-embodiment;
  - continual/developmental learning;
  - safety.
- [O] `references/MODEL_ATLAS.md`, `TIMELINE.md`, `SOURCE_CODE_ATLAS.md`.

## Part 50　从学习者到独立研究者

- [O] `book/SYLLABUS_36_WEEKS.md`.
- [O] `labs/EXPERIMENT_PROTOCOL.md`.
- [O] `book/EXERCISES.md` / `SOLUTION_SKETCHES.md`.
- [O] `case-studies/` and `references/SOURCE_CODE_ATLAS.md`.

---

# Reading rule

对每个现代模型至少同时读四层：

```text
paper / official technical description
+ code
+ data / benchmark protocol
+ deployment / controller interface
```

如果只有 demo，没有可审计的 action/data/system contract，就把结论限制在 demo 能支持的范围内。
