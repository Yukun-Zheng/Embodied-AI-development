# Complete Table of Contents

# 《具身智能：从物理世界到通用机器人》
## Embodied Intelligence: From Physical Principles to General-Purpose Robots

> **Curriculum baseline: v1.0 — knowledge frontier frozen at 2026-09-14.**
>
> 本目录由 `book/chapters/00-*.md` 到 `50-*.md` 的真实标题自动生成，**Chapter 是唯一真源**。不要手工维护一份会与正文漂移的平行目录。
>
> 主线：**物理世界 → 身体 → 感知 → 状态 → 决策 → 控制 → 学习 → 基础模型 → 预测与推理 → 泛化 → 经验学习 → 持续发展。**
>
> 模型会过时，知识结构不能随热点漂移。RT、Octo、OpenVLA、π、GR00T、Gemini Robotics、Helix、V-JEPA 等只作为历史节点和案例进入统一框架。

---

# Volume 0　导论：智能为什么必须进入物理世界

# [Part 0　具身智能究竟是什么](./chapters/00-what-is-embodied-intelligence.md)

## 学习目标
## 0.1 从函数拟合到闭环交互
## 0.2 Agent、Body、Environment
## 0.3 Observation 不等于 State
## 0.4 Embodiment 的五层含义
## 0.5 Affordance：世界是“能做什么”
## 0.6 时间与实时性
## 0.7 Morphological Computation
## 0.8 什么叫 General-Purpose Robot
## 0.9 一套统一分析框架
## 思考题
## 0.10 从“智能模型”到物理闭环的数据流
## 0.11 研究问题
## Source anchors / 原始来源

# [Part 1　思想史与技术史：从控制论到机器人基础模型](./chapters/01-history-and-lineage.md)

## 学习目标
## 1.1 控制论：智能首先是反馈
## 1.2 Sense–Plan–Act
## 1.3 Behavior-Based Robotics
## 1.4 Classical Robotics 的成熟
## 1.5 深度学习首先改变 Perception
## 1.6 Deep RL 与 Imitation 进入控制
## 1.7 Simulation Scaling
## 1.8 Transformer 进入 Robot Learning
## 1.9 语言模型进入机器人
## 1.10 RT-1 / RT-2
## 1.11 Open X-Embodiment
## 1.12 Octo / OpenVLA：开放化
## 1.13 π 系列：连续 Action Expert 与经验学习
## 1.14 GR00T / Gemini Robotics / Helix
## 1.15 World Model 的回归
## 1.16 历史中的循环
## 1.17 版本演进不等于科学问题演进
## 1.18 证据等级随历史阶段变化
## 1.19 读历史的常见失败
## 最小实验：做一次机制谱系审计
## 研究问题
## Source anchors / 原始来源


---

# Volume I　数学与计算语言

# [Part 2　线性代数、微积分与数值计算](./chapters/02-linear-algebra-calculus-numerics.md)

## 学习目标
## 2.1 Shape 是第一语义
## 2.2 线性映射
## 2.3 基与坐标
## 2.4 Rank / Range / Null Space
## 2.5 Least Squares
## 2.6 SVD 与 Pseudoinverse
## 2.7 Damped Least Squares
## 2.8 Eigenvalue 与系统模式
## 2.9 Gradient
## 2.10 Jacobian
## 2.11 Hessian
## 2.12 Chain Rule 与 Backprop
## 2.13 Automatic Differentiation
## 2.14 ODE 与 State Dynamics
## 2.15 Discretization
## 2.16 Conditioning
## 2.17 从公式到机器人代码的数据流
## 2.18 常见数值失败
## 研究问题
## Source anchors / 原始来源
## 必须掌握的结论

# [Part 3　概率、统计、信息与不确定性](./chapters/03-probability-information-uncertainty.md)

## 3.1 为什么机器人必须概率化
## 3.2 Random Variable 与 Distribution
## 3.3 Expectation / Variance / Covariance
## 3.4 Bayes Rule
## 3.5 Gaussian
## 3.6 Conditional Independence
## 3.7 MLE / MAP
## 3.8 Bayes Filter
## 3.9 Entropy
## 3.10 KL Divergence
## 3.11 Mutual Information
## 3.12 Epistemic vs Aleatoric
## 3.13 Calibration
## 3.14 Monte Carlo
## 3.15 Uncertainty 必须改变行为
## 3.16 从“不确定”到决策：Uncertainty 的闭环接口
## Source anchors / 原始来源

# [Part 4　优化、动态系统与最优决策](./chapters/04-optimization-dynamics-decision.md)

## 4.1 机器人问题几乎都可以写成优化
## 4.2 Lagrangian
## 4.3 KKT
## 4.4 Convexity
## 4.5 Gradient Descent
## 4.6 Dynamic System
## 4.7 Equilibrium 与 Linearization
## 4.8 Lyapunov Stability
## 4.9 Optimal Control
## 4.10 Dynamic Programming
## 4.11 LQR
## 4.12 iLQR / DDP
## 4.13 MPC
## 4.14 Pontryagin Minimum Principle
## 4.15 Optimal Transport / Flow
## 4.16 Model Mismatch：最优解只对所写问题最优
## 4.17 常见失败
## 4.18 研究问题
## Source anchors / 原始来源

# [Part 5　几何、流形、图与因果](./chapters/05-geometry-graphs-causality.md)

## 学习目标
## 5.1 为什么欧氏向量不够
## 5.2 Manifold
## 5.3 Lie Group
## 5.4 Lie Algebra 与 Exp / Log
## 5.5 Equivariance
## 5.6 Graph：身体和世界天然是关系结构
## 5.7 Message Passing
## 5.8 Factor Graph
## 5.9 Causal Graph
## 5.10 Confounding
## 5.11 Intervention
## 5.12 Counterfactual
## 5.13 Identifiability
## 5.14 几何与因果的结合
## 5.15 从 scene 到 action 的结构化数据流
## 5.16 常见失败
## 研究问题
## Source anchors / 原始来源


