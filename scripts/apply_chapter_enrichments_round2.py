#!/usr/bin/env python3
"""Second curated enrichment batch for all remaining 4/6 chapters.

The audit dimensions are not treated as cosmetic checkboxes. Each insertion adds
the specific missing scientific layer: system dataflow, failure analysis,
minimal experiment, mathematical framing, or explicit research questions.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
SOURCE_START = "<!-- CHAPTER-SOURCE-MAP:START -->"

ENRICHMENTS: dict[int, str] = {
    0: r"""
## 0.10 从“智能模型”到物理闭环的数据流

一个最小 embodied system 必须能把信息与物理作用连成闭环：

```text
physical world
→ sensor transduction
→ timestamped observation
→ state / belief / representation
→ task context / memory
→ policy / planner
→ action representation
→ IK / controller / safety layer
→ actuator
→ changed physical world
→ new observation
```

因此一个模型即使在离线 benchmark 上“理解场景”，只要它没有通过 action 改变世界并利用反馈修正，就还没有覆盖 embodied intelligence 的完整对象。

更精确地，闭环可以写为：

\[
o_t\sim p(o\mid x_t),\qquad
b_t=U(b_{t-1},o_t,a_{t-1}),
\]

\[
a_t\sim\pi(a\mid b_t,g,m_t),\qquad
x_{t+1}\sim p(x'\mid x_t,a_t).
\]

身体、传感器、控制频率、delay 与环境 dynamics 都进入这个系统，而不是网络外部的“工程细节”。

## 0.11 研究问题

1. 什么能力必须通过真实 closed-loop interaction 才能验证，离线 video/language benchmark 原理上无法证明？
2. Embodiment 提供的是限制、inductive bias、额外计算，还是三者同时存在？
3. 当同一 policy 换一个身体性能骤降时，应该把问题归因 representation、action interface 还是 controller？
4. General-purpose robot 的“通用”应按 object/scene/task/physics/embodiment/time 哪些轴定义？
5. 一个长期 physical agent 的最小内部状态是什么：belief、world model、memory，还是可在线生长的结构？
""",
    6: r"""
## 6.19 机电层 Failure Taxonomy

### Encoder / zero offset 错

视觉和 policy 都正确，但 joint zero、gear ratio 或 direction sign 错会让所有高层动作系统性偏移。应先做低层 joint-space sanity test。

### Command saturation

网络输出可能在归一化空间合理，但经过 gear/motor/driver 后触发 position、velocity、torque 或 current limit。clip 后的真实 action 与训练 action 已不是同一个分布。

### Backlash / compliance

同一 encoder position 不代表 end-effector 真正处于同一 pose。高精度 manipulation 中，传动间隙与结构柔性会形成 hysteresis。

### Communication jitter / packet loss

CAN/EtherCAT/USB/ROS path 的 jitter 会改变有效 control period。平均 1 ms 不代表 P99 也安全。

### Thermal / power derating

长时间运行后 actuator capability 会变化。只在冷机状态测试的 policy 可能产生典型 time-dependent distribution shift。

## 6.20 最小实验：高层 policy 不变，只改变机电链

对同一 joint target trajectory，依次注入：

```text
encoder zero bias
gear backlash
velocity saturation
20–100 ms command delay
random packet drop
motor-strength decay
```

记录：tracking RMSE、phase lag、overshoot、task success、safety intervention。然后固定这些 corruption，用更强网络替换 policy；若 failure 几乎不变，就证明瓶颈在机电/控制链而不是模型容量。

实验必须同时保存 requested command 与 actually applied command，不能只保存 policy output。
""",
    7: r"""
## 7.19 刚体几何在软件栈中的真实数据流

```text
camera pixels / depth
→ point / pose in camera frame
→ T_base_camera / T_world_base
→ object pose in world/base frame
→ desired EE pose
→ pose error on SE(3)
→ IK / controller
```

每一条边都应带：

```text
from_frame
to_frame
timestamp
rotation convention
units
```

一个 4×4 matrix 的 shape 无法告诉你它表示 `world←camera` 还是 `camera←world`。因此 geometry API 最好把 frame semantics 写进类型/变量名，而不是靠注释记忆。

## 7.20 最小实验：Frame-Convention Fuzz Test

随机生成一条变换链：

\[
{}^WT_B,\quad {}^BT_C,\quad {}^CT_O,
\]

验证：

\[
{}^WT_O={}^WT_B{}^BT_C{}^CT_O
\]

以及所有 inverse / round-trip identity。随后故意注入四类 bug：

1. 乘法顺序反转；
2. quaternion `xyzw/wxyz` 混淆；
3. degree/radian 混淆；
4. 使用旧 timestamp 的 extrinsic/base pose。

要求测试在进入 policy/IK 前就失败。目标不是“会算 SE(3)”，而是让 frame bug 在系统边界被机器检测。
""",
    9: r"""
## 9.24 Contact / Dynamics Failure Taxonomy

### Contact mode 预测错

free-space、sticking、sliding、impact 属于不同 dynamics regime。把它们平均成一个 smooth model 往往在接触切换处产生最大误差。

### Friction / compliance mismatch

几毫米 pose error 可能仍成功，但摩擦锥、接触刚度或物体变形预测错会直接改变 grasp/slip outcome。

### Force closure 与实际可执行性脱节

几何上 force-closure 的 grasp 仍可能因 actuator limit、approach collision、finger thickness 或 calibration error 无法执行。

### Dynamics parameter identifiability

仅从普通 successful trajectories 可能无法辨识 mass/friction。若 action excitation 不充分，多组参数都能解释 observation。

### Simulator contact artifact

solver timestep、contact regularization、mesh/collision geometry 会产生 simulator-specific strategy；高 sim reward 不等于真实接触策略正确。

## 9.25 最小实验：同一视觉状态，不同物理参数

固定 object geometry 与图像，构造不同：

```text
mass
friction coefficient
center of mass
contact compliance
```

让 policy / planner 接收相同视觉输入，测试加入 proprioception/tactile/system-ID 后能否区分。记录 grasp success、slip onset、peak force、recovery。

关键 negative control：保持视觉完全相同，只改变不可见 dynamics；若所谓“视觉物理理解”无法适配，说明 semantic/geometry feature 不能替代 physical state estimation。
""",
    28: r"""
## 28.15 Memory Failure Taxonomy

### Stale memory

环境已经改变，但旧 episodic/spatial memory 仍被检索并覆盖当前 observation。长期记忆必须具有时间、置信度与失效机制。

### Retrieval shortcut

系统看似“会长期任务”，实际只是通过相似场景检索训练 episode。必须用 novel layout / compositional negative control 区分记忆与模板匹配。

### Memory pollution

一次错误识别或失败操作被长期写入，后续 repeatedly retrieved，形成 self-reinforcing error。

### Catastrophic overwrite

新场景经验覆盖旧 task knowledge；或者为了避免遗忘而完全冻结 memory，导致无法适应。

### Context-length illusion

把更多历史 frame 直接塞入 Transformer 并不等于 memory system；需要验证信息在数分钟后是否仍可被选择性写入、检索与更新。

## 28.16 研究问题

1. Robot memory 应存 raw observation、latent state、event、language summary 还是 learned mechanism？
2. 写入策略怎样权衡 information value、storage cost 与未来 retrieval probability？
3. 错误 memory 如何被现实 observation 反证、降权或删除？
4. Episodic memory 与 world-model state 的边界在哪里：一个记录过去，一个预测未来，还是可以共享表示？
5. Lifelong robot 如何证明“记住了经验”，而不是 checkpoint 参数里静态编码了训练场景？
""",
    33: r"""
## 33.18 Bimanual / Dexterous Failure Taxonomy

### 两臂各自正确但整体失败

独立 arm policy 都能到达目标，却违反 relative pose、object rigidity 或 shared workspace constraint。双臂协调的单位应是**joint interaction**而不是两个 success 的乘积。

### Contact assignment 错

灵巧手多个 fingertip 同时接触时，哪个 finger 承担 normal/tangential force 会随物体姿态变化；固定 contact role 很脆弱。

### Tactile latency / saturation

触觉高频并不自动有用。若 sensor pipeline 降采样到 VLA rate 或发生 saturation，真实 reflex signal 已被抹掉。

### Symmetry / hand identity shortcut

左右臂/手在 geometry 上近似对称，但 camera、joint limit、task role 不对称。简单共享权重可能把真实 asymmetry 错当 nuisance。

### Demonstration synchronization

双臂 teleoperation 的左右时间错位几十毫秒，就可能让模型学到错误 handover/coupling phase。

## 33.19 研究问题

1. 双臂 policy 应在 world frame、object frame 还是 inter-arm relative frame 中生成动作？
2. 高频 tactile controller 与低频 VLA 的最优分层边界在哪里？
3. Dexterous hand 的 action dimension 很高时，diffusion/flow 的优势来自 multimodality 还是 temporal smoothness？
4. 如何设计 benchmark，把“单手能力强”与“真正 coordination 强”分开？
5. 对 handover/cable/deformable tasks，哪些 failure 必须靠 force/tactile 才能在视觉失败前被检测？
""",
    37: r"""
## 37.19 Cross-Embodiment Failure Taxonomy

### Padding illusion

把所有 action/state pad 到相同维度只统一了 tensor shape，没有统一 joint meaning、frame、range 与 controllability。

### Robot-ID shortcut

模型可以先识别 robot ID，再调用彼此隔离的子策略，在已见机器人上表现很好，却没有学到可迁移结构。

### Controller confound

不同 embodiment 配不同低层 controller，最终 success 差异可能来自 controller quality 而非 foundation policy transfer。

### Morphology extrapolation

训练只覆盖 6–7 DOF arms，却宣称“cross-embodiment”，并不能支持腿式、人形或不同 hand topology 的 unseen morphology。

### Shared semantics 不完整

“move end effector +x”在不同 base/frame/tool definition 下含义不同。canonical action 必须带 reference frame 与 embodiment kinematics。

## 37.20 研究问题

1. Cross-embodiment 的最小共享对象是 task-space effect、contact graph、kinematic graph 还是 learned latent operator？
2. unseen morphology test 应控制哪些因素，才能排除视觉/任务相似性带来的 shortcut？
3. morphology encoder 是否应该显式输入 URDF/graph/joint axis/limits，而不是只给 robot ID？
4. 一个 policy 在多机器人数据上提升，怎样测出 transfer 是正迁移还是 capacity-sharing regularization？
5. 是否存在真正 embodiment-agnostic 的中枢表示，同时允许不同身体通过在线 system identification 生长自己的 interface？
""",
    38: r"""
## 38.23 Continual Learning Failure Taxonomy

### Catastrophic forgetting

新任务性能提高，但旧任务快速下降。只报当前 task success 会把 continual learning 退化成 sequential fine-tuning。

### Stability–plasticity collapse

过度保护旧知识导致新任务学不进去；过度 plastic 则旧能力消失。两端都可能让平均指标看起来尚可。

### Hidden replay leakage

若方法保存大量旧 raw data，应把 memory budget 与训练成本计入比较；否则“无遗忘”可能只是无限 replay。

### Capacity growth without accounting

动态增加 module/parameter 可以降低 interference，但必须报告参数、compute、routing 与 retrieval cost 随时间的增长率。

### Task-boundary assumption

现实机器人通常不知道“现在进入 Task B”。依赖显式 task ID / phase boundary 的算法不等于 lifelong agent。

## 38.24 研究问题

1. 不提供 task boundary 时，机器人如何检测 distribution/mechanism change 并决定更新哪些结构？
2. 参数增长、memory replay、synaptic regularization 与 modular routing 的长期 compute scaling 谁更合理？
3. 遗忘是否永远应该避免，还是机器人需要主动删除失效规律与危险 shortcut？
4. Continual learning 的单位应该是 task、scene、skill、mechanism 还是一生连续 interaction stream？
5. 如何把“持续学习”从 benchmark sequence 扩展成关机/standby 后仍可恢复的长期实体状态？
""",
    39: r"""
## 39.19 最小实验：结构生长必须赢过等预算静态模型

构造持续到来的场景流 \(S_1\to S_2\to\cdots\to S_K\)，比较：

```text
A. 固定容量模型
B. 定期全量扩宽网络
C. replay + 固定结构
D. 条件模块 / routing
E. 提出的自生长与遗忘机制
```

所有方法必须匹配累计：

- 参数预算；
- FLOPs / wall-clock；
- replay bytes；
- interaction count；
- energy / deployment downtime。

评价不只看 final average success，而要画：

\[
C(t)=\bigl(\text{capability},\text{retention},\text{plasticity},\text{size},\text{compute}\bigr).
\]

最关键 negative control：如果把“何时新增模块”改成随机但保持相同参数增长，性能几乎不变，则所谓结构自进化机制没有被证明。

## 39.20 研究问题

1. 什么信号足以触发结构生长：prediction error、intervention surprise、gradient conflict、causal novelty 还是长期 utility？
2. 新结构应复制旧模块、随机初始化，还是由已有 mechanism composition 生成？
3. 遗忘应删除参数、连接、memory，还是只降低 routing probability？
4. 如何证明结构变化学到的是新规律，而不是给每个 scene 单独记忆一个 module？
5. 能否设计不区分 train/inference 的持续更新系统，同时保持安全、可回滚和长期稳定？
""",
    43: r"""
## 43.25 最小部署实验：把 latency 当成可控变量

固定同一个 checkpoint 和 controller，人为注入不同 observation-to-command delay：

```text
0 ms / 20 ms / 50 ms / 100 ms / 200 ms
```

再分别加入 jitter 与 burst packet loss。记录：

- task success；
- tracking / contact error；
- stale-action ratio；
- queue depth；
- P50/P95/P99 cycle time；
- watchdog / safety intervention。

对 chunk policy 再比较 blocking、async replacement、RTC-like continuity mechanism。只要 model 完全不变而闭环 success 显著变化，就直接证明 deployment runtime 是算法系统的一部分。

## 43.26 研究问题

1. VLA 论文应把 observation-to-command P99 latency 作为标准指标吗？
2. 当 GPU inference 与 1 kHz servo loop 分离时，哪一层负责 state extrapolation 与 stale-command rejection？
3. Edge/on-device model 的价值应按参数量、平均 latency，还是 worst-case deadline miss probability 衡量？
4. 如何把 watchdog、安全 PLC、E-stop 与 learned policy 的 intervention 统一记录进 evaluation protocol？
5. 多机/多 GPU 系统中，clock synchronization error 在什么量级开始影响 action learning 与真实控制？
""",
    47: r"""
## 47.19 Transformer-Induced Failure Taxonomy

### Tokenization destroys geometry

把连续 pose/action 离散成 token 可以复用 LM machinery，但 quantization boundary 与坐标系结构不会因此消失。

### Quadratic context cost 与实时性冲突

长视觉历史、memory、multi-view 让 token 数快速增长；attention FLOPs 与 KV cache 会直接进入 robot latency budget。

### Frequency mismatch

语言 reasoning 可能只需 1–5 Hz，motor correction 却需要几十到上千 Hz。单一同步 Transformer loop 往往在 compute 或控制上不合适。

### Attention ≠ causal use

高 attention weight、可解码 feature 或语言 explanation 都不能证明信息对 action 有因果作用。需要 masking/shuffling/intervention。

### Uniform architecture erases physical modularity

将 perception、memory、world dynamics、action generation 全做成同一种 token mixer，可能牺牲各子问题天然不同的 state/update timescale。

## 47.20 研究问题

1. 哪些具身变量天然适合 token sequence，哪些更适合 continuous field、graph、state-space 或 dynamical system？
2. Transformer 在 VLA 中真正不可替代的是 multimodal fusion、in-context conditioning，还是 scaling infrastructure？
3. 若替换 attention 后保持 data/parameter/compute 等预算，哪些 capability 会真正消失？
4. 多时间尺度机器人中，是否应该让 semantic model、world model、motor system 使用完全不同的 architecture family？
5. Post-Transformer 研究应以更低 loss 为目标，还是以更好的 physical invariance、online plasticity 与 real-time efficiency 为目标？
""",
    48: r"""
## 48.21 数学化失败：公式多不等于机制清楚

### 把 notation 当 explanation

给每个模块写一个符号，并没有解释它为什么存在、满足什么 invariant、在什么条件下会失败。

### Optimization objective 与 scientific objective 不同

训练 loss 可下降，但研究真正关心的是 task success、identifiability、stability、transfer 或 causal mechanism。二者必须显式连接。

### 过度连续化

Contact、mode switch、tool change、memory write/delete 等含离散事件。强行用光滑 ODE 描述全部系统可能隐藏关键 hybrid dynamics。

### 不可辨识模型也能拟合数据

\[
P_{\theta_1}(O)=P_{\theta_2}(O)
\]

不代表两个模型在 intervention 下相同。纯 prediction loss 无法自动发现“真实规律”。

### 数学保证建立在错误假设上

Lyapunov、convexity、observability 等结论都依赖假设。机器人最危险的情况是 theorem 正确，而真实 deployment 不满足模型假设。

## 48.22 研究问题

1. 下一代具身架构最应该显式编码哪些 invariant：SE(3)、contact、conservation、causal locality、morphology graph 还是 time-scale separation？
2. 能否从 interaction 中自动发现新的 state variable / constraint，而不是预先固定网络宽度与 latent dimension？
3. 如何把 identifiability 变成 active exploration objective，让机器人主动做最能区分 competing mechanisms 的实验？
4. 结构生长/遗忘能否被写成优化之外的离散结构动力学，而不只是在固定网络上更新权重？
5. 什么数学对象最适合描述“不分训练和推理、持续与世界交互更新”的长期 physical agent？
""",
    50: r"""
## 50.18 独立研究的最小闭环

研究成长可以抽象成一个反复收缩 uncertainty 的闭环。设候选机制集合为 \(\mathcal H_t\)，每次实验 \(e_t\) 产生证据 \(D_t\)：

\[
\mathcal H_{t+1}=\operatorname{Update}(\mathcal H_t,D_t,e_t).
\]

好的研究不是让 hypothesis 数量无限增加，而是主动选择最有区分力的实验：

\[
e_t^*=\arg\max_e I(H;D\mid e)-\lambda C(e),
\]

其中 \(C(e)\) 是时间、算力、真机风险与机会成本。

因此个人科研飞轮也应是：

```text
read / reproduce
→ identify unresolved mechanism
→ write falsifiable hypotheses
→ choose minimal discriminating experiment
→ inspect failures, not only averages
→ update theory
→ scale only after mechanism survives
```

这比“连续追最新论文 + 堆更多实验”更接近独立研究者的工作方式。

## 50.19 研究问题

1. 怎样判断一个 idea 已经具体到可以被证伪，而不是一句愿景？
2. 什么时候应该复现 baseline，什么时候应该直接构造最小机制实验？
3. 如何把 negative result 变成对 hypothesis space 的有效收缩，而不是“实验没跑通”？
4. 一篇论文的核心贡献应优先是新指标、新数据、新系统、新机制还是新理论；不同类型需要什么证据？
5. 如何建立自己的 Architecture Research Program，使连续多篇工作共享可累积的问题树，而不是每篇追一个热点？
6. 当计算资源足够大时，如何防止“能跑很多实验”反而降低实验设计质量？
""",
}


def target_path(part: int) -> Path:
    matches = sorted(CHAPTER_DIR.glob(f"{part:02d}-*.md"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one chapter for Part {part}, found {matches}")
    return matches[0]


def markers(part: int) -> tuple[str, str]:
    return (
        f"<!-- CHAPTER-ENRICHMENT-R2-P{part:02d}:START -->",
        f"<!-- CHAPTER-ENRICHMENT-R2-P{part:02d}:END -->",
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
    print(f"Applied round-2 chapter enrichments to Parts: {changed or 'none (already synchronized)'}")


if __name__ == "__main__":
    main()
