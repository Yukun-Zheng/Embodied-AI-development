# Part 3　概率、统计、信息与不确定性

## 3.1 为什么机器人必须概率化

现实传感器有噪声，世界被遮挡，动作执行有误差，同一视觉状态可能对应多个物理解释。确定性输出只能给一个答案，概率模型表达：

\[
p(x),\quad p(x\mid y),\quad p(x_{t+1}\mid x_t,a_t).
\]

机器人真正需要的不是“永远猜一个值”，而是知道什么时候自己不确定。

## 3.2 Random Variable 与 Distribution

随机变量 \(X\) 把样本映射到数值；分布描述其概率。离散：\(P(X=x)\)；连续：density \(p(x)\)，区间概率由积分得到。

## 3.3 Expectation / Variance / Covariance

\[
\mu=\mathbb E[X],\qquad
\mathrm{Var}(X)=\mathbb E[(X-\mu)^2].
\]

多维：

\[
\Sigma=\mathbb E[(x-\mu)(x-\mu)^T].
\]

Covariance 的非对角元素表示误差相关。例如 pose estimation 中位置和 yaw 不确定性常强耦合。

## 3.4 Bayes Rule

\[
p(x\mid y)=\frac{p(y\mid x)p(x)}{p(y)}.
\]

prior × likelihood → posterior。状态估计、system identification、active perception 都是不断更新 posterior。

## 3.5 Gaussian

\[
p(x)=\frac{1}{\sqrt{(2\pi)^d|\Sigma|}}
\exp\left[-\frac12(x-\mu)^T\Sigma^{-1}(x-\mu)\right].
\]

Gaussian 易计算，但现实 belief 经常多峰。物体被完全遮挡时“可能在左柜或右柜”不能由一个单峰均值可靠表达。

## 3.6 Conditional Independence

图模型的力量来自 independence assumptions。若

\[
p(x_t\mid x_{0:t-1},a_{0:t-1})=p(x_t\mid x_{t-1},a_{t-1}),
\]

就有 Markov property。大量估计/控制算法的效率来自这种结构，而不是“概率公式本身”。

## 3.7 MLE / MAP

\[
\theta_{MLE}=\arg\max_\theta p(D\mid\theta),
\]

\[
\theta_{MAP}=\arg\max_\theta p(D\mid\theta)p(\theta).
\]

很多深度学习 loss 都可以重新解释成某个 likelihood 假设。MSE 相当于固定方差 Gaussian negative log-likelihood，这也解释了它为何不适合强多模态动作。

## 3.8 Bayes Filter

预测：

\[
\bar b_t(x_t)=\int p(x_t\mid x_{t-1},a_{t-1})b_{t-1}(x_{t-1})dx_{t-1}.
\]

校正：

\[
b_t(x_t)\propto p(o_t\mid x_t)\bar b_t(x_t).
\]

所有 state estimator 的核心都是“模型预测 + 观测纠偏”。

## 3.9 Entropy

\[
H(X)=-\mathbb E[\log p(X)].
\]

分布越分散，entropy 越大。注意 continuous differential entropy 与离散 entropy 性质并不完全相同，不能机械比较不同单位变量。

## 3.10 KL Divergence

\[
D_{KL}(p\|q)=\mathbb E_p\left[\log\frac{p}{q}\right]\ge0.
\]

KL 不对称，因此不是距离。VAE、policy regularization、distribution shift 都常出现。

## 3.11 Mutual Information

\[
I(X;Y)=H(X)-H(X\mid Y).
\]

主动感知中，候选 observation \(O_v\) 的价值可写：

\[
v^*=\arg\max_v I(S;O_v)-\lambda C(v).
\]

这把“看哪里”变成信息价值与运动代价的权衡。

## 3.12 Epistemic vs Aleatoric

- **Aleatoric**：世界本身/观测随机性，更多数据也不能完全消除；
- **Epistemic**：模型由于数据覆盖不足而不知道，更多有用数据可降低。

