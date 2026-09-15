#!/usr/bin/env python3
"""Planning-horizon × model-bias probe for Lab 29.

This is deliberately separate from the base three-model falsification in run.py.
We take the learned action-aware linear world model, scale only its learned action
gain, and then sweep MPC planning horizon. The probe measures both imagined
rollout error and realized closed-loop control cost.

The point is not to claim that a particular learned model must fail at a long
horizon. The point is to make model bias an explicit intervention so students can
observe when a longer imagination horizon begins to amplify a wrong dynamics
assumption.
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
LAB_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

import run as lab29  # noqa: E402
from labs.runnable.common import load_json, write_csv, write_json  # noqa: E402

DEFAULT_CONFIG = LAB_DIR / "config" / "default.json"


def biased_action_gain_model(
    aware: lab29.LinearWorldModel,
    *,
    scale: float,
    horizon: int,
) -> lab29.LinearWorldModel:
    if not aware.action_aware:
        raise ValueError("The horizon probe requires an action-aware base model")
    weights = aware.weights.copy()
    # aware features are [position, velocity, action, bias]. Row 2 is the
    # identified intervention effect of action on next state.
    weights[2, :] *= scale
    return lab29.LinearWorldModel(
        name=f"biased_action_gain_h{horizon}",
        weights=weights,
        action_aware=True,
    )


def rollout_prediction_metrics(
    model: lab29.LinearWorldModel,
    *,
    horizon: int,
    cfg: dict[str, Any],
    sequences: int,
    seed: int,
) -> tuple[float, float]:
    """Return RMSE over all imagined steps and at the terminal imagined step."""
    rng = np.random.default_rng(seed)
    dt = float(cfg["dt"])
    limit = float(cfg["u_limit"])
    true_state = np.column_stack(
        [rng.uniform(-1.0, 1.0, sequences), rng.uniform(-1.0, 1.0, sequences)]
    )
    predicted_state = true_state.copy()
    actions = rng.uniform(-limit, limit, (sequences, horizon))

    squared_error_sum = 0.0
    scalar_count = 0
    for step in range(horizon):
        action = actions[:, step]
        true_state = np.stack(
            [lab29.true_step(state, float(u), dt) for state, u in zip(true_state, action)]
        )
        predicted_state = model.predict_batch(predicted_state, action)
        diff = predicted_state - true_state
        squared_error_sum += float(np.sum(diff**2))
        scalar_count += int(diff.size)

    all_step_rmse = math.sqrt(squared_error_sum / scalar_count)
    terminal_rmse = float(np.sqrt(np.mean((predicted_state - true_state) ** 2)))
    return all_step_rmse, terminal_rmse


def run_probe(
    cfg: dict[str, Any],
    *,
    output_root: Path,
    command: list[str],
    quick: bool,
) -> list[dict[str, Any]]:
    probe = dict(cfg["horizon_probe"])
    horizons = [int(x) for x in probe["horizons"]]
    sequences = int(probe["rollout_sequences"])
    control_steps = int(probe["control_steps"])
    candidates = int(probe["candidates"])
    if quick:
        horizons = [1, 4, 16, 32]
        sequences = min(sequences, 128)
        control_steps = min(control_steps, 30)
        candidates = min(candidates, 512)

    dt = float(cfg["dt"])
    train = lab29.generate_dataset(
        samples=int(cfg["train_samples"] if not quick else min(int(cfg["train_samples"]), 2500)),
        seed=int(cfg["seed"]),
        dt=dt,
        action_std=float(cfg["train_action_std"]),
        noise_std=float(cfg["observation_noise_std"]),
    )
    test = lab29.generate_dataset(
        samples=int(cfg["test_samples"] if not quick else min(int(cfg["test_samples"]), 1000)),
        seed=int(cfg["seed"]) + 1,
        dt=dt,
        action_std=float(cfg["train_action_std"]),
        noise_std=float(cfg["observation_noise_std"]),
    )
    aware = lab29.build_models(*train)["action_aware"]
    test_states, test_actions, test_next = test
    cf_states = test_states[: min(512, len(test_states))]

    rows: list[dict[str, Any]] = []
    for horizon in horizons:
        model = biased_action_gain_model(
            aware,
            scale=float(probe["action_gain_scale"]),
            horizon=horizon,
        )
        one_step = lab29.one_step_rmse(model, test_states, test_actions, test_next)
        cf_error, true_norm, predicted_norm = lab29.counterfactual_sensitivity_metrics(
            model,
            cf_states,
            float(cfg["counterfactual_action"]),
            dt,
        )
        rollout_rmse, terminal_rmse = rollout_prediction_metrics(
            model,
            horizon=horizon,
            cfg=cfg,
            sequences=sequences,
            seed=int(cfg["seed"]) + 2000 + horizon,
        )

        condition_cfg = copy.deepcopy(cfg)
        condition_cfg["control_steps"] = control_steps
        condition_cfg["mpc"]["horizon"] = horizon
        condition_cfg["mpc"]["candidates"] = candidates
        result = lab29.run_control(
            model=model,
            one_step_error=one_step,
            sensitivity_error=cf_error,
            true_sensitivity_norm=true_norm,
            predicted_sensitivity_norm=predicted_norm,
            cfg=condition_cfg,
            output_root=output_root,
            command=command,
        )
        rows.append(
            {
                "planning_horizon": horizon,
                "action_gain_scale": float(probe["action_gain_scale"]),
                "rollout_prediction_rmse": rollout_rmse,
                "terminal_prediction_rmse": terminal_rmse,
                **result,
            }
        )

    write_csv(output_root / "horizon_sweep.csv", rows)
    write_json(
        output_root / "horizon_probe_manifest.json",
        {
            "lab_id": lab29.LAB_ID,
            "probe": "planning_horizon_x_action_gain_bias",
            "action_gain_scale": float(probe["action_gain_scale"]),
            "horizons": horizons,
            "rollout_sequences": sequences,
            "control_steps": control_steps,
            "candidates": candidates,
            "results_file": "horizon_sweep.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Smaller deterministic CI probe.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if "horizon_probe" not in cfg:
        raise SystemExit("Config is missing horizon_probe")

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = LAB_DIR / "runs" / f"horizon-probe-{stamp}"
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_probe(cfg, output_root=output_root, command=sys.argv, quick=args.quick)
    print(f"Lab 29 horizon probe complete: {len(rows)} horizons")
    print(f"results: {output_root / 'horizon_sweep.csv'}")
    for row in rows:
        print(
            f"h={row['planning_horizon']:>2} "
            f"rollout-rmse={row['rollout_prediction_rmse']:.4f} "
            f"terminal-rmse={row['terminal_prediction_rmse']:.4f} "
            f"control-cost={row['realized_control_cost']:.4f} "
            f"final-error={row['final_position_error']:.4f}"
        )


if __name__ == "__main__":
    main()
