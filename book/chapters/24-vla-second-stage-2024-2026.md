# Part 24　VLA 的第二阶段：2024–2026 的架构分化

> 本章时间截面：2026-09-14。这里讨论的是“架构分化”，不是模型排行榜。任何公司或项目的能力描述都要区分：**官方演示、公开评测、论文证据、开放代码、独立复现**。

## 学习目标

读完本章，你应该能回答四个问题：

1. 为什么 2024 之后的 VLA 不再只是“VLM 后面接 action head”？
2. π、GR00T、Gemini Robotics、Helix 等路线真正分歧在哪里？
3. 一个模型声称“通用”“跨本体”“whole-body”时，具体跨越了哪些接口？
4. 怎样把架构创新与数据规模、后训练、控制系统改进分开评估？

---

## 24.1 π0：VLM + Flow-Matching Action Expert

π0 代表了一个重要转折：大模型负责语义和多模态条件，动作端不必再完全依赖离散 token 自回归，而可以使用连续生成模型。

可以抽象成：

\[
h = f_{\text{VLM}}(o_t,l,s_t),
\]

动作专家学习条件速度场：

\[
v_\theta(a_\tau,\tau,h),
\]

再由 ODE 从噪声或简单先验逐渐运输到动作分布。

关键不是“用了 flow matching”这几个字，而是：

- 动作空间保留连续几何；
- 可一次生成 action chunk；
- 语义 backbone 与动作专家承担不同功能；
- 为实时 chunking、RL post-training 和多本体适配留下接口。

现代 VLA 因此开始出现一个更清晰的分工：

```text
semantic / multimodal backbone
        ↓ context
continuous action expert
        ↓
action chunk
        ↓
temporal executor
        ↓
robot controller
```

---

## 24.2 FAST 与高效 Action Tokenization

连续生成并不意味着离散动作路线失效。FAST 一类方法重新研究如何把连续机器人轨迹压成更高效的 token 序列，使大模型可以用序列建模目标训练动作。

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

需要特别区分：

- scalar binning；
- vector quantization；
- trajectory compression；
- learned latent action；
- continuous action expert。

这些方法对“动作是什么”给出了不同答案。

---

## 24.3 π0.5：Open-World Generalization

π0.5 把问题从“训练任务内多任务学习”推进到更开放的环境和任务组合。其研究意义不是某几个 demo，而是尝试让大规模预训练知识、机器人数据与长任务结构发生更紧密的连接。

评价 open-world generalization 时必须至少拆成：

- novel object；
- novel scene；
- novel instruction；
- novel task composition；
- novel embodiment；
- perturbation recovery。

把其中任意一项成功统称为“open world”都过于宽泛。

一个更严格的 generalization vector 可以写成：

\[
G=(G_o,G_s,G_l,G_t,G_c,G_e,G_p),
\]

分别对应 object、scene、language、task、composition、embodiment 和 physics/perturbation。

---

## 24.4 π*0.6：从 Demonstration 走向 Experience / RL

π*0.6 的意义在于明确把 **autonomous experience + reinforcement learning** 放到 generalist VLA 的后训练流程里。

典型流程可以写成：

```text
large-scale pretraining
      ↓
offline / value-aware learning
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

截至本书时间截面，Physical Intelligence 公开报告 π*0.6 在多类真实任务中利用 on-robot experience 提升行为质量。科学上应继续区分：

- 官方结果；
- 同硬件复现；
- 跨实验室复现；
- 经验数据量带来的收益；
- RL objective 本身带来的收益。

---

## 24.5 π0.7：Steerability 与 Emergent Capability

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
\pi(a\mid o,c),
\]

其中 \(c\) 不再只是任务名字，而可以描述**如何做、做到什么程度、遵守什么中间约束**。

官方结果展示了对未直接演示任务的组合式泛化迹象。科学上真正应该验证的是：

1. 新任务能否分解为训练技能的已知组合？
2. 是 language coaching 在起作用，还是视觉/场景相似性？
3. compositional generalization 是否跨对象、场景、本体仍成立？
4. 数据去重后“emergent”是否仍存在？
5. 错误 coaching 是否能按预期破坏 motor behavior？

---

## 24.6 GR00T N1：Humanoid Foundation Model

GR00T N1 把 foundation policy 明确推向 humanoid、双臂与跨本体机器人学习。

其路线可以概括为：

```text
multimodal / language prior
+ heterogeneous robot data
+ embodiment information
        ↓
