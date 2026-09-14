# Complete Table of Contents

# 《具身智能：从物理世界到通用机器人》
## Embodied Intelligence: From Physical Principles to General-Purpose Robots

> **Curriculum baseline: v1.0 — knowledge frontier frozen at 2026-09-14.**
>
> 本目录不是“热门论文列表”，而是一张从第一性原理通往当前具身智能前沿的**知识依赖图**。主线遵循：
>
> **物理世界 → 身体 → 感知 → 状态 → 决策 → 控制 → 学习 → 基础模型 → 预测与推理 → 泛化 → 经验学习 → 持续发展。**
>
> 模型会过时，知识结构不能随热点漂移。RT、Octo、OpenVLA、π、GR00T、Gemini Robotics、Helix、V-JEPA 等模型作为“历史节点与案例”进入统一框架，而不是反过来用模型名字组织整本书。

---

# Volume 0　导论：智能为什么必须进入物理世界

# Part 0　具身智能究竟是什么

## 0.1 为什么智能进入物理世界后，一切都变了
## 0.2 Agent、Body、Environment：具身系统的三个基本对象
## 0.3 从函数映射到闭环交互
## 0.4 开环、闭环与反馈
## 0.5 部分可观测性：机器人永远看不见完整世界
## 0.6 时间、延迟、控制频率与异步系统
## 0.7 Embodiment：身体不是输出接口，而是智能的一部分
## 0.8 Morphology、Sensorimotor Loop 与 Morphological Computation
## 0.9 Affordance：世界不是物体集合，而是行动可能性
## 0.10 Intelligence、Autonomy、Agency 与 Generality
## 0.11 “Physical Intelligence”与传统 AI 的差异
## 0.12 什么叫 General-Purpose Robot
## 0.13 Embodied AI、Robotics、Robot Learning、Physical AI 的边界
## 0.14 本书的问题意识：为什么“能生成动作”不等于“理解物理世界”
## 0.15 如何使用本书：本科生、工程师与研究者的不同路线

# Part 1　思想史与技术史：从控制论到机器人基础模型

## 1.1 Cybernetics：反馈思想的起点
## 1.2 Classical AI 与 Symbolic Robotics
## 1.3 Shakey、Sense–Plan–Act 与早期移动机器人
## 1.4 Brooks 与 Subsumption Architecture
## 1.5 Situated Intelligence 与 Behavior-Based Robotics
## 1.6 Gibson、Ecological Psychology 与 Affordance
## 1.7 SLAM、Motion Planning 与 Classical Robotics 的成熟
## 1.8 Deep Learning 如何进入 perception
## 1.9 Deep RL 如何进入 control
## 1.10 Imitation Learning 与大规模 demonstration
## 1.11 Sim-to-Real 与并行仿真
## 1.12 Transformer 如何进入机器人
## 1.13 从 Gato / SayCan / PaLM-E 到 RT-1 / RT-2
## 1.14 Open X-Embodiment：机器人数据开始规模化
## 1.15 Diffusion Policy、ACT、Octo 与 OpenVLA
## 1.16 π、GR00T、Gemini Robotics、Helix 与新一代 foundation policy
## 1.17 World Model、JEPA 与 predictive intelligence 的回归
## 1.18 Humanoid、whole-body intelligence 与“通用身体”假说
## 1.19 2026：VLA 之后正在形成哪些新问题
## 1.20 历史给我们的教训：哪些“突破”后来被证明只是工程尺度变化

---

# Volume I　数学与计算语言

# Part 2　线性代数、微积分与数值计算

## 2.1 标量、向量、矩阵与张量
## 2.2 线性映射、基、坐标与 change of basis
## 2.3 Inner Product、Norm 与距离
## 2.4 Rank、Null Space、Range 与机器人冗余
## 2.5 Eigenvalue / Eigenvector 与稳定性直觉
## 2.6 SVD、Pseudoinverse 与 Least Squares
## 2.7 PCA 与低维结构
## 2.8 单变量与多变量微积分
## 2.9 Gradient、Jacobian、Hessian
## 2.10 Chain Rule 与计算图
## 2.11 Automatic Differentiation
## 2.12 Taylor Expansion 与局部线性化
## 2.13 ODE：连续时间动力系统
## 2.14 Difference Equation：离散时间系统
## 2.15 Euler / Runge–Kutta 与数值积分
## 2.16 数值误差、刚性系统与稳定积分

# Part 3　概率、统计、信息与不确定性

## 3.1 Random Variable 与 Probability Distribution
## 3.2 Joint / Marginal / Conditional Distribution
## 3.3 Bayes Rule
## 3.4 Expectation、Variance、Covariance
## 3.5 Gaussian Distribution
## 3.6 Maximum Likelihood / MAP
## 3.7 Bayesian Inference
## 3.8 Stochastic Process
## 3.9 Markov Property
## 3.10 Entropy、Cross Entropy、KL Divergence
## 3.11 Mutual Information
## 3.12 Epistemic 与 Aleatoric Uncertainty
## 3.13 Calibration
## 3.14 Monte Carlo Sampling
## 3.15 Importance Sampling
## 3.16 Probabilistic Graphical Models
## 3.17 Information Gain 与 Value of Information

# Part 4　优化、动态系统与最优决策

## 4.1 Optimization 的基本形式
## 4.2 Unconstrained / Constrained Optimization
## 4.3 Lagrange Multiplier
## 4.4 KKT Conditions
## 4.5 Convexity 与凸优化的边界
## 4.6 Gradient Descent、Momentum、Adam
## 4.7 Second-Order Optimization
## 4.8 Dynamic Systems 与 State Space
## 4.9 Equilibrium 与 Stability
## 4.10 Lyapunov Stability
## 4.11 Calculus of Variations
## 4.12 Optimal Control 的数学形式
## 4.13 Dynamic Programming
## 4.14 Bellman Principle
## 4.15 Pontryagin Minimum Principle
## 4.16 Optimal Transport：从 distribution 到 flow
## 4.17 Continuous Normalizing Flow 与 Flow Matching 的数学基础

# Part 5　几何、流形、图与因果

