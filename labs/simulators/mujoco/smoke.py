#!/usr/bin/env python3
"""Headless physics smoke test for the MuJoCo Lab 06 adapter."""

from __future__ import annotations

import csv
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "lab06_control.py"


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["condition"]: row for row in csv.DictReader(handle)}


def metric(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-mujoco-lab06-") as tmp:
        output = Path(tmp) / "lab06"
        subprocess.run(
            [sys.executable, str(RUN), "--output", str(output)],
            check=True,
        )

        metrics_path = output / "condition_metrics.csv"
        if not metrics_path.is_file():
            raise AssertionError("MuJoCo Lab 06 did not emit condition_metrics.csv")
        metrics = read_metrics(metrics_path)
        expected = {"no_feedback", "pd_feedback", "wrong_sign_feedback"}
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected MuJoCo conditions: {sorted(metrics)}")

        for condition, row in metrics.items():
            if int(float(row["finite"])) != 1:
                raise AssertionError(f"Non-finite MuJoCo rollout in {condition}")
            for key in (
                "final_error",
                "late_mean_error",
                "control_energy",
                "saturation_fraction",
                "peak_abs_position",
            ):
                if not math.isfinite(metric(row, key)):
                    raise AssertionError(f"Non-finite {key} in {condition}")

        no_feedback = metrics["no_feedback"]
        pd = metrics["pd_feedback"]
        wrong = metrics["wrong_sign_feedback"]

        if metric(pd, "final_error") >= 0.08:
            raise AssertionError("PD feedback did not settle near the target")
        if metric(pd, "late_mean_error") >= 0.12:
            raise AssertionError("PD feedback did not recover after disturbance")
        if metric(pd, "final_error") >= 0.25 * metric(no_feedback, "final_error"):
            raise AssertionError("Feedback did not decisively outperform no-feedback control")
        if metric(pd, "final_error") >= 0.10 * metric(wrong, "final_error"):
            raise AssertionError("Correct feedback sign did not separate from wrong-sign control")
        if metric(wrong, "saturation_fraction") <= metric(pd, "saturation_fraction") + 0.20:
            raise AssertionError("Wrong-sign controller did not produce the expected saturation pathology")
        if metric(wrong, "peak_abs_position") < 1.5:
            raise AssertionError("Wrong-sign controller did not drive the slider toward the joint boundary")
        if metric(pd, "disturbance_end_error") <= metric(pd, "final_error"):
            raise AssertionError("Disturbance/recovery relation is not visible in the PD trajectory")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 3:
            raise AssertionError(f"Expected three MuJoCo run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing simulator artifact: {run_dir / name}")

        print(
            "MuJoCo Lab 06 smoke: "
            f"final error no/pd/wrong="
            f"{metric(no_feedback, 'final_error'):.4f}/"
            f"{metric(pd, 'final_error'):.4f}/"
            f"{metric(wrong, 'final_error'):.4f}; "
            f"PD disturbance-end/final="
            f"{metric(pd, 'disturbance_end_error'):.4f}/"
            f"{metric(pd, 'final_error'):.4f}"
        )
        print("PASS: MuJoCo Lab 06 physics adapter + feedback mechanism")


if __name__ == "__main__":
    main()
