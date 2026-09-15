# Part 26　机器人数据规模化、人类视频与 Cross-Embodiment

## 26.1 为什么 Robot Data 是真正的瓶颈

互联网数据几乎免费复制，机器人数据不是。

一条真实 trajectory 的成本包含：

\[
C=C_{hardware}+C_{operator}+C_{reset}+C_{failure}+C_{annotation}+C_{storage}.
\]

而且每一条数据都绑定：

- embodiment；
- sensor layout；
- action interface；
- scene；
- control frequency；
- teleoperation system。

所以机器人 foundation model 的 scaling 问题，本质上首先是数据基础设施问题。

---

## 26.2 数据到底是什么

一个 episode 不应该只理解为 \((o_t,a_t)\)。更完整地：

\[
\mathcal E=\{(o_t,s_t,a_t,r_t,c_t,\tau_t,m_t)\}_{t=1}^{T},
\]

其中：

- \(o_t\)：外感知；
- \(s_t\)：proprioception / estimated state；
- \(a_t\)：policy/teleop command；
- \(r_t\)：reward / outcome；
- \(c_t\)：context / language；
- \(\tau_t\)：timestamp；
- \(m_t\)：metadata。

没有 timestamp 和 action convention 的“大数据”可能无法可靠复用。

---

## 26.3 Open X-Embodiment 的历史意义

Open X-Embodiment 最重要的贡献不是一个 dataset 数字，而是证明：

> 多机器人数据可以在统一训练协议中被混合，并产生跨任务、跨 embodiment 的正迁移。

它同时暴露了后来所有跨机器人模型都绕不开的问题：

- action space 不一致；
- camera setup 不一致；
- sampling rate 不一致；
- success criteria 不一致；
- task language 不一致。

Cross-embodiment 首先是 schema problem，然后才是 representation problem。

---

## 26.4 DROID、Bridge 与真实机器人数据

大规模真实数据通常在多样性和一致性之间权衡：

### 高一致性

- 同一硬件；
- 固定 teleop；
- action convention 统一。

优点：训练干净。缺点：embodiment 和 scene diversity 有限。

### 高多样性

- 多实验室；
- 多机器人；
- 多相机；
- 多操作者。

优点：覆盖广。缺点：domain heterogeneity 强。

foundation policy 必须同时解决这两种尺度。

---

## 26.5 Dataset Mixture

若有数据集 \(D_1,\dots,D_n\)，采样概率：

\[
p(i)=\frac{w_i |D_i|^\alpha}{\sum_jw_j |D_j|^\alpha}.
\]

这里 \(\alpha\) 决定大数据集支配程度，\(w_i\) 可表达质量或任务优先级。

如果只按样本量 proportional sampling，小机器人数据可能完全淹没；如果强行均匀，又可能过采样低质量小数据。

---

## 26.6 Data Curation

机器人数据的“质量”不能只看视频是否清晰。

至少要检查：

- task success；
- near-failure；
- operator correction；
- action smoothness；
- reset leakage；
- camera occlusion；
- calibration validity；
- timestamp drift；
- duplicated trajectory；
- accidental shortcut。

对于学习 recovery，失败数据甚至可能比成功数据更有价值。

---

## 26.7 Success Data 与 Failure Data

BC 只看成功 demonstration，会造成一个结构性空洞：

> 模型知道“正常状态下该做什么”，却没见过“错误状态下如何回来”。

因此更完整的数据应该覆盖：

```text
success
near miss
recoverable failure
irrecoverable failure
human correction
abort
```

这也是后续 RL、intervention learning、self-correction 的数据基础。

---

## 26.8 Internet Image / Video Co-Training

互联网视觉数据提供：

- object semantics；
- scene diversity；
- human activity prior；
- language grounding。

但缺少：

- robot action label；
- torque / force；
- camera calibration；
- robot embodiment；
- exact state transition。

所以 co-training 的核心是解决：

\[
\text{semantic abundance} + \text{action scarcity}.
\]

---

## 26.9 Human Video 为什么重要

人类视频的数据规模远大于机器人 demonstrations。

问题是人类与机器人之间存在巨大 domain gap：

\[
\mathcal B_h\neq\mathcal B_r,
\quad
\mathcal A_h\neq\mathcal A_r.
\]

但两者可能共享更高层的 effect：

```text
open drawer
move object A onto B
fold cloth
walk to refrigerator
```

因此 human-to-robot transfer 的关键可能不是复制人的关节动作，而是学习 **effect / affordance / subgoal**。

---

## 26.10 Human-to-Robot Transfer

可以把迁移分成四级：

### Level 1：视觉预训练

只学 representation。

### Level 2：动作伪标签

从视频估计手/物体运动。

### Level 3：latent action / effect space

把人和机器人映射到共享行为表征。

### Level 4：direct policy transfer

人类视频直接帮助机器人完成新任务。

截至 2025–2026，Figure 和 Physical Intelligence 都公开展示/研究了 human video 到 robot capability transfer 的迹象，但这一方向仍需更严格的数据泄漏与任务重合控制。