## 5.1 Euclidean Space 与非欧空间
## 5.2 Manifold、Tangent Space 与 Local Coordinates
## 5.3 Lie Group / Lie Algebra 的直觉
## 5.4 Graph、Tree 与 Factor Graph
## 5.5 Graph Laplacian 与关系结构
## 5.6 Message Passing 与 Graph Neural Network
## 5.7 Causal Graph 与 Intervention
## 5.8 Correlation、Prediction 与 Causation
## 5.9 Structural Causal Model
## 5.10 Counterfactual
## 5.11 Causality 在机器人交互中的机会与陷阱

---

# Volume II　机器人身体、几何、力学与控制

# Part 6　机器人身体与机电系统

## 6.1 Degree of Freedom
## 6.2 Rigid Body、Link、Joint 与 Kinematic Chain
## 6.3 Revolute、Prismatic、Spherical 与复合关节
## 6.4 Serial / Parallel / Closed-Chain Mechanism
## 6.5 Motor、Servo 与 Actuator
## 6.6 Gearbox、Harmonic Drive、Cycloidal Drive
## 6.7 Quasi-Direct Drive 与 Torque Density
## 6.8 Tendon / Cable / Underactuated Mechanism
## 6.9 Encoder、Current、Torque Sensing
## 6.10 Position / Velocity / Torque Interface
## 6.11 Stiffness、Compliance 与 Backdrivability
## 6.12 Power、Battery、Thermal 与续航
## 6.13 Embedded Compute、MCU、GPU 与 Robot Computer
## 6.14 EtherCAT、CAN、Serial 与实时通信
## 6.15 单臂、双臂、移动底盘、四足、人形与灵巧手
## 6.16 URDF、MJCF、USD 与 robot description
## 6.17 Hardware–Software Interface：学习算法最终控制的究竟是什么

# Part 7　空间、旋转与刚体几何

## 7.1 Coordinate Frame
## 7.2 2D Rotation
## 7.3 3D Rotation Matrix
## 7.4 SO(3)
## 7.5 Euler Angle 与 Gimbal Lock
## 7.6 Axis–Angle
## 7.7 Quaternion
## 7.8 Homogeneous Transformation
## 7.9 SE(3)
## 7.10 Transform Composition / Inverse
## 7.11 so(3)、se(3) 与 Hat / Vee Operator
## 7.12 Exponential / Logarithm Map
## 7.13 Twist 与 Screw Motion
## 7.14 Adjoint
## 7.15 Spatial Velocity / Body Velocity
## 7.16 Wrench 与力矩变换
## 7.17 Rotation Convention、左手右手系与工程灾难

# Part 8　机器人运动学

## 8.1 Forward Kinematics
## 8.2 Product of Exponentials
## 8.3 Denavit–Hartenberg：历史方法与现代位置
## 8.4 Manipulator Jacobian
## 8.5 Jacobian 的几何意义
## 8.6 Velocity Kinematics
## 8.7 Singularities
## 8.8 Inverse Kinematics
## 8.9 Analytical IK / Numerical IK
## 8.10 Pseudoinverse 与 Damped Least Squares
## 8.11 Redundancy 与 Null Space
## 8.12 Differential IK
## 8.13 Joint Limit 与 Constraint-Aware IK
## 8.14 Trajectory Interpolation
## 8.15 Joint-Space / Cartesian-Space Trajectory
## 8.16 双臂 Relative Kinematics
## 8.17 Multi-Chain / Whole-Body Kinematics

# Part 9　动力学、接触与抓取

## 9.1 Newton–Euler Mechanics
## 9.2 Lagrangian Mechanics
## 9.3 Manipulator Equation
## 9.4 Mass Matrix
## 9.5 Coriolis / Centrifugal Terms
## 9.6 Gravity
## 9.7 Forward / Inverse Dynamics
## 9.8 Constrained Dynamics
## 9.9 Contact Geometry
## 9.10 Normal Force、Friction 与 Friction Cone
## 9.11 Coulomb Friction
## 9.12 Complementarity
## 9.13 Rigid / Soft Contact
## 9.14 Contact Solver 的数值本质
## 9.15 Grasp Map 与 Force Closure
## 9.16 Form Closure
## 9.17 Center of Mass
## 9.18 ZMP、Capture Point 与 Centroidal Dynamics
## 9.19 Deformable / Articulated Object Dynamics
## 9.20 为什么 simulation physics 永远只是近似

# Part 10　反馈控制、最优控制与 Whole-Body Control

## 10.1 Control 到底控制什么
## 10.2 Open-Loop / Closed-Loop
## 10.3 PID
## 10.4 Feedforward + Feedback
## 10.5 Joint Position / Velocity / Torque Control
## 10.6 Computed Torque Control
## 10.7 Impedance Control
## 10.8 Admittance Control
## 10.9 Operational Space Control
## 10.10 Force Control
## 10.11 Hybrid Position / Force Control
## 10.12 LQR
## 10.13 iLQR / DDP
## 10.14 Model Predictive Control
## 10.15 Constrained MPC
## 10.16 Whole-Body Control
## 10.17 Hierarchical QP
## 10.18 Safety Filter / Control Barrier Function
## 10.19 Learned Policy 与低层 Controller 的职责边界
## 10.20 高频反射回路与低频智能回路

# Part 11　运动规划、任务规划与不确定决策

## 11.1 Configuration Space
## 11.2 Collision Detection
## 11.3 Graph Search：BFS / Dijkstra / A*
## 11.4 PRM / RRT / RRT*
## 11.5 Kinodynamic Planning
## 11.6 Trajectory Optimization
## 11.7 CHOMP / STOMP / TrajOpt 类方法
## 11.8 Optimization-Based Motion Planning
## 11.9 Task and Motion Planning
## 11.10 Symbolic / Geometric Planning 的接口
## 11.11 Hierarchical Planning
## 11.12 Planning under Uncertainty
## 11.13 Belief-Space Planning
## 11.14 Receding-Horizon Planning
## 11.15 Classical Planner 与 Learned Policy 如何组合

---

# Volume III　感知、状态与世界表示

# Part 12　机器人传感器、标定与时间

## 12.1 Physical Signal → Sensor → Observation
## 12.2 RGB Camera
## 12.3 Camera Intrinsics
## 12.4 Camera Extrinsics
## 12.5 Projection / Back-Projection
## 12.6 Stereo Camera
## 12.7 Structured-Light / ToF Depth
## 12.8 LiDAR
## 12.9 IMU
## 12.10 Encoder 与 Proprioception
## 12.11 Force/Torque Sensor
## 12.12 Tactile Sensor
## 12.13 Audio / Microphone
## 12.14 Event Camera
## 12.15 Calibration
## 12.16 Timestamp、Clock、Latency 与 Synchronization
## 12.17 Multi-Rate Sensor Fusion 的工程现实

