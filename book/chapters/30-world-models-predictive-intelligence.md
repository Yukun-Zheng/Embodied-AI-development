# Part 30　World Models 与 Predictive Intelligence

## 30.1 World Model 到底是什么

最宽泛地，world model 是对环境状态转移的预测模型：

\[
p(s_{t+1}\mid s_t,a_t).
\]

但机器人里经常只有 observation：

\[
p(o_{t+1}\mid o_{\le t},a_t).
\]

真正有用的 world model 必须回答：

> **如果机器人采取动作 \(a\)，未来与任务有关的世界变量会怎样变化？**

所以它不是“能生成视频”的同义词。

---

## 30.2 State-Space Dynamics Model

经典动力系统：

\[
x_{t+1}=f(x_t,u_t)+w_t,
\]

\[
y_t=h(x_t)+v_t.
\]

learned world model 只是把 \(f\) 或 \(h\) 部分换成可学习函数。

最重要的问题仍然是：state \(x\) 选什么。

---

## 30.3 Latent Dynamics

高维图像可编码：

\[
z_t=E(o_t),
\]

并预测：

\[
\hat z_{t+1}=F(z_t,a_t).
\]

优势：

- 避免像素级细节；
- 更快 planning；
- 可关注 task-relevant features。

风险：

- latent 丢失接触细节；
- prediction loss 与 control relevance 不一致。

---

## 30.4 Object-Centric Dynamics

把世界表示成对象：

\[
S_t=\{x_t^{(1)},\dots,x_t^{(N)}\}.
\]

再学习对象间相互作用：

\[
x_{t+1}^{(i)}=F(x_t^{(i)},\{x_t^{(j)}\}_{j\neq i},a_t).
\]

优点是组合性和可解释性。

对 manipulation 尤其自然，因为动作通常改变少数对象及其关系。

---

## 30.5 Video Prediction

直接预测未来帧：

\[
\hat I_{t+1:t+H}=G(I_{\le t},a_{t:t+H-1}).
\]

它提供丰富监督，但会浪费容量预测大量与控制无关细节：

- texture；
- lighting；
- background motion。

高视觉质量不等于高 dynamics fidelity。

---

## 30.6 Action-Conditioned Video Prediction

如果模型只预测自然视频：

\[
p(I_{future}\mid I_{past}),
\]

它不知道“机器人动作改变未来”的因果接口。

机器人 world model 更需要：

\[
p(I_{future}\mid I_{past},A).
\]

action conditioning 是从 video model 走向 control model 的关键一步。

---

## 30.7 Pixel-Space vs Latent-Space

### Pixel prediction

优点：监督完整、结果可视化。

缺点：昂贵、关注无关细节。

### Latent prediction

优点：紧凑、可能更 task relevant。

缺点：latent 是否保留物理变量需要验证。

真正比较应该固定 planner，测 downstream control，而不是只比较 reconstruction metric。

---

## 30.8 JEPA：Predict Representation, Not Pixels

JEPA 类思想学习在 representation space 中预测目标，而不是重建每个 pixel。

直觉：

> 智能体不需要预测窗帘每个纹理像素，只需要预测与世界结构和动作相关的抽象变化。

可写成：

\[
\hat z_{future}=P(z_{context}).
\]

---

## 30.9 V-JEPA 2

V-JEPA 2 将大规模视频自监督表示与 prediction / planning 连接起来。

机器人研究最值得关注两点：

1. video representation 是否包含 motion / interaction information；
2. action-conditioned predictor 是否足以用于 planning。

不能因为 encoder 在 video benchmark 上强，就自动认为 robot control 会更强。

---

## 30.10 V-JEPA 2.1

Meta 于 2026-03 发布 V-JEPA 2.1，强调更高质量且时间一致的 dense video features。

dense representation 对 robotics 潜在重要，因为精细 manipulation 需要：

- local correspondence；
- object boundary；
- motion consistency；
- spatially dense feature。

但仍必须通过 manipulation / navigation control experiment 证明价值。

---

## 30.11 Latent Action-Conditioned World Model

一种通用结构：

\[
z_t=E(o_t),
\]

\[
\hat z_{t+1}=F(z_t,a_t),
\]

planning 时：

\[
A^*=\arg\max_A R(\hat z_{t+1:t+H}).
\]

如果 action 不是 robot-native，也可以用 latent action \(u_t\)。

难点是 latent action 是否可执行、是否可跨 embodiment。

---

## 30.12 3D / 4D World Model

2D video 无法显式表示：

