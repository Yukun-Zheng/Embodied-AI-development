# Source-Code Atlas — 从论文主图追到真实执行链

> **Snapshot: 2026-09-14.**
>
> 这不是 GitHub 项目推荐列表，而是教材的**源码阅读导航**。所有路径均来自实际检查过的公开仓库。目标是让读者从：
>
> ```text
> paper concept
> → dataset / processor
> → model forward
> → loss / training loop
> → inference
> → action executor
> → robot / benchmark
> ```
>
> 一路追到底，而不是只读 README 或论文主图。

---

# 1. 阅读源码的统一方法

进入任何 robot-learning 仓库，先不要逐文件看。

按这个顺序：

```text
1. README / config
2. train entry
3. dataset / processor
4. model class
5. loss
6. inference API
7. action postprocess / horizon
8. evaluation / deployment
9. tests
```

每一步回答：

- 输入 tensor 是什么？
- shape 是什么？
- coordinate/action convention 是什么？
- 哪部分 trainable？
- action 到底控制什么？
- temporal horizon / rate 是多少？
- 真机执行前还有什么层？

---

# 2. ACT — Action Chunking Transformer

Official repository:

- https://github.com/tonyzhaozh/act

## 2.1 最重要的入口

```text
imitate_episodes.py
policy.py
detr/
utils.py
sim_env.py
```

实际代码搜索确认：

- `policy.py` 定义 `ACTPolicy`；
- `ACTPolicy` 调用 ACT model / optimizer builder；
- `imitate_episodes.py` 导入并实例化 `ACTPolicy`，承担训练/评测主流程。

## 2.2 推荐阅读顺序

### Step 1 — `imitate_episodes.py`

先看：

```text
config
→ dataset loading
→ policy construction
→ train loop
→ checkpoint
→ rollout evaluation
```

不要先钻 DETR internals。

### Step 2 — `policy.py`

追踪：

```text
images
qpos / state
future action chunk
padding mask
→ ACTPolicy.forward(...)
→ loss
```

重点核对：

- action chunk length；
- KL / reconstruction terms；
- train vs inference branch；
- normalization。

### Step 3 — `detr/`

再看真正的 transformer / latent architecture。

此时应该已经知道每个 token 对应什么物理变量，而不是把它当普通 vision transformer。

## 2.3 源码研究问题

1. chunk length 改变时，训练 target tensor 怎样变化？
2. temporal aggregation 是 model 内部还是 executor 外部？
3. CVAE latent 真正表达行为 multimodality 吗？
4. 去掉 latent 后，哪些任务下降？
5. action normalization 与不同 robot embodiment 怎样耦合？

对应教材：Part 19、Part 21、`case-studies/ACT_SOURCE_WALKTHROUGH.md`。

---

# 3. Diffusion Policy

Official repository:

- https://github.com/real-stanford/diffusion_policy

## 3.1 已核实的核心文件

```text
diffusion_policy/policy/diffusion_unet_image_policy.py
diffusion_policy/workspace/train_diffusion_unet_image_workspace.py
diffusion_policy/config/train_diffusion_unet_image_workspace.yaml
eval.py
eval_real_robot.py
demo_pusht.py
demo_real_robot.py
```

代码搜索确认：

- `DiffusionUnetImagePolicy` 位于 `policy/diffusion_unet_image_policy.py`；
- image-policy training workspace 位于 `workspace/train_diffusion_unet_image_workspace.py`；
- Hydra config 通过 `_target_` 实例化上述 policy。

## 3.2 推荐阅读顺序

### Step 1 — YAML config

先把：

```text
shape_meta
n_obs_steps
horizon
n_action_steps
policy target
noise scheduler
```

抄成一张表。

### Step 2 — `train_diffusion_unet_image_workspace.py`

追踪：

```text
cfg
→ dataset
→ model
→ optimizer
→ training batch
→ loss
→ checkpoint
```

### Step 3 — `diffusion_unet_image_policy.py`

重点找两条链：

训练：

```text
obs
+ clean action trajectory
+ sampled noise
+ diffusion timestep
→ noisy trajectory
→ predicted noise / sample
→ loss
```

推理：

```text
obs history
+ random action trajectory
→ iterative denoising
→ action trajectory
→ slice executable actions
```

### Step 4 — `eval_real_robot.py`

真正看清：

- model output 如何裁剪；
- action steps 如何送给 robot；
- wall-clock / timing 如何处理。

## 3.3 关键负对照

- MSE action regression；
- diffusion sampling steps 减少；
- shuffled observation history；
- fixed vs rolling horizon；
-相同 checkpoint，不同 executor。

对应教材：Part 21、`case-studies/DIFFUSION_POLICY_SOURCE_WALKTHROUGH.md`。

---

# 4. OpenVLA

Official repository:

- https://github.com/openvla/openvla

## 4.1 已核实的顶层结构

```text
experiments/
prismatic/
scripts/
vla-scripts/
```

`vla-scripts/` 实际包含：

```text
train.py
finetune.py
deploy.py
```