# Part 13　二维视觉与视觉表示学习

## 13.1 Pixel 并不是世界状态
## 13.2 CNN
## 13.3 Vision Transformer
## 13.4 Detection
## 13.5 Semantic / Instance / Panoptic Segmentation
## 13.6 Tracking
## 13.7 Optical Flow
## 13.8 Keypoint / Correspondence
## 13.9 Self-Supervised Visual Learning
## 13.10 Contrastive Learning
## 13.11 Masked Image / Video Modeling
## 13.12 Foundation Vision Encoder
## 13.13 Egocentric Video Representation
## 13.14 Video Representation 与 Temporal Feature
## 13.15 Task-Relevant Representation
## 13.16 视觉特征是否真的服务物理交互

# Part 14　三维、四维与对象级世界表示

## 14.1 Depth 与 3D Geometry
## 14.2 Point Cloud
## 14.3 Voxel / Occupancy
## 14.4 TSDF
## 14.5 Mesh
## 14.6 NeRF
## 14.7 3D Gaussian Splatting
## 14.8 Dynamic NeRF / Dynamic Gaussian
## 14.9 4D Scene Representation
## 14.10 Object-Centric Representation
## 14.11 Scene Graph
## 14.12 Part / Articulation Representation
## 14.13 3D Foundation Representation
## 14.14 Geometry-Aware Policy Representation
## 14.15 2D feature、3D geometry 与 action 的真正关系

# Part 15　状态估计、定位与 Belief

## 15.1 Observation ≠ State
## 15.2 Hidden State 与 Belief State
## 15.3 Bayes Filter
## 15.4 Kalman Filter
## 15.5 EKF / UKF
## 15.6 Particle Filter
## 15.7 Sensor Fusion
## 15.8 Visual Odometry
## 15.9 Inertial Odometry
## 15.10 SLAM
## 15.11 Factor-Graph SLAM
## 15.12 Object Pose Estimation
## 15.13 Category-Level Pose
## 15.14 Dynamic Scene State Estimation
## 15.15 Contact State Estimation
## 15.16 Learned State Estimator
## 15.17 Uncertainty Estimation 与 Calibration
## 15.18 POMDP

# Part 16　多模态感知、触觉与主动信息获取

## 16.1 Vision + Proprioception
## 16.2 Vision + Force
## 16.3 Vision + Touch
## 16.4 Vision + Language + Audio
## 16.5 Multimodal Fusion：Early / Late / Cross-Attention
## 16.6 Contact、Slip、Force 与 Hidden Physical State
## 16.7 Tactile Image / Tactile Token / Tactile Embedding
## 16.8 Visuo-Tactile Representation Learning
## 16.9 Observability
## 16.10 Passive Perception 的极限
## 16.11 Active Vision
## 16.12 Next-Best-View
## 16.13 Occlusion Reasoning
## 16.14 Viewpoint Planning
## 16.15 Active Touch
## 16.16 Information Gain 与 Action Cost
## 16.17 Task-Driven Active Perception
## 16.18 Embodiment-Agnostic View Goal
## 16.19 Perception–Action Coupling

---

# Volume IV　机器人学习的基础范式

# Part 17　为机器人重新学习机器学习

## 17.1 Supervised Learning
## 17.2 Generalization
## 17.3 Bias–Variance
## 17.4 Distribution Shift
## 17.5 Representation Learning
## 17.6 Sequence Modeling
## 17.7 RNN / LSTM / State-Space Model
## 17.8 Attention
## 17.9 Transformer
## 17.10 Multimodal Transformer
## 17.11 Self-Supervised Learning
## 17.12 VAE
## 17.13 Autoregressive Modeling
## 17.14 Diffusion Model
## 17.15 Score Matching
## 17.16 Flow Matching
## 17.17 Energy-Based Model
## 17.18 Mixture Model 与 Multimodality
## 17.19 为什么机器人学习不是普通 i.i.d. learning

# Part 18　机器人数据、Observation 与 Action Representation

## 18.1 Episode、Trajectory、Transition
## 18.2 Observation Space
## 18.3 State Space
## 18.4 Action Space
## 18.5 Absolute / Delta Action
## 18.6 Joint / Cartesian Action
## 18.7 Position / Velocity / Torque Command
## 18.8 End-Effector Pose Representation
## 18.9 Rotation Representation 对学习的影响
## 18.10 Gripper / Dexterous-Hand Action
## 18.11 Whole-Body Action
## 18.12 Normalization 与 Robot-Specific Statistics
## 18.13 Action Horizon / Chunk
## 18.14 Control Frequency 与 Data Frequency
## 18.15 Missing Data / Async Data
## 18.16 Language Annotation / Subtask Annotation
## 18.17 Dataset Schema：RLDS、LeRobot 类格式与自定义 HDF5
## 18.18 数据质量、覆盖度与偏差
## 18.19 Robot Data 不只是“更多 episode”

# Part 19　示范学习、模仿学习与 Offline Robot Learning

## 19.1 Demonstration 是什么
## 19.2 Kinesthetic Teaching
## 19.3 Leader–Follower Teleoperation
## 19.4 VR / Motion Capture / Hand Tracking Teleoperation
## 19.5 Human Video Demonstration
## 19.6 Behavior Cloning
## 19.7 Covariate Shift
## 19.8 DAgger
## 19.9 Intervention Learning
## 19.10 Inverse Reinforcement Learning
## 19.11 Goal-Conditioned Imitation
## 19.12 Multi-Task Imitation
## 19.13 Action Chunking
## 19.14 ACT
## 19.15 Latent Action Representation
## 19.16 Offline Demonstration Learning
## 19.17 Failure / Recovery Demonstration
## 19.18 Human-to-Robot Retargeting
## 19.19 Learning from Play
## 19.20 Demonstration 的信息瓶颈

# Part 20　强化学习、Offline RL 与交互学习

