# Part 13　二维视觉与视觉表示学习

## 学习目标

理解机器人从像素到可行动表示的完整链条；掌握 CNN、ViT、检测/分割/跟踪、光流、自监督视觉表示的核心机制；能够设计实验回答一个比“视觉 backbone 更强吗？”更重要的问题：**这个表示是否真正保留了物理交互需要的信息？**

---

## 13.1 图像不是世界

相机给出的图像可抽象为：

\[
I_t=\mathcal R(s_t,c_t,l_t,m_t)+\epsilon_t,
\]

其中 \(s_t\) 是世界状态，\(c_t\) 是 camera pose / optics，\(l_t\) 是 lighting，\(m_t\) 是 material appearance。

同一物理状态可以因光照、曝光、视角得到完全不同的像素；不同物理状态也可能产生相似投影。因此 robot vision 的目标不是“理解图片本身”，而是恢复对行动有用的 latent variables。

## 13.2 从 Hand-Crafted Feature 到 Deep Representation

传统视觉依赖 edges、corners、SIFT/HOG 等人工特征。深度学习的改变是让 feature：

\[
z=E_\theta(I)
\]

通过数据和 objective 学出来。

但 objective 决定 representation。Image classification 优化类别不变性，可能主动丢失精确位置；机器人操作却恰好需要 pose、contact point 和细粒度 geometry。

## 13.3 CNN

二维 convolution：

\[
y_{i,j,c_o}=
\sum_{\Delta i,\Delta j,c_i}
W_{\Delta i,\Delta j,c_i,c_o}
\,x_{i+\Delta i,j+\Delta j,c_i}.
\]

核心 inductive bias：

- locality；
- weight sharing；
- translation equivariance。

它让模型高效利用局部视觉结构。即使 ViT 盛行，轻量 robot policy 中 CNN 仍因低 latency 和 spatial bias 很有竞争力。

## 13.4 Receptive Field

堆叠 convolution / pooling 增大 receptive field。底层 feature 看 edge，中层看局部 shape，高层形成更大语义。

但过强 downsampling 会让毫米级 manipulation 所需 spatial precision 丢失。一个 ImageNet backbone 最后一层 feature 可能语义强，却不适合直接预测抓取接触点。

## 13.5 Feature Pyramid

多尺度 representation 保留：

```text
high resolution → precise geometry
low resolution  → broad semantics
```

检测/分割常使用 FPN；机器人视觉也可以让高层 VLM 语义与高分辨率 geometry feature 并存，而不是只取最后一个 pooled token。

## 13.6 Vision Transformer

图像切成 patch：

\[
I\rightarrow X\in\mathbb R^{N\times d}.
\]

Multi-head self-attention：

