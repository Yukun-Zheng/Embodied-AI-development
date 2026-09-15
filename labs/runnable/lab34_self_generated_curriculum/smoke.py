#!/usr/bin/env python3
"""Deterministic smoke test for Lab 34 self-generated curriculum."""

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
        return {row["strategy"]: row for row in csv.DictReader(handle)}


def finite_row(row: dict[str, str]) -> bool:
    for key, value in row.items():
        if key == "strategy" or value == "":
            continue
        if not math.isfinite(float(value)):
            return False
    return True


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab34-") as tmp:
        output = Path(tmp) / "lab34"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "strategy_metrics.csv"),
                str(output / "selection_counts.csv"),
                "--output-dir",
                str(output),
            ],
            check=True,
        )

        required = [
            "strategy_metrics.csv",
            "selection_counts.csv",
            "experiment_summary.json",
            "analysis.json",
            "ANALYSIS.md",
        ]
        for name in required:
            path = output / name
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty Lab 34 artifact: {path}")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 5:
            raise AssertionError(f"Expected five strategy run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing raw run artifact: {run_dir / name}")

        metrics = read_metrics(output / "strategy_metrics.csv")
        expected = {
            "learning_progress",
            "uniform",
            "fixed_curriculum",
            "hardest_first",
            "shuffled_progress",
        }
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected Lab 34 strategies: {sorted(metrics)}")
        if not all(finite_row(row) for row in metrics.values()):
            raise AssertionError("Lab 34 produced non-finite strategy metrics")
        if not all(int(float(row["practice_budget"])) == 180 for row in metrics.values()):
            raise AssertionError("Curriculum strategies no longer share the same practice budget")

        analysis = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
        if not analysis.get("pass") or not all(analysis["relations"].values()):
            failed = [
                name for name, passed in analysis.get("relations", {}).items() if not passed
            ]
            raise AssertionError(f"Independent Lab 34 analyzer failed: {failed}")

        progress = metrics["learning_progress"]
        uniform = metrics["uniform"]
        fixed = metrics["fixed_curriculum"]
        hardest = metrics["hardest_first"]
        shuffled = metrics["shuffled_progress"]

        if float(progress["learning_curve_auc"]) <= float(fixed["learning_curve_auc"]):
            raise AssertionError("Learning-progress scheduler no longer improves learning-curve AUC")
        if float(fixed["learning_curve_auc"]) <= float(uniform["learning_curve_auc"]):
            raise AssertionError("Fixed easy-to-hard order no longer beats equal-count uniform order")
        if float(progress["final_average_success"]) <= float(fixed["final_average_success"]):
            raise AssertionError("Learning progress no longer improves final competence over fixed curriculum")
        if float(hardest["final_average_success"]) >= float(uniform["final_average_success"]):
            raise AssertionError("Hardest-first unexpectedly stopped being a poor curriculum control")
        if float(shuffled["final_average_success"]) >= float(uniform["final_average_success"]):
            raise AssertionError("Shuffled progress-to-task binding no longer degrades learning")

        print(
            "Lab 34 smoke reference: "
            f"final progress/fixed/uniform/hardest/shuffled="
            f"{float(progress['final_average_success']):.3f}/"
            f"{float(fixed['final_average_success']):.3f}/"
            f"{float(uniform['final_average_success']):.3f}/"
            f"{float(hardest['final_average_success']):.3f}/"
            f"{float(shuffled['final_average_success']):.3f}; "
            f"AUC progress/fixed/uniform="
            f"{float(progress['learning_curve_auc']):.3f}/"
            f"{float(fixed['learning_curve_auc']):.3f}/"
            f"{float(uniform['learning_curve_auc']):.3f}"
        )
        print("PASS: Lab 34 raw artifacts + independent curriculum analysis")


if __name__ == "__main__":
    main()
