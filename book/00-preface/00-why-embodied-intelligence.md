# 0.1 为什么智能进入物理世界后，一切都变了

> **本章问题**：为什么一个在网页、文本或静态图像上表现很强的模型，一旦被放进机器人身体里，问题会发生根本变化？

---

## 0. 本章要解决的问题

假设我们已经拥有一个非常强的模型。它可以看图，可以理解语言，可以写代码，可以回答复杂问题。现在我们把它接到一台机器人上：相机图像作为输入，机器人动作作为输出。

是否只要把

```text
text token → text token
```

替换成

```text
image + language → robot action
```

就得到了具身智能？

答案是否定的。

真正的变化不在于“输出 token 变成了动作”，而在于系统进入了一个**持续演化、部分可观测、具有动力学约束、存在延迟和不可逆后果的闭环物理世界**。

这正是本书的起点。

---

## 1. 一个最小思想实验

考虑一个机械臂，需要把桌上的杯子拿起来。

如果这是一个静态视觉问答问题，我们可以给模型一张图：

```text
Image
  ↓
Model
  ↓
“The cup is on the left side of the table.”
```

回答结束，系统也结束。

但如果目标是“拿起杯子”，系统必须持续运行：

```text
Camera / Joint Encoder
        ↓
Observation at time t
        ↓
State Estimation / Representation
        ↓
Decision / Policy
        ↓
Action Command
        ↓
Low-level Controller
        ↓
Robot Motion
        ↓
World Changes
        ↓
New Observation at time t+1
        ↺
```

每一次动作都会改变下一次输入。

于是模型不再只是对一个固定数据样本做预测，而是在参与生成自己的未来数据分布。

这句话极其重要：

> **具身智能中的 agent 不只是从环境读取数据，它通过行动不断改变未来将看到的数据。**

这也是机器人学习与普通 i.i.d. 监督学习之间最根本的差异之一。

---

## 2. 从函数映射到动态系统

普通监督学习常被抽象为：

\[
f_\theta: x \mapsto y.
\]

给定输入 \(x\)，模型输出 \(y\)。

机器人则至少需要考虑环境状态：

\[
s_{t+1}=F(s_t,a_t,\xi_t),
\]

其中：

- \(s_t\)：时刻 \(t\) 的真实世界状态；
- \(a_t\)：机器人执行的动作；
- \(F\)：世界与机器人共同决定的动力学；
- \(\xi_t\)：摩擦、碰撞、传感器误差、外界扰动等不确定因素。

机器人通常又无法直接读取 \(s_t\)，只能得到 observation：

\[
o_t=G(s_t,\eta_t),
\]

其中 \(\eta_t\) 表示传感噪声等因素。

策略根据可获得的信息选择动作：

\[
a_t\sim\pi_\theta(a_t\mid o_{0:t},a_{0:t-1},g),
\]

其中 \(g\) 可以表示目标、语言指令或任务条件。

因此真正的系统不是：

\[
o_t\rightarrow a_t,
\]

而是：

\[
\boxed{
 s_t
 \rightarrow o_t
 \rightarrow \pi
 \rightarrow a_t
 \rightarrow F
 \rightarrow s_{t+1}
 \rightarrow \cdots
}
\]

智能存在于这个闭环里，而不只存在于 \(\pi\) 这个神经网络中。

---

## 3. 身体为什么不是“输出设备”

假设两个 agent 拥有完全相同的高级策略，但身体不同：

- A 是 7-DoF 单机械臂；
- B 是双臂移动机器人；
- C 是拥有双腿、双臂和灵巧手的人形机器人。

一句“把盒子从地上拿起来放到桌上”对三者而言对应完全不同的可行行为集合。

对于 A，盒子可能根本不在 workspace 中。

对于 B，可以先移动底盘，再操作。

对于 C，可能需要走近、下蹲、保持平衡、抓取、起身，再行走。

也就是说，身体改变了：

\[
\text{reachable states},
\]

\[
\text{available actions},
\]

\[
\text{observability},
\]

\[
\text{dynamics},
\]

以及任务本身的解空间。

因此 embodiment 不应该被理解为“给同一个大脑换一个输出接口”。

更准确地说：

