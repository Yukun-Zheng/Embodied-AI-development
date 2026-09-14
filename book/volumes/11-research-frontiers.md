# Volume XI　研究方法、理论前沿与下一代具身智能

> 本卷不再教“已有方法怎么用”，而是训练研究判断：怎样拆系统、怎样构造可证伪实验、怎样判断一个改进究竟来自数据还是机制，以及在 2026 年之后哪些问题值得建立新的数学与计算范式。

---

# Part 46　如何做严谨的具身智能研究

## 46.1 怎样读一篇具身论文

不要从 abstract 的 claim 开始信。按以下顺序拆：

1. **Research question**：到底想证明什么？
2. **System boundary**：哪些模块是作者贡献，哪些是现成？
3. **Inputs / outputs / shapes**：数据到底怎样流？
4. **Training distribution**：用了哪些数据？
5. **Test distribution**：真正 OOD 在哪里？
6. **Control interface**：action 是什么、如何执行？
7. **Baselines**：是否公平？
8. **Ablations**：能否隔离贡献？
9. **Failure cases**：什么时候失效？
10. **Reproducibility**：代码/数据/配置是否足够？

## 46.2 先画完整 System Diagram

任何机器人论文先画：

```text
raw sensors
  ↓
preprocessing / calibration
  ↓
representation / state
  ↓
policy / planner / world model
  ↓
action representation
  ↓
IK / WBC / controller / safety
  ↓
robot hardware / simulator
  ↓
physical environment
  ↺
```

若论文只画中间神经网络，主动补齐省略模块。很多“架构增益”实际来自 controller 或数据处理差异。

## 46.3 Input / Output / Shape Audit

对每个 tensor 写语义：

\[
I:B\times T\times V\times3\times H\times W,
\]

\[
q:B\times T\times n_q,
\qquad
A:B\times H_a\times d_a.
\]

再问：frame、unit、normalization、mask、timestamp。很多复现失败可以在这一步提前发现。

## 46.4 Reproduction 的四个层级

1. **Code runs**：脚本不报错；
2. **Metric reproduces**：得到相近数字；
3. **Mechanism reproduces**：关键 ablation/现象也出现；
4. **Claim reproduces**：在合理变化条件下仍支持原结论。

科研真正需要后两层。

## 46.5 Baseline Design

好 baseline 应回答“如果不用你的关键机制，最强合理替代是什么？”

错误 baseline：故意使用过时、小模型、少数据或更差调参。

公平性要求尽量匹配：

\[
\text{data},\quad\text{compute},\quad\text{backbone},\quad\text{controller},\quad\text{training steps}.
\]

## 46.6 Ablation

若方法包含 A+B+C，应至少比较：

\[
Base,\ Base+A,\ Base+B,\ Base+C,\ Base+A+B+C.
\]

若组合空间大，可用 factorial/orthogonal design。Ablation 的目标不是“表越大越好”，而是估计各因素的因果贡献。

## 46.7 Negative Control

机器人研究特别需要 negative control。例如声称 memory 有效：

- 真 memory；
- shuffled memory；
- unrelated memory；
- equal-token dummy context。

如果都提升，可能只是 context length/regularization，而非 memory semantics。

## 46.8 Data Gain vs Architecture Gain

设性能

\[
P=f(D,C,A,S),
\]

分别代表 data、compute、architecture、system。若新方法同时改四项，结论不可归因。

最有价值实验常是：固定 D/C/S，只改 A；再做 data scaling curve，看新 architecture 是否改变样本效率斜率。

## 46.9 Scaling Curve

不是只比较一个点：

\[
P(N)=a-bN^{-\alpha}
\]

或经验曲线。若架构只在巨量数据下略优，和小数据就显著提高 sample efficiency，是两种不同科学贡献。

## 46.10 Failure-First Research

先系统收集 failure，再提出机制：

