# Part 21　生成式动作模型与实时策略

## 学习目标

理解连续机器人动作为什么天然是条件分布；掌握 autoregressive action、action tokenization、Diffusion Policy、Flow Matching、continuous action expert、hybrid discrete–continuous policy、action chunking、receding-horizon execution、Real-Time Action Chunking 与 asynchronous inference；能够把“生成质量”与“真实控制可执行性”统一起来评价。

---

## 21.1 为什么动作不是一个点

同一 observation / task 下可能存在多条正确轨迹：

- 从左或右绕开障碍；
- 抓杯把或杯身；
- 双臂不同分工；
- 不同速度/姿态完成同一 effect。

因此更自然的对象是：

\[
p(A_t\mid o_{\le t},g),
\]

其中

\[
A_t=(a_t,\ldots,a_{t+H-1}).
\]

单点回归只给 conditional mean，可能落在任何真实 mode 之外。

## 21.2 Action Distribution 与 Physical Feasibility

“概率高”不等于“机器人做得到”。一个 action sample 还必须满足：

\[
A\in\mathcal A_{joint}\cap\mathcal A_{collision}\cap\mathcal A_{dynamics}\cap\mathcal A_{safety}.
\]

因此生成式 policy 最终仍需 controller / feasibility layer。

## 21.3 Autoregressive Action

将 action 表成 token sequence：

\[
p(a_{1:H}\mid c)
=\prod_{h=1}^H p(a_h\mid a_{<h},c).
\]

条件 \(c\) 可以是 image、language、state、memory。

优点：复用成熟 language-model training/inference；缺点：serial decoding、quantization、长动作序列 latency。

## 21.4 Continuous Action Discretization

若每个 action dimension \(a_j\in[l_j,u_j]\) 分为 B 个 bins：

\[
t_j=Q(a_j)\in\{0,\ldots,B-1\}.
\]

解码 quantization error 上界近似：

\[
\epsilon_j\le\frac{u_j-l_j}{2B}.
\]

对粗操作可以接受，对毫米级位置/小力控制可能成为瓶颈。

## 21.5 Token 序列长度

若 action 维数 \(d_a\)、horizon H，并且每维每步一个 token：

\[
T_{action}=H\cdot d_a.
\]

7D action × 50 steps = 350 tokens；humanoid 30+ DOF 会更长。

动作 tokenization 的真正问题是**利用时间/维度相关性压缩序列**。

## 21.6 FAST 类 Action Tokenization

高效 tokenizer 可以对 action trajectory 做 frequency / learned compression，将平滑连续 trajectory 变成更少 symbol，再由 autoregressive model 预测。

重要评价不是 compression ratio 本身，而是：

\[
\text{token count}\downarrow
\quad\text{while}\quad
\text{control error / task success unchanged}.
\]

## 21.7 Diffusion Policy

Forward noising：

\[
x_k=\sqrt{\bar\alpha_k}x_0+\sqrt{1-\bar\alpha_k}\epsilon,
\qquad \epsilon\sim\mathcal N(0,I).
\]

网络学习：

\[
\epsilon_\theta(x_k,k,c)
\]

或 score / clean sample，通过多步 reverse process 从 Gaussian 生成 action chunk。

## 21.8 为什么 Diffusion 适合 Robot Action

它天然表示：

- multimodal continuous distribution；
- high-dimensional correlated trajectory；
- 整个 horizon 的 joint consistency。

相比逐 step Gaussian BC，它能生成多种 coherent trajectory，而不是 mode averaging。

## 21.9 Observation Conditioning

Diffusion Policy 典型条件：

\[
c=E(o_{t-K+1:t}).
\]

可能包含多 frame RGB、proprioception。网络预测整个 future action trajectory：

\[
A_{t:t+H-1}.
\]

History 帮助估计 velocity / hidden state，future chunk 提供 temporal consistency。

## 21.10 Diffusion 的推理成本

若反向 denoising K 次，每次网络 forward：

\[
L_{infer}\approx K\cdot L_{net}.
\]

机器人控制关心 wall-clock latency，因此减少 diffusion steps、distillation、consistency model 等优化非常实际。

## 21.11 3D Diffusion Policy

把 condition 从 2D image feature 改为 point cloud / 3D feature：

\[
c=E_{3D}(P_t,q_t).
\]

其核心 hypothesis：显式 metric geometry 可提高 view robustness / spatial generalization。

必须做 same-data/same-head 的 2D vs 3D controlled comparison，否则提升可能只是 encoder/data augment 差异。

## 21.12 Flow Matching

构造从 base distribution \(p_0\) 到 action distribution \(p_1\) 的概率路径 \(p_t\)，学习 velocity field：

