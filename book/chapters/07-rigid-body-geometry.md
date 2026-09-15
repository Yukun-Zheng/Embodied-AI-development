# Part 7　空间、旋转与刚体几何

## 学习目标

能够无歧义地读写机器人位姿；掌握 rotation matrix、quaternion、SE(3)、Lie algebra、twist、adjoint 与 wrench 变换；能系统排查 frame convention 错误。

---

## 7.1 Frame 是机器人学的语法

令 \(\{A\}\)、\(\{B\}\) 为坐标系。本文约定：

\[
{}^AT_B
\]

表示“B frame 的坐标表达如何转换到 A frame”。若点在 B 中为 \({}^Bp\)：

\[
\begin{bmatrix}{}^Ap\\1\end{bmatrix}
={}^{A}T_B
\begin{bmatrix}{}^Bp\\1\end{bmatrix}.
\]

看到任何 pose 数字，先问：**谁相对谁？表达在哪个 frame？**

## 7.2 2D Rotation

\[
R(\theta)=
\begin{bmatrix}
\cos\theta&-\sin\theta\\
\sin\theta&\cos\theta
\end{bmatrix}.
\]

它满足 \(R^TR=I\)、\(\det R=1\)。三维 SO(3) 正是这个结构的推广。

## 7.3 SO(3)

\[
SO(3)=\{R\in\mathbb R^{3\times3}:R^TR=I,\det R=1\}.
\]

列向量可理解为被旋转 frame 的三个 basis 在参考 frame 中的表达。

逆变换：

\[
R^{-1}=R^T.
\]

## 7.4 Euler Angles

Euler angles 用三次轴旋转表示姿态。问题：

- rotation order 有歧义；
- intrinsic/extrinsic 有歧义；
- 存在 gimbal lock。

因此它适合 UI/人类阅读，不适合作为所有内部计算的唯一 representation。

## 7.5 Axis–Angle

用单位轴 \(\omega\) 与角度 \(\theta\) 表示：

\[
R=\exp(\hat\omega\theta).
\]

它与 Lie algebra 自然连接，适合 pose error 和局部优化。

## 7.6 Quaternion

单位 quaternion：

\[
q=[w,x,y,z],\qquad \|q\|=1.
\]

优点：无 gimbal lock、表示紧凑、易做 slerp。注意：

\[
q\equiv -q.
\]

如果直接用 quaternion MSE 训练 rotation prediction，必须处理 double-cover，否则同一旋转可能被当成“差很大”。

## 7.7 Homogeneous Transformation

\[
T=
\begin{bmatrix}
R&p\\0&1
\end{bmatrix}
\in SE(3).
\]

复合：

\[
{}^AT_C={}^AT_B{}^BT_C.
\]

逆：

\[
T^{-1}=\begin{bmatrix}R^T&-R^Tp\\0&1\end{bmatrix}.
\]

## 7.8 SO(3) Lie Algebra

向量 \(\omega\in\mathbb R^3\) 经 hat operator：

\[
\hat\omega=
\begin{bmatrix}
0&-\omega_3&\omega_2\\
\omega_3&0&-\omega_1\\
-\omega_2&\omega_1&0
\end{bmatrix}.
\]

满足：

\[
\hat\omega v=\omega\times v.
\]

## 7.9 Exponential Map

Rodrigues：

\[
R=I+\sin\theta\hat\omega+(1-\cos\theta)\hat\omega^2.
\]

Log map 则从 \(R\) 回到局部 axis-angle。它使 pose difference 可以在 tangent space 中表达。

## 7.10 SE(3) 与 Twist

刚体瞬时速度合并为：

\[
V=\begin{bmatrix}v\\\omega\end{bmatrix}\in\mathbb R^6.
\]

具体库也可能用 \([\omega,v]\)，必须显式确认。

Twist 可生成 screw motion，统一表达 rotation + translation。

## 7.11 Space vs Body Twist

同一物理速度在不同 frame 有不同数值：

\[
V_s=\operatorname{Ad}_T V_b.
\]

Adjoint 不是普通 rotation，因为线速度还受到 origin displacement 影响。

## 7.12 Adjoint

若 twist convention 为 \([v,\omega]\)：

\[
\operatorname{Ad}_T=
\begin{bmatrix}
R&\hat pR\\
0&R
\end{bmatrix}.
\]

若使用其他 convention，块顺序会变。复制公式前必须检查定义。

## 7.13 Wrench

\[
W=\begin{bmatrix}f\\\tau\end{bmatrix}.
\]

Twist 与 wrench 是功率对偶：

\[
P=W^TV.
\]

因此 frame 变换应保持 power invariant，由此得到 wrench 的相应 inverse-transpose adjoint 关系。

## 7.14 Pose Error

不要简单用 rotation matrix 元素 MSE。几何上更自然：

\[
T_e=T_d^{-1}T,
\qquad
\xi_e=\log(T_e)^\vee.
\]

\(\xi_e\in\mathbb R^6\) 是局部 pose error，可直接进入 IK/control。

## 7.15 Interpolation

Position 可线性插值；rotation 推荐 slerp 或 Lie-group interpolation：

\[
R(t)=R_0\exp\left(t\log(R_0^TR_1)\right).
\]

对完整 SE(3)，插值方式会决定 screw-like path 与分离 translation/rotation 的差异。

## 7.16 Convention Failure Checklist

最常见：

- `world_T_camera` / `camera_T_world` 反；
- row vs column vector；
- left/right handed；
- quaternion `wxyz` / `xyzw`；
- Euler `XYZ` / `ZYX`；
- angle deg/rad；
- active/passive rotation；
- delta action 在 world/body frame。

**规则**：每次 transform pipeline 都先用一个人工构造的简单点做 sanity check，而不是直接看真实视频“似乎对”。

## 实验

随机生成 10,000 个 SO(3)/SE(3) pose，验证：inverse、composition、exp/log round-trip。随后故意引入 quaternion 顺序错误和 transform 反向错误，观察末端 target 如何系统性偏离。

## 研究问题

对 foundation robot model，pose 是否应该继续被当普通 token/vector，还是应让 architecture 显式满足 SE(3) structure？
<!-- CHAPTER-ENRICHMENT-R2-P07:START -->
## 7.19 刚体几何在软件栈中的真实数据流

```text
camera pixels / depth
→ point / pose in camera frame
→ T_base_camera / T_world_base
→ object pose in world/base frame
→ desired EE pose
→ pose error on SE(3)
→ IK / controller
```

每一条边都应带：

```text
from_frame
to_frame
timestamp
rotation convention
units
```

一个 4×4 matrix 的 shape 无法告诉你它表示 `world←camera` 还是 `camera←world`。因此 geometry API 最好把 frame semantics 写进类型/变量名，而不是靠注释记忆。

## 7.20 最小实验：Frame-Convention Fuzz Test

随机生成一条变换链：

\[
{}^WT_B,\quad {}^BT_C,\quad {}^CT_O,
\]

验证：

\[
{}^WT_O={}^WT_B{}^BT_C{}^CT_O
\]

以及所有 inverse / round-trip identity。随后故意注入四类 bug：

1. 乘法顺序反转；
2. quaternion `xyzw/wxyz` 混淆；
3. degree/radian 混淆；
4. 使用旧 timestamp 的 extrinsic/base pose。

要求测试在进入 policy/IK 前就失败。目标不是“会算 SE(3)”，而是让 frame bug 在系统边界被机器检测。
<!-- CHAPTER-ENRICHMENT-R2-P07:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 07`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-07)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
