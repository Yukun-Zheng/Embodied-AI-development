# Volume II　机器人身体、几何、力学与控制

> 现代 VLA 不会使经典机器人学失效。任何神经策略最终都要穿过同一条物理链：action representation → kinematics/dynamics → actuator → contact → sensor feedback。本卷建立这条链。

---

# Part 6　机器人身体与机电系统

## 6.1 Degree of Freedom

自由度（DOF）是描述系统 configuration 所需的独立广义坐标数。一个空间刚体有 6 DOF：3 平移 + 3 旋转。一个典型 7-DOF 机械臂用

\[
q=[q_1,\ldots,q_7]^\top
\]

描述关节 configuration。

DOF 与 actuator 数量不同：欠驱动系统 actuator 少于 DOF；闭链系统虽然有多个关节，但约束会降低独立 DOF。

## 6.2 Link、Joint 与 Kinematic Chain

机器人由刚体 link 通过 joint 连接。常见关节：

- revolute：\(q_i=\theta_i\)；
- prismatic：\(q_i=d_i\)；
- spherical：多轴旋转；
- floating base：人形/四足基座常以 6-DOF floating joint 表示。

serial chain 的变换逐级相乘；parallel / closed-chain 则必须满足额外 loop constraint。

## 6.3 Actuator 不是“action”

学习策略输出的 action 可能是：

- joint position target；
- joint velocity target；
- joint torque；
- end-effector pose delta；
- whole-body target；
- latent skill。

但真正执行器接收的通常仍是电流、力矩或底层 servo setpoint。因此应明确三层：

```text
policy action
    ↓
robot command / controller target
    ↓
servo / drive command
    ↓
current → torque → motion
```

论文只写“action dimension = 7”而不说明这一链，往往不足以复现实验。

## 6.4 Motor、Gearbox 与 Backdrivability

电机近似有

\[
\tau_m=k_t i.
\]

减速器将速度换成力矩；理想情况下减速比 \(N\) 给出

\[
\tau_{out}\approx N\tau_m,
\qquad
\omega_{out}\approx \omega_m/N.
\]

但真实系统有摩擦、回差、效率损失和柔性。高减速比带来大力矩却降低 backdrivability；quasi-direct drive 则用更低减速比换取高动态和力控质量。

## 6.5 Position / Velocity / Torque Interface

**Position control** 易用稳定，但会隐藏真实力学；**velocity control** 直接控制运动速度；**torque control** 最接近动力学层，适合 impedance / whole-body control，但对模型、传感和安全要求更高。

因此比较两篇学习论文时，必须确认它们是否使用了同一种底层控制接口。

## 6.6 Stiffness、Compliance、Impedance

机械 stiffness 近似

\[
F=K\Delta x.
\]

高 stiffness 精确但碰撞危险；低 stiffness 安全但位置误差大。机器人接触任务的核心并非“位置跟得最精确”，而是**适当控制位置与力的关系**。

## 6.7 Power、Thermal 与 Battery

真实机器人能力受能量和热约束：

\[
P=\tau^\top\dot q.
\]

长时高力矩可能触发温度保护；快速 humanoid locomotion 受瞬时功率与电池放电能力限制。训练时若忽略这些限制，仿真策略可能在真机不可执行。

## 6.8 Embedded Compute 与实时网络

现代机器人常是多计算机系统：MCU/servo drive 负责高速环，CPU 负责 middleware，GPU 负责 perception/VLA。EtherCAT、CAN 等总线决定控制周期、同步与 jitter。

因此“模型 20 Hz”不等于整个机器人 20 Hz。真实系统可能是：

```text
Motor current loop      10–40 kHz
Joint servo              0.5–2 kHz
State estimator          100–1000 Hz
Whole-body controller    100–500 Hz
Vision                    15–60 Hz
VLA / planner              1–30 Hz
```

## 6.9 Robot Description

URDF、MJCF、USD 都在描述身体，但服务对象不同。核心字段包括 link、joint、collision geometry、visual geometry、mass、inertia、limit、actuator/sensor。一个 robot description 的错误惯量或关节轴会让后续仿真完全失真。

---

# Part 7　空间、旋转与刚体几何

## 7.1 Coordinate Frame

设 \(\{A\}\)、\(\{B\}\) 为两个 frame。符号约定必须先固定：

\[
{}^A T_B
\]