\[
\frac{dx}{dt}=v_\theta(x,t,c).
\]

Conditional flow matching loss：

\[
L=\mathbb E_{t,x_t,c}
\|v_\theta(x_t,t,c)-u_t(x_t\mid x_1)\|^2.
\]

推理用 ODE solver：

\[
x_1=x_0+\int_0^1v_\theta(x_t,t,c)dt.
\]

## 21.13 Flow vs Diffusion

二者都通过连续路径将简单噪声变成复杂 action distribution。工程差异常在：

- training target；
- solver；
- number of function evaluations；
- stochasticity；
- distillation/conditioning。

不能仅因“Flow 更新”就默认更强；应比较相同 compute/latency 下 downstream success。

## 21.14 Continuous Action Expert

现代 VLA 可把 VLM 作为语义/视觉 context provider，再用独立 continuous expert：

```text
vision + language
      ↓
VLM context
      ↓
state + context + noisy action + flow time
      ↓
Action Expert
      ↓
continuous action chunk
```

这样高精度 motor command 不必经过 language vocabulary。

## 21.15 为什么 Separate Expert 有意义

Web VLM 预训练目标与 robot motor dynamics 差异很大。独立 expert 可以：

- 使用更高频 state；
- 采用不同 width/depth；
- 专门做 continuous generation；
- 与 VLM 部分 freeze；
- 减少 robot loss 对 semantic backbone 的破坏。

这是一种“知识共享但计算职责分层”。

## 21.16 Hybrid Discrete–Continuous

高层离散：

\[
z_k\sim p(z\mid o,g)
\]

低层连续：

\[
A\sim p(A\mid o,z_k).
\]

例如 language model 选择 `grasp_handle`，flow expert 生成具体手臂动作。

这与机器人多时间尺度天然匹配。

## 21.17 Action Chunking

一次生成 horizon H：

\[
A_t\in\mathbb R^{H\times d_a}.
\]

但不一定执行全部 H 步。定义 execute horizon \(h\le H\)：

\[
A_t[0:h]\rightarrow robot,
\]

然后 reobserve / regenerate。

## 21.18 Receding-Horizon Execution

```text
obs_t
  ↓
generate H future actions
  ↓
execute first h
  ↓
obs_{t+h}
  ↓
regenerate
```

\(h\) 小：feedback 强、推理要求高；
\(h\) 大：吞吐高、staleness 风险大。

因此最佳 \(h\) 取决于 environment dynamics 与 inference latency。

## 21.19 Control Rate vs Model Rate

假设 low-level control 100 Hz，VLA 10 Hz。每次 VLA chunk 需被 interpolation / held / low-level controller 转成 10 个 control steps。

论文如果只写“10 Hz policy”而没解释 action interpolation，真实执行机制是不完整的。

## 21.20 Chunk Boundary Problem

旧 chunk 正在执行时，新 inference 完成。若直接切换：

\[
a_{old}^{next}\not\approx a_{new}^{first},
\]

会产生 velocity/pose discontinuity。

尤其 robot 已在 inference latency 期间移动，新 chunk 若仍基于旧 state 就更不一致。

## 21.21 Temporal Ensembling

多个重叠 chunk 对当前动作给出 prediction，按 recency 融合：

\[
a_t=\frac{\sum_k w_k\hat a_t^{(k)}}{\sum_kw_k}.
\]

可以平滑 boundary，但会增加 history dependency 和 lag。

## 21.22 Trajectory Blending

在旧 trajectory 与新 trajectory 之间构造短 transition：

\[
a(\alpha)=(1-\alpha)a_{old}+\alpha a_{new}.
\]

对 joint position 可能有效；对 rotation/contact mode 则不能简单线性 blend。

## 21.23 Real-Time Action Chunking

RTC 的核心不是“让模型更快”，而是**让新 action chunk 对齐到推理完成时的真实 robot state**。

设 inference latency \(\Delta\)，期间已执行动作 \(A_{exec}\)。新 prediction 应条件于这段已执行历史：

\[
A_{new}=F(o_{t},A_{exec\ during\ \Delta},g).
\]

否则模型实际上在为过去的 state 规划。

## 21.24 Latency 是 State Variable

如果 latency 随 GPU load 波动：

\[
\Delta_t\sim p(\Delta),
\]

同一模型 output 在不同 delay 下作用于不同 physical state。

一种更完整 formulation 应显式把 elapsed time / execution progress 加入 condition。

## 21.25 Asynchronous Inference

真实架构：

