# Case Study — Predictive World Model + Control
## 预测只有进入 Action Selection 才真正闭环

> 本案例不绑定某一个模型品牌。它定义 world model 对机器人控制的最低科学标准，并与 [`VJEPA2_1_SOURCE_WALKTHROUGH.md`](./VJEPA2_1_SOURCE_WALKTHROUGH.md) 形成互补：后者回答“源码怎样做 latent prediction”，这里回答“prediction 怎样才真正改变 action”。

---

# 1. 最低限度的 Robot World Model

当前 observation：

\[
o_t
\]

编码为 latent / state：

\[
z_t=E(o_t).
\]

给定 action：

\[
a_t,
\]

预测下一状态：

\[
\hat z_{t+1}=F_\theta(z_t,a_t).
\]

这才是最小 action-conditioned predictive model。

如果只有：

\[
\hat z_{t+1}=F(z_t),
\]

它可以学习自然视频演化，却还不能回答控制最关键的反事实：

> **如果我采取另一个动作，未来会怎样不同？**

---

# 2. 训练数据必须识别 Action Effect

机器人 trajectory：

```text
o_0, a_0, o_1, a_1, ..., o_T
```

窗口化后：

```text
context observations  [B, Tc, ...]
action sequence       [B, H, Da]
future observations   [B, H, ...]
```

如果只有无动作视频：

```text
video → future video
```

可以学 predictive representation，但不能单靠该数据识别：

