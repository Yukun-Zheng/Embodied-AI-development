# Part 8　机器人运动学

## 学习目标

能够从 robot geometry 推导 FK/Jacobian；理解 IK 为什么会多解、无解和数值不稳定；掌握 redundancy、null space、trajectory 与双臂/whole-body kinematics。

---

## 8.1 Forward Kinematics

给定 configuration：

\[
q=[q_1,\ldots,q_n]^T,
\]

求末端：

\[
T_{ee}=FK(q).
\]

运动学只描述 geometry，不问产生这个 pose 需要多少 torque。

## 8.2 Serial Chain

逐节变换：

\[
{}^0T_n={}^0T_1(q_1){}^1T_2(q_2)\cdots{}^{n-1}T_n(q_n).
\]

一旦 frame convention 清晰，FK 本质就是 transform composition。

## 8.3 Product of Exponentials

\[
T(q)=e^{[S_1]q_1}e^{[S_2]q_2}\cdots e^{[S_n]q_n}M.
\]

\(S_i\) 是 home pose 下第 i 个 joint screw axis，\(M\) 是 zero configuration 的末端 pose。

PoE 比 DH 更直接连接 Lie group 和 twist。

## 8.4 Denavit–Hartenberg

DH 通过四参数描述相邻 link frame。它历史重要、工业文档常见，但 frame assignment 规则容易出错。现代学习应会读 DH，但不必把它当唯一 kinematics 表达。

## 8.5 Differential Kinematics

末端 twist 与 joint velocity：

\[
V=J(q)\dot q.
\]

Jacobian 第 i 列可理解为：第 i 个 joint 以单位速度运动时，末端产生的瞬时 twist。

这个几何解释比“对 FK 求偏导”更可迁移。

## 8.6 Space / Body Jacobian

根据 twist 表达 frame 不同，有 \(J_s(q)\) 与 \(J_b(q)\)，两者通过 Adjoint 联系。

代码混用二者会导致 IK/control 方向看似随机错误。

## 8.7 Singularity

当

\[
\operatorname{rank}(J)<m
\]

时，末端失去某些瞬时自由方向。接近 singularity 时小 Cartesian target 可能要求很大 joint motion。

用 SVD：

\[
J=U\Sigma V^T
\]

观察 \(\sigma_{min}\) 是最直接诊断。

## 8.8 Manipulability Ellipsoid

若 \(\|\dot q\|\le1\)，可达末端速度集合形成 ellipsoid。奇异值描述各方向运动放大/衰减。

它能帮助选择 base pose、grasp pose 和 posture，使操作方向远离 singularity。

## 8.9 Inverse Kinematics

给定 \(T_d\) 求 \(q\)：

\[
FK(q)=T_d.
\]

IK 可能：无解、多解、连续无限解。数值 solver 还依赖 initial guess。

因此“IK success”应定义为：pose tolerance + joint limit + collision + convergence，而不是 solver 返回一个 vector。

## 8.10 Newton / Jacobian IK

局部 pose error \(e_k\)：

\[
q_{k+1}=q_k+J^+(q_k)e_k.
\]

只在局部有效，大 target 常需 step-size / line search。

## 8.11 Damped Least Squares

\[
\Delta q=J^T(JJ^T+\lambda^2I)^{-1}e.
\]

可以按 singularity 自适应增大 \(\lambda\)，在精度和稳定性之间折中。

## 8.12 Redundancy

当 \(n>m\)，完成末端任务后还有自由度：

\[
\dot q=J^+V_d+(I-J^+J)z.
\]

第二项可优化 joint-limit、collision、comfort、manipulability。

## 8.13 Joint Limit Avoidance

定义 cost：

\[
c(q)=\sum_i\left(\frac{q_i-q_{mid,i}}{q_{range,i}}\right)^2.
\]

取

\[
z=-k\nabla c(q)
\]

即可在不影响一阶末端任务的 null space 中远离 limit。

## 8.14 Constrained IK

更实际的 IK 是 optimization：

\[
\min_q \|\log(T_d^{-1}FK(q))\|_W^2
\]

subject to joint limits、collision、velocity/acceleration、balance constraints。

这比单纯 pseudoinverse 更符合真机。

## 8.15 Trajectory Generation

机器人不是从 \(q_0\) 瞬移到 \(q_f\)。Quintic polynomial 可满足起终点 position/velocity/acceleration。

Cartesian trajectory 则要分别处理 translation 与 rotation，或在 SE(3) 上插值。

## 8.16 Differential IK as Controller

高层 policy 给 desired twist：

\[
V_d=K_p e_{pose}
\]

低层 differential IK 转成 joint velocity target。这是很多 VLA 使用 Cartesian delta action 时真正发生的中间层。

## 8.17 Bimanual Kinematics

双臂经 torso/base 耦合。相对 pose：

\[
{}^LT_R=({}^WT_L)^{-1}{}^WT_R.
\]

共同搬物体时 relative constraint 往往比两个独立 absolute target 更重要。

## 8.18 Whole-Body Kinematics

Humanoid 任务可能同时约束：feet、hands、COM、gaze、posture。可写 stacked task：

\[
J_{task}\dot q=V_{task}.
\]

不同任务存在 priority，需要 hierarchical IK/QP。

## 8.19 Learning Policy 与 IK 的接口

三种常见设计：

1. policy 输出 joint action：表达力强，但 embodiment-specific；
2. policy 输出 EE delta：跨 arm 更容易，但依赖 IK；
3. policy 输出 latent/task-space goal：由 WBC 解算。

所谓“端到端”往往只是隐藏了其中一个接口，而不是物理约束消失。

## 实验

在 7-DOF arm 上采样 10,000 个 target，比较 pseudoinverse IK、DLS、constrained IK：success、iterations、joint-limit violation、minimum collision distance、\(\sigma_{min}(J)\)。

## 研究问题

跨本体 VLA 最合适的 shared action layer 是 joint、end-effector、task-space relation，还是更抽象的 world effect？
