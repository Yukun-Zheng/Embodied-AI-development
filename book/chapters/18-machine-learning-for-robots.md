# Part 18　为机器人重新学习机器学习

## 学习目标

本章不是重复一遍通用机器学习课程，而是重新检查监督学习、泛化、表示学习、序列模型、Transformer、自监督和生成模型在机器人闭环中的假设。核心目标：理解为什么 robot learning 不是普通 i.i.d. prediction，以及为什么一个 offline loss 很低的模型仍可能真机秒崩。

---

## 18.1 监督学习的标准形式

给定

\[
D=\{(x_i,y_i)\}_{i=1}^N,
\qquad (x_i,y_i)\sim p_{data},
\]

训练：

\[
\theta^*=\arg\min_\theta
\frac1N\sum_i\ell(f_\theta(x_i),y_i).
\]

隐含前提：训练和测试来自近似同一分布，样本之间相对独立。

机器人部署打破这个前提，因为模型输出会改变自己的下一条输入。

## 18.2 Policy-Induced Distribution

策略执行：

\[
a_t\sim\pi_\theta(a\mid s_t),
\qquad
s_{t+1}\sim P(s'\mid s_t,a_t).
\]

于是 state distribution 是：

\[
d_{\pi_\theta}(s),
\]

它依赖当前策略。

一个很小的预测误差可能把 robot 带到 expert dataset 从未覆盖的 state；随后误差更大，形成 compounding error。

## 18.3 Offline Metric 与 Rollout Metric

监督 loss：

\[
L_{offline}=\mathbb E_{(o,a)\sim D}
\ell(\pi(o),a).
\]

真正关心：

\[
J_{rollout}=\mathbb E_{\tau\sim\pi}[R(\tau)].
\]

二者分布不同，所以 offline MSE 不能直接代表 task success。

Robot learning 的第一条实验纪律：**所有可执行 policy 最终都要 rollout。**

## 18.4 Generalization 的维度

机器人“泛化”至少拆成：

\[
G=(G_{object},G_{scene},G_{task},G_{dynamics},G_{embodiment},G_{time}).
\]

- new object instance；
- new object category；
- new layout/building；
- new task composition；
- new mass/friction/control delay；
- new robot body；
- long-term distribution drift。

“test success 提升”若不说明在哪个维度 OOD，generalization claim 几乎没有意义。

## 18.5 Bias–Variance 只是开始

小模型可能 underfit，大模型可能高 variance。但在机器人里还多一层：

\[
\text{deployment error}
=\text{prediction error}
+\text{distribution shift}
+\text{closed-loop amplification}.
\]

因此仅通过 regularization 控制 statistical overfitting 不够。

## 18.6 Representation Learning

Encoder：

\[
z_t=E_\phi(o_t).
\]

对于机器人，一个有价值的 latent 应保留：

- geometry；
- motion；
- contact；
- object identity/state；
- uncertainty；
- task progress；
- action consequence。

高语义 classification accuracy 不代表这些变量存在。

## 18.7 Sufficient Representation

理想地：

\[
p(o_{t+1:T},r_{t:T}\mid o_{\le t},a_{t:T})
\approx
p(o_{t+1:T},r_{t:T}\mid z_t,a_{t:T}).
\]

即 \(z_t\) 对未来 decision-relevant information 近似充分。

这比“embedding 看起来聚类很好”更接近控制目标。

## 18.8 Sequence Modeling

机器人 observation/action 是序列：

\[
x_1,x_2,\ldots,x_T.
\]

模型必须处理：

- temporal dependence；
- variable latency；
- hidden state；
- multi-rate sensor；
- long-term memory。

## 18.9 RNN

\[
h_t=f_\theta(h_{t-1},x_t).
\]

优点：每步计算固定、适合在线流；缺点：长程梯度和信息保持困难。

对机器人，RNN 的 recurrent state 其实非常符合“系统持续运行”的直觉，只是现代大模型训练更偏 Transformer。

## 18.10 LSTM / GRU

Gate 控制写入与遗忘：

\[
f_t=\sigma(W_f[x_t,h_{t-1}]),
\]

\[
c_t=f_t\odot c_{t-1}+i_t\odot\tilde c_t.
\]

这种显式 forget gate 提醒我们：长期 robot memory 不能只“不断增加 token”，还需要更新和删除。

## 18.11 Attention

给定

\[
Q=XW_Q,\quad K=XW_K,\quad V=XW_V,
\]

\[
\operatorname{Attn}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V.
\]

它让任意 token 与任意 token 建立条件依赖，非常适合视觉、语言、state、action 的统一融合。

## 18.12 Transformer

一个 Transformer block 典型：

```text
X
→ LayerNorm
→ Multi-Head Attention
→ residual
→ LayerNorm
→ MLP
→ residual
```

对机器人，token 可以来自：

\[
X=[X_{vision};X_{language};X_{state};X_{action};X_{memory}].
\]

真正困难是 token 之间的物理语义是否正确对齐，而不是“能不能 concat”。

## 18.13 Causal vs Bidirectional Attention

Action autoregressive generation 需要 causal mask：

\[
p(a_{1:T})=\prod_t p(a_t\mid a_{<t},c).
\]

Encoder-style perception 可以双向看完整 observation window。

训练时若使用未来 observation 但部署时没有，会造成 temporal leakage。

## 18.14 Transformer 的二次复杂度

Standard attention：

\[
O(T^2d).
\]

机器人长视频、多 camera、长 memory、高频 tactile 很快让 \(T\) 爆炸。

因此需要 token compression、hierarchical memory、recurrent state 或 state-space architectures。

## 18.15 Self-Supervised Learning

机器人数据 label 贵，但 raw interaction 多。可利用：

- contrastive；
- masked prediction；
- temporal correspondence；
- future latent prediction；
- inverse dynamics；
- action-conditioned prediction。

不同 objective 会保留不同物理信息。

## 18.16 Inverse Dynamics Objective

给连续 observation：

\[
\hat a_t=f(o_t,o_{t+1}).
\]

如果模型能从 state change 恢复 action，representation 会关注 controllable factors。

但多个 action 可能产生相同 observation change，尤其有冗余 body，inverse dynamics 并不总可辨识。

## 18.17 Forward Prediction Objective

\[
\hat z_{t+1}=F(z_t,a_t).
\]

它让 representation 关注 action consequence，比单纯 image reconstruction 更贴近 robot dynamics。

World model 与 predictive representation 正从这里展开。

## 18.18 Contrastive Objective 的陷阱

Augmentation 决定 invariance。假如 training 把小位置移动当 augmentation，encoder 可能刻意不关心 precise pose，而 manipulation 恰恰需要 precise pose。

因此机器人 self-supervision 的 augmentation 不能照抄 ImageNet recipe。

## 18.19 Generative Modeling

机器人生成对象可以是：

- image/video；
- action trajectory；
- future latent；
- task plan；
- 3D world；
- synthetic demonstration。

“生成式模型”不是一种算法，而是一类 distribution modeling 目标。

## 18.20 Autoregressive Modeling

\[
p(x_{1:T})=\prod_t p(x_t\mid x_{<t}).
\]

优点：likelihood 清晰、sequence flexible；缺点：serial decoding latency、early error propagation。

动作 token 化后可以直接使用这一范式。

## 18.21 Variational Autoencoder

\[
q_\phi(z\mid x),
\qquad p_\theta(x\mid z).
\]

ELBO：

\[
\mathcal L=
\mathbb E_{q(z\mid x)}[\log p(x\mid z)]
-D_{KL}(q(z\mid x)\|p(z)).
\]

ACT 等序列 imitation 会使用 latent variable 表示 demonstration style / mode。

## 18.22 Diffusion Model

Forward noising：

\[
x_k=\sqrt{\bar\alpha_k}x_0+\sqrt{1-\bar\alpha_k}\epsilon.
\]

模型学习逆过程，能表示复杂多模态连续 distribution。

Action diffusion 的价值不是“图像模型拿来做机器人”，而是解决 multimodal trajectory distribution。

## 18.23 Flow Matching

定义概率路径 \(p_t\) 与 velocity field：

\[
\frac{dx}{dt}=v_\theta(x,t,c).
\]

训练匹配 target conditional velocity，推理通过 ODE 积分生成 action。

Flow action expert 已成为现代 VLA continuous-action 主线之一。

## 18.24 Multitask Learning

多任务 loss：

\[
L=\sum_k\lambda_kL_k.
\]

Gradient 可能互相促进，也可能 conflict。

Robot foundation model 的难点之一就是：web semantics、不同 embodiment action、world-model prediction 等 objective 是否共享同一 representation。

## 18.25 Gradient Interference

若两个 task gradient：

\[
\nabla L_i^T\nabla L_j<0,
\]

存在局部冲突。大规模 co-training 时，如果 robot loss 破坏 VLM semantic knowledge，就出现 knowledge insulation / catastrophic adaptation 问题。

## 18.26 Pretraining / Fine-Tuning / Post-Training

应区分：

- **pretraining**：大规模 broad data 学 general representation/policy；
- **fine-tuning**：目标 robot/task 适配；
- **post-training**：可能包括 RL、preference/correction、safety、experience learning。

不同论文叫法不完全统一，比较时必须看真实 data/objective。

## 18.27 Scaling Law 的正确读法

若性能随 data/compute 增加：

\[
P(N)\approx P_\infty-cN^{-\alpha}.
\]

不要因为 scale curve 上升就推断模型学到了新机制。真正“emergent”能力应通过 controlled threshold、组合泛化、data-matched baseline 验证。

## 18.28 Distribution Shift Taxonomy

机器人常见 shift：

```text
appearance
camera
object instance/category
layout/scene
task language
task composition
dynamics
controller
sensor
embodiment
human behavior
long-term wear
```

每项都应该单独 stress test。

## 18.29 Closed-Loop Learning Science

最终研究对象是：

\[
D\rightarrow \theta\rightarrow \pi_\theta
\rightarrow d_{\pi_\theta}
\rightarrow new\ D.
\]

数据不是静态资源，而是策略与环境共同生成。后面的 DAgger、online RL、data flywheel 都建立在这个闭环上。

## 常见失败

- 只报告 validation loss；
- train/test episode 随机切分导致同场景 leakage；
- VLM backbone 更大，同时 data 也更多，却宣称 architecture gain；
- 把 Transformer hidden state 直接当“world model”；
- 预训练 augmentation 丢掉精细 geometry；
- robot co-training 破坏原 VLM 能力却未测；
- rollout frequency 与训练 action interval 不一致。

## 最小实验

在 Push-T 或 2D manipulation 上训练两个 offline loss 相近的 BC policy。给其中一个 policy 的 action 加小系统偏差，观察 rollout state distribution 如何快速偏离 demonstration。再加入 DAgger-style on-policy state data，比较 distribution overlap 和 success。

## 研究问题

1. Robot representation learning 最小充分目标应该围绕 future prediction、control effect 还是 task success？
2. 大型 multimodal backbone 与 fast sensorimotor state 是否应该共享同一个 sequence model？
3. 机器人 scaling law 最值得横轴放 data 量、物理交互量、任务 diversity，还是 embodiment diversity？
