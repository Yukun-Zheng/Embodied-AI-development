# Complete Table of Contents

# 《具身智能：从物理世界到通用机器人》

> 本目录是知识依赖图，不是热门论文列表。章节顺序遵循：**世界 → 身体 → 感知 → 状态 → 预测 → 决策 → 控制 → 学习 → 泛化 → 持续发展**。

---

# Part 0　具身智能究竟是什么

## 0.1 为什么智能进入物理世界后，一切都变了
## 0.2 Agent、Body、Environment：具身系统的三个基本对象
## 0.3 从“输入—输出”到“闭环交互”
## 0.4 开环、闭环与反馈：机器人为什么不能只预测一次
## 0.5 部分可观测性：机器人永远看不见完整世界
## 0.6 时间、延迟与频率：真实系统中的隐形变量
## 0.7 Embodiment：身体不是输出接口，而是智能的一部分
## 0.8 从经典机器人到 Robot Learning，再到 Foundation Robot
## 0.9 什么叫“通用机器人”
## 0.10 如何使用本书：从初学者到研究者的路线

---

# Part I　具身智能的数学语言

## 1.1 标量、向量、矩阵与张量
## 1.2 线性映射、基与坐标变换
## 1.3 特征值、特征向量与稳定性直觉
## 1.4 SVD、PCA 与低维结构
## 1.5 微积分与多元微分
## 1.6 Jacobian、Hessian 与机器人中的导数
## 1.7 常微分方程：状态如何随时间变化
## 1.8 数值积分与离散时间系统
## 1.9 概率变量、分布与条件概率
## 1.10 Bayes Rule 与 belief
## 1.11 随机过程与时序不确定性
## 1.12 信息熵、互信息与任务相关信息
## 1.13 优化问题、约束与 Lagrangian
## 1.14 梯度优化与自动微分
## 1.15 凸优化和它的边界
## 1.16 动态系统、平衡点与稳定性
## 1.17 图论与机器人系统
## 1.18 从欧氏空间走向流形

---

# Part II　物理世界、机器人身体与机电系统

## 2.1 什么是自由度
## 2.2 刚体、连杆、关节与运动链
## 2.3 Revolute、Prismatic 与常见关节
## 2.4 电机、减速器、编码器与驱动器
## 2.5 Torque、Velocity、Position：三类控制接口
## 2.6 惯性、质量、摩擦与阻尼
## 2.7 刚度、柔顺与机械顺应性
## 2.8 传感器如何进入机器人身体
## 2.9 Serial、Parallel 与 Tendon-Driven 机构
## 2.10 单臂、双臂、移动操作、人形与灵巧手
## 2.11 Robot Description：URDF / MJCF / USD 在描述什么
## 2.12 机器人硬件与学习算法之间的真实接口

---

# Part III　空间、旋转与刚体几何

## 3.1 坐标系：机器人学中最容易被低估的问题
## 3.2 2D 旋转
## 3.3 3D Rotation Matrix
## 3.4 SO(3)：为什么旋转不是普通三维向量
## 3.5 Euler Angles 与万向节锁
## 3.6 Axis-Angle
## 3.7 Quaternion
## 3.8 Homogeneous Transformation
## 3.9 SE(3)：位姿的数学结构
## 3.10 Frame Composition 与 Inverse Transform
## 3.11 Lie Algebra：so(3) 与 se(3)
## 3.12 Exponential / Log Map
## 3.13 Twist 与 Screw Motion
## 3.14 Adjoint 与不同坐标系中的速度
## 3.15 Wrench 与力矩变换
## 3.16 代码中的位姿：常见 convention 灾难

---

# Part IV　机器人运动学

## 4.1 Forward Kinematics
## 4.2 Product of Exponentials
## 4.3 Denavit–Hartenberg：历史方法与现代使用方式
## 4.4 Manipulator Jacobian
## 4.5 Jacobian 的几何意义
## 4.6 Singularities
## 4.7 Velocity Kinematics
## 4.8 Inverse Kinematics
## 4.9 Analytical IK 与 Numerical IK
## 4.10 Damped Least Squares
## 4.11 Redundancy 与 Null Space
## 4.12 Differential IK
## 4.13 Trajectory Interpolation
## 4.14 Joint-space 与 Cartesian-space Trajectory
## 4.15 双臂与多链运动学

---

# Part V　动力学、接触与物理交互

