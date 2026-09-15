# Part 12　机器人传感器、标定与时间

## 学习目标

本章建立机器人 observation 的物理来源。读完后应能解释 RGB/depth/LiDAR/IMU/encoder/F-T/tactile/event camera 各自测什么、误差从哪里来；掌握 camera intrinsics/extrinsics、hand–eye calibration、sensor synchronization；理解 timestamp 与 latency 为什么不是工程附录，而是具身系统状态定义的一部分。

---

## 12.1 从物理量到 Observation

传感器不是直接“读取真实状态”，而是通过测量过程：

\[
o_t=h(s_t;\phi)+\epsilon_t,
\]

其中 \(s_t\) 是真实物理状态，\(h\) 是 sensor model，\(\phi\) 是 calibration parameter，\(\epsilon_t\) 是噪声。

同一个世界状态可能因为 exposure、视角、反光、bias、时间延迟产生不同 observation。模型学习的不是“现实本身”，而是现实经过 sensor pipeline 后的投影。

## 12.2 相机成像模型

Pinhole camera：相机坐标点

\[
P_c=(X,Y,Z)^T
\]

投影到像素：

\[
u=f_x\frac{X}{Z}+c_x,
\qquad
v=f_y\frac{Y}{Z}+c_y.
\]

齐次形式：

\[
\tilde p\sim K P_c,
\]

\[
K=
\begin{bmatrix}
f_x&s&c_x\\
0&f_y&c_y\\
0&0&1
\end{bmatrix}.
\]

\(f_x,f_y\) 是 pixel focal length，\((c_x,c_y)\) 是 principal point，\(s\) 通常近似 0。

## 12.3 Intrinsics 与 Distortion

真实镜头会有 radial / tangential distortion。常见 radial 模型：

\[
x_d=x(1+k_1r^2+k_2r^4+k_3r^6)+\cdots
\]

广角/fisheye camera 需要不同投影模型。

如果模型训练时图像已经 rectified，但部署时直接输入 raw fisheye，视觉分布会系统性变化。

## 12.4 Extrinsics

World point 先变到 camera frame：

\[
{}^CP={}^CT_W{}^WP.
\]

再投影到像素。

对于 wrist camera，extrinsic 随 robot joint 变化，但 hand-to-camera 固定：

\[
{}^WT_C(t)={}^WT_{EE}(t){}^{EE}T_C.
\]

因此 wrist-camera 视觉与 joint state 必须时间同步，否则使用的是错误 camera pose。

## 12.5 Back-Projection

已知 depth \(Z\)：

\[
X=(u-c_x)Z/f_x,
\qquad
Y=(v-c_y)Z/f_y.
\]

于是 RGB-D 可恢复 camera-frame point cloud：

\[
P_c\in\mathbb R^{N\times3}.
\]

再通过 extrinsics 转到 world/base frame。

## 12.6 Stereo Vision

理想 rectified stereo：

\[
Z=\frac{fB}{d},
\]

其中 baseline \(B\)，disparity \(d=u_L-u_R\)。

当 \(d\) 很小时，深度误差被放大，因此远距离 stereo precision 下降。

## 12.7 Structured Light / Time-of-Flight

Depth camera 常见：

- structured light：投射已知 pattern，通过变形三角测距；
- time-of-flight：测光飞行时间/相位差；
- active stereo：主动纹理辅助匹配。

透明、镜面、黑色材质、多路径、边缘都会导致 depth hole 或错误值。

真实 robot point cloud 远不像 simulator Z-buffer 那么干净。

## 12.8 LiDAR

LiDAR 直接获得距离与角度：

\[
p_i=r_i
\begin{bmatrix}
\cos\theta_i\cos\phi_i\\
\sin\theta_i\cos\phi_i\\
\sin\phi_i
\end{bmatrix}.
\]

优点是几何稳定、量程大；缺点是稀疏、材质依赖、成本/体积与 motion distortion。

移动平台常结合 LiDAR + IMU 做 odometry/SLAM。

## 12.9 IMU

Gyroscope：

\[
\omega_m=\omega+b_g+n_g.
\]

Accelerometer：

\[
a_m=R^T(a-g)+b_a+n_a.
\]

bias \(b_g,b_a\) 随时间漂移。直接积分：

\[
R_{t+1}=R_t\exp(\hat\omega\Delta t)
\]

会累积 drift，因此需要视觉/LiDAR/contact 等外部观测校正。

## 12.10 Encoder 与 Proprioception

Joint encoder 给 \(q\)；velocity 可由硬件直接测或差分估计：

\[
\dot q_t\approx\frac{q_t-q_{t-1}}{\Delta t}.
\]

简单差分会放大高频噪声，常配 low-pass / observer。

Proprioception 通常比 camera 更低 latency，是 locomotion 和 fast manipulation 稳定闭环的核心。

## 12.11 Motor Current 与 Torque Estimate

近似：

\[
\tau\approx k_t i\cdot N\eta.
\]

但 gearbox friction、temperature、current controller、elasticity 都使它与真实 joint torque 有偏差。

可以做粗 contact detection，但不能无条件替代 calibrated torque/F-T sensor。

