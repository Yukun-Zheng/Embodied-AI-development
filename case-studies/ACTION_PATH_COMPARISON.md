# Action Path Comparison — OpenVLA vs SmolVLA vs GR00T N1.7 vs V-JEPA 2.1

> 目标：把不同品牌系统投影到同一套**物理与计算接口**。比较的不是“谁更强”，而是每条路线对 action / state / time / embodiment / prediction 的建模假设。

---

# 1. 一张总表

| Axis | OpenVLA | SmolVLA | GR00T N1.7 | V-JEPA 2 / 2.1 AC predictor |
|---|---|---|---|---|
| Primary role | VLA policy | VLA policy | robot foundation policy | predictive representation / latent dynamics |
| Main input | image + language | images + language + state | images + text + state + embodiment | video latent + action + state (+ extrinsics) |
| Action representation | discrete action tokens | continuous action chunk | continuous padded multi-embodiment chunk | action is conditioning, not direct policy output |
| Default horizon seen in inspected source | one action vector | 50 | 40 | temporal latent rollout |
| Generator | autoregressive LM generation | flow matching | flow-matching DiT / action head | causal latent predictor |
| Training target | action-token cross entropy | velocity field | velocity field | target latent representation |
| Inference | generate D_a tokens | 10-step Euler flow | 4-step Euler flow | one-step / autoregressive future latent |
| Temporal executor | external | queue / async / RTC | deployment runtime / RTC | external planner/controller required |
| Embodiment conditioning | dataset/action stats largely external | robot/action preprocessing | explicit embodiment tag + category-specific enc/dec | state/action conditioning; not primarily embodiment-universal |
| Low-level controller | external | external robot stack | external / robot-specific deployment stack | external |
| Core source object | tokenized action suffix | VLM prefix + expert suffix | VL backbone + embodiment action system | predictive latent dynamics |

---

# 2. OpenVLA: robot control as next-token prediction

Training path:

\[
a\in\mathbb R^{D_a}
\rightarrow
Q(a)
\rightarrow
[t_1,\ldots,t_{D_a}].
\]

Then:

```text
image + language prompt + action-token answer
→ VLM next-token objective
```

Loss:

\[
L_{AR}=-\sum_i \log p(t_i\mid I,l,t_{<i}).
\]

Inference:

```text
VLM generate D_a tokens
→ de-tokenize to [-1,1]
→ q01/q99 unnormalize
→ continuous end-effector action
```

### Inductive bias

Robot action is treated as a sequence in the same symbolic interface as language.

### Benefits

- reuses mature autoregressive VLM stack;
- simple training interface;
- action can benefit from pretrained language backbone.

### Costs

- quantization;
- arbitrary action-dimension token order;
- AR decoding latency;
- one-step baseline path does not inherently model a temporal action chunk.

---

# 3. SmolVLA: VLM prefix + continuous action expert

Training uses a clean action chunk:

\[
A\in\mathbb R^{B\times 50\times D_a}.
\]

Noise interpolation in inspected source:

\[
x_t=t\epsilon+(1-t)A,
\]

with target:

\[
u_t=\epsilon-A.
\]

Model:

```text
PREFIX:
images + language + state
→ VLM context / KV cache

SUFFIX:
noisy action + time
→ action expert
→ velocity
```

Loss:

\[
L_{flow}=\|v_\theta-u_t\|^2.
\]

Inference:

- default chunk size = 50;
- default 10 flow steps;
- prefix cache reused;
- suffix repeatedly denoised.

### Inductive bias

Semantics and action dynamics have different computational roles while remaining jointly conditionable.

### Temporal system

The same model can be wrapped by:

- ordinary action queue;
- asynchronous inference;
- RTC guidance.

So checkpoint and executor are deliberately separate.

---

# 4. GR00T N1.7: continuous action + explicit embodiment system

Inspected source defaults:

\[
A\in\mathbb R^{B\times40\times D_a},\qquad D_a\le132.
\]

