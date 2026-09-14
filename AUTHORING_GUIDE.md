# AUTHORING GUIDE

本文件定义《具身智能：从物理世界到通用机器人》的统一写作、数学、引用、代码、实验和图示规范。

---

## 1. 总体原则

### 1.1 先机制，后术语

不要以术语堆砌代替解释。每个新概念必须先回答：

- 为什么存在；
- 它解决什么现实问题；
- 信息从哪里来，到哪里去；
- 它在物理系统中对应什么；
- 它与前后模块如何耦合。

### 1.2 先数据流，后公式

核心章节优先给出系统图，再进入公式。例如：

```text
Observation
  ├─ RGB: [B, T, C, H, W]
  ├─ Proprioception: [B, T, D_q]
  └─ Language: tokens
        ↓
Encoder / Fusion
        ↓
Latent State
        ↓
Policy / Planner
        ↓
Action Chunk: [B, H_a, D_a]
        ↓
Low-level Controller
        ↓
Robot
```

所有 shape、时间长度和坐标系应尽量显式。

### 1.3 不把“模型”当成“系统”

凡涉及真实机器人或仿真闭环，必须区分：

- perception model；
- policy；
- planner；
- controller；
- simulator / robot；
- communication；
- runtime frequency；
- safety layer。

不能用“模型输出动作”一句话掩盖整个执行链。

---

## 2. 每章建议结构

```text
# Chapter Title

## 0. 本章要解决的问题
## 1. 现实系统中的现象
## 2. 物理直觉
## 3. 系统与数据流
## 4. 数学形式化
## 5. 算法
## 6. 最小代码实现
## 7. 仿真 / 真机实验
## 8. 失败模式与边界
## 9. 论文谱系
## 10. 开放问题
## 11. 习题
## 12. 参考资料
```

并非所有章节必须机械复制，但核心技术章节尽量覆盖这些层次。

---

## 3. 数学写作规范

### 3.1 所有符号第一次出现必须定义

例如：

\[
\mathbf{q}\in\mathbb{R}^{n}
\]

表示机器人全部关节的位置，其中 \(n\) 为可控关节自由度数。

不要直接写：

\[
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau
\]

而不解释每一项。

### 3.2 公式必须连接物理意义

每个核心公式至少回答：

- 数学上是什么；
- 物理上是什么；
- 输入是什么；
- 输出是什么；
- 在机器人程序中如何获得这些量。

### 3.3 尽量保留维度

例如：

\[
\mathbf{J}(\mathbf{q})\in\mathbb{R}^{6\times n}
\]

并解释为什么是 `6 × n`，而不是只给公式。

### 3.4 坐标系永远明确

向量、位姿、速度、力如依赖参考系，应显式注明。例如：

\[
{}^{W}\mathbf{p}_{EE}
\]

表示末端在世界坐标系 \(W\) 下的位置。

### 3.5 旋转表示必须说明约定

凡涉及 quaternion、Euler angle、rotation matrix：

- 明确主动 / 被动旋转；
- 明确左乘 / 右乘约定；
- Euler 角明确轴顺序；
- quaternion 明确 `(w,x,y,z)` 或 `(x,y,z,w)`。

---

## 4. 代码规范

### 4.1 代码必须服务于理解

教材代码优先清晰，而不是追求框架技巧。

### 4.2 三层实现

推荐：

```text
minimal/
reference/
system/
```

- `minimal`：纯数学、尽量少依赖；
- `reference`：对齐标准论文 / 开源实现；
- `system`：接入真实机器人或大型仿真系统。

### 4.3 必须标出 tensor shape

神经网络核心路径中，重要变量旁应注明 shape。

### 4.4 训练与推理分开说明

必须明确：

- training-only component；
- inference-only path；
- train/inference 都存在但行为不同的模块；
- deployment 时实际保留哪些组件。

---

## 5. 引用与证据规范

### 5.1 来源优先级

优先：

