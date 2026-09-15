# Lab Execution Matrix

> 目的：把 [`LABS.md`](LABS.md) 中的 40 个 Lab + 3 个 Capstone 从“实验设计”进一步变成**可执行课程**。这里不把所有实验都强行塞进同一技术栈，而是明确每个实验最小可运行层、推荐 simulator 层和真实系统扩展层。

## 1. 三层执行模型

| 层级 | 含义 | 主要用途 | 是否进入轻量 CI |
|---|---|---|---|
| **M — Mechanism / CPU** | NumPy / PyTorch / toy physics，秒到分钟级 | 验证公式、机制、负对照、日志协议 | **是** |
| **S — Simulator** | MuJoCo / Isaac Lab / RoboTwin / Habitat / ManiSkill 等真实物理或任务平台 | 验证机制在接触、视觉、复杂动力学和多任务中是否仍成立 | 只做 import/config/preflight；重实验不进 hosted CI |
| **R — Real System** | ROS 2 + 真机 / 真实传感器 / 网络 / controller | external validity、latency、calibration、safety | **否**；只验证 schema / protocol |

原则：

```text
M: 机制是否存在？
        ↓
S: 机制是否经得住物理复杂性？
        ↓
R: 机制是否经得住真实系统误差？
```

任何昂贵实验在进入 S/R 前，都应该先有能够 falsify 核心假设的 M 层版本。

---

## 2. Track A — 数学、几何与经典机器人

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 01 Jacobian / autodiff | ✓ | — | — | NumPy + PyTorch | analytic / autodiff / finite difference error sweep |
| 02 2-Link Arm | ✓ | ○ | — | NumPy → MuJoCo | singularity + DLS negative control |
| 03 SO(3) / SE(3) | ✓ | ○ | — | NumPy | convention-bug injection suite |
| 04 Numerical IK | ✓ | ✓ | ○ | NumPy → MuJoCo / Isaac | 7-DOF IK solver matrix |
| 05 Rigid-Body Dynamics | ✓ | ✓ | ○ | NumPy → MuJoCo | analytic dynamics vs simulator rollout |
| 06 Control | ✓ | ✓ | ✓ | toy plant → MuJoCo / Isaac | PD / computed torque / impedance under disturbance |
| 07 Planning | ✓ | ✓ | ○ | grid/toy → OMPL / simulator | A* / RRT / smoothing with collision margin |

Legend: `✓` = recommended execution layer, `○` = useful extension, `—` = normally unnecessary.

---

## 3. Track B — 感知、状态与主动获取信息

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 08 Camera Geometry | ✓ | ✓ | ○ | NumPy → simulator camera | calibration perturbation → grasp-target error |
| 09 RGB-D Point Cloud | ✓ | ✓ | ○ | synthetic depth → Isaac/SAPIEN | depth noise × camera-pose error factorial |
| 10 KF → EKF | ✓ | ✓ | ○ | NumPy → mobile sim | RMSE + NIS calibration |
| 11 Pose Graph / Tiny SLAM | ✓ | ✓ | ○ | synthetic graph → simulator trajectory | loop-closure intervention |
| 12 Vision Representation Probe | ○ | ✓ | ○ | recorded robot dataset | semantics vs geometry vs downstream policy |
| **13 Active Perception** | **✓** | ✓ | ○ | toy POMDP → Isaac/RoboTwin | fixed/random/information-gain camera policy |
| **14 Force / Tactile Reflex** | **✓** | ✓ | ✓ | toy contact → MuJoCo/Isaac + tactile | slow policy vs fast residual loop |

---

## 4. Track C — Imitation、RL 与生成式策略

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 15 Behavior Cloning | ✓ | ✓ | ○ | Push-T / toy manipulation | offline loss vs rollout success |
| 16 DAgger | ✓ | ✓ | ○ | toy control → simulator | visited-state distribution shift |
| 17 ACT / Action Chunking | ✓ | ✓ | ○ | toy plant → Push-T/RoboTwin | horizon × feedback-delay sweep |
| 18 PPO Locomotion | ○ | ✓ | ○ | Isaac Lab / MuJoCo | reward ablation + gait diagnostics |
| 19 Offline RL | ✓ | ✓ | ○ | synthetic dataset → simulator | in/out-of-dataset Q extrapolation |
| 20 Diffusion Policy | ✓ | ✓ | ○ | toy multimodal action → Push-T | sampling steps × latency × success |
| 21 Flow Matching Policy | ✓ | ✓ | ○ | toy action distribution → Push-T | parameter/data/horizon matched comparison |
| **22 Async Policy Execution** | **✓** | **✓** | **✓** | double-integrator → RoboTwin / real robot | latency × executor strategy × action age |

