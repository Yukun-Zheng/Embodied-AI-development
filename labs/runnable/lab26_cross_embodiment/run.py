#!/usr/bin/env python3
"""Lab 26 — cross-embodiment transfer with explicit interface and morphology controls.

The same canonical PD policy is evaluated on two seen embodiments and two held-out
embodiments. The experiment separates four issues that are often conflated:

1. tensor/interface compatibility;
2. observation/action semantic calibration;
3. support for multiple *seen* robot identities;
4. zero-shot transfer to an *unseen* morphology descriptor.

No task rollout adaptation is permitted on held-out embodiments C/D.
"""

from __future__ import annotations

import argparse
import copy
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

LAB_ID = "lab26_cross_embodiment"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass(frozen=True)
class Embodiment:
    name: str
    split: str
    mass: float
    damping: float
    position_sensor_scale: float
    velocity_sensor_scale: float
    action_scale: float
    action_sign: float
    hardware_command_limit: float


@dataclass(frozen=True)
class Trial:
    episode: int
    initial_position: float
    initial_velocity: float
    goal: float


def embodiment_from_dict(data: dict[str, Any]) -> Embodiment:
    return Embodiment(
        name=str(data["name"]),
        split=str(data["split"]),
        mass=float(data["mass"]),
        damping=float(data["damping"]),
        position_sensor_scale=float(data["position_sensor_scale"]),
        velocity_sensor_scale=float(data["velocity_sensor_scale"]),
        action_scale=float(data["action_scale"]),
        action_sign=float(data["action_sign"]),
        hardware_command_limit=float(data["hardware_command_limit"]),
    )


def build_trials(cfg: dict[str, Any]) -> list[Trial]:
    trial_cfg = cfg["trial"]
    rng = np.random.default_rng(int(cfg["seed"]))
    trials: list[Trial] = []
    for episode in range(int(cfg["episodes"])):
        position = float(
            rng.uniform(
                float(trial_cfg["initial_position_min"]),
                float(trial_cfg["initial_position_max"]),
            )
        )
        velocity = float(
            rng.uniform(
                float(trial_cfg["initial_velocity_min"]),
                float(trial_cfg["initial_velocity_max"]),
            )
        )
        while True:
            goal = float(rng.uniform(float(trial_cfg["goal_min"]), float(trial_cfg["goal_max"])))
            if abs(goal - position) >= float(trial_cfg["minimum_goal_distance"]):
                break
        trials.append(
            Trial(
                episode=episode,
                initial_position=position,
                initial_velocity=velocity,
                goal=goal,
            )
        )
    return trials


def observe(position: float, velocity: float, embodiment: Embodiment) -> tuple[float, float]:
    return (
        embodiment.position_sensor_scale * position,
        embodiment.velocity_sensor_scale * velocity,
    )


def canonicalize_observation(
    raw_position: float,
    raw_velocity: float,
    embodiment: Embodiment,
) -> tuple[float, float]:
    return (
        raw_position / embodiment.position_sensor_scale,
        raw_velocity / embodiment.velocity_sensor_scale,
    )


def physical_force_from_hardware(command: float, embodiment: Embodiment) -> float:
    return embodiment.action_sign * embodiment.action_scale * command


def hardware_from_physical_force(force: float, embodiment: Embodiment) -> float:
    return embodiment.action_sign * force / embodiment.action_scale


def canonical_policy_acceleration(
    *, position: float, velocity: float, goal: float, kp: float, kd: float
) -> float:
    return kp * (goal - position) - kd * velocity


def wrong_tag_name(name: str) -> str:
    return {
        "A": "B",
        "B": "A",
        "C": "A",
        "D": "A",
    }[name]


def descriptor_for_condition(
    *,
    condition: str,
    embodiment: Embodiment,
    embodiments: dict[str, Embodiment],
) -> Embodiment | None:
    if condition == "morphology_conditioned":
        return embodiment
    if condition == "seen_robot_lookup":
        # A/B have robot-specific entries. Held-out C/D cannot be looked up and
        # therefore fall back to the nominal A dynamics. This deliberately
        # separates multi-seen support from unseen morphology transfer.
        return embodiment if embodiment.name in {"A", "B"} else embodiments["A"]
    if condition == "wrong_morphology_tag":
        return embodiments[wrong_tag_name(embodiment.name)]
    if condition == "wrong_action_semantics":
        return embodiment
    return None


