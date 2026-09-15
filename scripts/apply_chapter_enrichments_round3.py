#!/usr/bin/env python3
"""Final curated enrichment batch to close all strict chapter-structure gaps.

The strict audit requires six explicit dimensions in every canonical chapter:
math, code/dataflow, failure analysis, experiment, research questions, sources.
This batch adds only the missing scientific structure for each affected Part.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
SOURCE_START = "<!-- CHAPTER-SOURCE-MAP:START -->"

ENRICHMENTS: dict[int, str] = {
    0: r"""
## 0.12 Failure Taxonomy：什么时候“看起来智能”却不是具身智能

### Offline competence without closed-loop competence

模型能回答“下一步该抓杯子”，但在抓偏后不能利用新 observation 修正；这证明 semantic competence 不能替代 feedback competence。

### Body-agnostic claim without body intervention

只在同一机械臂、更换物体测试，不能支持 embodiment generality。必须改变 kinematics、action interface、sensor placement 或 controller 才真正触碰身体变化。

### World-model claim without action sensitivity

若预测未来不随候选 action 改变，模型更接近 video predictor，而不是可用于 control 的 counterfactual model。

### Memory claim without delayed necessity

若去掉历史后任务仍成功，所谓 memory module 可能只是额外容量。必须设计“当前 observation 不足、过去信息必要”的任务。

### Intelligence claim hidden by infrastructure

更强 simulator、controller、teleoperation data、reset protocol 或人工 intervention 都可能提高 success。系统能力必须展开到完整物理栈后再归因。
""",
    3: r"""
## 3.17 Uncertainty Failure Taxonomy

### Overconfidence under distribution shift

训练内 calibration 良好，但换 camera、object material、lighting 或 embodiment 后 \(\hat p\) 仍接近 1。安全系统若直接信任 confidence，会在最需要保守时最冒险。

### Variance without semantics

diffusion sample variance、ensemble disagreement 或 token entropy 不一定对应 task failure；它们可能只反映 action multimodality 或语言不确定性。

### Mean prediction hides multi-modality

用均值和方差描述高度多峰 grasp/action distribution，可能得到一个物理上不可执行的“平均动作”。

### Uncertainty never reaches the executor

模型输出 uncertainty，但 controller、planner、active perception 和 human handoff 都不读取它；这类 uncertainty 不能算系统能力。

### Wrong uncertainty source

把 sensor noise 当 epistemic、把 model ignorance 当 aleatoric，会导致错误的数据采集和 safety 策略。
""",
    15: r"""
## 15.30 State-Estimation Dataflow：从 Raw Sensor 到 Belief

```text
camera / IMU / encoder / force sensor
→ calibration + timestamp synchronization
→ measurement z_t with covariance R_t
→ motion/control input u_t
→ prediction p(x_t | x_{t-1}, u_{t-1})
→ innovation z_t - h(x_t)
→ update / optimization / factor graph
→ belief mean + covariance / particles
→ planner / policy / safety layer
→ action
→ next sensor measurements
```

实现中至少要显式保存：

```text
measurement timestamp
state timestamp
frame id
innovation / residual
covariance or confidence
rejected measurements
prediction horizon
```

否则 downstream policy 看到的“state tensor”会把估计误差、延迟与真实物理变化混成同一个数值变化。
""",
    24: r"""
## 24.20 Failure Taxonomy：第二阶段 VLA 真正还没解决什么

### Semantic generalization without geometric precision

能理解 novel instruction / object category，但 grasp pose、contact timing、force profile 仍不准确。语言/VLM scaling 不会自动填补毫米级控制误差。

### Better action generator, same stale execution

flow/diffusion chunk 离线更平滑，但推理 latency 仍让机器人执行旧 chunk。action model 与 temporal executor 必须分开评价。

### Cross-embodiment by mixture, not mechanism

多机器人训练后每台已见机器人都变强，不代表形成 morphology-agnostic representation；robot-ID shortcut 仍可能成立。