## 12.12 Force/Torque Sensor

六轴 sensor 输出：

\[
w_s=[F_x,F_y,F_z,\tau_x,\tau_y,\tau_z]^T.
\]

若 sensor 位于 wrist，还必须减去 tool gravity：

\[
w_{contact}=w_{measured}-w_{gravity}-w_{inertial}-b.
\]

重力补偿依赖 tool mass、COM、orientation。

## 12.13 Tactile Sensor

触觉测接触区域中的 pressure/deformation/shear/slip。视觉触觉通过观察 elastomer 的形变，把 contact 转换成高分辨率图像。

触觉与普通 RGB 的关键差别：其 observation 是**接触力学直接产生**，因此对遮挡后的局部 interaction 特别有价值。

## 12.14 Event Camera

Event camera 不按固定 frame rate 输出图像，而在 log intensity 变化超过 threshold 时产生：

\[
e_i=(x_i,y_i,t_i,p_i).
\]

优点：微秒级 temporal resolution、高 dynamic range；适合高速运动、低延迟 control。但 data representation 与传统 frame model 不同。

## 12.15 Audio

音频可用于：碰撞事件、机械故障、材料接触、语音交互。它是低成本但常被忽略的 modality。

例如倒水任务中，声音变化可能比视觉更早指示容器接近满。

## 12.16 Sensor Noise

噪声不应笼统写成 Gaussian。常见：

- white noise；
- bias drift；
- quantization；
- missing data；
- saturation；
- dead pixel；
- structured depth artifacts；
- correlated temporal noise。

训练 random noise 只有匹配真实 failure mode 才有价值。

## 12.17 Calibration 层级

完整 calibration 至少包括：

1. intrinsic；
2. camera extrinsic；
3. hand–eye；
4. robot kinematic parameter；
5. joint zero；
6. force/tactile bias；
7. clock offset；
8. actuator gain/latency。

一个 robot policy performance 下降，首先要排除 calibration drift，再怀疑 architecture。

## 12.18 Hand–Eye Calibration

经典形式：

\[
AX=XB.
\]

A 是机器人末端在两次姿态之间的运动，B 是 camera 观测到 calibration target 的相对运动，X 是未知 hand-to-camera transform。

标定 pose 必须具有足够 rotational / translational excitation，否则问题 ill-conditioned。

## 12.19 Kinematic Calibration

真实 link length、joint axis、zero offset 与 CAD 有误差。可利用 marker / tracker 观测末端 pose，优化：

\[
\phi^*=\arg\min_\phi\sum_i
\|\log(T_{obs,i}^{-1}FK(q_i;\phi))\|^2.
\]

对于毫米级 insertion，kinematic calibration 往往比换更大模型更重要。

## 12.20 Timestamp

每条 observation 必须携带 measurement time：

\[
(t_i,o_i).
\]

不要把“消息到达电脑的时间”当作“传感器采样时间”。网络/驱动 buffering 会让二者不同。

## 12.21 Synchronization

Camera 30 Hz、joint state 500 Hz、F/T 1 kHz。训练一个 observation window 时需要映射到共同时钟。

可使用：

- nearest neighbor；
- interpolation；
- hold-last-value；
- hardware trigger；
- clock synchronization。

每种方法隐含不同时间误差。

## 12.22 Motion-Induced Temporal Error

若 robot 末端速度 \(v\)，timestamp error \(\Delta t\)，则位置误差近似：

\[
\Delta x\approx v\Delta t.
\]

高速 motion 下 50 ms 已可能对应数厘米偏差。

所以“视觉 pose 很准”但 timestamp 错了，最终 grasp 仍会失败。

## 12.23 Rolling Shutter

很多 camera 每行曝光时间不同。高速运动时一张图本身对应多个时刻。普通 pinhole + single pose 模型因此失效。

高动态机器人应考虑 global shutter 或 motion compensation。

## 12.24 Observation Packet

工程上建议 observation 不只是 tensor，而是带 metadata 的 packet：

```text
modality
payload
timestamp
frame_id
unit
calibration_id
validity / confidence
```

这比把所有东西先 resize/concat 成网络输入更可调试、更可迁移。

## 常见失败

- depth 单位 mm 当 m；
- camera extrinsic 反向；
- wrist-camera frame 与 joint state 不同步；
- F/T 没做 tool gravity compensation；
- camera 自动曝光导致视觉分布变化；
- IMU bias 未估计；
- replay dataset 丢失原 timestamp；
- simulator sensor 太理想，真机 policy 崩溃。

## 最小实验

让机械臂末端以 0.5 m/s 横向运动，模拟 camera 延迟 0–200 ms。使用“当前 joint pose + 旧图像”计算物体 world pose，画定位误差随 latency 的关系。然后用 timestamp interpolation 修正，比较恢复程度。

## 研究问题

1. Foundation policy 应直接接 raw asynchronous stream，还是先由 state estimator 对齐？
2. 多模态 token 是否需要显式携带 timestamp/frame metadata？
3. 能否让模型主动判断 sensor calibration 已经漂移？

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 12`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-12)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