def command_for_condition(
    *,
    condition: str,
    raw_position: float,
    raw_velocity: float,
    goal: float,
    embodiment: Embodiment,
    descriptor: Embodiment | None,
    policy_cfg: dict[str, Any],
) -> tuple[float, dict[str, float]]:
    kp = float(policy_cfg["kp"])
    kd = float(policy_cfg["kd"])

    if condition == "raw_shared":
        # Shape-compatible but semantics-blind: raw sensor coordinates are
        # treated as SI state, and the canonical force-like output is sent
        # directly as a hardware command.
        estimated_position = raw_position
        estimated_velocity = raw_velocity
        canonical_acceleration = canonical_policy_acceleration(
            position=estimated_position,
            velocity=estimated_velocity,
            goal=goal,
            kp=kp,
            kd=kd,
        )
        desired_force = canonical_acceleration
        hardware_command = desired_force
        return hardware_command, {
            "estimated_position": estimated_position,
            "estimated_velocity": estimated_velocity,
            "canonical_acceleration": canonical_acceleration,
            "desired_force": desired_force,
            "descriptor_mass": float("nan"),
            "descriptor_damping": float("nan"),
        }

    estimated_position, estimated_velocity = canonicalize_observation(
        raw_position, raw_velocity, embodiment
    )
    canonical_acceleration = canonical_policy_acceleration(
        position=estimated_position,
        velocity=estimated_velocity,
        goal=goal,
        kp=kp,
        kd=kd,
    )

    if condition == "canonical_interface_only":
        descriptor_mass = float(policy_cfg["nominal_mass"])
        descriptor_damping = float(policy_cfg["nominal_damping"])
    else:
        if descriptor is None:
            raise ValueError(f"Condition {condition} requires a morphology descriptor")
        descriptor_mass = descriptor.mass
        descriptor_damping = descriptor.damping

    # The morphology-aware adapter maps the shared desired acceleration into
    # physical force using the selected body descriptor.
    desired_force = (
        descriptor_mass * canonical_acceleration
        + descriptor_damping * estimated_velocity
    )

    if condition == "wrong_action_semantics":
        # Pretend every robot uses Robot-A sign/scale. B/D therefore receive
        # physically reversed force despite correct state and morphology.
        hardware_command = desired_force
    else:
        hardware_command = hardware_from_physical_force(desired_force, embodiment)

    return hardware_command, {
        "estimated_position": estimated_position,
        "estimated_velocity": estimated_velocity,
        "canonical_acceleration": canonical_acceleration,
        "desired_force": desired_force,
        "descriptor_mass": descriptor_mass,
        "descriptor_damping": descriptor_damping,
    }


