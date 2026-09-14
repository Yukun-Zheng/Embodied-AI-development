# Volume V　Robot Foundation Models：从 VLM 到 VLA

> 本卷覆盖截至 2026-09-14 的机器人基础模型主线。目标不是追逐型号，而是理解每一代模型解决了什么系统瓶颈：语义 grounding、跨任务数据、动作表示、跨 embodiment、实时性、记忆、经验学习与 whole-body control。

---

# Part 22　语言、多模态基础模型与 Physical Grounding

## 22.1 Language 为什么进入机器人

语言可以承担四种不同角色：

1. **任务接口**：用户说“把杯子放进水槽”；
2. **抽象状态**：记录“杯子已经洗过”；
3. **规划空间**：把长任务分成 subtask；
4. **知识载体**：把 web-scale 常识迁移到物理任务。

但语言本身不是控制信号。最终还必须落到几何、接触、时序与 motor action。

## 22.2 Tokenization

文本被切成 token：

\[
(x_1,\ldots,x_T),\qquad x_t\in\{1,\ldots,V\}.
\]

VLA 若也把 action 离散为 token，就可以复用 next-token prediction：

\[
p(x_{t+1}\mid x_{\le t}).
\]

但连续机器人动作的精度、频率和维数使 tokenization 变成真正的系统设计问题，而非简单格式转换。

## 22.3 Vision-Language Pretraining

VLM 通常从大规模 image-text/video-text 数据学习视觉语义。CLIP 类对比目标使匹配图文 embedding 接近；LLaVA/BLIP 类模型把视觉 token 对齐到语言模型输入空间。

这提供了 open-vocabulary recognition、semantic relation 和常识 prior，但不能自动提供接触力、可达性、控制稳定性或 precise geometry。

## 22.4 Grounding

Physical grounding 要求语言词汇与可行动世界对齐：

```text
“红杯子” → which pixels / object?
“拿起”   → which grasp / trajectory / force?
“轻轻”   → what velocity / force profile?
“放进去” → what geometric/contact termination condition?
```

因此 grounding 至少跨越 semantic、spatial、temporal 和 motor 四层。

## 22.5 Open-Vocabulary Perception

VLM 让机器人可以识别训练 task dataset 没标过的物体类别，但 open-vocabulary detection 只回答“是什么/在哪里”。对 manipulation，还需要 pose、affordance、geometry、material、occlusion 与 uncertainty。

## 22.6 Spatial / Temporal / Physical Reasoning

三者应区分：

- spatial：左/右、inside、relative pose；
- temporal：先后、持续时间、task progress；
- physical：稳定性、可支撑性、接触、因果结果。

一个 VLM 在 VQA 上回答物理常识正确，并不意味着其 latent 足以驱动稳定 motor control。

## 22.7 Language-Conditioned Planning

高层可写

\[
g\xrightarrow{\text{planner}}(z_1,z_2,\ldots,z_K)
\]

其中 \(z_k\) 是语言 subtask。低层策略再执行

\[
a_t\sim\pi(a\mid o_t,z_k).
\]

这类分层能把分钟级任务与几十 Hz motor control 解耦。

---

# Part 23　VLA 的形成：2022–2024

## 23.1 什么才算 VLA

最宽泛定义：输入包含视觉与语言，模型输出可直接或经轻量后处理执行的 robot action。

\[
\pi_\theta(a_{t:t+H}\mid I_{\le t},l,q_{\le t}).
\]

如果模型只输出文字 plan，再由独立传统 planner/controller 完成动作，更适合称 embodied reasoning / VLM planner，而非严格意义 direct VLA。

## 23.2 Gato

Gato 把多任务、多模态交互统一成 token sequence，展示“一个 Transformer 可同时做很多任务”的 generalist idea。它对后续 robot foundation model 的影响更多是**统一序列接口**与 scaling 叙事，而非高性能真机控制。

## 23.3 SayCan

SayCan 的核心是把语言模型的高层 plausibility 与 skill affordance/value 结合：

\[
P(skill\mid instruction)\times V(skill\mid state).
\]

这明确暴露一个重要原则：语言模型认为“应该做”与机器人“做得到”是两回事。

## 23.4 PaLM-E

