# Part 23　VLA 的形成：2022–2024 的关键谱系

## 学习目标

本章不按“模型排行榜”讲 VLA，而是追踪一条问题链：generalist sequence modeling → language grounding → embodied multimodal LM → scaled robot transformer → web knowledge 到 action → cross-robot data → open generalist policy。读完应能解释 Gato、SayCan、PaLM-E、RT-1、RT-2、Open X-Embodiment / RT-X、RoboCat、Octo、OpenVLA 分别解决了哪一层问题，以及它们没有解决什么。

---

## 23.1 什么才算 VLA

广义 Vision-Language-Action：

\[
\pi_\theta(a_{t:t+H}\mid I_{\le t},l,s_{\le t}).
\]

最低要求是视觉与语言共同影响可执行机器人 action。

应区分：

- VLM planner：输出文字 subgoal；
- embodied LM：理解 sensor/context，但不直接控制；
- VLA：输出 action / action chunk；
- full embodied agent：VLA + memory + tools + safety + learning。

术语混用会夸大“模型已经会控制”的程度。

## 23.2 2022 前后的背景

Robot learning 已经有：

- large-scale imitation；
- Transformer policy；
- language-conditioned manipulation；
- multimodal pretraining；
- sim-to-real RL。

真正缺的不是“第一次把 Transformer 用在 robot”，而是把 web-scale semantic prior、robot-scale data 和可执行 action 接成统一可扩展系统。

## 23.3 Gato：Generalist Sequence Model

Gato 把不同 domain 的 observation/action 都序列化为统一 token sequence：

\[
x_{1:T}\rightarrow p(x_{t+1}\mid x_{\le t}).
\]

概念贡献：一个 Transformer 可以通过统一序列接口覆盖语言、游戏、机器人等任务。

它没有证明“一个大模型已经能成为通用机器人”，但建立了 generalist agent 的 scaling 想象：任务边界可以由数据而不是独立模型定义。

## 23.4 Gato 留下的问题

统一 tokenization 会把高度不同的 modality 强行塞进一个序列：

- image patch；
- text token；
- discrete action；
- continuous state quantization。

机器人随后十年的重要问题之一，就是重新思考**哪些东西应该统一，哪些应该保留物理结构**。

## 23.5 SayCan：语言知识 × Affordance

SayCan 没有直接让语言模型输出 motor action，而是对已有 robot skills 排序。

语言模型给：

\[
P(z\mid l,z_{<k}),
\]

value / affordance 给：

\[
V(z\mid s).
\]

最终选择：

\[
z^*=\arg\max_z P(z\mid l)V(z\mid s).
\]

它明确提出了至今仍重要的分工：**语义合理性和物理可行性不是一回事。**

## 23.6 PaLM-E：把 Sensor Token 注入大模型

PaLM-E 将 image、robot state 等连续 encoder embedding 投影到语言模型 token space，与文本一起处理。

结构：

```text
images / state → encoders → continuous embeddings
                         ↓
text tokens ─────────→ large language model
                         ↓
language / plan / task outputs
```

它把“embodied observation 也能成为 LM context”推向大规模多任务模型。

## 23.7 RT-1：规模化多任务 Robot Transformer

RT-1 的问题定义更直接：真实机器人数据是否可以通过大型多任务 Transformer 扩展能力范围？

输入：多帧图像 + task instruction；输出离散化动作。

关键变化不是某个 attention 公式，而是：

- 大量真实机器人 demonstration；
- 多任务统一 policy；
- 高容量视觉–语言条件；
- action tokenization；
- 真机大规模 eval。

这建立了 robot-policy scaling 的实证基础。

## 23.8 Tokenized Action

连续 action \(a_j\) 离散成 bins：

\[
Q(a_j)=t_j.
\]

Transformer 输出 token，解码回连续命令。

优点：可以使用 categorical cross-entropy；缺点：quantization、token 长度和高 DOF 扩展性。

后续 flow/diffusion action expert 很大程度上就是对此的一种重新设计。

## 23.9 RT-2：Web Knowledge 进入 Action

RT-2 的核心主张：将大规模 Vision-Language Model 与机器人 trajectory co-finetune，把 robot action 也表示成可被 VLM 输出的 token。

概念链：

```text
web image–text knowledge
          +
robot demonstrations
          ↓
vision-language-action model
          ↓
robot action tokens
```

这把 VLA 作为明确类别推入主流。

