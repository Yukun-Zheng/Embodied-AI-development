# Derivation Companion — 从矩阵、数据流到公式

> 本文件是全书的“长推导层”。每个推导固定回答四件事：
>
> 1. **变量 / shape 先画清楚**；
> 2. **一步一步推公式，不跳关键步骤**；
> 3. **解释物理意义**；
> 4. **指出代码里对应什么 tensor / variable**。
>
> GitHub 数学排版统一使用简洁的 `$...$` 与 `$$...$$`，尽量避免复杂嵌套环境。

---

# D1　Least Squares → Pseudoinverse → Differential IK

## 1. 先看数据流

```text
joint increment Δq ∈ R^n
        ↓ Jacobian J ∈ R^(m×n)
end-effector increment JΔq ∈ R^m
        ↓ compare
required error e ∈ R^m
```

目标：找一个 `Δq`，使末端运动尽量接近 `e`。

$$
J\Delta q \approx e
$$

若方程没有精确解，则求：

$$
\Delta q^*=\arg\min_{\Delta q}\frac12\|J\Delta q-e\|_2^2
$$

展开：

$$
L(\Delta q)=\frac12(J\Delta q-e)^T(J\Delta q-e)
$$

对 `Δq` 求梯度：

$$
\nabla_{\Delta q}L=J^T(J\Delta q-e)
$$

令梯度为零：

$$
J^TJ\Delta q=J^Te
$$

如果 `J^T J` 可逆：

$$
\Delta q=(J^TJ)^{-1}J^Te
$$

这就是一种 pseudoinverse 形式：

$$
J^+=(J^TJ)^{-1}J^T
$$

于是：

$$
\Delta q=J^+e
$$

### 物理意义

Jacobian 把**关节空间局部速度**映射到**任务空间局部速度**。Pseudoinverse 做的是逆方向的最小二乘映射。

### 代码变量

```text
J:      [B, task_dim, dof]
e:      [B, task_dim]
dq:     [B, dof]
```

PyTorch 中不要显式求逆，优先 `lstsq` / `pinv` / solve。

---

# D2　为什么需要 Damped Least Squares

接近 singularity 时，某个 singular value：

$$
\sigma_i\to 0
$$

SVD：

$$
J=U\Sigma V^T
$$

普通 pseudoinverse：

$$
J^+=V\Sigma^+U^T
$$

其中：

$$
\Sigma^+_{ii}=\frac1{\sigma_i}
$$

所以 `σ_i → 0` 时，关节速度会爆炸。

加入正则：

$$
\Delta q^*=\arg\min_{\Delta q}
\|J\Delta q-e\|^2+\lambda^2\|\Delta q\|^2
$$

求导：

$$
J^T(J\Delta q-e)+\lambda^2\Delta q=0
$$

得到：

$$
(J^TJ+\lambda^2I)\Delta q=J^Te
$$

因此：

$$
\Delta q=(J^TJ+\lambda^2I)^{-1}J^Te
$$

或任务空间形式：

$$
\Delta q=J^T(JJ^T+\lambda^2I)^{-1}e
$$

### 直觉

`λ` 在“末端误差小”和“关节运动别太大”之间做 trade-off。

---

# D3　Null Space：冗余机械臂为什么还能做第二件事

如果：

$$
Jv=0
$$

则 `v` 位于 Jacobian null space。

因此：

$$
\Delta q=J^+e+(I-J^+J)z
$$

第一项完成主任务；第二项不会一阶改变末端运动。

例如让关节远离 limit：

$$
z=-\alpha\nabla_q C(q)
$$

于是：

$$
\Delta q=J^+e-\alpha(I-J^+J)\nabla_q C(q)
$$

### 数据流

```text
end-effector error → primary dq
joint-limit cost   → null-space dq
                     ↓ add
                   final dq
```

这就是多任务层级控制的最小数学原型。

---

# D4　SO(3) 指数映射与 Rodrigues Formula

旋转轴单位向量：

$$
\omega=[\omega_x,\omega_y,\omega_z]^T
$$

对应 skew-symmetric matrix：

$$
[\omega]_\times=
\begin{bmatrix}
0&-\omega_z&\omega_y\\
\omega_z&0&-\omega_x\\
-\omega_y&\omega_x&0
\end{bmatrix}
$$