### Whole-body claim delegated to hidden controller

高层模型只给 hand/base goal，balance/contact stability 实际由 WBC/locomotion policy 完成。论文必须明确 capability credit。

### Experience learning with silent forgetting

on-robot RL/post-training 提升当前任务，但旧技能、safety calibration 或 generality 下降，不能只报新任务 throughput。

## 24.21 研究问题

1. 2026 VLA 的主要瓶颈已经从 representation 转向 temporal execution / controller interface 了吗？
2. VLM backbone 与 action expert 的 joint training 何时真正优于冻结语义 backbone？
3. RTC/async executor 应被视为 model architecture、control algorithm 还是 deployment runtime；怎样公平比较？
4. Cross-embodiment foundation policy 的核心共享对象究竟是 visual semantics、task relation、action effect 还是 morphology-conditioned dynamics？
5. Foundation policy + world model + memory 是否应继续融合成单模型，还是应该按时间尺度重新模块化？
6. 部署后持续 RL 如何同时优化新任务、避免 forgetting，并保持可审计的 safety boundary？
""",
    25: r"""
## 25.17 研究问题

1. VLA 中哪一层 representation 对真实 action success 具有最大 causal effect，而不仅是 probe accuracy？
2. 冻结 vision/VLM 后性能下降，来自 representation 不够还是 action distribution shift 无法适配？
3. Dataset mixture weight 能否被视为 architecture hyperparameter；怎样把 data effect 与 model effect 分开？
4. Proprioception、language、multi-view vision 在不同 task phase 的边际价值是否应该动态变化？
5. Action head 的 capacity 增加何时真正提高 physical precision，何时只提高 imitation fit？
6. 是否可以从梯度/activation intervention 中识别“knowledge insulation”并预测哪些 web knowledge 永远不会进入 motor behavior？
""",
    26: r"""
## 26.21 研究问题

1. Robot-data scaling 应按 hours/episodes 还是 state-action coverage、physics diversity、embodiment diversity 计量？
2. Human video 的 transfer gain 来自视觉表示、动作先验、任务分解，还是只是额外 scene diversity？
3. Synthetic/retargeted data 在哪些 contact-rich failure 上会系统性误导真实 policy？
4. Universal action space 应表示 joint command、task-space effect、object relation 还是 contact intent？
5. Dataset mixture 中低质量大数据与高质量小数据的最优权重能否由 downstream marginal value 自动学习？
6. Unseen-body transfer 需要 morphology graph / URDF / calibration data 到什么程度才能摆脱 robot-ID shortcut？
""",
    27: r"""
## 27.19 Agentic / Reasoning Failure Taxonomy

### Fluent plan, wrong physical precondition

语言计划逻辑通顺，但忽略 object pose、reachability、contact 或 robot state，导致第一步就不可执行。

### Stale task state

planner 使用旧 progress/memory，重复已完成 subtask 或跳过失败恢复。长时任务需要可更新的 task belief，而不是静态 chain-of-thought。

### Tool/skill hallucination

reasoner 调用不存在、参数不合法或当前 embodiment 不支持的 skill。skill library 必须有 machine-checkable contract。

### Reasoning latency exceeds physical timescale

高层推理耗时数秒，而环境继续变化。需要 async planning、progress monitor 与低层 reactive policy 并行。

### Explanation without causal control

模型能解释“为什么这样做”，但删除 explanation tokens 后行为不变。语言 reasoning 的因果价值必须通过 intervention 验证。

## 27.20 研究问题

1. Embodied reasoning 最小必要 state 是语言 task graph、symbolic predicates、continuous belief，还是多尺度混合？
2. Reasoner 与 motor policy 的刷新频率应该如何自适应任务 phase 与 uncertainty？
3. Tool/skill calling 如何在新 embodiment 上验证 precondition/effect，而不依赖手工 skill metadata？
4. Chain-of-thought 的价值应按解释质量还是行为 intervention gain 评价？
5. 长时 agent 应如何决定何时重规划、何时继续执行、何时请求人类澄清？
""",
    29: r"""
