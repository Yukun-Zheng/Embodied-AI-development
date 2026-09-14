# Solution Sketches & Acceptance Criteria

> 对应 [`EXERCISES.md`](./EXERCISES.md)。这里给的是**解题骨架与验收条件**，不是替代思考的完整标准答案。研究型题没有唯一答案；只有“变量是否明确、对照是否成立、claim 是否可被推翻”的质量标准。

---

# Volume 0

## Part 0

**0-C**　静态 `a=f(o)` 忽略历史、环境反馈和执行后世界变化。合格答案应至少指出：同一图像可能对应不同 hidden state；旧 action 会改变下一帧；扰动后 open-loop 无法修正。

**0-M**　POMDP 应写为 `(S,A,O,T,Z,R,γ)`；belief update：`b'(s') ∝ Z(o'|s',a) Σ_s T(s'|s,a)b(s)`。说明 belief 是 history 的压缩。

**0-I**　验收：相同目标/扰动分布，open-loop 与 closed-loop 至少 100 episodes；画 success vs disturbance magnitude。

**0-R**　必须保持视觉统计近似不变，只改变 body/environment interaction，例如 actuator gain、friction、delay；负对照可改变纹理但保持 dynamics。

## Part 1

**1-C**　Sense–Plan–Act：显式 world model/plan；Subsumption：行为层、快速反应；VLA：数据驱动感知—动作映射，但通常仍依赖低层 controller。

**1-M**　open-loop `x_{t+1}=f(x_t,u_t^*)`；feedback `u_t=π(x_t)`。误差在线性化后分别为 `e_{t+1}=Ae_t` 与 `e_{t+1}=(A+BK)e_t`。

**1-I**　动态障碍下 A* 若不重规划会失效；reactive 可避障但可能局部最优；learned policy 受训练分布影响。

**1-R**　合格输出应把“新模块”放回 perception/state/planning/control/data scaling 中，而非按论文术语复述。

---

# Volume I

## Part 2

**2-C**　rank 表示可控/可观测局部方向；null space 表示不改变末端任务的 joint motion；pseudoinverse 给最小范数局部解。

**2-M**　最小二乘 `min ||JΔq-e||²` 给 `Δq=J⁺e`；DLS：`Δq=Jᵀ(JJᵀ+λ²I)^{-1}e`。

**2-I**　必须验证数值 Jacobian 与解析/有限差分一致；至少测试 singularity 附近。

**2-R**　比较最大 joint velocity、condition number、tracking error、joint-limit violation；不能只看末端最终误差。

## Part 3

**3-C**　aleatoric 是数据内在噪声，通常不能靠更多数据消除；epistemic 来自模型/数据不足，可通过探索或更多数据降低。

**3-M**　information gain 可写 `IG(a)=H[b(s)]-E_o H[b'(s|o,a)]` 或 KL 形式。

**3-I**　验收：真实位置、观测、posterior 同时画出；加入错误 sensor model 看 filter 是否偏置。

**3-R**　应包含 calibration curve/ECE 或 Brier score；如果高 uncertainty 并不对应错误概率，不能用它指导 sensing。

## Part 4

**4-C**　optimization 是一般形式；optimal control 把变量扩成时间上的 control sequence；DP 利用 Markov + Bellman 分解时序优化。

**4-M**　离散 LQR `V_t=xᵀP_tx`，由 Bellman 最小化得到 `K_t` 与 Riccati backward recursion。

**4-I**　至少报告 settling time、overshoot、control effort、扰动恢复，而非“能立住”。

**4-R**　比较 raw policy 的 success/violation 与 projected policy 的 success/violation；安全层若把任务全部 stop 也不算好。

## Part 5

**5-C**　rotation 属于 manifold/group；body 是 graph 因 link/joint topology 不随编号顺序改变。

**5-M**　SO(2) 例：`f(Rx)=Rf(x)`；`do(a)` 切断 A 的父边，与观察到 `A=a` 不同。

**5-I**　随机 permutation object order，set encoder 输出应近似不变；MLP baseline 应明显变化。

**5-R**　合格实验需 `appearance` 与 `physics` 正交操控，测试 action/success 对二者的敏感度。

---

# Volume II

## Part 6

**6-C**　position action 容易但隐藏低层 dynamics；torque 最直接但更难、更危险；velocity 介于两者。

**6-M**　理想减速器近似 `τ_out=Nητ_motor`、`ω_out=ω_motor/N`；还应讨论效率/饱和/反驱。

