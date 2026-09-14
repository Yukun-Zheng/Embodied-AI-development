# Volume 0　导论：智能为什么必须进入物理世界

> **Edition:** v1.0 · frontier frozen at 2026-09-14  
> 本卷回答两个问题：具身智能究竟研究什么，以及为什么机器人不能被简化成“把多模态模型接到机械臂上”。

---

# Part 0　具身智能究竟是什么

## 0.1 从静态函数到闭环生命线

普通监督学习常写成

\[
\hat y=f_\theta(x).
\]

这隐含了一个非常强的假设：输入先给定，模型给出输出，世界不会因为输出而立刻改变。但机器人面对的是闭环系统：

\[
s_t \xrightarrow{h} o_t \xrightarrow{\pi_\theta} a_t
\xrightarrow{\text{body+physics}} s_{t+1}
\xrightarrow{h}o_{t+1}.
\]

这里 \(s_t\) 是真实世界状态，\(o_t\) 是传感器观测，\(a_t\) 是动作。动作会改变世界，而新世界又改变下一次观测。因此机器人学习的基本对象不是一次映射，而是**交互轨迹**

\[
\tau=(o_0,a_0,o_1,a_1,\ldots,o_T).
\]

只要把这一点真正理解，很多具身智能中的困难就会自然出现：分布会被自己的策略改变、错误会积累、延迟会导致动作过期、一次错误可能造成不可逆的物理后果。

## 0.2 Agent、Body、Environment

一个具身系统至少包含三个不可约对象。

**Agent** 决定如何从观测、记忆、目标和知识产生动作；**Body** 决定动作通过什么自由度、执行器、传感器和动力学进入现实；**Environment** 决定接触、摩擦、遮挡、其他主体和任务约束。

因此更合理的形式是

\[
a_t=\pi_\theta(o_{\le t},m_t,g,e),
\]

其中 \(m_t\) 是记忆，\(g\) 是目标，\(e\) 是 embodiment 描述。相同的“智能”如果换了一副身体，动作空间、可达域、速度上限、触觉信息甚至可观察世界都会改变。

## 0.3 Embodiment 不是输出接口

把 embodiment 看成动作向量维数是一种过度简化。身体同时决定：

- **可行动空间**：哪些状态物理可达；
- **可感知空间**：相机高度、视场、触觉位置、关节编码器；
- **动力学先验**：惯性、柔顺、摩擦、闭链约束；
- **学习难度**：动作维数、控制频率、延迟和稳定性；
- **策略归纳偏置**：两指夹爪和五指灵巧手会诱导完全不同的抓取策略。

这也是 cross-embodiment 研究的核心：我们究竟应该迁移参数、技能、目标、几何关系，还是更抽象的可供性与机制？

## 0.4 Partial Observability

机器人几乎从不直接获得 \(s_t\)。它得到的是

\[
o_t\sim p(o_t\mid s_t),
\]

因此必须维护某种隐状态或 belief：

\[
b_t(s)=p(s_t=s\mid o_{0:t},a_{0:t-1}).
\]

遮挡、相机视野之外的物体、物体内部状态、接触力、人的意图都使问题天然部分可观测。所谓 memory、world model、state estimator、active perception，本质上都在不同层次上处理这个事实。

## 0.5 时间是具身智能的第一等公民

数字模型可以晚 500 ms 回答，而机器人晚 500 ms 可能已经撞上障碍。设感知耗时 \(\Delta t_p\)、推理耗时 \(\Delta t_i\)、通信耗时 \(\Delta t_c\)，动作到达执行器时使用的是一个“过去世界”的估计：

\[
\Delta t=\Delta t_p+\Delta t_i+\Delta t_c.
\]

真正的实时机器人因此常采用多频率结构：例如低层电机控制在数百 Hz 到 kHz，状态估计几十至数百 Hz，高层 VLA 可能只有几 Hz。大模型策略能否可靠工作，不只由 benchmark accuracy 决定，还由这个多速率闭环能否稳定运行决定。