## 20.1 MDP
## 20.2 Return / Value / Q Function
## 20.3 Bellman Equation
## 20.4 Q-Learning
## 20.5 Policy Gradient
## 20.6 Actor–Critic
## 20.7 PPO
## 20.8 SAC
## 20.9 Model-Based RL
## 20.10 Offline RL
## 20.11 Goal-Conditioned RL
## 20.12 Hierarchical RL
## 20.13 Reward Design
## 20.14 Sparse Reward
## 20.15 Exploration
## 20.16 Curriculum Learning
## 20.17 Residual RL
## 20.18 RL for Manipulation
## 20.19 RL for Locomotion
## 20.20 Online RL on Real Robots
## 20.21 Safe Exploration
## 20.22 从高 reward 到真实可靠能力之间的鸿沟

# Part 21　生成式动作模型与实时策略

## 21.1 为什么动作需要 distribution
## 21.2 Multimodal Action Distribution
## 21.3 Autoregressive Action
## 21.4 Action Discretization
## 21.5 Action Tokenization
## 21.6 Diffusion Policy
## 21.7 3D Diffusion Policy
## 21.8 Flow-Matching Policy
## 21.9 Continuous Action Expert
## 21.10 Hybrid Discrete–Continuous Action Modeling
## 21.11 Action Chunking
## 21.12 Chunk Boundary Problem
## 21.13 Receding-Horizon Execution
## 21.14 Temporal Ensembling
## 21.15 Real-Time Chunking
## 21.16 Asynchronous Inference
## 21.17 Inference Latency 与 Dynamics Mismatch
## 21.18 Control Frequency、Action Rate 与 Model Rate
## 21.19 Diffusion / Flow / AR 的统一比较
## 21.20 Policy 输出动作后，真正的机器人系统还发生了什么

---

# Volume V　机器人基础模型：从 VLM 到 VLA

# Part 22　语言、多模态基础模型与 Physical Grounding

## 22.1 Language 为什么能帮助机器人
## 22.2 Tokenization
## 22.3 Vision–Language Pretraining
## 22.4 CLIP
## 22.5 BLIP / LLaVA 类多模态模型
## 22.6 Open-Vocabulary Perception
## 22.7 Grounding
## 22.8 Referring Expression
## 22.9 Affordance Grounding
## 22.10 Spatial Reasoning
## 22.11 Temporal Reasoning
## 22.12 Physical Reasoning
## 22.13 Language-Conditioned Planning
## 22.14 Internet Knowledge 与 Embodied Knowledge
## 22.15 VLM 知道什么、不知道什么
## 22.16 从 VLM 到 Robotics Foundation Model

# Part 23　VLA 的形成：2022–2024 的关键谱系

## 23.1 什么才算 Vision-Language-Action Model
## 23.2 Gato：generalist sequence model 的早期尝试
## 23.3 SayCan：语言模型 × affordance
## 23.4 PaLM-E：embodied multimodal language model
## 23.5 RT-1：大规模多任务 robot transformer
## 23.6 RT-2：web knowledge 到 action
## 23.7 RT-X / Open X-Embodiment：跨机器人规模化
## 23.8 RoboCat 与 self-improving generalist policy
## 23.9 Octo：开放 generalist policy
## 23.10 OpenVLA：开放 VLA 基线
## 23.11 2024 年 VLA 的统一架构模式
## 23.12 为什么“VLM + Action Head”成为主流

# Part 24　VLA 的第二阶段：2024–2026 的架构分化

## 24.1 π0：VLM + Flow-Matching Action Expert
## 24.2 FAST 与高效 Action Tokenization
## 24.3 π0.5：Open-World Generalization
## 24.4 π*0.6：从 experience / RL 改善 generalist policy
## 24.5 π0.7：Steerability 与 emergent capability
## 24.6 GR00T N1：Humanoid Foundation Model
## 24.7 GR00T N1.5：Cross-Embodiment 与 post-training
## 24.8 GR00T N1.6：VLM、DiT 与 loco-manipulation 的继续扩展
## 24.9 Gemini Robotics：VLA 与 embodied reasoning 的分层
## 24.10 Gemini Robotics 1.5：motion transfer 与 embodiment adaptation
## 24.11 Gemini Robotics 2：whole-body VLA
## 24.12 Gemini Robotics On-Device 2：端侧 VLA 与快速 embodiment adaptation
## 24.13 Helix：on-board generalist humanoid VLA
## 24.14 开源 VLA 生态：OpenVLA / SmolVLA / LeRobot 系路线
## 24.15 3D-aware / point-cloud-aware VLA 路线
## 24.16 Bimanual / Dexterous / Humanoid VLA 路线
## 24.17 中国具身基础模型生态与开放模型
## 24.18 2026 年 VLA 的共同结构与真正分歧

# Part 25　VLA 的内部机制：它到底学到了什么

## 25.1 Vision Encoder
## 25.2 Language Backbone
## 25.3 Proprioception Encoding
## 25.4 Action Expert / Action Head
## 25.5 Cross-Attention 与 Multimodal Fusion
## 25.6 State Tokenization
## 25.7 Continuous / Discrete Action Output
## 25.8 Co-Training 与 Joint Training
## 25.9 Knowledge Insulation / Gradient Interference
## 25.10 Post-Training
## 25.11 Dataset Mixture
## 25.12 Robot-Specific Adapter
## 25.13 Embodiment Conditioning
## 25.14 Low-Level Controller 去哪里了
## 25.15 Latency、Chunking 与闭环频率
## 25.16 Language Following 与 Motor Precision 的张力
## 25.17 Scaling Law 在机器人上是否成立
## 25.18 VLA 的 failure taxonomy
## 25.19 VLA 是否真的学到了物理规律

# Part 26　机器人数据规模化、人类视频与 Cross-Embodiment

## 26.1 为什么 Robot Data 是真正的瓶颈
## 26.2 Open X-Embodiment
## 26.3 DROID / Bridge / Large-Scale Real Robot Data
## 26.4 Multi-Robot Dataset Mixture
## 26.5 Dataset Weighting 与 Sampling
## 26.6 Data Curation
## 26.7 Success / Failure Data
## 26.8 Internet Image / Video Co-Training
## 26.9 Human Video Pretraining
## 26.10 Human-to-Robot Transfer
## 26.11 Retargeted Human Motion
## 26.12 Synthetic Trajectory
## 26.13 Neural-Generated Robot Data
## 26.14 Cross-Embodiment Representation
## 26.15 Morphology Encoding
## 26.16 Universal / Canonical Action Space
## 26.17 Motion Transfer
## 26.18 Few-Shot Embodiment Adaptation
## 26.19 数据规模、模型规模与能力涌现
## 26.20 什么数据真正提高 physical generalization

