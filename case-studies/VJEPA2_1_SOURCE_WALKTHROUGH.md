# Source Walkthrough — V-JEPA 2 / V-JEPA 2.1 for Predictive Intelligence

> Repository: `facebookresearch/vjepa2`  
> Source snapshot inspected: `204698b45b3712590f06245fbfba32d3be539812` (2026-03-23)  
> Goal: separate **representation-space prediction** from **action-conditioned robot dynamics prediction**, then ask what evidence is needed before calling the system a useful world model.

---

# 1. First distinction: V-JEPA pretraining is not automatically a robot world model

The generic training stack learns predictive visual representations.

A separate action-conditioned path introduces robot state/action.

So the correct hierarchy is:

```text
V-JEPA representation learner
        ↓
video / image predictive features
        ↓
optional action-conditioned predictor
        ↓
robot dynamics prediction in latent space
        ↓
planning / control only if explicitly connected
```

Do not collapse these four stages into one label.

---

# 2. V-JEPA 2.1 training entry

Key file:

```text
app/vjepa_2_1/train.py
```

The training code explicitly creates:

```text
encoder
predictor
target_encoder
```

with `target_encoder` updated by momentum/EMA rather than direct gradient descent.

The high-level objective is:

```text
visible / context video tokens
→ context encoder
→ predictor
→ predicted hidden representations

full / target video
→ EMA target encoder
→ target hidden representations

predicted hidden ≈ target hidden
```

No pixel decoder is required.

---

# 3. Input structure and video tokenization

The training config exposes:

- frames per clip;
- FPS;
- crop size;
- patch size;
- tubelet size;
- video/image dataset mixture;
- mask strategy.

If crop size is \(H=W\) and patch size is \(P\), spatial token grid is:

\[
G=\frac{H}{P}\times\frac{W}{P}.
\]

The source also supports multiple temporal frame counts and mixed image/video training.

This matters because “representation quality” depends on the temporal resolution of the pretraining problem.

---

# 4. Masked prediction defines the information bottleneck

`MaskCollator` produces encoder masks and prediction masks:

```text
masks_enc
masks_pred
```

The target branch encodes the clip without gradient.

The context branch receives masked input and must predict representation at target locations.

Conceptually:

\[
z=f_\theta(x_{visible}),
\]

\[
h=f_{\bar\theta}(x),
\]

\[
\hat h=g_\phi(z,m_{pred}).
\]

The objective compares \(\hat h\) to selected target features from \(h\).

This is representation prediction, not image reconstruction.

---

# 5. Target encoder: stabilized moving target

In the training loop:

```text
with no_grad:
    h = target_encoder(clips)
```

Target representations are layer-normalized.

After optimizer step, target parameters receive EMA update:

\[
\bar\theta
\leftarrow
m\bar\theta+(1-m)\theta.
\]

This creates a slowly moving target network.

The purpose is not ordinary teacher/student distillation from a fixed external teacher; both branches come from the same evolving representation family.

---

# 6. Predictor loss in V-JEPA 2.1

The current training code supports multi-level representations and optional context loss.

For prediction positions, source effectively computes an \(L_p\)-style latent loss:

\[
L_{pred}
=
\frac{1}{N}
\sum
\frac{\left|z_{pred}-h_{target}\right|^{p}}{p},
\]

where `loss_exp` controls \(p\).

When context prediction is enabled, another term compares predicted context representation against target context, potentially weighted by mask distance.

Total:

\[
L=L_{pred}+\lambda L_{context}.
\]

The code can progressively schedule \(\lambda\).

This is useful for understanding V-JEPA 2.1 as a structured representation-learning objective rather than a single MSE.

---

# 7. V-JEPA 2.1 exposes additional representation knobs

The source config includes options such as:

```text
normalize_predictor
modality_embedding
levels_predictor
is_causal
pred_is_causal
use_rope
register tokens
image/video loss weights
```

These are scientifically meaningful because they determine whether the learned representation emphasizes:

- temporal consistency;
- dense local features;
- image/video shared structure;
- causal temporal context.

A paper summary that says only “V-JEPA 2.1 improves dense features” hides these design choices.

---

# 8. Action-conditioned predictor is a separate model

Key file:

```text
src/models/ac_predictor.py
```

Class:

```text
VisionTransformerPredictorAC
```

The predictor receives:

```text
context visual tokens x
actions
states
optional camera extrinsics
```

The source defines separate linear encoders:

```text
action_encoder
state_encoder
extrinsics_encoder
```

This is the actual robotics bridge.

---

# 9. Action and state become tokens at each frame

Suppose visual representation has:

\[
x\in\mathbb{R}^{B\times (T\cdot HW)\times D}.
\]

The source reshapes to:

\[
[B,T,HW,D].
\]

Then action/state are encoded and inserted per frame.

Without camera extrinsics:

```text
[action token | state token | H×W visual tokens]
```

With extrinsics:

```text
[action | state | extrinsics | H×W visual tokens]
```

Then flatten across time.

This is an extremely concrete answer to:

> how does action enter a predictive visual world model?

It becomes a temporal conditioning token aligned with each visual frame.

---

# 10. Causal attention enforces intervention direction

The action-conditioned predictor builds a frame-causal attention mask.

Future visual tokens should not leak into prediction of the current/future state.

The conditional structure is conceptually:

\[
\hat z_{t+1}
=
f(z_{\le t},a_{\le t},s_{\le t}).
\]

If camera extrinsics are enabled:

\[
\hat z_{t+1}
=
f(z_{\le t},a_{\le t},s_{\le t},E_{\le t}).
\]

The causal mask is essential if the model is later interpreted as predictive dynamics.

---

# 11. DROID training path turns representation prediction into robot prediction

Key entry:

```text
app/vjepa_droid/train.py
```

This training path exposes robot-specific data configuration:

```text
camera views
camera frame option
states
actions
camera extrinsics
frames per clip
```

The action embedding dimension is set to 7 in the current setup path.

So the action-conditioned predictor is not an abstract future-video module. It is explicitly instantiated for robot trajectories.

---

# 12. Two robot-prediction losses: teacher forcing and autoregressive rollout

The DROID training code evaluates two predictive modes.

## 12.1 Teacher forcing

The predictor receives previous ground-truth context tokens and corresponding actions/states.

Conceptually:

\[
\hat z_{t+1}^{TF}
=f(z_{\le t}^{true},a_{\le t},s_{\le t}).
\]

## 12.2 Autoregressive rollout

The predictor starts with initial true context, then recursively feeds its own predicted latent frames.

\[
\hat z_{t+1}
=f(\hat z_{\le t},a_{\le t},s_{\le t}).
\]

The code explicitly constructs this rollout for `auto_steps`.

This is scientifically important because one-step prediction can look strong while rollout drifts badly.

---

# 13. DROID loss separates one-step and rollout error

Source computes:

```text
jloss = loss(z_teacher_forced, target)
sloss = loss(z_autoregressive, target)
loss  = jloss + sloss
```

Thus the optimization penalizes both:

- local predictive error;
- multi-step self-generated rollout error.

This is closer to what a control-oriented world model needs than only one-step latent prediction.

Still, it is not yet proof of planning usefulness.

---

# 14. Representation prediction vs control usefulness

We should distinguish four evidence levels.

## E1 — Latent prediction

\[
\hat z_{t+1}\approx z_{t+1}.
\]

## E2 — Action sensitivity

Changing \(a_t\) changes prediction appropriately:

\[
\hat z_{t+1}(a)\neq\hat z_{t+1}(a').
\]

## E3 — Counterfactual validity

For interventions not seen in the exact trajectory, predicted effect remains physically correct.

## E4 — Control gain

Using the model improves decision quality:

\[
J_{policy+WM}>J_{policy-no-WM}.
\]

A V-JEPA predictive representation may satisfy E1 strongly. Robotics requires testing E2–E4.

---

# 15. Critical negative controls

## A. Shuffle action

During evaluation:

```text
correct action
vs
shuffled action sequence
```

If prediction changes little, action conditioning is weak.

## B. Wrong state

Keep image/action fixed, perturb proprioceptive state.

Measure latent sensitivity.

## C. Wrong timing

Shift action sequence by one frame.

This tests temporal alignment rather than mere action statistics.

## D. Frozen random predictor

If downstream policy performance is unchanged, the world-model path may be decorative.

## E. Representation-only baseline

Use the same encoder without action-conditioned predictive training.

This isolates whether dynamics training adds control-relevant information.

---

# 16. Camera extrinsics are not a minor option

The AC predictor can explicitly encode camera extrinsics.

For moving-camera robots, observed pixel change is caused by both:

```text
world/object motion
+
camera/robot motion
```

Without extrinsic information, the model may conflate the two.

This is especially important for:

- wrist cameras;
- mobile manipulators;
- humanoid head cameras;
- active perception.

A useful ablation:

```text
correct extrinsics
vs
no extrinsics
vs
perturbed extrinsics
```

under identical visual data.

---

# 17. Why latent prediction can beat pixel prediction

Pixel prediction must model nuisance detail:

- texture;
- lighting;
- sensor noise;
- high-frequency background.

A latent target can emphasize task-relevant invariants.

But this creates a new danger:

> the latent representation may discard exactly the small geometric/contact cue needed for control.

Therefore robotics evaluation should include probes for:

- pose;
- depth;
- contact state;
- motion;
- action effect;
- uncertainty.

---

# 18. Six experiments worth running

## A. Action causality score

For same initial state, sample actions \(a_i\).

Compare latent prediction separation with true future separation.

## B. One-step vs rollout drift

Plot:

\[
E(k)=\|\hat z_{t+k}-z_{t+k}\|.
\]

Teacher-forced accuracy alone is insufficient.

## C. Planning value

Use the same downstream planner with:

```text
correct AC predictor
representation-only predictor
shuffled-action predictor
random predictor
```

## D. Moving-camera test

Use wrist/head camera trajectories with and without extrinsics.

## E. Dense representation vs motor precision

Test whether V-JEPA 2.1 dense features improve:

- insertion tolerance;
- object-pose error;
- contact timing;

not just segmentation probes.

## F. State-ablation test

Remove robot state from AC predictor and measure which tasks become ambiguous.

---

# 19. The final source-level mental model

Generic V-JEPA 2.1:

```text
masked video
→ context encoder
→ predictor
→ predicted latent targets
        ↑
EMA target encoder
```

Robot action-conditioned route:

```text
visual latent history
+ action history
+ state history
+ optional camera extrinsics
        ↓
causal AC predictor
        ↓
future latent trajectory
        ↓
(optional) planner / evaluator / control
```

Only the second route begins to resemble a robot world model.

And even there, the decisive scientific question remains:

> **Does the predictive model change action selection in a way that improves physical control?**

That question cannot be answered by latent prediction loss alone.