**6-I**　解析树时必须识别 fixed/mimic joints 与 actuated DOF，不能把 link 数当 DOF。

**6-R**　控制 morphology、payload、controller gain；报告 tracking bandwidth 与 impact/contact difference。

## Part 7

**7-C**　frame bug 会系统性旋转/平移动作；模型可在视觉上“识别对”，执行仍完全错误。

**7-M**　Rodrigues：`R=I+sinθ[K]+(1-cosθ)[K]²`；`T^{-1}=[Rᵀ,-Rᵀp;0,1]`。

**7-I**　随机 10k rotations，互转后检查 orthogonality、det=1、geodesic error。

**7-R**　单元测试必须使用非对称 pose；单位矩阵/轴对齐样例无法暴露很多 convention bug。

## Part 8

**8-C**　FK：q→pose；IK：pose→q；differential IK：twist/error→dq；trajectory interpolation 负责时间参数化。

**8-M**　2R Jacobian 由末端 `x,y` 对 `q1,q2` 求偏导；singularity 对应 `det(J)=0` 或 rank drop。

**8-I**　记录 success basin、iteration count、final error、joint-limit failures。

**8-R**　若 Cartesian representation 在新 link length 上 transfer 更好，但 low-level IK 重新求解，则说明 generality 来自 interface abstraction。

## Part 9

**9-C**　接触引入离散 mode、摩擦不确定性、冲击和非光滑约束；free-space 只有连续 kinematics/dynamics。

**9-M**　应明确 kinetic/potential energy，Euler–Lagrange 后识别 `M,C,g`；不要求所有展开项背诵。

**9-I**　contact onset 前后必须时间对齐；至少画 normal force、tangential force、pose error。

**9-R**　视觉完全相同情况下 friction intervention 若显著破坏策略，说明策略没有足够 dynamics/contact adaptation。

## Part 10

**10-C**　PID joint-level；impedance 控制 motion-force relation；OSC 在 task space；MPC 显式预测约束；WBC 协调多任务全身。

**10-M**　`m xdd + D xd + Kx=0`，`ω_n=sqrt(K/m)`，`ζ=D/(2sqrt(mK))`。

**10-I**　软环境下应比较 contact force peak 与 tracking；不能只测 free-space。

**10-R**　若 pose+impedance 在扰动下更强，需要进一步控制 controller tuning，避免把 gain tuning 当架构收益。

## Part 11

**11-C**　C-space 把碰撞变成配置障碍；TAMP 联合离散任务与连续运动；belief-space 规划把 uncertainty 当 state。

**11-M**　A* 最优要求 heuristic admissible；一致性保证更强的图搜索性质。

**11-I**　RRT* 随样本增多 path cost 应趋于改善；需要多 seed 统计。

**11-R**　好任务应含全局几何约束与局部复杂接触，使 planner 与 learned skill 各自发挥不可替代作用。

---

# Volume III

## Part 12

**12-C**　错位 `(o_t,a_{t+δ})` 相当于学习错误的 conditional relation，尤其高速运动时形成系统性偏差。

**12-M**　`[u,v,1]ᵀ ∝ K[X/Z,Y/Z,1]ᵀ`；back-project 使用 depth 与 `K^{-1}`。

**12-I**　输出每个 sample 的 source timestamp、aligned timestamp 与 max skew。

**12-R**　performance vs delay 曲线应显示任务的 time sensitivity；还要区分 sensor delay 与 actuator delay。

## Part 13

**13-C**　semantic 回答“是什么”；geometry 回答“在哪里/形状”；physical task representation 还要保留 contact/dynamics/action relevance。

**13-M**　ViT token `N≈HW/P²`，attention 计算/显存主项随 `N²` 增长。

**13-I**　统一 action head、data、augmentation；否则不能归因 encoder。

**13-R**　几何干预可保持类别不变改变 pose/scale；语义干预可换 object category 保持 geometry。

## Part 14

**14-C**　point cloud metric 但稀疏；TSDF 融合多帧；NeRF/3DGS 擅长 rendering；scene graph 擅长 object relations。

**14-M**　典型 TSDF `D_new=(wD+w_obsD_obs)/(w+w_obs)`；pose error 会造成表面 ghosting。

**14-I**　需验证 frame transform，随机选点投回 image 检查 reprojection。

