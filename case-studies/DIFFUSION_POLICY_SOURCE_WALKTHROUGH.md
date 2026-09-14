# Source Walkthrough — Diffusion Policy

> Repository: `real-stanford/diffusion_policy`  
> Source snapshot inspected: `5ba07ac6661db573af695b419a7947ecb704690f`  
> Goal: trace **observation history → normalized action trajectory → DDPM training → iterative denoising → executable action window → timestamped real-robot commands**.

---

# 1. Start from config: horizon is not the executed horizon

Key config:

```text
diffusion_policy/config/train_diffusion_unet_image_workspace.yaml
```

Default image-policy values in the inspected config:

```text
horizon          = 16
n_obs_steps      = 2
n_action_steps   = 8
n_latency_steps  = 0
num_train_steps  = 100
num_infer_steps  = 100
prediction_type  = epsilon
backbone          ResNet18
crop              76 × 76
```

This immediately defines three different temporal quantities:

\[
T_{model}=16,
\qquad
T_{obs}=2,
\qquad
T_{exec}=8.
\]

A common misunderstanding is to call all three “action horizon”.

They play different roles:

- `horizon`: length of the denoised trajectory tensor;
- `n_obs_steps`: observation history used for conditioning;
- `n_action_steps`: slice actually returned for execution.

---

# 2. Policy tensor contract

Key file:

```text
diffusion_policy/policy/diffusion_unet_image_policy.py
```

The constructor reads:

```text
action_dim = shape_meta['action']['shape'][0]
obs_feature_dim = obs_encoder.output_shape()[0]
```

So action tensor is:

\[
A\in\mathbb{R}^{B\times T\times D_a}.
\]

Observation inputs are dictionaries of modalities, typically each shaped:

\[
O_k\in\mathbb{R}^{B\times T_o\times\cdots}.
\]

The policy supports two conditioning patterns:

1. `obs_as_global_cond=True` — observation features become a global conditioning vector;
2. inpainting-style condition — observation features occupy the trajectory tensor and are masked as known.

The default inspected config uses **global conditioning**.

---

# 3. Observation encoder path

For global conditioning:

```text
normalize obs
→ take first n_obs_steps
→ flatten B×T_obs
→ MultiImageObsEncoder
→ reshape back to [B, T_obs·D_obs]
```

Mathematically:

\[
O_{1:T_o}
\xrightarrow{f_{obs}}
Z_o
\in\mathbb{R}^{B\times (T_oD_o)}.
\]

This becomes `global_cond` for the 1D conditional U-Net.

The action trajectory remains the denoised object.

---

# 4. Training normalization is part of the learned problem

The workspace obtains:

```text
normalizer = dataset.get_normalizer()
```

and installs it into both model and EMA model.

Training uses:

```text
nobs     = normalizer.normalize(batch['obs'])
nactions = normalizer['action'].normalize(batch['action'])
```

Thus the model learns diffusion geometry in **normalized action space**, not raw physical units.

Again:

\[
\pi_{deploy}
=
Decode_{normalizer}
\circ
\pi_{diffusion}
\circ
Encode_{normalizer}.
\]

Changing normalizer changes the effective policy.

---

# 5. Forward diffusion during training

Let clean normalized trajectory be:

\[
x_0=A^{norm}.
\]

The source samples Gaussian noise:

\[
\epsilon\sim\mathcal N(0,I)
\]

and a random diffusion timestep:

\[
t\sim Uniform\{0,\ldots,T_D-1\}.
\]

Then scheduler constructs:

\[
x_t
=
\sqrt{\bar\alpha_t}x_0
+
\sqrt{1-\bar\alpha_t}\epsilon.
\]

In code:

```text
noisy_trajectory = noise_scheduler.add_noise(
    trajectory, noise, timesteps
)
```

The policy is trained to reverse this corruption conditional on observation context.

---

# 6. Conditional U-Net predicts noise residual by default

The source calls:

```text
pred = model(
    noisy_trajectory,
    timesteps,
    global_cond=global_cond
)
```

Default scheduler config:

```text
prediction_type = epsilon
```

so target is:

\[
y=\epsilon.
\]

Loss:

\[
L
=
\mathbb E
\left[
\|\epsilon_\theta(x_t,t,Z_o)-\epsilon\|^2
\right].
\]

If scheduler uses `prediction_type=sample`, target becomes clean trajectory instead.

This configurability matters when comparing forks/checkpoints.

---

# 7. Mask generator makes the same policy support inpainting-style conditioning

The source creates:

```text
LowdimMaskGenerator(...)
```

