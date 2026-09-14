# Exercises — Part 0–50 章末题

> 每个 Part 固定四类题：**C（Concept）概念题、M（Mathematics）推导题、I（Implementation）实现题、R（Research）研究/证伪题**。共 51 × 4 = **204 题**。
>
> 目标不是刷题，而是强制读者从“会复述”走到“能形式化、能实现、能推翻自己的解释”。

---

# Volume 0　导论与技术史

## Part 0　具身智能究竟是什么

**0-C**　解释为什么把机器人策略写成静态函数 `action = f(image)` 会遗漏反馈、时间与部分可观测性。给出一个真实失败例子。

**0-M**　把具身智能写成 POMDP：明确状态、观测、动作、转移、观测模型与 reward；解释 belief state 为什么比单帧 observation 更接近决策充分统计量。

**0-I**　写一个 2D toy agent：相同 perception model 下分别实现 open-loop 与 closed-loop controller，加入随机扰动并比较成功率。

**0-R**　设计一个实验区分“模型记住视觉模式”与“模型利用 embodiment–environment coupling”。至少包含一个干预变量和一个负对照。

## Part 1　思想史与技术史

**1-C**　比较 Sense–Plan–Act、Subsumption、现代 VLA 三种范式的信息流与时间尺度。

**1-M**　用状态空间形式写出 feedback control 与一次性 planning 的区别，并说明误差传播结构。

**1-I**　实现一个 grid-world：分别使用 A*、reactive rule、learned policy，记录静态与动态障碍下的差异。

**1-R**　选择一个 2023–2026 的“机器人基础模型” claim，追溯它真正继承了哪些经典机器人概念，哪些部分才是新增机制。

---

# Volume I　数学与计算语言

## Part 2　线性代数、微积分与数值计算

**2-C**　解释 rank、null space、pseudoinverse 分别如何出现在冗余机械臂 IK 中。

**2-M**　从最小二乘推导 Moore–Penrose pseudoinverse 解，并进一步推导 damped least squares。

**2-I**　不用现成 IK 库，实现一个平面 3R 机械臂的 Jacobian numerical IK，并画误差收敛曲线。

**2-R**　构造一个接近 singularity 的任务，比较 pseudoinverse、DLS、带 joint-limit null-space objective 的稳定性。

## Part 3　概率、信息与不确定性

**3-C**　解释 epistemic 与 aleatoric uncertainty 在机器人部署中的不同处理方式。

**3-M**　从 Bayes rule 推导一次离散 Bayes filter update；再写出 information gain 的定义。

**3-I**　实现一个有噪声传感器的 1D localization Bayes filter，并可视化 belief 随时间变化。

**3-R**　设计一个 active perception 任务，检验模型的不确定性是否真的 calibrated 到足以指导“是否移动相机”。

## Part 4　优化、动态系统与最优决策

**4-C**　解释 constrained optimization、optimal control、dynamic programming 三者的关系。

**4-M**　推导离散 LQR 的 Bellman recursion 与 Riccati equation。

**4-I**　实现 inverted pendulum 的 LQR，与 PID 比较 disturbance recovery。

**4-R**　设计实验比较“learned policy + safety projection”与“纯 learned policy”在 constraint violation 与 task performance 上的 trade-off。

## Part 5　几何、图与因果

**5-C**　为什么 rotation 不能简单当作普通三维向量相加？为什么 robot morphology 天然适合图表示？

**5-M**　证明一个简单 SO(2) equivariant mapping；再写出 SCM 中 intervention `do(a)` 与条件概率 `p(y|a)` 的区别。

**5-I**　实现一个 permutation-invariant set encoder，再与普通 MLP 在 object-order permutation 下比较。

**5-R**　设计一个“视觉相关性不变但物理机制改变”的机器人因果实验，例如改变摩擦但保持纹理。

---

# Volume II　机器人身体、几何、力学与控制

## Part 6　机器人身体与机电系统

**6-C**　比较 position、velocity、torque control interface 对学习策略 action space 的影响。

**6-M**　给定电机 torque–speed curve 与减速比，推导末端可用速度/力矩的基本关系。

**6-I**　读取一个 URDF/MJCF，自动输出 joint type、limit、kinematic tree、actuated DOF。

**6-R**　比较同一 policy 在高减速高刚度与 quasi-direct-drive 机器人上的行为差异，提出需要控制的硬件变量。

## Part 7　空间、旋转与刚体几何

**7-C**　解释 world/base/camera/end-effector frame 混淆为什么能造成“像模型错误一样”的失败。

