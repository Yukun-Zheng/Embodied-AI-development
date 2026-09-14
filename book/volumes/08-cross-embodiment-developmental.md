# Volume VIII　持续学习、跨本体与发展型智能

> 如果一个智能系统只能服务一台固定机器人、一个固定实验室、一次离线训练，它距离“通用具身智能”仍然很远。本卷研究三个更长期的问题：**知识如何跨身体迁移？系统如何在多年交互中继续学习而不遗忘？一个机器人能否像发展中的个体一样主动练习、形成记忆并扩展能力？**

---

# Part 37　Cross-Embodiment Intelligence

## 37.1 Embodiment 到底包含什么

一个 embodiment 不只是 robot ID，而是一组结构与能力：

\[
e=(\mathcal G_{body},\mathcal A,\mathcal O,\mathcal D,\mathcal L),
\]

其中：

- \(\mathcal G_{body}\)：身体拓扑与几何；
- \(\mathcal A\)：动作空间与执行器；
- \(\mathcal O\)：传感器与 observation interface；
- \(\mathcal D\)：动力学；
- \(\mathcal L\)：joint/torque/reachability 等限制。

因此 cross-embodiment 不是把数据拼起来，而是寻找这些差异之上的共享结构。

## 37.2 Morphology

Morphology 决定身体图：

\[
G_e=(V_{link/joint},E_{connection}).
\]

固定长度 robot-state vector 难以适配关节数不同的身体；graph / tokenized body representation 更自然：每个关节/连杆为 token，并编码 type、axis、limit、geometry、parent-child relation。

## 37.3 Action Space Mismatch

两台机器人可能分别使用：

\[
a^A\in\mathbb R^7,
\qquad
a^B\in\mathbb R^{23}.
\]

直接共享 action head 没有意义。常见解决路径：

1. **embodiment-specific head**；
2. **universal task space**，如 end-effector delta；
3. **body-token decoder**，按每个 joint 生成动作；
4. **latent action**，再由 embodiment adapter 映射；
5. **skill/subgoal transfer**，不直接迁 motor action。

## 37.4 Observation Space Mismatch

camera 数量、位置、深度/触觉、proprioception dimension 都不同。因此共享模型必须区分：

\[
\text{world information}
\quad\text{vs}\quad
\text{sensor-specific encoding}.
\]

多 camera token + modality mask + calibration metadata 是工程方法；更强目标则是学习 sensor-invariant world representation。

## 37.5 Morphology-Conditioned Policy

\[
a_t=\pi_\theta(o_t,g,e).
\]

若 \(e\) 显式描述身体，理论上同一 policy 可根据 morphology 改变行为。关键实验不是“训练集里的多机器人都能跑”，而是 unseen morphology 的 zero/few-shot transfer。

## 37.6 Universal End-Effector Space

对操作任务，可把共享 action 设为：

\[
a^{task}=[\Delta T_{L},\Delta T_R,g_L,g_R].
\]

每个 robot 用自己的 IK/WBC 实现。这显著降低 morphology mismatch，但损失了关节级策略可表达性，而且对 humanoid balance、dexterous hand 等任务不够。

## 37.7 Latent Action

学习 embodiment-independent latent \(z_a\)：

\[
z_a=E_a(a^{(e)},e),
\qquad
a^{(e)}=D_a(z_a,e).
\]

若 \(z_a\) 真正表示“向左推”“保持相对位姿”这类 effect，而非特定 actuator pattern，就更利于跨身体迁移。

验证方法是 cross-decoding：A 机器人 action 编码成 latent，再由 B decoder 执行是否产生相似 world effect。

## 37.8 Effect-Centric Representation

比“动作相同”更合理的是“结果相同”。定义 effect：

\[
\Delta s^{world}=s_{t+1}-s_t.
\]

两个 embodiment 动作不同，但若实现相似 object displacement/contact outcome，可被视为等价 skill。

这将 cross-embodiment 从 action alignment 转为 **effect alignment**。

## 37.9 Cross-Robot Dataset

数据混合：

\[
D=\bigcup_e D_e.
\]

必须统一至少：

- timestamp；
- coordinate convention；
- state/action semantic；
- normalization；
- language/task labels；
- episode termination；
- embodiment metadata。

Open X-Embodiment 的历史价值就在于把这个问题第一次大规模公开化。

## 37.10 Human-to-Robot Transfer

人类是一个特殊 embodiment。人视频提供巨大行为分布，但没有 robot action。可迁移层级从低到高：

```text
pixel motion
  → hand/object trajectory
  → contact / affordance
  → subgoal / skill
  → task strategy
  → abstract mechanism
```

越高层越容易跨身体，但越难自动从视频准确抽取。

## 37.11 Motion Transfer

retargeting 的目标是保留任务效果，而不是复制 joint angle：