\[
p(s'\mid s,do(a)).
\]

要成为控制 world model，必须把 action intervention 接进去，或通过其他监督恢复可操作因果结构。

---

# 3. Representation 与 Dynamics 应分开理解

Encoder：

\[
z_t=E_\phi(o_t).
\]

Dynamics：

\[
\hat z_{t+1}=F_\theta(z_t,a_t).
\]

可选 decoder：

\[
\hat o_{t+1}=D(\hat z_{t+1}).
\]

控制并不天然需要 pixel decoder。

如果 latent 已足以估计：

- object pose；
- contact mode；
- collision；
- goal progress；
- uncertainty；

那么重建背景纹理可能是额外负担。

更合理的目标可能是：

\[
\text{Task-Sufficient Predictive State}.
\]

---

# 4. JEPA / Latent Prediction 的位置

JEPA 类路线更强调：

\[
\hat z_{future}=P(z_{context},a)
\]

而不是必须：

\[
\hat I_{future}=Decoder(\hat z).
\]

潜在优势：

- 不浪费容量复原难预测但任务无关的纹理；
- representation 可以更集中在结构和动态。

但：

> latent 更漂亮 / probe 更强 ≠ 已经理解物理。

仍必须做 action intervention 与 downstream control test。

---

# 5. Action-Conditioned Prediction 的 Tensor Contract

假设：

```text
context latent: [B, N, D]
action chunk:   [B, H, Da]
```

world model 可输出：

```text
future latent:  [B, H, N', D]
```

Object-centric 版本可写为：

```text
objects_t:       [B, M, D_obj]
actions:         [B, H, Da]
future objects:  [B, H, M, D_obj]
```

真正关键的是时间结构是否保持：

- 同一个 object identity；
- 同一关节/部件；
- contact event；
- action-effect mapping。

---

# 6. Training Objective 不止一种

## Latent prediction

\[
\mathcal L_{pred}
=
\|\hat z_{t+1}-sg(z_{t+1})\|^2.
\]

## Contrastive / energy objective

让正确 future 更近，错误 future 更远。

## Pixel / video generation

\[
\mathcal L_{video}.
\]

## State supervision

\[
\mathcal L_{state}
=
\|g(\hat z)-s_{future}\|^2.
\]

## Contact/event supervision

\[
\mathcal L_{contact}
=CE(\hat c,c).
\]

不同 objective 对**控制价值**的影响必须分开验证。

---

# 7. One-Step Accurate 远远不够

单步误差：

\[
\|\hat z_{t+1}-z_{t+1}\|\ll1
\]

并不保证长 rollout 正确。

若：

\[
e_{k+1}\le Le_k+\epsilon,
\]

则：

\[
e_H
\le
\epsilon\sum_{i=0}^{H-1}L^i.
\]

当 \(L>1\) 时，误差会快速放大。

因此 world-model evaluation 至少要画：

```text
prediction error vs rollout horizon
```

并同时区分：

- teacher-forced；
- autoregressive rollout。

---

# 8. World Model 怎样真正改变 Action

最经典闭环：MPC。

候选动作序列：

\[
A=[a_t,\ldots,a_{t+H-1}].
\]

Imagined rollout：

\[
\hat z_{t+1:t+H}=Rollout(F,z_t,A).
\]

Cost：

\[
J(A)=\sum_{k=1}^{H}c(\hat z_{t+k},a_{t+k-1}).
\]

选择：

\[
A^*=\arg\min_A J(A).
\]

只执行：

\[
a_t=A_0^*.
\]

然后重新观察真实世界并重规划。

```text
observe
→ imagine candidate futures
→ score
→ act one step
→ observe reality
→ reset belief
→ imagine again
```

教材最小实现：

`code/minimal/world_model_mpc.py`

---

# 9. Search / Optimization 方法

## Random Shooting

直接随机采很多 action sequence。

## CEM

```text
sample sequences
→ score imagined futures
→ keep elites
→ refit Gaussian
→ repeat
```

## Gradient-Based Planning

若 world model 与 cost 可微：

\[
\nabla_A J(A)
\]

可以直接优化 action sequence。

## Policy-Guided Search

```text
policy proposes candidates
→ world model predicts consequences
→ evaluator reranks
```

在高维 action space 中往往更现实。

---

# 10. Receding Horizon 为什么核心

若 learned model 一次规划很长并全部执行：

```text
small model bias
→ rollout drift
→ late-horizon action increasingly wrong
```

MPC 每步让真实 observation 把 agent 拉回世界：

```text
predict
→ act one step
→ observe
→ correct belief
→ predict again
```

这与具身智能最重要的闭环原则完全一致。

---

# 11. Counterfactual Test：最重要的 World Model 实验

固定当前 state，施加不同 action：

\[
a^{(1)},a^{(2)},a^{(3)}.
\]

模型预测：

\[
\hat s'^{(i)}=F(s,a^{(i)}).
\]

真实环境分别干预：

\[
s'^{(i)}_{real}.
\]

比较模型能否保持正确的**action ordering / effect geometry**。

如果不同 action 都预测出近似同一个平均未来，这个模型对控制帮助有限。

---

# 12. Contact 是最强压力测试之一

视觉预测可以很好捕捉：

- camera motion；
- gross object motion；

却仍可能错误预测：

- contact onset；
- slip；
- jam；
- force transmission；
- deformation。

而这些像素占比很小、任务影响却极大。

所以必须增加 task-relevant metric，不能只报 PSNR/FVD/latent loss。

---

# 13. World Model + Evaluator

Prediction 本身不知道什么是“好”。

还需要：

\[
r=R(z,g)
\]

或：

\[
V(z,g).
\]

完整系统：

```text
world model: what will happen?
+
evaluator: is that future desirable?
+
planner/search: which action should I choose?
```

如果 evaluator 也是 VLM/foundation model，必须另外检查 calibration 与 feasibility。

---

# 14. 视觉真实 ≠ 控制真实

一个 video future 可以：

- visually plausible；
- temporally smooth；

同时：

- object pose 差 5 cm；
- contact 早/晚 200 ms；
- friction effect 错；
- hand-object topology 错。

这些已经足够使机器人失败。

因此：

\[
\boxed{Visual\ Realism\neq Control\ Fidelity}
\]

---

# 15. World Model 四层证据

## Level 1 — Representation

- probe；
- correspondence；
- object consistency。

## Level 2 — Prediction

- one-step state error；
- rollout error；
- contact/event accuracy。

## Level 3 — Counterfactual

- action intervention ranking；
- alternative-future discrimination。

## Level 4 — Control

- MPC success；
- policy improvement；
- real task success。

只有 Level 4 直接证明 prediction 对 action 有用。

---

# 16. Negative Control A — Random World Model

把 learned model 换成 frozen random network。

如果 planner success 几乎不变：

- planner 没真正使用 prediction；或
- task 不需要 model。

---

# 17. Negative Control B — Shuffled Action/Future

保持 latent marginal distribution，但打乱 action–future pairing。

检验收益是否来自：

> 正确的 action-conditioned mapping，还是只要“有某种未来 feature”即可？

---

# 18. Negative Control C — Wrong Physics

人为改变预测中的：

- friction；
- mass；
- contact rule；
- latency。

如果 downstream action selection 对这些错误不敏感，说明 planner 可能没依赖物理细节。

---

# 19. Negative Control D — Current-State-Only Policy

Baseline：

\[
a_t=\pi(z_t,g)
\]

vs：

\[
a_t=Plan(F,z_t,g).
\]

必须尽量固定：

- perception backbone；
- data；
- controller；
- compute budget。

否则无法归因 world model。

---

# 20. Joint Training 不自动证明 Prediction 被使用

可以训练：

\[
\mathcal L
=
\mathcal L_{policy}
+
\lambda\mathcal L_{prediction}.
\]

但需要问：

- prediction 是真正参与决策？
- 还是只充当 regularizer？
- policy 是否读取 predicted future？

可以做：

- detach；
- gradient blocking；
- replace future with wrong future；
- remove predictive branch。

---

# 21. Predictive Representation ≠ Full Simulator

World model 不一定需要复制宇宙所有细节。

对一个 manipulation task，可能足够预测：

```text
object pose
relation
contact mode
collision risk
goal progress
```

因此问题不是“生成得有多像”，而是：

\[
\text{Does the predictive state retain all decision-relevant variables?}
\]

---

# 22. V-JEPA 2.1 怎样接进这套框架

源码案例见：

[`VJEPA2_1_SOURCE_WALKTHROUGH.md`](./VJEPA2_1_SOURCE_WALKTHROUGH.md)

普通 V-JEPA 2.1 预训练：

```text
masked video
→ context encoder
→ predictor
→ target latent representation
```

DROID action-conditioned route：

```text
visual latent
+ action
+ state
+ optional extrinsics
→ causal future-latent predictor
```

这已经满足本案例的 dynamics-model形式。

但仍需再接：

```text
predictive model
→ evaluator / planner / policy search
→ real action
```

才能证明 control usefulness。

---

# 23. World Action Model 的判断标准不变

即使模型把：

- world generation；
- reasoning；
- action prediction

统一在一个大网络里，仍可回到两个简单问题：

1. **改变 action 是否产生正确 counterfactual future？**
2. **使用这些 future 是否改善真实 action selection？**

模型名字改变不了科学标准。

---

# 24. 最小复现实验

教材脚本：

`code/minimal/world_model_mpc.py`

流程：

```text
collect random real transitions
→ train action-conditioned dynamics MLP
→ CEM imagined rollout
→ execute first action in true dynamics
→ observe
→ replan
```

验收：

- held-out one-step RMSE 合理；
- MPC 能到目标；
- open-loop long rollout 出现 model drift；
- wrong/random model 让 planning 退化。

---

# 25. 一个论文级实验

任务：遮挡 + friction variation 的 manipulation。

比较：

```text
A. reactive policy
B. policy + video predictor
C. policy + action-conditioned latent model
D. C + contact/tactile prediction
```

固定：

- training data；
- visual backbone；
- controller；
- parameter/compute budget。

测：

- latent/state rollout error；
- action-counterfactual ranking；
- real task success；
- contact failure taxonomy；
- planning latency。

如果 D 只提高 predictive metric，不改善控制，就不能支持 contact-aware world model 的 action-value claim。

---

# 26. 一句话抓住 World Model

> **机器人 world model 的最低科学标准不是“能想象未来”，而是“能在动作干预下预测不同未来，并且这些预测对真实动作选择具有可测的因果价值”。**
