# Source Walkthrough — SmolVLA + LeRobot Runtime

> Repository: `huggingface/lerobot`  
> Source snapshot inspected: `8c894413c0967d83624d17a440afd70754fddb01` (2026-09-13)  
> Goal: trace a modern small/open VLA from tensors to action queue and RTC, not just explain its architecture diagram.

---

# 1. The source-level system

SmolVLA is implemented as more than a model class. The execution stack is roughly:

```text
LeRobotDataset / processor
        ↓
image / language / state batch
        ↓
SmolVLAPolicy
        ↓
VLAFlowMatching
  ├─ SmolVLM prefix
  └─ action expert suffix
        ↓
flow integration
        ↓
action chunk
        ↓
queue OR RTC / async executor
        ↓
robot-specific action postprocess
        ↓
robot driver
```

This is exactly why LeRobot is useful for this textbook: policy, dataset, camera, motor, robot and runtime are exposed in one ecosystem.

---

# 2. Configuration defines the physical contract

Key file:

```text
src/lerobot/policies/smolvla/configuration_smolvla.py
```

Default values visible in source:

```text
n_obs_steps       = 1
chunk_size        = 50
n_action_steps    = 50
max_state_dim     = 32
max_action_dim    = 32
num_steps         = 10
image size        = 512 × 512 padded
language max len  = 48
freeze vision     = True
train expert only = True
train state proj  = True
```

VLM backbone:

```text
HuggingFaceTB/SmolVLM2-500M-Video-Instruct
```

Default normalization:

```text
visual : identity
state  : mean/std
action : mean/std
```

Therefore the model’s default action tensor is conceptually:

\[
A\in\mathbb{R}^{B\times 50\times D_a},
\qquad D_a\le32.
\]

The chunk horizon is not hidden in an evaluator script. It is a first-class config contract.

---

# 3. `SmolVLAPolicy`: wrapper, queue and robot-facing semantics

Key file:

```text
src/lerobot/policies/smolvla/modeling_smolvla.py
```

`SmolVLAPolicy` wraps `VLAFlowMatching`.

Its key responsibilities are not merely neural-network forwarding:

- input preparation;
- image normalization;
- state/action padding;
- ALOHA-specific action-space conversion;
- action queue management;
- RTC initialization;
- training loss reduction;
- chunk vs single-action inference API.

This immediately demonstrates:

> a deployable VLA policy class contains **representation + action semantics + temporal execution policy**.

---

# 4. Two inference APIs expose two temporal regimes

## 4.1 `select_action`

This method is intended for ordinary one-step environment interaction.

Internally it keeps:

```text
ACTION: deque(maxlen=n_action_steps)
```

When the queue is empty:

```text
observation
→ generate full chunk
→ enqueue first n_action_steps
```

Then each environment step does:

```text
queue.popleft()
```

Conceptually:

\[
\hat A_t=[a_t,a_{t+1},\ldots,a_{t+H-1}],
\]

but execution is:

\[
a_t, a_{t+1},\ldots
\]

without replanning until queue refresh.

This is a temporal executor decision, not a neural-network property.

## 4.2 `predict_action_chunk`

This returns the entire predicted chunk.

It is the correct API when RTC / asynchronous inference is used.

Source explicitly rejects RTC in `select_action` and instructs callers to use chunk prediction instead.

Thus:

```text
single-action API
≠
RTC-capable chunk API
```

---

# 5. Images are explicitly normalized and masked

`prepare_images()` handles multiple cameras.

For each present image feature:

1. take latest frame if a temporal dimension exists;
2. resize with padding;
3. map pixels:

\[
[0,1]\rightarrow[-1,1]
\]

for SigLIP-style visual encoding;
4. create presence mask.

Missing cameras can be replaced by padded empty images with zero masks.

This is useful for multi-camera robot datasets where some embodiments lack a camera used by others.

Research implication:

> camera absence is encoded both as an image tensor and a mask. A model can potentially learn camera-layout identity from missing-camera patterns.

That deserves a negative control in cross-embodiment studies.

---

# 6. Robot-specific action conversion is inside the policy