**7-M**　从 axis–angle 推导 Rodrigues formula；写出 SE(3) inverse 和 composition。

**7-I**　从零实现 quaternion、rotation matrix、SE(3) 的互转，并用随机测试验证闭环误差。

**7-R**　构造四种常见 convention bug（xyzw/wxyz、左/右乘、deg/rad、camera axis）并建立自动单元测试。

## Part 8　机器人运动学

**8-C**　解释 FK、IK、differential IK、trajectory interpolation 的职责边界。

**8-M**　对一个 2R/3R 机械臂手推 FK 与 Jacobian；求 singular configurations。

**8-I**　实现 analytical/numerical IK 对比，并记录 convergence basin。

**8-R**　在相同 end-effector task 下比较 joint-space 与 Cartesian-space policy 对 embodiment change 的敏感性。

## Part 9　动力学、接触与抓取

**9-C**　为什么 contact-rich manipulation 比 free-space reaching 难得多？

**9-M**　对 2-link arm 写出 Lagrangian，并推导 `M(q)qdd + C(q,qd)qd + g(q) = tau` 的结构。

**9-I**　在 simulator 中记录一次 peg insertion 的 contact force、slip、pose error，画时间对齐曲线。

**9-R**　在视觉保持不变的条件下改变 friction，测试 vision-only policy 是否学到真正 contact mechanism。

## Part 10　反馈、最优与 Whole-Body Control

**10-C**　比较 PID、impedance、operational-space control、MPC、WBC 的适用层级。

**10-M**　推导一维 impedance controller 的闭环二阶系统，分析 `K,D` 与自然频率/阻尼比关系。

**10-I**　实现一个 Cartesian impedance controller，并对刚/软环境做接触实验。

**10-R**　比较 VLA 输出 pose target + impedance controller 与直接 joint action，控制数据量不变，分析 robustness 来源。

## Part 11　运动规划、任务规划与不确定决策

**11-C**　解释 C-space、TAMP、belief-space planning 分别解决什么问题。

**11-M**　证明 A* 在 admissible heuristic 下的最优性条件；写出 belief-space action selection 目标。

**11-I**　实现 RRT/RRT*，在同一障碍场景比较 path cost 与 planning time。

**11-R**　设计一个需要 learned policy + classical planner 才明显优于任一单独方法的任务。

---

# Volume III　感知、状态与世界表示

## Part 12　传感器、标定与时间

**12-C**　为什么 timestamp error 能让正确模型学到错误动作？

**12-M**　推导 pinhole camera projection 与 back-projection；写出 camera extrinsic 的 SE(3) 形式。

**12-I**　模拟 RGB 30 Hz、joint 200 Hz、tactile 500 Hz 的异步流，实现 timestamp-based synchronization。

**12-R**　逐步加入 10/30/60/100 ms sensor–action misalignment，量化 policy performance 对时序错位的敏感性。

## Part 13　二维视觉与视觉表示

**13-C**　语义表征、几何表征、task-relevant physical representation 有何区别？

**13-M**　写出 self-attention 的 tensor shape 流，并分析图像 token 数与计算复杂度。

**13-I**　冻结多个视觉 encoder，用同一 downstream policy 比较 novel object 与 precise reaching。

**13-R**　设计 intervention 判断一个视觉 backbone 的增益来自 semantic recognition 还是 metric geometry。

## Part 14　三维 / 四维世界表示

**14-C**　比较 point cloud、voxel/TSDF、NeRF、3DGS、object-centric scene graph 对机器人控制的优缺点。

**14-M**　写出 TSDF 融合的加权更新；讨论坐标变换误差如何积累。

**14-I**　从 RGB-D 构建 point cloud，并将 object pose 从 camera frame 转到 world frame。

**14-R**　比较“视觉重建质量最好”的 representation 与“控制成功率最高”的 representation 是否一致。

## Part 15　状态估计、定位与 Belief

**15-C**　为什么 observation 不等于 state？何时需要 particle filter 而非 Kalman filter？

**15-M**　推导线性 Kalman filter prediction/update；解释 Kalman gain 的意义。

**15-I**　实现 EKF 融合 wheel odometry + IMU，加入 bias 与 dropout。

**15-R**　比较 deterministic state estimator 与 uncertainty-aware belief planner 在遮挡任务中的行为。

## Part 16　触觉、力觉与 Contact Intelligence

**16-C**　解释为什么 tactile observation function 比 camera 更 embodiment-specific。

