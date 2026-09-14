# Appendices　附录系统

> 本文件提供正文之外的速查、实验规范、技术谱系和研究索引。模型/软件随时间更新；其中涉及前沿的 Atlas 以 **2026-09-14** 为时间截面。

---

# Appendix A　全书数学符号表

| 符号 | 含义 |
|---|---|
| \(q,\dot q,\ddot q\) | 关节位置、速度、加速度 |
| \(x,s\) | 状态 |
| \(o,z\) | observation / latent representation |
| \(a,u,\tau\) | action / control / joint torque |
| \(R\in SO(3)\) | 旋转矩阵 |
| \(T\in SE(3)\) | 刚体位姿 |
| \(V\in\mathbb R^6\) | twist / spatial velocity |
| \(W\in\mathbb R^6\) | wrench |
| \(J(q)\) | manipulator Jacobian |
| \(M(q)\) | mass/inertia matrix |
| \(C(q,\dot q)\dot q\) | Coriolis / centrifugal term |
| \(g(q)\) | gravity term |
| \(\pi(a\mid s)\) | policy |
| \(V^\pi,Q^\pi,A^\pi\) | value, action-value, advantage |
| \(b_t(s)\) | belief state |
| \(E,D\) | encoder / decoder |
| \(f_\theta\) | parameterized model |
| \(D\) | dataset；与 decoder 需按上下文区分 |
| \(H\) | entropy 或 horizon；按上下文区分 |
| \(\gamma\) | discount factor |
| \(\lambda\) | regularization / multiplier |

**记号纪律**：章节第一次使用符号必须定义；frame-dependent 量必须标 frame；所有 tensor 第一次出现必须给 shape。

---

# Appendix B　坐标系与 Rotation Convention 速查

推荐本书默认：

- 右手坐标系；
- column vector；
- \({}^AT_B\)：把 B-frame 坐标转为 A-frame；
- quaternion 正文默认 `wxyz`，代码必须显式注明；
- twist 默认 \([v,\omega]\)，若库使用 \([\omega,v]\) 必须转换。

最常见排错：

```text
1. 单位：m / mm？rad / deg？
2. transform 方向：A_T_B 还是 B_T_A？
3. active / passive rotation？
4. quaternion wxyz / xyzw？
5. Euler intrinsic / extrinsic、XYZ / ZYX？
6. delta pose 在 world / body frame？
7. timestamp 对齐了吗？
```

---

# Appendix C　SO(3) / SE(3) 公式速查

\[
SO(3)=\{R:R^TR=I,\det R=1\}
\]

\[
T=\begin{bmatrix}R&p\\0&1\end{bmatrix},\qquad
T^{-1}=\begin{bmatrix}R^T&-R^Tp\\0&1\end{bmatrix}
\]

Rodrigues：

\[
\exp(\hat\omega\theta)=I+\sin\theta\hat\omega+(1-\cos\theta)\hat\omega^2.
\]

Pose composition：

\[
{}^AT_C={}^AT_B{}^BT_C.
\]

**代码验证规则**：每个 transform 函数都做 identity、inverse、composition、random round-trip 四类 unit test。

---

# Appendix D　运动学 / 动力学公式表

\[
T(q)=e^{[S_1]q_1}\cdots e^{[S_n]q_n}M
\]

\[
V=J(q)\dot q
\]

\[
\dot q=J^+V+(I-J^+J)z
\]

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J^TF_{ext}
\]

\[
\|f_t\|\le\mu f_n
\]

\[
J_c\ddot q+\dot J_c\dot q=0
\]

---

# Appendix E　Control / Planning 速查

PID：

\[
u=K_Pe+K_I\int e\,dt+K_D\dot e
\]

LQR：

\[
J=\sum x^TQx+u^TRu,\qquad u=-Kx
\]

MPC：每次解 horizon \(H\)，只执行第一段。

CBF：

\[
\dot h(x,u)+\alpha(h(x))\ge0
\]

Planner 选型：

| 问题 | 常用方法 |
|---|---|
| grid / topology | A*, Dijkstra |
| high-dimensional geometry | PRM / RRT / RRT* |
| smooth constrained trajectory | TrajOpt / CHOMP / optimization |
| dynamics-aware | kinodynamic planning / MPC |
| symbolic + geometry | TAMP |
| uncertainty | belief-space planning |

