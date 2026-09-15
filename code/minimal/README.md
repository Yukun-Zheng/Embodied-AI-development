# Minimal Executable Code

> 这一目录不是“论文仓库大杂烩”，而是教材公式与关键机制的 **20–200 行可运行镜像**。原则：先把数学、数据流和系统接口跑明白，再进入 MuJoCo / SAPIEN / Isaac Lab / 真实机器人。

## 环境

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy torch matplotlib
```

Python 3.10+ 即可。核心脚本不需要 CUDA。

## 文件

| 文件 | 对应教材 | 学什么 |
|---|---|---|
| `se3.py` | Part 7 / D4–D5 | SO(3)、Rodrigues、SE(3)、frame composition |
| `planar_arm.py` | Part 8 / D1–D3/D6 | FK、Jacobian、DLS IK、null space |
| `control.py` | Part 10 / D8–D9 | PID、impedance、LQR |
| `kalman_filter.py` | Part 15 / D10–D11 | prediction/update、uncertainty fusion |
| `active_perception.py` | Part 17 / D12 | entropy、information gain、NBV |
| `bc_dagger.py` | Part 19 / D13 | covariate shift、DAgger |
| `generative_actions.py` | Part 18/21 / D15–D16 | multimodal regression、diffusion、flow |
| `action_tokenization.py` | Part 21/23/25 | OpenVLA-style uniform action bins、token round-trip、quantization / clipping error |
| `chunk_latency.py` | Part 21/24/43 | blocking chunk vs asynchronous replacement、stale action、latency as a control variable |
| `embodiment_interfaces.py` | Part 24/26/37 | padding ≠ shared semantics、embodiment-specific mapping、action mask |
| `world_model_mpc.py` | Part 30 / D19–D20 | learned dynamics + CEM/MPC |
| `continual_metrics.py` | Part 38/39 / D26 | forgetting、forward transfer、growth metrics |
| `evaluation_stats.py` | Part 44 | success rate、Wilson interval、calibration |

## 三个现代 Action-Path 实验

### 1. Action tokenization

```text
continuous action [-1,1]
→ uniform bin
→ reserved token id
→ bin center
→ continuous action
```

`action_tokenization.py` 直接量化 32 / 64 / 256 / 1024 bins 的 round-trip error，并展示超出训练范围的 action 会先被 clipping。读者应看到：**tokenization resolution 和 normalization range 本身就是 control design variable。**

### 2. Chunk latency

```text
same policy
same dynamics
same inference delay
        ↓
blocking executor  vs  asynchronous executor
        ↓
different closed-loop error
```

`chunk_latency.py` 故意不伪装成 RTC 实现；它只证明 RTC / async inference 要解决的前提事实：**temporal executor 本身会改变任务表现，离线 action loss 无法描述这一层。**

### 3. Cross-embodiment interface

```text
canonical intent z
   ├─ embodiment A mapping → 3-D raw action
   └─ embodiment B mapping → 5-D raw action
```

`embodiment_interfaces.py` 展示两个同为 `[B,5]` 的 padded action tensor 可以具有完全不同的物理语义；只有 embodiment-aware mapping 与 valid-dimension mask 才能恢复共享 intent。

## 统一约定

所有示例都尽量显式打印 shape：

```text
state      [B, state_dim]
action     [B, action_dim]
trajectory [B, T, ...]
```

代码与教材统一遵循：

1. 不隐藏 coordinate frame；
2. 不把 batch/time/joint 维混写；
3. 先用 numerical check 验证公式；
4. 每个脚本都包含至少一个会失败的 counterexample / negative control；
5. 学习代码优先 toy problem，不用 benchmark complexity 掩盖机制；
6. 明确区分 **model / sampler / temporal executor / controller**，不把它们混成一个“policy”。

## 推荐顺序

```text
se3.py
→ planar_arm.py
→ control.py
→ kalman_filter.py
→ active_perception.py
→ bc_dagger.py
→ generative_actions.py
→ action_tokenization.py
→ chunk_latency.py
→ embodiment_interfaces.py
→ world_model_mpc.py
→ continual_metrics.py
→ evaluation_stats.py
```

一键回归：

```bash
python code/minimal/run_all.py
```

跑完这里，再进入 `labs/LABS.md` 的 simulator / foundation-model 实验，以及 `case-studies/` 的官方源码 walkthrough。
