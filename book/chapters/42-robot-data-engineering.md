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

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 42`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-42)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
