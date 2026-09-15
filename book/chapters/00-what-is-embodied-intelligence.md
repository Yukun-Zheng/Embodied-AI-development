# Part 0　具身智能究竟是什么

## 学习目标

读完本章，应能够：区分静态 AI 与闭环物理智能；解释 Agent–Body–Environment；用 POMDP 表达部分可观测交互；解释 embodiment、affordance、实时性和 morphological computation；给出“通用机器人”比“多任务机器人”更严格的定义。

---

## 0.1 从函数拟合到闭环交互

很多机器学习问题可写成

\[
\hat y=f_\theta(x).
\]

输入和标签在训练前已经存在，模型预测不会反过来改变下一条数据。机器人不是这样。机器人动作会改变物理世界，因此基本对象是闭环：

\[
s_t\xrightarrow{h}o_t\xrightarrow{\pi_\theta}a_t
\xrightarrow{F(\cdot)}s_{t+1}\xrightarrow{h}o_{t+1}.
\]

其中 \(s_t\) 是世界状态，\(o_t\) 是 observation，\(a_t\) 是动作。真正的学习对象是交互轨迹：

\[
\tau=(o_0,a_0,o_1,a_1,\ldots,o_T).
\]

这带来四个后果：

1. 策略决定自己未来会看到什么，因此部署分布依赖策略；
2. 错误会通过环境积累；
3. 动作具有物理代价和不可逆性；
4. 延迟会使模型基于“过去的世界”行动。

这四点贯穿全书。

## 0.2 Agent、Body、Environment

更完整的策略形式：

\[
a_t=\pi_\theta(o_{\le t},m_t,g,e),
\]

其中 \(m_t\) 是 memory，\(g\) 是目标，\(e\) 是 embodiment 描述。

**Agent** 负责表示、预测、决策与学习；**Body** 定义传感器、执行器、自由度、可达域和动力学；**Environment** 提供对象、接触、社会主体与物理规律。

不能把 Body 当成模型最后一个“action API”。如果相机换了位置、夹爪换成灵巧手、轮式底盘换成人形腿，同一任务的 observation、可行动空间、稳定条件和最优策略都会改变。

## 0.3 Observation 不等于 State

机器人几乎从不直接获得完整状态：

\[
o_t\sim O(o_t\mid s_t).
\]

遮挡、视场、接触力、人的意图、物体内部状态都不可完全观测。因此系统需要 belief：

\[
b_t(s)=P(s_t=s\mid o_{0:t},a_{0:t-1}).
\]

POMDP 形式：

\[
\mathcal M=(\mathcal S,\mathcal A,T,R,\Omega,O,\gamma).
\]

Memory、state estimator、world model、active perception 都可以看成在不同层面解决部分可观测性。

## 0.4 Embodiment 的五层含义

一个身体至少决定：

- **Geometry**：哪里能到、哪里会碰撞；
- **Dynamics**：质量、惯性、摩擦、柔顺性；
- **Sensing**：能看到/摸到/测到什么；
- **Actuation**：能施加什么动作、频率和力；
- **Morphology-induced prior**：什么行为天然容易实现。

因此跨本体学习不只是把 action dimension padding 成一样长。

## 0.5 Affordance：世界是“能做什么”

对于机器人，杯子不只是 category=`cup`，还意味着可抓取、可盛液体、可能易碎、有把手、可作为容器。

可抽象为：

\[
A(o,e,g)\rightarrow \{\text{feasible actions/effects}\}.
\]

Affordance 是世界属性、身体能力和任务目标之间的关系。这也是为什么图像分类 accuracy 并不能直接预测 manipulation success。

## 0.6 时间与实时性

总延迟：

\[
\Delta t=\Delta t_{sense}+\Delta t_{pre}+\Delta t_{infer}+\Delta t_{comm}+\Delta t_{act}.
\]

当机器人在运动时，\(\Delta t\) 会形成 state mismatch。真实系统往往是多速率：电流环 kHz，joint servo 数百 Hz–kHz，WBC 数十到数百 Hz，camera 15–60 Hz，VLA 数 Hz–几十 Hz，高层 reasoning 更慢。

因此“模型 latency”不是部署附属指标，而是 policy semantics 的一部分。

## 0.7 Morphological Computation

柔顺手指会自动包络物体；弹性腿会储存/释放能量；机械限位会阻止危险姿态。身体本身承担一部分 computation。

