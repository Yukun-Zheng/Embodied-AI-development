# Volume IX　仿真、数据基础设施与系统工程

> 机器人研究最容易被低估的部分，是“模型之外的一切”。同一算法在不同 simulator、数据 schema、timestamp 处理、controller、GPU pipeline 上可以得到完全不同结果。本卷把 simulation、synthetic data、sim-to-real、data engineering 和真实部署当成研究对象本身。

---

# Part 40　Physics Simulation 与 Robot Learning Platform

## 40.1 为什么离不开 Simulation

真实机器人数据成本高、并行度低、危险、硬件会磨损。仿真提供：

\[
\text{cheap reset}+\text{parallel rollout}+\text{privileged state}+\text{controlled intervention}.
\]

但 simulator 的价值不是“代替现实”，而是让我们可控地研究哪些变量影响行为。

## 40.2 Physics Engine 的数值本质

连续 dynamics：

\[
M(q)\ddot q+h(q,\dot q)=\tau+J^T\lambda
\]

必须在离散 timestep 上数值积分，同时求接触约束。不同引擎在 contact regularization、constraint solver、friction approximation、integrator 上选择不同，因此相同 URDF 并不必然得到相同物理行为。

## 40.3 Time Step

设仿真步长 \(\Delta t\)。太大：高速碰撞漏检、刚性接触不稳定；太小：计算成本增加。

控制周期还可能是多个 physics step：

\[
\Delta t_{ctrl}=k\Delta t_{sim}.
\]

论文必须同时报告 simulator Hz 与 policy/control Hz。

## 40.4 Contact Solver

常见思想：penalty-based、constraint-based、complementarity approximation。solver iteration 数、contact stiffness/damping 和 friction cone approximation 都会改变插入、抓取、行走行为。

因此接触任务复现时 simulator config 与模型 checkpoint 同样重要。

## 40.5 MuJoCo

MuJoCo 强项：高效刚体/contact simulation、经典控制/RL、MJCF 模型、成熟 CPU 并行生态。适合 locomotion、manipulation、MPC/trajectory optimization 与大批量 RL。

## 40.6 SAPIEN

SAPIEN 面向 manipulation / embodied AI，提供渲染、物理、articulated object 生态，与 ManiSkill 等 benchmark 紧密相关。对精细物体交互和视觉操作研究较方便。

## 40.7 Isaac Sim

Isaac Sim 基于 Omniverse/USD，强调高质量 RTX sensor simulation、复杂场景、工业数字孪生与 ROS 2 / synthetic-data 生态。

它更像完整 robotics simulator/platform，而不仅是一个 physics library。

## 40.8 Isaac Lab

Isaac Lab 在 Isaac Sim 上提供统一 robot-learning framework，覆盖 reinforcement learning、learning from demonstrations、motion planning、domain randomization 等工作流，并利用 GPU parallel simulation。其价值是把环境、资产、传感器、manager、RL/LfD workflow 统一起来。

## 40.9 RoboTwin 与双臂 Benchmark Platform

RoboTwin 类平台的价值在于：将双臂任务、资产、demo collection、policy interfaces、randomization 与 evaluation 固化，使 ACT/DP3/VLA 等方法可以在同一任务分布上比较。

但 benchmark 平台永远只是实验载体，不能把“在 RoboTwin 上领先”直接等同于“真实双臂通用性更强”。

## 40.10 ManiSkill / Habitat / BEHAVIOR / OmniGibson

不同平台服务不同研究问题：

- ManiSkill：manipulation 与 GPU simulation；
- Habitat：large-scale embodied navigation；
- BEHAVIOR / OmniGibson：household activity、复杂对象与长任务；
- MetaWorld / LIBERO：多任务 manipulation 与 continual/generalization 研究。

选 simulator 应从研究问题反推，而不是跟热点。

## 40.11 Robot / Asset Import

一个资产至少包含：

- visual mesh；
- collision mesh；
- mass / inertia；
- material / friction；
- articulation；
- joint limits；
- actuator；
- semantic annotation。

高精视觉 mesh 直接当 collision mesh 会极慢；错误 inertia 则会让 physics 完全不可信。

## 40.12 USD / URDF / MJCF Pipeline

