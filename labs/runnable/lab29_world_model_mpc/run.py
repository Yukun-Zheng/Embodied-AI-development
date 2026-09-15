#!/usr/bin/env python3
"""Lab 29 — world-model prediction quality versus control utility.

A passive low-action dataset is used to fit two linear world models:
- action_aware: predicts x_{t+1} from state and action;
- action_blind: predicts x_{t+1} from state only.

A third negative-control model flips the learned action effect. All three can have
small one-step error on the passive test distribution, but only a model with the
correct counterfactual action sensitivity should support useful MPC.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab29_world_model_mpc"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass
class LinearWorldModel:
    name: str
    weights: np.ndarray
    action_aware: bool

    def predict_batch(self, states: np.ndarray, actions: np.ndarray) -> np.ndarray:
        if self.action_aware:
            features = np.column_stack([states, actions, np.ones(len(states))])
        else:
            features = np.column_stack([states, np.ones(len(states))])
        return features @ self.weights

    def predict(self, state: np.ndarray, action: float) -> np.ndarray:
        return self.predict_batch(state[None, :], np.asarray([action], dtype=np.float64))[0]


def true_step(state: np.ndarray, action: float, dt: float) -> np.ndarray:
    """Deterministic 1-D damped double-integrator used as the physical plant."""
    position, velocity = float(state[0]), float(state[1])
    next_position = position + dt * velocity + 0.5 * dt * dt * action
    next_velocity = 0.98 * velocity + dt * action
    return np.asarray([next_position, next_velocity], dtype=np.float64)


def generate_dataset(
    *,
    samples: int,
    seed: int,
    dt: float,
    action_std: float,
    noise_std: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    states = np.column_stack(
        [rng.uniform(-1.0, 1.0, samples), rng.uniform(-1.0, 1.0, samples)]
    )
    actions = rng.normal(0.0, action_std, samples)
    next_states = np.stack([true_step(x, u, dt) for x, u in zip(states, actions)])
    next_states += rng.normal(0.0, noise_std, next_states.shape)
    return states, actions, next_states


def fit_linear_model(
    states: np.ndarray,
    actions: np.ndarray,
    next_states: np.ndarray,
    *,
    action_aware: bool,
    name: str,
) -> LinearWorldModel:
    if action_aware:
        features = np.column_stack([states, actions, np.ones(len(states))])
    else:
        features = np.column_stack([states, np.ones(len(states))])
    weights, *_ = np.linalg.lstsq(features, next_states, rcond=None)
    return LinearWorldModel(name=name, weights=weights, action_aware=action_aware)


def build_models(
    states: np.ndarray,
    actions: np.ndarray,
    next_states: np.ndarray,
) -> dict[str, LinearWorldModel]:
    aware = fit_linear_model(
        states,
        actions,
        next_states,
        action_aware=True,
        name="action_aware",
    )
    blind = fit_linear_model(
        states,
        actions,
        next_states,
        action_aware=False,
        name="action_blind",
    )
    wrong_weights = aware.weights.copy()
    # For aware features [position, velocity, action, bias], row 2 encodes the
    # learned action effect. Flipping it is a direct counterfactual negative control.
    wrong_weights[2, :] *= -1.0
    wrong = LinearWorldModel(
        name="wrong_action_sign",
        weights=wrong_weights,
        action_aware=True,
    )
    return {model.name: model for model in [aware, blind, wrong]}


def one_step_rmse(
    model: LinearWorldModel,
    states: np.ndarray,
    actions: np.ndarray,
    next_states: np.ndarray,
) -> float:
    pred = model.predict_batch(states, actions)
    return float(np.sqrt(np.mean((pred - next_states) ** 2)))


def counterfactual_sensitivity_metrics(
    model: LinearWorldModel,
    states: np.ndarray,
    action_magnitude: float,
    dt: float,
) -> tuple[float, float, float]:
    plus = np.full(len(states), action_magnitude, dtype=np.float64)
    minus = -plus
    pred_delta = model.predict_batch(states, plus) - model.predict_batch(states, minus)
    true_plus = np.stack([true_step(x, action_magnitude, dt) for x in states])
    true_minus = np.stack([true_step(x, -action_magnitude, dt) for x in states])
    true_delta = true_plus - true_minus
    error = float(np.sqrt(np.mean((pred_delta - true_delta) ** 2)))
    true_norm = float(np.mean(np.linalg.norm(true_delta, axis=1)))
    pred_norm = float(np.mean(np.linalg.norm(pred_delta, axis=1)))
    return error, true_norm, pred_norm


def rollout_candidates(
    model: LinearWorldModel,
    state: np.ndarray,
    action_sequences: np.ndarray,
) -> np.ndarray:
    n_candidates, horizon = action_sequences.shape
    states = np.repeat(state[None, :], n_candidates, axis=0)
    trajectory = np.empty((n_candidates, horizon, 2), dtype=np.float64)
    for k in range(horizon):
        states = model.predict_batch(states, action_sequences[:, k])
        trajectory[:, k, :] = states
    return trajectory


def choose_mpc_action(
    model: LinearWorldModel,
    state: np.ndarray,
    target: float,
    cfg: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[float, float]:
    mpc = cfg["mpc"]
    horizon = int(mpc["horizon"])
    candidates = int(mpc["candidates"])
    limit = float(cfg["u_limit"])

    actions = np.clip(rng.normal(0.0, 1.0, (candidates, horizon)), -limit, limit)
    actions[0, :] = 0.0
    # Deterministic structured candidates improve search coverage and make the
    # action-blind model select zero through the action penalty rather than a tie.
    constants = [-limit, -0.5 * limit, 0.0, 0.5 * limit, limit]
    for i, value in enumerate(constants, start=1):
        actions[i, :] = value
    for i, value in enumerate([0.5 * limit, limit, -0.5 * limit, -limit], start=10):
        actions[i, : horizon // 2] = value
        actions[i, horizon // 2 :] = -value

    trajectory = rollout_candidates(model, state, actions)
    position = trajectory[:, :, 0]
    velocity = trajectory[:, :, 1]
    cost = (
        float(mpc["position_weight"]) * np.sum((position - target) ** 2, axis=1)
        + float(mpc["velocity_weight"]) * np.sum(velocity**2, axis=1)
        + float(mpc["terminal_position_weight"]) * (position[:, -1] - target) ** 2
        + float(mpc["terminal_velocity_weight"]) * velocity[:, -1] ** 2
        + float(mpc["action_weight"]) * np.sum(actions**2, axis=1)
    )
    best = int(np.argmin(cost))
    return float(actions[best, 0]), float(cost[best])


def run_control(
    *,
    model: LinearWorldModel,
    one_step_error: float,
    sensitivity_error: float,
    true_sensitivity_norm: float,
    predicted_sensitivity_norm: float,
    cfg: dict[str, Any],
    output_root: Path,
    command: list[str],
) -> dict[str, Any]:
    seed = int(cfg["seed"])
    dt = float(cfg["dt"])
    target = float(cfg["target_position"])
    steps = int(cfg["control_steps"])
    rng = np.random.default_rng(seed + 1000)
    state = np.zeros(2, dtype=np.float64)

    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=model.name,
        seed=seed,
        config={**cfg, "condition": {"model": model.name}},
        repo_root=REPO_ROOT,
        command=command,
    )

    positions: list[float] = []
    velocities: list[float] = []
    controls: list[float] = []
    realized_cost = 0.0
    divergence_active = False

    for step in range(steps):
        action, predicted_plan_cost = choose_mpc_action(model, state, target, cfg, rng)
        next_state = true_step(state, action, dt)
        position_error = float(next_state[0] - target)
        realized_cost += position_error**2 + 0.05 * float(next_state[1]) ** 2 + 0.005 * action**2

        if abs(position_error) > 2.0 and not divergence_active:
            recorder.log_failure(
                category="closed_loop_divergence",
                step=step,
                time_s=(step + 1) * dt,
                details={
                    "position_error": position_error,
                    "model": model.name,
                    "action": action,
                },
            )
            divergence_active = True
        elif abs(position_error) < 1.5:
            divergence_active = False

        recorder.log_step(
            step=step,
            time_s=(step + 1) * dt,
            position=float(next_state[0]),
            velocity=float(next_state[1]),
            target_position=target,
            action=action,
            position_error=position_error,
            predicted_plan_cost=predicted_plan_cost,
        )
        positions.append(float(next_state[0]))
        velocities.append(float(next_state[1]))
        controls.append(action)
        state = next_state

    position_array = np.asarray(positions, dtype=np.float64)
    velocity_array = np.asarray(velocities, dtype=np.float64)
    control_array = np.asarray(controls, dtype=np.float64)
    summary = {
        "model": model.name,
        "one_step_rmse": one_step_error,
        "counterfactual_sensitivity_error": sensitivity_error,
        "true_counterfactual_sensitivity_norm": true_sensitivity_norm,
        "predicted_counterfactual_sensitivity_norm": predicted_sensitivity_norm,
        "closed_loop_position_rmse": float(np.sqrt(np.mean((position_array - target) ** 2))),
        "final_position": float(position_array[-1]),
        "final_position_error": float(abs(position_array[-1] - target)),
        "final_velocity": float(velocity_array[-1]),
        "realized_control_cost": float(realized_cost),
        "mean_action_magnitude": float(np.mean(np.abs(control_array))),
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_experiment(cfg: dict[str, Any], output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    dt = float(cfg["dt"])
    train = generate_dataset(
        samples=int(cfg["train_samples"]),
        seed=int(cfg["seed"]),
        dt=dt,
        action_std=float(cfg["train_action_std"]),
        noise_std=float(cfg["observation_noise_std"]),
    )
    test = generate_dataset(
        samples=int(cfg["test_samples"]),
        seed=int(cfg["seed"]) + 1,
        dt=dt,
        action_std=float(cfg["train_action_std"]),
        noise_std=float(cfg["observation_noise_std"]),
    )
    models = build_models(*train)

    model_payload = {
        name: {
            "action_aware": model.action_aware,
            "weights": model.weights.tolist(),
        }
        for name, model in models.items()
    }
    write_json(output_root / "models.json", model_payload)

    test_states, test_actions, test_next = test
    cf_states = test_states[: min(512, len(test_states))]
    rows: list[dict[str, Any]] = []
    for name in cfg["models"]:
        model = models[str(name)]
        pred_error = one_step_rmse(model, test_states, test_actions, test_next)
        sensitivity_error, true_norm, predicted_norm = counterfactual_sensitivity_metrics(
            model,
            cf_states,
            float(cfg["counterfactual_action"]),
            dt,
        )
        rows.append(
            run_control(
                model=model,
                one_step_error=pred_error,
                sensitivity_error=sensitivity_error,
                true_sensitivity_norm=true_norm,
                predicted_sensitivity_norm=predicted_norm,
                cfg=cfg,
                output_root=output_root,
                command=command,
            )
        )

    write_csv(output_root / "model_metrics.csv", rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "models": list(cfg["models"]),
            "passive_test_action_std": float(cfg["train_action_std"]),
            "counterfactual_action": float(cfg["counterfactual_action"]),
            "metrics_file": "model_metrics.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Smaller MPC search for CI.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["train_samples"] = 2500
        cfg["test_samples"] = 1000
        cfg["control_steps"] = 35
        cfg["mpc"] = dict(cfg["mpc"])
        cfg["mpc"]["candidates"] = 1024
        cfg["mpc"]["horizon"] = 16

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root, sys.argv)
    print(f"Lab 29 complete: {len(rows)} world-model conditions")
    print(f"metrics: {output_root / 'model_metrics.csv'}")
    for row in rows:
        print(
            f"{row['model']:<18} one-step={row['one_step_rmse']:.5f} "
            f"cf-error={row['counterfactual_sensitivity_error']:.4f} "
            f"final-error={row['final_position_error']:.4f} "
            f"control-rmse={row['closed_loop_position_rmse']:.4f}"
        )


if __name__ == "__main__":
    main()