`prismatic/` 实际包含：

```text
conf/
models/
preprocessing/
training/
vla/
```

## 4.2 推荐阅读顺序

### Step 1 — `vla-scripts/train.py`

找：

```text
model config
robot dataset
batch formatter
optimizer
training strategy
```

### Step 2 — `prismatic/vla/`

这里是 VLA-specific 数据/模型接口的重要入口。

重点查：

- image + instruction 怎样组成 model input；
- action 怎样离散/编码；
- token sequence 如何构造；
- robot normalization statistics 在哪里进入。

### Step 3 — `prismatic/models/`

再进入 vision-language backbone。

不要反过来先读大模型 backbone；否则很容易懂 language model，却不知道 action token 是怎样插进去的。

### Step 4 — `vla-scripts/finetune.py`

研究：

- pretrained VLA 如何适配 downstream robot dataset；
- 哪些参数冻结；
- data transform / normalization；
- fine-tuning budget。

### Step 5 — `vla-scripts/deploy.py`

这一步最重要：

```text
camera / instruction
→ model request
→ decoded action
→ external robot client
```

研究模型和机器人之间真正的系统边界。

## 4.3 OpenVLA 最适合研究的问题

- action tokenization；
- VLM prior 到 robot action 的迁移；
- parameter-efficient fine-tuning；
- robot-specific normalization；
- open VLA reproducibility。

对应教材：Parts 23–25。

---

# 5. LeRobot — 不只是模型，而是完整 Robot Learning Stack

Official repository:

- https://github.com/huggingface/lerobot

## 5.1 已核实的系统目录

`src/lerobot/` 中实际包含：

```text
async_inference/
cameras/
configs/
data_processing/
datasets/
distributed/
envs/
model/
motors/
policies/
```

这使 LeRobot 特别适合教材，因为它同时暴露：

```text
hardware
↕
data
↕
policy
↕
inference runtime
```

## 5.2 SmolVLA 已核实路径

```text
src/lerobot/policies/smolvla/configuration_smolvla.py
src/lerobot/policies/smolvla/modeling_smolvla.py
src/lerobot/policies/smolvla/processor_smolvla.py
src/lerobot/policies/smolvla/smolvlm_with_expert.py
examples/tutorial/smolvla/using_smolvla_example.py
```

`src/lerobot/policies/smolvla/__init__.py` 实际导出：

```text
SmolVLAConfig
SmolVLAPolicy
make_smolvla_pre_post_processors
```

## 5.3 RTC 与 Asynchronous Inference

已核实文档：

```text
docs/source/policy_rtc_README.md
docs/source/rtc.mdx
docs/source/async.mdx
src/lerobot/async_inference/
```

LeRobot 文档明确把 RTC 描述为**inference-time technique**，不是独立 policy；并展示它可作用于 flow-matching policy。

这非常适合解释教材中的：

\[
\text{policy} \neq \text{temporal executor}.
\]

`async.mdx` 又把 action prediction 与 action execution 解耦，因此可以直接研究：

- policy latency；
- stale action；
- chunk overlap；
- execution continuity。

## 5.4 LeRobot 推荐阅读路线

```text
LeRobotDataset
→ policy config
→ policy model
→ pre/post processor
→ train/eval CLI
→ async inference
→ robot abstraction
→ camera / motor driver
```

它比单个 model repo 更适合研究真实机器人系统工程。

---

# 6. NVIDIA Isaac-GR00T / GR00T N1.7

Official repository:

- https://github.com/NVIDIA/Isaac-GR00T

Official release:

- `n1.7-release`, published 2026-04-18.

## 6.1 已核实的核心路径

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
gr00t/model/gr00t_n1d7/setup.py
gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py
gr00t/configs/base_config.py
gr00t/data/embodiment_tags.py
getting_started/policy.md
getting_started/real_world_deployment.md
scripts/deployment/README.md
```

测试层也值得读：

```text
tests/gr00t/model/test_model_forward.py
tests/gr00t/model/test_gr00t_processor.py
tests/gr00t/model/test_action_head.py
tests/gr00t/model/test_action_horizon_validation.py
tests/gr00t/data/test_embodiment_tags.py
```

## 6.2 N1.7 模型入口

代码搜索确认：

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
```

导入 `Gr00tN1d7Config`，并使用包括 DiT / transformer action components 在内的模块。

`setup.py` 则把：

```text
Config
Gr00tN1d7Config
DatasetFactory
```

接到完整模型/数据 setup。

## 6.3 Embodiment Tag 是重要科学接口

```text
gr00t/data/embodiment_tags.py
```

实际定义 N1.7 checkpoint 支持的 embodiment tags。

研究时不要只问“支持几个 robot”，而应做：

```text
correct tag
wrong tag
shuffled tag
no tag
unseen morphology
```

判断 tag 是真正的 embodiment conditioning，还是 dataset identifier。

## 6.4 Action Head / Horizon

建议从：

```text
test_action_head.py
test_action_horizon_validation.py
```

