# Robotics Foundation Model / Policy / World Model Atlas

> **Snapshot: 2026-09-14**
>
> 这张 Atlas 不做“谁最强”排行榜，而是把代表系统投影到同一组**机制轴**上。VLM、VLA、policy、world model、memory、temporal executor、controller 本来就不是同一种东西，不能只拿一个 success rate 横排。

---

# 1. 先区分系统角色

```text
VLM / Reasoning Model
        ↓ semantics / planning / task state
VLA / Foundation Policy
        ↓ actions / targets / chunks
Temporal Executor
        ↓ when and how chunks are consumed / replaced
Controller / WBC
        ↓ stable physical command
Robot / World
```

另一条预测链：

```text
World / Video / Predictive Model
        ↓ predicted future / latent state
Planner / Evaluator / Policy
        ↓ action selection
```

另一条长期状态链：

```text
Memory System
        ↓ persistent task/world context
Reasoner / Policy
```

因此 `V-JEPA 2.1`、`RTC`、`π0.7`、`GR00T N1.7`、`Gemini Robotics 2` 解决的不是同一个问题。

---

# 2. 统一比较的 12 个机制轴

以后任何机器人基础模型先填这张表，再谈“更强”。

| 轴 | 必答问题 |
|---|---|
| **Perception** | RGB? Multi-view? Depth? Point cloud? Tactile? |
| **Language** | VLM/LLM 是否参与动作生成？训练时如何进入？ |
| **State** | proprioception、history、belief 怎样表示？ |
| **Memory** | context-only、external、episodic、semantic、multi-scale？ |
| **Action** | joint / Cartesian / torque？absolute / delta？frame？ |
| **Generator** | regression / AR / diffusion / flow / DiT / hybrid？ |
| **Temporal** | policy rate、action horizon、chunk、async、RTC？ |
| **Embodiment** | robot ID、adapter、morphology descriptor、tag、unseen-body test？ |
| **Controller** | PID / impedance / WBC / learned motor policy？ |
| **Data** | robot data、human video、synthetic、failure、online experience？ |
| **Learning after deployment** | frozen、fine-tune、RL、online adaptation、continual？ |
| **Evidence** | official demo、public benchmark、open code、independent reproduction？ |

没有这些信息，不应只用“参数量 + benchmark success”比较模型。

---

# 3. 2022–2024：VLA / Generalist Policy 形成期

| 系统 | 年份 | 主要角色 | Observation / Context | Action / Output | 核心机制变化 | 应避免的过度解读 |
|---|---:|---|---|---|---|---|
| **Gato** | 2022 | Generalist sequence agent | vision / text / task tokens | tokenized actions | 多任务统一为 sequence modeling | 支持很多任务 ≠ 通用机器人已解决 |
| **SayCan** | 2022 | Language planner + skill selection | language + affordance/value | skill choice | LLM knowledge × robot feasibility | 不是端到端 motor VLA |
| **RT-1** | 2022 | Multi-task robot policy | image + language | discretized action | 大规模真实多任务 robot Transformer | 多任务 ≠ open world |
| **PaLM-E** | 2023 | Embodied multimodal LM | vision / language / sensor embeddings | language / high-level outputs | sensor information 注入 LLM | reasoning 强 ≠ motor precision 强 |
| **RT-2** | 2023 | VLA | image + language | action as token vocabulary | web VLM knowledge → action | web knowledge ≠ dynamics model |
| **RoboCat** | 2023 | Generalist robot policy | visual/task context | robot action | new-task data → retrain → broaden | self-improvement 不等于 autonomous lifelong learning |
| **ACT / ALOHA** | 2023 | Imitation policy | image + proprioception | continuous action chunk | chunking + CVAE + low-cost bimanual data | 不是 VLA，但深刻影响后续真实机器人 policy |
| **Diffusion Policy** | 2023 | Generative visuomotor policy | observation history | continuous action sequence | diffusion 建模 multimodal action | 不含 language/foundation prior |
| **Open X-Embodiment / RT-X** | 2023–24 | Dataset + scaling | heterogeneous robot datasets | heterogeneous normalized actions | 多机构数据混合 | action alignment 仍是核心难题 |
| **Octo** | 2024 | Open generalist policy | multimodal robot observations | continuous robot actions | 开放跨数据源 generalist policy | 跨已见机器人 ≠ unseen morphology zero-shot |
| **OpenVLA** | 2024 | Open VLA | image + language | tokenized robot actions | 开放 VLM→action baseline | language capability 不能替代控制分析 |
| **π0** | 2024 | Foundation VLA | vision + language + state | continuous action via flow expert | VLM + continuous action expert | continuous action ≠ 自动解决 latency / whole-body |

