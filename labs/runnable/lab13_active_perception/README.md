# Lab 13 — Active Perception：Information Gain 是否值得移动成本

对应课程：[`Lab 13 Active Perception`](../../LABS.md#lab-13active-perception)。

## Question

当目标被部分遮挡时，机器人应该固定看、随机换视角，还是根据当前不确定性主动决定**下一眼去哪里看**？

更严格的问题是：

> 主动视角选择降低 belief uncertainty 之后，是否真的提高最终任务判断，而且收益是否值得额外 sensing motion？

---

## Physical / information loop

实验使用一个最小 embodied sensing world：隐藏目标位于 7 个 scene cell 之一，相机只能处在 5 个离散 rail viewpoints。不同 viewpoint 对不同 cell 有不同 visibility。

```text
hidden target cell
      ↓
view-dependent occlusion
      ↓
noisy observation
      ↓
Bayesian belief update
      ↓
choose next camera view
      ↓
physical view movement cost
      ↺
```

每个 viewpoint 都有 observation model：

\[
M_v(o,s)=P(o\mid s,v),
\]

其中：

- \(s\)：真实 target cell；
- \(v\)：camera viewpoint；
- \(o\)：传感器输出的 target-cell observation。

可见 cell 的 recognition accuracy 较高；被遮挡 cell 仍提供弱但噪声更大的证据。

belief 更新：

\[
b_{t+1}(s)
\propto
b_t(s)M_{v_t}(o_t,s).
\]

---

## Policies

### `fixed_center`

相机始终停在中心 viewpoint。

它是零额外 sensing motion 的基线，但中心视角存在 blind region。

### `random_view`

每次 sensing 随机选择 viewpoint。

它测试“多换视角”本身是否足够。

### `info_gain`

对每个 candidate view 计算 expected information gain：

\[
IG(v)
=
H[b_t]
-
\mathbb E_{o\sim P(o\mid b_t,v)}H[b_{t+1}],
\]

再扣除 physical view-motion cost：

\[
S(v)
=
IG(v)
-
\lambda d(v_t,v).
\]

执行：

\[
v_{t+1}=\arg\max_v S(v).
\]

### `info_gain_shuffled_geometry`

这是机制负对照。

真实 observation 和 Bayesian update 都保持正确，但**view selection 阶段故意把 viewpoint geometry / observation model 的对应关系打乱**。

因此它攻击的是：

> “信息增益策略之所以有效，是因为它知道哪个物理视角会提供哪类信息。”

而不是攻击 posterior update 本身。

---

## Paired randomness

不同 policy 不能因为抽到不同 hidden targets 或不同 sensor noise 而被误判。

本实验固定：

```text
hidden_target = f(seed, episode)
potential_observation = g(seed, episode, view, sensing_step)
```

所以两个 policy 若在同一 episode、同一步选择同一 view，就会看到同一个 observation draw。

被比较的差异只来自**view-selection policy**。

---

## Metrics

每个 policy 报告：

- final target-inference accuracy；
- final belief entropy；
- total sensing movement distance；
- entropy reduction；
- unique viewpoints visited；
- failure events；
- task utility：

\[
U
=
\mathbb 1[\hat s=s]
-
\beta D_{sense}.
\]

这里的 utility 不是新的 benchmark score，而是为了防止把“信息更多”与“移动代价免费”混在一起。

---

## Run

完整实验：

```bash
python labs/runnable/lab13_active_perception/run.py
```

CI / quick experiment：

```bash
python labs/runnable/lab13_active_perception/run.py \
  --quick \
  --output /tmp/lab13
```

派生分析：

```bash
python labs/runnable/lab13_active_perception/analyze.py \
  /tmp/lab13/policy_metrics.csv \
  --output-dir /tmp/lab13
```

输出：

```text
experiment_manifest.json
policy_metrics.csv
analysis.json
ANALYSIS.md
<policy-run>/manifest.json
<policy-run>/steps.csv
<policy-run>/failures.jsonl
<policy-run>/summary.json
```

默认参数：[`config/default.json`](config/default.json)。

---

## Mechanism checks

### Check A — uncertainty

若 `info_gain` 不能比 random/fixed 显著降低 final entropy，则 next-best-view mechanism 没有被验证。

### Check B — task success

即使 entropy 下降，如果最终 target inference accuracy 不提高，也不能宣称 active perception 改善了任务能力。

### Check C — motion efficiency

与 random-view 相比，主动策略应以更短 sensing travel 获得更强或至少更有价值的信息。

### Check D — geometry negative control

若 `info_gain_shuffled_geometry` 与正确 `info_gain` 一样好，则“正确 viewpoint model 驱动信息获取”的机制解释受到直接质疑。

---

## Failure analysis

至少区分：

- **occlusion ambiguity**：当前所有已访问视角都难以区分候选 target；
- **view-model mismatch**：策略错误估计哪个 view 有信息；
- **motion over-spending**：为了很小 entropy gain 走太远；
- **posterior overconfidence**：belief 很尖锐但猜错；
- **sensor noise**：高价值 view 产生异常 observation；
- **task/uncertainty mismatch**：entropy 降低但 task decision 不改善。

---

## Simulator extension

Toy world 后续迁移到 manipulation simulator 时保持同一 contract：

```text
partial observation / occlusion
→ belief or task-relevant uncertainty
→ candidate View Goal
→ view-motion cost / reachability
→ new observation
→ task policy
```

需要新增：

- camera SE(3)；
- collision-free view motion；
- RGB-D / point cloud；
- object pose / grasp uncertainty；
- sensing latency；
- task success after perception；
- extra robot travel / time。

真正要验证的是：

> **task-relevant uncertainty reduction 是否值得 embodied information-gathering action 的物理成本。**
