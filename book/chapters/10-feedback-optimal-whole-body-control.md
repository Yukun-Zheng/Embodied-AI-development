# Part 10　反馈控制、最优控制与 Whole-Body Control

## 学习目标

本章把“模型输出 action”继续往下追到底：动作怎样变成一个稳定、柔顺、满足接触与安全约束的物理闭环。读完后应能解释 PID、computed torque、impedance/admittance、operational-space control、LQR/iLQR/MPC、whole-body QP 与 Control Barrier Function 各自解决什么问题，以及它们如何与 learned policy / VLA 分工。

---

## 10.1 控制真正控制的是什么

控制不是“让机器人听话”，而是设计闭环动力系统。给定真实状态 \(x_t\)、目标 \(r_t\) 与控制输入 \(u_t\)：

\[
x_{t+1}=f(x_t,u_t),
\qquad
u_t=\pi_c(x_t,r_t).
\]

控制器最关心的是：扰动后是否回到目标、误差是否收敛、是否违反约束、接触力是否安全。

这与高层 policy 的职责不同。高层可以决定“往哪里去”，低层控制必须保证“怎么去时系统不失稳”。

## 10.2 Open Loop 与 Closed Loop

开环：

\[
u_t=u_t^{plan}.
\]

执行期间不根据新状态修正。任何模型误差、外力、抓取滑动都会累积。

闭环：

\[
u_t=\pi_c(x_t,r_t),
\]

持续根据 error 修正。机器人领域真正可靠的系统几乎总有多层 feedback，即使高层 VLA 一次输出一个 action chunk。

## 10.3 PID

误差

\[
e(t)=r(t)-y(t).
\]

PID：

\[
u(t)=K_Pe(t)+K_I\int_0^te(\tau)d\tau+K_D\dot e(t).
\]

直觉：

- P：当前位置错多少，就施加多少恢复作用；
- I：累积长期偏差，消除 steady-state error；
- D：对误差变化提供阻尼。

实际机器人需要 derivative filtering、integrator anti-windup、output saturation。教材里干净的 PID 式子并不是直接可部署实现。

## 10.4 Joint-Space PD

机械臂最常见低层形式：

\[
\tau=K_P(q_d-q)+K_D(\dot q_d-\dot q).
\]

如果 policy 输出 joint position target，真正动作通常经过这种 servo。于是 policy 的行为强烈依赖 \(K_P,K_D\)。同一 checkpoint 换 servo gain，实际闭环已经变了。

## 10.5 Gravity Compensation

若机械臂静态保持姿态，至少需抵消：

\[
\tau_g=g(q).
\]

常见控制：

\[
\tau=g(q)+K_P(q_d-q)-K_D\dot q.
\]

没有 gravity compensation 时，高增益 PD 必须同时承担“撑住手臂”和 tracking 两个职责。

## 10.6 Computed Torque Control

利用模型主动抵消 nonlinear dynamics：

\[
\tau=M(q)v+C(q,\dot q)\dot q+g(q),
\]

其中

\[
v=\ddot q_d+K_D(\dot q_d-\dot q)+K_P(q_d-q).
\]

如果动力学模型准确，闭环误差近似：

\[
\ddot e+K_D\dot e+K_Pe=0.
\]

这说明经典控制的一个核心思想：不是让网络重新学全部 dynamics，而是先用已知结构把系统变简单。

## 10.7 Impedance Control

接触任务不应死守 pose。希望机器人在外力下表现为虚拟质量—弹簧—阻尼：

\[
M_d\ddot e+D_d\dot e+K_de=F_{ext}.
\]

低 stiffness 使系统能顺应装配误差，高 damping 防止震荡。

对 VLA 来说，输出 nominal end-effector target + impedance low-level controller，往往比让慢速 VLA 直接学习毫米级接触修正更可靠。

## 10.8 Admittance Control

Admittance 将测得的外力转换为参考运动：

\[
M_d\ddot x_d+D_d\dot x_d+K_dx_d=F_{ext}.
\]

适用于本身是强位置 servo 的工业机器人：外层根据 F/T sensor 生成 pose offset，内层 position controller 跟踪。

## 10.9 Operational-Space Control

希望直接规定 end-effector dynamics。定义 task coordinate \(x\)：

\[
\dot x=J(q)\dot q.
\]

等效 task-space inertia：

\[
\Lambda=(JM^{-1}J^T)^{-1}.
\]

可设计 desired task wrench：

\[
F=\Lambda\ddot x^*+\mu+p,
\]

再映射：

\[
\tau=J^TF+N^T\tau_{null}.
\]

这样末端任务与 null-space posture 可以同时处理。

## 10.10 Hybrid Position / Force Control

沿某些方向控制位置，沿另一些方向控制力。用 selection matrix \(S\)：

\[
F_c=S F_{force}+(I-S)F_{position}.
\]

例如擦桌子：切向控制轨迹，法向维持接触力。

## 10.11 Passivity 直觉

接触人或环境时，控制器不能无界地产生能量。Passivity 提供一类稳定交互保证：系统输出的总能量不应超过初始储能加输入能量。