主动探索应主要针对 epistemic uncertainty。否则 agent 会被不可预测噪声吸引。

## 3.13 Calibration

如果模型给出 0.8 success confidence 的 episode 中约 80% 真的成功，才叫 calibrated。

可评估 reliability diagram、ECE、Brier score、negative log-likelihood；机器人更应画 risk–coverage curve：随着只执行高置信任务，failure 是否下降。

## 3.14 Monte Carlo

\[
\mathbb E[f(X)]\approx\frac1N\sum_i f(x^{(i)}).
\]

Sampling 是 particle filter、MPC sampling、diffusion、world-model planning 的共同语言。

## 3.15 Uncertainty 必须改变行为

一个系统即使输出 uncertainty，如果低置信时仍照常执行，其 uncertainty 对安全没有价值。应设计 threshold policy：

```text
low uncertainty   → execute
medium            → observe more / slow down
high              → ask human
critical          → safe stop
```

## 最小实验

构造两个重叠 Gaussian class。训练一个分类器后制造 OOD 区域，分别比较 softmax confidence、ensemble uncertainty、distance-based OOD score。画 risk–coverage curve，并让高 uncertainty 触发“拒绝执行”。
<!-- CHAPTER-ENRICHMENT-P03:START -->
## 3.16 从“不确定”到决策：Uncertainty 的闭环接口

不确定性只有进入 action selection 才有系统价值。设机器人维护 belief

\[
b_t(x)=p(x_t=x\mid o_{\le t},a_{<t}),
\]

决策不应只依赖 posterior mean，而应比较**信息价值、任务收益与风险**：

\[
a_t^*=\arg\max_a\;\mathbb E_{x\sim b_t}[R(x,a)]-\lambda\,\mathrm{Risk}(a,b_t).
\]

如果还允许主动获取观测，则可以加入信息项：

\[
a_t^*=\arg\max_a\;\mathbb E[R]-\lambda_r\mathrm{Risk}+\lambda_i I(X;O_{future}\mid a).
\]

这把 calibration、active perception、human handoff 和 safe stop 统一为同一个问题：**belief 如何改变行为。**

### 研究问题

1. VLA 的 token probability / diffusion variance / ensemble variance，哪一种最接近真实 task-failure probability？
2. Epistemic 与 aleatoric uncertainty 在真实机器人上怎样通过 intervention 被区分，而不是只靠模型结构命名？
3. Risk–coverage curve 是否比单一 success rate 更适合评价“会说不知道”的机器人？
4. 当 perception uncertainty 与 action uncertainty 同时存在时，应该先主动看、慢速执行、还是直接请求人类？
5. 一个 uncertainty head 若不改变 policy/executor，是否应被视为系统能力的一部分？
<!-- CHAPTER-ENRICHMENT-P03:END -->
<!-- CHAPTER-ENRICHMENT-R3-P03:START -->
## 3.17 Uncertainty Failure Taxonomy

### Overconfidence under distribution shift

训练内 calibration 良好，但换 camera、object material、lighting 或 embodiment 后 \(\hat p\) 仍接近 1。安全系统若直接信任 confidence，会在最需要保守时最冒险。

### Variance without semantics

diffusion sample variance、ensemble disagreement 或 token entropy 不一定对应 task failure；它们可能只反映 action multimodality 或语言不确定性。

### Mean prediction hides multi-modality

用均值和方差描述高度多峰 grasp/action distribution，可能得到一个物理上不可执行的“平均动作”。

### Uncertainty never reaches the executor

模型输出 uncertainty，但 controller、planner、active perception 和 human handoff 都不读取它；这类 uncertainty 不能算系统能力。

### Wrong uncertainty source

把 sensor noise 当 epistemic、把 model ignorance 当 aleatoric，会导致错误的数据采集和 safety 策略。
<!-- CHAPTER-ENRICHMENT-R3-P03:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 03`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-03)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
