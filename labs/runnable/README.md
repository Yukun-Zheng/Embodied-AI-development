# Runnable Labs

`labs/runnable/` 是 [`labs/LABS.md`](../LABS.md) 的可执行层。这里不复制实验说明，而是把统一实验协议落实成**能运行、能记录、能失败、能复现**的程序。

执行层分工见 [`labs/EXECUTION_MATRIX.md`](../EXECUTION_MATRIX.md)。

## 目录契约

每个 runnable Lab 尽量遵循：

```text
labXX_name/
├── README.md
├── config/
│   └── default.json
├── run.py
└── analyze.py              # 当机制结论需要从 raw outputs 派生时
```

运行时生成的文件不提交为教材源文件：

```text
runs/<run-id>/
├── manifest.json
├── steps.csv
├── failures.jsonl
└── summary.json
```

跨条件 sweep 还应生成：

```text
results.csv / policy_metrics.csv / model_metrics.csv
analysis.json
ANALYSIS.md
```

公共记录逻辑放在 [`common.py`](common.py)。

## 统一输出

### `manifest.json`

至少记录：

- lab id；
- seed；
- git commit；
- Python / OS；
- start/end time；
- config；
- command-line parameters。

### `steps.csv`

保存能够重新分析机制的逐步量，而不是只留 final score。

### `failures.jsonl`

失败事件必须显式记录类别、时间步和上下文。没有 failure event 不等于没有失败，而可能意味着 logger 不完整。

### `summary.json`

只保存由 raw logs 可重建的摘要指标。

### `analysis.json / ANALYSIS.md`

当实验 claim 不是单个 scalar 能表达时，用 analyzer 从 raw/sweep outputs 推导：

```text
intermediate mechanism changed?
→ downstream task changed?
→ negative control degraded?
→ failure explanation still holds?
```

CI 可以直接检查 machine-readable `analysis.json`，避免把自然语言解释与实际数据分离。

## CI 原则

Hosted CI 只运行：

- CPU mechanism test；
- deterministic smoke test；
- config/schema check；
- simulator adapter import / dry-run（后续）。

不会在 GitHub-hosted runner 上运行：

- Isaac Sim / Isaac Lab GPU rollout；
- RoboTwin 大规模采集；
- 大型 VLA checkpoint；
- 真机 ROS 2 实验。

这些重实验仍应使用同一 manifest/results/failure schema，从而让本地、服务器和真机结果可以进入同一分析链。

## Current runnable reference labs

### [`Lab 13 — Active Perception`](lab13_active_perception/README.md)

在 partially observable toy scene 中显式模拟：

```text
occlusion
→ belief uncertainty
→ candidate viewpoints
→ information gain - motion cost
→ camera movement
→ new observation
→ task decision
```

比较 `fixed_center / random_view / info_gain / info_gain_shuffled_geometry`。关键机制问题是：**主动减少 uncertainty 是否真的提高任务判断，而且正确的 view geometry 是否因果必要。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab13_active_perception/REFERENCE_RESULTS.md)。

### [`Lab 14 — Force / Tactile Reflex`](lab14_tactile_reflex/README.md)

把接触恢复问题显式写成多速率闭环：

```text
transient friction loss
→ tactile timestamp / delay
→ slip detection
→ fast residual or slow policy
→ gripper actuator response
→ slip displacement
→ object retention
```

比较 `slow_policy_only / fast_tactile_reflex / delayed_tactile_reflex`。关键机制问题是：**高频 feedback 的收益是否来自及时信息进入闭环，而不只是 correction function 被高频调用。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab14_tactile_reflex/REFERENCE_RESULTS.md)。

### [`Lab 22 — Asynchronous Policy Execution`](lab22_async_execution/README.md)

在 double-integrator 闭环中显式模拟：

```text
observation timestamp
→ inference latency
→ action chunk timestamp
→ executor
→ action age
→ closed-loop tracking
```

比较 blocking/synchronous、naive async queue 与 latency-aware rebase。它的关键教学结果是：**降低 action age 是可验证的机制干预，但不保证 tracking 一定改善。**

### [`Lab 26 — Cross-Embodiment Transfer`](lab26_cross_embodiment/README.md)

把 cross-embodiment claim 分解成三个不能混写的层级：

```text
raw robot interface semantics
→ canonical state/action contract
→ multiple seen robot identities
→ held-out interpolation / extrapolation
→ continuous morphology conditioning
→ physical closed-loop success
```

比较 `raw_shared / canonical_interface_only / seen_robot_lookup / morphology_conditioned / wrong_morphology_tag / wrong_action_semantics`。关键机制问题是：**同一 policy 支持多个已见 robot 是否真的意味着未见 morphology transfer；新身体的 interface metadata、连续 morphology descriptor 与 task adaptation budget 各自贡献什么。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab26_cross_embodiment/REFERENCE_RESULTS.md)。

### [`Lab 27 — Long-Horizon Memory`](lab27_long_horizon_memory/README.md)

