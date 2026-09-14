# Part 17　主动感知：让机器人决定“下一眼看哪里”

## 学习目标

理解主动感知不是“多拍几张图”，而是在部分可观测世界里把 sensing 本身纳入 decision；掌握 observability、information gain、next-best-view、task-driven active vision、active touch、viewpoint planning 与 embodiment-agnostic view goal；能设计实验区分“看得更多”与“看到了真正有用的信息”。

---

## 17.1 被动视觉的上限

假设目标物被抽屉边缘完全遮住。即使视觉模型参数无限大，当前 camera ray 根本没有携带目标背面的确定信息。

这不是 recognition model 不够强，而是 observation channel 本身缺信息。

机器人与静态视觉模型的关键区别是：

> 它可以行动，改变自己未来能观察到什么。

因此感知决策本身可以写成 action：

\[
a_t^{sense}\in\mathcal A_{sense}.
\]

## 17.2 Perception–Action Coupling

经典被动 pipeline：

```text
world → sensor → perception → action
```

主动感知：

```text
belief / uncertainty
      ↓
choose sensing action
      ↓
move camera/body/object/touch
      ↓
new observation
      ↓
update belief
      ↺
```

Action 不只是完成任务，也能**制造信息**。

## 17.3 Observability

线性系统：

\[
x_{t+1}=Ax_t+Bu_t,
\qquad y_t=Cx_t.
\]

Observability matrix：

\[
\mathcal O=
\begin{bmatrix}
C\\CA\\CA^2\\\vdots\\CA^{n-1}
\end{bmatrix}.
\]

若 rank 为 \(n\)，理论上可以从输出历史恢复 state。

主动感知可以通过改变 camera pose / interaction，让原本不可观变量进入 observation。

## 17.4 Task-Relevant Uncertainty

不是所有 uncertainty 都值得消除。

假设桌上背景纹理不确定，但抓取只关心：object pose、handle orientation、free approach direction。

更合理的 uncertainty：

\[
U_{task}=U(z_{task-relevant}).
\]

主动感知目标应最大化任务相关信息，而不是重建整个世界到最高精度。

## 17.5 Entropy Reduction

当前 belief entropy：

\[
H(S\mid o_{\le t}).
\]

执行 sensing action \(a\) 后，未来 observation \(O'\) 的预期信息增益：

\[
IG(a)=H(S\mid h_t)
-\mathbb E_{O'}[H(S\mid h_t,a,O')].
\]

其中 \(h_t\) 是历史。

## 17.6 Mutual Information 形式

