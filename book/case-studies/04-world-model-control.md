# Case Study 04 — Predictive World Model + Control
## 预测只有进入 Action Selection 才真正闭环

> 目标：把“World Model”从一个模糊的流行词拆成可实验的控制结构。一个真正服务机器人的 world model 至少要回答：**给定当前状态和候选动作，未来会怎样变化；这些预测是否能改变动作选择；错误预测又如何被真实反馈纠正。**

---

# 1. 先定义最低限度的 World Model

当前 observation：

$$
o_t
$$

编码为 latent state：

$$
z_t=E(o_t)
$$

给定 action：

$$
a_t
$$

预测下一 latent：

$$
\hat z_{t+1}=F_\theta(z_t,a_t)
$$

这就是最小 action-conditioned predictive model。

如果模型只有：

$$
\hat z_{t+1}=F(z_t)
$$

它可以预测视频演化，但还不能回答：

> “如果我采取另一个动作，会怎样？”

而后者才是控制真正需要的 counterfactual。

---

# 2. Raw Data 必须包含 Action

训练 episode：

```text
o_0, a_0, o_1, a_1, ..., o_T
```

window：

```text
context observations  [B, Tc, ...]
action sequence       [B, H, Da]
future observations   [B, H, ...]
```

如果只有无动作视频：

```text
video → future video
```

可以学习 predictive representation，但要变成 robot world model，仍需要把 action intervention 接进去。

---

# 3. Representation Model 与 Dynamics Model 要分开

Encoder：

$$
z_t=E_\phi(o_t)
$$

Dynamics：

$$
\hat z_{t+1}=F_\theta(z_t,a_t)
$$

Decoder 可选：

$$
\hat o_{t+1}=D(\hat z_{t+1})
$$

关键：**控制不一定需要 pixel decoder。**

如果 latent 已经足够判断：

- object pose；
- contact；
- goal progress；
- collision；

那么重建每个背景像素可能是多余任务。

---

# 4. JEPA / Predictive Representation 的不同思路

传统 autoencoder/world model 常预测输入空间或 reconstruct pixel。

JEPA 类思路更强调在 representation space 预测目标 latent：

$$
\hat z_{future}=P(z_{context},a)
$$

而不是：

$$
\hat I_{future}=Decoder(\hat z)
$$

潜在优势：

- 不浪费容量重建难以预测但任务无关的纹理；
- representation 更容易保留高层动态结构。

但最终是否“更物理”，仍需 intervention/control test，而不是看 latent visualization。

---

# 5. Action-Conditioned Prediction 的 Shape

假设：

```text
context latent z_t: [B, N, D]
action chunk A:     [B, H, Da]
```

world model 输出：

```text
future latent:      [B, H, N', D]
```

或者 object-centric：

```text
objects_t:          [B, M, D_obj]
actions:            [B, H, Da]
future objects:     [B, H, M, D_obj]
```

真正重要的是：模型能否保持**同一个物体、同一个关节、同一个 contact event**在时间上的身份和结构。

---

# 6. Training Objective 不只一种

## Latent prediction

$$
\mathcal L_{pred}=\|\hat z_{t+1}-sg(z_{t+1})\|^2
$$

## Contrastive / energy objective

让正确 future 更接近，错误 future 更远。

## Pixel/video generation

$$
\mathcal L_{video}
$$

## State supervision

$$
\mathcal L_{state}=\|g(\hat z)-s_{future}\|^2
$$

## Contact / event supervision

$$
\mathcal L_{contact}=CE(\hat c,c)
$$

不同 objective 对“控制上有用”影响必须单独实验。

---

# 7. One-Step Accurate 仍不够

单步：

$$
\|\hat z_{t+1}-z_{t+1}\|\ll1
$$

并不保证 rollout：

$$
\hat z_{t+H}
$$

准确。

若每步误差：

$$
e_{k+1}\le Le_k+\epsilon
$$

则：

$$
e_H\le\epsilon\sum_{i=0}^{H-1}L^i
$$

如果 `L>1`，误差会快速放大。

所以 world-model paper 至少应该画：

```text
prediction error vs horizon
```

而不是只报 one-step loss。

---

# 8. World Model 怎样真正改变 Action

最经典：MPC。

给候选 action sequence：

$$
A=[a_t,\ldots,a_{t+H-1}]
$$

rollout：

$$
\hat z_{t+1:t+H}=Rollout(F,z_t,A)
$$

计算 value / cost：

$$
J(A)=\sum_{k=1}^H c(\hat z_{t+k},a_{t+k-1})
$$

选择：

$$
A^*=\arg\min_A J(A)
$$

执行：

$$
a_t=A_0^*
$$

只执行第一个动作，再重新观察。

---

# 9. Search / Optimization 可以怎么做

### Random Shooting

随机采样很多 action sequences。

### CEM

```text
sample action sequences
→ score imagined futures
→ keep elites
→ update Gaussian
→ repeat
```

### Gradient-based

若 world model 可微：

$$
\nabla_A J
$$

直接优化 action。

### Policy-guided search

policy 给 proposal，world model rerank。

后者尤其适合大 action space。

---

# 10. 为什么 Receding Horizon 是核心

如果一次用 learned model 规划 100 步并全部执行：

```text
small model bias
→ rollout drift
→ wrong action late in horizon
```

MPC 每步：

```text
predict
→ act one step
→ observe reality
→ reset latent / belief
→ predict again
```

真实 observation 不断把系统拉回世界。

