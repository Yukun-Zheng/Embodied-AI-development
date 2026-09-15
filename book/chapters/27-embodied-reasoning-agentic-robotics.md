# Part 27　Embodied Reasoning、Agentic Robotics 与长时程任务

## 27.1 Reactive Policy 的极限

一个 reactive policy：

\[
a_t=\pi(o_t).
\]

对短任务足够，但长任务需要记住：

- 已经做了什么；
- 当前子目标；
- 哪一步失败；
- 哪些资源已使用；
- 用户是否改变要求。

所以更一般地：

\[
a_t=\pi(o_t,m_t,g_t,p_t),
\]

其中 \(m_t\) 是 memory，\(g_t\) 是 goal，\(p_t\) 是 plan/progress state。

---

## 27.2 Goal Representation

goal 可以是：

- language；
- target image；
- object state；
- pose；
- reward；
- symbolic predicate；
- latent goal。

例如“把厨房收拾干净”不是直接 motor target，而是一个可能包含几十个 state predicates 的抽象目标。

高层 reasoning 首先要把：

\[
g_{abstract}\rightarrow \{g_1,g_2,\dots,g_n\}.
\]

---

## 27.3 Skill / Primitive / Option

长期任务不能每次从 torque level 规划。

可以定义 option：

\[
o=(I_o,\pi_o,\beta_o),
\]

分别表示 initiation set、内部 policy、termination condition。

现代“tool calling / skill calling”其实和经典 hierarchical RL / task planning 有深刻对应关系。

---

## 27.4 Task Decomposition

长任务：

> “把桌上的脏杯放进洗碗机并启动。”

可以分解：

```text
locate cup
→ grasp
→ navigate/open dishwasher
→ place cup
→ close door
→ choose program
→ press start
```

好的 decomposition 必须满足：

- 子目标可观测；
- 子目标可验证；
- 失败可恢复；
- skill library 可执行。

LLM 生成一个听起来合理的 plan 不代表这些条件成立。

---

## 27.5 Hierarchical Policy

典型双层结构：

\[
g_k=\pi_H(o_{0:t},l,m),
\]

\[
a_t=\pi_L(o_t,g_k).
\]

高层低频运行，低层高频闭环。

它对应经典系统中的：

```text
task planner
↓
motion / skill planner
↓
controller
```

区别只是各层越来越多由 learned model 实现。

---

## 27.6 Language Planner + Motor Policy

这种架构的优势：

- high-level compositionality；
- low-level motor specialization；
- plan 可读；
- skill 可复用。

弱点：

- semantic plan 与 physical feasibility 脱节；
- skill boundary 难定义；
- error propagation；
- planner latency；
- world state 可能过时。

所以 planner 必须持续接收 execution feedback，而不是一次性生成完整脚本。

---

## 27.7 Embodied Reasoning Model

Embodied reasoning 不应被定义为“模型输出了一段思维文本”。更严格的定义应是：

> 中间推理状态对物理任务的动作选择、子目标选择或失败恢复产生可测量的因果贡献。

设 latent reasoning \(r_t\)：

\[
r_t=f(o_{0:t},g,m_t),
\]

\[
a_t=\pi(o_t,r_t).
\]

要证明 reasoning 有用，需要干预 \(r_t\) 而不是只展示文本。

---

## 27.8 Spatial / Temporal / Physical Reasoning

### Spatial

- inside / on / behind；
- reachability；
- collision；
- viewpoint relation。

### Temporal

- before / after；
- progress；
- event boundary；
- waiting。

### Physical

- support；
- gravity；
- friction；
- deformation；
- tool affordance。

一个 VLM 在问答中答对这些，不等于 robot policy 能在闭环里用对。

---

## 27.9 Tool Use 与 Skill Calling

Agentic robot 可以调用：

- navigation；
- grasp detector；
- motion planner；
- force controller；
- VLA skill；
- database；
- human query。

系统形态：

```text
reasoning model
↓ choose tool + arguments
robot skill / planner / controller
↓ execution result
reasoning model
↺
```

这让具身系统更像 operating system，而不是单个 neural network。

---

## 27.10 Long-Horizon Planning

长任务成功率会乘法衰减。

若每一步成功率为 \(p\)，\(n\) 步任务近似：

\[
P_{success}=p^n.
\]

即使 \(p=0.98\)，100 个关键步骤：

\[
0.98^{100}\approx0.133.
\]

这说明长时程不能只靠“单步更准”，还必须有：

- verification；
- retries；
- recovery；
- replanning；
- memory。

---

## 27.11 Online Replanning

正确闭环：

```text
plan
→ execute one segment
→ observe
→ verify
→ update belief
→ replan
```

而不是：

```text
plan 30 steps
→ blindly execute 30 steps
```

replanning frequency 本身也是系统参数。

---

## 27.12 Progress Monitoring

定义 task progress \(p_t\)：