## 23.10 RT-2 的真正科学问题

不是“VLM 能不能接 action head”，而是：

> Web-scale semantic representation 是否能帮助 robot 在未直接示范的 object / instruction / semantic combination 上行动？

这个问题到 2026 仍没有完全解决，因为 semantic transfer 与 physical generalization 不是同一件事。

## 23.11 Semantic Generalization vs Physical Generalization

例：模型知道“香蕉皮应该丢垃圾桶”，属于 semantic transfer。

但面对一个新重量、新摩擦、新把手结构物体仍稳定抓取，属于 physical/general motor transfer。

必须把二者分开评测。

## 23.12 Open X-Embodiment

Open X-Embodiment 汇聚多机构 robot datasets，公开工作报告覆盖 22 类机器人、500+ skills、超过百万 episodes 的规模。

数据形式可以抽象：

\[
D=\bigcup_e D_e,
\]

每个 embodiment \(e\) 有不同 observation/action/state semantics。

真正难点是异质性，而不只是总 episode 数。

## 23.13 RT-X：跨机器人训练

RT-X 将多机器人数据共同训练，并展示 cross-embodiment data sharing 可以提升多个机器人上的 policy performance。

这给出重要证据：

\[
D_{other\ robots}\not\equiv\text{noise}.
\]

不同身体的数据可以提供共享视觉、语义、物体交互先验。

但“共同训练已见机器人”仍不等于 zero-shot unseen body。

## 23.14 Cross-Embodiment Data 的技术债

必须解决：

- action dimension；
- absolute / delta；
- joint / EE control；
- frame；
- camera number/pose；
- state dimension；
- frequency；
- language labels；
- normalization。

如果 dataset adapter 处理得不好，模型会把“robot ID”当成一组彼此隔离的 task，而不是学共享机制。

## 23.15 RoboCat：Self-Improvement 的早期信号

RoboCat 强调 generalist agent 可以少量适配新 task / embodiment，再收集自己的新经验加入后续训练。

概念上，它把 robot foundation model 从静态预训练推进到：

\[
\text{generalist}\rightarrow\text{adapt}\rightarrow\text{collect}\rightarrow\text{retrain}.
\]

这条 data flywheel 后来在 2025–2026 experience learning 中重新变得中心。

## 23.16 Octo：开放 Generalist Policy

Octo 以大规模 Open X-Embodiment 数据预训练，采用 Transformer backbone 与 diffusion action head，支持多 camera、language/image goal 与不同 robot action fine-tuning。

它的意义有两层：

1. 技术上把 generalist policy 与生成式 continuous action 结合；
2. 科学上提供开放 checkpoint/code，使 cross-dataset robot pretraining 可被社区真正复现。

## 23.17 Octo 的结构性选择

典型思路：

```text
observation tokens
+ task tokens
+ readout / action tokens
      ↓
Transformer
      ↓
diffusion action head
```

它没有把所有 action 变成语言 token，而是保留更适合连续轨迹的生成头。

这是随后 VLA 架构分化的预演。

## 23.18 OpenVLA

OpenVLA 将开放 VLM backbone 与 robot action tokenization 结合，公开 7B 级模型、训练与评测链。

其价值之一是让研究者可以真正追踪：

- vision encoder；
- language backbone；
- robot action token；
- fine-tuning strategy；
- data mixture；
- LoRA / full fine-tune；
- inference latency。

VLA 开始从 proprietary system demo 进入可审计研究对象。

## 23.19 2024 年形成的共同 VLA 模板

```text
RGB / multi-view
      ↓
vision encoder / VLM
      +
language instruction
      +
(optional proprioception)
      ↓
multimodal backbone
      ↓
action representation
      ↓
chunk / control command
      ↓
low-level controller
```

分歧集中在最后两层：action token、diffusion、continuous expert，以及 backbone 是否 freeze。

## 23.20 Robot Foundation Model 的定义逐渐变化

早期“foundation”强调多任务、多机器人 pretraining；后来又加入：

- human video；
- web multimodal data；
- simulation；
- world-model auxiliary；
- RL experience；
- memory；
- whole-body humanoid。

因此到 2026，foundation model 不应再被简单等同于“一个大 VLA checkpoint”。

## 23.21 数据 vs 架构

这段历史最大的研究方法教训：很多模型同时改变 data scale、backbone size、pretraining source、action head。

性能提升：

