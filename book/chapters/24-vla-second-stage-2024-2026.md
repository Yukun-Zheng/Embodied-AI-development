# Part 24　VLA 的第二阶段：2024–2026 的架构分化

> 本章时间截面：2026-09-14。这里讨论的是“架构分化”，不是模型排行榜。任何公司或项目的能力描述都要区分：**官方演示、公开评测、论文证据、独立复现**。

## 学习目标

读完本章，你应该能回答四个问题：

1. 为什么 2024 之后的 VLA 不再只是“VLM 后面接 action head”？
2. π、GR00T、Gemini Robotics、Helix 等路线真正分歧在哪里？
3. 一个模型声称“通用”“跨本体”“whole-body”时，具体跨越了哪些接口？
4. 怎样把架构创新与数据规模、后训练、控制系统改进分开评估？

---

## 24.1 第二阶段的核心变化

第一阶段 VLA 的基本模板可以写成：

```text
image + language + robot state
        ↓
large multimodal backbone
        ↓
action head
        ↓
action chunk / token sequence
```

第二阶段并没有抛弃这个骨架，而是在五个方向发生分化：

```text
(1) action generation: token / diffusion / flow / regression
(2) temporal architecture: synchronous / asynchronous / multi-rate
(3) embodiment interface: fixed robot / adapters / morphology-conditioned
(4) learning regime: imitation / post-training / offline RL / online RL
(5) control scope: arm → bimanual → hands → loco-manipulation → whole body
```

所以“某个模型是不是 VLA”已经不是最重要的问题。更重要的是它在这五个轴上选了什么设计。

---

## 24.2 π0：连续动作专家与 Flow Matching

π0 代表了一个重要转折：大模型负责语义和多模态条件，动作端不必再完全依赖离散 token 自回归，而可以使用连续生成模型。

可以抽象成：

\[
h = f_{\text{VLM}}(o_t, l, s_t),
\]

动作专家学习条件速度场：

\[
v_\theta(a_\tau, \tau, h),
\]

再由 ODE 从噪声或简单先验逐渐运输到动作分布。

关键不是“用了 flow matching”这几个字，而是：

- 动作空间保留连续几何；
- 可一次生成 action chunk；
- 语义 backbone 与高频动作专家可以承担不同功能；
- 为之后的实时 chunking、RL post-training 和多本体适配留下了接口。

---

## 24.3 FAST：动作 tokenization 并没有消失

连续生成并不意味着离散动作路线失效。FAST 一类方法研究如何把连续机器人轨迹压成更高效的 token 序列，使大模型能够以语言模型式目标训练动作。

核心权衡是：

\[
\text{compression ratio}
\leftrightarrow
\text{control precision}
\leftrightarrow
\text{autoregressive latency}.
\]

动作 tokenization 真正要解决的不是“把浮点数变整数”，而是：

> 怎样找到对机器人控制足够精确、又对 sequence model 足够高效的时间—动作码本？

---

## 24.4 π0.5：Open-World Generalization

π0.5 把问题从“训练任务内多任务学习”推进到更开放的环境和任务组合。其研究意义不是某几个 demo，而是尝试让大规模预训练知识、机器人数据与长任务结构发生更紧密的连接。

评价 open-world generalization 时必须至少拆成：

- novel object；
- novel scene；
- novel instruction；
- novel task composition；
- novel embodiment；
- perturbation recovery。

把其中任意一项成功称为“open world”都过于宽泛。

---

## 24.5 π*0.6：从 Demonstration 走向 Experience

π*0.6 的意义在于明确把 **autonomous experience + reinforcement learning** 放到 generalist VLA 的后训练流程里。

一个典型流程可以写成：

```text
large-scale pretraining
      ↓
offline RL / value-aware pretraining
      ↓
task demonstrations
      ↓
on-robot autonomous experience
      ↓
correction + reward
      ↓
RL post-training
```

这改变了 VLA 的目标：

> 不只是“模仿人怎么做”，而是“部署后能否根据成败继续变好”。