\[
\min_{q_r} L_{task}(FK_r(q_r),X_{human})
+\lambda L_{posture}
\]

subject to robot limits / collision / balance。

Gemini Robotics 1.5 等系统展示了跨 embodiment motion transfer，但“能迁移 motion”仍不等于“拥有 morphology-independent policy”。

## 37.12 Calibration / Adaptation to New Bodies

新机器人部署常需要：

1. kinematic calibration；
2. sensor extrinsics；
3. action scaling；
4. dynamics identification；
5. a few demonstration / autonomous adaptation。

理想 foundation policy 应让 adaptation cost 随 pretraining diversity 降低：

\[
N_{adapt}(e_{new})\downarrow
\quad\text{as}\quad
\text{pretraining diversity}\uparrow.
\]

## 37.13 “一个 checkpoint 控很多机器人”意味着什么

必须区分：

- 同一个文件但每台 robot 有专属 adapter；
- 同 backbone + 多 action heads；
- 同一 universal action interface；
- 新 robot few-shot；
- zero-shot unseen embodiment。

只有最后两类才真正接近强 cross-embodiment generalization。

## 37.14 Cross-Embodiment 的上限

若两种身体能力差异巨大，某些技能根本不可迁移。没有手的移动机器人不能执行五指 in-hand manipulation。因此目标不是“所有能力无条件共享”，而是：

\[
\text{transfer what is invariant, adapt what is embodiment-specific}.
\]

---

# Part 38　Continual、Lifelong 与 Developmental Robot Learning

## 38.1 Continual Learning

传统训练假设数据集固定；continual learning 数据按时间到来：

\[
D_1,D_2,\ldots,D_t,\ldots
\]

模型在学习 \(D_t\) 时不能完整重训全部历史数据，也不能严重破坏以前能力。

## 38.2 Catastrophic Forgetting

新任务梯度可能覆盖旧任务重要参数：

\[
\theta_{t+1}=\theta_t-\eta\nabla L_{new}
\]

但 \(L_{old}(\theta_{t+1})\) 显著上升。

机器人尤其危险，因为一次在线适应不应让原本可靠的安全技能突然失效。

## 38.3 Replay

保留旧 experience buffer：

\[
L=L_{new}+\lambda\mathbb E_{(x,y)\sim B_{replay}}L(x,y).
\]

难点从“有没有 replay”转向“记什么”：稀有 failure、代表性 skill、safety-critical state 应有更高保留优先级。

## 38.4 Regularization

限制重要参数变化：

\[
L=L_{new}+\lambda\sum_i F_i(\theta_i-\theta_i^*)^2.
\]

EWC 类方法用 Fisher 近似参数重要性。对超大 foundation model，全参数 importance 成本高，因此 adapter / modular parameterization 更现实。

## 38.5 Parameter Isolation

每个新任务增加 adapter / expert：

\[
\theta=\theta_{shared}\cup\theta_{task}.
\]

优点是减少干扰，缺点是参数随任务数增长，且知识容易被割裂。

真正难题是决定：**什么时候复用，什么时候新增长，什么时候合并。**

## 38.6 Dynamic Architecture

模型容量可以随经验增长：

\[
\mathcal G_t\rightarrow\mathcal G_{t+1}.
\]

但简单“加一层/加一个 expert”并不等于 biological plasticity。必须有 capacity budget、贡献评估、合并/删除机制，否则只是无限扩参数。

## 38.7 Online Adaptation

在线 adaptation 可能发生在多个层次：

- calibration parameter；
- normalization；
- visual adapter；
- dynamics model；
- policy residual；
- memory / retrieval；
- full model weight。

越靠底层参数风险越低；越靠 full model plasticity 越强但回归风险越高。

## 38.8 Test-Time Adaptation

在没有 label/reward 的情况下，利用 self-supervised signal 调整模型，例如 temporal consistency、reconstruction、prediction error。

危险是自监督目标可能与 task objective 不一致。部署前必须测试 adaptation 是否会让控制 drift。

## 38.9 Lifelong Robot Learning

lifelong 要处理：

\[
\text{skill acquisition}+
\text{retention}+
\text{transfer}+
\text{maintenance}+
\text{recovery}.
\]

不仅是 continual-learning benchmark 上的 average accuracy。

## 38.10 Developmental Robotics

Developmental robotics 借鉴婴幼儿：能力不是一次预训练装入，而通过长期身体交互逐步形成。

重要原则：

1. curriculum 来自环境和自身能力；
2. perception 与 action 共同发展；
3. 身体变化会改变学习；
4. social interaction 也提供监督；
5. internal motivation 决定探索什么。

## 38.11 Curriculum as Development

课程不是手工把环境 level 从 1 调到 10，而可根据 competence 自动调节：

\[
P(task_i)\propto f(\text{learning progress}_i).
\]