现代 learned residual 若叠加在 impedance controller 上，也应考虑是否破坏原系统 passivity。

## 10.12 LQR

线性系统：

\[
x_{t+1}=Ax_t+Bu_t.
\]

二次代价：

\[
J=\sum_{t=0}^{T-1}(x_t^TQx_t+u_t^TRu_t)+x_T^TQ_fx_T.
\]

通过 Riccati recursion 得到：

\[
u_t=-K_tx_t.
\]

LQR 的价值不是“只能控制线性系统”，而是展示 dynamics、future cost 与 feedback gain 的严格关系。

## 10.13 iLQR / DDP

非线性系统

\[
x_{t+1}=f(x_t,u_t)
\]

在 nominal trajectory 周围做 local linearization / quadratic approximation，反向计算 value，再 forward rollout。

最终得到的不只是一条 open-loop trajectory，还能得到局部 feedback law：

\[
u_t=u_t^*+K_t(x_t-x_t^*).
\]

## 10.14 Model Predictive Control

MPC 每个 control cycle 解：

\[
\min_{u_{t:t+H-1}} \sum_{k=t}^{t+H-1}\ell(x_k,u_k)+\ell_f(x_{t+H})
\]

subject to dynamics 与 constraints，然后只执行第一个 control。

流程：

```text
current state
   ↓
predict horizon
   ↓
optimize constrained controls
   ↓
execute first piece
   ↓
new state → re-optimize
```

这与 learned action chunk 的 receding-horizon execution 有相同系统思想：未来一次规划，现实只执行一部分，再反馈。

## 10.15 Constraint Handling

机器人约束包括：

\[
q_{min}\le q\le q_{max},
\]

\[
|\dot q|\le v_{max},\qquad |\tau|\le\tau_{max},
\]

collision、friction cone、contact mode、workspace boundary。MPC/QP 的重要优势是可以显式写这些 constraint，而不是期待训练数据隐式教会模型。

## 10.16 Whole-Body Control

Humanoid 同时有 hands、feet、COM、torso、gaze 等任务。一个常见 inverse-dynamics QP：

\[
\min_{\ddot q,\tau,\lambda}
\sum_i w_i\|J_i\ddot q+\dot J_i\dot q-a_i^*\|^2
\]

subject to

\[
M\ddot q+h=S^T\tau+J_c^T\lambda,
\]

以及 contact、friction、torque/joint-limit constraints。

这里 \(S\) 选择 actuated joints；floating base 没有直接 actuator。

## 10.17 Task Priority

简单加权 \(w_i\) 不能保证高优先级任务严格不被低优先级破坏。Hierarchical QP / null-space hierarchy 可以表达：

1. safety/contact；
2. balance；
3. hand task；
4. posture。

这类结构特别适合 humanoid：跌倒约束应高于“手更接近目标”。

## 10.18 Control Barrier Function

安全集合：

\[
\mathcal C=\{x:h(x)\ge0\}.
\]

若控制满足：

\[
\dot h(x,u)+\alpha(h(x))\ge0,
\]

可以保证系统不离开 safe set（在相应假设下）。

可把 learned policy 输出 \(u_{nom}\) 投影为最接近的安全输入：

\[
u^*=\arg\min_u\|u-u_{nom}\|^2
\]

subject to CBF / joint / collision constraints。

## 10.19 Learned Policy 与 Controller 的分工

四种层级：

```text
A. policy → torque
B. policy → joint target → PD
C. policy → EE target → IK / impedance
D. policy → task/skill → WBC / MPC / controller
```

A 最端到端但最 embodiment-specific、最难保证安全；D 利用最多结构，但高层表达更受 interface 限制。

没有一种层级永远最佳，取决于数据规模、robot dynamics、任务与安全要求。

## 10.20 多时间尺度

一个合理 humanoid stack 可能是：

```text
0.5–2 Hz      reasoning / task planner
5–30 Hz       VLA / skill policy
50–200 Hz     WBC / impedance reference
500–2000 Hz   joint servo
10 kHz+       motor current loop
```

不要让一个 5 Hz foundation model承担本来需要 1 kHz 闭环的职责。

## 常见失败

- policy 训练时用理想 position action，真机低层 servo 语义不同；
- high gain 导致接触振荡；
- action clipping 后破坏 trajectory continuity；
- WBC weight 调节掩盖高层 policy failure；
- controller frequency 改变后 checkpoint 明显退化；
- safety filter 频繁修改动作，但论文只报告原始 policy output。

## 最小实验

在同一机械臂 contact task 上固定 high-level target generator，分别使用：position PD、computed torque、impedance。加入 1–20 mm pose error 和外部扰动，比较 tracking、peak contact force、recovery。随后固定 controller，再对 learned policy 做公平比较。

## 研究问题

1. 未来 VLA 应直接输出 torque，还是输出让 WBC 可验证的任务空间目标？
2. 能否把 CBF / passivity / stability guarantee 与 foundation policy joint training，而不是部署后再加 patch？
3. 当 learned policy 和 model-based controller disagree 时，谁拥有最终 authority？
