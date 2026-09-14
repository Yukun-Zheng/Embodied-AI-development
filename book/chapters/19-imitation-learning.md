# Part 19　模仿学习

## 学习目标

理解 demonstration 的来源、偏差与覆盖；掌握 Behavior Cloning、covariate shift、DAgger、human intervention、action chunking、ACT、teleoperation、learning from play/video、failure/recovery data；能把“更多示范”拆成状态覆盖、动作质量、策略多模态和恢复能力四个问题。

---

## 19.1 Demonstration 是什么

一条轨迹：

\[
\tau=(o_0,a_0,o_1,a_1,\ldots,o_T,a_T).
\]

数据集：

\[
D=\{\tau_i\}_{i=1}^N.
\]

但 demonstration 不是中性的“真值”。它总带着 demonstrator、teleop interface、controller 和任务定义的偏差。

例如同一抓取任务，leader-arm operator 会产生平滑连续轨迹，键鼠 teleop 会产生离散方向脉冲。模型最终会模仿采集系统的行为风格。

## 19.2 Demonstration 来源

常见：

- human teleoperation；
- kinesthetic teaching；
- scripted controller；
- motion planner；
- RL expert；
- simulation privileged policy；
- human video；
- autonomous policy + correction。

不同来源包含不同信息。Planner 数据通常 collision-free 但接触自然度差；human data 灵活但有 operator inconsistency；RL expert 可能利用 simulation-specific behavior。

## 19.3 Behavior Cloning

最简单：

\[
\pi_\theta^*=\arg\min_\theta
\mathbb E_{(o,a)\sim D}
\ell(\pi_\theta(o),a).
\]

若连续 action 用 MSE：

\[
L=\|a-\hat a\|_2^2.
\]

这等价于假设条件动作分布近似单峰 Gaussian 且固定 variance。

## 19.4 Multimodal Demonstration

同一 state 可能有多种正确动作：绕左、绕右；左手先动、右手先动。

MSE 会预测平均：

\[
\hat a\approx\frac12(a^{(1)}+a^{(2)}),
\]

而平均动作可能两边都不对。

因此 mixture model、latent policy、diffusion/flow 等生成式策略有直接动机。

## 19.5 Covariate Shift

Expert data 来自：

\[
s\sim d_{\pi_E}.
\]

部署 learner 访问：

\[
s\sim d_{\pi_\theta}.
\]

小误差导致进入 expert 从未示范的 state，后续 prediction 更差。若单步 error rate 为 \(\epsilon\)，long-horizon cumulative degradation 可远大于普通 i.i.d. classification 的 \(O(T\epsilon)\) 直觉。

## 19.6 Recovery Blind Spot

成功 demonstration 往往故意避免错误，因此 dataset 中几乎没有：抓偏、物体滑落、门没开到位。

模型部署一旦进入这些 state，没有任何正确 action supervision。

所以“高质量数据”不能简单等于“只留完美轨迹”。

## 19.7 DAgger

Dataset Aggregation：

1. 训练初始 policy \(\pi_1\)；
2. 用 learner rollout；
3. 在 learner 访问 state 查询 expert action；
4. 聚合 \(D\leftarrow D\cup D_{new}\)；
5. 重训。

核心不是算法名字，而是：

\[
\text{training state distribution}
\rightarrow
\text{deployment state distribution}.
\]

## 19.8 Mixture Policy

早期 DAgger 可混 expert 与 learner：

\[
\pi_i=\beta_i\pi_E+(1-\beta_i)\pi_L.
\]

逐渐减小 \(\beta_i\)，避免初期 learner 立刻进入危险区域。

真机上 human intervention 是更自然的混合机制。

## 19.9 Human Intervention

机器人自主运行，人只在需要时接管。保存：

\[
(s_{pre},a_{policy},a_{human},reason,s_{post}).
\]

这类数据特别有价值，因为它集中在 decision boundary / failure frontier。

但人类何时选择接管也有 bias：两个 operator 对“危险”定义可能不同。

## 19.10 Intervention Prediction

可以训练：

\[
p(I_t=1\mid o_t,a_t),
\]

预测“人是否即将接管”。它可成为 uncertainty/failure score。

但要防止模型学 human visual cue，例如看到人的手伸过来才判断需要 intervention。

## 19.11 Action Chunking

一次预测：

\[
A_t=[a_t,a_{t+1},\ldots,a_{t+H-1}].
\]

相较一步一预测：

- 减少 model call；
- 学习短期 temporal coordination；
- 平滑动作；
- 降低某些 compounding error。

代价：chunk 内 feedback 变弱。

## 19.12 Chunk Horizon

\(H\) 太短：模型频繁 inference，动作不连贯；

\(H\) 太长：环境变化后，剩余动作 stale。

因此真正变量不是“有没有 chunk”，而是：

\[
H,\quad h_{execute},\quad f_{model},\quad f_{control},\quad latency.
\]

## 19.13 ACT

Action Chunking with Transformers 的关键系统结构：

- observation 编码；
- Transformer 建模序列；
- CVAE latent 表示示范风格/多样性；
- 一次输出 action chunk；
- temporal ensemble 平滑多个重叠预测。

它与低成本 ALOHA 双臂硬件共同证明：数据采集系统 + policy representation 需要共同设计。

## 19.14 ACT 的 CVAE 直觉

训练时由真实未来 action chunk 推断 latent：

\[
q_\phi(z\mid A,o),
\]

decoder：

\[
p_\theta(A\mid o,z).
\]

KL regularization 让 latent 接近 prior。部署时从 prior/确定 latent 生成 action。

这允许同一 observation 下保留 demonstration mode，而不是全部平均。

## 19.15 Temporal Ensembling

多个过去 query 会对当前 action 给预测：

