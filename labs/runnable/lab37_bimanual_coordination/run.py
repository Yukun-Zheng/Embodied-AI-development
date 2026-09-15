#!/usr/bin/env python3
"""Lab 37 — bimanual coordination through shared-object relative feedback.

Two 1-D end-effectors manipulate one compliant object. The object center should
follow a common motion command while the end-effector separation should remain
near a nominal grasp width. Episodes pair actuator-gain asymmetry with a short
unilateral disturbance on the left arm.

Controls:
- independent_world: each arm tracks its own world-frame endpoint target;
- midpoint_only: both arms regulate only object midpoint, with no relative term;
- relative_coordinated: midpoint + explicit relative-separation feedback;
- wrong_relative_sign: same information/budget but the relative correction sign
  is reversed.

The scientific point is not whether both endpoints eventually reach their final
positions. We evaluate transient shared-object strain and internal coupling force
as closed-loop outcomes of the coordination mechanism.
"""

from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab37_bimanual_coordination"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass(frozen=True)
class Trial:
    episode: int
    left_gain: float
    right_gain: float
    disturbance: float
    target_center: float


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    low = int(math.floor(position))
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def build_trials(cfg: dict[str, Any]) -> list[Trial]:
    rng = random.Random(int(cfg["seed"]))
    return [
        Trial(
            episode=episode,
            left_gain=rng.uniform(
                float(cfg["left_gain_min"]), float(cfg["left_gain_max"])
            ),
            right_gain=rng.uniform(
                float(cfg["right_gain_min"]), float(cfg["right_gain_max"])
            ),
            disturbance=rng.uniform(
                float(cfg["disturbance_min"]), float(cfg["disturbance_max"])
            ),
            target_center=rng.uniform(
                float(cfg["target_center_min"]), float(cfg["target_center_max"])
            ),
        )
        for episode in range(int(cfg["episodes"]))
    ]


def desired_center(time_s: float, trial: Trial, cfg: dict[str, Any]) -> tuple[float, float]:
    start = float(cfg["trajectory_start_s"])
    if time_s <= start:
        return 0.0, 0.0
    tau = time_s - start
    rate = float(cfg["trajectory_rate"])
    exp_term = math.exp(-rate * tau)
    position = trial.target_center * (1.0 - exp_term)
    velocity = trial.target_center * rate * exp_term
    return position, velocity


def controller(
    *,
    condition: str,
    center_desired: float,
    center_velocity_desired: float,
    x_left: float,
    x_right: float,
    v_left: float,
    v_right: float,
    cfg: dict[str, Any],
) -> tuple[float, float, dict[str, float]]:
    nominal = float(cfg["nominal_separation"])
    center = 0.5 * (x_left + x_right)
    center_velocity = 0.5 * (v_left + v_right)
    separation = x_right - x_left
    relative_velocity = v_right - v_left

    center_error = center_desired - center
    separation_error = nominal - separation

    if condition == "independent_world":
        desired_left = center_desired - 0.5 * nominal
        desired_right = center_desired + 0.5 * nominal
        u_left = float(cfg["independent_kp"]) * (desired_left - x_left) + float(
            cfg["independent_kd"]
        ) * (center_velocity_desired - v_left)
        u_right = float(cfg["independent_kp"]) * (desired_right - x_right) + float(
            cfg["independent_kd"]
        ) * (center_velocity_desired - v_right)
        common_effort = 0.5 * (u_left + u_right)
        differential_effort = u_right - u_left
    else:
        common_effort = float(cfg["center_kp"]) * center_error + float(
            cfg["center_kd"]
        ) * (center_velocity_desired - center_velocity)
        correction = float(cfg["relative_kp"]) * separation_error + float(
            cfg["relative_kd"]
        ) * (-relative_velocity)

        if condition == "midpoint_only":
            correction = 0.0
        elif condition == "wrong_relative_sign":
            correction = -correction
        elif condition != "relative_coordinated":
            raise ValueError(f"Unknown condition: {condition}")

        # Positive correction increases separation: push right arm right and
        # left arm left. The two commands keep the same common-mode budget.
        u_left = common_effort - 0.5 * correction
        u_right = common_effort + 0.5 * correction
        differential_effort = correction

    limit = float(cfg["max_effort"])
    u_left = clamp(u_left, -limit, limit)
    u_right = clamp(u_right, -limit, limit)

    return u_left, u_right, {
        "center": center,
        "center_velocity": center_velocity,
        "separation": separation,
        "relative_velocity": relative_velocity,
        "center_error": center_error,
        "separation_error": separation_error,
        "common_effort": common_effort,
        "differential_effort": differential_effort,
    }


