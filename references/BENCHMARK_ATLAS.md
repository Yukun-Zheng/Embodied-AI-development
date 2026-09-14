# Benchmark / Simulator / Dataset Atlas

> 机器人领域最危险的习惯之一，是把“某 benchmark 上更高”直接翻译成“更强具身智能”。本 Atlas 把常见平台按**环境、身体、观测、动作、任务结构、评测维度、最适合回答的问题、不能回答的问题**统一整理。
>
> Benchmark 版本变化很快；具体 task 数、asset 数以对应 release 的官方文档为准。这里优先记录长期稳定的研究定位。

---

# 1. 先区分四种东西

## Simulator

提供 physics / rendering / sensor / robot dynamics。

例：MuJoCo、SAPIEN、Isaac Sim。

## Framework

在 simulator 上提供 training / env / RL / robot interfaces。

例：Isaac Lab、robosuite、ManiSkill。

## Benchmark

固定任务、数据分布、metric、protocol。

例：RLBench、CALVIN、LIBERO。

## Dataset

提供 demonstrations / trajectories / videos，不一定定义统一测试环境。

例：Open X-Embodiment、DROID、LeRobot datasets。

同一个项目可能兼具多个角色，但研究论文必须说明自己实际使用的是哪一层。

---

# 2. Classical / Manipulation Platforms

## MuJoCo

### 类型

Physics simulator。

### 强项

- fast rigid-body dynamics；
- contact-rich control；
- mature robotics/control ecosystem；
- CPU simulation 非常实用。

### 适合

- control；
- RL；
- manipulation；
- locomotion；
- model-based control。

### 不能单独证明

- photorealistic visual generalization；
- real sensor robustness；
- sim-to-real without anchor。

---

## SAPIEN

### 类型

Simulation / rendering platform。

### 强项

- articulated objects；
- manipulation；
- physically interactive scenes；
- 与 ManiSkill 等 robot-learning ecosystem 紧密关联。

### 适合

- articulated-object manipulation；
- RGB-D / point cloud policy；
- synthetic data；
- large-scale robot learning。

---

## Isaac Sim / Isaac Lab

### 类型

GPU-oriented simulation + robot-learning framework。

### 强项

- parallel simulation；
- modern NVIDIA GPU pipeline；
- RL / imitation / domain randomization；
- complex robots / humanoids；
- synthetic sensors。

### 适合

- humanoid/legged；
- large parallel RL；
- whole-body control；
- synthetic data；
- sim-to-real workflow。

### 研究注意

高 throughput 不等于正确 physics。仍要验证：

- contact solver；
- asset inertial parameters；
- render/sensor domain；
- real hardware anchor。

---

# 3. Meta-World

### 类型

MuJoCo manipulation benchmark / task suite。

### 核心用途

多任务 continuous-control / meta-RL / generalization。

### 观测

常见 state observation；部分工作扩展视觉。

### 适合回答

- multi-task learning；
- task conditioning；
- RL / imitation algorithm behavior。

### 不适合直接回答

- large-scale visual grounding；
- realistic household perception；
- real-world contact robustness。

---

# 4. robosuite

### 类型

MuJoCo-based manipulation framework。

### 强项

- standardized robot arms；
- manipulation task construction；
- controller options；
- OSC / joint control 接口清楚。

### 最适合教学

它非常适合连接：

```text
robot model
→ controller
→ manipulation env
→ learning policy
```

比一开始就进复杂 foundation benchmark 更容易看清低层系统。

---

# 5. RLBench

### 类型

Language-described manipulation benchmark / task suite。

### 平台传统

基于 CoppeliaSim / PyRep 生态。

### 强项

- 大量不同 manipulation task；
- language task descriptions；
- demonstration generation；
- 视觉 policy benchmarking。

### 适合回答

- multi-task manipulation；
- language conditioning；
- 3D/voxel/point-cloud representation；
- imitation / diffusion policy。

### 典型风险

- scripted demonstration distribution；
- simulator-specific visual/physics cues；
- task success ≠ real-world deployment。

---

# 6. CALVIN

### 类型

Long-horizon language-conditioned manipulation benchmark。

### 核心价值