太容易没有信息，太难没有学习信号；最大学习进步区域最值得练习。

## 38.12 Intrinsic Motivation

常见内在奖励：novelty、prediction error、information gain、empowerment。

例如 curiosity：

\[
r_t^{int}=\|\phi(s_{t+1})-\hat\phi(s_{t+1}\mid s_t,a_t)\|^2.
\]

但纯 prediction-error curiosity 会被随机电视等不可预测噪声吸引，因此需区分 epistemic novelty 与 irreducible randomness。

## 38.13 Memory Formation 与 Consolidation

长期学习不能每个 timestep 都更新全部长期知识。可借鉴 fast/slow weights：

```text
fast memory / adapter
      ↓ repeated evidence
consolidation
      ↓
slow semantic / skill model
```

这类似 hippocampus–cortex 的功能分工思想，但应作为工程假说验证，而不是简单生物类比。

## 38.14 Forgetting as Function

遗忘不是 defect。若环境改变、sensor 换了、旧策略不再安全，就应降低旧经验权重。

可用 recency × utility × confidence：

\[
w_i=f(r_i,u_i,c_i).
\]

关键是**选择性遗忘**，而不是 catastrophic forgetting。

## 38.15 Structural Plasticity

强 structural plasticity 应允许 computation graph / module relation 改变，而非只 mask weight：

\[
G_{t+1}=\mathcal U(G_t,E_t).
\]

需要同时解决：

- 新模块何时生成；
- 如何初始化；
- 如何连接旧模块；
- 如何信用分配；
- 低贡献结构何时压缩；
- 怎样不破坏实时性。

## 38.16 Growth / Pruning 的局限

简单 magnitude pruning、network widening、copy expert 都是工程手段，但尚未证明可以产生开放式能力增长。结构变化只有在**提高可组合性、样本效率或长期稳定性**时才有科学意义。

## 38.17 不区分“训练/推理”的系统

现实生物不存在严格 train/eval 开关。机器人也可以持续：

\[
\text{observe}\rightarrow\text{act}\rightarrow\text{evaluate}\rightarrow\text{update memory/model}.
\]

但“持续更新”不能等于“每步 SGD 全模型”。实际可能是多时间尺度：

```text
milliseconds : state / reflex
seconds      : working memory
minutes      : local adaptation
hours        : skill update
nights       : replay / consolidation / regression test
weeks        : architecture revision
```

这是更可控的 developmental system。

## 38.18 从 Fixed Model 到 Developing Agent

fixed model 问：“训练后性能是多少？”

developing agent 更应画 learning curve：

\[
C_i(t)=\text{capability}_i\text{ after lifetime experience }t.
\]

评价对象从 checkpoint 变成**整个生命史学习过程**。

---

# Part 39　Self-Evolving Physical Intelligence

## 39.1 “自进化”必须可证伪

不能把自动 fine-tuning 叫 self-evolving。至少满足：

1. 系统能在没有人工逐任务标注的情况下产生学习数据；
2. 能检测能力缺口；
3. 能选择练习目标；
4. 学会以前没有的能力；
5. 保留关键旧能力；
6. 改进可由独立 benchmark 验证；
7. update 不是只扩大参数或记忆库。

## 39.2 Capability Acquisition

把能力定义成任务分布上的函数：

\[
C_k(\theta)=\mathbb E_{x\sim\mathcal T_k}[S(\pi_\theta,x)].
\]

真正新增能力要求存在 \(k\) 使

\[
C_k(\theta_{t+1})\gg C_k(\theta_t)
\]

且该任务组合未直接演示。

## 39.3 Autonomous Practice

机器人可在安全 sandbox 中主动练习：

1. 估计 competence；
2. 找 failure frontier；
3. 生成 practice episode；
4. 收集 outcome；
5. 更新；
6. regression test。

类似自动 curriculum，但目标是持续扩展能力边界。

## 39.4 Self-Generated Goals

goal generator：

\[
g_t\sim G(M_t,\mathcal E,C_t).
\]

好的目标应：可执行、有学习价值、不过于重复、符合 safety budget。

可以最大化预计 learning progress：

\[
g^*=\arg\max_g \mathbb E[\Delta C\mid g]-\lambda \mathrm{Risk}(g).
\]

## 39.5 Failure-Driven Evolution

failure 不只是负 reward，而是结构化诊断：

```text
failure
  ↓
which assumption failed?
  ↓
missing perception / memory / model / skill / controller?
  ↓
collect targeted evidence
  ↓
update smallest responsible component
```

这比全模型盲目 fine-tune 更接近工程上的“自我修复”。

## 39.6 Reflection 的可操作定义

机器人 reflection 不应只生成文字“我失败因为没抓稳”。真正 reflection 必须产生后续可验证变化，例如：

