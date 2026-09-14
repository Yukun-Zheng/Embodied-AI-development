# Part 16　触觉、力觉与接触智能

## 学习目标

理解为什么视觉无法替代接触感知；掌握 F/T、视觉触觉、压力阵列、滑移检测、多模态融合与高频触觉反馈的系统角色；理解触觉 foundation model / tactile world model 的真正研究问题不是“再加一种 modality”，而是如何建立对**局部接触状态**可预测、可迁移、可实时利用的表征。

---

## 16.1 为什么 Vision 不够

摄像头通常能看见“手指接近物体”，却很难直接知道：

- 是否已经产生接触；
- 接触点具体在哪里；
- normal / shear force 多大；
- 接触面是否正在滑；
- 软材料怎样局部形变；
- 两个隐藏表面是否已经对齐。

在 peg insertion、拧瓶盖、布料折叠、in-hand manipulation 中，决定成败的变量往往就在这些视觉难观测状态里。

## 16.2 Contact 是局部但高带宽的事件

视觉 observation 常覆盖整个 scene，却只有 15–60 Hz；触觉只覆盖几平方厘米，却可以高频读取接触细节。

这形成一种天然互补：

```text
vision    → global context / object / geometry
proprio   → body state / motion
force     → net interaction wrench
tactile   → local contact geometry / shear / slip
```

一个通用机器人不应把所有 modality 强行压到同一频率和同一 token 化方式。

## 16.3 Force/Torque Sensing

六轴 wrist F/T：

\[
w=[F_x,F_y,F_z,\tau_x,\tau_y,\tau_z]^T.
\]

它反映工具整体受到的外部 wrench，但无法唯一推断多个接触点的空间分布。

例如同样 \(F_z\) 可能来自一个中心接触，也可能来自两个边缘接触。

## 16.4 Contact Detection

最简单阈值：

\[
\|F\|>F_{th}.
\]

但需要去除 gravity / inertia / bias。运动中更合理：

\[
w_{res}=w_{measured}-\hat w_{model}.
\]

若 residual 超过动态 threshold，则判断外部接触。

## 16.5 Joint Torque Residual

没有 F/T sensor 时，也可比较 measured torque 与 dynamics prediction：

\[
r_\tau=\tau_{meas}-\hat\tau_{dyn}.
\]

由

\[
r_\tau\approx J^TF_{ext}
\]

估计外力。精度受 friction/model error 影响，但适合碰撞检测。

## 16.6 Tactile Sensor 类型

常见：

- pressure/capacitive array；
- piezoresistive；
- magnetic tactile；
- optical tactile；
- elastomer + camera 的 vision-based tactile。

不同 sensor 输出空间完全不同，因此 cross-sensor transfer 是触觉 foundation model 的核心难点。

## 16.7 Vision-Based Tactile

相机观察 elastomer 表面 marker / illumination change：

\[
I_{touch}=\mathcal R(\text{contact geometry},F_n,F_t,material).
\]

优点是空间分辨率高；缺点是成像外观依赖 elastomer、lighting、camera calibration 和磨损。

它本质仍是 image，但其 image formation physics 与普通 RGB camera 完全不同。

## 16.8 Contact Patch

Tactile 可估接触区域：

\[
C(x,y)\in\{0,1\}
\]

或 pressure field：

\[
p(x,y)\ge0.
\]

接触 patch 的中心、面积、shape 与变化率可以判断 grasp 稳定性和物体局部几何。

## 16.9 Normal 与 Shear

对抓取，normal force 决定摩擦上限：

\[
\|F_t\|\le\mu F_n.
\]

Shear 增大而 normal 不变时，接触更接近 friction cone 边界，滑移风险上升。

因此 tactile controller 可以在 incipient slip 前主动增加 grip force。

## 16.10 Slip Detection

滑移信号可能来自：

- marker flow；
- high-frequency vibration；
- shear field change；
- object pose drift。

可训练 classifier：

\[
p(slipping\mid T_{t-k:t},q_{t-k:t}).
\]

但部署真正需要的不只是“检测到滑了”，还要触发 fast corrective action。

## 16.11 Tactile Reflex

快速回路：

\[
\Delta a_t=\pi_{reflex}(T_t,q_t,F_t),
\]

与慢速 nominal policy 组合：

\[
a_t=a_t^{VLA}+\Delta a_t.
\]

这是一种 residual control：高层决定意图，触觉只修正局部接触。

## 16.12 为什么不能把 Tactile 只塞进慢速 VLA

如果 VLA 5 Hz，而 slip event 50 ms 内就会掉物：

\[
T_{response}^{VLA}\approx200\text{ ms}
\]

已来不及。

因此触觉最值得研究的系统问题是**multi-rate fusion**，而不只是多模态 Transformer。

## 16.13 Early / Late / Hierarchical Fusion

**Early fusion**：tactile token 与视觉 token 一起进入 backbone；

**Late fusion**：各自 encoder 后融合；

