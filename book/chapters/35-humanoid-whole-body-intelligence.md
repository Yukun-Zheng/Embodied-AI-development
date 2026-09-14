# Part 35　Legged Locomotion、Humanoid 与 Whole-Body Intelligence

## 35.1 Legged Robot State / Action

人形状态不仅有关节：

\[
s=[q,\dot q,x_{base},R_{base},v_{base},\omega_{base},c,\dots].
\]

其中 floating base 不能直接被 actuator 控制。

动作通常是：

- joint torque；
- joint target；
- residual；
- task-space target。

---

## 35.2 Gait

步态可以描述为周期 contact sequence。

双足需要在：

```text
left support
→ double support
→ right support
```

之间稳定切换。

学习式 locomotion 把许多手工 gait 设计隐式吸收到 policy 中，但接触结构仍存在。

---

## 35.3 Balance

balance 的核心是控制质心与支撑域。

简单静态条件：

\[
CoM_{proj}\in SupportPolygon.
\]

动态情况下必须考虑 momentum。

---

## 35.4 ZMP / Capture Point

ZMP 和 capture point 提供经典稳定性直觉。

对线性倒立摆，capture point：

\[
\xi=x+\frac{\dot x}{\omega_0}.
\]

它告诉我们：机器人必须把下一步脚放到哪里才能“接住”当前动量。

---

## 35.5 Centroidal Dynamics

whole-body motion 可先关注全身 momentum：

\[
\dot h=\sum_i w_i + w_g.
\]

这比直接在所有 joint 上思考更适合 balance / loco-manipulation。

---

## 35.6 Quadruped Locomotion

四足拥有更大 support redundancy，因此 locomotion 更容易实现 robust dynamic gait。

但复杂地形仍要求：

- foothold；
- terrain perception；
- contact adaptation。

---

## 35.7 Biped Locomotion

双足 margin 更小，fall cost 更高。

sim-to-real 必须处理：

- actuator dynamics；
- latency；
- foot contact；
- state estimator；
- terrain shift。

---

## 35.8 Locomotion RL

常见 reward：

\[
r=w_v r_v+w_o r_{orient}-w_eE-w_sSlip+\dots
\]

reward engineering 能学出稳定 gait，但也可能产生 unnatural shortcut。

motion prior 是减少 reward engineering 的重要方向。

---

## 35.9 Motion Imitation

给定 reference motion：

\[
q^{ref}_{1:T},x^{ref}_{1:T},
\]

policy 学习跟踪：

\[
r_{track}=-\|q-q^{ref}\|^2-\lambda\|x-x^{ref}\|^2.
\]

它可以从 mocap 大规模获得 dense supervision。

---

## 35.10 Motion Retargeting

人类 motion 需要映射到机器人 morphology。

必须保持：

- end-effector semantics；
- balance；
- joint limits；
- contact timing。

所以 retargeting 不只是骨架缩放。

---

## 35.11 Human Motion Prior

大规模 human motion 提供：

- natural coordination；
- locomotion diversity；
- transition；
- recovery pattern。

它可能成为 humanoid 的“motor pretraining data”。

---

## 35.12 Humanoid Teleoperation

全身遥操作可通过：

- VR；
- motion capture；
- camera-based human pose；
- exoskeleton。

数据采集需要同时解决 retargeting 和 balance。

---

## 35.13 Whole-Body Motion Tracking

whole-body tracking 的价值是把多种行为统一成同一个训练目标：

\[
\pi(s,reference)\rightarrow a.
\]

reference 可以来自人类动作、生成 motion 或 planner。

---

## 35.14 SONIC：Scaling Humanoid Motion Tracking

NVIDIA SONIC 把“规模化”明确带入 humanoid low-level control：通过扩大模型、motion data 和计算，训练统一 whole-body motion tracking controller。

2026 年该工作进入 Science Robotics，并公开模型/工程生态。

它的重要意义不是某个舞蹈 demo，而是提出：

> motion tracking 可以成为 humanoid motor foundation model 的 scalable pretraining task。

---

## 35.15 Whole-Body Control

whole-body task 可能同时包括：

- CoM；
- foot contact；
- hand target；
- gaze；
- collision。

传统方法可用 hierarchical QP。

learned policy 则需要隐式或显式满足这些约束。

---

## 35.16 Loco-Manipulation

真正人形任务要求边走边操作：

```text
locomotion
+
manipulation
+
balance
+
perception
```

不能简单“腿策略 + 手策略”相加，因为上身动作会改变全身 momentum。

---

## 35.17 Humanoid Manipulation

相比固定机械臂，人形有：

- moving base；
- torso；
- head/gaze；
- two arms；
- hands；
- balance constraints。

它增加自由度，也增加 failure modes。

---

## 35.18 Whole-Body VLA

2026 的 Gemini Robotics 2、Helix 02、GR00T 路线表明 VLA / foundation policy 正从 tabletop 进入 whole-body。

但必须追问：

- VLA 输出什么 action？
- balance 由谁负责？
- servo rate？
- low-level motion prior 是否冻结？
- fall safety 怎么做？

“feet-to-fingertips”是系统范围描述，不等于全部动力学都由一个 Transformer 端到端解决。

---

## 35.19 Fall Detection / Recovery

fall recovery 必须包括：

- early instability detection；
- safe fall；
- impact mitigation；
- get-up policy。

部署系统需要把跌倒当正常可恢复事件，而非实验终止。

---

## 35.20 Energy、Speed 与 Reliability

humanoid benchmark 不能只测 success。

还要测：

\[
E/task,\quad time/task,\quad falls/hour,\quad interventions/hour.
\]

商业价值往往由这些指标决定。

---

## 35.21 从 Tabletop 到 Feet-to-Fingertips

能力扩张引入新的闭环：

```text
head motion changes camera
leg motion changes arm workspace
arm motion changes balance
contact changes whole-body dynamics
```

这就是 whole-body intelligence 的本质：所有子系统互相改变彼此的状态空间。

---

## 35.22 General-Purpose Humanoid 的现实瓶颈

截至 2026 仍包括：

- reliability；
- battery / thermal；
- dexterity；
- safe human coexistence；
- long-horizon autonomy；
- data collection；
- maintenance cost；
- fall robustness。

单个 impressive demo 不能消除这些工程事实。

---

## Source anchors

- NVIDIA SONIC: https://nvlabs.github.io/GEAR-SONIC/
- Google DeepMind Gemini Robotics 2: https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Figure Helix 02: https://www.figure.ai/news/helix-02
- NVIDIA GR00T N1.6: https://research.nvidia.com/labs/gear/gr00t-n1_6/

---

## 最小实验

在 humanoid 上分级比较：

1. locomotion-only；
2. upper-body manipulation with fixed feet；
3. locomotion + reach；
4. full loco-manipulation。

记录：success、falls、CoM margin、energy、task time。

这样可以量化 whole-body coupling 到底带来多少难度。

---

## 本章结论

Humanoid 不是“机械臂加两条腿”。当视觉、手臂、躯干、腿和接触同时闭环时，局部动作会改变全身可观测性和动力学。Whole-body intelligence 真正要求把 **motion prior、balance、manipulation、perception 与高层任务**连接成多时间尺度系统。