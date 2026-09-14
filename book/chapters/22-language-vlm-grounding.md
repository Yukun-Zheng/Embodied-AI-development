# Part 22　语言、多模态基础模型与 Physical Grounding

## 学习目标

理解语言进入机器人系统后到底提供了什么、又不能提供什么；掌握 tokenization、vision-language pretraining、open-vocabulary perception、grounding、affordance grounding、spatial/temporal/physical reasoning 与 language-conditioned planning；能够区分“模型会说物理常识”与“模型的表示足以驱动物理行为”。

---

## 22.1 为什么机器人需要语言

语言不是机器人必需的低层控制信号，但它极适合承担四种高层功能：

1. **Goal interface**：人类用自然语言描述任务；
2. **Semantic abstraction**：把视觉世界映射成对象、关系、意图；
3. **Task decomposition**：把分钟级目标拆成秒级 subgoal；
4. **Knowledge carrier**：把互联网常识、物体用途和社会语义迁入机器人。

例如：

> “把洗好的杯子放进左边柜子，但不要碰那只玻璃碗。”

这句话包含对象 identity、状态“洗好”、空间关系、操作目标和 constraint。

## 22.2 语言不是 Motor Command

最终机器人必须执行：

\[
a_t\in\mathbb R^{d_a}
\]

而语言 token 是离散符号。中间需要至少一层 grounding：

```text
language
→ object / relation / subgoal
→ geometric / contact target
→ motion/action
→ controller
```

如果系统从文字直接生成 joint target，grounding 并没有消失，只是被神经网络内部化。

## 22.3 Tokenization

文本被映射为 token：

\[
(w_1,\ldots,w_T)\rightarrow(x_1,\ldots,x_L),
\qquad x_i\in\{1,\ldots,V\}.
\]

Subword tokenizer 对语言高效，但它的 vocabulary 并不是物理 ontology。`grasp`, `hold`, `touch`, `support` 是语言词，不代表模型自动区分其物理接触条件。

## 22.4 Language Model Pretraining

Autoregressive objective：

\[
L_{LM}=-\sum_t\log p_\theta(x_t\mid x_{<t}).
\]

大规模文本让模型学习语言统计、概念关系和世界知识。

但文本只记录人类**关于世界的描述**，不是直接的力、摩擦、碰撞、控制数据。

## 22.5 Vision-Language Pretraining

CLIP-style：图像 embedding \(z_I\) 与文本 embedding \(z_T\) 对齐：

\[
L_{CLIP}
=-\log
\frac{e^{sim(z_I,z_T)/\tau}}
{\sum_j e^{sim(z_I,z_{T,j})/\tau}}.
\]

这带来强 open-vocabulary semantics。

多模态生成模型则将 image tokens/projected features 输入 LLM，使其能基于图像生成语言。

## 22.6 VLM 的强项

VLM 特别擅长：

- object/category semantics；
- text-image alignment；
- common-sense object usage；
- natural-language instruction understanding；
- broad visual question answering；
- open-vocabulary recognition。

这些正是传统 robot vision 最缺 web-scale supervision 的部分。

## 22.7 VLM 的天然缺口

普通 web VLM 没有被直接训练去保证：

\[
\text{metric geometry},\quad
\text{force},\quad
\text{friction},\quad
\text{contact dynamics},\quad
\text{real-time control}.
\]

例如“这只杯子很重”在图片里可能根本不可观测；语言模型只能基于类别 prior 猜。

因此 physical grounding 不能靠语言知识全部填补。

## 22.8 Grounding 的四层

### Semantic Grounding

“红色杯子”对应哪个 image region / object identity？

### Spatial Grounding

“柜子左侧第二层”对应什么 3D region / relation？

### Affordance Grounding

“拿起”需要哪类 grasp point / approach？

### Motor Grounding

“轻轻放下”最终是什么速度、force、trajectory 和 termination condition？

完整机器人必须跨越四层。

## 22.9 Open-Vocabulary Detection / Segmentation

语言驱动 detection：

\[
p(b,m\mid I,text),
\]

输出 box / mask。

这使机器人能够处理训练 task dataset 没显式标注的 category。

但 box/mask 仍不是 grasp pose。Open-vocabulary perception 解决“找谁”，不直接解决“怎么安全操作”。

## 22.10 Referring Expression

“拿桌上靠近蓝碗的那个小红杯”要求用多对象关系 disambiguate。

这对机器人比普通 VQA 更严格，因为 grounding 错一个对象就会产生错误物理动作。

因此 evaluation 应看实际 selected object，而不是生成一句看起来合理的描述。

## 22.11 Spatial Reasoning

语言里的 `left`, `behind`, `inside` 依赖 frame。

例如“杯子在机器人左边”和“杯子在盘子的左边”参照系不同。

真正 physical spatial reasoning 最好连接到连续 transform：

\[
{}^AT_B,
\]

而不是只保留语言 label。

## 22.12 Temporal Reasoning

长任务需要理解：

- before / after；
- 已完成/未完成；
- 正在进行；
- 发生过失败；
- 某状态是否因 action 改变。

单帧 VLM 无法可靠回答这些问题，需要视频/history/memory。

