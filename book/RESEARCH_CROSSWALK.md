# Research Crosswalk — 51 Part 如何连接到代码、Labs、源码与研究问题

> 本页解决一个教材常见断层：**正文读懂了，但不知道下一步该手算什么、跑什么、读哪段源码、怎样把它变成可证伪研究。**
>
> 使用方式：读完任意 Part 后，从同一行继续进入 minimal code / Lab / Case Study / Atlas；最后必须回答该行的“研究验收问题”。

---

## Volume 0　导论与技术史

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **0 具身智能究竟是什么** | 从 `code/minimal/control.py` 看最小 feedback loop | `figures/CORE_DIAGRAMS.md`、`references/FAILURE_ATLAS.md` | 一个“智能”模块若不进入闭环，怎样证明它对真实行为有因果作用？ |
| **1 思想史与技术史** | 任选一个当前系统反向画技术谱系 | `references/TIMELINE.md`、`MODEL_ATLAS.md` | 今天的新名词究竟改变了旧问题的哪个数学对象、接口或规模条件？ |

## Volume I　数学与计算语言

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **2 线代、微积分与数值计算** | Lab 01；`planar_arm.py` | `DERIVATIONS.md` D1–D3/D6 | 数值误差、rank 与 conditioning 什么时候会被误判成“模型失败”？ |
| **3 概率、信息与不确定性** | [Runnable Lab 13](../labs/runnable/lab13_active_perception/README.md)；Lab 10；`kalman_filter.py`、`active_perception.py` | [Lab 13 CI Reference](../labs/runnable/lab13_active_perception/REFERENCE_RESULTS.md)、Failure Atlas 的 uncertainty/calibration 条目 | 置信度是否校准？不确定性是否真的改变 sensing decision，而且这种变化是否传到任务成功？ |
| **4 优化、动态系统与决策** | Lab 05–07；`control.py` | `DERIVATIONS.md` 的 optimal/control 推导 | 优化器改善的是 objective，还是实际闭环行为？模型误差进入稳定性后会怎样？ |
| **5 几何、图与因果** | Lab 03 / 11 / 31 | Experiment Protocol 的 intervention/negative control | correlation、prediction、intervention、control 四者怎样分开验证？ |

## Volume II　机器人身体、几何、力学与控制

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **6 机器人身体与机电系统** | Lab 39 / 40 | Hardware Atlas | policy 输出之后经过哪些 driver、bus、actuator 与 safety boundary？ |
| **7 刚体几何与 SE(3)** | Lab 03；`se3.py` | D4–D5；Core Diagrams 的 frame 图 | world/base/camera/EE frame 是否在代码、数据和标注中完全一致？ |
| **8 运动学与 Jacobian** | Lab 02 / 04；`planar_arm.py` | D1–D3/D6 | 同一个 learned action 在 singularity / joint limit 附近是否仍可执行？ |
| **9 动力学、接触与抓取** | [Runnable Lab 14](../labs/runnable/lab14_tactile_reflex/README.md)；Lab 05 | [Lab 14 CI Reference](../labs/runnable/lab14_tactile_reflex/REFERENCE_RESULTS.md)、Failure Atlas 的 contact/dynamics 条目 | contact failure 来自 policy、摩擦/动力学、controller bandwidth 还是 feedback latency？这些因素能否独立干预？ |
| **10 Feedback / Optimal / Whole-Body Control** | Lab 06；`control.py` | Hardware Atlas、Part 35 | learned policy 与 PID/impedance/WBC 的边界究竟在哪里？ |
| **11 Motion / Task / Uncertainty Planning** | [Runnable Lab 29](../labs/runnable/lab29_world_model_mpc/README.md)；Lab 07；`world_model_mpc.py` | [Lab 29 CI Reference](../labs/runnable/lab29_world_model_mpc/REFERENCE_RESULTS.md)、World Model Control case | planner 的收益来自搜索、模型预测还是更大 compute budget？planning horizon 何时开始放大 model bias？ |