## 5.1 从运动学到动力学
## 5.2 Newton–Euler 方法
## 5.3 Lagrangian Dynamics
## 5.4 Manipulator Equation
## 5.5 Mass Matrix
## 5.6 Coriolis / Centrifugal Term
## 5.7 Gravity Compensation
## 5.8 Forward 与 Inverse Dynamics
## 5.9 Contact、Constraint 与 Reaction Force
## 5.10 Coulomb Friction 与接触摩擦
## 5.11 Complementarity 与 Contact Solver
## 5.12 Soft Contact 与刚体近似
## 5.13 Grasp Mechanics
## 5.14 Center of Mass / ZMP / Centroidal Dynamics
## 5.15 为什么仿真中的物理从来不是“真实世界本身”

---

# Part VI　反馈控制与最优控制

## 6.1 控制到底控制什么
## 6.2 Open-loop vs Closed-loop
## 6.3 PID 从误差反馈推导
## 6.4 Stability 与 Lyapunov 直觉
## 6.5 Joint Position / Velocity / Torque Control
## 6.6 Computed Torque Control
## 6.7 Impedance Control
## 6.8 Admittance Control
## 6.9 Operational Space Control
## 6.10 Force Control 与 Hybrid Position/Force Control
## 6.11 Linear Quadratic Regulator
## 6.12 Optimal Control
## 6.13 Model Predictive Control
## 6.14 Constrained Control
## 6.15 Whole-Body Control 基础
## 6.16 Learning Policy 与低层 Controller 如何分工

---

# Part VII　机器人感知系统

## 7.1 从物理量到 observation
## 7.2 RGB Camera
## 7.3 Camera Intrinsics
## 7.4 Camera Extrinsics
## 7.5 Projection 与 Back-Projection
## 7.6 Stereo Vision
## 7.7 Depth Camera
## 7.8 LiDAR
## 7.9 IMU
## 7.10 Joint Encoder 与 Proprioception
## 7.11 Force/Torque Sensor
## 7.12 Tactile Sensor
## 7.13 Event Camera 与高速感知
## 7.14 Sensor Noise、Calibration 与 Synchronization
## 7.15 多模态传感器时间对齐

---

# Part VIII　视觉、三维几何与机器人表征

## 8.1 图像是机器人看到的世界吗
## 8.2 CNN 与视觉特征
## 8.3 Vision Transformer
## 8.4 Self-Supervised Visual Representation
## 8.5 Detection / Segmentation / Tracking
## 8.6 Optical Flow
## 8.7 Depth 与 Geometry
## 8.8 Point Cloud
## 8.9 Voxel / TSDF / Occupancy
## 8.10 NeRF 与隐式三维表示
## 8.11 3D Gaussian Splatting 与动态场景
## 8.12 Object-Centric Representation
## 8.13 Scene Graph
## 8.14 Egocentric Representation
## 8.15 Task-Relevant Representation
## 8.16 Representation 是否真的服务物理交互

---

# Part IX　状态估计、定位与世界状态

## 9.1 Observation 不等于 State
## 9.2 Hidden State 与 Belief State
## 9.3 Bayes Filter
## 9.4 Kalman Filter
## 9.5 Extended / Unscented Kalman Filter
## 9.6 Particle Filter
## 9.7 Sensor Fusion
## 9.8 Visual Odometry
## 9.9 SLAM
## 9.10 Object Pose Estimation
## 9.11 Dynamic Scene State Estimation
## 9.12 Uncertainty Calibration
## 9.13 POMDP：部分可观测世界的统一框架

---

# Part X　规划、搜索与决策

## 10.1 什么是 Planning
## 10.2 Configuration Space
## 10.3 Collision Checking
## 10.4 Graph Search：BFS / Dijkstra / A*
## 10.5 Sampling-Based Planning：PRM / RRT
## 10.6 RRT* 与渐近最优性
## 10.7 Trajectory Optimization
## 10.8 CHOMP / STOMP 类方法
## 10.9 Task and Motion Planning
## 10.10 Hierarchical Planning
## 10.11 Planning under Uncertainty
## 10.12 Receding-Horizon Planning
## 10.13 Planning 与 Learned Policy 的边界

---

# Part XI　机器学习基础：为机器人而重新学习

## 11.1 Supervised Learning
## 11.2 Generalization
## 11.3 Distribution Shift
## 11.4 Representation Learning
## 11.5 Sequence Modeling
## 11.6 Attention
## 11.7 Transformer
## 11.8 Self-Supervised Learning
## 11.9 Contrastive Learning
## 11.10 Generative Modeling
## 11.11 Variational Autoencoder
## 11.12 Diffusion Model
## 11.13 Flow Matching
## 11.14 Autoregressive Modeling
## 11.15 为什么机器人学习不是普通 i.i.d. 学习