```text
Camera / state threads
      ↓ latest timestamped buffer
Model worker
      ↓ future chunk queue
Control worker @ high Hz
      ↓ interpolate + safety + execute
Robot
```

Model inference 不应阻塞 high-frequency control loop。

## 21.26 Double Buffer / Queue

可以维护：

- current executing chunk；
- next prepared chunk；
- timestamp / validity horizon。

Control thread 在 boundary 原子切换，避免 thread race。

## 21.27 Stale Observation

模型开始计算时 observation age 已经不是 0。定义：

\[
age=t_{now}-t_{sensor}.
\]

若 age 超 threshold，应丢弃/重采，而不是盲目 inference。

## 21.28 Action Semantics

同样 \(d_a=7\) 可能是：

\[
[\Delta x,\Delta y,\Delta z,
\Delta r_x,\Delta r_y,\Delta r_z,g]
\]

但还要说明：

- world/body frame；
- delta/absolute；
- rotation representation；
- scale；
- clipping；
- frequency；
- controller。

没有这些，action model 不可复现。

## 21.29 Relative vs Absolute Action

Absolute target 对 drift 不敏感，但跨 scene frame/calibration 需要一致；relative delta 更容易局部控制，却会累计 integration error。

Modern foundation policies 常使用 state-relative action chunk，以提高不同 initial pose / embodiment 的兼容性。

## 21.30 Action Normalization

训练常 normalize：

\[
\tilde a=(a-\mu)/\sigma
\]

或按 quantile scale 到 [-1,1]。

跨 robot 时若每个 embodiment normalization 不同，model 必须知道对应 transform，否则同一数值语义不一致。

## 21.31 Sampling Temperature / Guidance

生成式 policy 还涉及 stochasticity。更大 sampling noise 可增加 mode diversity，却可能降低 precision。

机器人部署通常需要“有限多样、可重复、可安全”而非无限创意。

## 21.32 Candidate Sampling + Critic

生成 K 个 action chunk：

\[
A^{(1:K)}\sim p_\theta(A\mid c),
\]

再由 value/world model/safety critic 打分：

\[
A^*=\arg\max_k S(A^{(k)}).
\]

这是 generative policy 与 planning/world model 的自然结合。

## 21.33 Diffusion / Flow / AR 对比

| 维度 | AR | Diffusion | Flow |
|---|---|---|---|
| 连续动作 | 需 token/continuous AR | 自然 | 自然 |
| 多模态 | 强 | 强 | 强 |
| 序列一致性 | 依赖 factorization | 整段强 | 整段强 |
| 推理成本 | token serial | denoise steps | ODE NFE |
| LLM 复用 | 高 | 中 | 中 |
| 精细控制 | 取决于表示 | 高 | 高 |
| 实时难点 | token latency | sampling latency | integration latency |

选择应由系统约束决定，不应只看最新论文。

## 21.34 评价指标

除了 task success：

- end-to-end P50/P95/P99 latency；
- action jerk；
- boundary discontinuity；
- control frequency；
- sample diversity；
- collision / safety violation；
- success under injected delay；
- throughput。

## 常见失败

- 只测 neural forward，不测 camera→command latency；
- train 用 fixed latency，deploy latency 抖动；
- action chunk 生成后执行太久，不 reobserve；
- temporal ensemble 把快速 recovery 平滑掉；
- action normalization 错 robot；
- rotation delta 直接线性插值；
- diffusion/flow 网络更大，比较却不匹配 compute；
- sample 多样性高，但大量 trajectory 实际不可执行。

## 最小实验

同一 Push-T/robot task 上训练：Gaussian BC、autoregressive token action、diffusion、flow matching。统一 visual encoder、dataset、action horizon 与 parameter budget。扫描 artificial latency 0/50/100/250/500 ms，并测试同步执行、temporal ensemble、asynchronous queue、RTC-style state alignment。最终画三维 tradeoff：

\[
\text{success}\;\text{vs}\;\text{latency}\;\text{vs}\;\text{compute}.
\]

## 研究问题

1. Action generation 的下一步瓶颈究竟是概率模型，还是实时闭环接口？
2. Humanoid whole-body action 是否还能用统一 chunk，还是必须分多个时间尺度 expert？
3. 能否训练生成模型直接输出满足 kinematic/dynamic/safety constraints 的 trajectory，而不是生成后投影？

## 延伸阅读

- Diffusion Policy — https://diffusion-policy.cs.columbia.edu/
- Physical Intelligence, Real-Time Action Chunking — https://www.pi.website/research/real_time_chunking
- Physical Intelligence, FAST / π-series — https://www.pi.website/
- Hugging Face SmolVLA — https://huggingface.co/blog/smolvla