---

# Appendix F　PyTorch / JAX 最小实现原则

本书代码约定：

1. 先写 NumPy/纯数学最小版；
2. 再写 batched tensor 版；
3. 每个 tensor 旁注 shape；
4. forward 与 loss 独立；
5. 固定 seed 不能被当作完全 deterministic 保证；
6. 每个数学模块有 gradient / finite-difference test；
7. 模型之外的 normalization、frame conversion 单独单测。

---

# Appendix G　ROS 2 / TF / Real-Time System 速查

```text
Topic   = continuous stream
Service = short request / response
Action  = long-running goal + feedback + cancel
TF      = time-dependent transform tree
```

部署 checklist：

- QoS 与 sensor semantics 匹配；
- 每个 message 有 timestamp；
- TF lookup 使用对应 sensor time；
- control path 不依赖不确定延迟的 UI/network；
- watchdog 独立于 policy；
- E-stop 不通过 foundation model。

---

# Appendix H　Simulator 选型

| 平台 | 典型优势 | 注意 |
|---|---|---|
| MuJoCo | 高效刚体、RL/control | 复杂 photorealistic scene 非核心 |
| SAPIEN / ManiSkill | manipulation、articulation、GPU | 平台 task assumptions |
| Isaac Sim | RTX sensor、USD、digital twin | 系统较重 |
| Isaac Lab | GPU robot learning workflow | 依赖 Isaac Sim stack |
| Habitat | navigation | 非精细接触主场 |
| OmniGibson / BEHAVIOR | household activities | 复杂、资源需求高 |
| RoboTwin | bimanual learning/evaluation | benchmark ≠ whole real world |

选平台先写 research question，再写需要的 physics / sensor / scale。

---

# Appendix I　Robot Dataset Schema 与 Action Convention

每个 dataset README 必须回答：

```text
observation modalities?
state definition?
action semantics?
absolute or delta?
world/body/end-effector frame?
units?
frequency?
chunk horizon?
low-level controller?
robot morphology?
success/failure/intervention labels?
timestamps?
```

跨数据集训练前做 schema adapter，而不是在 model 内偷偷兼容。

---

# Appendix J　Teleoperation 与数据采集 Checklist

采集前：calibration、clock、storage、task definition、safety、operator training。

采集中：monitor dropped frames、action saturation、latency、success/failure、operator intervention。

采集后：automatic validation、episode review、failure tagging、hash/version、train/test split provenance。

---

# Appendix K　Sim-to-Real Checklist

1. real/sim robot geometry 一致？
2. joint limit / actuator semantics 一致？
3. action/control frequency 一致？
4. latency 是否模拟？
5. friction/mass/motor gain 是否辨识？
6. camera pose / noise 是否接近？
7. controller gain 是否一致？
8. domain randomization 是否覆盖 real residual？
9. 先低速/低力 rollout？
10. 真机 failure 是否回馈 simulation？

---

# Appendix L　真实机器人 Safety Checklist

**实验前**：workspace 清空、E-stop 可达、速度/力限制、human exclusion zone、通信 watchdog、模型 hash、safe pose。

**实验中**：一名 operator 负责 stop；不让无验证 policy 拥有无限权限；实时 monitor force/current/joint error。

**实验后**：记录所有 near-miss / intervention，不只成功率。

---

# Appendix M　Benchmark / Evaluation Checklist

- Train/test 是否真正分离？
- pretraining contamination 是否讨论？
- trial 数足够？
- multiple seeds？
- success detector 是否客观？
- latency / intervention / failure 是否报告？
- OOD 类型是否明确？
- controller/hardware 是否公平？
- baseline data/compute 是否匹配？
- raw failures 是否公开或至少统计？

---

# Appendix N　Reproducibility Checklist

保存：

```text
Git commit
uncommitted diff
Python + packages
CUDA/driver (if relevant)
simulator version
asset hashes
checkpoint hash
dataset version
config
seeds
hardware
raw logs
metric script version
```

任何表格应能由 raw log 自动生成。

---

# Appendix O　经典教材与公开课程地图

**机器人学**：Modern Robotics；Robotics: Modelling, Planning and Control；Robot Modeling and Control。

**控制**：Underactuated Robotics；Feedback Systems；optimal control/MPC courses。

