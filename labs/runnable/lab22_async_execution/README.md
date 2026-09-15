# Lab 22 — Asynchronous Policy Execution

对应课程：[`Lab 22 Asynchronous Policy Execution`](../../LABS.md#lab-22asynchronous-policy-execution)。

## Question

当 policy inference latency 接近或超过 policy period 时，机器人失败究竟来自**模型不会控制**，还是来自**生成的 action 在真正执行时已经过时**？

## Hypothesis

如果 stale action chunk 是主要失败机制之一，那么：

1. latency 增大时，naive `async_queue` 的 action age 应近似随 latency 增长；
2. 只要保持同一 policy、同一 plant、同一 disturbance，latency-aware `async_rebase` 应显著降低 action age；
3. 若 action age 降低却 tracking 不改善，则瓶颈不只是 temporal staleness，需继续检查 model/controller mismatch。

这使“RTC/async inference 有用”变成一个可证伪命题，而不是系统术语。

---

## Mechanism

Toy physical loop：

```text
state q,v at observation time t_o
        ↓
chunk policy / internal rollout
        ↓ inference latency τ
chunk becomes available at t_o + τ
        ↓
executor
  ├─ sync_hold
  ├─ async_queue
  └─ async_rebase
        ↓
u_t
        ↓
noisy double-integrator plant
        ↓
new state
```

Plant：

\[
\dot q=v,
\qquad
\dot v=u-dv+w_t,
\]

其中 \(d\) 为 damping，\(w_t\) 为小 process disturbance。

Policy 在 observation time 生成 action chunk：

\[
a_{0:H-1}=\pi(q_{t_o},v_{t_o},r_{t_o:t_o+H}).
\]

真正关键的是第 \(k\) 个动作的 **action age**：

\[
\tau_{age}=t_{exec}-(t_o+k\Delta t).
\]

如果一个动作计划给过去的状态，却在未来执行，\(\tau_{age}\) 就会变大。

---

## Three executors

### `sync_hold`

policy inference 期间保持上一控制命令，相当于 blocking execution 的最小模型。

### `async_queue`

推理期间继续执行旧 chunk；新 chunk 到达后仍从 index 0 开始执行。

这会制造明确的 stale-action failure：

```text
planned for t_o
      ↓ wait τ
execute action[0] at t_o + τ
```

### `async_rebase`

新 chunk 到达时跳过已经属于过去的动作：

\[
k_{start}=\left\lfloor\frac{t_{now}-t_o}{\Delta t}\right\rfloor.
\]

这是一个**最小 latency-aware / RTC-like control**，不是任何特定论文 RTC 实现的复刻。它只用于验证“action timestamp alignment 本身是否有价值”。

---

## Controlled variables

三种 executor 固定：

- plant；
- target trajectory；
- controller gain；
- chunk policy；
- chunk horizon；
- control rate；
- policy request rate；
- disturbance seed。

只改变：

```text
executor mode × inference latency
```

默认 latency：

```text
0 / 50 / 100 / 250 / 500 ms
```

---

## Metrics

主要指标：

- tracking RMSE；
- `mean_action_age_s`；
- `p95_action_age_s`；
- success fraction；
- missed policy requests；
- discarded chunks；
- saturation fraction；
- control energy；
- failure events。

**Primary mechanism metric 是 action age，不是 success。** 只有先证明 executor 真正改变了 temporal variable，才能解释 downstream success 变化。

---

## Run

```bash
python labs/runnable/lab22_async_execution/run.py
```

CI / quick sweep：

```bash
python labs/runnable/lab22_async_execution/run.py --quick --output /tmp/lab22
```

默认配置：[`config/default.json`](config/default.json)。

输出：

```text
results.csv
sweep_manifest.json
<condition-run>/manifest.json
<condition-run>/steps.csv
<condition-run>/failures.jsonl
<condition-run>/summary.json
```

---

## Negative controls

### Control A — zero latency

当 \(\tau=0\) 时，`async_queue` 与 `async_rebase` 不应出现系统性的 action-age 差异。

### Control B — same seed

所有 condition 使用同一 disturbance seed。若不同方法使用不同噪声，executor gain 会和 environment stochasticity 混在一起。

### Control C — action-age intervention

核心检查：在非零 latency 下，`async_rebase` 必须比 naive `async_queue` 显著降低 p95 action age。若没有，说明所谓“latency-aware executor”根本没有改变它声称改变的变量。

---

## Failure analysis

需要区分：

- **stale action**：action age 高；
- **missed inference deadline**：request 在前一个 inference 未完成时到达；
- **chunk exhausted**：新 chunk 尚未到达但旧 chunk 已执行完；
- **controller saturation**：动作受到限幅；
- **tracking failure**：误差越过 failure threshold；
- **model mismatch**：action age 已低但 tracking 仍差。

这些 failure 不应压缩成一个 success rate。

---

## Simulator / real-robot extension

这个 Lab 的 executor contract 后续直接迁移到：

```text
Toy plant
  ↓
RoboTwin manipulation
  ↓
ROS 2 policy node + controller node
  ↓
real robot
```

替换环境时保持同一组时间变量：

```text
observation timestamp
request timestamp
inference ready timestamp
planned action timestamp
execution timestamp
action age
```

这样才能比较“同一 executor mechanism”是否跨 toy / simulator / real system 成立。
