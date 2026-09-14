# Case Study 01 — ACT / ALOHA
## Action Chunking Transformer：从双臂示范到闭环执行

> 目标：不把 ACT 记成“一个 Transformer”。真正需要掌握的是：**为什么要一次预测一段动作、CVAE latent 在训练中干什么、图像与 proprioception 怎样进入 Transformer，以及 action chunk 最终怎样进入双臂控制系统。**

参考入口：ALOHA / ACT 原始论文与官方代码。不同 fork 的相机数量、action dimension、数据格式可能变化，因此本文优先写稳定的数据流，而不是绑定某一个仓库 commit 的函数名。

---

# 1. 研究问题

逐步 BC：

$$
a_t=\pi(o_t)
$$

对精细双臂任务存在两个问题：

1. 高频动作逐点预测容易抖动；
2. 人类示范本身包含短时间内连贯的动作模式。

ACT 改为：

$$
A_t=
[a_t,a_{t+1},\ldots,a_{t+H-1}]
$$

一次预测一个 **action chunk**。

它把“每一步动作”提升成“短时间运动片段”。

---

# 2. Raw Episode 里有什么

一个典型双臂 episode 可抽象成：

```text
episode/
├── images/
│   ├── cam_high[t]
│   ├── cam_left_wrist[t]
│   └── cam_right_wrist[t]
├── qpos[t]
├── action[t]
└── metadata / success / task
```

示意 shape：

```text
RGB image:  [T, H_img, W_img, 3]
qpos:       [T, Dq]
action:     [T, Da]
```

在原始 ALOHA 类双臂系统里，`Dq/Da` 常对应左右臂关节与夹爪状态；具体维数取决于数据预处理与机器人接口，不能只记一个固定数字。

---

# 3. DataLoader 做的第一件事：从 Episode 抽一个时刻

随机选：

$$
t\sim Uniform(0,T-1)
$$

取当前 observation：

$$
o_t=(I_t^{1:V},q_t)
$$

以及从当前时刻开始的未来 action sequence：

$$
A_t=[a_t,\ldots,a_{t+H-1}]
$$

如果 episode 剩余长度不足 `H`，需要 padding mask。

于是 batch 可能变成：

```text
images:      [B, V, C, H_img, W_img]
qpos:        [B, Dq]
action_seq:  [B, H_a, Da]
is_pad:      [B, H_a]
```

这一步已经决定了模型“看当前、预测未来一段”的学习问题。

---

# 4. 为什么 Training 有一个 CVAE Latent

同一个 observation 可能对应多种合理示范动作。

ACT 训练时用 action sequence 帮助 posterior encoder 得到 latent：

```text
current robot state q_t
+
future expert action chunk A_t
        ↓
CVAE encoder
        ↓
z
```

形式化：

$$
q_\phi(z\mid q_t,A_t)
$$

然后 decoder 学：

$$
p_\theta(A_t\mid I_t,q_t,z)
$$

训练 loss 典型包含：

$$
\mathcal L
=
\mathcal L_{action}
+
\beta D_{KL}
\left(
q_\phi(z\mid q_t,A_t)
\|\mathcal N(0,I)
\right)
$$

这里 latent 的作用不是“让 Transformer 更大”，而是让训练可以表示 demonstration style / trajectory variation。

---

# 5. 训练时的数据流

```text
Expert action chunk A_t ───────────────┐
                                        ↓
qpos q_t ───────────────────────→ CVAE Encoder
                                        ↓
                                     latent z
                                        ↓
Multi-view images ─→ CNN backbone ─→ visual tokens
                                        ↓
qpos q_t ─────────────→ state embedding
                                        ↓
visual tokens + state + z
                ↓
          Transformer Decoder
                ↓
       predicted action chunk Â_t
```

真正值得追的 tensor 是：

```text
image feature per view  [B, C_f, H_f, W_f]
flattened visual tokens [B, N_visual, D]
state token             [B, 1, D]
latent token            [B, 1, D]
transformer hidden      [B, N_total, D]
action output           [B, H_a, Da]
```

不同实现的 token 拼接顺序可能不同，但 shape 逻辑相同。

---

# 6. 图像分支不是“看一眼图片”

多相机图像通常先由 CNN / visual backbone 编码：

$$
I^{(v)}
\rightarrow
F^{(v)}
\in\mathbb R^{C_f\times H_f\times W_f}
$$

然后 spatial flatten：

$$
F^{(v)}
\rightarrow
\{f_1,\ldots,f_{H_fW_f}\}
$$

多个 camera 的 token 再拼接。

读代码时必须问：

- camera identity 怎么编码？
- positional encoding 是 image 内部还是全局？
- 多相机 feature 共享 backbone 吗？
- 图像是否每个 control step 都重新 encode？

这些会直接影响 latency 和 multi-view fusion。

---

# 7. qpos 分支提供什么

视觉无法告诉模型每个关节当前精确在哪里。

因此 proprioception：

$$
q_t\in\mathbb R^{D_q}
$$

经过 linear projection：

$$
e_q=W_q q_t+b_q
$$

形成 state token。

这使 policy 能区分：

> 看起来相同的桌面画面，但机器人手臂实际处在不同 joint configuration。

---

# 8. Transformer 真正在做什么

Transformer 接收到：

- spatial visual tokens；
- robot state；
- latent style/context；
- query / learned action positions。

输出 `H_a` 个未来 action slots。

因此 ACT 的 sequence axis 不只有“时间”，还混合：