## Volume III　感知、状态与世界表示

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **12 Sensors、Calibration 与 Time** | Lab 08 / 39 | Failure Atlas F-SEN 系列 | timestamp / calibration error 能否解释所谓视觉泛化失败？ |
| **13 2D Vision 与 Representation** | Lab 12 / 25 | Model Atlas、视觉 intervention protocol | feature 里“有信息”与 policy “因果使用信息”如何区分？ |
| **14 3D / 4D World Representation** | Lab 09 / 11 | Benchmark Atlas | 几何精度提升是否真的提高 manipulation，而非只提高 probe？ |
| **15 State Estimation / Localization** | Lab 10 / 11；`kalman_filter.py` | Failure Atlas state/belief 条目 | observation 与 belief 混用会产生什么 failure？ |
| **16 Tactile / Contact Intelligence** | [Runnable Lab 14](../labs/runnable/lab14_tactile_reflex/README.md) | [Lab 14 CI Reference](../labs/runnable/lab14_tactile_reflex/REFERENCE_RESULTS.md)、Hardware Atlas、Failure Atlas contact/slip | 高频 tactile residual 是否在慢语义策略之外提供独立增益？若 tactile 数据 stale，高更新频率还是否有效？ |
| **17 Active Perception** | [Runnable Lab 13](../labs/runnable/lab13_active_perception/README.md)；`active_perception.py` | [Lab 13 CI Reference](../labs/runnable/lab13_active_perception/REFERENCE_RESULTS.md)、Benchmark Atlas、Experiment Protocol | information gain 是否真正提高任务判断？正确 view geometry 是否因果必要？额外 sensing motion 是否值得？ |

## Volume IV　Robot Learning

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **18 为机器人重新学习 ML** | Lab 15–21 | Derivations、Evaluation Atlas | i.i.d. validation loss 为什么不能替代 closed-loop rollout？ |
| **19 Imitation Learning** | Lab 15–17；`bc_dagger.py` | `ACT_SOURCE_WALKTHROUGH.md` | dataset coverage、covariate shift、chunking 各自贡献多少？ |
| **20 RL / Offline RL / Interaction** | Lab 18 / 19 / 32 | Experiment Protocol | improvement 来自 reward、exploration、critic 还是新数据本身？ |
| **21 Generative Action + Real-Time Policy** | [Runnable Lab 22](../labs/runnable/lab22_async_execution/README.md)；Lab 20–21；`generative_actions.py`、`action_tokenization.py`、`chunk_latency.py` | Diffusion Policy / SmolVLA cases、Action Path Comparison | action generator 与 temporal executor 的收益能否被独立隔离？ |

## Volume V　Robot Foundation Models

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **22 Language / VLM / Physical Grounding** | Lab 23 / 31 | Model Atlas | 语言/VLM 提升的是 task semantics 还是 motor precision？ |
| **23 VLA 形成：2022–2024** | Lab 23；`action_tokenization.py` | `OPENVLA_SOURCE_WALKTHROUGH.md` | web semantic prior 到 action 的路径在哪里，量化/归一化又丢了什么？ |
| **24 VLA 第二阶段：2024–2026** | [Runnable Lab 22](../labs/runnable/lab22_async_execution/README.md) / Lab 24 / 26；`chunk_latency.py`、`embodiment_interfaces.py` | SmolVLA / GR00T N1.7 cases | flow expert、RTC、embodiment conditioning 哪一项对 success 有独立因果贡献？ |
| **25 VLA 内部机制** | Lab 23–25 | Action Path Comparison、Source-Code Atlas | 冻结/打乱某一 modality 后行为如何变化？所谓 reasoning/vision 是否被读取？ |
| **26 Robot Data / Human Video / Cross-Embodiment** | Lab 26；`embodiment_interfaces.py` | Dataset Atlas、cross-matrix | 数据量增加与 coverage dimension 增加如何分开？padding 是否掩盖 action semantics？ |

