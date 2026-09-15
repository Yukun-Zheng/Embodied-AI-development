#!/usr/bin/env python3
"""Apply curated research-layer enrichments to selected chapters.

This script preserves the existing manuscript and inserts a marked, idempotent
block immediately before the generated source-map fallback (or at EOF if the
chapter has authored sources). Each block targets a concrete structural gap from
`scripts/audit_chapters.py`: failure analysis, experiments, and/or explicit
research questions.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
SOURCE_START = "<!-- CHAPTER-SOURCE-MAP:START -->"

ENRICHMENTS: dict[int, str] = {
    3: r"""
## 3.16 从“不确定”到决策：Uncertainty 的闭环接口

不确定性只有进入 action selection 才有系统价值。设机器人维护 belief

\[
b_t(x)=p(x_t=x\mid o_{\le t},a_{<t}),
\]

决策不应只依赖 posterior mean，而应比较**信息价值、任务收益与风险**：

\[
a_t^*=\arg\max_a\;\mathbb E_{x\sim b_t}[R(x,a)]-\lambda\,\mathrm{Risk}(a,b_t).
\]

如果还允许主动获取观测，则可以加入信息项：

\[
a_t^*=\arg\max_a\;\mathbb E[R]-\lambda_r\mathrm{Risk}+\lambda_i I(X;O_{future}\mid a).
\]

这把 calibration、active perception、human handoff 和 safe stop 统一为同一个问题：**belief 如何改变行为。**

### 研究问题

1. VLA 的 token probability / diffusion variance / ensemble variance，哪一种最接近真实 task-failure probability？
2. Epistemic 与 aleatoric uncertainty 在真实机器人上怎样通过 intervention 被区分，而不是只靠模型结构命名？
3. Risk–coverage curve 是否比单一 success rate 更适合评价“会说不知道”的机器人？
4. 当 perception uncertainty 与 action uncertainty 同时存在时，应该先主动看、慢速执行、还是直接请求人类？
5. 一个 uncertainty head 若不改变 policy/executor，是否应被视为系统能力的一部分？
""",
    4: r"""
## 4.16 Model Mismatch：最优解只对所写问题最优

优化器返回的 \(x^*\) 只对**当前 objective、constraint 与 dynamics model**有意义：

\[
x^*=\arg\min_x f_{\hat\theta}(x)\quad\text{s.t.}\quad g_{\hat\theta}(x)\le0.
\]

如果真实系统参数是 \(\theta\neq\hat\theta\)，则 solver 数值收敛并不保证真实闭环最优。机器人里最典型的是：friction、payload、delay、contact mode 或 actuator saturation 被错误建模。

因此必须把两种误差分开：

```text
optimization error: 没有把已定义的问题解好
modeling error:      把错误的问题解得非常好
```

## 4.17 常见失败

### Objective hacking

一个 reward/cost 可以被 policy 以设计者没预期的方式满足。仿真 reward 上升不代表真实任务语义改善。

### Constraint 只在 nominal trajectory 成立

trajectory optimizer 在预测模型中满足 collision/force bound，但 tracking error 与 model mismatch 会让真实轨迹越界。需要 margin、robust constraint 或 feedback correction。

### Open-loop optimality 冒充 feedback robustness

一次求出的长 horizon trajectory 可能在 nominal model 上最优，但 disturbance 后没有 recovery。必须比较 open-loop plan 与 receding-horizon / feedback execution。

### 非凸 solver 的“成功”依赖 initialization

同一 target 不同 initial guess 得到不同 local optimum。只汇报最好结果会隐藏 basin-of-attraction 问题。

### Learned optimizer 改变了问题而不自知

神经网络可能 amortize 求解，但如果训练数据隐式改变 constraint distribution，不能只比较 wall-clock time 就宣称“替代了优化”。

## 4.18 研究问题

1. Learned policy、MPC 与 trajectory optimization 在相同 model/data/compute budget 下，性能差异究竟来自哪里？
2. Foundation policy 的 action expert 是否可以解释为 amortized optimizer；若可以，它隐式优化的 objective 是什么？
3. 对 contact-rich manipulation，robust MPC、online system identification 与 experience-based policy adaptation 应怎样分工？
4. 如何设计 benchmark，把 optimizer failure、model mismatch 与 controller tracking failure 分开记录？
5. Flow-matching action generator 的 ODE integration error 在什么条件下会真正影响 physical control，而不是仅影响离线 likelihood？
""",
    23: r"""
## 23.23 VLA 谱系的 Failure Taxonomy

这一阶段的系统容易被同一个“success rate”掩盖不同失败源：