```text
spatial image tokens
+
state/latent tokens
+
future action queries
```

不能简单理解成普通 NLP 自回归 Transformer。

---

# 9. Action Loss 到底比较什么

最简单可写成：

$$
\mathcal L_{action}
=\sum_{k=0}^{H_a-1}
M_k\|\hat a_{t+k}-a_{t+k}\|_1
$$

其中：

$$
M_k=1-is\_pad_k
$$

padding 的 future action 不进入 loss。

注意：如果 action 做了 normalization，loss 比较的是 normalized space；真实执行前还必须 denormalize。

---

# 10. Inference 时为什么没有 Expert Action

部署时不知道未来专家轨迹，所以 posterior encoder 无法使用：

```text
future expert action → z
```

通常直接取 prior 中的确定性代表，例如：

$$
z=0
$$

然后：

$$
\hat A_t=\pi(I_t,q_t,z=0)
$$

这说明 CVAE latent 在训练与推理角色不同。

读源码时如果不区分 training/inference branch，很容易看糊涂。

---

# 11. Action Chunk 不等于一次全部执行

模型输出：

$$
\hat A_t=[\hat a_t,\ldots,\hat a_{t+H_a-1}]
$$

但真实系统仍可以：

- 只执行前几个动作；
- 下一次 inference 重新预测；
- 对多个历史预测做 temporal aggregation。

因此实际闭环是：

```text
observe
→ predict chunk
→ execute / aggregate
→ observe again
→ predict new chunk
```

不是：

```text
observe once
→ run H actions open-loop
```

---

# 12. Temporal Aggregation 的核心直觉

在不同时刻：

$$
t-k,t-k+1,\ldots,t
$$

模型都可能预测“当前时刻应该做什么”。

可以把这些预测加权平均：

$$
\bar a_t
=
\frac{\sum_i w_i\hat a_t^{(i)}}{\sum_iw_i}
$$

其中较新的 prediction 权重更大。

作用：

- 平滑动作；
- 减少 chunk boundary discontinuity；
- 利用多个 temporal estimates。

但它也可能增加 lag，所以需要结合任务速度评价。

---

# 13. Action 最终怎样进入双臂机器人

ACT 输出通常仍不是 torque。

典型系统：

```text
ACT normalized action
→ denormalize
→ desired joint position / gripper command
→ robot low-level position controller
→ motor driver
→ joints
```

所以 ACT 的成功包含两部分：

1. policy 给出的 target 好；
2. low-level controller 能稳定追踪。

如果换成 torque-control robot，不能原样照搬 action interface。

---

# 14. Action Chunking 为什么有效

可以理解成 temporal abstraction：

逐点策略：

$$
a_t=f(o_t)
$$

chunk 策略：

$$
A_t=f(o_t)
$$

后者显式利用：

- 人类示范的局部平滑性；
- 短期运动模式；
- 多步动作之间的相关性。

这也是后来大量 robot policy 继续使用 action chunk 的原因。

---

# 15. 但 Chunking 带来了新的问题

如果 `H_a` 太长：

$$
Age(\hat a_{t+k})
\approx T_{infer}+k\Delta t
$$

后半段动作建立在越来越旧的 observation 上。

环境被扰动后：

```text
old chunk says continue closing gripper
but object has already slipped
```

这就是 stale-action problem，后来 RTC / asynchronous chunking 明确针对它。

---

# 16. 最小机制复现

不需要 ALOHA 真机也能验证 ACT 核心。

### Toy task

2D point manipulation，专家动作有局部 temporal pattern。

### Baselines

```text
single-step BC
chunk BC H=10
chunk BC H=50
temporal aggregation
```

### Measurements

- closed-loop success；
- smoothness；
- disturbance recovery；
- latency sensitivity。

只有 chunk 在平滑任务有优势、但过长 chunk 在 disturbance task 变差，才真正复现 action chunking 的机制边界。

---

# 17. 负对照

## Negative Control A：随机打乱 chunk 内动作顺序

保留单步动作分布，但破坏 temporal coherence。

若性能明显下降，说明 chunk 学到了时间结构。

## Negative Control B：相同 H，但只监督第一个 action

控制参数量，测试收益是否真的来自 future supervision。

## Negative Control C：关闭 temporal aggregation

分离：

- action chunk training gain；
- inference smoothing gain。

---

# 18. Failure Taxonomy

ACT 常见失败可分：

1. visual grounding；
2. action chunk 方向错误；
3. chunk stale；
4. gripper timing；
5. bimanual desynchronization；
6. contact error；
7. temporal aggregation lag；
8. low-level tracking failure。

不能所有失败都叫“imitation learning error”。

---

# 19. 从 ACT 到现代 VLA 的桥

ACT 没有大语言 backbone，但很多现代 VLA 延续了它的系统结构：

```text
multi-view visual input
+
proprioception
→ sequence model
→ action chunk
→ temporal executor
→ controller
```

现代模型主要把：

- language knowledge；
- larger visual backbone；
- cross-task/cross-robot data；
- diffusion/flow action generator

接了进来。

因此理解 ACT，是理解今天 VLA action side 的非常好入口。

---

# 20. 一句话抓住 ACT

> **ACT 的关键不是“用了 Transformer”，而是把双臂 imitation learning 的预测单位从单个 action 提升成有内部时间结构的 action chunk，并用 CVAE 表示示范多样性，再在闭环执行中聚合这些短期计划。**