---

# Volume II　机器人身体、几何、力学与控制

# [Part 6　机器人身体、执行器与机电系统](./chapters/06-robot-body-mechatronics.md)

## 学习目标
## 6.1 Degree of Freedom
## 6.2 Joint 与 Link
## 6.3 Actuator Chain
## 6.4 Motor
## 6.5 Gearbox
## 6.6 Position / Velocity / Torque Control Interface
## 6.7 Stiffness 与 Compliance
## 6.8 Series Elastic / Tendon / Underactuation
## 6.9 Sensor Integration
## 6.10 Power 与 Thermal
## 6.11 Communication
## 6.12 Embedded Compute
## 6.13 Robot Description
## 6.14 身体是算法的一部分
## 实验
## 研究问题
## 6.19 机电层 Failure Taxonomy
## 6.20 最小实验：高层 policy 不变，只改变机电链
## Source anchors / 原始来源

# [Part 7　空间、旋转与刚体几何](./chapters/07-rigid-body-geometry.md)

## 学习目标
## 7.1 Frame 是机器人学的语法
## 7.2 2D Rotation
## 7.3 SO(3)
## 7.4 Euler Angles
## 7.5 Axis–Angle
## 7.6 Quaternion
## 7.7 Homogeneous Transformation
## 7.8 SO(3) Lie Algebra
## 7.9 Exponential Map
## 7.10 SE(3) 与 Twist
## 7.11 Space vs Body Twist
## 7.12 Adjoint
## 7.13 Wrench
## 7.14 Pose Error
## 7.15 Interpolation
## 7.16 Convention Failure Checklist
## 实验
## 研究问题
## 7.19 刚体几何在软件栈中的真实数据流
## 7.20 最小实验：Frame-Convention Fuzz Test
## Source anchors / 原始来源

# [Part 8　机器人运动学](./chapters/08-robot-kinematics.md)

## 学习目标
## 8.1 Forward Kinematics
## 8.2 Serial Chain
## 8.3 Product of Exponentials
## 8.4 Denavit–Hartenberg
## 8.5 Differential Kinematics
## 8.6 Space / Body Jacobian
## 8.7 Singularity
## 8.8 Manipulability Ellipsoid
## 8.9 Inverse Kinematics
## 8.10 Newton / Jacobian IK
## 8.11 Damped Least Squares
## 8.12 Redundancy
## 8.13 Joint Limit Avoidance
## 8.14 Constrained IK
## 8.15 Trajectory Generation
## 8.16 Differential IK as Controller
## 8.17 Bimanual Kinematics
## 8.18 Whole-Body Kinematics
## 8.19 Learning Policy 与 IK 的接口
## 8.20 一条真实 Cartesian-action 数据流
## 8.21 IK Failure Taxonomy
## 8.22 Hierarchical Task Priority
## 研究问题
## Source anchors / 原始来源

# [Part 9　动力学、接触与抓取](./chapters/09-dynamics-contact-grasping.md)

## 学习目标
## 9.1 从 Kinematics 到 Dynamics
## 9.2 Manipulator Equation
## 9.3 Mass Matrix
## 9.4 Lagrangian Derivation
## 9.5 Newton–Euler
## 9.6 Forward Dynamics
## 9.7 Inverse Dynamics
## 9.8 Friction
## 9.9 Contact Geometry
## 9.10 Contact Constraint
## 9.11 Complementarity
## 9.12 Coulomb Friction Cone
## 9.13 Soft Contact
## 9.14 Grasp Map
## 9.15 Form Closure vs Force Closure
## 9.16 Grasp Quality
## 9.17 Contact Mode
## 9.18 Deformable Contact
## 9.19 Centroidal Dynamics
## 9.20 ZMP / Support
## 9.21 Simulator Contact 不是 Reality
## 9.22 Learning Dynamics Residual
## 实验
## 研究问题
## 9.24 Contact / Dynamics Failure Taxonomy
## 9.25 最小实验：同一视觉状态，不同物理参数
## Source anchors / 原始来源

# [Part 10　反馈控制、最优控制与 Whole-Body Control](./chapters/10-feedback-optimal-whole-body-control.md)

## 学习目标
## 10.1 控制真正控制的是什么
## 10.2 Open Loop 与 Closed Loop
## 10.3 PID
## 10.4 Joint-Space PD
## 10.5 Gravity Compensation
## 10.6 Computed Torque Control
## 10.7 Impedance Control
## 10.8 Admittance Control
## 10.9 Operational-Space Control
## 10.10 Hybrid Position / Force Control
## 10.11 Passivity 直觉
## 10.12 LQR
## 10.13 iLQR / DDP
## 10.14 Model Predictive Control
## 10.15 Constraint Handling
## 10.16 Whole-Body Control
## 10.17 Task Priority
## 10.18 Control Barrier Function
## 10.19 Learned Policy 与 Controller 的分工
## 10.20 多时间尺度
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 11　运动规划、任务规划与不确定决策](./chapters/11-motion-task-uncertainty-planning.md)

## 学习目标
## 11.1 Planning 的基本对象
## 11.2 Configuration Space
## 11.3 Collision Checking
## 11.4 Graph Search
## 11.5 PRM
## 11.6 RRT
## 11.7 RRT*
## 11.8 Narrow Passage
## 11.9 Path vs Trajectory
## 11.10 Trajectory Optimization
## 11.11 Kinodynamic Planning
## 11.12 Motion Primitive
## 11.13 Task Planning
## 11.14 Task and Motion Planning
## 11.15 Affordance 与 Planner
## 11.16 Planning Under Uncertainty
## 11.17 Information-Gathering Action
## 11.18 Receding-Horizon Planning
## 11.19 Hierarchical Planning
## 11.20 Learned Planner
## 11.21 VLM / LLM Planner
## 11.22 VLA 与 Planning
## 11.23 Planner–Policy Hybrid
## 11.24 常见失败
## 研究问题
## Source anchors / 原始来源