## 0.6 Affordance：物体不是标签，而是行动可能性

在机器人任务中，“杯子”不是一个分类标签，而可能意味着“可抓取”“可盛液体”“有把手”“易碎”“可作为容器”。Gibson 的 affordance 思想提醒我们：智能体真正需要的表征往往是对象和身体之间的关系。

可把任务相关 affordance 抽象为

\[
A(o,e,g)\rightarrow \{\text{feasible actions / effects}\}.
\]

这解释了为什么视觉语义精度高并不自动等于操作成功率高：一个表示可能擅长识别物体，却忽略接触位置、可达性、局部几何和材料性质。

## 0.7 Morphological Computation

身体本身也会“计算”。被动顺应结构可以吸收冲击；合适的足部几何可以简化稳定控制；欠驱动手指可以利用接触自动包络物体。并非所有能力都必须由神经网络显式计算。

因此设计具身智能系统时应始终问：

\[
\text{总能力}=\text{机械结构}+\text{控制}+\text{学习}+\text{环境结构}.
\]

把所有问题都交给模型参数往往既低效又脆弱。

## 0.8 Physical Intelligence 与传统 AI

传统 AI 常可容忍“答错一次再重来”；物理智能面对能量、惯性、接触与安全边界。三个差异尤其关键：

1. **动作具有代价与不可逆性**：打翻液体与输出错误 token 不同；
2. **数据由行动产生**：策略决定未来能看到什么；
3. **世界不会等待推理结束**：实时性成为算法语义的一部分。

因此一个可靠的具身系统通常是混合系统，而非单模型：

```text
Goal / language
      ↓
Reasoning / task planner
      ↓
Skill or VLA policy
      ↓
Trajectory / action chunk
      ↓
Safety + IK/WBC/controller
      ↓
Robot body ↔ physical world
      ↑
State estimation / perception / memory
```

## 0.9 什么叫 General-Purpose Robot

“任务多”并不足以称为通用。至少要区分五种 generalization：

\[
G=G_{object}\times G_{scene}\times G_{task}\times G_{embodiment}\times G_{time}.
\]

即跨物体、跨场景、跨任务、跨身体以及跨长期运行条件。一个能在同一张桌子上做一百个预训练任务的模型，与能在新家庭、新机器人、新指令下组合已有技能的系统，不是同一层次的 generality。

## 0.10 评价一个具身系统的六层问题

本书后续反复使用如下分析框架：

1. **Perception**：它到底观测到什么？
2. **Representation**：保留了哪些任务相关变量？
3. **Prediction / State**：是否知道世界现在和接下来怎样？
4. **Decision**：怎样决定目标、子任务和动作？
5. **Control**：动作怎样稳定进入真实身体？
6. **Learning**：失败之后系统会不会真的变得更好？

这六问比“模型参数多少、用了什么 backbone”更接近物理智能本质。

---

# Part 1　思想史与技术史：从控制论到机器人基础模型

## 1.1 Cybernetics：反馈思想

Wiener 所代表的控制论把“控制、通信、反馈”放进同一框架。机器人领域最持久的思想不是某个网络架构，而是：**观察结果，比较目标，根据误差继续行动。**

经典反馈写成

\[
u_t=K(r_t-y_t),
\]

现代闭环策略虽然形式复杂，精神仍然一样。

## 1.2 Sense–Plan–Act 与 Shakey

早期机器人把系统清晰拆成感知、符号世界模型、规划和执行。这种架构的优点是可解释、可验证；缺点是每个模块的误差会传递，而且动态真实世界很难被一个精确符号状态完整描述。

## 1.3 Behavior-Based Robotics

Brooks 的 subsumption architecture 反对先构建完美世界模型再行动，强调并行、反应式行为层。它留下的重要遗产是：**很多智能来自及时闭环，而不是离线推理长度。**

今天所谓 reactive policy 与 deliberative planner 的分层，仍然在重复这个张力。

