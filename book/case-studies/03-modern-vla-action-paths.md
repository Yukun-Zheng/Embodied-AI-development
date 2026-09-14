# Case Study 03 — Modern VLA Action Paths
## OpenVLA-style Action Tokens vs π-style Continuous Action Expert

> 目标：理解现代 VLA 的一个核心分叉——**动作究竟继续作为语言模型 token 预测，还是交给独立连续动作 expert 生成？** 这不是实现细节，而是决定 precision、sequence length、training objective 与 latency 的架构选择。

---

# 1. 共同输入：Image + Language + Robot State

抽象 observation：

$$
o_t=(I_t,\ell,s_t)
$$

其中：

- `I_t`：单/多视角视觉；
- `ℓ`：语言任务；
- `s_t`：proprioception / robot state。

共同目标：

$$
\pi(a_{t:t+H-1}\mid I,\ell,s)
$$

真正分歧出现在**动作怎么表示、怎么训练、怎么解码**。

---

# 2. Path A：Action Token VLA

典型思路：把连续 robot action 离散化。

若一个 action dimension：

$$
a_i\in[a_i^{min},a_i^{max}]
$$

离散成 `K` 个 bins：

$$
q_i=Q(a_i)\in\{0,\ldots,K-1\}
$$

再映射成词表里的 token。

于是：

```text
image
+
language tokens
+
(optional state tokens)
→ VLM / autoregressive backbone
→ action token 1
→ action token 2
→ ...
→ de-tokenize
→ continuous robot command
```

---

# 3. 为什么这条路很自然

已有大型 VLM 已经非常擅长：

$$
p(token_{n+1}|token_{\le n})
$$

所以只要把 action 也变成 token，就能直接复用：

- tokenizer / vocabulary；
- autoregressive objective；
- pretrained Transformer；
- language/vision context。

训练 loss 仍然可以写成交叉熵：

$$
\mathcal L_{action-token}
=-\sum_j\log p_\theta(q_j|context,q_{<j})
$$

这是 RT-2 / OpenVLA 类设计背后的重要工程吸引力。

---

# 4. Action Tokenization 的代价

连续动作离散后出现：

## Quantization Error

若 bin width：

$$
\Delta_i=\frac{a_i^{max}-a_i^{min}}{K}
$$

最坏单维量化误差约：

$$
\frac{\Delta_i}{2}
$$

对粗粒度 reaching 可能不严重；对 insertion / dexterous control 可能明显。

## Sequence Length

一个 action 若 `Da` 维、chunk 长 `H`：

$$
N_{action-token}\propto H\times D_a
$$

高维 humanoid action 会迅速变成长 token sequence。

## Temporal Semantics 被拆碎

一个向量动作本来是同时发生的：

$$
[a^1_t,a^2_t,\ldots,a^{D_a}_t]
$$

AR tokenization 却按某顺序预测。

这个顺序是 computational convention，不是物理因果顺序。

---

# 5. Action Token 的 Shape Flow

示意：

```text
image tensor       [B, V, C, H, W]
language ids       [B, L]
state              [B, Ds]
        ↓ multimodal embedding
context hidden     [B, N_ctx, D]
        ↓ autoregressive decoding
action token ids   [B, N_action]
        ↓ de-tokenize / reshape
action chunk       [B, H_a, D_a]
```

读源码时最重要的问题之一：

> `N_action` 怎样映射回 `[H_a, D_a]`？

如果不追这一步，就还没真正看到 robot action。

---

# 6. Path B：Continuous Action Expert

另一条路线保留 VLM 做语义/视觉上下文，但不强迫动作进入语言词表。

```text
image + language
→ pretrained multimodal backbone
→ context / hidden representation
                     ↓
robot state ─────→ continuous action expert
                     ↓
               action trajectory
```

action expert 可以是：

- diffusion；
- flow matching；
- DiT / continuous Transformer；
- other conditional generative model。

---

# 7. π-style 思路的核心

抽象写法：

VLM 生成上下文：

$$
h=f_{VLM}(I,\ell)
$$

机器人 state：

$$
s_t\in\mathbb R^{D_s}
$$

continuous action expert：

$$
A_t=G_\phi(h,s_t,\epsilon)
$$

其中：

$$
A_t\in\mathbb R^{H_a\times D_a}
$$

如果使用 flow matching：

$$
\frac{dA(\tau)}{d\tau}=v_\phi(A(\tau),\tau,h,s_t)
$$

从 noise distribution 连续运输到 action distribution。

---

# 8. 为什么把 VLM 和 Action Expert 分开

因为两类信息有不同性质：

### VLM side

- semantic；
- object identity；
- instruction；
- broad world knowledge。

### Motor side

- continuous precision；
- temporal smoothness；
- multi-DoF correlation；
- high-rate trajectory distribution。

所以架构隐含一个观点：

> **语言空间和 motor space 不必使用同一种输出参数化。**

---

# 9. Continuous Expert 也不是免费午餐

优点：

- 无离散量化；
- 天然建模连续多模态轨迹；
- action chunk 整体生成。

代价：

- 多一个训练 objective；
- backbone / expert 如何 joint-train；
- diffusion/flow sampling cost；
- model synchronization；
- end-to-end latency。

---

# 10. Backbone 与 Action Expert 怎样连接

常见接口：

## Context token conditioning

$$
H\in\mathbb R^{B\times N\times D}
$$