---

# Volume III　感知、状态与世界表示

# [Part 12　机器人传感器、标定与时间](./chapters/12-sensors-calibration-time.md)

## 学习目标
## 12.1 从物理量到 Observation
## 12.2 相机成像模型
## 12.3 Intrinsics 与 Distortion
## 12.4 Extrinsics
## 12.5 Back-Projection
## 12.6 Stereo Vision
## 12.7 Structured Light / Time-of-Flight
## 12.8 LiDAR
## 12.9 IMU
## 12.10 Encoder 与 Proprioception
## 12.11 Motor Current 与 Torque Estimate
## 12.12 Force/Torque Sensor
## 12.13 Tactile Sensor
## 12.14 Event Camera
## 12.15 Audio
## 12.16 Sensor Noise
## 12.17 Calibration 层级
## 12.18 Hand–Eye Calibration
## 12.19 Kinematic Calibration
## 12.20 Timestamp
## 12.21 Synchronization
## 12.22 Motion-Induced Temporal Error
## 12.23 Rolling Shutter
## 12.24 Observation Packet
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 13　二维视觉与视觉表示学习](./chapters/13-2d-vision-representation.md)

## 学习目标
## 13.1 图像不是世界
## 13.2 从 Hand-Crafted Feature 到 Deep Representation
## 13.3 CNN
## 13.4 Receptive Field
## 13.5 Feature Pyramid
## 13.6 Vision Transformer
## 13.7 Patch Size 的物理含义
## 13.8 Positional Encoding
## 13.9 Detection
## 13.10 Semantic 与 Instance Segmentation
## 13.11 Tracking
## 13.12 Optical Flow
## 13.13 Scene Flow
## 13.14 Visual Servoing
## 13.15 Contrastive Learning
## 13.16 Masked Image Modeling
## 13.17 Self-Distillation
## 13.18 Vision-Language Pretraining
## 13.19 Video Self-Supervision
## 13.20 Egocentric Human Video
## 13.21 Task-Relevant Representation
## 13.22 Probe 不是终点
## 13.23 Counterfactual Visual Intervention
## 13.24 Multi-Camera Fusion
## 13.25 Wrist Camera vs Global Camera
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 14　三维、四维与对象中心世界表示](./chapters/14-3d-4d-world-representation.md)

## 学习目标
## 14.1 为什么机器人需要 3D
## 14.2 Point Cloud
## 14.3 PointNet 思想
## 14.4 Local Geometry
## 14.5 Point Transformer
## 14.6 Voxel
## 14.7 Occupancy
## 14.8 Signed Distance Field
## 14.9 TSDF
## 14.10 Mesh
## 14.11 NeRF
## 14.12 NeRF for Robotics
## 14.13 3D Gaussian Splatting
## 14.14 3D Representation 的统一比较
## 14.15 Dynamic Scene
## 14.16 4D Representation
## 14.17 Scene Flow
## 14.18 Rigid Object Factorization
## 14.19 Object-Centric Representation
## 14.20 Articulated Object
## 14.21 Scene Graph
## 14.22 Spatial Relation 不应只离散化
## 14.23 Affordance Field
## 14.24 Signed Distance + Affordance
## 14.25 Egocentric vs Allocentric
## 14.26 Embodiment-Agnostic Representation
## 14.27 Uncertainty in 3D
## 14.28 Occlusion
## 14.29 Representation 与 World Model
## 14.30 怎样评价 3D/4D 表示
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 15　状态估计、定位与世界状态](./chapters/15-state-estimation-localization.md)

## 学习目标
## 15.1 什么是 State
## 15.2 Observation 与 Hidden State
## 15.3 Belief State
## 15.4 Bayes Filter
## 15.5 Kalman Filter
## 15.6 一维例子
## 15.7 Extended Kalman Filter
## 15.8 Unscented Kalman Filter
## 15.9 Particle Filter
## 15.10 Sensor Fusion
## 15.11 Observability
## 15.12 Visual Odometry
## 15.13 SLAM
## 15.14 Loop Closure
## 15.15 Object Pose Estimation
## 15.16 Pose Tracking
## 15.17 Articulated State Estimation
## 15.18 Contact State Estimation
## 15.19 Dynamic World State
## 15.20 POMDP
## 15.21 Learned Hidden State
## 15.22 State Representation 与 Sufficiency
## 15.23 Uncertainty Calibration
## 15.24 Estimation–Control Coupling
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 16　触觉、力觉与接触智能](./chapters/16-tactile-contact-intelligence.md)

## 学习目标
## 16.1 为什么 Vision 不够
## 16.2 Contact 是局部但高带宽的事件
## 16.3 Force/Torque Sensing
## 16.4 Contact Detection
## 16.5 Joint Torque Residual
## 16.6 Tactile Sensor 类型
## 16.7 Vision-Based Tactile
## 16.8 Contact Patch
## 16.9 Normal 与 Shear
## 16.10 Slip Detection
## 16.11 Tactile Reflex
## 16.12 为什么不能把 Tactile 只塞进慢速 VLA
## 16.13 Early / Late / Hierarchical Fusion
## 16.14 Tactile Representation
## 16.15 Visuo-Tactile Alignment
## 16.16 Material Perception
## 16.17 Tactile World Model
## 16.18 Predictive + Reactive 触觉
## 16.19 Cross-Sensor Tactile Learning
## 16.20 Dexterous Hand
## 16.21 Bimanual Contact
## 16.22 Tactile Data Collection
## 16.23 Simulating Tactile
## 16.24 Safety
## 常见失败
## 研究问题
## 2026 延伸阅读

# [Part 17　主动感知：让机器人决定“下一眼看哪里”](./chapters/17-active-perception.md)