---

# Volume VI　VLA 之后：推理、记忆、经验学习与世界模型

# Part 27　Embodied Reasoning、Agentic Robotics 与长时程任务

## 27.1 Reactive Policy 的极限
## 27.2 Goal Representation
## 27.3 Skill / Primitive / Option
## 27.4 Task Decomposition
## 27.5 Hierarchical Policy
## 27.6 Language Planner + Motor Policy
## 27.7 Embodied Reasoning Model
## 27.8 Spatial / Temporal / Physical Reasoning
## 27.9 Tool Use 与 API / Skill Calling
## 27.10 Long-Horizon Planning
## 27.11 Online Replanning
## 27.12 Progress Monitoring
## 27.13 Error Detection
## 27.14 Recovery
## 27.15 Human Clarification / Intervention
## 27.16 Steerability：人在执行中如何改变机器人
## 27.17 “Chain-of-Thought”是否真的导致更好的 motor behavior
## 27.18 Agentic orchestration 与 end-to-end policy 的边界

# Part 28　机器人记忆：从 context window 到 lifelong memory

## 28.1 为什么无记忆 VLA 很难做长任务
## 28.2 Short-Term Sensorimotor Memory
## 28.3 Working Memory
## 28.4 Episodic Memory
## 28.5 Semantic Memory
## 28.6 Spatial Memory
## 28.7 External Memory
## 28.8 Retrieval-Augmented Robot Policy
## 28.9 Multi-Scale Embodied Memory
## 28.10 Long / Short-Term Memory 协同
## 28.11 Memory Compression
## 28.12 Forgetting
## 28.13 Memory 与 World Model 的区别
## 28.14 Memory 对 10+ minute task 的意义

# Part 29　从 Demonstration 到 Experience：机器人如何继续学习

## 29.1 Pretraining、Post-Training 与 Deployment Learning
## 29.2 为什么 imitation 不能解决所有 precision 问题
## 29.3 Reinforcement Learning Post-Training
## 29.4 RL Token / Lightweight Online Adaptation
## 29.5 Experience Replay
## 29.6 Autonomous Data Collection
## 29.7 Self-Generated Curriculum
## 29.8 Failure Mining
## 29.9 Human Feedback
## 29.10 Preference / Ranking Signal
## 29.11 Self-Evaluation
## 29.12 Self-Correction
## 29.13 Test-Time Adaptation
## 29.14 Online System Identification
## 29.15 Policy Improvement in Deployment
## 29.16 Safety-Constrained Online Learning
## 29.17 从“训练好的模型”走向“会积累经验的机器人”

# Part 30　World Models 与 Predictive Intelligence

## 30.1 World Model 到底是什么
## 30.2 State-Space Dynamics Model
## 30.3 Latent Dynamics
## 30.4 Object-Centric Dynamics
## 30.5 Video Prediction
## 30.6 Action-Conditioned Video Prediction
## 30.7 Pixel-Space vs Latent-Space Prediction
## 30.8 JEPA 与 representation-space prediction
## 30.9 V-JEPA 2：understanding、prediction 与 planning
## 30.10 V-JEPA 2.1：dense / temporally consistent representation
## 30.11 Latent Action-Conditioned World Model
## 30.12 3D / 4D World Model
## 30.13 Contact-Aware World Model
## 30.14 Tactile World Model
## 30.15 Counterfactual Prediction
## 30.16 Uncertainty-Aware Prediction
## 30.17 Learned Simulator / Neural Simulator
## 30.18 Foundation World Model
## 30.19 World Model + MPC
## 30.20 World Model + Policy Search
## 30.21 World Model + Evaluator
## 30.22 “生成未来视频”与“理解物理规律”的差别
## 30.23 如何证明 world model 真正提高了行动能力

# Part 31　生成式世界、视频模型与 Physical Simulation Foundation Models

## 31.1 Video Generation 为什么进入 robotics
## 31.2 Internet Video 里的物理先验
## 31.3 Actionable Video Representation
## 31.4 Image-to-Video / Text-to-Video 与 robot data augmentation
## 31.5 Video-to-Action 与 Inverse Dynamics
## 31.6 Latent Action Model
## 31.7 Generative World Simulator
## 31.8 Cosmos 类 Physical AI World Foundation Model
## 31.9 Synthetic Scene / Synthetic Trajectory Generation
## 31.10 Video Model 与 Physics Engine 的互补
## 31.11 Neural Simulator 的可靠性边界
## 31.12 从“看起来真实”到“控制上有用”的评价标准

---

# Volume VII　操作、导航、灵巧与人形

# Part 32　机器人操作：从抓取到长时程任务

## 32.1 Manipulation 的本质
## 32.2 Reach / Push / Pull
## 32.3 Pick and Place
## 32.4 Grasp Planning
## 32.5 Grasping in Clutter
## 32.6 Contact-Rich Manipulation
## 32.7 Insertion / Assembly
## 32.8 Tool Use
## 32.9 Articulated Object Manipulation
## 32.10 Deformable Object
## 32.11 Cloth
## 32.12 Rope / Cable
## 32.13 Food / Fluid / Granular Object
## 32.14 Mobile Manipulation
## 32.15 Long-Horizon Manipulation
## 32.16 Open-World Household Manipulation
## 32.17 Industrial Manipulation
## 32.18 Real-World Manipulation Failure Taxonomy

# Part 33　双臂、灵巧手与触觉智能

## 33.1 为什么双臂不是两个单臂
## 33.2 Relative Pose / Coordinated Frame
## 33.3 Bimanual Constraint
## 33.4 Symmetric / Asymmetric Coordination
## 33.5 Leader–Follower Coordination
## 33.6 Handover
## 33.7 Cooperative Manipulation
## 33.8 Collision / Deadlock / Safety
## 33.9 Dexterous Hand Kinematics
## 33.10 Grasp Synergy
## 33.11 In-Hand Manipulation
## 33.12 Whole-Hand Contact
## 33.13 Visuo-Tactile Dexterity
## 33.14 Tactile Pretraining
## 33.15 Predictive + Reactive Tactile Control
## 33.16 High-Frequency Tactile Residual Policy
## 33.17 Tactile Foundation Model
## 33.18 Bimanual / Dexterous VLA
## 33.19 灵巧操作离人类水平还差什么