表示把 B-frame 坐标表达转换到 A-frame。

若点在 B 中坐标为 \({}^Bp\)，则齐次坐标下

\[
\begin{bmatrix}{}^Ap\\1\end{bmatrix}
={}^{A}T_B
\begin{bmatrix}{}^Bp\\1\end{bmatrix}.
\]

## 7.2 Rotation Matrix 与 SO(3)

\[
R\in SO(3),\qquad R^TR=I,\ \det R=1.
\]

若 \({}^AR_B\) 表示 B 在 A 中的朝向，那么

\[
{}^Av={}^AR_B\,{}^Bv.
\]

逆旋转就是转置：

\[
R^{-1}=R^T.
\]

## 7.3 Euler、Axis-Angle、Quaternion

Euler angle 易读但存在顺序歧义和 gimbal lock。Axis-angle 用单位轴 \(\omega\) 与角度 \(\theta\)。Quaternion

\[
q=[w,x,y,z],\qquad \|q\|=1
\]

无 gimbal lock，适合插值和数值计算，但 \(q\) 与 \(-q\) 表示同一旋转，训练损失必须处理 double cover。

## 7.4 Homogeneous Transform 与 SE(3)

\[
T=
\begin{bmatrix}
R&p\\0&1
\end{bmatrix}
\in SE(3).
\]

变换复合：

\[
{}^AT_C={}^AT_B{}^BT_C.
\]

逆：

\[
T^{-1}=
\begin{bmatrix}
R^T&-R^Tp\\0&1
\end{bmatrix}.
\]

## 7.5 Lie Algebra、Hat 与 Exponential Map

角速度 \(\omega\in\mathbb R^3\) 的 hat：

\[
\hat\omega=
\begin{bmatrix}
0&-\omega_3&\omega_2\\
\omega_3&0&-\omega_1\\
-\omega_2&\omega_1&0
\end{bmatrix}.
\]

Rodrigues 公式：

\[
R=e^{\hat\omega\theta}
=I+\sin\theta\hat\omega+(1-\cos\theta)\hat\omega^2.
\]

SE(3) 的 twist

\[
\xi=\begin{bmatrix}v\\\omega\end{bmatrix}\in\mathbb R^6
\]

通过 matrix exponential 生成刚体运动。

## 7.6 Spatial / Body Velocity

同一刚体速度可用 space frame 或 body frame 表达：

\[
V_s=\operatorname{Ad}_T V_b.
\]

Adjoint 对 \(T=[R,p;0,1]\)：

\[
\operatorname{Ad}_T=
\begin{bmatrix}
R&\hat pR\\0&R
\end{bmatrix}
\]

（具体块顺序随 twist convention 改变，因此代码中必须固定 \([v,\omega]\) 或 \([\omega,v]\)）。

## 7.7 Wrench

wrench 合并 force 与 torque：

\[
W=\begin{bmatrix}f\\\tau\end{bmatrix}.
\]

速度与 wrench 的变换必须保持瞬时功率不变：

\[
P=W^T V.
\]

由此可推导 wrench 使用 inverse-transpose adjoint 变换。

## 7.8 Convention 灾难清单

最常见的工程事故：

- world-to-camera 与 camera-to-world 反了；
- quaternion 顺序 `wxyz` / `xyzw` 混淆；
- Euler `XYZ` / `ZYX` 混淆；
- active / passive rotation 混淆；
- column vector / row vector convention 混淆；
- left-handed / right-handed frame 混淆；
- delta pose 是 local frame 还是 world frame 未说明。

任何实验记录都应打印 frame tree 与单位测试，而不是靠“看起来差不多”。

---

# Part 8　机器人运动学

## 8.1 Forward Kinematics

给定 joint configuration \(q\)，求末端 pose：

\[
T_{ee}=FK(q).
\]

对 serial chain，可直接逐节相乘，也可用 Product of Exponentials：

\[
T(q)=e^{[S_1]q_1}\cdots e^{[S_n]q_n}M.
\]

这里 \(S_i\) 是 screw axis，\(M\) 是 home configuration。

## 8.2 Jacobian

微分关系：

\[
V=J(q)\dot q.
\]

Jacobian 的列向量表示“只让第 i 个关节以单位速度运动时，末端瞬时产生什么 twist”。这比把 Jacobian 当成偏导矩阵更重要。

