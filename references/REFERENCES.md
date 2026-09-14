# References & Source Map

> **Frontier cutoff: 2026-09-14.**  
> 本参考文献表不是为了堆 citation，而是为整本书提供可追溯的知识来源。优先级：原始论文 / 官方项目页 / 官方文档 > 高质量教材与课程 > survey。动态模型页面会随版本更新，因此正文中的“截至 2026-09-14”是版本语义的一部分。

---

# 1. 数学、优化与动态系统

1. Gilbert Strang. *Introduction to Linear Algebra*.
2. Stephen Boyd, Lieven Vandenberghe. *Convex Optimization*.
3. Dimitri P. Bertsekas. *Dynamic Programming and Optimal Control*.
4. Hassan K. Khalil. *Nonlinear Systems*.
5. Eduardo D. Sontag. *Mathematical Control Theory*.
6. Steven Strogatz. *Nonlinear Dynamics and Chaos*.
7. Cédric Villani. *Optimal Transport: Old and New*.
8. Yaron Lipman et al. “Flow Matching for Generative Modeling.”
9. Ricky T. Q. Chen et al. “Neural Ordinary Differential Equations.”
10. Judea Pearl. *Causality*.
11. Jonas Peters, Dominik Janzing, Bernhard Schölkopf. *Elements of Causal Inference*.

---

# 2. 经典机器人学、几何与动力学

12. Kevin M. Lynch, Frank C. Park. *Modern Robotics: Mechanics, Planning, and Control*.  
    Official course/book: https://modernrobotics.northwestern.edu/
13. Bruno Siciliano et al. *Robotics: Modelling, Planning and Control*.
14. Mark W. Spong, Seth Hutchinson, M. Vidyasagar. *Robot Modeling and Control*.
15. John J. Craig. *Introduction to Robotics: Mechanics and Control*.
16. Roy Featherstone. *Rigid Body Dynamics Algorithms*.
17. Richard M. Murray, Zexiang Li, S. Shankar Sastry. *A Mathematical Introduction to Robotic Manipulation*.
18. Timothy D. Barfoot. *State Estimation for Robotics*.
19. Jean Gallier, Jocelyn Quaintance. materials on Lie groups / rigid transformations.
20. Oussama Khatib. “A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation.”
21. Neville Hogan. foundational impedance-control papers.
22. Antonio Bicchi. grasping / dexterous manipulation literature.

---

# 3. 控制、规划与状态估计

23. Russ Tedrake. *Underactuated Robotics*. https://underactuated.csail.mit.edu/
24. Karl J. Åström, Richard M. Murray. *Feedback Systems*.
25. Steven M. LaValle. *Planning Algorithms*. http://planning.cs.uiuc.edu/
26. Sebastian Thrun, Wolfram Burgard, Dieter Fox. *Probabilistic Robotics*.
27. Kalman, R. E. “A New Approach to Linear Filtering and Prediction Problems.”
28. Steven M. LaValle, James J. Kuffner. RRT literature.
29. Lydia E. Kavraki et al. PRM literature.
30. Nathan Ratliff et al. CHOMP.
31. Mrinal Kalakrishnan et al. STOMP.
32. John Schulman et al. TrajOpt.
33. Task and Motion Planning literature: Kaelbling & Lozano-Pérez and subsequent TAMP work.
34. Aaron Ames et al. Control Barrier Function literature.

---

# 4. 计算机视觉、3D 与机器人感知

35. Richard Szeliski. *Computer Vision: Algorithms and Applications*.
36. Richard Hartley, Andrew Zisserman. *Multiple View Geometry in Computer Vision*.
37. Alexey Dosovitskiy et al. “An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale.”
38. Alec Radford et al. “Learning Transferable Visual Models From Natural Language Supervision” (CLIP).
39. Mathilde Caron et al. DINO / DINOv2 line.
40. Meta Segment Anything / visual foundation model line.
41. Ben Mildenhall et al. “NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis.”
42. Bernhard Kerbl et al. “3D Gaussian Splatting for Real-Time Radiance Field Rendering.”
43. PointNet / PointNet++ literature.
44. Point Transformer literature.
45. Visual odometry and SLAM: ORB-SLAM / factor-graph literature.