```text
failure cluster
    ↓
minimal counterexample
    ↓
hypothesis
    ↓
small controlled test
    ↓
mechanism
    ↓
full benchmark
```

这比“先想一个模块名，再找 benchmark 提分”更容易产生真正研究问题。

## 46.11 Minimal Experiment

一个新思想先在最小环境验证：2D point mass、Push-T、planar arm、single-contact task。若核心机制在最小 setting 都不成立，不要直接烧八卡跑大模型。

## 46.12 Stress Test

主 benchmark 之外主动攻击模型：

- 极端 camera angle；
- unseen composition；
- latency；
- missing sensor；
- contradictory language；
- dynamics shift；
- adversarial distractor；
- embodiment swap。

研究者的工作不是保护自己的方法，而是找它什么时候错。

## 46.13 Statistical Discipline

预先定义主要指标；多个 seed；报告 CI；不隐藏失败 run；明确 hyperparameter search budget。真实机器人样本少时，paired protocol 和 bootstrap 尤其重要。

## 46.14 Artifact Discipline

每个结果绑定：

```text
commit + config + checkpoint + dataset version
+ simulator version + seeds + hardware + raw logs
```

图表应能从 raw artifact 一键重生成。

## 46.15 怎样判断 VLA 真 Generalize

必须隔离：new object、new scene、new task composition、new embodiment。尤其要防止 web/pretraining leakage。

真正强证据是训练 constituent、测试未见组合，并通过 counterfactual 证明模型使用正确视觉/物理变量。

## 46.16 怎样判断 World Model 被 Policy 利用

仅有 world-model auxiliary loss 不够。做 intervention：

1. 破坏/冻结 world model；
2. 保持参数量相同的 dummy auxiliary；
3. 提高 prediction accuracy 是否单调改善 control；
4. planning 时 counterfactual ranking 是否正确。

如果 policy performance 不依赖 world-model quality，就不能声称预测机制带来控制收益。

## 46.17 怎样判断视觉服务物理交互

不要只做 ImageNet probe。测试：geometry/contact probe、viewpoint intervention、task-irrelevant texture swap、representation-to-success mediation。

理想证据链：

\[
\text{representation change}\rightarrow
\text{better physical variable estimate}\rightarrow
\text{better action}\rightarrow
\text{higher task success}.
\]

## 46.18 怎样判断 Reasoning 不是包装

让 reasoning 产生可验证 causal effect。随机/错误 thought 应显著伤害对应行为；正确 plan 在未见组合任务中应提升 execution；reasoning 中提及的 state 应可由环境证据验证。

---

# Part 47　Transformer 在具身智能中的作用与边界

## 47.1 Transformer 真正解决了什么

Transformer 提供：

- 高并行序列建模；
- flexible token mixing；
- scale-friendly optimization；
- multimodal interface；
- in-context conditioning。

这些非常重要，但并不自动提供：physics、causality、stable control、persistent memory、structural plasticity。

## 47.2 Attention 的代价

标准 attention：

\[
O(T^2d)
\]

随 sequence 长度平方增长。视频、多 camera、长记忆、触觉高频 stream 会迅速使 token 数爆炸。

因此 embodied system 必须做 temporal/spatial compression、memory hierarchy 或换用更线性结构。

## 47.3 Sequence Model ≠ Dynamics Model

一个模型能 next-token predict action，不代表其 hidden state 满足物理 dynamics consistency。

Dynamics model 要求 intervention-sensitive：

\[
f(s,a_1)\ne f(s,a_2)
\]

并且结果与真实 action effect 一致。

## 47.4 Tokenization 与连续物理

位置、速度、力和时间本质连续。离散 token 会引入 quantization：

\[
\epsilon_q=|a-Q^{-1}(Q(a))|.
\]

高频精细控制中误差累积明显。因此现代 VLA 出现 continuous flow/diffusion expert，是对纯 token action 的自然修正。

## 47.5 Attention 不等于 Memory