**Hierarchical**：slow visual-language policy + fast tactile controller。

第三种更符合不同物理时间尺度，也更容易验证 tactile contribution。

## 16.14 Tactile Representation

一个触觉 latent \(z_t^T\) 可以编码：

\[
\{contact\ location,normal,shear,slip,material,shape\}.
\]

训练 objective：classification、reconstruction、contrastive、future prediction、action-conditioned prediction。

真正优质 representation 应跨 object、sensor、robot hand 迁移。

## 16.15 Visuo-Tactile Alignment

视觉看到接触前后大尺度对象，触觉观察局部 patch。可通过同步数据学习：

\[
z_V\leftrightarrow z_T.
\]

例如根据 camera image 预测 tactile future，或根据 tactile 找视觉对应 surface region。

这能建立“外观—接触属性”关联，但必须防止背景/对象 ID shortcut。

## 16.16 Material Perception

触觉与 action 可帮助估计 stiffness、friction、texture：

\[
\hat\phi_{material}=f(T_{0:t},a_{0:t}).
\]

Passive touch 信息有限，主动压/滑动作会提高 identifiability。

这就是 active touch。

## 16.17 Tactile World Model

学习：

\[
z_{t+1}^{T}=F(z_t^T,z_t^V,q_t,a_t).
\]

预测 nominal tactile response。如果 observed 与 prediction 大幅偏差：

\[
\delta_t=\|z_{t+1}^{obs}-\hat z_{t+1}\|
\]

可用于异常 contact / slip / misalignment detection。

## 16.18 Predictive + Reactive 触觉

一个更完整系统分两部分：

- **predictive**：知道即将发生什么接触；
- **reactive**：实际偏离预测时快速纠正。

截至 2026，TouchWorld、T-Rex 等公开研究进一步把触觉推向 predictive/reactive foundation-policy 与 variable-rate control 方向。教材关注的是它们代表的机制：**触觉既是 world-model signal，也是 fast feedback signal**。

## 16.19 Cross-Sensor Tactile Learning

不同 sensor 图像外观差异大，但底层 physical contact variables 更共享。

目标可以是学习 latent：

\[
z_{physical}=E_e(T^{(e)}),
\]

不同 sensor-specific encoder 映射到同一 physical representation。

验证方式：在 sensor A 训练 material/slip classifier，在 sensor B 少量数据甚至 zero-shot 测试。

## 16.20 Dexterous Hand

多手指会同时有多个 contact：

\[
\mathcal C=\{C_1,\ldots,C_m\}.
\]

全手控制需要估计 contact graph、每指 force、object pose 与 internal force。

仅有 wrist F/T 不够区分每根手指的贡献。

## 16.21 Bimanual Contact

两臂共同持物时，还需知道 load distribution：

\[
W_{object}=W_L+W_R.
\]

Handover 中 release condition 最好基于 receiver 已接管 load，而不是固定 timer。

## 16.22 Tactile Data Collection

触觉 dataset 特别容易缺 metadata：

- sensor type/version；
- elastomer age；
- calibration；
- contact object/material；
- robot pose；
- action/force；
- timestamp。

如果只有 tactile image，没有 action/pose，就很难研究 contact dynamics。

## 16.23 Simulating Tactile

高保真触觉 simulation 远比 RGB render 难，需要 contact deformation、material、sensor optics。很多 sim-to-real tactile policy 因 simulator 不能复现微观接触而失败。

因此 tactile foundation model 的真实数据价值尤其高。

## 16.24 Safety

Tactile/force 也是 safety sensor：检测 human contact、unexpected collision、fragile object force。

但 safety trigger 应独立于大模型主 policy，以保证 policy failure 时仍可停止。

## 常见失败

- 把 tactile image 当普通 RGB augmentation；
- 触觉与 robot state 时间不同步；
- tactile sensor 长期磨损导致 distribution shift；
- VLA 融合触觉但 frequency 被降到 5 Hz；
- slip detector 高 accuracy，但 action correction 太慢；
- training 中对象 ID 与 material 绑定，模型通过视觉外观猜 material；
- simulation tactile 过于理想。

## 最小实验

抓取同一个可滑物体。设置四组：视觉-only、F/T、tactile classifier、tactile fast residual。逐步降低 friction / 增加外部扰动。记录 slip detection delay、drop rate、grip force、VLA inference rate。目标是证明“触觉价值来自哪条反馈链”，而不是只比较最终 success。

## 研究问题

1. Tactile foundation model 的共享 latent 应是像素 feature，还是 contact geometry/force 的物理状态？
2. 触觉应该和 VLA 统一进同一 backbone，还是形成类似“脊髓反射”的独立快速模块？
3. 怎样构造跨 sensor / hand / embodiment 的标准 tactile benchmark？

## 2026 延伸阅读

- TouchWorld (2026), arXiv:2607.07287.
- T-Rex (2026), arXiv:2606.17055.
- *Vision-Based Tactile Intelligence for Robotics* survey (2026), arXiv:2608.15490.