def run_episode(
    *,
    condition: str,
    trial: Trial,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> dict[str, Any]:
    dt = float(cfg["dt"])
    steps = int(round(float(cfg["duration_s"]) / dt))
    nominal = float(cfg["nominal_separation"])
    spring_k = float(cfg["object_spring_k"])
    object_damping = float(cfg["object_damping"])
    log_stride = int(cfg["log_stride"])

    x_left = -0.5 * nominal
    x_right = 0.5 * nominal
    v_left = 0.0
    v_right = 0.0

    squared_center_error = 0.0
    squared_relative_error = 0.0
    peak_abs_strain = 0.0
    internal_forces: list[float] = []
    efforts: list[float] = []
    first_strain_violation_logged = False

    for step in range(steps):
        time_s = step * dt
        center_desired, center_velocity_desired = desired_center(time_s, trial, cfg)
        u_left, u_right, diagnostics = controller(
            condition=condition,
            center_desired=center_desired,
            center_velocity_desired=center_velocity_desired,
            x_left=x_left,
            x_right=x_right,
            v_left=v_left,
            v_right=v_right,
            cfg=cfg,
        )

        if float(cfg["disturbance_start_s"]) < time_s < float(
            cfg["disturbance_end_s"]
        ):
            u_left += trial.disturbance

        effort_limit = float(cfg["max_effort"])
        u_left = clamp(u_left, -effort_limit, effort_limit)
        u_right = clamp(u_right, -effort_limit, effort_limit)

        separation = x_right - x_left
        relative_velocity = v_right - v_left
        strain = separation - nominal
        internal_force = spring_k * strain + object_damping * relative_velocity

        # A positive tensile force pulls the two end-effectors together.
        acceleration_left = trial.left_gain * u_left + internal_force
        acceleration_right = trial.right_gain * u_right - internal_force

        v_left += acceleration_left * dt
        v_right += acceleration_right * dt
        x_left += v_left * dt
        x_right += v_right * dt

        center = 0.5 * (x_left + x_right)
        separation = x_right - x_left
        strain = separation - nominal
        center_error = center - center_desired

        squared_center_error += center_error**2
        squared_relative_error += strain**2
        peak_abs_strain = max(peak_abs_strain, abs(strain))
        internal_forces.append(abs(internal_force))
        efforts.append(abs(u_left) + abs(u_right))

        if (
            abs(strain) >= float(cfg["strain_limit"])
            and not first_strain_violation_logged
        ):
            first_strain_violation_logged = True
            recorder.log_failure(
                category="shared_object_strain_limit",
                step=step,
                time_s=time_s,
                details={
                    "episode": trial.episode,
                    "strain": strain,
                    "limit": float(cfg["strain_limit"]),
                    "condition": condition,
                },
            )

        if step % log_stride == 0 or step == steps - 1:
            recorder.log_step(
                episode=trial.episode,
                step=step,
                time_s=time_s,
                condition=condition,
                target_center=trial.target_center,
                center_desired=center_desired,
                center=center,
                center_error=center_error,
                nominal_separation=nominal,
                separation=separation,
                strain=strain,
                internal_force=internal_force,
                x_left=x_left,
                x_right=x_right,
                v_left=v_left,
                v_right=v_right,
                u_left=u_left,
                u_right=u_right,
                left_gain=trial.left_gain,
                right_gain=trial.right_gain,
                unilateral_disturbance=(
                    trial.disturbance
                    if float(cfg["disturbance_start_s"]) < time_s < float(
                        cfg["disturbance_end_s"]
                    )
                    else 0.0
                ),
                center_control_error=diagnostics["center_error"],
                relative_control_error=diagnostics["separation_error"],
                differential_effort=diagnostics["differential_effort"],
            )

    final_center = 0.5 * (x_left + x_right)
    final_separation = x_right - x_left
    final_center_error = abs(final_center - trial.target_center)
    final_separation_error = abs(final_separation - nominal)
    center_rmse = math.sqrt(squared_center_error / steps)
    relative_rmse = math.sqrt(squared_relative_error / steps)
    success = (
        final_center_error < float(cfg["final_center_tolerance"])
        and final_separation_error < float(cfg["final_separation_tolerance"])
        and peak_abs_strain < float(cfg["strain_limit"])
    )

    return {
        "condition": condition,
        "episode": trial.episode,
        "success": int(success),
        "center_rmse": center_rmse,
        "relative_rmse": relative_rmse,
        "peak_abs_strain": peak_abs_strain,
        "p95_internal_force": percentile(internal_forces, 0.95),
        "final_center_error": final_center_error,
        "final_separation_error": final_separation_error,
        "mean_total_effort": statistics.fmean(efforts),
        "left_gain": trial.left_gain,
        "right_gain": trial.right_gain,
        "disturbance": trial.disturbance,
        "target_center": trial.target_center,
    }


def aggregate_condition(condition: str, rows: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        raise RuntimeError(f"No episode rows for {condition}")
    peak_strains = [float(row["peak_abs_strain"]) for row in rows]
    return {
        "condition": condition,
        "episodes": len(rows),
        "success_rate": statistics.fmean(float(row["success"]) for row in rows),
        "strain_violation_rate": statistics.fmean(
            float(row["peak_abs_strain"] >= float(cfg["strain_limit"]))
            for row in rows
        ),
        "mean_center_rmse": statistics.fmean(float(row["center_rmse"]) for row in rows),
        "mean_relative_rmse": statistics.fmean(float(row["relative_rmse"]) for row in rows),
        "mean_peak_abs_strain": statistics.fmean(peak_strains),
        "p95_peak_abs_strain": percentile(peak_strains, 0.95),
        "mean_p95_internal_force": statistics.fmean(
            float(row["p95_internal_force"]) for row in rows
        ),
        "mean_final_center_error": statistics.fmean(
            float(row["final_center_error"]) for row in rows
        ),
        "mean_final_separation_error": statistics.fmean(
            float(row["final_separation_error"]) for row in rows
        ),
        "mean_total_effort": statistics.fmean(
            float(row["mean_total_effort"]) for row in rows
        ),
    }


def run_experiment(cfg: dict[str, Any], output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output.mkdir(parents=True, exist_ok=True)
    trials = build_trials(cfg)
    write_csv(
        output / "trial_specs.csv",
        [
            {
                "episode": trial.episode,
                "left_gain": trial.left_gain,
                "right_gain": trial.right_gain,
                "disturbance": trial.disturbance,
                "target_center": trial.target_center,
            }
            for trial in trials
        ],
    )

    all_episode_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []

    for condition in [str(value) for value in cfg["conditions"]]:
        recorder = RunRecorder(
            output_root=output / "runs",
            lab_id=LAB_ID,
            condition=condition,
            seed=int(cfg["seed"]),
            config=cfg,
            repo_root=REPO_ROOT,
        )
        rows = [
            run_episode(
                condition=condition,
                trial=trial,
                cfg=cfg,
                recorder=recorder,
            )
            for trial in trials
        ]
        summary = aggregate_condition(condition, rows, cfg)
        recorder.finalize(summary)
        all_episode_rows.extend(rows)
        condition_rows.append(summary)

    write_csv(output / "episode_metrics.csv", all_episode_rows)
    write_csv(output / "condition_metrics.csv", condition_rows)
    write_json(
        output / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "episodes_per_condition": int(cfg["episodes"]),
            "conditions": condition_rows,
        },
    )
    return all_episode_rows, condition_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab37"))
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["episodes"] = min(int(cfg["episodes"]), 120)

    _, condition_rows = run_experiment(cfg, args.output)
    print("Lab 37 bimanual coordination experiment complete")
    for row in condition_rows:
        print(
            f"{row['condition']:24s} "
            f"success={row['success_rate']:.3f} "
            f"center-rmse={row['mean_center_rmse']:.4f} "
            f"rel-rmse={row['mean_relative_rmse']:.4f} "
            f"peak-strain={row['mean_peak_abs_strain']:.4f} "
            f"p95-force={row['mean_p95_internal_force']:.3f}"
        )
    print(f"metrics: {args.output / 'condition_metrics.csv'}")


if __name__ == "__main__":
    main()
