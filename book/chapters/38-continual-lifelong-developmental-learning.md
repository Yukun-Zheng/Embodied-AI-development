# Part 38　Continual、Lifelong 与 Developmental Robot Learning

## 38.1 Continual Learning

连续任务序列：

\[
\mathcal T_1,\mathcal T_2,\dots,\mathcal T_n.
\]

目标不是最后任务最好，而是整体能力保持：

\[
P_{i,j}=performance\ on\ T_i\ after\ learning\ T_j.
\]

由此可以定义 forgetting 和 forward transfer。

---

## 38.2 Catastrophic Forgetting

学习新任务后旧任务下降：

\[
F_i=\max_{j<i}P_{i,j}-P_{i,n}.
\]

机器人比图像分类更严重，因为任务分布、环境和 embodiment 会连续改变。

---

## 38.3 Replay

保存旧 experience：

\[
D_{train}=D_{new}\cup D_{replay}.
\]

优点直接；缺点：

- storage；
- privacy；
- sampling；
- long-term scaling。

不可能永久均匀重放所有过去数据。

---

## 38.4 Regularization

限制重要参数变化：

\[
\mathcal L=\mathcal L_{new}+\lambda\sum_i\Omega_i(\theta_i-\theta_i^{old})^2.
\]

它假设旧能力可以通过参数重要性局部保护。

对巨大 foundation model，这种方法可能过于粗糙。

---

## 38.5 Parameter Isolation

为新任务新增：

- adapter；
- expert；
- LoRA；
- module。

优点是少覆盖旧知识；缺点是模型不断膨胀。

如果每个新场景都加一个模块，最终不是通用智能，而是模块仓库。

---

## 38.6 Modular Network

更好的模块化不是“每任务一个头”，而是让模块对应可复用机制：

- perception primitive；
- contact skill；
- dynamics expert；
- memory；
- planner。

新任务组合已有模块，只有真正新机制才增长。

---

## 38.7 Dynamic Architecture

网络结构可以随经验变化：

\[
G_{t+1}=Update(G_t,experience_t).
\]

操作包括：

- add node/module；
- merge；
- prune；
- reroute。

但结构变化必须有明确 objective，否则只是 architecture search。

---

## 38.8 Online Adaptation

在线适应分三个尺度：

### state adaptation

更新 belief，不改参数。

### fast parameter adaptation

小 adapter / latent 更新。

### structural/long-term learning

模型本身改变。

很多“在线学习”其实只是第一种，需要区分。

---

## 38.9 Lifelong Robot Learning

Lifelong 目标是：

\[
\max \sum_t performance_t
\]

subject to finite compute, memory, safety。

这引入资源分配问题：机器人不能无限存储和无限训练。

---

## 38.10 Developmental Robotics

Developmental robotics 更强调：

- 从身体交互开始；
- 能力逐渐形成；
- perception/action 共发展；
- curriculum 不完全预定义。

它与“先大规模预训练，再部署”形成不同研究视角。

---

## 38.11 Intrinsic Motivation

没有外部任务时，agent 可以奖励新颖性或学习进展：

\[
r_t^{int}=f(novelty,prediction\ error,learning\ progress).
\]

但单纯 novelty 会让机器人沉迷噪声。

更合理的是可学习结构的进展。

---

## 38.12 Curiosity

经典 curiosity 使用 prediction error：

\[
r_t^{cur}=\|\hat s_{t+1}-s_{t+1}\|^2.
\]

问题：随机不可预测现象也给高奖励。

所以需要区分 epistemic uncertainty 与 irreducible noise。

---

## 38.13 Self-Supervised Skill Discovery

agent 在无明确任务标签下学习技能 latent \(z\)：

\[
\pi(a\mid s,z).
\]

希望不同 \(z\) 产生可区分 state visitation。

对机器人意义在于先形成 primitive repertoire，再组合成任务。

---

## 38.14 Open-Ended Learning

open-ended 不设固定最终 task set。

系统需要不断产生：

- 新目标；
- 新环境；
- 新挑战；
- 新能力。

衡量难点：没有单一 benchmark 能定义“进步”。

---

## 38.15 Memory Formation / Consolidation / Forgetting

长期学习需要把 experience 分层：

```text
raw episode
→ important event
→ consolidated knowledge
→ parameter / semantic memory
```

这比“全部 replay”更接近可扩展系统。

---

## 38.16 Structural Plasticity

结构可塑性真正问题是：

> 什么证据足以让系统改变自身计算结构？

可能基于：

- persistent prediction error；
- new causal factor；
- repeated interference；
- capacity saturation。

结构变化必须可回滚和验证。

---

## 38.17 Network Growth / Pruning 的局限

简单：

```text
loss high → add neurons
unused → prune
```

不是完整发展型学习。

因为它没有定义：

- 新结构语义；
- 模块复用；
- skill composition；
- memory interaction。

---

## 38.18 不区分“训练/推理”的持续交互系统

更激进的范式：

机器人始终处于：

\[
observe\rightarrow act\rightarrow evaluate\rightarrow update.
\]

关机只是停止交互，不代表进入“训练模式”。

但工程上仍需不同时间尺度：

- milliseconds：state update；
- seconds：memory；
- minutes/hours：fast adaptation；
- days：consolidation / structural change。

---

## 38.19 从 Fixed Model 到 Developing Agent

fixed model：

\[
\theta_t=\theta_0.
\]

developing agent：

\[
(\theta_{t+1},M_{t+1},G_{t+1})
=U(\theta_t,M_t,G_t,experience_t).
\]

这里 \(M\) 是 memory，\(G\) 是结构。

真正发展型智能必须同时研究三者。

---

## 最小实验

让同一个 agent 顺序进入 10 个场景，每个场景学习新 object/skill。

每轮记录：

- current task gain；
- old task retention；
- forward transfer；
- memory size；
- parameter/module growth；
- update compute。

最后回到场景 1–10 全量复测。

---

## 本章结论

Continual learning 的目标不是“永远更新权重”，而是在有限资源下保持旧能力、利用旧知识加速新学习，并让 memory、parameters 和 architecture 在不同时间尺度上协调变化。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 38`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-38)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
