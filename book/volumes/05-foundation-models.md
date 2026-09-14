# Volume V　Robot Foundation Models：从 VLM 到 VLA

> **Frontier snapshot: 2026-09-14.**
>
> 本卷是 Part 22–26 的连续通读版。目标不是背模型，而是理解 foundation robotics 的五个核心接口：**semantic grounding、robot data、action generation、temporal execution、embodiment adaptation**。

---

# Part 22　语言、多模态基础模型与 Physical Grounding

## 22.1 Language 为什么进入机器人

语言可以承担四种角色：

1. **任务接口**：用户说“把杯子放进水槽”；
2. **抽象状态**：记录“杯子已经洗过”；
3. **规划空间**：把长任务分成 subtask；
4. **知识载体**：把 web-scale 常识迁移到物理任务。

但语言不是 motor command。

最终必须落到：

```text
object / region
→ geometry
→ affordance
→ trajectory
→ contact
→ controller
```

所以：

\[
\text{semantic correctness}\not\Rightarrow\text{physical executability}.
\]

## 22.2 从 CLIP/VLM 到 Physical Grounding

VLM 能提供：

- open-vocabulary recognition；
- semantic relation；
- language-conditioned attention；
- commonsense prior。

机器人还需要：

- pose；
- metric geometry；
- reachability；
- material/contact；
- temporal progress；
- uncertainty。

Physical grounding 至少跨四层：

```text
semantic
→ spatial
→ temporal
→ motor / physical
```

例如“轻轻放下杯子”不是一个语言标签，而最终要求 velocity / force / termination condition。

## 22.3 VLM 的天然缺口

一个模型可以正确回答：

> “这个杯子放在桌子边缘可能会掉。”

却未必能预测：

\[
p(s_{t+1}\mid s_t,do(a_t))
\]

也未必能给出稳定抓取。

因此本书始终区分：

- **descriptive physical knowledge**；
- **actionable physical state**；
- **interventional dynamics knowledge**。

---

# Part 23　VLA 的形成：2022–2024

## 23.1 Gato：统一序列接口

Gato 展示一个 Transformer 可以统一处理不同 modality/task 的 token sequence。

它为后续 generalist robot model 提供的是：

> **统一接口 + scaling imagination**，而不是高精度机器人控制答案。

## 23.2 SayCan：Language × Affordance

SayCan 把语言模型对 skill 的语义可行性与 robot skill value 结合：

\[
Score(skill)
\propto
P(skill\mid instruction)\cdot V(skill\mid state).
\]

这是一个长期有效的思想：

> “应该做什么”与“当前身体做不做得到”必须同时考虑。

## 23.3 PaLM-E：Sensor Token 进入语言模型

PaLM-E 把 embodied sensor embedding 注入大型语言模型，使 language model 可以处理连续 observation context。

它把问题推进到：

```text
multimodal observation
→ foundation representation
→ reasoning / planning
```

但仍不等于直接 motor control。

## 23.4 RT-1：多任务真实机器人 Transformer

RT-1 证明了大量真实 robot demonstration + multi-task Transformer 可以扩展 visuomotor competence。

关键变量：

- real robot data；
- task diversity；
- tokenized action；
- shared policy。

## 23.5 RT-2：Vision-Language-Action

RT-2 将 web-scale VLM pretraining 与 robot action data co-finetune，并把 action 表示成模型可输出的 token。

形成经典 VLA recipe：

```text
pretrained VLM
+ robot demonstrations
+ compatible action representation
→ VLA
```

但 web knowledge 不等于 contact/dynamics understanding。

## 23.6 Open X-Embodiment / RT-X

跨实验室 robot dataset mixture 使问题从：

```text
one robot, many tasks
```

推进到：

```text
many robots, many tasks
```

数据可写成：

\[
D=\bigcup_e D^{(e)}.
\]

真正困难是不同 embodiment 的：

