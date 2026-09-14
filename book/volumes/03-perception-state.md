# Volume III　感知、状态与世界表示

> 机器人“看到”像素，不等于它“知道”世界。感知系统的任务是把物理信号转成对行动有用的状态、几何、关系与不确定性。本卷从 sensor physics 一路推到 2D/3D/4D representation、state estimation、触觉与主动感知。

---

# Part 12　机器人传感器、标定与时间

## 12.1 Physical Signal → Sensor → Observation

真实世界变量 \(s_t\) 通过传感器模型变成观测：

\[
o_t=h(s_t)+\epsilon_t.
\]

这里 \(h\) 可能是透视投影、惯导积分、弹性体形变成像或电机编码器量化。理解一个传感器，至少要知道：**测什么、怎么测、单位、频率、延迟、噪声、饱和、标定方法。**

## 12.2 Pinhole Camera

相机坐标点 \((X,Y,Z)\) 投影到像素：

\[
\begin{bmatrix}u\\v\\1\end{bmatrix}
\sim
K
\begin{bmatrix}X/Z\\Y/Z\\1\end{bmatrix},
\qquad
K=\begin{bmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{bmatrix}.
\]

完整 world-to-pixel：

\[
\tilde p=K[R\mid t]P_W.
\]

**intrinsics** 描述相机自身投影，**extrinsics** 描述相机相对世界/机器人 frame 的 pose。

## 12.3 Back-Projection

已知深度 \(z\)：

\[
X=(u-c_x)z/f_x,\qquad
Y=(v-c_y)z/f_y,\qquad
Z=z.
\]

这一步把二维 RGB-D 恢复为 camera-frame point cloud。若 extrinsics 错几厘米，后续 grasp pose 也会整体错几厘米。

## 12.4 Depth Sensor

常见原理包括 stereo、structured light 与 time-of-flight。深度误差通常随距离变化，并在反光、透明、黑色材质和边缘处恶化。深度图不是“真值 Z-buffer”，真实系统必须处理孔洞、flying pixel 与多路径干扰。

## 12.5 LiDAR

LiDAR 直接测距并产生稀疏三维点。移动机器人常把 LiDAR 与 IMU、wheel odometry 融合。对 manipulation，近距离 RGB-D 更常见；对 navigation 和 outdoor autonomy，LiDAR 几何稳定性仍有重要价值。

## 12.6 IMU

IMU 常含 accelerometer 与 gyroscope：

\[
\omega_m=\omega+b_g+n_g,
\]

\[
a_m=R^T(a-g)+b_a+n_a.
\]

bias 会随时间漂移。单纯积分角速度/加速度会迅速累计误差，因此必须与视觉、里程计等融合。

## 12.7 Proprioception

关节 encoder 给出 \(q\)，差分/滤波得到 \(\dot q\)；电流可粗略反映 torque。对 learning policy，proprioception 通常比视觉延迟更低，是保持快速闭环的重要信号。

## 12.8 Force/Torque

六维 F/T sensor 输出 wrench：

\[
w=[F_x,F_y,F_z,\tau_x,\tau_y,\tau_z]^T.
\]

必须补偿 sensor frame、工具重力、bias 和惯性项。接触事件、插入、打磨、双臂内力控制都高度依赖该信号。

## 12.9 Tactile

触觉可分压阻/电容阵列、光学触觉、磁/流体等。视觉触觉（如通过相机观察软胶形变）能提供高分辨率接触几何、法向/剪切与 slip 线索。触觉最大的意义是观察视觉无法可靠看见的**局部接触状态**。

## 12.10 Event Camera 与 Audio

Event camera 按亮度变化事件异步输出，适合高速运动与高动态范围；audio 可提供碰撞、机器状态、人类语音等信息。它们提醒我们：机器人 observation 不应默认等于 RGB frame。

## 12.11 Calibration

标定至少包含：

- camera intrinsic；
- camera-to-robot extrinsic；
- hand-eye calibration；
- joint zero / kinematic parameter；
- F/T bias；
- tactile sensor mapping；
- clock offset。

Hand-eye 常写成

\[
AX=XB,
\]

求未知 transform \(X\)。

## 12.12 Timestamp、Latency 与 Synchronization

若 camera frame 来自 \(t_c\)，joint state 来自 \(t_q\)，而 action 在 \(t_a\) 执行，简单拼成同一 observation 可能产生不存在于现实的“混合时刻”。高质量 robot dataset 必须记录原始 timestamp，并明确 resampling / interpolation 规则。

---

# Part 13　二维视觉与视觉表示学习

## 13.1 Pixel 不等于 State

RGB 图像是光照、材质、视角、相机响应共同形成的结果。同一物理状态可产生不同像素，不同物理状态也可能产生相似像素。视觉 encoder 的目标不是“压缩图像”本身，而是产生对当前任务有用的 sufficient representation。

## 13.2 CNN

卷积利用局部连接与平移共享：

\[
y_{i,j,c_o}=\sum_{\Delta i,\Delta j,c_i}W_{\Delta i,\Delta j,c_i,c_o}x_{i+\Delta i,j+\Delta j,c_i}.
\]

CNN 在机器人视觉中仍因效率与局部几何偏置有价值。

## 13.3 Vision Transformer

图像切成 patch token：

\[
X\in\mathbb R^{N\times d}.
\]

self-attention：

\[
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^T}{\sqrt d}\right)V.
\]