```text
semantic failure
→ instruction / object grounding 错

representation failure
→ 看见了对象但缺 precision / geometry

action-interface failure
→ tokenization / normalization / frame 不合适

temporal failure
→ inference latency / stale action

controller failure
→ policy target 合理但 IK / low-level controller 执行失败

data failure
→ train mixture / embodiment / scene coverage 不足
```

如果论文只给最终成功率，无法知道 VLM pretraining、robot data scaling 与 action representation 各自解决了哪一种 failure。

## 23.24 最小受控实验：把“VLA 提升”拆开

固定同一个 robot、task split、vision encoder、controller 与训练步数，只改变一个轴：

```text
A. BC regression head
B. action-token head
C. diffusion head
D. flow head
```

再分别加入：

```text
+ web/VLM pretraining
+ cross-robot data
+ language conditioning
```

要求报告：

- seen-task success；
- novel-object / novel-instruction success；
- action quantization / trajectory error；
- inference latency；
- recovery；
- controller saturation / IK failure。

这比直接比较 RT-2、Octo、OpenVLA 的论文数字更接近因果问题，因为后者的数据、参数量、controller 与 benchmark 通常都不同。

## 23.25 Negative Controls

1. **Shuffled language**：保持视觉与动作数据不变，打乱 instruction，测 language 是否真的被读取；
2. **Frozen/random VLM features**：控制 parameter count，测 web semantic prior 的真实贡献；
3. **Matched robot-data budget**：避免“更多机器人数据”被误写成 architecture gain；
4. **Action de-tokenization oracle**：把量化误差单独隔离；
5. **Same controller**：不同 policy 必须经过同一 IK / low-level controller 才能做 architecture credit assignment。

## 23.26 研究问题

1. VLA 的关键跨越究竟是“语言进入 action”，还是“大规模异质数据终于进入统一 policy”？
2. Web-scale semantic prior 对真实 precision manipulation 的边际贡献在什么任务上接近零？
3. Cross-robot training 学到的是 embodiment-agnostic interaction structure，还是 robot-ID-conditioned mixture of experts？
4. Action tokenization 何时是合理 inductive bias，何时只是复用 LLM 工具链的工程便利？
5. 一个模型能在多个已见 robot 上工作，需要什么额外实验才能支持 unseen-morphology generalization？
""",
    34: r"""
## 34.17 Navigation Failure Taxonomy

### Localization drift

路径规划正确，但 belief pose 漂移，导致 map-relative waypoint 与真实世界错位。应同时画 localization error 与 task failure，而不是只看 SPL。

### Semantic shortcut

ObjectNav policy 可能学到“冰箱常在厨房右侧”等数据集统计，而没有真正建立可更新的 spatial belief。改变 layout 后性能骤降是典型证据。

### Map staleness

动态障碍、开关门、人群移动会使静态 map 过期。系统必须区分 persistent map 与 transient obstacle state。

### Planner–controller mismatch

global path 在几何上可行，但 local controller 受最小转弯半径、加速度、轮胎/底盘约束无法跟踪。

### Memory aliasing

相似走廊/房间产生 perceptual aliasing。单帧视觉 policy 可能反复走回已访问区域，却把它当新位置。

## 34.18 Navigation 的完整闭环接口

```text
RGB / depth / LiDAR / odometry
→ localization + belief
→ metric / semantic / topological memory
→ global goal / frontier selection
→ path / waypoint
→ local collision-aware command
→ base controller
→ physical motion
→ new observation
```

端到端 policy 可以隐藏中间表示，但不能消除这些功能需求。研究者应通过 intervention 判断功能究竟是否存在，例如冻结 memory、注入 pose error、交换地图、移动动态障碍。

## 34.19 研究问题

1. Learned implicit memory 何时比 explicit metric/semantic map 更高效，何时只是更难诊断？
2. ObjectNav/VLN 的 language prior 对真正新布局是帮助还是 shortcut？
3. Mobile manipulation 中 base placement 应由高层 VLA、motion planner 还是 whole-body optimizer 决定？
4. 如何把 localization uncertainty 传播到 learned navigation policy，而不是只把一个估计 pose 当真值？
5. 对家庭机器人，SPL 是否仍是合理主指标，还是应联合 success、human disturbance、time、energy 与 intervention rate？
""",
    41: r"""
## 41.15 Transfer Gap 不应只报一个数字

定义任务指标 \(J\) 后，可写：

\[
G_{transfer}=J_{sim}-J_{real}.
\]

但一个 scalar gap 仍然太粗。更有诊断价值的是按扰动轴分解：

```text
visual gap      → light / texture / exposure
geometry gap    → asset shape / collision mesh / tolerances
dynamics gap    → mass / inertia / friction / damping
sensor gap      → noise / latency / dropped frames
actuation gap   → motor model / backlash / saturation
contact gap     → compliance / deformation / slip
human/world gap → unmodeled agents / long-tail events
```

