# Source-Level Case Studies

> 这里不是 paper summary。每一份源码案例都从**真实开源仓库的 commit / 文件路径**出发，追踪 dataset → processor → tensor → loss → inference → executor → controller boundary，并给出可证伪的源码级实验；机制案例则把源码/数学对象真正接入控制闭环。

## 当前 7 个 Case Studies

| Case Study | 路线 | 核心问题 |
|---|---|---|
| [ACT / ALOHA](./ACT_SOURCE_WALKTHROUGH.md) | action chunking imitation | CVAE latent、parallel action queries、chunk execution 与 temporal aggregation 如何组成细粒度双臂策略？ |
| [Diffusion Policy](./DIFFUSION_POLICY_SOURCE_WALKTHROUGH.md) | generative continuous action | 16-step trajectory、2-step observation、8-step execution、100-step DDPM 与真机 stale-action filtering 如何连接？ |
| [OpenVLA](./OPENVLA_SOURCE_WALKTHROUGH.md) | discrete action-token VLA | 连续动作怎样进入 256-bin LLM token vocabulary，再经 dataset stats 变回物理动作？ |
| [SmolVLA + LeRobot](./SMOLVLA_LEROBOT_SOURCE_WALKTHROUGH.md) | small/open VLA + flow action expert | VLM prefix、flow expert、50-step chunk、queue / async / RTC 如何分工？ |
| [GR00T N1.7](./GR00T_N17_SOURCE_WALKTHROUGH.md) | embodiment-conditioned foundation policy | processor、embodiment tags、DiT、flow、4-step integration、RTC、deployment 如何组成现代 robot foundation system？ |
| [V-JEPA 2 / 2.1](./VJEPA2_1_SOURCE_WALKTHROUGH.md) | predictive representation / latent dynamics | EMA target、masked latent prediction、action/state/extrinsics conditioning 何时才真正成为控制 world model？ |
| [World Model + Control](./WORLD_MODEL_CONTROL.md) | mechanism/control case | action-conditioned prediction 怎样通过 MPC/CEM、counterfactual test 与 negative controls 真正改善 action selection？ |

横向比较：

- [Action Path Comparison](./ACTION_PATH_COMPARISON.md) — OpenVLA vs SmolVLA vs GR00T N1.7 vs V-JEPA predictive path
- [Source-Code Atlas](../references/SOURCE_CODE_ATLAS.md) — 六个代表开源栈的 verified file map
- [Failure Atlas](../references/FAILURE_ATLAS.md) — 每条执行链的全栈 failure taxonomy

---

# 统一阅读模板

每个源码项目都强制回答：

```text
Repository / commit:
Training entry:
Dataset class:
Processor:
Observation tensors:
Action tensors:
Action semantics:
Loss:
Inference entry:
Sampling / decoding:
Action horizon:
Temporal executor:
Controller boundary:
Deployment boundary:
Tests worth reading:
Negative control:
```

只有能把这些问题回答清楚，才算真正从代码层理解一个具身模型。

---

# 现在已经形成三条历史链 + 一条预测链

## 1. Action chunking / generative control

```text
ACT
observation
→ parallel H action queries
→ chunk
→ temporal aggregation

Diffusion Policy
observation history
+ random trajectory
→ iterative denoising
→ trajectory slice
→ timestamp-aware execution
```

## 2. Action-token VLA

```text
OpenVLA
continuous action
→ discrete tokens
→ autoregressive VLM generation
→ de-tokenize / unnormalize
```

## 3. Continuous-expert VLA

```text
SmolVLA
VLM prefix
→ flow action expert
→ 10-step integration
→ queue / RTC

GR00T N1.7
VL backbone + embodiment
→ DiT / flow
→ 4-step integration
→ RTC / deployment runtime
```

## 4. Predictive intelligence

```text
V-JEPA 2.1
video / robot trajectory
→ representation prediction
→ action-conditioned latent dynamics

World Model + Control
latent dynamics
→ counterfactual rollout
→ evaluator / MPC / CEM
→ real action
```

前三条主要回答“动作怎样生成”；第四条回答“动作会让世界怎样变化，以及这种预测怎样改变决策”。

---

# 最重要的横向问题

这些代码共同暴露一个事实：

\[
\boxed{
\text{Embodied Policy}
\neq
\text{Checkpoint Only}
}
\]

真实系统能力至少还取决于：

```text
pre/post processor
normalization / convention
action representation
temporal horizon
sampling / decoding latency
queue / RTC / replanning
controller
robot hardware
```

所以后续源码案例的目标不是再收集模型，而是逐步回答：

> **哪些接口应该 joint learn，哪些应该保持 modular；哪些 gain 来自模型，哪些其实来自 executor、controller 或 data contract？**
