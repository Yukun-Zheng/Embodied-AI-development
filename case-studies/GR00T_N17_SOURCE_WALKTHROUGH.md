# Source Walkthrough — NVIDIA GR00T N1.7

> Repository: `NVIDIA/Isaac-GR00T`  
> Source snapshot inspected: `51d4c89f72fda44cbf77285c6a8114b52676b8a1` (2026-08-20 main)  
> Model release anchor: `n1.7-release`, published 2026-04-18.

This walkthrough is not a product summary. It reconstructs the actual dataflow exposed by the open source implementation.

---

# 1. Start from the config, not the architecture figure

Key file:

```text
gr00t/configs/model/gr00t_n1d7.py
```

The default `Gr00tN1d7Config` makes several system contracts explicit:

```text
backbone            Cosmos-Reason2-2B / Qwen3-VL architecture
backbone dim         2048
max state dim        132
max action dim       132
action horizon       40
state history        1
DiT hidden size      1024
input embedding dim  1536
DiT layers           16
attention heads      32
flow inference steps 4
max embodiments      32
```

The first scientific lesson is immediate:

> N1.7 is not a scalar-action policy. The action stack is designed around a padded multi-embodiment tensor contract.

A useful abstract input contract is therefore:

\[
S\in\mathbb{R}^{B\times T_s\times D_s},
\qquad
A\in\mathbb{R}^{B\times H\times D_a},
\]

with default maxima:

\[
T_s=1,\quad D_s\le132,\quad H\le40,\quad D_a\le132.
\]

Different robots occupy different valid subsets through masks / embodiment-specific processing.

---

# 2. Processor: raw episode → VLM + state/action tensors

Key file:

```text
gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py
```

The processor is not boilerplate. It defines the effective learning problem.

## 2.1 Visual-language collation

`Gr00tN1d7DataCollator` collects `vlm_content` and calls a `Qwen3VLProcessor` with:

```text
text
images
→ input_ids
→ attention_mask
→ pixel_values / image-grid metadata
```

Other fields such as:

```text
state
state_mask
action
action_mask
embodiment_id
```

are stacked into batch tensors.

So the model sees two semantically different streams:

```text
VLM stream
  text + images

robot stream
  state + action + masks + embodiment_id
```

They meet later in the action head.

## 2.2 Normalization is part of the model

The processor wraps a `StateActionProcessor`, with switches such as:

```text
use_percentiles
clip_outliers
use_relative_action
apply_sincos_state_encoding
```

This means a model comparison that changes preprocessing has changed the policy, even if checkpoint architecture is unchanged.

## 2.3 Horizon validation

The code checks every embodiment’s configured `action.delta_indices` against the model’s `max_action_horizon`.

That is a valuable design lesson:

> action horizon is a **schema constraint**, not merely a training hyperparameter.

Without such validation, a data/model mismatch can survive until the first forward pass.

---

# 3. Embodiment conditioning is explicit

Two source locations matter:

```text
gr00t/data/embodiment_tags.py
processing_gr00t_n1d7.py
```

The processor contains a mapping from physical embodiment tags to projector indices.

The source comments explicitly distinguish:

- same physical robot represented by multiple data-source/subtask tags;
- a genuinely new embodiment requiring a new projector index.

This is more informative than a generic `robot_id`.

It lets us formulate a concrete experiment:

```text
correct embodiment tag
wrong physical-robot tag
same robot / different dataset-source tag
random tag
no tag
unseen embodiment
```

Measure not only task success but intermediate action distribution.

If wrong tags barely affect behavior, embodiment conditioning may be weak or redundant.

---

# 4. Backbone → action head boundary

Main model file:

```text
gr00t/model/gr00t_n1d7/gr00t_n1d7.py
```

`Gr00tN1d7` constructs:

```text
Qwen3Backbone
+
Gr00tN1d7ActionHead
+
Gr00tN1d7DataCollator
```

The backbone is selected when model name matches Cosmos-Reason2 / Qwen3-VL.

The source class documents N1.7 as a VLA with **Cosmos-Reason2-2B (Qwen3-VL) backbone**.

The action head consumes backbone output containing approximately:

\[
Z_{VL}\in\mathbb{R}^{B\times N\times D_{VL}},
\]

where default backbone embedding dimension is 2048.

The policy therefore does not directly concatenate raw pixels with action vectors. It first obtains contextual vision-language features.

---

# 5. State encoder is embodiment-conditioned

The action head creates:

```text
CategorySpecificMLP state_encoder
MultiEmbodimentActionEncoder action_encoder
CategorySpecificMLP action_decoder
```

The state encoder receives:

\[
S\in\mathbb{R}^{B\times T_s\times D_s}
\]

and reshapes history into one feature vector per sample:

\[
[B,T_s,D_s]\rightarrow[B,1,T_sD_s].
\]

Then:

\[
z_s=f_{state}(S,e),
\]

where \(e\) is `embodiment_id`.

So embodiment affects both encoding and decoding, not only a prompt token.

---

# 6. Training target: flow-matching velocity

The training path is especially clean.

Given clean action chunk:

\[
A\in\mathbb{R}^{B\times H\times D_a},
\]

sample Gaussian noise:

\[
\epsilon\sim\mathcal N(0,I).
\]

Sample time \(t\) from a configured Beta distribution, then build:

\[
A_t=(1-t)\epsilon+tA.
\]

The target vector field is:

\[
v^*=A-\epsilon.
\]

In code this is exactly the logic:

```text
noise = randn_like(actions)
noisy_trajectory = (1 - t) * noise + t * actions
velocity = actions - noise
```

The noisy action is embedded with:

```text
action_encoder(noisy_trajectory, timestep, embodiment_id)
```

Then state and action tokens are joined:

```text
[state feature | action features]
```

and processed by a DiT / AlternateVLDiT conditioned on vision-language features.

Finally:

```text
action_decoder(..., embodiment_id)
```

predicts velocity.

Masked MSE:

\[
L=
\frac{
\sum M\odot\|\hat v-v^*\|^2
}{
\sum M+\epsilon
}.
\]

The mask is essential because different embodiments need not use all 132 padded action dimensions.

---

# 7. Why the action path is not “VLM predicts joints”

The actual chain is:

```text
images + language
→ Qwen3-VL-style backbone
→ contextual VL features

state + embodiment
→ embodiment-conditioned state encoder

noise action chunk + t + embodiment
→ multi-embodiment action encoder

[state tokens + action tokens]
        ×
VL cross-attention context
→ AlternateVLDiT / DiT
→ embodiment-conditioned action decoder
→ velocity field
```

This is a **conditional continuous trajectory generator**, not next-token regression.

---

# 8. Inference: four-step Euler integration by default

At inference the action chunk starts from noise:

\[
A_0\sim\mathcal N(0,I),
\qquad
A_0\in\mathbb{R}^{B\times40\times132}
\]

under the default config.

The source uses:

\[
dt=\frac{1}{N},
\]

with default:

\[
N=4.
\]

At each step:

1. encode current action trajectory;
2. concatenate with state feature;
3. condition on VL features;
4. predict velocity;
5. Euler update:

\[
A\leftarrow A+dt\cdot \hat v.
\]

The final tensor is returned as `action_pred`.

The scientific trade-off is visible directly:

\[
N_{steps}
\leftrightarrow
\text{sampling quality}
\leftrightarrow
\text{latency}.
\]

---

# 9. RTC is implemented inside the action-generation process

One of the most important source-level findings is that RTC is not just external trajectory blending.

When a previous action chunk is supplied, code interprets it as RTC mode.

Inputs include:

```text
action_horizon
rtc_overlap_steps
rtc_frozen_steps
rtc_ramp_rate
```

## 9.1 Overlap initialization

The overlapping prefix of the new action trajectory is initialized from the previous chunk rather than random noise.

Conceptually:

\[
A_0^{new}[0:K]
\leftarrow
A^{old}[H-K:H].
\]

## 9.2 Frozen latency region

A velocity-strength mask is set to zero for `rtc_frozen_steps`.

Those actions are effectively held fixed during denoising because they may correspond to time already consumed by policy latency.

## 9.3 Ramp region

Between frozen and fully editable actions, an exponential ramp increases velocity update strength from near 0 to 1.

Thus the new chunk is not stitched by a hard boundary.

It is gradually allowed to diverge from the old plan.

This is a concrete implementation of:

> **latency-aware action generation**.

---

# 10. State dropout is a deliberate robustness mechanism

The default config contains a large state dropout probability.

During training, state feature can be zeroed for selected samples.

This is scientifically interesting because it pushes the model not to over-rely on perfect proprioception.

But it also creates an ablation opportunity:

```text
state_dropout = 0
vs
state_dropout > 0
vs
exclude_state = True
```

Measure:

- nominal accuracy;
- sensor/state corruption robustness;
- embodiment transfer;
- recovery after observation mismatch.

---

# 11. Freeze / tune boundaries are explicit

