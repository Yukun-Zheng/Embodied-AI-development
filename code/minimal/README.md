# Minimal Executable Code

> 这一目录不是“论文仓库大杂烩”，而是教材公式的 **20–200 行可运行镜像**。原则：先把数学和数据流跑明白，再进入 MuJoCo / SAPIEN / Isaac Lab / 真实机器人。

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
| `world_model_mpc.py` | Part 30 / D19–D20 | learned dynamics + CEM/MPC |
| `continual_metrics.py` | Part 38/39 / D26 | forgetting、forward transfer、growth metrics |
| `evaluation_stats.py` | Part 44 | success rate、Wilson interval、calibration |

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
4. 每个脚本都包含至少一个会失败的 counterexample；
5. 学习代码优先 toy problem，不用 benchmark complexity 掩盖机制。

## 推荐顺序

```text
se3.py
→ planar_arm.py
→ control.py
→ kalman_filter.py
→ active_perception.py
→ bc_dagger.py
→ generative_actions.py
→ world_model_mpc.py
→ continual_metrics.py
→ evaluation_stats.py
```

跑完这里，再进入 `labs/LABS.md` 的 simulator / foundation-model 实验。