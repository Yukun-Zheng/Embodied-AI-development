# Reading Map — Part 0–50 原始教材 / 论文 / 官方来源地图

> 本文件不是“推荐论文列表”，而是每一章的**证据入口**。优先顺序：经典教材 / 原始论文 / 官方项目页 / 官方代码库；综述只用于建立全景，不替代原始来源。
>
> 阅读标记：`[F]` Foundation textbook / monograph；`[P]` Primary paper；`[O]` Official project/code/docs；`[S]` Survey / synthesis。

---

# Volume 0　导论与技术史

## Part 0　具身智能究竟是什么

- [F] Rolf Pfeifer & Josh Bongard, *How the Body Shapes the Way We Think*, 2006.
- [P] Rodney Brooks, “Intelligence without Representation,” *Artificial Intelligence*, 1991.
- [F] James J. Gibson, *The Ecological Approach to Visual Perception*, 1979 — affordance / ecological view.
- [S] Pfeifer, Lungarella & Iida, “Self-Organization, Embodiment, and Biologically Inspired Robotics,” *Science*, 2007.

## Part 1　从控制论到机器人基础模型

- [F] Norbert Wiener, *Cybernetics*, 1948.
- [P] Nilsson et al., Shakey / STRIPS lineage, 1960s–1970s.
- [P] Brooks, “A Robust Layered Control System for a Mobile Robot,” 1986.
- [P] Reed et al., “A Generalist Agent (Gato),” 2022.
- [P] Brohan et al., “RT-1,” 2022; “RT-2,” 2023.
- [P] Open X-Embodiment Collaboration, “Open X-Embodiment,” 2023/2024.

---

# Volume I　数学与计算语言

## Part 2　线性代数、微积分与数值计算

- [F] Gilbert Strang, *Introduction to Linear Algebra*.
- [F] Trefethen & Bau, *Numerical Linear Algebra*.
- [F] Steven Strogatz, *Nonlinear Dynamics and Chaos* — ODE / dynamics intuition.
- [O] MIT OpenCourseWare 18.06 Linear Algebra.

## Part 3　概率、信息与不确定性

- [F] Kevin Murphy, *Probabilistic Machine Learning*.
- [F] Cover & Thomas, *Elements of Information Theory*.
- [F] Bishop, *Pattern Recognition and Machine Learning* — classical probabilistic view.
- [P] Guo et al., “On Calibration of Modern Neural Networks,” ICML 2017.

## Part 4　优化、动态系统与最优决策

- [F] Boyd & Vandenberghe, *Convex Optimization*.
- [F] Bertsekas, *Dynamic Programming and Optimal Control*.
- [F] Kirk, *Optimal Control Theory*.
- [P] Lipman et al., “Flow Matching for Generative Modeling,” ICLR 2023.

## Part 5　几何、图与因果

- [F] Barfoot, *State Estimation for Robotics* — Lie groups for robotics.
- [P] Bronstein et al., “Geometric Deep Learning,” 2021.
- [F] Judea Pearl, *Causality*.
- [F] Peters, Janzing & Schölkopf, *Elements of Causal Inference*.

---

# Volume II　机器人身体、几何、力学与控制

## Part 6　机器人身体与机电系统

- [F] Siciliano et al., *Robotics: Modelling, Planning and Control*.
- [F] Lynch & Park, *Modern Robotics*, Ch. 1–2. https://modernrobotics.org/
- [F] Spong, Hutchinson & Vidyasagar, *Robot Modeling and Control*.
- [O] ROS / URDF, MuJoCo MJCF, OpenUSD specifications — robot description interfaces.

## Part 7　空间、旋转与刚体几何

- [F] Lynch & Park, *Modern Robotics*, Ch. 3.
- [F] Barfoot, *State Estimation for Robotics*, Lie group chapters.
- [F] Murray, Li & Sastry, *A Mathematical Introduction to Robotic Manipulation*.

## Part 8　机器人运动学

- [F] Lynch & Park, *Modern Robotics*, Ch. 4–6.
- [F] Siciliano et al., kinematics / redundancy chapters.
- [P] Whitney, “Resolved Motion Rate Control of Manipulators and Human Prostheses,” 1969 — differential IK lineage.