## 1.4 Classical Robotics 的成熟

20 世纪末到 2010 年代，机器人学形成了非常坚固的数学与系统骨架：SE(3)、运动学、刚体动力学、反馈控制、SLAM、采样规划、轨迹优化、最优控制。这些内容不会因为 VLA 出现而过时。相反，VLA 真正进入真机时仍要面对关节极限、奇异位形、碰撞、接触与稳定性。

## 1.5 Deep Learning 进入机器人

深度视觉首先显著改变 perception；随后深度强化学习和模仿学习将神经网络从“识别器”变为“策略”。关键变化是，不再要求工程师显式规定所有中间变量，而允许网络从数据中形成表征。

代价则是系统更难解释、训练分布更重要、失败模式更隐蔽。

## 1.6 Imitation Learning 与 Demonstration Data

行为克隆把机器人学习写成

\[
\min_\theta \mathbb E_{(o,a)\sim D}[-\log \pi_\theta(a\mid o)].
\]

但 rollout 时状态分布由自己的动作产生，因此会出现 covariate shift。DAgger 的历史意义就在于把“训练分布必须覆盖策略自己会到达的状态”明确写进算法。

## 1.7 Transformer、Action Chunking 与生成式策略

Transformer 解决长序列条件建模后，ACT 等工作把 action chunk 作为基本输出单元；Diffusion Policy 则把动作序列建模成条件生成问题，显著改善多模态动作分布。后续 flow matching、autoregressive action token、hybrid action expert 都是在回答同一个问题：

> 给定当前历史，一个机器人未来一段时间的**动作分布**应该如何表示和高效生成？

## 1.8 从 Language Model 到 VLA

Gato 展示 generalist sequence model；SayCan 将语言模型的语义知识与可执行 affordance 结合；PaLM-E 把连续传感输入送进语言模型；RT-1 强调大规模机器人多任务 Transformer；RT-2 将动作离散成 token，与 web-scale VLM 共同训练，从而正式普及 Vision-Language-Action 这一范式。Google DeepMind 对 RT-2 的定义就是：从视觉和语言输入直接生成机器人动作，并通过 web 与机器人数据联合训练实现更强泛化。

## 1.9 Open X-Embodiment：数据成为主角

2023 年 Open X-Embodiment 将 20 多种机器人、超过百万 episode 汇聚为统一资源，并训练 RT-X 系模型。其意义不只是“数据更多”，而是机器人研究第一次大规模正面处理

\[
D=\bigcup_e D_e
\]

这样一个跨 embodiment 数据混合问题：动作空间、相机、控制频率、任务定义并不天然一致。

## 1.10 Octo 与 OpenVLA：开放基础模型路线

Octo 以 Open X-Embodiment 数据训练 Transformer-based diffusion policy，强调可适配不同观测与动作空间；OpenVLA 则把预训练 VLM 直接改造成 action-token VLA，并开放模型与训练管线。两者共同降低了“通用策略”研究门槛，但也暴露出一个核心问题：数据规模增加后，模型到底学到跨任务机制，还是更强的相似性检索？

## 1.11 π 系列：从 flow action 到 experience learning

Physical Intelligence 的 π 路线把 VLM 与连续 action expert 结合，并逐步把研究焦点从 demonstration scaling 扩展到 open-world generalization、实时 action chunk、记忆和机器人自主经验。

- **π0.5** 强调 open-world generalization 与高低层联合；
- **RTC** 针对大型 VLA 延迟提出 Real-Time Action Chunking；
- **π*0.6** 将 offline RL、demonstration 与真实机器人 autonomous experience 结合；
- **2026 Multi-Scale Embodied Memory** 把长短期记忆显式引入十分钟级任务；
- **π0.7** 通过 richer context conditioning / steering 展示更强组合泛化与 zero-shot cross-embodiment 行为。

这条路线的重要趋势是：**基础策略不再只学习“专家做过什么”，开始学习“自己做过什么、哪里失败、如何被人纠正”。**