## 8.3 Singularity

若 \(J\) rank 降低，某些 Cartesian 速度方向无法产生。接近 singularity 时：

- IK 数值不稳定；
- joint velocity 可能爆炸；
- force transmission 特性恶化。

因此 learning policy 若直接预测 Cartesian delta pose，也不能无视当前 configuration 的可实现性。

## 8.4 Inverse Kinematics

目标：给定 \(T_d\) 求 \(q\)。数值 IK 常迭代：

\[
q_{k+1}=q_k+J^+(q_k)e_k.
\]

DLS、joint limit、collision constraint 会形成更现实的 constrained IK。

## 8.5 Redundancy 与 Null Space

对冗余机器人：

\[
\dot q=J^+V_d+(I-J^+J)z.
\]

第一项完成末端任务，第二项在 null space 中优化 secondary objective，例如远离 joint limit：

\[
z=-k\nabla_q c(q).
\]

## 8.6 Trajectory

从 \(q_0\) 到 \(q_f\) 不能只“瞬移 target”。常用 cubic / quintic polynomial 约束起终点位置、速度、加速度。

Cartesian trajectory 还必须在 \(SE(3)\) 上正确插值；位置可线性插值，旋转应使用 geodesic / slerp 等方式。

## 8.7 Bimanual Kinematics

双臂任务常关心相对 pose：

\[
{}^{L}T_R=({}^{W}T_L)^{-1}{}^{W}T_R.
\]

例如双手共同搬物体时，相对约束可能比各自 world-frame target 更关键。所谓 coordinated frame 的目的就是把两臂任务转换到共同任务坐标。

## 8.8 Whole-Body Kinematics

人形 floating base + 四肢构成多链系统。任务往往同时包括：

- hand pose；
- foot contact；
- center-of-mass；
- gaze；
- posture；
- collision avoidance。

这自然导向 hierarchical IK / QP，而不是单个 end-effector IK。

---

# Part 9　动力学、接触与抓取

## 9.1 Manipulator Equation

刚体机器人动力学核心式：

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)+\tau_f
=\tau+J^T(q)F_{ext}.
\]

其中：

- \(M(q)\)：mass matrix；
- \(C\dot q\)：Coriolis / centrifugal；
- \(g(q)\)：gravity；
- \(\tau_f\)：friction；
- \(\tau\)：actuator torque；
- \(J^TF_{ext}\)：外部末端 wrench 映射到 joint torque。

这条式子是“action 怎样变成 motion”的物理核心。

## 9.2 Lagrangian Derivation

\[
L(q,\dot q)=K(q,\dot q)-U(q).
\]

Euler–Lagrange：

\[
\frac{d}{dt}\frac{\partial L}{\partial\dot q_i}
-\frac{\partial L}{\partial q_i}=\tau_i.
\]

Newton–Euler 更适合递归计算；Lagrangian 更适合理解能量结构。

## 9.3 Forward / Inverse Dynamics

Forward dynamics：

\[
\ddot q=M^{-1}(\tau-C\dot q-g+\cdots).
\]

Inverse dynamics：给定 \(q,\dot q,\ddot q_d\) 求所需 \(\tau\)。computed torque control 就直接使用 inverse dynamics 补偿。

## 9.4 Contact Constraint

若接触要求某方向相对加速度为零，可写

\[
J_c\ddot q+\dot J_c\dot q=0.
\]

动力学加入 contact force：

\[
M\ddot q+h=\tau+J_c^T\lambda.
\]

求 \(\ddot q,\lambda\) 就形成 constrained dynamics。

## 9.5 Friction Cone

Coulomb friction：

\[
\|f_t\|\le \mu f_n.
\]

三维中允许摩擦力形成 cone；优化器常以多面体近似 friction pyramid。抓取是否稳定，很大程度取决于接触 wrench 是否能落在这些 cone 的组合内。

## 9.6 Complementarity

刚性单边接触满足：

\[
\phi(q)\ge0,\quad \lambda_n\ge0,\quad \phi(q)\lambda_n=0.
\]

即物体不能穿透、法向力不能拉物体、只有真正接触时才有法向力。contact solver 之所以难，正是因为这种非光滑约束。

## 9.7 Grasp Map

多个接触力 \(f_c\) 映射到物体 wrench：

\[
w=Gf_c.
\]