---

# Part XII　模仿学习

## 12.1 Demonstration 是什么
## 12.2 Behavior Cloning
## 12.3 Covariate Shift
## 12.4 DAgger
## 12.5 Dataset Aggregation 与 Intervention
## 12.6 Action Chunking
## 12.7 ACT
## 12.8 Latent Action Representation
## 12.9 Human Demonstration / Teleoperation
## 12.10 Learning from Video
## 12.11 Offline Demonstration Data
## 12.12 Multi-Task Imitation Learning
## 12.13 Failure Recovery from Demonstrations

---

# Part XIII　强化学习与交互学习

## 13.1 MDP
## 13.2 Return 与 Value Function
## 13.3 Bellman Equation
## 13.4 Q-Learning
## 13.5 Policy Gradient
## 13.6 Actor–Critic
## 13.7 PPO
## 13.8 SAC
## 13.9 Model-Based RL
## 13.10 Offline RL
## 13.11 Reward Design
## 13.12 Sparse Reward 与 Exploration
## 13.13 Curriculum Learning
## 13.14 Residual RL
## 13.15 RL for Manipulation
## 13.16 RL for Locomotion
## 13.17 从仿真高 reward 到真实机器人能力之间的鸿沟

---

# Part XIV　生成式机器人策略

## 14.1 为什么动作需要分布而不是单点回归
## 14.2 Multimodal Action Distribution
## 14.3 Diffusion Policy
## 14.4 Observation Conditioning
## 14.5 Action Horizon
## 14.6 Receding-Horizon Execution
## 14.7 3D Diffusion Policy
## 14.8 Flow-Matching Robot Policy
## 14.9 Autoregressive Action Token
## 14.10 Continuous vs Discrete Actions
## 14.11 Chunking、Latency 与 Control Frequency
## 14.12 Generative Policy Failure Modes
## 14.13 Diffusion / Flow / AR：何时该用谁

---

# Part XV　语言、视觉语言模型与机器人

## 15.1 Language 如何进入机器人系统
## 15.2 Tokenization
## 15.3 Vision-Language Pretraining
## 15.4 CLIP
## 15.5 BLIP / LLaVA 类多模态模型
## 15.6 Grounding
## 15.7 Affordance
## 15.8 Open-Vocabulary Perception
## 15.9 Language-conditioned Planning
## 15.10 VLM 能知道什么、不能知道什么
## 15.11 Internet Knowledge 与 Physical Knowledge 的差异
## 15.12 从 VLM 到 Robotics Foundation Model

---

# Part XVI　Vision-Language-Action 与通用机器人策略

## 16.1 VLA 的系统定义
## 16.2 RT 系列与早期大规模机器人 Transformer
## 16.3 Open X-Embodiment 与跨机器人数据
## 16.4 Generalist Robot Policy
## 16.5 Octo 类开放通用策略
## 16.6 π 系列与 Flow-Based Action Generation
## 16.7 Action Tokenization
## 16.8 Vision / Language / Proprioception Fusion
## 16.9 Training Objective
## 16.10 Robot Dataset Mixture
## 16.11 Cross-Task Generalization
## 16.12 Cross-Robot Generalization
## 16.13 Inference Latency 与 Real-Time Control
## 16.14 VLA 的低层 Controller 去哪里了
## 16.15 VLA 失败模式
## 16.16 “规模化”究竟解决了哪些问题
## 16.17 VLA 是否真的学习了物理世界

---

# Part XVII　World Models 与预测式智能

## 17.1 什么叫 World Model
## 17.2 Dynamics Model
## 17.3 Latent Dynamics
## 17.4 Video Prediction
## 17.5 Action-Conditioned Prediction
## 17.6 Model Predictive Control with Learned Dynamics
## 17.7 JEPA / Predictive Representation
## 17.8 V-JEPA 类路线
## 17.9 Object-Centric World Model
## 17.10 3D / 4D World Model
## 17.11 Contact-Aware Prediction
## 17.12 Counterfactual Prediction
## 17.13 Uncertainty-aware World Model
## 17.14 World Model 如何被 policy 真正利用
## 17.15 “会生成视频”是否等于“理解物理”

---

# Part XVIII　具身推理、记忆与长时程任务

