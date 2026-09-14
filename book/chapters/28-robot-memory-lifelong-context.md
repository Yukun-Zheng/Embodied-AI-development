# Part 28　机器人记忆：从 Context Window 到 Lifelong Memory

## 28.1 为什么无记忆 VLA 很难做长任务

短任务可以近似：

\[
a_t=\pi(o_t,l).
\]

但十分钟以上任务中，当前 observation 往往不足以判断：

- 哪些步骤已完成；
- 哪些物体已经处理；
- 用户之前给过什么约束；
- 某次失败发生在哪里；
- 某个抽屉里曾经看见什么。

因此更合理的系统是：

\[
m_{t+1}=F(m_t,o_t,a_t,e_t),
\]

\[
a_t=\pi(o_t,l,m_t).
\]

记忆不再是“加长 context”，而是一个持续更新的状态变量。

---

## 28.2 Short-Term Sensorimotor Memory

最短期记忆通常就是 observation history：

\[
H_t=[o_{t-k+1},\dots,o_t].
\]

它可以解决：

- velocity inference；
- object motion；
- transient occlusion；
- contact onset；
- action continuity。

但窗口长度固定时，时间跨度也固定。

如果相机 30 Hz、窗口 12 帧，模型只看到约 0.4 秒历史。

这对“刚才发生了什么”够用，对“5 分钟前把杯子放哪”完全不够。

---

## 28.3 Working Memory

working memory 保存当前任务执行所需的中间变量，例如：

```text
current subgoal = open dishwasher
holding = cup
opened cabinets = {2, 5}
failed grasps = 1
user constraint = do not move blue bowl
```

它接近 classical task state，但可以由 learned model 更新。

关键要求：

- 可写；
- 可读；
- 可纠错；
- 与 perception 对齐；
- 不无限增长。

---

## 28.4 Episodic Memory

episodic memory 记录过去的具体交互：

\[
e_i=(context_i,trajectory_i,outcome_i).
\]

新任务时检索：

\[
\mathcal R(g,o)=TopK(\text{sim}(q(g,o),k_i)).
\]

它的价值在于：

> 机器人不必把所有经验立即压进参数；它可以先保存“发生过什么”，之后按需调用。

这为 lifelong learning 提供 parameter update 之外的第二条路径。

---

## 28.5 Semantic Memory

semantic memory 保存从多次 episode 中抽象出的稳定知识，例如：

- 这个厨房杯子通常放在第二层；
- 某类抽屉需要先向上抬再拉；
- 用户偏好玻璃杯放右侧。

它和 episode 的区别类似：

```text
episodic: 昨天 10:20 我打开了这个抽屉
semantic: 这个抽屉通常很紧
```

从 episode 到 semantic memory 需要 consolidation。

---

## 28.6 Spatial Memory

空间任务中，memory 往往必须绑定几何位置。

可以是：

- occupancy map；
- semantic map；
- scene graph；
- object memory；
- neural spatial field。

对象记忆可写成：

\[
m_i=(id_i,category_i,pose_i,time_i,confidence_i).
\]

当对象移动后，旧 memory 必须衰减或更新，否则机器人会根据过时世界状态行动。

---

## 28.7 External Memory

external memory 把长期信息放在模型上下文之外：

```text
policy / reasoning model
      ↕ read / write
memory store
  - vector DB
  - scene graph
  - episodic log
  - task state
```

优势：

- 容量大；
- 可持久化；
- 可查询；
- 不需要每次全塞进 token context。

风险：

- retrieval 错误；
- stale memory；
- privacy；
- identity mismatch；
- 写入污染。

---

## 28.8 Retrieval-Augmented Robot Policy

类似 RAG：

\[
z_{mem}=Retrieve(o_t,l,memory),
\]

\[
a_t=\pi(o_t,l,z_{mem}).
\]

但机器人 retrieval 比文本 RAG 更困难，因为 query 包含：

- 当前视觉；
- 几何位置；
- embodiment state；
- task phase；
- time。

所以相似度不应只有 semantic embedding。

---

## 28.9 Multi-Scale Embodied Memory

2026 年 Physical Intelligence 公布的 Multi-Scale Embodied Memory（MEM）明确把 long-term 与 short-term memory 结合到 VLA 中，用于更长的多阶段任务。

这个方向最重要的思想不是某个模块名字，而是承认：

> 机器人记忆天然具有多个时间尺度。

可以写成：

\[
m_t=(m_t^{fast},m_t^{mid},m_t^{slow}).
\]

不同层承担：

- fast：运动与局部接触；
- mid：当前任务阶段；
- slow：跨任务/跨 episode 知识。

---

## 28.10 Long / Short-Term Memory 协同

多尺度系统需要解决写入和路由：

\[
\alpha_t=Gate(o_t,m_t),
\]

决定信息进入哪层 memory。

如果所有 observation 都写入长期 memory，会造成：

- 存储爆炸；
- retrieval noise；
- 无意义细节污染。

因此必须学习“什么值得记住”。

---

## 28.11 Memory Compression

长 trajectory：

\[
O(Td)
\]

直接保存 token 成本会线性增长。

可使用：

- keyframe；
- event segmentation；
- state summarization；
- latent compression；
- object-centric memory；
- task milestone。

压缩目标不是视觉重建最优，而是未来决策足够：

\[
\min I(M;H)\quad
\text{s.t.}\quad
I(M;A_{future})\ge\eta.
\]

这是一个信息瓶颈视角。

---

## 28.12 Forgetting

机器人不应该永久保存所有信息。

合理 forgetting 包括：

- stale spatial state；
- transient human instruction；
- low-confidence observation；
- redundant episodes。

可以定义 memory utility：

\[
U(m_i)=\mathbb E[\Delta performance\mid m_i].
\]

低 utility、长期未使用的条目可降低优先级。

但“遗忘”与 catastrophic forgetting 不同：前者是主动管理，后者是能力意外丢失。

---

## 28.13 Memory 与 World Model 的区别

两者容易混淆。

### Memory

回答：

> 过去发生了什么？

### World Model

回答：

> 如果现在这样做，未来可能发生什么？

形式上：

\[
Memory: m_t=F(history),
\]

\[
WorldModel: p(s_{t+1:t+H}\mid s_t,a_{t:t+H-1}).
\]

一个系统可以有 memory 而没有 dynamics model，也可以有 world model 但没有跨 episode memory。

---

## 28.14 Memory 对 10+ Minute Task 的意义

长任务真正考验的不是单一 skill，而是：

- temporal credit；
- progress tracking；
- state persistence；
- error recovery；
- object permanence；
- user intent persistence。

如果任务持续 20 分钟但模型只能看 2 秒 history，那么它必须依赖外部或压缩 memory。

---

## 最小实验：记忆的必要性曲线

构造长度逐渐增加的任务：

```text
30 s
2 min
5 min
10 min
20 min
```

比较：

1. fixed observation window；
2. larger context；
3. episodic retrieval；
4. structured task memory；
5. multi-scale memory。

测：

- success；
- repeated action rate；
- forgotten subgoal；
- wrong-object revisit；
- recovery latency；
- memory compute/storage。

如果 memory 真有用，优势应该随 horizon 增长而扩大。

---

## Source anchor

- Physical Intelligence, “VLAs with Long and Short-Term Memory”, 2026-03-03: https://www.pi.website/research/memory

---

## 本章结论

机器人记忆不是“把 context window 做大”。真正的 embodied memory 必须解决 **写什么、存多久、按什么检索、如何压缩、何时遗忘、怎样与空间/任务状态绑定**。当机器人开始执行十分钟乃至跨天任务时，memory 将从附加模块变成核心系统状态。