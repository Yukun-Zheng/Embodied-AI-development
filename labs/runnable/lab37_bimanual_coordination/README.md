# Lab 37 — Bimanual Coordination

> **Question:** 两个单臂 controller 都能到达各自 world-frame target，是否就足以说明系统完成了双臂协调？

这个 runnable Lab 把“双臂协调”压缩成一个可证伪的 shared-object mechanism test。两个 1-D end-effector 同时抓住一个有顺应性的物体；物体中心需要沿轨迹移动，而两端间距必须保持在 nominal grasp width 附近。

每个 paired episode 都固定：

- 左右臂不同的 actuator gain；
- 同一 target center；
- 左臂同一段短时 unilateral disturbance；
- 同一 spring–damper shared-object dynamics。

唯一改变的是 controller 如何组织同一批状态。

## 机制链

```text
left / right endpoint state
        ↓
world-frame independent control
        or
midpoint + relative coordinates
        ↓
left / right effort
        ↓
actuator asymmetry + unilateral disturbance
        ↓
shared compliant object
        ↓
center tracking + separation error + internal force
        ↓
physical bimanual success / failure
```

核心 distinction 是：

\[
 c = \frac{x_L + x_R}{2},
 \qquad
 r = x_R - x_L,
\]

其中 `c` 是 object midpoint，`r` 是双臂相对间距。只把 `c` 跟好并不保证 `r` 正确。

共享物体用最小 spring–damper coupling：

\[
F_{int}=k(r-r_0)+b(\dot x_R-\dot x_L),
\]

并把该 internal force 反向作用到两臂。实验因此评估的不是 Boolean “coordination enabled”，而是有限动力学后的 strain 与 internal load。

## Conditions

### `independent_world`

两臂分别跟踪

\[
x_L^*=c^*-r_0/2,
\qquad
x_R^*=c^*+r_0/2,
\]

但控制律没有 cross-arm relative feedback。

它可以最终到达正确 endpoints，却会在 actuator mismatch 和 unilateral disturbance 下产生 transient shared-object strain。

### `midpoint_only`

只反馈 object midpoint：

\[
u_L=u_R=u_c.
\]

这是一个重要负对照：**center RMSE 可以很好，但 relative state 仍然很差。**

因此“物体中心到了”不能被当作“双臂协调成功”的充分证据。

### `relative_coordinated`

控制律拆成 common mode 与 differential mode：

\[
u_c=K_c(c^*-c)+D_c(\dot c^*-\dot c),
\]

\[
u_r=K_r(r_0-r)-D_r\dot r,
\]

\[
u_L=u_c-\frac{1}{2}u_r,
\qquad
u_R=u_c+\frac{1}{2}u_r.
\]

这让 controller 能在不牺牲 object-center tracking 的前提下主动抑制 relative deformation。

### `wrong_relative_sign`

保留相同 observation、相同 relative term、相同 effort limit，只把 differential correction 的符号反过来。

它测试的不是“多一个 controller branch 是否有用”，而是**正确的相对坐标结构是否因果必要**。

## Paired perturbations

每个 episode 对四个 condition 完全复用同一组：

```text
left actuator gain
right actuator gain
target center
left-arm disturbance magnitude
```

因此 condition difference 不来自重新采样一批更容易的任务。

## Metrics

实验至少报告：

- `success_rate`；
- `mean_center_rmse`；
- `mean_relative_rmse`；
- `mean_peak_abs_strain`；
- `p95_peak_abs_strain`；
- `mean_p95_internal_force`；
- final center / separation error；
- mean total control effort。

成功条件同时要求：

```text
final center reaches target
+ final separation returns near nominal
+ transient peak strain never crosses the shared-object limit
```

所以一个 controller 即使最后两个 endpoint 都“到位”，只要过程中把共享物体拉伸过限，也不能算成功。

## Quick reference expectation

CI 的 deterministic quick configuration 使用 **120 paired episodes**。设计目标不是给出真实机器人性能，而是得到稳定的机制排序：

```text
relative_coordinated
    >> independent_world
    >> midpoint_only
    >> wrong_relative_sign
```

并额外要求：

```text
relative feedback reduces relative RMSE
relative feedback reduces peak strain
relative feedback reduces internal force
center tracking is not traded away
midpoint-only can have good center RMSE but poor shared-object success
wrong relative sign produces a strong negative control
coordination gain is not explained by a much larger effort budget
```

## Run

```bash
python labs/runnable/lab37_bimanual_coordination/run.py \
  --quick \
  --output /tmp/lab37

python labs/runnable/lab37_bimanual_coordination/analyze.py \
  /tmp/lab37/condition_metrics.csv \
  --output-dir /tmp/lab37
```

CI regression:

```bash
python labs/runnable/lab37_bimanual_coordination/smoke.py
```

## Outputs

```text
/tmp/lab37/
├── trial_specs.csv
├── episode_metrics.csv
├── condition_metrics.csv
├── experiment_summary.json
├── analysis.json
├── ANALYSIS.md
└── runs/
    └── <condition-run>/
        ├── manifest.json
        ├── steps.csv
        ├── failures.jsonl
        └── summary.json
```

`steps.csv` 保存 midpoint、relative separation、strain、internal force、左右 effort、actuator gain 与 disturbance；因此 aggregate result 可以从 raw trajectory 重新审计。

## Scientific scope

这个 Lab 只支持一个窄结论：

> 在这个 paired compliant shared-object mechanism test 中，显式 relative-coordinate feedback 能在 actuator heterogeneity 与 unilateral disturbance 下显著降低双臂相对误差、shared-object strain 和 internal force；仅有独立 world-frame endpoint tracking 或 midpoint tracking 不足以证明 bimanual coordination。

它**不**声称解决真实双臂 manipulation。真实系统还需要 SE(3) relative pose、contact wrench、grasp geometry、force/impedance control、object inertia、collision、vision/tactile latency、controller saturation 与 safety boundary。这个 M 层实验的作用是先把“相对坐标 feedback 是否因果必要”做成可重复 falsification target。
