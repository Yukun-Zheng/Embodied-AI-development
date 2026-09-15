# Part 14　三维、四维与对象中心世界表示

## 学习目标

理解从 RGB-D/多视角 observation 到 point cloud、voxel、TSDF、occupancy、NeRF、3D Gaussian、dynamic 4D representation、object-centric latent、scene graph 和 affordance field 的主要路线；能够从机器人任务角度比较表示，而不是只看新视角渲染质量。

---

## 14.1 为什么机器人需要 3D

二维图像压缩了深度。Manipulation 却天然发生在三维空间：

\[
T_{object},T_{grasp},T_{ee}\in SE(3).
\]

机器人必须回答：

- 物体离我多远？
- 抓取点法向是什么？
- 末端能否从这里靠近？
- 后方有无碰撞？
- 两个对象空间关系是什么？

这些问题若完全让 2D visual token 隐式学习，数据需求通常更大。

## 14.2 Point Cloud

点云：

\[
P=\{p_i\}_{i=1}^N,
\qquad p_i\in\mathbb R^3.
\]

可附颜色、法向、语义：

\[
p_i=(x_i,y_i,z_i,r_i,g_i,b_i,n_i,c_i,\ldots).
\]

优势：坐标与 robot action 都可表达在同一 metric 3D frame。缺点：无规则、稀疏、遮挡严重、点数变化。

## 14.3 PointNet 思想

点集顺序不应影响结果。PointNet 使用共享 MLP + symmetric pooling：

\[
z=\operatorname{MAX}_i\phi(p_i).
\]

Permutation invariance 简洁，但 global pooling 容易损失局部结构，因此后续 PointNet++ / point transformer 引入局部 neighborhood。

## 14.4 Local Geometry

对点 \(p_i\) 取 kNN / radius neighborhood，估计 local surface normal、curvature、feature。

接触任务关心毫米级局部几何，因此 downsampling 不能只按网络吞吐做，需要保持 task-relevant surface。

## 14.5 Point Transformer

在 3D neighbor 中做 attention：

\[
y_i=\sum_{j\in\mathcal N(i)}\alpha_{ij}(W_vx_j+\delta_{ij}),
\]

其中 relative position encoding \(\delta_{ij}=\phi(p_i-p_j)\) 显式注入三维关系。

## 14.6 Voxel

将空间离散到规则 grid：

\[
V\in\mathbb R^{X\times Y\times Z\times C}.
\]

优势：可用 3D convolution、邻接关系明确；代价：分辨率提高时 memory 立方增长。

Sparse voxel 只存占用区域，可大幅提高效率。

## 14.7 Occupancy

定义空间点占用概率：

\[
o(x)=P(x\text{ occupied}).
\]

Occupancy 对 collision planning 很直接，却不天然表示 object identity、material 或 motion。

## 14.8 Signed Distance Field

SDF：

\[
\phi(x)=
\begin{cases}
+d(x,\partial O),&x\text{ outside}\\
-d(x,\partial O),&x\text{ inside}
\end{cases}
\]

梯度

\[
\nabla\phi(x)
\]

近似表面法向。Collision cost、trajectory optimization、implicit geometry 都常用。

## 14.9 TSDF

Truncated SDF 只在表面附近保留 signed distance，并把远处截断。RGB-D fusion 中可从多 frame 融合出稳定表面。

它是经典 3D reconstruction 与 modern neural field 之间的重要桥梁。

## 14.10 Mesh

Mesh 用 vertices + faces：

\[
\mathcal M=(V,F).
\]

对 collision/rendering 很方便，明确表面拓扑。但从 noisy sensor 在线重建 mesh 比 point cloud 更复杂，动态拓扑变化也困难。

## 14.11 NeRF

Neural Radiance Field：

\[
F_\theta(x,d)\rightarrow(\sigma,c).
\]

沿 camera ray \(r(t)=o+td\) 做 volume rendering：

\[
C(r)=\int T(t)\sigma(r(t))c(r(t),d)dt.
\]

NeRF 强在 view-consistent appearance、新视角合成，但原始 objective 并不要求 contact geometry、collision surface、material dynamics 正确。

## 14.12 NeRF for Robotics

Robot application 可从 NeRF 提取：depth、surface、semantic field、occupancy、pose gradient。

但必须问：

- online update 快吗？
- dynamic object 怎么处理？
- geometry error 对 grasp 有多大？
- radiance ambiguity 会不会让 collision map 错？

## 14.13 3D Gaussian Splatting

场景由高斯 primitives：

\[
\mathcal G_i=(\mu_i,\Sigma_i,c_i,\alpha_i)
\]

组成。显式 primitive 使 rendering 快、优化高效。

对 robotics 更有意义的扩展是给 Gaussian 附加：semantics、velocity、uncertainty、affordance、material，而不是只追 photorealism。

## 14.14 3D Representation 的统一比较

| 表示 | 优势 | 核心限制 |
|---|---|---|
| Point cloud | metric、直接 | sparse / unordered |
| Voxel | regular | memory cubic |
| TSDF/SDF | geometry/collision | semantics/dynamics 弱 |
| Mesh | explicit surface | online topology 难 |
| NeRF | continuous view synthesis | rendering objective ≠ physics |
| 3DGS | fast explicit rendering | physical semantics 需额外学习 |

没有“最先进表示”脱离任务存在。

## 14.15 Dynamic Scene

静态 3D 不够。真实 manipulation 中物体、手、人都在动。可定义 time-dependent field：

\[
\mathcal F(x,t)\rightarrow z.
\]

或 canonical space + deformation：

\[
x_t=\Phi_t(x_c).
\]