During training:

```text
condition_mask = mask_generator(trajectory.shape)
loss_mask = ~condition_mask
noisy_trajectory[condition_mask] = cond_data[condition_mask]
```

and loss is multiplied by `loss_mask`.

For the default global-observation setup, action dimensions are not visible and observation context is external global conditioning.

But the same code structure can support known segments embedded in trajectory tensors.

This is conceptually useful for constrained / inpainting-style action generation.

---

# 8. Inference starts from a full random trajectory

`conditional_sample(...)` begins:

\[
x_T\sim\mathcal N(0,I)
\]

with the exact shape of condition data.

For global observation conditioning:

\[
x_T\in\mathbb{R}^{B\times16\times D_a}
\]

under the inspected default config.

Scheduler timesteps are set to:

```text
num_inference_steps = 100
```

then for each reverse step:

1. re-apply known conditioning if any;
2. predict model output;
3. call scheduler `step`;
4. replace trajectory with `.prev_sample`.

So inference is a full iterative generative process, not one forward pass.

---

# 9. Denoised trajectory is larger than executed action window

After sampling:

```text
naction_pred = nsample[..., :Da]
action_pred = unnormalize(naction_pred)
```

Then source selects:

```text
start = To - 1
end   = start + n_action_steps
action = action_pred[:, start:end]
```

With defaults:

\[
T_o=2,
\qquad
n_{action}=8,
\]

so returned executable window is approximately trajectory indices:

\[
[1,2,\ldots,8].
\]

This is a crucial architecture/runtime distinction:

```text
predicted trajectory length = 16
executed slice length       = 8
```

The first index alignment is tied to observation history.

---

# 10. Why the action window starts at `To - 1`

The predicted horizon is aligned with a temporal window that includes observation context.

If observations cover two recent steps, the action slice begins near the last observed state.

Conceptually:

```text
obs:        o_{t-1}, o_t
trajectory: [ ... aligned around t ... ]
execute:                 a_t ...
```

This alignment is easy to destroy when porting the model to a new dataloader.

A one-step indexing error is a real physical latency/error, not a cosmetic tensor bug.

---

# 11. Training workspace: policy + dataset + EMA + rollout

Key file:

```text
diffusion_policy/workspace/train_diffusion_unet_image_workspace.py
```

The workspace does:

```text
Hydra config
→ instantiate policy
→ instantiate dataset
→ dataset normalizer
→ DataLoader
→ EMA copy
→ optimizer / LR scheduler
→ environment runner
→ train loop
→ validation
→ rollout
→ checkpoints
```

This is a good example of a reproducible robot-learning experiment where **model training and task rollout are first-class in the same workspace**.

---

# 12. EMA is the evaluated policy by default

When enabled:

```text
self.ema_model = copy.deepcopy(self.model)
```

and after each optimization step:

```text
ema.step(self.model)
```

During evaluation:

```text
policy = self.ema_model
```

So the deployed/evaluated checkpoint is not simply the raw last optimizer parameters.

A reproduction that disables EMA has changed the method.

The config comment also notes BatchNorm interaction and therefore uses GroupNorm in the visual backbone path.

---

# 13. Real-robot execution contains a hidden timing algorithm

Key file:

```text
eval_real_robot.py
```

The policy loop explicitly records:

```text
obs_timestamps
inference latency
steps_per_inference
command latency
action execution latency
```

After `predict_action`, action timestamps are constructed relative to the **last observation timestamp**.

Conceptually:

\[
t^{cmd}_i
=
t^{obs}_{last}
+(i+offset)\Delta t.
\]

Then the code checks which predicted actions are still in the future:

```text
is_new = action_timestamps > current_time + action_exec_latency
```

Already-stale actions are discarded.

This is extremely important.

The real system is not:

```text
predict 8 actions → execute all 8
```

but:

```text
predict 8 timestamped actions
→ account for inference time
→ drop actions whose intended execution time already passed
→ execute remaining future targets
```

---

# 14. Over-budget fallback reveals stale-action failure explicitly

If **all** predicted actions are already stale:

```text
if sum(is_new) == 0:
    use last target pose only
    schedule it for next available control step
```

The runtime prints `Over budget`.

This is a strong source-level lesson:

> latency can destroy an otherwise correct trajectory before it reaches the robot.

The model’s offline action quality does not tell you whether any of those actions survive the timing filter.

---

# 15. Real-robot action conversion is task-specific

The inspected script supports a 2-D task action that is converted into target TCP pose updates.

Depending on `delta_action`:

- action may be interpreted as delta translation;
- or inserted into selected components of a target pose.

Then workspace bounds clip target positions before `env.exec_actions(...)`.

So physical semantics are:

```text
Diffusion model output
→ task-specific action conversion
→ target pose
→ workspace clipping
→ timestamp scheduling
→ robot environment/controller
```

Again, the diffusion model is only one layer.

---

# 16. The full training graph

```text
DEMONSTRATION EPISODES
  obs history + action trajectory
        ↓
dataset normalizer
        ↓
obs encoder (ResNet18 / multi-image)
        ↓
global context

normalized action trajectory
        ↓
random diffusion timestep t
+ Gaussian noise ε
        ↓
noisy trajectory x_t
        ↓
Conditional U-Net 1D
        ↓
predicted ε
        ↓
MSE on unconditioned elements
        ↓
optimizer + EMA
```

---

# 17. The full deployment graph

```text
latest real observations
+ timestamps
        ↓
normalizer
        ↓
obs encoder
        ↓
random action trajectory
        ↓
100-step DDPM reverse process
        ↓
16-step predicted trajectory
        ↓
slice 8 executable steps
        ↓
unnormalize
        ↓
task-specific pose conversion
        ↓
attach timestamps to each action
        ↓
drop stale actions after inference
        ↓
execute surviving future commands
```

This graph is the actual scientific object.

---

# 18. Five errors that can be misdiagnosed as “diffusion failure”

## A. Observation/action alignment off by one

Wrong slice start changes physical timing.

## B. Normalizer mismatch

Model outputs plausible normalized values but wrong physical scale.

## C. Inference too slow

Most generated actions are stale before execution.

## D. Task-specific conversion wrong

The 2-D/pose mapping can be wrong even if model predicts correct abstract action.

## E. Controller/robot cannot track timestamped poses

The learned trajectory is dynamically infeasible.

---

# 19. Source-level ablations worth running

## A. Inference steps

\[
N_{infer}\in\{10,25,50,100\}.
\]

Measure jointly:

- offline action MSE;
- task success;
- inference latency;
- fraction of actions discarded as stale.

This is better than measuring only sampling quality.

## B. Action horizon vs executed horizon

Keep model horizon 16 and vary:

\[
n_{action}\in\{1,4,8,15\}.
\]

Measure closed-loop recovery.

## C. Observation history

\[
T_o\in\{1,2,4\}.
\]

Test tasks with velocity/occlusion ambiguity.

## D. EMA

Same trained run:

```text
raw model
vs
EMA model
```

## E. Global conditioning vs inpainting-style conditioning

Use same observation encoder and data.

This isolates how temporal conditioning enters the U-Net.

## F. Latency injection

Add controlled delay after sampling.

Compare:

```text
naive execute-all
vs
timestamp stale-action filtering
```

This demonstrates why system timing belongs in policy evaluation.

---

# 20. Diffusion Policy vs ACT

Both predict action trajectories, but their action-distribution assumptions differ.

## ACT

```text
observation
→ Transformer parallel queries
→ H action vectors
```

with CVAE regularization in training.

## Diffusion Policy

```text
observation context
+ random trajectory
→ iterative denoising
→ H action vectors
```

Thus:

- ACT has one main model forward per chunk;
- diffusion has many denoising forwards;
- diffusion can represent complex multimodal trajectory distributions more explicitly;
- latency cost becomes more severe.

Both still require an external decision about **how many predicted actions to execute before replanning**.

---

# 21. Diffusion Policy vs modern flow VLA

Modern flow policies preserve the same high-level idea:

> generate a continuous action trajectory conditioned on robot context.

But replace discrete stochastic diffusion timesteps with a learned continuous vector field and often far fewer integration steps.

Compare source defaults:

```text
Diffusion Policy image config: 100 reverse steps
SmolVLA:                       10 flow steps
GR00T N1.7:                     4 flow steps
```

These are not apples-to-apples architectures/data, but they clearly show why **sampling latency became a central design pressure**.

---

# 22. Final source-level mental model

\[
\boxed{
\text{Diffusion Policy System}
=
\text{Observation Encoder}
+
\text{Conditional Action Diffusion}
+
\text{Trajectory Slice Rule}
+
\text{Normalizer}
+
\text{Timestamp / Stale-Action Runtime}
+
\text{Task Controller}
}
\]

The most important source-code lesson is not merely “diffusion models robot actions”.

It is:

> **a generated trajectory only becomes a robot policy after temporal alignment, physical decoding and deadline-aware execution are defined.**