## 22.13 Physical Reasoning

语言问题“哪一摞更容易倒”与机器人真正物理能力之间存在层级：

1. 回答文字正确；
2. 从视觉估计相关变量；
3. 对 action consequence 预测正确；
4. 用 prediction 选择动作；
5. 真机执行成功。

只有后几层才越来越接近 embodied physical reasoning。

## 22.14 Affordance

Affordance 可写：

\[
P(\text{action succeeds}\mid o,e,g,a).
\]

它依赖环境、embodiment 和 goal。

同一杯把对双指夹爪可抓，对大型吸盘可能不可抓；所以 affordance 不是物体的静态标签。

## 22.15 SayCan 式分离

高层语言模型给 skill 语义合理性：

\[
P(skill\mid instruction),
\]

低层 affordance/value 给当前可执行性：

\[
V(skill\mid state).
\]

综合：

\[
score(skill)=P(skill\mid instruction)V(skill\mid state).
\]

这条结构至今仍重要：**应该做什么**与**现在做不做得到**应该分开验证。

## 22.16 Language-Conditioned Policy

更端到端：

\[
\pi(a\mid o,l).
\]

Language embedding 充当 task condition。

关键实验必须包含：

- same observation, different instruction；
- same instruction, different state。

否则模型可能只根据 task label 记 trajectory。

## 22.17 Language-Conditioned Planning

高层：

\[
l\rightarrow(z_1,\ldots,z_K),
\]

低层：

\[
a_t\sim\pi(a\mid o,z_k).
\]

这种层级自然适合 long-horizon。高层语言每几秒更新，低层 motor feedback 高频运行。

## 22.18 Tool Use

多模态模型可以调用：

- object detector；
- search/database；
- map；
- motion planner；
- grasp planner；
- calculator；
- safety checker。

Tool use 的价值是让语言模型不必“凭语言猜”所有几何和物理细节。

## 22.19 Internet Knowledge vs Embodied Knowledge

Internet knowledge：

```text
杯子通常能盛水
剪刀用来剪
冰箱里常放食物
```

Embodied knowledge：

```text
这只杯子当前装满水
这个杯把从右侧更易抓
这扇门铰链今天有阻力
当前夹爪抓力不足
```

前者可预训练，后者必须来自当前 sensor / memory / experience。

## 22.20 Physical Grounding 的在线性

Physical state 会持续变化：

\[
G_t=Ground(I_t,l,m_t).
\]

Grounding 不是任务开始时做一次。机器人移动后，相对关系、遮挡、抓取状态都会变化。

因此 grounding 必须被当作 closed-loop state estimation 的一部分。

## 22.21 VLM Hallucination

VLM 可能因为 semantic prior “看见”不存在的对象。对 chat 这是回答错误；对 robot 可能变成危险 action。

需要：

- grounded detector evidence；
- uncertainty；
- re-observation；
- ask-human；
- execution feasibility check。

## 22.22 Language Ambiguity

“把那个杯子给我”在有三个杯子时目标不确定。

安全 agent 不应 arbitrarily choose，而应：

\[
U(g)>\tau\Rightarrow \text{ask clarification}.
\]

主动澄清本身是 embodied interaction 的一部分。

## 22.23 Language Shortcut

如果 training 中 instruction 唯一决定 trajectory，模型可能完全忽略视觉：

\[
I(a;l)\gg I(a;I\mid l).
\]

测试 object position change 时仍输出原动作。

必须做 visual intervention 才能发现。

## 22.24 Physical Vocabulary 是否应该离散

语言擅长离散概念，但接触力/pose 是连续的。一个合理 architecture 可能让语言只承担高层离散 abstraction，而低层使用 continuous representation。

这正是 VLM + continuous action expert 路线的理论动机之一。

## 22.25 From VLM to Robot Foundation Model

一个 robot foundation model 需要在 VLM 基础上新增：

\[
\text{proprioception}+
\text{action}+
\text{temporal feedback}+
\text{robot data}+
\text{embodiment}.
\]

如果再加入 world model、memory、RL、safety，则逐渐从 multimodal language model 变成完整 physical agent。

## 常见失败

- VLM 文本回答正确，却执行完全失败；
- grounding 只在 task 开始做一次；
- open-vocabulary detector 找对 category，但误选 instance；
- same instruction 训练位置固定，policy 学语言 shortcut；
- VLM hallucination 被直接送到 controller；
- language planner 不检查 reachability/collision；
- 把网络生成“我会轻轻抓”当作 force control 证据。

## 最小实验

构造桌面任务：同一句 instruction 下随机改变目标位置、障碍、目标 instance；再固定 scene 改 instruction。比较 VLM-only plan、VLM + explicit grounding/geometry、end-to-end language-conditioned policy。做视觉遮挡/错误语言/歧义指令三种 stress test，统计 object-selection error、physical infeasibility、clarification rate 和最终 success。

## 研究问题

1. Web-scale language prior 最适合迁移到 physical system 的层级到底在哪里？
2. Physical grounding 是否需要独立 persistent world state，而不是每次让 VLM 重读图像？
3. 语言是否应该成为长期 robot memory 的压缩层，还是会丢失过多几何/接触细节？