## 学习目标
## 17.1 被动视觉的上限
## 17.2 Perception–Action Coupling
## 17.3 Observability
## 17.4 Task-Relevant Uncertainty
## 17.5 Entropy Reduction
## 17.6 Mutual Information 形式
## 17.7 Epistemic vs Aleatoric
## 17.8 Next-Best-View
## 17.9 Coverage-Based NBV
## 17.10 Task-Driven NBV
## 17.11 Learned View Utility
## 17.12 Occlusion Reasoning
## 17.13 Viewpoint Geometry
## 17.14 Self-Occlusion
## 17.15 Head / Wrist / Base：谁来动？
## 17.16 Embodiment-Agnostic View Goal
## 17.17 Active Object Manipulation for Perception
## 17.18 Active Touch
## 17.19 Dual Control
## 17.20 Exploration vs Task Execution
## 17.21 Stopping Rule
## 17.22 Active Perception 与 VLA
## 17.23 Active Perception 与 World Model
## 17.24 Active Mapping
## 17.25 Information Bottleneck 与 Attention
## 17.26 主动感知的公平 Benchmark
## 17.27 核心指标
## 常见失败
## 研究问题
## Source anchors / 原始来源


---

# Volume IV　机器人学习的基础范式

# [Part 18　为机器人重新学习机器学习](./chapters/18-machine-learning-for-robots.md)

## 学习目标
## 18.1 监督学习的标准形式
## 18.2 Policy-Induced Distribution
## 18.3 Offline Metric 与 Rollout Metric
## 18.4 Generalization 的维度
## 18.5 Bias–Variance 只是开始
## 18.6 Representation Learning
## 18.7 Sufficient Representation
## 18.8 Sequence Modeling
## 18.9 RNN
## 18.10 LSTM / GRU
## 18.11 Attention
## 18.12 Transformer
## 18.13 Causal vs Bidirectional Attention
## 18.14 Transformer 的二次复杂度
## 18.15 Self-Supervised Learning
## 18.16 Inverse Dynamics Objective
## 18.17 Forward Prediction Objective
## 18.18 Contrastive Objective 的陷阱
## 18.19 Generative Modeling
## 18.20 Autoregressive Modeling
## 18.21 Variational Autoencoder
## 18.22 Diffusion Model
## 18.23 Flow Matching
## 18.24 Multitask Learning
## 18.25 Gradient Interference
## 18.26 Pretraining / Fine-Tuning / Post-Training
## 18.27 Scaling Law 的正确读法
## 18.28 Distribution Shift Taxonomy
## 18.29 Closed-Loop Learning Science
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 19　模仿学习](./chapters/19-imitation-learning.md)

## 学习目标
## 19.1 Demonstration 是什么
## 19.2 Demonstration 来源
## 19.3 Behavior Cloning
## 19.4 Multimodal Demonstration
## 19.5 Covariate Shift
## 19.6 Recovery Blind Spot
## 19.7 DAgger
## 19.8 Mixture Policy
## 19.9 Human Intervention
## 19.10 Intervention Prediction
## 19.11 Action Chunking
## 19.12 Chunk Horizon
## 19.13 ACT
## 19.14 ACT 的 CVAE 直觉
## 19.15 Temporal Ensembling
## 19.16 Teleoperation
## 19.17 Leader–Follower Hardware
## 19.18 Kinesthetic Teaching
## 19.19 Learning from Play
## 19.20 Goal Relabeling
## 19.21 Multi-Task Imitation
## 19.22 Language Annotation
## 19.23 Learning from Video
## 19.24 Retargeting
## 19.25 Offline Demonstration Dataset
## 19.26 Failure Data
## 19.27 Recovery Demonstration
## 19.28 Curriculum of Demonstrations
## 19.29 Dataset Aggregation at Scale
## 19.30 BC 什么时候仍然最合理
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 20　强化学习、Offline RL 与交互学习](./chapters/20-reinforcement-offline-online.md)

## 学习目标
## 20.1 MDP
## 20.2 Return
## 20.3 Value Function
## 20.4 Bellman Equation
## 20.5 Q-Learning
## 20.6 Policy Gradient
## 20.7 Actor–Critic
## 20.8 Generalized Advantage Estimation
## 20.9 PPO
## 20.10 PPO 不等于“简单”
## 20.11 SAC
## 20.12 On-Policy vs Off-Policy
## 20.13 Reward Design
## 20.14 Dense vs Sparse Reward
## 20.15 Exploration
## 20.16 Goal-Conditioned RL
## 20.17 Hindsight Experience Replay
## 20.18 Hierarchical RL
## 20.19 Option
## 20.20 Model-Based RL
## 20.21 Model Bias
## 20.22 Offline RL
## 20.23 Extrapolation Error
## 20.24 Conservative Q Learning
## 20.25 IQL / Advantage-Weighted Regression
## 20.26 Demonstration + RL
## 20.27 Residual RL
## 20.28 Curriculum Learning
## 20.29 Locomotion RL
## 20.30 Dexterous RL
## 20.31 Real-World Online RL
## 20.32 Foundation Policy + Online RL
## 20.33 Experience Data Flywheel
## 20.34 Safe Exploration
## 20.35 Sim-to-Real RL
## 20.36 RL 与 Imitation 的统一视角
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 21　生成式动作模型与实时策略](./chapters/21-generative-action-real-time.md)