context 中 token 只能在一次 forward 中存在；跨小时/天 persistence 需要外部或可更新 memory。并且 memory 需要 write/erase/consolidate，而 attention 只负责读取当前 context。

## 47.6 Transformer 不天然满足 Equivariance

旋转/平移结构若只通过数据学习，样本效率低。SE(3)-equivariant network、geometry-aware attention 可将对称性直接写进架构。

## 47.7 State-Space Models

SSM：

\[
h_{t+1}=Ah_t+Bx_t,
\qquad y_t=Ch_t.
\]

现代 selective SSM / recurrent linear-time sequence architecture 可在长序列上提供更低复杂度。对高频 sensor stream、长记忆具有潜力。

但线性复杂度本身不等于更懂物理；仍需任务实验证明。

## 47.8 Recurrent / Predictive State

具身 agent 天然在线运行。recurrent state

\[
h_t=F(h_{t-1},o_t,a_{t-1})
\]

只保留必要历史，计算量每步固定。关键问题是如何让 \(h_t\) 避免漂移、长期保持可解释/可纠正信息。

## 47.9 World-Model-Centric Architecture

另一方向把 predictive state 放在中心：

```text
observation → latent state
                ↓
        action-conditioned dynamics
                ↓
       predicted futures / belief
                ↓
        planner / policy / memory
```

这里 policy 只是 world model 上的决策器，而不是所有知识都压进 action model。

## 47.10 Graph / Object-Centric Architecture

机器人身体、场景对象、接触天然是图。关系结构：

\[
G=(V_{body}\cup V_{object},E_{kin}\cup E_{contact}\cup E_{spatial}).
\]

图结构有利于 variable morphology、compositionality 和 mechanism reuse。

## 47.11 Geometry-Centric Architecture

以 3D point/field/SE(3) token 为基本表示，直接编码 spatial relation，而非先把所有东西投影成二维 patch。对 manipulation 可能更自然，但语义 scaling 和高效大模型训练仍是挑战。

## 47.12 Continuous-Time Architecture

真实世界没有 token timestep。Neural ODE / continuous-time latent dynamics：

\[
\dot z=f_\theta(z,u,t)
\]

可以自然处理异步 sensor 与不同 control rate。事件相机、触觉和多速率 control 尤其适合这一视角。

## 47.13 Modular / Hierarchical Architecture

具身系统存在显著时间尺度分层，因此模块化并非退步：

- ms：reflex/control；
- sec：motor skill；
- min：task reasoning；
- hours：learning/memory consolidation。

真正问题不是“端到端还是模块化”，而是**模块边界是否对应稳定可验证的计算职责**。

## 47.14 Transformer 之后真正值得问的问题

不要问“下一个能替代 Transformer 的 block 名字是什么”。应该问：

1. 哪些物理变量值得持久表示？
2. 怎样在多时间尺度更新？
3. 怎样利用 symmetry / topology / causality？
4. 怎样跨 embodiment 保留机制？
5. 怎样持续生长而不遗忘？
6. 怎样让预测真正改善控制？
7. 怎样在 bounded compute 下长期运行？

架构应从这些问题导出。

---

# Part 48　数学化具身智能：从相关性到结构与规律

## 48.1 Physical Invariance

如果某规律与坐标原点无关，模型不应重新学习每个平移情况。Invariance：

\[
f(gx)=f(x).
\]

例如物体类别对全局平移不变。

## 48.2 Equivariance

若输入旋转，输出也按同样群作用变化：

\[
f(gx)=g'f(x).
\]

robot pose / vector field 更需要 equivariance 而非 invariance。

SE(3)-equivariant architecture 可以显著减少需要数据覆盖的姿态组合。

## 48.3 Symmetry

对称性不仅是几何。双臂左右对称、多个同类对象 permutation symmetry、多机器人交换 symmetry 都可以成为 inductive bias。

## 48.4 Conservation Law

