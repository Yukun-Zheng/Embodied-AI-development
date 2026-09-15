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
<!-- CHAPTER-ENRICHMENT-P41:START -->
## 41.15 Transfer Gap 不应只报一个数字

定义任务指标 \(J\) 后，可写：

\[
G_{transfer}=J_{sim}-J_{real}.
\]

但一个 scalar gap 仍然太粗。更有诊断价值的是按扰动轴分解：

```text
visual gap      → light / texture / exposure
geometry gap    → asset shape / collision mesh / tolerances
dynamics gap    → mass / inertia / friction / damping
sensor gap      → noise / latency / dropped frames
actuation gap   → motor model / backlash / saturation
contact gap     → compliance / deformation / slip
human/world gap → unmodeled agents / long-tail events
```

每一项都应该有可控 intervention，才能判断该增加 randomization、做 system ID、改 simulator，还是收真实数据。

## 41.16 Sim2Real 常见失败

### Randomization 范围越宽越好

错误。过宽分布会把 policy 推向极度保守甚至不可学习的策略；关键是覆盖**真实 posterior**而不是最大化参数范围。

### 只随机视觉却声称解决 reality gap

fine manipulation 失败可能来自 friction/contact/latency，视觉 domain randomization 对这些没有直接作用。

### Simulator success 饱和后继续加算力

当瓶颈是 model bias 时，更多 sim rollout 只会更精确地适配错误 simulator。

### Real fine-tuning 掩盖 zero-shot transfer

如果大量真实数据参与适配，应分别报告 zero-shot sim2real 与 post-adaptation performance，不能把两者合称“sim2real”。

### Digital twin 追求像素真实而忽略 task fidelity

对控制而言，正确的 contact、reachability、latency 可能比 photorealism 更重要。

## 41.17 研究问题

1. Domain randomization 的 distribution 能否由 real-world posterior 在线更新，而不是人工拍脑袋设范围？
2. 哪些 simulator fidelity 维度对 VLA / diffusion policy / locomotion policy 的 sensitivity 不同？
3. World model 生成的 synthetic trajectories 与 physics simulator 数据，分别在哪些 failure mode 上更可信？
4. Real-to-sim reconstruction 是否能形成自动 failure replay：真机失败 → 仿真重建 → counterfactual sweep → 修复？
5. 如何定义 task-sufficient digital twin，使建模预算集中在真正影响 action selection 的变量？
<!-- CHAPTER-ENRICHMENT-P41:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 41`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-41)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