## Part 9　动力学、接触与抓取

- [F] Featherstone, *Rigid Body Dynamics Algorithms*.
- [F] Mason, *Mechanics of Robotic Manipulation*.
- [F] Lynch & Park, *Modern Robotics*, dynamics chapters.
- [P] Stewart & Trinkle, contact / complementarity dynamics lineage.

## Part 10　反馈、最优与 Whole-Body Control

- [F] Spong et al., *Robot Modeling and Control*.
- [P] Khatib, “A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation,” 1987.
- [F] Rawlings, Mayne & Diehl, *Model Predictive Control*.
- [P] Ames et al., Control Barrier Function literature for safety-critical control.

## Part 11　运动规划、任务规划与不确定决策

- [F] Steven LaValle, *Planning Algorithms*. https://lavalle.pl/planning/
- [P] Kavraki et al., PRM, 1996.
- [P] LaValle, RRT, 1998; Karaman & Frazzoli, RRT*, 2011.
- [S] Garrett et al., Task and Motion Planning survey / lineage.

---

# Volume III　感知、状态与世界表示

## Part 12　传感器、标定与时间

- [F] Hartley & Zisserman, *Multiple View Geometry in Computer Vision*.
- [F] Szeliski, *Computer Vision: Algorithms and Applications*.
- [O] Kalibr — camera/IMU calibration tooling and associated papers.
- [O] ROS 2 time / message-filter documentation for synchronization practice.

## Part 13　二维视觉与视觉表示

- [P] Dosovitskiy et al., “An Image is Worth 16×16 Words,” ViT, 2020/2021.
- [P] He et al., “Masked Autoencoders Are Scalable Vision Learners,” 2021/2022.
- [P] Oquab et al., DINOv2, 2023.
- [P] Radford et al., CLIP, 2021.

## Part 14　三维 / 四维世界表示

- [P] Qi et al., PointNet / PointNet++, 2017.
- [P] Curless & Levoy, TSDF volumetric integration, 1996.
- [P] Mildenhall et al., NeRF, 2020.
- [P] Kerbl et al., 3D Gaussian Splatting, 2023.
- [S] Object-centric learning / scene graph literature for relational representations.

## Part 15　状态估计、定位与 Belief

- [F] Thrun, Burgard & Fox, *Probabilistic Robotics*.
- [F] Barfoot, *State Estimation for Robotics*.
- [P] Durrant-Whyte & Bailey, SLAM tutorial series, 2006.
- [P] Mur-Artal et al., ORB-SLAM lineage.

## Part 16　触觉、力觉与 Contact Intelligence

- [P] Yuan et al., GelSight tactile sensing lineage.
- [P] Lambeta et al., DIGIT tactile sensor, 2020.
- [S] Recent visuo-tactile manipulation surveys.
- [P/O] 2025–2026 predictive/reactive tactile foundation-model work — see `REFERENCES.md` frontier section for versioned links.

## Part 17　主动感知

- [P] Ruzena Bajcsy, “Active Perception,” *Proceedings of the IEEE*, 1988.
- [F] Aloimonos et al., active vision lineage.
- [S] Next-Best-View / information-gathering robotics literature.
- [F] Information-theoretic planning connections: Cover & Thomas + POMDP literature.

---

# Volume IV　Robot Learning

## Part 18　为机器人重新学习机器学习

- [F] Goodfellow, Bengio & Courville, *Deep Learning*.
- [P] Vaswani et al., “Attention Is All You Need,” 2017.
- [P] Ho et al., DDPM, 2020.
- [P] Lipman et al., Flow Matching, 2023.

## Part 19　模仿学习

- [S] Argall et al., “A Survey of Robot Learning from Demonstration,” 2009.
- [P] Ross, Gordon & Bagnell, DAgger, 2011.
- [P] Chi et al., Diffusion Policy, 2023.
- [P] Zhao et al., ACT / ALOHA, “Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware,” RSS 2023.

## Part 20　强化学习、Offline RL 与交互学习