- 修改 next trial 的 grasp；
- 增加 active view；
- 调低速度；
- 请求 tactile confirmation；
- 写入 episodic memory；
- 触发 targeted training。

因此可定义 reflection utility：

\[
U_R=\mathbb E[S_{next}\mid R]-\mathbb E[S_{next}\mid \text{no }R].
\]

## 39.7 Self-Modification 与安全边界

允许模型修改自己会带来回归与安全风险。可采用 staged update：

```text
candidate update
     ↓
offline validation
     ↓
simulation / shadow mode
     ↓
safety regression suite
     ↓
limited deployment
     ↓
full promotion / rollback
```

机器人不能像网页推荐系统一样未经验证直接在线更新关键 torque policy。

## 39.8 Architecture Search vs Development

AutoML 搜索架构通常在外部 optimizer 主导下重复训练候选模型；developmental architecture 则要求系统内部根据自己的经验改变结构，并继承已有知识。

二者评价指标也不同：

\[
\text{developmental efficiency}
=\frac{\Delta \text{capability}}{\text{new physical interaction}+\text{compute}+\text{memory}}.
\]

## 39.9 Mechanism Library

一种候选方向是形成可组合 mechanism：

\[
\mathcal M=\{m_1,m_2,\ldots\}
\]

每个 mechanism 有适用条件、预测 effect 和 confidence。新任务通过 composition/search 组合，而不是每次从 dense network 重新拟合。

这与 classical skill library 不同之处在于：mechanism 应可从经验中自动发现、修改和合并。

## 39.10 Structural Credit Assignment

如果系统由多个可生长 module 组成，失败后要判断“是哪一部分缺能力”。这形成比 gradient credit assignment 更高层的问题：

\[
\text{failure}\rightarrow \text{module responsibility}\rightarrow\text{structure update}.
\]

错误归因会导致结构无意义膨胀。

## 39.11 Open-Endedness

真正 open-ended 系统没有固定最终 task list。环境持续提供 novelty，agent 持续产生新目标和能力。

但“无限随机探索”不等于 open-ended intelligence。必须出现**累积复杂性**：后来的能力利用并重组早期能力。

## 39.12 Developmental Benchmark

传统 benchmark 比 checkpoint；发展型 benchmark 应比较 lifetime protocol：

```text
Stage A environment → freeze evaluation
        ↓
Stage B new environment → learn
        ↓
re-evaluate A + B + composition
        ↓
Stage C ...
```

核心指标：

\[
\text{plasticity},\quad
\text{retention},\quad
\text{forward transfer},\quad
\text{backward transfer},\quad
\text{growth efficiency}.
\]

## 39.13 一个可实现的多时间尺度中枢

可以把长期发展系统组织为：

```text
Fast sensorimotor loop
        │
        ├── short-term predictive state
        │
        ├── episodic memory
        │
        ├── skill / mechanism library
        │
        ├── semantic world model
        │
        └── developmental controller
                 ├─ choose practice
                 ├─ diagnose failure
                 ├─ consolidate
                 ├─ grow/merge/prune
                 └─ regression/safety gate
```

这只是研究框架，不是已解决架构。每个箭头都应对应可证伪实验。

---

# 本卷的核心矛盾：Plasticity vs Stability

长期具身智能始终面对：

\[
\boxed{\text{learn new things quickly} \quad\text{vs}\quad \text{do not destroy old reliable behavior}}
\]

进一步还有：

\[
\text{shared abstraction}\quad\text{vs}\quad\text{embodiment-specific control}
\]

和

\[
\text{open-ended growth}\quad\text{vs}\quad\text{bounded compute/memory/safety}.
\]

真正下一代架构必须同时处理这三组张力。

## 必做实验

1. 两种不同 action-space 机械臂做 cross-embodiment transfer；
2. universal EE action vs embodiment-specific joint action；
3. graph body encoder 在 unseen DOF 上测试；
4. human trajectory → robot retarget → task execution；
5. sequential tasks A→B→C，测 forgetting；
6. replay / adapter / regularization 对比；
7. 自动 curriculum 依据 learning progress 选择任务；
8. 多场景长期训练，测 forward/backward transfer；
9. failure-driven targeted data collection；
10. module growth / merge / prune，固定 compute budget 做负对照。

## 延伸阅读

- Open X-Embodiment / RT-X.
- Developmental Robotics literature: Cangelosi & Schlesinger, *Developmental Robotics*.
- Continual learning surveys and EWC / replay / progressive-network families.
- Physical Intelligence human-to-robot transfer — https://www.pi.website/research/human_to_robot
- Gemini Robotics 1.5 cross-embodiment motion transfer.
- NVIDIA GR00T cross-embodiment humanoid foundation models.

> 本卷的自进化/结构可塑部分属于开放研究纲领。教材会明确区分“已被广泛验证的方法”与“尚待证伪的研究假说”，不把未来愿景包装成现有事实。
