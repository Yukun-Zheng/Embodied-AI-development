# Case Study 02 — Diffusion Policy
## 从 Observation History 到去噪 Action Horizon

> 目标：把“机器人用 diffusion”拆成真实数据流。Diffusion Policy 的核心不是把图像生成模型换成动作，而是：**条件在 observation history 上，对未来一段连续动作的联合分布建模，并以 receding-horizon 方式闭环执行。**

---

# 1. 为什么单点回归会出问题

假设机器人看到一个物体，可以：

- 从左绕过去抓；
- 从右绕过去抓。

数据中动作分布是双峰：

$$
p(a|o)=\frac12\mathcal N(-\mu,\Sigma)+\frac12\mathcal N(+\mu,\Sigma)
$$

MSE 回归最优解接近条件均值：

$$
\hat a=\mathbb E[a|o]\approx0
$$

但 `0` 可能恰好撞向障碍物。

Diffusion Policy 的出发点就是：**不要把合法多模态动作压成一个均值。**

---

# 2. Raw Episode

一个典型 visuomotor dataset：

```text
episode/
├── rgb[t]
├── state[t]
├── action[t]
└── task metadata
```

训练不是逐帧独立抽样，而是切窗口：

```text
observation history:  t-To+1 ... t
action horizon:       t ... t+Ta-1
```

shape：

```text
RGB:    [B, To, V, C, H, W]
state:  [B, To, Ds]
action: [B, Ta, Da]
```

这里：

- `To`：observation horizon；
- `Ta`：prediction/action horizon。

二者作用不同。

---

# 3. Observation Encoder

视觉分支：

$$
I_{t-To+1:t}
\rightarrow
f_{vision}
\rightarrow
z_{vision}
$$

state 分支：

$$
s_{t-To+1:t}
\rightarrow
f_{state}
\rightarrow
z_{state}
$$

组合为 conditioning：

$$
c=f(o_{t-To+1:t})
$$

不同实现可以把 `c` 做成：

- 一个全局向量；
- 一组 temporal/spatial tokens；
- FiLM / cross-attention conditioning。

核心不变：**diffusion dynamics 发生在 action trajectory space，而 observation 提供条件。**

---

# 4. Action Trajectory 是被加噪的对象

干净 action chunk：

$$
A^0\in\mathbb R^{T_a\times D_a}
$$

前向扩散第 `k` 步：

$$
A^k=
\sqrt{\bar\alpha_k}A^0
+
\sqrt{1-\bar\alpha_k}\epsilon
$$

其中：

$$
\epsilon\sim\mathcal N(0,I)
$$

shape 不变：

```text
A^0: [B, Ta, Da]
A^k: [B, Ta, Da]
eps: [B, Ta, Da]
```

这很重要：**扩散过程没有把时间步 `Ta` 拆成独立动作。整个 trajectory 一起被建模。**

---

# 5. Noise Prediction Network

网络学习：

$$
\epsilon_\theta(A^k,k,c)
$$

输入有三类：

```text
noisy action trajectory
+
diffusion timestep
+
observation conditioning
```

输出：

```text
predicted noise [B, Ta, Da]
```

backbone 可以是 temporal U-Net、Transformer 等。

所以“Diffusion Policy”不是特指 U-Net；关键是训练目标和 action-trajectory generation mechanism。

---

# 6. Training Objective

最常见形式：

$$
\mathcal L=
\mathbb E_{A^0,k,\epsilon}
\left[
\|\epsilon-\epsilon_\theta(A^k,k,c)\|_2^2
\right]
$$

训练数据流：

```text
clean action chunk A0
→ sample k
→ sample epsilon
→ construct noisy Ak
→ network(Ak, k, observation condition)
→ predict epsilon
→ MSE
```

注意：policy 并没有在训练时真正执行 diffusion rollout；它随机抽一个 noise level 训练单步 denoising prediction。

---

# 7. Inference 才真正从 Noise 生成动作

初始化：

$$
A^K\sim\mathcal N(0,I)
$$

然后：

```text
K
↓ denoise
K-1
↓
...
↓
0
```

得到：

$$
\hat A^0
=[\hat a_t,\ldots,\hat a_{t+T_a-1}]
$$

这意味着 inference cost 和 denoising steps 强相关。

机器人里不能只看 model parameter count，还必须测：

$$
T_{infer}=N_{denoise}\times T_{network\ forward}
$$

---

# 8. 为什么 Action Horizon 很重要

如果只生成单步 action：

$$
p(a_t|o_t)
$$

无法显式建模未来动作间的 temporal consistency。

生成轨迹：

$$
p(a_{t:t+T_a-1}|o_{history})
$$

则可以表示：

- smooth approach；
- grasp timing；
- coordinated bimanual motion；
- multimodal path choice。

这也是生成式机器人策略的共同趋势。

---

# 9. 但为什么不能一次执行完整 Horizon

因为真实世界会偏离预测：

```text
object moved
contact slipped
human touched robot
camera changed
```

如果仍执行完整 old chunk，就是 open-loop。

Diffusion Policy 通常采用 receding horizon：

```text
observe To frames
→ sample Ta future actions
→ execute first Te actions
→ get new observations
→ sample again
```

其中：