**16-M**　定义 slip detection 的 binary Bayes decision rule，并推导阈值与代价的关系。

**16-I**　实现 vision slow-policy + tactile high-rate residual 的 toy control loop。

**16-R**　做 cross-sensor transfer：训练一种 tactile sensor，测试另一种，区分 representation 与 hardware domain gap。

## Part 17　主动感知

**17-C**　主动感知与普通 camera motion planning 的区别是什么？

**17-M**　推导 `information gain - action cost` 的 one-step objective；讨论 multi-step 时为何更难。

**17-I**　实现一个有遮挡 object-search toy environment，使用 entropy reduction 选择 next-best-view。

**17-R**　加入“随机移动相机”负对照，验证主动感知收益是否真的来自信息选择而不是多看几帧。

---

# Volume IV　Robot Learning

## Part 18　为机器人重新学习机器学习

**18-C**　为什么 i.i.d. generalization 不足以描述 closed-loop robot policy？

**18-M**　推导 autoregressive NLL、diffusion denoising objective、flow matching objective 的基本形式并比较。

**18-I**　在同一个 2D multimodal action dataset 上训练 regression、AR、diffusion、flow model。

**18-R**　控制参数量与训练数据，分析四种生成目标在闭环而非离线 MSE 上的排名是否改变。

## Part 19　模仿学习

**19-C**　解释 BC covariate shift 与 DAgger 为什么有效。

**19-M**　用状态分布差异写出 BC 误差随 horizon 累积的直觉上界。

**19-I**　在 Push-T 或简单导航中实现 BC→DAgger，画 intervention round 与 success curve。

**19-R**　比较“更多成功 demonstration”与“少量 recovery/failure demonstration”的数据价值。

## Part 20　强化学习、Offline RL 与交互学习

**20-C**　比较 on-policy、off-policy、offline RL 在真实机器人上的成本和风险。

**20-M**　推导 policy gradient theorem 的核心步骤；解释 entropy regularization 在 SAC 中的作用。

**20-I**　同一环境训练 PPO 与 SAC，并记录 sample efficiency、wall-clock 与稳定性。

**20-R**　用固定 robot-hours 比较 BC+更多 demo、BC+offline RL、BC+online RL 的收益。

## Part 21　生成式动作模型与实时策略

**21-C**　action chunking 为什么既解决 latency 又制造 stale-action 问题？

**21-M**　设 model latency `Tm`、control period `Tc`、chunk H，推导同步/异步执行的有效 observation age。

**21-I**　实现一个异步 action-chunk executor，可在新 chunk 到达时替换旧计划。

**21-R**　在动态扰动任务中比较 fixed chunk、temporal ensemble、RTC/async replacement，画 latency–success frontier。

---

# Volume V　Robot Foundation Models

## Part 22　语言、VLM 与 Physical Grounding

**22-C**　为什么“知道杯子是什么”不等于“知道如何稳定抓杯子”？

**22-M**　把 language-conditioned policy 写成 latent grounding + control，两阶段形式化其信息瓶颈。

**22-I**　用 VLM 输出 object/affordance candidate，再接传统 planner 完成一个 language-conditioned toy task。

**22-R**　设计一组语义相同但几何/物理不同的任务，测 VLM prior 在何处失效。

## Part 23　VLA 的形成：2022–2024

**23-C**　比较 Gato、SayCan、PaLM-E、RT-1/2、Octo、OpenVLA 的“通用性”分别发生在哪一层。

**23-M**　写出 multi-dataset mixture loss，分析 sampling weight 对 small dataset gradient contribution 的影响。

**23-I**　选一个开放 VLA，追踪一条样本从 dataset loader 到 action output 的所有 shape。

**23-R**　在同一数据上比较 VLM frozen + action head 与 end-to-end fine-tuning，分析 semantic retention 与 motor precision。

## Part 24　VLA 第二阶段：2024–2026

**24-C**　列出 π、GR00T、Gemini Robotics、Helix 在 action generation、frequency、embodiment、post-training、whole-body 五轴上的差异。

**24-M**　构造 `ΔP = Δdata + Δmodel + Δobjective + Δsystem + interaction` 的 factorial decomposition。

**24-I**　做一个模型卡：强制填写 action interface、policy rate、controller、adaptation budget，而不仅是 parameter count。

**24-R**　设计组合负对照检验“emergent capability”是否可由训练技能简单组合解释。

## Part 25　VLA 内部机制