---

# 4. 2025：从“会出动作”向开放世界、经验学习与多时间尺度分化

| 系统 / 技术 | 组织 | 主要角色 | 机制轴 | 研究意义 |
|---|---|---|---|---|
| **Gemini Robotics** | Google DeepMind | VLA / embodied system | multimodal foundation → robot action | foundation multimodality 更直接进入 robotics |
| **Gemini Robotics-ER** | Google DeepMind | Embodied reasoning | spatial / physical reasoning + planning | high-level reasoning 与 motor policy 开始显式分工 |
| **π0.5** | Physical Intelligence | Open-world policy | broader task/environment generalization | 从封闭 task set 推向 open-world 问题 |
| **π*0.6** | Physical Intelligence | Experience/RL-enhanced policy | foundation policy + RL / experience | demonstration-only → deployment experience |
| **FAST** | Physical Intelligence | Action representation | efficient action tokenization | 高维连续轨迹如何进入 sequence model |
| **Real-Time Action Chunking** | Physical Intelligence | Temporal executor | async / real-time chunk replacement | stale action 与 latency 成为一等问题 |
| **Helix** | Figure | Humanoid VLA | slow semantic + fast visuomotor | multi-rate architecture 进入 humanoid foundation policy |
| **GR00T N1** | NVIDIA | Humanoid foundation model | multimodal + action generation | humanoid foundation model 路线开放化 |
| **GR00T N1.5** | NVIDIA | Cross-embodiment / post-training | embodiment adaptation | 多机器人 post-training 成为主线 |
| **SmolVLA / LeRobot ecosystem** | Hugging Face | Small/open VLA stack | open policy + dataset + robot tooling | 低资源、可复现 foundation robotics |
| **V-JEPA 2** | Meta | Predictive representation | video representation + action-conditioned prediction | predictive intelligence 再次进入中心 |
| **Cosmos family** | NVIDIA | World foundation model | world/video generation + synthetic data | physical-AI data infrastructure 与 generative world model 合流 |

> 注：**GR00T N1.6 与 N1.7 都是 2026 年 4 月版本**，不应放入 2025 表格。

---

# 5. 2026：Memory、Experience、Whole-Body、World Action 与实时部署合流

| 日期/时期 | 系统 / 技术 | 类别 | 机制变化 | 本书位置 |
|---|---|---|---|---|
| **2026-01** | **Helix 02** | Whole-body humanoid policy | locomotion + manipulation + full-body coordination | Part 35 |
| **2026-03** | **Multi-Scale Embodied Memory** | Memory | long + short-term embodied context | Part 28 |
| **2026-03** | **Efficient online RL / RL-token-style adaptation** | Experience learning | low-cost online robot improvement | Part 29 |
| **2026-03** | **V-JEPA 2.1** | Predictive representation | dense / temporally consistent representation | Part 30 |
| **2026-04** | **π0.7** | Foundation policy | steerability / composition / new capability tests | Part 24/27 |
| **2026-04-15** | **GR00T N1.6** | Foundation policy | stronger VLM/DiT line, humanoid / loco-manipulation expansion | Part 24/35 |
| **2026-04-18** | **GR00T N1.7 release** | Open foundation policy stack | new VLM backbone, explicit embodiment tags, N1.7 processor/action-head stack, broader deployment tooling | Part 24/37/43 |
| **2026-05** | **Cosmos 3** | World / World-Action model | reasoning + world generation + action prediction | Part 31 |
| **2026-07** | **Gemini Robotics 2** | Whole-body VLA | whole-body, dexterity, multi-robot, embodied reasoning | Part 24/35/36 |
| **2026-07** | **Gemini Robotics On-Device 2** | Edge VLA | edge inference + faster embodiment adaptation | Part 24/37/43 |
| **2026** | **SONIC / scalable humanoid tracking** | Humanoid motor foundation | scalable whole-body motion tracking | Part 35 |

## 5.1 Why GR00T N1.7 matters as a textbook node

N1.7 is not added because “7 > 6”. It is useful because the open repository exposes an unusually complete scientific path:

