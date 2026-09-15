#!/usr/bin/env python3
"""Deterministic CI mechanism checks for runnable Lab 40."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB_DIR = Path(__file__).resolve().parent
RUN = LAB_DIR / "run.py"
ANALYZE = LAB_DIR / "analyze.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    assert math.isfinite(value), f"{key} is not finite in {row}"
    return value


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab40-") as tmpdir:
        output = Path(tmpdir) / "lab40"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

        condition_path = output / "condition_metrics.csv"
        scenario_path = output / "scenario_metrics.csv"
        manifest_path = output / "experiment_manifest.json"
        for required in [condition_path, scenario_path, manifest_path]:
            assert required.is_file(), f"Lab 40 missing {required.name}"

        conditions = read_rows(condition_path)
        scenarios = read_rows(scenario_path)
        assert len(conditions) == 5
        assert len(scenarios) == 25
        keyed = {row["condition"]: row for row in conditions}
        assert set(keyed) == {
            "no_shield",
            "static_rules",
            "predictive_no_freshness",
            "predictive_shield",
            "overconservative_shield",
        }
        by_pair = {(row["condition"], row["scenario"]): row for row in scenarios}

        for row in conditions:
            for metric in [
                "normal_completion_rate",
                "normal_false_intervention_rate",
                "fault_violation_rate",
                "fault_intervention_rate",
                "model_timeout_violation_rate",
                "stale_camera_violation_rate",
                "unsafe_target_violation_rate",
                "human_proximity_violation_rate",
                "unsafe_target_ask_human_rate",
            ]:
                finite(row, metric)

            run_dir = output / row["run_dir"]
            for required in [
                "manifest.json",
                "steps.csv",
                "failures.jsonl",
                "summary.json",
                "episodes.csv",
                "scenario_metrics.csv",
                "audit_events.jsonl",
            ]:
                assert (run_dir / required).is_file(), (
                    f"Lab 40 missing {required} for {row['condition']}"
                )
            assert (run_dir / "steps.csv").stat().st_size > 0
            episode_rows = read_rows(run_dir / "episodes.csv")
            assert len(episode_rows) == 5 * 60

        def v(condition: str, scenario: str) -> float:
            return finite(by_pair[(condition, scenario)], "violation_rate")

        def intervention(condition: str, scenario: str) -> float:
            return finite(by_pair[(condition, scenario)], "intervention_rate")

        def ask(condition: str, scenario: str) -> float:
            return finite(by_pair[(condition, scenario)], "ask_human_rate")

        for scenario in [
            "model_timeout",
            "stale_camera",
            "unsafe_joint_target",
            "human_proximity",
        ]:
            assert v("no_shield", scenario) > 0.95

        assert v("static_rules", "unsafe_joint_target") < 0.05
        assert ask("static_rules", "unsafe_joint_target") > 0.95
        assert v("static_rules", "model_timeout") > 0.90
        assert v("static_rules", "stale_camera") > 0.90
        assert v("static_rules", "human_proximity") > 0.90

        assert v("predictive_no_freshness", "stale_camera") > 0.80
        assert v("predictive_no_freshness", "human_proximity") < 0.05

        for scenario in [
            "model_timeout",
            "stale_camera",
            "unsafe_joint_target",
            "human_proximity",
        ]:
            assert v("predictive_shield", scenario) < 0.05
            assert intervention("predictive_shield", scenario) > 0.95
        assert ask("predictive_shield", "unsafe_joint_target") > 0.95
        assert finite(keyed["predictive_shield"], "normal_completion_rate") > 0.95
        assert finite(keyed["predictive_shield"], "normal_false_intervention_rate") < 0.05

        assert finite(keyed["overconservative_shield"], "fault_violation_rate") < 0.05
        assert finite(keyed["overconservative_shield"], "normal_false_intervention_rate") > 0.20
        assert (
            finite(keyed["predictive_shield"], "normal_completion_rate")
            - finite(keyed["overconservative_shield"], "normal_completion_rate")
            > 0.20
        )

        predictive_run = output / keyed["predictive_shield"]["run_dir"]
        audit = read_jsonl(predictive_run / "audit_events.jsonl")
        interventions = [row for row in audit if row.get("event") == "intervention"]
        violations = [row for row in audit if row.get("event") == "safety_violation"]
        assert not violations, "Predictive shield audit contains a physical safety violation"
        reason_counts = Counter(str(row.get("reason")) for row in interventions)
        assert reason_counts["model_timeout"] == 60
        assert reason_counts["stale_camera"] == 60
        assert reason_counts["unsafe_joint_target"] == 60
        assert reason_counts["predictive_human_proximity"] == 60
        unsafe_events = [
            row
            for row in interventions
            if row.get("reason") == "unsafe_joint_target"
        ]
        assert all(row.get("response") == "reject_and_ask_human" for row in unsafe_events)
        assert all(row.get("ask_human") is True for row in unsafe_events)

        no_shield_run = output / keyed["no_shield"]["run_dir"]
        no_shield_audit = read_jsonl(no_shield_run / "audit_events.jsonl")
        assert any(
            row.get("event") == "safety_violation" for row in no_shield_audit
        ), "No-shield condition did not preserve violation audit evidence"

        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        assert manifest["shared_trial_schedule"] is True
        assert manifest["safety_contract"]["max_model_age_s"] > 0
        assert manifest["safety_contract"]["max_camera_age_s"] > 0
        assert manifest["safety_contract"]["max_brake_acceleration"] > 0

        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(condition_path),
                str(scenario_path),
                "--output-dir",
                str(output),
            ],
            cwd=ROOT,
            check=True,
        )
        analysis_path = output / "analysis.json"
        assert analysis_path.is_file()
        assert (output / "ANALYSIS.md").is_file()
        with analysis_path.open("r", encoding="utf-8") as handle:
            analysis = json.load(handle)
        for key in [
            "faults_are_physically_consequential_without_shield",
            "static_target_rejection_catches_obvious_unsafe_target",
            "static_rules_are_too_late_for_dynamic_hazards",
            "predictive_stopping_beats_reactive_human_rule",
            "freshness_check_is_causally_necessary_for_stale_camera",
            "model_watchdog_prevents_timeout_runaway",
            "predictive_shield_prevents_all_injected_fault_violations",
            "predictive_shield_intervenes_on_all_fault_classes",
            "unsafe_target_routes_to_human_review",
            "predictive_shield_preserves_normal_availability",
            "zero_violation_alone_is_not_a_valid_safety_solution",
            "safety_availability_tradeoff_is_explicit",
        ]:
            assert analysis[key] is True, f"Lab 40 mechanism assertion failed: {key}"

        print(
            "PASS lab40_safety_shield: timeout, stale-sensor, unsafe-target, "
            "predictive-stopping and safety/availability controls verified"
        )


if __name__ == "__main__":
    main()