**14-R**　控制 policy/head，分别以 PSNR/geometry error/control success 排名，观察 ranking 是否一致。

## Part 15

**15-C**　单 observation 因噪声/遮挡不充分；particle filter 适合非高斯/多模态 belief。

**15-M**　预测 `P-=APAᵀ+Q`，更新 `K=P-Hᵀ(HP-Hᵀ+R)^{-1}`（注意标准符号写法应检查维度），核心是 covariance-weighted fusion。

**15-I**　加入 IMU bias 后若 EKF 未建 bias state 会系统漂移；这是重要验收。

**15-R**　belief planner 应在高 uncertainty 状态主动测量/保守行动，而 deterministic estimator 可能过度自信。

## Part 16

**16-C**　触觉信号由 sensor material/geometry 与接触共同生成，因此 sensor 本体改变，observation mapping 也变。

**16-M**　Bayes decision 根据 posterior 与 false-positive/false-negative cost 选择阈值。

**16-I**　slow/base action 与 tactile residual 必须不同 update rate；记录 residual latency。

**16-R**　若 cross-sensor 性能差，可分别用 sensor normalization 与 paired-contact data 判断 gap 来自表征还是硬件。

## Part 17

**17-C**　active perception 优化的是未来 information state，而普通 camera motion 可能只优化轨迹/可达性。

**17-M**　`a*=argmax E[H(b_t)-H(b_{t+1})]-λC(a)`；多步需要考虑 future belief tree。

**17-I**　NBV 应在同等 sensing budget 下优于 random camera motion。

**17-R**　若 random motion 同样提升，claim 应改成“multi-view helps”，而非“uncertainty-driven active perception helps”。

---

# Volume IV

## Part 18

**18-C**　policy 会改变之后的数据分布，训练分布不再固定，错误还会通过状态转移累积。

**18-M**　AR：`-Σ log p(a_i|a_<i,c)`；diffusion 学 score/noise；flow matching 学 path velocity field。

**18-I**　必须统一 data split / parameter budget / sampling steps，并在同一 multimodal target 测 mode coverage。

**18-R**　闭环排名和离线 MSE 不同是常见现象；以 task success/robustness 为主结果。

## Part 19

**19-C**　BC 只在 expert state distribution 上监督；DAgger 收集 policy-induced states 并询问 expert action。

**19-M**　合格答案需说明每步小误差会使 visited state 分布偏离，导致最坏情况 horizon 级累积。

**19-I**　每轮保存 intervention states，验证新数据是否集中在原 BC failure region。

**19-R**　固定 annotation hours；如果 recovery data 对 OOD 更有效，说明数据覆盖比纯数量重要。

## Part 20

**20-C**　on-policy sample hungry；off-policy 重用经验；offline 无在线风险但有 distributional extrapolation。

**20-M**　policy gradient 核心 `∇J=E[∇logπ(a|s)Q(s,a)]`；SAC 加 `αH(π)` 鼓励随机性。

**20-I**　不能只报 environment steps，还要 wall-clock、replay ratio、seed variance。

**20-R**　固定 robot-hours 是关键，否则 online RL 使用更多真实交互不公平。

## Part 21

**21-C**　chunk 减少 inference frequency，却让后半段 action 基于更旧 observation。

**21-M**　同步 chunk 平均 observation age 随 chunk position 增长；异步可降低新 chunk 等待但要解决 replacement consistency。

**21-I**　executor 必须记录 action 的 generation timestamp 与 execution timestamp。

**21-R**　动态扰动下 chunk 长度越长通常 stale risk 越大；RTC 应改善 latency–reactivity frontier。

---

# Volume V

## Part 22

**22-C**　semantic knowledge 不包含 grasp pose、friction、force、controller bandwidth 等 physical details。

**22-M**　可写 `z=g_VLM(o,l)`、`a=π(z,s)`；瓶颈在 `z` 是否保留 action-relevant geometry/physics。

**22-I**　验收：VLM 只负责 grounding，motion feasibility 由 planner 检查；失败时记录是哪一层。

**22-R**　语义相同、几何不同；若性能只与 semantic score 相关，则 physical grounding 不充分。

## Part 23

**23-C**　Gato 是 general sequence agent；SayCan 是 LLM planning×affordance；RT 是 robot policy scaling；Open X/Octo/OpenVLA 强调数据/开放模型通用化。

**23-M**　small dataset gradient contribution 由采样概率与 batch count 决定；不能只看 dataset size。