## 29.18 研究问题

1. Autonomous experience 中最有价值的数据来自成功、near-failure、intervention 还是 recovery？
2. Online RL 的 reward 如何避免把吞吐提升换成更激进、更不安全的行为？
3. Foundation policy 的局部 task adaptation 如何保持 broad generality 与 calibration？
4. Experience replay 应按 recency、novelty、TD error、failure severity 还是 mechanism novelty 采样？
5. 真机学习何时应该更新 policy 参数，何时只更新 memory/world model/system ID？
6. 如何让机器人长期学习同时具备 rollback：新策略出问题时能恢复到已验证的行为版本？
""",
    30: r"""
## 30.26 World-Model Failure Taxonomy

### One-step accuracy, long-rollout collapse

\(\hat z_{t+1}\) 很准，但 autoregressive rollout 误差快速累积。只报 one-step loss 不能支持 planning claim。

### Action insensitivity

改变候选 action，预测 future 几乎不变；模型学到 environment dynamics prior，而没有学到 intervention effect。

### Visually plausible, physically wrong

future video 很真实，但 object pose、contact onset、friction effect 或 tool geometry 有小误差，足以让 planner 失败。

### Representation predicts nuisance better than task state

latent 容易预测背景/camera motion，却丢失 contact、goal progress、support relation 等低像素占比变量。

### Planner ignores the model

加入 world model 后 success 提升，但用 shuffled/random model 也同样提升，说明收益可能来自额外 compute / proposal search。

## 30.27 最小实验：World Model 必须通过 Intervention + Control

固定当前 state \(s_t\)，选择多个动作 \(a^{(i)}\)，比较真实后果与预测：

\[
\hat s_{t+1}^{(i)}=F(s_t,a^{(i)}),\qquad
s_{t+1}^{(i)}=Env(s_t,a^{(i)}).
\]

至少做三层评测：

1. **Prediction**：one-step 与 H-step error；
2. **Counterfactual ranking**：是否正确排序不同 action 的 outcome；
3. **Control**：MPC/search 使用该模型是否比 current-state-only baseline 提高真实 success。

Negative controls：random predictor、shuffled action labels、frozen representation、same planner budget without model。

对应最小实现：[`code/minimal/world_model_mpc.py`](../../code/minimal/world_model_mpc.py)。

## 30.28 研究问题

1. Task-sufficient world state 应保留哪些变量，哪些像素/纹理可以主动丢弃？
2. Action-conditioned JEPA/latent model 与 generative video model 在 contact-rich control 上谁更有效，为什么？
3. World model 是否应预测 uncertainty / alternative futures，而不是单一 deterministic future？
4. Planning horizon 应由 model confidence 自适应缩短吗？
5. 如何证明 world model 对 policy 的作用不是 auxiliary regularization，而是真正 counterfactual reasoning？
6. Continual robot 的 world model 怎样在线更新而不破坏已经可靠的 dynamics knowledge？
""",
    31: r"""
## 31.17 Generative-World Failure Taxonomy

### Photorealism–control gap

更高 FID/visual quality 不保证 pose/contact/dynamics 更准确。生成世界必须接受 task-state 与 intervention tests。

### Action conditioning weak or post-hoc

视频模型主要按视觉 prior 生成，robot action 只产生轻微变化，无法支撑 counterfactual planning。

### Temporal smoothness hides conservation violations

画面连续但物体穿透、质量/动量/接触关系不合理；人眼观感不能替代 physical metrics。

### Synthetic-data feedback loop

模型生成的数据训练下一代模型，错误模式可能被不断自我放大。需要真实 anchor data 与 provenance。

### World generation too slow for receding-horizon control

高质量视频生成耗时远高于 control cycle，最终只能用于 offline data augmentation 而非 online planning。

## 31.18 研究问题

