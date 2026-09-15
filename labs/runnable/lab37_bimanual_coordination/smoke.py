#!/usr/bin/env python3
"""Deterministic smoke test for Lab 37 bimanual coordination."""

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


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["condition"]: row for row in csv.DictReader(handle)}


def close(value: str, expected: float, tol: float = 1e-12) -> bool:
    return math.isclose(float(value), expected, rel_tol=0.0, abs_tol=tol)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab37-") as tmp:
        output = Path(tmp) / "lab37"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "condition_metrics.csv"),
                "--output-dir",
                str(output),
            ],
            check=True,
        )

        required = [
            "trial_specs.csv",
            "episode_metrics.csv",
            "condition_metrics.csv",
            "experiment_summary.json",
            "analysis.json",
            "ANALYSIS.md",
        ]
        for name in required:
            path = output / name
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty Lab 37 artifact: {path}")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 4:
            raise AssertionError(f"Expected four condition run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing raw run artifact: {run_dir / name}")

        metrics = read_metrics(output / "condition_metrics.csv")
        expected = {
            "independent_world",
            "midpoint_only",
            "relative_coordinated",
            "wrong_relative_sign",
        }
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected Lab 37 conditions: {sorted(metrics)}")

        # The quick reference uses 120 paired deterministic episodes.
        if not close(metrics["independent_world"]["success_rate"], 52 / 120):
            raise AssertionError("Independent-world quick reference drifted")
        if not close(metrics["midpoint_only"]["success_rate"], 5 / 120):
            raise AssertionError("Midpoint-only quick reference drifted")
        if not close(metrics["relative_coordinated"]["success_rate"], 115 / 120):
            raise AssertionError("Relative-coordinated quick reference drifted")
        if not close(metrics["wrong_relative_sign"]["success_rate"], 0.0):
            raise AssertionError("Wrong-sign negative control unexpectedly succeeded")

        independent = metrics["independent_world"]
        midpoint = metrics["midpoint_only"]
        coordinated = metrics["relative_coordinated"]
        wrong = metrics["wrong_relative_sign"]

        if float(coordinated["mean_peak_abs_strain"]) >= 0.65 * float(
            independent["mean_peak_abs_strain"]
        ):
            raise AssertionError("Explicit relative feedback did not reduce shared-object strain")
        if float(coordinated["mean_p95_internal_force"]) >= 0.65 * float(
            independent["mean_p95_internal_force"]
        ):
            raise AssertionError("Explicit relative feedback did not reduce internal force")
        if float(midpoint["mean_center_rmse"]) >= float(independent["mean_center_rmse"]):
            raise AssertionError("Midpoint-only counterexample no longer has good center tracking")
        if float(midpoint["mean_relative_rmse"]) <= 1.40 * float(
            independent["mean_relative_rmse"]
        ):
            raise AssertionError("Midpoint-only counterexample no longer loses relative state")
        if float(wrong["mean_p95_internal_force"]) <= 20.0 * float(
            coordinated["mean_p95_internal_force"]
        ):
            raise AssertionError("Wrong relative sign no longer produces the intended force failure")
        if float(coordinated["mean_total_effort"]) >= 1.10 * float(
            independent["mean_total_effort"]
        ):
            raise AssertionError("Coordination gain is confounded by a much larger effort budget")

        analysis = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
        if not analysis.get("pass") or not all(analysis["relations"].values()):
            raise AssertionError("Independent Lab 37 analyzer did not verify every relation")

        print(
            "Lab 37 smoke reference: "
            f"independent={float(independent['success_rate']):.6f}, "
            f"midpoint={float(midpoint['success_rate']):.6f}, "
            f"coordinated={float(coordinated['success_rate']):.6f}, "
            f"wrong={float(wrong['success_rate']):.6f}"
        )
        print("PASS: Lab 37 raw artifacts + independent bimanual coordination analysis")


if __name__ == "__main__":
    main()
