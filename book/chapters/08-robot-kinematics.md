# Part 8　机器人运动学

## 学习目标

能够从 robot geometry 推导 FK/Jacobian；理解 IK 为什么会多解、无解和数值不稳定；掌握 redundancy、null space、trajectory 与双臂/whole-body kinematics；并能沿着 policy → task-space target → IK → joint command 的真实接口诊断失败。

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

## 8.20 一条真实 Cartesian-action 数据流

```text
VLA / policy
→ Δx, ΔR in camera/base/EE frame
→ frame transform
→ desired SE(3) pose / twist
→ Jacobian + IK / differential IK
→ joint position/velocity target
→ joint controller
→ actuator
```

若 task success 降低，必须沿链逐层检查，而不是直接归因于 policy。尤其应记录：

```text
input frame
pose-error convention
sigma_min(J)
IK residual
joint-limit margin
collision margin
command saturation
```

在很多真实系统中，高层网络输出只有 6–7 维，而 IK/WBC 才负责把它变成几十维 joint target。这个中间层决定了“action representation 是否真正可执行”。

## 8.21 IK Failure Taxonomy

### Target 根本不可达

目标超出 workspace。任何局部 solver 都不该被期待“优化出来”。先做 reachable-set / coarse planning 检查。

### Target 几何可达但约束不可行

满足 EE pose 的解可能违反 joint limit、self-collision、environment collision 或 humanoid balance。

### 接近 singularity

\(\sigma_{min}(J)\to0\) 时 Cartesian error 很小也可能映射成巨大 \(\Delta q\)。clip joint velocity 只能缓解症状，会引入新的 task-space tracking error。

### Frame / quaternion convention 错

最危险的一类：solver 看起来能收敛，但总朝稳定的错误方向移动。检查 world/base/camera/EE frame、left/right multiplication 与 quaternion order。

### Initial guess 导致错误 branch

多解 IK 中，数值解可能跳到 elbow-up / elbow-down 的另一 branch，产生大关节跃迁。连续控制应将前一时刻 solution 作为 prior，并对 configuration distance 加代价。

### Position success、orientation failure

只看 position tolerance 会让 grasp approach、tool orientation、bimanual relative pose 等任务产生“假成功”。

## 8.22 Hierarchical Task Priority

对于 whole-body robot，不是简单把所有 task stack 后 least squares 就够了。若 feet contact 必须严格保持，而 hand target 只是 soft objective，需要显式 priority：

```text
Priority 1: contact / balance / hard safety
Priority 2: hand / tool task
Priority 3: posture / manipulability / comfort
```

理想的 null-space projection 应确保低优先级更新不破坏高优先级 task。实际 QP/WBC 还会加入 torque、friction cone 和 dynamics constraints，因此 IK 与 control 在 humanoid 上逐渐汇合。

## 最小实验

在 7-DOF arm 上采样 10,000 个 target，比较 pseudoinverse IK、DLS、constrained IK：success、iterations、joint-limit violation、minimum collision distance、\(\sigma_{min}(J)\)。

必须增加四个 slice：

1. workspace boundary；
2. singularity neighborhood；
3. near joint limits；
4. same target but different initial guesses。

对应最小实现：[`code/minimal/planar_arm.py`](../../code/minimal/planar_arm.py)，再进入 Lab 02 / Lab 04。

## 研究问题

1. 跨本体 VLA 最合适的 shared action layer 是 joint、end-effector、task-space relation，还是更抽象的 world effect？
2. 如果两个 VLA 使用不同 IK/controller，能否仅凭 policy success rate 比较架构优劣？
3. 学习型 IK 相比 DLS/QP 的增益来自更好处理多解、collision，还是只是更快 amortized optimization？
4. morphology-conditioned policy 是否应该显式读取 kinematic Jacobian / graph，还是让模型隐式学习？
5. Whole-body foundation policy 的 high-level action 应该位于 IK 之前、WBC task-space，还是直接 joint/motor space？

## Source anchors / 原始来源

- Lynch & Park, *Modern Robotics: Mechanics, Planning, and Control*: https://modernrobotics.northwestern.edu/
- Siciliano et al., *Robotics: Modelling, Planning and Control*: https://doi.org/10.1007/978-1-84628-642-1
- Liégeois, “Automatic Supervisory Control of the Configuration and Behavior of Multibody Mechanisms,” IEEE SMC 1977（经典 redundancy/null-space 思想）: https://doi.org/10.1109/TSMC.1977.4309644
- 配套推导：[`book/DERIVATIONS.md`](../DERIVATIONS.md) D1–D3 / D6。

## 本章结论

运动学不是 foundation policy 之前的“旧知识”，而是 learned action 与真实身体之间的可执行性约束。只要 policy 输出的不是 motor current，FK/Jacobian/IK/frame convention 就仍然存在；隐藏接口不等于接口消失。