因此能力更合理的分解是：

\[
\text{Capability}=f(\text{morphology},\text{control},\text{learning},\text{environment}).
\]

把所有结构先验都去掉，再让神经网络从数据重学，并不一定更“通用”。

## 0.8 什么叫 General-Purpose Robot

至少区分：

\[
G=G_{object}\times G_{scene}\times G_{task}\times G_{embodiment}\times G_{time}.
\]

即跨对象、场景、任务、身体和长期运行条件。一个模型在同一实验室完成 100 个训练任务，可称 generalist；但真正 general-purpose 更要求未见组合、错误恢复、环境迁移、长期适应。

## 0.9 一套统一分析框架

以后遇到任何模型，都问：

1. 它感知什么？
2. 内部表示什么？
3. 是否估计不确定性？
4. 是否预测 action consequence？
5. 怎样决定动作？
6. action 如何穿过 controller 进入硬件？
7. feedback 在哪里？
8. failure 后会不会改变？

## 最小实验

构造一个有遮挡的 2D navigation toy world：同一当前像素对应两个隐藏状态。比较 memoryless policy 与有 belief/memory policy，观察为什么单帧 reactive mapping 无法达到最优。

## 思考题

- 如果一个系统没有身体，但可以远程调用机器人 API，它算不算具身？边界取决于什么？
- 为什么“动作输出正确率”很少是机器人最重要的 offline metric？
- 一个模型能跨 10 台训练过的机器人工作，与能 zero-shot 控制第 11 台机器人有什么本质差别？
<!-- CHAPTER-ENRICHMENT-R2-P00:START -->
## 0.10 从“智能模型”到物理闭环的数据流

一个最小 embodied system 必须能把信息与物理作用连成闭环：

```text
physical world
→ sensor transduction
→ timestamped observation
→ state / belief / representation
→ task context / memory
→ policy / planner
→ action representation
→ IK / controller / safety layer
→ actuator
→ changed physical world
→ new observation
```

因此一个模型即使在离线 benchmark 上“理解场景”，只要它没有通过 action 改变世界并利用反馈修正，就还没有覆盖 embodied intelligence 的完整对象。

更精确地，闭环可以写为：

\[
o_t\sim p(o\mid x_t),\qquad
b_t=U(b_{t-1},o_t,a_{t-1}),
\]

\[
a_t\sim\pi(a\mid b_t,g,m_t),\qquad
x_{t+1}\sim p(x'\mid x_t,a_t).
\]

身体、传感器、控制频率、delay 与环境 dynamics 都进入这个系统，而不是网络外部的“工程细节”。

## 0.11 研究问题

1. 什么能力必须通过真实 closed-loop interaction 才能验证，离线 video/language benchmark 原理上无法证明？
2. Embodiment 提供的是限制、inductive bias、额外计算，还是三者同时存在？
3. 当同一 policy 换一个身体性能骤降时，应该把问题归因 representation、action interface 还是 controller？
4. General-purpose robot 的“通用”应按 object/scene/task/physics/embodiment/time 哪些轴定义？
5. 一个长期 physical agent 的最小内部状态是什么：belief、world model、memory，还是可在线生长的结构？
<!-- CHAPTER-ENRICHMENT-R2-P00:END -->
<!-- CHAPTER-ENRICHMENT-R3-P00:START -->
## 0.12 Failure Taxonomy：什么时候“看起来智能”却不是具身智能

### Offline competence without closed-loop competence

模型能回答“下一步该抓杯子”，但在抓偏后不能利用新 observation 修正；这证明 semantic competence 不能替代 feedback competence。

### Body-agnostic claim without body intervention

只在同一机械臂、更换物体测试，不能支持 embodiment generality。必须改变 kinematics、action interface、sensor placement 或 controller 才真正触碰身体变化。

### World-model claim without action sensitivity

若预测未来不随候选 action 改变，模型更接近 video predictor，而不是可用于 control 的 counterfactual model。

### Memory claim without delayed necessity

若去掉历史后任务仍成功，所谓 memory module 可能只是额外容量。必须设计“当前 observation 不足、过去信息必要”的任务。

### Intelligence claim hidden by infrastructure

更强 simulator、controller、teleoperation data、reset protocol 或人工 intervention 都可能提高 success。系统能力必须展开到完整物理栈后再归因。
<!-- CHAPTER-ENRICHMENT-R3-P00:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 00`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-00)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