- [F] Sutton & Barto, *Reinforcement Learning: An Introduction*.
- [P] Schulman et al., PPO, 2017.
- [P] Haarnoja et al., SAC, 2018.
- [P] Kumar et al., CQL, 2020; Kostrikov et al., IQL, 2021/2022.
- [S] Levine et al., offline RL / robotic RL lecture material and surveys.

## Part 21　生成式动作模型与实时策略

- [P/O] Diffusion Policy: https://diffusion-policy.cs.columbia.edu/
- [P] Ze et al., 3D Diffusion Policy / DP3.
- [P] Flow-matching robot-policy lineage including π0.
- [P/O] FAST action tokenizer, Physical Intelligence.
- [O] Real-Time Action Chunking, Physical Intelligence: https://www.pi.website/research/real_time_chunking

---

# Volume V　Robot Foundation Models / VLA

## Part 22　语言、VLM 与 Physical Grounding

- [P] Radford et al., CLIP, 2021.
- [P] Li et al., BLIP / BLIP-2 lineage.
- [P] Liu et al., LLaVA lineage.
- [P] Driess et al., PaLM-E, 2023.
- [P] Ahn et al., SayCan, 2022.

## Part 23　VLA 的形成：2022–2024

- [P] Reed et al., Gato, 2022.
- [P] Brohan et al., RT-1, 2022; RT-2, 2023.
- [P] Open X-Embodiment Collaboration, RT-X / Open X-Embodiment, 2023/2024.
- [P/O] Octo, 2024. https://octo-models.github.io/
- [P/O] OpenVLA, 2024.
- [P] RoboCat, 2023 — self-improving generalist agent lineage.

## Part 24　VLA 第二阶段：2024–2026

- [O] Physical Intelligence π0 / π0.5 / π*0.6 / π0.7: https://www.pi.website/
- [O] NVIDIA GR00T N1.6: https://research.nvidia.com/labs/gear/gr00t-n1_6/
- [O] Google DeepMind Gemini Robotics 2: https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- [O] Figure Helix / Helix 02: https://www.figure.ai/
- [O] Hugging Face LeRobot / SmolVLA ecosystem.

## Part 25　VLA 内部机制

- [P/O] OpenVLA paper/code for VLM→action architecture.
- [P/O] π0 technical work for continuous action expert / flow matching.
- [P/O] RT / Octo papers for dataset mixture and action-head comparisons.
- [P/O] Helix for explicit slow/fast multi-rate architecture.

## Part 26　机器人数据、人类视频与 Cross-Embodiment Data

- [P] Open X-Embodiment, 2023/2024.
- [P] DROID, large in-the-wild manipulation dataset, 2024.
- [P/O] LeRobot datasets / RLDS ecosystem.
- [P/O] Human-video-to-robot scaling work from 2025–2026; use official model/project pages to track exact version.

---

# Volume VI　Reasoning、Memory、Experience、World Models

## Part 27　Embodied Reasoning / Agentic Robotics

- [P] SayCan, 2022 — language planning × affordance.
- [P] Inner Monologue, 2022/2023 — environment feedback in language-model planning.
- [P] VoxPoser, 2023 — language-to-3D value map / planning lineage.
- [O] Gemini Robotics Embodied Reasoning model lineage, DeepMind.

## Part 28　Embodied Memory

- [O] Physical Intelligence, “VLAs with Long and Short-Term Memory,” 2026-03-03: https://www.pi.website/research/memory
- [F] POMDP / belief-state literature for short-term hidden state.
- [S] Episodic / semantic memory literature for agents; distinguish external memory from parametric memory.

## Part 29　Learning from Experience

- [O] Physical Intelligence π*0.6: https://www.pi.website/blog/pistar06
- [O] Physical Intelligence, efficient online RL / RL-token work, 2026-03-19: https://www.pi.website/research/rlt
- [P] RoboCat, 2023 — self-improvement through new robot data.
- [F] Sutton & Barto for policy improvement / off-policy foundations.

## Part 30　World Models 与 Predictive Intelligence

- [P] Ha & Schmidhuber, “World Models,” 2018 — modern naming lineage.
- [P] Hafner et al., PlaNet / Dreamer lineage.
- [P] Hansen et al., TD-MPC / TD-MPC2 lineage.
- [P/O] Meta V-JEPA 2 / V-JEPA 2.1: https://github.com/facebookresearch/vjepa2
- [P] Action-conditioned latent/world-model robotics literature.