旋转：

$$
R=\exp([\omega]_\times\theta)
$$

利用矩阵指数级数：

$$
\exp(A)=I+A+\frac{A^2}{2!}+\frac{A^3}{3!}+\cdots
$$

对单位旋转轴有：

$$
[\omega]_\times^3=-[\omega]_\times
$$

因此奇数次和偶数次分别合并成 `sin` 与 `cos`：

$$
R=I+\sin\theta[\omega]_\times+(1-\cos\theta)[\omega]_\times^2
$$

这就是 Rodrigues formula。

### 为什么重要

它把 Lie algebra 中的局部三维旋转向量，映射到合法的 rotation matrix，而不是直接对 matrix 元素做任意回归。

---

# D5　SE(3) Composition 与 Inverse

齐次变换：

$$
T_{AB}=
\begin{bmatrix}
R_{AB}&p_{AB}\\
0&1
\end{bmatrix}
$$

若：

$$
p_A=R_{AB}p_B+p_{AB}
$$

以及：

$$
p_B=R_{BC}p_C+p_{BC}
$$

代入：

$$
p_A=R_{AB}R_{BC}p_C+R_{AB}p_{BC}+p_{AB}
$$

所以：

$$
R_{AC}=R_{AB}R_{BC}
$$

$$
p_{AC}=R_{AB}p_{BC}+p_{AB}
$$

矩阵形式正好是：

$$
T_{AC}=T_{AB}T_{BC}
$$

反变换由：

$$
p_B=R_{AB}^T(p_A-p_{AB})
$$

得到：

$$
T_{AB}^{-1}=
\begin{bmatrix}
R_{AB}^T&-R_{AB}^Tp_{AB}\\
0&1
\end{bmatrix}
$$

### 代码检查

随机 `T` 后验证：

$$
TT^{-1}\approx I
$$

这是机器人代码最应该有的单元测试之一。

---

# D6　Manipulator Jacobian 从微分得到

假设末端位置：

$$
x=f(q)
$$

小扰动：

$$
f(q+\Delta q)\approx f(q)+\frac{\partial f}{\partial q}\Delta q
$$

定义：

$$
J(q)=\frac{\partial f}{\partial q}
$$

因此：

$$
\Delta x\approx J(q)\Delta q
$$

除以 `Δt`，令 `Δt→0`：

$$
\dot x=J(q)\dot q
$$

### Shape

若任务空间 twist 6D，机械臂 n DOF：

```text
qdot: [n]
J:    [6, n]
twist:[6]
```

### 力的对偶关系

功率守恒：

$$
\tau^T\dot q=w^TV
$$

又有：

$$
V=J\dot q
$$

所以：

$$
\tau^T\dot q=w^TJ\dot q
$$

对任意 `qdot` 成立，因此：

$$
\tau=J^Tw
$$

这就是为什么 Jacobian transpose 能把末端 wrench 映射到 joint torque。

---

# D7　Euler–Lagrange → Manipulator Equation

广义坐标：

$$
q\in\mathbb R^n
$$

动能：

$$
K(q,\dot q)=\frac12\dot q^TM(q)\dot q
$$

势能：

$$
V(q)
$$

Lagrangian：

$$
L(q,\dot q)=K-V
$$

Euler–Lagrange equation：

$$
\frac{d}{dt}\frac{\partial L}{\partial \dot q_i}-\frac{\partial L}{\partial q_i}=\tau_i
$$

把所有维度组合后得到：

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)=\tau
$$

其中：

- `M(q)`：配置相关惯性；
- `C(q,qdot)qdot`：Coriolis / centrifugal；
- `g(q)=∂V/∂q`：重力项。

有接触时增加：

$$
M\ddot q+C\dot q+g=\tau+J_c^T\lambda
$$

### 物理意义

学习策略输出 `τ` 时，必须直接面对这整个方程；输出 target position 时，低层 controller 会替它处理很多动力学。

---

# D8　Impedance Control 为什么像“虚拟弹簧阻尼器”

期望末端 `x_d`，误差：

$$
e=x_d-x
$$

定义期望 wrench：

