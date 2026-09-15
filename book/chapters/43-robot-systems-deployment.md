# Part 43　机器人系统工程与真实部署

## 43.1 从 Python Policy 到 Robot System

论文里的 policy 通常是：

\[
a_t=\pi_\theta(o_t).
\]

真实机器人却是：

```text
camera / sensors
→ drivers
→ synchronization
→ preprocessing
→ policy inference
→ safety filtering
→ frame transform
→ IK / controller
→ fieldbus
→ actuator
→ physical world
→ sensors
↺
```

任何一层失败都可能被误判为“模型不行”。

---

## 43.2 ROS 2

ROS 2 提供模块化机器人通信：

- node；
- topic；
- service；
- action；
- QoS。

它不是实时控制器本身，而是连接 perception、planning、policy、driver 的系统骨架。

---

## 43.3 Topic / Service / Action

### Topic

持续异步数据流，例如 camera、joint state。

### Service

短请求—响应，例如 reset gripper。

### Action

长时任务，可反馈进度和取消，例如 navigate to pose。

接口选错会造成系统结构不自然。

---

## 43.4 TF / Transform Tree

真实系统必须维护：

```text
world
└── base
    ├── camera
    ├── left_arm
    │   └── left_ee
    └── right_arm
        └── right_ee
```

TF 错误会导致 policy 看起来“方向感很差”，实际上是 frame transform 错。

---

## 43.5 Node Architecture

不要把所有代码放进一个 Python process。

典型拆分：

- sensor nodes；
- state estimator；
- policy server；
- planner；
- controller；
- safety monitor；
- logger。

边界应按时间尺度和 failure isolation 划分。

---

## 43.6 Real-Time Control

硬实时循环要求：

\[
T_{compute}<T_{deadline}
\]

不仅平均满足，而是最坏情况也满足。

大模型 inference 通常不是 hard real-time，因此不能直接承担电机级 servo。

---

## 43.7 Multi-Rate Architecture

机器人天然多频率：

```text
motor servo:     500–2000 Hz
state estimator: 100–500 Hz
tactile reflex:  100–1000 Hz
visuomotor:      10–100 Hz
VLM/reasoning:   1–10 Hz
```

具体数值取决于系统，但层级差异普遍存在。

因此需要 sample-and-hold、shared state 和 asynchronous updates。

---

## 43.8 Camera / Sensor Streaming

传感 pipeline 包括：

- capture；
- DMA/copy；
- decode；
- resize；
- normalization；
- batching。

端到端 sensor latency：

\[
T_s=T_{capture}+T_{transfer}+T_{decode}+T_{preprocess}.
\]

只测 model forward time 会严重低估系统延迟。

---

## 43.9 Robot Driver

driver 负责把高层 command 转成硬件协议：

- CAN；
- EtherCAT；
- serial；
- vendor SDK。

必须处理：

- timeout；
- watchdog；
- fault code；
- encoder zero；
- command limits。

---

## 43.10 Motion Planner Service

即使使用 VLA，motion planner 仍可能承担：

- collision-free transit；
- global reachability；
- safe reset；
- fallback。

现代系统不是“learned vs classical”二选一，而是按强项组合。

---

## 43.11 Policy Server

大模型常作为独立 server：

```text
observation request
→ GPU model
→ action chunk response
```

需要定义：

- request timestamp；
- queue policy；
- timeout；
- stale result handling；
- batching。

---

## 43.12 GPU Inference Pipeline

典型延迟：

\[
T=T_{H2D}+T_{encoder}+T_{backbone}+T_{action}+T_{D2H}.
\]

优化要先 profile，而不是盲目量化。

有时 video decode 比 Transformer 更慢。

---

## 43.13 Edge / On-Device Inference

on-device 优势：

- low network latency；
- privacy；
- offline operation；
- predictable connection。

代价：

- power；
- memory；
- thermal；
- model size。

2026 的 humanoid/VLA 系统越来越重视本地推理。

---

## 43.14 Quantization / Compilation

可使用：

- FP16/BF16；
- INT8；
- TensorRT 类编译；
- kernel fusion；
- KV/cache optimization。

但机器人模型量化后必须重新测：

- action precision；
- latency jitter；
- closed-loop success。

单看 token/s 不够。

---

## 43.15 Network Latency

远程 inference：

\[
T_{total}=T_{uplink}+T_{queue}+T_{infer}+T_{downlink}.
\]

网络 jitter 比平均 latency 更危险。

机器人必须定义：如果 500 ms 没有新 action 怎么办？

---

## 43.16 Async Pipeline

异步结构：

```text
sensor thread ────────────────┐
policy thread ───── latent ───┤
controller thread ────────────┤→ robot
logger thread ────────────────┘
```

共享数据必须带 timestamp/version，避免读到跨时刻拼接状态。

---

## 43.17 Safety Monitor

safety monitor 独立检查：

- joint limit；
- velocity；
- acceleration；
- force；
- collision；
- workspace；
- communication heartbeat。

不应完全依赖 policy 自己“记得安全”。

---

## 43.18 Logging / Replay

每次 rollout 至少记录：

- raw observation；
- processed model input；
- model output；
- filtered command；
- controller command；
- robot state；
- timestamp；
- safety event。

这样才能区分模型错还是系统错。

---

## 43.19 Experiment Reproducibility

保存：

```text
code commit
model checkpoint hash
dataset version
config
robot calibration
firmware/software version
random seed
```

真机复现实验比仿真更依赖这些元数据。

---

## 43.20 Distributed Training

foundation robot model 训练涉及：

- data parallel；
- tensor/model parallel；
- checkpoint sharding；
- massive dataloader。

但训练基础设施与部署基础设施是两套不同系统，不能混为一谈。

---

## 43.21 Model Serving for Robots

多机器人共享 model service 时，需要：

- robot identity；
- embodiment config；
- session state；
- priority；
- SLA；
- rollback。

错误模型版本推给机器人比普通 web service 错误代价更高。

---

## 43.22 一次真实 Rollout 到底发生了什么

完整时间线：

```text
t0 camera exposure
t1 image arrives
t2 preprocess done
t3 inference starts
t4 action chunk produced
t5 safety filter
t6 robot command sent
t7 motor controller executes
t8 physical contact occurs
t9 sensors observe consequence
```

真正闭环 delay：

\[
T_{loop}=t_9-t_0.
\]

这才是 policy 实际面对的系统。

---

## 本章结论

机器人算法只有进入真实时间、真实驱动器和真实故障模式之后才成为机器人系统。系统工程不是“部署细节”，而是决定 observation 和 action 是否仍对应正确物理时刻的核心科学变量。

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 43`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-43)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