动态 representation 必须区分 camera motion 与 object motion。

## 14.16 4D Representation

“4D”通常指 3D + time。核心任务：

- persistent object identity；
- trajectory；
- deformation；
- contact event；
- appearance changes；
- future prediction。

单纯把每时刻独立重建 3D 再堆起来，不等于形成一致的 4D world model。

## 14.17 Scene Flow

三维点运动：

\[
F(p_t)=p_{t+1}-p_t.
\]

它可连接 observation dynamics 与 object motion，但 occlusion/reappearance、nonrigid correspondence 仍困难。

## 14.18 Rigid Object Factorization

若场景有 K 个 rigid object，可以表示：

\[
s_t=\{(T_i^t,\mathcal G_i)\}_{i=1}^K.
\]

这样运动主要由 pose 更新，而不是每帧重新生成全场像素。

对 tabletop manipulation，这种 object-centric state 往往比 dense pixel latent 更有组合性。

## 14.19 Object-Centric Representation

一般形式：

\[
Z_t=\{z_1^t,\ldots,z_K^t\}.
\]

每个 slot 可以包含 identity、pose、geometry、semantic、dynamic state。

优点：组合与 persistent memory；困难：对象边界并非总明确，例如 cloth、liquid、articulated furniture、两个物体形成接触组合后。

## 14.20 Articulated Object

抽屉/门/剪刀不只是一个 rigid pose，而有内部 configuration：

\[
s_{obj}=(T_{base},q_{art}).
\]

若表示能恢复 articulation axis/limit，机器人可以把“开抽屉”的机制迁移到新外观。

## 14.21 Scene Graph

场景图：

\[
G=(V,E).
\]

Node 是 object/agent/place；edge 是：on、inside、attached、holding、left-of、supports。

它适合 high-level reasoning：

```text
robot --holding--> cup
cup --above--> sink
cabinet --contains--> bowl
```

但 graph 必须从 noisy perception 连续维护，不能把 oracle symbolic state 当真实能力。

## 14.22 Spatial Relation 不应只离散化

“left-of”适合语言，但 precise manipulation 还需要连续 relative transform：

\[
{}^AT_B.
\]

因此更完整 scene graph edge 可以同时包含 discrete semantics + continuous geometry。

## 14.23 Affordance Field

将“可行动性”直接定义在空间：

\[
A(x,R,k\mid o,g)
\]

表示在 pose \((x,R)\) 执行 skill \(k\) 的可行性/价值。

抓取 field、push direction field、navigation traversability 都属于此思想。

## 14.24 Signed Distance + Affordance

一个强 robot representation 可以同时有：

\[
\phi(x)\quad\text{geometry safety}
\]

与

\[
A(x,k)\quad\text{task opportunity}.
\]

前者回答“能不能到”，后者回答“到这里有没有用”。

## 14.25 Egocentric vs Allocentric

**Egocentric**：相对机器人表达，直接用于 action；

**Allocentric/world-centric**：相对固定世界表达，利于 memory/map。

长期 agent 往往需要两者：persistent world map + current egocentric control frame。

## 14.26 Embodiment-Agnostic Representation

如果 world representation 全部编码成 robot joint state，就很难跨身体。更抽象的 object pose、contact relation、affordance、goal field 有望共享：

\[
Z_{world}\quad\text{shared},
\qquad
D_e(Z_{world})\rightarrow a^{(e)}.
\]

这为 cross-embodiment 提供一个自然分层。

## 14.27 Uncertainty in 3D

3D reconstruction 不能只输出点。每个区域应知道 confidence：

\[
P(\text{surface at }x),
\quad
\Sigma_{pose},
\quad
U_{occlusion}(x).
\]

Planner 才能区分“这里确定是空的”和“这里没有观测到”。两者对安全完全不同。

## 14.28 Occlusion

Depth camera 只观测 first visible surface。物体后方不是 free space，而是 unknown。

Occupancy map 应至少区分：free / occupied / unknown。

把 unknown 当 free 是许多视觉操作碰撞的根源。

## 14.29 Representation 与 World Model

Static representation 说明“现在世界是什么”；world model 说明“动作后世界会如何变”。

理想接口：

\[
z_t=E(o_{\le t}),
\]

\[
z_{t+1}=F(z_t,a_t).
\]

Representation 是否好，最终应看 \(F\) 是否容易、准确、可组合地预测。

## 14.30 怎样评价 3D/4D 表示

不要只测 rendering PSNR。对机器人至少测：

1. pose / geometry error；
2. collision correctness；
3. contact-point prediction；
4. object persistence under occlusion；
5. dynamics prediction；
6. downstream grasp/planning success；
7. memory/update latency。

## 常见失败

- point cloud frame 错；
- 多 camera extrinsic 小误差造成 ghost geometry；
- voxel resolution 不足以表示细线缆；
- NeRF 视觉漂亮但 surface 偏移；
- object slot identity 在遮挡后交换；
- scene graph 使用 oracle object state，无法真机复现；
- 3D representation 每帧重算，没有 persistent state。

## 最小实验

同一 tabletop manipulation 场景构建三种表示：RGB feature、point cloud、TSDF/occupancy。固定 planner/policy，分别做 obstacle avoidance 与 grasp。再制造 depth hole 和 occlusion，测碰撞 false-negative、grasp pose error 与 task success。

## 研究问题

1. 通用具身模型是否应该有显式 persistent 3D/4D world state，而不是每次从图像重新推断？
2. Object-centric representation 对 deformable world 的“对象”边界如何定义？
3. 未来 world representation 最基本 primitive 会是 token、object、Gaussian、field，还是 learned mechanism？

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 14`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-14)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
