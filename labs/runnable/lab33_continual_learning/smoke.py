#!/usr/bin/env python3
"""Deterministic CI mechanism checks for runnable Lab 33."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB_DIR = Path(__file__).resolve().parent
RUN = LAB_DIR / "run.py"
ANALYZE = LAB_DIR / "analyze.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    assert math.isfinite(value), f"{key} is not finite in {row}"
    return value


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab33-") as tmpdir:
        output = Path(tmpdir) / "lab33"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

        metrics_path = output / "method_metrics.csv"
        manifest_path = output / "experiment_manifest.json"
        assert metrics_path.is_file(), "Lab 33 did not write method_metrics.csv"
        assert manifest_path.is_file(), "Lab 33 did not write experiment_manifest.json"

        rows = read_rows(metrics_path)
        assert len(rows) == 4, f"Expected 4 continual-learning methods, got {len(rows)}"
        keyed = {row["method"]: row for row in rows}
        assert set(keyed) == {
            "naive_finetune",
            "replay",
            "quadratic_anchor",
            "replay_shuffled_labels",
        }

        for row in rows:
            for metric in [
                "final_average_accuracy",
                "average_old_task_forgetting",
                "backward_transfer",
                "forward_transfer_probe",
                "mean_current_task_plasticity",
                "final_task_A_accuracy",
                "final_task_B_accuracy",
                "final_task_C_accuracy",
                "final_trunk_drift_from_initial",
            ]:
                finite(row, metric)
            assert int(float(row["parameter_growth"])) == 0

            run_dir = output / row["run_dir"]
            for required in [
                "manifest.json",
                "steps.csv",
                "failures.jsonl",
                "summary.json",
                "performance_matrix.csv",
                "probe_matrix.csv",
            ]:
                assert (run_dir / required).is_file(), f"Lab 33 missing {required} for {row['method']}"

            performance_rows = read_rows(run_dir / "performance_matrix.csv")
            probe_rows = read_rows(run_dir / "probe_matrix.csv")
            assert len(performance_rows) == 4, "Expected initial + three learned phases"
            assert len(probe_rows) == 4, "Expected initial + three probe phases"

        naive = keyed["naive_finetune"]
        replay = keyed["replay"]
        anchor = keyed["quadratic_anchor"]
        shuffled = keyed["replay_shuffled_labels"]

        naive_forgetting = finite(naive, "average_old_task_forgetting")
        replay_forgetting = finite(replay, "average_old_task_forgetting")
        anchor_forgetting = finite(anchor, "average_old_task_forgetting")
        shuffled_forgetting = finite(shuffled, "average_old_task_forgetting")
        naive_plasticity = finite(naive, "mean_current_task_plasticity")
        replay_plasticity = finite(replay, "mean_current_task_plasticity")
        anchor_plasticity = finite(anchor, "mean_current_task_plasticity")

        # A valid diagnostic must first exhibit forgetting under naive sequential learning.
        assert naive_forgetting > 0.10

        # Correct replay should strongly improve stability, while finite shared
        # capacity makes that stability visibly compete with current-task plasticity.
        assert replay_forgetting < 0.35 * naive_forgetting
        assert replay_plasticity < naive_plasticity - 0.05

        # Parameter anchoring should show the same stability/plasticity tension
        # through a different mechanism.
        assert anchor_forgetting < 0.50 * naive_forgetting
        assert anchor_plasticity < naive_plasticity - 0.05

        # Same replay memory/update structure with corrupted old labels must fail,
        # proving replay information—not merely extra optimizer work—is causal.
        assert shuffled_forgetting > replay_forgetting + 0.15
        assert finite(shuffled, "final_average_accuracy") < finite(replay, "final_average_accuracy") - 0.05

        assert int(float(naive["extra_method_memory_bytes"])) == 0
        assert int(float(replay["extra_method_memory_bytes"])) > 0
        assert int(float(anchor["extra_method_memory_bytes"])) > 0
        assert int(float(shuffled["extra_method_memory_bytes"])) > 0

        subprocess.run(
            [sys.executable, str(ANALYZE), str(metrics_path), "--output-dir", str(output)],
            cwd=ROOT,
            check=True,
        )
        analysis_json = output / "analysis.json"
        analysis_md = output / "ANALYSIS.md"
        assert analysis_json.is_file()
        assert analysis_md.is_file()
        with analysis_json.open("r", encoding="utf-8") as handle:
            analysis = json.load(handle)
        for key in [
            "naive_forgets_under_bottleneck",
            "correct_replay_reduces_forgetting",
            "replay_has_plasticity_cost_under_fixed_capacity",
            "anchor_trades_plasticity_for_stability",
            "replay_content_is_causal",
            "fixed_capacity_no_parameter_growth",
            "memory_cost_is_explicit",
        ]:
            assert analysis[key] is True, f"Lab 33 mechanism assertion failed: {key}"

        print("PASS lab33_continual_learning: fixed-capacity stability/plasticity, replay and negative control verified")


if __name__ == "__main__":
    main()
