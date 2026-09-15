# Part 15　状态估计、定位与世界状态

## 学习目标

理解为什么 observation 不等于 state；掌握 Bayes filter、Kalman/EKF/UKF/Particle Filter 的核心结构；理解 visual odometry、SLAM、object pose estimation、dynamic world state 与 POMDP 之间的关系；能够判断一个现代神经 policy 的 hidden state 是否真的承担了 state estimation 的职责。

---

## 15.1 什么是 State

对动态系统，一个理想状态 \(s_t\) 应满足 Markov 性：

\[
p(s_{t+1}\mid s_{0:t},a_{0:t})
=p(s_{t+1}\mid s_t,a_t).
\]

也就是说，一旦知道当前 state 和未来 action，就不再需要完整历史预测未来。

RGB frame 通常不是 state：它看不到遮挡后物体、速度、接触力、人的隐藏意图。

## 15.2 Observation 与 Hidden State

传感器：

\[
o_t\sim p(o_t\mid s_t).
\]

系统必须从 history 恢复 state：

\[
\hat s_t=E(o_{0:t},a_{0:t-1}).
\]

经典 state estimator 显式做这件事；RNN/Transformer/world model 则把它藏在 latent 中。

## 15.3 Belief State

如果无法确定唯一状态，维护 posterior：

\[
b_t(s)=P(s_t=s\mid o_{0:t},a_{0:t-1}).
\]

Belief 本身可以作为 POMDP 上的充分状态。

重要区别：

> “不知道物体在哪里”不是估计一个错误位置，而应该表示多个可能位置及其概率。

## 15.4 Bayes Filter

Prediction：

\[
\bar b_t(s_t)=
\int p(s_t\mid s_{t-1},a_{t-1})
 b_{t-1}(s_{t-1})ds_{t-1}.
\]

Correction：

\[
b_t(s_t)=\eta\,p(o_t\mid s_t)\bar b_t(s_t).
\]

这是 state estimation 的统一骨架：**dynamics 预测 + sensor 证据纠正**。

## 15.5 Kalman Filter

线性高斯系统：

\[
x_t=Ax_{t-1}+Bu_{t-1}+w_t,
\qquad w_t\sim\mathcal N(0,Q),
\]

\[
z_t=Hx_t+v_t,
\qquad v_t\sim\mathcal N(0,R).
\]

预测：

\[
\hat x_t^-=A\hat x_{t-1}+Bu_{t-1},
\]

\[
P_t^-=AP_{t-1}A^T+Q.
\]

更新：

\[
K_t=P_t^-H^T(HP_t^-H^T+R)^{-1},
\]

\[
\hat x_t=\hat x_t^-+K_t(z_t-H\hat x_t^-),
\]

\[
P_t=(I-K_tH)P_t^-.
\]

Kalman gain 的直觉：预测越不确定、传感器越可靠，就越相信 measurement。

## 15.6 一维例子

若 prior variance \(P^-=4\)，measurement variance \(R=1\)，且 \(H=1\)：

\[
K=\frac4{4+1}=0.8.
\]

说明新 measurement 权重高。反之若 sensor 很差 \(R=100\)，\(K\approx0.038\)，系统更相信 dynamics prior。

## 15.7 Extended Kalman Filter

非线性：

\[
x_t=f(x_{t-1},u)+w,
\quad z_t=h(x_t)+v.
\]

在当前 estimate 线性化：

\[
F=\frac{\partial f}{\partial x},
\qquad
H=\frac{\partial h}{\partial x}.
\]

EKF 对小 uncertainty 有效；强非线性/多模态时 linearization 可能严重错误。

## 15.8 Unscented Kalman Filter

UKF 不显式求 Jacobian，而选择 sigma points：

\[
\{\chi_i\}
\]

通过 nonlinear dynamics 传播，再重构 mean/covariance。它可以更准确保留非线性变换后的前两阶矩，但仍是近似单峰 distribution。

## 15.9 Particle Filter

用粒子表示：

\[
b_t(s)\approx\sum_{i=1}^N w_i\delta(s-s_i).
\]

流程：sample dynamics → likelihood weighting → resampling。

优势是可表达多峰；缺点是高维 state 需要大量粒子，易 particle degeneracy。

## 15.10 Sensor Fusion

例如 camera + IMU：IMU 高频预测 orientation/motion，camera 低频但长期稳定，用于纠正 drift。

多传感器的价值不只是“信息更多”，还在于 error mode 互补。

## 15.11 Observability

若系统某个 state component 永远不影响 observation，就无法从传感器恢复。

线性系统：

\[
\mathcal O=
\begin{bmatrix}
C\\CA\\CA^2\\\vdots
\end{bmatrix}.
\]

若 rank 满，系统 observable。

机器人主动感知本质上可以通过改变 action / viewpoint 改善 observability。

## 15.12 Visual Odometry

VO 从连续图像估计 camera relative motion：

\[
{}^{t}T_{t+1}.
\]

常见 pipeline：feature/dense correspondence → geometry → pose → local optimization。