PaLM-E 把连续 sensor embedding 注入大型语言模型，使语言模型能够处理 embodied multimodal input，并执行规划、VQA、机器人任务。它是“把 embodied observation 当作 language model context”的关键节点。

## 23.5 RT-1

RT-1 以大量真实机器人 demonstration 训练多任务 Transformer policy，突出 data scale、任务多样性和 tokenized action。历史意义：证明 robot transformer 可以从大量 real robot data 获得更广泛 manipulation competence。

## 23.6 RT-2

RT-2 将 VLM 与 robot action 数据 co-finetune，并把离散动作写成文本式 token 输出。Google DeepMind 把它称为 Vision-Language-Action model，其关键主张是 web-scale 视觉语言知识能迁移到 robot control。

它建立了随后最主流的 recipe：

```text
pretrained VLM
   + robot demonstrations
   + action representation compatible with model
             ↓
            VLA
```

## 23.7 Open X-Embodiment / RT-X

Open X-Embodiment 汇聚 22 种机器人、500+ skills、超过百万 episodes。RT-X 显示跨 embodiment 数据混合可以提高多个机器人的表现。

真正研究问题是数据异质性：

\[
D=\bigcup_e \{o^{(e)},a^{(e)},l^{(e)},f^{(e)}\}.
\]

不同 \(e\) 的 action dimension、camera、frequency、normalization 与 control semantics 都可能不同。

## 23.8 RoboCat

RoboCat 强调 generalist agent 通过新任务数据再训练、生成自己的经验并扩展能力。它提前提出 foundation robot 的另一核心：**self-improvement loop**，而不是静态预训练一次。

## 23.9 Octo

Octo 是开放 generalist manipulation policy：Transformer backbone + diffusion action head，在 Open X-Embodiment 的大规模混合数据上预训练，支持 language/goal image、多 camera 与不同 action space fine-tuning。

它的重要价值是把 generalist policy 从 proprietary demo 变成社区可复现基线。

## 23.10 OpenVLA

OpenVLA 以 Prismatic VLM 为基础，融合 SigLIP/DINOv2 visual encoder 与 Llama-family backbone，把 action 离散成 token。其 7B 开源 checkpoint 与完整训练链让 VLA 研究进入可审计阶段。

## 23.11 2024 VLA 的共同模板

```text
RGB + language + robot state
          ↓
vision encoder / VLM backbone
          ↓
multimodal tokens
          ↓
action head or action tokens
          ↓
action chunk
          ↓
robot low-level controller
```

真正差异集中在：action representation、是否冻结 VLM、如何混数据、是否有 memory、是否跨 embodiment、推理频率和 post-training。

---

# Part 24　VLA 第二阶段：2024–2026 的架构分化

## 24.1 π0：VLM + Flow Action Expert

π0 把 pretrained VLM 与独立 flow-matching action expert 结合。高维连续动作不再强制经过 language tokenizer，而通过连续生成头产生 action chunk。

这成为 2025–2026 很重要的范式：

\[
\text{semantic/VLM context}\rightarrow\text{continuous motor expert}.
\]

## 24.2 FAST

FAST 的目标是高效压缩连续动作序列，使 autoregressive action modeling 不必为每个维度每个 timestep 产生大量 token。它提醒我们：action tokenizer 本身可以是 robot foundation model 的瓶颈。

## 24.3 π0.5：Open-World Generalization

π0.5 进一步联合 robot data、web multimodal data、high-level subtask/instruction supervision，使同一个 VLA 同时产生语义层推断和低层动作，目标是部署到训练未见的新家庭环境。

这里出现一个核心转变：VLA 不只追求“新物体”，而是**new scene + long task + semantic decomposition**。

## 24.4 RTC：大模型进入实时控制

Real-Time Action Chunking 直接处理推理延迟：模型生成新 chunk 时机器人仍在执行旧动作。RTC 让模型/系统考虑这段执行历史，从而减少 chunk stitch 时的 discontinuity。

实时性从 deployment optimization 变成 model design。

## 24.5 π*0.6：Learning from Experience

π*0.6 通过 Recap 把 offline RL、demonstration fine-tuning、on-robot corrections 和 autonomous reward feedback 组合。官方报告在复杂 espresso/laundry/box assembly 等任务上显著提高 throughput 与 failure rate。

概念意义：foundation policy 的训练集开始包含**自己过去的行为后果**。

