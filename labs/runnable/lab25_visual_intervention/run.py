#!/usr/bin/env python3
"""Lab 25 — causal visual intervention test for a VLA-like action head.

All policies receive the same compact visual representation and fixed
instruction. On the observational/base distribution, target appearance and an
irrelevant distractor are perfectly correlated with target geometry, so every
policy can look competent. Paired interventions then break one factor at a time:
target position, texture, background, camera yaw, distractor position, or the
target-geometry token itself.

The central counterexample is that a geometry probe can decode target position
from the representation even when the action head ignores that geometry and
acts through a spurious appearance shortcut.
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

LAB_ID = "lab25_visual_intervention"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass(frozen=True)
class Episode:
    episode: int
    bin_index: int
    jitter: float
    target_world: float
    texture_id: int
    background_id: int
    distractor_world: float
    target_delta: float
    camera_yaw: float
    distractor_delta: float


def project_x(world_x: float, yaw: float) -> float:
    """Normalized pinhole coordinate for a point (x, z=1) under camera yaw."""
    c = math.cos(yaw)
    s = math.sin(yaw)
    denominator = s * world_x + c
    if abs(denominator) < 1e-9:
        raise ZeroDivisionError("Projected point is on the camera plane")
    return (c * world_x - s) / denominator


def deproject_x(pixel_u: float, yaw: float) -> float:
    """Invert project_x for z=1."""
    c = math.cos(yaw)
    s = math.sin(yaw)
    denominator = c - pixel_u * s
    if abs(denominator) < 1e-9:
        raise ZeroDivisionError("Cannot deproject point")
    return (s + pixel_u * c) / denominator


def build_episodes(cfg: dict[str, Any]) -> list[Episode]:
    centers = [float(value) for value in cfg["target_bin_centers"]]
    rng = random.Random(int(cfg["seed"]))
    episodes: list[Episode] = []
    for index in range(int(cfg["episodes"])):
        bin_index = index % len(centers)
        jitter = rng.uniform(
            -float(cfg["target_jitter_abs"]), float(cfg["target_jitter_abs"])
        )
        target = centers[bin_index] + jitter
        sign = 1.0 if index % 2 == 0 else -1.0
        episodes.append(
            Episode(
                episode=index,
                bin_index=bin_index,
                jitter=jitter,
                target_world=target,
                texture_id=bin_index,
                background_id=bin_index,
                distractor_world=target + float(cfg["distractor_offset"]),
                target_delta=sign * float(cfg["target_position_delta"]),
                camera_yaw=sign * float(cfg["camera_yaw_rad"]),
                distractor_delta=sign * float(cfg["distractor_intervention_delta"]),
            )
        )
    return episodes


def observation(
    episode: Episode,
    intervention: str,
    cfg: dict[str, Any],
) -> dict[str, Any]:
    centers = [float(value) for value in cfg["target_bin_centers"]]
    count = len(centers)

    true_target = episode.target_world
    geometry_source = true_target
    texture_id = episode.texture_id
    background_id = episode.background_id
    distractor_world = episode.distractor_world
    yaw = 0.0

    if intervention == "base":
        pass
    elif intervention == "target_position":
        true_target = episode.target_world + episode.target_delta
        geometry_source = true_target
    elif intervention == "texture_swap":
        texture_id = (
            episode.texture_id + int(cfg["appearance_swap_bins"])
        ) % count
    elif intervention == "background_swap":
        background_id = (
            episode.background_id + int(cfg["appearance_swap_bins"])
        ) % count
    elif intervention == "camera_angle":
        yaw = episode.camera_yaw
    elif intervention == "distractor_move":
        distractor_world += episode.distractor_delta
    elif intervention == "geometry_shuffle":
        donor_bin = (
            episode.bin_index + int(cfg["geometry_shuffle_bins"])
        ) % count
        geometry_source = centers[donor_bin] + episode.jitter
    else:
        raise ValueError(f"Unknown intervention: {intervention}")

    return {
        "instruction": str(cfg["instruction"]),
        "true_target_world": true_target,
        "target_pixel_u": project_x(geometry_source, yaw),
        "camera_yaw": yaw,
        "texture_id": texture_id,
        "background_id": background_id,
        "distractor_pixel_u": project_x(distractor_world, yaw),
        "distractor_world": distractor_world,
        "geometry_source_world": geometry_source,
    }


def action_from_policy(policy: str, obs: dict[str, Any], cfg: dict[str, Any]) -> float:
    centers = [float(value) for value in cfg["target_bin_centers"]]

    if policy == "geometry_causal":
        return deproject_x(float(obs["target_pixel_u"]), float(obs["camera_yaw"]))

    if policy == "appearance_shortcut":
        return 0.5 * (
            centers[int(obs["texture_id"])] + centers[int(obs["background_id"])]
        )

    if policy == "camera_unaware":
        # Correct only when the camera remains at the canonical yaw=0 pose.
        return float(obs["target_pixel_u"])

    if policy == "distractor_shortcut":
        distractor = deproject_x(
            float(obs["distractor_pixel_u"]), float(obs["camera_yaw"])
        )
        return distractor - float(cfg["distractor_offset"])

    raise ValueError(f"Unknown policy: {policy}")


def rmse(values: list[float]) -> float:
    return math.sqrt(statistics.fmean(value * value for value in values))


def aggregate_intervention(
    policy: str,
    intervention: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    gains = [
        float(row["signed_response_gain"])
        for row in rows
        if row["signed_response_gain"] != ""
    ]
    return {
        "policy": policy,
        "intervention": intervention,
        "episodes": len(rows),
        "success_rate": statistics.fmean(float(row["success"]) for row in rows),
        "mean_abs_action_error": statistics.fmean(
            float(row["abs_action_error"]) for row in rows
        ),
        "mean_abs_action_change": statistics.fmean(
            float(row["abs_action_change"]) for row in rows
        ),
        "mean_signed_response_gain": statistics.fmean(gains) if gains else "",
    }


def run_experiment(
    cfg: dict[str, Any], output: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    output.mkdir(parents=True, exist_ok=True)
    episodes = build_episodes(cfg)
    policies = [str(value) for value in cfg["policies"]]
    interventions = [str(value) for value in cfg["interventions"]]
    tolerance = float(cfg["success_tolerance"])

    write_csv(
        output / "episode_specs.csv",
        [
            {
                "episode": episode.episode,
                "bin_index": episode.bin_index,
                "jitter": episode.jitter,
                "target_world": episode.target_world,
                "texture_id": episode.texture_id,
                "background_id": episode.background_id,
                "distractor_world": episode.distractor_world,
                "target_delta": episode.target_delta,
                "camera_yaw": episode.camera_yaw,
                "distractor_delta": episode.distractor_delta,
            }
            for episode in episodes
        ],
    )

    all_rows: list[dict[str, Any]] = []
    intervention_rows: list[dict[str, Any]] = []
    policy_rows: list[dict[str, Any]] = []

    for policy in policies:
        recorder = RunRecorder(
            output_root=output / "runs",
            lab_id=LAB_ID,
            condition=policy,
            seed=int(cfg["seed"]),
            config=cfg,
            repo_root=REPO_ROOT,
        )

        base_actions = {
            episode.episode: action_from_policy(
                policy, observation(episode, "base", cfg), cfg
            )
            for episode in episodes
        }
        base_probe_errors = []
        for episode in episodes:
            base_obs = observation(episode, "base", cfg)
            decoded = deproject_x(
                float(base_obs["target_pixel_u"]), float(base_obs["camera_yaw"])
            )
            base_probe_errors.append(decoded - episode.target_world)

        policy_intervention_rows: list[dict[str, Any]] = []
        step_index = 0
        for intervention in interventions:
            episode_rows: list[dict[str, Any]] = []
            for episode in episodes:
                obs = observation(episode, intervention, cfg)
                action = action_from_policy(policy, obs, cfg)
                base_action = base_actions[episode.episode]
                true_target = float(obs["true_target_world"])
                action_error = action - true_target
                success = abs(action_error) <= tolerance

                signed_gain: float | str = ""
                expected_action_delta = 0.0
                if intervention == "target_position":
                    expected_action_delta = episode.target_delta
                    signed_gain = (action - base_action) / episode.target_delta

                row = {
                    "policy": policy,
                    "intervention": intervention,
                    "episode": episode.episode,
                    "true_target_world": true_target,
                    "action": action,
                    "base_action": base_action,
                    "action_change": action - base_action,
                    "abs_action_change": abs(action - base_action),
                    "expected_action_delta": expected_action_delta,
                    "signed_response_gain": signed_gain,
                    "action_error": action_error,
                    "abs_action_error": abs(action_error),
                    "success": int(success),
                    "target_pixel_u": obs["target_pixel_u"],
                    "camera_yaw": obs["camera_yaw"],
                    "texture_id": obs["texture_id"],
                    "background_id": obs["background_id"],
                    "distractor_pixel_u": obs["distractor_pixel_u"],
                    "geometry_source_world": obs["geometry_source_world"],
                }
                episode_rows.append(row)
                all_rows.append(row)

                recorder.log_step(step=step_index, time_s=float(step_index), **row)
                if not success:
                    recorder.log_failure(
                        category="visual_intervention_action_failure",
                        step=step_index,
                        time_s=float(step_index),
                        details={
                            "episode": episode.episode,
                            "policy": policy,
                            "intervention": intervention,
                            "true_target_world": true_target,
                            "action": action,
                            "abs_action_error": abs(action_error),
                        },
                    )
                step_index += 1

            aggregate = aggregate_intervention(policy, intervention, episode_rows)
            intervention_rows.append(aggregate)
            policy_intervention_rows.append(aggregate)

        by_intervention = {
            str(row["intervention"]): row for row in policy_intervention_rows
        }
        policy_summary = {
            "policy": policy,
            "geometry_probe_rmse": rmse(base_probe_errors),
            "base_success_rate": float(by_intervention["base"]["success_rate"]),
            "target_position_success_rate": float(
                by_intervention["target_position"]["success_rate"]
            ),
            "target_position_response_gain": float(
                by_intervention["target_position"]["mean_signed_response_gain"]
            ),
            "texture_swap_success_rate": float(
                by_intervention["texture_swap"]["success_rate"]
            ),
            "texture_swap_action_change": float(
                by_intervention["texture_swap"]["mean_abs_action_change"]
            ),
            "background_swap_success_rate": float(
                by_intervention["background_swap"]["success_rate"]
            ),
            "background_swap_action_change": float(
                by_intervention["background_swap"]["mean_abs_action_change"]
            ),
            "camera_angle_success_rate": float(
                by_intervention["camera_angle"]["success_rate"]
            ),
            "camera_angle_action_change": float(
                by_intervention["camera_angle"]["mean_abs_action_change"]
            ),
            "distractor_move_success_rate": float(
                by_intervention["distractor_move"]["success_rate"]
            ),
            "distractor_move_action_change": float(
                by_intervention["distractor_move"]["mean_abs_action_change"]
            ),
            "geometry_shuffle_success_rate": float(
                by_intervention["geometry_shuffle"]["success_rate"]
            ),
            "geometry_shuffle_action_change": float(
                by_intervention["geometry_shuffle"]["mean_abs_action_change"]
            ),
        }
        policy_rows.append(policy_summary)
        recorder.finalize(policy_summary)

    write_csv(output / "episode_results.csv", all_rows)
    write_csv(output / "intervention_metrics.csv", intervention_rows)
    write_csv(output / "policy_metrics.csv", policy_rows)
    write_json(
        output / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "instruction": str(cfg["instruction"]),
            "episodes": int(cfg["episodes"]),
            "policies": policy_rows,
        },
    )
    return all_rows, intervention_rows, policy_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab25"))
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["episodes"] = min(int(cfg["episodes"]), 160)

    _, _, policy_rows = run_experiment(cfg, args.output)
    print("Lab 25 visual intervention experiment complete")
    for row in policy_rows:
        print(
            f"{row['policy']:22s} "
            f"base={row['base_success_rate']:.3f} "
            f"position={row['target_position_success_rate']:.3f} "
            f"pos-gain={row['target_position_response_gain']:.3f} "
            f"texture={row['texture_swap_success_rate']:.3f} "
            f"camera={row['camera_angle_success_rate']:.3f} "
            f"distractor={row['distractor_move_success_rate']:.3f} "
            f"geom-shuffle={row['geometry_shuffle_success_rate']:.3f} "
            f"probe-rmse={row['geometry_probe_rmse']:.2e}"
        )
    print(f"metrics: {args.output / 'policy_metrics.csv'}")


if __name__ == "__main__":
    main()