**Phase 1 首个 runnable lab：Lab 22。** 它连接 Part 21 的 action generation、真实部署中的 latency、controller boundary 与 failure diagnosis，同时不依赖大型 checkpoint 就能做机制 falsification。

---

## 5. Track D — VLA 与 Foundation Policy

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 23 Action-Token VLA | ✓ | ✓ | ○ | tiny VLA → OpenVLA | tokenization/decode error + tensor trace |
| 24 Continuous Action Expert | ✓ | ✓ | ○ | tiny flow expert → SmolVLA | continuous expert vs token action |
| **25 VLA Visual Intervention** | **✓** | ✓ | ✓ | synthetic visual causal mechanism → RoboTwin / LIBERO / real arm | geometry × appearance × camera × distractor intervention matrix |
| **26 Cross-Embodiment** | **✓** | ✓ | ○ | 1-D physical mechanism → two+ robot sims | interface semantics × seen lookup × held-out morphology conditioning |
| **27 Long-Horizon VLA + Memory** | **✓** | ✓ | ○ | partially observable memory task → household sim | bounded context × episodic × semantic × shuffled/unrelated controls |

Lab 25 已进入 permanent executable CI：同一 fixed instruction 与同一 representation schema 下，构造 geometry-causal、appearance-shortcut、camera-unaware 与 distractor-shortcut action head；base distribution 故意让四者都达到 100% success，再逐一干预 target position、texture、background、camera yaw、irrelevant distractor 与 target-geometry token。CI 同时检查 action sensitivity、nuisance invariance、downstream success 与 geometry-probe RMSE，从而显式区分“feature 中可解码信息”与“policy 因果使用信息”。

Lab 26 已进入 permanent executable CI：同一 shared canonical policy 在 A/B seen bodies 与 C/D held-out bodies 上执行；分别控制 raw interface、canonical state/action semantics、seen robot-ID lookup、continuous morphology descriptor、wrong morphology tag 与 wrong action semantics，并强制 `adaptation_steps=0` 报告 held-out interpolation / extrapolation。

Lab 27 已进入 permanent executable CI：one-shot mission binding 只在 episode 开头可见，随后经过 4/10/16 个 distractor subtasks 再做 object/gate/bin 三次 memory-dependent 决策；比较 no-memory、8-observation frame context、full episodic log、compact semantic state、capacity-matched shuffled memory 与 unrelated persistent memory，并同时记录 success、query accuracy、memory bytes 和 retrieval cost。

---

## 6. Track E — World Model、Reasoning 与持续学习

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 28 Latent World Model | ✓ | ✓ | ○ | synthetic dynamics → robot sim | multi-step error vs control utility |
| **29 World Model MPC** | **✓** | ✓ | ○ | toy dynamics → Push-T | planning horizon × model bias |
| 30 Video WM Executability | ○ | ✓ | ○ | robot video / simulator | visual quality vs executable success |
| **31 Reasoning Negative Control** | **✓** | ✓ | ○ | symbolic causal world → VLA benchmark | correct/no-plan/random/fluent-wrong/binding controls |
| 32 Experience Learning Flywheel | ✓ | ✓ | ✓ | toy → simulator/real | failure mining → correction → regression audit |
| **33 Continual Learning** | **✓** | ✓ | ○ | 3-D tasks → 2-D shared bottleneck → robot tasks | A→B→C retention/plasticity/replay matrix |
| **34 Self-Generated Curriculum** | **✓** | ✓ | ○ | competence-frontier task pool → simulator | learning progress × ordering × correct task binding |

Lab 31 已进入 permanent executable CI：同一批 episode 上比较 correct plan、no-plan、random-order、coherent-but-wrong causal model 与 shuffled entity binding；同时分别测 plan 在内部模型与真实世界中的 success、action validity、prerequisite failure 和 plan-budget matching。

Lab 33 已进入 permanent executable CI：固定参数容量下比较 naive fine-tune、correct replay、quadratic anchor 与 shuffled-label replay，并显式记录 performance matrix、probe matrix、forgetting、BWT、plasticity 和 method-specific memory cost。

Lab 34 已进入 permanent executable CI：五种 scheduler 共享 180-step practice budget 与相同 warmup。`uniform` 和 `fixed_curriculum` 具有相同每任务总 practice counts，用于隔离顺序效应；`learning_progress` 和 `shuffled_progress` 保留 progress magnitude、只打乱 task identity，用于隔离正确 progress-to-task binding。CI 同时记录 final competence、learning-curve AUC、selected-task learnability、frontier distance、mastered difficulty 与 allocation counts。

---

## 7. Track F — Humanoid、Whole-Body 与系统工程