若在摩擦约束下可以抵抗任意小外部 wrench，则形成 force closure。抓取不是“夹爪点碰到物体”，而是接触集合能否生成所需 wrench space。

## 9.8 COM、ZMP、Capture Point

腿式机器人必须管理重心与支撑面。经典 ZMP 要求地面反力合力矩条件满足稳定支撑；Linear Inverted Pendulum 给出简化动力学。Capture Point 近似描述系统为了不倒下应该把脚落在哪里。

现代 RL locomotion 可以不显式输出 ZMP，但这些物理变量仍解释策略为什么稳定或失败。

## 9.9 Deformable Objects

衣物、绳索、软包装不再满足少量刚体 state 的假设。状态维数巨大、接触拓扑变化、材料参数难辨识。因此 cloth folding / cable manipulation 常成为检验 world model 与视觉 representation 的强测试。

## 9.10 Simulation Physics 只是近似

仿真器必须在：精度、稳定性、速度之间折中。接触 stiffness、friction regularization、solver iteration、time step 都会改变行为。所谓 sim-to-real gap 很大部分来自

\[
\hat f_{sim}(x,u)\ne f_{real}(x,u).
\]

不要把“PhysX/MuJoCo 中成功”误解为物理定律证明。

---

# Part 10　反馈控制、最优控制与 Whole-Body Control

## 10.1 PID

误差 \(e=r-y\)：

\[
u=K_Pe+K_I\int e\,dt+K_D\dot e.
\]

P 产生恢复力，I 消除稳态偏差，D 提供阻尼。PID 简单却仍遍布工业机器人。

## 10.2 Computed Torque

利用动力学补偿：

\[
\tau=M(q)v+C(q,\dot q)\dot q+g(q),
\]

其中

\[
v=\ddot q_d+K_D(\dot q_d-\dot q)+K_P(q_d-q).
\]

若模型准确，闭环近似变成线性二阶系统。

## 10.3 Impedance Control

希望末端表现成虚拟质量-弹簧-阻尼：

\[
M_d\ddot e+D_d\dot e+K_de=F_{ext}.
\]

接触任务中，目标不是死守位置，而是规定“受到外力时应该怎样让步”。

## 10.4 Admittance Control

与 impedance 相反，admittance 从外力生成参考运动。对本身位置控制很强的工业臂，可在外层根据力传感器计算位姿偏移。

## 10.5 Operational Space Control

在 task space 直接设计动力学：

\[
F=\Lambda(q)\ddot x_d+\mu(q,\dot q)+p(q),
\]

再通过

\[
\tau=J^TF
\]

映射到关节。它是“直接控制手的任务动力学”的经典方法。

## 10.6 Force / Hybrid Control

装配任务常有方向分工：沿表面切向控制位置，法向控制力。hybrid position/force control 通过 selection matrix 把 task space 分解。

## 10.7 LQR

线性系统

\[
x_{t+1}=Ax_t+Bu_t
\]

代价

\[
J=\sum x_t^TQx_t+u_t^TRu_t
\]

得到最优反馈

\[
u_t=-Kx_t.
\]

LQR 重要不在于只能解线性问题，而在于展示“预测动力学 + 未来代价 → feedback gain”的结构。

## 10.8 iLQR / DDP

对非线性 dynamics 和 cost，沿当前轨迹局部线性/二次化，反向计算 value approximation，再前向 rollout 更新 trajectory。它们连接 trajectory optimization 与 feedback control。

## 10.9 MPC

每个时刻：

1. 估计当前 state；
2. 预测未来 \(H\) 步；
3. 解 constrained optimal control；
4. 只执行第一步；
5. 重复。

这与现代 action-chunk policy 的 receding horizon 思想高度相似，只是优化器被学习模型替代或辅助。

## 10.10 Whole-Body Control

人形同时有多个任务。QP 形式可写：

\[
\min_{\ddot q,\tau,\lambda}
\sum_i w_i\|J_i\ddot q+\dot J_i\dot q-a_i^*\|^2
\]

subject to rigid-body dynamics、contact、friction cone、torque/joint limit。

Hierarchical QP 进一步保证高优先级任务严格压过低优先级任务。

## 10.11 Control Barrier Function

安全集合

\[
\mathcal C=\{x:h(x)\ge0\}.
\]

若控制保证

\[
\dot h(x,u)+\alpha(h(x))\ge0,
\]

