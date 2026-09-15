# Part 44　Datasets、Benchmarks 与 Evaluation Science

## 学习目标

本章目标不是记住 benchmark 名字，而是能够判断一个机器人结果**是否可比较、是否有统计证据、是否被 protocol 污染、是否真的支持论文 claim**。Evaluation 不是论文最后一节，而是定义“什么叫进步”的科学基础设施。

---

## 44.1 Benchmark 为什么会塑造研究方向

研究者优化被测量的东西。

\[
Research\ Direction\approx f(Metric,Benchmark).
\]

如果 benchmark 只测短任务 success，社区就会忽略：

- recovery；
- latency；
- safety；
- long horizon；
- energy。

所以 benchmark design 本身是一种研究议程。

## 44.2 Training Dataset vs Evaluation Benchmark

必须严格分离：

\[
D_{train}\cap D_{test}=\varnothing.
\]

但机器人里“泄漏”不只相同 episode：

- same object instance；
- same scene layout；
- same seed；
- same task template；
- internet video overlap。

Foundation-model 时代还要记录 pretrained model 是否可能见过 benchmark 图片、资产或语言模板。

## 44.3 MetaWorld / robosuite / RLBench

这类经典 benchmark 适合验证：

- multi-task learning；
- manipulation policy；
- imitation/RL algorithm。

它们提供标准化比较，但不能代表完整真实世界。

## 44.4 CALVIN

CALVIN 强调长时序语言条件 manipulation 和 task chaining。

关键评价不是单 task success，而是连续完成多个指令的能力。

## 44.5 LIBERO

LIBERO 侧重 lifelong / transfer / multi-task manipulation。

使用时应关注 task suite 是否和训练策略产生 template-specific bias。

## 44.6 ManiSkill

ManiSkill 提供丰富 simulated manipulation 和统一环境接口。

适合大规模训练与 visual manipulation baseline。

## 44.7 RoboTwin 2.0

双臂平台的价值在于统一复杂 bimanual tasks、data collection 和 policy evaluation。

研究时必须固定 platform commit、asset version、randomization、controller 和 evaluation seed。只写“RoboTwin 2.0 success”不足以重现实验。

## 44.8 Navigation / Habitat Benchmarks

导航常用：

- success；
- SPL；
- path length；
- collision。

但真实移动机器人还应测 dynamic obstacle、localization failure 和 recovery。

## 44.9 Humanoid Benchmarks

humanoid 不能只测 motion tracking reward。

还要报告：

- fall rate；
- energy；
- speed；
- task success；
- terrain robustness；
- manipulation coupling。

## 44.10 Real-World Evaluation

真机评测需要：

- randomization protocol；
- reset procedure；
- human intervention rule；
- failure definition；
- enough trials；
- controller / firmware version；
- camera/calibration state；
- environment recovery procedure。

只有视频精选不是 evaluation protocol。

## 44.11 Task Success Rate

\[
SR=\frac{N_{success}}{N_{trials}}.
\]

简单直观，但丢失 progress 信息。

对长任务，binary success 方差很大。

## 44.12 Bernoulli Uncertainty 与 Confidence Interval

如果每次 trial 是 Bernoulli variable：

\[
X_i\sim Bernoulli(p),\qquad \hat p=\frac1n\sum_iX_i.
\]

标准误差近似为：

\[
SE\approx\sqrt{\frac{\hat p(1-\hat p)}{n}}.
\]

但小样本或 \(\hat p\) 接近 0/1 时，简单 Wald interval 很差。实践中可用 Wilson interval 或 exact/binomial 方法。

这意味着：10 次测试的 7/10 与 8/10 往往远不足以支持“架构显著更强”。

对应最小代码：[`code/minimal/evaluation_stats.py`](../../code/minimal/evaluation_stats.py)。

## 44.13 Partial Credit / Progress Metric

定义 milestones：