| Lab | M | S | R | 推荐后端 | 第一可执行目标 |
|---|:---:|:---:|:---:|---|---|
| 35 Humanoid Retargeting | ○ | ✓ | ○ | Isaac Lab / MuJoCo | tracking + contact + balance feasibility |
| 36 Whole-Body Loco-Manipulation | — | ✓ | ○ | Isaac Lab | hierarchical vs unified whole-body |
| **37 Bimanual Coordination** | **✓** | ✓ | ✓ | compliant shared object → RoboTwin | midpoint × relative separation × internal-load controls |
| **38 Multi-Robot Collaboration** | **✓** | ✓ | ○ | heterogeneous work system → multi-robot sim | capability allocation × heartbeat freshness × failure reallocation |
| 39 ROS 2 Multi-Rate Deployment | ○ | ✓ | ✓ | ROS 2 + fake hardware → real | P50/P95/P99 latency + action age |
| **40 Watchdog / Safety Shield** | **✓** | ✓ | ✓ | closed-loop fake system → simulator/real | timeout/stale/unsafe/human-proximity gates + braking outcome |

Lab 37 已进入 permanent executable CI：在同一 paired actuator-gain / unilateral-disturbance episodes 上比较 independent world-frame endpoint control、midpoint-only common mode、midpoint+relative coordinated control 与 wrong-relative-sign negative control。CI 同时检查 object-center tracking、relative separation、transient shared-object strain、internal force、final feasibility 与 effort budget；其中 midpoint-only 明确构造“center RMSE 更好但 bimanual success 更差”的反例。

Lab 38 已进入 permanent executable CI：在同一组异构 precision/haul jobs 上比较 no-communication、fresh coordination、2-step delayed heartbeats、75% heartbeat dropout 与 shuffled capability metadata；另用同一失败时间/同一 interrupted job 比较 detected-failure 后是否 release/reallocate 中断工作。CI 同时记录 completion、makespan、duplicate claims、blocked/stale-idle steps、status age、capability mismatch、communication ratio/bytes 与 recovery latency。

Lab 40 已进入 permanent executable CI：在同一闭环 plant 中注入 model timeout、stale camera、unsafe joint target 与 human proximity，比较 no shield、static rules、freshness-blind predictive stop、complete predictive shield 与 overconservative shield。CI 不把“规则触发”当安全，而是在有限 braking dynamics 后检查 physical violation、normal availability、ask-human routing 与 audit reason；该 M 层结果**不是 functional-safety certification**。

---

## 8. Capstones

| Capstone | M | S | R | 推荐平台 | 最低完成条件 |
|---|:---:|:---:|:---:|---|---|
| C1 RoboTwin / Manipulation Arena | ○ | ✓ | ○ | RoboTwin | ACT + Diffusion/DP3 + Flow + VLA 同协议比较 |
| C2 Humanoid Developmental Agent | ○ | ✓ | ○ | Isaac Lab | A→B→C + revisit，测 plasticity/retention/transfer |
| C3 Falsifiable New Architecture | ✓ | ✓ | ○ | 由 hypothesis 决定 | toy falsification → controlled benchmark → external validity |

---

## 9. Phase roadmap

### Phase 1 — Runnable scientific harness

先解决所有 Lab 都共享的问题：

```text
config
→ deterministic seed
→ environment/system contract
→ per-step raw log
→ summary metrics
→ failure event
→ run manifest
→ reproducible output directory
```

首个 reference implementation 是 **Lab 22 Asynchronous Policy Execution**；当前 CI-verified reference set 已扩展为 **Lab 13 / 14 / 22 / 25 / 26 / 27 / 29 / 31 / 33 / 34 / 37 / 38 / 40**。

### Phase 2 — Physics adapters

优先增加：

1. MuJoCo adapter：Lab 04/05/06/18；
2. RoboTwin adapter：Lab 17/22/25/26/37 + Capstone 1；
3. Isaac Lab adapter：Lab 18/26/35/36 + Capstone 2。

Hosted CI 只做 adapter import / config / dry-run，真正 GPU simulator rollout 在研究机器上执行。

### Phase 3 — Real-system adapters

再进入：

- ROS 2 multi-rate executor；
- timestamp / calibration manifest；
- watchdog / e-stop integration；
- synchronized RGB/depth/state/tactile logging；
- real-robot reset / intervention protocol。

---

## 10. 验收原则

一个 Lab 从“课程题目”升级为“可执行 Lab”，至少需要：

```text
README / hypothesis
config
run command
raw per-step log
summary metrics
failure events
manifest with seed + git + environment
negative control
smoke test
```

只有 notebook 截图、成功视频或一个 final success number，不算 executable lab。