$$
F=K_pe+K_d\dot e
$$

通过 Jacobian transpose：

$$
\tau=J^TF+g(q)
$$

一维情况下，如果环境/机器人等效质量为 `m`：

$$
m\ddot e+K_d\dot e+K_pe=0
$$

标准二阶系统：

$$
\omega_n=\sqrt{\frac{K_p}{m}}
$$

$$
\zeta=\frac{K_d}{2\sqrt{mK_p}}
$$

### 直觉

`Kp` 越大越“硬”；`Kd` 控制振荡。Contact-rich manipulation 中，不一定越硬越好。

---

# D9　LQR：从 Bellman 到 Riccati

系统：

$$
x_{t+1}=Ax_t+Bu_t
$$

cost：

$$
J=\sum_t x_t^TQx_t+u_t^TRu_t
$$

假设 value function：

$$
V_{t+1}(x)=x^TP_{t+1}x
$$

Bellman：

$$
V_t(x)=\min_u\left[x^TQx+u^TRu+(Ax+Bu)^TP_{t+1}(Ax+Bu)\right]
$$

对 `u` 求导：

$$
2Ru+2B^TP_{t+1}(Ax+Bu)=0
$$

整理：

$$
(R+B^TP_{t+1}B)u=-B^TP_{t+1}Ax
$$

所以：

$$
u=-K_tx
$$

其中：

$$
K_t=(R+B^TP_{t+1}B)^{-1}B^TP_{t+1}A
$$

再代回得到 Riccati recursion。

### 意义

LQR 是“预测 dynamics + 优化 future cost + feedback”的最小完整范例，也是理解 MPC/RL 的桥。

---

# D10　Bayes Filter：历史怎样被压成 Belief

已有 belief：

$$
b_t(s_t)=P(s_t\mid o_{1:t},a_{1:t-1})
$$

执行动作 `a_t` 后先预测：

$$
\bar b_{t+1}(s')=\sum_sP(s'\mid s,a_t)b_t(s)
$$

得到新 observation `o_{t+1}` 后：

$$
b_{t+1}(s')=\eta P(o_{t+1}\mid s')\bar b_{t+1}(s')
$$

其中 `η` 是归一化常数。

因此：

```text
old belief
→ transition model + action
→ predictive belief
→ observation likelihood
→ posterior belief
```

这就是 POMDP 中“历史压缩”的核心。

---

# D11　Kalman Filter：为什么是两个 Gaussian 的最优线性融合

系统：

$$
x_t=Ax_{t-1}+Bu_t+w_t
$$

$$
z_t=Hx_t+v_t
$$

其中：

$$
w_t\sim\mathcal N(0,Q),\quad v_t\sim\mathcal N(0,R)
$$

预测均值：

$$
\hat x_t^-=A\hat x_{t-1}+Bu_t
$$

预测 covariance：

$$
P_t^-=AP_{t-1}A^T+Q
$$

innovation：

$$
y_t=z_t-H\hat x_t^-
$$

innovation covariance：

$$
S_t=HP_t^-H^T+R
$$

Kalman gain：

$$
K_t=P_t^-H^TS_t^{-1}
$$

更新：

$$
\hat x_t=\hat x_t^-+K_ty_t
$$

$$
P_t=(I-K_tH)P_t^-
$$

### 直觉

`R` 大 → 不信 sensor；`P^-` 大 → 更依赖 sensor。

---

# D12　Information Gain → Next-Best-View

当前 belief entropy：

$$
H(b_t)
$$

候选 sensing action `a` 后，可能收到不同 observation `o`。

期望 posterior entropy：

$$
\mathbb E_o[H(b_{t+1}\mid a,o)]
$$

因此：

$$
IG(a)=H(b_t)-\mathbb E_oH(b_{t+1}|a,o)
$$

如果移动也有代价：

$$
a^*=\arg\max_a IG(a)-\lambda C(a)
$$

### Embodiment-agnostic 分层

高层只输出：

$$
g_{view}^*=\arg\max_g IG(g)-\lambda C(g)
$$

具体机器人再求：

$$
a^*=Planner(g_{view}^*, embodiment)
$$

这把“应该从哪里看”与“这个身体怎样走过去看”分开。

---

# D13　Behavior Cloning 为什么产生 Covariate Shift

专家状态分布：

$$
s\sim d_{\pi_E}
$$

BC 优化：

$$
\min_\theta \mathbb E_{s\sim d_{\pi_E}}\ell(\pi_\theta(s),\pi_E(s))
$$

部署时实际访问：

$$
s\sim d_{\pi_\theta}
$$

只要策略早期有小错误：

```text
small action error
→ new state not in expert dataset
→ larger prediction error
→ further state shift
```

所以训练和测试 state distribution 不同。

DAgger 的核心就是：

$$
D\leftarrow D\cup\{(s,\pi_E(s)):s\sim d_{\pi_\theta}\}
$$

直接收集 learner 自己访问的状态。

---

# D14　Policy Gradient 的最小推导

轨迹概率：

$$
p_\theta(\tau)=p(s_0)\prod_t\pi_\theta(a_t|s_t)P(s_{t+1}|s_t,a_t)
$$

目标：

$$
J(\theta)=\mathbb E_{\tau\sim p_\theta}[R(\tau)]
$$

使用 log-derivative trick：

$$
\nabla_\theta J
=\mathbb E_\tau[R(\tau)\nabla_\theta\log p_\theta(\tau)]
$$

环境 transition 不依赖 `θ`：

$$
\nabla_\theta\log p_\theta(\tau)
=\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)
$$