shared robot foundation model
        ↓
action generation
        ↓
robot-specific post-training / deployment
```

它的重要性不在于“模型能控制 humanoid”这一句宣传语，而在于把以下问题同时放进开放研究栈：

- heterogeneous embodiment；
- multimodal input；
- action generation；
- post-training；
- synthetic / real data mixture；
- deployment tooling。

---

## 24.7 GR00T N1.5：Cross-Embodiment 与 Post-Training

N1.5 进一步把“同一个 foundation model 怎样适配不同机器人”推到主线。

研究上最值得拆的不是 checkpoint 名字，而是三个接口：

### 1. Embodiment representation

模型怎样知道当前控制的是哪一种身体？

### 2. Action/state normalization

不同机器人 joint、末端、gripper 与 action scale 怎样进入共同空间？

### 3. Post-training budget

新机器人需要多少：

- demonstrations；
- gradient steps；
- environment interactions；
- calibration；
- adapter parameters？

跨本体能力必须和 adaptation budget 一起报告。

---

## 24.8 GR00T N1.6：VLM、DiT 与 Loco-Manipulation 扩展

N1.6 在公开研究材料中进一步扩展：

- VLM / visual-language representation；
- DiT / generative action component；
- embodied reasoning-oriented training；
- bimanual / humanoid action；
- loco-manipulation / whole-body 方向。

这里最重要的问题是：

> **VLM 的语义能力、DiT 的动作分布建模、robot-specific post-training 与 whole-body controller 究竟怎样分工？**

如果只看最终 success rate，很难知道收益来自哪一层。

---

## 24.9 GR00T N1.7：新 VLM Backbone、Embodiment Tags 与部署栈

**GR00T N1.7 必须包含在本书 2026-09-14 的快照中。** NVIDIA 的 GitHub Release `n1.7-release` 发布于 **2026-04-18**；当前官方仓库把 N1.7 标记为 GR00T N1 的 latest / General Availability 版本。

官方开放仓库中可直接看到几项结构变化。

### 24.9.1 新 VLM backbone

N1.7 README 明确写出：

```text
Cosmos-Reason2-2B
(Qwen3-VL architecture)
```

替换 N1.6 所用的旧 backbone，并支持更灵活的原生图像比例输入。

这使得一个重要研究问题更容易被控制变量实验回答：

\[
\Delta P = \Delta P_{VLM} + \Delta P_{action} + \Delta P_{data} + \Delta P_{system}.
\]

N1.6 → N1.7 的比较不应只解释为“新版本更强”，而应拆 backbone、数据、action head、训练与部署栈。

### 24.9.2 显式 embodiment tags

开放代码包含：

```text
gr00t/data/embodiment_tags.py
```

并定义 N1.7 checkpoint 支持的 embodiment tags。

这提供了一个非常具体的 cross-embodiment 研究入口：

> embodiment conditioning 是否真的学习了身体差异，还是只充当 dataset ID？

可设计负对照：

- correct embodiment tag；
- wrong tag；
- shuffled tag；
- hidden tag；
- unseen morphology。

### 24.9.3 Action head 与 Horizon

开放实现包含：

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
processing_gr00t_n1d7.py
tests/gr00t/model/test_action_head.py
tests/gr00t/model/test_action_horizon_validation.py
```

这意味着读者可以直接从源码追踪：

```text
observation / language / embodiment
→ processor
→ VLM representation
→ action head
→ action horizon
→ deployment executor
```

而不必只看 architecture figure。

### 24.9.4 真实部署、Async Inference 与 RTC

官方 `getting_started/real_world_deployment.md` 明确讨论 **Asynchronous Inference + RTC**，并说明 RTC 在当前代码中的实验性接口状态。

这再次说明 foundation robotics 的性能不是：

\[
\text{model only}
\]

而是：

\[
\text{model}
+
\text{temporal executor}
+
\text{network/runtime}
+
\text{controller}.
\]

### 24.9.5 开放 checkpoint 与 benchmark 路径

官方仓库公开展示了：

- `nvidia/GR00T-N1.7-3B`；
- DROID；
- LIBERO；
- RoboCasa；
- SimplerEnv；
- real-robot examples；
- PyTorch / TensorRT deployment。

