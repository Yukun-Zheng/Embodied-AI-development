# Robotics Foundation Model / Policy / World Model Atlas

> **Snapshot: 2026-09-14**
>
> 这张 Atlas 不做“谁最强”排行榜，而是强制把代表系统放在同一组**机制轴**上比较。很多工作并不属于同一种类别：VLM、VLA、policy、world model、executor、memory module 不应混成一张 leaderboard。

---

# 1. 先区分类别

```text
VLM / Reasoning Model
        ↓ may provide semantics / planning
VLA / Foundation Policy
        ↓ generates robot actions / targets
Temporal Executor
        ↓ decides when/how to execute chunks
Controller / WBC
        ↓ converts targets to stable physical commands
Robot / World
```

另一条线：

```text
World / Video Model
        ↓ predicts future / representation
Planner / Evaluator / Policy
        ↓ uses prediction to choose action
```

以及：

```text
Memory System
        ↓ preserves state across long horizons
Reasoner / Policy
```

所以 `V-JEPA 2.1`、`RTC`、`π0.7`、`Gemini Robotics 2` 解决的不是同一个问题。

---

# 2. 2022–2024：VLA / Generalist Robot Policy 形成期

| 系统 | 年份 | 主要角色 | Observation / Context | Action / Output | 核心机制变化 | 应避免的过度解读 |
|---|---:|---|---|---|---|---|
| **Gato** | 2022 | Generalist sequence agent | vision / text / task-specific tokens | tokenized actions across domains | 多任务统一为序列建模 | 支持很多任务 ≠ 机器人具身基础模型已经解决 |
| **SayCan** | 2022 | Language planner + skill selection | language + skill affordance/value | skill choice | LLM knowledge 与 robot feasibility 组合 | 不是端到端低层 VLA |
| **RT-1** | 2022 | Multi-task robot policy | image + language | discretized robot action | 大规模真实多任务 robot Transformer | task 数量扩大 ≠ open-world generalization |
| **PaLM-E** | 2023 | Embodied multimodal language model | vision / language / sensor embeddings | language / high-level embodied output | 把连续 sensor 信息注入大语言模型 | 强 VLM reasoning ≠ 精密 motor policy |
| **RT-2** | 2023 | VLA | image + language | actions represented in token vocabulary | web VLM knowledge 迁移到 robot action | web knowledge ≠ physical dynamics understanding |
| **RoboCat** | 2023 | Generalist self-improving robot policy | visual / task context | robot action | 新任务数据 → 再训练 → 更广 generalist policy | self-improvement 仍需区分 autonomous vs curated loop |
| **ACT / ALOHA** | 2023 | Imitation policy | image + proprioception | continuous action chunk | action chunking + CVAE + low-cost bimanual data | 不是 VLA，但对后续真实机器人 policy 影响极大 |
| **Diffusion Policy** | 2023 | Generative visuomotor policy | observation history | continuous action sequence | diffusion 建模 multimodal action distribution | 生成式 action 强 ≠ language/foundation model |
| **Open X-Embodiment / RT-X** | 2023–24 | Dataset + cross-robot scaling | heterogeneous robot datasets | heterogeneous normalized actions | 多机构数据混合，cross-embodiment scaling | 数据异构对齐仍是核心难题 |
| **Octo** | 2024 | Open generalist robot policy | multimodal robot observations + task conditioning | continuous robot actions | 开放、可 fine-tune 的跨数据/机器人 generalist policy | 跨已见数据源 ≠ unseen morphology zero-shot |
| **OpenVLA** | 2024 | Open VLA | image + language | discretized action tokens | 开放 VLM→action baseline | 参数规模/语言能力不能替代控制频率和 action interface 分析 |
| **π0** | 2024 | Foundation VLA / policy | vision + language + state | continuous action via flow-matching expert | VLM backbone + continuous action expert | continuous action head ≠ 自动解决 latency / whole-body |

---

# 3. 2025：VLA 开始明显分化