# Part 34　移动机器人、导航与 Embodied Navigation

## 34.1 Differential / Omnidirectional Mobile Base
## 34.2 Localization
## 34.3 Mapping
## 34.4 Global / Local Navigation
## 34.5 Obstacle Avoidance
## 34.6 Exploration
## 34.7 Active Mapping
## 34.8 Visual Navigation
## 34.9 ObjectNav / PointNav
## 34.10 Vision-Language Navigation
## 34.11 Embodied Question Answering
## 34.12 Semantic Navigation
## 34.13 Navigation + Manipulation
## 34.14 Home / Office / Warehouse Navigation
## 34.15 Habitat / BEHAVIOR / OmniGibson 类环境
## 34.16 Drone / Field Robot / Autonomous Vehicle：同一 embodied framework 的外延

# Part 35　Legged Locomotion、Humanoid 与 Whole-Body Intelligence

## 35.1 Legged Robot State / Action
## 35.2 Gait
## 35.3 Balance
## 35.4 ZMP / Capture Point
## 35.5 Centroidal Dynamics
## 35.6 Quadruped Locomotion
## 35.7 Biped Locomotion
## 35.8 Locomotion RL
## 35.9 Motion Imitation
## 35.10 Motion Retargeting
## 35.11 Human Motion Prior
## 35.12 Humanoid Teleoperation
## 35.13 Whole-Body Motion Tracking
## 35.14 SONIC 类大规模 humanoid motion tracking
## 35.15 Whole-Body Control
## 35.16 Loco-Manipulation
## 35.17 Humanoid Manipulation
## 35.18 Whole-Body VLA
## 35.19 Fall Detection / Fall Recovery
## 35.20 Energy、Speed 与 Reliability
## 35.21 从 tabletop manipulation 到 feet-to-fingertips control
## 35.22 General-Purpose Humanoid 的现实瓶颈

# Part 36　Human–Robot Interaction 与 Multi-Robot Intelligence

## 36.1 Human-in-the-Loop Robotics
## 36.2 Shared Autonomy
## 36.3 Natural-Language Instruction
## 36.4 Interactive Correction
## 36.5 Intent Inference
## 36.6 Human Proximity 与 Social Safety
## 36.7 Multi-Robot Communication
## 36.8 Coordination
## 36.9 Task Allocation
## 36.10 Centralized / Decentralized Planning
## 36.11 CTDE
## 36.12 Shared World State / Shared Memory
## 36.13 Heterogeneous Robot Collaboration
## 36.14 Embodiment-Aware Role Assignment
## 36.15 Foundation Model for Multi-Robot Coordination
## 36.16 Agentic Multi-Robot Collaboration

---

# Volume VIII　持续学习、跨本体与发展型智能

# Part 37　Cross-Embodiment Intelligence

## 37.1 Embodiment 到底包含什么
## 37.2 Morphology
## 37.3 Sensor Configuration
## 37.4 Action Topology
## 37.5 Embodiment Descriptor / Token
## 37.6 Morphology-Conditioned Policy
## 37.7 Robot-Agnostic Representation
## 37.8 Universal Action Representation
## 37.9 Skill Space / Latent Action Space
## 37.10 Cross-Robot Transfer
## 37.11 Zero / Few-Shot Embodiment Transfer
## 37.12 Motion Transfer
## 37.13 新身体的 calibration / adaptation
## 37.14 “一个 checkpoint 控不同机器人”意味着什么
## 37.15 Cross-Embodiment 的真正上限

# Part 38　Continual、Lifelong 与 Developmental Robot Learning

## 38.1 Continual Learning
## 38.2 Catastrophic Forgetting
## 38.3 Replay
## 38.4 Regularization
## 38.5 Parameter Isolation
## 38.6 Modular Network
## 38.7 Dynamic Architecture
## 38.8 Online Adaptation
## 38.9 Lifelong Robot Learning
## 38.10 Developmental Robotics
## 38.11 Intrinsic Motivation
## 38.12 Curiosity
## 38.13 Self-Supervised Skill Discovery
## 38.14 Open-Ended Learning
## 38.15 Memory Formation / Consolidation / Forgetting
## 38.16 Structural Plasticity
## 38.17 Network Growth / Pruning 的局限
## 38.18 不区分“训练/推理”的持续交互系统
## 38.19 从 fixed model 到 developing agent

# Part 39　Self-Evolving Physical Intelligence

## 39.1 “自进化”必须满足什么可证伪条件
## 39.2 Capability Acquisition
## 39.3 Autonomous Practice
## 39.4 Self-Generated Goals
## 39.5 Curriculum Emergence
## 39.6 Failure-Driven Learning
## 39.7 Mechanism Discovery
## 39.8 Compositional Skill Growth
## 39.9 Memory–Structure Co-Adaptation
## 39.10 Policy–World-Model Co-Evolution
## 39.11 Structure Search vs Structural Plasticity
## 39.12 Self-Modification 的稳定性问题
## 39.13 Continual Safety Constraint
## 39.14 如何区分真正能力生长与数据记忆

---

# Volume IX　仿真、数据基础设施与系统工程

# Part 40　Physics Simulation 与 Robot Learning Platform

## 40.1 为什么机器人研究离不开 simulation
## 40.2 Physics Engine 的数值基础
## 40.3 MuJoCo
## 40.4 SAPIEN
## 40.5 Isaac Sim
## 40.6 Isaac Lab
## 40.7 ManiSkill
## 40.8 robosuite / MetaWorld
## 40.9 RLBench
## 40.10 RoboTwin / RoboTwin 2.0
## 40.11 Habitat
## 40.12 BEHAVIOR / OmniGibson
## 40.13 Humanoid / Whole-Body Simulation
## 40.14 Asset、Material 与 Scene
## 40.15 USD / MJCF / URDF Import Pipeline
## 40.16 Parallel Simulation
## 40.17 GPU-Accelerated Simulation
## 40.18 Determinism 与 Simulator Versioning
## 40.19 Benchmark Platform 与真实研究问题的错位

# Part 41　Synthetic Data、Domain Randomization 与 Sim-to-Real