把“memory”从长 context 和 persistent storage 中拆出来：

```text
one-shot mission binding
→ 4 / 10 / 16 distractor subtasks
→ bounded recent context or persistent state
→ object / gate / bin memory queries
→ physical task success
→ storage / retrieval cost
```

比较 `no_memory / frame_context / episodic_log / semantic_memory / shuffled_memory / unrelated_memory`。关键机制问题是：**当 task-relevant cue 真正离开 recent context 后，正确 persistent state 是否因果必要；同容量但错误/无关的 memory 是否仍然失败；episodic trace 与 task-sufficient semantic state 的代价如何不同。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab27_long_horizon_memory/REFERENCE_RESULTS.md)。

### [`Lab 29 — World Model MPC`](lab29_world_model_mpc/README.md)

把 world model 拆成：

```text
passive one-step prediction
→ counterfactual action sensitivity
→ multi-step rollout bias
→ MPC control utility
```

比较 `action_aware / action_blind / wrong_action_sign`，再对 action-aware model 注入可控 action-gain bias 并扫描 planning horizon。核心目标是复现两个反例：

1. **被动分布上的小 prediction error 可以和错误 intervention model、失败 closed-loop planning 同时存在；**
2. **更长 planning horizon 先可能带来 look-ahead 收益，随后也可能放大 model bias。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab29_world_model_mpc/REFERENCE_RESULTS.md)。

### [`Lab 31 — Reasoning Negative Control`](lab31_reasoning_negative_control/README.md)

把 embodied reasoning 从“解释文本”改写成可执行因果链：

```text
world state + goal
→ causal model
→ high-level plan
→ executable operators
→ prerequisites / entity bindings
→ real state transitions
→ task success
```

比较 `correct_plan / no_plan / random_plan / fluent_wrong_plan / shuffled_binding`。其中 `fluent_wrong_plan` 在自己的错误世界模型里完全自洽，但进入真实 transition 后在 locked episodes 上失败。关键机制问题是：**中间 reasoning trace 的因果模型、顺序与实体绑定是否真正被执行并改变行为，而不只是表面流畅。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab31_reasoning_negative_control/REFERENCE_RESULTS.md)。

### [`Lab 33 — Continual Learning`](lab33_continual_learning/README.md)

把 stability–plasticity dilemma 放进固定容量 sequential learning：

```text
3 independent task directions
→ 2-D shared bottleneck
→ A → B → C sequential updates
→ representation drift
→ retention / plasticity / transfer
→ replay or anchor memory cost
```

比较 `naive_finetune / replay / quadratic_anchor / replay_shuffled_labels`。关键机制问题是：**旧能力保留是否来自正确旧信息，而且 retention gain 付出了多少 plasticity 与 memory 成本。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab33_continual_learning/REFERENCE_RESULTS.md)。

### [`Lab 38 — Multi-Robot Collaboration`](lab38_multi_robot_collaboration/README.md)

把“多机器人协作”拆成异构能力、通信 freshness 与故障恢复三条可独立攻击的机制链：

```text
heterogeneous capabilities
→ task ownership / allocation
→ heartbeat freshness
→ duplicate / stale / mismatched assignment
→ real work progress
→ agent failure
→ interrupted-work reallocation
→ system completion
```

比较 `independent_no_comm / coordinated_fresh / coordinated_delayed / coordinated_dropout / shuffled_capability_map`，并单独比较 `failure_no_reallocation / failure_reallocation`。关键机制问题是：**协作收益是否来自正确 capability-aware allocation；状态消息变 stale/drop 后会先损失时间还是直接损失完成率；检测到机器人故障后是否真的释放并恢复中断工作。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab38_multi_robot_collaboration/REFERENCE_RESULTS.md)。

### [`Lab 40 — Watchdog / Safety Shield`](lab40_safety_shield/README.md)

把 safety layer 从“规则是否触发”改写成闭环物理机制：

```text
model / sensor fault
→ timestamp / freshness
→ proposed command
→ reject / predictive safe-stop / ask-human
→ finite braking dynamics
→ physical safety outcome
→ audit evidence
```

比较 `no_shield / static_rules / predictive_no_freshness / predictive_shield / overconservative_shield`。关键机制问题是：**target rejection、freshness watchdog 与 stopping-distance prediction 是否各自因果必要；以及 safety gain 是否以正常任务可用性为代价。**

CI-verified quick reference results 见 [`REFERENCE_RESULTS.md`](lab40_safety_shield/REFERENCE_RESULTS.md)。该 Lab 是闭环机制实验，**不构成真实机器人 functional-safety certification**。

## Phase 1 completion criterion

Runnable Lab 不是“有 `run.py`”就算完成。当前 reference labs 必须经过同一长期 CI：

```text
raw artifacts exist
+ metrics finite
+ negative controls pass
+ claimed mechanism variable actually changes
+ downstream task consequence is measured
+ falsification condition behaves as designed
```

后续加入 simulator adapter 时仍复用这套条件，而不是另起一套“GPU demo”标准。