## 18.1 Reactive Policy 的极限
## 18.2 Goal Representation
## 18.3 Skill / Option / Primitive
## 18.4 Hierarchical Policy
## 18.5 Task Decomposition
## 18.6 Embodied Chain-of-Thought 的证据问题
## 18.7 External Memory
## 18.8 Episodic Memory
## 18.9 Semantic Memory
## 18.10 Long-Horizon Planning
## 18.11 Closed-Loop Replanning
## 18.12 Error Detection
## 18.13 Recovery Policy
## 18.14 Self-Evaluation 与 Reflection
## 18.15 Reasoning 到底怎样影响 motor behavior

---

# Part XIX　主动感知与信息获取

## 19.1 被动视觉为什么不够
## 19.2 Observability
## 19.3 Epistemic vs Aleatoric Uncertainty
## 19.4 Information Gain
## 19.5 Next-Best-View
## 19.6 Active Vision
## 19.7 Task-Driven Active Perception
## 19.8 Occlusion Reasoning
## 19.9 Viewpoint Planning
## 19.10 Embodiment-Agnostic View Goal
## 19.11 Perception-Action Coupling
## 19.12 Active Touch
## 19.13 信息价值与动作代价
## 19.14 主动感知如何与 VLA / World Model 融合

---

# Part XX　机器人操作

## 20.1 Manipulation 的本质
## 20.2 Reach / Push / Pull
## 20.3 Pick and Place
## 20.4 Grasp Planning
## 20.5 Contact-Rich Manipulation
## 20.6 Tool Use
## 20.7 Deformable Object
## 20.8 Cable / Rope / Cloth
## 20.9 Mobile Manipulation
## 20.10 Long-Horizon Manipulation
## 20.11 Generalization Across Objects
## 20.12 Real-World Failure Taxonomy

---

# Part XXI　双臂、灵巧手与协同操作

## 21.1 为什么双臂不是两个单臂
## 21.2 Relative Pose 与 Coordinated Frame
## 21.3 Bimanual Constraint
## 21.4 Leader–Follower Coordination
## 21.5 Symmetric / Asymmetric Collaboration
## 21.6 Handover
## 21.7 Cooperative Manipulation
## 21.8 双臂 Collision 与 Safety
## 21.9 Dexterous Hand Kinematics
## 21.10 In-Hand Manipulation
## 21.11 Tactile Dexterity
## 21.12 Whole-Hand Contact
## 21.13 Learning Bimanual Policies
## 21.14 Learning Dexterous Policies

---

# Part XXII　Locomotion 与 Humanoid

## 22.1 Legged Robot 的状态与动作
## 22.2 Gait
## 22.3 Balance
## 22.4 ZMP 与 Capture Point
## 22.5 Centroidal Dynamics
## 22.6 Quadruped Locomotion
## 22.7 Biped Locomotion
## 22.8 RL Locomotion
## 22.9 Sim-to-Real for Locomotion
## 22.10 Humanoid Whole-Body State
## 22.11 Motion Retargeting
## 22.12 Human Motion Prior
## 22.13 Humanoid Manipulation
## 22.14 Locomotion + Manipulation
## 22.15 Fall Recovery
## 22.16 General-Purpose Humanoid 的现实瓶颈

---

# Part XXIII　Whole-Body Intelligence 与 Multi-Robot

## 23.1 Whole-Body Task Representation
## 23.2 Hierarchical Whole-Body Policy
## 23.3 Unified Action Space
## 23.4 Whole-Body MPC
## 23.5 Whole-Body RL
## 23.6 Whole-Body VLA
## 23.7 多机器人系统基础
## 23.8 Communication
## 23.9 Coordination
## 23.10 Task Allocation
## 23.11 Multi-Agent Planning
## 23.12 Shared World Model
## 23.13 Centralized Training / Decentralized Execution
## 23.14 多机器人具身基础模型

---

# Part XXIV　Cross-Embodiment、持续学习与发展型智能

## 24.1 Embodiment 到底包含什么
## 24.2 Morphology 与 Action Space
## 24.3 Embodiment Encoding
## 24.4 Cross-Embodiment Dataset
## 24.5 Cross-Robot Transfer
## 24.6 Morphology-Conditioned Policy
## 24.7 Universal Action Representation
## 24.8 Continual Learning
## 24.9 Catastrophic Forgetting
## 24.10 Replay / Regularization / Modular Growth
## 24.11 Online Adaptation
## 24.12 Test-Time Adaptation
## 24.13 Lifelong Robot Learning
## 24.14 Developmental Robotics
## 24.15 Structural Plasticity
## 24.16 Memory Formation 与 Forgetting
## 24.17 不区分“训练/推理”的持续交互系统
## 24.18 从固定网络到可生长中枢

---