action expert cross-attend：

$$
A_{hidden}=CrossAttention(A_{queries},H)
$$

## Global pooled context

$$
h=Pool(H)\in\mathbb R^{B\times D}
$$

通过 FiLM / AdaLN 等进入 action network。

不同接口决定：

- semantic information bandwidth；
- spatial correspondence；
- compute cost。

---

# 11. Proprioception 在哪里进入

VLM pretraining 通常没有 robot qpos。

所以 state 需要专门 encoder：

$$
e_s=W_s s_t+b_s
$$

可能：

- 作为 token 加入 backbone；
- 只加入 action expert；
- 两边都用。

这会影响 cross-embodiment：如果 backbone 直接绑定固定维度 joint state，换机器人更难。

---

# 12. Embodiment Conditioning

多机器人时：

$$
\pi(a|o,\ell,e)
$$

`e` 可以是：

- robot ID；
- learned embedding；
- kinematic descriptor；
- morphology graph；
- action-space metadata。

只用 robot ID 可以支持多个**已见**机器人，但不能自然支持 unseen morphology。

这也是“multi-robot model”与“cross-embodiment intelligence”的分界。

---

# 13. Joint Training 的梯度冲突

如果共同 backbone 同时训练：

$$
\mathcal L
=\mathcal L_{VLM}
+\lambda\mathcal L_{action}
$$

对应梯度：

$$
g=g_{VLM}+\lambda g_{action}
$$

若：

$$
g_{VLM}^Tg_{action}<0
$$

局部存在梯度冲突。

可能现象：

- motor precision 上升；
- semantic capability 下降。

所以需要比较：

```text
frozen backbone
adapter / partial tune
full joint training
```

而不是默认 end-to-end 一定最好。

---

# 14. Dataset Mixture 是模型的一部分

如果训练混合：

```text
robot A: 100k episodes
robot B: 5k episodes
web VLM data: massive
human video: massive
```

采样策略直接决定梯度贡献。

设 dataset `i` 的 sampling probability：

$$
p_i\propto w_i|D_i|^\alpha
$$

改变 `α` 与 `w_i` 就会改变所谓“模型能力”。

因此 architecture comparison 必须控制 data mixture。

---

# 15. Inference 不是 Action Head 结束

无论 token 还是 continuous expert：

```text
VLA output
→ denormalize
→ frame transform
→ temporal executor
→ IK / WBC / impedance / motor policy
→ actuator
```

一个模型 paper 如果只给 `action tokens`，你还要继续追：

- 绝对还是 delta？
- base frame 还是 ee frame？
- 多少 Hz？
- action chunk 多长？
- 谁控制 gripper？
- 谁做 collision safety？

---

# 16. Temporal Executor 是第三条轴

模型生成：

$$
A_t=[a_t,\ldots,a_{t+H-1}]
$$

系统还需要决定：

- 什么时候重新 inference；
- 新 chunk 是否替换旧 chunk；
- 如何平滑 boundary；
- model 延迟时做什么。

所以真实现代 VLA 可以拆成：

```text
Foundation Backbone
        +
Action Generator
        +
Temporal Executor
        +
Low-Level Controller
```

只比较前两项是不完整的。

---

# 17. Token vs Continuous Expert：公平实验

固定：

- visual/language backbone；
- robot data；
- parameter budget；
- action horizon；
- controller；
- policy update rate。

只改变 action representation / objective：

```text
A. discretized AR tokens
B. continuous regression
C. diffusion expert
D. flow expert
```

测：

- task success；
- action precision；
- inference latency；
- mode coverage；
- disturbance recovery。

---

# 18. 精细接触任务为什么重要

粗粒度 pick-and-place 可能掩盖 quantization。

更有区分力：

- insertion；
- screw / rotate；
- precise tool use；
- deformable manipulation；
- dexterous finger control。

如果 continuous expert 的优势来自 action precision，这些任务应该放大差异。

这就是 mechanism-oriented benchmark design。

---

# 19. Negative Controls

## A. More bins for token model

如果 token model 加大 `K` 后追平，说明差异可能主要是 quantization，不是 autoregressive 本身。

## B. Same continuous expert with shuffled VLM context

如果仍高成功，说明任务可能主要靠 proprio/action prior，而没有真正利用 semantic backbone。

## C. Frozen random backbone

检测 visual/language foundation knowledge 是否真的贡献。

## D. Same model, different low-level controller

如果排名翻转，说明 paper claim 强依赖 controller。

---

# 20. 读 OpenVLA / π 类代码时逐层追什么

```text
Dataset
↓
image processor / tokenizer
↓
multimodal prompt / embeddings
↓
VLM hidden states
↓
ACTION BRANCH
├── token logits → token IDs → de-tokenize
└── continuous expert → ODE/diffusion integration
↓
action normalization inverse
↓
robot-specific postprocess
↓
controller
```

每一层都记录：

```text
shape
frame
unit
frequency
trainable/frozen
```

---

# 一句话抓住现代 VLA 架构分叉

> **Action-token VLA 的核心赌注是“语言模型的离散序列接口足够通用，可以连 motor 也一起表示”；continuous-action-expert 路线的核心赌注是“语义推理与连续物理控制应共享上下文，但不必共享输出空间和生成机制”。真正答案必须在相同数据、控制器和延迟预算下由物理任务决定。**
