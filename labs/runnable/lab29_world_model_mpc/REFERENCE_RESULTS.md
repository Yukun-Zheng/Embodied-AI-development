# Lab 29 — CI-Verified Reference Observation

> These numbers are a deterministic **quick/smoke configuration**, not a benchmark claim. They exist so readers can verify that the intended mechanisms are observable before scaling to a larger simulator or model.

## Base falsification

GitHub Actions `Executable textbook regression` verified the following reference behavior on the quick configuration:

| world model | passive one-step RMSE | counterfactual sensitivity error | final position error | closed-loop position RMSE |
|---|---:|---:|---:|---:|
| `action_aware` | 0.00200 | 0.0002 | 0.0031 | 0.3967 |
| `action_blind` | 0.00395 | 0.1416 | 1.0000 | 1.0000 |
| `wrong_action_sign` | 0.00708 | 0.2831 | 11.0037 | 5.5953 |

The important observation is not the absolute score. `action_blind` and `wrong_action_sign` still have small passive one-step errors, yet their counterfactual action semantics are wrong and MPC fails. This is a concrete counterexample to:

\[
\text{low observational prediction error}
\Rightarrow
\text{planning-ready world model}.
\]

## Planning-horizon × model-bias probe

The probe scales only the learned action gain to

\[
\hat B_{probe}=0.5\hat B
\]

and keeps the physical plant, cost function, MPC mechanism and target fixed.

The CI quick sweep produced:

| planning horizon | rollout prediction RMSE | terminal prediction RMSE | realized control cost | final position error |
|---:|---:|---:|---:|---:|
| 1 | 0.0399 | 0.0399 | 6.8288 | 0.0266 |
| 4 | 0.0578 | 0.0703 | **5.6755** | 0.0091 |
| 16 | 0.1311 | 0.1956 | 6.4751 | 0.0408 |
| 32 | 0.2230 | 0.3875 | 8.4535 | 0.0452 |

From horizon 1 to 32, terminal imagined-state error grows by roughly

\[
\frac{0.3875}{0.0399}\approx9.7\times.
\]

The realized control cost is **non-monotonic**: horizon 4 is better than horizon 1, showing a real look-ahead benefit, but horizon 32 is substantially worse because the biased dynamics are applied repeatedly inside imagined rollouts.

This supports a more precise statement than “long horizons are bad”:

\[
\text{useful planning horizon}
=\operatorname*{argmin}_H
\left[
\text{insufficient-lookahead cost}(H)
+
\text{compounding-model-bias cost}(H)
\right].
\]

The optimal horizon is therefore a property of **model fidelity × task dynamics × planner objective**, not a universal constant.

## Reproduce

```bash
python labs/runnable/lab29_world_model_mpc/run.py --quick --output /tmp/lab29
python labs/runnable/lab29_world_model_mpc/horizon_probe.py --quick --output /tmp/lab29
python labs/runnable/lab29_world_model_mpc/analyze.py /tmp/lab29
```

The generated `analysis.json` is the machine-readable source of the mechanism assertions. If the configuration changes, regenerate the analysis rather than copying these numbers forward.