- metric geometry；
- camera motion 与 object motion 分离；
- occluded structure。

3D/4D world model 可以把状态建立在：

- point cloud；
- voxel；
- neural field；
- dynamic Gaussian；
- object pose graph。

但维度更高、数据要求更强。

---

## 30.13 Contact-Aware World Model

机器人 manipulation 的未来高度依赖 contact mode：

\[
c_t\in\{no\ contact, sticking, sliding, impact, grasped\}.
\]

接触转换是非平滑 dynamics。

只看 RGB 的 predictor 很可能无法精确预测：

- slip；
- normal force；
- micro-contact；
- friction transition。

因此 contact/tactile state 可能必须显式进入 world model。

---

## 30.14 Tactile World Model

加入 tactile：

\[
p(z_{t+1}^{vision},z_{t+1}^{tactile}\mid z_t,a_t).
\]

可用于预测：

- grasp stability；
- contact onset；
- slip；
- deformation。

这类模型可能比纯视觉 world model 更接近 manipulation dynamics。

---

## 30.15 Counterfactual Prediction

真正用于决策的 world model 必须比较不同动作：

\[
p(s'\mid s,do(a_1)),
\quad
p(s'\mid s,do(a_2)).
\]

如果模型只是按数据相关性生成“最常见未来”，就不够用于 action selection。

counterfactual accuracy 是比 video realism 更本质的指标。

---

## 30.16 Uncertainty-Aware Prediction

长期 prediction 不确定性会积累：

\[
H[p(s_{t+H}\mid s_t,A)]\uparrow H.
\]

planner 应考虑：

- epistemic uncertainty；
- multimodal future；
- OOD state。

如果 world model 对错误未来非常自信，planning 反而会被误导。

---

## 30.17 Learned / Neural Simulator

world model 可被当作 simulator：

```text
state + action
→ neural dynamics
→ next state / video / reward
```

优势是速度、可微、可从真实数据拟合。

缺点是 rollout drift：

\[
\epsilon_H\approx\sum_{t=1}^{H}\epsilon_t
\]

甚至会非线性放大。

因此 neural simulator 不能只测 one-step error。

---

## 30.18 Foundation World Model

foundation world model 希望利用大规模视频和物理数据获得通用先验，再 post-train 到具体 embodiment。

理想目标：

\[
W_{general}+D_{robot}\rightarrow W_{robot}.
\]

真正挑战是互联网视频里缺少准确 action、force 和 robot state。

---

## 30.19 World Model + MPC

最直接使用：

\[
A^*=\arg\max_{A}\sum_{k=0}^{H}R(\hat s_{t+k})
\]

subject to learned dynamics。

执行第一步后重规划：

```text
predict
→ optimize actions
→ execute first action
→ observe real world
→ replan
```

真实 observation 能不断纠正 model drift。

---

## 30.20 World Model + Policy Search

world model 可生成候选 rollout，policy search 选择：

- CEM；
- MCTS；
- trajectory optimization；
- diffusion planning；
- learned value。

但搜索质量上限受 world model fidelity 限制。

---

## 30.21 World Model + Evaluator

即使不直接产生 action，world model 也可以：

- imagined rollout；
- failure prediction；
- value estimate；
- policy ranking。

这种“critic/world model”角色可能比完全替代 simulator 更现实。

---

## 30.22 会生成未来视频 ≠ 理解物理规律

视频模型可能依靠视觉统计生成合理-looking future，却在这些变量上错误：

- exact contact；
- object mass；
- friction；
- hidden constraint；
- force propagation。

因此“看起来对”不能作为 physical understanding 的证据。

---

## 30.23 如何证明 World Model 真正提高行动能力

最严格实验：

### Baseline

\[
a=\pi(o)
\]

### World-model agent

\[
a=Planner(W,o).
\]

固定 perception、数据和 policy capacity，比较：

- OOD success；
- sample efficiency；
- counterfactual task；
- recovery；
- perturbation robustness。

再做 shuffled / wrong world model 负对照。

如果错误 world model 与正确 world model 性能相同，就说明 policy 根本没真正利用它。

---

## Source anchors

- Meta V-JEPA 2 / 2.1 repository: https://github.com/facebookresearch/vjepa2
- V-JEPA 2.1 release date in official README: 2026-03-16

---

## 本章结论

World model 的价值不在于“内部有个世界的视频生成器”，而在于它能否提供 **action-conditioned、counterfactual、uncertainty-aware、对控制有用的未来预测**。最终检验标准只有一个：加入 world model 后，机器人是否在真实决策中变得更强。
