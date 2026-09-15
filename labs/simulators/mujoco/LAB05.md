# MuJoCo S-Layer — Lab 05 Rigid-Body Dynamics

Lab 05 moves the textbook's rigid-body dynamics equation into an independent physics engine and asks a precise question:

> Can MuJoCo's own forward acceleration be reconstructed from its mass matrix and generalized-force terms, and how quickly does prediction degrade when the assumed dynamics are wrong?

## 1. Dynamics identity under test

For generalized coordinates \(q\), the experiment uses

\[
M(q)\ddot q
=
\tau_{\mathrm{applied}}
+	au_{\mathrm{actuator}}
+	au_{\mathrm{passive}}
-h(q,\dot q),
\]

where MuJoCo exposes the corresponding quantities as:

```text
qM               → packed mass matrix
qfrc_applied     → externally applied generalized force
qfrc_actuator    → actuator generalized force
qfrc_passive     → damping / other passive force
qfrc_bias        → bias force h(q, qdot)
qacc             → engine forward acceleration
```

`mj_fullM` expands `qM` into the dense \(M(q)\) used by the reconstruction.

## 2. Probe states

Five nontrivial 3R arm states are evaluated. Each probe changes all three of:

- joint configuration \(q\);
- joint velocity \(\dot q\);
- applied generalized force \(\tau\).

The arm therefore includes configuration-dependent inertia, velocity-dependent bias terms and nonzero joint damping.

## 3. Compared model variants

### `matched`

Use MuJoCo's actual \(M\), bias and passive-force terms.

### `wrong_mass_scale`

Keep the same state, bias, passive force and applied force, but replace

\[
M \rightarrow 0.6M.
\]

This isolates inertia mismatch.

### `omit_passive`

Keep the true mass matrix and bias force but set

\[
\tau_{\mathrm{passive}}=0.
\]

This isolates what happens when damping/passive terms disappear from the model.

## 4. Additional structural checks

For every state the Lab records:

- symmetry error \(\max |M-M^\top|\);
- minimum eigenvalue of the symmetric mass matrix;
- dynamics residual

\[
\left\|M\ddot q-\left(\tau_{\mathrm{applied}}+	au_{\mathrm{actuator}}+	au_{\mathrm{passive}}-h\right)\right\|.
\]

The matched model should have near-machine-precision prediction error and residual, while the wrong-model controls should not.

## 5. Evidence products

```text
probe_rows.csv
model_metrics.csv
experiment_summary.json
runs/dynamics_identity/
├── manifest.json
├── steps.csv
├── failures.jsonl
└── summary.json
```

Each `probe_rows.csv` row stores the physical state, force terms, true MuJoCo acceleration and one model prediction.

## 6. Run

```bash
python -m pip install -r labs/simulators/mujoco/requirements.txt
python labs/simulators/mujoco/lab05_dynamics.py --output /tmp/mujoco-lab05
python labs/simulators/mujoco/lab05_smoke.py
```

## 7. Falsification criteria

The intended result fails if:

- the matched reconstruction cannot reproduce MuJoCo `qacc`;
- \(M(q)\) is not symmetric positive definite at the tested unconstrained states;
- a 40% mass-matrix error has negligible acceleration consequences;
- omitting passive damping is indistinguishable from the matched model;
- prediction errors become non-finite rather than interpretable model mismatch.

## 8. Why this matters for learned robot policies

A policy or world model may output a plausible desired action while the controller or planner relies on an incorrect dynamics model. This Lab separates two failure sources:

```text
policy / planner chooses action
        ↓
assumed dynamics maps action → acceleration
        ↓
physical engine produces actual acceleration
```

The difference between assumed and physical acceleration is a mechanism-level source of planning/control error, not merely a generic "sim-to-real gap".

## 9. Next extension

The next step is to feed the matched and mismatched dynamics into the **same computed-torque / MPC controller**, measuring when acceleration-model error becomes tracking, energy or stability error.