每一项都应该有可控 intervention，才能判断该增加 randomization、做 system ID、改 simulator，还是收真实数据。

## 41.16 Sim2Real 常见失败

### Randomization 范围越宽越好

错误。过宽分布会把 policy 推向极度保守甚至不可学习的策略；关键是覆盖**真实 posterior**而不是最大化参数范围。

### 只随机视觉却声称解决 reality gap

fine manipulation 失败可能来自 friction/contact/latency，视觉 domain randomization 对这些没有直接作用。

### Simulator success 饱和后继续加算力

当瓶颈是 model bias 时，更多 sim rollout 只会更精确地适配错误 simulator。

### Real fine-tuning 掩盖 zero-shot transfer

如果大量真实数据参与适配，应分别报告 zero-shot sim2real 与 post-adaptation performance，不能把两者合称“sim2real”。

### Digital twin 追求像素真实而忽略 task fidelity

对控制而言，正确的 contact、reachability、latency 可能比 photorealism 更重要。

## 41.17 研究问题

1. Domain randomization 的 distribution 能否由 real-world posterior 在线更新，而不是人工拍脑袋设范围？
2. 哪些 simulator fidelity 维度对 VLA / diffusion policy / locomotion policy 的 sensitivity 不同？
3. World model 生成的 synthetic trajectories 与 physics simulator 数据，分别在哪些 failure mode 上更可信？
4. Real-to-sim reconstruction 是否能形成自动 failure replay：真机失败 → 仿真重建 → counterfactual sweep → 修复？
5. 如何定义 task-sufficient digital twin，使建模预算集中在真正影响 action selection 的变量？
""",
    42: r"""
## 42.19 Dataset Contract：数据也需要可执行规范

一个可复现 robot dataset 不应只给文件格式，还要定义 contract：

```text
observation keys + dtype + shape + unit + frame
state/action semantics + normalization + valid mask
source timestamp + aligned timestamp + interpolation rule
episode boundary + success/failure/abort semantics
robot/calibration/controller/software version
```

训练前可以把这些 contract 写成 machine-checkable schema。这样 action convention 改变、camera 丢帧、时间戳倒序等问题会在 dataset ingestion 阶段失败，而不是训练数天后才从 loss 中猜。

## 42.20 数据价值不等于 Episode 数量

数据的边际价值更接近 coverage：

\[
V(D)\approx f(\text{state},\text{action},\text{object},\text{scene},\text{failure},\text{embodiment coverage}).
\]

重复 10 万次同一简单成功轨迹，未必比 1000 条覆盖 recovery/contact edge case 的数据更有价值。

因此 data flywheel 应优化：

\[
\frac{\Delta \text{capability}}{\Delta \text{collection cost}},
\]

而不是只优化累计小时数。

## 42.21 最小实验：Data QA 能否提前发现训练灾难

构造一份小型 episodic dataset，然后分别注入：

1. camera/action 错位 100 ms；
2. action unit 从 rad 改成 degree 但 metadata 不变；
3. 5% success label 翻转；
4. duplicate episodes；
5. train/test scene leakage；
6. action convention 从 absolute 改成 delta。

要求 data validator 在**不训练模型**的前提下尽量发现问题，并记录哪些只能通过 statistical / downstream test 发现。

再训练一个极小 BC policy，比较每类 corruption 对 offline loss 与 closed-loop success 的影响。尤其关注：哪些 corruption 的 train loss 看起来正常，却让真实控制崩溃。

## 42.22 研究问题

1. 机器人 foundation model 的 scaling law 应按 hours/episodes，还是按独立 state-action coverage / intervention entropy 计量？
2. 如何自动估计一条新 episode 对当前模型的 marginal information value？
3. Failure data 应以多大权重进入 mixture，才能提高 recovery 而不让 policy 过度保守？
4. 跨实验室 dataset mixture 中，action semantics 对齐应靠 canonical action space、embodiment adapters 还是 explicit morphology graph？
5. 数据版本改变后，如何追踪某个 checkpoint 的所有上游 raw episodes、derived transforms 与 annotation versions？
6. 能否把 timestamp/calibration/schema validation 做成机器人数据系统的 CI，像软件测试一样阻止坏数据进入训练？
""",
}


def target_path(part: int) -> Path:
    matches = sorted(CHAPTER_DIR.glob(f"{part:02d}-*.md"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one chapter for Part {part}, found {matches}")
    return matches[0]


def markers(part: int) -> tuple[str, str]:
    return (
        f"<!-- CHAPTER-ENRICHMENT-P{part:02d}:START -->",
        f"<!-- CHAPTER-ENRICHMENT-P{part:02d}:END -->",
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
    print(f"Applied chapter enrichments to Parts: {changed or 'none (already synchronized)'}")


if __name__ == "__main__":
    main()