## Volume VI　Reasoning、Memory、Experience 与 World Models

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **27 Embodied Reasoning / Agentic Robotics** | [Runnable Lab 31](../labs/runnable/lab31_reasoning_negative_control/README.md) | [Lab 31 CI Reference](../labs/runnable/lab31_reasoning_negative_control/REFERENCE_RESULTS.md)、Failure Atlas、Experiment Protocol | correct / no-plan / random-order / fluent-wrong / binding controls 能否把表面自洽、局部可执行与真实因果正确性分开？ |
| **28 Robot Memory** | Lab 27 | Model Atlas | memory 是保存 task state，还是只扩大 context？shuffled memory 会怎样？ |
| **29 Learning from Experience** | [Runnable Lab 33](../labs/runnable/lab33_continual_learning/README.md)；Lab 32 | [Lab 33 CI Reference](../labs/runnable/lab33_continual_learning/REFERENCE_RESULTS.md)、Timeline、Dataset Atlas | autonomous data 的 marginal value 是否超过 curated demonstrations？新经验写入后旧能力退化多少，retention 又付出多少 plasticity / memory 成本？ |
| **30 World Models / Predictive Intelligence** | [Runnable Lab 29](../labs/runnable/lab29_world_model_mpc/README.md)；Lab 28；`world_model_mpc.py` | [Lab 29 CI Reference](../labs/runnable/lab29_world_model_mpc/REFERENCE_RESULTS.md)、V-JEPA 2.1 case、World Model Control case | passive prediction、counterfactual action sensitivity、multi-step rollout accuracy 与 closed-loop control gain 能否逐层分开？ |
| **31 Generative Worlds / Physical Simulation Foundation Models** | Lab 30 | World Model Control、Benchmark Atlas | visual realism 与 counterfactual/control fidelity 的相关性有多强？ |

## Volume VII　Manipulation、Navigation、Humanoid 与 Multi-Robot

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **32 Manipulation** | Lab 15 / 20；Capstone 1 | Benchmark Atlas、Failure Atlas | success failure 是 perception、action distribution、contact 还是 controller？ |
| **33 Bimanual / Dexterity / Tactile** | [Runnable Lab 14](../labs/runnable/lab14_tactile_reflex/README.md)；Lab 17 / 37 | [Lab 14 CI Reference](../labs/runnable/lab14_tactile_reflex/REFERENCE_RESULTS.md)、ACT case、Hardware Atlas | 双臂/灵巧接触中，慢语义策略与快 contact residual 应如何分工？收益来自 tactile modality 还是低延迟闭环？ |
| **34 Mobile / Embodied Navigation** | [Runnable Lab 13](../labs/runnable/lab13_active_perception/README.md)；Lab 07 | [Lab 13 CI Reference](../labs/runnable/lab13_active_perception/REFERENCE_RESULTS.md)、Benchmark Atlas | map/belief/planner 与 learned policy 的边界怎样做公平比较？主动 sensing 的信息收益如何计入额外运动成本？ |
| **35 Humanoid / Whole-Body** | Lab 35 / 36 | Hardware Atlas、GR00T N1.7 case | whole-body 不是 action dim 变大：balance/contact/WBC 哪一层承担了稳定性？ |
| **36 Human–Robot / Multi-Robot** | Lab 38 | Failure Atlas communication/system 条目 | collaboration gain 在 communication delay/dropout 下是否仍成立？ |

## Volume VIII　Cross-Embodiment 与长期发展

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **37 Cross-Embodiment Intelligence** | Lab 26；`embodiment_interfaces.py` | GR00T case、Hardware Atlas | 已见 robot mixture 与 unseen morphology transfer 必须怎样分开报告？ |
| **38 Continual / Lifelong / Developmental Learning** | [Runnable Lab 33](../labs/runnable/lab33_continual_learning/README.md)；`continual_metrics.py` | [Lab 33 CI Reference](../labs/runnable/lab33_continual_learning/REFERENCE_RESULTS.md)、Experiment Protocol | plasticity、retention、transfer、memory 是否同时报告？正确 replay 信息是否因果必要？新能力是否靠不可控参数扩张换来？ |
| **39 Self-Evolving Physical Intelligence** | [Runnable Lab 33](../labs/runnable/lab33_continual_learning/README.md)；Lab 32–34；Capstone 2 | [Lab 33 CI Reference](../labs/runnable/lab33_continual_learning/REFERENCE_RESULTS.md)、Failure Atlas、Timeline | 系统“自我进化”具体改变参数、结构、记忆还是数据分布？它能否在持续更新时跨越 stability–plasticity，而不是只会覆盖旧能力？怎样证伪？ |