真实动力学受能量、动量等守恒/耗散结构约束。学习模型若完全自由拟合，可能产生 nonphysical rollout。

Hamiltonian / Lagrangian neural network 尝试通过结构表达：

\[
\dot q=\frac{\partial H}{\partial p},
\qquad
\dot p=-\frac{\partial H}{\partial q}.
\]

## 48.5 Constraints

关节、接触、不可穿透、闭链都可写约束：

\[
g(q)=0,\qquad h(q)\ge0.
\]

比事后 penalty 更强的做法是把 constraint manifold 直接写入 parameterization / solver。

## 48.6 Hybrid Systems

机器人接触导致连续 dynamics + 离散 mode：

\[
\dot x=f_m(x,u),
\qquad m\in\{free,contact,slip,grasp,...\}.
\]

很多 manipulation failure 来自 mode transition，纯平滑网络容易把不同 mode 平均。

## 48.7 Control-Theoretic Priors

稳定性、passivity、barrier certificate 可作为 learned policy 的结构约束，而非只用 rollout 数据期待网络自己学会。

目标是：

\[
\text{learning flexibility}+\text{mathematical guarantees}.
\]

## 48.8 Identifiability

从有限 observation 能否唯一恢复 dynamics parameter / latent mechanism？如果多个模型都解释数据，就不能声称网络“发现了真实规律”。

研究 mechanism discovery 必须讨论 identifiability 与 intervention design。

## 48.9 Causal Interventions

机器人最大的优势是可主动改变世界。通过控制 \(a\) 产生 intervention data，比被动互联网视频更适合区分因果：

\[
p(y\mid do(a))
\]

而非只学 observational correlation。

## 48.10 Compositional Operators

希望把技能从 trajectory template 提升为 operator：