\[
p_t=P(g\text{ achieved}\mid o_{0:t},m_t).
\]

progress model 可以判断：

- 子任务完成；
- 停滞；
- 倒退；
- 意外事件。

2026 年 Gemini Robotics ER 2 等公开系统已把 progress understanding 作为长任务关键能力之一。

---

## 27.13 Error Detection

错误检测不应只依赖终局 success label。

可以用：

- visual anomaly；
- state constraint violation；
- unexpected contact；
- plan-state mismatch；
- world model prediction error；
- low confidence。

定义 surprise：

\[
S_t=-\log p(o_{t+1}\mid o_{\le t},a_t).
\]

高 surprise 可以触发检查，但不能自动等同于失败。

---

## 27.14 Recovery

恢复通常需要先判断 failure state 属于哪一类：

```text
object dropped
object not grasped
collision
wrong object
blocked path
lost localization
human interruption
```

再选择 recovery skill。

真正 robust 的机器人必须在 failure distribution 上训练，而不是只在 nominal trajectory 上学习。

---

## 27.15 Human Clarification / Intervention

机器人不确定时最合理动作可能是问人。

若错误代价为 \(C_e\)，询问代价为 \(C_q\)，则当：

\[
P(error)C_e>C_q
\]

就值得 clarification。

这本质上是 value of information。

---

## 27.16 Steerability

Steerability 指执行中可被用户、视觉 subgoal、metadata 或其他控制信号重新引导。

它不同于一次性 instruction following：

\[
\pi(a_t\mid o_t,c_t),\quad c_t\text{ can change online}.
\]

这对真实机器人尤其重要，因为用户经常在执行中改变意图。

---

## 27.17 Chain-of-Thought 的证据问题

不能因为 robot model 输出：

> “I should move around the chair first...”

就说它具有 embodied reasoning。

至少需要比较：

1. 无 reasoning channel；
2. 随机 reasoning；
3. 错误 reasoning；
4. 正确 reasoning；
5. latent reasoning。

如果动作几乎不变，文本可能只是旁白。

---

## 27.18 Agentic Orchestration vs End-to-End

### Agentic system 优势

- 模块可检查；
- 可以接传统 planner；
- 容易安全隔离；
- 长任务更自然。

### End-to-end 优势

- 减少 hand-designed interface；
- 避免 module mismatch；
- 可共同优化。

真实系统很可能是混合：

\[
\text{learned end-to-end skills}
+
\text{agentic high-level orchestration}
+
\text{classical safety/control}.
\]

---

## 最小实验：Reasoning 是否有因果作用

选 20 个需要多步规划的任务，比较：

- reactive VLA；
- planner + VLA；
- planner + memory + VLA；
- planner + memory + progress monitor + recovery。

再对 reasoning plan 做干预：

- shuffle step；
- remove key subgoal；
- inject impossible step。

测：

- task success；
- recovery rate；
- human intervention；
- unnecessary actions；
- execution time。

如果模型真的利用 reasoning，错误 plan 应产生可解释的行为退化。

---

## 本章结论

Embodied reasoning 的核心不是“机器人会说自己在想什么”，而是它能否在**多步、部分可观测、可失败的物理任务中维护目标、监控进度、选择技能、发现错误并闭环重规划**。这是一套系统能力，不是一个 prompt 技巧。
<!-- CHAPTER-ENRICHMENT-R3-P27:START -->
## 27.19 Agentic / Reasoning Failure Taxonomy

### Fluent plan, wrong physical precondition

语言计划逻辑通顺，但忽略 object pose、reachability、contact 或 robot state，导致第一步就不可执行。

### Stale task state

planner 使用旧 progress/memory，重复已完成 subtask 或跳过失败恢复。长时任务需要可更新的 task belief，而不是静态 chain-of-thought。

### Tool/skill hallucination

reasoner 调用不存在、参数不合法或当前 embodiment 不支持的 skill。skill library 必须有 machine-checkable contract。

### Reasoning latency exceeds physical timescale

高层推理耗时数秒，而环境继续变化。需要 async planning、progress monitor 与低层 reactive policy 并行。

### Explanation without causal control

模型能解释“为什么这样做”，但删除 explanation tokens 后行为不变。语言 reasoning 的因果价值必须通过 intervention 验证。

## 27.20 研究问题

1. Embodied reasoning 最小必要 state 是语言 task graph、symbolic predicates、continuous belief，还是多尺度混合？
2. Reasoner 与 motor policy 的刷新频率应该如何自适应任务 phase 与 uncertainty？
3. Tool/skill calling 如何在新 embodiment 上验证 precondition/effect，而不依赖手工 skill metadata？
4. Chain-of-thought 的价值应按解释质量还是行为 intervention gain 评价？
5. 长时 agent 应如何决定何时重规划、何时继续执行、何时请求人类澄清？
<!-- CHAPTER-ENRICHMENT-R3-P27:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 27`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-27)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