---

# 5. 强化学习与模仿学习

46. Richard S. Sutton, Andrew G. Barto. *Reinforcement Learning: An Introduction*.
47. John Schulman et al. “Proximal Policy Optimization Algorithms.”
48. Tuomas Haarnoja et al. “Soft Actor-Critic.”
49. Stéphane Ross, Geoffrey Gordon, Drew Bagnell. “A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning” (DAgger).
50. Sergey Levine et al. end-to-end visuomotor / guided policy search literature.
51. Offline RL: CQL, IQL, AWAC and related literature.
52. Goal-conditioned RL / hindsight experience replay literature.
53. Residual RL literature.
54. Adversarial motion prior / motion imitation literature for legged and humanoid control.

---

# 6. Robot Learning、Action Chunking 与生成式策略

55. Cheng Chi et al. **Diffusion Policy: Visuomotor Policy Learning via Action Diffusion.**  
    Project: https://diffusion-policy.cs.columbia.edu/
56. Tony Z. Zhao et al. **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware** (ACT / ALOHA line).
57. ALOHA 2 and related low-cost teleoperation / bimanual data work.
58. 3D Diffusion Policy (DP3) and point-cloud-conditioned policy literature.
59. Flow-matching policy literature for continuous robot action generation.
60. Action tokenization and learned action representation literature.

---

# 7. Language / VLM 进入机器人

61. Anthony Brohan et al. **RT-1: Robotics Transformer for Real-World Control at Scale.**
62. Michael Ahn et al. **Do As I Can, Not As I Say: Grounding Language in Robotic Affordances** (SayCan).
63. Danny Driess et al. **PaLM-E: An Embodied Multimodal Language Model.**
64. Scott Reed et al. **A Generalist Agent** (Gato).
65. VLM grounding / open-vocabulary perception literature: CLIP, BLIP, LLaVA and successors.

---

# 8. RT-2、Open X-Embodiment 与第一代 VLA

66. Google DeepMind. **RT-2: New model translates vision and language into action.**  
    https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/
67. Open X-Embodiment Collaboration. **Open X-Embodiment: Robotic Learning Datasets and RT-X Models.**
68. Google DeepMind official overview: **Scaling up learning across many different robot types.**  
    https://deepmind.google/blog/scaling-up-learning-across-many-different-robot-types
69. DeepMind RoboCat work on self-improving generalist robotic agents.
70. **Octo: An Open-Source Generalist Robot Policy.**  
    https://octo-models.github.io/
71. **OpenVLA: An Open-Source Vision-Language-Action Model.**  
    https://openvla.github.io/

---

# 9. Physical Intelligence π 系列与持续经验学习

72. Physical Intelligence. Research index.  
    https://www.pi.website/
73. **π0: A Vision-Language-Action Flow Model for General Robot Control.**
74. Physical Intelligence. **FAST: Efficient Action Tokenization for Vision-Language-Action Models.**
75. Physical Intelligence. **π0.5: a VLA with Open-World Generalization.**  
    https://www.pi.website/blog/pi05
76. Physical Intelligence. **Real-Time Action Chunking with Large Models.**  
    https://www.pi.website/research/real_time_chunking
77. Physical Intelligence. **π*0.6 / Learning from Experience** (2025).  
    https://www.pi.website/blog/pistar06
78. Physical Intelligence. **Multi-Scale Embodied Memory** (2026).  
    https://www.pi.website/research/memory
79. Physical Intelligence. **Efficient / Precise Online RL for robotic manipulation** (2026 research line).  
    https://www.pi.website/research/rlt
80. **π0.7: A Steerable Generalist Robotic Foundation Model with Emergent Capabilities** (2026), arXiv:2604.15483.
81. Physical Intelligence. **Human-to-Robot Transfer** research line.  
    https://www.pi.website/research/human_to_robot

---

# 10. NVIDIA GR00T / Humanoid Foundation Models

