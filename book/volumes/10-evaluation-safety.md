# Volume X　评测、可靠性与安全

> 具身智能最危险的幻觉之一，是把“成功视频”当作能力证明。机器人研究必须同时回答三件事：**它能不能做？在什么分布上能做？失败时会发生什么？** 本卷建立从 benchmark science 到 physical/agentic safety 的完整评价体系。

---

# Part 44　Datasets、Benchmarks 与 Evaluation Science

## 44.1 Benchmark 会塑造研究方向

Benchmark 不只是测量工具，它定义研究者优化什么。若 benchmark 只奖励最终 task success，社区会忽略：

- 速度；
- 能耗；
- intervention；
- recovery；
- uncertainty；
- unsafe near-miss；
- long-term degradation。

因此任何 benchmark 都隐含一个 utility function。

## 44.2 Training Dataset ≠ Evaluation Benchmark

评测分布必须与训练数据独立到足以回答研究问题。若同一场景、对象、语言模板、演示轨迹同时出现在 pretraining 与 test，就会产生 leakage。

应记录：

\[
\text{overlap}=f(\text{scene},\text{object},\text{task},\text{trajectory},\text{language},\text{source}).
\]

## 44.3 Success Rate

最基础指标：

\[
\hat p=\frac{k}{n}.
\]

但 8/10 与 80/100 都是 80%，统计置信完全不同。机器人实验必须报告 trial 数与 confidence interval。

Wilson interval 比简单 normal approximation 在小样本下更可靠。

## 44.4 Partial Credit / Progress

长任务二元 success 太稀疏。可分阶段：

\[
S=\sum_{i=1}^K w_i\mathbf 1[\text{subgoal}_i].
\]

但 progress metric 不能奖励无意义中间行为。最好每个 subgoal 都对应可验证世界状态。

## 44.5 Time-to-Completion

两个策略 success 都 90%，一个 20 秒、一个 3 分钟，部署价值不同。

可报告：median/P90 completion time，或 success-weighted throughput：

