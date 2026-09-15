# Part 9　动力学、接触与抓取

## 学习目标

能够从运动学进一步回答“为什么会这样动”；理解 manipulator equation 各项；理解 contact constraint、friction cone、complementarity、grasp wrench 与 humanoid centroidal dynamics；知道 simulator contact 为什么会影响学习结论。

---

## 9.1 从 Kinematics 到 Dynamics

运动学描述

\[
q\rightarrow T,\qquad \dot q\rightarrow V.
\]

动力学则回答给定 torque / external force 时状态怎样演化：

\[
(q,\dot q,\tau,F_{ext})\rightarrow \ddot q.
\]

对于真实机器人，action 是否可执行最终由动力学决定。

## 9.2 Manipulator Equation

经典刚体机械臂：

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)+\tau_f
=\tau+J^T(q)F_{ext}.
\]

逐项解释：

- \(M(q)\)：configuration-dependent mass matrix；
- \(C\dot q\)：Coriolis / centrifugal；
- \(g(q)\)：gravity；
- \(\tau_f\)：friction / unmodeled effects；
- \(\tau\)：actuator generalized force；
- \(J^TF_{ext}\)：外部 wrench 映射到 joint space。

## 9.3 Mass Matrix

\(M(q)\) 对正常 rigid body system 对称正定：

\[
x^TM(q)x>0.
\]

Kinetic energy：

\[
K=\frac12\dot q^TM(q)\dot q.
\]

因此 \(M\) 不只是“一个网络可学矩阵”，它编码 configuration-dependent inertia geometry。

## 9.4 Lagrangian Derivation

\[
L(q,\dot q)=K-U.
\]

Euler–Lagrange：

\[
\frac{d}{dt}\frac{\partial L}{\partial \dot q_i}
-\frac{\partial L}{\partial q_i}=\tau_i.
\]

这条公式可以从能量直接推导 dynamics，特别适合理解 conservative structure。

## 9.5 Newton–Euler

Newton–Euler 沿 kinematic tree 做 forward/backward recursion：forward 计算 link velocity/acceleration，backward 汇总 force/torque。它的计算复杂度比直接 symbolic Lagrange 更适合高 DOF robot。

## 9.6 Forward Dynamics

\[
\ddot q=M^{-1}(\tau-C\dot q-g+J^TF_{ext}).
\]

实际实现用 linear solve，不显式求 \(M^{-1}\)。随后数值积分得到 \(\dot q,q\)。

## 9.7 Inverse Dynamics

给定期望 \(q,\dot q,\ddot q\)，求 torque：

\[
\tau=M\ddot q+C\dot q+g.
\]

Computed-torque control、feedforward tracking、whole-body optimization 都大量使用 inverse dynamics。

## 9.8 Friction

简单 Coulomb + viscous：

\[
\tau_f=b\dot q+\tau_c\operatorname{sign}(\dot q).
\]

真实 gearbox friction 还有 stiction、Stribeck、temperature dependence。Sim2real 中，低速接触任务经常比高速 free-space 对 friction mismatch 更敏感。

## 9.9 Contact Geometry

定义 signed distance \(\phi(q)\)：

\[
\phi(q)>0\text{ separated},\quad
\phi(q)=0\text{ contact}.
\]

理想刚性 unilateral contact 不允许 \(\phi<0\)。

## 9.10 Contact Constraint

若接触点在法向方向速度/加速度受限：

\[
J_c(q)\ddot q+\dot J_c(q,\dot q)\dot q=0.
\]

Dynamics 加入 reaction force：

\[
M\ddot q+h=\tau+J_c^T\lambda.
\]

未知 \(\lambda\) 与 \(\ddot q\) 需要联合求解。

## 9.11 Complementarity

单边接触可写：

\[
0\le \lambda_n\perp\phi(q)\ge0.
\]

即：没有穿透；法向力不能“拉”；只有接触闭合时才有法向力。这个非光滑结构是 contact simulation/optimization 困难的根源之一。

## 9.12 Coulomb Friction Cone

\[
\|f_t\|\le\mu f_n.
\]

三维允许 tangential force 落在 cone 内。优化中常用 friction pyramid 线性近似。

滑动时 friction direction 与 relative tangential velocity 反向。

## 9.13 Soft Contact

Penalty model 常写：

\[
f_n=k\delta+c\dot\delta.
\]

优点是简单可微；缺点是 stiffness 与 timestep 共同决定数值稳定，且 penetration 是模型近似，不是现实刚体真的互穿。

## 9.14 Grasp Map

多个接触 force 合成物体 wrench：

\[
w=Gf_c.
\]

\(G\) 由 contact position/orientation 决定。Force closure 问：在 friction constraints 下，是否能生成足够 wrench 抵抗任意小外扰。

## 9.15 Form Closure vs Force Closure

**Form closure** 依靠几何约束完全限制物体；**force closure** 利用摩擦接触力实现任意 wrench。现实夹爪更多依赖 force closure + compliance。

## 9.16 Grasp Quality

可用 wrench-space margin、minimum singular value、distance to friction-cone boundary 等度量。但几何 grasp score 不能替代 reachability、collision、material/tactile uncertainty。

## 9.17 Contact Mode

Manipulation trajectory 不是一个平滑 dynamics：

```text
free motion
→ first touch
→ sticking contact
→ sliding
→ grasp closure
→ lift
→ release
```

每个 mode 有不同约束，因此 manipulation 本质接近 hybrid dynamical system。

## 9.18 Deformable Contact

软物体、cloth、cable 不再能由少量 rigid-body pose 完整描述。接触会改变形状甚至 topology。模型若只预测 object rigid transform，无法表达这些任务。

## 9.19 Centroidal Dynamics

对 humanoid，常把全身高维 dynamics 压缩到 center of mass 与 centroidal momentum：

\[
h=A_G(q)\dot q.
\]

外部 contact wrench 决定 momentum rate。Whole-body planning 常先规划 COM/contact force，再恢复 joint motion。

## 9.20 ZMP / Support

ZMP 是经典平衡指标，但适用在特定接触和近似条件。现代动态 humanoid 不应把“ZMP 在 support polygon 内”当成完整 stability definition。

## 9.21 Simulator Contact 不是 Reality

Physics engine 必须选择：solver、regularization、substep、friction approximation。两个 simulator 即使 robot URDF 相同，contact-rich policy 也可能显著不同。

所以接触任务论文必须记录 physics config。

## 9.22 Learning Dynamics Residual

已知 physics + learned residual：

\[
\ddot q=f_{rigid}(q,\dot q,\tau)+r_\theta(q,\dot q,\tau,o).
\]

比完全黑盒 dynamics 更容易利用结构、减少数据，并可将 residual 聚焦到 friction/compliance/unmodeled contact。

## 实验

做一个平面推物任务：固定视觉与 policy，单独扫 mass、friction、contact stiffness、simulation timestep。画 object displacement error 与 policy success，观察哪些物理变量最影响 sim2real。

## 研究问题

World model 应显式表示 contact mode，还是让大 latent model 自己隐式学习？如何设计实验区分二者？

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 09`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-09)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
