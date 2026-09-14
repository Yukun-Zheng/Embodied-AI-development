# Case Studies — 从数据 Tensor 追到真实 Action

> 这一层专门训练“读源码与拆系统”的能力。每个 Case Study 不以论文主图为结束，而要回答：
>
> **dataset 里一条样本长什么样 → DataLoader 怎么变 shape → 模型每个分支吃什么 → loss 怎么形成 → inference 怎么输出 action → action 怎样进入 controller → 哪里最可能失败。**

## Case 01 — ACT / ALOHA

[ACT：Action Chunking Transformer 从双臂示范到闭环执行](./01-act-aloha.md)

重点：

```text
episode
→ multi-view images + qpos + action sequence
→ CVAE latent during training
→ Transformer
→ action chunk
→ temporal aggregation / receding execution
→ bimanual robot
```

## Case 02 — Diffusion Policy

[Diffusion Policy：从 Observation History 到去噪 Action Horizon](./02-diffusion-policy.md)

重点：

```text
observation history
→ visual encoder
→ conditioning vector/tokens
→ noisy action trajectory
→ denoising process
→ action horizon
→ execute prefix
→ re-observe
```

## Case 03 — OpenVLA vs π-style Continuous Action Expert

[两类现代 VLA：Action Token 与 Continuous Action Expert](./03-modern-vla-action-paths.md)

重点：

```text
image + language + robot state
→ foundation backbone
→ discrete action token path
vs
→ continuous flow/diffusion expert path
→ temporal executor
→ low-level controller
```

## Case 04 — Predictive World Model + Control

[World Model：预测只有进入 Action Selection 才真正闭环](./04-world-model-control.md)

重点：

```text
video / state / action
→ predictive representation
→ action-conditioned future
→ evaluator / MPC
→ real action
→ new observation
```

---

# 统一拆解模板

以后加入任何论文源码，必须填写：

```text
1. Research claim
2. Robot / environment
3. Raw episode schema
4. Observation shape
5. Action definition / frame / frequency
6. Dataset windowing
7. Model inputs
8. Intermediate representations
9. Training objective
10. Inference loop
11. Low-level controller
12. Latency
13. Failure taxonomy
14. Positive control
15. Negative control
16. Minimal reproduction
17. What the code actually proves
18. What it does NOT prove
```

如果缺第 11 项，通常还没有读完整个机器人系统；如果缺第 15 项，通常还没有进入机制研究。