| 系统 / 技术 | 组织 | 主要角色 | 机制轴 | 研究意义 |
|---|---|---|---|---|
| **Gemini Robotics** | Google DeepMind | VLA + embodied intelligence system | multimodal foundation model → robot action | 把 Gemini foundation capabilities 更直接接入 robotics |
| **Gemini Robotics-ER** | Google DeepMind | Embodied reasoning | spatial/physical reasoning + planning | 强调 high-level embodied reasoning 与低层 action 的分工 |
| **π0.5** | Physical Intelligence | Open-world foundation policy | 更开放环境/任务 generalization | VLA 从固定实验室 task 走向更开放世界 |
| **π*0.6** | Physical Intelligence | Experience/RL-enhanced policy | foundation policy + RL / experience | “只模仿 demonstration”开始转向“部署后继续改善” |
| **FAST** | Physical Intelligence | Action representation | efficient action tokenization | 重新审视高维连续 robot trajectory 怎样被序列模型表示 |
| **Real-Time Action Chunking** | Physical Intelligence | Temporal executor | asynchronous / real-time chunk replacement | 明确把 inference latency 与 stale action 当一等问题 |
| **Helix** | Figure | Humanoid VLA | slow semantic layer + fast visuomotor layer | multi-rate architecture 明确进入 humanoid foundation policy |
| **GR00T N1** | NVIDIA | Humanoid foundation model | multimodal reasoning + action generation | humanoid robot foundation model 路线公开化 |
| **GR00T N1.5** | NVIDIA | Cross-embodiment / post-training | transfer + adaptation | 把多 embodiment 与 post-training 放在主线 |
| **GR00T N1.6** | NVIDIA | Humanoid foundation policy | stronger VLM + DiT / loco-manipulation expansion | 继续向 whole-body、复杂 humanoid action 扩张 |
| **SmolVLA / LeRobot ecosystem** | Hugging Face | Small/open VLA ecosystem | smaller model + open dataset/tooling | foundation robotics 开始进入低资源/可复现实验层 |
| **V-JEPA 2** | Meta | Predictive representation / world model | video representation + action-conditioned prediction | world-model / predictive-intelligence 路线重新成为主轴 |
| **Cosmos family** | NVIDIA | World foundation models | video/world generation + physical-AI data | synthetic physical world 与 robot-learning data infrastructure 合流 |

---

# 4. 2026：Memory、Whole-Body、Experience、World Action 合流

| 系统 / 技术 | 时间 | 类别 | 核心问题 | 本书中的位置 |
|---|---:|---|---|---|
| **Helix 02** | 2026-01 | Whole-body humanoid policy | locomotion + manipulation + full-body coordination | Part 35 |
| **Multi-Scale Embodied Memory** | 2026-03 | Memory system | long + short-term embodied context | Part 28 |
| **Efficient Online RL / RL-token style adaptation** | 2026-03 | Experience learning | 用较低在线更新成本优化 precise manipulation | Part 29 |
| **V-JEPA 2.1** | 2026-03 | Predictive representation | dense, temporally consistent video representation | Part 30 |
| **π0.7** | 2026-04 | Foundation policy | steerability、复杂技能组合与 emergent capability | Part 24/27 |
| **Cosmos 3** | 2026-05 | World / World-Action foundation model | reasoning + world generation + action prediction | Part 31 |
| **Gemini Robotics 2** | 2026-07 | Whole-body VLA | whole-body control、dexterity、multi-robot、embodied reasoning | Part 24/35/36 |
| **Gemini Robotics On-Device 2** | 2026-07 | Edge VLA | on-device inference + faster new-embodiment adaptation | Part 24/37/43 |
| **SONIC publication / scaling line** | 2026 | Humanoid motor foundation | scalable whole-body motion tracking | Part 35 |

---

# 5. 用 10 个轴比较任何 VLA

以后出现任何新模型，不需要新建 Part。先填这张表：

