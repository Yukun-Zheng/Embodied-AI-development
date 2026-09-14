# Volume VI　Reasoning、Memory、Experience 与 World Models

> 一个机器人会输出动作，并不等于它拥有世界模型。本卷研究更强的问题：机器人怎样维持任务状态、记住过去、预测动作后果、比较未执行方案、从失败更新，并把“想象”真正变成可执行控制。

---

# Part 27　Embodied Reasoning：从语义推理到物理决策

## 27.1 Reactive Policy 的边界

最简单 policy：

\[
a_t=\pi(o_t,g).
\]

它不显式记历史，也不显式规划。对于短时、可完全从当前 observation 判断的任务足够，但长时任务会遇到：

- 已完成哪些步骤？
- 某个物体刚才放在哪里？
- 上一次抓取为什么失败？
- 当前子任务结束了吗？
- 下一步应先开门还是先抓物？

这些都要求 internal state。

## 27.2 Goal、Subgoal 与 Skill

长任务可分层：

\[
g\rightarrow z_1,z_2,\ldots,z_K
\]

其中 \(z_k\) 可以是 language subtask、symbolic goal、latent skill 或 geometric target。

低层：

\[
a_t\sim\pi_L(a\mid o_t,z_k).
\]

高层只需在低频决策点更新，从而避免每个 motor timestep 都做昂贵语言推理。

## 27.3 Task Decomposition

好的 decomposition 不是把指令机械拆成句子，而是找到**可独立验证 termination 的子目标**。例如“洗杯子”可能分成：拿杯 → 移到水槽 → 开水 → 冲洗 → 关闭水 → 放置。每步都应有 progress detector。

## 27.4 Embodied Chain-of-Thought 的证据问题

模型输出“我先抓杯子，再打开柜门”并不证明内部真正依赖这些文字 reasoning。可能只是 post-hoc explanation。

更可靠的验证：

1. 干预 reasoning token，行为是否按因果方式改变；
2. 隐藏中间视觉证据，reasoning 是否发现缺失；
3. 同一语言解释是否对应一致动作；
4. 在组合未见任务中 reasoning 是否提升成功率；
5. 把 reasoning 换成随机/错误计划做 negative control。

## 27.5 Tool Use

高层 embodied agent 可调用：search、地图、数据库、motion planner、grasp planner、safety checker。工具调用把语言模型从“直接猜答案”变成 orchestrator。

Gemini Robotics ER 路线明确体现：reasoning model 负责工具与多步 plan，VLA 负责物理执行。

## 27.6 Progress Estimation

长任务不能只在最终看 success。定义 progress：

\[
p_t=P(\text{goal completion}\mid o_{\le t},g).
\]

或预测当前 phase \(k\)。如果 progress 长时间不增长，可触发 replan / recovery。

## 27.7 Self-Evaluation

self-evaluation 应基于外部可观测证据，而不是让同一模型无条件说“成功”。更可靠架构：

```text
policy proposal
   ↓
execution
   ↓
independent outcome verifier
   ↓
success / retry / replan / ask human
```

verifier 可来自视觉、force、task state、VLM judge 或 reward model，但都应做 calibration。

---

# Part 28　Memory：短期、长期与技能记忆

## 28.1 为什么 Context Window 不是 Memory

把过去所有 RGB frame 塞进 context：

\[
C_t=(o_0,o_1,\ldots,o_t)
\]

成本随任务长度增长，而且大量细节与当前任务无关。真正 memory system 要做**选择、压缩、检索、遗忘**。

## 28.2 Short-Term Visual Memory

短期 memory 需要保留最近几秒的精细动态：对象刚被移动、手是否滑落、哪个抓法失败。可用 temporal encoder：

\[
z_t^{short}=E_v(o_{t-k:t}).
\]

它比单帧 observation 更能处理自遮挡和短时动作连续性。

## 28.3 Long-Term Semantic Memory

更长时间尺度可把事件压成语言/结构化 note：

```text
- 已把锅盖放到左侧台面
- 冰箱上层还缺牛奶
- 上一次从杯把抓取失败
```

这相当于将高带宽视觉历史压缩成低带宽 semantic state。

## 28.4 Episodic / Semantic / Procedural

- **episodic**：具体经历，“昨天抓这个杯子滑了”；
- **semantic**：抽象知识，“湿玻璃表面摩擦低”；
- **procedural**：技能，“怎样沿杯把抓取”。

长期机器人系统需要三者相互转化：多次 episode → 归纳 semantic → 更新 procedure。

## 28.5 Multi-Scale Embodied Memory

2026 MEM 路线把短期视频与长期语言记忆结合，并让模型主动决定记什么。关键思想：不同时间尺度应使用不同 compression。