$$
T_e<T_a
$$

---

# 10. 三个 Horizon 不能混

很多初学者会混淆：

### Observation horizon

$$
T_o
$$

模型看多少历史。

### Action prediction horizon

$$
T_a
$$

一次生成多少未来动作。

### Execution horizon

$$
T_e
$$

真正执行多少动作后重新规划。

三者决定：

- temporal context；
- trajectory coherence；
- reactivity；
- inference frequency。

---

# 11. Action Normalization

机器人 action 各维量纲不同：

```text
meters
radians
gripper scalar
joint position
```

训练前通常 normalization：

$$
\tilde a=(a-\mu)/\sigma
$$

或者映射到固定区间。

Diffusion 的 Gaussian noise 是加在 normalized action space。

执行前必须：

$$
a=\sigma\tilde a+\mu
$$

如果 action normalization 统计和 deployment robot 不一致，policy 会出现系统性 scale error。

---

# 12. Position Prediction vs Action Prediction

不同 dataset 的 `action` 可能是：

- absolute joint position；
- delta joint；
- Cartesian pose delta；
- velocity。

Diffusion Policy 本身并不规定物理 action interface。

所以复现时最先问：

> **这个仓库的 `action` 到底控制什么？**

不是先看 U-Net 层数。

---

# 13. 多视角视觉进入哪里

如果有多个 camera：

```text
cam0 image
cam1 image
cam2 image
```

可能：

- 各自 encode 后拼接；
- batch/view 维展开共享 encoder；
- token 级 attention fusion。

shape 示例：

```text
[B, To, V, C, H, W]
→ reshape
[B*To*V, C, H, W]
→ visual encoder
[B*To*V, D]
→ reshape/fuse
[B, To, V, D]
```

这就是“论文图里的一个 Vision Encoder”在代码中真正发生的 shape 变化。

---

# 14. 3D Diffusion Policy 为什么不是简单换输入

2D 图像 conditioning：

$$
c=f_{2D}(I)
$$

3D policy：

$$
c=f_{3D}(P)
$$

其中 point cloud：

$$
P\in\mathbb R^{N\times(3+F)}
$$

真正变化是 inductive bias：

- metric 3D geometry 显式进入 representation；
- camera appearance dependence 下降；
- coordinate frame / augmentation 变得更关键。

所以 DP3 类路线的核心问题是：**3D representation 是否让 action distribution 更贴近 physical geometry。**

---

# 15. Diffusion Policy 最大的系统成本：Latency

如果 100 次 denoising，每次网络 forward 5 ms：

$$
T_{infer}=500\,ms
$$

对于动态 manipulation 已经非常慢。

因此后续出现：

- fewer-step diffusion；
- flow matching；
- consistency / distillation；
- asynchronous execution。

生成建模质量和 real-time control 必须一起评价。

---

# 16. Minimal Reproduction

教材 `code/minimal/generative_actions.py` 已构造双峰动作：

$$
a=0.4c\pm1.5+noise
$$

比较：

- MSE regression；
- Diffusion；
- Flow Matching。

预期：

```text
regression → predicts near 0 (mode average)
diffusion  → samples both ± modes
flow       → samples both ± modes
```

这不是 benchmark success，但直接验证生成式 action model 最基本的机制。

---

# 17. 更强的最小实验

用 Push-T / 2D obstacle task：

设置两条合法路径。

比较：

```text
MSE BC
mixture density network
diffusion policy
flow-matching policy
```

控制：

- observation encoder；
- dataset；
- parameter budget；
- action horizon。

看 closed-loop success，而不是 action MSE。

---

# 18. Negative Controls

## A. Shuffle action time order

如果性能没下降，trajectory model 可能没真正利用 temporal structure。

## B. Replace observation condition with shuffled observation

如果性能仍高，task 可能存在 action prior shortcut。

## C. Same diffusion model, different execution horizon

分离：

- generative modeling gain；
- receding-horizon gain。

## D. Same architecture, regression objective

分离：

- U-Net/Transformer architecture；
- diffusion objective。

---

# 19. Failure Taxonomy

Diffusion Policy 失败不只一种：

1. observation representation wrong；
2. mode sampled but wrong mode for scene；
3. action scale/frame wrong；
4. denoising insufficient；
5. long inference latency；
6. stale action horizon；
7. contact mismatch；
8. OOD observation；
9. controller tracking failure。

---

# 20. Diffusion → Flow：真正要比较什么

不要只问：

> Diffusion 还是 Flow 更先进？

应该比较：

| 维度 | 问题 |
|---|---|
| Mode coverage | 多模态动作保留程度 |
| Sampling steps | 需要几次 network eval |
| Latency | 真机 end-to-end inference |
| Closed-loop success | 真正任务结果 |
| Horizon sensitivity | 长 chunk 是否退化 |
| Training stability | 对 data scale 的敏感性 |
| OOD robustness | 新场景/物体/动力学 |

---

# 一句话抓住 Diffusion Policy

> **Diffusion Policy 把机器人策略从“给一个 observation 回归一个动作”改写成“在 observation history 条件下生成一整段多模态连续动作分布，并在 receding-horizon 闭环中不断重采样未来”。它真正的价值与代价都来自这个改变。**