\[
\Delta P=\Delta_{data}+\Delta_{scale}+
\Delta_{pretrain}+\Delta_{action}+\Delta_{system}+\text{interaction terms}.
\]

没有 controlled ablation 时，不应把全部提升归因给模型名字。

## 23.22 一条压缩谱系

```text
Gato
  └─ generalist sequence interface
SayCan
  └─ semantic reasoning × affordance
PaLM-E
  └─ embodied sensor embeddings into LM
RT-1
  └─ scaled multitask robot Transformer
RT-2
  └─ web VLM knowledge → direct action
Open X / RT-X
  └─ cross-robot data scaling
RoboCat
  └─ adaptation / self-generated experience
Octo
  └─ open generalist + continuous diffusion policy
OpenVLA
  └─ open large VLA baseline
```

每一步都解决前一步一个瓶颈，同时留下新问题。

## 常见误读

- “RT-2 首次把语言用于机器人”——错误，语言机器人研究更早；
- “Open X 证明一个 policy zero-shot 控任意机器人”——远未达到；
- “VLA 取代经典机器人控制”——实际大多仍依赖低层 controller；
- “多任务 = 通用”——训练任务覆盖广与强 OOD generalization 不同；
- “模型更大所以物理理解更强”——需要 physical intervention 证据。

## 最小研究练习

选 RT-2、Octo、OpenVLA 三个公开描述，画三张完全相同模板的系统图：input、backbone、action representation、training data、controller、evaluation distribution。禁止保留论文原图布局。然后回答：性能差异中哪些变量根本没有被控制？

## 延伸来源

- RT-2 — https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/
- Open X-Embodiment / RT-X — https://deepmind.google/blog/scaling-up-learning-across-many-different-robot-types
- Octo — https://octo-models.github.io/
- OpenVLA — https://openvla.github.io/
<!-- CHAPTER-ENRICHMENT-P23:START -->
## 23.23 VLA 谱系的 Failure Taxonomy

这一阶段的系统容易被同一个“success rate”掩盖不同失败源：

```text
semantic failure
→ instruction / object grounding 错

representation failure
→ 看见了对象但缺 precision / geometry

action-interface failure
→ tokenization / normalization / frame 不合适

temporal failure
→ inference latency / stale action

controller failure
→ policy target 合理但 IK / low-level controller 执行失败

data failure
→ train mixture / embodiment / scene coverage 不足
```

如果论文只给最终成功率，无法知道 VLM pretraining、robot data scaling 与 action representation 各自解决了哪一种 failure。

## 23.24 最小受控实验：把“VLA 提升”拆开

固定同一个 robot、task split、vision encoder、controller 与训练步数，只改变一个轴：

```text
A. BC regression head
B. action-token head
C. diffusion head
D. flow head
```

再分别加入：

```text
+ web/VLM pretraining
+ cross-robot data
+ language conditioning
```

要求报告：

- seen-task success；
- novel-object / novel-instruction success；
- action quantization / trajectory error；
- inference latency；
- recovery；
- controller saturation / IK failure。

这比直接比较 RT-2、Octo、OpenVLA 的论文数字更接近因果问题，因为后者的数据、参数量、controller 与 benchmark 通常都不同。

## 23.25 Negative Controls

1. **Shuffled language**：保持视觉与动作数据不变，打乱 instruction，测 language 是否真的被读取；
2. **Frozen/random VLM features**：控制 parameter count，测 web semantic prior 的真实贡献；
3. **Matched robot-data budget**：避免“更多机器人数据”被误写成 architecture gain；
4. **Action de-tokenization oracle**：把量化误差单独隔离；
5. **Same controller**：不同 policy 必须经过同一 IK / low-level controller 才能做 architecture credit assignment。

## 23.26 研究问题

1. VLA 的关键跨越究竟是“语言进入 action”，还是“大规模异质数据终于进入统一 policy”？
2. Web-scale semantic prior 对真实 precision manipulation 的边际贡献在什么任务上接近零？
3. Cross-robot training 学到的是 embodiment-agnostic interaction structure，还是 robot-ID-conditioned mixture of experts？
4. Action tokenization 何时是合理 inductive bias，何时只是复用 LLM 工具链的工程便利？
5. 一个模型能在多个已见 robot 上工作，需要什么额外实验才能支持 unseen-morphology generalization？
<!-- CHAPTER-ENRICHMENT-P23:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 23`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-23)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
