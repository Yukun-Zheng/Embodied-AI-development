# Part 29　从 Demonstration 到 Experience：机器人如何继续学习

## 29.1 固定模型范式的问题

传统流程：

```text
collect data
→ train
→ freeze checkpoint
→ deploy
```

真实机器人一旦部署，就会遇到训练数据没有覆盖的长尾状态。

更合理的长期系统：

```text
pretrain
→ deploy
→ collect outcomes
→ identify failure
→ update policy / memory / model
→ redeploy
↺
```

这意味着“训练”和“推理”的边界开始模糊。

---

## 29.2 为什么 Imitation 不能解决所有 Precision 问题

behavior cloning 优化：

\[
\min_\theta \mathbb E_{(o,a^*)\sim D}[-\log\pi_\theta(a^*\mid o)].
\]

它学习“专家做什么”，但没有直接优化：

- task success；
- cycle time；
- energy；
- precision；
- recovery。

某些高精度行为甚至 expert demonstration 的动作噪声都比任务容差大。

RL 可以利用 outcome 对策略做针对性改进。

---

## 29.3 Reinforcement Learning Post-Training

foundation policy \(\pi_0\) 作为 prior：

\[
\pi^*=\arg\max_\pi J(\pi)-\beta D(\pi\|\pi_0).
\]

约束策略不要远离预训练能力，同时根据真实 task reward 改善局部行为。

这比从零 RL 容易，因为基础模型已经拥有：

- perception；
- language grounding；
- broad manipulation prior。

RL 主要精修困难区域。

---

## 29.4 RL Token / Lightweight Online Adaptation

2026 年 Physical Intelligence 公布了针对 precise manipulation 的 efficient online RL 方法，核心动机是：

> 不必每次在线 RL 都更新整个巨大 VLA。

可以引入小的可学习条件 \(z_{RL}\)：

\[
a\sim\pi(a\mid o,l,z_{RL}),
\]

在线阶段主要更新或搜索低维 adaptation variable。

这一思路把 foundation model 当作固定的“大能力底座”，把在线 RL 压缩到较低维空间。

---

## 29.5 Experience Replay

机器人 experience buffer：

\[
\mathcal B=\{(o_t,a_t,r_t,o_{t+1},meta_t)\}.
\]

不能简单 uniform replay，因为真实部署中 99% 可能是重复正常状态。

更有价值的 replay：

- rare failure；
- near miss；
- human correction；
- novel object；
- high uncertainty；
- high TD error。

---

## 29.6 Autonomous Data Collection

机器人从“被人示范”转向“自己练习”。

需要：

1. goal proposal；
2. safe execution；
3. outcome evaluation；
4. automatic reset 或 task continuation；
5. data logging。

真正瓶颈常常不是 policy，而是 reset。

一个机器人完成一次失败后，如果必须人工把环境恢复，autonomous learning 吞吐量会急剧下降。

---

## 29.7 Self-Generated Curriculum

设任务难度 \(d\)。

理想 curriculum 不是一直选最难任务，而是最大化学习进展：

\[
g^*=\arg\max_g \Delta Learnability(g).
\]

如果任务太容易，没有新信息；太难则全失败，没有有效 gradient。

“刚好在能力边界附近”通常信息量最高。

---

## 29.8 Failure Mining

部署日志应该自动聚类 failure：

```text
perception failure
slip
missed grasp
collision
wrong object
timeout
stale action
planner deadlock
recovery loop
```

然后优先采集/学习最影响系统吞吐的 cluster。

这比“再采 1000 小时随机数据”更高效。

---

## 29.9 Human Feedback

人类可以提供：

- correction trajectory；
- binary success；
- preference；
- natural-language critique；
- intervention timing。

不同反馈信息量不同。

例如 intervention time 本身就包含：

> “从这一刻开始，机器人行为开始危险/错误。”

可作为 temporal supervision。

---

## 29.10 Preference / Ranking Signal

当 reward 很难直接写，比较两个 rollout：

\[
\tau_A \succ \tau_B.
\]

可学习 reward model：

\[
P(A\succ B)=\sigma(R_\phi(\tau_A)-R_\phi(\tau_B)).
\]

但机器人 preference 比语言偏好更危险，因为 reward model 错误可能直接驱动实体行动。

---

## 29.11 Self-Evaluation

机器人可以预测自己的成功概率：

