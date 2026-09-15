# Part 46　如何做严谨的具身智能研究

## 46.1 怎样读一篇具身论文

不要从 abstract 的“提升了多少”开始，而先回答：

1. robot / embodiment 是什么？
2. observation 是什么？
3. action 是什么？
4. low-level controller 是什么？
5. train data 从哪里来？
6. evaluation distribution 是什么？
7. baseline 是否同等数据/算力？

只有这些回答清楚，结果数字才有意义。

---

## 46.2 怎样画完整 System Diagram

强制把论文画成：

```text
physical world
→ sensor
→ preprocessing
→ representation
→ state/memory
→ policy/planner
→ action representation
→ controller
→ actuator
→ physical world
```

每条箭头标：

- tensor shape；
- frequency；
- coordinate frame；
- trainable/frozen；
- source of supervision。

如果画不出来，说明论文还没真正读懂。

---

## 46.3 Observation → Representation → Action

研究机制时不要只看 architecture block。

追踪一个真实样本：

\[
I\in\mathbb R^{B\times T\times C\times H\times W}
\]

经过 encoder 后：

\[
z\in\mathbb R^{B\times N\times d},
\]

再进入 action head：

\[
A\in\mathbb R^{B\times H_a\times d_a}.
\]

逐层问“哪个维度对应什么物理量”。

---

## 46.4 复现论文而不只是跑通代码

复现至少分四级：

### L0：代码运行

没有报错。

### L1：指标复现

得到接近论文数字。

### L2：机制复现

关键 ablation 和 failure pattern 一致。

### L3：外推复现

换任务/场景后仍能验证作者机制解释。

真正科研价值从 L2 开始。

---

## 46.5 怎样设计 Baseline

baseline 必须回答：

> 如果不使用你的核心创新，最强合理替代是什么？

不要故意选弱 baseline。

应尽量匹配：

- data；
- backbone；
- parameter count；
- training steps；
- augmentation；
- evaluation protocol。

---

## 46.6 怎样设计 Ablation

ablation 不是“删模块然后分数下降”。

真正要验证因果链：

\[
Mechanism\rightarrow Intermediate\ Variable\rightarrow Performance.
\]

例如声称 active perception 有用：

1. 它是否真的改变 viewpoint？
2. uncertainty 是否下降？
3. task success 是否因此提升？

三层都要测。

---

## 46.7 怎样构造 Negative Control

负对照能击穿“看起来合理的解释”。

例：

### World model

换成 shuffled predictor。

### Memory

检索随机 episode。

### Reasoning

注入错误 plan。

### Geometry module

随机旋转 frame。

如果性能不变，说明模块可能没被使用。

---

## 46.8 怎样控制 Data Gain

架构论文最常见混淆：新方法同时用了更多数据。

至少比较：

\[
Method_{new}(D)
\quad vs\quad
Baseline(D)
\]

而不是：

\[
Method_{new}(10D)
\quad vs\quad
Baseline(D).
\]

---

## 46.9 Architecture Gain vs Data Gain

建议 factorial design：

| | old data | new data |
|---|---:|---:|
| old arch | A | B |
| new arch | C | D |

则：

- data gain \(\approx B-A\)；
- architecture gain \(\approx C-A\)；
- interaction \(\approx D-C-B+A\)。

这比只报 D vs A 强得多。

---

## 46.10 可证伪 Hypothesis

坏假说：

> “我们的模块让模型更理解物理。”

好假说：

> “在视觉外观不变、摩擦系数改变的 intervention 下，加入 contact-aware latent dynamics 的模型成功率下降幅度显著小于视觉-only baseline。”

好假说必须指定：

- intervention；
- metric；
- baseline；
- failure condition。

---

## 46.11 Failure Taxonomy

研究前先定义 failure categories。

例如 VLA：

```text
semantic
grounding
geometry
planning
action generation
latency
contact
controller
recovery
```

然后统计每类比例。

总体 success 提升 5% 只有知道哪类失败减少，才产生机制知识。

---

## 46.12 Mechanism Analysis

Mechanism study 常用工具：

- representation probe；
- activation intervention；
- input counterfactual；
- causal ablation；
- feature visualization；
- controlled simulation。

目标不是“解释网络每个神经元”，而是回答研究假说中的中间机制是否存在。

---

## 46.13 统计可信度

报告：

- trials；
- seeds；
- confidence interval；
- effect size。

真实机器人 trial 贵，但这不是只测 5 次的充分理由。

可以通过分层实验：先大量 sim，再关键真机确认。

---

## 46.14 防 Benchmark Overfitting

研究过程反复看 test set，会形成隐式 overfit。

建议：

- public validation；
- hidden test；
- held-out embodiment；
- final frozen protocol。

---

## 46.15 如何报告真实机器人实验

至少报告：

- robot model；
- controller；
- camera/sensors；
- policy frequency；
- action representation；
- number of trials；
- reset protocol；
- human intervention；
- failure cases；
- hardware/software version。

---

## 46.16 从 Failure Mode 产生问题

科研飞轮：

```text
reproduce
→ cluster failures
→ choose dominant unexplained failure
→ hypothesize mechanism
→ design minimal intervention
→ test
→ generalize
```

这比先想一个漂亮模块再找 benchmark 更可靠。

---

## 46.17 判断 VLA 是否真的 Generalize

需要 decomposition：

- novel object；
- novel scene；
- novel task composition；
- novel embodiment。

同时检查 data overlap。

对 compositional generalization 做 component-held-out 设计，而不是只换 instruction wording。

---

## 46.18 判断 World Model 是否被 Policy 利用

负对照：

- correct world model；
- frozen random world model；
- shuffled future；
- wrong dynamics。

若 policy 性能差不多，world model 可能只是装饰。

---

## 46.19 判断视觉表征是否服务物理交互

不要只做 linear probe classification。

要测：

- pose perturbation；
- contact prediction；
- depth sensitivity；
- action-conditioned success；
- geometry OOD。

---

## 46.20 判断 Reasoning 是否只是语言包装

干预 reasoning channel：

- remove；
- random；
- wrong；
- correct。

如果 motor behavior 不受影响，“reasoning”可能只是 post-hoc narration。

---

## 一页 Research Protocol

每个项目开始前写：

```text
Question:
Hypothesis:
Mechanism:
Minimal experiment:
Positive control:
Negative control:
Primary metric:
Failure criterion:
Scale-up condition:
```

如果这页写不清，不应该直接训练大模型。

---

## 本章结论

严谨具身研究的核心不是模型复杂，而是**控制变量、可证伪假说、机制中间量、负对照和真实 failure analysis**。大规模算力应该放在已经通过最小实验的问题上，而不是替代思考。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 46`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-46)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