N1.7 exposes separate switches for:

```text
tune_llm
tune_visual
tune_projector
tune_diffusion_model
tune_vlln
```

Therefore “fine-tuning GR00T” is underspecified.

A reproduction must state exactly which subsystems receive gradients.

Recommended ablation matrix:

| VLM | visual | state/action projector | DiT | question |
|---|---|---|---|---|
| frozen | frozen | train | train | action adaptation only |
| frozen | frozen | train | frozen | projector capacity |
| top layers | frozen | train | train | semantic adaptation |
| train | train | train | train | full co-adaptation |

---

# 12. Processor-level details can dominate policy behavior

The preprocessing layer includes:

- crop / resize;
- image augmentation;
- language formalization;
- percentile or mean/std normalization;
- relative-action option;
- state sin/cos option;
- embodiment-specific modality configs.

Hence:

\[
\pi_\theta
\neq
\text{neural weights alone}.
\]

The effective deployed policy is:

\[
\pi_{system}=Decode\circ Model\circ Processor.
\]

---

# 13. A source-level tensor map

A useful conceptual trace is:

```text
RAW EPISODE
  images / text / state / action / tag
          ↓
Gr00tN1d7Processor
          ↓
Qwen3VLProcessor              StateActionProcessor
  input_ids                   normalized state
  attention_mask              normalized action
  visual tensors              masks / embodiment id
          ↓                          ↓
       Qwen3 backbone             action path
          ↓                          ↓
backbone_features [B,N,2048]   state/action encoders
          \_________________________/
                      ↓
              AlternateVLDiT
                      ↓
          action decoder by embodiment
                      ↓
velocity field [B,H,Da]
                      ↓
flow integration / RTC
                      ↓
action_pred [B,H,Da]
                      ↓
de-normalize / robot deployment
```

---

# 14. Tests are part of the textbook

Do not only read implementation.

Key tests include:

```text
test_model_forward.py
test_gr00t_processor.py
test_action_head.py
test_action_horizon_validation.py
test_embodiment_tags.py
```

Why tests matter:

- they expose expected shapes;
- they show invalid configurations;
- they define horizon contracts;
- they reveal processor/model assumptions more clearly than papers.

A strong source study should always read tests.

---

# 15. Deployment is a second architecture

Read:

```text
getting_started/policy.md
getting_started/real_world_deployment.md
scripts/deployment/README.md
```

The deployed system is conceptually:

```text
robot sensors
→ preprocessing client/server boundary
→ foundation policy inference
→ async action prediction
→ optional RTC
→ action transport
→ robot-specific controller
→ actuator
```

If network latency or action queue behavior changes, the physical policy changes even with identical checkpoint weights.

---

# 16. Six experiments worth running

## Experiment A — Embodiment-tag causality

Compare:

```text
correct tag
wrong tag
shuffled tag
hidden tag
```

Measure action divergence before robot execution.

## Experiment B — Action horizon

Compare:

\[
H\in\{10,20,40\}
\]

under matched training data.

Measure:

- latency;
- smoothness;
- recovery;
- success.

## Experiment C — Inference steps

Compare flow integration steps:

\[
N\in\{1,2,4,8\}.
\]

This directly exposes quality/latency trade-off.

## Experiment D — RTC mechanism

At fixed checkpoint:

```text
naive chunk replacement
vs overlap only
vs frozen latency region
vs full RTC ramp
```

Measure boundary jerk and task recovery.

## Experiment E — VLM backbone contribution

Use matched downstream data and freeze action-side modules where possible.

Question:

> how much N1.6→N1.7 gain is attributable to the VLM change rather than other pipeline changes?

## Experiment F — State robustness

Use:

```text
normal state
noisy state
delayed state
state dropout
no state
```

This probes whether visual-language context can compensate for proprioceptive degradation.

---

# 17. What this source code does **not** prove

Open code lets us inspect mechanism, but it does not by itself prove:

- unseen-morphology generalization;
- universal physical reasoning;
- independent real-world reproducibility;
- safety under distribution shift;
- superiority over all other VLA families.

Those remain empirical questions.

---

# 18. Final mental model

The key lesson from N1.7 source is:

\[
\boxed{
\text{Robot Foundation Model}
=
\text{Backbone}
+
\text{Embodiment-aware State/Action Encoding}
+
\text{Generative Action Head}
+
\text{Temporal Executor}
+
\text{Processor}
+
\text{Deployment Runtime}
}
\]

This is much closer to the real scientific object than “3B VLA checkpoint”.
