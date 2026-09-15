#!/usr/bin/env python3
"""Lab 40 — watchdog / safety shield in a physical closed loop.

A 1-D robot axis tracks a goal while deterministic fault scenarios inject:
- model heartbeat timeout;
- stale camera / human-state data;
- unsafe model target;
- human proximity.

The experiment compares no shield, static rules, predictive stopping without
freshness checks, a complete predictive shield, and an intentionally
conservative shield. Safety is evaluated after physical braking dynamics, not by
counting whether a Boolean rule fired.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab40_safety_shield"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass(frozen=True)
class Trial:
    scenario: str
    episode: int
    initial_position: float
    initial_velocity: float
    goal: float


@dataclass
class ShieldState:
    latched: bool = False
    reason: str = ""
    response: str = "pass"
    intervention_time_s: float | None = None
    ask_human: bool = False


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def build_trials(cfg: dict[str, Any]) -> list[Trial]:
    trial_cfg = cfg["trial"]
    trials: list[Trial] = []
    per_scenario = int(cfg["episodes_per_scenario"])
    base_seed = int(cfg["seed"])
    for scenario_index, scenario in enumerate(cfg["scenarios"]):
        rng = random.Random(base_seed + 1009 * scenario_index)
        for episode in range(per_scenario):
            trials.append(
                Trial(
                    scenario=str(scenario),
                    episode=episode,
                    initial_position=rng.uniform(
                        float(trial_cfg["initial_position_min"]),
                        float(trial_cfg["initial_position_max"]),
                    ),
                    initial_velocity=rng.uniform(
                        float(trial_cfg["initial_velocity_min"]),
                        float(trial_cfg["initial_velocity_max"]),
                    ),
                    goal=rng.uniform(
                        float(trial_cfg["normal_goal_min"]),
                        float(trial_cfg["normal_goal_max"]),
                    ),
                )
            )
    return trials


def scenario_human_initial(
    scenario: str, trial_cfg: dict[str, Any]
) -> tuple[float, float, float, bool]:
    if scenario == "stale_camera":
        return (
            float(trial_cfg["stale_camera_human_initial_position"]),
            float(trial_cfg["stale_camera_human_velocity"]),
            float(trial_cfg["stale_camera_human_stop_position"]),
            True,
        )
    if scenario == "human_proximity":
        return (
            float(trial_cfg["proximity_human_initial_position"]),
            float(trial_cfg["proximity_human_velocity"]),
            float(trial_cfg["proximity_human_stop_position"]),
            True,
        )
    return 10.0, 0.0, 10.0, False


def braking_command(
    velocity: float, *, max_brake_acceleration: float, stopped_tolerance: float
) -> float:
    if abs(velocity) <= stopped_tolerance:
        return 0.0
    return -max_brake_acceleration * (1.0 if velocity > 0.0 else -1.0)


def shield_decision(
    *,
    condition: str,
    state: ShieldState,
    time_s: float,
    position: float,
    velocity: float,
    target: float,
    measured_human_position: float,
    measured_human_velocity: float,
    human_measurement_present: bool,
    model_age_s: float,
    camera_age_s: float,
    raw_policy_acceleration: float,
    cfg: dict[str, Any],
) -> tuple[float, ShieldState, dict[str, float]]:
    plant_cfg = cfg["plant"]
    watchdog_cfg = cfg["watchdog"]
    max_brake = float(plant_cfg["max_brake_acceleration"])
    speed_toward_positive_limit = max(velocity, 0.0)
    stopping_distance = speed_toward_positive_limit**2 / (2.0 * max_brake)
    reaction_distance = speed_toward_positive_limit * float(
        watchdog_cfg["reaction_time_s"]
    )
    distance_to_joint_limit = float(plant_cfg["joint_hard_limit"]) - position
    measured_human_separation = measured_human_position - position
    closing_speed = max(velocity - measured_human_velocity, 0.0)
    brake_time = (
        speed_toward_positive_limit / max_brake
        if speed_toward_positive_limit > 0.0
        else 0.0
    )
    human_required_separation = (
        float(watchdog_cfg["human_hard_min_distance"])
        + stopping_distance
        + closing_speed * float(watchdog_cfg["reaction_time_s"])
        + max(-measured_human_velocity, 0.0) * brake_time
        + float(watchdog_cfg["predictive_human_margin"])
    )

    diagnostics = {
        "stopping_distance": stopping_distance,
        "reaction_distance": reaction_distance,
        "distance_to_joint_limit": distance_to_joint_limit,
        "measured_human_separation": measured_human_separation,
        "human_required_separation": human_required_separation,
    }

    if condition == "no_shield":
        return raw_policy_acceleration, state, diagnostics

    if not state.latched:
        allowed_goal = (
            float(watchdog_cfg["conservative_allowed_goal_abs"])
            if condition == "overconservative_shield"
            else float(watchdog_cfg["allowed_goal_abs"])
        )

        reason = ""
        response = "pass"
        ask_human = False

        if abs(target) > allowed_goal:
            if abs(target) > float(watchdog_cfg["allowed_goal_abs"]):
                reason = "unsafe_joint_target"
            else:
                reason = "conservative_goal_reject"
            response = "reject_and_ask_human"
            ask_human = True

        elif condition in {"predictive_shield", "overconservative_shield"} and model_age_s > float(
            watchdog_cfg["max_model_age_s"]
        ):
            reason = "model_timeout"
            response = "safe_stop"

        elif condition in {"predictive_shield", "overconservative_shield"} and camera_age_s > float(
            watchdog_cfg["max_camera_age_s"]
        ):
            reason = "stale_camera"
            response = "safe_stop"

        elif condition == "static_rules":
            if abs(position) >= float(plant_cfg["joint_reactive_trigger"]):
                reason = "reactive_joint_limit"
                response = "safe_stop"
            elif human_measurement_present and measured_human_separation <= float(
                watchdog_cfg["human_reactive_trigger"]
            ):
                reason = "reactive_human_proximity"
                response = "safe_stop"

        elif condition in {
            "predictive_no_freshness",
            "predictive_shield",
            "overconservative_shield",
        }:
            if speed_toward_positive_limit > 0.0 and distance_to_joint_limit <= (
                stopping_distance
                + reaction_distance
                + float(watchdog_cfg["predictive_joint_margin"])
            ):
                reason = "predictive_joint_stop"
                response = "safe_stop"
            elif human_measurement_present and measured_human_separation <= human_required_separation:
                reason = "predictive_human_proximity"
                response = "safe_stop"

        if reason:
            state.latched = True
            state.reason = reason
            state.response = response
            state.intervention_time_s = time_s
            state.ask_human = ask_human

    if state.latched:
        return (
            braking_command(
                velocity,
                max_brake_acceleration=max_brake,
                stopped_tolerance=float(watchdog_cfg["stopped_velocity_tolerance"]),
            ),
            state,
            diagnostics,
        )
    return raw_policy_acceleration, state, diagnostics


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def run_episode(
    *,
    condition: str,
    trial: Trial,
    cfg: dict[str, Any],
    recorder: RunRecorder,
    audit_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    plant_cfg = cfg["plant"]
    policy_cfg = cfg["policy"]
    watchdog_cfg = cfg["watchdog"]
    trial_cfg = cfg["trial"]
    dt = float(cfg["dt"])
    steps = int(cfg["steps"])
    fault_time = float(cfg["fault_time_s"])

    position = trial.initial_position
    velocity = trial.initial_velocity
    true_human_position, true_human_velocity, human_stop_position, human_present = (
        scenario_human_initial(trial.scenario, trial_cfg)
    )
    measured_human_position = true_human_position
    measured_human_velocity = true_human_velocity
    last_camera_update_time = 0.0
    last_model_update_time = 0.0
    last_policy_acceleration = 0.0
    shield_state = ShieldState()
    intervention_audited = False
    joint_violation = False
    human_collision = False
    joint_violation_audited = False
    human_collision_audited = False
    min_human_separation = float("inf")
    max_abs_position = abs(position)
    integrated_squared_error = 0.0
    control_energy = 0.0

    for step in range(steps):
        time_s = step * dt

        if human_present and time_s >= fault_time and true_human_position > human_stop_position:
            true_human_position = max(
                human_stop_position,
                true_human_position + true_human_velocity * dt,
            )
            if true_human_position <= human_stop_position:
                true_human_velocity = 0.0

        camera_alive = not (
            trial.scenario == "stale_camera" and time_s >= fault_time
        )
        if camera_alive:
            measured_human_position = true_human_position
            measured_human_velocity = true_human_velocity
            last_camera_update_time = time_s
        camera_age_s = time_s - last_camera_update_time

        model_alive = not (
            trial.scenario == "model_timeout" and time_s >= fault_time
        )
        target = trial.goal
        if trial.scenario == "unsafe_joint_target" and time_s >= fault_time:
            target = float(trial_cfg["unsafe_joint_target"])
        if model_alive:
            last_policy_acceleration = clamp(
                float(policy_cfg["kp"]) * (target - position)
                - float(policy_cfg["kd"]) * velocity,
                -float(plant_cfg["max_policy_acceleration"]),
                float(plant_cfg["max_policy_acceleration"]),
            )
            last_model_update_time = time_s
        model_age_s = time_s - last_model_update_time

        raw_policy_acceleration = last_policy_acceleration
        command_acceleration, shield_state, diagnostics = shield_decision(
            condition=condition,
            state=shield_state,
            time_s=time_s,
            position=position,
            velocity=velocity,
            target=target,
            measured_human_position=measured_human_position,
            measured_human_velocity=measured_human_velocity,
            human_measurement_present=human_present,
            model_age_s=model_age_s,
            camera_age_s=camera_age_s,
            raw_policy_acceleration=raw_policy_acceleration,
            cfg=cfg,
        )

        if shield_state.latched and not intervention_audited:
            audit_rows.append(
                {
                    "event": "intervention",
                    "condition": condition,
                    "scenario": trial.scenario,
                    "episode": trial.episode,
                    "time_s": time_s,
                    "reason": shield_state.reason,
                    "response": shield_state.response,
                    "ask_human": shield_state.ask_human,
                    "model_age_s": model_age_s,
                    "camera_age_s": camera_age_s,
                    "position": position,
                    "velocity": velocity,
                    "target": target,
                    **diagnostics,
                }
            )
            intervention_audited = True

        before_position = position
        before_velocity = velocity
        command_acceleration = clamp(
            command_acceleration,
            -float(plant_cfg["max_brake_acceleration"]),
            float(plant_cfg["max_brake_acceleration"]),
        )
        physical_acceleration = (
            command_acceleration - float(plant_cfg["damping"]) * velocity
        )
        velocity = velocity + physical_acceleration * dt
        if shield_state.latched and before_velocity * velocity < 0.0:
            velocity = 0.0
        position = position + velocity * dt

        max_abs_position = max(max_abs_position, abs(position))
        error = trial.goal - position
        integrated_squared_error += error * error * dt
        control_energy += command_acceleration * command_acceleration * dt
        if human_present:
            min_human_separation = min(
                min_human_separation, true_human_position - position
            )

        current_joint_violation = abs(position) > float(plant_cfg["joint_hard_limit"])
        current_human_collision = (
            human_present
            and true_human_position - position
            < float(watchdog_cfg["human_hard_min_distance"])
        )
        joint_violation = joint_violation or current_joint_violation
        human_collision = human_collision or current_human_collision

        if current_joint_violation and not joint_violation_audited:
            audit_rows.append(
                {
                    "event": "safety_violation",
                    "violation": "hard_joint_limit",
                    "condition": condition,
                    "scenario": trial.scenario,
                    "episode": trial.episode,
                    "time_s": time_s,
                    "position": position,
                    "velocity": velocity,
                    "target": target,
                    "model_age_s": model_age_s,
                    "camera_age_s": camera_age_s,
                    "shield_reason": shield_state.reason,
                }
            )
            recorder.log_failure(
                category="hard_joint_violation",
                step=step,
                time_s=time_s,
                details={
                    "scenario": trial.scenario,
                    "condition": condition,
                    "position": position,
                    "velocity": velocity,
                    "target": target,
                    "shield_reason": shield_state.reason,
                },
            )
            joint_violation_audited = True

        if current_human_collision and not human_collision_audited:
            audit_rows.append(
                {
                    "event": "safety_violation",
                    "violation": "human_collision",
                    "condition": condition,
                    "scenario": trial.scenario,
                    "episode": trial.episode,
                    "time_s": time_s,
                    "position": position,
                    "velocity": velocity,
                    "true_human_position": true_human_position,
                    "measured_human_position": measured_human_position,
                    "model_age_s": model_age_s,
                    "camera_age_s": camera_age_s,
                    "shield_reason": shield_state.reason,
                }
            )
            recorder.log_failure(
                category="human_collision",
                step=step,
                time_s=time_s,
                details={
                    "scenario": trial.scenario,
                    "condition": condition,
                    "position": position,
                    "velocity": velocity,
                    "true_human_position": true_human_position,
                    "measured_human_position": measured_human_position,
                    "camera_age_s": camera_age_s,
                    "shield_reason": shield_state.reason,
                },
            )
            human_collision_audited = True

        recorder.log_step(
            scenario=trial.scenario,
            episode=trial.episode,
            step=step,
            time_s=time_s,
            model_alive=int(model_alive),
            camera_alive=int(camera_alive),
            model_age_s=model_age_s,
            camera_age_s=camera_age_s,
            goal=trial.goal,
            policy_target=target,
            before_position=before_position,
            before_velocity=before_velocity,
            true_human_position=true_human_position,
            measured_human_position=measured_human_position,
            measured_human_velocity=measured_human_velocity,
            raw_policy_acceleration=raw_policy_acceleration,
            command_acceleration=command_acceleration,
            physical_acceleration=physical_acceleration,
            shield_latched=int(shield_state.latched),
            shield_reason=shield_state.reason,
            shield_response=shield_state.response,
            ask_human=int(shield_state.ask_human),
            stopping_distance=diagnostics["stopping_distance"],
            distance_to_joint_limit=diagnostics["distance_to_joint_limit"],
            measured_human_separation=diagnostics["measured_human_separation"],
            human_required_separation=diagnostics["human_required_separation"],
            after_position=position,
            after_velocity=velocity,
            hard_joint_violation=int(current_joint_violation),
            human_collision=int(current_human_collision),
            error=error,
        )

    safety_violation = joint_violation or human_collision
    completion = (
        abs(position - trial.goal) < float(trial_cfg["completion_position_tolerance"])
        and abs(velocity) < float(trial_cfg["completion_velocity_tolerance"])
        and not safety_violation
    )
    return {
        "scenario": trial.scenario,
        "episode": trial.episode,
        "success": int(completion),
        "safety_violation": int(safety_violation),
        "joint_violation": int(joint_violation),
        "human_collision": int(human_collision),
        "intervened": int(shield_state.latched),
        "intervention_reason": shield_state.reason,
        "intervention_response": shield_state.response,
        "ask_human": int(shield_state.ask_human),
        "intervention_time_s": (
            shield_state.intervention_time_s
            if shield_state.intervention_time_s is not None
            else ""
        ),
        "final_position": position,
        "final_velocity": velocity,
        "final_position_error": abs(position - trial.goal),
        "max_abs_position": max_abs_position,
        "min_human_separation": (
            min_human_separation if human_present else ""
        ),
        "integrated_squared_error": integrated_squared_error,
        "control_energy": control_energy,
    }


def average(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return sum(float(row[key]) for row in rows) / len(rows)


def optional_average(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row[key] != ""]
    return sum(values) / len(values) if values else None


def aggregate_scenario(
    *, condition: str, scenario: str, episode_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    rows = [row for row in episode_rows if row["scenario"] == scenario]
    return {
        "condition": condition,
        "scenario": scenario,
        "episodes": len(rows),
        "completion_rate": average(rows, "success"),
        "violation_rate": average(rows, "safety_violation"),
        "joint_violation_rate": average(rows, "joint_violation"),
        "human_collision_rate": average(rows, "human_collision"),
        "intervention_rate": average(rows, "intervened"),
        "ask_human_rate": average(rows, "ask_human"),
        "mean_intervention_time_s": optional_average(rows, "intervention_time_s"),
        "mean_final_position_error": average(rows, "final_position_error"),
        "mean_max_abs_position": average(rows, "max_abs_position"),
        "mean_min_human_separation": optional_average(rows, "min_human_separation"),
        "mean_integrated_squared_error": average(rows, "integrated_squared_error"),
        "mean_control_energy": average(rows, "control_energy"),
    }


def run_condition(
    *,
    condition: str,
    cfg: dict[str, Any],
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
    audit_rows: list[dict[str, Any]] = []
    episode_rows = [
        run_episode(
            condition=condition,
            trial=trial,
            cfg=cfg,
            recorder=recorder,
            audit_rows=audit_rows,
        )
        for trial in trials
    ]
    write_csv(recorder.run_dir / "episodes.csv", episode_rows)
    write_jsonl(recorder.run_dir / "audit_events.jsonl", audit_rows)

    scenario_rows = [
        aggregate_scenario(
            condition=condition,
            scenario=str(scenario),
            episode_rows=episode_rows,
        )
        for scenario in cfg["scenarios"]
    ]
    write_csv(recorder.run_dir / "scenario_metrics.csv", scenario_rows)
    scenario_map = {row["scenario"]: row for row in scenario_rows}
    fault_rows = [
        row for row in episode_rows if row["scenario"] != "normal"
    ]
    normal = scenario_map["normal"]
    summary = {
        "condition": condition,
        "episodes_per_scenario": int(cfg["episodes_per_scenario"]),
        "normal_completion_rate": normal["completion_rate"],
        "normal_false_intervention_rate": normal["intervention_rate"],
        "fault_violation_rate": average(fault_rows, "safety_violation"),
        "fault_intervention_rate": average(fault_rows, "intervened"),
        "model_timeout_violation_rate": scenario_map["model_timeout"]["violation_rate"],
        "stale_camera_violation_rate": scenario_map["stale_camera"]["violation_rate"],
        "unsafe_target_violation_rate": scenario_map["unsafe_joint_target"]["violation_rate"],
        "human_proximity_violation_rate": scenario_map["human_proximity"]["violation_rate"],
        "unsafe_target_ask_human_rate": scenario_map["unsafe_joint_target"]["ask_human_rate"],
        "audit_events": len(audit_rows),
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}, scenario_rows


def run_experiment(
    cfg: dict[str, Any], *, output_root: Path, command: list[str]
) -> list[dict[str, Any]]:
    trials = build_trials(cfg)
    condition_rows: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    for condition in cfg["conditions"]:
        summary, rows = run_condition(
            condition=str(condition),
            cfg=cfg,
            trials=trials,
            output_root=output_root,
            command=command,
        )
        condition_rows.append(summary)
        scenario_rows.extend(rows)

    write_csv(output_root / "condition_metrics.csv", condition_rows)
    write_csv(output_root / "scenario_metrics.csv", scenario_rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "shared_trial_schedule": True,
            "scenarios": [str(scenario) for scenario in cfg["scenarios"]],
            "conditions": [str(condition) for condition in cfg["conditions"]],
            "fault_time_s": float(cfg["fault_time_s"]),
            "safety_contract": {
                "joint_hard_limit": float(cfg["plant"]["joint_hard_limit"]),
                "human_hard_min_distance": float(
                    cfg["watchdog"]["human_hard_min_distance"]
                ),
                "max_model_age_s": float(cfg["watchdog"]["max_model_age_s"]),
                "max_camera_age_s": float(cfg["watchdog"]["max_camera_age_s"]),
                "max_brake_acceleration": float(
                    cfg["plant"]["max_brake_acceleration"]
                ),
            },
            "results": {
                "condition_metrics": "condition_metrics.csv",
                "scenario_metrics": "scenario_metrics.csv",
            },
        },
    )
    return condition_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use deterministic CI episode count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = copy.deepcopy(cfg)
        cfg["episodes_per_scenario"] = int(cfg["quick_episodes_per_scenario"])

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 40 complete: {len(rows)} safety-shield conditions")
    print(f"metrics: {output_root / 'condition_metrics.csv'}")
    for row in rows:
        print(
            f"{row['condition']:<26} normal-complete={row['normal_completion_rate']:.3f} "
            f"false-stop={row['normal_false_intervention_rate']:.3f} "
            f"fault-violation={row['fault_violation_rate']:.3f} "
            f"timeout={row['model_timeout_violation_rate']:.3f} "
            f"stale={row['stale_camera_violation_rate']:.3f} "
            f"human={row['human_proximity_violation_rate']:.3f}"
        )


if __name__ == "__main__":
    main()