不是只测单个 primitive，而是测连续多步 skill composition / sequence completion。

### 适合回答

- language-conditioned policy；
- long-horizon execution；
- compositional skill chaining；
- memory / planning。

### 推荐额外指标

除了官方 sequence metric，再报告：

- per-skill success；
- first-failure position；
- recovery ability；
- error accumulation。

否则难以知道长任务到底在哪里断。

---

# 7. LIBERO

### 类型

Language-conditioned robot manipulation benchmark，常用于 lifelong / transfer / representation research。

### 强项

- 多 task suite；
- language instruction；
- spatial/object/task variations；
- continual-learning evaluation 生态。

### 适合回答

- representation transfer；
- lifelong learning；
- task generalization；
- imitation policy。

### 注意

如果研究的是“continual intelligence”，不能只报 final average；必须附：

$$
P_{i,j}
$$

和 forgetting / forward transfer。

---

# 8. ManiSkill

### 类型

SAPIEN-based robot manipulation benchmark / framework。

### 强项

- GPU simulation；
- RGB-D / point cloud；
- diverse manipulation；
- RL / imitation；
- articulated objects。

### 适合回答

- 3D policy；
- RL scaling；
- motion planning + learning；
- sim data generation。

### 注意

平台 throughput 很高，容易让研究变成“更大训练量”。应控制 environment steps / wall-clock / data budget。

---

# 9. RoboTwin / RoboTwin 2.x

### 类型

面向双臂/机器人学习的模拟与评测平台，强调多任务、数据生成与现代 policy 集成。

### 强项

- 双臂任务；
- RGB/depth/point-cloud data；
- modern imitation/VLA policy interface；
- 可作为多模型统一实验平台。

### 适合回答

- bimanual coordination；
- ACT / DP3 / VLA comparison；
- shared data schema；
- representation/action-interface study。

### 使用原则

若比较不同方法，必须统一：

```text
same tasks
same demonstrations
same randomization
same controller
same success predicate
same evaluation seeds
```

否则平台统一了，实验仍不公平。

---

# 10. Push-T

### 类型

小型 visuomotor manipulation task。

### 为什么重要

它足够简单，可以明确看出：

- multimodal action distribution；
- diffusion vs regression；
- observation history；
- receding horizon。

### 教材定位

Push-T 很适合**机制最小实验**，不适合证明 general-purpose robotics。

这正是好 benchmark 的另一种价值：可解释，而不是“大”。

---

# 11. ALOHA / Mobile ALOHA Task Ecosystem

### 类型

真实低成本双臂 / mobile-manipulation hardware + demonstration ecosystem。

### 强项

- teleoperation data；
- bimanual manipulation；
- ACT/action chunking；
- real robot long-horizon tasks。

### 适合回答

- imitation learning；
- bimanual coordination；
- data collection economics；
- real-world policy deployment。

### 研究注意

hardware calibration、camera placement、human demonstrator skill 都是隐藏变量。

---

# 12. Habitat

### 类型

Embodied navigation simulator / benchmark ecosystem。

### 强项

- large 3D scenes；
- navigation；
- PointNav / ObjectNav / embodied tasks；
- standardized metrics。

### 适合回答

- navigation memory；
- mapping；
- active exploration；
- visual-language navigation；
- embodied agent planning。

### 不能自动回答

- contact-rich manipulation；
- high-fidelity actuator dynamics。

---

# 13. BEHAVIOR / OmniGibson

### 类型

Interactive household activity benchmark / simulator ecosystem。

### 核心价值

更强调：

- household scenes；
- many objects；
- long-horizon activity；
- interaction / state change。

### 适合回答

- embodied task planning；
- household manipulation；
- long-horizon memory；
- scene graph / object state。

### 难点

复杂度高会使 failure diagnosis 更难，所以不适合所有新方法的第一轮最小实验。

---

# 14. Adroit / Dexterous-Hand Environments

### 类型

Dexterous manipulation control benchmark family。

### 强项

- high-dimensional continuous action；
- contact-rich hand control；
- RL / imitation。

### 适合回答

- action representation；
- dexterous RL；
- trajectory prior。

### 局限

state-based benchmark success 与真实 tactile dexterity 相距很远。

---