ViT 强于全局关系建模，但空间精确性取决于 patch 分辨率、position encoding 和训练目标。

## 13.4 Detection、Segmentation、Tracking

- detection：对象 + bounding box；
- semantic segmentation：每像素类别；
- instance segmentation：同类不同实例；
- tracking：维持时间身份。

机器人需要的不只是“哪里有杯子”，还要知道哪个杯子、当前 pose、遮挡关系以及它是否被手抓住。

## 13.5 Optical Flow

光流近似每个像素的二维运动：

\[
I_xu+I_yv+I_t=0.
\]

它不等同于三维 motion，但提供强 temporal correspondence，可用于动态场景、视觉伺服、视频表示。

## 13.6 Self-Supervised Representation

机器人数据昂贵，因此大量视觉 backbone 来自无标签图像/视频预训练。常见目标：contrastive、masked prediction、distillation、predictive latent learning。

一个关键区别：**语义预训练优化“是什么”，物理交互还需要“在哪里、如何动、怎样接触”。**

## 13.7 Egocentric Video

第一视角视频与 robot camera 在视点和任务结构上更接近，可提供海量 human interaction prior。但人体 hand 与 gripper、视线与 camera rig、动力学能力均不同，所以 human-to-robot transfer 不是把视频直接当 action supervision。

## 13.8 Task-Relevant Representation

理想 representation \(z=E(o)\) 应保留对 action/reward/dynamics 必要的信息：

\[
p(s_{t+1},r_t\mid o_{\le t},a_t)
\approx
p(s_{t+1},r_t\mid z_t,a_t).
\]

这比 linear-probe image classification accuracy 更符合机器人目标。

## 13.9 怎样检验视觉真的服务物理交互

建议至少做四类诊断：

1. **遮挡/视角 perturbation**：representation 是否稳定？
2. **geometry probe**：相对深度、pose、contact point 是否可恢复？
3. **intervention**：改变任务无关纹理，策略是否被误导？
4. **causal ablation**：冻结/替换视觉 encoder 后，成功率变化来自哪里？

---

# Part 14　三维、四维与对象中心世界表示

## 14.1 Point Cloud

\[
P=\{p_i\in\mathbb R^3\}_{i=1}^N.
\]

点云直接保留几何，但无规则网格结构。PointNet 类方法用 permutation-invariant pooling；Point Transformer 使用局部/全局 attention。

对 manipulation，点云的优点是 action 与 geometry 处在同一三维坐标系，缺点是 RGB 语义、遮挡和稀疏噪声处理困难。

## 14.2 Voxel、TSDF、Occupancy

Voxel 把空间离散成三维格；TSDF 存储到表面的 signed distance；occupancy 表示空间是否被占据。它们把三维几何转成规则结构，但计算量随空间分辨率立方增长。

## 14.3 NeRF

NeRF 学习

\[
F_\theta(x,d)\rightarrow(\sigma,c)
\]

并通过 volume rendering 合成新视角。其价值是连续视图一致表示；局限是动态场景、在线更新、控制时延与精确物理属性并非原始目标。

## 14.4 3D Gaussian Splatting

3DGS 用显式高斯 primitives 表示场景，渲染快、适合重建和动态扩展。对 robotics，更值得研究的是：这些 primitives 是否能同时携带 geometry、semantics、uncertainty、affordance 和 dynamics，而不仅是 photorealistic appearance。

## 14.5 Dynamic / 4D Representation

真实世界不仅有 \(x,y,z\)，还有时间：

\[
\mathcal W(x,y,z,t).
\]

4D 表示要区分 camera motion、object rigid motion、deformation 和 topology change。cloth、human、双臂交互都要求动态 representation。

## 14.6 Object-Centric Representation

把场景分成对象 latent：

