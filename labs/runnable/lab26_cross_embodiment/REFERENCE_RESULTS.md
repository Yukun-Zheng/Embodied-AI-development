# Lab 26 — CI-Verified Reference Observation

> These values come from the deterministic GitHub Actions **quick/smoke configuration**. They demonstrate a controlled interface/morphology mechanism in a 1-D physical plant; they are not benchmark claims about any specific VLA, arm, humanoid or real-robot transfer system.

## CI configuration

The permanent `Executable textbook regression` evaluates the same **120 paired trials** on four embodiments:

- **A/B** — seen bodies;
- **C** — held-out interpolation;
- **D** — held-out extrapolation.

All conditions use one canonical PD policy with exactly two shared policy parameters, \((k_p,k_d)\). Held-out C/D receive **zero task adaptation steps**.

## Runner observations

| condition | seen success | held-out success | C interpolation | D extrapolation |
|---|---:|---:|---:|---:|
| `raw_shared` | 0.500 | 0.087 | 0.175 | 0.000 |
| `canonical_interface_only` | 0.887 | 0.567 | 1.000 | 0.133 |
| `seen_robot_lookup` | **1.000** | 0.567 | **1.000** | **0.133** |
| `morphology_conditioned` | **1.000** | **1.000** | **1.000** | **1.000** |
| `wrong_morphology_tag` | 0.887 | 0.567 | 1.000 | 0.133 |
| `wrong_action_semantics` | 0.500 | 0.500 | 1.000 | 0.000 |

For the reversed-action embodiments B and D, `wrong_action_semantics` produced **0.000 success on both bodies**. The interface round-trip checks were numerically exact within the CI tolerance.

## What the numbers establish

### 1. Shared tensor shape is not shared physical semantics

The semantics-blind `raw_shared` condition reaches only

\[
S_{seen}=0.500,
\qquad
S_{heldout}=0.087.
\]

After only correcting sensor units and hardware action sign/scale, `canonical_interface_only` reaches

\[
0.887\quad\text{and}\quad0.567.
\]

The paired gains are therefore

\[
\Delta_{seen}=0.387,
\qquad
\Delta_{heldout}=0.480.
\]

This isolates a systems-level mechanism: a universal tensor shape or padding convention does not establish a universal action/state meaning.

### 2. Multi-seen support is not unseen morphology transfer

`seen_robot_lookup` has exact robot-specific dynamics entries for A and B, so it achieves

\[
S_{seen}=1.000.
\]

But C/D have no lookup entry. The held-out aggregate falls to

\[
S_{heldout}=0.567.
\]

More importantly, reporting the two held-out bodies separately reveals:

\[
S_C=1.000,
\qquad
S_D=0.133.
\]

C happens to be close enough to the nominal body that the fallback controller still works; extrapolation D exposes the failure. A single held-out average would partially hide this distinction.

So the experiment directly reproduces the warning:

> One checkpoint or controller supporting several already-known robot identities is not, by itself, evidence of cross-embodiment generalization.

### 3. Continuous morphology information enables zero-shot transfer in this mechanism test

`morphology_conditioned` uses the new robot's mass/damping descriptor in the physical adapter while keeping the shared policy gains fixed. It achieves

\[
S_A=S_B=S_C=S_D=1.000.
\]

For C/D the recorded task adaptation budget is

\[
N_{adapt}=0.
\]

Relative to seen-ID lookup, held-out success increases by

\[
1.000-0.567=\mathbf{0.433}.
\]

The experiment therefore distinguishes **metadata-conditioned zero-shot execution** from task fine-tuning on the held-out body.

### 4. The morphology descriptor is causally used

When observation/action semantics remain correct but the morphology tag is deliberately swapped or replaced by the nominal body, held-out success returns to

\[
0.567,
\]

including D=0.133.

Thus the correct descriptor is not decorative metadata: changing it changes physical behavior by 0.433 held-out success in this controlled system.

### 5. Action conventions remain a hard boundary

`wrong_action_semantics` keeps the canonical state estimate and morphology descriptor correct, but applies Robot-A action sign/scale to every embodiment.

The two reversed-action bodies satisfy

\[
S_B=S_D=0.000.
\]

A correct high-level policy and a correct morphology model therefore do not rescue an incorrect actuator convention.

## CI mechanism assertions

The permanent runner verifies all of the following:

```text
interface state/action round trips are exact
+ canonical semantics improve seen-body performance
+ canonical semantics improve held-out performance
+ seen robot lookup succeeds on A/B
+ seen lookup still has a large unseen/extrapolation gap
+ C interpolation and D extrapolation are reported separately
+ morphology-conditioned execution succeeds on C/D
+ C/D use zero task adaptation
+ continuous morphology conditioning beats seen-ID lookup on held-out bodies
+ wrong morphology metadata degrades transfer
+ wrong action semantics break B/D
+ shared policy parameter count stays fixed at 2
```

## Scientific scope

The supported claim is deliberately narrow:

> Cross-embodiment evaluation must separate interface semantics, multi-seen robot support, held-out interpolation, held-out extrapolation and adaptation budget. In this fixed-policy physical mechanism test, correct continuous morphology metadata enables zero-shot execution that a table of seen robot identities cannot provide.

It does **not** establish that mass/damping metadata is sufficient for real manipulators, nor that a particular foundation policy generalizes to unseen robots. Real systems add geometry, joint topology, contacts, controller differences, perception viewpoints, delays and safety constraints.

## Reproduce

```bash
python labs/runnable/lab26_cross_embodiment/run.py \
  --quick \
  --output /tmp/lab26

python labs/runnable/lab26_cross_embodiment/analyze.py \
  /tmp/lab26/condition_metrics.csv \
  /tmp/lab26/embodiment_metrics.csv \
  /tmp/lab26/interface_checks.csv \
  --output-dir /tmp/lab26
```

Use `embodiment_metrics.csv` rather than only `condition_metrics.csv` whenever the held-out interpolation/extrapolation distinction matters.

If body parameters, action conventions, control horizon or success tolerances change, regenerate the analysis rather than copying these values forward.