| 轴 | 必填问题 |
|---|---|
| **Perception** | RGB? Multi-view? Depth? Point cloud? Tactile? |
| **Language** | 是否使用 VLM/LLM？语言参与训练还是只做 task conditioning？ |
| **State** | proprioception 怎样编码？有没有 history / belief？ |
| **Memory** | context-only、external memory、episodic、multi-scale？ |
| **Action** | joint / Cartesian / torque？absolute / delta？frame？ |
| **Generator** | regression / AR / diffusion / flow / hybrid？ |
| **Temporal** | policy rate、action horizon、chunk execution、async？ |
| **Embodiment** | robot ID、adapter、morphology descriptor、unseen-body test？ |
| **Controller** | low-level PID / impedance / WBC / learned motor policy？ |
| **Learning after deployment** | frozen、fine-tune、RL、online adaptation、continual？ |

没有这些信息，不应只用“参数量 + benchmark success”比较模型。

---

# 6. VLA 架构模式 Atlas

## Pattern A：Tokenized Action VLA

```text
image + language
→ VLM / Transformer
→ action tokens
→ de-tokenize
→ controller
```

代表历史节点：RT-2、OpenVLA 等。

优点：

- 统一序列接口；
- 可复用 language-model machinery。

问题：

- quantization；
- token length；
- continuous precision。

---

## Pattern B：VLM + Continuous Action Expert

```text
vision/language backbone
        ↓ context
continuous action expert
(flow / diffusion / DiT)
        ↓
action chunk
```

代表路线：π 系列、部分现代 humanoid/foundation policies。

优点：连续动作自然；缺点：backbone 与 action expert 如何 joint-train、实时执行仍是系统问题。

---

## Pattern C：Slow Semantic + Fast Motor

```text
slow semantic / reasoning model
              ↓ latent / goal
fast visuomotor / motor policy
              ↓
controller
```

代表路线：Helix 等 multi-rate whole-body system。

它显式承认：语言/语义推理与高频物理控制不应拥有相同更新频率。

---

## Pattern D：Planner / Reasoner + Skill Library

```text
VLM / LLM reasoner
→ skill / subgoal
→ pretrained controller / policy
```

代表历史节点：SayCan、部分 agentic robotics systems。

优点：可解释、组合；缺点：skill boundary 与 error recovery。

---

## Pattern E：World Model + Policy / Search

```text
observation
→ world model
→ imagined futures
→ evaluator / search
→ action
```

这不一定叫 VLA，但可能更接近真正 predictive physical intelligence。

---

# 7. 数据 Scaling Atlas

机器人 foundation models 的“规模”至少有六种：

$$
Scale=(N_{episodes},N_{hours},N_{tasks},N_{robots},N_{scenes},N_{modalities})
$$

还要加：

- human video；
- synthetic data；
- failure data；
- online experience。

所以“我们用了更多数据”不够。必须说明**哪一个 coverage dimension 增加了**。

---

# 8. Generality Atlas

把“通用”拆开：

```text
G_object
G_scene
G_instruction
G_task
G_composition
G_physics
G_robot
G_morphology
G_time
```

一个模型可能 `G_object` 很强、`G_morphology` 很弱。

因此本书拒绝使用没有维度说明的单一 `generalization` 词。

---

# 9. 不能直接横向比较的常见情况

以下数字不能直接放同一 leaderboard：

- simulator success vs real robot success；
- tabletop arm vs humanoid whole-body；
- fixed camera vs moving-head perception；
- different low-level controllers；
- different action frequency；
- different task reset / intervention rules；
- pretrained data unknown vs fully controlled data；
- cherry-picked demo vs all-trial benchmark。

Atlas 的作用正是提醒：**模型名字相似，不代表实验对象相同。**

---

# 10. 未来模型进入 Atlas 的规则

新系统发布时，只做三步：

1. 先确定它属于 `VLM / Policy / VLA / Memory / World Model / Executor / Controller` 哪一类；
2. 填 10 个机制轴；
3. 找它真正改变了哪一个长期问题。

只有当模型引入新的基本数学对象或 physical-system interface 时，才考虑修改主教材一级目录。