因此 N1.7 对教材的价值不仅是“多一个模型”，而是提供了一条相对完整的：

```text
data
→ config
→ model
→ fine-tune
→ inference
→ benchmark
→ real deployment
```

开放源码链。

---

## 24.10 Gemini Robotics：VLA 与 Embodied Reasoning 分层

Gemini Robotics 路线体现了一个重要趋势：高层 reasoning 与低层 action 不一定应该塞进同一个同步循环。

抽象为：

```text
Embodied Reasoning Model
  - goal decomposition
  - spatial/physical reasoning
  - progress tracking
  - human interaction
          ↓
VLA / Motor Policy
  - perception-to-action
  - dexterous control
          ↓
low-level control / hardware
```

这重新提出经典机器人学里的分层问题：只是 planner 换成了 multimodal reasoning model，policy 换成 learned VLA。

---

## 24.11 Gemini Robotics 1.5：Motion Transfer 与 Embodiment Adaptation

Gemini Robotics 1.5 一类中间版本所代表的问题是：

> foundation model 如何把已有能力迁移到新的 robot morphology 与 action interface？

评价时应显式报告：

- source embodiment；
- target embodiment；
- calibration；
- adaptation data；
- parameter update budget；
- transfer 后精度与稳定性。

“能迁移”如果没有 adaptation budget，就不是完整结论。

---

## 24.12 Gemini Robotics 2：Whole-Body VLA

2026 年公开版本把控制范围推进到：

- whole-body humanoid control；
- dexterous hands / grippers；
- multi-robot collaboration；
- 较长时程任务中的 progress understanding；
- richer embodied reasoning。

注意：“whole-body VLA”并不意味着低层 torque loop 消失。读者应继续追问：

- action interface；
- balance / WBC；
- servo rate；
- contact switching；
- fall handling；
- safety layer。

---

## 24.13 Gemini Robotics On-Device 2：端侧推理与快速适配

On-device 路线把另一个长期问题推到前台：

\[
\text{foundation capability}
\leftrightarrow
\text{latency / memory / power / thermal budget}.
\]

机器人端侧部署需要同时优化：

- model size；
- inference latency；
- memory footprint；
- sensor I/O；
- adaptation time；
- hardware energy budget。

因此 on-device VLA 本质上是 **hardware–model–control co-design**。

---

## 24.14 Helix：On-Board、Multi-Rate 与 Whole-Body

Figure 的 Helix 路线特别适合用来理解 **多时间尺度**。

早期 Helix 采用快慢双系统：

```text
System 2: VLM-level semantics, slow rate
              ↓ latent intent
System 1: visuomotor policy, high rate
              ↓
continuous humanoid control
```

公开技术说明中，早期 Helix 的低层 visuomotor policy 可运行到远高于高层语义模块的频率。训练与部署需要显式处理两者时间偏移。

Helix 02 又把范围扩展到 full-body loco-manipulation，并把 vision、touch、proprioception 接入 whole-body visuomotor loop。

核心教训是：

> 大模型时代没有消灭控制频率问题，反而让 multi-rate architecture 更重要。

---

## 24.15 开源 VLA 生态：OpenVLA / SmolVLA / LeRobot

开放生态的重要性不是简单“模型免费”，而是让研究者可以真正研究：

- action representation；
- fine-tuning recipe；
- dataset mixture；
- hardware abstraction；
- asynchronous inference；
- policy latency；
- cross-robot adaptation；
- reproducible benchmark。

例如 OpenVLA 当前开放仓库可以从：

```text
vla-scripts/train.py
vla-scripts/finetune.py
vla-scripts/deploy.py
prismatic/models/
prismatic/training/
prismatic/vla/
```

追踪完整训练—部署路径。

LeRobot 则把：

```text
datasets
policies
robots
motors
cameras
envs
async_inference
```

放在统一工程框架中，非常适合研究“policy 如何真正连接硬件”。

---

## 24.16 3D-Aware / Point-Cloud-Aware VLA

随着 motor precision 提升，纯 2D semantic representation 的不足更明显。

3D-aware 路线尝试显式加入：

- point cloud；
- depth；
- voxel / occupancy；
- object pose；
- geometry-aware token；
- SE(3)-aware representation。

真正应该验证的是：

> 3D representation 是否减少了 geometry/contact failure，而不只是提高了一个平均 success score？

---

