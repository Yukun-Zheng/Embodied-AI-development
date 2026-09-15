# Lab 29 — World Model MPC：Prediction ≠ Control Utility

对应课程：[`Lab 29 World Model MPC`](../../LABS.md#lab-29world-model-mpc)。

## Question

一个 world model 在 held-out dataset 上 one-step prediction error 很低，是否足以证明它可以用于 planning / control？

本 Lab 把这个问题拆成三层：

```text
observational prediction
        ↓
counterfactual action sensitivity
        ↓
closed-loop control utility
```

重点不是“训练一个更强 world model”，而是构造**预测分数很好但控制机制错误**的反例。

---

## Hypothesis

在训练数据的 action variation 很小时，一个忽略 action 的模型仍可能获得很小 one-step RMSE：

\[
\hat x_{t+1}=f(x_t),
\]

因为数据分布里：

\[
\operatorname{Var}(u_t)\ll1.
\]

但 MPC 真正需要的是：

\[
f(x_t,u_t)
\]

对不同候选动作有正确的**反事实敏感性**。

因此本 Lab 预测：

1. `action_blind` 的 passive one-step RMSE 可以仍然很小；
2. 但它预测不出改变 action 后 next state 怎样变化；
3. 放进 MPC 后，它没有可用的 action gradient / ranking，因此控制失败；
4. `wrong_action_sign` 即使 passive prediction error 仍是“小数”，control 也会因为 intervention direction 错误而严重失败。

---

## Physical toy system

真实 plant 是 1-D damped double integrator：

\[
p_{t+1}=p_t+\Delta t v_t+\frac12\Delta t^2u_t,
\]

\[
v_{t+1}=0.98v_t+\Delta t u_t.
\]

训练数据不是由强控制动作覆盖整个 action space，而是：

```text
state ~ broad distribution
action ~ N(0, small σ)
next state = true dynamics + observation noise
```

默认：

```text
train action std = 0.05
counterfactual probe action = ±1.0
MPC action limit = ±2.0
```

这故意制造一个常见研究陷阱：**observational data 很容易拟合，但 planning 需要的 intervention region 没有被充分激发。**

---

## Three world models

### A. `action_aware`

线性模型输入：

\[
[p_t,v_t,u_t,1]
\]

预测：

\[
[p_{t+1},v_{t+1}].
\]

它可以学习 action effect。

### B. `action_blind`

输入只有：

\[
[p_t,v_t,1].
\]

训练 distribution 的动作很小，因此它仍可能获得看起来不错的 one-step prediction score。

但对同一 state：

\[
\hat f(x,+a)-\hat f(x,-a)=0.
\]

这直接破坏 MPC 所需的 counterfactual ranking。

### C. `wrong_action_sign`

从 `action_aware` 的 learned model 出发，直接翻转 action coefficient：

\[
\hat B\rightarrow-\hat B.
\]

这是一个强负对照：模型可能仍能描述 state persistence，却把“往右推”和“往左推”的因果方向弄反。

---

## Three evaluations

### 1. Passive one-step RMSE

在与训练相同的小 action distribution 上测试：

\[
E_{1step}=\sqrt{\mathbb E\|\hat x_{t+1}-x_{t+1}\|^2}.
\]

这是最容易被论文单独报告的指标。

### 2. Counterfactual action sensitivity

固定同一个 state，比较：

\[
\Delta_{true}(x)=f(x,+a)-f(x,-a),
\]

\[
\Delta_{model}(x)=\hat f(x,+a)-\hat f(x,-a).
\]

定义：

\[
E_{cf}=\operatorname{RMSE}(\Delta_{model},\Delta_{true}).
\]

它直接测试：world model 是否知道 action 会怎样改变世界。

### 3. Closed-loop MPC

三种 world model 使用**完全相同**的 random-shooting MPC：

```text
current real state
→ sample candidate action sequences
→ rollout candidate futures through world model
→ rank future cost
→ execute only first action on real plant
→ observe real next state
→ repeat
```

固定：

- MPC horizon；
- candidate count；
- cost function；
- action bound；
- target；
- random candidate seed。

只换 world model。

---

## Metrics

`model_metrics.csv` 同时报告：

- `one_step_rmse`；
- `counterfactual_sensitivity_error`；
- true / predicted counterfactual sensitivity norm；
- `closed_loop_position_rmse`；
- final position error；
- realized control cost；
- mean action magnitude；
- failure events。

关键比较不是：

> 谁的 one-step RMSE 最小？

而是：

> **prediction error、action sensitivity、control utility 三者的排序是否一致？**

---

## Run

完整实验：

```bash
python labs/runnable/lab29_world_model_mpc/run.py
```

CI / quick experiment：

```bash
python labs/runnable/lab29_world_model_mpc/run.py \
  --quick \
  --output /tmp/lab29
```

输出：

```text
models.json
experiment_manifest.json
model_metrics.csv
<model-run>/manifest.json
<model-run>/steps.csv
<model-run>/failures.jsonl
<model-run>/summary.json
```

默认参数：[`config/default.json`](config/default.json)。

---

## Negative controls

### Control A — action-blind world model

如果 passive one-step RMSE 仍很低，但 counterfactual sensitivity 接近 0 且 MPC 失败，就证明：

> low observational prediction error **不是** planning-ready world model 的充分条件。

### Control B — wrong action sign

它测试的不是“有没有 action input”，而是：

> action-conditioned prediction 的**方向是否正确**。

### Control C — receding horizon remains identical

所有模型每一步都重新 observe real state 并重新 planning，因此失败不能简单归因于“没有 closed-loop feedback”。

---

## Failure analysis

至少区分：

- **observational shortcut**：state persistence 足以解释 passive dataset；
- **action blindness**：预测对 candidate action 无敏感性；
- **wrong intervention direction**：action effect 符号/方向错误；
- **planning exploitation**：planner 主动寻找 model error；
- **distribution shift**：MPC candidate action 超出 identification data 的 action scale；
- **closed-loop divergence**：错误 model 导致真实状态持续远离目标。

尤其要注意：

\[
\text{small one-step error}
\not\Rightarrow
\text{correct counterfactual}
\not\Rightarrow
\text{useful control}.
\]

---

## Research interpretation

这个 Lab 对 V-JEPA / video world model / latent world model 的启发不是“线性模型比大模型更好”，而是提供一个统一的 falsification template：

```text
1. observational prediction test
2. action intervention test
3. counterfactual ranking test
4. closed-loop planning test
```

如果一个 world model 只通过第 1 层，就不能直接把 representation/video prediction quality 写成“physical reasoning”或“planning capability”。

---

## Simulator extension

下一层迁移到 Push-T / RoboTwin 时保持同一结构：

```text
real/sim observation
→ candidate action chunk
→ world model rollout
→ predicted task cost
→ receding-horizon execution
```

需要额外记录：

- prediction horizon；
- action distribution coverage；
- visual / latent prediction error；
- object-pose/contact error；
- candidate ranking consistency；
- MPC success / recovery。

真正值得研究的问题是：**哪一种 prediction metric 最能预测 control utility？**