State:

\[
S\in\mathbb R^{B\times1\times D_s},\qquad D_s\le132.
\]

The model additionally consumes:

\[
e\in\{1,\ldots,E\}
\]

as explicit embodiment ID/tag.

Training interpolation:

\[
x_t=(1-t)\epsilon+tA,
\]

with target:

\[
u_t=A-\epsilon.
\]

The sign/time orientation differs from SmolVLA, but both learn a conditional vector field connecting noise and clean action.

Computation:

```text
images + language
→ Qwen3-VL-style backbone
→ VL features

state + embodiment
→ category-specific state encoder

noisy actions + time + embodiment
→ multi-embodiment action encoder

VL context + state/action tokens
→ DiT
→ embodiment-conditioned action decoder
→ velocity
```

Inference defaults to 4 Euler steps.

### Distinctive inductive bias

Cross-embodiment heterogeneity is acknowledged explicitly in state/action encoders and masks rather than only in dataset normalization.

### Temporal system

RTC is implemented at the action-generation level:

- previous chunk overlap;
- frozen latency region;
- gradual editable ramp.

---

# 5. V-JEPA 2.1 action-conditioned predictor: action predicts world, not action

The key conceptual reversal:

```text
Policy model:
world state → action

Action-conditioned world model:
world state + action → future world representation
```

V-JEPA 2.1 generic pretraining:

\[
\hat h=g_\phi(f_\theta(x_{visible}))
\]

matches target representation:

\[
h=f_{\bar\theta}(x).
\]

Action-conditioned predictor:

\[
\hat z_{t+1}
=f(z_{\le t},a_{\le t},s_{\le t},E_{\le t}).
\]

Here action/state are inserted as per-frame tokens.

DROID path trains both:

- teacher-forced prediction;
- autoregressive latent rollout.

### Inductive bias

The network is asked to represent **consequences of actions**, not directly choose them.

To become a control system it still needs:

```text
world model
→ evaluator / cost / planner / policy search
→ action
```

---

# 6. Three fundamentally different questions

These systems answer different questions.

## Question A — How should action be represented?

OpenVLA:

\[
A\rightarrow Tokens.
\]

SmolVLA / GR00T:

\[
A\rightarrow Continuous\ trajectory\ distribution.
\]

## Question B — How should time be represented?

OpenVLA baseline:

- one action vector generated as token sequence.

SmolVLA / GR00T:

- temporal action chunk built into output tensor.

V-JEPA AC predictor:

- temporal state transition built into future latent prediction.

## Question C — Where should embodiment enter?

OpenVLA:

- dataset statistics / action interface mostly external to core generation.

SmolVLA:

- policy preprocessing and shared padded state/action spaces.

GR00T N1.7:

- explicit embodiment ID with category-specific encoders/decoders.

World model:

- embodiment may enter through observed state/action dynamics; explicit morphology conditioning is a separate design choice.

---

# 7. The right controlled comparison

A paper claiming one action architecture is superior should ideally freeze:

```text
same robot
same observations
same instructions
same training episodes
same action semantics
same low-level controller
same policy frequency
same evaluation seeds
```

Then vary only:

```text
A. discrete token AR
B. continuous flow
C. continuous diffusion
D. direct regression
```

Metrics:

- task success;
- physical action error;
- action smoothness;
- contact precision;
- latency mean/p95;
- recovery after perturbation;
- sample efficiency;
- calibration / multimodality.

Without matched conditions, architecture conclusions are confounded by data/backbone/system differences.

---

# 8. Quantization vs numerical integration

The two paradigms have different approximation errors.

## Tokenized action

Quantization error:

\[
e_q=a-Q^{-1}(Q(a)).
\]

Then language-generation error adds on top.

## Flow action

No discrete quantization, but numerical integration introduces:

\[
e_{int}=A_{true}-A_{Euler/N-step}.
\]