\[
M_t=\{M_t^{fast},M_t^{semantic},M_t^{episodic}\}.
\]

一个未来更完整的系统还需要跨天/跨场景存储、检索、权重衰减与冲突解决。

## 28.6 Causal Confusion

加入历史并不一定更好。如果训练中某个历史事件与 action 偶然相关，模型会依赖 spurious memory。例如“之前人手出现”恰好总发生在纠正之前，policy 可能把人手当成功能性 cue。

必须通过 intervention 检验 memory token 的因果作用。

## 28.7 Forgetting

无限积累 memory 会污染决策。可设计 importance：

\[
I(m)=\alpha\,\text{task relevance}+\beta\,\text{novelty}+\gamma\,\text{failure value}-\delta\,\text{age}.
\]

低 importance memory 被删除、压缩或归并。遗忘本身是智能系统的必要功能。

---

# Part 29　Learning from Experience：机器人怎样真正“越用越好”

## 29.1 Static Checkpoint 的局限

传统 pipeline：

```text
collect → train → deploy → freeze
```

真实通用机器人需要：

```text
pretrain → deploy → experience → diagnose → update → redeploy → ...
```

问题从 supervised learning 变成**持续数据闭环**。

## 29.2 Autonomous Rollout Data

机器人自己产生的数据包含：成功、失败、边界状态、恢复过程。它与 expert demonstration 的价值不同：expert 告诉模型“正确行为长什么样”，autonomous data 告诉模型“自己哪里会错”。

## 29.3 Corrections

人类 correction 可分：

- takeover：直接接管；
- action correction：修一小段轨迹；
- language coaching：说明下一步；
- preference：两种行为哪个好；
- outcome label：成功/失败；
- safety veto。

每种 feedback 监督粒度不同。

## 29.4 Offline → Online

现实上常先用大规模 offline data 得到强 prior，再在线改进：

\[
\pi_0\xrightarrow{D_{offline}}\pi_{base}
\xrightarrow{D_{online}}\pi_{adapted}.
\]

这比随机探索安全得多。

## 29.5 Experience Replay 与 Non-Stationarity

持续更新会遗忘旧能力。训练 mixture 可写：

\[
D_t=\lambda_{new}D_{new}+\lambda_{replay}D_{old}+\lambda_{anchor}D_{foundation}.
\]

权重决定 plasticity 与 stability 的平衡。

## 29.6 Failure Mining

不应平均采样所有 rollout。高价值 episode：

- 高 uncertainty；
- 临界失败；
- novel state；
- human intervention；
- long-horizon bottleneck。

可以定义 priority：

\[
p_i\propto \alpha |\delta_i|+\beta U_i+\gamma N_i.
\]

## 29.7 Precise Online RL

2026 的 VLA + efficient online RL 路线说明：foundation policy 提供 broad competence，在线 RL 可专门打磨高精度、速度和 dexterity。这种“通才 base + 局部自适应”很可能比一个永远冻结的 universal model 更现实。

## 29.8 Continual Evaluation

持续学习系统每次 update 都可能退化。必须维护 regression suite：

\[
E=E_{core}\cup E_{new}\cup E_{safety}\cup E_{cross-env}.
\]

只有新任务提升且核心能力不明显下降，update 才可接受。

---

# Part 30　World Models：预测世界，而不是只生成动作

## 30.1 定义

最小 world model：

\[
p_\phi(s_{t+1}\mid s_t,a_t).
\]

若 state 不可见，可在 latent：

\[
z_t=E(o_{\le t}),\qquad
p_\phi(z_{t+1}\mid z_t,a_t).
\]

视频 world model 则预测未来 observation：

\[
p_\phi(o_{t+1:t+H}\mid o_{\le t},a_{t:t+H-1}).
\]

## 30.2 为什么需要 World Model

直接 policy 学

\[
o\rightarrow a.
\]

world model 多了一条：

\[
(o,a)\rightarrow\text{future consequence}.
\]

它允许：planning、counterfactual、policy evaluation、synthetic data、uncertainty estimation。

## 30.3 State-Space vs Observation-Space

**State-space model**：紧凑、物理可解释，但 state definition/estimation 难；

**video/observation model**：可直接从像素学习，视觉丰富，但 photorealism 容易掩盖错误 physics。

理想系统可能同时维护 structured state 与 dense visual latent。

## 30.4 Latent Dynamics

\[
z_{t+1}=f_\phi(z_t,a_t).
\]

如果 \(z\) 只保留 reward/decision 相关信息，预测比完整像素容易。但 latent 是否具有真实 physical semantics 需要 probe 与 intervention 验证。