- action dimension；
- camera layout；
- control rate；
- normalization；
- controller semantics。

## 23.7 Octo

Octo 代表开放 generalist policy：大规模 heterogeneous robot data、task conditioning 与 generative action head。

它的重要价值是**开放可复现**，使 cross-dataset generalist robot policy 变成社区研究对象。

## 23.8 OpenVLA

OpenVLA 将开放 VLM stack 接到 robot action token，并公开训练、fine-tuning 与 deployment 路径。

当前源码可从：

```text
vla-scripts/train.py
vla-scripts/finetune.py
vla-scripts/deploy.py
prismatic/models/
prismatic/training/
prismatic/vla/
```

直接追踪 VLM → action 的真实工程链。

## 23.9 2024 的共同模板

```text
RGB / language / robot state
        ↓
multimodal backbone
        ↓
action representation / action head
        ↓
action chunk
        ↓
low-level controller
```

从 2025 开始，主要分歧不再只是 backbone，而转向 action、time、embodiment、experience 和 whole-body。

---

# Part 24　VLA 第二阶段：2024–2026

## 24.1 π0：Continuous Action Expert

π0 将 pretrained VLM 与 flow-matching continuous action expert 组合：

\[
h=f_{VLM}(o,l,s),
\qquad
v_\theta(a_\tau,\tau,h).
\]

这使 continuous robot geometry 不必完全被离散 token 化。

## 24.2 FAST：Action Tokenization 仍然重要

离散路线并没有消失。

FAST 类方法研究：

\[
\text{trajectory compression}
\leftrightarrow
\text{precision}
\leftrightarrow
\text{sequence length}.
\]

所以 action tokenizer 本身就是模型设计。

## 24.3 π0.5：Open-World Generalization

Open-world 不应只指“新物体”。

应拆成：

```text
novel object
novel scene
novel instruction
novel task composition
novel embodiment
novel physical perturbation
```

一个 policy 可能只在其中两项 generalize。

## 24.4 Real-Time Action Chunking / Async Inference

大模型 latency 使动作执行出现：

\[
a_t=\pi(o_{t-k}),\quad k>0.
\]

RTC / async execution 将 inference 与 action execution 解耦，使 temporal executor 成为独立系统模块。

这意味着：

\[
\text{policy}\neq\text{executor}.
\]

## 24.5 π*0.6：Learning from Experience

foundation policy 开始系统吸收自己的 on-robot experience：

```text
pretraining
→ demonstration adaptation
→ autonomous rollout
→ reward / correction
→ RL post-training
```

研究问题从“能不能模仿”变成“部署后能不能继续变好”。

## 24.6 Multi-Scale Embodied Memory

长任务要求 persistent memory。

可分：

- short-term sensorimotor；
- working memory；
- episodic memory；
- semantic memory；
- spatial memory。

真正问题是：

\[
\text{what to store? what to retrieve? when to forget?}
\]

## 24.7 π0.7：Steerability

context 不再只是 task name：

```text
language coaching
visual subgoal
metadata
control modality
```

可以进一步 steer policy“怎样做”。

需要用 wrong-coaching / composition-held-out 等负对照验证所谓 emergent capability。

## 24.8 GR00T N1 → N1.5

GR00T 将 foundation policy 明确推向 humanoid / bimanual / cross-embodiment。

N1.5 继续强化：

- embodiment adaptation；
- post-training；
- future-latent / representation alignment；
- human / synthetic / robot data mixture。

## 24.9 GR00T N1.6

**官方 GitHub release `n1.6-release` 发布于 2026-04-15。**

N1.6 延伸：

- stronger VLM / visual representation；
- larger generative action component；
- humanoid / bimanual data；
- loco-manipulation / whole-body direction。

它不属于 2025 时间线。

## 24.10 GR00T N1.7

**官方 `n1.7-release` 发布于 2026-04-18；当前 Isaac-GR00T 仓库将 N1.7 描述为 latest / General Availability line。**