\[
\hat p_t=P(success\mid history_t).
\]

若 calibration 良好，可用于：

- abort；
- ask human；
- switch skill；
- retry；
- collect hard case。

关键指标不是 accuracy，而是 calibration：

\[
P(success\mid \hat p=0.8)\approx0.8.
\]

---

## 29.12 Self-Correction

self-correction 需要三步：

```text
detect mismatch
→ diagnose cause
→ choose corrective action
```

如果只重新采样同一个 policy，很可能重复失败。

真正 correction 应改变：

- viewpoint；
- grasp；
- subgoal；
- force；
- speed；
- planner path。

---

## 29.13 Test-Time Adaptation

TTA 在不完整 retraining 的情况下利用新环境数据更新模型。

风险是 test-time drift：

\[
\theta_{t+1}=\theta_t-\eta\nabla \mathcal L_{self}(x_t)
\]

如果自监督信号错，机器人会越适应越差。

所以真实机器人 TTA 需要：

- bounded update；
- rollback；
- safety guard；
- held-out monitor。

---

## 29.14 Online System Identification

某些失败不是 policy 不够聪明，而是 dynamics 变了：

- payload；
- friction；
- actuator delay；
- battery state；
- gripper wear。

在线估计：

\[
\hat\phi_t=\arg\min_\phi\sum_k\|s_{k+1}-f_\phi(s_k,a_k)\|^2.
\]

然后 controller / world model 根据 \(\hat\phi_t\) 适配。

---

## 29.15 Policy Improvement in Deployment

一个部署 flywheel：

```text
real deployment
↓
telemetry + outcome
↓
failure mining
↓
relabel / human correction / autonomous practice
↓
offline update
↓
canary evaluation
↓
gradual redeployment
```

“在线学习”不一定意味着每秒直接修改线上权重。工程上更安全的是 staged update。

---

## 29.16 Safety-Constrained Online Learning

在线探索时，必须限制可访问动作集合：

\[
a_t\in\mathcal A_{safe}(s_t).
\]

可由：

- CBF；
- joint/force limit；
- collision checker；
- safe action projection；
- human stop；
- uncertainty threshold。

组成 shield。

一个 learning agent 如果可以为了 reward 随意撞人或损坏硬件，就不是可部署学习系统。

---

## 29.17 从“训练好的模型”到“会积累经验的机器人”

真正持续改善的机器人需要至少五种记忆/更新介质：

1. episodic log；
2. replay dataset；
3. policy parameter；
4. world model / system ID；
5. semantic / user memory。

这比“每晚 fine-tune checkpoint”复杂得多。

---

## 最小实验：Demonstration vs Experience

选一个高精度 insertion 任务：

1. BC only；
2. BC + more demos；
3. BC + failure data；
4. BC + offline RL；
5. BC + online RL；
6. BC + lightweight RL adaptation。

固定总 robot-hours，比较：

- success；
- throughput；
- intervention；
- number of catastrophic failures；
- adaptation sample efficiency。

这能直接回答：经验学习是否比“继续收 demonstration”更值。

---

## Source anchors

- Physical Intelligence, π*0.6: https://www.pi.website/blog/pistar06
- Physical Intelligence, Precise Manipulation with Efficient Online RL, 2026-03-19: https://www.pi.website/research/rlt

---

## 本章结论

机器人 foundation model 若永远冻结，它只能依赖训练分布；真正可部署的长期智能必须形成 **experience → evaluation → memory → policy/world-model update → safer redeployment** 的闭环。未来的重要分界线，不是“有没有 VLA”，而是“模型能不能在真实世界中安全地继续学”。
<!-- CHAPTER-ENRICHMENT-R3-P29:START -->
## 29.18 研究问题

1. Autonomous experience 中最有价值的数据来自成功、near-failure、intervention 还是 recovery？
2. Online RL 的 reward 如何避免把吞吐提升换成更激进、更不安全的行为？
3. Foundation policy 的局部 task adaptation 如何保持 broad generality 与 calibration？
4. Experience replay 应按 recency、novelty、TD error、failure severity 还是 mechanism novelty 采样？
5. 真机学习何时应该更新 policy 参数，何时只更新 memory/world model/system ID？
6. 如何让机器人长期学习同时具备 rollback：新策略出问题时能恢复到已验证的行为版本？
<!-- CHAPTER-ENRICHMENT-R3-P29:END -->