则可使系统保持在安全集合中。CBF 可作为 learning policy 外层的 safety filter。

## 10.12 高频反射与低频智能

一个实用的 foundation-robot architecture 通常不会让 VLA 直接 1 kHz 输出 motor current。更合理的是：

```text
1–10 Hz      reasoning / task goal
5–30 Hz      VLA / learned action chunk
50–200 Hz    IK / WBC / impedance target update
500–2000 Hz  joint servo
10 kHz+      drive current loop
```

这不是“端到端不纯”，而是符合不同动态时间尺度。

---

# Part 11　运动规划、任务规划与不确定决策

## 11.1 Configuration Space

机器人 configuration \(q\) 的集合构成 C-space。障碍物在工作空间中映射成 C-space obstacle：

\[
\mathcal C_{free}=\mathcal C\setminus\mathcal C_{obs}.
\]

运动规划变成在 \(\mathcal C_{free}\) 中找连续路径。

## 11.2 Graph Search

Dijkstra 在非负边权图上给最短路；A* 使用 heuristic：

\[
f(n)=g(n)+h(n).
\]

若 \(h\) admissible，则仍能保证最优。机器人 task planner、grid navigation 都大量使用。

## 11.3 PRM / RRT / RRT*

高维 C-space 很难网格化。sampling-based planner 通过采样 free configuration 建图/树。RRT 擅长快速探索；RRT* 在条件下 asymptotically optimal。

## 11.4 Kinodynamic Planning

若不能任意连接两个 configuration，而必须满足 dynamics：

\[
\dot x=f(x,u),
\]

规划就必须同时考虑状态与控制。例如高速无人机、车辆、人形不能把“几何可达”当成“动力学可达”。

## 11.5 Trajectory Optimization

直接优化离散轨迹：

\[
\min_{x_{0:T},u_{0:T-1}} J
\]

subject to dynamics、collision、joint limit。CHOMP 利用 functional gradient；STOMP 使用 stochastic sampling；TrajOpt 类方法把碰撞约束纳入连续优化。

## 11.6 Task and Motion Planning

任务“把杯子放进柜子”包含离散选择（抓哪个杯子、开哪扇门、先做什么）与连续可行性（机械臂是否够得到、有没有碰撞）。TAMP 尝试把 symbolic plan 与 geometric feasibility 联合。

## 11.7 Planning under Uncertainty

若 state 不确定，planner 应在 belief space 中规划。一个动作可能不是直接接近目标，而是先降低不确定性。这就是 active perception 与 planning 连接的位置。

## 11.8 Classical Planner 与 Learned Policy

两者不是非此即彼。

- classical planner：约束清晰、可验证、组合结构强；
- learned policy：适合高维感知、复杂接触和难建模 dynamics；
- hybrid：高层 planner / reasoning 给 subgoal，learned skill 执行，低层 controller 保证物理稳定。

2025–2026 的 embodied reasoning + VLA 分层正重新体现这种 hybrid 结构。

---

# 本卷统一数据流

```text
Task goal
   ↓
Task / motion planner
   ↓  desired pose / trajectory / skill
Kinematics + collision constraints
   ↓
WBC / impedance / MPC
   ↓  joint targets / torques
Actuator + drivetrain
   ↓
Rigid-body/contact dynamics
   ↓
Physical motion
   ↓
Sensors → state estimation → feedback
```

学习模型可以替换或增强其中多个模块，但不能绕开这条因果链。

## 必做实验

1. 手算并代码验证 2-link FK / Jacobian / singularity；
2. 用 pseudoinverse 与 DLS 做同一 IK，比较奇异附近行为；
3. 仿真 PD 与 computed-torque controller；
4. 对同一接触任务比较 position control 与 impedance control；
5. 实现 A*、RRT 和 trajectory optimization；
6. 构造一个简单 QP whole-body task；
7. 改变 simulator timestep / friction，观察策略或 controller 的行为变化。

## 推荐资料

- Lynch & Park, *Modern Robotics* — https://modernrobotics.northwestern.edu/
- Siciliano et al., *Robotics: Modelling, Planning and Control*.
- Spong, Hutchinson & Vidyasagar, *Robot Modeling and Control*.
- Tedrake, *Underactuated Robotics*.
- LaValle, *Planning Algorithms*.
- Khatib, operational-space control papers.