\[
\mathrm{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V.
\]

ViT 的优势是长程关系与 scale-friendly pretraining；代价是 standard attention 随 token 数近似平方增长。

## 13.7 Patch Size 的物理含义

若图像 224×224、patch=16，则只有 14×14 visual tokens。一个小夹爪尖端、薄线缆、插孔边缘可能只占一两个 token。

因此视觉 token budget 直接限制 robot spatial resolution。扩大语言模型参数不会自动恢复预处理阶段已经丢掉的细节。

## 13.8 Positional Encoding

Attention 本身对 token permutation 不知道空间位置，需要 position encoding。2D absolute、relative position、RoPE-like extension 等方案决定模型怎样表示空间关系。

若 robot camera pose 会显著变化，仅有 image-plane positional encoding 不等于懂 3D geometry。

## 13.9 Detection

Object detection 输出：

\[
\{(b_i,c_i,p_i)\}_{i=1}^K.
\]

Bounding box 适合高层 object localization，却不提供精确 contact geometry。用于 manipulation 时，通常还需 mask / pose / depth。

## 13.10 Semantic 与 Instance Segmentation

Semantic segmentation 给每 pixel category；instance segmentation 区分同类不同物体。

机器人真正需要 persistent identity：如果桌上有三个相同杯子，“我刚才拿过哪个？”需要跨时间 object tracking/memory，而不仅是单帧 mask。

## 13.11 Tracking

Tracking 建立时间 correspondence：

\[
id_i^t\leftrightarrow id_j^{t+1}.
\]

困难来自 occlusion、appearance change、object interaction。Manipulator 自己常会遮挡目标，因此“被手挡住后重新出现还是同一个对象”是机器人状态估计核心问题。

## 13.12 Optical Flow

Brightness constancy 近似：

\[
I(x+u,y+v,t+1)\approx I(x,y,t).
\]

线性化：

\[
I_xu+I_yv+I_t=0.
\]

光流描述 image-plane motion，不直接等于 3D velocity，但对 hand/object motion、contact onset、video representation 很有用。

## 13.13 Scene Flow

当有 depth/stereo，可估 3D scene flow：

\[
F_i=p_i^{t+1}-p_i^t.
\]

它比 2D flow 更接近物理 motion，但需要可靠 correspondence 与 depth。

## 13.14 Visual Servoing

视觉不仅用于“先看一眼再规划”，还可直接进 feedback loop。

Image-based visual servoing：

\[
e=s(I)-s^*,
\]

通过 image Jacobian / interaction matrix 将 feature error 转换为 camera velocity。

它体现一个经典原则：不一定要先重建完整 3D 世界，局部视觉误差也能驱动稳定控制。

## 13.15 Contrastive Learning

设两种 augmentation 后的同一图像为正样本：

\[
L=-\log
\frac{\exp(\operatorname{sim}(z_i,z_i^+)/\tau)}
{\sum_j\exp(\operatorname{sim}(z_i,z_j)/\tau)}.
\]

对比学习能形成强语义 representation，但 augmentation 定义了哪些变化应该被模型忽略。若 crop/颜色增强把 manipulation-critical cue 当 nuisance，表示可能损失物理信息。

## 13.16 Masked Image Modeling

遮盖一部分 patch，让模型恢复 pixel/token/feature。它迫使模型利用上下文。

机器人场景更值得问：恢复 texture 与恢复 geometry/contact 哪个 objective 对 control 更有用？

## 13.17 Self-Distillation

Teacher/student 在不同 crop 上保持 feature consistency，使模型学到稳定视觉结构。DINO/DINOv2 类 representation 在 robotics 中常被作为 frozen visual encoder。

但“通用视觉强”仍需 downstream robot evidence。

## 13.18 Vision-Language Pretraining

CLIP-style objective 将图像与文本 embedding 对齐：

\[
\operatorname{sim}(z_I,z_T).
\]

这带来 open-vocabulary semantics，但语言 supervision 更偏“是什么”，不自然提供：

- 精确 metric depth；
- contact normal；
- friction；
- articulation axis；
- object hidden state。

因此 VLM representation 与 physical representation 不能默认等价。

## 13.19 Video Self-Supervision

视频比单图多出 motion / temporal continuity。训练目标可预测 future feature、mask future tube、跟踪 correspondence。

视频为物理学习提供信息：对象如何移动、手如何接触，但被动视频仍存在 confounding；如果动作不可知，不能唯一确定 causality。

## 13.20 Egocentric Human Video

第一视角 human video 与 robot camera 相似之处：手—物交互、task sequence、object affordance。差异：

- human hand morphology；
- camera/head dynamics；
- action 未记录；
- muscle/contact force 不可见；
- 人的控制能力远强于当前 robot。

因此 human video 更适合作为 representation / goal / skill prior，而不是直接 action label。

## 13.21 Task-Relevant Representation

一个更机器人化的目标是 representation 对未来可行动变量 sufficient：

\[
p(s_{t+1},r_t\mid o_{\le t},a_t)
\approx
p(s_{t+1},r_t\mid z_t,a_t).
\]

如果两个图像在 task-relevant latent 上相同，即使 texture 不同，表示应接近；如果 contact condition 不同，即使外观近似，表示应区分。

## 13.22 Probe 不是终点

Linear probe 可以测 latent 是否含某变量，但“可线性读出”不证明 policy 实际使用它。

证据强度从弱到强：

```text
representation visualization
→ linear probe
→ controlled intervention
→ policy sensitivity
→ task-success mediation
```

## 13.23 Counterfactual Visual Intervention

固定任务语义，单独改一个视觉变量：

- object position；
- texture；
- lighting；
- irrelevant distractor；
- camera pose；
- contact geometry。

若真正因果变量改变时 action 不变，或无关变量改变时 action 剧烈变化，说明 visual representation 有问题。

## 13.24 Multi-Camera Fusion

多个 camera：

\[
I\in\mathbb R^{B\times V\times C\times H\times W}.
\]

Fusion 方法：

- feature concat；
- view token attention；
- 先回投到 3D；
- geometry-aware cross-view attention。

简单 concat 能工作，但不显式保证不同 view 对同一物体的 correspondence。

## 13.25 Wrist Camera vs Global Camera

Global camera 提供 scene context；wrist camera 提供近距离精细 geometry，但运动剧烈、易 motion blur/occlusion。

很多 manipulation policy 同时使用两者，本质是将“全局任务状态”和“局部接触细节”分层。

## 常见失败

- 只看语义 probe，忽略 spatial precision；
- patch 太粗，小物体信息在 encoder 前已丢失；
- train/test camera pose 不一致；
- visual encoder 被 language shortcut 架空；
- texture/background 与 task 强相关，模型学 shortcut；
- wrist camera motion blur 在 simulator 不存在；
- representation 对 segmentation 很强，对 contact/pose 很弱。

## 最小实验

在同一 manipulation dataset 上冻结两个 encoder：一个 image-language semantic backbone，一个 self-supervised video/geometry backbone。统一 action head、数据与训练步数。测：object class probe、relative depth、pose、contact-point probe、最终 task success。再做 texture swap 和 camera shift，分析“哪些 representation property 真正中介了 success”。

## 研究问题

1. 机器人视觉最重要的 pretraining objective 是否应该从 semantic invariance 转向 action-conditioned predictive structure？
2. 是否需要为 contact region 分配动态更高视觉分辨率？
3. 一个统一 VLA visual encoder，能否同时兼顾 web semantics 与毫米级 geometry，还是应该双视觉分支？

<!-- CHAPTER-SOURCE-MAP:START -->
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part 13`](../../references/CHAPTER_SOURCE_ANCHORS.md#part-13)。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
<!-- CHAPTER-SOURCE-MAP:END -->