## 学习目标
## 21.1 为什么动作不是一个点
## 21.2 Action Distribution 与 Physical Feasibility
## 21.3 Autoregressive Action
## 21.4 Continuous Action Discretization
## 21.5 Token 序列长度
## 21.6 FAST 类 Action Tokenization
## 21.7 Diffusion Policy
## 21.8 为什么 Diffusion 适合 Robot Action
## 21.9 Observation Conditioning
## 21.10 Diffusion 的推理成本
## 21.11 3D Diffusion Policy
## 21.12 Flow Matching
## 21.13 Flow vs Diffusion
## 21.14 Continuous Action Expert
## 21.15 为什么 Separate Expert 有意义
## 21.16 Hybrid Discrete–Continuous
## 21.17 Action Chunking
## 21.18 Receding-Horizon Execution
## 21.19 Control Rate vs Model Rate
## 21.20 Chunk Boundary Problem
## 21.21 Temporal Ensembling
## 21.22 Trajectory Blending
## 21.23 Real-Time Action Chunking
## 21.24 Latency 是 State Variable
## 21.25 Asynchronous Inference
## 21.26 Double Buffer / Queue
## 21.27 Stale Observation
## 21.28 Action Semantics
## 21.29 Relative vs Absolute Action
## 21.30 Action Normalization
## 21.31 Sampling Temperature / Guidance
## 21.32 Candidate Sampling + Critic
## 21.33 Diffusion / Flow / AR 对比
## 21.34 评价指标
## 常见失败
## 研究问题
## 延伸阅读


---

# Volume V　机器人基础模型：从 VLM 到 VLA

# [Part 22　语言、多模态基础模型与 Physical Grounding](./chapters/22-language-vlm-grounding.md)

## 学习目标
## 22.1 为什么机器人需要语言
## 22.2 语言不是 Motor Command
## 22.3 Tokenization
## 22.4 Language Model Pretraining
## 22.5 Vision-Language Pretraining
## 22.6 VLM 的强项
## 22.7 VLM 的天然缺口
## 22.8 Grounding 的四层
## 22.9 Open-Vocabulary Detection / Segmentation
## 22.10 Referring Expression
## 22.11 Spatial Reasoning
## 22.12 Temporal Reasoning
## 22.13 Physical Reasoning
## 22.14 Affordance
## 22.15 SayCan 式分离
## 22.16 Language-Conditioned Policy
## 22.17 Language-Conditioned Planning
## 22.18 Tool Use
## 22.19 Internet Knowledge vs Embodied Knowledge
## 22.20 Physical Grounding 的在线性
## 22.21 VLM Hallucination
## 22.22 Language Ambiguity
## 22.23 Language Shortcut
## 22.24 Physical Vocabulary 是否应该离散
## 22.25 From VLM to Robot Foundation Model
## 常见失败
## 研究问题
## Source anchors / 原始来源

# [Part 23　VLA 的形成：2022–2024 的关键谱系](./chapters/23-vla-formation-2022-2024.md)

## 学习目标
## 23.1 什么才算 VLA
## 23.2 2022 前后的背景
## 23.3 Gato：Generalist Sequence Model
## 23.4 Gato 留下的问题
## 23.5 SayCan：语言知识 × Affordance
## 23.6 PaLM-E：把 Sensor Token 注入大模型
## 23.7 RT-1：规模化多任务 Robot Transformer
## 23.8 Tokenized Action
## 23.9 RT-2：Web Knowledge 进入 Action
## 23.10 RT-2 的真正科学问题
## 23.11 Semantic Generalization vs Physical Generalization
## 23.12 Open X-Embodiment
## 23.13 RT-X：跨机器人训练
## 23.14 Cross-Embodiment Data 的技术债
## 23.15 RoboCat：Self-Improvement 的早期信号
## 23.16 Octo：开放 Generalist Policy
## 23.17 Octo 的结构性选择
## 23.18 OpenVLA
## 23.19 2024 年形成的共同 VLA 模板
## 23.20 Robot Foundation Model 的定义逐渐变化
## 23.21 数据 vs 架构
## 23.22 一条压缩谱系
## 常见误读
## 最小研究练习
## 延伸来源
## 23.23 VLA 谱系的 Failure Taxonomy
## 23.24 最小受控实验：把“VLA 提升”拆开
## 23.25 Negative Controls
## 23.26 研究问题
## Source anchors / 原始来源

# [Part 24　VLA 的第二阶段：2024–2026 的架构分化](./chapters/24-vla-second-stage-2024-2026.md)

## 学习目标
## 24.1 π0：VLM + Flow-Matching Action Expert
## 24.2 FAST 与高效 Action Tokenization
## 24.3 π0.5：Open-World Generalization
## 24.4 π*0.6：从 Demonstration 走向 Experience / RL
## 24.5 π0.7：Steerability 与 Emergent Capability
## 24.6 GR00T N1：Humanoid Foundation Model
## 24.7 GR00T N1.5：Cross-Embodiment 与 Post-Training
## 24.8 GR00T N1.6：VLM、DiT 与 Loco-Manipulation 扩展
## 24.9 GR00T N1.7：新 VLM Backbone、Embodiment Tags 与部署栈
## 24.10 Gemini Robotics：VLA 与 Embodied Reasoning 分层
## 24.11 Gemini Robotics 1.5：Motion Transfer 与 Embodiment Adaptation
## 24.12 Gemini Robotics 2：Whole-Body VLA
## 24.13 Gemini Robotics On-Device 2：端侧推理与快速适配
## 24.14 Helix：On-Board、Multi-Rate 与 Whole-Body
## 24.15 开源 VLA 生态：OpenVLA / SmolVLA / LeRobot
## 24.16 3D-Aware / Point-Cloud-Aware VLA
## 24.17 Bimanual / Dexterous / Humanoid VLA
## 24.18 中国具身基础模型与开放生态
## 24.19 2026 VLA 的共同结构与真正分歧
## 问题 A：Scaling 到底带来什么？
## 问题 B：语义泛化会自动变成物理泛化吗？
## 问题 C：Whole-body 只是 action dimension 变大吗？
## 问题 D：所谓 emergent capability 如何证伪？

# [Part 25　VLA 的内部机制：它到底学到了什么](./chapters/25-vla-internal-mechanisms.md)

