# Volume IV　Robot Learning：从 Demonstration 到 Generative Policy

> 本卷研究机器人如何从数据与交互中获得策略。重点不是罗列网络，而是理解：数据分布如何产生、策略输出什么、训练目标对应什么概率模型、rollout 为什么会失效，以及 imitation / RL / generative policy 如何组合。

---

# Part 18　为机器人重新学习机器学习

## 18.1 Supervised Learning 的基本假设

监督学习常假设数据独立同分布：

\[
(x_i,y_i)\overset{i.i.d.}{\sim}p_{data}(x,y).
\]

训练

\[
\min_\theta \frac1N\sum_i \ell(f_\theta(x_i),y_i).
\]

机器人 rollout 却破坏这一假设：策略输出 action 后会改变下一状态，因此测试分布依赖策略自己：

\[
s_{t+1}\sim p(s'\mid s_t,\pi_\theta(s_t)).
\]

这就是 robot learning 与静态分类最根本的差别之一。

## 18.2 Representation Learning

设 observation encoder

\[
z_t=E_\phi(o_t).
\]

一个好的 robot representation 不只应让 object class 线性可分，还应保留动作相关变量：pose、velocity、contact、affordance、uncertainty、task progress。

可用 predictive sufficiency 来思考：若

\[
p(o_{t+1:T},r_{t:T}\mid o_{\le t},a_{t:T})
\approx p(o_{t+1:T},r_{t:T}\mid z_t,a_{t:T}),
\]

则 \(z_t\) 对控制更有意义。

## 18.3 Sequence Modeling

机器人数据天然是序列：

\[
(o_0,a_0,o_1,a_1,\ldots).
\]

RNN 用 hidden state

\[
h_t=f(h_{t-1},x_t)
\]

压缩历史；Transformer 用 attention 直接建立 token 间依赖。长序列优势伴随计算与 memory 成本：标准 attention 复杂度近似 \(O(T^2)\)。

## 18.4 Transformer

输入 token \(X\in\mathbb R^{T\times d}\)：

\[
Q=XW_Q,\quad K=XW_K,\quad V=XW_V,
\]

\[
\mathrm{Attn}(X)=\mathrm{softmax}(QK^T/\sqrt d)V.
\]

机器人里 token 可以是 image patch、language、state、action、tactile、history。Transformer 的核心贡献是条件建模与可扩展序列计算，不应被神化为“物理推理机制”。

## 18.5 Contrastive / Masked / Predictive Learning

无标签预训练常见三类：

1. contrastive：拉近正样本、推远负样本；
2. masked modeling：根据上下文恢复被遮盖内容；
3. predictive latent learning：预测未来或隐藏部分的 representation。

机器人应关注：预训练目标是否鼓励模型保留 dynamics / contact / geometry，而非只保留语义。

## 18.6 Distribution Shift

至少区分：

- observation shift：光照、背景、camera；
- object shift；
- task shift；
- dynamics shift；
- embodiment shift；
- policy-induced shift；
- temporal shift：硬件磨损、相机移动、环境长期变化。

“泛化”必须说明是哪一种。

---

# Part 19　模仿学习

## 19.1 Demonstration

一个 demonstration dataset：

\[
D=\{\tau_i\}_{i=1}^N,
\qquad
\tau_i=(o_0,a_0,\ldots,o_T,a_T).
\]

来源可能是：expert policy、teleoperation、kinesthetic teaching、human video、scripted planner、simulation oracle、autonomous rollout + correction。

数据质量不仅是成功/失败，还包括速度、平滑性、策略多样性、状态覆盖和 operator 风格。

## 19.2 Behavior Cloning

连续动作常用 MSE：

\[
L_{BC}=\mathbb E\|a-\pi_\theta(o)\|^2.
\]

但 MSE 隐含单峰 Gaussian 假设。如果绕障可以左绕或右绕，均值动作可能恰好撞障碍。

概率 BC 更一般：

\[
L=-\mathbb E\log p_\theta(a\mid o).
\]

## 19.3 Covariate Shift

训练看到 expert state distribution \(d_{\pi_E}\)，部署产生 \(d_{\pi_\theta}\)。小误差把机器人带到训练没见过的状态，随后误差继续放大。

这解释了为什么 offline validation loss 很低的 policy 仍可能 rollout 秒崩。

## 19.4 DAgger

DAgger 让 learner 自己 rollout，在其访问状态上查询 expert：

1. rollout \(\pi_i\)；
2. 收集访问状态 \(s\)；
3. expert 标注 \(a_E(s)\)；
4. 聚合数据并重训。

核心思想：**训练分布要跟随部署分布。**

## 19.5 Human Intervention

真实机器人中 expert query 昂贵。常用 intervention：机器人自主运行，只有危险/错误时人接管。这既产生 corrective data，也能定义 failure boundary。

但 intervention dataset 有选择偏差：人最常纠正的状态可能不是整个 failure distribution。

## 19.6 Action Chunking

不逐步预测 \(a_t\)，而输出

\[
A_t=(a_t,a_{t+1},\ldots,a_{t+H-1}).
\]

优点：减少 compounding error、提高时间一致性、允许模型规划短期动作结构。缺点：chunk 内缺乏反馈，环境变化时动作可能过期。

## 19.7 ACT

Action Chunking with Transformers 将历史 observation 编码后一次产生 action sequence，并用 latent variable 建模 demonstration style。其历史地位在于把低成本双臂 teleoperation 与 chunked Transformer policy 组合成强实用 baseline。

## 19.8 Temporal Ensembling

若每个时刻都预测未来 chunk，不同 chunk 对同一未来动作有多个预测。可按时间距离加权平均：

\[
\hat a_t=\frac{\sum_k w_k a_t^{(k)}}{\sum_k w_k}.
\]

这能平滑动作，但也可能在快速状态变化时引入滞后。

## 19.9 Learning from Play

play data 不要求每条轨迹完成预先定义任务，而鼓励广泛交互覆盖。其价值在于提高 state-action diversity，并允许后续通过 goal / language relabel 重用数据。

## 19.10 Human Video

human video 有规模优势，却缺 robot action。常见桥梁：

- hand/object trajectory retargeting；
- latent action inference；
- visual goal / subgoal；
- inverse dynamics；
- cross-modal pretraining；
- embodiment-independent skill representation。

难点是 human morphology、动力学和接触能力与机器人不同。

## 19.11 Failure / Recovery Demonstration

只收成功轨迹会让 policy 不知道如何恢复。应系统加入：物体滑落、抓空、姿态偏移、遮挡、工具未对齐等 failure state，再示范恢复。

一个实用数据集应覆盖

\[
D=D_{success}\cup D_{near-failure}\cup D_{recovery}.
\]

---

# Part 20　强化学习、Offline RL 与交互学习

## 20.1 MDP

\[
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
\]

目标最大化

\[
J(\pi)=\mathbb E_\pi\left[\sum_{t=0}^{\infty}\gamma^t r_t\right].
\]

## 20.2 Value / Q / Advantage

\[
V^\pi(s)=\mathbb E[G_t\mid s_t=s],
\]

\[
Q^\pi(s,a)=\mathbb E[G_t\mid s_t=s,a_t=a],
\]

\[
A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s).
\]

