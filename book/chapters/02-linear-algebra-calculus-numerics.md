# Part 2　线性代数、微积分与数值计算

## 学习目标

本章只保留机器人真正反复使用的数学。重点不是熟练做题，而是看到 \(J\)、\(M\)、projection、least squares、autodiff 时知道它们在系统中意味着什么；更重要的是，知道什么时候一个“算法失败”其实是 shape、conditioning、离散化或浮点数值问题。

---

## 2.1 Shape 是第一语义

在机器人代码里，先写 shape：

\[
q\in\mathbb R^{n_q},\quad
T\in\mathbb R^{4\times4},\quad
P\in\mathbb R^{N\times3},
\]

\[
I\in\mathbb R^{B\times T\times V\times C\times H\times W},
\quad
A\in\mathbb R^{B\times H_a\times d_a}.
\]

矩阵维度往往直接对应物理语义。一个 shape 对不上，常说明 frame、时间维或 action semantics 已经错了。

## 2.2 线性映射

\[
y=Ax
\]

不要把 \(A\) 只看成二维数字。它是从一个向量空间到另一个向量空间的映射。Camera projection 的局部线性化、Jacobian、neural linear layer 都属于这类对象。

## 2.3 基与坐标

几何向量 \(v\) 与它在某个 basis 下的坐标不同：

\[
[v]_B=P_{BA}[v]_A.
\]

机器人 frame bug 的根源之一，就是把“物理向量”与“某 frame 中的数字”当成同一对象。

## 2.4 Rank / Range / Null Space

对于 \(A\in\mathbb R^{m\times n}\)：

\[
\operatorname{rank}(A)=\dim \mathcal R(A).
\]

Null space：

\[
\mathcal N(A)=\{x:Ax=0\}.
\]

机械臂 \(V=J\dot q\) 中，\(\dot q_N\in\mathcal N(J)\) 不改变末端瞬时运动，因此可以完成 secondary objective。

## 2.5 Least Squares

当 \(Ax=b\) 无精确解：

\[
x^*=\arg\min_x\|Ax-b\|_2^2.
\]

对满列秩情况：

\[
A^TAx=A^Tb,
\qquad
x^*=(A^TA)^{-1}A^Tb.
\]

实际数值计算不要显式求逆；QR/SVD 更稳定。

## 2.6 SVD 与 Pseudoinverse

\[
A=U\Sigma V^T,
\qquad
A^+=V\Sigma^+U^T.
\]

SVD 揭示系统在不同方向的增益。若 Jacobian 最小奇异值接近 0，机械臂接近 singularity。

Manipulability 的一个经典量：

\[
w(q)=\sqrt{\det(JJ^T)}.
\]

## 2.7 Damped Least Squares

\[
x=A^T(AA^T+\lambda^2I)^{-1}b.
\]

Damping 用少量 bias 换数值稳定。在 IK 中尤其重要：不要等到 pseudoinverse 输出巨大 joint velocity 后再 clip。

## 2.8 Eigenvalue 与系统模式

离散线性系统：

\[
x_{k+1}=Ax_k.
\]

若谱半径 \(\rho(A)<1\)，状态趋于 0。连续系统 \(\dot x=Ax\) 则要求 eigenvalue 实部 < 0。

这建立 stability、optimization curvature、dynamics mode 的共同直觉。

## 2.9 Gradient

标量函数：

\[
\nabla f(x)=\left[\frac{\partial f}{\partial x_1},\ldots,\frac{\partial f}{\partial x_n}\right]^T.
\]

Gradient 指向局部最快上升方向。优化用 \(-\nabla f\) 下降。

## 2.10 Jacobian

向量函数 \(f:\mathbb R^n\to\mathbb R^m\)：

\[
J_{ij}=\frac{\partial f_i}{\partial x_j}.
\]

一阶近似：

\[
f(x+\Delta x)\approx f(x)+J(x)\Delta x.
\]

机器人末端 kinematics 正是这个局部映射。

## 2.11 Hessian

\[
H_{ij}=\frac{\partial^2 f}{\partial x_i\partial x_j}.
\]

二阶近似：

\[
f(x+\Delta x)\approx f(x)+g^T\Delta x+\frac12\Delta x^TH\Delta x.
\]

Newton、iLQR/DDP、二次近似都依赖它。

## 2.12 Chain Rule 与 Backprop

如果 \(y=f(g(x))\)：

\[
\frac{dy}{dx}=\frac{dy}{dg}\frac{dg}{dx}.
\]

深度学习 backprop、differentiable simulator、differentiable planning 都是 chain rule 在大型计算图上的重复应用。

## 2.13 Automatic Differentiation

Autodiff 不等于 symbolic derivative，也不等于 finite difference。它对程序执行的 elementary operations 应用 chain rule，获得机器精度梯度。