## 24.6 Multi-Scale Embodied Memory

2026 MEM 显式加入：

- short-term visual/video memory；
- long-term language-semantic memory；
- policy 主动决定记什么。

这样可以执行十分钟级任务，并利用历史失败做 in-context adaptation。

memory 不再只是把更多 frame 堆进 context，而是一个资源分配问题：

\[
\text{what to remember? at what abstraction? for how long?}
\]

## 24.7 Efficient Online RL / RL Token

2026 Physical Intelligence 继续研究从 VLA 中抽取/利用紧凑 RL 表示，使 precise manipulation 可以用少量真实交互快速 RL fine-tune。趋势是让 broad foundation competence 与 local specialization 共存。

## 24.8 π0.7：Steerable Generalist Foundation Model

π0.7 在 2026 年将 richer context conditioning 推向核心：语言 coaching、任务 metadata、visual subgoal 等 context 不只说明“做什么”，还能 steer“怎样做”。官方工作报告了 unseen multi-stage scenario、zero-shot cross-embodiment 与组合泛化迹象。

研究上更值得关注的问题是：

\[
\text{generalization gain} = ?
\]

究竟来自 data diversity、context interface、model scale、representation alignment 还是架构本身？必须用受控实验拆开。

## 24.9 Human-to-Robot Transfer

Physical Intelligence 2025 的实验显示，随着 robot pretraining diversity 增加，简单加入 egocentric human data 的 transfer 效果显著增强，并出现 human/robot latent alignment。

这提示一个重要 scaling hypothesis：足够多样的 robot data 可能先学出更 embodiment-agnostic 的 representation，从而使廉价 human video 真正可用。

## 24.10 GR00T N1

NVIDIA GR00T N1 面向 humanoid：混合 egocentric human video、real/sim robot trajectory、synthetic data，采用 vision-language 与 action generation 双系统。

与 tabletop VLA 相比，humanoid 数据迫使模型处理更大 action space、whole-body state、locomotion 与双臂协同。

## 24.11 GR00T N1.5

N1.5 加入 FLARE future-latent alignment，把 policy learning 与未来 representation prediction 联合，并展示更强 low-data post-training 与 human-video utilization。

这说明 world modeling objective 开始进入 foundation policy pretraining，而不再是独立研究岛。

## 24.12 GR00T N1.6

N1.6 使用内部 Cosmos VLM 变体、更大的 DiT、部分 VLM unfreezing，并增加 YAM、Agibot Genie-1、Unitree G1 whole-body locomanipulation 等大量数据。其默认 action 进一步偏向 state-relative chunk。

它代表 2026 humanoid foundation policy 的工程方向：**跨 embodiment pretraining + task post-training + locomanipulation。**

## 24.13 Gemini Robotics 1 / 1.5

Gemini Robotics 把 Gemini multimodal capability 延伸到 robot action；1.5 更明确分成：

- **Gemini Robotics-ER 1.5**：高层 embodied reasoning、tool use、planning；
- **Gemini Robotics 1.5**：VLA motor execution。

1.5 还展示跨 embodiment motion transfer 与“think before acting”的 agentic control。

## 24.14 Gemini Robotics 2

2026 Gemini Robotics 2 把能力扩展到：

- full humanoid whole-body control；
- multifinger / gripper dexterity；
- minutes-long embodied reasoning；
- multi-robot collaboration；
- On-Device 2 的本地运行与数小时数据适配新 embodiment。

这表明 frontier 已从 tabletop generalist manipulation 迈向 whole-body multi-agent physical system。

## 24.15 Helix

Figure Helix 以单一 VLA 控制 humanoid upper body，包括 wrist、torso、head、finger，并展示双机器人协作。随后 Project Go-Big 强调 internet-scale human video pretraining 与 human-to-robot transfer。

Helix 代表“硬件—数据—模型共同设计”的 industrial humanoid 路线。

## 24.16 SmolVLA 与轻量开放 VLA

SmolVLA 450M 使用小型 VLM + flow-matching expert、少量 visual tokens 和 asynchronous inference，说明基础模型路线并不必然要求数十 B 参数。对于实验室研究，轻量模型的价值在于：

- 可完整重训；
- 可做 architecture ablation；
- 可测 latency；
- 可在低成本机器人上收 data flywheel。