## Part 31　生成式世界 / 视频 / Physical Simulation Foundation Models

- [O] NVIDIA Cosmos: https://www.nvidia.com/en-us/ai/cosmos/
- [O] NVIDIA Cosmos 3: https://research.nvidia.com/labs/cosmos-lab/cosmos3/
- [O] Cosmos-Predict family and World Action Model resources.
- [S] Generative video model → robot planning / synthetic data literature, evaluated by downstream control rather than visual realism alone.

---

# Volume VII　操作、导航、灵巧与人形

## Part 32　Manipulation

- [F] Mason, *Mechanics of Robotic Manipulation*.
- [P] Dex-Net lineage for data-driven grasping.
- [P] Transporter Networks, 2020 — spatial action representation.
- [P] Diffusion Policy / ACT for modern visuomotor manipulation.

## Part 33　Bimanual / Dexterity / Tactile

- [P] ALOHA / ACT, RSS 2023.
- [P] OpenAI dexterous-hand RL lineage; Dactyl.
- [P] Shadow-hand / in-hand manipulation RL literature.
- [P] GelSight / DIGIT and 2025–2026 predictive-reactive tactile policy work.

## Part 34　Navigation / Embodied Navigation

- [O/P] Habitat / Habitat 2.0.
- [P] Anderson et al., Vision-and-Language Navigation, 2018.
- [S] ObjectNav / PointNav benchmark literature.
- [O/P] BEHAVIOR / OmniGibson for interactive household environments.

## Part 35　Humanoid / Whole-Body

- [P] Peng et al., DeepMimic, 2018.
- [P] AMP / motion-prior locomotion lineage.
- [P] Hwangbo et al., legged RL / sim-to-real lineage.
- [O] NVIDIA SONIC: https://nvlabs.github.io/GEAR-SONIC/
- [O] Gemini Robotics 2, Helix 02, GR00T N1.6 for 2026 whole-body foundation-policy frontier.

## Part 36　Human–Robot / Multi-Robot

- [F] Multi-agent systems / Dec-POMDP foundations.
- [P] Lowe et al., MADDPG, 2017 — CTDE lineage.
- [S] Shared autonomy / human-in-the-loop robotics literature.
- [O] 2026 multi-robot embodied-reasoning demonstrations from leading robotics foundation-model systems; distinguish orchestration from learned low-level coordination.

---

# Volume VIII　Cross-Embodiment 与 Developmental Intelligence

## Part 37　Cross-Embodiment

- [P] Open X-Embodiment.
- [P/O] Octo.
- [P/O] GR00T cross-embodiment work.
- [O] Gemini Robotics embodiment adaptation lineage.
- [S] Universal / morphology-conditioned policy literature.

## Part 38　Continual / Lifelong / Developmental Learning

- [S] Parisi et al., “Continual Lifelong Learning with Neural Networks,” 2019.
- [F/S] Developmental Robotics literature: Lungarella, Metta, Pfeifer, Sandini and successors.
- [P] EWC / replay / progressive-network literature for continual learning.
- [P] DIAYN and unsupervised skill-discovery lineage.

## Part 39　Self-Evolving Physical Intelligence

- [P] POET, open-ended environment/agent co-evolution lineage.
- [P] RoboCat self-improvement lineage.
- [O] π*0.6 / autonomous experience-learning work.
- [S] Open-ended learning / quality-diversity / developmental-robotics literature.
- Scientific requirement of this book: growth claims must report retention, forward transfer, autonomy and resource growth.

---

# Volume IX　Simulation、Data 与 Deployment

## Part 40　Physics Simulation / Platforms

- [O/P] MuJoCo: Todorov, Erez & Tassa, 2012; https://mujoco.org/
- [O/P] SAPIEN: https://sapien.ucsd.edu/
- [O] Isaac Sim / Isaac Lab: https://isaac-sim.github.io/IsaacLab/
- [O/P] ManiSkill.
- [O/P] Habitat, BEHAVIOR, OmniGibson, RoboTwin.