## 30.5 Video Prediction

video model 可生成动作后的未来画面，但常见失败：

- object hallucination/disappearance；
- 接触点漂移；
- 非物理穿透；
- hand/robot geometry 变形；
- action-following 不精确；
- 长时 identity 丢失。

视觉“像真的”不等于 dynamics 正确。

## 30.6 Action-Conditioned World Model

如果模型没有准确 action conditioning，就不能用于 planning。需要评测 intervention：同一初始帧给两个不同动作，未来是否产生正确分叉：

\[
p(o'\mid o,a_1)\ne p(o'\mid o,a_2).
\]

## 30.7 JEPA / Predictive Representation

JEPA 不直接生成像素，而预测 latent representation。V-JEPA 2 从大规模视频预训练 motion/predictive representation，再用少量 robot trajectory 做 action-conditioned model；V-JEPA 2.1 进一步增强 dense temporal feature。

这种路线假设：**预测抽象 latent 可能比生成所有像素更接近智能所需结构。**

## 30.8 Object-Centric World Model

将 dynamics 分解到对象：

\[
z_i^{t+1}=f(z_i^t,\{z_j^t\},a_t).
\]

优点是组合与 counterfactual；难点是 contact 使对象强耦合，软物体对象边界也不稳定。

## 30.9 Contact-Aware World Model

manipulation 关键事件往往发生在很小空间/时间尺度：第一次接触、slip、卡住、插入。仅预测大尺度 RGB motion 可能忽略这些决定成功的变量。

应显式加入 force/tactile/contact latent 或对 contact phase 提高 loss 权重。

## 30.10 Uncertainty

world model 应输出 distribution：

\[
p_\phi(z_{t+1:t+H}\mid z_t,a_{t:t+H-1}).
\]

多个可能未来不可简单平均。planning 应同时考虑 expected return 与 model uncertainty，避免利用模型盲区。

---

# Part 31　World Action Models 与生成式仿真

## 31.1 World Model 与 Policy 的断层

视频模型可能生成“正确未来”，却没有机器人可执行 action。反过来 policy 会输出 action，却不展示未来后果。

World Action Model 试图连接：

\[
\text{future prediction}\leftrightarrow\text{executable action}.
\]

## 31.2 四种连接范式

### Imagine → Execute

\[
o_t,g\rightarrow \hat o_{t+1:t+H}\rightarrow\text{inverse dynamics}\rightarrow A.
\]

优点：visual plan 易看；风险：inverse dynamics 可能无法实现生成视频。

### Future Feature → Action

world model 产生 future latent，action decoder 根据 latent 输出动作。

### Joint Video–Action Model

共同预测：

\[
p(o_{future},A\mid o_{past},g).
\]

动作与视频共享 latent，可减少两模型不一致。

### Auxiliary Prediction

主任务仍是 action policy，但训练时加 future prediction loss：

\[
L=L_{action}+\lambda L_{future}.
\]

NVIDIA FLARE/N1.5 类路线属于这一思想族。

## 31.3 Policy Evaluation in Generated Worlds

若 world model 足够准确，可以在虚拟未来中 rollout policy：

\[
\pi\rightarrow a_t\rightarrow WM\rightarrow \hat o_{t+1}\rightarrow\pi\rightarrow\cdots
\]

这会极大降低真机 eval 成本。但前提比“视频看起来真实”严格得多：virtual ranking 必须与 real ranking 高相关。

OSCAR 等 2026 工作开始探索 cross-embodiment generated evaluation。

## 31.4 RoboWM-Bench 给出的警告

2026 RoboWM-Bench 的核心发现是：当前视频 world model 即使视觉质量高，也常出现 spatial reasoning、contact instability 与 non-physical deformation，导致生成行为转成机器人动作后不可执行。

因此 world model evaluation 应包括：

\[
\boxed{\text{executability}}
\]

而不仅是 FVD/CLIP/video quality。

## 31.5 Robot-Factored World Model

一个有价值的 2026 方向是把“robot action 如何通过 controller 变成 robot motion”从 world model 中分离出来。先用已知 controller/kinematics 生成 nominal robot trajectory，再把 robot geometry render 给 world model，只让它学习环境如何响应。

这是一种强 inductive bias：

```text
action command
   ↓ known robot realization
nominal robot motion/render
   ↓ learned environment model
object/contact future
```

可以提高跨 robot generalization。

## 31.6 World Model 作为 Data Generator

生成数据可用于 policy pretraining，但必须防止错误 physics 被 policy 学进去。合成数据价值取决于：

\[
\text{utility} \approx \text{coverage gain} - \text{model-bias contamination}.
\]

