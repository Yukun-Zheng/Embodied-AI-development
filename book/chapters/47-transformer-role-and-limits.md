# Part 47　Transformer 在具身智能中的作用与边界

## 47.1 Transformer 真正解决了什么

Transformer 的核心能力是基于 attention 的序列信息路由：

\[
Attention(Q,K,V)=softmax\left(\frac{QK^T}{\sqrt d}\right)V.
\]

它特别适合：

- 多模态 token 融合；
- 长上下文；
- scaling；
- 预训练迁移。

它并没有天然解决：

- rigid-body dynamics；
- contact；
- stability；
- persistent memory；
- real-time control。

---

## 47.2 Attention 的优势与代价

全局 attention 可以灵活连接任意 token。

代价：

\[
O(N^2)
\]

以及结构先验较弱。

对机器人而言，joint graph、object relation、spatial locality 都可能值得显式编码，而不是全部交给 attention 自己学。

---

## 47.3 Sequence Model 是否等于 Dynamics Model

不是。

一个 sequence model：

\[
p(x_{t+1}\mid x_{\le t})
\]

可以利用统计相关性预测下一步，却不一定学到 intervention dynamics：

\[
p(s'\mid s,do(a)).
\]

预测准确与因果控制能力不同。

---

## 47.4 Tokenization 对物理连续性的破坏

连续量：

\[
a\in\mathbb R^d
\]

离散成 token：

\[
Q(a)\in\{1,\dots,K\}.
\]

会产生：

- quantization；
- discontinuity；
- long token sequence。

这就是 flow/diffusion continuous action expert 再次兴起的原因之一。

---

## 47.5 Fixed Context 与 Persistent World

Transformer context 是临时计算状态。

机器人世界却持续存在：

> 昨天放进柜子的工具今天仍在那里。

因此需要 external/persistent memory，而不是无限 context window。

---

## 47.6 Reactive Transformer 与 Closed-Loop Control

即使每帧重新推理，也可能因 latency 导致：

\[
a_t=\pi(o_{t-k}),\quad k>0.
\]

这不是充分闭环。

高频 control 仍需要 fast layer / controller。

---

## 47.7 Transformer + External Controller

现代 VLA 常输出 target，然后由传统 controller 执行：

```text
Transformer/VLA
→ target pose/action chunk
→ impedance/WBC/PID
→ motor
```

这不是妥协，而是把不同时间尺度交给合适计算结构。

---

## 47.8 Transformer + Memory

Transformer 可以作为 read/write controller：

\[
z_t=Transformer(o_t,Retrieve(M,q_t)).
\]

memory 不必存在权重或 context 内。

---

## 47.9 Transformer + World Model

可能结构：

```text
Transformer policy
↕
latent dynamics / world model
```

policy 负责 action proposal，world model 负责 counterfactual evaluation。

两者不必是同一种 architecture。

---

## 47.10 Transformer + Structural Module

结构模块包括：

- kinematic graph；
- scene graph；
- differentiable planner；
- contact graph；
- geometric layer。

Transformer 可负责 flexible routing，结构模块负责 hard inductive bias。

---

## 47.11 State-Space / Recurrent Model 的重新价值

具身系统天然 streaming。

递归状态：

\[
h_{t+1}=F(h_t,o_t,a_t)
\]

提供固定每步计算和 persistent state。

SSM/RNN 在 long-stream robotics 中可能比每次重读整个 context 更自然。

---

## 47.12 Graph / Object-Centric / Geometry-Centric Architecture

机器人世界不是 token bag。

它具有：

- body graph；
- object relation；
- Euclidean geometry；
- contact topology。

显式结构可能提高 data efficiency 和 cross-embodiment generalization。

---

## 47.13 Continuous-Time Architecture

物理世界连续演化：

\[
\dot x=f(x,u).
\]

而常规 Transformer 处理离散 sample。

continuous-time model、Neural ODE、event-driven architecture 可以更自然地处理异步 sensor 和多频率系统。

---

## 47.14 Modular / Hierarchical Architecture

复杂机器人可能需要：

```text
reasoning
memory
world model
skill policy
reflex
controller
```

模块化的挑战不是“模块越多越好”，而是学习出稳定接口。

---

## 47.15 Transformer 之后真正值得问的问题

不应该问：

> “下一个替代 Transformer 的名字是什么？”

应该问：

1. 哪些状态必须 persistent？
2. 哪些关系必须结构化？
3. 哪些环节需要 continuous time？
4. 哪些动作需要高频 reflex？
5. 哪些知识应通过 mechanism 而不是 parameter memory 表达？
6. architecture 能否随 embodiment / experience 生长？

未来架构很可能是多个计算范式的组合，而不是单一 backbone 一统所有时间尺度。

---

## 最小实验

固定数据和参数量，比较：

- vanilla Transformer；
- recurrent/SSM；
- Transformer + persistent memory；
- graph-conditioned model；
- slow Transformer + fast controller。

任务专门选择 long-stream、cross-embodiment、latency-sensitive 场景。

---

## 本章结论

Transformer 是极其强大的通用信息路由器和预训练载体，但物理智能还需要**持续状态、几何结构、动力学、接触、实时反馈和多时间尺度**。下一代具身架构的问题不是“推翻 Transformer”，而是找到哪些物理/计算结构不应继续被压扁成 token sequence。