1. 原始论文；
2. 官方项目页；
3. 官方代码仓库；
4. 官方技术报告 / 文档；
5. 高质量教材和课程；
6. 二手综述；
7. 博客 / 媒体仅作为补充背景。

### 5.2 不把宣传语言写成事实

例如“general-purpose”“human-level”“understands physics”等表述，必须检查论文实际评测与适用范围。

### 5.3 时间敏感内容标注版本

前沿章节建议包含：

```text
Last verified: YYYY-MM-DD
Model / code version: ...
```

### 5.4 区分四种陈述

正文中应清楚区分：

- 已知事实；
- 实验结果；
- 社区常见解释；
- 作者假说 / 推断。

---

## 6. 图示规范

### 6.1 图的目的必须是解释机制

优先画：

- 坐标系；
- 运动链；
- 数据流；
- 时间尺度；
- tensor shape；
- architecture；
- closed-loop control；
- training / inference difference；
- failure mode；
- paper genealogy。

### 6.2 尽量原创

若重绘论文架构，应：

- 明确“adapted from / redrawn from”；
- 保留原始来源；
- 不直接复制受版权保护的图像作为教材主体。

---

## 7. 实验规范

每个正式实验至少包含：

```text
Question
Hypothesis
Environment
Robot / embodiment
Observation
Action
Controller
Policy / algorithm
Dataset
Training configuration
Seeds
Metrics
Baselines
Ablations
Failure cases
Reproduction command
Expected result
Actual result
Interpretation
```

### 7.1 不只报成功率

根据任务补充：

- time-to-completion；
- path length；
- control smoothness；
- collision；
- force / impulse；
- intervention rate；
- calibration；
- uncertainty；
- compute / latency；
- robustness under perturbation。

### 7.2 失败样例是一等数据

实验章节必须保留：

- 失败视频 / trajectory；
- failure taxonomy；
- 对失败原因的证据与不确定性。

---

## 8. 论文谱系写法

不要写成：

```text
Paper A (2021)
Paper B (2022)
Paper C (2023)
```

而应写成：

```text
Problem P0
  ↓ limitation
Method A
  ↓ still fails because ...
Method B
  ↓ introduces ... but sacrifices ...
Method C
```

重点是“为什么下一篇工作会出现”。

---

## 9. 前沿模型章节统一解剖模板

对 VLA、world model、policy 等现代系统，至少回答：

1. 输入模态；
2. 输入 shape；
3. tokenizer / encoder；
4. fusion；
5. temporal modeling；
6. action representation；
7. action horizon；
8. training objective；
9. dataset composition；
10. inference path；
11. control frequency；
12. low-level controller；
13. deployment hardware；
14. benchmark；
15. strongest evidence；
16. known failure modes；
17. what is actually novel；
18. what remains unresolved。

---

## 10. 研究问题规范

教材最后不只给“未来工作”，而给可实验的研究问题。

一个合格研究问题应尽量写成：

```text
Hypothesis:
If mechanism X is genuinely responsible for capability Y,
then under controlled condition Z,
changing X while holding A/B/C fixed
should cause measurable effect ΔY.
```

避免：

- “加入更多模态可能更好”；
- “未来可使用更大的模型”；
- “进一步提高泛化能力”。

---

## 11. 文字风格

- 中文为主，必要专业术语保留英文；
- 首次出现给出中英文；
- 避免营销式形容词；
- 不用“显然”“众所周知”跳过关键推理；
- 不为追求严肃而写得晦涩；
- 不为追求易懂而牺牲精确性；
- 先建立直觉，再给严格定义；
- 尽量让读者知道“这一行公式为什么存在”。

---

## 12. 最终质量标准

一章写完后，作者应检查：

- 初学者是否知道问题从哪来；
- 工程人员是否知道系统如何运行；
- 研究者是否知道方法的真实边界；
- 公式是否能落到变量和代码；
- 实验是否能验证核心论断；
- 关键结论是否有来源；
- 有没有把相关性误写成机制；
- 有没有把 benchmark improvement 误写成 general intelligence。

如果这些问题不能回答，这一章仍不算完成。
