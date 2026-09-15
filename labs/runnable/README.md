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
└── run.py
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
results.csv
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

### [`Lab 29 — World Model MPC`](lab29_world_model_mpc/README.md)

把 world model 拆成：

```text
passive one-step prediction
→ counterfactual action sensitivity
→ MPC control utility
```

比较 `action_aware / action_blind / wrong_action_sign`。核心目标是复现一个反例：**被动分布上的小 prediction error 可以和错误的 intervention model、失败的 closed-loop planning 同时存在。**

## Phase 1 completion criterion

Runnable Lab 不是“有 `run.py`”就算完成。当前 reference labs 必须经过同一长期 CI：

```text
raw artifacts exist
+ metrics finite
+ negative controls pass
+ claimed mechanism variable actually changes
+ falsification condition behaves as designed
```

后续加入 simulator adapter 时仍复用这套条件，而不是另起一套“GPU demo”标准。