截至本书时间截面，Physical Intelligence 公开报告 π*0.6 在咖啡、叠衣、装箱等任务上利用 on-robot experience 提升吞吐与成功率。这里应视为重要公开证据，但仍应区分官方结果与跨实验室独立复现。

---

## 24.6 π0.7：Steerability 与组合泛化

π0.7 把“prompt”从单一语言命令扩展为更广泛的控制条件：

```text
language
metadata
control modality
visual subgoal
language coaching
        ↓
steerable policy
```

这提出了一个比 language following 更一般的问题：

\[
\pi(a\mid o, c),
\]

其中 \(c\) 不再只是任务名字，而可以描述**如何做、做到什么程度、遵守什么中间约束**。

官方报告中，π0.7 展示了对未直接演示任务的组合式泛化迹象。科学上真正应该验证的是：

1. 新任务能否分解为训练技能的已知组合？
2. 是语言 coaching 在起作用，还是视觉/场景相似性？
3. compositional generalization 是否跨场景、跨对象、跨本体仍成立？
4. 是否存在结构化负对照能击穿这种“涌现”？

---

## 24.7 GR00T：Humanoid Foundation Model 路线

GR00T 系列把 foundation policy 明确推向 humanoid 与 cross-embodiment。

### GR00T N1 / N1.5

核心思想包括：

- 大规模视觉语言知识；
- humanoid / bimanual demonstrations；
- action expert；
- embodiment-specific post-training；
- synthetic data 与 simulation pipeline。

### GR00T N1.6

NVIDIA 在公开技术页面中描述 N1.6 相对 N1.5 的变化包括：

- 更强的 VLM backbone；
- 更大的 DiT/action component；
- 针对 embodied reasoning 的视觉语言训练；
- 在多种双臂/人形平台上继续验证 post-training。

这里最值得研究的不是版本号，而是：

> **VLM 的语义能力、DiT 的动作分布建模、机器人专属后训练之间究竟怎样分工？**

---

## 24.8 Gemini Robotics：VLA 与 Embodied Reasoning 分层

Gemini Robotics 路线清楚体现了一个趋势：高层 reasoning 与低层 action 不一定应该塞进同一个同步循环。

抽象为：

```text
Embodied Reasoning Model
  - goal decomposition
  - progress tracking
  - human interaction
  - multi-robot coordination
          ↓
VLA
  - perception-to-action
  - dexterous control
  - whole-body control
          ↓
low-level control / hardware
```

这重新提出经典机器人学里的分层问题：只是 planner 换成了 multimodal reasoning model，policy 换成了 learned VLA。

### Gemini Robotics 2

2026 年公开版本把控制范围推进到：

- whole-body humanoid control；
- dexterous hands / grippers；
- multi-robot collaboration；
- 较长时程任务中的 progress understanding；
- on-device 版本与新 embodiment 适配。

注意：“whole-body VLA”并不意味着低层 torque loop 消失。读者应继续追问 action interface、servo rate、balance controller 和 safety layer。

---

## 24.9 Helix：Multi-Rate、On-Board 与 Whole-Body

Figure 的 Helix 路线特别适合用来理解 **多时间尺度**。

早期 Helix 明确采用快慢双系统：

```text
System 2: VLM-level semantics, ~slow rate
              ↓ latent intent
System 1: visuomotor policy, high rate
              ↓
continuous humanoid control
```

公开技术说明中，早期 Helix 的高层模块运行在个位数 Hz，而低层 visuomotor policy 可运行到约 200 Hz。训练时甚至显式建模两者的时间偏移，以缩小 deployment latency gap。

Helix 02 又把范围扩展到 full-body loco-manipulation，并把 vision、touch、proprioception 接入统一 visuomotor 系统。

它给出的核心教训是：

> 大模型时代并没有消灭控制频率问题，反而让 multi-rate architecture 更重要。

---

## 24.10 开源 VLA 生态