倒着读 implementation。

测试往往比论文主图更清楚地暴露：

- expected shape；
- horizon contract；
- invalid condition；
- processor/model boundary。

## 6.5 Async Inference + RTC

`getting_started/real_world_deployment.md` 明确讨论：

```text
Asynchronous Inference + RTC
```

并说明 RTC 在当前代码中的 experimental/low-level interface 状态。

所以 GR00T 的真实部署链应写成：

```text
observation
→ processor
→ N1.7 model
→ action head / horizon
→ async runtime
→ optional RTC overlap handling
→ robot policy server / client
→ low-level control
```

而不是：

```text
image → foundation model → robot
```

## 6.6 为什么 N1.7 特别适合教学

因为它同时提供：

- model source；
- processor；
- embodiment tags；
- tests；
- DROID / LIBERO / RoboCasa / SimplerEnv examples；
- real-world deployment docs；
- PyTorch / TensorRT deployment path。

它可以被用来完整演示一个现代 robot foundation model 的**软件系统边界**。

---

# 7. V-JEPA 2 / V-JEPA 2.1

Official repository:

- https://github.com/facebookresearch/vjepa2

## 7.1 已核实的核心结构

```text
app/
configs/
evals/
notebooks/
src/
```

关键源码搜索结果：

```text
src/models/predictor.py
src/models/ac_predictor.py
app/vjepa/train.py
app/vjepa_2_1/train.py
app/vjepa_2_1/models/predictor.py
app/vjepa_2_1/wrappers.py
app/vjepa_droid/train.py
notebooks/utils/world_model_wrapper.py
```

## 7.2 V-JEPA 2 基础训练链

`app/vjepa/train.py` 中实际初始化：

```text
encoder
predictor
```

结合 target encoder 和 masked latent prediction objective。

推荐追：

```text
video batch
→ mask generation
→ encoder context
→ predictor
→ target encoder representation
→ latent prediction loss
```

重点是：预测发生在**representation space**，不是要求重建 pixel future。

## 7.3 Action-Conditioned Predictor

```text
src/models/ac_predictor.py
```

是 robotics / action-conditioned predictive intelligence 的关键入口。

研究时追踪：

```text
latent state
+ action
→ predictor
→ future latent
```

然后问：

> predicted latent 是否真正对 action intervention 敏感？

## 7.4 V-JEPA 2.1

代码已经明确分出：

```text
app/vjepa_2_1/train.py
app/vjepa_2_1/models/predictor.py
app/vjepa_2_1/wrappers.py
```

适合直接比较 V2 与 V2.1：

- model config；
- predictor normalization；
- modality embedding；
- temporal/dense representation design。

## 7.5 DROID 路径

```text
app/vjepa_droid/train.py
```

让 predictive representation 与 robot dataset 发生直接连接，是比 image/video benchmark 更有价值的 robotics 阅读入口。

## 7.6 最关键的源码负对照

- frozen random predictor；
- shuffled action；
- wrong action timing；
- pixel-only feature baseline；
- same encoder without predictive training。

最终要验证：

\[
\text{predictive representation improvement}
\rightarrow
\text{better physical decision/control}.
\]

---

# 8. 六个仓库怎样串起来读

不要孤立阅读。

推荐 progression：

```text
ACT
  ↓ learn chunking / imitation
Diffusion Policy
  ↓ learn generative continuous actions
OpenVLA
  ↓ learn VLM → action-token foundation policy
LeRobot
  ↓ learn unified data/policy/hardware/runtime stack
GR00T N1.7
  ↓ learn embodiment-conditioned modern foundation policy + deployment
V-JEPA 2 / 2.1
  ↓ learn predictive representation / world-model direction
```

这六个仓库正好覆盖：

```text
imitation
→ generative action
→ VLA
→ engineering stack
→ cross-embodiment foundation policy
→ predictive intelligence
```

---

# 9. 源码阅读记录模板

每读一个 model repository，建立一页：

```text
Repository:
Commit:
Date:
Training entry:
Dataset class:
Processor:
Model class:
Observation shapes:
Action shapes:
Action semantics:
Loss:
Inference entry:
Action horizon:
Temporal executor:
Controller boundary:
Robot interface:
Tests worth reading:
Three key failure modes:
One negative control:
One architecture question:
```

必须记录 commit；否则快速变化的 robotics repo 很快会失去可复现性。

---

# 10. 源码阅读的最终标准

真正读懂一个机器人模型，不是能解释 class hierarchy，而是能从一条真实样本开始完整追踪：

```text
raw episode
→ dataset indexing
→ normalization
→ tensor shapes
→ backbone / encoder
→ latent/state
→ action head
→ loss
→ checkpoint
→ inference
→ chunk / executor
→ controller interface
→ physical action
```

并且能指出：

1. 哪一层体现论文创新；
2. 哪一层只是 engineering；
3. 哪一层最可能制造 failure；
4. 哪个 negative control 能验证核心机制。

这才是本书所谓的 **source-level understanding**。