```text
data / embodiment tag
→ processor
→ VLM
→ action head
→ action horizon
→ asynchronous inference / RTC interface
→ deployment runtime
→ real / simulated benchmark
```

Verified source entry points include:

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py
gr00t/data/embodiment_tags.py
getting_started/policy.md
getting_started/real_world_deployment.md
scripts/deployment/README.md
```

The current repository README describes the latest/GA N1.7 line with a **Cosmos-Reason2-2B / Qwen3-VL architecture** backbone. The GitHub `n1.7-release` tag was published on **2026-04-18**, before this textbook snapshot date.

---

# 6. Architecture-pattern Atlas

## Pattern A — Tokenized Action VLA

```text
image + language
→ VLM / Transformer
→ action tokens
→ de-tokenize
→ controller
```

Representative nodes: RT-2, OpenVLA.

Strength:
- unified sequence machinery.

Risk:
- quantization;
- long token sequence;
- continuous precision loss.

---

## Pattern B — VLM + Continuous Action Expert

```text
vision / language backbone
        ↓ context
continuous action expert
(flow / diffusion / DiT)
        ↓
action chunk
```

Representative modern line: π-family and multiple current foundation policies.

Strength:
- continuous geometry retained.

Open questions:
- backbone/action-expert joint training;
- action horizon;
- latency;
- low-level control interface.

---

## Pattern C — Slow Semantic + Fast Motor

```text
slow semantic / reasoning model
              ↓ latent / goal
fast visuomotor / motor policy
              ↓
controller
```

Representative line: Helix-style multi-rate humanoid systems.

Key insight:
> semantic reasoning and stabilizing control need not share a clock.

---

## Pattern D — Planner / Reasoner + Skill Library

```text
VLM / LLM reasoner
→ skill / subgoal
→ pretrained controller / policy
```

Representative historical node: SayCan and later agentic systems.

Strength:
- compositional structure.

Weakness:
- skill boundary;
- execution monitoring;
- error recovery.

---

## Pattern E — World Model + Policy / Search

```text
observation
→ predictive model
→ imagined futures
→ evaluator / search
→ action
```

This may be more appropriate than direct VLA when counterfactual physical prediction is required.

---

## Pattern F — Explicit Embodiment-Conditioned Foundation Policy

```text
observation + language + embodiment descriptor/tag
                    ↓
shared policy representation
                    ↓
robot-conditioned action head / decoder
```

GR00T N1.7’s open embodiment-tag machinery makes this pattern directly inspectable.

The critical test is not whether a tag exists, but whether it captures transferable morphology/dynamics information rather than acting as a dataset ID.

---

# 7. Scaling Atlas

Robot-foundation-model “scale” should be represented as a vector:

\[
Scale=(N_{episodes},N_{hours},N_{tasks},N_{robots},N_{scenes},N_{modalities},N_{failures},N_{online}).
\]

Also report:

- human-video pretraining;
- synthetic trajectories;
- world-model-generated data;
- intervention data;
- online experience.

“More data” is not one variable.

---

# 8. Generality Atlas

The word “general” should be decomposed:

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

A model may have strong `G_object` and weak `G_morphology`. One scalar “generalization” score hides the distinction.

---

# 9. Evidence Atlas

For every capability claim attach an evidence class:

| Level | Evidence |
|---|---|
| E0 | curated demo |
| E1 | official repeated evaluation |
| E2 | public benchmark with protocol |
| E3 | open code/checkpoint and reproducible run |
| E4 | independent reproduction |
| E5 | cross-lab / cross-hardware reproduction |

Open code raises inspectability, not automatically correctness.

---

# 10. Common invalid comparisons

Do not put the following numbers in one leaderboard without normalization:

- simulator vs real robot;
- tabletop arm vs humanoid whole-body;
- fixed camera vs moving-head perception;
- different low-level controllers;
- different action frequency / latency;
- different reset/intervention protocol;
- unknown pretraining overlap vs controlled data;
- cherry-picked demo vs all-trial benchmark;
- seen-robot adaptation vs unseen-morphology transfer.

---

# 11. Future-model admission rule

When a new system appears:

1. classify it as `VLM / Policy / VLA / Memory / World Model / Executor / Controller / System`;
2. fill the 12 mechanism axes;
3. assign evidence level;
4. identify what durable problem it changes;
5. attach it to an existing Part/Atlas entry.

Only a genuinely new mathematical object, learning paradigm or physical-system interface should modify the textbook’s top-level structure.
