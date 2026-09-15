#!/usr/bin/env python3
"""Headless MuJoCo smoke test for Lab 05 rigid-body dynamics."""

from __future__ import annotations

import csv
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "lab05_dynamics.py"


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["variant"]: row for row in csv.DictReader(handle)}


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-mujoco-lab05-") as tmp:
        output = Path(tmp) / "lab05"
        subprocess.run(
            [sys.executable, str(RUN), "--output", str(output)],
            check=True,
        )

        metrics_path = output / "model_metrics.csv"
        rows_path = output / "probe_rows.csv"
        summary_path = output / "experiment_summary.json"
        for path in (metrics_path, rows_path, summary_path):
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty MuJoCo Lab 05 artifact: {path}")

        metrics = read_metrics(metrics_path)
        expected = {"matched", "wrong_mass_scale", "omit_passive"}
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected dynamics variants: {sorted(metrics)}")

        matched = metrics["matched"]
        wrong_mass = metrics["wrong_mass_scale"]
        no_passive = metrics["omit_passive"]
        for row in metrics.values():
            if int(float(row["finite"])) != 1:
                raise AssertionError("Non-finite MuJoCo dynamics prediction")
            for key in (
                "rmse",
                "relative_rmse",
                "max_abs_error",
                "truth_rms",
                "mean_dynamics_residual",
                "max_mass_matrix_symmetry_error",
                "min_mass_matrix_eigenvalue",
            ):
                if not math.isfinite(f(row, key)):
                    raise AssertionError(f"Non-finite Lab 05 metric: {key}")

        if f(matched, "rmse") >= 1e-8:
            raise AssertionError("MuJoCo mass/bias/passive reconstruction does not match qacc")
        if f(matched, "mean_dynamics_residual") >= 1e-8:
            raise AssertionError("Rigid-body dynamics identity residual is too large")
        if f(matched, "max_mass_matrix_symmetry_error") >= 1e-10:
            raise AssertionError("MuJoCo mass matrix is unexpectedly asymmetric")
        if f(matched, "min_mass_matrix_eigenvalue") <= 1e-5:
            raise AssertionError("MuJoCo mass matrix lost positive definiteness")

        if f(wrong_mass, "relative_rmse") <= 0.20:
            raise AssertionError("Wrong-mass model did not produce a material acceleration error")
        if f(wrong_mass, "rmse") <= 1000.0 * max(f(matched, "rmse"), 1e-12):
            raise AssertionError("Wrong-mass and matched dynamics are not clearly separated")
        if f(no_passive, "relative_rmse") <= 0.01:
            raise AssertionError("Omitting joint passive forces did not change dynamics enough")
        if f(no_passive, "rmse") <= 100.0 * max(f(matched, "rmse"), 1e-12):
            raise AssertionError("Passive-force ablation is not separated from the matched model")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 1:
            raise AssertionError(f"Expected one Lab 05 run directory, got {len(run_dirs)}")
        for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
            if not (run_dirs[0] / name).is_file():
                raise AssertionError(f"Missing Lab 05 simulator artifact: {name}")

        print(
            "MuJoCo Lab 05 smoke: "
            f"relative RMSE matched/wrong-mass/no-passive="
            f"{f(matched, 'relative_rmse'):.3e}/"
            f"{f(wrong_mass, 'relative_rmse'):.3f}/"
            f"{f(no_passive, 'relative_rmse'):.3f}; "
            f"lambda_min={f(matched, 'min_mass_matrix_eigenvalue'):.6f}"
        )
        print("PASS: MuJoCo Lab 05 dynamics identity + model-mismatch controls")


if __name__ == "__main__":
    main()