82. NVIDIA. **GR00T N1: An Open Foundation Model for Generalist Humanoid Robots.**
83. NVIDIA Research. **GR00T N1.5** — future-latent / FLARE and post-training improvements.  
    https://research.nvidia.com/labs/gear/gr00t-n1_5/
84. NVIDIA Research. **GR00T N1.6** — expanded VLM/DiT and loco-manipulation / additional embodiment data (2025).  
    https://research.nvidia.com/labs/gear/gr00t-n1_6/
85. NVIDIA Isaac GR00T / data generation / simulation ecosystem documentation.

---

# 11. Google DeepMind Gemini Robotics

86. Google DeepMind. **Gemini Robotics brings AI into the physical world** (2025).
87. Google DeepMind. **Gemini Robotics 1.5 brings AI agents into the physical world** (2025).  
    https://deepmind.google/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/
88. Google DeepMind. **Gemini Robotics 2 brings whole body intelligence to robots** (2026-07-30).  
    https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
89. Google DeepMind. **Gemini Robotics ER 2 Model Card** (2026-07).  
    https://deepmind.google/models/model-cards/gemini-robotics-er-2/
90. Google DeepMind. **Gemini Robotics On-Device 2 Model Card** (2026-07).  
    https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/
91. Google DeepMind Evals. **ASIMOV-Agentic-v1** robotics safety benchmark (2026).  
    https://deepmind.google/research/evals/

---

# 12. Figure / Industrial Humanoid Foundation Models

92. Figure. **Helix: A Vision-Language-Action Model for Generalist Humanoid Control** (2025).  
    https://www.figure.ai/news/helix
93. Figure. Project Go-Big / human-video pretraining and human-to-robot scaling line.

---

# 13. Lightweight / Open VLA Ecosystem

94. Hugging Face. **LeRobot** documentation and open robot-learning ecosystem.  
    https://huggingface.co/docs/lerobot/
95. Hugging Face. **SmolVLA** (2025): compact VLA with flow-matching action expert and asynchronous inference.  
    https://huggingface.co/blog/smolvla
96. Open-source π-family / OpenPI codebase where applicable.
97. Open VLA / LeRobot dataset and policy training ecosystems.

---

# 14. World Models、JEPA 与 World-Action Models

98. Yann LeCun. JEPA / world-model research program.
99. Meta AI. **V-JEPA 2** project and research overview.  
    https://ai.meta.com/research/vjepa/
100. Meta AI. **V-JEPA 2 / 2.1** official code.  
     https://github.com/facebookresearch/vjepa2
101. V-JEPA 2 action-conditioned world-model work for robotic planning.
102. NVIDIA GR00T N1.5 / FLARE as future-latent auxiliary prediction in robot policy training.
103. **RoboWM-Bench: Benchmarking World Models for Robotics** (CVPR Workshops 2026), arXiv:2604.19092.
104. **OSCAR** (2026): cross-embodiment / generated-world policy evaluation, arXiv:2606.04463.
105. **Robot-Factored World Models** (2026), arXiv:2607.22535.
106. **H2R-Bench** (2026): human-to-robot world-model transfer benchmark, arXiv:2608.13049.
107. **Qwen-RobotWorld** (2026), arXiv:2606.17030.
108. Joint video-action / world-action-model literature including τ0-WM family (2026).
109. WFM-Eval / executable-future evaluation literature (2026).

---

# 15. Tactile / Dexterous Intelligence

110. Foundational GelSight / vision-based tactile sensing literature.
111. Dexterous-hand RL and in-hand manipulation literature.
112. **TouchWorld** (2026): predictive/reactive tactile world-model/foundation-policy direction, arXiv:2607.07287.
113. **T-Rex** (2026): variable-rate tactile reactive control / large tactile-data direction, arXiv:2606.17055.
114. **Vision-Based Tactile Intelligence for Robotics** survey (2026), arXiv:2608.15490.
115. Human-hand retargeting, tactile residual control and cross-sensor tactile representation literature.

---

# 16. Navigation、Household 与 Embodied Environments

116. Habitat platform / datasets / embodied navigation benchmarks.
117. Gibson / HM3D navigation data lines.
118. BEHAVIOR / BEHAVIOR-1K household activity benchmarks.
119. OmniGibson simulation environment.
120. Vision-Language Navigation foundational literature.
121. ObjectNav / ImageNav / semantic mapping literature.

