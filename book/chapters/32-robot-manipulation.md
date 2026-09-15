# Part 32　机器人操作：从抓取到长时程任务

## 32.1 Manipulation 的本质

机器人操作不是“把末端移动到目标位姿”，而是主动改变世界状态：

\[
s_{t+1}=F(s_t,a_t,c_t),
\]

其中 \(c_t\) 表示接触模式。Manipulation 的难点来自：

- 几何约束；
- 接触与摩擦；
- 对象动力学；
- 部分可观测；
- 多模态动作；
- 长时程误差累积。

所以操作系统必须把 perception、planning、control、learning 放进同一个闭环。

---

## 32.2 Reach / Push / Pull

最基础三类动作已经包含机器人操作的核心结构。

### Reach

目标是让末端进入目标 region：

\[
\|x_{ee}-x_g\|<\epsilon.
\]

### Push

末端通过接触改变物体状态：

\[
x_{obj,t+1}=f(x_{obj,t},x_{ee,t},u_t,\mu).
\]

### Pull

除了接触，还依赖稳定约束或 grasp。

这三个 primitive 形成很多复杂任务的基础。

---

## 32.3 Pick and Place

典型 pipeline：

```text
object detection / pose
→ pre-grasp
→ approach
→ close gripper
→ verify grasp
→ transport
→ pre-place
→ release
→ verify placement
```

真正系统中必须显式处理：

- failed grasp；
- object slip；
- collision；
- uncertain pose；
- placement tolerance。

一次性从 RGB 到 trajectory 的 policy 也隐式承担了这些步骤。

---

## 32.4 Grasp Planning

抓取不是“夹爪中心对准物体”。

稳定 grasp 需要考虑：

- contact point；
- surface normal；
- friction cone；
- force closure；
- collision；
- downstream task。

任务相关抓取比通用稳定抓取更重要。例如拿锤子时，抓住锤头可能稳定，却不利于使用。

---

## 32.5 Grasping in Clutter

杂乱环境引入：

- occlusion；
- object entanglement；
- narrow free space；
- collision uncertainty。

因此策略可能先做 non-prehensile rearrangement，再抓取目标。

这说明 perception 和 manipulation 是耦合的：

> 有时最优动作不是完成任务，而是先让世界变得更容易看、更容易抓。

---

## 32.6 Contact-Rich Manipulation

插入、拧、擦、拉链、折叠都依赖持续接触。

此时视觉误差可能很小，但接触力差异决定成败。

控制目标可写成：

\[
\min_a \mathcal L_{pose}+\lambda_f\mathcal L_{force}+\lambda_c\mathcal L_{contact}.
\]

纯 pose imitation 往往不足。

---

## 32.7 Insertion / Assembly

peg-in-hole 类任务展示了 precision manipulation 的典型结构：

```text
coarse visual alignment
→ contact search
→ compliant alignment
→ insertion
→ force verification
```

误差来源：

- calibration；
- grasp offset；
- object tolerance；
- compliance；
- perception noise。

RL post-training 特别适合优化这种 narrow tolerance task。

---

## 32.8 Tool Use

工具把机器人 action space 扩展为：

\[
robot \rightarrow tool \rightarrow object.
\]

系统要推理：

- 工具 affordance；
- grasp location；
- functional endpoint；
- force transmission；
- task sequence。

“识别锤子”远不等于“会锤钉子”。

---

## 32.9 Articulated Object Manipulation

门、抽屉、柜子可以表示为 articulated system：

\[
q_{obj}\in\mathcal Q_{obj}.
\]

机器人需要估计：

- joint type；
- axis；
- handle；
- limits；
- friction。

未知 articulation 可以通过 small exploratory motion 在线识别。

---

## 32.10 Deformable Object

布料、绳子、软包装的状态维度远高于刚体。

若用 \(N\) 个点表示：

\[
x\in\mathbb R^{3N}.
\]

难点：

- state estimation；
- long-range coupling；
- self-contact；
- non-unique inverse action。

这也是为什么 deformable manipulation 是检验 world model 和 visuomotor representation 的强 benchmark。

---

## 32.11 Cloth

布料任务常见子问题：

- unfolding；
- corner detection；
- smoothing；
- folding；
- hanging。

视觉上同一件衣服存在大量等价形态。

因此 object-centric rigid pose 已经不够，需要 topology / keypoint / dense correspondence。

---

## 32.12 Rope / Cable

绳索操作引入拓扑状态：

- knot；
- crossing；
- loop；
- endpoint。

小的局部动作可能导致全局形态变化。

适合研究：

- long-horizon planning；
- bimanual coordination；
- topology-aware representation。

---

## 32.13 Food / Fluid / Granular Object

液体与颗粒不能被简单描述为单个 rigid pose。

这类任务需要预测：

- volume；
- flow；
- spill risk；
- container interaction。

它们是检验“world model 是否真的有物理内容”的高难度场景。

---

## 32.14 Mobile Manipulation

移动操作扩大可达空间：

\[
q=[q_{base},q_{arm}].
\]

规划必须同时考虑：

- base placement；
- visibility；
- arm reachability；
- collision；
- navigation cost。

把 navigation 与 manipulation 分成两个完全独立模块，容易出现 base 停在“看起来近但手够不到”的位置。

---

## 32.15 Long-Horizon Manipulation

多步任务的难点不是动作更长，而是状态误差不断积累。

因此必须有：

- subgoal；
- memory；
- verification；
- recovery；
- replanning。

长任务成功率不能只靠增加 action horizon。

---

## 32.16 Open-World Household Manipulation

家庭环境具有：

- object diversity；
- clutter；
- human interruption；
- deformables；
- unseen tools；
- scene change。

因此 household robotics 是对 generalist model 的高强度综合测试。

---

## 32.17 Industrial Manipulation

工业场景往往比家庭结构化，但要求更高：

- cycle time；
- repeatability；
- uptime；
- safety certification；
- tolerance。

一个 90% success 的 demo policy 可能完全不具备产线价值。

---

## 32.18 Real-World Manipulation Failure Taxonomy

建议统一记录：

1. detect/grounding failure；
2. pose error；
3. reachability failure；
4. grasp failure；
5. slip/contact failure；
6. collision；
7. planning failure；
8. controller failure；
9. latency；
10. task-state/recovery failure。

---

## 最小实验

在 pick-place、insertion、cloth 三类任务上比较同一 policy：

- vision only；
- vision + proprioception；
- vision + force；
- vision + tactile。

这样可以观察不同传感模态在 rigid、contact-rich、deformable 操作中的价值边界。

---

## 本章结论

Manipulation 是具身智能最集中的试验场：语义、几何、接触、动力学、控制、长期记忆都必须在真实时间里共同工作。越复杂的操作任务，越不可能被简化为“看图输出动作”。
<!-- CHAPTER-ENRICHMENT-R3-P32:START -->
## 32.22 研究问题

1. Manipulation generalization 的主要瓶颈是 visual semantics、3D geometry、contact dynamics 还是 recovery data？
2. Grasp/placement policy 应输出 pose、trajectory、contact mode 还是 object-centric effect？
3. 对 deformable/articulated objects，object-centric representation 需要怎样表示 hidden state 与 topology change？
4. Long-horizon manipulation 中，高层 skill composition 与低层 continuous policy 的最佳边界在哪里？
5. Failure/recovery demonstrations 的 marginal value 是否高于继续收集更多成功 demonstration？
6. 同一 manipulation task 中，force/tactile 信息应进入 foundation policy 还是独立高速 residual controller？
<!-- CHAPTER-ENRICHMENT-R3-P32:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 32`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-32)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