\[
Z=\{z_1,\ldots,z_K\}.
\]

优势是组合性和持久 identity；难点是对象边界并不总自然，例如绳索、液体、抽屉-柜体关节、两物体接触后形成的联合系统。

## 14.7 Scene Graph

节点是 entity，边是关系：

```text
[cup] --on--> [table]
[cup] --inside--> [gripper workspace]
[drawer] --part-of--> [cabinet]
[hand] --holding--> [cloth]
```

scene graph 适合 reasoning 与 planning，但必须持续从 noisy perception 更新，不能假设符号关系是 oracle。

## 14.8 Affordance Field

比 object label 更行动导向的表示是给空间位置/姿态赋予可操作性分数：

\[
A(x,R,skill\mid o,g).
\]

例如哪里可抓、哪里可推、哪个方向可拉。它天然连接 perception 与 action proposal。

---

# Part 15　状态估计、定位与世界状态

## 15.1 Observation ≠ State

state 应具有 Markov 性：

\[
p(s_{t+1}\mid s_{0:t},a_{0:t})=p(s_{t+1}\mid s_t,a_t).
\]

单帧 RGB 往往不满足，因此系统要显式估计 state 或用 recurrent/memory model 学隐状态。

## 15.2 Kalman Filter

线性高斯系统：

\[
x_t=Ax_{t-1}+Bu_t+w_t,
\]

\[
z_t=Hx_t+v_t.
\]

预测：

\[
\hat x_t^-=A\hat x_{t-1}+Bu_t,
\qquad
P_t^-=AP_{t-1}A^T+Q.
\]

更新：

\[
K_t=P_t^-H^T(HP_t^-H^T+R)^{-1},
\]

\[
\hat x_t=\hat x_t^-+K_t(z_t-H\hat x_t^-).
\]

Kalman gain 本质是模型预测与传感器证据按不确定性加权。

## 15.3 EKF / UKF / Particle Filter

EKF 对非线性 \(f,h\) 做 Jacobian 线性化；UKF 用 sigma points 传播分布；particle filter 用带权样本表示多模态 belief。

当“物体可能在两个遮挡区域之一”时，单 Gaussian EKF 天然不够。

## 15.4 Visual Odometry / SLAM

VO 估计相邻 frame 的 camera motion；SLAM 同时估计 trajectory 与 map：

\[
\arg\max_{X,M}p(X,M\mid Z,U).
\]

现代 SLAM 常转为 factor graph / nonlinear least squares。机器人操作也有“局部 SLAM”问题：手眼相机、移动底盘、物体 pose 均随时间变化。

## 15.5 Object Pose Estimation

目标是估计

\[
{}^WT_O\in SE(3).
\]

对对称物体，多个 pose 可能视觉等价；对软物体，单一刚体 pose 根本不够。评测时必须考虑 symmetry 与 task relevance。

## 15.6 Dynamic Scene State

更完整 world state 可写：

\[
s_t=\{q_t,\dot q_t,\text{objects},\text{contacts},\text{articulation},\text{human},\text{memory}\}.
\]

现代 foundation policy 往往不显式输出这些变量，而存在 hidden state/token 中。但“隐式”不意味着不存在；研究者仍应探测它是否编码了这些因素。

## 15.7 POMDP

POMDP：

\[
(\mathcal S,\mathcal A,T,R,\Omega,O,\gamma).
\]

agent 不能直接看 \(s\)，因此 policy 应基于 belief：

\[
a_t\sim\pi(a\mid b_t).
\]

Memory、world model、active sensing 其实都可放回 POMDP 统一理解。

---

# Part 16　触觉、力觉与接触智能

## 16.1 为什么 Vision 不够

视觉可以看到“手指接近插孔”，却未必知道：

- 是否真正接触；
- 接触在哪；
- 正在滑还是粘；
- 法向力是否过大；
- 软物体内部如何受力。

接触丰富任务因此需要 tactile / force feedback。

## 16.2 Tactile Representation

视觉触觉 observation 常是图像序列：

\[
T_t\in\mathbb R^{H\times W\times C}.
\]

可学习 contact mask、depth/normal、shear、slip latent，或直接端到端输入 policy。关键不是“又加一个 camera”，而是其观测由**接触力学**生成。

## 16.3 Multi-Rate Fusion

视觉语言 reasoning 可能 2–20 Hz，触觉却可几十至数百 Hz。若把触觉简单 downsample 后塞进慢速 VLA，会丢失 slip 等瞬态事件。

更合理的分层：

```text
slow: language + RGB → task / nominal action chunk
fast: tactile + proprioception → residual correction / reflex
```