**状态估计**：Probabilistic Robotics；State Estimation for Robotics。

**规划**：Planning Algorithms。

**优化**：Convex Optimization。

**RL**：Sutton & Barto；Deep RL / Offline RL 课程。

学习顺序不是按书名，而是：线代/微分 → SE(3) → kinematics/dynamics → control → estimation/planning → robot learning。

---

# Appendix P　1950–2026 技术时间线（压缩版）

- 1940s–50s：控制论、反馈、早期 AI；
- 1960s：Shakey / symbolic planning；
- 1980s：behavior-based robotics、operational-space control；
- 1990s–2000s：SLAM、sampling-based planning、probabilistic robotics；
- 2010s：deep perception、deep RL、large-scale sim-to-real；
- 2018–2021：Transformer、多任务 robot learning、diffusion/large-scale representation；
- 2022：Gato、SayCan、PaLM-E 前后 generalist/LLM robotics；
- 2023：RT-2、Open X-Embodiment、Diffusion Policy、ALOHA/ACT 生态；
- 2024：Octo、OpenVLA、π0、robot foundation policy 开源化；
- 2025：π0.5、RTC、π*0.6、GR00T N1/N1.5、Gemini Robotics 1/1.5、Helix、V-JEPA 2；
- 2026：π0.7、multi-scale embodied memory、efficient online RL、GR00T N1.6、Gemini Robotics 2 / On-Device 2、V-JEPA 2.1、world-action-model/tactile foundation model 等方向进一步形成。

时间线用于定位问题演化，不用于把“年份更新”误认为“科学进步”。

---

# Appendix Q　2016–2026 Robot Learning 关键谱系

建议按问题读而非按年份背：

```text
Imitation:
BC → DAgger → large demonstrations → action chunking / ACT

Continuous multimodal actions:
mixture models → Diffusion Policy → flow matching action experts

RL:
PPO/SAC → offline RL → demonstration + RL → foundation-policy online RL

Sim-to-real:
domain randomization → privileged learning → massively parallel GPU RL

Generalist:
multi-task policies → Gato/RT-1 → Open X/RT-X → Octo/OpenVLA → modern VLA
```

---

# Appendix R　2022–2026 Robotics Foundation Model / VLA Atlas

| 路线 | 核心接口 / 贡献 |
|---|---|
| Gato | multi-domain sequence modeling |
| SayCan | LLM semantic score × skill affordance |
| PaLM-E | sensor embeddings into embodied LM |
| RT-1 | scaled multi-task robot Transformer |
| RT-2 | web VLM knowledge → action tokens |
| Open X / RT-X | cross-embodiment data scaling |
| RoboCat | self-improving generalist concept |
| Octo | open generalist transformer + diffusion |
| OpenVLA | open VLM → action-token VLA |
| π0 | VLM + continuous flow action expert |
| π0.5 | open-world / high–low-level joint generalization |
| RTC | latency-aware real-time chunk execution |
| π*0.6 | experience / RL post-training |
| MEM | multi-scale embodied memory |
| π0.7 | richer context / steerability / emergent generalization |
| GR00T N1.x | humanoid, human/sim/robot data, whole-body scaling |
| Gemini Robotics | VLA + embodied reasoning hierarchy |
| Gemini Robotics 2 | whole-body, dexterity, multi-robot, on-device |
| Helix | industrial humanoid generalist upper-body control |
| SmolVLA | compact open flow-based VLA |

不要把 Atlas 当排名表；每个模型应回到正文的统一系统框架比较。

---

# Appendix S　2024–2026 World Model / Video / JEPA Atlas

主要轴：

1. pixel/video generation；
2. latent predictive representation；
3. action-conditioned world model；
4. joint world-action model；
5. world model as simulator/evaluator；
6. object/contact/robot-factored inductive bias。

代表方向：V-JEPA 2/2.1、action-conditioned JEPA、robot video world models、FLARE/future-latent objectives、RoboWM-Bench、OSCAR、robot-factored world models、joint video-action models。

统一评价：**action fidelity、physical executability、counterfactual correctness、downstream control utility**。

---

# Appendix T　2024–2026 Humanoid / Whole-Body Learning Atlas

技术链：