> **身体定义了智能能够如何感知世界、如何作用于世界，以及哪些策略在物理上可能成立。**

这也是后面讨论 cross-embodiment 时必须面对的根本问题。

---

## 4. 时间为什么突然变得重要

在离线图像分类中，一次推理慢 50 ms 和慢 500 ms，很多时候只影响用户体验。

机器人中却不同。

假设机器人以 20 Hz 运行高层策略，则每个周期只有：

\[
\Delta t=\frac{1}{20}=50\text{ ms}.
\]

如果模型推理本身耗时 120 ms，那么当动作被真正执行时，它依赖的 observation 可能已经过时。

真实系统中至少同时存在多种时间尺度：

```text
Motor current loop       ~ kHz
Joint controller          ~ 100–1000 Hz
State estimation          ~ 50–500 Hz
Camera                    ~ 15–60 Hz
Learned policy            ~ 5–50 Hz
High-level reasoning      ~ sub-Hz to several Hz
```

这些数字不是统一标准，只是典型数量级示意；具体系统取决于硬件与任务。

重要的是：

> **机器人智能天然是 multi-rate system。**

因此一个 VLA 即使“预测动作正确”，如果延迟、动作 chunk、控制频率和低层控制设计不合适，机器人依然可能失败。

---

## 5. 为什么“看见”不等于“知道状态”

桌上有一个杯子，摄像头只看到它的一侧。

机器人不知道：

- 杯子背后有没有障碍物；
- 杯子是否装满液体；
- 杯子底部是否粘住桌面；
- 遮挡区域中是否还有其他物体；
- 抓住之后会不会滑落。

因此 observation 与 state 不等价：

\[
o_t \neq s_t.
\]

机器人只能根据历史信息维护某种内部估计：

\[
b_t(s)=P(s_t=s\mid o_{0:t},a_{0:t-1}).
\]

这个 \(b_t\) 称为 belief state。

即使现代系统未显式计算完整 Bayesian belief，它们仍然无法逃避同一个事实：

> **世界中始终存在当前传感器没有直接提供的信息。**

这将自然导向：

- state estimation；
- memory；
- world model；
- uncertainty；
- active perception；
- information gathering。

也就是说，“主动看一眼”“换个视角”“先碰一下再决定”并不是附加功能，而可能是部分可观测世界中的必要行为。

---

## 6. 动作具有不可逆后果

语言模型生成了一个错误 token，可以重新生成。

机器人把玻璃杯推下桌子，无法通过“重新采样”让杯子恢复。

机器人系统中的动作可能带来：

- 碰撞；
- 物体损坏；
- 机器人自身损坏；
- 对人的伤害；
- 状态进入不可恢复区域。

因此机器人决策不仅关心：

\[
\text{expected task success},
\]

还必须考虑：

\[
\text{risk},\quad
\text{constraint},\quad
\text{uncertainty},\quad
\text{recoverability}.
\]

这也是为什么安全、控制、规划和不确定性不能在具身智能教材中被 relegated 为“传统机器人部分”。

它们仍然构成现代学习系统的物理底座。

---

## 7. 智能不应该只定位在神经网络中

一个工作的机器人系统可能是：

```text
RGB / Depth / Tactile / Proprioception
                ↓
        perception modules
                ↓
      state / representation
                ↓
     VLA / policy / planner
                ↓
      Cartesian target
                ↓
       inverse kinematics
                ↓
        joint target
                ↓
 impedance / torque controller
                ↓
             robot
                ↓
             world
                ↺
```

如果任务成功，我们不能未经实验就说：

> “大模型理解了物理。”

成功可能来自：

- 强大的视觉预训练；
- 大规模 demonstration；
- 很好的低层控制器；
- 极其稳定的机械设计；
- task-specific planner；
- 数据覆盖足够好；
- benchmark 本身变化较小；
- 或者这些因素共同作用。

因此本书始终坚持一个原则：

> **不要把系统级能力自动归因给其中最显眼的模型模块。**

真正的研究，需要通过 controlled experiment 和 ablation 找到能力来自哪里。

---

## 8. 从经典机器人到现代具身智能

现代具身智能不是与经典机器人学断裂的全新领域。