跨平台迁移常见问题：joint axis、coordinate convention、mesh scale、inertia、mimic joint、tendon、actuator gain 丢失。任何 converter 后都应做“静态 + 运动 + 动力学”三层验证，而不是只看模型能显示出来。

## 40.13 Sensors in Simulation

synthetic camera / depth / segmentation 很容易生成，但真实 sensor 的 noise model、exposure、motion blur、depth hole、rolling shutter 未必被模拟。

所谓 photorealistic render 与 sensor-realistic render 是两回事。

## 40.14 Parallel Simulation

若单环境状态 \(x_i\)，批量环境：

\[
X\in\mathbb R^{N\times d}.
\]

GPU/vectorized simulator 能一次推进 thousands envs，显著提高 RL throughput。但同步并行也会产生高度相关 experience，需注意 replay / randomization。

## 40.15 Determinism

即使固定 random seed，也可能因 GPU parallel reduction、physics contact ordering、driver/library 版本产生 non-determinism。

可复现记录至少包括：

```text
simulator commit/version
GPU/driver
physics backend
scene asset hash
time step / substeps
solver iterations
random seeds
robot asset hash
```

## 40.16 Benchmark Platform 的错位

平台设计会决定论文研究什么。如果任务全是无遮挡桌面抓取，研究自然忽略 active perception；如果 reset 永远完美，recovery 不会出现；如果提供 oracle state，视觉 representation 问题被掩盖。

因此 benchmark 本身就是一种 inductive bias。

---

# Part 41　Synthetic Data、Domain Randomization 与 Sim-to-Real

## 41.1 Synthetic Observation

仿真可直接生成：RGB、depth、normal、segmentation、optical flow、object pose、contact、force、privileged state。

这些 label 几乎免费，因此适合 pretraining perception / state estimator。但 synthetic label 的分布偏差仍可能让模型学到 simulator artifact。

## 41.2 Synthetic Trajectory

trajectory 来源可为：

- motion planner；
- scripted controller；
- RL expert；
- privileged policy；
- teleoperation in simulation；
- generative policy/world model。

synthetic trajectory 的关键不是数量，而是覆盖和真实性。

## 41.3 Procedural Scene Generation

通过程序生成房间布局、对象组合、材质、光照、任务条件，可显著增加组合 diversity：

\[
scene\sim p(geometry,object,material,lighting,layout).
\]

如果 generator 分布太窄，模型仍会过拟合 generator 本身。

## 41.4 Domain Randomization

训练时随机化 nuisance：

\[
\phi\sim p(\phi),
\qquad
s_{t+1}=f_\phi(s_t,a_t).
\]

视觉：texture/light/camera；动力学：mass/friction/damping/motor strength；sensor：noise/bias/latency。

思想是让真实世界成为随机化分布中的一个样本。

## 41.5 Dynamics Randomization

若参数范围过窄，真机不在 support；过宽则 policy 变得过度保守、难学。

可根据 system identification posterior 设置：

\[
\phi\sim p(\phi\mid D_{real}).
\]

比盲目 uniform randomization 更有效。

## 41.6 System Identification

通过真实输入输出数据估计参数：

\[
\phi^*=\arg\min_\phi\sum_t\|y_t^{real}-y_t^{sim}(\phi)\|^2.
\]

可估质量、摩擦、motor gain、delay、compliance。复杂系统中参数可能不可辨识，因此应关注 task-relevant identification，而非追求全部物理参数精确。

## 41.7 Sim-to-Real

Sim-to-real gap 可分：

\[
\Delta=\Delta_{visual}+\Delta_{dynamics}+\Delta_{sensor}+\Delta_{control}+\Delta_{task}.
\]

不同任务瓶颈不同。locomotion 往往 dynamics/latency 更关键；vision manipulation 则 camera/geometry/data gap 更大。

## 41.8 Real-to-Sim

从真实图像/扫描重建场景，恢复 object pose / geometry / material / articulation，然后在 simulation 复现任务。它支持 debug、counterfactual 和 policy search。

## 41.9 Real-to-Sim-to-Real

闭环：

```text
real observations
   ↓
reconstruct / identify sim
   ↓
train / plan / generate data
   ↓
deploy real
   ↓
new residual → update sim
```

这是数字孪生比单次 domain randomization 更长期的形式。