The source contains explicit ALOHA conversion code:

- flips selected joint signs;
- maps gripper representation between spaces;
- converts state/action conventions used by a prior runtime.

This is extremely important pedagogically.

The model sees a normalized semantic action space, while the hardware may use another convention.

So:

\[
A_{model}\neq A_{hardware}
\]

in general.

Cross-robot reproduction must inspect these conversion functions before comparing policies.

---

# 7. `VLAFlowMatching`: VLM prefix + action-expert suffix

The source class itself draws the conceptual architecture:

```text
images ───────┐
language ─────┼→ VLM ── KV cache ─┐
state ────────┘                    │
                                  ↓
noise/action+timestep → Action Expert
                                  ↓
                               actions
```

The implementation creates:

```text
SmolVLMWithExpertModel
state_proj
action_in_proj
action_out_proj
action_time_mlp
```

There are therefore two representation widths:

- VLM hidden space;
- action-expert hidden space.

---

# 8. Prefix: images + language + state

`embed_prefix(...)` builds a sequence containing:

```text
image embeddings
language embeddings
state embedding
```

## 8.1 Image embeddings

Images are embedded by the visual component and scaled by square root of embedding dimension.

## 8.2 Language embeddings

Language token embeddings are similarly normalized/scaled.

## 8.3 State

State is projected:

\[
s\in\mathbb{R}^{B\times D_s}
\rightarrow
z_s\in\mathbb{R}^{B\times D_{VLM}}.
\]

The attention-mask construction explicitly controls which token groups can attend to later state/action tokens.

This is not a single flat concatenation.

---

# 9. Suffix: noisy action + flow time

`embed_suffix(noisy_actions, timestep)` performs:

\[
a_t\rightarrow W_a a_t
\]

and computes sinusoidal time embedding:

\[
e(t).
\]

Then concatenates:

\[
[W_a a_t\;\Vert\; e(t)]
\]

and processes it through an MLP before entering the action expert.

So the action suffix carries both:

- current noisy trajectory state;
- where the sample currently lies along the flow path.

---

# 10. Training objective: flow matching

Source training code uses:

\[
x_t=t\epsilon+(1-t)A,
\]

where:

- \(A\) is clean action chunk;
- \(\epsilon\) is sampled noise.

Target velocity:

\[
u_t=\epsilon-A.
\]

This parameterizes the path from data at \(t=0\) toward noise at \(t=1\).

The model predicts:

\[
v_\theta(x_t,t\mid I,l,s).
\]

Loss is elementwise MSE:

\[
L=\|v_\theta-u_t\|^2.
\]

Note that GR00T N1.7 uses the opposite interpolation orientation in its implementation:

\[
x_t=(1-t)\epsilon+tA,
\quad
u=A-\epsilon.
\]

These are not contradictory. They correspond to opposite time parameterization conventions.

The important invariant is:

> the vector field transports between noise and clean action conditional on robot context.

---

# 11. VLM + expert forward is split into prefix and suffix

Training creates:

```text
prefix_embs = images + language + state
suffix_embs = noisy action + time
```

Then `SmolVLMWithExpertModel.forward(...)` processes both streams.

Only the final action-suffix outputs are retained:

```text
suffix_out[:, -chunk_size:]
```

and projected to action velocity.

This is a clean implementation of:

```text
semantic / perceptual context
        ↓
continuous action expert
```

rather than action tokens appended to ordinary language decoding.

---

# 12. Inference reuses a prefix KV cache

`sample_actions(...)` first computes prefix embeddings from:

```text
images + language + state
```

Then it runs the VLM prefix once and caches key/value tensors.

The denoising loop only recomputes the action suffix.

This reduces repeated cost because the visual-language context is constant during one action-chunk sample.

Conceptually:

```text
prefix encode once
      ↓ cache
for k = 1..10:
    action suffix(t_k)
    → expert using prefix cache
    → velocity
    → Euler step
```

Default decoding steps:

\[
N=10.
\]

This is a concrete model/runtime co-design choice.

---

# 13. `denoise_step`: suffix-only repeated computation

At each step:

1. embed noisy action + current time;
2. construct suffix attention masks;
3. reuse prefix `past_key_values`;
4. run VLM/expert suffix;
5. crop cache back to prefix length;
6. project suffix output to action velocity.

This shows why the architecture can be much cheaper than rerunning the entire VLM ten times.

A useful profiling experiment is to measure:

```text
prefix time
+ 10 × suffix time
```

instead of reporting only total policy latency.

---

# 14. RTC path in LeRobot

Key file:

```text
src/lerobot/policies/rtc/modeling_rtc.py
```

The RTC processor wraps an existing denoiser.

Inputs include:

```text
current latent chunk x_t
previous unexecuted chunk
inference delay
execution horizon
flow time
base denoiser
```

## 14.1 Prefix weights

The processor constructs a temporal weight vector over the chunk.

Supported schedules include:

- zeros / hard prefix;
- ones;
- linear;
- exponential.

The weights encode how strongly each position in the new chunk should agree with the leftover previous chunk.

## 14.2 Predict current clean trajectory

The implementation forms an estimate of clean endpoint:

\[
\hat x_1=x_t-time\cdot v_t.
\]

Then prefix error:

\[
e=(A_{prev}-\hat x_1)\odot w.
\]

## 14.3 Autograd correction

The source computes gradient of the predicted endpoint with respect to current latent:

\[
\frac{\partial \hat x_1}{\partial x_t},
\]

using `torch.autograd.grad`.

This yields a correction direction that asks:

> how should the current flow velocity change so its clean endpoint better matches the still-relevant previous action prefix?

The final velocity is:

\[
v_{RTC}=v_t-\gamma(t)\,c_t,
\]

with guidance weight clamped by configuration.

This is qualitatively different from simple linear blending after sampling.

---

# 15. Three temporal layers coexist

SmolVLA / LeRobot makes the distinction explicit:

```text
1. chunk_size = 50
2. n_action_steps = 50 by default
3. RTC / async execution may overlap or replace chunks before full execution
```

Thus `chunk_size` is a model output horizon, while actual executed horizon is a runtime decision.

In deployment you should log:

- chunk size;
- execution horizon;
- inference delay;
- overlap length;
- action age;
- queue length.

Without these, a “SmolVLA result” is underspecified.

---

# 16. Fine-tuning boundaries

Defaults:

```text
freeze_vision_encoder = True
train_expert_only      = True
train_state_proj       = True
```

The policy also exposes PEFT targets focused on:

- expert q/v projections;
- state projection;
- action projections;
- action-time MLP.

A strong ablation should distinguish:

```text
expert-only adaptation
vs
state/action projector adaptation
vs
VLM adaptation
vs
full adaptation
```

rather than treating all as “fine-tuning”.

---

# 17. Five experiments worth running

## A. Queue vs RTC

Same checkpoint:

```text
execute full queue
vs
async chunk generation
vs
RTC-guided overlap
```

Measure:

- action discontinuity;
- task cycle time;
- failure recovery;
- p95 latency.

## B. Flow decoding steps

\[
N\in\{2,5,10,20\}.
\]

Measure quality vs latency.

## C. Missing-camera identity leak

Compare:

```text
real missing-camera mask
randomized missing-camera pattern
all-camera standardized input
```

Question:

> is the policy using camera absence as a hidden embodiment identifier?

## D. Expert-only vs broader fine-tuning

Keep data fixed.

Test whether motor precision gain requires updating the VLM or only action expert.

## E. ALOHA conversion ablation

Intentionally perturb sign / gripper conversion in a controlled simulator.

This demonstrates how “small” action convention bugs dominate model performance.

---

# 18. Why SmolVLA matters scientifically

SmolVLA’s value for this textbook is not just parameter count.

It exposes in one readable codebase:

```text
VLM
+
continuous flow action expert
+
action queue
+
RTC
+
robot-specific conversion
+
LeRobot dataset/runtime/hardware stack
```

This makes it ideal for studying a central 2026 question:

> **where does the model end and the robot system begin?**

The source answer is: there is no single clean boundary. Policy quality depends on preprocessing, action semantics, temporal execution and hardware interface together.