## 41.1 Synthetic RGB / Depth / Segmentation
## 41.2 Synthetic Trajectory
## 41.3 Procedural Scene Generation
## 41.4 Domain Randomization
## 41.5 Dynamics Randomization
## 41.6 Visual Randomization
## 41.7 System Identification
## 41.8 Sim-to-Real
## 41.9 Real-to-Sim
## 41.10 Real-to-Sim-to-Real
## 41.11 Digital Twin
## 41.12 Neural Asset / Generative Scene
## 41.13 Reality Gap 的分解
## 41.14 哪些能力可以在 simulation 学，哪些不能

# Part 42　机器人数据工程

## 42.1 Data Collection System
## 42.2 Teleoperation Hardware
## 42.3 Episode Lifecycle
## 42.4 Timestamp 与 Synchronization
## 42.5 RGB / Depth / Point Cloud / State Alignment
## 42.6 Compression / Storage / Streaming
## 42.7 HDF5 / Parquet / RLDS / LeRobot Formats
## 42.8 Metadata
## 42.9 Annotation
## 42.10 Quality Control
## 42.11 Duplicate / Leakage Detection
## 42.12 Failure Data
## 42.13 Dataset Versioning
## 42.14 Dataset Mixture
## 42.15 Data Loader for Massive Robot Corpora
## 42.16 Distributed Storage
## 42.17 Data Governance / Privacy
## 42.18 Robotics Data Flywheel

# Part 43　机器人系统工程与真实部署

## 43.1 从 Python Policy 到 Robot System
## 43.2 ROS 2
## 43.3 Topic / Service / Action
## 43.4 TF / Transform Tree
## 43.5 Node Architecture
## 43.6 Real-Time Control
## 43.7 Multi-Rate Architecture
## 43.8 Camera / Sensor Streaming
## 43.9 Robot Driver
## 43.10 Motion Planner Service
## 43.11 Policy Server
## 43.12 GPU Inference Pipeline
## 43.13 Edge / On-Device Inference
## 43.14 Quantization / Compilation / TensorRT 类优化
## 43.15 Network Latency
## 43.16 Async Pipeline
## 43.17 Safety Monitor
## 43.18 Logging / Replay
## 43.19 Experiment Reproducibility
## 43.20 Distributed Training
## 43.21 Model Serving for Robots
## 43.22 一次真实机器人 rollout 到底发生了什么

---

# Volume X　评测、可靠性与安全

# Part 44　Datasets、Benchmarks 与 Evaluation Science

## 44.1 Benchmark 为什么会塑造研究方向
## 44.2 Training Dataset vs Evaluation Benchmark
## 44.3 MetaWorld / robosuite / RLBench
## 44.4 CALVIN
## 44.5 LIBERO
## 44.6 ManiSkill
## 44.7 RoboTwin 2.0
## 44.8 Navigation / Habitat Benchmarks
## 44.9 Humanoid Benchmarks
## 44.10 Real-World Evaluation
## 44.11 Task Success Rate
## 44.12 Partial Credit / Progress Metric
## 44.13 Robustness
## 44.14 Generalization Matrix
## 44.15 Object / Scene / Task / Embodiment OOD
## 44.16 Perturbation Test
## 44.17 Long-Horizon Evaluation
## 44.18 Intervention Rate
## 44.19 Recovery Rate
## 44.20 Latency / Throughput / Energy
## 44.21 Calibration / Uncertainty
## 44.22 Benchmark Leakage
## 44.23 Statistical Significance / Confidence Interval
## 44.24 “成功视频”为什么不是科学证据

# Part 45　可靠性、Safety 与 Human Intervention

## 45.1 Physical Safety
## 45.2 Functional Safety
## 45.3 Collision / Joint / Force Limit
## 45.4 Safe Controller
## 45.5 Control Barrier Function
## 45.6 Runtime Monitor
## 45.7 Uncertainty-Aware Stop
## 45.8 Human Override
## 45.9 Safe Exploration
## 45.10 Unsafe Instruction Refusal
## 45.11 Task Feasibility Estimation
## 45.12 Human-Proximity Safety
## 45.13 Agentic Safety Orchestration
## 45.14 Multi-Robot Safety
## 45.15 Cybersecurity for Robots
## 45.16 Foundation Model Safety for Physical Systems
## 45.17 可靠性工程：从 70% success 到可部署系统
## 45.18 Safety 与 Capability 为什么不能分开研究

---

# Volume XI　研究方法、理论前沿与下一代具身智能

# Part 46　如何做严谨的具身智能研究

## 46.1 怎样读一篇具身论文
## 46.2 怎样画出完整 system diagram
## 46.3 怎样追踪 observation → representation → action
## 46.4 怎样复现论文而不只是跑通代码
## 46.5 怎样设计 Baseline
## 46.6 怎样设计 Ablation
## 46.7 怎样构造 Negative Control
## 46.8 怎样控制 Data Gain
## 46.9 怎样区分 Architecture Gain 与 Data Gain
## 46.10 怎样构造可证伪 hypothesis
## 46.11 怎样建立 Failure Taxonomy
## 46.12 怎样做 Mechanism Analysis
## 46.13 怎样检查统计可信度
## 46.14 怎样防 benchmark overfitting
## 46.15 怎样报告真实 robot experiment
## 46.16 怎样从 failure mode 产生研究问题
## 46.17 怎样判断一个 VLA 是否真的 generalize
## 46.18 怎样判断一个 World Model 是否真的被 policy 利用
## 46.19 怎样判断视觉表征是否服务物理交互
## 46.20 怎样判断“reasoning”是否只是语言包装

# Part 47　Transformer 在具身智能中的作用与边界

## 47.1 Transformer 真正解决了什么
## 47.2 Attention 的优势与代价
## 47.3 Sequence Model 是否等于 Dynamics Model
## 47.4 Tokenization 对物理连续性的破坏
## 47.5 Fixed Context 与 Persistent World
## 47.6 Reactive Transformer 与 closed-loop control
## 47.7 Transformer + External Controller
## 47.8 Transformer + Memory
## 47.9 Transformer + World Model
## 47.10 Transformer + Structural Module
## 47.11 State-Space Model / Recurrent Model 的重新崛起
## 47.12 Graph / Object-Centric / Geometry-Centric Architecture
## 47.13 Continuous-Time Architecture
## 47.14 Modular / Hierarchical Architecture
## 47.15 Transformer 之后真正值得问的问题

