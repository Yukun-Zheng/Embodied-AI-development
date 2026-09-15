#!/usr/bin/env python3
"""Deterministic CI mechanism checks for runnable Lab 31."""

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


def optional_float(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key, "")
    if raw in {"", "None", "null"}:
        return None
    value = float(raw)
    assert math.isfinite(value), f"{key} is not finite in {row}"
    return value


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab31-") as tmpdir:
        output = Path(tmpdir) / "lab31"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

        metrics_path = output / "condition_metrics.csv"
        manifest_path = output / "experiment_manifest.json"
        assert metrics_path.is_file(), "Lab 31 did not write condition_metrics.csv"
        assert manifest_path.is_file(), "Lab 31 did not write experiment_manifest.json"

        rows = read_rows(metrics_path)
        assert len(rows) == 5, f"Expected 5 reasoning controls, got {len(rows)}"
        keyed = {row["condition"]: row for row in rows}
        assert set(keyed) == {
            "correct_plan",
            "no_plan",
            "random_plan",
            "fluent_wrong_plan",
            "shuffled_binding",
        }

        for row in rows:
            for metric in [
                "success_rate",
                "locked_success_rate",
                "unlocked_success_rate",
                "mean_action_validity",
                "mean_invalid_actions",
                "mean_violations",
                "mean_steps",
                "mean_final_progress",
                "mean_max_progress",
                "mean_optimal_plan_length",
            ]:
                finite(row, metric)

            run_dir = output / row["run_dir"]
            for required in [
                "manifest.json",
                "steps.csv",
                "failures.jsonl",
                "summary.json",
                "episodes.csv",
                "plans.jsonl",
            ]:
                assert (run_dir / required).is_file(), f"Lab 31 missing {required} for {row['condition']}"

            episode_rows = read_rows(run_dir / "episodes.csv")
            assert len(episode_rows) == 300, f"Expected 300 quick episodes for {row['condition']}"
            assert all("required_key" in episode_row for episode_row in episode_rows)
            assert all("target_package" in episode_row for episode_row in episode_rows)
            assert all("target_bin" in episode_row for episode_row in episode_rows)

        correct = keyed["correct_plan"]
        no_plan = keyed["no_plan"]
        random_plan = keyed["random_plan"]
        wrong = keyed["fluent_wrong_plan"]
        binding = keyed["shuffled_binding"]

        assert finite(correct, "success_rate") > 0.99
        assert finite(correct, "locked_success_rate") > 0.99
        assert finite(correct, "mean_action_validity") > 0.99

        # Planning must matter specifically when the latent prerequisite exists.
        assert finite(no_plan, "locked_success_rate") < 0.05
        assert finite(no_plan, "unlocked_success_rate") > 0.95

        wrong_self_model = optional_float(wrong, "self_model_success_rate")
        correct_self_model = optional_float(correct, "self_model_success_rate")
        assert wrong_self_model is not None and wrong_self_model > 0.99
        assert correct_self_model is not None and correct_self_model > 0.99
        assert finite(wrong, "locked_success_rate") < 0.05
        assert finite(wrong, "unlocked_success_rate") > 0.95

        # The coherent wrong plan must look substantially more executable than a
        # random permutation while still being causally wrong in the true world.
        assert finite(wrong, "mean_action_validity") > finite(random_plan, "mean_action_validity") + 0.25
        assert finite(random_plan, "success_rate") < 0.10
        assert finite(binding, "success_rate") < 0.10

        plan_lengths = []
        for name in ["correct_plan", "random_plan", "fluent_wrong_plan", "shuffled_binding"]:
            value = optional_float(keyed[name], "mean_plan_length")
            assert value is not None
            plan_lengths.append(value)
        assert max(plan_lengths) - min(plan_lengths) < 1e-9, "Plan-based controls do not match output budget"

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
            "correct_plan_success_is_high",
            "locked_dependency_requires_reasoning",
            "easy_unlocked_cases_do_not_require_reasoning",
            "correct_reasoning_has_causal_gain",
            "fluent_wrong_is_internally_coherent",
            "fluent_wrong_fails_in_reality",
            "fluent_wrong_is_not_random_garbage",
            "random_order_control_fails",
            "binding_control_fails",
            "matched_plan_budget",
            "correct_binding_and_order_are_jointly_necessary",
        ]:
            assert analysis[key] is True, f"Lab 31 mechanism assertion failed: {key}"

        print(
            "PASS lab31_reasoning_negative_control: causal plan, no-plan, random-order, "
            "fluent-wrong-model and binding controls verified"
        )


if __name__ == "__main__":
    main()
