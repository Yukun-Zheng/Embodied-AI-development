# Part 44　Datasets、Benchmarks 与 Evaluation Science

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

---

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

---

## 44.3 MetaWorld / robosuite / RLBench

这类经典 benchmark 适合验证：

- multi-task learning；
- manipulation policy；
- imitation/RL algorithm。

它们提供标准化比较，但不能代表完整真实世界。

---

## 44.4 CALVIN

CALVIN 强调长时序语言条件 manipulation 和 task chaining。

关键评价不是单 task success，而是连续完成多个指令的能力。

---

## 44.5 LIBERO

LIBERO 侧重 lifelong / transfer / multi-task manipulation。

使用时应关注 task suite 是否和训练策略产生 template-specific bias。

---

## 44.6 ManiSkill

ManiSkill 提供丰富 simulated manipulation 和统一环境接口。

适合大规模训练与 visual manipulation baseline。

---

## 44.7 RoboTwin 2.0

双臂平台的价值在于统一复杂 bimanual tasks、data collection 和 policy evaluation。

研究时必须固定 platform version、asset、randomization 和 evaluation seed。

---

## 44.8 Navigation / Habitat Benchmarks

导航常用：

- success；
- SPL；
- path length；
- collision。

但真实移动机器人还应测 dynamic obstacle、localization failure 和 recovery。

---

## 44.9 Humanoid Benchmarks

humanoid 不能只测 motion tracking reward。

还要报告：

- fall rate；
- energy；
- speed；
- task success；
- terrain robustness；
- manipulation coupling。

---

## 44.10 Real-World Evaluation

真机评测需要：

- randomization protocol；
- reset procedure；
- human intervention rule；
- failure definition；
- enough trials。

只有视频精选不是 evaluation protocol。

---

## 44.11 Task Success Rate

\[
SR=\frac{N_{success}}{N_{trials}}.
\]

简单直观，但丢失 progress 信息。

对长任务，binary success 方差很大。

---

## 44.12 Partial Credit / Progress Metric

定义 milestones：

\[
P=\frac{\#completed\ milestones}{\#total\ milestones}.
\]

可更细致分析 failure 位于哪一步。

---

## 44.13 Robustness

robustness 不是平均 success，而是对 perturbation 的性能变化：

\[
R=\mathbb E_{\delta\sim\Delta}[P(\pi;\delta)].
\]

扰动应覆盖真实 deployment variation。

---

## 44.14 Generalization Matrix

建立矩阵：

| | seen | novel |
|---|---:|---:|
| object | | |
| scene | | |
| task | | |
| embodiment | | |

不要用一个 “OOD success” 把不同泛化维度混在一起。

---

## 44.15 Object / Scene / Task / Embodiment OOD

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

---

## 44.16 Perturbation Test

执行中主动扰动：

- 移动物体；
- 推机器人手；
- 遮挡相机；
- 改变目标；
- 插入新障碍。

这比静态 OOD 更能测试 closed-loop capability。

---

## 44.17 Long-Horizon Evaluation

记录：

\[
P(success\ at\ horizon\ H).
\]

随着 H 增长画 curve。

可以识别 memory、recovery、cumulative error 问题。

---

## 44.18 Intervention Rate

\[
IR=\frac{N_{human\ interventions}}{hours\ of\ operation}.
\]

对真实部署，比 success rate 更接近运维成本。

---

## 44.19 Recovery Rate

\[
RR=P(recover\mid failure\ detected).
\]

一个会出错但能恢复的系统，可能比“平时成功率略高但一错就停”更实用。

---

## 44.20 Latency / Throughput / Energy

机器人能力必须在物理时间里评价。

报告：

- inference latency；
- cycle time；
- tasks/hour；
- Wh/task；
- GPU power。

---

## 44.21 Calibration / Uncertainty

如果模型预测 success probability \(p\)，应测试：

\[
P(success\mid \hat p=p)\approx p.
\]

可靠 uncertainty 是安全 stop 和 human handoff 的基础。

---

## 44.22 Benchmark Leakage

泄漏检查：

- dataset hash；
- object identity；
- scene asset；
- task instruction；
- pretrained web source。

foundation model 时代，完全排除 web overlap 很难，所以应公开已知可能性。

---

## 44.23 Statistical Significance

二项 success rate 的标准误差：

\[
SE=\sqrt{\frac{p(1-p)}{n}}.
\]

10 次测试从 7/10 到 8/10 通常不足以证明架构突破。

应报告 confidence interval、多 seeds/episodes。

---

## 44.24 “成功视频”为什么不是科学证据

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

---

## 一个推荐的统一评测向量

\[
E=(SR,Progress,OOD,Robustness,RR,IR,Latency,Energy,Safety).
\]

没有单一 scalar 可以完整代表 general-purpose robot capability。

---

## 本章结论

Evaluation 不是论文最后一节，而是定义“什么叫进步”的科学基础。具身智能尤其需要从精选 demo 和单一 success rate 转向多维、带不确定性、可复现的 evaluation science。