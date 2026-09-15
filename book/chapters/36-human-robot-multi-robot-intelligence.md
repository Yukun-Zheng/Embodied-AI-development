# Part 36　Human–Robot Interaction 与 Multi-Robot Intelligence

## 36.1 Human-in-the-Loop Robotics

真实机器人系统很少是“完全自动”与“完全遥操作”的二选一。

更常见的是：

```text
autonomy
→ uncertainty / failure
→ human assistance
→ resume autonomy
```

人类介入可以同时承担：

- safety；
- correction；
- labeling；
- demonstration；
- preference feedback。

因此 intervention 既是控制机制，也是数据源。

---

## 36.2 Shared Autonomy

共享控制可以写成：

\[
a=\alpha a_{human}+(1-\alpha)a_{robot}.
\]

但简单线性混合不是唯一方式。

还可以：

- human 给目标，robot 完成轨迹；
- human 控方向，robot 管碰撞；
- robot 执行，human 只在异常时接管。

最关键的问题是 authority allocation：谁在什么时候拥有控制权？

---

## 36.3 Natural-Language Instruction

语言为人机交互提供低带宽、高抽象接口。

但语言命令：

> “把这个轻轻放到那边。”

需要解析为：

- referent；
- target region；
- speed；
- force；
- constraints。

所以 language interface 最终必须落到 physical parameter 或 skill selection。

---

## 36.4 Interactive Correction

用户在执行中说：

- “不是那个，是左边的”；
- “慢一点”；
- “先别放”；
- “从下面抓”。

系统需要 online conditioning：

\[
a_t=\pi(o_t,c_{\le t}).
\]

这比一次性 prompt 更接近真实协作。

---

## 36.5 Intent Inference

机器人可能从：

- gaze；
- gesture；
- speech；
- human motion；
- task context

推断意图。

但 intent 是 latent variable：

\[
p(g\mid o^{human}_{0:t}).
\]

错误的高置信意图推断可能比“不知道”更危险，因此 uncertainty calibration 非常重要。

---

## 36.6 Human Proximity 与 Social Safety

安全不只有碰撞约束。

人在附近时机器人还要考虑：

- speed；
- path predictability；
- personal space；
- surprise motion；
- handover comfort。

优化目标可包含：

\[
J=J_{task}+\lambda_sJ_{safety}+\lambda_hJ_{human\ comfort}.
\]

---

## 36.7 Multi-Robot Communication

多机器人可以共享：

- state；
- map；
- intent；
- task status；
- learned representation。

通信有成本和延迟：

\[
C_{comm}(m_t)>0.
\]

因此不是“共享越多越好”。

---

## 36.8 Coordination

多个 agent 的 joint policy：

\[
\pi(a^1,\dots,a^N\mid o^1,\dots,o^N).
\]

真实系统通常只能每个机器人看到局部 observation。

这使问题变成 Dec-POMDP。

---

## 36.9 Task Allocation

给任务集合 \(T\) 和机器人集合 \(R\)，分配：

\[
\min_{x_{ij}}\sum_{i,j}c_{ij}x_{ij}
\]

同时满足 capacity / capability constraints。

如果机器人异构，成本 \(c_{ij}\) 与 morphology 和 skill 强相关。

---

## 36.10 Centralized / Decentralized Planning

### Centralized

全局 planner 知道所有状态。

优点：全局协调；缺点：单点故障、通信压力。

### Decentralized

每个机器人本地决策。

优点：robust；缺点：coordination 更难。

---

## 36.11 CTDE

Centralized Training, Decentralized Execution：

训练时使用全局信息：

\[
Q(s,a^1,\dots,a^N),
\]

部署时每个 agent：

\[
a^i=\pi_i(o^i).
\]

这是多智能体 RL 的经典折中。

---

## 36.12 Shared World State / Shared Memory

多机器人协作中，共享 memory 可能保存：

```text
object locations
completed subtasks
reserved workspace
robot intentions
failures
```

但 memory 必须解决 concurrency：两个 robot 同时修改状态时如何一致？

这已经接近 distributed systems 问题。

---

## 36.13 Heterogeneous Robot Collaboration

异构机器人可能包括：

- mobile base；
- arm；
- humanoid；
- drone。

它们能力集合不同：

\[
\mathcal C_i\neq\mathcal C_j.
\]

任务分配应利用差异，而不是强行共享同一 action space。

---

## 36.14 Embodiment-Aware Role Assignment

角色分配可以写成：

\[
r_i=f(task,e_i,state_i).
\]

例如：

- 高机器人负责高处；
- 灵巧手负责精细装配；
- mobile base 负责运输。

真正的 multi-robot intelligence 必须理解身体能力。

---

## 36.15 Foundation Model for Multi-Robot Coordination

foundation model 可以提供共享 semantic/task prior，但协作仍需要：

- identity；
- role；
- communication protocol；
- collision/safety；
- shared progress。

“同一模型权重控制两个机器人”与“两个机器人真正协作”不是同一个命题。

---

## 36.16 Agentic Multi-Robot Collaboration

2025–2026 的公开系统已经展示 VLA/embodied reasoning model 驱动的多机器人任务。

可分为三层：

```text
high-level task coordinator
→ per-robot goal / role
→ local VLA / controller
```

也有系统不显式通信，而通过观察伙伴动作隐式协调。

科学问题是：

- 协作来自共同训练还是语言 prompt？
- 是否能处理新 partner？
- partner 故障时是否 reallocate？
- 是否存在真正 shared belief？

---

## 最小实验

双机器人搬运/整理任务，比较：

1. independent policies；
2. explicit communication；
3. shared memory；
4. centralized coordinator；
5. implicit visual coordination。

同时随机让一个 robot 延迟或失效，测 recovery 与 task reallocation。

---

## 本章结论

Human–Robot 与 Multi-Robot 的共同核心是：**智能体必须推断其他 agent 的状态和意图，并在共享物理世界中协调控制权、空间、任务和安全**。这是单体 VLA success rate 无法覆盖的另一层具身智能。
<!-- CHAPTER-ENRICHMENT-R3-P36:START -->
## 36.20 Human / Multi-Robot Failure Taxonomy

### Human intent misread with high confidence

语言/gesture ambiguity 被 policy 当确定指令执行；系统缺少 clarification / consent state。

### Coordination protocol hidden in training distribution

多机器人看似会协作，实际角色固定、start pose 固定；交换 robot role 后崩溃说明没有学到 general coordination。

### Communication delay / packet loss

集中式 multi-agent policy 在理想网络有效，真实 Wi-Fi/edge network 下 stale teammate state 导致碰撞或重复工作。

### Responsibility ambiguity

失败后无法区分 perception、planner、robot A、robot B 或 human instruction 的责任，导致 recovery strategy错误。

### Safety/social norm outside reward

task success 高，但运动路径让人不适、抢夺物体、侵犯 personal space；interaction metric 必须超出任务完成率。

## 36.21 研究问题

1. Human–robot interaction 中 uncertainty 何时应触发 clarification，而不是自主猜测？
2. Multi-robot coordination 应共享全局 world model，还是只交换 task-relevant messages？
3. 通信 bandwidth / latency 如何作为算法变量进入 benchmark，而不是固定理想条件？
4. heterogeneous robots 的 role assignment 能否根据 morphology/capability 在线重规划？
5. 如何定义人机协作的 safety / trust metric，使其不被 task success 掩盖？
<!-- CHAPTER-ENRICHMENT-R3-P36:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 36`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-36)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