**25-C**　为什么 dataset mixture、low-level controller、latency 都应被视为 VLA system 的一部分？

**25-M**　分析 `L = L_VL + λL_action` 两梯度夹角对 joint training 的影响。

**25-I**　实现 frozen vision / partial tune / full tune 三种方案，比较 representation probe 与 task success。

**25-R**　通过改变 mass/friction/hinge 而保持视觉外观，检验 VLA 是否依赖物理机制还是视觉 shortcut。

## Part 26　机器人数据、人类视频与 Cross-Embodiment Data

**26-C**　为什么 cross-embodiment 首先是 schema problem？

**26-M**　分析 dataset sampling `p(i) ∝ wi|Di|^α` 中 `α` 对大/小数据集有效采样比例的影响。

**26-I**　构造统一 dataset schema，把两个不同 action convention 的 toy robots 转成统一 effect-centric representation。

**26-R**　固定模型，依次加入更多同任务数据、新对象、新机器人、人类视频、failure data，画 OOD marginal value curve。

---

# Volume VI　Reasoning、Memory、Experience、World Models

## Part 27　Embodied Reasoning / Agentic Robotics

**27-C**　为什么输出 chain-of-thought 文本不能证明 reasoning 对 motor behavior 有作用？

**27-M**　对 `n` 步任务、单步成功率 `p` 推导 `p^n`，并加入 recovery probability 后重新推导任务成功率。

**27-I**　实现 planner → skill policy → progress monitor → replanner 的 toy agent。

**27-R**　注入 shuffled/wrong plan，测试 reasoning channel 是否对动作有因果影响。

## Part 28　Embodied Memory

**28-C**　区分 short-term、working、episodic、semantic、spatial memory。

**28-M**　把 memory compression 写成 information bottleneck：最小化 memory size，同时保留 future-action information。

**28-I**　实现 episodic retrieval + structured task memory，对比单纯长 context。

**28-R**　让任务 horizon 从 30 s 增到 20 min，测试 memory 方案优势是否随 horizon 增长。

## Part 29　Learning from Experience

**29-C**　为什么 autonomous practice 的 bottleneck 往往是 reset 而非 policy？

**29-M**　写出带 KL-to-foundation-policy regularization 的 RL post-training objective。

**29-I**　实现 failure replay prioritization：按 rarity / TD error / human intervention 采样。

**29-R**　固定 robot-hours 比较“更多 demonstration”与“autonomous experience + RL”的 sample efficiency。

## Part 30　World Models

**30-C**　为什么 video prediction、latent dynamics、counterfactual world model 是不同层级？

**30-M**　写出 action-conditioned latent dynamics + MPC 目标；分析 horizon 增长下 model error accumulation。

**30-I**　训练一个小 latent world model，用 CEM 做 action planning。

**30-R**　加入 shuffled/wrong world-model 负对照，证明 planner 是否真的利用预测。

## Part 31　生成式世界 / Neural Simulator

**31-C**　为什么 visual realism 不能作为 robot world model 的核心指标？

**31-M**　定义 state/contact/reward/policy-ranking 四种 rollout error，并讨论它们与视觉 metric 的关系。

**31-I**　用同一 action sequence 比较 physics simulator 与 learned predictor 的 horizon error。

**31-R**　训练多个 visual-quality 不同但 state-accuracy 不同的 world model，测试哪种指标最能预测 real-control utility。

---

# Volume VII　操作、导航、灵巧与人形

## Part 32　Manipulation

**32-C**　解释 why manipulation is state-changing interaction rather than end-effector motion.

**32-M**　对 grasp map 写出 object wrench 与 contact forces 关系，并说明 internal force。

**32-I**　实现 pick-and-place state machine，显式加入 grasp verification 与 recovery。

**32-R**　在 rigid、articulated、deformable 三类对象上比较同一 representation，寻找 generality boundary。

## Part 33　Bimanual / Dexterity / Tactile

**33-C**　为什么双臂不是两个单臂 policy 的拼接？

**33-M**　推导相对位姿约束的 differential form；写出 cooperative object wrench。

**33-I**　实现 left/right relative-frame controller，并加入 self-collision constraint。

**33-R**　比较 vision+tactile 同频融合与 slow vision + fast tactile residual，在 slip/insertion 上测 latency sensitivity。

## Part 34　Navigation

**34-C**　为什么 navigation 是研究 memory 与 belief 的天然场景？

**34-M**　写出 differential-drive kinematics 和 information-gain exploration objective。