## 24.17 开源生态的意义

OpenVLA、OpenPI、LeRobot/SmolVLA、GR00T open weights 等使研究问题从“看 demo 猜结构”转向可真正问：

- loss 到底是什么？
- 哪些层 freeze？
- normalization 怎样做？
- action chunk 如何执行？
- dataset mixture 对结果影响多大？

这是机器人基础模型成为科学而非展示的重要条件。

---

# Part 25　VLA 内部机制：到底学到了什么

## 25.1 Vision Encoder

输入通常是多 camera、多 frame：

\[
I\in\mathbb R^{B\times T\times V\times H\times W\times3}.
\]

visual encoder 产生 patch/features：

\[
Z_v\in\mathbb R^{B\times N_v\times d}.
\]

最关键问题不只是 semantic quality，而是 geometry、motion、contact precursor 是否保留。

## 25.2 Language Backbone

language model 提供 semantic prior、instruction parsing、world knowledge。但它也可能带来两个问题：

1. web prior 与 physical reality 冲突；
2. 过强语言 feature 让 action head shortcut，通过 task label 猜动作而忽略视觉变化。

## 25.3 Proprioception

\[
s_t^{robot}=[q_t,\dot q_t,g_t,\ldots].
\]

state 常经 MLP/projector 变成 token。若 normalization 不同 embodiment 不一致，cross-robot learning 会受到严重影响。

## 25.4 Action Head

三大类型：

- discrete autoregressive token；
- diffusion trajectory decoder；
- flow-matching action expert。

架构选择直接决定 precision、latency、multimodality 与可扩展 horizon。

## 25.5 Multimodal Fusion

常见：early concatenation、cross-attention、joint transformer、VLM context → expert cross-attention。

一个重要诊断是做 attention / gradient / intervention：如果遮掉 language 或某 camera，动作变化多大？如果视觉 token 变化而 action 几乎不变，模型可能没有真正使用视觉。

## 25.6 Co-Training 与 Knowledge Insulation

robot data 相对 web data 很小。如果直接全模型 fine-tune，可能破坏 VLM 原有语义知识；若完全 freeze，又可能无法形成物理任务所需表示。

因此存在 trade-off：

\[
\text{adaptation to physical world}
\quad\leftrightarrow\quad
\text{retention of pretrained knowledge}.
\]

部分 unfreeze、adapter、separate expert、multi-task web loss 都是在处理这一问题。

## 25.7 Dataset Mixture

训练 objective 实际是

\[
L=\sum_k \lambda_k\mathbb E_{D_k}L_k.
\]

\(\lambda_k\) 决定每类 embodiment/task/web data 的贡献。大模型论文常强调 architecture，但 mixture weight、sampling temperature、task relabeling 可能同样决定结果。

## 25.8 Embodiment Conditioning

方法包括：

- robot ID token；
- morphology vector；
- joint/action mask；
- state/action normalization；
- kinematic graph encoder；
- embodiment-specific head；
- universal end-effector space。

真正跨 embodiment 的目标不是让一个 checkpoint“支持多个 robot ID”，而是在新身体上少量甚至零数据就能重组已有知识。

## 25.9 Post-Training

foundation pretraining 后常需 task/robot post-training。来源可为 demonstrations、RL、preference/correction、synthetic rollout。

因此“foundation model 成绩”要区分：

- zero-shot；
- few-shot adaptation；
- full fine-tune；
- task-specific RL；
- embodiment-specific calibration。

把这些混在一起比较会严重误导。

## 25.10 Action Semantics

同样 7D action 可能是：

\[
[\Delta x,\Delta y,\Delta z,\Delta r_x,\Delta r_y,\Delta r_z,g]
\]

也可能是 joint target。还需说明：

- world/body frame；
- delta / absolute；
- position / velocity；
- scale/clipping；
- execution frequency；
- low-level controller。

否则“同一 VLA”在两个平台上实际面对不同问题。

---

# Part 26　VLA 的能力边界与科学评测

## 26.1 Scale 不等于机制

若模型 B 比 A 多 10 倍 data、3 倍参数、更新了 backbone、改 action head，又提升 10% success，不能直接得出“新 architecture 更好”。

需要控制变量：