\[
IG(a)=I(S;O'\mid h_t,a).
\]

如果 sensing action 成本为 \(C(a)\)：

\[
a^*=\arg\max_a IG(a)-\lambda C(a).
\]

这是主动感知最基本的决策式。

## 17.7 Epistemic vs Aleatoric

如果 uncertainty 来自模型不知道（epistemic），换视角可能降低；如果来自不可消除随机性（aleatoric），继续看也没用。

例如：

- 遮挡后把手朝向未知 → epistemic，可移动 camera；
- 物体下一秒可能随机滑向两侧 → aleatoric，不一定靠观察解决。

主动系统必须区分二者，否则会陷入无意义 sensing loop。

## 17.8 Next-Best-View

候选相机 pose \(v\in SE(3)\)，选择：

\[
v^*=\arg\max_v
\left[
IG(v)-\lambda d(v)-\beta R(v)
\right].
\]

其中：

- \(d(v)\)：移动距离/时间；
- \(R(v)\)：碰撞/安全/可达性风险。

NBV 不是纯视觉优化，还受机器人 kinematics 限制。

## 17.9 Coverage-Based NBV

经典 3D reconstruction 可最大化 unseen surface coverage：

\[
U(v)=\#\text{new visible voxels}.
\]

适合建图，但 manipulation 未必需要完整 coverage。

如果只需要确认插孔位置，多绕一圈重建物体背面是浪费。

## 17.10 Task-Driven NBV

直接优化 task variable：

\[
IG_{task}(v)=I(Z_{task};O_v).
\]

例如抓取前只关心 grasp affordance / collision corridor 的 uncertainty。

这比 generic reconstruction 更符合 robot utility。

## 17.11 Learned View Utility

可以训练：

\[
Q_{view}(b_t,v,g)
\]

预测“移动到这个视角后，最终 task success 会提升多少”。

监督可以来自 simulation oracle：尝试候选 view，随后执行 task，测 downstream improvement。

这样 active perception 直接对 success 优化，而不依赖手工 entropy proxy。

## 17.12 Occlusion Reasoning

Occulusion 不等于 object absence。地图/representation 至少区分：

```text
visible free
visible occupied
occluded unknown
```

若目标可能在 unknown 区域，应主动选择能揭示该区域的 viewpoint。

## 17.13 Viewpoint Geometry

给定目标表面法向 \(n\)、camera optical axis \(z_c\)，极端 grazing angle 会降低 depth/visual quality。

可加入 viewing angle score：

\[
S_{angle}=n^T(-z_c).
\]

还需考虑 distance、field-of-view、focus、self-occlusion。

## 17.14 Self-Occlusion

机器人自己的手臂/夹爪可能挡住 camera。特别是 wrist camera，接近目标时 gripper 常占据大量画面。

主动策略应把 robot geometry 本身加入 visibility model。

## 17.15 Head / Wrist / Base：谁来动？

同一个 desired viewpoint 可以由不同 body part 实现：

- 转 head；
- 移 wrist camera；
- 移 base；
- 蹲下/侧身；
- 拿起物体转动。

高层 perception objective 与具体 embodiment action 应解耦。

## 17.16 Embodiment-Agnostic View Goal

定义高层 view goal：

\[
g_v=(target,relative\ pose,visibility,scale).
\]

它表达“我需要从目标右上方约 30 cm、无遮挡地看把手”，而不指定用 neck/base/arm 怎么完成。

每种 embodiment 再用自己的 planner：

\[
\pi_e(a\mid g_v,s_e).
\]

这是一种有潜力的跨本体主动感知接口。

## 17.17 Active Object Manipulation for Perception

有时移动 camera 不够，可以移动物体：

- 转动盒子看背面；
- 拉开抽屉观察内部；
- 抬起布料查看被遮挡区域。

这时 sensing action 会改变 task state，需要同时评估 information gain 与 state disturbance。

## 17.18 Active Touch

触觉也可以主动获取信息：

- 轻推估质量/摩擦；
- 捏压估 stiffness；
- 滑动估 texture；
- 沿轮廓探索 shape。

选择 probe action：

\[
a^*=\arg\max_a I(\phi_{material};T'\mid a)-\lambda C(a).
\]

这是真正 physical active sensing。

## 17.19 Dual Control

经典 dual control 中，一个 control action 同时：

1. 驱动系统完成目标；
2. 激发系统以学习未知 dynamics/parameter。

例如抓住未知重量物体时，先做小幅试探 acceleration，可估 mass，再决定后续高速动作。

主动感知其实是 dual-control 思想在 perception 上的自然延伸。

## 17.20 Exploration vs Task Execution

纯 exploration 最大化知识；task-driven system 需要权衡任务时间：

\[
J=J_{task}+\lambda J_{info}+\beta J_{cost}.
\]

信息不是越多越好。一个 5 秒能做完的任务，不应为了 1% uncertainty reduction 观察一分钟。

## 17.21 Stopping Rule

何时停止 sensing？

可设：

\[
\max_v IG(v)<\epsilon
\]

或当前 task success confidence 超过阈值：

\[
P(success\mid b_t)>\tau.
\]

否则 active perception 容易无限循环。

## 17.22 Active Perception 与 VLA

三种融合：

### 模式 A：VLA 自己输出 camera/body sensing action

优点端到端；难解释为什么看。

### 模式 B：独立 uncertainty / view planner

先判断“需要更多信息吗”，再给 VLA/robot controller view goal。

### 模式 C：World model imagination

对候选 view 预测未来 observation/value，再选最好。

模式 B/C 更容易做可证伪实验。

## 17.23 Active Perception 与 World Model

World model 可以回答：

\[
\hat o_{t+1}=F(o_t,a_t^{sense}).
\]

然后估计候选 observation 对 belief/task 的价值。

但若 world model 对遮挡区域 hallucinate 过度自信，NBV 会被误导，因此 uncertainty calibration 尤其重要。

## 17.24 Active Mapping

Navigation 中同时定位、建图、规划探索路径：

\[
\text{where should I move to improve map and localization?}
\]

这与 manipulation active view 本质相同，只是空间尺度不同。

## 17.25 Information Bottleneck 与 Attention

视觉 attention “看哪里”与真正 active perception 不同。Attention 只在**已有图像内部**分配计算；active perception 改变 sensor pose，从物理世界采集原本不存在的新证据。

不要把 Transformer attention map 当成 active vision。

## 17.26 主动感知的公平 Benchmark

需要控制：

- 初始 observation 一样；
- task difficulty 一样；
- sensing motion cost 计入；
- 被动 baseline 可使用相同 model compute；
- 对 active 方法报告额外时间/能耗。

否则“多看几次所以更准”是显然的，不构成研究贡献。

## 17.27 核心指标

除了最终 success：

\[
\Delta U=U_{before}-U_{after},
\]

\[
\Delta P_{succ}=P_{succ}^{after}-P_{succ}^{before},
\]

再报告：sensing distance、time、number of views、collision risk、compute。

最重要的是单位信息成本：

\[
\eta=\frac{\Delta P_{succ}}{C_{sense}}.
\]

## 常见失败

- 只最大化 surface coverage，与 task 无关；
- uncertainty 实际未校准；
- NBV 使用 simulator oracle occlusion；
- view action 本身造成物体移动，却仍用旧 belief；
- active method 多花 5 倍时间但只报告 success；
- policy 本身已从多视角训练，baseline 不公平；
- 模型 hallucinate 被遮挡内容，反而不愿主动看。

## 最小实验

构造“目标把手被遮挡”的操作任务。三个系统：固定 camera、随机第二视角、task-driven NBV。每次 sensing 都计入运动时间。最终比较：handle pose uncertainty、grasp success、额外时间和单位 sensing cost 的成功率增益。

进一步负对照：让 NBV 最大化与任务无关的背景 reconstruction，看是否仍能提升抓取。

## 研究问题

1. 通用 VLA 是否应该学习“什么时候不行动，而是先获取信息”？
2. 如何让主动感知目标跨 embodiment 表达，而不依赖某台机器人的 head/base/arm？
3. World model 应该主动预测“我去看那里能得到什么证据”，还是直接学习 observation value？
4. 机器人是否可以通过长期经验自动形成 sensing skill library？
