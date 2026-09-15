#!/usr/bin/env python3
"""Deterministic smoke test for Lab 25 causal visual interventions."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "run.py"
ANALYZE = HERE / "analyze.py"


def read_policy_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["policy"]: row for row in csv.DictReader(handle)}


def close(value: str, expected: float, tol: float = 1e-12) -> bool:
    return math.isclose(float(value), expected, rel_tol=0.0, abs_tol=tol)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab25-") as tmp:
        output = Path(tmp) / "lab25"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "policy_metrics.csv"),
                "--output-dir",
                str(output),
            ],
            check=True,
        )

        required = [
            "episode_specs.csv",
            "episode_results.csv",
            "intervention_metrics.csv",
            "policy_metrics.csv",
            "experiment_summary.json",
            "analysis.json",
            "ANALYSIS.md",
        ]
        for name in required:
            path = output / name
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty Lab 25 artifact: {path}")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 4:
            raise AssertionError(f"Expected four policy run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing raw run artifact: {run_dir / name}")

        metrics = read_policy_metrics(output / "policy_metrics.csv")
        expected = {
            "geometry_causal",
            "appearance_shortcut",
            "camera_unaware",
            "distractor_shortcut",
        }
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected Lab 25 policies: {sorted(metrics)}")

        causal = metrics["geometry_causal"]
        appearance = metrics["appearance_shortcut"]
        camera = metrics["camera_unaware"]
        distractor = metrics["distractor_shortcut"]

        for policy, row in metrics.items():
            if not close(row["base_success_rate"], 1.0):
                raise AssertionError(f"Base benchmark no longer matched for {policy}")
            if float(row["geometry_probe_rmse"]) >= 1e-12:
                raise AssertionError(f"Target geometry no longer probe-decodable for {policy}")

        if not close(causal["target_position_success_rate"], 1.0) or not close(
            causal["target_position_response_gain"], 1.0
        ):
            raise AssertionError("Causal geometry policy stopped tracking physical target motion")
        if not close(causal["texture_swap_success_rate"], 1.0) or not close(
            causal["background_swap_success_rate"], 1.0
        ):
            raise AssertionError("Causal policy became appearance-sensitive")
        if not close(causal["camera_angle_success_rate"], 1.0) or not close(
            causal["distractor_move_success_rate"], 1.0
        ):
            raise AssertionError("Causal policy lost nuisance invariance")
        if not close(causal["geometry_shuffle_success_rate"], 0.0):
            raise AssertionError("Geometry shuffle no longer breaks the causal policy")
        if float(causal["geometry_shuffle_action_change"]) <= 0.80:
            raise AssertionError("Geometry corruption no longer changes the causal action")

        if not close(appearance["target_position_success_rate"], 0.0) or not close(
            appearance["target_position_response_gain"], 0.0
        ):
            raise AssertionError("Appearance shortcut unexpectedly tracks target geometry")
        if not close(appearance["texture_swap_success_rate"], 0.0) or not close(
            appearance["background_swap_success_rate"], 0.0
        ):
            raise AssertionError("Appearance interventions no longer expose the shortcut")
        if float(appearance["texture_swap_action_change"]) <= 0.15 or float(
            appearance["background_swap_action_change"]
        ) <= 0.15:
            raise AssertionError("Appearance interventions no longer move shortcut actions")
        if not close(appearance["geometry_shuffle_success_rate"], 1.0):
            raise AssertionError("Appearance shortcut became dependent on target geometry")

        if not close(camera["camera_angle_success_rate"], 0.0) or float(
            camera["camera_angle_action_change"]
        ) <= 0.15:
            raise AssertionError("Camera-pose intervention no longer exposes frame misuse")
        if not close(camera["target_position_success_rate"], 1.0):
            raise AssertionError("Camera-unaware policy should still track position at canonical camera")

        if not close(distractor["target_position_success_rate"], 0.0):
            raise AssertionError("Distractor shortcut unexpectedly follows target motion")
        if not close(distractor["distractor_move_success_rate"], 0.0) or float(
            distractor["distractor_move_action_change"]
        ) <= 0.20:
            raise AssertionError("Distractor intervention no longer exposes the shortcut")
        if not close(distractor["geometry_shuffle_success_rate"], 1.0):
            raise AssertionError("Distractor shortcut became dependent on target geometry")

        analysis = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
        if not analysis.get("pass") or not all(analysis["relations"].values()):
            raise AssertionError("Independent Lab 25 analyzer did not verify every relation")

        print(
            "Lab 25 smoke reference: "
            f"base=1.000 for all; position causal/appearance/camera/distractor="
            f"{float(causal['target_position_success_rate']):.3f}/"
            f"{float(appearance['target_position_success_rate']):.3f}/"
            f"{float(camera['target_position_success_rate']):.3f}/"
            f"{float(distractor['target_position_success_rate']):.3f}; "
            f"camera-unaware camera={float(camera['camera_angle_success_rate']):.3f}; "
            f"distractor-shortcut distractor={float(distractor['distractor_move_success_rate']):.3f}"
        )
        print("PASS: Lab 25 raw artifacts + independent visual-causality analysis")


if __name__ == "__main__":
    main()