1. World foundation model 最应该优化 pixel likelihood、latent predictive sufficiency，还是 downstream control value？
2. 如何建立 physical consistency metric，捕获 contact、support、occlusion、object permanence 与 action causality？
3. 生成模型用于 synthetic robot data 时，哪些 error 会被 policy 放大而不是平均掉？
4. Neural simulator 与 classical physics simulator 应如何 hybrid：哪些变量由物理求解，哪些由生成模型补全？
5. Online world generation 要进入真实 MPC，需要怎样的 latency/uncertainty interface？
""",
    32: r"""
## 32.22 研究问题

1. Manipulation generalization 的主要瓶颈是 visual semantics、3D geometry、contact dynamics 还是 recovery data？
2. Grasp/placement policy 应输出 pose、trajectory、contact mode 还是 object-centric effect？
3. 对 deformable/articulated objects，object-centric representation 需要怎样表示 hidden state 与 topology change？
4. Long-horizon manipulation 中，高层 skill composition 与低层 continuous policy 的最佳边界在哪里？
5. Failure/recovery demonstrations 的 marginal value 是否高于继续收集更多成功 demonstration？
6. 同一 manipulation task 中，force/tactile 信息应进入 foundation policy 还是独立高速 residual controller？
""",
    35: r"""
## 35.26 Humanoid / Whole-Body Failure Taxonomy

### Task success with hidden balance controller

VLA 给出手部/身体目标，但稳定性来自独立 locomotion/WBC；若不披露接口，会错误归因“VLA 学会了平衡”。

### Motion-tracking success without task robustness

高 tracking reward 不代表面对外力、未知地形、moving camera 与 manipulation contact 时仍稳定。

### Upper-body competence breaks locomotion

手臂大幅动作改变 centroidal dynamics；把 locomotion 与 manipulation 独立训练后简单拼接可能产生耦合失败。

### Simulator contact exploit

脚底/手部接触策略可能利用 solver artifact，真机出现 foot slip、impact 或 self-collision。

### Whole-body action latency

高维 action chunk 推理慢，几十毫秒 stale command 对 balance 比桌面机械臂更危险。

## 35.27 研究问题

1. Humanoid foundation model 应直接输出 joint target、WBC task、motion latent 还是 contact schedule？
2. Locomotion 与 manipulation 的共享 representation 应在哪里发生，才能兼顾稳定性与语义任务？
3. Human video 对 whole-body policy 的主要贡献是 motion prior、task semantics 还是 scene coverage？
4. Moving-head perception 与 body motion 如何共同进入 state estimation，避免视觉 ego-motion 被误认为 object motion？
5. Whole-body VLA 的实时 deadline 应怎样定义并进入 benchmark？
""",
    36: r"""
## 36.20 Human / Multi-Robot Failure Taxonomy

### Human intent misread with high confidence

语言/gesture ambiguity 被 policy 当确定指令执行；系统缺少 clarification / consent state。

### Coordination protocol hidden in training distribution

多机器人看似会协作，实际角色固定、start pose 固定；交换 robot role 后崩溃说明没有学到 general coordination。

### Communication delay / packet loss

集中式 multi-agent policy 在理想网络有效，真实 Wi-Fi/edge network 下 stale teammate state 导致碰撞或重复工作。

### Responsibility ambiguity

失败后无法区分 perception、planner、robot A、robot B 或 human instruction 的责任，导致 recovery strategy错误。

### Safety/social norm outside reward

task success 高，但运动路径让人不适、抢夺物体、侵犯 personal space；interaction metric 必须超出任务完成率。

## 36.21 研究问题

1. Human–robot interaction 中 uncertainty 何时应触发 clarification，而不是自主猜测？
2. Multi-robot coordination 应共享全局 world model，还是只交换 task-relevant messages？
3. 通信 bandwidth / latency 如何作为算法变量进入 benchmark，而不是固定理想条件？
4. heterogeneous robots 的 role assignment 能否根据 morphology/capability 在线重规划？
5. 如何定义人机协作的 safety / trust metric，使其不被 task success 掩盖？
""",
    40: r"""