\[
P=\frac{\#completed\ milestones}{\#total\ milestones}.
\]

可更细致分析 failure 位于哪一步。

但 milestone 必须在实验前定义，否则容易 post-hoc 调整评价标准。

## 44.14 Robustness

robustness 不是平均 success，而是对 perturbation 的性能变化：

\[
R=\mathbb E_{\delta\sim\Delta}[P(\pi;\delta)].
\]

扰动应覆盖真实 deployment variation。

更有信息的报告方式是画 robustness curve：扰动强度增加时性能怎样退化，而不是只给一个“robust success”。

## 44.15 Generalization Matrix

建立矩阵：

| | seen | novel |
|---|---:|---:|
| object | | |
| scene | | |
| task | | |
| embodiment | | |

不要用一个 “OOD success” 把不同泛化维度混在一起。

## 44.16 Object / Scene / Task / Embodiment OOD

四者难度不同。

### Object OOD

同任务新物体。

### Scene OOD

环境布局变化。

### Task OOD

新目标或组合。

### Embodiment OOD

新身体。

“generalist”至少应说明覆盖哪种。

## 44.17 Perturbation Test

执行中主动扰动：

- 移动物体；
- 推机器人手；
- 遮挡相机；
- 改变目标；
- 插入新障碍。

这比静态 OOD 更能测试 closed-loop capability。

扰动测试还应记录 disturbance onset 相对 policy cycle 的时刻，否则不同系统可能拥有不同反应时间预算。

## 44.18 Long-Horizon Evaluation

记录：

\[
P(success\ at\ horizon\ H).
\]

随着 H 增长画 curve。

可以识别 memory、recovery、cumulative error 问题。

若单个 subtask 独立成功率近似 \(p\)，简单串联 \(H\) 次的成功概率已可能近似 \(p^H\)。长时任务的下降不能自动归因 memory failure，需要拆分 error accumulation、state estimation 与 recovery。

## 44.19 Intervention Rate

\[
IR=\frac{N_{human\ interventions}}{hours\ of\ operation}.
\]

对真实部署，比 success rate 更接近运维成本。

但必须预先定义什么算 intervention：急停、人工重置、口头澄清、重新抓取是否都计入？

## 44.20 Recovery Rate

\[
RR=P(recover\mid failure\ detected).
\]

一个会出错但能恢复的系统，可能比“平时成功率略高但一错就停”更实用。

还应分开：

\[
P(detect\ failure),\qquad P(recover\mid detected).
\]

否则高 recovery rate 可能只是只统计了容易检测的 failure。

## 44.21 Latency / Throughput / Energy

机器人能力必须在物理时间里评价。

报告：

- model inference latency；
- end-to-end observation-to-command latency；
- P50/P95/P99 cycle time；
- tasks/hour；
- Wh/task；
- GPU power；
- dropped/stale action rate。

一个离线分数更高但实时周期更慢的模型，闭环表现可能反而更差。

## 44.22 Calibration / Uncertainty

如果模型预测 success probability \(p\)，应测试：

\[
P(success\mid \hat p=p)\approx p.
\]

可靠 uncertainty 是安全 stop 和 human handoff 的基础。

除了 ECE，还应画 reliability diagram，并检查 OOD 下 calibration 是否崩溃。

## 44.23 Benchmark Leakage

泄漏检查：

- dataset hash；
- object identity；
- scene asset；
- task instruction；
- pretrained web source。

foundation model 时代，完全排除 web overlap 很难，所以应公开已知可能性，而不是把“不知道是否见过”写成“zero-shot”。

## 44.24 Paired Evaluation 与 Seed Control

若两个 policy 在相同初始条件上评测，应尽量 paired：

```text
same task
same object pose
same scene randomization
same simulator seed / real reset protocol
A policy and B policy evaluated separately
```

这样比较的是**同一难度 realization** 下的差异，而不是两个随机任务集的差异。

真机无法完全复现初始状态时，应记录可测 confounders，并随机化 evaluation order，避免温度、光照、设备磨损与模型版本共变。

## 44.25 多 Seed 不等于大量独立样本

训练 seed、environment seed、episode trial 是不同层级的随机变量。

例如：

```text
3 training seeds × 50 eval episodes
```

不能简单当作 150 个完全独立的 architecture samples。应分层报告：每个 seed 的结果、seed-to-seed variation、episode-level interval。

## 44.26 Model × Data × System × Protocol

一个真实结果应展开为：

\[
E=f(M,D,H,C,B,P),
\]

其中：

- \(M\)：model / checkpoint；
- \(D\)：training data；
- \(H\)：hardware / embodiment；
- \(C\)：controller / executor；
- \(B\)：benchmark / task distribution；
- \(P\)：evaluation protocol。

只有其中大部分被固定，才能把 \(\Delta E\) 归因到某个 architecture change。

本书因此维护 [`MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md`](../../references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md)，拒绝把不同实验系统的数字机械放进同一 leaderboard。

## 44.27 “成功视频”为什么不是科学证据

公开视频往往存在 selection bias：

\[
P(video\ shown\mid success)\gg P(video\ shown\mid failure).
\]

科学证据需要：

- denominator；
- protocol；
- all-trial stats；
- failure examples；
- baseline。

## 44.28 Evaluation Dataflow

一个出版级 evaluation pipeline 应显式化：

```text
benchmark version / assets
+ task split / seed list
+ robot + controller + calibration
+ policy checkpoint + normalization
              ↓
pre-registered reset / intervention / timeout rules
              ↓
ALL trials + timestamps + raw logs
              ↓
per-trial success / progress / latency / safety / failures
              ↓
confidence intervals + paired comparisons + slices
              ↓
claim table: what evidence supports / does not support
```

如果论文只能保留一个 evaluation artifact，优先保留**逐 trial raw table**，而不是漂亮的 aggregate bar chart。

## 常见失败

### 改模型时同时改 controller

success 提升无法归因 architecture。

### 只报最佳 seed

这是隐式 selection bias；至少应提前定义 model selection protocol。

### Reset procedure 不一致

某方法在失败后获得更有利的人工摆放，可能产生比模型改进更大的效果。

### Benchmark version 漂移

asset、physics、task script、success detector 更新后，旧结果不一定可直接比较。

### 把 simulator success 外推真机

sim benchmark 能隔离 algorithm variable，但不能自动证明 calibration/contact/hardware robustness。

### 用平均数掩盖 failure slice

总体 success 相同的两个系统，可能一个在遮挡下全失败、一个在小物体上全失败。failure taxonomy 比一个 scalar 更能指导研究。

## 最小实验

用 [`code/minimal/evaluation_stats.py`](../../code/minimal/evaluation_stats.py) 做三组模拟：

1. 比较 7/10 vs 8/10、70/100 vs 80/100 的 Wilson interval；
2. 构造两个 overall success 相同但 OOD slice 完全不同的 policy；
3. 构造 paired 与 unpaired task difficulty，比较同一模型差异的统计方差。

再从你自己的 simulator benchmark 导出逐 trial CSV，必须包含：

```text
policy_commit, seed, task, object, scene, reset_id,
success, progress, latency_ms, intervention, failure_type
```

## 研究问题

1. General-purpose robot 是否需要类似“evaluation vector”而非单一 leaderboard score？
2. Foundation model 无法完全排除互联网预训练泄漏时，zero-shot 应怎样重新定义？
3. 如何设计 benchmark，使 recovery、information gathering 与 long-horizon capability 不被短任务 success 掩盖？
4. 真机 benchmark 怎样在可重复性与真实环境多样性之间取平衡？
5. 是否可以把 controller/executor 规范化成标准接口，使 VLA architecture comparison 更接近真正 controlled experiment？
6. 当 real-world trial 极昂贵时，怎样用 sequential testing / Bayesian estimation 获得足够证据而不浪费机器人时间？

## Source anchors / 原始来源

- Wilson, “Probable Inference, the Law of Succession, and Statistical Inference,” JASA 1927: https://doi.org/10.1080/01621459.1927.10502953
- Agarwal et al., “Deep Reinforcement Learning at the Edge of the Statistical Precipice,” NeurIPS 2021: https://arxiv.org/abs/2108.13264
- Guo et al., “On Calibration of Modern Neural Networks,” ICML 2017: https://arxiv.org/abs/1706.04599
- CALVIN official repository: https://github.com/mees/calvin
- LIBERO official project: https://libero-project.github.io/
- Habitat: https://aihabitat.org/
- RoboTwin official repository: https://github.com/RoboTwin-Platform/RoboTwin
- 本书 Benchmark / Protocol 索引：[`references/BENCHMARK_ATLAS.md`](../../references/BENCHMARK_ATLAS.md) 与 [`labs/EXPERIMENT_PROTOCOL.md`](../../labs/EXPERIMENT_PROTOCOL.md)。

## 一个推荐的统一评测向量

\[
E=(SR,Progress,OOD,Robustness,RR,IR,Latency,Energy,Safety).
\]

没有单一 scalar 可以完整代表 general-purpose robot capability。

## 本章结论

Evaluation science 的核心不是“多报几个 metric”，而是控制实验系统、公开 protocol、量化不确定性、保存 denominator 与 failure slices，并明确数字究竟支持多强的 claim。机器人领域如果不能把 model、data、controller、hardware、benchmark 和 protocol 分开，就很容易把系统工程差异误写成架构突破。