因此：

$$
\nabla_\theta J
=\mathbb E\left[\sum_t\nabla_\theta\log\pi_\theta(a_t|s_t)G_t\right]
$$

进一步把 `G_t` 换成 advantage 得到常见 actor–critic estimator。

---

# D15　Diffusion Policy：从噪声到动作块

动作块：

$$
A^0=[a_t,\dots,a_{t+H-1}]
$$

前向扩散：

$$
A^k=\sqrt{\bar\alpha_k}A^0+\sqrt{1-\bar\alpha_k}\epsilon
$$

训练网络预测噪声：

$$
\mathcal L=
\mathbb E\|\epsilon-\epsilon_\theta(A^k,k,c)\|^2
$$

其中 condition：

$$
c=f(o_{t-h:t})
$$

推理：

```text
A^K ~ N(0,I)
→ denoise step K
→ ...
→ A^0
→ execute first h actions
→ observe again
```

### 为什么适合机器人

同一 observation 可能存在多个合法动作模式；diffusion 建模完整 action distribution，而不是取均值。

---

# D16　Flow Matching：把噪声连续运输到 Action

取 source：

$$
x_0\sim p_0
$$

目标动作：

$$
x_1\sim p_{data}
$$

定义 interpolation path，例如：

$$
x_t=(1-t)x_0+tx_1
$$

真实 path velocity：

$$
\dot x_t=x_1-x_0
$$

训练：

$$
\mathcal L=\mathbb E\|v_\theta(x_t,t,c)-(x_1-x_0)\|^2
$$

推理时积分 ODE：

$$
\frac{dx}{dt}=v_\theta(x,t,c)
$$

从 source distribution 运输到 action distribution。

### Diffusion vs Flow

二者都可建模多模态连续动作；具体性能取决于 path、solver、steps、conditioning 和系统 latency，不应只凭生成模型标签判断。

---

# D17　Action Chunking 与 Stale Action

设模型观察时刻：

$$
t_0
$$

一次输出 `H` 个动作，每个控制周期 `Δt`。

第 `k` 个动作实际执行时，它依据的 observation age 近似：

$$
Age_k=T_{infer}+k\Delta t
$$

所以 chunk 越长，后段 action 越“旧”。

如果环境在期间被扰动：

$$
s_{t+k}\neq \hat s_{t+k|t}
$$

仍执行旧 chunk 就会产生 stale-action failure。

RTC / async replacement 的目标是缩小：

$$
\mathbb E[Age(a_{executed})]
$$

同时保持动作连续性。

---

# D18　PPO Clipped Objective

旧策略：

$$
\pi_{old}
$$

新策略概率比：

$$
r_t(\theta)=
\frac{\pi_\theta(a_t|s_t)}{\pi_{old}(a_t|s_t)}
$$