\[
\mathrm{Throughput}=\frac{\#\text{successful tasks}}{\text{wall-clock time}}.
\]

## 44.6 Intervention Rate

自主系统若频繁需要人救援，不应只报告最终 success：

\[
IR=\frac{N_{intervention}}{N_{episodes}}
\]

或每小时 intervention 数。

对 data flywheel，intervention 既是 failure signal，也是后续训练数据。

## 44.7 Recovery Rate

定义：发生可检测失败后，系统无需人工成功恢复的比例：

\[
RR=P(\text{eventual success}\mid\text{failure detected}).
\]

这是长时机器人比单 skill policy 更重要的指标。

## 44.8 Robustness

对扰动 \(\delta\)：

\[
R(\delta)=P(\text{success}\mid x+\delta).
\]

应扫描扰动强度形成 curve，而非只挑一个“看起来很难”的 demo。

扰动类型：camera shift、lighting、object displacement、latency、force disturbance、human interruption、sensor dropout。

## 44.9 Generalization Matrix

把训练/测试变化维度显式列成矩阵：

| 维度 | ID | Mild OOD | Strong OOD |
|---|---|---|---|
| object | seen instance | new instance | new category |
| scene | seen layout | new layout | new building/home |
| task | seen | paraphrase/composition | new skill composition |
| embodiment | seen robot | variant | unseen morphology |
| dynamics | nominal | randomized | materially new |

“Generalization”必须指出具体格子。

## 44.10 Compositional Generalization

训练见过 A、B，但从未见 A∘B；测试组合：

\[
\mathcal T_{test}=m_A\circ m_B,
\qquad
\mathcal T_{test}\notin D_{train}.
\]

这是检验 mechanism reuse 比换背景颜色强得多的设计。

## 44.11 Long-Horizon Evaluation

除整体 success，记录：

- subtask transition accuracy；
- memory error；
- replan count；
- recovery count；
- idle/loop behavior；
- cumulative latency；
- context/memory growth。

长任务失败要定位到时间轴，而不是只给一个 0。

## 44.12 Counterfactual Evaluation

保持场景几乎相同，只改 causal variable。例如物体位置变而 texture 不变，或 friction 改而视觉相同。若 policy 行为不随关键变量变化，说明 representation 可能依赖 shortcut。

## 44.13 Perturbation Test

机械扰动尤其重要：在执行中轻推物体、移动目标、让人经过、夹爪轻微滑移。闭环系统应观察新 state 并纠正，而不是继续执行过时 trajectory。

## 44.14 Efficiency

至少报告：

\[
\text{params},\quad\text{FLOPs},\quad\text{latency},\quad\text{GPU memory},\quad\text{energy},\quad\text{control Hz}.
\]

对 on-device robot，P95/P99 latency 比平均 token/s 更有意义。

## 44.15 Energy / Mechanical Cost

真实机器人还需：motor energy、peak torque、joint travel、impact、thermal load。可定义

\[
J_E=\int |\tau^T\dot q|dt.
\]

高 success 但极端撞击/磨损的策略不可部署。

## 44.16 Calibration / Selective Prediction

如果模型能估计 confidence \(c\)，应测 risk-coverage：只执行 confidence 最高的前 \(x\%\) 任务时失败率如何变化？

理想系统在低置信时选择 ask-human / observe-more，而不是硬做。

## 44.17 Dataset / Benchmark Families

不同 benchmark 代表不同问题：

- MetaWorld：多任务连续控制；
- LIBERO：lifelong / multitask manipulation；
- RLBench：视觉操控与多任务；
- ManiSkill：GPU manipulation；
- RoboTwin：双臂与通用 policy；
- Habitat：navigation；
- BEHAVIOR / OmniGibson：household activity；
- real-robot suites：真实分布、系统噪声与可靠性。

不能拿一个平台覆盖的能力外推到整个 embodied intelligence。

## 44.18 Sim Benchmark vs Real Benchmark

Simulation 适合 controlled ablation；real robot 才暴露 calibration、latency、wear、sensor artifact 和 unexpected contact。

严谨论文常需要：

\[
\text{sim mechanism study}\quad +\quad\text{real-world validation}.
\]

二者职责不同。

## 44.19 Benchmark Leakage

foundation model 可能在 web/video/pretraining robot corpus 中见过 benchmark scene 或 task。即使作者没有显式训练 benchmark，也不代表 zero exposure。

未来 benchmark 应维护 asset/task provenance、holdout physical environments 和 contamination audit。

## 44.20 Statistical Significance

两个 success rate 差 2% 可能只是随机性。建议：

- multiple seeds；
- enough episodes；
- paired evaluation when possible；
- bootstrap CI；
- effect size；
- pre-defined metric；
- failure breakdown。

不要只挑最好 seed。

## 44.21 “成功视频”为什么不是科学证据

公开视频通常被选择性展示。科学证据要求知道：

\[
\text{成功次数}/\text{总尝试次数}.
\]

还需要失败案例、环境分布、是否人工重置、是否多次挑选、是否用了不可见 operator intervention。

## 44.22 Evaluation Protocol 应版本化

任务、资产、reset、camera、controller、success detector 都要版本化。否则 benchmark score 改变可能来自 evaluation script 变化。

建议每次结果绑定：

```text
benchmark commit
asset hashes
policy commit/checkpoint
controller config
seed set
hardware
raw episode logs
```

---

# Part 45　可靠性、Safety 与 Human Intervention

## 45.1 Safety 不只是“别撞人”

Foundation-model-enabled robot safety 至少可分：

1. **action safety**：动作是否物理可行/满足约束；
2. **decision safety**：任务决定是否合适；
3. **human-centered safety**：是否符合人的意图、空间和社会规范；
4. **system safety**：硬件/网络/软件故障时能否安全退化；
5. **learning safety**：模型更新后旧安全能力是否退化。

## 45.2 Physical Safety

典型硬约束：

\[
q_{min}\le q\le q_{max},
\quad
|\dot q|\le v_{max},
\quad
|\tau|\le \tau_{max},
\quad
d_{collision}\ge d_{safe}.
\]

这些约束应在模型外层独立执行，而不是只靠训练数据让 VLA“学会注意”。

## 45.3 Functional Safety

Functional safety 关注系统故障时是否进入可控安全状态。例如 encoder failure、通信中断、GPU crash、控制线程 deadline miss。

核心思想：

\[
\text{single fault}\not\Rightarrow\text{uncontrolled hazardous motion}.
\]

## 45.4 Safe Controller

Safety layer 可以做 action projection：

\[
a^*=\arg\min_a\|a-a_{policy}\|^2
\]

subject to joint/collision/CBF constraints。

这样尽量保留 policy 意图，同时阻止危险动作。

## 45.5 Control Barrier Function

安全集合 \(\mathcal C=\{x:h(x)\ge0\}\)。通过约束

\[
\dot h(x,u)+\alpha(h(x))\ge0
\]

保证系统不离开 safe set。CBF 尤其适合与 learned controller 组合成 runtime shield。

## 45.6 Workspace / Collision Guard

可用 signed distance field / capsule model 快速检测 self/environment collision。高层 VLA 可以提出目标，但 runtime guard 对每个 command 做几何验证。

## 45.7 Force / Contact Safety

人机协作或 fragile object 任务必须限制 contact wrench：

\[
\|F\|\le F_{safe},\qquad \|\tau\|\le\tau_{safe}.
\]

还要监测 force derivative / impact，而非只看稳态值。

## 45.8 Human Proximity

当人进入 safety zone，机器人可 slow down / stop / replan。2026 Gemini Robotics ER 2 的公开安全评测已把 human proximity、protective stop 和 safety tool call 作为 embodied reasoning safety 的显式指标。

## 45.9 Semantic Safety

危险不一定违反关节限制。例如：

- 用户让机器人把刀递给儿童；
- 让机器人把热锅放到易燃表面；
- 指令含糊，两个瓶子一个是清洁剂一个是饮料。

这类 safety 需要 semantic/world reasoning，单纯 CBF 无法解决。

## 45.10 Agentic Safety

2026 Google DeepMind 的 **ASIMOV-Agentic** 将机器人 agent 安全显式拆成：拒绝违反 operational constraints 的任务、在硬件故障/人靠近时触发 intervention、阻止 VLA 执行 infeasible/OOD task，以及在歧义/不确定时主动请求人类帮助。

这代表 safety evaluation 从“单动作不碰撞”扩展到整个 agent orchestration。

## 45.11 Uncertainty → Intervention

安全系统应将低 confidence 映射为行动：

\[
U>\tau_1\Rightarrow\text{observe more},
\]

\[
U>\tau_2\Rightarrow\text{ask human},
\]

\[
U>\tau_3\Rightarrow\text{safe stop}.
\]

仅输出 uncertainty 数字而不改变行为，没有部署价值。

## 45.12 Human Override

任何高自主机器人都应有明确 override path：物理 E-stop、软件 stop、teleop takeover、permission boundary。override 延迟本身需要 benchmark。

## 45.13 Fault Detection

监测：

- stale sensor；
- actuator tracking error；
- unexpected current/force；
- camera blackout；
- model timeout；
- network loss；
- localization jump。

fault detector 应独立于主 policy，避免同一模型同时制造错误又判断“没问题”。

## 45.14 FMEA

Failure Mode and Effects Analysis：对每个 failure mode 评估 severity、occurrence、detectability，并设计 mitigation。

例如：

| Failure | Effect | Detect | Mitigate |
|---|---|---|---|
| stale camera | old action | timestamp | hold/reobserve |
| gripper slip | object drop | tactile/F/T | regrasp |
| VLA timeout | no new chunk | watchdog | safe hold |
| human enters path | collision risk | proximity | protective stop |

## 45.15 Fault Tree

从 hazard 反推多个原因组合。例如“机器人撞人”可能来自：human detection failure AND speed not limited AND safety monitor failure。Fault tree 强迫我们分析多层 defense，而不是把所有责任推给 policy。

## 45.16 Safety Case

部署安全不是一个 score，而是证据集合：

```text
hazards identified
→ safety requirements
→ architecture mitigations
→ verification tests
→ residual risks
→ operational limits
→ monitoring / incident response
```

foundation model model card 只能是其中一部分。

## 45.17 Continual / Upgrade Safety

持续学习系统还必须回答：更新后是否破坏安全？

每次 upgrade 应测：

\[
E_{new}+E_{regression}+E_{safety}+E_{override}.
\]

2026 已出现专门讨论 embodied upgrade/governance safety 的 benchmark 方向，说明“会自我更新”必须伴随 rollback、audit 和 human control。

## 45.18 Reliability Engineering

从 70% success 到部署不是再加一点数据。若每天执行 1000 次，1% failure 意味着每天约 10 次事故/干预。

工程目标可能要求：

\[
P(failure)\ll10^{-3}
\]

并且 failure 必须可检测、可恢复、可归因。

可靠性提升常来自：

- 分层架构；
- explicit checks；
- redundancy；
- recovery；
- confidence gating；
- data flywheel；
- hardware maintenance；
- constrained operating domain。

## 45.19 Capability 与 Safety 不能分开

能力更强会减少某些危险（更懂场景、更会恢复），也可能引入新风险（更大自主权限、更开放任务、更难预测）。因此 safety 不是训练结束后加一个 filter，而应与 capability co-design。

---

# 一套完整 Robotics Eval Card

每个新模型建议统一报告：

```text
1. Scope
   - robots / tasks / scenes / control interface
2. Training exposure
   - datasets / pretraining / possible contamination
3. Capability
   - success / progress / long-horizon
4. Generalization
   - object / scene / task / embodiment / dynamics
5. Robustness
   - visual / physical / latency / sensor perturbations
6. Efficiency
   - latency / control Hz / compute / energy
7. Reliability
   - intervention / recovery / repeated-trial statistics
8. Uncertainty
   - calibration / selective execution
9. Safety
   - physical / semantic / agentic / human proximity
10. Failures
   - taxonomy + representative raw failures
11. Reproducibility
   - code / checkpoint / benchmark commit / configs
```

这比一张 success-rate 表更接近真实科学结论。

## 必做实验

1. 对 10/50/100 trials 计算 success CI；
2. 同模型构造 generalization matrix；
3. camera/object/latency perturbation curves；
4. long-horizon 分阶段 failure timeline；
5. confidence threshold → risk-coverage；
6. stale command / network loss watchdog test；
7. CBF / action projection shield；
8. human proximity protective stop；
9. unsafe/ambiguous instruction → refuse/clarify/human intervention；
10. 模型升级前后 regression + safety suite。

## 2026 前沿与参考

- Google DeepMind, Gemini Robotics 2 / ASIMOV-Agentic — https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/
- Google DeepMind Evals: ASIMOV-Agentic-v1 — https://deepmind.google/research/evals/
- Gemini Robotics ER 2 Model Card — https://deepmind.google/models/model-cards/gemini-robotics-er-2/
- EmbodiedGovBench (2026), arXiv:2604.11174.
- “Modular Safety Guardrails Are Necessary for Foundation-Model-Enabled Robots in the Real World” (2026), arXiv:2602.04056.
- Standard robotics functional-safety / collaborative-robot standards should be consulted for the relevant deployment domain; this textbook does not treat a research benchmark score as regulatory certification.