---

## 26.11 Retargeting

若已知人体动作 \(x_h(t)\)，传统 retargeting 求：

\[
q_r^*=\arg\min_{q_r}\mathcal L_{pose}(FK(q_r),x_h)
+\lambda\mathcal L_{constraint}.
\]

难点包括：

- limb ratio 不同；
- DOF 不同；
- contact 不同；
- hand morphology 不同；
- balance constraints。

retargeted motion 是强监督，但它不是天然可执行动作。

---

## 26.12 Synthetic Trajectory

合成数据来源包括：

- scripted planner；
- motion planner；
- RL expert；
- simulator rollout；
- generative model；
- human motion retargeting。

合成数据的优点是规模和标签完整，缺点是 bias。

训练分布可能变成：

\[
p_{train}=\beta p_{real}+(1-\beta)p_{syn}.
\]

真正问题不是“synthetic 越多越好”，而是怎样控制 synthetic bias 不吞没真实物理统计。

---

## 26.13 Neural-Generated Robot Data

world model / video model 可以生成：

- future frames；
- scene variation；
- subgoal video；
- pseudo-trajectory；
- counterfactual outcomes。

但如果把生成数据当真值直接回灌，会出现 model collapse 式风险：

\[
p_{model}\rightarrow p_{model-generated},
\]

而不是逼近真实世界。

所以必须保持真实数据锚点和 uncertainty filtering。

---

## 26.14 Cross-Embodiment Representation

理想目标是找到 representation \(z\)，使不同机器人执行相似 physical effect 时靠近：

\[
z^{(A)}_{effect}\approx z^{(B)}_{effect}.
\]

候选空间包括：

- end-effector trajectory；
- object-centric displacement；
- contact graph；
- scene effect；
- skill latent；
- language-described subgoal。

比 joint angle 更容易跨 embodiment。

---

## 26.15 Morphology Encoding

一个机器人可以表示为图：

\[
G=(V,E),
\]

节点包含 link / actuator / sensor 属性，边表示 kinematic relation。

morphology-conditioned policy：

\[
\pi(a\mid o,G).
\]

比 robot-ID embedding 更有希望对 unseen morphology 泛化，因为结构是可组合的。

---

## 26.16 Universal Action Representation

不存在天然唯一的 universal action space。

常见候选：

- Cartesian end-effector delta；
- target keypoints；
- object-centric effect；
- contact target；
- latent skill；
- normalized actuator token。

每一种都牺牲不同东西。

例如 object-centric effect 很通用，却无法直接表达腿部 balance；joint target 精确，却高度 embodiment-specific。

---

## 26.17 Motion Transfer

跨机器人 motion transfer 的本质：

\[
\text{intent/effect}
\rightarrow
\text{new embodiment feasible motion}.
\]

这需要同时满足：

- reachability；
- collision；
- dynamics；
- actuator limits；
- contact stability。

因此 motion transfer 不只是 representation problem，也是 constrained optimization problem。

---

## 26.18 Few-Shot Embodiment Adaptation

对新机器人 \(e_{new}\)，希望少量数据 \(D_{new}\) 即可：

\[
\theta' = Adapt(\theta,D_{new},e_{new}).
\]

真正需要报告：

- adaptation data 小时数；
- 是否需要人工 teleop；
- 是否重新训练 backbone；
- 是否只调 adapter；
- 新任务还是旧任务；
- 新 sensor / actuator 是否变化。

不报告这些，“few-shot”没有可比性。

---

## 26.19 Scale 与 Emergence

如果能力随数据规模变化：

\[
P(N)=a-bN^{-\alpha}
\]

可能表现为平滑 scaling，也可能在离散成功指标上看起来像“突然涌现”。

因此研究 emergence 时必须同时画：

- continuous proxy；
- success threshold；
- dataset overlap；
- task compositionality。

不要只用一条成功视频定义 emergent ability。

---

## 26.20 什么数据真正提高 Physical Generalization

建议把数据价值写成条件互信息问题：

\[
I(D_{new};Y_{OOD}\mid D_{old}).
\]

真正有价值的数据不是“更多相似 rollout”，而是补足模型当前不知道的变化因素：

- 新接触模式；
- 新材质；
- 新视角；
- 新 embodiment；
- 新失败状态；
- 新任务组合。

---

## 最小实验：数据增量价值曲线

固定模型架构，依次加入：

1. 同任务更多数据；
2. 新对象数据；
3. 新场景数据；
4. 新机器人数据；
5. 人类视频；
6. failure / recovery data。

分别测 ID 与 OOD performance。

如果第 1 类只提高 ID，而 4–6 类显著提高 OOD，就能开始回答“什么数据真正产生 generalization”。

---

## 本章结论

机器人 foundation model 的核心竞争力不只是参数量，而是能否把**异构真实数据、人类视频、synthetic data、失败经验和不同身体**压入一个可迁移的学习系统。Cross-embodiment 的真正突破点，很可能来自共享的 physical effect，而不是强行把所有机器人关节塞进同一个向量。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 26`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-26)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