它更像多个历史方向逐渐汇合：

```text
Classical Robotics
  ├─ geometry
  ├─ kinematics
  ├─ dynamics
  ├─ planning
  └─ control
        │
        ├─────────────┐
        ↓             │
Robot Learning        │
  ├─ imitation        │
  ├─ reinforcement    │
  └─ representation   │
        │             │
        ↓             │
Deep Vision / NLP     │
  ├─ Transformer      │
  ├─ VLM              │
  └─ generative model │
        │             │
        └──────┬──────┘
               ↓
       Foundation Robotics
        / Embodied AI
```

经典机器人学往往具有明确模型、结构和约束，但泛化有限。

现代机器学习擅长从大量数据中拟合复杂函数，但容易隐藏机制、依赖数据分布。

具身智能真正困难的方向，恰恰在于如何把两者的优势结合起来，而不是简单让一方消灭另一方。

---

## 9. “具身”不代表反对内部表示

历史上，Rodney Brooks 的 *Intelligence without Representation* 强调直接通过 perception/action 与真实世界交互，并批评传统 AI 对中心化内部表示的依赖。这篇 1991 年工作对行为式机器人学和 embodied AI 的思想史具有重要影响。[Brooks, 1991](https://doi.org/10.1016/0004-3702(91)90053-M)

但“具身智能”并不意味着现代系统必须拒绝 representation、memory 或 world model。

更关键的问题是：

> 一个内部表示是否因为真实交互而形成，并且是否真正帮助智能体预测、决策和行动？

Margaret Wilson 在对 embodied cognition 的经典梳理中也强调，“embodied cognition”实际上包含多个强弱不同的主张，并非一个单一、无争议的命题。[Wilson, 2002](https://doi.org/10.3758/BF03196322)

因此本书不会把“具身”当成哲学口号，而会尽量把它转化为可以实验的问题。

例如：

- 改变 morphology，策略是否还能迁移？
- 遮挡关键物体后，agent 会不会主动获取信息？
- representation 是否保留接触与运动所需信息？
- world model 是否真的提升 closed-loop success，而不仅是生成好看的视频？
- memory 是否提高了长时程任务，而不是只增加参数量？

---

## 10. 本书的统一立场：闭环优先

后续不论讲：

- IK；
- impedance control；
- SLAM；
- Diffusion Policy；
- VLA；
- world model；
- active perception；
- humanoid；
- developmental learning；

都会不断回到同一个闭环：

\[
\boxed{
\text{World}
\rightarrow
\text{Observation}
\rightarrow
\text{Internal State}
\rightarrow
\text{Decision}
\rightarrow
\text{Action}
\rightarrow
\text{World}
}
\]

我们最终关心的不是模型在静态数据集上的某个数字，而是：

> **它能否在真实的时间、空间、动力学、接触、不确定性和身体约束下持续形成有效行为。**

这就是本书所说的具身智能。

---

## 11. 本章之后

接下来我们不会立刻进入 VLA。

我们首先建立具身智能所需的数学语言，然后进入机器人身体、空间几何、运动学、动力学与控制。

只有真正理解：

\[
\mathbf q,
\quad
\dot{\mathbf q},
\quad
\boldsymbol\tau,
\quad
SE(3),
\quad
\mathbf J(\mathbf q),
\quad
M(\mathbf q),
\]

分别是什么之后，现代 robot policy 的 action space、representation 和控制接口才不会只是抽象 token。

最终，当我们再回到 VLA、world model 和 humanoid foundation model 时，我们看到的将不再是一张神经网络结构图，而是一套真正运行在物理世界中的智能系统。

---

## 12. 参考资料

1. Brooks, R. A. (1991). *Intelligence without representation*. **Artificial Intelligence, 47**(1–3), 139–159. https://doi.org/10.1016/0004-3702(91)90053-M
2. Wilson, M. (2002). *Six views of embodied cognition*. **Psychonomic Bulletin & Review, 9**, 625–636. https://doi.org/10.3758/BF03196322
3. Lynch, K. M., & Park, F. C. *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press. Free companion materials: https://modernrobotics.northwestern.edu/

---

**Status:** v0.1 draft  
**Last verified:** 2026-09-14