advantage 描述“这个动作比该状态下平均策略好多少”。

## 20.3 Bellman Equation

\[
Q^\pi(s,a)=r(s,a)+\gamma\mathbb E_{s',a'}Q^\pi(s',a').
\]

RL 许多算法只是以不同方式逼近这个递归关系。

## 20.4 Q-Learning

\[
Q(s,a)\leftarrow Q(s,a)+\alpha[r+\gamma\max_{a'}Q(s',a')-Q(s,a)].
\]

连续高维机器人 action 下直接 max 很难，因此 actor-critic 更常用。

## 20.5 Policy Gradient

\[
\nabla_\theta J
=\mathbb E[\nabla_\theta\log\pi_\theta(a\mid s)\,A(s,a)].
\]

REINFORCE 方差大；actor-critic 用 critic 估值降低方差。

## 20.6 PPO

PPO 使用 clipped surrogate：

\[
L^{clip}=\mathbb E\left[\min(r_tA_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t)\right].
\]

它因稳定、实现成熟，成为 locomotion / sim RL 高频 baseline。

## 20.7 SAC

SAC 最大化 reward 与 entropy：

\[
J=\mathbb E\sum_t[r_t+\alpha\mathcal H(\pi(\cdot\mid s_t))].
\]

off-policy 数据复用率高，适合真实机器人样本昂贵场景，但高维视觉训练仍复杂。

## 20.8 Model-Based RL

学习 dynamics

\[
\hat s_{t+1}=f_\phi(s_t,a_t)
\]

或 latent dynamics，再用于 planning / imagined rollout。优势是数据效率；风险是 model bias 随 horizon 累积。

## 20.9 Offline RL

只用固定数据集 \(D\)，不在线探索。最大问题是 distributional extrapolation：critic 可能给数据外动作虚高价值。

典型思想包括 conservative Q、behavior regularization、advantage-weighted regression。

## 20.10 Goal-Conditioned RL

\[
\pi(a\mid s,g),\qquad r=r(s,g).
\]

同一 experience 可通过 hindsight relabeling 产生多个 goal supervision，提高数据复用。

## 20.11 Hierarchical RL

高层选 skill / subgoal \(z_k\)，低层执行：

\[
z_k\sim\pi_H(z\mid s,g),
\qquad
 a_t\sim\pi_L(a\mid s,z_k).
\]

它与 embodied reasoning + VLA 的分层在结构上相似，只是高层变量可能从 learned option 变成 language subtask。

## 20.12 Reward Design

reward shaping 很容易让 agent 钻空子。一个机器人“拿起杯子”若 reward 只按高度，可能把杯子撞飞也得到高分。reward 必须与真正任务 outcome 对齐，并设 safety / energy / smoothness guardrail。

## 20.13 Exploration

真实机器人不能无限 random exploration。常见替代：

- simulation pretraining；
- demonstration initialization；
- residual RL；
- uncertainty-driven exploration；
- human-in-the-loop correction；
- safe set / shield。

## 20.14 Residual RL

在已有 controller 上学 residual：

\[
a=a_{base}+\Delta a_\theta.
\]

可保留经典控制稳定结构，让 RL 只修正模型误差和接触细节。

## 20.15 Locomotion RL

腿式 RL 通常输入 proprioception + command，输出 joint target/torque；大量并行 simulation、domain randomization 与 privileged critic 是成功关键。

不要把“PPO 很强”与“PPO 学会物理”混为一谈：很多能力来自精心 reward、curriculum、reset 和 simulator throughput。

## 20.16 Real-World Online RL

2025–2026 的重要趋势是 foundation policy 先提供强 prior，再用少量真实 autonomous experience 做 post-training，而不是从随机策略开始。

以 \(\pi^*_{0.6}\) 为代表的路线把 offline RL、demonstration fine-tuning、on-robot correction 与 reward feedback 串成 data flywheel。这比传统“训练一次后冻结部署”更接近长期机器人系统。

---

# Part 21　生成式动作模型与实时策略

## 21.1 为什么动作是分布

给定同一场景，机器人可能存在多条可行轨迹：左绕/右绕、从杯把/杯壁抓、双臂分工不同。因此需要

\[
p(a_{t:t+H}\mid o_{\le t},g)
\]

而非单点平均。

## 21.2 Autoregressive Action

离散/连续量化后：

\[
p(a_{1:H}\mid c)=\prod_{h=1}^H p(a_h\mid a_{<h},c).
\]

优点是复用语言模型技术、灵活长度；缺点是 token-by-token latency、quantization error 与长 action sequence 的累积误差。

## 21.3 Action Tokenization

连续 action 可 uniform binning，也可学习 tokenizer。tokenizer 决定精度、序列长度和跨 embodiment 兼容性。

如果每个自由度每个 timestep 一个 token，长 horizon 会极长；FAST 等方法尝试利用 temporal structure 压缩动作序列。

## 21.4 Diffusion Policy

前向过程逐渐加噪：

\[
x_k=\sqrt{\bar\alpha_k}x_0+\sqrt{1-\bar\alpha_k}\epsilon.
\]

网络学习噪声/score，反向从噪声生成 action trajectory。condition 来自 observation history。

Diffusion 的优势：天然表示多模态连续动作、整段轨迹联合生成；缺点：多步 denoising 带来推理延迟。

## 21.5 3D Diffusion Policy

把 observation 从 RGB feature 转为 point cloud / 3D feature，主要动机是让 policy 对 camera appearance 更鲁棒，并显式利用三维几何。是否有效取决于 point cloud quality、坐标 frame、action representation 和任务。

## 21.6 Flow Matching Policy

定义时间依赖 velocity field：

\[
\frac{dx}{dt}=v_\theta(x,t\mid c).
\]

训练直接匹配目标 flow velocity，推理通过 ODE integration 从简单分布到 action distribution。相比 diffusion，可用更少 integration steps 获得高质量连续动作，因此成为现代 VLA action expert 的重要选择。

## 21.7 Continuous Action Expert

大型 VLM 负责语义/视觉 context，独立连续 action expert 接收其 feature 与 robot state，输出 action chunk。这样避免把高精度 motor command 强行离散成 language token。

## 21.8 Hybrid Discrete–Continuous

高层可能离散生成 subtask / skill token，低层连续 flow/diffusion 生成 motor trajectory：

\[
\text{language/skill token}\rightarrow z
\rightarrow p(A\mid z,o).
\]

这是 reasoning 与 control 时间尺度分离的一种自然形式。

## 21.9 Receding-Horizon Execution

生成长度 \(H\) 的 chunk，但只执行前 \(h<H\) 步，然后重新观察：

```text
observe → generate A[0:H] → execute A[0:h]
   ↑                                ↓
   └──────────── re-observe ────────┘
```

\(h\) 越小反馈越强，但推理频率要求越高。

## 21.10 Chunk Boundary Problem

如果下一个 chunk 生成时机器人还在执行旧 chunk，直接替换会出现速度/位置不连续。尤其大模型推理延迟不可忽略。

需要：overlap、temporal ensemble、trajectory blending、asynchronous queue 或训练时显式建模延迟。

## 21.11 Real-Time Action Chunking

RTC 的问题意识：大型 VLA 推理期间世界仍在运动。系统必须让新 chunk 与“推理完成时真正到达的 state”对齐，而不是与发起推理时的过时 state 对齐。

可抽象为

\[
A_{new}=F(o_{t-\Delta},A_{executed\ during\ \Delta}).
\]

这把 latency 从工程 nuisance 提升为 policy modeling 的一部分。

## 21.12 Asynchronous Inference

生产系统常有独立线程：

```text
Sensor thread → latest observation buffer
Model thread  → future chunk queue
Control thread → interpolate / execute / safety check
```

三者不能用简单 synchronous `while` loop 代替。必须记录 action timestamp、queue state 和 stale-policy 行为。

## 21.13 Diffusion / Flow / AR 怎样选

| 维度 | AR | Diffusion | Flow |
|---|---|---|---|
| 连续精度 | 依赖 tokenization | 高 | 高 |
| 多模态 | 强 | 强 | 强 |
| 推理步数 | 序列长度相关 | 常较多 | 可较少 |
| 复用 LLM | 最自然 | 需独立 head | 需独立 expert |
| 实时性 | token latency | denoise latency | ODE steps |
| 轨迹整体性 | 中 | 强 | 强 |

没有“永远最优”的生成范式。最终选择应由 action bandwidth、robot dynamics、hardware latency 和数据量决定。

---

# Robot Learning 的统一闭环

```text
Demonstrations / web / simulation / autonomous experience
                         ↓
                    dataset D
                         ↓
   representation + policy / value / world model
                         ↓
                   robot rollout
                         ↓
          success / failure / intervention
                         ↓
             new data + reward + correction
                         └────────→ update
```

真正长期可扩展的机器人系统必须让这条 flywheel 运转，而不是只把一个 checkpoint 部署到底。

## 必做实验

1. BC on Push-T：观察 covariate shift；
2. DAgger：比较同样 expert query 数量；
3. ACT/action chunk：扫描 horizon；
4. PPO locomotion：分析 reward ablation；
5. SAC / offline RL：观察 OOD action overestimation；
6. diffusion policy：可视化同一 observation 下多条 action sample；
7. flow matching policy：比较 NFE 与 latency；
8. asynchronous inference：人为加入 100–500 ms latency，测成功率；
9. recovery data：加入失败恢复 demonstration，测 intervention rate。

## 推荐资料与源码

- Sutton & Barto, *Reinforcement Learning: An Introduction*.
- Ross et al., DAgger.
- Chi et al., Diffusion Policy — https://diffusion-policy.cs.columbia.edu/
- Zhao et al., ACT / ALOHA.
- Octo — https://octo-models.github.io/
- Physical Intelligence RTC — https://www.pi.website/research/real_time_chunking
- Physical Intelligence π*0.6 — https://www.pi.website/blog/pistar06
- Hugging Face LeRobot — https://huggingface.co/docs/lerobot/
