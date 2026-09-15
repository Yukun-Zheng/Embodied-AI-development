# Part 25　VLA 的内部机制：它到底学到了什么

## 学习目标

本章不问“VLA benchmark 分数多少”，而问：

> 从图像和语言进入网络，到电机最终动作，中间究竟形成了什么信息瓶颈？

你应该能够沿着一次 rollout，指出每个变量的语义、shape、时间尺度和可能失效的位置。

---

## 25.1 一个最小 VLA 计算图

设：

- 图像 \(I_t\)；
- 语言指令 \(l\)；
- 本体状态 \(s_t\)；
- 历史窗口 \(H_t\)；
- 动作块 \(A_t = [a_t,\dots,a_{t+K-1}]\)。

最小形式：

\[
z_t=f_\phi(I_t,l,s_t,H_t),
\]

\[
A_t\sim p_\theta(A\mid z_t).
\]

真实系统则是：

```text
cameras ─┐
         ├─> preprocess ─> vision encoder ─┐
language ─> tokenizer ─> language backbone ├─> fusion ─> action expert
state  ──> state encoder ───────────────────┘          ↓
                                                action chunk
                                                     ↓
                                               temporal executor
                                                     ↓
                                               robot controller
                                                     ↓
                                               physical world
                                                     ↺
```

任何论文如果没有把最后三层讲清楚，读者就不能从 architecture diagram 判断真实闭环行为。

---

## 25.2 Vision Encoder：看见了什么

视觉 encoder 可能来自：

- internet image pretraining；
- VLM joint training；
- robot-image pretraining；
- egocentric human video；
- self-supervised video representation；
- 3D / point cloud encoder。

必须区分三种表示需求：

### 语义

“这是杯子、抽屉、衣服。”

### 几何

“把手距离夹爪 4 cm，朝向偏 12°。”

### 动力学/可操作性

“这个角度推会滑，那个边缘可以形成稳定接触。”

VLM 视觉表征擅长语义并不自动意味着后两项足够。

### 可证伪测试

固定 action head，分别替换视觉 backbone；除 success 外测：

- pose sensitivity；
- occlusion robustness；
- small-object precision；
- contact onset prediction；
- perturbation recovery。

---

## 25.3 Language Backbone：语义先验如何进入动作

语言 backbone 主要带来：

- object / concept semantics；
- compositional instruction understanding；
- commonsense task prior；
- open-vocabulary grounding。

但 language token 并不天然含有机器人学单位。

例如：

> “轻轻放下杯子”

真正执行必须映射成：

- lower approach velocity；
- lower normal force；
- release timing；
- collision constraints。

所以 semantic intent 必须经过 physical grounding。

---

## 25.4 Proprioception Encoding

机器人 state 常包括：

\[
s_t=[q_t,\dot q_t,g_t,T_t^{ee},f_t,\dots].
\]

常见错误是把这些量简单拼接后送入 MLP，却不考虑：

- 不同量纲；
- 不同坐标系；
- 不同频率；
- 关节 topology；
- embodiment-specific dimension。

跨机器人 VLA 的难点之一正是：

\[
\dim s^{(i)} \neq \dim s^{(j)}.
\]

如果 state interface 没有结构，所谓 cross-embodiment 往往只是多套 adapter 的组合。

---

## 25.5 Multimodal Fusion

典型方式包括：

- early concatenation；
- cross-attention；
- shared token sequence；
- latent query；
- hierarchical slow/fast fusion。

最关键的问题不是 attention map 好不好看，而是：

> 动作梯度能否真正改变任务相关视觉/语言表征？

如果 backbone 冻结，action head 只能读取已有特征；如果端到端 joint training，动作信号可能改善 physical relevance，也可能破坏 internet-scale semantic knowledge。

---

## 25.6 Knowledge Insulation 与 Gradient Interference

设总损失：

\[
\mathcal L=\mathcal L_{VL}+\lambda\mathcal L_{action}.
\]

两个梯度可能方向一致，也可能冲突：

\[
\cos(\nabla \mathcal L_{VL},\nabla \mathcal L_{action})<0.
\]

这解释了为什么一些系统选择：

- frozen VLM；
- adapter；
- action expert；
- partial fine-tuning；
- alternating objective。

“知识隔离”不是架构美学，而是在保护 semantic prior 与学习 motor precision 之间做优化折中。

---

## 25.7 Action Expert / Head

Action head 可能输出：

### 离散 token

\[
p(a_i\mid a_{<i},z)
\]

### 直接回归

\[
\hat A=f_\theta(z)
\]

### Diffusion

\[
\epsilon_\theta(A^k,k,z)
\]

### Flow Matching

\[
v_\theta(A_\tau,\tau,z)
\]

不同生成目标产生不同 inductive bias：

- AR：顺序概率建模自然，但 latency 随 token 数增长；
- regression：最快，但容易平均多模态行为；
- diffusion：多模态强，但多步采样成本高；
- flow：连续生成与少步积分之间折中。

---

## 25.8 State / Action Tokenization