## 24.17 Bimanual / Dexterous / Humanoid VLA

高维本体把 action problem 从“末端 6D + gripper”扩展到：

```text
left arm
+ right arm
+ hands
+ torso
+ base / legs
```

新的难点包括：

- relative bimanual frame；
- self-collision；
- contact coordination；
- high-dimensional action generation；
- tactile feedback；
- balance and locomotion；
- heterogeneous control rates。

whole-body 不是简单把 action dimension 加大。

---

## 24.18 中国具身基础模型与开放生态

到 2026 年，中国也形成了大量 VLA、humanoid foundation policy、robot world model 与开放 benchmark / simulator 工作。

本书不按公司/机构逐项列榜，而要求任何模型统一填写：

1. observation；
2. state / memory；
3. action representation；
4. action generator；
5. data mixture；
6. embodiment conditioning；
7. temporal executor；
8. low-level controller；
9. deployment learning；
10. independent evaluation。

只有这样才能与全球其他路线做机制级比较。

---

## 24.19 2026 VLA 的共同结构与真正分歧

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
2. action generator 是 AR、diffusion、flow、DiT 还是 regression；
3. 是否多时间尺度；
4. embodiment 是否显式条件化；
5. 是否允许部署后学习；
6. world model / memory / reasoning 是否独立存在；
7. safety 是外部 shield 还是进入 policy training；
8. execution/runtime 是否被视为模型的一部分。

---

# 不要被版本号掩盖的科学问题

## 问题 A：Scaling 到底带来什么？

需要把能力变化分解成：

\[
\Delta P
=
\Delta P_{data}
+
\Delta P_{model}
+
\Delta P_{objective}
+
\Delta P_{system}
+
\Delta P_{interaction}.
\]

现实中这些项高度耦合。

## 问题 B：语义泛化会自动变成物理泛化吗？

不会。认识“拉链”与精确捏住拉链头是不同能力。

## 问题 C：Whole-body 只是 action dimension 变大吗？

不只是。它同时引入：

- floating-base dynamics；
- balance；
- contact switching；
- self-collision；
- moving camera；
- changing reachable set；
- multi-rate actuation。

## 问题 D：所谓 emergent capability 如何证伪？

必须做：

- data overlap audit；
- composition-held-out split；
- geometry novelty control；
- wrong-condition negative control；
- multi-seed / multi-scene repetition。

---

# 最小实验

选择同一机器人任务，固定数据和视觉 encoder，仅改变 action generator：

1. MSE regression；
2. autoregressive token；
3. diffusion；
4. flow matching / DiT。

统一：

- action horizon；
- control frequency；
- parameter budget；
- training steps；
- observation history；
- low-level controller。

评估：

- success；
- cycle time；
- action smoothness；
- recovery；
- inference latency；
- action age；
- perturbation robustness。

这个实验比单纯复现四篇论文更能回答“架构分化到底改变了什么”。

---

## Source anchors

- Physical Intelligence, π0.7: https://www.pi.website/blog/pi07
- Physical Intelligence, π*0.6: https://www.pi.website/blog/pistar06
- Physical Intelligence, Real-Time Action Chunking: https://www.pi.website/research/real_time_chunking
- NVIDIA GR00T N1.6 research page: https://research.nvidia.com/labs/gear/gr00t-n1_6/
- NVIDIA Isaac-GR00T N1.7 release: https://github.com/NVIDIA/Isaac-GR00T/releases/tag/n1.7-release
- NVIDIA Isaac-GR00T source: https://github.com/NVIDIA/Isaac-GR00T
- Google DeepMind, Gemini Robotics 2: https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Figure, Helix: https://www.figure.ai/news/helix
- Figure, Helix 02: https://www.figure.ai/news/helix-02
- OpenVLA: https://github.com/openvla/openvla
- LeRobot: https://github.com/huggingface/lerobot

---

## 本章结论

2024–2026 的 VLA 发展不是“Transformer 越来越大”，而是 robot foundation model 开始正面碰撞经典机器人学长期存在的问题：**连续控制、时延、多频率、接触、跨本体、whole-body、安全、经验学习和部署系统**。

GR00T N1.7 进一步说明：一个现代 foundation robot system 已经不能只用“backbone + action head”描述。processor、embodiment tag、action horizon、async inference、RTC、deployment runtime 与 low-level control 都属于科学对象的一部分。