## 1.12 GR00T：Humanoid Foundation Model

NVIDIA GR00T N1 将 egocentric human video、真实机器人轨迹、仿真与合成数据混合用于 humanoid foundation model；到 N1.6，架构使用 VLM + 更大的 diffusion transformer，并加入双臂、Agibot 与 Unitree G1 whole-body locomanipulation 等数据。这里的变化标志着 foundation policy 从 tabletop manipulation 进入 whole-body embodiment。

## 1.13 Gemini Robotics：VLA 与 Embodied Reasoning 分层

Gemini Robotics 1.5 明确采用两层 agentic 体系：ER 模型负责物理世界理解、工具调用和多步规划，VLA 负责 motor action；Gemini Robotics 2 又推进到 full humanoid whole-body control、dexterity、multi-robot collaboration 与 on-device adaptation。

这说明“一个模型端到端解决一切”并不是唯一收敛方向。高层 reasoning 与低层实时 policy 重新形成模块化分工。

## 1.14 Helix 与通用人形控制

Figure 的 Helix 体现另一种工程取向：统一视觉、语言与高频连续 upper-body control，并展示双机器人协作。后续 human-video pretraining 又将数据源从 robot-only 扩张到人类第一视角视频。

## 1.15 World Model 与 JEPA 的回归

World model 并不是 2025 年才出现的概念，但视频自监督和 latent predictive learning 使它重新成为中心问题。V-JEPA 2 使用大规模视频学习 latent prediction；action-conditioned 版本再用少量机器人交互数据做规划。V-JEPA 2.1 进一步强调 temporally consistent dense features。

这条路线挑战纯 reactive VLA：如果一个模型只会直接输出动作，却无法预测“这样做以后会发生什么”，它是否真的拥有足够的物理世界模型？

## 1.16 2026 年的研究主矛盾

截至 2026-09，具身智能的中心问题已经从“能不能让机器人做任务”转向：

1. **真正的组合泛化**：新任务是否能由已有机制重组，而非近邻记忆？
2. **经验学习**：机器人 rollout 后如何高效更新自己？
3. **长时记忆**：十分钟、数小时、数月的经验如何影响当前决策？
4. **跨本体**：知识怎样独立于特定关节与 action space？
5. **whole-body intelligence**：行走、平衡、双手与操作能否统一？
6. **预测与因果**：模型是否理解动作造成的物理结果？
7. **实时性与可靠性**：大模型怎样成为稳定控制系统的一部分？
8. **评测**：怎样证明改进来自机制而不是更多数据、更多参数或更宽松场景？

这些问题构成本书余下各卷的主线。

---

## 本卷小结

如果只记住一句话，请记住：

\[
\boxed{\text{Embodied Intelligence is closed-loop intelligence under physical constraints.}}
\]

模型、数据、控制器、身体、环境和时间必须同时进入分析。

## 核心来源与延伸阅读

1. Wiener, *Cybernetics*.
2. Brooks, “Intelligence without Representation,” 1991.
3. Gibson, *The Ecological Approach to Visual Perception*.
4. Lynch & Park, *Modern Robotics* — https://modernrobotics.northwestern.edu/
5. Google DeepMind, RT-2 — https://deepmind.google/blog/rt-2-new-model-translates-vision-and-language-into-action/
6. Google DeepMind, Open X-Embodiment / RT-X — https://deepmind.google/blog/scaling-up-learning-across-many-different-robot-types
7. Octo — https://octo-models.github.io/
8. OpenVLA — https://openvla.github.io/
9. Physical Intelligence research — https://www.pi.website/
10. NVIDIA GR00T N1.6 — https://research.nvidia.com/labs/gear/gr00t-n1_6/
11. Google DeepMind, Gemini Robotics 2 — https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
12. Figure, Helix — https://www.figure.ai/news/helix
13. Meta, V-JEPA 2 — https://ai.meta.com/research/vjepa/