## Part 41　Synthetic Data / Sim-to-Real

- [P] Tobin et al., Domain Randomization, 2017.
- [P] Peng et al., dynamics randomization / sim-to-real locomotion lineage.
- [P] Chebotar et al., SimOpt, 2019.
- [S] System identification + domain randomization literature.

## Part 42　Robot Data Engineering

- [O/P] RLDS.
- [O/P] Open X-Embodiment dataset schema.
- [O] Hugging Face LeRobot datasets.
- [P] DROID.
- Engineering sources: HDF5 / Parquet / object-storage / streaming documentation as appropriate.

## Part 43　Systems / Real Deployment

- [O] ROS 2 documentation: https://docs.ros.org/
- [O] TF2 documentation.
- [O] EtherCAT/CAN/vendor real-time control documentation for actual hardware interfaces.
- [O] Physical Intelligence RTC and Figure Helix for modern async/multi-rate learned-policy deployment examples.

---

# Volume X　Evaluation / Reliability / Safety

## Part 44　Benchmarks / Evaluation Science

- [P/O] RLBench.
- [P/O] CALVIN.
- [P/O] LIBERO.
- [P/O] ManiSkill.
- [P/O] RoboTwin / RoboTwin 2.0.
- [F] Basic statistical inference texts for confidence intervals / significance; success videos are not denominators.

## Part 45　Reliability / Safety

- [P] Ames et al., Control Barrier Function literature.
- [S] Safe Reinforcement Learning surveys.
- [F/O] Functional-safety / industrial robot safety standards should be consulted for deployment-specific work; academic policy success is not a safety case.
- [S] Runtime assurance / shield / human-override literature.

---

# Volume XI　Research Method / Next Architecture

## Part 46　严谨研究方法

- [F] Popper, *The Logic of Scientific Discovery* — falsifiability historical foundation.
- [F] Montgomery, *Design and Analysis of Experiments* — factorial design / control variables.
- [S] Reproducibility and empirical-ML methodology literature.
- [O] Each robotics benchmark’s official evaluation protocol should be treated as part of the experiment specification.

## Part 47　Transformer 的作用与边界

- [P] Vaswani et al., Transformer, 2017.
- [P] Gu et al., S4 / state-space sequence modeling lineage.
- [P] Gu & Dao, Mamba lineage.
- [P] Battaglia et al., graph-network relational inductive biases.
- [P] Chen et al., Neural ODE, 2018.

## Part 48　数学化具身智能

- [P] Cohen & Welling, group-equivariant CNN lineage.
- [P] Thomas et al. / SE(3)-Transformer / equivariant 3D-learning lineage.
- [F/P] Koopman operator literature for nonlinear dynamics.
- [P] Raissi et al., Physics-Informed Neural Networks.
- [P] Greydanus et al., Hamiltonian Neural Networks.
- [F] Pearl / Peters et al. for causal intervention and counterfactual reasoning.

## Part 49　截至 2026-09 的开放问题

前沿事实优先查官方源并记录日期：

- Physical Intelligence: https://www.pi.website/
- Google DeepMind robotics: https://deepmind.google/
- NVIDIA Robotics / GEAR / Cosmos: https://research.nvidia.com/
- Figure: https://www.figure.ai/
- Meta V-JEPA: https://github.com/facebookresearch/vjepa2

这一 Part 的使命不是预测赢家，而是持续维护**仍未被公开证据解决的问题集合**。

## Part 50　从学习者到独立研究者

- [F/O] Lynch & Park, *Modern Robotics* + course.
- [F] Sutton & Barto, RL.
- [O] Berkeley / Stanford / CMU / MIT robotics and robot-learning public courses as supplementary learning paths.
- [O] Open-source implementations from primary papers; always read code together with paper and evaluation protocol.

---

# 使用方法

每读一个 Part，至少完成四层：

```text
1. Chapter manuscript
2. 经典/原始来源 2–4 篇
3. 对应 Lab 或最小代码实验
4. 一个能推翻当前理解的 negative control
```

不要把阅读量当进度。真正的进度是：你能否把原论文 claim 重新写成一个**明确变量、明确干预、明确失败条件**的实验。