## 40.22 Platform / Simulation Failure Taxonomy

### Environment version drift

同名 task 在 asset、physics parameter、success detector 或 controller 更新后已不是同一个 benchmark。必须固定 commit 与 asset hash。

### Headless/render mismatch

GPU compute 正常不代表 Vulkan/RTX render path 正常；视觉任务可能悄悄退到 software renderer 或不同 camera pipeline。

### Physics-step / control-step confusion

sim 以 1 kHz physics、20 Hz policy、50 Hz controller 运行时，substep/decimation 配错会改变真实 dynamics。

### Reset leakage

reset 过程留下上一 episode state、cache、random seed 或 object pose pattern，造成异常高 success。

### Simulator-specific observation shortcut

segmentation ID、perfect state、deterministic lighting 等训练时可见信号，真机不存在。

## 40.23 最小实验：Platform Doctor + Cross-Simulator Slice

对同一最小 task 固定 policy/input-output convention，建立 doctor：

```text
GPU compute
renderer / camera
physics dt
control dt
asset hash
seed determinism
joint/action units
contact/friction sanity
trajectory logging
```

随后在两套 simulator 或两组 physics parameter 上执行相同 action sequence，比较 state/contact divergence。目标不是证明 simulator 一致，而是量化**哪些差异足以改变算法结论**。
""",
    43: r"""
## 43.27 Deployment Failure Taxonomy

### Deadline miss

平均 inference latency 合格，但 P99 超过 control deadline，造成周期性 stale action 与 queue buildup。

### Clock drift / timestamp-domain mismatch

camera、robot controller、GPU host 使用不同 clock，简单减 timestamp 得到错误 latency，进而错误对齐 observation/action。

### Queue backpressure

producer 比 consumer 快，系统不是掉帧而是越来越旧；必须显式定义 drop-oldest / drop-newest / latest-only 策略。

### Silent fallback

TensorRT/CUDA/renderer/driver 出错后系统退回 CPU 或低性能路径，功能仍运行但实时约束已破坏。

### Safety layer masks model regression

policy 变差但 watchdog 不断拦截，最终“无事故”；若不报告 intervention rate，会把 safety shield 的功劳算给模型。
""",
    45: r"""
## 45.23 Safety / Reliability Failure Taxonomy

### High average success, catastrophic tail

99% success 仍可能每 100 次出现一次不可接受碰撞。Safety 需要 tail-risk / severity，而不是只看平均失败率。

### Detector blind spot

系统只会恢复“自己能检测”的 failure。未检测错误不会进入 recovery-rate denominator。

### False-positive safety stop

shield 过度保守导致机器人频繁停止、人工接管，安全但不可用。必须同时报 false stop / intervention burden。

### Distribution-shifted safety model

OOD 时 policy 与 safety detector 同时失准；不能假设外部 shield 永远比 policy 更可靠。

### Recovery creates secondary hazard

一次 grasp failure 后自动 recovery 可能撞到人、其他机器人或已移动物体。Recovery 本身也需要 safety verification。

## 45.24 研究问题

1. General-purpose robot 的 risk metric 应如何同时编码概率与伤害 severity？
2. Learned safety critic 与 model-independent CBF/WBC constraint 应怎样分工？
3. Human intervention 何时算失败、何时算系统合理的 uncertainty management？
4. 如何评价“安全但不可用”和“高效但风险高”之间的 Pareto frontier？
5. Continual-learning robot 更新 policy 后，哪些 safety property 必须重新验证，哪些可以 compositional reuse？
""",
    46: r"""
## 46.24 研究问题