普通 surrogate：

$$
r_tA_t
$$

如果 `r` 变化过大，单次 update 可能破坏策略。

PPO 使用：

$$
L^{clip}=\mathbb E\left[
\min(r_tA_t,
clip(r_t,1-\epsilon,1+\epsilon)A_t)
\right]
$$

### 直觉

当 update 已经把某个 action 概率推得过远时，进一步收益被截断，从而形成近似 trust region。

---

# D19　World Model + MPC

latent state：

$$
z_t=E(o_t)
$$

learned dynamics：

$$
z_{k+1}=F_\theta(z_k,a_k)
$$

给定候选 action sequence：

$$
A=[a_t,\dots,a_{t+H-1}]
$$

预测：

$$
\hat z_{t+1:t+H}=Rollout(F,z_t,A)
$$

优化：

$$
A^*=\arg\max_A
\sum_{k=1}^{H}R(\hat z_{t+k},a_{t+k-1})
$$

只执行第一步：

$$
a_t=A_0^*
$$

然后获取真实 observation，重新编码与规划。

### 为什么 receding horizon 重要

真实 observation 每一步都把 learned model rollout 拉回现实，限制 long-horizon drift。

---

# D20　World Model Error 怎样随 Horizon 累积

设真实 dynamics：

$$
x_{t+1}=f(x_t,a_t)
$$

learned：

$$
\hat x_{t+1}=\hat f(\hat x_t,a_t)
$$

假设模型单步误差：

$$
\|f(x,a)-\hat f(x,a)\|\le\epsilon
$$

且 `f` 对 state 是 `L`-Lipschitz：

$$
\|f(x,a)-f(y,a)\|\le L\|x-y\|
$$

则递推：

$$
e_{t+1}\le Le_t+\epsilon
$$

因此：

$$
e_H\le \epsilon\sum_{i=0}^{H-1}L^i
$$

如果 `L>1`，误差可能指数式放大。

这解释了为什么 one-step prediction 很准，不保证 long rollout 可用。

---

# D21　Control Barrier Function 的最小推导

定义安全集合：

$$
\mathcal S=\{x:h(x)\ge0\}
$$

系统：

$$
\dot x=f(x)+g(x)u
$$

为了不离开安全集合，希望边界附近：

$$
\dot h(x)\ge-\alpha(h(x))
$$

而：

$$
\dot h=\nabla h^T(f+gu)
$$

因此：

$$
\nabla h^Tf+\nabla h^Tgu+\alpha(h)\ge0
$$

给 learned policy `u_raw`，求最接近的安全动作：

$$
u^*=\arg\min_u\|u-u_{raw}\|^2
$$

subject to 上述 CBF constraint。

### 意义

这形成一个 policy-independent safety projection layer。

---

# D22　Capture Point：机器人为什么要“迈一步接住自己”

线性倒立摆模型：

$$
\ddot x=\omega_0^2(x-p)
$$

其中：

$$
\omega_0=\sqrt{g/z_0}
$$

定义 capture point：

$$
\xi=x+\frac{\dot x}{\omega_0}
$$

若把支撑点 `p` 放到 `ξ`，理想模型下 divergent component 可被捕获。

### 直觉

不仅当前 CoM 位置重要，速度也重要。人快向前倒时，必须把脚落在更前方。

这也是静态 support polygon 不能完整描述动态平衡的原因。

---

# D23　Grasp Map 与 Internal Force

接触力堆叠：

$$
f=[f_1^T,\dots,f_m^T]^T
$$

物体 wrench：

$$
w=Gf
$$

如果：

$$
f_{int}\in Null(G)
$$

则：

$$
Gf_{int}=0
$$

所以：

$$
w=G(f+f_{int})=Gf
$$

`f_int` 不改变物体净 wrench，却改变接触内部受力。

### 双臂意义

两只手可以互相“挤压”物体而不改变物体运动；过大 internal force 会损坏对象或导致 slip/contact instability。

---

# D24　Long-Horizon 成功率为什么迅速下降

若一个任务由 `n` 个关键步骤组成，每步独立成功概率近似 `p`：

$$
P_{task}=p^n
$$

例如：

$$
p=0.98,\quad n=100
$$

