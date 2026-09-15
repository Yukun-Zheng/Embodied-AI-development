# Part 50　从学习者到独立研究者

## 50.1 第一阶段：数学与经典机器人学底座

必须真正掌握：

- linear algebra；
- probability；
- optimization；
- SO(3)/SE(3)；
- FK/IK/Jacobian；
- dynamics；
- feedback control。

目标不是考试，而是看到论文里的 \(T,J,M(q),\tau\) 就知道物理对象是什么。

### 验收

从零手写：

- 6-DoF FK；
- numerical IK；
- Jacobian；
- impedance controller。

---

## 50.2 第二阶段：亲手实现 Perception / Planning / Control

做一个小机械臂完整闭环：

```text
RGB-D
→ object pose
→ target pose
→ planner / IK
→ controller
→ manipulation
```

这一步让你知道“一个神经网络模块”在机器人系统里到底接在哪。

---

## 50.3 第三阶段：Imitation / RL / Generative Policy

顺序建议：

```text
BC
→ DAgger
→ PPO/SAC
→ ACT
→ Diffusion Policy
→ Flow/AR action
```

同一 toy task 上对比，而不是每种算法换一个 benchmark。

这样能真正建立方法差异直觉。

---

## 50.4 第四阶段：复现主流 VLA

复现目标不是“下载 checkpoint 跑 demo”。

至少做到：

1. 读数据 loader；
2. 追 observation tensor；
3. 看 backbone 与 action head；
4. 跑 train/fine-tune；
5. 测 latency；
6. 做一个结构性 ablation。

---

## 50.5 第五阶段：拆 Failure Mechanism

开始停止追 leaderboard。

为一个模型建立 failure database：

```text
semantic
geometry
contact
latency
recovery
OOD
```

选择占比最高、机制最不清楚的一类作为研究入口。

---

## 50.6 第六阶段：进入真正前沿

按问题而非模型选择：

- world model；
- embodied memory；
- active perception；
- tactile；
- humanoid；
- cross-embodiment；
- continual learning。

每个方向都先问：

> 它解决闭环中的哪一个基本缺陷？

---

## 50.7 第七阶段：Architecture Research Program

不要只有一个“idea”。

建立长期 program：

```text
Grand Question
├── Hypothesis A
│   ├── falsification test
│   └── minimal experiment
├── Hypothesis B
└── Hypothesis C
```

每轮：

1. 发散；
2. 攻击；
3. 思想实验；
4. 最小实验；
5. 综合修订。

失败的 hypothesis 也积累知识。

---

## 50.8 从“追论文”转向“追问题”

初学者看到：

> 新论文用了什么模块？

研究者看到：

> 为什么这个 failure 十篇论文都没有解决？

建立问题表：

```text
problem
current assumptions
known solutions
known failures
missing experiment
```

新论文只是更新表格的证据。

---

## 50.9 如何形成持续科研飞轮

理想状态：

```text
一篇在投
一篇在写
一篇在实验
一篇在调研
一组 idea 在筛选
基础知识持续补
```

但关键不是并行数量，而是阶段错开。

### Research Pipeline

```text
Question Bank
→ Literature / Reproduction
→ Minimal Experiment
→ Main Experiment
→ Writing
→ Submission
→ Failure / Review feedback
→ Question Bank
```

---

## 50.10 如何提出一个值得做三年的问题

好长期问题通常满足：

### 1. Fundamental

不是某 benchmark 的局部 bug。

### 2. Repeatedly observable

在很多系统里反复出现。

### 3. Falsifiable

能设计实验证明你的核心观点错。

### 4. Scalable

小实验可以验证机制，大实验可以扩大影响。

### 5. Generative

一个答案会自然产生下一批问题。

例如：

> “机器人如何从持续物理交互中形成可跨任务、跨场景、跨本体复用的机制，而不是只拟合动作分布？”

它可以继续拆成 representation、memory、world model、structure、learning rule 多条线。

---

# 一套完整学习路线

## Year / Stage A：基础

读数学、Modern Robotics、control；实现 toy system。

## Stage B：Robot Learning

同平台跑 BC/RL/ACT/Diffusion。

## Stage C：Foundation Models

复现至少一个开放 VLA，并深入源码。

