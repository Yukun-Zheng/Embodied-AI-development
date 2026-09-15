# Part 45　可靠性、Safety 与 Human Intervention

## 45.1 Physical Safety

机器人错误会产生真实能量与接触。

风险近似取决于：

\[
Risk=P(hazard)\times Severity(hazard).
\]

因此低概率高伤害事件仍必须严肃处理。

---

## 45.2 Functional Safety

不仅要防“AI 做错事”，还要防：

- sensor failure；
- communication loss；
- encoder fault；
- software crash；
- actuator runaway。

安全系统必须覆盖整个 cyber-physical stack。

---

## 45.3 Collision / Joint / Force Limit

最基础约束：

\[
q_{min}\le q\le q_{max},
\]

\[
\|\dot q\|\le v_{max},
\]

\[
\|f\|\le f_{max}.
\]

这些应在低层独立 enforcement，不能只写进 prompt。

---

## 45.4 Safe Controller

safe controller 可把 policy command \(a_{raw}\) 投影到可行集合：

\[
a_{safe}=\arg\min_a\|a-a_{raw}\|^2
\quad s.t.\quad a\in\mathcal A_{safe}.
\]

这提供 model-agnostic safety layer。

---

## 45.5 Control Barrier Function

对安全函数 \(h(x)\ge0\)：

\[
\dot h(x,u)+\alpha(h(x))\ge0.
\]

CBF 可把安全约束变成在线优化条件。

适合 collision、distance、velocity 等连续约束。

---

## 45.6 Runtime Monitor

monitor 检查：

- action bound；
- state anomaly；
- prediction mismatch；
- collision distance；
- system heartbeat。

一旦违反规则：

```text
slow down
→ stop
→ retract
→ handoff human
```

---

## 45.7 Uncertainty-Aware Stop

若：

\[
U(o_t)>\tau,
\]

机器人可以不行动。

关键是 uncertainty 必须 calibrated，否则“自信地错”会绕过保护。

---

## 45.8 Human Override

人类 override 需要：

- low-latency stop；
- clear authority；
- state handoff；
- resume protocol。

如果接管后无法安全恢复 autonomy，shared autonomy 仍不完整。

---

## 45.9 Safe Exploration

RL exploration 必须限定安全 state/action set。

可使用：

- conservative policy；
- shield；
- simulation pretraining；
- human approval；
- staged difficulty。

现实机器人不能用“撞坏几百次之后学会”作为默认训练方式。

---

## 45.10 Unsafe Instruction Refusal

VLA 也需要拒绝：

- 明显伤人动作；
- 超出 payload；
- 不可达/危险目标；
- 与安全区域冲突指令。

语言安全必须落到 physical feasibility/safety checker，而不是纯文本分类。

---

## 45.11 Task Feasibility Estimation

执行前估计：

\[
P(success\land safe\mid task,state).
\]

若过低，应：

- ask clarification；
- call planner；
- request human；
- refuse。

“先执行再看”在物理世界代价很高。

---

## 45.12 Human-Proximity Safety

与人共处时动态安全 envelope：

\[
d_{safe}=f(v_{robot},v_{human},reaction\ time,uncertainty).
\]

机器人速度越高、感知越不确定，安全距离应更大。

---

## 45.13 Agentic Safety Orchestration

高层 agent 可以选择：

```text
normal VLA
safe slow skill
classical planner
human help
stop
```

但 orchestrator 本身也可能失误，因此最底层 safety invariant 不能依赖它。

---

## 45.14 Multi-Robot Safety

多个机器人之间增加：

- shared workspace；
- deadlock；
- communication failure；
- conflicting goals。

需要 collision reservation / coordination protocol。

---

## 45.15 Cybersecurity for Robots

机器人是联网执行器。

攻击面包括：

- command channel；
- camera stream；
- model server；
- update package；
- credentials。

安全不只防物理 accident，还要防 malicious control。

---

## 45.16 Foundation Model Safety for Physical Systems

foundation model 带来新的风险：

- prompt injection from scene/text；
- hallucinated object/action；
- OOD overconfidence；
- unsafe generalization。

因此需要把 AI safety 与 control safety 结合。

---

## 45.17 从 70% Success 到可部署系统

如果独立 task success 为 70%，每小时做 20 次任务，预期每小时失败约 6 次。

商业部署通常需要 failure rate 低几个数量级，或者拥有低成本恢复机制。

所以系统价值更接近：

\[
Utility=Throughput-C_{intervention}-C_{failure}-C_{downtime}.
\]

而不是单一 success rate。

---

## 45.18 Safety 与 Capability 为什么不能分开

更强 capability 可以降低风险：

- 更好 perception；
- 更好 recovery；
- 更准 uncertainty。

但也扩大可行动范围和潜在能量。

因此：

\[
Safety=f(Capability,Constraints,Monitoring,Human\ Oversight).
\]

不是后加一个 emergency stop 就结束。

---

## Safety Case

部署前应形成结构化 safety case：

1. hazards；
2. mitigations；
3. evidence；
4. residual risk；
5. monitoring；
6. incident response。

这比“我们测试过很多次没出事”更严谨。

---

## 最小实验

对 policy 注入：

- perception dropout；
- 500 ms latency；
- wrong language instruction；
- unexpected human entry；
- actuator saturation。

比较无 safety layer 与 layered safety system 的事故率、false stop、task completion。

---

## 本章结论

物理 AI 的 Safety 不是语言模型安全的简单延伸。它必须同时处理 **动力学约束、实时控制、模型不确定性、人类接管、系统故障和网络攻击**。可靠部署的目标不是“从不出错”，而是让错误可检测、可约束、可恢复、不会演化成灾难。
<!-- CHAPTER-ENRICHMENT-R3-P45:START -->
## 45.23 Safety / Reliability Failure Taxonomy

### High average success, catastrophic tail

99% success 仍可能每 100 次出现一次不可接受碰撞。Safety 需要 tail-risk / severity，而不是只看平均失败率。

### Detector blind spot

系统只会恢复“自己能检测”的 failure。未检测错误不会进入 recovery-rate denominator。

### False-positive safety stop

shield 过度保守导致机器人频繁停止、人工接管，安全但不可用。必须同时报 false stop / intervention burden。

### Distribution-shifted safety model

OOD 时 policy 与 safety detector 同时失准；不能假设外部 shield 永远比 policy 更可靠。

### Recovery creates secondary hazard

一次 grasp failure 后自动 recovery 可能撞到人、其他机器人或已移动物体。Recovery 本身也需要 safety verification。

## 45.24 研究问题

1. General-purpose robot 的 risk metric 应如何同时编码概率与伤害 severity？
2. Learned safety critic 与 model-independent CBF/WBC constraint 应怎样分工？
3. Human intervention 何时算失败、何时算系统合理的 uncertainty management？
4. 如何评价“安全但不可用”和“高效但风险高”之间的 Pareto frontier？
5. Continual-learning robot 更新 policy 后，哪些 safety property 必须重新验证，哪些可以 compositional reuse？
<!-- CHAPTER-ENRICHMENT-R3-P45:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 45`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-45)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
