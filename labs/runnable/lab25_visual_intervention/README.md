# Lab 25 — VLA Visual Intervention

> **Question:** 如果 visual representation 里可以被 probe 读出目标几何，能否据此断言 policy 真正在用这份视觉信息控制动作？

这个 runnable Lab 把 “vision matters” 从 feature visualization 改写成 paired causal intervention。

所有 policy 接收：

- 同一个固定 instruction；
- 同一个 visual representation schema；
- 同一批 base episodes；
- 同一 action space。

base distribution 故意让 target appearance、irrelevant distractor 与真实 target geometry 强相关，因此四种 policy 在普通 benchmark 上都能达到 100% success。随后每次只干预一个视觉因素，观察 action 和 downstream success 是否按物理因果关系变化。

## 视觉表示

最小 scene 是一个 1-D reach task，真实 target 位于 world coordinate `x`，深度固定为 `z=1`。camera yaw 为 `theta` 时，normalized image coordinate 为

\[
u=\frac{\cos\theta\,x-\sin\theta}{\sin\theta\,x+\cos\theta}.
\]

如果 camera pose 被正确使用，可以反解

\[
x=\frac{\sin\theta+u\cos\theta}{\cos\theta-u\sin\theta}.
\]

representation 同时包含：

```text
fixed instruction
target pixel coordinate u
camera yaw
target texture id
background id
irrelevant distractor pixel coordinate
```

因此 target geometry 在四种 policy 的 representation 中都真实存在，而且外部 geometry probe 都可以几乎零误差恢复 `x`。

## 四个 action head

### `geometry_causal`

显式使用 target pixel + camera pose 恢复 world target。

预期行为：

```text
target moves      → action follows
texture changes   → action invariant
background changes→ action invariant
camera changes    → world action invariant
distractor moves  → action invariant
geometry corrupted→ action fails
```

### `appearance_shortcut`

忽略 target geometry，用训练分布中与 target bin 完全相关的 texture/background shortcut 产生 action。

重要的是：**它仍接收同一个、可被 probe 精确解码几何的 representation。**

因此这个 condition 直接测试：

```text
information is present in representation
≠
policy causally uses that information
```

### `camera_unaware`

使用 target pixel coordinate，但把 pixel 直接当 world coordinate，不使用 camera yaw。

它在 canonical camera 下表现完美，但 camera-angle intervention 后失败，用来攻击 frame / calibration misuse。

### `distractor_shortcut`

base distribution 中 irrelevant distractor 与 target 保持固定 offset；该 policy 因而可以靠 distractor 位置间接恢复 target。

当只移动 distractor、真实 target 不变时，action 会跟着无关物体移动。

## Intervention matrix

每个 episode 由同一个 base scene 派生六个 counterfactual intervention：

### 1. `target_position`

只改变真实 target position，appearance、background 和 distractor 保持原值。

这是 task-relevant intervention。正确 policy 应满足近似

\[
\frac{\Delta a}{\Delta x_{target}}\approx 1.
\]

### 2. `texture_swap`

只交换 target texture，world target 不动。

### 3. `background_swap`

只换 background id，world target 不动。

### 4. `camera_angle`

只改变 camera yaw。像素坐标变化，但 world target 不变。

### 5. `distractor_move`

只移动 irrelevant distractor，world target 不变。

### 6. `geometry_shuffle`

保留 instruction、appearance、background 和真实 task target，只把 target geometry token 替换成来自另一个远距离 target bin 的几何。

它是对 `geometry_causal` 的直接负对照：若 policy 真使用 target geometry，corruption 必须传播到 action failure。

## 为什么普通 benchmark 不够

base episodes 中：

```text
true target geometry
↔ texture/background label
↔ distractor location
```

三者高度相关。

因此：

```text
geometry-causal policy
appearance shortcut
distractor shortcut
camera-unaware geometry policy
```

都可以在 observational benchmark 上拿到 100% success。

只有 intervention 才能区分：

```text
correlation available
from
causal variable actually read by the action head
```

## Metrics

实验记录：

- base success；
- intervention success；
- mean absolute action error；
- mean absolute action change；
- task-position signed response gain；
- base geometry-probe RMSE；
- raw per-episode action / target / visual feature values。

其中最关键的组合证据是：

```text
appearance_shortcut:
geometry probe RMSE ≈ 0
+ base success = 1
+ target-position response gain = 0
+ texture/background intervention changes action
```

这比单独展示 probe accuracy 或 attention/saliency 更接近“policy 是否因果使用视觉变量”这个问题。

## Deterministic quick protocol

CI 使用 **160 paired episodes**。target 分布在 5 个位置 bin，每个 bin 加小幅 jitter；camera intervention 正负 yaw 平衡；target/distractor displacement 正负平衡。

quick reference 设计为：

```text
all four policies:
base success = 1.0
geometry probe RMSE ≈ 0

geometry_causal:
target_position = 1.0
texture/background/camera/distractor = 1.0
geometry_shuffle = 0.0

appearance_shortcut:
target_position = 0.0
texture_swap = 0.0
background_swap = 0.0
geometry_shuffle = 1.0

camera_unaware:
target_position = 1.0
camera_angle = 0.0

distractor_shortcut:
target_position = 0.0
distractor_move = 0.0
geometry_shuffle = 1.0
```

## Run

```bash
python labs/runnable/lab25_visual_intervention/run.py \
  --quick \
  --output /tmp/lab25

python labs/runnable/lab25_visual_intervention/analyze.py \
  /tmp/lab25/policy_metrics.csv \
  --output-dir /tmp/lab25
```

CI regression:

```bash
python labs/runnable/lab25_visual_intervention/smoke.py
```

## Outputs

```text
/tmp/lab25/
├── episode_specs.csv
├── episode_results.csv
├── intervention_metrics.csv
├── policy_metrics.csv
├── experiment_summary.json
├── analysis.json
├── ANALYSIS.md
└── runs/
    └── <policy-run>/
        ├── manifest.json
        ├── steps.csv
        ├── failures.jsonl
        └── summary.json
```

## Scientific scope

这个 M 层实验支持的结论很窄：

> 在一个 representation 同时含 task geometry 与 spurious visual correlates 的 controlled task 中，probe-decodable information 不能证明 action head 因果使用该信息；paired visual interventions 可以把 task-relevant geometry use、appearance shortcut、camera-frame misuse 和 distractor shortcut 分开。

它**不**声称代表真实 VLA 的视觉复杂度。下一层必须把相同 intervention schema 搬到真实图像 / simulator / open VLA checkpoint：真实 object translation、texture replacement、background compositing、camera extrinsic perturbation、distractor insertion/removal，并继续测 action distribution 与 physical success，而不是只测 feature probe。