教材 `code/minimal/world_model_mpc.py` 就实现了这一闭环。

---

# 11. Counterfactual Test：最重要的 World Model 实验

固定当前 observation `o_t`，给不同 action：

$$
a^{(1)},a^{(2)},a^{(3)}
$$

测试：

$$
\hat s'^{(i)}=F(o_t,a^{(i)})
$$

与真实 intervention：

$$
s'^{(i)}_{real}
$$

比较。

如果模型只会预测“最常见 future”，无论 action 怎么换都差不多，它就不是好的 control world model。

---

# 12. Contact 是最强压力测试之一

视觉世界模型可能很好预测：

- camera motion；
- gross object motion。

但机器人真正需要：

- contact onset；
- slip；
- jam；
- force transmission；
- deformation。

这些事件通常在 pixel loss 中占比很小，却对 action 成败极重要。

所以必须加 task-relevant metric。

---

# 13. World Model + Reward / Goal Evaluator

预测本身不知道什么是“好”。

还需要：

$$
r=R(z,g)
$$

或者：

$$
V(z,g)
$$

系统：

```text
world model predicts what happens
+
evaluator says whether it is useful
→ planner chooses action
```

如果 evaluator 也由 VLM 给出，要额外验证它的 calibration。

---

# 14. 视频生成为什么容易制造错觉

一个 future video 可以：

- visually plausible；
- temporally smooth；

但：

- object pose 差 5 cm；
- contact 早 200 ms；
- friction effect 错；

这些足以让机器人失败。

所以：

$$
Visual\ Realism\neq Control\ Fidelity
$$

这应该成为所有 generative-world-model 评测的第一原则。

---

# 15. 评测 World Model 的四层指标

## Level 1：Representation

- linear probe；
- dense correspondence；
- object consistency。

## Level 2：Prediction

- one-step state error；
- H-step rollout error；
- contact/event accuracy。

## Level 3：Counterfactual

- action intervention ranking；
- alternative future discrimination。

## Level 4：Control

- MPC success；
- policy improvement；
- real robot task success。

只有 Level 4 才直接证明 world model 对 action 有用。

---

# 16. Negative Control A：Random World Model

把 learned world model 换成 frozen random network。

如果 planner success 几乎不变：

- planner 没真正用预测；或
- task 根本不需要 model。

---

# 17. Negative Control B：Shuffled Future

保持 future latent 的 marginal distribution，但把对应 action 打乱。

这样可检验：

> 收益来自“有一个未来 representation”，还是来自正确 action-conditioned mapping？

---

# 18. Negative Control C：Wrong Physics

人为改变 predicted friction / mass / contact rule。

如果 policy 对这些错误不敏感，说明它可能没有依赖物理细节。

如果真实 success 明显下降，则能说明这些机制对 planning 有因果作用。

---

# 19. Negative Control D：Use Current State Only

baseline：

$$
a_t=\pi(z_t,g)
$$

vs：

$$
a_t=Plan(F,z_t,g)
$$

必须在**相同 perception backbone / data** 下比较，才能归因 prediction。

---

# 20. World Model 与 Policy 可以共同训练吗

可以：

$$
\mathcal L
=\mathcal L_{policy}
+\lambda\mathcal L_{prediction}
$$

但需问：

- prediction loss 是否帮助 policy？
- 还是只作为 regularizer？
- representation 是否被 policy 读取？

可以通过 gradient blocking / detach ablation 检查。

---

# 21. Predictive Representation ≠ Full Simulator

world model 不一定要预测全部真实世界。

任务可能只需要：

```text
object relation
contact mode
goal progress
collision risk
```

因此更合理目标可能是：

$$
Task\text{-}Sufficient\ Predictive\ State
$$

而不是复制宇宙的每个像素。

---

# 22. 从 V-JEPA / Predictive Video 到 Robotics

预测式视觉表示的价值可以分三步验证：

1. video representation 更稳定；
2. robot downstream task probe 更好；
3. action-conditioned control 真正提高。

不能从第 1 步直接跳到：

> “模型已经理解物理世界。”

中间还缺 intervention 和 control evidence。

---

# 23. World Action Model

更进一步的模型把：

- world generation；
- reasoning；
- action prediction

放在更统一系统。

但评价仍可以回到同一原则：

```text
Does changing the action produce the right counterfactual future?
Does using that future improve real action selection?
```

模型名字变化不改变科学标准。

---

# 24. 最小复现实验

教材脚本：

`code/minimal/world_model_mpc.py`

流程：

```text
random real transitions
→ train action-conditioned dynamics MLP
→ CEM imagined rollout
→ execute first action in true dynamics
→ replan
```

验收：

- held-out one-step RMSE 小；
- MPC 能到目标；
- 更长 open-loop rollout 显示 model drift 风险。

---

# 25. 一个真正论文级实验

任务：遮挡 + friction variation 的 manipulation。

比较：

```text
A. reactive policy
B. policy + video predictor
C. policy + action-conditioned latent model
D. C + contact/tactile prediction
```

控制：

- training data；
- visual backbone；
- parameter budget。

测：

- state rollout error；
- counterfactual ranking；
- real control success；
- contact failure。

如果 D 只让视频更漂亮、不改善真实任务，就不能支持 contact-aware world model claim。

---

# 一句话抓住 World Model

> **机器人 world model 的最低科学标准不是“能想象未来”，而是“能在动作干预下预测不同未来，并且这些预测对真实动作选择具有可测的因果价值”。**
