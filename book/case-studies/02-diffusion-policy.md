# Legacy Diffusion Policy Case Study

> 本路径保留用于兼容旧链接。最新版已经迁移到：
>
> **[`case-studies/DIFFUSION_POLICY_SOURCE_WALKTHROUGH.md`](../../case-studies/DIFFUSION_POLICY_SOURCE_WALKTHROUGH.md)**

新版基于 `real-stanford/diffusion_policy` 官方源码，追踪 Hydra config → dataset/normalizer → image encoder → ConditionalUnet1D → DDPM loss/sampling → EMA → real-robot timestamped execution，并显式分析 horizon、observation history、action execution window 与 stale-action latency。