\[
a_t^{(t)},a_t^{(t-1)},\ldots.
\]

按 recency 权重：

\[
\hat a_t=\frac{\sum_k w_k a_t^{(k)}}{\sum_k w_k}.
\]

优点平滑；缺点在快速变化环境中引入滞后。

## 19.16 Teleoperation

Teleop 不只是输入设备。必须设计：

- pose mapping；
- scaling；
- clutch；
- workspace mapping；
- gripper mapping；
- haptic feedback；
- delay compensation；
- operator ergonomics。

采集 10 万条差的 demo 比 1 万条一致、高覆盖 demo 更可能伤模型。

## 19.17 Leader–Follower Hardware

双臂 ALOHA 类系统用 leader arm 直接驱动 follower，降低示范成本。优势是自然双臂协调和高数据吞吐。

但 leader/follower kinematics 不完全一致时，需要 calibration / mapping；机械摩擦也会影响 human motion style。

## 19.18 Kinesthetic Teaching

人直接推 robot 到目标 pose。适合低维 waypoint / compliant robot，却难收高速动态和双臂复杂接触。

它产生的是“机器人自身 embodiment 中的合法轨迹”，这是优势。

## 19.19 Learning from Play

Play dataset 不要求每条 episode 对应明确任务。Human/robot 自由与环境交互，覆盖更丰富 state-action distribution。

后续可 relabel goal：

\[
(\tau,g')
\]

让同一 trajectory 支持多个任务。

## 19.20 Goal Relabeling

一个 episode 最终到达状态 \(s_T\)，可以把它当 retrospective goal：

\[
g'=\phi(s_T).
\]

这与 Hindsight Experience Replay 思想相通，提高数据复用。

## 19.21 Multi-Task Imitation

Policy：

\[
\pi(a\mid o,g).
\]

如果 task label 过于模板化，模型可能直接根据语言猜 trajectory 而忽视视觉。必须通过同 instruction 不同 state、同 state 不同 instruction 的 factorial tests 检查 grounding。

## 19.22 Language Annotation

同一 demonstration 可以配：

- task-level instruction；
- subtask description；
- step-level narration；
- outcome/failure annotation。

语言越细，不一定越好。自动生成 narration 可能把模型带向语言 shortcut。

## 19.23 Learning from Video

Human video 没有 robot action：

\[
D_H=\{I_{0:T}^{human}\}.
\]

要转成机器人 supervision，可学习：

- visual representation；
- hand/object trajectory；
- future goal；
- latent action；
- inverse dynamics；
- high-level skill / task structure。

越靠低层 motor，embodiment gap 越大。

## 19.24 Retargeting

若能估 human hand pose/object trajectory，映射到 robot：

\[
q_r^*=\arg\min_{q_r}
\sum_i\|p_i^{robot}(q_r)-p_i^{human}\|^2
\]

subject to robot joint limit、collision、balance。

目标应该保留 task effect，不是复制 human joint angle。

## 19.25 Offline Demonstration Dataset

质量维度：

\[
Q_D=
(\text{success},\text{coverage},\text{diversity},\text{consistency},\text{recovery},\text{metadata}).
\]

只用“episode 数”描述机器人数据规模过于粗糙。

## 19.26 Failure Data

建议显式保存：

\[
D=D_{success}\cup D_{near-failure}\cup D_{failure}\cup D_{recovery}.
\]

Failure 本身不应全部作为 imitation target；需要知道失败动作是什么、正确 recovery 是什么。

## 19.27 Recovery Demonstration

最有价值的 recovery 数据通常从策略自己 failure state 开始，再由人恢复。

这比随机制造异常更贴近部署 distribution。

## 19.28 Curriculum of Demonstrations

新 policy 早期需要 clean core skill；成熟后更应补 boundary / rare failure。数据策略可以随能力动态变化：

```text
core demonstrations
→ broad diversity
→ policy rollout
→ failure mining
→ targeted corrections
```

这已经接近 data flywheel。

## 19.29 Dataset Aggregation at Scale

大规模 foundation robot 的 DAgger 不一定逐 state 查询 expert，而可能通过：

- autonomous rollout；
- human correction；
- reward verifier；
- preference；
- remote fleet logs。

本质仍是把数据采集从静态 corpus 变成依赖当前 policy 的闭环。

## 19.30 BC 什么时候仍然最合理

如果：

- expert 很强；
- state coverage 足；
- task horizon 短；
- environment reset 稳定；
- intervention data 可补；

BC 往往比复杂 RL 更稳定、更样本高效。

不要因为 RL/VLA 更潮就忽略一个调好数据的 BC baseline。

## 常见失败

- train/test 同场景随机切 episode，夸大泛化；
- 只保留成功 demo，部署不会 recovery；
- 示范者风格多样但 MSE policy 平均；
- action timestamp 与 image 对不上；
- teleop action 与部署 controller action semantics 不同；
- human intervention 被删掉而不是用于 failure learning；
- action chunk 很长但环境动态变化；
- human video transfer 实际只学了对象类别。

## 最小实验

在 Push-T 或桌面抓取任务中比较：

1. success-only BC；
2. BC + near-failure state；
3. DAgger；
4. BC + recovery demonstrations。

固定总 expert annotation budget。统计 success、首次偏离 expert manifold 的时间、recovery rate、visited-state coverage。目标不是证明“DAgger 总更强”，而是拆出 on-policy state coverage 的价值。

## 研究问题

1. Foundation policy 的数据瓶颈究竟是成功 demo 数量，还是 failure/recovery coverage？
2. 人类视频可以提供哪一层最稳定的 embodiment-independent supervision？
3. 是否可以让机器人自动判断“我现在缺哪类示范”，从而主动请求最有价值的人类 correction？
