# Part 39　Self-Evolving Physical Intelligence

> “自进化”“自我成长”很容易成为不可证伪的宣传词。本章只讨论能够被实验击败的定义。

## 39.1 自进化必须满足什么可证伪条件

一个系统要称为 self-evolving，至少应同时满足：

1. **Autonomous experience acquisition**：不依赖研究者手工持续提供全部训练集；
2. **Capability change**：经验后出现可测新能力；
3. **Retention**：新能力不是以严重遗忘旧能力为代价；
4. **Transfer**：过去学习能帮助未来问题；
5. **Bounded resources**：不能靠无限参数复制伪装成长；
6. **Safety**：自我修改不能突破安全约束。

缺一项时，应使用更准确的词：online fine-tuning、continual learning、architecture search 等。

---

## 39.2 Capability Acquisition

能力不是 benchmark 分数单点。

可定义 capability set：

\[
\mathcal C_t=\{c_1,c_2,\dots\}.
\]

成长意味着：

\[
\mathcal C_{t+1}\supsetneq\mathcal C_t
\]

并在严格新任务上验证。

如果只是同一任务 success 从 80% 到 85%，这是 skill refinement，不一定是新能力产生。

---

## 39.3 Autonomous Practice

agent 自主练习需要闭环：

```text
choose practice target
→ execute
→ evaluate
→ store experience
→ update
→ re-test
```

最大工程难点包括：

- reset；
- safe exploration；
- automatic outcome detection。

没有这三项，自主练习很容易依赖隐藏人工。

---

## 39.4 Self-Generated Goals

goal generator：

\[
g_t\sim G(s_t,M_t,competence_t).
\]

好的 goal 应满足：

- 可执行；
- 有学习价值；
- 不危险；
- 不只是重复已掌握任务。

可用 learning progress 作为选择信号。

---

## 39.5 Curriculum Emergence

不是研究者预写：

```text
先学走路，再学抓取，再学整理
```

而是 agent 根据能力边界形成学习顺序。

可测试：不同随机种子是否出现相似 curriculum structure，还是完全依赖偶然噪声。

---

## 39.6 Failure-Driven Learning

失败是最直接的信息源。

定义 failure set：

\[
F_t=Detect(trajectory_t).
\]

系统根据高频/高代价 failure 分配学习资源。

例如：

```text
slip repeatedly
→ collect tactile episodes
→ learn slip predictor
→ add high-rate correction
```

这才是结构化 growth，而不是盲目扩大模型。

---

## 39.7 Mechanism Discovery

更强目标是从交互中识别可复用规律：

- support；
- friction；
- hinge；
- containment；
- tool leverage。

可表示为 mechanism \(m\)：

\[
s_{t+1}=f_m(s_t,a_t).
\]

如果发现机制后能迁移到未见对象/场景，才比记住 trajectory 更有意义。

---

## 39.8 Compositional Skill Growth

新能力可通过已有 skill 组合：

\[
c_{new}=Compose(c_i,c_j,\dots).
\]

真正开放式成长不能每次新任务都增加一个不可复用 policy。

应测：

- reuse ratio；
- new module count；
- composition depth。

---

## 39.9 Memory–Structure Co-Adaptation

当某类经验频繁被检索，可能值得固化成结构；长期不用的结构可能退回 memory 或被合并。

概念上：

```text
episode memory
→ repeated pattern
→ semantic memory
→ reusable mechanism/module
```

这是比简单 neuron growth 更有意义的结构可塑路径。

---

## 39.10 Policy–World-Model Co-Evolution

policy 决定 agent 去哪里采数据，world model 决定哪些地方“不懂”。

可以形成主动闭环：

\[
a_t=\arg\max_a
\underbrace{R(a)}_{task}
+eta\underbrace{IG(a)}_{learning}.
\]

policy 用 world-model uncertainty 选择有价值交互，新的 experience 又改善 world model。

---

## 39.11 Structure Search vs Structural Plasticity

### Architecture Search

通常在训练阶段搜索，然后冻结。

### Structural Plasticity

部署生命周期中，结构继续改变。

关键差异是时间尺度与触发信号。

如果每次 offline NAS 后部署新模型，不应直接称为“在线结构生长”。

---

## 39.12 Self-Modification 的稳定性问题

自我修改系统存在递归风险：

\[
U_t\text{ changes }U_{t+1}.
\]

必须有：

- versioning；
- rollback；
- regression suite；
- safety invariants；
- canary deployment。

否则一次错误 update 可能永久破坏已有能力。

---

## 39.13 Continual Safety Constraint

无论 agent 怎样学习，都必须满足安全集合：

\[
s_t\in\mathcal S_{safe},\quad \forall t.
\]

安全边界不能完全依赖正在自我修改的 policy 本身。

需要外层稳定 invariant，例如：

- torque/velocity limits；
- collision envelope；
- human proximity rule；
- hardware emergency stop。

---

## 39.14 如何区分真正能力生长与数据记忆

设计五层测试：

1. same instance；
2. new object；
3. new scene；
4. new composition；
5. new embodiment。

如果能力只在 Level 1 成功，可能只是 memorization。

真正 growth 应在至少 3–5 层表现 transfer。

同时做 data leakage audit。

---

## 一套可量化的“成长”指标

### Retention

\[
R=\frac1N\sum_iP_i^{after}/P_i^{before}.
\]

### Forward Transfer

\[
FT=P(new\mid prior\ learning)-P(new\mid scratch).
\]

### Growth Efficiency

\[
GE=\frac{\Delta capability}{\Delta compute+\lambda\Delta params+\mu\Delta data}.
\]

### Autonomy Ratio

\[
AR=1-\frac{human\ intervention\ time}{total\ learning\ time}.
\]

这些指标比“模型变大了多少”更接近发展型智能。

---

## 最小长期实验

把同一机器人连续放入多个物理环境：

```text
A: tabletop rigid objects
B: articulated furniture
C: deformables
D: navigation + manipulation
E: collaborative human environment
```

每个环境长期交互，然后冻结 checkpoint 做全历史回测。

禁止：

- 手工为每环境新增专属 head；
- 清空旧 memory；
- 每阶段重新初始化。

测 capability acquisition、retention、transfer、resource growth 和 autonomy ratio。

---

## 本章结论

Self-evolving physical intelligence 不应该被定义为“网络会自己改参数”。更严格的目标是：**机器人能自主选择有信息的交互，从失败和成功中形成记忆与机制，组合旧能力产生新能力，并在有限资源与持续安全约束下长期保持和扩张能力集合。** 只要不能被这些实验指标证伪，就还不是科学意义上的“自进化”。