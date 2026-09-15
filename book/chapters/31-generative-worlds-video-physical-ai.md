# Part 31　生成式世界、视频模型与 Physical Simulation Foundation Models

## 31.1 为什么 Video Generation 进入 Robotics

机器人数据昂贵，而互联网视频极多。

生成式视频模型带来三个诱惑：

1. 从大规模视频学习 physical prior；
2. 生成 synthetic training data；
3. 用视频 rollout 作为 imagined future。

但必须始终记住：

\[
\text{visual plausibility}\neq\text{physical correctness}.
\]

---

## 31.2 Internet Video 里的物理先验

视频确实包含：

- gravity；
- object permanence；
- human-object interaction；
- deformable motion；
- navigation；
- tool use。

但大多数互联网视频没有：

- exact action label；
- force；
- torque；
- calibration；
- mass/friction metadata。

因此它提供的是弱物理监督，而不是 simulator-quality dynamics data。

---

## 31.3 Actionable Video Representation

机器人不需要理解视频里的全部内容，只需要提取可行动信息。

理想 representation \(z\) 应保留：

\[
I(z;A_{useful})
\]

同时压缩与任务无关细节。

可能包含：

- object motion；
- affordance；
- contact event；
- human hand trajectory；
- subgoal transition。

---

## 31.4 Image-to-Video / Text-to-Video 用于 Data Augmentation

可生成：

- lighting variation；
- background；
- object appearance；
- rare scenario；
- alternate outcome。

但训练前必须问：

> 生成变化是否改变了 action label 的正确性？

如果把一个物体视觉上换成更重材质，却保留原动作，数据就产生物理矛盾。

---

## 31.5 Video-to-Action 与 Inverse Dynamics

如果观察到：

\[
I_t,I_{t+1},
\]

可学习 inverse dynamics：

\[
\hat a_t=G(I_t,I_{t+1}).
\]

但对人类视频，\(a_t\) 不是 robot action。

更合理的是预测 latent action / effect：

\[
u_t=G(I_t,I_{t+1}),
\]

再通过 embodiment-specific decoder：

\[
a_t^{robot}=D(u_t,e).
\]

---

## 31.6 Latent Action Model

latent action 试图捕捉“状态如何变化”，而不是具体关节命令。

优势：

- 无需真实 action label；
- 可从人类视频学习；
- 可能跨 embodiment。

难点：

- latent 可控性；
- identifiability；
- one-to-many action；
- 是否能映射到可执行 robot command。

---

## 31.7 Generative World Simulator

生成模型可模拟：

\[
\hat o_{t+1:t+H}=G(o_t,A,c).
\]

如果足够准确，就可以：

- planning；
- policy evaluation；
- data generation；
- failure rehearsal。

但 neural simulator 最危险的是“自洽但错误”：

它可能生成连贯视频，却违反真实接触或摩擦。

---

## 31.8 Cosmos 类 Physical AI World Foundation Model

NVIDIA Cosmos 是这一方向的重要代表。

2025 初期 Cosmos 平台主要提供 world foundation model、video curation、post-training 与 physical AI 数据生成工具。

到 2026 年，Cosmos 3 进一步把：

- vision reasoning；
- world generation；
- action prediction

放进统一的 omnimodal physical-AI 模型框架。

NVIDIA 官方公开资料将 Cosmos 3 描述为可用于 world simulation、reasoning、synthetic data 和 World Action Model backbone 的开放模型。

这里应区分：

- foundation world model 的泛化能力；
- post-trained robot policy 的真实控制能力；
- world generation fidelity。

三者不能混为一个 benchmark。

---

## 31.9 Synthetic Scene / Trajectory Generation

synthetic pipeline：

```text
scene specification
→ asset / world generation
→ physics / neural rollout
→ camera rendering
→ annotation
→ policy training
```

可以扩展 rare scenario 和 long tail。

但必须对 synthetic-to-real gap 做 decomposition：

- appearance gap；
- geometry gap；
- dynamics gap；
- sensor gap；
- behavior gap。

---

## 31.10 Video Model 与 Physics Engine 的互补

Physics engine：

```text
explicit state
+ known dynamics assumptions
→ numerically integrated future
```

Video model：

```text
high-dimensional observation
+ learned data prior
→ plausible future
```

最合理的方向可能不是谁替代谁，而是 hybrid：

\[
\text{physics simulator} + \text{learned residual / rendering / uncertainty}.
\]

Physics engine 负责可约束动力学，生成模型负责难以手工建模的视觉与复杂场景分布。

---

## 31.11 Neural Simulator 的可靠性边界

至少测试五类 intervention：

1. unseen object mass；
2. friction shift；
3. collision geometry change；
4. actuator latency；
5. contact-rich long horizon。

指标不能只用 FVD/视觉质量，还需要：

\[
E_{state}(H),\quad
E_{contact}(H),\quad
E_{reward}(H),\quad
E_{policy-rank}.
\]

其中最后一个问题是：

> simulator 是否至少能正确判断 policy A 比 B 更好？

即使像素不完全准确，这仍可能足够有用。

---

## 31.12 从“看起来真实”到“控制上有用”

World/video model 的评价层级：

### Level 0：Visual realism

人看起来像真的。

### Level 1：Representation consistency

关键对象和关系保持。

### Level 2：Dynamics consistency

动作导致的状态变化正确。

### Level 3：Counterfactual consistency

不同动作产生正确不同未来。

### Level 4：Planning utility

用它规划能提高真实任务成功率。

### Level 5：Policy improvement utility

用生成 experience 训练后，真机 policy 更强。

只有 Level 4–5 才能说明它真正成为机器人智能的一部分。

---

## 31.13 World Action Model：World 与 Action 开始融合

2026 年“world model”和“policy model”的边界开始变模糊。

统一模型可学习：

\[
p(o_{future},a_{future},text\mid history).
\]

它既能预测未来，也能生成行动。

优势是共享 representation；风险是：

- prediction 与 action objective 冲突；
- hallucinated future 影响 action；
- policy evaluation 变得难解释。

这是未来值得重点跟踪的范式。

---

## 最小实验：视频逼真度与控制效用是否相关

训练多个 world model，故意形成不同取舍：

- 高 pixel quality；
- 高 object-state accuracy；
- 高 contact prediction；
- 高 reward prediction。

分别作为 planner model。

画：

\[
\text{video metric} \leftrightarrow \text{real control success}.
\]

如果相关性很弱，就能直接证明“生成得像”不是 robotics world model 的核心目标。

---

## Source anchors

- NVIDIA Cosmos platform: https://www.nvidia.com/en-us/ai/cosmos/
- NVIDIA Cosmos 3, released 2026-05-31: https://research.nvidia.com/labs/cosmos-lab/cosmos3/
- Cosmos-Predict2.5: https://research.nvidia.com/labs/dir/cosmos-predict2.5/

---

## 本章结论

生成式世界模型给机器人研究带来了极大的数据与预测想象空间，但评价标准必须从“画面真实”升级到 **action-conditioned dynamics、counterfactual consistency、planning utility 和 real-policy improvement**。当 world generation、reasoning 与 action generation 开始合并时，机器人领域更需要严格的物理负对照，而不是更漂亮的 demo。