And the velocity field itself has function-approximation error.

Thus:

```text
token policy error
= representation quantization
+ token prediction
+ executor/controller

flow policy error
= vector-field approximation
+ numerical integration
+ executor/controller
```

This gives a more meaningful comparison than “AR vs flow”.

---

# 9. Multimodality: policy or missing state?

A multimodal action distribution can mean two different things.

### Genuine behavioral multimodality

Two equally valid trajectories exist.

### Apparent multimodality from partial observability

The observation does not reveal the hidden state, so demonstrations disagree.

A stronger representation / active perception / memory module may collapse the uncertainty.

Therefore before claiming a generative action model is necessary, measure:

\[
H(A\mid O)
\quad\text{vs}\quad
H(A\mid S_{better}).
\]

Some multimodality belongs in the policy; some belongs in the state estimator.

---

# 10. Executor is a first-class variable

Suppose two identical chunk policies output:

\[
A_t=[a_t,\ldots,a_{t+H-1}].
\]

Execution variants:

```text
full open-loop chunk
receding-horizon first-k
queue with fixed refresh
async generation
RTC overlap guidance
```

These can produce very different physical trajectories without changing model weights.

So any benchmark of foundation robot policy should report:

- model inference rate;
- action/control rate;
- chunk size;
- executed horizon;
- inference delay;
- queue policy;
- overlap/replacement policy.

---

# 11. World model introduces a fourth architecture axis

Once a predictive model exists, the decision architecture becomes:

```text
Direct policy:
O → A

Policy + memory:
O,M → A

Policy + world model:
O → candidate A
(O,A) → predicted futures
predicted futures → score / choose A

Planner over world model:
state + action sequences
→ future state distribution
→ optimize
```

This is not a new action representation; it is a new **decision loop**.

Therefore world-model papers should not be compared with VLA papers as if both are simply action heads.

---

# 12. A unified tensor-level interface

A future model family can be described with five tensors:

Observation:

\[
O_t.
\]

Belief / representation:

\[
Z_t=f(O_{\le t},M_t).
\]

Candidate action trajectory:

\[
A_{t:t+H}=g(Z_t,c,e).
\]

Predicted future:

\[
\hat Z_{t+1:t+K}=F(Z_t,A_{t:t+K},e).
\]

Executed command:

\[
u_t=C(A_t,Z_t,q_t,\dot q_t).
\]

This separates five scientific roles:

```text
perception
memory/state
policy
dynamics/world model
controller
```

A “general embodied model” can combine them, but evaluation should still probe them separately.

---

# 13. Research matrix

| Hypothesis | Minimal experiment | Negative control |
|---|---|---|
| action tokens lose precision | insertion task vs bin count | same controller/data |
| flow preserves multimodality | two-mode Push-T variant | MSE regression |
| RTC reduces stale-action failures | injected inference latency | same checkpoint, no RTC |
| embodiment tags matter | cross-robot matched task | wrong/shuffled tag |
| world model is used | planner with correct WM | random/shuffled-action WM |
| memory helps long horizon | delayed dependency task | random retrieved memory |
| VLM semantics helps action | novel language/task | wrong instruction / frozen random language embedding |

---

# 14. The textbook-level conclusion

The modern embodied stack is not converging to one monolithic model. The source code suggests a more useful decomposition:

\[
\boxed{
\text{Embodied Agent}
=
\text{Perception}
+
\text{State/Memory}
+
\text{Action Generator}
+
\text{Temporal Executor}
+
\text{World Model}
+
\text{Controller}
+
\text{Embodiment Interface}
}
\]

OpenVLA, SmolVLA, GR00T N1.7 and V-JEPA 2.1 occupy different points in this factorization.

The research question after 2026 is therefore less likely to be:

> Which single Transformer should replace all of them?

and more likely to be:

> **Which interfaces should be learned jointly, which should remain modular, and what evidence proves that information actually flows between them?**
