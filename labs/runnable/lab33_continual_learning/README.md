# Lab 33 — Continual Learning：Stability–Plasticity 不是一个平均分

对应课程：[`Lab 33 Continual Learning`](../../LABS.md#lab-33continual-learning)。

## Question

机器人按顺序学习任务：

\[
A\rightarrow B\rightarrow C
\]

时，如何同时回答：

1. 新任务学得多快、学得多好？
2. 旧任务遗忘多少？
3. 新任务是否从旧表示中得到 forward transfer？
4. 保留旧能力用了多少 replay memory / regularization state？
5. 收益来自“保存了正确旧信息”，还是只因为多做了优化步骤？

这个 Lab 的目标不是找一个“continual learning 最佳算法”，而是把 **stability–plasticity dilemma** 做成可干预、可记录、可反驳的实验。

---

## Fixed-capacity construction

输入：

\[
x\in\mathbb R^3.
\]

三个任务分别依赖三条正交方向：

\[
A:\ y=\mathbb 1[x_1+\epsilon>0],
\]

\[
B:\ y=\mathbb 1[x_2+\epsilon>0],
\]

\[
C:\ y=\mathbb 1[x_3+\epsilon>0].
\]

但 shared representation 只能输出：

\[
z=W x,\qquad z\in\mathbb R^2.
\]

每个任务拥有独立 head：

\[
\hat y_j=h_j(z).
\]

因此实验刻意满足：

```text
3 independent task directions
→ 2-D shared bottleneck
→ task-specific heads
```

这消除了两个常见混淆：

- **不是标签语义冲突**：A/B/C 有自己的 heads；
- **不是靠参数无限增长**：所有方法网络参数量固定。

真正发生竞争的是共享表示容量。

---

## Four methods

### `naive_finetune`

只使用当前任务数据：

\[
\mathcal L=\mathcal L_{current}.
\]

它提供高 plasticity 基线，但 shared trunk 会持续被新任务重写。

### `replay`

当前任务 batch 加上旧任务 memory：

\[
\mathcal L
=\mathcal L_{current}
+\lambda_r\mathcal L_{replay}.
\]

每个旧任务存固定数量的原始样本，memory budget 单独报告。

### `quadratic_anchor`

不存旧样本，而是惩罚 shared trunk 偏离上一阶段参数：

\[
\mathcal L
=\mathcal L_{current}
+\lambda_a\|W-W_{anchor}\|_2^2.
\]

它代表最小 regularization-based retention mechanism。

### `replay_shuffled_labels`

保存同样数量的旧样本，也执行 replay update，但 replay labels 被确定性打乱。

这是关键 negative control：

> 如果“replay 有效”只是因为多做 gradient steps 或多占 memory，那么错误 replay 也应该有效。

若正确 replay 保留旧任务，而 shuffled replay 反而破坏 retention，则 replay 中**保存的旧任务信息**才是 causal variable。

---

## Sequential protocol

训练顺序固定：

```text
initial
→ learn A
→ evaluate A/B/C
→ learn B
→ evaluate A/B/C
→ learn C
→ evaluate A/B/C
```

形成标准 performance matrix：

\[
R_{i,j}
=
\text{performance on task }j
\text{ after learning phase }i.
\]

保存为每个 run 的：

```text
performance_matrix.csv
```

---

## Why task-specific heads

如果三个任务共享同一个输出 head，遗忘可能来自：

- representation drift；
- label semantics 冲突；
- classifier boundary 重写。

这里让每个任务保留自己的 head，是为了尽量把实验聚焦到：

> **shared representation 是否还能承载旧任务所需方向。**

旧 head 不更新，但 trunk 更新后旧任务仍可能失败，这就是 representational forgetting。

---

## Forward-transfer probe

直接在未训练的新 task head 上测 accuracy 没有意义，因为随机 head 会把“表示是否有用”和“head 是否训练过”混在一起。

因此每个 phase 后冻结 trunk，再为每个任务训练一个全新的小线性 probe：

```text
frozen trunk
→ small fixed-budget probe training
→ probe accuracy
```

得到：

```text
probe_matrix.csv
```

对任务 B/C 的 forward transfer 使用：

\[
FWT_j
=
P_{before\ learning\ j,j}
-
P_{initial,j}.
\]

这里的 \(P\) 是 fresh-probe performance，而不是随机旧 head 的输出。

---

## Metrics

### Final average performance

\[
A_{final}
=
\frac1K\sum_j R_{K,j}.
\]

### Forgetting

对旧任务 \(j\)：

\[
F_j
=
\max_{i\ge j}R_{i,j}-R_{K,j}.
\]

报告旧任务平均 forgetting。

### Backward Transfer

\[
BWT_j
=R_{K,j}-R_{j,j}.
\]

### Plasticity

本 Lab 用每个任务刚学完时的 performance：

\[
P
=
\frac1K\sum_j R_{j,j}.
\]

它回答“当前任务能不能快速进入 shared representation”，而不是只看最终 retained score。

### Resource accounting

同时报告：

- replay samples；
- replay bytes；
- anchor bytes；
- network parameter count；
- parameter growth；
- optimizer steps；
- trunk drift。

因此不能用“replay 更稳”掩盖 memory 成本，也不能用 adapter/扩参偷偷改变模型容量。

---

## Run

完整实验：

```bash
python labs/runnable/lab33_continual_learning/run.py
```

CI quick setting：

```bash
python labs/runnable/lab33_continual_learning/run.py \
  --quick \
  --output /tmp/lab33
```

派生分析：

```bash
python labs/runnable/lab33_continual_learning/analyze.py \
  /tmp/lab33/method_metrics.csv \
  --output-dir /tmp/lab33
```

输出：

```text
experiment_manifest.json
method_metrics.csv
analysis.json
ANALYSIS.md
<method-run>/manifest.json
<method-run>/steps.csv
<method-run>/failures.jsonl
<method-run>/summary.json
<method-run>/performance_matrix.csv
<method-run>/probe_matrix.csv
```

默认参数：[`config/default.json`](config/default.json)。

---

## Mechanism checks

### Check A — naive forgetting exists

固定 3D→2D bottleneck 下，如果 naive fine-tuning 几乎不遗忘，则这个 toy setting 没有制造出有效 stability–plasticity stress test。

### Check B — correct replay improves stability

正确 replay 应显著降低 old-task forgetting。

但**不要求 replay 的 final average 一定最高**：固定容量下，为旧任务保留方向本身可能牺牲新任务完整表示。

### Check C — plasticity cost must be visible

若 replay / anchor 在同一 2-D trunk 中保留旧任务，它们应表现出某种新任务 plasticity cost。否则需要怀疑实验其实没有产生容量竞争。

### Check D — replay information negative control

`replay_shuffled_labels` 与正确 replay 使用同样 replay memory 量和 replay update 结构，但旧标签信息错误。

它必须显著比正确 replay 更容易遗忘。

### Check E — no hidden capacity growth

所有方法：

\[
\Delta N_{parameter}=0.
\]

这样 stability gain 才不是简单靠网络扩张换来的。

---

## Failure analysis

至少区分：

- **representation overwrite**：shared trunk 向新任务方向旋转；
- **catastrophic forgetting**：旧任务 accuracy 大幅下降；
- **over-stability**：旧任务保留但新任务学不进去；
- **replay corruption**：memory 中错误信息反向破坏旧能力；
- **memory cost**：retention 依赖不断增长的 replay buffer；
- **capacity saturation**：有限 trunk 无法同时高质量编码全部任务轴。

---

## Scientific interpretation

这个 Lab 最重要的输出不是：

> replay 比 fine-tune 高多少分。

而是把 continual learning 写成一组同时受约束的量：

\[
\text{continual capability}
=
(\text{plasticity},\text{retention},\text{transfer},\text{memory},\text{capacity},\text{compute}).
\]

一个方法如果只提高 retention，却通过冻结几乎所有表示让新任务学不进去，不是更强的 continual learner；一个方法如果 plasticity 极高却持续覆盖旧能力，也不是。

真正值得研究的是 Pareto frontier，而不是单一平均准确率。

---

## Embodied extension

迁移到机器人时，A→B→C 不再是三个分类方向，而可以是：

```text
A: push / reach
B: grasp / place
C: new scene or new embodiment
```

仍必须在每个阶段重测所有旧能力，并额外报告：

- task success；
- intervention rate；
- recovery；
- replay storage；
- adaptation samples；
- wall-clock / gradient steps；
- model/adapter growth；
- failure taxonomy。

这正是后续 Developmental / Self-Evolving Agent 必须跨越的最小门槛：**系统不能把“会学新的”误写成“会持续学习”。**