---

# 17. Simulation、Robot Learning Platforms 与 Data Infrastructure

122. MuJoCo documentation. https://mujoco.org/
123. SAPIEN project and documentation.
124. ManiSkill benchmark / simulator ecosystem.
125. NVIDIA Isaac Sim documentation.
126. NVIDIA **Isaac Lab** documentation.  
     https://isaac-sim.github.io/IsaacLab/main/
127. RoboTwin platform.  
     https://github.com/RoboTwin-Platform/RoboTwin
128. ROS 2 documentation. https://docs.ros.org/
129. RLDS / TFDS robot dataset ecosystem.
130. LeRobotDataset and related scalable robot-data formats.

---

# 18. Continual、Developmental 与 Cross-Embodiment Learning

131. Angelo Cangelosi, Matthew Schlesinger. *Developmental Robotics: From Babies to Robots*.
132. Continual learning: EWC, replay, progressive networks, parameter isolation and modern continual-learning surveys.
133. Intrinsic motivation / curiosity / learning-progress literature.
134. Universal policy / morphology-conditioned control / graph policy literature.
135. Cross-embodiment transfer literature around Open X, RT-X, GR00T and modern VLA systems.
136. Human-to-robot representation/alignment literature.

---

# 19. Safety、Governance 与 Reliability

137. Robotics safety / functional safety standards relevant to the deployment domain (standards must be checked in their current official editions before real deployment).
138. Aaron Ames et al. Control Barrier Functions and safe control literature.
139. Google DeepMind. **ASIMOV-Agentic-v1** and Gemini Robotics 2 safety technical materials (2026).
140. **EmbodiedGovBench: A Benchmark for Governance, Recovery, and Upgrade Safety in Embodied Agent Systems** (2026), arXiv:2604.11174.
141. **Modular Safety Guardrails Are Necessary for Foundation-Model-Enabled Robots in the Real World** (2026), arXiv:2602.04056.
142. FMEA / fault-tree / reliability-engineering literature for safety-critical mechatronic systems.

---

# 20. 科研方法、可复现与评测科学

143. Papers With Code / benchmark reproducibility culture — used critically, not as ground truth.
144. ACM / IEEE reproducibility and artifact-review guidelines.
145. NeurIPS / ICML reproducibility checklists and statistical reporting guidance.
146. Robot-learning benchmark papers: MetaWorld, RLBench, LIBERO, ManiSkill, RoboTwin and real-robot benchmark literature.
147. Evaluation literature on calibration, risk-coverage, robustness and OOD generalization.

---

# 21. 优先阅读顺序

如果只读一条主线：

```text
Modern Robotics
  ↓
Probabilistic Robotics / State Estimation
  ↓
Underactuated Robotics / Planning Algorithms
  ↓
Sutton & Barto
  ↓
DAgger / ACT / Diffusion Policy
  ↓
RT-1 / RT-2 / Open X
  ↓
Octo / OpenVLA / π0
  ↓
π0.5 / RTC / π*0.6 / π0.7
  ↓
GR00T / Gemini Robotics / Helix
  ↓
V-JEPA 2 / world-action models / tactile foundation models
  ↓
continual / cross-embodiment / safety / developmental intelligence
```

但真正的学习顺序仍应由正文知识依赖决定，而不是论文年份。

---

# 22. 来源使用规则

1. **事实性历史结论**尽量引用原始论文或官方项目页。
2. **最新模型能力**优先用官方技术报告/model card，而不是新闻二手描述。
3. **数学与经典机器人学**优先用稳定教材。
4. **2026 前沿**标注时间，不把预印本结论写成已形成共识。
5. **公司产品/模型 claim**在正文中使用“作者/机构报告”“展示”“声称”等准确措辞，并与独立评测区分。
6. **URL 会变化**：长期版本应逐步增加 DOI / arXiv ID / BibTeX，而不只依赖网页链接。
7. **任何新模型**优先进入 Atlas 与本参考表；只有出现新的独立技术范式时才调整主目录。