## 学习目标
## 25.1 一个最小 VLA 计算图
## 25.2 Vision Encoder：看见了什么
## 25.3 Language Backbone：语义先验如何进入动作
## 25.4 Proprioception Encoding
## 25.5 Multimodal Fusion
## 25.6 Knowledge Insulation 与 Gradient Interference
## 25.7 Action Expert / Head
## 25.8 State / Action Tokenization
## 25.9 Dataset Mixture 其实也是模型的一部分
## 25.10 Post-Training
## 25.11 Embodiment Conditioning
## 25.12 Low-Level Controller 没有消失
## 25.13 Latency、Chunking 与闭环频率
## 25.14 Language Following 与 Motor Precision 的张力
## 25.15 VLA Failure Taxonomy
## 25.16 VLA 是否学到了物理规律
## 最小实验：逐层冻结
## Source anchors / 原始来源

# [Part 26　机器人数据规模化、人类视频与 Cross-Embodiment](./chapters/26-robot-data-human-video-cross-embodiment.md)

## 26.1 为什么 Robot Data 是真正的瓶颈
## 26.2 数据到底是什么
## 26.3 Open X-Embodiment 的历史意义
## 26.4 DROID、Bridge 与真实机器人数据
## 26.5 Dataset Mixture
## 26.6 Data Curation
## 26.7 Success Data 与 Failure Data
## 26.8 Internet Image / Video Co-Training
## 26.9 Human Video 为什么重要
## 26.10 Human-to-Robot Transfer
## 26.11 Retargeting
## 26.12 Synthetic Trajectory
## 26.13 Neural-Generated Robot Data
## 26.14 Cross-Embodiment Representation
## 26.15 Morphology Encoding
## 26.16 Universal Action Representation
## 26.17 Motion Transfer
## 26.18 Few-Shot Embodiment Adaptation
## 26.19 Scale 与 Emergence
## 26.20 什么数据真正提高 Physical Generalization
## 最小实验：数据增量价值曲线
## Source anchors / 原始来源


---

# Volume VI　VLA 之后：推理、记忆、经验学习与世界模型

# [Part 27　Embodied Reasoning、Agentic Robotics 与长时程任务](./chapters/27-embodied-reasoning-agentic-robotics.md)

## 27.1 Reactive Policy 的极限
## 27.2 Goal Representation
## 27.3 Skill / Primitive / Option
## 27.4 Task Decomposition
## 27.5 Hierarchical Policy
## 27.6 Language Planner + Motor Policy
## 27.7 Embodied Reasoning Model
## 27.8 Spatial / Temporal / Physical Reasoning
## 27.9 Tool Use 与 Skill Calling
## 27.10 Long-Horizon Planning
## 27.11 Online Replanning
## 27.12 Progress Monitoring
## 27.13 Error Detection
## 27.14 Recovery
## 27.15 Human Clarification / Intervention
## 27.16 Steerability
## 27.17 Chain-of-Thought 的证据问题
## 27.18 Agentic Orchestration vs End-to-End
## 最小实验：Reasoning 是否有因果作用
## Source anchors / 原始来源

# [Part 28　机器人记忆：从 Context Window 到 Lifelong Memory](./chapters/28-robot-memory-lifelong-context.md)

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
## 28.14 Memory 对 10+ Minute Task 的意义
## 最小实验：记忆的必要性曲线
## Source anchor
## 28.15 Memory Failure Taxonomy
## 28.16 研究问题

# [Part 29　从 Demonstration 到 Experience：机器人如何继续学习](./chapters/29-learning-from-experience-deployment.md)

## 29.1 固定模型范式的问题
## 29.2 为什么 Imitation 不能解决所有 Precision 问题
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
## 29.17 从“训练好的模型”到“会积累经验的机器人”
## 最小实验：Demonstration vs Experience

# [Part 30　World Models 与 Predictive Intelligence](./chapters/30-world-models-predictive-intelligence.md)

## 30.1 World Model 到底是什么
## 30.2 State-Space Dynamics Model
## 30.3 Latent Dynamics
## 30.4 Object-Centric Dynamics
## 30.5 Video Prediction
## 30.6 Action-Conditioned Video Prediction
## 30.7 Pixel-Space vs Latent-Space
## 30.8 JEPA：Predict Representation, Not Pixels
## 30.9 V-JEPA 2
## 30.10 V-JEPA 2.1
## 30.11 Latent Action-Conditioned World Model
## 30.12 3D / 4D World Model
## 30.13 Contact-Aware World Model
## 30.14 Tactile World Model
## 30.15 Counterfactual Prediction
## 30.16 Uncertainty-Aware Prediction
## 30.17 Learned / Neural Simulator
## 30.18 Foundation World Model
## 30.19 World Model + MPC
## 30.20 World Model + Policy Search
## 30.21 World Model + Evaluator
## 30.22 会生成未来视频 ≠ 理解物理规律
## 30.23 如何证明 World Model 真正提高行动能力

# [Part 31　生成式世界、视频模型与 Physical Simulation Foundation Models](./chapters/31-generative-worlds-video-physical-ai.md)

## 31.1 为什么 Video Generation 进入 Robotics
## 31.2 Internet Video 里的物理先验
## 31.3 Actionable Video Representation
## 31.4 Image-to-Video / Text-to-Video 用于 Data Augmentation
## 31.5 Video-to-Action 与 Inverse Dynamics
## 31.6 Latent Action Model
## 31.7 Generative World Simulator
## 31.8 Cosmos 类 Physical AI World Foundation Model
## 31.9 Synthetic Scene / Trajectory Generation
## 31.10 Video Model 与 Physics Engine 的互补
## 31.11 Neural Simulator 的可靠性边界
## 31.12 从“看起来真实”到“控制上有用”
## 31.13 World Action Model：World 与 Action 开始融合
## 最小实验：视频逼真度与控制效用是否相关


---

# Volume VII　操作、导航、灵巧与人形

# [Part 32　机器人操作：从抓取到长时程任务](./chapters/32-robot-manipulation.md)

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
## Source anchors / 原始来源