```text
motion retargeting / imitation
→ proprioceptive RL locomotion
→ whole-body control / loco-manipulation
→ human-video scaling
→ humanoid foundation policy
→ whole-body VLA / reasoning / dexterity
```

研究时始终区分：motion tracking、command locomotion、loco-manipulation、upper-body VLA、full-body VLA。

---

# Appendix U　2024–2026 Dexterity / Tactile Atlas

核心路线：

- dexterous-hand RL；
- human-hand retargeting；
- tactile representation；
- visuo-tactile policy；
- high-frequency tactile residual；
- tactile predictive/world model；
- cross-sensor tactile foundation representation；
- bimanual/dexterous VLA。

触觉的核心不是增加 modality 数，而是为**接触状态**提供高频直接观测。

---

# Appendix V　Datasets / Benchmarks / Simulators Atlas

按问题分类，而非“谁最火”：

| 类别 | 例子 |
|---|---|
| cross-robot data | Open X-Embodiment、LeRobot ecosystem |
| multitask manipulation | RLBench、MetaWorld、LIBERO、ManiSkill |
| bimanual | ALOHA-style datasets、RoboTwin |
| navigation | Habitat ecosystem |
| household activity | BEHAVIOR / OmniGibson |
| humanoid | motion datasets + simulator-specific task suites |
| simulator | MuJoCo、SAPIEN、Isaac Sim/Lab |

使用任何 benchmark 前先读 task generation、reset、action interface 和 success detector。

---

# Appendix W　Open-Source Codebase 与复现索引

建议至少熟悉：

- Modern Robotics code；
- MuJoCo；
- Isaac Lab；
- SAPIEN / ManiSkill；
- LeRobot；
- Diffusion Policy；
- ACT/ALOHA implementations；
- OpenVLA；
- OpenPI / open π-family code when available；
- GR00T open stack；
- V-JEPA 2；
- RoboTwin。

复现顺序：**读算法 → 画数据流 → 跑最小 example → 对齐数据/action → reproduce metric → reproduce ablation**。

---

# Appendix X　Research Question Bank

1. 什么视觉变量真正决定 manipulation success？
2. 主动视角是否比扩大视觉 backbone 更有效？
3. world-model prediction quality 在什么条件下真正改善 policy？
4. tactile feedback 应进入 VLA backbone 还是独立快速回路？
5. cross-embodiment 最合适的 invariant 是 geometry、effect 还是 mechanism？
6. 真实 online RL 如何控制 regression risk？
7. action chunk 长度与 dynamics / latency 的最优关系是什么？
8. 长期 memory 应按视觉、语言还是事件存储？
9. 哪些任务必须显式 contact state？
10. human video transfer 的瓶颈来自 representation 还是 embodiment mapping？
11. whole-body VLA 是否应直接输出全部 joint？
12. 如何定量区分 memorization、composition 与 mechanism discovery？
13. structural plasticity 能否在固定 compute budget 下提高长期能力增长？
14. 能否构造可证伪的“physical understanding”测试？
15. benchmark 如何避免 foundation-model contamination？

每个问题都应进一步写成 hypothesis + minimal falsification experiment。

---

# Appendix Y　Failure Mode Taxonomy

一级分类：

```text
P  Perception
S  State estimation / memory
R  Reasoning / planning
A  Action generation
K  Kinematics / planning feasibility
C  Control / contact
H  Hardware
T  Timing / communication
L  Learning / distribution shift
F  Foundation-model semantic failure
X  Safety / human interaction
```

每次 episode failure 至少记录：类别、timestamp、first observable symptom、root-cause confidence、recovery、是否应进入训练集。

---

# Appendix Z　术语中英对照索引

完整版本见 `book/GLOSSARY.md`。建议写作中第一次出现使用：

> 中文术语（English Term, abbreviation）

后续选定一种稳定表达，不在“本体/形态/身体”“策略/policy”等同义词间随意漂移。

---

# 附录维护规则

- A–N 属于稳定技术速查，修改需保证与正文符号一致；
- O–W 属于动态 Atlas，允许按版本更新；
- X–Y 属于研究工具，应随着失败与研究问题持续扩充；
- Z 与 `GLOSSARY.md` 保持同步；
- 新模型默认进入 R/S/T/U/W，而不是修改正文一级知识结构，除非它真的引入新的独立范式。