**34-I**　实现 occupancy-grid A* + local obstacle avoidance，再实现一个 learned reactive baseline。

**34-R**　用 ObjectNav 比较 reactive、recurrent memory、explicit semantic map、active exploration。

## Part 35　Humanoid / Whole-Body

**35-C**　为什么 humanoid 不能理解为“机械臂 + 两条腿”？

**35-M**　推导 capture point 基本公式，并解释 upper-body momentum 如何影响 balance。

**35-I**　记录一个 humanoid motion-tracking rollout 的 CoM、contact、joint error、energy。

**35-R**　逐级测试 locomotion-only、fixed-feet manipulation、locomotion+reach、full loco-manipulation，量化 coupling cost。

## Part 36　Human–Robot / Multi-Robot

**36-C**　区分 shared autonomy、multi-agent coordination、centralized orchestration。

**36-M**　写出一个 Dec-POMDP 的局部 observation / joint reward 形式；推导简单 task allocation assignment objective。

**36-I**　实现双 agent shared-memory task board，并模拟通信延迟与 robot failure。

**36-R**　对比 explicit communication、implicit visual coordination、centralized coordinator 在新 partner 上的 generalization。

---

# Volume VIII　Cross-Embodiment 与 Developmental Intelligence

## Part 37　Cross-Embodiment

**37-C**　为什么“一个 checkpoint 支持多机器人”不等于 unseen-body generalization？

**37-M**　把 morphology 表示成 graph，形式化 `π(a|o,g,Gbody)`。

**37-I**　训练一个 graph-conditioned toy morphology policy，测试未见 link 数量。

**37-R**　比较 robot-ID、padded joint vector、morphology graph、effect-centric latent 在 zero/few-shot transfer 上的曲线。

## Part 38　Continual / Lifelong / Developmental Learning

**38-C**　区分 adaptation、continual learning、developmental learning、open-ended learning。

**38-M**　根据 performance matrix `Pij` 推导 forgetting、forward transfer、average accuracy。

**38-I**　实现 replay 与 parameter-isolation 两种 continual baseline，顺序学习 5 个 task。

**38-R**　把 parameter growth、memory growth、retention 同时作为指标，检验“不断加模块”是否只是隐藏资源扩张。

## Part 39　Self-Evolving Physical Intelligence

**39-C**　给出一个不满足“自进化”定义但容易被营销成自进化的系统例子。

**39-M**　定义并计算 retention、forward transfer、growth efficiency、autonomy ratio。

**39-I**　实现一个 toy agent：failure cluster 达阈值时触发 memory consolidation / module creation，并支持 rollback。

**39-R**　设计跨场景长期实验，区分真正 capability growth 与 dataset memorization；明确什么结果会推翻“自进化” claim。

---

# Volume IX　Simulation、Data、Deployment

## Part 40　Physics Simulation / Platforms

**40-C**　为什么 simulator version、solver 与 asset 都是实验变量？

**40-M**　分析 integration step size 对简单 spring–mass system 稳定性的影响。

**40-I**　同一机械臂在两个 simulator 中跑相同 controller，比较 trajectory/contact discrepancy。

**40-R**　设计 benchmark 测 simulator-specific overfitting：训练一个平台、测试另一个平台与真机。

## Part 41　Synthetic Data / Sim-to-Real

**41-C**　区分 visual、geometry、dynamics、sensor、control、task reality gap。

**41-M**　对四类 randomization 做 `2^4` factorial design，写出主效应与交互效应估计。

**41-I**　实现 dynamics randomization + system ID，比较 blind-wide 与 ID-centered randomization。

**41-R**　找出一个“sim success 很高但 real 失败”的任务，定位 gap 属于哪一类而不是笼统归咎 sim2real。

## Part 42　Robot Data Engineering

**42-C**　为什么 timestamp、schema、metadata 可以改变模型学到的因果关系？

**42-M**　计算多频率 sensor resampling 的时间误差上界；分析最近邻对齐与插值误差。

**42-I**　写 dataset validator：timestamp monotonicity、NaN、action bounds、frame counts、checksum、duplicate detection。

**42-R**　故意注入 20–100 ms action misalignment，训练相同 policy，量化 data-engineering error 的 downstream cost。

## Part 43　真实系统部署

**43-C**　解释 model latency 与 end-to-end loop latency 的区别。

**43-M**　分解 `Tloop = sensor + transfer + preprocess + infer + safety + bus + actuator + observe`，计算 jitter budget。

**43-I**　实现 async sensor/policy/controller/logger 四线程 mock system，所有共享状态带 timestamp/version。