机器人中需警惕：contact switch、clamp、argmax 等非光滑操作会让梯度不稳定或为零。

## 2.14 ODE 与 State Dynamics

\[
\dot x=f(x,u,t).
\]

Euler：

\[
x_{k+1}=x_k+\Delta t f(x_k,u_k).
\]

RK4 用多个中间 slope 提高精度。数值积分误差可能直接改变 controller stability 和 contact behavior。

## 2.15 Discretization

连续系统采样后：

\[
x_{k+1}=f_d(x_k,u_k,\Delta t).
\]

同一 controller 换 control rate，等价系统已变。所有真机实验必须把 Hz 当核心参数记录。

## 2.16 Conditioning

若矩阵 condition number

\[
\kappa(A)=\frac{\sigma_{max}}{\sigma_{min}}
\]

很大，小输入误差会导致大输出误差。IK、calibration、least squares 都应检查 conditioning，而不是只看“solver 成功”。

## 2.17 从公式到机器人代码的数据流

一个 differential-IK loop 可以把本章大部分对象串起来：

```text
q [n]
↓ FK
T_ee [4,4]
↓ pose error
 e [6]
↓ J(q)
J [6,n]
↓ SVD / conditioning / DLS solve
Δq [n]
↓ rate limit + integration
q_next [n]
```

真正实现时不要只检查最终 pose error，还应记录：

```text
sigma_min(J)
condition_number(J)
||dq||
solver residual
step size / dt
floating dtype
```

因为这些中间量能区分“目标不可达”“接近奇异”“线性化步长过大”“数值求解不稳”四种完全不同的失败。

## 2.18 常见数值失败

### 显式求逆

写成 `inv(A) @ b` 往往比 `solve(A, b)` 更慢、更不稳，也更容易掩盖 rank deficiency。

### 把有限差分当真值

finite difference 有两个相反误差：步长过大产生 truncation error，步长过小产生 cancellation / floating-point error。正确做法是扫 \(\epsilon\)，寻找误差谷底，而不是只测一个步长。

### 忽略单位尺度

把 meter、millimeter、radian、degree 混进同一个 least-squares objective，会直接改变 Hessian / conditioning。所谓“优化器偏好某个维度”可能只是单位没归一化。

### Autodiff 正确但模型错误

\[
\nabla_x f_\theta(x)
\]

即使数值完全正确，也只是在求错误模型 \(f_\theta\) 的梯度。梯度正确不等于 dynamics、contact 或 objective 正确。

### 离散化改变系统

controller 在 1 kHz 稳定，不代表原参数直接放到 20 Hz 仍稳定。sampling、delay 和 zero-order hold 都改变 closed-loop dynamics。

## 最小实验

对 2-link arm：手算 FK；用 finite difference、autodiff、解析式三种方法得到 Jacobian；沿 workspace 画 \(\sigma_{min}(J)\) 热图；比较 pseudoinverse 与 DLS 在奇异附近的 joint velocity。

再增加一个 numerical-only 对照：对同一个 Jacobian 扫 finite-difference \(\epsilon\in[10^{-10},10^{-1}]\)，画 derivative error 的 U-shaped curve，并分别用 float32 / float64 重复。

对应代码：[`code/minimal/planar_arm.py`](../../code/minimal/planar_arm.py)。

## 研究问题

1. 学习型 IK / differentiable controller 的提升，是否只是隐藏了更好的 damping、normalization 或 step-size policy？
2. 在 contact-rich simulation 中，gradient failure 来自模型不准还是非光滑 dynamics 本身？
3. 当 action space 从 joint 改为 Cartesian delta 时，conditioning 是否系统性改变 learning difficulty？
4. 一个机器人 benchmark 是否应该把 solver residual、condition number 与 control rate 当作标准诊断量？

## Source anchors / 原始来源

- Lloyd N. Trefethen & David Bau III, *Numerical Linear Algebra*: https://people.maths.ox.ac.uk/trefethen/text.html
- Nicholas J. Higham, *Accuracy and Stability of Numerical Algorithms*: https://nhigham.com/accuracy-and-stability-of-numerical-algorithms/
- Kevin M. Lynch & Frank C. Park, *Modern Robotics*: https://modernrobotics.northwestern.edu/
- PyTorch Autograd documentation（实现层参考）: https://pytorch.org/docs/stable/autograd.html

## 必须掌握的结论

- 不要显式求逆，能 solve 就 solve；
- shape、frame、unit 与 dtype 都是数学对象的一部分；
- singularity 是映射 rank / conditioning 问题，不是“软件报错”；
- autodiff 能给梯度，但不保证目标、模型或数值积分合理；
- 在机器人系统里，**数值稳定性本身就是闭环性能的一部分**。