N1.7 很适合源码教学，因为开放栈显式暴露：

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py
gr00t/data/embodiment_tags.py
getting_started/policy.md
getting_started/real_world_deployment.md
```

官方 README 说明其新 VLM backbone 为：

```text
Cosmos-Reason2-2B
(Qwen3-VL architecture)
```

并提供 `nvidia/GR00T-N1.7-3B`、benchmark example、real deployment、PyTorch/TensorRT 路径。

### 为什么这比“新 checkpoint”更重要

它让研究者能从源码追：

```text
embodiment tag
→ processor
→ VLM representation
→ action head
→ action horizon
→ async inference / RTC
→ deployment runtime
→ controller
```

所以现代 robot foundation system 已经无法只用“backbone + action head”描述。

## 24.11 Gemini Robotics：Reasoning 与 Motor 分层

可以抽象为：

```text
embodied reasoning
  ↓ subgoal / plan / progress
VLA / motor policy
  ↓
controller
```

重新体现经典 hierarchical robotics，只是高层和低层都变成 foundation model / learned policy。

## 24.12 Gemini Robotics 2 / On-Device 2

2026 年路线进一步覆盖：

- whole-body humanoid；
- dexterous manipulation；
- multi-robot collaboration；
- long-horizon embodied reasoning；
- on-device inference；
- faster new-embodiment adaptation。

on-device foundation robotics 本质上是：

\[
\text{model}\times\text{compute}\times\text{latency}\times\text{power}\times\text{control}.
\]

## 24.13 Helix / Helix 02

Helix 特别适合说明 multi-rate architecture：

```text
slow semantic system
        ↓ latent intent
fast visuomotor system
        ↓
continuous control
```

Helix 02 再扩展到 full-body loco-manipulation。

大模型没有消灭 control frequency，反而让不同时间尺度的职责划分更重要。

## 24.14 OpenVLA / SmolVLA / LeRobot 开放栈

LeRobot 当前源码把：

```text
datasets
policies
robots
motors
cameras
async_inference
RTC
```

放在统一框架中。

这让研究从“模型 checkpoint”推进到**完整 robot learning system**。

## 24.15 3D / Dexterous / Whole-Body 分支

foundation policy 正同时碰到四个难题：

\[
\text{semantic generality}
+
\text{geometric precision}
+
\text{high-dimensional action}
+
\text{real-time feedback}.
\]

单纯扩大 VLM 并不能保证四项共同成立。

---

# Part 25　VLA 的内部机制

## 25.1 最小计算图

```text
vision
language
proprioception
embodiment
      ↓
multimodal representation
      ↓
action generator
      ↓
action chunk
      ↓
temporal executor
      ↓
