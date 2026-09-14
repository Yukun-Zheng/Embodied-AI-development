# Part 1　思想史与技术史：从控制论到机器人基础模型

## 学习目标

本章不是背年份，而是理解具身智能反复出现的五组张力：**反馈 vs 离线规划、显式模型 vs 端到端学习、符号 vs 连续控制、模块化 vs 通用模型、离线数据 vs 自主经验。**

---

## 1.1 控制论：智能首先是反馈

控制论把 sensing、communication、feedback 放到统一系统中。经典误差反馈：

\[
u_t=K(r_t-y_t).
\]

它留下最重要的思想是：系统不能只“算一次答案”，而要观察动作结果并继续修正。

今天的 closed-loop VLA、receding-horizon action chunk、MPC、tactile reflex，本质都延续反馈思想。

## 1.2 Sense–Plan–Act

早期机器人把系统分成：感知世界 → 建模 → 规划 → 执行。优点是职责清晰、可验证；缺点是动态世界中，等完整 world model 建好再行动可能已经过时，而且模块误差逐级传播。

## 1.3 Behavior-Based Robotics

Brooks 等工作反对“先拥有完整符号世界再行动”，强调实时、分层、反应式行为。它提出的挑战到今天仍存在：

> 智能究竟来自更深的内部模型，还是来自高质量的 perception–action feedback？

现代系统往往重新走向混合：低层 reactive，高层 deliberative。

## 1.4 Classical Robotics 的成熟

1980s–2010s 逐渐形成稳定骨架：

- SO(3)/SE(3) 与刚体几何；
- FK/IK/Jacobian；
- rigid-body dynamics；
- feedback / optimal control；
- SLAM；
- sampling-based planning；
- trajectory optimization。

这些并没有被深度学习替代。现代 foundation policy 真正部署时仍必须遵守同样的几何、动力学和安全约束。

## 1.5 深度学习首先改变 Perception

大规模 CNN/ViT 让识别、检测、分割、视觉表示显著增强。机器人由手工 feature 逐渐转向 learned representation。

但 perception score 与 robot success 并非单调等价：物理任务更需要 geometry、motion、contact、affordance。

## 1.6 Deep RL 与 Imitation 进入控制

深度 RL 让策略从高维 state/image 直接产生 action；imitation learning 利用 demonstration 绕开 reward/exploration 难题。

BC 的核心缺陷是 covariate shift，DAgger 明确指出训练数据必须覆盖 learner 自己访问的状态。

## 1.7 Simulation Scaling

GPU/并行 simulator 让数千环境同时 rollout，推动 locomotion、dexterous RL、domain randomization。仿真成为机器人 learning 的“数据中心”，但也形成新的风险：研究者开始优化 simulator-specific reward，而不是现实能力。

## 1.8 Transformer 进入 Robot Learning

Transformer 带来统一 sequence interface：图像、语言、状态、动作都可 token/embedding 化。Action Chunking Transformer、generalist sequence model 等路线由此出现。

真正贡献不是“attention 等于智能”，而是可扩展地建模多模态历史与未来动作序列。

## 1.9 语言模型进入机器人

SayCan 将语言 plausibility 与 affordance/value 相乘；PaLM-E 将 sensor embedding 注入大语言模型；Gato 展示多领域统一 sequence model。

这形成一个新问题：互联网语义知识能否迁移成 physical action competence？

## 1.10 RT-1 / RT-2

RT-1 展示大规模真实机器人多任务 Transformer；RT-2 进一步将 VLM 与机器人 action co-training，把动作离散成 token，使 web-scale视觉语言知识进入直接 robot control。

从此 Vision-Language-Action 成为主流术语。

## 1.11 Open X-Embodiment

Open X-Embodiment 将多实验室、多机器人数据汇聚为统一 corpus。技术意义不只在“更多数据”，而在首次大规模面对跨机器人异质性：不同 camera、action、frequency、morphology、task schema 如何共同训练？

## 1.12 Octo / OpenVLA：开放化

Octo 以 Transformer + diffusion policy 做开放 generalist policy；OpenVLA 让 VLM→action-token VLA 的训练与权重更可审计。

开放模型使研究从“看公司 demo 猜机制”转向可真正做 architecture/data/action ablation。

## 1.13 π 系列：连续 Action Expert 与经验学习

π0 用 VLM + flow-matching continuous action expert；π0.5 强调 open-world；RTC 处理推理 latency；π*0.6 将 autonomous experience / RL 带入 post-training；2026 的 embodied memory、online RL、π0.7 则把长期记忆、steerability 与新组合泛化推到中心。

趋势：机器人 foundation policy 从“拟合 demonstration”走向“吸收自己的经验”。

## 1.14 GR00T / Gemini Robotics / Helix

GR00T 将 human video、simulation、real robot 数据用于 humanoid foundation model，并继续走向 loco-manipulation；Gemini Robotics 把 embodied reasoning 与 VLA 分层，并在 Robotics 2 进入 whole-body、dexterity、multi-robot、on-device；Helix 展示 industrial humanoid 的统一 upper-body VLA 路线。

2026 的问题已不再是“机械臂能否 follow language”，而是完整身体、长时任务、跨本体与可靠性。

## 1.15 World Model 的回归

World model 从来不是新概念，但 JEPA/video prediction/latent dynamics 使问题重新中心化：机器人是否应该只学 \(o\to a\)，还是应该先学“动作后世界如何变化”？

V-JEPA 2/2.1、robot video world models、world-action models 都在探索预测与控制的关系。

## 1.16 历史中的循环

机器人史不断在以下两端摆动：

```text
explicit world model ←→ reactive policy
modular systems       ←→ end-to-end models
symbolic abstraction  ←→ dense continuous representation
hand-designed priors  ←→ data scaling
offline planning      ←→ online feedback
```

成熟系统往往不是一端彻底胜利，而是重新找到更好的分工边界。

## 1.17 读历史的正确方法

每篇经典工作只记录四件事：

1. 前一代什么假设失败？
2. 它引入什么新计算机制？
3. 在什么实验上证实？
4. 新机制又留下什么失败？

这样历史变成“问题谱系”，而不是论文年表。

## 小练习

选择 RT-2、Diffusion Policy、V-JEPA 2 三条路线，各画一张“它反对/补充上一代什么假设”的因果图。不要比较 benchmark 分数，比较**问题定义**。
