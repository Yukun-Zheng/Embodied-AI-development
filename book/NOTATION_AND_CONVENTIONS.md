# Notation & Conventions — 全书统一符号、坐标系、Shape 与 Action 规范

> 机器人教材最危险的错误往往不是大公式，而是“同一个字母在不同章节含义变了”“pose 到底是谁相对谁”“quaternion 顺序不清楚”“action 是绝对还是 delta”。本文件是全书的**单一 convention 源**。

---

# 1. 字体与对象类型

| 写法 | 含义 | 例子 |
|---|---|---|
| $x$ | 标量或语境明确的一维对象 | time $t$ |
| $\mathbf{x}$ | 向量 | position $\mathbf{p}$ |
| $\mathbf{A}$ | 矩阵 / 线性算子 | Jacobian $\mathbf{J}$ |
| $\mathcal{S}$ | 集合 / 空间 | state space |
| $p(x)$ | 概率密度 / 质量函数 | belief |
| $f_\theta$ | 参数化函数 | neural network |
| $\hat{x}$ | 估计量 | estimated state |
| $x^*$ | 最优值 | optimal action |
| $x^{ref}$ | reference / demonstration | reference motion |

正文允许为可读性省略粗体，但推导层优先保留对象类型。

---

# 2. 时间索引

统一：

- $t$：当前离散控制时刻；
- $t-1$：上一时刻；
- $t+1$：下一时刻；
- $T$：episode / sequence 总长度；
- $H$：planning/action horizon；
- $h$：实际从 action chunk 执行的短前缀长度。

历史窗口：

$$
o_{t-k+1:t}=[o_{t-k+1},\ldots,o_t]
$$

未来动作块：

$$
a_{t:t+H-1}=[a_t,\ldots,a_{t+H-1}]
$$

除非特别说明，**history length 与 action horizon 不是一个变量**。

---

# 3. State / Observation / Belief

统一区分：

$$
s_t\in\mathcal S
$$

表示真实/任务定义的 world state；

$$
o_t\in\mathcal O
$$

表示 sensor observation；

$$
b_t(s)=P(s_t=s\mid o_{\le t},a_{<t})
$$

表示 belief。

学习模型内部 latent：

$$
z_t=f_\theta(o_{\le t})
$$

**不要自动把 latent $z_t$ 称为 state**，除非证明它对目标决策具有足够性。

---

# 4. Robot Joint Symbols

| 符号 | 含义 | 单位 |
|---|---|---|
| $q$ | joint configuration | rad / m |
| $\dot q$ | joint velocity | rad/s / m/s |
| $\ddot q$ | joint acceleration | rad/s² / m/s² |
| $\tau$ | joint torque / generalized force | N·m / N |
| $q^{des}$ | desired joint position | rad / m |
| $\tau^{cmd}$ | command sent to low-level actuator/controller | implementation-specific |

如果 robot 有 floating base，应明确：

$$
q=[q_{base},q_{actuated}]
$$

并说明 base 部分是否可直接 actuate。

---

# 5. Coordinate Frame Naming

统一使用：

```text
W / world       世界/地图坐标系
B / base        机器人基座坐标系
C / camera      相机坐标系
E / ee          末端执行器坐标系
O / object      物体坐标系
G / goal        目标坐标系（若需要）
```

变换记号：

$$
{}^AT_B
$$

表示：**把 B frame 中的坐标转换到 A frame**。

等价简写：

$$
T_{AB}
$$

本书优先在容易混淆的推导中使用上标形式 `${}^AT_B`。

点变换：

$$
{}^A\mathbf p = {}^AT_B\;{}^B\mathbf p
$$

组合：

$$
{}^AT_C={}^AT_B{}^BT_C
$$

---

# 6. Homogeneous Transform

$$
{}^AT_B=
\begin{bmatrix}
{}^AR_B & {}^A\mathbf p_B\\
0&1
\end{bmatrix}
$$

其中：

- `${}^AR_B`：B frame basis 在 A frame 中的 rotation；
- `${}^A\mathbf p_B`：B origin 在 A frame 中的位置。

这一定义决定整本书左右乘 convention。

---

# 7. Rotation Convention

## 7.1 Rotation matrix

本书用 column vector：

$$
\mathbf p_A=R_{AB}\mathbf p_B
$$

组合从右向左作用。

## 7.2 Quaternion

正文默认写：

$$
q=(w,x,y,z)
$$

但**代码必须显式写库 convention**。

常见库并不统一：

- 某些使用 `wxyz`；
- 某些使用 `xyzw`。

禁止在代码注释中只写 `quat` 而不写顺序。

## 7.3 Euler angles

必须同时写：

- 轴顺序，例如 `XYZ` / `ZYX`；
- intrinsic / extrinsic；
- degrees / radians。

否则 Euler angle 数值没有完整含义。

---

# 8. Twist / Wrench

正文默认 spatial twist 排列：

$$
V=
\begin{bmatrix}
\omega\\
v
\end{bmatrix}
\in\mathbb R^6
$$

wrench：

$$
F=
\begin{bmatrix}
\tau\\
f
\end{bmatrix}
\in\mathbb R^6
$$

但实际库可能采用 `[linear, angular]` 顺序。代码必须在 interface 处转换并写清。

功率配对：

$$
P=F^TV
$$

---

# 9. Jacobian

本书默认：

$$
V=J(q)\dot q
$$

因此：

```text
J shape = [task_dim, dof]
qdot    = [dof]
V       = [task_dim]
```

wrench 到 torque：

$$
\tau=J^TF
$$

如果某库返回 transpose convention，必须在代码边界处理，正文不跟着库改变数学定义。

