# Embodied Intelligence Laboratory Curriculum

> 配套《具身智能：从物理世界到通用机器人》v1.0。实验不是“照 README 跑通”，而是要求读者测量机制、做失败分析、保存可复现实验记录。

## 统一实验规范

每个 Lab 必须提交：

1. `README.md`：研究问题与假设；
2. `config/`：所有参数；
3. `src/`：可运行代码；
4. `runs/`：seed / commit / environment manifest；
5. `results.csv`：原始指标；
6. `figures/`：由脚本自动生成；
7. `FAILURES.md`：至少 5 个失败案例；
8. `REPORT.md`：结论、负对照、局限。

统一原则：**先最小实验，再大模型；先机制，再 leaderboard。**

---

# Track A　数学、几何与经典机器人

## Lab 01　矩阵、Jacobian 与自动微分

**目标**：把多元微分从公式变成可计算对象。

- 手算二维函数 Jacobian；
- PyTorch/JAX autodiff 验证；
- 对数值 finite difference；
- 扫 step size，观察 truncation / floating-point error。

**指标**：analytic vs autodiff vs finite-difference error。

## Lab 02　2-Link Planar Arm

实现：

\[
(x,y)=FK(q_1,q_2)
\]

并手推 Jacobian。可视化 workspace、singularity、manipulability。

**负对照**：在奇异附近直接 pseudoinverse vs DLS。

## Lab 03　SO(3) / SE(3)

实现 rotation matrix、axis-angle、quaternion、exp/log map、pose composition。随机生成 10,000 个 rotation 做 round-trip test。

**必须故意制造**：`wxyz/xyzw`、world↔camera、degree/radian 三类 convention bug，并记录表现。

## Lab 04　Numerical IK

用 6/7-DOF arm：

- pseudoinverse IK；
- DLS；
- null-space joint-limit avoidance；
- collision-aware IK。

**指标**：pose error、iterations、failure rate、max joint velocity。

## Lab 05　Rigid-Body Dynamics

对 2-link arm 推导 \(M,C,g\)，实现 forward dynamics；与 simulator 对比。

**实验**：改变 mass/inertia，观察 trajectory。

## Lab 06　PID / Computed Torque / Impedance

同一 tracking task 比较：

- PD/PID；
- computed torque；
- impedance control。

加入外力扰动与 contact，比较 tracking error 和 peak force。

## Lab 07　Planning

实现 A*、RRT、RRT*；再用 trajectory optimization 平滑。

**指标**：planning time、path length、collision margin、success rate。

---

# Track B　感知、状态与主动获取信息

## Lab 08　Camera Geometry

从 intrinsic/extrinsic 把 world point 投影到 RGB，再用 depth back-project 到 3D。

**指标**：reprojection error；extrinsic 扰动 1–50 mm 对 grasp target 的影响。

## Lab 09　RGB-D Point Cloud

融合多视角 RGB-D 到 world frame；实现 voxel downsample / crop / object segmentation。

**问题**：相机 pose error 与 depth noise 哪个更影响 downstream grasp？

## Lab 10　Kalman → EKF

从一维 constant-velocity KF 开始，再做移动机器人 nonlinear EKF。

**指标**：RMSE、NIS/calibration、不同 Q/R 配置。

## Lab 11　Pose Graph / Tiny SLAM

构造 2D/3D pose graph，加入 loop closure，做 nonlinear least squares。

**观察**：没有 loop closure 时 drift 怎样积累。

## Lab 12　Visual Representation Probe

选两个 vision encoder，在同一 robot dataset 上 probe：

- object semantics；
- relative depth；
- object pose；
- contact point；
- task progress。

最后比较 downstream policy，而非只比较 probe score。

## Lab 13　Active Perception

构造遮挡 manipulation toy task：

- fixed camera；
- random view；
- next-best-view by information gain。

**指标**：task success、额外运动距离、information gain、decision latency。

## Lab 14　Force / Tactile Reflex

在 simulation 或真实传感器上检测 contact/slip；实现快速 residual correction。

比较 slow VLA-only loop 与 VLA + fast tactile loop。

---

# Track C　Imitation、RL 与生成式策略

## Lab 15　Behavior Cloning

在 Push-T / simple manipulation 上 BC。

记录 offline validation loss 与 rollout success，展示两者不一致。

## Lab 16　DAgger

固定 expert-query budget，比 BC 与 DAgger。

**核心图**：visited-state distribution 随 iteration 的变化。

## Lab 17　ACT / Action Chunking

扫描 chunk horizon \(H\)：1, 5, 10, 20, 50。

**指标**：success、smoothness、feedback delay、latency。

## Lab 18　PPO Locomotion

在 Isaac Lab / MuJoCo 做 legged locomotion。

必须做 reward ablation：移除 smoothness、foot-contact、energy 等项，分析 gait 变化。

## Lab 19　Offline RL

从固定 demonstration + imperfect data 训练 offline RL。

可视化 critic 对 dataset 内外 action 的 Q 估计，观察 extrapolation error。

## Lab 20　Diffusion Policy

同一 observation 采样多条 action trajectory；可视化 multimodality。

扫描 diffusion steps，画 success–latency curve。

## Lab 21　Flow Matching Policy

实现最小 conditional flow matching action generator，与 diffusion 在相同 backbone/data 对比。

**控制变量**：参数、数据、action horizon。