def run_episode(
    *,
    condition: str,
    embodiment: Embodiment,
    embodiments: dict[str, Embodiment],
    trial: Trial,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> dict[str, Any]:
    dt = float(cfg["dt"])
    steps = int(cfg["steps"])
    trial_cfg = cfg["trial"]
    position_tolerance = float(trial_cfg["success_position_tolerance"])
    velocity_tolerance = float(trial_cfg["success_velocity_tolerance"])
    policy_cfg = cfg["policy"]

    position = trial.initial_position
    velocity = trial.initial_velocity
    integrated_squared_error = 0.0
    force_energy = 0.0
    saturated_steps = 0
    max_abs_position = abs(position)
    descriptor = descriptor_for_condition(
        condition=condition,
        embodiment=embodiment,
        embodiments=embodiments,
    )

    for step in range(steps):
        raw_position, raw_velocity = observe(position, velocity, embodiment)
        hardware_unclipped, internals = command_for_condition(
            condition=condition,
            raw_position=raw_position,
            raw_velocity=raw_velocity,
            goal=trial.goal,
            embodiment=embodiment,
            descriptor=descriptor,
            policy_cfg=policy_cfg,
        )
        hardware_command = float(
            np.clip(
                hardware_unclipped,
                -embodiment.hardware_command_limit,
                embodiment.hardware_command_limit,
            )
        )
        saturated = abs(hardware_command - hardware_unclipped) > 1e-12
        saturated_steps += int(saturated)
        physical_force = physical_force_from_hardware(hardware_command, embodiment)
        acceleration = (
            physical_force - embodiment.damping * velocity
        ) / embodiment.mass

        before_position = position
        before_velocity = velocity
        velocity = velocity + dt * acceleration
        position = position + dt * velocity
        error = trial.goal - position
        integrated_squared_error += error * error * dt
        force_energy += physical_force * physical_force * dt
        max_abs_position = max(max_abs_position, abs(position))

        recorder.log_step(
            episode=trial.episode,
            embodiment=embodiment.name,
            split=embodiment.split,
            adaptation_steps=0,
            step=step,
            time_s=step * dt,
            goal=trial.goal,
            before_position=before_position,
            before_velocity=before_velocity,
            raw_position=raw_position,
            raw_velocity=raw_velocity,
            estimated_position=internals["estimated_position"],
            estimated_velocity=internals["estimated_velocity"],
            canonical_acceleration=internals["canonical_acceleration"],
            descriptor_mass=internals["descriptor_mass"],
            descriptor_damping=internals["descriptor_damping"],
            desired_force=internals["desired_force"],
            hardware_command_unclipped=hardware_unclipped,
            hardware_command=hardware_command,
            saturated=int(saturated),
            physical_force=physical_force,
            acceleration=acceleration,
            after_position=position,
            after_velocity=velocity,
            error=error,
        )

    final_position_error = abs(trial.goal - position)
    final_velocity_error = abs(velocity)
    success = (
        final_position_error < position_tolerance
        and final_velocity_error < velocity_tolerance
    )
    return {
        "episode": trial.episode,
        "embodiment": embodiment.name,
        "split": embodiment.split,
        "seen": int(embodiment.split == "seen"),
        "adaptation_steps": 0,
        "success": int(success),
        "final_position_error": final_position_error,
        "final_velocity_error": final_velocity_error,
        "integrated_squared_error": integrated_squared_error,
        "force_energy": force_energy,
        "saturation_fraction": saturated_steps / steps,
        "max_abs_position": max_abs_position,
        "goal": trial.goal,
        "initial_position": trial.initial_position,
        "initial_velocity": trial.initial_velocity,
    }


def mean(rows: list[dict[str, Any]], key: str) -> float:
    return float(np.mean([float(row[key]) for row in rows])) if rows else float("nan")


def aggregate_rows(
    *, condition: str, episode_rows: list[dict[str, Any]], embodiment: Embodiment
) -> dict[str, Any]:
    rows = [row for row in episode_rows if row["embodiment"] == embodiment.name]
    return {
        "condition": condition,
        "embodiment": embodiment.name,
        "split": embodiment.split,
        "seen": int(embodiment.split == "seen"),
        "episodes": len(rows),
        "adaptation_steps": 0,
        "success_rate": mean(rows, "success"),
        "mean_final_position_error": mean(rows, "final_position_error"),
        "mean_final_velocity_error": mean(rows, "final_velocity_error"),
        "mean_integrated_squared_error": mean(rows, "integrated_squared_error"),
        "mean_force_energy": mean(rows, "force_energy"),
        "mean_saturation_fraction": mean(rows, "saturation_fraction"),
        "mean_max_abs_position": mean(rows, "max_abs_position"),
    }


def run_condition(
    *,
    condition: str,
    cfg: dict[str, Any],
    embodiments: dict[str, Embodiment],
    trials: list[Trial],
    output_root: Path,
    command: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=condition,
        seed=int(cfg["seed"]),
        config={**cfg, "condition": {"name": condition}},
        repo_root=REPO_ROOT,
        command=command,
    )

    episode_rows: list[dict[str, Any]] = []
    for embodiment in embodiments.values():
        for trial in trials:
            row = run_episode(
                condition=condition,
                embodiment=embodiment,
                embodiments=embodiments,
                trial=trial,
                cfg=cfg,
                recorder=recorder,
            )
            episode_rows.append(row)
            if not bool(row["success"]):
                recorder.log_failure(
                    category="tracking_failure",
                    step=trial.episode,
                    time_s=float(cfg["steps"]) * float(cfg["dt"]),
                    details={
                        "embodiment": embodiment.name,
                        "split": embodiment.split,
                        "condition": condition,
                        "final_position_error": row["final_position_error"],
                        "final_velocity_error": row["final_velocity_error"],
                        "saturation_fraction": row["saturation_fraction"],
                        "adaptation_steps": 0,
                    },
                )

    write_csv(recorder.run_dir / "episodes.csv", episode_rows)
    embodiment_rows = [
        aggregate_rows(
            condition=condition,
            episode_rows=episode_rows,
            embodiment=embodiment,
        )
        for embodiment in embodiments.values()
    ]
    write_csv(recorder.run_dir / "embodiment_metrics.csv", embodiment_rows)

    seen_rows = [row for row in episode_rows if int(row["seen"]) == 1]
    unseen_rows = [row for row in episode_rows if int(row["seen"]) == 0]
    interp_rows = [
        row for row in episode_rows if row["split"] == "unseen_interpolation"
    ]
    extrap_rows = [
        row for row in episode_rows if row["split"] == "unseen_extrapolation"
    ]

    summary = {
        "condition": condition,
        "episodes_per_embodiment": len(trials),
        "total_episodes": len(episode_rows),
        "policy_parameter_count": 2,
        "adaptation_steps_seen": 0,
        "adaptation_steps_unseen": 0,
        "seen_success_rate": mean(seen_rows, "success"),
        "unseen_success_rate": mean(unseen_rows, "success"),
        "unseen_interpolation_success_rate": mean(interp_rows, "success"),
        "unseen_extrapolation_success_rate": mean(extrap_rows, "success"),
        "overall_success_rate": mean(episode_rows, "success"),
        "mean_final_position_error": mean(episode_rows, "final_position_error"),
        "mean_integrated_squared_error": mean(episode_rows, "integrated_squared_error"),
        "mean_force_energy": mean(episode_rows, "force_energy"),
        "mean_saturation_fraction": mean(episode_rows, "saturation_fraction"),
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}, embodiment_rows


def interface_checks(embodiments: dict[str, Embodiment]) -> list[dict[str, Any]]:
    probes = [(-0.73, 0.21, -2.4), (0.44, -0.17, 1.7)]
    rows: list[dict[str, Any]] = []
    for embodiment in embodiments.values():
        state_errors: list[float] = []
        action_errors: list[float] = []
        for position, velocity, force in probes:
            raw_position, raw_velocity = observe(position, velocity, embodiment)
            reconstructed_position, reconstructed_velocity = canonicalize_observation(
                raw_position, raw_velocity, embodiment
            )
            command = hardware_from_physical_force(force, embodiment)
            reconstructed_force = physical_force_from_hardware(command, embodiment)
            state_errors.extend(
                [
                    abs(position - reconstructed_position),
                    abs(velocity - reconstructed_velocity),
                ]
            )
            action_errors.append(abs(force - reconstructed_force))
        rows.append(
            {
                "embodiment": embodiment.name,
                "split": embodiment.split,
                "max_state_roundtrip_error": max(state_errors),
                "max_action_roundtrip_error": max(action_errors),
            }
        )
    return rows


def run_experiment(
    cfg: dict[str, Any], *, output_root: Path, command: list[str]
) -> list[dict[str, Any]]:
    embodiment_list = [embodiment_from_dict(data) for data in cfg["embodiments"]]
    embodiments = {embodiment.name: embodiment for embodiment in embodiment_list}
    if set(embodiments) != {"A", "B", "C", "D"}:
        raise ValueError("Lab 26 expects embodiments A/B/C/D")
    if any(embodiments[name].split != "seen" for name in ("A", "B")):
        raise ValueError("A/B must be seen embodiments")
    if any(embodiments[name].split == "seen" for name in ("C", "D")):
        raise ValueError("C/D must be held-out embodiments")

    trials = build_trials(cfg)
    checks = interface_checks(embodiments)
    write_csv(output_root / "interface_checks.csv", checks)

    condition_rows: list[dict[str, Any]] = []
    all_embodiment_rows: list[dict[str, Any]] = []
    for condition in cfg["conditions"]:
        summary, embodiment_rows = run_condition(
            condition=str(condition),
            cfg=cfg,
            embodiments=embodiments,
            trials=trials,
            output_root=output_root,
            command=command,
        )
        condition_rows.append(summary)
        all_embodiment_rows.extend(embodiment_rows)

    write_csv(output_root / "condition_metrics.csv", condition_rows)
    write_csv(output_root / "embodiment_metrics.csv", all_embodiment_rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "shared_trial_schedule": True,
            "task": "1-D point-mass goal reaching",
            "canonical_policy": {
                "type": "PD desired-acceleration policy",
                "kp": float(cfg["policy"]["kp"]),
                "kd": float(cfg["policy"]["kd"]),
                "parameter_count": 2,
            },
            "seen_embodiments": ["A", "B"],
            "held_out_embodiments": ["C", "D"],
            "held_out_task_adaptation_steps": 0,
            "conditions": [str(condition) for condition in cfg["conditions"]],
            "results": {
                "condition_metrics": "condition_metrics.csv",
                "embodiment_metrics": "embodiment_metrics.csv",
                "interface_checks": "interface_checks.csv",
            },
        },
    )
    return condition_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use the deterministic CI episode count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = copy.deepcopy(cfg)
        cfg["episodes"] = int(cfg["quick_episodes"])

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 26 complete: {len(rows)} cross-embodiment controls")
    print(f"metrics: {output_root / 'condition_metrics.csv'}")
    for row in rows:
        print(
            f"{row['condition']:<25} "
            f"seen={row['seen_success_rate']:.3f} "
            f"unseen={row['unseen_success_rate']:.3f} "
            f"interp={row['unseen_interpolation_success_rate']:.3f} "
            f"extra={row['unseen_extrapolation_success_rate']:.3f} "
            f"adapt={row['adaptation_steps_unseen']}"
        )


if __name__ == "__main__":
    main()