# [Part 33　双臂、灵巧手与触觉智能](./chapters/33-bimanual-dexterity-tactile-intelligence.md)

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
## 33.18 Bimanual / Dexterous Failure Taxonomy
## 33.19 研究问题
## Source anchors / 原始来源

# [Part 34　移动机器人、导航与 Embodied Navigation](./chapters/34-mobile-embodied-navigation.md)

## 34.1 Mobile Base
## 34.2 Localization
## 34.3 Mapping
## 34.4 Global / Local Navigation
## 34.5 Obstacle Avoidance
## 34.6 Exploration
## 34.7 Active Mapping
## 34.8 Visual Navigation
## 34.9 PointNav / ObjectNav
## 34.10 Vision-Language Navigation
## 34.11 Embodied Question Answering
## 34.12 Semantic Navigation
## 34.13 Navigation + Manipulation
## 34.14 Home / Office / Warehouse
## 34.15 Habitat / BEHAVIOR / OmniGibson
## 34.16 Drone / Field Robot / Autonomous Vehicle
## 34.17 Navigation Failure Taxonomy
## 34.18 Navigation 的完整闭环接口
## 34.19 研究问题
## Source anchors / 原始来源

# [Part 35　Legged Locomotion、Humanoid 与 Whole-Body Intelligence](./chapters/35-humanoid-whole-body-intelligence.md)

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
## 35.14 SONIC：Scaling Humanoid Motion Tracking
## 35.15 Whole-Body Control
## 35.16 Loco-Manipulation
## 35.17 Humanoid Manipulation
## 35.18 Whole-Body VLA
## 35.19 Fall Detection / Recovery
## 35.20 Energy、Speed 与 Reliability
## 35.21 从 Tabletop 到 Feet-to-Fingertips
## 35.22 General-Purpose Humanoid 的现实瓶颈

# [Part 36　Human–Robot Interaction 与 Multi-Robot Intelligence](./chapters/36-human-robot-multi-robot-intelligence.md)

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
## Source anchors / 原始来源


---

# Volume VIII　持续学习、跨本体与发展型智能

# [Part 37　Cross-Embodiment Intelligence](./chapters/37-cross-embodiment-intelligence.md)

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
## 37.13 新身体的 Calibration / Adaptation
## 37.14 “一个 Checkpoint 控不同机器人”意味着什么
## 37.15 Cross-Embodiment 的真正上限
## 37.19 Cross-Embodiment Failure Taxonomy
## 37.20 研究问题
## Source anchors / 原始来源

# [Part 38　Continual、Lifelong 与 Developmental Robot Learning](./chapters/38-continual-lifelong-developmental-learning.md)

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
## 38.19 从 Fixed Model 到 Developing Agent
## 38.23 Continual Learning Failure Taxonomy
## 38.24 研究问题
## Source anchors / 原始来源

# [Part 39　Self-Evolving Physical Intelligence](./chapters/39-self-evolving-physical-intelligence.md)

## 39.1 自进化必须满足什么可证伪条件
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
## 一套可量化的“成长”指标
## 最小长期实验
## 39.19 最小实验：结构生长必须赢过等预算静态模型
## 39.20 研究问题
## Source anchors / 原始来源


---

# Volume IX　仿真、数据基础设施与系统工程

# [Part 40　Physics Simulation 与 Robot Learning Platform](./chapters/40-physics-simulation-robot-platforms.md)

## 40.1 为什么机器人研究离不开 Simulation
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
## 40.18 Determinism 与 Versioning
## 40.19 Benchmark Platform 与研究问题错位
## Source anchors / 原始来源

# [Part 41　Synthetic Data、Domain Randomization 与 Sim-to-Real](./chapters/41-synthetic-data-sim2real.md)

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
## 41.13 Reality Gap 分解
## 41.14 哪些能力适合在 Simulation 学
## 41.15 Transfer Gap 不应只报一个数字
## 41.16 Sim2Real 常见失败
## 41.17 研究问题
## Source anchors / 原始来源

# [Part 42　机器人数据工程](./chapters/42-robot-data-engineering.md)

## 42.1 Data Collection System
## 42.2 Teleoperation Hardware
## 42.3 Episode Lifecycle
## 42.4 Timestamp 与 Synchronization
## 42.5 Multi-Modal Alignment
## 42.6 Compression / Storage / Streaming
## 42.7 HDF5 / Parquet / RLDS / LeRobot Formats
## 42.8 Metadata
## 42.9 Annotation
## 42.10 Quality Control
## 42.11 Duplicate / Leakage Detection
## 42.12 Failure Data
## 42.13 Dataset Versioning
## 42.14 Dataset Mixture
## 42.15 Massive Robot Corpora Data Loader
## 42.16 Distributed Storage
## 42.17 Governance / Privacy
## 42.18 Robotics Data Flywheel
## 42.19 Dataset Contract：数据也需要可执行规范
## 42.20 数据价值不等于 Episode 数量
## 42.21 最小实验：Data QA 能否提前发现训练灾难
## 42.22 研究问题
## Source anchors / 原始来源

# [Part 43　机器人系统工程与真实部署](./chapters/43-robot-systems-deployment.md)

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
## 43.14 Quantization / Compilation
## 43.15 Network Latency
## 43.16 Async Pipeline
## 43.17 Safety Monitor
## 43.18 Logging / Replay
## 43.19 Experiment Reproducibility
## 43.20 Distributed Training
## 43.21 Model Serving for Robots
## 43.22 一次真实 Rollout 到底发生了什么
## 43.25 最小部署实验：把 latency 当成可控变量
## 43.26 研究问题
## Source anchors / 原始来源


---

# Volume X　评测、可靠性与安全

# [Part 44　Datasets、Benchmarks 与 Evaluation Science](./chapters/44-benchmarks-evaluation-science.md)

