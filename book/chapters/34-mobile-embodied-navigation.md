# Part 34　移动机器人、导航与 Embodied Navigation

## 34.1 Mobile Base

差速底盘：

\[
\dot x=v\cos\theta,\quad
\dot y=v\sin\theta,\quad
\dot\theta=\omega.
\]

全向底盘则具有更自由的平面速度。

navigation policy 必须尊重 platform kinematics。

---

## 34.2 Localization

导航首先要知道“我在哪里”。

估计：

\[
p(x_t\mid o_{0:t},a_{0:t-1}).
\]

来源可包括：

- wheel odometry；
- IMU；
- camera；
- LiDAR；
- map matching。

---

## 34.3 Mapping

地图可以是：

- occupancy grid；
- metric map；
- semantic map；
- topological graph；
- neural map。

不同任务需要不同 map。

对“去冰箱”而言 semantic topology 可能比厘米级 dense map 更重要；对窄通道避障则相反。

---

## 34.4 Global / Local Navigation

经典 stack：

```text
global planner
→ path
→ local planner
→ velocity command
→ base controller
```

现代 learned navigation 并没有消除这个分层问题，只是可能把其中某些模块变成 learned policy。

---

## 34.5 Obstacle Avoidance

局部避障要处理动态障碍：

\[
\mathcal O_t=\{O_t^{static},O_t^{dynamic}\}.
\]

仅用静态 occupancy map 会在有人移动时失败。

---

## 34.6 Exploration

未知地图中要同时：

- move；
- reduce uncertainty。

可定义 frontier 或 information gain：

\[
a^*=\arg\max_a I(M;O_{future})-\lambda C(a).
\]

这和主动感知是同一数学结构。

---

## 34.7 Active Mapping

机器人不只是被动建图，而是主动选择轨迹以提高地图质量。

例如绕到物体背后、进入未探索房间。

---

## 34.8 Visual Navigation

只用 RGB 做导航时，模型必须隐式解决：

- localization；
- obstacle understanding；
- scene semantics；
- action selection。

视觉导航是研究 representation 与 memory 的经典场景。

---

## 34.9 PointNav / ObjectNav

### PointNav

目标是相对/全局坐标点。

### ObjectNav

目标是语义对象，例如“找到冰箱”。

ObjectNav 更依赖 semantic prior 和 exploration。

---

## 34.10 Vision-Language Navigation

VLN 输入自然语言路径描述：

> “走出房间，左转，在沙发后面的门进入厨房。”

需要：

- instruction grounding；
- spatial memory；
- landmark recognition；
- temporal progress。

---

## 34.11 Embodied Question Answering

机器人需要行动来获得回答，例如：

> “厨房里有几个红杯子？”

这将 question answering 变成 active perception / exploration problem。

回答质量取决于行动策略，而不仅是 VLM。

---

## 34.12 Semantic Navigation

语义先验可以引导搜索：

\[
P(location\mid object,scene).
\]

例如“微波炉更可能在厨房”。

但过强 prior 会造成 shortcut：新环境布局不符合常识时失败。

---

## 34.13 Navigation + Manipulation

mobile manipulation 的真实任务：

```text
navigate to workspace
→ choose base pose
→ manipulate
→ possibly move base again
```

base placement 应优化：

\[
J=J_{nav}+\lambda_rJ_{reach}+\lambda_vJ_{visibility}.
\]

---

## 34.14 Home / Office / Warehouse

不同场景约束完全不同：

### Home

狭窄、动态、人类共存、物体高度变化。

### Office

门、桌椅、人员流动。

### Warehouse

大尺度、结构化、高 throughput、安全区域明确。

不能用单一 navigation benchmark 推断所有场景能力。

---

## 34.15 Habitat / BEHAVIOR / OmniGibson

这些平台推动了 embodied navigation / household activity 研究。

使用 benchmark 时要关注：

- scene realism；
- interaction physics；
- sensor model；
- task reset；
- training scene leakage。

---

## 34.16 Drone / Field Robot / Autonomous Vehicle

它们与室内机器人共享同一个核心：

\[
\text{perception}\rightarrow\text{belief}\rightarrow\text{planning}\rightarrow\text{control}.
\]

但 dynamics、速度和安全边界不同。

Embodied AI 不应狭义等于桌面机械臂。

---

## 最小实验

构造同一 ObjectNav 任务：

- reactive vision policy；
- policy + recurrent memory；
- policy + explicit map；
- policy + semantic map；
- active exploration policy。

测 success、SPL、visited area、重复路径率。

---

## 本章结论

导航展示了一个重要事实：智能必须维护跨时间的空间状态。没有 localization、memory、map 或等价内部机制，长距离具身任务很容易退化成短视的 reactive behavior。
<!-- CHAPTER-ENRICHMENT-P34:START -->
## 34.17 Navigation Failure Taxonomy

### Localization drift

路径规划正确，但 belief pose 漂移，导致 map-relative waypoint 与真实世界错位。应同时画 localization error 与 task failure，而不是只看 SPL。

### Semantic shortcut

ObjectNav policy 可能学到“冰箱常在厨房右侧”等数据集统计，而没有真正建立可更新的 spatial belief。改变 layout 后性能骤降是典型证据。

### Map staleness

动态障碍、开关门、人群移动会使静态 map 过期。系统必须区分 persistent map 与 transient obstacle state。

### Planner–controller mismatch

global path 在几何上可行，但 local controller 受最小转弯半径、加速度、轮胎/底盘约束无法跟踪。

### Memory aliasing

相似走廊/房间产生 perceptual aliasing。单帧视觉 policy 可能反复走回已访问区域，却把它当新位置。

## 34.18 Navigation 的完整闭环接口

```text
RGB / depth / LiDAR / odometry
→ localization + belief
→ metric / semantic / topological memory
→ global goal / frontier selection
→ path / waypoint
→ local collision-aware command
→ base controller
→ physical motion
→ new observation
```

端到端 policy 可以隐藏中间表示，但不能消除这些功能需求。研究者应通过 intervention 判断功能究竟是否存在，例如冻结 memory、注入 pose error、交换地图、移动动态障碍。

## 34.19 研究问题

1. Learned implicit memory 何时比 explicit metric/semantic map 更高效，何时只是更难诊断？
2. ObjectNav/VLN 的 language prior 对真正新布局是帮助还是 shortcut？
3. Mobile manipulation 中 base placement 应由高层 VLA、motion planner 还是 whole-body optimizer 决定？
4. 如何把 localization uncertainty 传播到 learned navigation policy，而不是只把一个估计 pose 当真值？
5. 对家庭机器人，SPL 是否仍是合理主指标，还是应联合 success、human disturbance、time、energy 与 intervention rate？
<!-- CHAPTER-ENRICHMENT-P34:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 34`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-34)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
