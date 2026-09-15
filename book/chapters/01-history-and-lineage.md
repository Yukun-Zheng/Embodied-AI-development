# Part 1　思想史与技术史：从控制论到机器人基础模型

## 学习目标

本章不是背年份，而是理解具身智能反复出现的五组张力：**反馈 vs 离线规划、显式模型 vs 端到端学习、符号 vs 连续控制、模块化 vs 通用模型、离线数据 vs 自主经验。**

真正会读技术史，不是能列出模型版本，而是能解释：前一代什么假设失效、下一代改了哪一个计算对象或系统接口、实验究竟支持了多强的结论。

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

重要的是不要把它简化成“旧式模块化失败了”。在安全、工业机器人和 whole-body system 中，perception / planning / controller / safety boundary 仍然必须被工程化区分。

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

RT-1 展示大规模真实机器人多任务 Transformer；RT-2 进一步将 VLM 与机器人 action co-training，把动作离散成 token，使 web-scale 视觉语言知识进入直接 robot control。

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

GR00T 将 human video、simulation、real robot 数据用于 humanoid foundation model，并继续走向 loco-manipulation；Gemini Robotics 把 embodied reasoning 与 VLA 分层，并在 Robotics 2 进入 whole-body、dexterity、multi-robot、on-device；Helix 展示 industrial humanoid 的 multi-rate foundation-policy 路线。

截至本书 2026-09-14 的冻结截面，GR00T N1.7 已进入公开源码主线。本书不把版本号本身当科学进步，而追踪 backbone、action expert、embodiment interface、executor 与 controller 的机制变化。

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

## 1.17 版本演进不等于科学问题演进

同一条产品/模型线可以连续发布多个版本，但科学分析应换一套坐标轴：

```text
What changed?
├─ data coverage
├─ representation / backbone
├─ action representation
├─ objective / post-training
├─ temporal executor
├─ embodiment interface
├─ low-level controller
└─ evaluation protocol
```

如果一个新版本同时更换数据、模型、controller 和 benchmark，单纯观察 success 提升不能归因“新架构有效”。

反过来，两个名字完全不同的系统也可能在机制上高度相似，例如都采用：

```text
slow semantic model
→ latent goal / context
→ fast motor expert
→ conventional low-level controller
```

所以历史学习的单位应该是**机制与接口**，而不是品牌。

## 1.18 证据等级随历史阶段变化

前沿技术常先经历：

```text
concept claim
→ curated demo
→ official benchmark
→ paper / technical report
→ public code / checkpoint
→ independent reproduction
→ cross-lab real-world evidence
```

不能把这几层证据混成一句“已经证明”。教材对 2025–2026 系统尤其需要区分：官方公开结果、论文证据、开放源码和独立复现。

## 1.19 读历史的常见失败

### Survivorship bias

今天被反复引用的方法不一定是当年唯一合理路线。只看成功谱系，会误以为技术演进是线性的。

### Hindsight bias

知道 Transformer/VLA 后再读早期工作，很容易把所有历史都解释成“等待大模型”。实际上许多限制来自传感器、计算、数据、控制硬件与实验基础设施。

### Rename bias

把旧问题换成新名字后误认为是全新科学对象，例如：

- world model ↔ learned dynamics / model-based control；
- memory ↔ belief / persistent task state；
- embodied reasoning ↔ planning + state tracking + feedback；
- whole-body VLA ↔ semantic policy + whole-body control。

新计算工具确实改变可扩展性，但问题谱系必须连续阅读。

### Demo bias

工业系统往往先公开最成功的能力。历史记录必须区分“首次展示”“系统化评测”“开放复现”。

## 最小实验：做一次机制谱系审计

任选一个今天的系统，例如 OpenVLA、GR00T N1.7、V-JEPA 2.1：

1. 从 `references/TIMELINE.md` 向前追 3–5 个祖先节点；
2. 每个节点只写 `problem → mechanism → evidence → failure`；
3. 把模型名全部删掉，只保留机制描述；
4. 检查读者是否仍能理解为什么下一代出现。

输出示例：

```text
single-step BC
→ covariate shift
→ dataset aggregation / chunking
→ latency & stale actions
→ asynchronous execution / RTC-like mechanism
```

若删除品牌名后逻辑断裂，说明你记住的是 timeline，不是技术史。

## 研究问题

1. 机器人基础模型时代，模块化与 end-to-end 的新最优边界在哪里？
2. 哪些“新能力”来自 architecture，哪些只是 data / simulator / hardware scaling 首次让旧思想可运行？
3. 当 foundation model 与经典 controller 强耦合时，论文应如何分配 capability credit？
4. autonomous experience 是否会把机器人学习从静态 dataset paradigm 再次推回 cybernetic continual feedback？
5. 下一个真正的范式变化，需要引入新的数学对象，还是更强的 physical-system interface 就足够？

## Source anchors / 原始来源

- Wiener, *Cybernetics*（反馈、控制与通信的历史起点之一）: https://mitpress.mit.edu/9780262730099/cybernetics/
- Brooks, “A Robust Layered Control System for a Mobile Robot,” 1986: https://doi.org/10.1109/JRA.1986.1087032
- Brooks, “Intelligence without Representation,” 1991: https://doi.org/10.1016/0004-3702(91)90053-M
- Open X-Embodiment Collaboration, 2023: https://arxiv.org/abs/2310.08864
- Brohan et al., RT-2, 2023: https://arxiv.org/abs/2307.15818
- Meta V-JEPA 2 / 2.1 official code: https://github.com/facebookresearch/vjepa2
- 本书跨年代证据索引：[`references/TIMELINE.md`](../../references/TIMELINE.md) 与 [`references/READING_MAP.md`](../../references/READING_MAP.md)。

## 本章结论

技术史不是版本号序列，而是**失败假设 → 新机制 → 新证据 → 新失败**的循环。具身智能今天看似被 foundation models 重新定义，但 feedback、geometry、state、planning、control、data coverage 与 physical deployment 这些核心矛盾从未消失。
