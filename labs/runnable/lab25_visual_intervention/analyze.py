#!/usr/bin/env python3
"""Analyze whether visual information is causally used by Lab 25 policies."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "geometry_causal",
    "appearance_shortcut",
    "camera_unaware",
    "distractor_shortcut",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze(path: Path) -> dict[str, Any]:
    rows = read_csv(path)
    by_policy = {row["policy"]: row for row in rows}
    if set(by_policy) != EXPECTED:
        raise AssertionError(
            f"Expected policies {sorted(EXPECTED)}, got {sorted(by_policy)}"
        )

    causal = by_policy["geometry_causal"]
    appearance = by_policy["appearance_shortcut"]
    camera = by_policy["camera_unaware"]
    distractor = by_policy["distractor_shortcut"]

    relations = {
        "observational_base_cannot_distinguish_policies": all(
            f(row, "base_success_rate") > 0.99 for row in by_policy.values()
        ),
        "geometry_is_probe_decodable_for_every_policy": all(
            f(row, "geometry_probe_rmse") < 1e-12 for row in by_policy.values()
        ),
        "causal_policy_tracks_task_relevant_position": f(
            causal, "target_position_success_rate"
        )
        > 0.99
        and abs(f(causal, "target_position_response_gain") - 1.0) < 1e-12,
        "causal_policy_is_invariant_to_appearance_nuisance": f(
            causal, "texture_swap_success_rate"
        )
        > 0.99
        and f(causal, "background_swap_success_rate") > 0.99
        and f(causal, "texture_swap_action_change") < 1e-12
        and f(causal, "background_swap_action_change") < 1e-12,
        "causal_policy_handles_camera_change": f(
            causal, "camera_angle_success_rate"
        )
        > 0.99
        and f(causal, "camera_angle_action_change") < 1e-12,
        "causal_policy_ignores_distractor_motion": f(
            causal, "distractor_move_success_rate"
        )
        > 0.99
        and f(causal, "distractor_move_action_change") < 1e-12,
        "corrupting_target_geometry_breaks_causal_policy": f(
            causal, "geometry_shuffle_success_rate"
        )
        < 0.01
        and f(causal, "geometry_shuffle_action_change") > 0.80,
        "probe_information_does_not_imply_policy_use": f(
            appearance, "geometry_probe_rmse"
        )
        < 1e-12
        and f(appearance, "target_position_success_rate") < 0.01
        and abs(f(appearance, "target_position_response_gain")) < 1e-12
        and f(appearance, "geometry_shuffle_success_rate") > 0.99,
        "appearance_shortcut_is_exposed_by_texture_swap": f(
            appearance, "texture_swap_success_rate"
        )
        < 0.01
        and f(appearance, "texture_swap_action_change") > 0.15,
        "appearance_shortcut_is_exposed_by_background_swap": f(
            appearance, "background_swap_success_rate"
        )
        < 0.01
        and f(appearance, "background_swap_action_change") > 0.15,
        "camera_metadata_is_causally_required_for_camera_invariance": f(
            camera, "camera_angle_success_rate"
        )
        < 0.01
        and f(camera, "camera_angle_action_change") > 0.15
        and f(causal, "camera_angle_success_rate") > 0.99,
        "irrelevant_distractor_shortcut_is_causally_exposed": f(
            distractor, "distractor_move_success_rate"
        )
        < 0.01
        and f(distractor, "distractor_move_action_change") > 0.20
        and f(causal, "distractor_move_success_rate") > 0.99,
        "position_intervention_separates_geometry_from_shortcuts": f(
            appearance, "target_position_success_rate"
        )
        < 0.01
        and f(distractor, "target_position_success_rate") < 0.01
        and f(causal, "target_position_success_rate") > 0.99
        and f(camera, "target_position_success_rate") > 0.99,
    }

    return {
        "pass": all(relations.values()),
        "relations": relations,
        "policies": {
            policy: {
                key: float(value)
                for key, value in row.items()
                if key != "policy" and value != ""
            }
            for policy, row in by_policy.items()
        },
    }


def write_report(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# Lab 25 Analysis",
        "",
        f"Overall pass: **{result['pass']}**",
        "",
        "## Mechanism assertions",
        "",
    ]
    for name, passed in result["relations"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} — `{name}`")
    lines.extend(
        [
            "",
            "The central counterexample is `appearance_shortcut`: the shared representation still has essentially zero target-geometry probe error, yet the action does not move when target position changes and instead changes under texture/background interventions. Probe availability is therefore separated from causal policy use.",
            "",
        ]
    )
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.policy_metrics)
    write_report(result, args.output_dir)
    if not result["pass"]:
        failed = [name for name, value in result["relations"].items() if not value]
        raise SystemExit(f"Lab 25 analysis failed: {failed}")

    policies = result["policies"]
    print("PASS: Lab 25 visual intervention relations")
    print(
        "position success causal/appearance/camera/distractor = "
        f"{policies['geometry_causal']['target_position_success_rate']:.3f}/"
        f"{policies['appearance_shortcut']['target_position_success_rate']:.3f}/"
        f"{policies['camera_unaware']['target_position_success_rate']:.3f}/"
        f"{policies['distractor_shortcut']['target_position_success_rate']:.3f}"
    )
    print(
        "probe RMSE appearance shortcut = "
        f"{policies['appearance_shortcut']['geometry_probe_rmse']:.3e}"
    )


if __name__ == "__main__":
    main()