## 41.10 Digital Twin

真正 digital twin 不只是 3D mesh，而是与真实设备持续同步的 state + geometry + dynamics + maintenance information。工业机器人可用它做 predictive maintenance、offline validation 和 safe rollout testing。

## 41.11 Generative Scene / Neural Asset

生成模型可以扩大场景/对象资产，但生成视觉质量高不代表 collision/articulation/physical property 正确。机器人资产生成应同时输出：

\[
\text{geometry}+\text{collision}+\text{mass}+\text{joint}+\text{material}+\text{semantics}.
\]

## 41.12 哪些能力适合在 Sim 学

较适合：

- locomotion；
- collision-aware planning；
- gross manipulation；
- state-based RL；
- rare safety scenario；
- high-level curriculum。

较难完全靠 sim：

- fine tactile contact；
- deformable material fidelity；
- wet/slippery surfaces；
- sensor artifacts；
- human interaction nuances；
- open-world household variation。

因此应把 sim 看成 data/source of interventions，而非现实替代品。

---

# Part 42　机器人数据工程

## 42.1 Data Collection System

高质量机器人数据链：

```text
sensors / robot state / command
            ↓
      timestamped recorder
            ↓
     episode segmentation
            ↓
       validation / QA
            ↓
         metadata
            ↓
      storage / index
            ↓
         dataloader
```

任何一环错误都会成为“模型问题”。

## 42.2 Teleoperation Hardware

常见采集接口：VR controller、leader arm、SpaceMouse、joystick、motion capture、exoskeleton、hand tracking、kinesthetic teaching。

采集接口会塑造 action distribution。例如 leader arm 更自然产生 smooth joint/EE trajectory；键鼠可能导致离散、低频动作。

## 42.3 Episode Lifecycle

一个 episode 应有明确：

- start condition；
- task instruction；
- initial state / randomization seed；
- timestamped stream；
- terminal condition；
- success/failure；
- intervention；
- operator / robot metadata。

## 42.4 Timestamp 与 Synchronization

不要用 array index 假装所有传感器同步。每条 stream 都应保存原 timestamp：

\[
(t_i^{cam},I_i),\quad(t_j^{joint},q_j),\quad(t_k^{action},a_k).
\]

训练前再按目标 clock interpolate / nearest-neighbor / hold-last-value，并保存处理规则。

## 42.5 Observation / Action Schema

推荐逻辑层级：

```text
observation/
  images/front
  images/wrist_left
  images/wrist_right
  depth/...
  state/joint_position
  state/joint_velocity
  state/gripper
  force_torque/...
action/
  command
language/
  instruction
metadata/
```

字段应表达语义，而不是 `x1`, `x2`。

## 42.6 Units 与 Frames

每个连续量必须定义：unit、frame、absolute/delta、normalization。

例如：

```text
action.ee_delta.translation: meter, body frame
action.ee_delta.rotation: axis-angle rad, body frame
```

缺少这些元数据，跨实验室 dataset 几乎无法可靠复用。

## 42.7 Data Formats

生态中常见 HDF5、Zarr、RLDS/TFDS、Parquet + video、LeRobotDataset 等。选择取决于：random access、streaming、compression、cloud/distributed training、versioning。

格式不是核心，**schema + metadata + version control** 才是长期价值。

## 42.8 Video Compression

RGB 占存储主体。把每帧 JPEG 单独存通常低效；视频 codec 高压缩但随机访问成本高。大规模 robot corpus 常把 structured state 用 columnar format，视觉用 chunked video，并建立 timestamp/index。

## 42.9 Data Validation

自动 QA：

- missing frame；
- timestamp monotonicity；
- action NaN/out-of-range；
- camera frozen；
- joint discontinuity；
- terminal label；
- episode length；
- success consistency。

训练前先让 dataset 通过 machine-checkable doctor。

## 42.10 Data Cleaning

清洗不是“只保留成功轨迹”。失败与恢复本身有价值。应区分：

- sensor corruption；
- operator mistake；
- policy failure；
- legitimate hard negative；
- recovery trajectory。

只有第一类必然应删除。

## 42.11 Deduplication

大规模 mixed dataset 可能包含近重复 episode。若 train/test 场景和 trajectory 重复，会制造虚假 generalization。需要按 scene/object/task/time/source 做 split，不只随机按 episode 分。

