# Embodied Intelligence Timeline — 1948–2026

> **Frontier snapshot: 2026-09-14.**
>
> 这条时间线不是“论文年表”，而是回答：具身智能的**基本问题、计算工具与系统接口**如何一步步形成。模型名称只是历史节点；反馈、状态、控制、部分可观测性、交互学习、世界预测与身体约束才是长期主线。

---

# 1948–1960s　反馈、信息与机器智能的基础

| 时间 | 节点 | 长期意义 |
|---|---|---|
| 1948 | Wiener《Cybernetics》 | feedback / communication / control 成为统一视角 |
| 1948 | Shannon 信息论 | entropy、information、communication channel |
| 1950 | Turing 机器智能讨论 | 可计算智能成为系统性研究对象 |
| 1950s–60s | 早期 control / state-space 理论 | 动态系统、估计、最优控制逐步成熟 |
| 1960s | Kalman filter | belief / state estimation 的经典支柱 |

这一阶段已经提出今天具身智能仍然绕不开的核心闭环：

```text
sense → estimate → decide → act → world changes → sense again
```

---

# 1960s–1980s　机器人学成为独立工程与数学体系

| 节点 | 关键变化 |
|---|---|
| industrial manipulators | 机器人第一次大规模进入稳定结构化物理环境 |
| rigid-body kinematics / dynamics | FK、IK、Jacobian、Newton–Euler、Lagrangian 成为标准语言 |
| configuration-space planning | collision-free motion 被形式化 |
| force / impedance control | 从“到达位置”走向“与世界接触” |
| optimal control / dynamic programming | 动态决策和控制建立统一数学基础 |

这个时期的重要结论：

> 身体、几何、动力学和控制器不是 AI 的“外设”，而是智能能否执行的物理条件。

---

# 1980s–1990s　Situated / Behavior-Based Robotics 与移动机器人

| 节点 | 关键变化 |
|---|---|
| Brooks / Subsumption | 对纯 Sense–Plan–Act 管线提出挑战，强调 situated behavior |
| behavior-based robotics | reactive control 与环境交互成为智能的一部分 |
| probabilistic robotics | localization / mapping / uncertainty 开始系统化 |
| SLAM | perception、geometry、state estimation 合流 |

现代“end-to-end policy”并不是第一次有人质疑模块化规划；历史可以帮助我们区分旧问题与新工具。

---

# 2000s　概率机器人、优化与学习开始合流

| 节点 | 关键变化 |
|---|---|
| particle / graph-based SLAM | 大规模状态估计与优化成熟 |
| sampling-based planning | PRM / RRT / RRT* 成为高维规划主力 |
| MPC / trajectory optimization | online optimization 更深入进入控制 |
| imitation / inverse RL | 从 demonstration 学习行为成为独立范式 |
| reinforcement learning | interaction-based policy improvement 逐渐进入真实控制研究 |

这一时期奠定了今天 model-based / model-free robot learning 的大部分问题定义。

---

# 2012–2016　Deep Learning 进入感知与控制

| 节点 | 关键变化 |
|---|---|
| deep vision | CNN 大幅改变 detection / recognition / representation |
| end-to-end visuomotor learning | image → action 逐渐可行 |
| deep RL | high-dimensional policy / value learning 扩展 |
| large-scale robot data collection | robot learning 开始从小数据走向 fleet/data scaling |

关键变化不是“神经网络替代机器人学”，而是 perception / representation 的能力和规模发生跃迁。

---

# 2016–2020　Sim-to-Real、Meta-Learning、Large-Scale Robot Learning

| 节点 | 关键变化 |
|---|---|
| domain randomization | 仿真数据开始规模化服务真机 |
| dexterous RL | contact-rich high-dimensional control 进入深度强化学习 |
| large-scale imitation | demonstration-driven manipulation 越来越成熟 |
| Transformer | sequence modeling / attention 为后续多模态 foundation model 提供基础 |
| language-conditioned robotics | language 开始更直接参与 robot task specification |

机器人学习开始同时面对：

```text
data scale
+ simulation
+ generalization
+ multimodality
```

---

# 2021–2022　Generalist Agent 与 Language → Robot Planning

| 节点 | 关键变化 |
|---|---|
| Decision Transformer 等 | trajectory 作为 sequence modeling 对象 |
| Gato | 多 domain/generalist sequence agent 的代表节点 |
| SayCan | LLM semantic prior × robot affordance/skill value |
| RT-1 | 大规模真实多任务 robot Transformer |

从这一阶段开始，foundation-model 思想正式进入 robot policy 设计。

---

# 2023　VLA、生成式动作与低成本双臂汇合

| 节点 | 关键变化 |
|---|---|
| PaLM-E | embodied multimodal language model |
| RT-2 | web-scale visual-language prior → robot action |
| Open X-Embodiment / RT-X | 多实验室、多机器人数据规模化 |
| Diffusion Policy | diffusion 建模 multimodal continuous action |
| ACT / ALOHA | action chunking + low-cost bimanual demonstration |
| RoboCat | generalist robot policy + new-task data loop |

这年之后，机器人研究越来越频繁地把：

```text
data
+ backbone
+ action representation
+ temporal execution
+ robot fleet
```

放在同一个 scaling 问题中。

---

# 2024　开放 VLA 与 Generalist Policy 生态形成