离散化会引入量化误差：

\[
e_q=\|a-Q(a)\|.
\]

但连续动作也不是“原始物理动作”：模型通常仍在某个规范化 action space 中学习，例如：

\[
a_t=[\Delta x,\Delta y,\Delta z,\Delta r,g].
\]

真正到硬件前还会经过：

```text
policy output
→ de-normalize
→ frame transform
→ workspace clip
→ IK / controller
→ joint target
→ servo
→ motor current
```

因此论文里的 action space 只是控制链的一层。

---

## 25.9 Dataset Mixture 其实也是模型的一部分

若多数据源分布为 \(D_i\)，训练目标：

\[
\mathcal L=\sum_i w_i\,\mathbb E_{x\sim D_i}[\ell(x)].
\]

权重 \(w_i\) 会直接决定模型“更像哪种机器人、哪类任务”。

需要考虑：

- dataset size imbalance；
- task difficulty imbalance；
- embodiment imbalance；
- success-only bias；
- camera convention；
- action convention。

所以 dataset recipe 不应被当作 appendix 里的工程细节。

---

## 25.10 Post-Training

现代 VLA 越来越像 LLM：预训练后还有多层 post-training。

```text
foundation pretraining
→ supervised robot fine-tuning
→ embodiment adaptation
→ preference / reward / RL
→ deployment experience
```

科学比较模型时必须标出究竟比较的是：

- base checkpoint；
- task-finetuned；
- embodiment-finetuned；
- RL-post-trained；
- on-robot adapted。

否则“架构 A > 架构 B”可能只是 post-training budget 不同。

---

## 25.11 Embodiment Conditioning

一个更一般的 policy 应写成：

\[
\pi(a\mid o,l,e),
\]

其中 \(e\) 描述 embodiment。

可能包含：

- joint graph；
- link geometry；
- actuator limits；
- sensor layout；
- end-effector type；
- action topology。

若只给 robot ID，模型最多学到一个 lookup embedding；若给结构化 morphology，才有机会对 unseen embodiment 做组合泛化。

---

## 25.12 Low-Level Controller 没有消失

VLA 输出常常不是 torque，而是：

- target pose；
- delta pose；
- joint position target；
- velocity target；
- high-level skill。

下游仍需要：

\[
\tau=K_p(q_d-q)+K_d(\dot q_d-\dot q)+g(q),
\]

或 impedance / WBC / safety filter。

这意味着“VLA 成功率”是上层 policy 与下层 control stack 的联合结果。

---

## 25.13 Latency、Chunking 与闭环频率

设推理延迟 \(T_m\)，动作执行周期 \(T_c\)。如果：

\[
T_m \gg T_c,
\]

就必须采用：

- action chunk；
- asynchronous inference；
- temporal ensembling；
- real-time chunk replacement；
- slow/fast hierarchy。

最危险的情况不是“模型慢一点”，而是：

> 新 observation 已经说明世界改变，但旧 action chunk 仍在执行。

这本质上是 stale policy problem。

---

## 25.14 Language Following 与 Motor Precision 的张力

大模型擅长 broad semantics，小 policy 擅长 local precision。

可以把矛盾写成：

\[
\text{generality}\uparrow
\quad\text{vs}\quad
\text{control bandwidth / precision}\uparrow.
\]

多时间尺度架构之所以反复出现，不是偶然：它在系统结构上承认这两个目标可能需要不同模型和频率。

---

## 25.15 VLA Failure Taxonomy

建议统一成九类：

1. semantic misunderstanding；
2. grounding error；
3. geometry error；
4. state estimation error；
5. action generation error；
6. latency / stale action；
7. contact / dynamics mismatch；
8. low-level control failure；
9. recovery / memory failure。

只有分清 failure source，ablation 才有意义。

---

## 25.16 VLA 是否学到了物理规律

不要问“模型会不会推门”，而应设计干预：

- 改质量但不改视觉；
- 改摩擦；
- 改 hinge 位置；
- 改对象尺度；
- 改动力学但保持 texture；
- 反事实交换视觉相关性。

若策略仅依赖表面视觉模式，性能会在这些 intervention 下崩溃。

可以定义：

\[
\Delta_{phys}
=P(\text{success}\mid do(physics'))-P(\text{success}\mid physics).
\]

物理理解应体现在干预响应，而不只是 in-distribution success。

---

## 最小实验：逐层冻结

对同一 VLA 做四组：

1. frozen vision + train action；
2. tune vision + train action；
3. frozen language + tune vision/action；
4. full joint training。

同时测：

- semantic instruction following；
- geometric precision；
- novel object；
- perturbation recovery；
- representation probing。

这样可以观察“动作训练到底改变了哪里”。

---

## 本章结论

VLA 不是一个黑盒函数。它是由 **视觉先验、语言先验、本体状态、融合机制、动作生成器、数据混合、后训练、执行器和低层控制器**共同组成的系统。研究它“学到了什么”，必须沿整条数据流做干预，而不是只看最终成功率。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 25`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-25)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
