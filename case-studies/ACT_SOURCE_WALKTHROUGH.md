# Source Walkthrough — ACT / ALOHA

> Repository: `tonyzhaozh/act`  
> Source snapshot inspected: `742c753c0d4a5d87076c8f69e5628c79a8cc5488`  
> Goal: trace **dataset → CVAE latent → multi-view vision → Transformer queries → action chunk → temporal aggregation → robot joint target**.

---

# 1. Start from the physical contract

In the inspected official implementation, `imitate_episodes.py` hardcodes:

```text
state_dim = 14
backbone  = ResNet18
ACT encoder layers = 4
ACT decoder layers = 7
attention heads    = 8
num_queries        = chunk_size
```

So the main robot state/action contract is:

\[
q_t\in\mathbb{R}^{14},
\qquad
A_t\in\mathbb{R}^{H\times14}.
\]

For ALOHA-style bimanual control, those 14 dimensions correspond to the two 7-D arm/gripper state/action vectors used by this codebase.

The important design change from stepwise BC is:

\[
a_t=\pi(o_t)
\]

becomes:

\[
A_t=[a_t,a_{t+1},\ldots,a_{t+H-1}]
=\pi(o_t).
\]

The policy predicts a short motor plan, not one control point.

---

# 2. Training entry: `imitate_episodes.py`

This file owns the full experiment loop:

```text
task config
→ dataset_dir / episode_len / camera_names
→ load_data(...)
→ dataset statistics
→ ACTPolicy
→ train_bc(...)
→ checkpoint
→ eval_bc(...)
```

The model is not trained on raw physical values directly. Dataset statistics are saved:

```text
dataset_stats.pkl
```

and evaluation reconstructs:

\[
q^{norm}=\frac{q-\mu_q}{\sigma_q},
\]

\[
a=\hat a^{norm}\sigma_a+\mu_a.
\]

So normalization is part of the deployable policy contract.

---

# 3. The batch contract

`forward_pass(...)` unpacks:

```text
image_data
qpos_data
action_data
is_pad
```

and calls:

```text
policy(qpos, image, action, is_pad)
```

Conceptually:

```text
image      [B, V, 3, H, W]
qpos       [B, 14]
actions    [B, H_a, 14]
is_pad     [B, H_a]
```

`ACTPolicy` truncates the action sequence and mask to:

```text
self.model.num_queries == chunk_size
```

Therefore the training target horizon is enforced at the policy boundary.

---

# 4. `ACTPolicy`: loss and train/inference split

Key file:

```text
policy.py
```

`ACTPolicy` constructs the model via:

```text
build_ACT_model_and_optimizer(...)
```

and stores `kl_weight`.

Images are normalized using ImageNet mean/std before model forward.

## Training

```text
a_hat, is_pad_hat, (mu, logvar)
    = model(qpos, image, env_state, actions, is_pad)
```

Reconstruction uses elementwise L1:

\[
L_{L1}
=
\operatorname{mean}
\left(
|A-\hat A|\odot\neg M_{pad}
\right).
\]

KL term:

\[
D_{KL}
=
-\frac12
\sum_j
(1+\log\sigma_j^2-\mu_j^2-\sigma_j^2).
\]

Total:

\[
L=L_{L1}+\beta D_{KL}.
\]

## Inference

At inference no expert action is provided:

```text
model(qpos, image, env_state)
```

The CVAE posterior is unavailable, so the source uses a zero latent sample rather than sampling a demonstration-conditioned posterior.

That detail matters: ACT’s latent primarily regularizes / structures training-time variation; the default inference path is deterministic with respect to that latent input.

---

# 5. The CVAE encoder in `detr/models/detr_vae.py`

The source defines:

```text
latent_dim = 32
encoder_action_proj : 14 → hidden_dim
encoder_joint_proj  : 14 → hidden_dim
latent_proj         : hidden_dim → 64
```

The encoder sequence is:

```text
[CLS]
+ qpos token
+ H action tokens
```

Shapes:

\[
A\in\mathbb{R}^{B\times H\times14}
\rightarrow
E_A\in\mathbb{R}^{B\times H\times D},
\]

\[
q\in\mathbb{R}^{B\times14}
\rightarrow
e_q\in\mathbb{R}^{B\times1\times D}.
\]

Then:

\[
E=[e_{CLS},e_q,E_A]
\in\mathbb{R}^{B\times(H+2)\times D}.
\]

After permutation to Transformer encoder convention, the CLS output is projected to:

\[
[\mu,\log\sigma^2]\in\mathbb{R}^{B\times64}.
\]

Split:

\[
\mu,\log\sigma^2\in\mathbb{R}^{B\times32}.
\]

Reparameterization:

\[
z=\mu+\sigma\odot\epsilon,
\qquad
\epsilon\sim\mathcal N(0,I).
\]

At inference:

\[
z=0.
\]

---

# 6. Multi-view visual path

For each configured camera:

```text
features, pos = backbone(image[:, cam_id])
features = last feature level
features = 1×1 projection to hidden_dim
```

Then all camera features are concatenated **along the feature-map width dimension**:

```text
src = cat(all_cam_features, axis=3)
pos = cat(all_cam_pos, axis=3)
```

This is an important source-level detail.

The camera dimension is not represented as an outer sequence axis at this stage; spatial maps are tiled/concatenated horizontally before Transformer processing.

This raises useful questions:

- does camera order matter?
- are camera boundaries explicitly encoded?
- would separate camera tokens or camera-ID embeddings improve transfer?

---

# 7. Proprioception and latent are additional Transformer conditions

Current qpos is projected:

\[
q_t\rightarrow e_q^{dec}\in\mathbb{R}^{B\times D}.
\]

Latent:

\[
z\rightarrow e_z\in\mathbb{R}^{B\times D}.
\]

The Transformer receives:

```text
visual source feature map
query embeddings (H action slots)
visual positional encoding
latent input
proprio input
additional learned positions
```

So the decoder’s H queries correspond to **future action positions**.

This is not language-style next-token generation.

All action slots are produced from parallel learned queries conditioned on the same current observation/context.

---

# 8. Output head

Transformer hidden states:

\[
H_{dec}\in\mathbb{R}^{B\times H\times D}
\]

are mapped by:

```text
action_head : D → 14
is_pad_head : D → 1
```

giving:

\[
\hat A\in\mathbb{R}^{B\times H\times14}.
\]

The padding head exists in model output, while the policy loss in the inspected `policy.py` primarily applies the provided `is_pad` mask to L1 action reconstruction.

---

# 9. Evaluation without temporal aggregation

In `eval_bc(...)`:

```text
query_frequency = num_queries
```

The policy is queried only when:

```text
t % query_frequency == 0
```

and the next action is selected by:

```text
raw_action = all_actions[:, t % query_frequency]
```

So a chunk of H predictions can be executed open-loop for H environment steps.

This is computationally efficient but vulnerable to perturbations inside the chunk.

---

# 10. Temporal aggregation changes the deployed policy

With `temporal_agg=True`:

```text
query_frequency = 1
```

A new action chunk is predicted every environment step.

The code stores all chunks in a large tensor:

```text
all_time_actions[t, t:t+H]
```

For current physical time `t`, it collects all previously predicted chunks that contain an estimate for that same action time.

Then applies exponential weights:

\[
w_i\propto e^{-ki},
\qquad k=0.01.
\]

Current action:

\[
a_t
=
\sum_i w_i\hat a_t^{(i)}.
\]

This is not part of the Transformer forward pass.

It is a **temporal executor / ensemble layer** outside the neural policy.

Therefore:

\[
\text{ACT checkpoint}\neq\text{ACT deployed system}.
\]

---

# 11. The final robot-facing action is joint target

After chunk prediction:

```text
raw_action
→ dataset-stat de-normalization
→ target_qpos
→ env.step(target_qpos)
```

The evaluated policy therefore ultimately produces normalized 14-D targets that become target joint positions in this environment API.

For the real robot path, `make_real_env` and ALOHA robot utilities define the lower-level actuation.

This is a very different physical interface from a Cartesian-delta VLA.

---

# 12. Training vs deployment graph

## Training

```text
multi-view images
current qpos
future expert action chunk
        ↓
CVAE encoder(qpos + action chunk)
        ↓ z

images → ResNet18 feature maps
qpos → proprio embedding
z → latent embedding
        ↓
Transformer + H query slots
        ↓
predicted H×14 action chunk
        ↓
masked L1 + β KL
```

## Inference

```text
multi-view images
current qpos
z = 0
        ↓
Transformer
        ↓
H×14 action chunk
        ↓
open-loop indexing OR temporal aggregation
        ↓
de-normalize
        ↓
target qpos
        ↓
robot environment / controller
```

---

# 13. What action chunking actually buys

Chunking changes three things simultaneously.

## 1. Temporal representation

Output is a local trajectory rather than a point.

## 2. Supervision density

One observation trains multiple future action positions.

## 3. Runtime compute

If chunks are executed open-loop, model inference is reduced from every control step to every H steps.

These benefits come with a trade-off:

\[
H\uparrow
\Rightarrow
\text{longer temporal coherence}
+
\text{lower inference rate}
-
\text{closed-loop responsiveness}.
\]

Temporal aggregation partially changes this by querying every step and combining overlapping chunks.

---

# 14. Source-level ablations worth running

## A. Chunk horizon

\[
H\in\{1,10,25,50,100\}.
\]

Measure:

- success;
- inference rate;
- trajectory smoothness;
- perturbation recovery.

## B. Open-loop vs temporal aggregation

Same checkpoint:

```text
execute each chunk directly
vs
query every step + exponential aggregation
```

This isolates executor gain from model gain.

## C. Latent ablation

Compare training with:

- KL/CVAE;
- no latent;
- shuffled latent;
- different latent dimensions.

The key question is whether training-time latent improves multimodal imitation or merely regularizes optimization.

## D. Camera-order intervention

Because camera maps are concatenated along width:

```text
normal camera order
vs
permuted order
vs
explicit camera-ID augmentation
```

## E. qpos removal / corruption

Measure how much visual ambiguity is resolved by proprioception.

## F. Action normalization error

Perturb dataset stats at deployment to quantify how easily system-level preprocessing overwhelms architecture quality.

---

# 15. ACT vs later flow/chunk policies

ACT already established two ideas that remain central in 2026:

1. predict a **trajectory chunk**;
2. separate the neural prediction from a **temporal execution strategy**.

Later flow/diffusion VLA systems change the action distribution model:

```text
ACT:
observation → deterministic/CVAE-conditioned parallel chunk regression

Diffusion / Flow:
observation + noise/time → iterative generative trajectory
```

But both still need decisions about:

- chunk horizon;
- replanning rate;
- overlap;
- controller interface.

ACT is therefore not an obsolete pre-VLA curiosity. It is a key ancestor of modern action-chunk architecture.

---

# 16. Final source-level mental model

\[
\boxed{
\text{ACT System}
=
\text{Multi-view Visual Encoder}
+
\text{Proprioception}
+
\text{CVAE Training Latent}
+
\text{Parallel Action Queries}
+
\text{Chunk Executor / Temporal Aggregation}
+
\text{Joint-Target Controller Interface}
}
\]

The Transformer is only one component.

The deeper lesson is that **temporal abstraction and execution policy are part of robot intelligence**, not afterthoughts added after model training.
