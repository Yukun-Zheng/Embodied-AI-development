# Source-Level Case Studies

> 这里不是 paper summary。每一份 Case Study 都从**真实开源仓库的 commit / 文件路径**出发，追踪 dataset → processor → tensor → loss → inference → executor → controller boundary，并给出可证伪的源码级实验。

## 当前 Case Studies

| Case Study | 路线 | 核心问题 |
|---|---|---|
| [OpenVLA](./OPENVLA_SOURCE_WALKTHROUGH.md) | discrete action-token VLA | 连续动作怎样进入 LLM token vocabulary，再变回物理动作？ |
| [SmolVLA + LeRobot](./SMOLVLA_LEROBOT_SOURCE_WALKTHROUGH.md) | small/open VLA + flow action expert | VLM prefix、action expert、action queue 与 RTC 如何分工？ |
| [GR00T N1.7](./GR00T_N17_SOURCE_WALKTHROUGH.md) | embodiment-conditioned robot foundation policy | processor、embodiment tags、DiT、flow、RTC、deployment 如何组成一个现代 foundation robot system？ |
| [V-JEPA 2 / 2.1](./VJEPA2_1_SOURCE_WALKTHROUGH.md) | predictive representation / action-conditioned latent dynamics | representation prediction 什么时候才真正成为可用于控制的 world model？ |

另见：

- [Action Path Comparison](./ACTION_PATH_COMPARISON.md)
- [Source-Code Atlas](../references/SOURCE_CODE_ATLAS.md)

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

# 四条路线现在已经形成互补

```text
OpenVLA
continuous action
→ discrete tokens
→ autoregressive VLM generation

SmolVLA
continuous action chunk
→ flow matching
→ VLM prefix + action expert
→ queue / RTC

GR00T N1.7
multi-embodiment state/action
→ embodiment-conditioned encoders
→ VL-conditioned DiT / flow
→ RTC / deployment runtime

V-JEPA 2.1
video / robot trajectory
→ representation prediction
→ action-conditioned latent dynamics
→ optional planner / policy
```

前三条回答“动作怎样生成”；第四条回答“世界怎样预测”。

下一步的研究问题就是：

> **action model、world model、memory、controller 到底应该怎样组合，而不是继续把所有能力塞进一个 Transformer。**
