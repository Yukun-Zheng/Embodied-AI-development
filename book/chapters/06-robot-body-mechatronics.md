# Part 6　机器人身体、执行器与机电系统

## 学习目标

理解一个学习策略输出以后，命令如何穿过 robot interface、servo、motor、gearbox 变成真实力矩；理解 DOF、actuation、compliance、power、thermal、communication 为什么会决定算法上限。

---

## 6.1 Degree of Freedom

自由度是描述 configuration 所需的独立广义坐标数：

\[
q=[q_1,\ldots,q_n]^T.
\]

空间刚体有 6 DOF，但一个 articulated robot 的 DOF 由 joint 与 constraint 决定。DOF 不等于 motor 数量：欠驱动手可以 10+ joint 只有较少 actuator；闭链结构会通过 constraint 降低独立自由度。

## 6.2 Joint 与 Link

最基本关节：revolute 与 prismatic。现实机器人还有 spherical、planar、mimic、tendon/coupled joints。人形常有 floating base：基座在世界中有 6 DOF，却没有直接“控制 base pose”的 actuator。

这一区别很关键：RL policy 输出所有 joint target，不代表它能独立指定 base motion；base 由接触力间接控制。

## 6.3 Actuator Chain

神经策略的 `action` 与 motor command 之间通常还有多层：

```text
policy action
  ↓
robot API target
  ↓
trajectory / interpolation
  ↓
position / velocity / torque servo
  ↓
current controller
  ↓
motor
  ↓
gear / tendon / linkage
  ↓
joint torque
```

复现论文必须问：到底在哪一层定义 action？

## 6.4 Motor

对常见电机近似：

\[
\tau_m=k_t i,
\qquad e=k_e\omega.
\]

高速度时 back-EMF 限制可用电流，因此 motor torque 并非任何速度下都能达到峰值。真实控制受 torque–speed envelope 约束。

## 6.5 Gearbox

理想减速：

\[
\tau_{out}=\eta N\tau_m,
\qquad
\omega_{out}\approx\frac{\omega_m}{N}.
\]

大减速比提高 torque，却带来摩擦、backlash、反驱困难与冲击。Quasi-direct-drive 通过较低 gear ratio 提升 backdrivability 和 dynamic control。

## 6.6 Position / Velocity / Torque Control Interface

**Position**：稳定、易用，但真正接触力由 servo gain 与误差间接产生；

**Velocity**：直接控制运动率；

**Torque**：最接近动力学，适合 impedance/WBC，但对模型、sensor、safety 要求高。

同一 policy architecture 在 position-controlled arm 与 torque-controlled humanoid 上，实际问题完全不同。

## 6.7 Stiffness 与 Compliance

虚拟/机械弹簧：

\[
F=K\Delta x.
\]

高 stiffness 让 pose 精准，却使 contact impact 大；低 stiffness 更安全、更能适应误差，但 tracking 差。操作任务常真正需要的是“合适机械阻抗”，而不是绝对位置最准。

## 6.8 Series Elastic / Tendon / Underactuation

Series Elastic Actuator 通过弹性元件估计/调节力；tendon drive 可把 motor 放远离 distal link、减轻末端质量；underactuated hand 用机械耦合让手指自动包络物体。

这些设计直接改变学习问题的 conditioning。

## 6.9 Sensor Integration

机器人身体通常集成：encoder、motor current、IMU、F/T、tactile、camera。传感器不是“外挂输入”，它们的位置、带宽与 delay 由机电结构决定。

## 6.10 Power 与 Thermal

机械瞬时功率：

\[
P=\tau^T\dot q.
\]

策略可能在 simulator 中不断输出大 torque，但真机受 battery、driver current、motor temperature 和 gearbox load 限制。Humanoid 评价如果没有 energy / thermal margin，很难判断是否可长期运行。

## 6.11 Communication

CAN、EtherCAT、serial、Ethernet/ROS network 的 latency、bandwidth、jitter 不同。高频 torque loop 通常不应跨不可靠网络闭环。

这也是多速率系统存在的工程原因。

## 6.12 Embedded Compute

真实机器人常分层：

- motor MCU / drive：µs–ms；
- realtime CPU：servo / estimator；
- GPU computer：vision / VLA；
- remote compute：可选 high-level reasoning。

计算位置决定 latency、fault isolation 和 power budget。

## 6.13 Robot Description

URDF/MJCF/USD 至少描述：link、joint、axis、visual/collision geometry、mass、inertia、limit。Simulator 能“显示模型”不代表动力学正确；一个错误 inertia tensor 会让 sim-to-real 学错。

## 6.14 身体是算法的一部分

一个更公平的能力比较应写：

\[
\text{system}=\text{mechanism}+\text{sensors}+\text{controller}+\text{policy}.
\]

如果新机器人本身夹爪更顺应、相机更好、控制频率更高，不能把全部 gain 归因给 neural architecture。

## 实验

对同一单关节系统模拟：position servo、torque PD、series elasticity。施加相同外部碰撞，比较 peak force、tracking error 与 recovery。然后改变 control delay，观察 high-gain position loop 何时开始震荡。

## 研究问题

- 一个 universal policy 应看到完整 motor/gear parameter，还是只看抽象 embodiment token？
- 能否让 morphology 自动吸收一部分控制复杂度，从而减少 data requirement？