2026 年 TouchWorld、T-Rex 等工作正体现这种 predictive + reactive / variable-rate 设计趋势。

## 16.4 Tactile World Model

可学习

\[
\hat z_{t+1}^{touch}=F(z_t^{touch},z_t^{vision},a_t),
\]

预测“正常接触应怎样演化”。如果真实 tactile 与预测偏差增大，系统可检测 slip、misalignment 或异常 force，并快速纠正。

## 16.5 Cross-Sensor Tactile Generalization

不同 tactile hardware 的像素外观差异很大。真正可迁移的 representation 应尽量编码 physical contact state，而非特定 elastomer/lighting 外观。2026 年大规模 visuo-tactile 数据与 cross-sensor representation 已成为独立 scaling 方向。

---

# Part 17　主动感知：让机器人决定“下一眼看哪里”

## 17.1 被动感知的局限

如果目标物被遮挡，再强的单帧视觉模型也无法从不存在的光线中恢复确定信息。机器人与普通图像模型最大的区别是：**它可以移动相机、身体或物体来改变未来观测。**

## 17.2 Observability

动态系统的 observability 问：从一段输入输出能否恢复内部 state？对线性系统，可用 observability matrix 判断：

\[
\mathcal O=\begin{bmatrix}C\\CA\\CA^2\\\vdots\end{bmatrix}.
\]

在现代机器人里，这个概念扩展为：当前 viewpoint / sensing action 是否足以辨别任务关键变量？

## 17.3 Next-Best-View

候选视角 \(v\) 可按

\[
U(v)=\mathbb E[\Delta I(v)]-\lambda C(v)-\beta R(v)
\]

排序，其中信息增益、运动成本和安全风险共同决定价值。

NBV 不应只最大化 3D coverage。操作任务真正关心的是**task-relevant uncertainty**，例如插头方向、把手背后空间、抓取面是否被遮挡。

## 17.4 Epistemic-Driven Exploration

若模型对某区域“不知道”，主动移动以降低 epistemic uncertainty。关键是避免把 aleatoric noise 当作可消除不确定性，否则机器人会无限观察一个本来就随机的现象。

## 17.5 View Goal 与 Embodiment-Agnostic Planning

一种有价值的解耦方式是高层输出 desired view / information goal：

\[
g_v=(target,relative\ pose,visibility\ constraints),
\]

再由不同 embodiment 自己完成移动。这样主动感知知识不绑定具体 neck/base/arm DOF，更利于 cross-embodiment。

## 17.6 Active Touch

机器人也可以主动选择接触：轻推判断质量、捏压判断软硬、沿边缘滑动恢复形状。此时 sensing action 本身改变世界，因此必须考虑信息价值与扰动代价。

## 17.7 Perception–Action Loop

真正的主动感知循环：

```text
belief / uncertainty
       ↓
choose sensing action
       ↓
move camera/body/touch
       ↓
new observation
       ↓
update belief
       ↓
execute task or sense again
```

这比“多拍几张图再平均”更接近具身 intelligence。

---

# 本卷的统一表示问题

从最底层到最高层：

```text
photons / force / acceleration
        ↓
raw sensor streams
        ↓
2D / tactile features
        ↓
3D geometry / object / contact
        ↓
state + uncertainty + memory
        ↓
affordance / task-relevant belief
        ↓
decision and action
```

一个 representation 的价值不应只由 reconstruction 或 probe score 判断，而应由它是否让下游预测、规划和控制更可靠来判断。

## 必做实验

1. camera projection / back-projection 与 hand-eye transform；
2. RGB-D 生成 point cloud 并在 world frame 融合；
3. 1D Kalman filter → nonlinear EKF；
4. visual odometry 或小型 pose graph；
5. 给 point cloud/vision encoder 做 geometry probe；
6. 构造遮挡任务，对比 passive vs next-best-view；
7. 触觉或 F/T 信号做 slip/contact event detection；
8. 比较 slow fusion 与 fast residual tactile feedback。

## 推荐资料与 2026 前沿

- Hartley & Zisserman, *Multiple View Geometry*.
- Szeliski, *Computer Vision: Algorithms and Applications*.
- Barfoot, *State Estimation for Robotics*.
- Thrun, Burgard & Fox, *Probabilistic Robotics*.
- Meta V-JEPA 2 / 2.1 — https://github.com/facebookresearch/vjepa2
- TouchWorld (2026), arXiv:2607.07287.
- T-Rex (2026), arXiv:2606.17055.
- Vision-Based Tactile Intelligence for Robotics survey (2026), arXiv:2608.15490.