# Part 48　数学化具身智能：从相关性到结构与规律

## 48.1 Physical Invariance
## 48.2 Equivariance
## 48.3 Symmetry
## 48.4 Conservation Law
## 48.5 Constraint
## 48.6 Geometry-Aware Learning
## 48.7 Koopman Operator
## 48.8 System Identification
## 48.9 Causal Representation
## 48.10 Object / Relation / Mechanism Decomposition
## 48.11 Compositionality
## 48.12 Mechanism Learning
## 48.13 Hybrid Symbolic–Continuous System
## 48.14 Differentiable Physics
## 48.15 Neural ODE / Continuous Dynamics
## 48.16 Physics-Informed / Physics-Constrained Learning
## 48.17 从“拟合动作”到“学习规律”

# Part 49　开放问题：截至 2026-09 的真正前沿

## 49.1 Robust Open-World Generalization
## 49.2 Long-Horizon Autonomy
## 49.3 Reliable Dexterity
## 49.4 Contact-Rich Intelligence
## 49.5 Real-Time Foundation Policy
## 49.6 Embodied Memory
## 49.7 Learning from Experience
## 49.8 Cross-Embodiment Transfer
## 49.9 Whole-Body Intelligence
## 49.10 World Model that Actually Helps Control
## 49.11 Active Perception
## 49.12 Data Efficiency
## 49.13 Autonomous Data Flywheel
## 49.14 Continual / Developmental Learning
## 49.15 Structural Plasticity
## 49.16 Self-Evolving Architecture
## 49.17 Causal Physical Reasoning
## 49.18 Multi-Robot Intelligence
## 49.19 Safety under Continual Adaptation
## 49.20 Sim-to-Real at Foundation-Model Scale
## 49.21 Hardware–Intelligence Co-Design
## 49.22 General-Purpose Humanoid 是否是终局形态
## 49.23 Embodied Intelligence 是否需要新的计算范式
## 49.24 什么才算“理解了物理世界”
## 49.25 具身智能距离真正通用智能还有什么

# Part 50　从学习者到独立研究者

## 50.1 第一阶段：建立数学与经典机器人学底座
## 50.2 第二阶段：亲手实现 perception / planning / control
## 50.3 第三阶段：掌握 imitation / RL / generative policy
## 50.4 第四阶段：复现主流 VLA
## 50.5 第五阶段：拆解 foundation policy 的失败机制
## 50.6 第六阶段：进入 world model / reasoning / humanoid / touch 等前沿
## 50.7 第七阶段：提出自己的 Architecture Research Program
## 50.8 从“追论文”转向“追问题”
## 50.9 如何形成持续科研飞轮
## 50.10 如何提出一个值得做三年的具身智能问题

---

# Appendices　附录系统

## Appendix A　全书数学符号表
## Appendix B　机器人坐标系与 Rotation Convention 速查
## Appendix C　SO(3) / SE(3) 公式与代码
## Appendix D　机器人运动学 / 动力学公式表
## Appendix E　Control / Planning 算法速查
## Appendix F　PyTorch / JAX 最小实现
## Appendix G　ROS 2 / TF / Real-Time System 速查
## Appendix H　MuJoCo / SAPIEN / Isaac Sim / Isaac Lab 环境指南
## Appendix I　Robot Dataset Schema 与 Action Convention
## Appendix J　Teleoperation 与数据采集 Checklist
## Appendix K　Sim-to-Real Checklist
## Appendix L　真实机器人实验 Safety Checklist
## Appendix M　Benchmark 与 Evaluation Checklist
## Appendix N　Reproducibility Checklist
## Appendix O　经典教材与公开课程地图
## Appendix P　1950–2026 具身智能技术时间线
## Appendix Q　2016–2026 Robot Learning 关键论文谱系
## Appendix R　2022–2026 Robotics Foundation Model / VLA Atlas
## Appendix S　2024–2026 World Model / Video Model / JEPA Atlas
## Appendix T　2024–2026 Humanoid / Whole-Body Learning Atlas
## Appendix U　2024–2026 Dexterity / Tactile Learning Atlas
## Appendix V　Datasets / Benchmarks / Simulators Atlas
## Appendix W　Open-Source Codebase 与复现索引
## Appendix X　Research Question Bank
## Appendix Y　Failure Mode Taxonomy
## Appendix Z　术语中英对照表

---

# 截至 2026-09-14 的前沿覆盖检查

本目录在冻结前必须覆盖以下已经形成独立方法论的问题，而不是只覆盖模型名字：

- VLA 与 robotics foundation policy；
- continuous action expert、diffusion、flow matching、autoregressive action 与 action tokenization；
- action chunking、real-time chunking、asynchronous inference 与 latency；
- open-world generalization、steerability 与 cross-embodiment transfer；
- human video / internet video → robot transfer；
- embodied reasoning、long-horizon planning 与 agentic orchestration；
- short-term / long-term embodied memory；
- RL post-training、online experience learning 与 autonomous improvement；
- latent / video / JEPA / action-conditioned world models；
- V-JEPA 2 / 2.1 类 predictive representation；
- whole-body VLA、humanoid locomotion + manipulation 与 motion tracking；
- tactile pretraining、visuo-tactile policy 与 predictive/reactive touch；
- multi-robot collaboration；
- on-device robotics foundation model；
- synthetic data、world foundation model、neural simulator 与 sim-to-real；
- continual learning、developmental robotics 与 self-evolving physical intelligence；
- safety、uncertainty、human intervention 与可靠部署。

---

# 目录冻结与维护规则

**v1.0 之后，正文写作必须服从本目录，而不是边写边随意改变知识结构。**

新增一个 Part 级主题必须至少满足一项：

1. 出现了现有知识树无法容纳的新问题；
2. 出现了具有独立数学对象、训练范式或系统接口的新技术范式；
3. 该方向已持续形成一组相互关联的工作，而非单篇热点论文；
4. 新方向改变了“感知—状态—预测—决策—控制—学习”闭环中的基本接口。

单个新模型原则上只进入对应 Part 的案例、论文谱系或 Atlas，不因为品牌或热度单独增加 Part。

每次前沿更新都记录明确时间截面，例如 `2026-09-14 frontier snapshot`，避免把不同时间版本的技术状态混在一起。