**23-I**　必须记录图像 tensor→token→multimodal hidden→action 的实际 shape。

**23-R**　joint-tune 若提高 precision 但 semantic probe 降低，体现 gradient interference / knowledge trade-off。

## Part 24

**24-C**　合格答案必须基于五轴比较，而非“谁参数更大”。

**24-M**　2×2 或多因素设计估计 main effect 与 interaction；实际 scaling study需更多 factor levels。

**24-I**　模型卡若没有 controller/frequency/adaptation data，不足以比较真实系统。

**24-R**　组合负对照应保持 primitive 都见过，只改变组合关系；同时排查训练数据重合。

## Part 25

**25-C**　因为最终 behavior 是这些组件的联合函数；仅 neural architecture 无法决定 closed-loop outcome。

**25-M**　`cos(g1,g2)<0` 表示 objectives 局部冲突；可比较 frozen/adapter/joint training。

**25-I**　同时报告 semantic probe 与 motor metric，观察 trade-off。

**25-R**　物理干预后若 VLA 能快速根据 tactile/state 修正，比仅视觉 similarity 更能支持 physical model claim。

## Part 26

**26-C**　不同 robots 的 observation/action convention、rate、frame 不同，数据在进入 model 前就需要语义对齐。

**26-M**　`α=1` 更接近按规模，`α=0` 更接近 dataset-level uniform（若 `w` 相同）。

**26-I**　effect-centric schema 至少应保留 task effect 与 embodiment-specific decoder 的边界。

**26-R**　计算每增加一类数据的 OOD marginal gain，而不是混合后只看总分。

---

# Volume VI

## Part 27

**27-C**　文本可能是 post-hoc narration；只有干预 reasoning 后 behavior 改变才能支持因果作用。

**27-M**　无恢复 `p^n`；若每次失败可用概率 `r` 恢复并重试，需根据 retry model 写新的递推，不存在唯一通式。

**27-I**　progress monitor 必须可触发 replan，而不只是显示状态。

**27-R**　错误 plan 应系统性降低对应 subgoal behavior；若无影响，reasoning channel 未被 policy 使用。

## Part 28

**28-C**　short-term 是局部 sensorimotor；working 是当前任务变量；episodic 是具体经历；semantic 是抽象知识；spatial 绑定位置。

**28-M**　可写 `min I(M;H)` s.t. `I(M;A_future)>=η` 或 task loss constraint。

**28-I**　检索需包含 task/spatial context，不应只 semantic cosine。

**28-R**　memory 方法应在短任务无明显额外收益、长任务逐步拉开，否则可能只是额外容量。

## Part 29

**29-C**　没有自动 reset 就需要人不断恢复环境，autonomous experience 吞吐被人工 bottleneck 限制。

**29-M**　示例 `max J(π)-βE_s KL(π(.|s)||π0(.|s))`。

**29-I**　priority 要防止只重放极端失败造成 distribution collapse。

**29-R**　同等 robot-hours 才能比较“数据 vs experience learning”。

## Part 30

**30-C**　video predictor 可相关性生成；latent dynamics 预测 compact state；counterfactual model 必须对不同 actions 给正确差异。

**30-M**　`A*=argmax ΣR(z_k)` s.t. `z_{k+1}=F(z_k,a_k)`；model error 常随 horizon 累积/放大。

**30-I**　CEM 应在每个 real step replan，验证 receding horizon 能限制 drift。

**30-R**　错误 world model 若不影响 behavior，说明 planner 没依赖它或 task 不需要预测。

## Part 31

**31-C**　视觉 metric 可奖励 texture/background，控制需要 state/contact/counterfactual fidelity。

**31-M**　应分别在 state/contact/reward/ranking 空间定义 error；不能强行合成单一数字。

**31-I**　至少画 error vs rollout horizon；one-step accuracy 不够。

**31-R**　如果 policy utility 与 state/contact metric 相关而与 FVD/PSNR 弱相关，即支持章节核心观点。

---

# Volume VII

## Part 32

**32-C**　manipulation 的目标是通过 contact 改变 world state，而不是仅移动 robot configuration。

**32-M**　`w=Gf`；internal force 属于 `Null(G)`，可改变接触力而不改变 object wrench。

**32-I**　state machine 必须有 verify/retry transitions，不能只 nominal sequence。

**32-R**　representation 若只在 rigid object 有效，应明确 generality boundary 而非称“通用操作”。