只有相对运动累积会 drift，因此需要 loop closure / external reference。

## 15.13 SLAM

Simultaneous Localization and Mapping：同时估计 robot trajectory \(X\) 与 map \(M\)：

\[
P(X,M\mid Z,U).
\]

现代 graph-based SLAM 常转成：

\[
\min_X\sum_k\|r_k(X)\|_{\Sigma_k^{-1}}^2.
\]

每个 odometry / loop closure / landmark measurement 是一个 factor。

## 15.14 Loop Closure

机器人回到曾经地点时，识别同一 place 并加入 constraint。它能把长期累计 drift 拉回全局一致。

错误 loop closure 也会毁掉整张地图，所以 place recognition 需要 confidence / geometric verification。

## 15.15 Object Pose Estimation

对于 rigid object：

\[
{}^WT_O\in SE(3).
\]

方法可基于 keypoints、PnP、point cloud registration、direct neural pose prediction。

对称物体存在等价 pose 集合：

\[
T\sim TS,
\qquad S\in\mathcal S_{sym}.
\]

评测若忽略 symmetry，会把物理上等价姿态误判成大误差。

## 15.16 Pose Tracking

单帧 pose estimation 之后，还应结合 dynamics：

\[
T_t=f(T_{t-1},v_{t-1})+\epsilon.
\]

Tracking 可以在短暂 occlusion 时维持 object belief，而不是每帧失忆。

## 15.17 Articulated State Estimation

抽屉/门状态：

\[
s_{obj}=(T_{base},q_{art},\dot q_{art}).
\]

仅估整件家具 pose 不够。操作策略真正需要 articulation coordinate、limit、current progress。

## 15.18 Contact State Estimation

很多 interaction state 视觉不可见：

- contact / no contact；
- sticking / sliding；
- grasp secure / slip；
- force distribution。

应融合 F/T、tactile、motor current 与 proprioception，形成 hybrid mode belief。

## 15.19 Dynamic World State

完整场景可能写：

\[
s_t=\{x_{robot},\mathcal O_t,\mathcal R_t,\mathcal C_t,\mathcal H_t\},
\]

其中对象集合 \(\mathcal O_t\)、关系 \(\mathcal R_t\)、接触 \(\mathcal C_t\)、human state \(\mathcal H_t\)。

长期 agent 还需 persistent identity 与 memory。

## 15.20 POMDP

POMDP：

\[
(\mathcal S,\mathcal A,T,R,\Omega,O,\gamma).
\]

策略理想上基于 belief：

\[
a_t\sim\pi(a\mid b_t).
\]

这统一了 state estimation 与 decision making：不确定性不是先“估完再忽略”，而应影响 action。

## 15.21 Learned Hidden State

RNN：

\[
h_t=f_\theta(h_{t-1},o_t,a_{t-1}).
\]

Transformer 则把 history token 作为 context。

要验证 \(h_t\) 是否真是有效 world state，可 probe：

- hidden object location；
- object velocity；
- contact mode；
- task progress；
- uncertainty。

更重要的是 intervention：破坏某项 hidden information 后，policy 是否按预期失败。

## 15.22 State Representation 与 Sufficiency

理想 latent \(z_t\) 满足：

\[
P(o_{t+1:T},r_{t:T}\mid o_{\le t},a_{t:T})
\approx
P(o_{t+1:T},r_{t:T}\mid z_t,a_{t:T}).
\]

这把“好 representation”定义为对未来与 decision 足够，而非视觉上易解释。

## 15.23 Uncertainty Calibration

State estimator 不只输出 mean：

\[
(\hat x_t,P_t).
\]

若 covariance 长期过小，planner 会过度自信。应做 normalized innovation squared、coverage test、pose error vs predicted covariance。

## 15.24 Estimation–Control Coupling

高动态动作会使 perception 变差：motion blur、occlusion、IMU vibration；控制又依赖 estimate。

因此 estimation 与 control 不是单向 pipeline，而是耦合闭环。Active perception 更进一步主动选择动作提高 estimation quality。

## 常见失败

- 把网络最后一层 feature 直接叫 state；
- EKF covariance 长期不校准；
- SLAM map 用未来 frame 造成 benchmark leakage；
- object tracker 遮挡后 ID switch；
- symmetric object pose loss 错；
- F/T contact 与视觉 timestamp 不对齐；
- policy 不读取 uncertainty，却声称使用 belief。

## 最小实验

实现 2D mobile robot EKF：wheel odometry + range landmark。逐渐提高 process/sensor noise，检查 RMSE 与 covariance calibration。然后加入遮挡导致 landmark 暂时缺失，比较“只输出 mean”与“belief-aware planner”在安全避障上的差异。

## 研究问题

1. Foundation robot model 是否需要显式 belief，还是大 Transformer hidden state 足够？
2. 怎样让 learned state estimator 输出可用于安全决策的 calibrated uncertainty？
3. Persistent object/world state 是否应该从 VLA 中独立出来，成为长期 robot operating system 的公共服务？

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 15`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-15)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
