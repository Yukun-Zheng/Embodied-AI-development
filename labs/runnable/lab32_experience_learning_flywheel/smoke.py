#!/usr/bin/env python3
"""Deterministic smoke test for Lab 32 experience-learning flywheel."""

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
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab32-") as tmp:
        output = Path(tmp) / "lab32"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "condition_metrics.csv"),
                str(output / "round_metrics.csv"),
                "--output-dir",
                str(output),
            ],
            check=True,
        )

        required = [
            "condition_metrics.csv",
            "round_metrics.csv",
            "selection_events.csv",
            "experiment_summary.json",
            "analysis.json",
            "ANALYSIS.md",
        ]
        for name in required:
            path = output / name
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty Lab 32 artifact: {path}")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 6:
            raise AssertionError(f"Expected six condition run directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing raw run artifact: {run_dir / name}")

        metrics = read_metrics(output / "condition_metrics.csv")
        expected = {
            "no_update",
            "targeted_failure_mining",
            "random_new_data",
            "success_only_data",
            "shuffled_corrections",
            "targeted_reset_no_replay",
        }
        if set(metrics) != expected:
            raise AssertionError(f"Unexpected Lab 32 conditions: {sorted(metrics)}")

        targeted = metrics["targeted_failure_mining"]
        random_data = metrics["random_new_data"]
        success_only = metrics["success_only_data"]
        shuffled = metrics["shuffled_corrections"]
        reset = metrics["targeted_reset_no_replay"]
        no_update = metrics["no_update"]

        if not close(targeted["base_new_success"], 1.0 / 3.0):
            raise AssertionError("Base new-task competence changed from 4/12")
        if not close(targeted["base_old_success"], 1.0):
            raise AssertionError("Base old-task competence is no longer perfect")

        for condition in expected - {"no_update"}:
            if int(float(metrics[condition]["new_examples_added"])) != 8:
                raise AssertionError(f"Matched data budget broke for {condition}")

        if not close(targeted["final_new_success"], 1.0):
            raise AssertionError("Targeted failure mining no longer solves all new contexts")
        if not close(targeted["selection_precision"], 1.0):
            raise AssertionError("Failure-mining selection precision is no longer 1.0")
        if int(float(targeted["unique_corrected_contexts"])) != 8:
            raise AssertionError("Targeted mining no longer corrects all eight missing contexts")

        if not close(random_data["final_new_success"], 2.0 / 3.0):
            raise AssertionError("Seeded random-data reference changed")
        if not close(random_data["selection_precision"], 0.5):
            raise AssertionError("Random-data condition no longer spends half its budget on failures")
        if float(targeted["learning_curve_auc"]) <= float(random_data["learning_curve_auc"]):
            raise AssertionError("Targeted failure mining no longer improves sample efficiency")

        if not close(success_only["final_new_success"], 1.0 / 3.0):
            raise AssertionError("Success-only data unexpectedly repaired unseen failures")
        if not close(shuffled["final_new_success"], 1.0 / 3.0):
            raise AssertionError("Shuffled corrective labels unexpectedly repaired failures")
        if not close(shuffled["selection_precision"], 1.0):
            raise AssertionError("Shuffled-label control stopped mining actual failures")

        if not close(reset["final_new_success"], 1.0):
            raise AssertionError("Reset/no-replay condition should learn the new task")
        if not close(reset["final_old_success"], 0.0):
            raise AssertionError("Reset/no-replay condition no longer exposes old-task regression")
        if not close(targeted["final_old_success"], 1.0):
            raise AssertionError("Targeted incremental update should preserve old-task competence")
        if not close(no_update["final_new_success"], 1.0 / 3.0):
            raise AssertionError("No-update baseline drifted")

        analysis = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
        if not analysis.get("pass") or not all(analysis["relations"].values()):
            failed = [
                name for name, passed in analysis.get("relations", {}).items() if not passed
            ]
            raise AssertionError(f"Independent Lab 32 analyzer failed: {failed}")

        print(
            "Lab 32 smoke reference: "
            f"new targeted/random/success-only/shuffled/reset/no-update="
            f"{float(targeted['final_new_success']):.3f}/"
            f"{float(random_data['final_new_success']):.3f}/"
            f"{float(success_only['final_new_success']):.3f}/"
            f"{float(shuffled['final_new_success']):.3f}/"
            f"{float(reset['final_new_success']):.3f}/"
            f"{float(no_update['final_new_success']):.3f}; "
            f"old targeted/reset={float(targeted['final_old_success']):.3f}/"
            f"{float(reset['final_old_success']):.3f}"
        )
        print("PASS: Lab 32 raw artifacts + independent experience-learning analysis")


if __name__ == "__main__":
    main()