## Part 33

**33-C**　共享对象造成闭链、relative pose、internal force、collision coupling。

**33-M**　若固定 relative transform，约束 derivative 可写两末端 twists 的关系；具体 Jacobian 根据 frame convention 推导。

**33-I**　必须测试 crossing/self-collision 与 one-arm perturbation。

**33-R**　fast tactile residual 若在高 latency setting 明显更强，支持 multi-rate hypothesis。

## Part 34

**34-C**　当前 frame 看不到全局位置和历史探索结果，所以 navigation 需要 memory/belief/map 或其隐式等价物。

**34-M**　差速底盘 `xd=v cosθ, yd=v sinθ, θd=ω`；探索目标与 Part 17 同构。

**34-I**　local planner 必须应对动态 obstacle，否则 A* 结果只是静态 path。

**34-R**　比较路径重复率/visited area 能揭示 memory 是否真的被使用。

## Part 35

**35-C**　floating base、balance/contact 与 manipulation 强耦合，手臂运动会改变 whole-body momentum。

**35-M**　LIPM capture point `ξ=x+xd/ω0`；上身角动量改变 centroidal dynamics。

**35-I**　motion tracking 还需 report fall/contact slip，不能只 joint error。

**35-R**　随着从 fixed-feet 到 loco-manipulation，新增失败应按 balance/perception/reach/contact 分解。

## Part 36

**36-C**　shared autonomy 是人机 authority；multi-agent coordination 是多个 autonomous agents；orchestration 是高层分工，不等于低层协同。

**36-M**　Dec-POMDP 需定义 joint transition/reward 与 local observations；assignment objective 可用 binary `x_ij`。

**36-I**　shared memory 需处理 stale updates / conflict；这也是 distributed-systems 问题。

**36-R**　新 partner/generalization 是核心；训练搭档上协作不能证明 partner-general coordination。

---

# Volume VIII

## Part 37

**37-C**　已见多机器人可由 ID/adapter memorization 实现；unseen morphology 才测试结构泛化。

**37-M**　graph-conditioned policy 节点/边特征应包括 morphology 和 actuator/sensor metadata。

**37-I**　必须测试 node count/topology 超出训练组合。

**37-R**　zero-shot/few-shot curve 需统一 adaptation budget；不能把更多数据当更强 generality。

## Part 38

**38-C**　adaptation 是局部变化；continual 强调 retention；developmental 强调能力随交互形成；open-ended 不预定义有限任务集。

**38-M**　forgetting/forward transfer 由 performance matrix 按标准 continual-learning definitions 计算；必须明确 baseline。

**38-I**　同时限制 replay size 与 parameter growth，才是公平资源比较。

**38-R**　若模块数与任务数线性增长，可能只是“每任务一网络”，而非高效 lifelong intelligence。

## Part 39

**39-C**　例：每晚人工收集数据、人工重训更大 checkpoint，不满足 autonomous acquisition / bounded growth。

**39-M**　指标必须统一 denominator，growth efficiency 需把新增 data/compute/parameters 纳入成本。

**39-I**　structure change 前后必须跑 regression suite，支持 rollback。

**39-R**　核心是跨场景历史回测；只在当前场景变强不能证明 growth。

---

# Volume IX

## Part 40

**40-C**　solver/contact/integration 决定 transition function；asset 决定 geometry/inertia；版本变更就是环境变更。

**40-M**　显式 Euler 对 stiff spring 的稳定条件随 `dt` 与 eigenvalues 变化；合格答案应展示步长过大导致发散。

**40-I**　统一 initial state/controller/dt，报告 trajectory、contact impulse、energy discrepancy。

**40-R**　cross-simulator test 能检测 simulator artifact；最终仍需 real anchor。

## Part 41

**41-C**　六类 gap 应分别提出 measurement，不能只说“domain gap”。

**41-M**　2^4 design 可用 ±1 coding 估计 main/interactions；至少解释 effect confounding。

**41-I**　ID-centered randomization 应在真实 parameter 附近集中，同时覆盖 uncertainty。

**41-R**　通过逐项替换 visual/dynamics/sensor/controller 找 dominant gap。

## Part 42

**42-C**　这些工程量决定训练样本是否真的对应同一 physical event。

**42-M**　nearest-neighbor 最大 skew 与 source periods 有关；线性插值还受 signal bandwidth 限制。