## 学习目标
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
## 44.12 Bernoulli Uncertainty 与 Confidence Interval
## 44.13 Partial Credit / Progress Metric
## 44.14 Robustness
## 44.15 Generalization Matrix
## 44.16 Object / Scene / Task / Embodiment OOD
## 44.17 Perturbation Test
## 44.18 Long-Horizon Evaluation
## 44.19 Intervention Rate
## 44.20 Recovery Rate
## 44.21 Latency / Throughput / Energy
## 44.22 Calibration / Uncertainty
## 44.23 Benchmark Leakage
## 44.24 Paired Evaluation 与 Seed Control
## 44.25 多 Seed 不等于大量独立样本
## 44.26 Model × Data × System × Protocol
## 44.27 “成功视频”为什么不是科学证据
## 44.28 Evaluation Dataflow
## 常见失败
## 研究问题
## Source anchors / 原始来源
## 一个推荐的统一评测向量

# [Part 45　可靠性、Safety 与 Human Intervention](./chapters/45-reliability-safety-human-intervention.md)

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
## 45.17 从 70% Success 到可部署系统
## 45.18 Safety 与 Capability 为什么不能分开
## Safety Case
## Source anchors / 原始来源


---

# Volume XI　研究方法、理论前沿与下一代具身智能

# [Part 46　如何做严谨的具身智能研究](./chapters/46-rigorous-embodied-ai-research.md)

## 46.1 怎样读一篇具身论文
## 46.2 怎样画完整 System Diagram
## 46.3 Observation → Representation → Action
## 46.4 复现论文而不只是跑通代码
## 46.5 怎样设计 Baseline
## 46.6 怎样设计 Ablation
## 46.7 怎样构造 Negative Control
## 46.8 怎样控制 Data Gain
## 46.9 Architecture Gain vs Data Gain
## 46.10 可证伪 Hypothesis
## 46.11 Failure Taxonomy
## 46.12 Mechanism Analysis
## 46.13 统计可信度
## 46.14 防 Benchmark Overfitting
## 46.15 如何报告真实机器人实验
## 46.16 从 Failure Mode 产生问题
## 46.17 判断 VLA 是否真的 Generalize
## 46.18 判断 World Model 是否被 Policy 利用
## 46.19 判断视觉表征是否服务物理交互
## 46.20 判断 Reasoning 是否只是语言包装
## 一页 Research Protocol
## Source anchors / 原始来源

# [Part 47　Transformer 在具身智能中的作用与边界](./chapters/47-transformer-role-and-limits.md)

## 47.1 Transformer 真正解决了什么
## 47.2 Attention 的优势与代价
## 47.3 Sequence Model 是否等于 Dynamics Model
## 47.4 Tokenization 对物理连续性的破坏
## 47.5 Fixed Context 与 Persistent World
## 47.6 Reactive Transformer 与 Closed-Loop Control
## 47.7 Transformer + External Controller
## 47.8 Transformer + Memory
## 47.9 Transformer + World Model
## 47.10 Transformer + Structural Module
## 47.11 State-Space / Recurrent Model 的重新价值
## 47.12 Graph / Object-Centric / Geometry-Centric Architecture
## 47.13 Continuous-Time Architecture
## 47.14 Modular / Hierarchical Architecture
## 47.15 Transformer 之后真正值得问的问题
## 47.19 Transformer-Induced Failure Taxonomy
## 47.20 研究问题
## Source anchors / 原始来源

# [Part 48　数学化具身智能：从相关性到结构与规律](./chapters/48-mathematical-embodied-intelligence.md)

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
## 最小实验：规律还是记忆
## 48.21 数学化失败：公式多不等于机制清楚
## 48.22 研究问题
## Source anchors / 原始来源

# [Part 49　开放问题：截至 2026-09 的真正前沿](./chapters/49-open-frontiers-2026-09.md)

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
## 49.22 General-Purpose Humanoid 是终局吗
## 49.23 是否需要新的计算范式
## 49.24 什么才算“理解了物理世界”
## 49.25 距离真正通用智能还有什么
## Source anchors / 原始来源

# [Part 50　从学习者到独立研究者](./chapters/50-from-learner-to-independent-researcher.md)

## 50.1 第一阶段：数学与经典机器人学底座
## 50.2 第二阶段：亲手实现 Perception / Planning / Control
## 50.3 第三阶段：Imitation / RL / Generative Policy
## 50.4 第四阶段：复现主流 VLA
## 50.5 第五阶段：拆 Failure Mechanism
## 50.6 第六阶段：进入真正前沿
## 50.7 第七阶段：Architecture Research Program
## 50.8 从“追论文”转向“追问题”
## 50.9 如何形成持续科研飞轮
## 50.10 如何提出一个值得做三年的问题
## Year / Stage A：基础
## Stage B：Robot Learning
## Stage C：Foundation Models
## Stage D：Mechanism Research
## Stage E：Independent Program
## 全书结束语
## 50.18 独立研究的最小闭环
## 50.19 研究问题
## Source anchors / 原始来源

---

# Appendices　附录系统

- [Appendix A–Z：公式、系统、平台、Atlas 与 Checklists](./APPENDICES.md)
- [中英术语表](./GLOSSARY.md)
- [符号、坐标系与 Action Convention](./NOTATION_AND_CONVENTIONS.md)
- [30 组核心推导](./DERIVATIONS.md)
- [204 道章末题](./EXERCISES.md)
- [解题要点](./SOLUTION_SKETCHES.md)
- [36 周系统课程](./SYLLABUS_36_WEEKS.md)
- [概念索引](./CONCEPT_INDEX.md)
- [知识依赖图](./DEPENDENCY_GRAPH.md)

---

# 目录维护规则

1. `book/chapters/` 是正文与编号的唯一真源；
2. `book/TOC.md` 由 `scripts/generate_toc.py` 自动生成；
3. 新模型原则上进入现有 Part 的案例 / Atlas，而不是自动新增 Part；
4. 只有出现新的基本数学对象、训练范式或 physical-system interface，才考虑改变 Part 级骨架；
5. 每次前沿更新保留明确 snapshot 日期。