因此应先做 downstream policy utility test，而非只看 synthetic video visual score。

## 31.7 Language-Conditioned World Models

2026 Qwen-RobotWorld 等工作把 language 作为统一 action/intent interface，试图跨 manipulation、navigation、driving、human-to-robot 预测未来。这扩大数据规模，但语言 action 比低层 control 更模糊，physical executability 更需要独立验证。

## 31.8 Human-to-Robot World Generation

世界模型也可把 human demonstration 转成指定 robot embodiment 的未来视频。H2R-Bench 等 2026 评测表明，当前模型在 embodiment consistency、functional contact 和 task execution 上仍明显困难。

## 31.9 Test-Time Search

若 world model 可评估候选 action：

1. sample \(A^{(1)},\ldots,A^{(K)}\)；
2. rollout \(WM(o,A^{(k)})\)；
3. score goal progress / safety；
4. 执行最佳候选。

\[
A^*=\arg\max_{A^{(k)}}S(WM(o,A^{(k)}),g).
\]

这将 inference compute 换成更可靠行为，类似 model-predictive planning。

---

# Part 32　Counterfactual、Causality 与 Mechanism

## 32.1 Prediction 不等于 Causation

模型从历史数据学到

\[
p(o_{t+1}\mid o_t,a_t)
\]

如果 action 分布高度偏置，它可能用场景 shortcut 预测未来，而不真正理解 action effect。

需要 intervention：同一 state 主动施加不同动作，观察结果分叉。

## 32.2 Counterfactual Control

决策真正需要问：

> “如果我做 A，而不是 B，会发生什么？”

即比较

\[
Y(a_1),Y(a_2),\ldots.
\]

World model 若只能重放 dataset 中最常见 future，而不能正确响应 unseen action，就不能承担 planning。

## 32.3 Mechanism Discovery

更强目标不是记住每个 task trajectory，而是发现可复用规律：

- 推物体：接触点 + 力方向 → motion；
- 拉抽屉：constraint axis；
- 双手搬物：relative constraint；
- 折衣：material + contact topology。

若模型能显式或隐式组合这些 mechanism，新任务所需数据可能显著下降。

## 32.4 Compositionality

假设技能机制集合 \(\{m_i\}\)，新任务由 composition：

\[
\mathcal T_{new}=m_{i_1}\circ m_{i_2}\circ\cdots\circ m_{i_k}.
\]

真正组合泛化要求训练数据中未出现完整组合，只出现 constituents。否则所谓“组合”可能只是 trajectory memorization。

## 32.5 Falsifiable Test

对任何宣称“学到物理规律”的模型，应至少测试：

1. unseen combination；
2. changed embodiment；
3. changed material/dynamics；
4. intervention on causal variable；
5. irrelevant visual change；
6. counterfactual ranking；
7. mechanism transfer with less data。

---

# 本卷统一架构

```text
                ┌──────── semantic / episodic memory ───────┐
                │                                            │
observation → state/belief → reasoning → candidate actions  │
      │             │             │                │          │
      │             └──── world model / counterfactual ──────┘
      │                              │
      │                         future scores
      │                              │
      └──── fast feedback ← execute chosen action
                                   │
                              experience
                                   │
                          correction / reward
                                   │
                                update
```

这比“VLA 直接从图像到动作”多出的部分，正是长期物理智能可能需要的核心结构。

## 必做实验

1. POMDP memory task：frame stacking vs RNN vs semantic memory；
2. 长 horizon 任务加入 progress estimator；
3. autonomous rollout + recovery data flywheel；
4. latent dynamics on Push-T；
5. image/video world model 对两个 counterfactual action 的分叉；
6. 用 learned world model 做 MPC，并测 model bias 随 horizon；
7. generated video → inverse dynamics → simulated execution，测 executability；
8. world-model visual metric 与 downstream policy success 做相关性；
9. unseen composition / causal intervention negative controls。

## 核心来源

- Physical Intelligence MEM — https://www.pi.website/research/memory
- Physical Intelligence Online RL — https://www.pi.website/research/rlt
- V-JEPA 2 / 2.1 — https://github.com/facebookresearch/vjepa2
- Meta V-JEPA 2 overview — https://ai.meta.com/research/vjepa/
- GR00T N1.5 / FLARE — https://research.nvidia.com/labs/gear/gr00t-n1_5/
- RoboWM-Bench, CVPR Workshops 2026 — arXiv:2604.19092
- OSCAR, 2026 — arXiv:2606.04463
- Robot-Factored World Models, 2026 — arXiv:2607.22535
- H2R-Bench, 2026 — arXiv:2608.13049
- Qwen-RobotWorld, 2026 — arXiv:2606.17030