## 42.12 Dataset Mixture

若有多个 dataset：

\[
p(D_k)\propto n_k^\alpha w_k.
\]

\(\alpha<1\) 可防止最大数据源吞噬所有 batch；\(w_k\) 可提升高质量/目标 domain。mixture policy 本身必须作为实验变量记录。

## 42.13 Language Annotation

同一轨迹可有 task name、free-form instruction、subtask、outcome description。语言 annotation 太模板化会让 VLA 通过 instruction shortcut 记 task ID。

应增加 paraphrase 和真实自然语言，但也必须保持 task semantics 可验证。

## 42.14 Failure / Intervention Labels

每次 human intervention 保存：时间、原因、接管前状态、纠正动作、恢复结果。这样后续可训练 failure detector / recovery policy，而不只是把接管片段删掉。

## 42.15 Massive Robot Corpora Dataloader

训练数据加载应支持：

- 多源采样；
- temporal window；
- camera subset；
- action horizon；
- normalization per embodiment；
- asynchronous sensor alignment；
- online augmentation；
- distributed sharding。

如果 dataloader 不能完整复现，模型实验不可复现。

## 42.16 Data Governance

真实家庭机器人数据可能包含人脸、语音、家庭布局和私人信息。数据治理需要 consent、retention、access control、de-identification、audit trail。技术上“能收”不等于研究伦理上“该收”。

## 42.17 Robotics Data Flywheel

```text
model deployment
      ↓
hard/novel/failure episodes
      ↓
automatic + human triage
      ↓
label / reward / correction
      ↓
retrain / post-train
      ↓
regression evaluation
      ↓
new deployment
```

成熟 robotics organization 的核心资产往往不是单个模型，而是这条 flywheel。

---

# Part 43　机器人系统工程与真实部署

## 43.1 从 Python Policy 到 Robot System

研究代码可能是：

```python
obs = env.get_obs()
action = policy(obs)
env.step(action)
```

真机却需要：sensor driver、clock、middleware、state estimator、policy server、controller、safety monitor、logging、watchdog、UI、emergency stop。

## 43.2 ROS 2

ROS 2 提供分布式 robotics middleware。核心实体：node、topic、service、action、parameter、TF。DDS 提供通信层和 QoS。

ROS 2 不是实时 controller 本身，但可承载高层/中层组件。

## 43.3 Topic / Service / Action

- topic：持续 stream；
- service：短 request/response；
- action：长时可取消任务 + feedback。

camera/state 适合 topic，校准请求适合 service，导航到某位置适合 action。

## 43.4 TF / Transform Tree

TF 维护随时间变化的 frame transform。任何 perception-to-control pipeline 都应能回答：

\[
{}^{world}T_{camera}(t),\quad{}^{world}T_{ee}(t).
\]

若 transform timestamp 不匹配图像 timestamp，空间误差会随机器人运动变大。

## 43.5 Real-Time Control

实时不是“平均很快”，而是 deadline 可保证。控制 loop 更关心 worst-case latency / jitter：

\[
T_{loop}=T_{sense}+T_{compute}+T_{comm}+T_{actuate}.
\]

必须满足 \(T_{loop}\le T_{deadline}\) 并控制 jitter。

## 43.6 Multi-Rate Architecture

典型真实系统：

```text
10 kHz       current loop
1 kHz        joint servo
200 Hz       WBC / impedance
50 Hz        state estimator
30 Hz        cameras
5–20 Hz      VLA
0.1–2 Hz     task reasoning / memory planning
```

设计目标是让每个模块只承担适合自己时间尺度的责任。

## 43.7 GPU Inference Pipeline

视觉/VLA pipeline 包含：capture → decode → resize → H2D → model → decode action → safety → command。优化时不能只测 model `forward()`。

端到端 latency：

\[
L_{e2e}=L_{capture}+L_{pre}+L_{transfer}+L_{model}+L_{post}+L_{comm}.
\]

## 43.8 Streaming 与 Zero-Copy

高分辨率多 camera 如果反复 CPU/GPU copy 会成为瓶颈。可使用 pinned memory、shared memory、hardware decode、batched preprocessing、zero-copy transport。