# 15. Locomotion / Humanoid Benchmark 不是一个单一体系

常见研究分别使用：

- MuJoCo humanoid；
- Isaac Gym / Isaac Lab custom tasks；
- motion-tracking datasets；
- real humanoid platforms。

所以 humanoid paper 横向比较尤其危险。

至少统一报告：

```text
robot morphology
control frequency
action space
low-level controller
reference motion source
terrain distribution
fall/reset rule
energy
real vs sim
```

---

# 16. Open X-Embodiment

### 类型

多来源机器人 dataset mixture / standardization effort，而不是单一物理 benchmark。

### 核心价值

证明 robot data 可以跨实验室汇聚，并支持 generalist policy scaling。

### 适合回答

- dataset mixture；
- cross-robot pretraining；
- action normalization；
- foundation policy。

### 不能自动证明

unseen morphology zero-shot generalization。

---

# 17. DROID

### 类型

大规模真实 in-the-wild manipulation dataset。

### 强项

- scene diversity；
- real robot interaction；
- data scaling。

### 适合回答

- pretraining / representation；
- real-world dataset value；
- data-mixture scaling。

### 研究问题

真正要看的是：新增真实多样性在哪个 OOD 维度提升，而不是只看数据小时数。

---

# 18. LeRobot Dataset / Tooling Ecosystem

### 类型

开放机器人数据、模型与训练工具生态。

### 价值

把：

```text
data schema
policy training
robot interfaces
model sharing
```

做得更标准化。

对教材尤其重要，因为它让学生能用较统一方式复现多个 robot policy。

---

# 19. Benchmark 选型：按研究问题，不按热度

## 如果研究 Action Distribution

优先：

- Push-T；
- 简单 manipulation；
- controlled multimodal tasks。

原因：能清晰做 regression/diffusion/flow mechanism test。

## 如果研究 3D Representation

优先：

- RLBench；
- ManiSkill；
- RoboTwin。

要求：加入 camera/geometry OOD。

## 如果研究 Long-Horizon Memory

优先：

- CALVIN；
- Habitat/ObjectNav；
- BEHAVIOR 类 long activity。

## 如果研究 Cross-Embodiment

不能只选多个已见 robot task。

必须构造：

```text
train morphologies
→ held-out morphology
→ zero/few-shot adaptation curve
```

## 如果研究 Humanoid Whole-Body

优先选择能明确读取：

- contact；
- centroidal state；
- motor command；
- energy；
- fall event

的平台，而不是只提供 video success。

---

# 20. Benchmark Difficulty 的五个维度

不要用一个“难/简单”形容任务。

定义：

$$
D=(D_{perception},D_{dynamics},D_{horizon},D_{OOD},D_{system})
$$

### Perception Difficulty

- clutter；
- occlusion；
- moving camera。

### Dynamics Difficulty

- contact；
- deformable；
- friction uncertainty。

### Horizon Difficulty

- steps；
- recovery requirement；
- memory duration。

### OOD Difficulty

- new object；
- scene；
- task；
- physics；
- embodiment。

### System Difficulty

- real-time；
- asynchronous sensors；
- safety；
- hardware noise。

两个 benchmark 总 success 一样，可能难在完全不同维度。

---

# 21. 一个统一 Evaluation Matrix

建议任何平台都最终整理成：

| Dimension | ID | OOD-1 | OOD-2 | Intervention |
|---|---:|---:|---:|---:|
| Object |  |  |  |  |
| Scene |  |  |  |  |
| Task |  |  |  |  |
| Physics |  |  |  |  |
| Embodiment |  |  |  |  |
| Horizon |  |  |  |  |

再附：

- latency；
- energy；
- intervention rate；
- recovery rate；
- confidence interval。

这比一个平均 success rate 更接近真正“能力地图”。

---

# 22. 教材的 Benchmark 原则

```text
Toy task     → isolate mechanism
Benchmark    → test breadth
Real robot   → test physical validity
Cross-domain → test generalization
Long-running → test reliability/development
```

没有任何一个 benchmark 能同时承担五种角色。

一个严谨研究路线应该逐级扩张，而不是一开始就在最复杂平台堆模型、最后不知道提升从哪里来。