## Volume IX　Simulation、Data 与 Deployment

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **40 Physics Simulation / Robot Platforms** | Lab 18 / 35 / 36 | Benchmark / Hardware Atlas | simulator fidelity 的哪一部分对目标任务真正敏感？ |
| **41 Synthetic Data / Sim2Real** | Capstone 1 / 2 | Dataset Atlas | synthetic data 的收益来自 coverage、label quality 还是 domain randomization？ |
| **42 Robot Data Engineering** | Lab 32 | Dataset Atlas、cross-matrix | schema / normalization / timestamp / success label 错误能否被训练 loss 检测？ |
| **43 Robot Systems / Deployment** | [Runnable Lab 22](../labs/runnable/lab22_async_execution/README.md) / [Runnable Lab 14](../labs/runnable/lab14_tactile_reflex/README.md) / Lab 39 / 40；`chunk_latency.py` | Lab 14/22 CI References、SmolVLA / GR00T cases、Hardware Atlas | P50/P95/P99 latency、jitter、queue、action age、sensor age、multi-rate residual 和 watchdog 是否作为实验变量报告？ |

## Volume X　Evaluation 与 Safety

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **44 Benchmarks / Evaluation Science** | `evaluation_stats.py`；所有 Lab 的统一统计 | Benchmark Atlas、cross-matrix | 不同 robot/controller/reset/protocol 的 success rate 是否有资格放在同一表？ |
| **45 Reliability / Safety / Human Intervention** | Lab 40 | Failure Atlas | unsafe action 在 model、executor、controller、watchdog 哪一层被拦截？漏检/误杀率是多少？ |

## Volume XI　研究方法与下一代架构

| Part | 可执行 / Lab | 连接资产 | 研究验收问题 |
|---|---|---|---|
| **46 Rigorous Embodied-AI Research** | [Runnable Lab 31](../labs/runnable/lab31_reasoning_negative_control/README.md)；Capstone 3 | [Lab 31 CI Reference](../labs/runnable/lab31_reasoning_negative_control/REFERENCE_RESULTS.md)、`EXPERIMENT_PROTOCOL.md`、Failure Atlas | hypothesis 是否提前给出能让方法失败的 negative control？能否证明负对照攻击的是因果机制而非输出长度、动作词表或 compute budget？ |
| **47 Transformer 的角色与边界** | Lab 23/24；Action Path Comparison | OpenVLA / SmolVLA / GR00T cases | tokenization / attention 的收益是机制必需，还是工程惯性？ |
| **48 Mathematical Embodied Intelligence** | Lab 01–07；全部 Derivations | `DERIVATIONS.md` | 能否把模糊“智能模块”写成状态、约束、objective、operator 与可验证不变量？ |
| **49 Open Frontiers 2026-09** | Capstone 3 | Model Atlas、Timeline、Source-Code Atlas | 新模型到底改变哪个长期科学问题，而不是多一个品牌名？ |
| **50 从学习者到独立研究者** | 36 周路线 + 3 Capstones | 全部 Research Atlas | 能否从 failure 出发提出机制 hypothesis，并完成 controlled falsification？ |

---

# 推荐的“每 Part 完成定义”

读完一章，不以“看完文字”为完成。至少留下：

```text
1. 一张自己重画的数据流 / 物理流图
2. 一个关键公式的 shape-level 推导
3. 一个 minimal executable check
4. 一个 Lab / source-code trace
5. 一个 failure case
6. 一个 negative control
7. 一个仍然未解决、可实验的问题
```

当这七项都存在时，知识才从“知道名词”进入“可用于科研”。