## 43.9 Policy Server vs Onboard

远程 server 有更强 GPU，但引入 network latency/failure；onboard inference 延迟稳定、隐私更好，但算力/功耗有限。

Gemini Robotics On-Device、轻量 SmolVLA 等路线说明端侧 foundation policy 是独立重要方向。

## 43.10 Watchdog 与 Fail-Safe

任何控制服务都应有 heartbeat。若 command timeout：

\[
t-t_{last}>\Delta_{max}
\]

则进入 safe state：hold、slow stop、gravity compensation 或 emergency brake，视机器人类型而定。

## 43.11 Safety Monitor

policy action 在真正执行前经过：

```text
joint limit
velocity/acceleration limit
workspace boundary
collision distance
force/torque limit
human proximity
command freshness
controller state
```

foundation model 不应拥有绕过 hard safety layer 的权限。

## 43.12 Logging 与 Replay

每次实验必须记录：

- raw sensor timestamp；
- policy input/output；
- controller command；
- robot state；
- model/version/hash；
- safety event；
- task metadata。

否则失败后无法重演数据流。

## 43.13 Determinism 与 Reproducibility

真实系统完全 deterministic 很难，但可追踪。至少保证同一个 episode 能回答：

> 当时运行的代码、checkpoint、calibration、配置、硬件和输入究竟是什么？

推荐 immutable experiment manifest。

## 43.14 Deployment Optimization

优化顺序应从 profile 开始：

1. preprocessing bottleneck？
2. vision encoder？
3. action generation steps？
4. CPU/GPU transfer？
5. network？

再选择 quantization、TensorRT/compile、caching、frame reuse、fewer flow/diffusion steps、smaller backbone。

## 43.15 Distributed Training

大 VLA training 受 GPU memory、data throughput、checkpoint IO 约束。常见 data/tensor/pipeline parallel、FSDP/ZeRO。机器人数据视频解码常比模型本身更先成为 input bottleneck。

## 43.16 Robot Deployment Lifecycle

```text
model candidate
  ↓
offline eval
  ↓
simulation
  ↓
shadow / dry-run
  ↓
limited real tasks
  ↓
safety + regression approval
  ↓
production
  ↓
monitor / rollback
```

每个模型都应可回滚到已验证版本。

## 43.17 一次真实机器人实验发生了什么

完整事件链：

1. operator/reset environment；
2. calibration/state health check；
3. sensor streams timestamp；
4. state estimator 更新；
5. task/memory context 构建；
6. policy inference；
7. action conversion；
8. safety filter；
9. controller interpolation；
10. drive execution；
11. physical contact；
12. new observation；
13. progress/failure monitor；
14. logger 落盘；
15. terminal/result classification。

任何论文若只画“RGB → network → action”，都省略了大量真正决定系统行为的机制。

---

# 本卷统一原则

\[
\boxed{\text{Robotics performance} \neq \text{model performance alone}}
\]

更接近：

\[
P_{system}=F(
P_{model},
D_{quality},
S_{timing},
C_{controller},
H_{hardware},
E_{environment}
).
\]

研究者必须把模型外变量当作一等实验变量。

## 必做实验

1. 同一 controller 扫 simulator timestep / contact solver；
2. MuJoCo / SAPIEN / Isaac Lab 复现同一简单动力学任务；
3. domain randomization 范围 ablation；
4. 用真实 rollout 做 system identification；
5. 构建带 timestamp 的 RGB + proprio + action dataset；
6. 人为制造 dropped frame / stale state，验证 dataset doctor；
7. 多 dataset mixture 权重扫描；
8. 搭一个异步 sensor–policy–control pipeline 并测 P50/P95/P99 latency；
9. policy server 断网触发 watchdog；
10. 保存完整 experiment manifest 并从 log 重放一次失败。

## 参考资源

- MuJoCo documentation.
- SAPIEN / ManiSkill ecosystem.
- NVIDIA Isaac Sim documentation.
- Isaac Lab documentation — https://isaac-sim.github.io/IsaacLab/main/
- RoboTwin — https://github.com/RoboTwin-Platform/RoboTwin
- ROS 2 documentation.
- Hugging Face LeRobot / LeRobotDataset.
- Open X-Embodiment / RLDS ecosystem.