# Part XXV　仿真、数据与 Sim-to-Real

## 25.1 为什么机器人研究离不开仿真
## 25.2 Physics Engine 基础
## 25.3 MuJoCo
## 25.4 SAPIEN
## 25.5 Isaac Sim
## 25.6 Isaac Lab
## 25.7 RoboTwin 类机器人学习平台
## 25.8 Scene / Asset / Robot Import
## 25.9 Parallel Simulation
## 25.10 Synthetic Data
## 25.11 Robot Dataset Schema
## 25.12 Episode / Trajectory / Transition
## 25.13 RGB / Depth / Point Cloud / State 同步
## 25.14 Dataset Cleaning
## 25.15 Data Mixture
## 25.16 Domain Randomization
## 25.17 Dynamics Randomization
## 25.18 System Identification
## 25.19 Sim-to-Real
## 25.20 Real-to-Sim-to-Real

---

# Part XXVI　机器人系统工程与部署

## 26.1 从 Python Script 到 Robot System
## 26.2 ROS 2
## 26.3 Topic / Service / Action
## 26.4 TF 与坐标树
## 26.5 Real-Time Control
## 26.6 Multi-Rate System
## 26.7 Network Latency
## 26.8 GPU Inference Pipeline
## 26.9 Camera Streaming
## 26.10 Robot Driver
## 26.11 Safety Monitor
## 26.12 Logging 与 Replay
## 26.13 Determinism 与 Reproducibility
## 26.14 Deployment Optimization
## 26.15 Distributed Training
## 26.16 大模型与机器人端侧推理
## 26.17 一次真实机器人实验到底发生了什么

---

# Part XXVII　Benchmark、评测与安全

## 27.1 Benchmark 为什么会误导研究
## 27.2 Task Success Rate
## 27.3 Robustness
## 27.4 Generalization Matrix
## 27.5 OOD Evaluation
## 27.6 Perturbation Test
## 27.7 Long-Horizon Evaluation
## 27.8 Intervention Rate
## 27.9 Efficiency / Latency / Energy
## 27.10 Calibration 与 Uncertainty
## 27.11 Benchmark Leakage
## 27.12 Reproducibility
## 27.13 Physical Safety
## 27.14 Constraint / Shield / Safe Controller
## 27.15 Human-Robot Interaction Safety
## 27.16 Foundation Model Safety for Robots
## 27.17 “成功一次”与“可靠系统”的区别

---

# Part XXVIII　具身智能研究方法与开放前沿

## 28.1 怎样读一篇具身论文
## 28.2 怎样拆一个机器人系统
## 28.3 怎样复现论文而不只是跑通代码
## 28.4 怎样设计 Baseline
## 28.5 怎样做 Ablation
## 28.6 怎样构造 Negative Control
## 28.7 怎样从 Failure Mode 找研究问题
## 28.8 怎样区分 Data Gain 与 Architecture Gain
## 28.9 怎样判断一个 World Model 是否真的有用
## 28.10 怎样判断视觉表征是否真正服务物理交互
## 28.11 怎样判断“Reasoning”是不是包装
## 28.12 怎样研究 VLA 的物理能力边界
## 28.13 Transformer 在具身智能中的真正作用
## 28.14 Transformer 之后可能是什么
## 28.15 Causality 与 Physical Intelligence
## 28.16 Compositionality
## 28.17 Mechanism Discovery
## 28.18 Self-Evolving Architecture
## 28.19 Mathematical Embodied Intelligence
## 28.20 具身智能距离“通用智能”还有什么
## 28.21 如何提出一个可证伪的新架构
## 28.22 从本科生到独立具身研究者

---

# Appendices

## Appendix A　符号表
## Appendix B　机器人学常用坐标与旋转 Convention
## Appendix C　PyTorch / JAX 最小数学实现
## Appendix D　MuJoCo / SAPIEN / Isaac Lab 环境指南
## Appendix E　ROS 2 快速参考
## Appendix F　机器人数据格式参考
## Appendix G　重要论文时间线
## Appendix H　经典教材与课程地图
## Appendix I　实验复现清单
## Appendix J　研究设计 Checklist

---

# 目录维护原则

目录不是永久冻结的。新增章节必须满足至少一个条件：

1. 补上现有知识依赖中的真实缺口；
2. 新技术已经形成足够独立的方法论；
3. 新问题无法被现有章节自然覆盖；
4. 新研究方向具有持续价值，而非短期模型热点。

任何前沿模型都应优先进入已有知识框架，而不是每出现一个新模型就新增一个孤立章节。
