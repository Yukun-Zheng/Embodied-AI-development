# Part 42　机器人数据工程

## 42.1 Data Collection System

机器人数据系统至少包括：

```text
sensors
→ timestamping
→ synchronization
→ action/state logging
→ episode manager
→ storage
→ validation
→ dataset index
```

“录到视频”远远不等于拥有训练数据。

---

## 42.2 Teleoperation Hardware

常见采集接口：

- leader arm；
- VR；
- joystick；
- SpaceMouse；
- motion capture；
- exoskeleton。

teleop device 会塑造 demonstration distribution。

例如 leader-follower arm 数据往往更自然地匹配 robot kinematics。

---

## 42.3 Episode Lifecycle

episode 应有明确：

```text
start
→ active
→ success / failure / abort
→ reset
→ validated
```

必须记录终止原因，不应所有终止都标成 done=True。

---

## 42.4 Timestamp 与 Synchronization

每条 observation/action 应带 source timestamp。

如果 camera 延迟 \(80\,ms\)，action 却用最新 joint state，训练 pair 可能错位。

对齐目标：

\[
(o_{t},s_t,a_t)
\]

应该表示同一 physical time。

---

## 42.5 Multi-Modal Alignment

RGB 30 Hz、depth 30 Hz、joint 200 Hz、tactile 500 Hz。

不能简单按 array index 拼。

需要：

- interpolation；
- nearest timestamp；
- resampling；
- raw stream retention。

---

## 42.6 Compression / Storage / Streaming

机器人数据很快达到 TB–PB。

设计要权衡：

- random read；
- sequential throughput；
- video codec；
- lossless state；
- cloud/local storage。

训练经常不是 GPU 算力瓶颈，而是 data loader 吞吐瓶颈。

---

## 42.7 HDF5 / Parquet / RLDS / LeRobot Formats

格式没有绝对优劣。

要看：

- episodic hierarchy；
- columnar analytics；
- streaming；
- cloud friendliness；
- video handling；
- interoperability。

最重要的是 schema 明确且 versioned。

---

## 42.8 Metadata

必须记录：

- robot ID / configuration；
- software commit；
- calibration；
- scene；
- task；
- operator；
- timestamp；
- success；
- controller mode。

没有 metadata，未来很难解释 dataset shift。

---

## 42.9 Annotation

annotation 可包括：

- language instruction；
- subgoal；
- event boundary；
- failure type；
- object labels；
- reward。

自动 VLM annotation 必须抽样人工审计。

---

## 42.10 Quality Control

数据进入训练前做：

1. decode test；
2. timestamp monotonicity；
3. finite state values；
4. action bounds；
5. frame count；
6. calibration check；
7. visual corruption；
8. success label audit。

---

## 42.11 Duplicate / Leakage Detection

重复 episode 会扭曲 sampling。

benchmark scene/task 泄漏进训练则会制造虚假 generalization。

需要 hash、perceptual hash、trajectory similarity 和 metadata join。

---

## 42.12 Failure Data

failure 不是垃圾数据。

应该区分：

- operator error；
- robot error；
- hardware fault；
- environment invalid；
- intentional negative example。

不同失败对学习价值完全不同。

---

## 42.13 Dataset Versioning

数据集必须像代码一样版本化：

```text
v1.0 raw
v1.1 fixed labels
v1.2 added failures
v2.0 changed action convention
```

模型 checkpoint 必须记录训练 dataset manifest。

---

## 42.14 Dataset Mixture

建立 mixture manifest：

```yaml
dataset_A: weight 0.4
dataset_B: weight 0.2
human_video: weight 0.3
failure_data: weight 0.1
```

否则模型不可复现。

---

## 42.15 Massive Robot Corpora Data Loader

高性能 loader 需要：

- sharding；
- prefetch；
- parallel decode；
- local cache；
- distributed sampler。

训练吞吐：

\[
Throughput=\min(T_{IO},T_{decode},T_{augment},T_{GPU}).
\]

---

## 42.16 Distributed Storage

需要考虑：

- object storage；
- NAS；
- local NVMe cache；
- checksum；
- immutable raw data。

原始数据最好 append-only，清洗结果通过 derived dataset 生成。

---

## 42.17 Governance / Privacy

家庭机器人视频可能包含：

- 人脸；
- 住址；
- 屏幕内容；
- 私人物品。

数据治理必须包含权限、脱敏、retention 和 consent。

---

## 42.18 Robotics Data Flywheel

完整 flywheel：

```text
deploy
→ log
→ detect hard cases
→ annotate/correct
→ train
→ evaluate
→ redeploy
```

真正有价值的数据平台不是“存很多数据”，而是能自动发现最值得采的新数据。

---

## 本章结论

机器人数据工程决定 foundation model 的上限。Timestamp、schema、action convention、failure label 和 versioning 看似琐碎，却会直接决定模型是否学到真实因果关系，还是只学到错位的数据相关性。
<!-- CHAPTER-ENRICHMENT-P42:START -->
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
<!-- CHAPTER-ENRICHMENT-P42:END -->

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 42`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-42)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