OpenVLA、SmolVLA、LeRobot 等开放生态的重要性不是简单“模型免费”，而是它们让研究者可以真正研究：

- action representation；
- fine-tuning recipe；
- dataset mixture；
- low-cost deployment；
- policy latency；
- cross-robot adaptation；
- reproducible benchmark。

没有开放实现，许多“架构比较”只能停留在公司演示层面。

---

## 24.11 3D-aware、Bimanual、Dexterous 与 Humanoid 分支

随着 action dimension 提升，纯 2D semantic feature 的不足更加明显。

研究开始沿几个方向扩张：

- point-cloud / 3D-aware input；
- wrist + external multi-view；
- bimanual relative representation；
- dexterous hand state；
- tactile + vision；
- base / legs / torso / arms / hands 的 unified whole-body action。

核心问题变成：

\[
\text{semantic generality}
+
\text{geometric precision}
+
\text{high-dimensional control}
+
\text{real-time feedback}.
\]

四项必须同时成立。

---

## 24.12 2026 VLA 的共同结构

不同系统虽然名字很多，但可以抽象为：

```text
Internet-scale prior
        +
Robot multimodal data
        +
Embodiment/state interface
        ↓
Shared representation / multimodal backbone
        ↓
Action generator
        ↓
Temporal execution layer
        ↓
Robot-specific low-level system
        ↓
Experience / post-training loop
```

真正的架构分歧集中在：

1. shared representation 是否与动作梯度共同训练；
2. action generator 是 AR、diffusion、flow 还是 regression；
3. 是否多时间尺度；
4. embodiment 是否显式条件化；
5. 是否允许部署后学习；
6. world model / memory / reasoning 是否独立存在；
7. safety 是否是外部 shield 还是进入 policy training。

---

## 24.13 不要被版本号掩盖的科学问题

### 问题 A：Scaling 到底带来什么？

需要把能力变化分解成：

\[
\Delta P = \Delta P_{data}+\Delta P_{model}+\Delta P_{objective}+\Delta P_{system}.
\]

现实中这四项高度耦合，论文常常无法完全隔离。

### 问题 B：语义泛化会自动变成物理泛化吗？

不会。认识“拉链”与精确捏住拉链头是完全不同的能力。

### 问题 C：Whole-body 是 action dimension 变大了吗？

不只是。它同时引入：

- floating-base dynamics；
- balance；
- contact switching；
- self-collision；
- moving camera；
- changing reachable set。

### 问题 D：所谓 emergent capability 如何证伪？

必须设计组合负对照、数据去重、几何新颖性控制和多 seed 重复。

---

## 最小实验

选择同一机器人任务，固定数据和视觉 encoder，仅改变 action generator：

1. MSE regression；
2. autoregressive token；
3. diffusion；
4. flow matching。

统一：

- action horizon；
- control frequency；
- parameter budget；
- training steps；
- observation history。

评估：

- success；
- cycle time；
- action smoothness；
- recovery；
- inference latency；
- perturbation robustness。

这个实验比单纯复现四篇论文更能回答“架构分化到底改变了什么”。

---

## Source anchors

- Physical Intelligence, π0.7: https://www.pi.website/blog/pi07
- Physical Intelligence, π*0.6: https://www.pi.website/blog/pistar06
- Physical Intelligence, Real-Time Action Chunking: https://www.pi.website/research/real_time_chunking
- NVIDIA GR00T N1.6: https://research.nvidia.com/labs/gear/gr00t-n1_6/
- Google DeepMind, Gemini Robotics 2: https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Figure, Helix: https://www.figure.ai/news/helix
- Figure, Helix 02: https://www.figure.ai/news/helix-02

---

## 本章结论

2024–2026 的 VLA 发展不是“Transformer 越来越大”，而是机器人基础模型开始正面碰撞经典机器人学长期存在的问题：**连续控制、时延、多频率、接触、跨本体、whole-body、安全和经验学习**。真正有价值的研究，需要把这些系统变量从品牌和版本号中剥离出来。