**43-R**　比较本地与远程 model serving，在 network jitter 下测 stale-action、success 与 safety-stop。

---

# Volume X　Evaluation / Safety

## Part 44　Benchmark / Evaluation Science

**44-C**　为什么一次成功视频不能作为科学证据？

**44-M**　对二项 success rate 推导标准误与 Wilson interval；计算 70/100 与 80/100 差异的置信度。

**44-I**　写 evaluation harness：固定 seed、记录 all trials、failure taxonomy、confidence interval。

**44-R**　把“generalization”拆成 object/scene/task/embodiment 四维矩阵，设计 held-out protocol 防止混淆。

## Part 45　Reliability / Safety

**45-C**　区分 model safety、control safety、functional safety、cybersecurity。

**45-M**　对一维系统构造简单 CBF safety constraint，并求 safe action projection。

**45-I**　实现 runtime safety monitor：joint/velocity/workspace/heartbeat/uncertainty stop。

**45-R**　注入 perception dropout、500 ms latency、unexpected human、actuator saturation，测 layered safety 的事故率与 false-stop trade-off。

---

# Volume XI　Research Method / Next Architecture

## Part 46　严谨具身研究

**46-C**　什么是 L0–L3 复现？为什么“代码跑通”不是机制复现？

**46-M**　用 2×2 factorial design 分解 data gain、architecture gain 与 interaction。

**46-I**　选一篇论文，把 system diagram 重画到 sensor→controller→actuator，标 shape/frequency/frame。

**46-R**　把论文核心 claim 改写成一个含 positive control、negative control、failure criterion 的可证伪 hypothesis。

## Part 47　Transformer 的作用与边界

**47-C**　列出 Transformer 擅长与不天然解决的具身问题各五项。

**47-M**　比较 full attention `O(N²)` 与 recurrent/state-space constant-state streaming 的计算/内存增长。

**47-I**　同一长序列任务比较 Transformer、RNN/SSM、Transformer+external memory。

**47-R**　设计 latency-sensitive / persistent-memory / morphology-change 三个任务，检验“更大 Transformer”是否都能解决。

## Part 48　数学化具身智能

**48-C**　解释 invariance、equivariance、constraint、mechanism、causality 如何减少纯经验拟合。

**48-M**　给出一个 SO(2)/SE(2) equivariant mapping；写 Koopman lifting 的最小例子。

**48-I**　实现 known physics + learned residual dynamics，与纯 neural dynamics 比较 OOD rollout。

**48-R**　构造 unseen appearance × unseen physics 的 2×2 test，检验模型学的是视觉相关性还是可迁移机制。

## Part 49　截至 2026-09 的开放问题

**49-C**　从本章 25 个问题中选 5 个，说明它们为什么不是单纯 scaling 就自动解决。

**49-M**　为其中一个问题定义正式 metric / state / intervention，使其从口号变成可测研究对象。

**49-I**　建立一个 frontier tracker：每项问题记录公开证据、反证、benchmark、未解变量、最新日期。

**49-R**　选一个你认为“已经基本解决”的问题，设计最强反例；如果反例成功，重新定义问题边界。

## Part 50　从学习者到独立研究者

**50-C**　解释“追模型”与“追问题”的不同科研行为。

**50-M**　为自己的研究飞轮定义 throughput：idea→minimal experiment→full experiment→writing→submission 的各阶段 WIP 上限与瓶颈。

**50-I**　建立个人 Research Question Bank，每个条目必须含 hypothesis、negative control、minimum experiment、kill criterion。

**50-R**　提出一个你愿意做三年的具身智能问题，并回答：什么实验结果会让你彻底放弃当前核心假设？

---

# 最终 Capstone Written Exam

完成 Part 0–50 后，不看教材回答：

1. 从一条自然语言指令开始，完整画出直到 motor current 与 contact feedback 的数据流。
2. 给一个 VLA 的 performance gain，设计实验分离 data / architecture / post-training / controller 四类贡献。
3. 给一个“world model 提高物理理解”的 claim，构造至少两个 counterfactual negative controls。
4. 给一个“跨本体通用 policy”的 claim，设计 unseen-body test。
5. 给一个“机器人会自我进化”的 claim，定义 retention / transfer / resource / autonomy / safety 五类指标。
6. 最后说明：**什么实验结果会证明你关于具身智能的核心世界观是错的？**

如果第 6 题没有可回答的失败条件，就还没有形成真正的研究立场。