controller
```

分析 VLA 必须沿这条链逐层追，而不是只看 Transformer block。

## 25.2 Vision Encoder

问题不是“用 ViT 还是 CNN”，而是 representation 是否保留：

- geometry；
- contact-relevant cues；
- object identity；
- temporal motion；
- uncertainty。

一个 classification-strong feature 可能 motor-useless。

## 25.3 Language Backbone

语言提供：

- semantic prior；
- instruction parsing；
- compositional structure；
- planning context。

但动作梯度可能扰动 language representation，因此出现：

- frozen backbone；
- partial unfreezing；
- separate expert；
- adapter；
- knowledge insulation。

## 25.4 Proprioception / Embodiment

真实 state 至少包含：

\[
q,\dot q,\text{gripper},\text{base state},\text{contact / IMU when available}.
\]

跨本体还需 explicit embodiment descriptor/tag 或隐式 robot-specific statistics。

研究问题：tag 是 morphology knowledge，还是 dataset ID？

## 25.5 Action Generator

主要路线：

```text
regression
AR tokens
Diffusion
Flow matching
DiT / continuous expert
hybrid
```

比较时必须匹配：

- data；
- horizon；
- parameter budget；
- controller；
- policy rate。

## 25.6 Dataset Mixture 是模型的一部分

训练分布：

\[
p(D)=\sum_k\alpha_k p(D_k).
\]

不同 mixture weight 会改变模型学到的 representation 和 action prior。

所以 data sampler 不是“工程细节”。

## 25.7 Post-Training

现代 foundation policy 越来越采用：

```text
large pretraining
→ robot / task post-training
→ optional online experience / RL
```

应分别报告每阶段数据与 compute。

## 25.8 Temporal Executor

大模型常输出 chunk，但机器人逐步执行。

需要区分：

- model rate；
- action rate；
- low-level control rate；
- chunk horizon；
- queue / buffer；
- action age；
- async replacement。

很多所谓“model failure”其实来自 executor。

## 25.9 Low-Level Controller 没有消失

VLA 可能输出：

```text
joint target
Cartesian delta
target pose
whole-body target
```

后面仍有：

```text
IK / impedance / WBC / safety filter / servo
```

没有 controller information 的 VLA comparison 不完整。

## 25.10 VLA Failure Taxonomy

建议至少拆：

```text
semantic
object grounding
geometry
state estimation
planning
motion generation
latency
contact
controller
recovery
```

总体 success 提升只有在知道哪类 failure 减少时才产生机制知识。

---

# Part 26　机器人数据、人类视频与 Cross-Embodiment

## 26.1 Robot Data 是模型的一部分

episode 不只包含：

\[
(o_t,a_t).
\]

还隐含：

- controller；
- action frequency；
- frame convention；
- robot morphology；
- operator style；
- reset distribution。

这些都决定可学分布。

## 26.2 Dataset Mixture

多源数据：

\[
p(D)=\sum_e\alpha_e p(D_e).
\]

必须报告：

- source weight；
- transition count；
- task/robot diversity；
- action conversion；
- normalization。

## 26.3 Human Video

human video 提供：

- semantic task structure；
- object interaction order；
- hand-object cue；
- affordance；
- motion prior。

但缺失 robot action：

\[
I_{1:T}^{human}\not\Rightarrow a_{1:T}^{robot}.
\]

因此 human-to-robot transfer 需要 latent alignment、retargeting、inverse dynamics 或 robot-data anchor。

## 26.4 Synthetic Data

可来自：

- simulator expert；
- motion retargeting；
- procedural scenes；
- world model；
- privileged-state planner。

关键不是“synthetic 是否真实”，而是哪一类变量可信。

## 26.5 Cross-Embodiment

真正强 transfer 应逐级测试：

1. same robot, new task；
2. new robot, same morphology family；
3. new morphology；
4. changed sensor layout；
5. changed action topology。

同时报告 adaptation budget：

\[
B=(N_{demo},N_{interaction},N_{updates},T_{wall}).
\]

## 26.6 Universal Action Representation

可能的共享空间：

- Cartesian end-effector delta；
- object-relative effect；
- latent skill；
- task-space goal；
- morphology-conditioned action decoder。

不存在一个天然对所有 robot 都正确的 universal action space。

---

# 本卷总结：Foundation Robotics 的真正结构

到 2026-09-14，机器人基础模型已经不能简化成：

```text
big VLM + action head
```

更准确的是：

```text
Internet / human / robot / synthetic data
              ↓
multimodal representation
              ↓
state + embodiment + memory
              ↓
action generator
              ↓
temporal executor
              ↓
robot-specific controller
              ↓
physical interaction
              ↓
experience / failure / post-training
              ↺
```

真正的研究前沿不是“哪个品牌模型更大”，而是这些接口能否被统一、验证并跨任务、跨场景、跨身体长期工作。

源码级阅读入口见 [`../../references/SOURCE_CODE_ATLAS.md`](../../references/SOURCE_CODE_ATLAS.md)。