**42-I**　validator 必须失败 fast，并输出 episode ID/field/timestamp，而不是只 boolean。

**42-R**　延迟注入是直接的数据因果实验；若 performance 对小错位极敏感，采集链必须优先改。

## Part 43

**43-C**　forward time 只是 loop 的一个 term；sensor/network/controller 都贡献 age/jitter。

**43-M**　总 latency 是链路和；real-time correctness 更关注 worst-case/jitter，不只平均。

**43-I**　线程共享最新状态时需 sequence number/timestamp 避免 tearing/stale data。

**43-R**　远程 serving 若平均一样但 jitter 更大，closed-loop safety 可能显著更差。

---

# Volume X

## Part 44

**44-C**　成功视频缺 denominator、selection process、failures 和 protocol，存在严重 selection bias。

**44-M**　不要只用 Wald interval 在小样本；实现 Wilson/Jeffreys 等更稳健区间并说明选择。

**44-I**　evaluation harness 必须保存所有 trial outcome，不允许手工删除“异常”失败。

**44-R**　四维 OOD 分开 hold-out；否则“新场景+新对象”混合难定位 generalization source。

## Part 45

**45-C**　model safety 处理模型决策；control safety 处理动作约束；functional safety 处理系统故障；cybersecurity 处理恶意攻击。

**45-M**　CBF action projection 应证明/数值验证下一步不离开 safe set（在假设成立下）。

**45-I**　monitor 应 independent process / watchdog 思路，不能与主 policy 同故障域。

**45-R**　安全系统还要报告 false stop；永远停机事故率为零但没有任务价值。

---

# Volume XI

## Part 46

**46-C**　L0 能运行；L1 指标；L2 机制/ablation；L3 换场景仍支持解释。

**46-M**　interaction 项检查“新架构在新数据上是否有额外协同”，不能只比较两个角点。

**46-I**　如果画不出 controller/actuator，说明对真实 system boundary 理解不完整。

**46-R**　hypothesis 必须有明确 kill criterion；“结果不好再调”不是可证伪研究。

## Part 47

**47-C**　Transformer 强：multimodal routing/scaling/context；弱：hard geometry/contact/stability/persistent state/realtime guarantees。

**47-M**　attention history 长度 N 时显存/计算增长；recurrent/SSM 维护 fixed-size state，但表达/训练特性不同。

**47-I**　长流任务不要把所有方法强行相同 API，需记录 actual latency/memory。

**47-R**　若更大 Transformer 仍无法解决 physical constraint，而结构模块能，用数据支持“需要新 inductive bias”。

## Part 48

**48-C**　这些数学结构把已知规律加入 hypothesis space，减少样本需求与不合理外推。

**48-M**　Koopman toy 可选非线性标量系统并选 observable；关键展示 lifted dynamics 更线性。

**48-I**　OOD rollout 要改变 physics parameter，而不只是 random seed。

**48-R**　2×2 appearance/physics 设计可分离视觉相关性和机制 generalization。

## Part 49

**49-C**　合格答案必须指出“scaling 无法自动保证”的具体变量，例如 persistent memory、safety invariant、contact sensing。

**49-M**　把开放问题变成 state/action/intervention/metric，是从观点到科研题的关键一步。

**49-I**　tracker 每条 evidence 必须带日期和 source type（paper/official/demo/independent replication）。

**49-R**　能主动寻找最强反例，才说明不是在维护信念而是在做科学。

## Part 50

**50-C**　追模型按发布日期切换注意力；追问题维护长期假说与 evidence table。

**50-M**　研究飞轮可类比 queueing/WIP；瓶颈阶段堆积会导致大量“开坑不收尾”。

**50-I**　Question Bank 里没有 kill criterion 的条目不得进入 expensive experiment。

**50-R**　三年问题必须 fundamental、重复出现、可证伪、可由小实验扩张；最重要的是明确“什么结果会让我放弃”。

---

# 最终评分标准

对 204 道题，不建议按“答案相似度”评分。建议四级 rubric：

| 等级 | 标准 |
|---|---|
| 0 | 复述术语，无法建立变量与系统关系 |
| 1 | 概念正确，能写基本公式/流程 |
| 2 | 能实现、验证、分析 failure，并控制主要变量 |
| 3 | 能设计负对照、定义 kill criterion，并把结果反推到机制假说 |

真正达到本书目标，需要绝大多数核心章节达到 **Level 2**，研究主线章节达到 **Level 3**。