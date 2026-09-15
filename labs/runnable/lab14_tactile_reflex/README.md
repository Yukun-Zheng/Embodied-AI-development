# Lab 14 — Force / Tactile Reflex：快接触闭环为什么不能等慢策略

对应课程：[`Lab 14 Force / Tactile Reflex`](../../LABS.md#lab-14force--tactile-reflex)。

## Question

如果一个高层 policy / VLA 只以几 Hz 更新，而 slip/contact event 在一次 policy cycle 内就可能完成，机器人应该：

1. 等高层模型下一次重新推理；还是
2. 允许一个更快的 tactile / force residual loop 直接修改低层抓持命令？

本 Lab 不把问题写成“视觉 vs 触觉”，而是写成一个**多时间尺度闭环**问题：

> 高频 feedback 的价值来自额外 modality，还是来自它能在物理事件仍可逆时进入控制环？

---

## Toy physical system

一个 gripper 用法向夹持力 \(F_g\) 抓住物体，物体受到等效负载 \(L\)。摩擦承载能力：

\[
F_{friction}=\mu F_g.
\]

定义 grip margin：

\[
m=\mu F_g-L.
\]

当 \(m<0\) 时产生 slip drive：

\[
s=\max(-m,0).
\]

最小滑移动力学：

\[
\dot v_{slip}=k_s s-d_s v_{slip},
\qquad
\dot x_{slip}=v_{slip}.
\]

当：

\[
x_{slip}\ge x_{drop}
\]

认为物体掉落。

Gripper actuator 不是瞬时到达命令，而是一阶响应：

\[
\dot F_g=\frac{F_{cmd}-F_g}{\tau_g}.
\]

因此实验同时包含：sensor/update latency、controller reaction、actuator bandwidth 和 contact dynamics。

---

## Transient slip event

默认抓取在 nominal friction 下稳定：

```text
base grip force = 8 N
nominal friction = 0.60
object load = 3 N
```

中途发生一次短暂摩擦下降：

```text
friction: 0.60 → 0.25
event duration: 140 ms
```

关键时间尺度：

```text
slow policy period: 200 ms  (5 Hz)
fast tactile period: 5 ms   (200 Hz)
slip event: 140 ms
```

因此一个完整 slip event 可以落在两个 slow-policy sample 之间。

---

## Three control modes

### `slow_policy_only`

只有 5 Hz 高层 loop 能读取 tactile slip signal 并切换到 rescue grip force。

如果事件恰好在 sample 之前发生，它可能被捕获；如果事件完整落在两个 sample 之间，高层 loop 可能完全漏掉。

这不是故意让 slow baseline “永远失败”，而是显式测量 phase-dependent event miss。

### `fast_tactile_reflex`

高层 policy 仍维持 nominal grasp，但 200 Hz tactile residual 可以在检测到 slip 后直接覆盖：

\[
F_{cmd}
=
F_{base}+\Delta F_{tactile}.
\]

当前 toy 实现将 residual 写成 rescue grip command，重点研究 reaction timing，而不是设计复杂 tactile network。

### `delayed_tactile_reflex`

保留相同 200 Hz 执行频率，但 tactile signal 人为延迟 120 ms。

这是一条关键负对照：

> **高频调用一个 correction function，不等于拥有高频 feedback。**

如果信息本身 stale，200 Hz loop 仍可能来不及阻止 slip。

---

## Paired randomness

三种模式必须经历同一批物理事件。

每个 episode 的：

- slip-event start phase；
- 每个 5 ms step 的 tactile sensor noise；

都只由 `(seed, episode, step)` 决定，而不依赖 control mode。

因此对比不会混入“某个方法刚好抽到更容易的 slip event”。

---

## Metrics

主要指标：

- `drop_rate` / object retention；
- p95 max slip displacement；
- reaction detection rate；
- mean reaction latency；
- slow-event miss rate；
- mean peak grip force；
- extra grip-force energy；
- failure events。

这避免把结果压成一个 success rate。

例如，一个方法可能不掉物，但靠长期过大的 grip force 完成；这与真正快速、局部的 tactile correction 不是同一个机制。

---

## Run

完整实验：

```bash
python labs/runnable/lab14_tactile_reflex/run.py
```

CI / quick experiment：

```bash
python labs/runnable/lab14_tactile_reflex/run.py \
  --quick \
  --output /tmp/lab14
```

派生分析：

```bash
python labs/runnable/lab14_tactile_reflex/analyze.py \
  /tmp/lab14/mode_metrics.csv \
  --output-dir /tmp/lab14
```

输出：

```text
experiment_manifest.json
mode_metrics.csv
analysis.json
ANALYSIS.md
<mode-run>/manifest.json
<mode-run>/steps.csv
<mode-run>/failures.jsonl
<mode-run>/summary.json
```

默认参数：[`config/default.json`](config/default.json)。

---

## Mechanism checks

### Check A — short-event miss

由于：

\[
T_{event}<T_{slow-policy},
\]

`slow_policy_only` 应存在显著 event-miss rate，而不是每次都能及时看到 slip。

### Check B — reaction latency

`fast_tactile_reflex` 的 mean reaction latency 应显著低于 slow policy。

### Check C — physical consequence

更快 reaction 必须传到物理量：p95 slip displacement 和 drop rate 都应下降。

如果只看到“检测更快”，但 slip / retention 不变，不能宣称 tactile feedback 改善了控制。

### Check D — delayed tactile negative control

`delayed_tactile_reflex` 仍以 200 Hz 执行，但输入 stale 120 ms。

若它仍与无延迟 fast reflex 一样好，则“及时 tactile information 是机制关键”这一解释受到直接质疑。

---

## Failure analysis

至少区分：

- **event missed by high-level sampling**；
- **tactile detection latency**；
- **stale tactile data**；
- **actuator response too slow**；
- **insufficient rescue grip**；
- **slip displacement exceeds recovery envelope**；
- **excessive grip / unnecessary control energy**。

真正系统里还要增加：contact localization、sensor saturation、force calibration、material-dependent friction、object damage risk。

---

## What this Lab does not claim

这个 toy experiment 不证明：

- tactile 一定比 vision 更重要；
- 所有 tactile controller 都应是 200 Hz；
- VLA 不应读取 tactile；
- 一个简单 threshold reflex 足以解决真实 dexterous manipulation。

它只验证一个更基础的系统命题：

> **当关键物理事件的时间尺度短于高层 policy cycle 时，把全部 correction 都等待高层模型重新推理会产生可测的闭环损失；一个低延迟 residual feedback path 可以承担不同时间尺度的职责。**

---

## Simulator / real-robot extension

迁移到 Isaac Lab / RoboTwin / 真机时保持同一时间变量：

```text
tactile timestamp
contact/slip event time
policy timestamp
reflex timestamp
controller timestamp
actuator response
object motion
```

并把 toy `slip_signal` 换成真实：

- tactile shear / marker motion；
- force/torque residual；
- contact patch change；
- learned slip probability。

下一层实验应比较：

```text
slow VLA only
vs
VLA + fast tactile residual
vs
VLA + delayed tactile residual
vs
VLA + wrong/shuffled tactile residual
```

从而把“多模态输入”与“多速率闭环”两个问题真正拆开。