## Lab 22　Asynchronous Policy Execution

人为加入 0/50/100/250/500 ms inference delay。

比较 synchronous chunk、trajectory blending、asynchronous queue / RTC-like correction。

---

# Track D　VLA 与 Foundation Policy

## Lab 23　Action-Token VLA

使用开放 VLA / 小型模型：

- 明确 vision tokens；
- language tokens；
- state tokens；
- action tokenization；
- action decode。

把每层 tensor shape 记录成 diagram。

## Lab 24　Continuous Action Expert VLA

使用 SmolVLA / open π-style flow expert 或自建小模型，与 Lab 23 用同一数据比较。

**核心问题**：continuous action expert 是否改善 precision / latency？

## Lab 25　VLA Visual Intervention

固定 instruction，改变：object position、texture、background、camera angle、irrelevant distractor。

测 action / success sensitivity，判断模型是否真正使用 task-relevant vision。

## Lab 26　Cross-Embodiment

用两个不同 arm / action spaces：

- robot-specific heads；
- universal EE action；
- morphology-conditioned policy。

在 held-out body variant 上测 few-shot / zero-shot adaptation。

## Lab 27　Long-Horizon VLA + Memory

构造 5–20 subtask 环境。

比较：无 memory、frame context、episodic log、semantic long-term memory。

**负对照**：shuffled/unrelated memory。

---

# Track E　World Model、Reasoning 与持续学习

## Lab 28　Latent World Model

学习

\[
z_{t+1}=f(z_t,a_t)
\]

测 1/5/10/20-step prediction error，并与 control performance 关联。

## Lab 29　World Model MPC

在 learned dynamics 上 sample action sequences、预测 future、选最优执行第一步。

扫描 planning horizon，观察 model bias 何时超过 planning benefit。

## Lab 30　Video World Model Executability

对同一 initial state + two actions 生成未来。

把预测未来转为 action/inverse dynamics 再执行，测“视频质量”与“可执行成功率”的相关性。

## Lab 31　Reasoning Negative Control

让高层 planner 产生 plan；比较：

- correct reasoning；
- random plan；
- semantically fluent but wrong plan；
- no plan。

只在行为显著受正确 reasoning 因果影响时，才认为 reasoning 有用。

## Lab 32　Experience Learning Flywheel

流程：base policy → autonomous rollout → failure mining → correction → retrain。

记录每轮：success、intervention、new-data volume、old-task regression。

## Lab 33　Continual Learning

Sequential A→B→C tasks；比较 naive fine-tune、replay、adapter、regularization。

指标：Average Accuracy、Forgetting、Forward Transfer、Backward Transfer。

## Lab 34　Self-Generated Curriculum

让 agent 按 learning progress 从任务池选择 practice goal。

**对照**：uniform、fixed curriculum、hardest-first。

---

# Track F　Humanoid、Whole-Body 与系统工程

## Lab 35　Humanoid Retargeting

human motion → humanoid joint/EE targets；加入 foot contact、joint limit、balance constraint。

评测 pose tracking + physical feasibility。

## Lab 36　Whole-Body Locomotion + Manipulation

一个 humanoid 需要走到目标、伸手、抓取、搬运。

比较：locomotion/arm 分层 vs unified whole-body policy。

## Lab 37　Bimanual Coordination

做共同搬物 / handover。

比较独立双臂 policy 与 relative-frame/coordinated policy。

## Lab 38　Multi-Robot Collaboration

两个 heterogeneous robot 完成 task allocation + execution。

加入 communication delay/dropout、single-agent failure。

## Lab 39　ROS 2 / Multi-Rate Deployment

搭：camera node、state node、policy node、controller node、safety node、logger。

记录端到端 P50/P95/P99 latency 与 jitter。

## Lab 40　Watchdog / Safety Shield

故意制造：model timeout、stale camera、unsafe joint target、human proximity。

系统必须自动 safe-stop / reject / ask-human，并保留完整 audit log。

---

# Capstone 1　统一 RoboTwin / Manipulation Arena

在统一任务、数据与 action convention 下复现至少：

1. ACT；
2. Diffusion Policy / DP3；
3. 一种 flow policy；
4. 一种 VLA。

要求固定：dataset split、camera、controller、training steps、evaluation seeds。

最终报告不是“谁分最高”，而是：

- visual reliance；
- latency；
- data efficiency；
- recovery；
- OOD matrix；
- failure taxonomy。

# Capstone 2　Humanoid Developmental Agent

在 Isaac Lab 中构造长期环境序列 A→B→C：

- locomotion；
- manipulation；
- active exploration；
- new scene；
- previous-scene revisit。

系统维护 memory / skill / world model，并允许有限 online adaptation。

最终指标：

\[
\text{plasticity},\ 
\text{retention},\ 
\text{forward transfer},\ 
\text{recovery},\ 
\text{compute per capability gain}.
\]

# Capstone 3　一个可证伪的新架构

最终不是复现，而是独立提出 hypothesis：

> Existing systems fail at **X** because they lack **Y mechanism**. We introduce **Z**, predicting measurable gains under **C**, but not under **D**.

必须包含：

- minimal toy falsification；
- parameter/data-matched baseline；
- negative control；
- standardized benchmark；
- real/sim transfer if relevant；
- failure cases；
- compute/data accounting。

这才是从“学完教材”进入独立具身研究的毕业标准。