\[
m_i:(s,\theta_i)\mapsto(s',\Delta,\text{precondition},\text{effect}).
\]

新任务通过 operator composition，而不是再训练一个 monolithic network。

## 48.11 Koopman View

非线性 dynamics 可寻找 lifted observable \(z=\phi(x)\) 使

\[
z_{t+1}\approx Kz_t.
\]

Koopman 方法提供“在合适表征中让 dynamics 更线性”的思路，但有限维闭包通常困难。其价值更多是结构化 latent dynamics 假说，而非万能线性化。

## 48.12 Predictive State Representation

不把 latent 当隐藏“真实 state”，而直接用未来可观测量预测来定义 state。对 partial observability 和跨 embodiment，PSR 提供不同于 object-centric world state 的理论路线。

## 48.13 Differentiable Physics

若 simulator 对参数可微：

\[
\frac{\partial L}{\partial\theta}
=\frac{\partial L}{\partial x_T}
\frac{\partial x_T}{\partial\theta},
\]

可直接优化 controller、material、robot design。但接触不光滑、长 horizon gradient 不稳定仍是挑战。

## 48.14 Neural ODE / Continuous Dynamics

连续 latent：

\[
\dot z=f_\theta(z,u)
\]

使模型能按任意时间间隔积分，适合 irregular sensor timestamp。需要和普通 discrete sequence model 在相同数据上比较，不应仅因数学形式优雅就认为更物理。

## 48.15 Physics-Informed / Physics-Constrained Learning

将 known equation 加入 loss：

\[
L=L_{data}+\lambda\|\dot x-f_{physics}(x,u)\|^2.
\]

或把 known physics 作为 model core，只学习 residual：

\[
\dot x=f_{known}(x,u)+r_\theta(x,u).
\]

后者往往更易解释与 sim-to-real。

## 48.16 从“拟合动作”到“学习规律”

真正的数学化具身智能希望 learned object 具备：

- invariance / equivariance；
- causal intervention consistency；
- compositionality；
- identifiable mechanism；
- uncertainty；
- stability / constraint awareness；
- cross-embodiment transfer。

“网络预测得准”只是起点。

---

# Part 49　开放问题：截至 2026-09 的真正前沿

## 49.1 Robust Open-World Generalization

现有 VLA 已展示很强分布扩展，但离“随便放到陌生家庭可靠工作”仍有巨大距离。核心是任务、场景、物体和社会规则同时变化，而不是单维 OOD。

## 49.2 Long-Horizon Autonomy

分钟级任务需要 memory、progress、recovery；小时/天级自主还需要 battery management、maintenance、long-term map、persistent identity、cross-session memory。

## 49.3 Reliable Dexterity

人手级 dexterity 需要 tactile bandwidth、compliance、precise actuation 与大量 practice。视觉 VLA 单独很难解决。

## 49.4 Contact-Rich Intelligence

大部分开放 benchmark 仍偏 free-space / simple grasp。真正家务、装配、工具使用高度依赖接触。未来 foundation model 必须让 tactile/force 从附加 modality 变成核心 state。

## 49.5 Active Perception

多数 VLA 被动接受 camera。真正 agent 应决定去哪里看、何时摸、何时移动物体获得信息，并权衡 sensing cost。

## 49.6 Persistent World State

从每帧重建世界太浪费。机器人需要长期维护：对象 identity/location/state、房间地图、任务历史、人与偏好，并处理世界变化。

## 49.7 Memory Consolidation

如何把海量 episode 变成少量可重用知识？简单 RAG 储存日志不等于 learning。需要从 episodic → semantic → procedural 的 consolidation。

## 49.8 Learning from Failure

失败通常比成功更有信息，但当前训练 pipeline 大多仍以成功 demonstrations 为主。如何自动诊断、采样 targeted correction，并安全在线更新，是数据 flywheel 核心。

## 49.9 World Model Utility

生成视频越来越强，但“看起来真实”不等于可以规划。2026 world-model benchmark 已明确暴露 physical executability 问题。下一阶段必须把评价转到 action consequence 和 downstream control。

## 49.10 Cross-Embodiment Abstraction

什么才是身体无关的知识？语言 subtask、object effect、contact relation、mechanism、world dynamics 各有不同 invariance。不存在一个显然 universal action space。

## 49.11 Human Video Scaling

human video 数据量巨大。难题是从视觉动作中恢复 robot-useful causal structure，同时避免 morphology gap。2025–2026 已出现 human-to-robot transfer 随 robot pretraining diversity 增强的证据，但还远未解决。

## 49.12 Whole-Body Foundation Policy

humanoid 正从 locomotion/controller 与 manipulation/VLA 两条线汇合。真正统一 feet-to-fingertips policy 要同时解决 balance、contact、hands、reasoning 和多时间尺度 control。

## 49.13 Multi-Robot Intelligence

多机器人 collaboration 将暴露 coordination、communication、shared memory 与 heterogeneity 问题。一个 foundation model 如何扩展到 team size 变化仍非常开放。

## 49.14 Efficient On-Device Intelligence

远程大模型延迟/网络不适合所有机器人。小型 VLA、quantization、hierarchical compute、on-device reasoning 将决定大规模部署成本。

## 49.15 Safety of Open-Ended Agents

当机器人可以 tool-call、改计划、主动学习，safety 不再是 action clip。需要 permission、uncertainty resolution、human override、upgrade governance、audit。

## 49.16 Continual Learning Without Catastrophic Regression

机器人不能每学一个新家庭技能就忘掉旧安全动作。长期 plasticity–stability 仍无通用解决方案。

## 49.17 Structural Plasticity

固定 architecture + SGD 是否足以支撑开放式能力增长？这是尚无答案的问题。结构可塑方向必须证明其在有限 compute 下提高长期学习效率，而非简单参数膨胀。

## 49.18 Causal / Mechanistic Learning

机器人是可以做 intervention 的 AI，但当前大模型训练仍以 observational imitation 为主。如何主动发现可组合物理机制，可能是从“数据拟合”走向“物理智能”的关键。

## 49.19 Mathematical Guarantees + Foundation Models

如何把 stability、constraints、geometry、uncertainty 与 billion-parameter foundation models 统一，而不是一边 neural、一边传统 safety patch，是重要交叉前沿。

## 49.20 Benchmark Science

如果 benchmark 无法隔离 data leakage、system confounder、human intervention，就无法判断真正进展。具身领域需要更强 evaluation science，而非更多 leaderboards。

## 49.21 General-Purpose Humanoid 是不是终局

人形适合人类环境和工具，但在轮式效率、工业精度、微型/飞行形态等方面不一定最优。真正通用 physical intelligence 可能应是**跨 morphology 的核心智能**，而不是押注一种身体。

## 49.22 是否需要新的计算范式

Transformer 仍然极强。没有证据表明“换 block”本身会带来具身突破。真正可能需要改变的是：persistent state、continuous-time interaction、causal intervention、structural plasticity、multi-scale learning。

## 49.23 什么才算理解物理世界

一个操作性定义：若系统能在未见组合和 intervention 下，正确预测动作后果、选择可执行策略、发现错误、跨 embodiment 迁移并用少量经验更新，则我们才有更强理由说它形成了物理结构，而非统计模仿。

## 49.24 距离真正通用智能还有什么

至少还有：

\[
\text{robustness}+
\text{autonomy}+
\text{lifelong learning}+
\text{causal/world understanding}+
\text{safety}+
\text{economic reliability}.
\]

“会做很多 demo”只是开始。

---

# Part 50　从学习者到独立研究者

## 50.1 阶段一：数学与经典机器人学

必须真正掌握：linear algebra、probability、optimization、SE(3)、FK/IK/Jacobian、dynamics、feedback control、planning。

目标：看到机器人论文公式不再“跳过 robotics 部分”。

## 50.2 阶段二：亲手做完整闭环

实现：camera projection、state estimator、planner、controller、simulator task。目标是理解**没有 neural network 时机器人怎样工作**。

## 50.3 阶段三：Robot Learning

依次：BC → DAgger → PPO/SAC → ACT → Diffusion Policy → Flow policy。每次都做 failure analysis，而非只跑官方 demo。

## 50.4 阶段四：Foundation Policies

复现至少两种不同路线：

- action-token VLA（如 OpenVLA family）；
- continuous action expert（如 open π / SmolVLA/flow family）。

统一 dataset/benchmark，比较 action representation 和 latency。

## 50.5 阶段五：World Model / Memory / Active Perception

不要直接追 SOTA，先用小环境回答：prediction 是否改善 control？memory 是否因果有效？主动观察是否降低 task-relevant uncertainty？

## 50.6 阶段六：真实机器人系统

至少独立完成一次：采数据 → 标定 → policy train → deploy → safety → logs → failure → retrain。只有经历这一整环，才会知道论文省略了多少系统变量。

## 50.7 阶段七：建立 Research Program

不是“一篇 paper 一个 idea”，而维护一组长期可证伪假说：

```text
H1: current visual representation misses X
H2: world model helps only under Y
H3: cross-embodiment requires invariant Z
...
```

每轮：发散 → 攻击 → 最小实验 → 负对照 → 综合 → 更新假说。

## 50.8 怎样提出新问题

最可靠来源：

1. 重复出现的 failure；
2. 两类方法之间无法统一的接口；
3. benchmark 与真实部署的巨大差距；
4. 一个重要变量在所有现有模型中被隐式忽略；
5. 现有 claim 无法通过因果/负对照。

## 50.9 怎样提出新架构

架构必须服务明确机制。格式：

> 由于 **A** 造成 **B failure**，我们假设缺少 **C computational capability**。因此引入 **D mechanism**，它预测在 **E controlled condition** 下应产生 **F measurable effect**。

如果无法写成这个句子，架构大概率还只是造模块。

## 50.10 怎样证明不是“多参数”

匹配 parameter/FLOP/data；做 same-backbone ablation；绘制 scaling curve；做 parameter-matched control；报告 training budget。

## 50.11 怎样建立论文谱系

不要按年份背 paper。为每条技术线维护：

```text
problem
→ prior assumption
→ failure
→ new mechanism
→ remaining failure
→ next work
```

这样论文史就变成问题演化史。

## 50.12 怎样选择 Benchmark

先写 hypothesis，再选能 falsify 它的最小 benchmark，最后才上大 benchmark。不要倒过来“benchmark 有什么就研究什么”。

## 50.13 怎样做真实机器人论文

至少分三层证据：

- controlled sim mechanism evidence；
- standardized benchmark comparison；
- real-world system validation。

真实实验应报告 raw trial count、failure、intervention、latency，而非只剪成功视频。

## 50.14 怎样写论文

结构应围绕逻辑链：

\[
\text{problem}\rightarrow
\text{evidence of gap}\rightarrow
\text{hypothesis}\rightarrow
\text{method}\rightarrow
\text{falsifiable predictions}\rightarrow
\text{experiments}\rightarrow
\text{limits}.
\]

写作清晰来自研究逻辑清晰，而不是术语复杂。

## 50.15 终点：能质疑前沿

真正掌握具身智能，不是能背 π0.7、GR00T、Gemini Robotics 2，而是面对下一篇新论文时能独立问：

- 它到底改了什么？
- 证据足够吗？
- 和经典 robotics 的关系是什么？
- data / controller confounder 被控制了吗？
- 有什么更小实验可以推翻它？
- 它留下的真正研究问题是什么？

达到这一点，你就不再只是学习这个领域，而开始参与定义这个领域。

---

# 全书最终统一式

把全书压缩成一个 lifelong embodied loop：

\[
\boxed{
\begin{aligned}
&\text{Sense}\rightarrow\text{Estimate}\rightarrow\text{Represent}\rightarrow\text{Predict}\\
&\rightarrow\text{Reason/Plan}\rightarrow\text{Act}\rightarrow\text{Control}\rightarrow\text{World}\\
&\rightarrow\text{Evaluate}\rightarrow\text{Remember}\rightarrow\text{Learn}\rightarrow\text{Develop}
\end{aligned}}
\]

身体与物理世界贯穿始终；时间、uncertainty、safety 和 embodiment 不是附加章节，而是每个箭头的约束。

这就是本书所采用的具身智能定义：

> **具身智能，是一个受身体与物理规律约束的智能体，通过持续闭环交互建立对世界与自身的可行动表征，并利用感知、预测、决策、控制、记忆与学习，在变化环境中可靠地获得、组合和发展能力。**

## 最后的研究原则

1. **不要把语言流畅当作 physical reasoning。**
2. **不要把视频真实感当作 world understanding。**
3. **不要把一个 checkpoint 控多台已见机器人当作强 cross-embodiment。**
4. **不要把更多数据带来的提升包装成新机制。**
5. **不要把一次成功 demo 当作 reliability。**
6. **不要因为 Transformer 流行就把所有物理变量 token 化。**
7. **不要为了“类脑”而类脑；生物启发必须转成可证伪计算假说。**
8. **先问世界需要什么计算，再决定网络长什么样。**

## 推荐长期参考

- Lynch & Park, *Modern Robotics*.
- Tedrake, *Underactuated Robotics*.
- Thrun, Burgard & Fox, *Probabilistic Robotics*.
- Sutton & Barto, *Reinforcement Learning: An Introduction*.
- LaValle, *Planning Algorithms*.
- Boyd & Vandenberghe, *Convex Optimization*.
- Barfoot, *State Estimation for Robotics*.
- 持续跟踪 OpenReview/arXiv 与主要机器人会议：RSS、CoRL、ICRA、IROS，以及 CV/ML 会议中的 embodied / robot learning 工作；但永远以问题谱系而不是论文数量组织知识。