| 节点 | 关键变化 |
|---|---|
| Octo | 开放 generalist robot policy |
| OpenVLA | 开放 VLA baseline |
| DROID | 多场景真实 manipulation data |
| π0 | VLM + continuous flow-matching action expert |
| 3D-aware / DP3-style policies | point cloud / 3D representation 进入生成式 action 主线 |
| LeRobot ecosystem | dataset / policy / hardware tooling 更统一 |

“VLA”从少数封闭系统逐渐变成可公开研究的架构类别。

---

# 2025　VLA 开始分化：开放世界、实时、经验学习、Predictive Intelligence

| 节点 | 关键变化 |
|---|---|
| Gemini Robotics | foundation multimodality 更直接进入 robotics |
| Gemini Robotics-ER | embodied reasoning / planning 更显式分层 |
| GR00T N1 | humanoid foundation model 路线公开化 |
| GR00T N1.5 | cross-embodiment / post-training 成为主线 |
| Helix | slow semantic + fast visuomotor multi-rate humanoid architecture |
| π0.5 | open-world generalization |
| Real-Time Action Chunking | stale action / async inference 被显式建模 |
| π*0.6 | foundation policy + RL / experience |
| V-JEPA 2 | predictive video representation 与 action-conditioned prediction |
| Cosmos | world foundation model / synthetic physical-AI data |

> **勘误：GR00T N1.6 不属于 2025。官方 GitHub release `n1.6-release` 发布于 2026-04-15。**

重要变化：研究问题从“能不能用大模型出动作”转向：

- real-time execution；
- whole-body；
- experience learning；
- predictive model；
- deployment。

---

# 2026　VLA 之后：Memory、Experience、Whole-Body、World Action 与长期实体智能

> 以下节点以 **2026-09-14** 为冻结截面。

| 日期 | 节点 | 本书如何理解 |
|---|---|---|
| 2026-01 | **Helix 02** | full-body loco-manipulation 与 whole-body visuomotor control |
| 2026-03 | **Multi-Scale Embodied Memory** | long/short-term embodied memory 显式进入 VLA |
| 2026-03 | **efficient online RL / RL-token-style adaptation** | foundation policy 开始低成本吸收 on-robot experience |
| 2026-03 | **V-JEPA 2.1** | dense / temporally consistent predictive representation |
| 2026-04 | **π0.7** | steerability、复杂组合、新能力证据成为评价重点 |
| **2026-04-15** | **GR00T N1.6** | stronger VLM/DiT line 与 humanoid/loco-manipulation 扩展；官方 `n1.6-release` |
| **2026-04-18** | **GR00T N1.7 release** | 新 VLM backbone、显式 embodiment tags、N1.7 processor/action-head stack 与部署工具链；官方 `n1.7-release` |
| 2026-05 | **Cosmos 3** | reasoning、world generation、action prediction 更紧密融合 |
| 2026-07 | **Gemini Robotics 2** | whole-body、dexterity、multi-robot、embodied reasoning 合流 |
| 2026-07 | **Gemini Robotics On-Device 2** | edge inference + faster new-embodiment adaptation |
| 2026 | **SONIC / scalable humanoid motion tracking** | humanoid motor foundation / whole-body tracking scaling |

## GR00T N1.6 → N1.7 为什么值得单独记

这不是“版本号增加”本身，而是一个很好的系统研究样本。

公开仓库让我们可以追踪：

```text
embodiment tag / dataset
→ processor
→ VLM backbone
→ action head
→ action horizon
→ async inference / RTC
→ deployment
```

N1.7 当前官方仓库 README 把其描述为 latest / General Availability line，并说明新 VLM backbone 为：

```text
Cosmos-Reason2-2B
(Qwen3-VL architecture)
```

它因此特别适合教材中的 source-level system dissection。

---

# 2026 截面的研究问题发生了什么变化

前沿已经明显从：

```text
Can a model generate robot actions?
```

转向：

```text
Can it act in real time?
Can it remember persistent task/world state?
Can it learn from its own experience?
Can it predict counterfactual physical futures?
Can it coordinate the whole body?
Can it transfer to a new embodiment?
Can it keep improving without forgetting?
Can it remain safe while adapting?
```

研究对象逐渐从单独的 `policy` 变成长期存在的 **physical agent system**。

---

# 历史给我们的四个方法论教训

## 1. 新名字往往承载旧问题

今天的：

- VLA ↔ perception–action mapping + generalization；
- world model ↔ model-based control / system identification；
- active perception ↔ information gathering；
- memory ↔ belief / task state / persistent world state；
- whole-body VLA ↔ whole-body control + learned semantic policy。

历史可以防止把旧问题重新命名成“突然出现的新范式”。

## 2. 规模确实改变了可实验的问题

大模型、大数据、GPU simulation 和 foundation representation 让过去很难验证的：

- cross-task；
- cross-robot；
- human-video pretraining；
- long-horizon memory；
- whole-body generalist policy

成为现实实验对象。

## 3. Runtime 重新成为模型的一部分

2025–2026 的 RTC、async inference、on-device policy、whole-body multi-rate systems 说明：

\[
\text{intelligence quality}
\neq
\text{checkpoint quality only}.
\]

真实系统能力是：

\[
\text{model}
+
\text{executor}
+
\text{controller}
+
\text{latency}
+
\text{hardware}.
\]

## 4. 下一阶段更像“长期实体智能”而不是“更大的动作模型”

```text
VLA
+ Memory
+ World Model
+ Experience Learning
+ Whole-Body
+ Cross-Embodiment
+ Safety
+ Continual Development
```

这才是 2026 以后更值得追踪的统一问题。