则：

$$
P_{task}\approx0.133
$$

因此长时程机器人必须依赖：

```text
verification
+ retry
+ recovery
+ memory
+ replanning
```

而不是只把单步 success 从 97% 提到 98%。

---

# D25　Calibration：80% 自信到底意味着什么

模型预测成功概率：

$$
\hat p_i
$$

理想 calibration：

$$
P(Y=1\mid \hat p=p)=p
$$

Brier score：

$$
BS=\frac1N\sum_i(\hat p_i-y_i)^2
$$

ECE 把概率分桶：

$$
ECE=\sum_m\frac{|B_m|}{N}
|acc(B_m)-conf(B_m)|
$$

### 机器人意义

如果机器人说“99% 可以安全抓”，实际只有 70%，uncertainty-aware stop 就失效。

---

# D26　Continual Learning Performance Matrix

任务顺序：

$$
T_1,T_2,\dots,T_N
$$

定义：

$$
P_{i,j}=\text{after learning }T_j\text{, performance on }T_i
$$

遗忘：

$$
F_i=\max_{j<i}P_{i,j}-P_{i,N}
$$

Forward transfer 可与 scratch baseline 比：

$$
FT_i=P_{i,i}^{prior}-P_{i,i}^{scratch}
$$

这张 matrix 比“最后平均分”更能描述机器人长期成长。

---

# D27　Cross-Embodiment 的两层分解

共享任务机制：

$$
z_{skill}=F(o,g)
$$

具体身体 decoder：

$$
a^{(e)}=D(z_{skill},s^{(e)},morphology_e)
$$

于是：

```text
Task Effect / Skill
      ↓ shared
Embodiment-independent latent
      ↓ conditioned by morphology
Embodiment-specific executable action
```

真正 zero-shot generalization 要求新 morphology `e_new` 在训练中未出现。

若只是新 robot ID + 新 adapter 数据，就不是严格 zero-shot。

---

# D28　Known Physics + Learned Residual

真实 dynamics：

$$
x_{t+1}=f_{real}(x_t,u_t)
$$

已有物理模型：

$$
f_{phys}(x,u)
$$

学习 residual：

$$
r_\theta(x,u)=f_{real}(x,u)-f_{phys}(x,u)
$$

预测：

$$
\hat f(x,u)=f_{phys}(x,u)+r_\theta(x,u)
$$

### 为什么可能比纯神经网络好

已知 invariance / dynamics 不需要数据重新学；模型容量集中拟合 friction、unmodeled contact、delay 等 residual。

但如果 `f_phys` 偏差非常大，也可能形成错误 inductive bias。

---

# D29　Architecture Gain 与 Data Gain 的 2×2 分解

四个实验：

```text
A = old architecture + old data
B = old architecture + new data
C = new architecture + old data
D = new architecture + new data
```

粗略主效应：

$$
Gain_{data}\approx B-A
$$

$$
Gain_{arch}\approx C-A
$$

交互：

$$
Interaction=D-C-B+A
$$

### 为什么重要

如果论文只比较 `D` 与 `A`，就无法知道提升到底来自更多数据、新架构还是二者协同。

---

# D30　从 Claim 到可证伪 Hypothesis

不可证伪说法：

> “我们的模型更理解物理。”

形式化：

定义干预 `δ`：改变摩擦，保持视觉外观不变。

定义 robustness：

$$
R(\pi)=P(success\mid do(\mu=\mu'))
$$

具体假说：

$$
R(\pi_{contact-aware})
-
R(\pi_{vision-only})>\Delta
$$

并预注册：

```text
if difference <= Δ
→ reject the mechanism claim
```

这一步把研究从“讲故事”变成科学实验。

---

# 使用方式

不要连续把 30 个推导都背完。推荐按正文出现顺序回查：

```text
Chapter
→ 看变量/shape
→ 自己先推
→ 对照 DERIVATIONS
→ 手算一个小例子
→ 写 20–50 行最小代码
→ 用数值结果验证公式
```

公式真正掌握的标准不是“看懂”，而是：

> **你能从物理对象重新写出它，并知道代码里哪一个 tensor 如果 shape / frame / timestamp 错了，会让公式失去意义。**