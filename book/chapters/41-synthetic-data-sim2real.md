# Part 41　Synthetic Data、Domain Randomization 与 Sim-to-Real

## 41.1 Synthetic RGB / Depth / Segmentation

仿真可以免费获得精确标签：

- RGB；
- depth；
- segmentation；
- normal；
- optical flow；
- pose。

真实世界这些标签往往昂贵。

但 synthetic sensor model 必须接近真实噪声统计。

---

## 41.2 Synthetic Trajectory

轨迹可来自：

- planner；
- scripted expert；
- RL policy；
- mocap retarget；
- world model。

synthetic expert 可能形成过于“干净”的动作分布，导致真实部署遇到 human-like noisy correction 时不适应。

---

## 41.3 Procedural Scene Generation

自动生成：

\[
scene\sim p(geometry,objects,layout,materials).
\]

其价值是覆盖长尾组合。

需要保证生成场景物理可行，而不只是视觉随机。

---

## 41.4 Domain Randomization

训练时随机环境参数：

\[
\phi\sim p(\phi),
\]

\[
\pi^*=\arg\max_\pi \mathbb E_{\phi}[J(\pi;\phi)].
\]

目标是让 real world 落在训练分布内部。

---

## 41.5 Dynamics Randomization

随机：

- mass；
- friction；
- damping；
- motor strength；
- latency；
- payload。

范围过窄无法迁移，过宽会让 policy 过度保守。

---

## 41.6 Visual Randomization

随机：

- texture；
- lighting；
- color；
- camera pose；
- background。

它主要针对 visual gap，而非 dynamics gap。

---

## 41.7 System Identification

从真实数据估计参数：

\[
\phi^*=\arg\min_\phi\sum_t\|s^{real}_{t+1}-f_\phi(s_t,a_t)\|^2.
\]

随后仿真围绕 \(\phi^*\) randomize，比盲目扩大参数范围更有效。

---

## 41.8 Sim-to-Real

标准路径：

```text
train in simulation
→ validate randomized simulation
→ zero-shot real robot
→ collect discrepancy
→ adapt
```

真正 sim2real 报告应同时给 sim performance 与 real performance，量化 transfer gap。

---

## 41.9 Real-to-Sim

把真实世界重建进 simulator：

- geometry scan；
- object pose；
- material estimate；
- system ID。

目标是形成可重复的 digital twin。

---

## 41.10 Real-to-Sim-to-Real

闭环：

```text
real failure
→ reconstruct in sim
→ mass parallel experiments
→ improve policy
→ redeploy real
```

这比一次性 sim2real 更接近长期机器人开发。

---

## 41.11 Digital Twin

digital twin 不是漂亮 3D 模型，而是对任务相关状态和 dynamics 有足够 fidelity 的可计算副本。

评价：

\[
\epsilon_{twin}=D(T_{real},T_{sim}).
\]

距离应定义在 task-relevant quantities 上。

---

## 41.12 Neural Asset / Generative Scene

生成模型可以从图像创建：

- geometry；
- texture；
- scene variation。

但生成 asset 需要额外 physics annotation：

- collision；
- mass；
- articulation；
- friction。

image-to-3D 并不自动等于 robot-ready asset。

---

## 41.13 Reality Gap 分解

建议至少分：

\[
Gap=G_{visual}+G_{geometry}+G_{dynamics}+G_{sensor}+G_{control}+G_{task}.
\]

不同算法解决不同 gap。

不要用 domain randomization 解释所有问题。

---

## 41.14 哪些能力适合在 Simulation 学

更适合：

- locomotion；
- collision avoidance；
- gross motion；
- curriculum exploration；
- rare dangerous events。

更困难：

- fine tactile contact；
- deformable dynamics；
- wear / backlash；
- human interaction nuance。

未来 hybrid real+sim+world-model data 会长期共存。

---

## 最小实验

固定 policy，分别 randomize：视觉、动力学、延迟、接触。

做 2^4 factorial design，量化每种 randomization 对 real transfer 的主效应和交互效应。

---

## 本章结论

Sim-to-real 不是一个技巧，而是一套**误差建模工程**。只有先分解 reality gap，才能知道该用 system ID、randomization、real fine-tuning 还是更好的 simulator。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 41`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-41)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
