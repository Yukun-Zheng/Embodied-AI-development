# Part 5　几何、流形、图与因果

## 5.1 为什么欧氏向量不够

三维位置属于 \(\mathbb R^3\)，旋转却不是一个普通三维向量。旋转矩阵属于：

\[
SO(3)=\{R\in\mathbb R^{3\times3}:R^TR=I,\det R=1\}.
\]

它有约束、曲率和群结构。若直接对两个 rotation matrix 做普通线性插值，结果通常不再是合法 rotation。

## 5.2 Manifold

流形 \(\mathcal M\) 局部类似欧氏空间，但全局可能有复杂结构。每个点 \(x\) 有 tangent space \(T_x\mathcal M\)，可在其中表示局部速度/扰动。

机器人位姿优化的正确直觉是：state 在 manifold 上，increment 在 tangent space 中。

## 5.3 Lie Group

Lie group 同时是群和光滑流形。\(SO(3)\)、\(SE(3)\) 是最重要例子。

Group operation 对应 compose transform，identity 对应无变换，inverse 对应反向 transform。

## 5.4 Lie Algebra

Lie algebra 是 identity 附近 tangent space。三维角速度向量映射为 skew matrix：

\[
\hat\omega=\begin{bmatrix}
0&-\omega_z&\omega_y\\
\omega_z&0&-\omega_x\\
-\omega_y&\omega_x&0
\end{bmatrix}.
\]

Exponential map 将局部速度积分回 group。

## 5.5 Equivariance

若输入通过群作用 \(g\) 变化，输出按相应作用变化：

\[
f(gx)=\rho(g)f(x).
\]

这是一种“把物理对称性写进模型”的方法。对 3D manipulation，SE(3)-equivariant feature 可能比纯数据 augmentation 更 sample-efficient。

## 5.6 Graph

图：

\[
G=(V,E).
\]

机器人身体本来就是 graph：link/joint 是 node/edge；场景也是 graph：对象与 spatial/contact relation 构成边；多机器人 communication 也形成 graph。

## 5.7 Message Passing

\[
m_i=\operatorname{AGG}_{j\in\mathcal N(i)}\psi(h_i,h_j,e_{ij}),
\]

\[
h_i'=\phi(h_i,m_i).
\]

Graph architecture 能自然适应 variable number of joints / objects，是 cross-embodiment 与 object-centric model 的重要候选。

## 5.8 Factor Graph

概率后验常分解：

\[
p(X\mid Z)\propto\prod_k\phi_k(X_k,Z_k).
\]

取负 log 变成稀疏 nonlinear least squares。SLAM 中 pose、landmark、IMU、loop closure 都可作为变量与 factor。

## 5.9 Causal Graph

结构因果模型：

\[
X_i=f_i(PA_i,U_i).
\]

相关性问 \(p(y\mid x)\)，干预问：

\[
p(y\mid do(x)).
\]

机器人最大的优势是能**真的 do(action)**，因此比纯互联网观察更适合收集因果数据。

## 5.10 Confounding

如果训练中红色物体总是轻，模型可能学到 color→required force 的伪相关。换成红色重物时失败。

解决不是简单“更多同分布数据”，而是主动打破 confounding：控制颜色、质量独立变化。

## 5.11 Counterfactual

决策需要比较未执行动作：

> 如果刚才从另一侧抓，会不会滑？

形式上比较潜在结果 \(Y(a_1),Y(a_2)\)。World model 真正用于 planning，必须对 counterfactual action 有正确敏感性。

## 5.12 Identifiability

即使模型拟合所有 observation，也不一定唯一恢复真实 mechanism。多个 hidden causal model 可能产生相同 observational distribution。

因此“发现物理规律”的 claim 必须说明哪些 intervention 足以辨识机制。

## 5.13 几何与因果的结合

机器人很多 mechanism 同时具有 geometry 与 causality：抽屉的关节轴是几何 constraint，同时决定“沿什么方向施力才会开”。如果 representation 只识别语义“drawer”，却没有 axis/contact/effect，就很难跨柜子迁移。

## 最小实验

构造两个变量：object color 与 mass。在 training 中让它们高度相关，再在 test 打破相关。比较普通 policy 与显式利用 force feedback/active intervention 的 policy，观察 shortcut 如何形成并被打破。