## Stage D：Mechanism Research

不再以“换模块”为主，开始设计 intervention/negative control。

## Stage E：Independent Program

围绕一个 fundamental question 连续做多篇互相关联工作。

---

# 最终自测

如果你能回答下面的问题，才算真正进入独立研究阶段：

1. 你的模型 observation 到底包含什么？
2. action 最终控制什么硬件量？
3. 你的提升来自数据还是架构？
4. 哪个负对照最可能推翻你的解释？
5. 为什么 benchmark improvement 对真实机器人有意义？
6. failure distribution 是什么？
7. 你的方法在新 embodiment 上会怎样？
8. 如果 Transformer 拿掉，你真正需要保留的机制是什么？
9. 这个问题三年后还存在吗？
10. 什么实验结果会让你放弃当前方向？

如果第 10 个问题没有答案，你的研究计划还不是可证伪的。

---

## 全书结束语

具身智能最终研究的不是“如何让一个模型输出漂亮的动作序列”，而是：

> **一个有限计算资源的实体，如何依靠自己的身体，在部分可观测、持续变化、充满接触与不确定性的物理世界中，通过长期交互形成关于世界和自身的可迁移规律，并据此安全地行动、学习、记忆、修正和成长。**

数学给它结构，物理给它约束，身体给它接口，感知给它证据，控制给它稳定闭环，学习给它适应，记忆给它时间连续性，世界模型给它反事实，实验科学告诉我们它是否真的学会了。

这也是本书从第一章到最后一章唯一不变的问题。
<!-- CHAPTER-ENRICHMENT-R2-P50:START -->
## 50.18 独立研究的最小闭环

研究成长可以抽象成一个反复收缩 uncertainty 的闭环。设候选机制集合为 \(\mathcal H_t\)，每次实验 \(e_t\) 产生证据 \(D_t\)：

\[
\mathcal H_{t+1}=\operatorname{Update}(\mathcal H_t,D_t,e_t).
\]

好的研究不是让 hypothesis 数量无限增加，而是主动选择最有区分力的实验：

\[
e_t^*=\arg\max_e I(H;D\mid e)-\lambda C(e),
\]

其中 \(C(e)\) 是时间、算力、真机风险与机会成本。

因此个人科研飞轮也应是：

```text
read / reproduce
→ identify unresolved mechanism
→ write falsifiable hypotheses
→ choose minimal discriminating experiment
→ inspect failures, not only averages
→ update theory
→ scale only after mechanism survives
```

这比“连续追最新论文 + 堆更多实验”更接近独立研究者的工作方式。

## 50.19 研究问题

1. 怎样判断一个 idea 已经具体到可以被证伪，而不是一句愿景？
2. 什么时候应该复现 baseline，什么时候应该直接构造最小机制实验？
3. 如何把 negative result 变成对 hypothesis space 的有效收缩，而不是“实验没跑通”？
4. 一篇论文的核心贡献应优先是新指标、新数据、新系统、新机制还是新理论；不同类型需要什么证据？
5. 如何建立自己的 Architecture Research Program，使连续多篇工作共享可累积的问题树，而不是每篇追一个热点？
6. 当计算资源足够大时，如何防止“能跑很多实验”反而降低实验设计质量？
<!-- CHAPTER-ENRICHMENT-R2-P50:END -->
<!-- CHAPTER-ENRICHMENT-R3-P50:START -->
## 50.20 最小实验：从一条 Failure Note 生成研究项目

任选一次真实/仿真失败，强制只用 1–2 天预算完成：

```text
1. raw failure replay
2. root-cause candidate tree
3. two competing hypotheses H1/H2
4. one discriminating intervention
5. minimal implementation
6. all-trial result + failure slice
7. update hypothesis tree
```

例如“VLA 抓取遮挡物失败”不要直接改网络，而先比较：

```text
H1: representation 看不到目标几何
H2: representation 足够，但 policy 没有主动换视角
```

用 oracle view / oracle geometry 与 active-view intervention 就能比“训练一个更大 VLA”更快区分机制。独立研究能力首先体现在**选择正确实验**，而不是把所有可能性都并行 brute-force。
<!-- CHAPTER-ENRICHMENT-R3-P50:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 50`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-50)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
