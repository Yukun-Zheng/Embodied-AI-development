#!/usr/bin/env python3
"""Headless smoke test for the Lab 05 -> Lab 06 MuJoCo cross-layer experiment."""

from __future__ import annotations

import csv
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "lab05_06_model_based_control.py"


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["condition"]: row for row in csv.DictReader(handle)}


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-mujoco-cross-layer-") as tmp:
        output = Path(tmp) / "cross-layer"
        subprocess.run([sys.executable, str(RUN), "--output", str(output)], check=True)

        metrics_path = output / "condition_metrics.csv"
        if not metrics_path.is_file() or metrics_path.stat().st_size == 0:
            raise AssertionError("Missing cross-layer condition_metrics.csv")
        metrics = read_metrics(metrics_path)
        expected = {
            "computed_torque_matched",
            "computed_torque_wrong_mass",
            "computed_torque_omit_passive",
            "plain_pd",
        }
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected cross-layer conditions: {sorted(metrics)}")

        for condition, row in metrics.items():
            if int(float(row["finite"])) != 1:
                raise AssertionError(f"Non-finite cross-layer rollout in {condition}")
            for key in (
                "position_rmse",
                "velocity_rmse",
                "max_position_error_norm",
                "disturbance_end_error_norm",
                "late_mean_error_norm",
                "control_energy",
                "saturation_fraction",
            ):
                if not math.isfinite(f(row, key)):
                    raise AssertionError(f"Non-finite {key} in {condition}")

        matched = metrics["computed_torque_matched"]
        wrong_mass = metrics["computed_torque_wrong_mass"]
        omit_passive = metrics["computed_torque_omit_passive"]
        plain_pd = metrics["plain_pd"]

        if f(matched, "position_rmse") >= 0.05:
            raise AssertionError("Matched computed torque did not track the trajectory accurately")
        if f(matched, "late_mean_error_norm") >= 0.08:
            raise AssertionError("Matched computed torque did not recover after the shared disturbance")
        if f(matched, "saturation_fraction") >= 0.25:
            raise AssertionError("Reference trajectory spends too much time in actuator saturation")

        # Model mismatch should have a measurable physical consequence under the
        # same trajectory and disturbance. Which metric carries the effect is
        # allowed to differ, so compare both tracking and late recovery.
        if not (
            f(wrong_mass, "position_rmse") > 1.20 * f(matched, "position_rmse")
            or f(wrong_mass, "late_mean_error_norm")
            > 1.20 * f(matched, "late_mean_error_norm")
        ):
            raise AssertionError("Wrong-mass dynamics did not produce a measurable closed-loop penalty")

        if not (
            f(omit_passive, "position_rmse") > 1.05 * f(matched, "position_rmse")
            or f(omit_passive, "late_mean_error_norm")
            > 1.05 * f(matched, "late_mean_error_norm")
        ):
            raise AssertionError("Omitting passive dynamics did not produce a measurable closed-loop penalty")

        if not (
            f(plain_pd, "position_rmse") > 1.10 * f(matched, "position_rmse")
            or f(plain_pd, "late_mean_error_norm")
            > 1.10 * f(matched, "late_mean_error_norm")
        ):
            raise AssertionError("Plain PD is not separated from matched computed torque")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 4:
            raise AssertionError(f"Expected four cross-layer run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing cross-layer simulator artifact: {run_dir / name}")

        print(
            "MuJoCo Lab05->06 smoke: pos-rmse matched/wrong-mass/omit-passive/plain-PD="
            f"{f(matched, 'position_rmse'):.4f}/"
            f"{f(wrong_mass, 'position_rmse'):.4f}/"
            f"{f(omit_passive, 'position_rmse'):.4f}/"
            f"{f(plain_pd, 'position_rmse'):.4f}; "
            "late="
            f"{f(matched, 'late_mean_error_norm'):.4f}/"
            f"{f(wrong_mass, 'late_mean_error_norm'):.4f}/"
            f"{f(omit_passive, 'late_mean_error_norm'):.4f}/"
            f"{f(plain_pd, 'late_mean_error_norm'):.4f}"
        )
        print("PASS: MuJoCo dynamics-model mismatch -> closed-loop control consequence")


if __name__ == "__main__":
    main()