1. 一个 architecture claim 的最小充分实验是什么，如何避免一开始就跑最大 benchmark？
2. 当 data/model/controller 同时变化时，怎样设计 factorial ablation 或 intervention 才能获得 mechanism attribution？
3. Negative result 应如何记录，使未来工作能缩小 hypothesis space，而不是重复同一失败？
4. 机器人论文的 reproduction package 应至少保存哪些 raw logs、assets、firmware、calibration 与 failure videos？
5. 如何避免 benchmark overfitting：一个 idea 在多少 task family / embodiment / physics slice 上存活，才值得称为 general mechanism？
6. 何时应该优先发表 measurement / benchmark / dataset contribution，而不是强行包装成新模型？
""",
    49: r"""
## 49.28 Frontier Failure Taxonomy

### Demo frontier mistaken for scientific frontier

最新公司 demo 可能代表工程整合能力，但缺少可控 ablation/独立复现；不能自动当作已解决科学问题。

### Version chasing

每次新 checkpoint 发布就新增章节，会让教材结构随品牌漂移。应追踪长期问题轴：memory、experience、world model、whole-body、cross-embodiment、safety、continual development。

### Benchmark saturation illusion

某 benchmark 接近饱和，可能只是 task narrow / reset easy / controller strong，而不代表 open-world physical intelligence 接近解决。

### Scaling substitutes for mechanism understanding

更大数据/模型继续提升，但没有解释 failure boundary；研究可能得到产品能力却失去可累积的机制知识。

### Open-source lag

前沿闭源系统与开放研究能力存在时间差。教材应明确证据等级，避免把不可验证 claim 写成机制事实。

## 49.29 最小实验：Frontier Claim Stress Test

任选一个 2026 新 claim，把品牌名删除后写成可检验句：

```text
Claim
→ required hidden capability
→ observable consequence
→ strongest alternative explanation
→ minimal negative control
→ task / embodiment / physics slice
→ evidence needed to accept or reject
```

然后只做最小实验区分“新机制”与“更多 data/compute/system integration”。如果无法提出能推翻 claim 的实验，这个 research question 还不够具体。
""",
    50: r"""
## 50.20 最小实验：从一条 Failure Note 生成研究项目

任选一次真实/仿真失败，强制只用 1–2 天预算完成：

```text
1. raw failure replay
2. root-cause candidate tree
3. two competing hypotheses H1/H2
4. one discriminating intervention
5. minimal implementation
6. all-trial result + failure slice
7. update hypothesis tree
```

例如“VLA 抓取遮挡物失败”不要直接改网络，而先比较：

```text
H1: representation 看不到目标几何
H2: representation 足够，但 policy 没有主动换视角
```

用 oracle view / oracle geometry 与 active-view intervention 就能比“训练一个更大 VLA”更快区分机制。独立研究能力首先体现在**选择正确实验**，而不是把所有可能性都并行 brute-force。
""",
}


def target_path(part: int) -> Path:
    matches = sorted(CHAPTER_DIR.glob(f"{part:02d}-*.md"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one chapter for Part {part}, found {matches}")
    return matches[0]


def markers(part: int) -> tuple[str, str]:
    return (
        f"<!-- CHAPTER-ENRICHMENT-R3-P{part:02d}:START -->",
        f"<!-- CHAPTER-ENRICHMENT-R3-P{part:02d}:END -->",
    )


def apply(part: int, body: str) -> bool:
    path = target_path(part)
    text = path.read_text(encoding="utf-8")
    start, end = markers(part)
    block = f"\n{start}\n{body.strip()}\n{end}\n"

    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip("\n")
        new_text = before + block + ("\n" + after if after else "")
    elif SOURCE_START in text:
        before, after = text.split(SOURCE_START, 1)
        new_text = before.rstrip() + block + "\n" + SOURCE_START + after
    else:
        new_text = text.rstrip() + block

    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    changed = []
    for part, body in ENRICHMENTS.items():
        if apply(part, body):
            changed.append(part)
    print(f"Applied round-3 chapter enrichments to Parts: {changed or 'none (already synchronized)'}")


if __name__ == "__main__":
    main()