---

# 10. Dynamics

Manipulator equation：

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau+J_c^T\lambda
$$

统一：

- $M(q)$：mass/inertia matrix；
- $C(q,\dot q)\dot q$：Coriolis / centrifugal combined term；
- $g(q)$：gravity generalized force；
- $J_c$：contact Jacobian；
- $\lambda$：contact wrench/constraint force。

有些软件直接提供 bias force：

$$
b(q,\dot q)=C(q,\dot q)\dot q+g(q)
$$

必须注明 API 返回的是 `C` 还是完整 `bias`。

---

# 11. Camera Convention

Pinhole：

$$
\tilde p=K[X/Z,Y/Z,1]^T
$$

本书用 image pixel：

```text
u → image horizontal / column
v → image vertical / row
```

实际 camera optical frame 常见：

```text
+x right
+y down
+z forward
```

而机器人 base/world 常见 z-up。任何 RGB-D→world point cloud 代码必须明确这一步 frame conversion。

---

# 12. Tensor Shape Convention

默认 batch-first：

```text
B = batch
T = history / sequence length
V = number of camera views
C = image channels
H,W = image height,width
N = point/token count
D = hidden dimension
Da = action dimension
H_a = action horizon
```

常见输入：

```text
RGB:          [B, T, V, C, H, W]
Depth:        [B, T, V, 1, H, W]
Point cloud:  [B, T, N, 3(+F)]
Proprio:      [B, T, Ds]
Language:     [B, L]
Action chunk: [B, H_a, Da]
```

如果模型库采用 `[T,B,D]`，在代码入口处显式转换。

---

# 13. Action Convention

任何 policy 必须回答六个问题：

1. action space 是什么？
2. absolute 还是 delta？
3. frame 是什么？
4. unit 是什么？
5. frequency 是多少？
6. 谁把它变成 actuator command？

常见 action：

### Joint position

$$
a_t=q_t^{des}
$$

### Joint delta

$$
a_t=\Delta q_t
$$

### Cartesian delta pose

$$
a_t=(\Delta p,\Delta r,g)
$$

### Torque

$$
a_t=\tau_t
$$

### Action chunk

$$
A_t\in\mathbb R^{H_a\times D_a}
$$

**禁止只在论文表格写 `action_dim=7` 而不说明 7 个量分别是什么。**

---

# 14. Delta Pose Convention

若 action 是 translation + rotation delta，必须注明：

- `Δp` 在 world/base/ee 哪个 frame；
- rotation 用 Euler/axis-angle/quaternion；
- left composition 还是 right composition。

例如 body-frame right composition：

$$
T_{t+1}=T_t\exp(\hat\xi_t)
$$

world-frame left composition：

$$
T_{t+1}=\exp(\hat\xi_t)T_t
$$

两者物理含义不同。

---

# 15. Frequency / Latency

统一区分：

```text
sensor rate
policy input rate
model inference rate
new-chunk rate
command/control rate
motor servo rate
```

延迟：

$$
T_{loop}=T_{sense}+T_{transfer}+T_{pre}+T_{model}+T_{post}+T_{bus}+T_{actuate}
$$

模型报告 `10 Hz` 时必须问：是 new inference 10 Hz，还是 controller 10 Hz？

---

# 16. Dataset Convention

episode：

$$
\tau=(o_0,a_0,o_1,a_1,\ldots,o_T)
$$

建议每条样本保留：

```text
timestamp
robot_id / embodiment
observation streams
action raw
controller command if available
success/failure/abort
instruction/task
calibration version
software commit
```

若重采样产生 aligned sample，原始 timestamp 不应被覆盖。

---

# 17. Probability / Uncertainty

- $p_\theta$：model distribution；
- $b_t$：belief；
- $H[p]$：entropy；
- $D_{KL}(p\|q)$：KL divergence；
- $I(X;Y)$：mutual information。

写 uncertainty 时必须说明：

- predictive entropy？
- ensemble variance？
- epistemic approximation？
- aleatoric variance？

“uncertainty score”不是完整定义。

---

# 18. Reward / Cost

RL 统一用 reward 最大化：

$$
J(\pi)=\mathbb E\sum_t\gamma^tr_t
$$

控制/规划章节常用 cost 最小化：

$$
J(A)=\sum_t c(s_t,a_t)
$$

两者只是符号选择：

$$
r=-c
$$

章节切换时应说明，避免“高/低更好”混乱。

---

# 19. Evaluation Convention

每个机器人 success rate 必须同时写：

```text
successes / total trials
number of seeds / scene instances
confidence interval when meaningful
human-intervention rule
reset rule
failure taxonomy
```

不允许只写：

```text
Success = 83%
```

而不给 denominator。

---

# 20. Claim Strength Vocabulary

本书统一区分：

### Demonstrates

公开视频/实验展示在给定场景能做到。

### Supports

数据支持某 hypothesis，但不排除所有替代解释。

### Establishes

有较强、重复、多对照证据。

### Suggests / Hypothesizes

值得研究，但证据不足。

### Does not establish

明确指出某结果**不能推出**更强结论。

前沿章节应避免把公司 demo 的 `demonstrates` 自动写成科学意义上的 `establishes`。

---

# 21. 最终规则：任何公式旁边都能回答四个问题

对于：

$$
y=f(x)
$$

必须能回答：

1. `$x$` 在现实机器人中是什么物理量？
2. `$y$` 是什么？
3. frame / unit / shape / time 是什么？
4. 代码中哪个 tensor 对应它？

如果回答不了，公式还没有真正进入具身智能系统。