\[
\Delta P=\Delta_{data}+\Delta_{compute}+\Delta_{pretrain}+\Delta_{architecture}+\Delta_{system}.
\]

研究的任务是估计每一项。

## 26.2 Memorization vs Generalization

至少设计：

- new object；
- new layout；
- new scene；
- new instruction composition；
- new task composition；
- new embodiment；
- new dynamics；
- adversarial distractor。

只换颜色不能证明 open-world generalization。

## 26.3 视觉是否被真正使用

可做 counterfactual visual intervention：

- 固定 language，替换物体位置；
- 保持 geometry，替换 texture；
- 把 irrelevant object 改色；
- 遮挡关键 contact region；
- 改 camera pose。

观察 action sensitivity：

\[
S=\left\|\frac{\partial a}{\partial z_v}\right\|
\]

或更可靠的 black-box intervention effect。

## 26.4 Physical Reasoning 是否真实存在

不要只看“模型说对了”。应测试 action consequence：

- 预测哪个物体会倒；
- 选择正确支撑点；
- 估计抓取后是否碰撞；
- 根据重量/摩擦调整策略；
- 在未演示组合下执行。

语言解释可以是 post-hoc；物理能力必须体现在行为。

## 26.5 Long-Horizon

长任务成功率近似受每个阶段 reliability 乘积制约。若 20 个子任务每个成功率 0.95：

\[
0.95^{20}\approx0.358.
\]

因此长时任务真正需要 memory、recovery、progress estimation 和 replan，而不仅是更长 context。

## 26.6 Real-Time

必须报告：

- model latency；
- action frequency；
- chunk horizon；
- observation delay；
- hardware；
- network；
- async/sync；
- throughput。

机器人“同样 success 但慢 5 倍”可能在真实场景价值完全不同。

## 26.7 Reliability

一次漂亮 demo 不代表 system reliability。建议至少统计：

\[
\text{success},\quad
\text{time-to-completion},\quad
\text{intervention rate},\quad
\text{failure type},\quad
\text{recovery rate}.
\]

并把 failure 分成 perception、planning、action generation、control、hardware、safety。

---

# 2026 VLA 谱系压缩图

```text
Gato / SayCan / PaLM-E
          ↓
RT-1 ─→ RT-2 ─→ Open X / RT-X
          ↓
   Octo / OpenVLA
          ↓
 ┌────────┼───────────────┐
 │        │               │
π-series  GR00T         Gemini Robotics
 │        │               │
flow      humanoid        ER + VLA
RTC       human/sim       whole-body
memory    FLARE           multi-robot
RL        locomanip       on-device
π0.7      N1.6            Robotics 2
 │
 └─ human-video transfer / steerability

parallel open/efficient line:
LeRobot → SmolVLA → reproducible low-cost VLA

industrial humanoid line:
Figure Helix → human-video scaling → generalist humanoid control
```

## 本卷结论

VLA 不是具身智能的终点，而是一个**统一条件策略接口**。真正未解决的是：

\[
\boxed{\text{How does a robot acquire reusable physical structure from experience?}}
\]

如果模型只能在更大的数据集上拟合更广的行为分布，它仍可能缺少可组合机制、长期记忆、因果预测和持续学习。下一卷专门研究这些问题。

## 核心来源

- RT-2 — https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/
- Open X-Embodiment — https://deepmind.google/blog/scaling-up-learning-across-many-different-robot-types
- Octo — https://octo-models.github.io/
- OpenVLA — https://openvla.github.io/
- Physical Intelligence — https://www.pi.website/
- π0.5 — https://www.pi.website/blog/pi05
- RTC — https://www.pi.website/research/real_time_chunking
- π*0.6 — https://www.pi.website/blog/pistar06
- MEM — https://www.pi.website/research/memory
- π0.7 — arXiv:2604.15483
- Human-to-Robot Transfer — https://www.pi.website/research/human_to_robot
- GR00T N1.5 — https://research.nvidia.com/labs/gear/gr00t-n1_5/
- GR00T N1.6 — https://research.nvidia.com/labs/gear/gr00t-n1_6/
- Gemini Robotics 1.5 — https://deepmind.google/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/
- Gemini Robotics 2 — https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Helix — https://www.figure.ai/news/helix
- SmolVLA — https://huggingface.co/blog/smolvla
