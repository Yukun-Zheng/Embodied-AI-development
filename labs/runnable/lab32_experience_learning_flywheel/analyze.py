#!/usr/bin/env python3
"""Analyze Lab 32 experience-learning flywheel outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "no_update",
    "targeted_failure_mining",
    "random_new_data",
    "success_only_data",
    "shuffled_corrections",
    "targeted_reset_no_replay",
}
MATCHED_UPDATE = EXPECTED - {"no_update"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze(condition_metrics: Path, round_metrics: Path) -> dict[str, Any]:
    rows = read_csv(condition_metrics)
    by_condition = {row["condition"]: row for row in rows}
    if set(by_condition) != EXPECTED:
        raise AssertionError(
            f"Expected conditions {sorted(EXPECTED)}, got {sorted(by_condition)}"
        )

    round_rows = read_csv(round_metrics)
    rounds: dict[str, list[dict[str, str]]] = {name: [] for name in EXPECTED}
    for row in round_rows:
        rounds[row["condition"]].append(row)
    for values in rounds.values():
        values.sort(key=lambda row: int(row["round"]))

    no_update = by_condition["no_update"]
    targeted = by_condition["targeted_failure_mining"]
    random_data = by_condition["random_new_data"]
    success_only = by_condition["success_only_data"]
    shuffled = by_condition["shuffled_corrections"]
    reset = by_condition["targeted_reset_no_replay"]

    matched_budget = int(float(targeted["matched_update_budget"]))
    relations = {
        "base_policy_is_partial_on_new_and_perfect_on_old": (
            abs(f(targeted, "base_new_success") - (4.0 / 12.0)) < 1e-12
            and abs(f(targeted, "base_old_success") - 1.0) < 1e-12
        ),
        "matched_update_conditions_receive_equal_new_data_budget": all(
            int(float(by_condition[name]["new_examples_added"])) == matched_budget == 8
            for name in MATCHED_UPDATE
        ),
        "no_update_baseline_stays_flat": (
            abs(f(no_update, "final_new_success") - f(no_update, "base_new_success"))
            < 1e-12
            and int(float(no_update["new_examples_added"])) == 0
        ),
        "targeted_failure_mining_solves_all_new_contexts": (
            abs(f(targeted, "final_new_success") - 1.0) < 1e-12
            and abs(f(targeted, "selection_precision") - 1.0) < 1e-12
            and int(float(targeted["unique_corrected_contexts"])) == 8
        ),
        "targeted_mining_beats_equal_volume_random_data": (
            f(targeted, "final_new_success") - f(random_data, "final_new_success")
            > 0.30
            and f(targeted, "learning_curve_auc") - f(random_data, "learning_curve_auc")
            > 0.12
            and f(targeted, "gain_per_new_example")
            > f(random_data, "gain_per_new_example") * 1.8
        ),
        "success_only_experience_does_not_repair_unseen_failures": (
            abs(f(success_only, "new_success_gain")) < 1e-12
            and abs(f(success_only, "selection_precision")) < 1e-12
        ),
        "correct_correction_semantics_are_causal": (
            f(targeted, "final_new_success") - f(shuffled, "final_new_success") > 0.60
            and abs(f(shuffled, "selection_precision") - 1.0) < 1e-12
            and abs(f(shuffled, "new_success_gain")) < 1e-12
        ),
        "targeted_update_preserves_old_task": (
            abs(f(targeted, "final_old_success") - 1.0) < 1e-12
            and abs(f(targeted, "old_task_regression")) < 1e-12
        ),
        "reset_without_retention_regresses_old_task": (
            abs(f(reset, "final_new_success") - f(targeted, "final_new_success")) < 1e-12
            and f(reset, "final_old_success") < 0.01
            and f(reset, "old_task_regression") > 0.99
        ),
        "targeted_learning_is_monotonic_across_rounds": all(
            float(after["new_success_after"]) >= float(before["new_success_after"])
            for before, after in zip(
                rounds["targeted_failure_mining"],
                rounds["targeted_failure_mining"][1:],
            )
        ),
        "random_data_spends_budget_on_nonfailures": (
            f(random_data, "selection_precision") < 0.75
            and f(random_data, "selection_precision") > 0.25
        ),
    }

    return {
        "pass": all(relations.values()),
        "relations": relations,
        "conditions": {
            condition: {
                key: float(value)
                for key, value in row.items()
                if key != "condition" and value != ""
            }
            for condition, row in by_condition.items()
        },
    }


def write_report(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Lab 32 Analysis",
        "",
        f"Overall pass: **{result['pass']}**",
        "",
        "## Mechanism assertions",
        "",
    ]
    for name, passed in result["relations"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} — `{name}`")
    lines.extend(
        [
            "",
            "The main matched-data comparison holds the new experience budget fixed at eight records. `targeted_failure_mining` versus `random_new_data` isolates state-selection value; `targeted_failure_mining` versus `shuffled_corrections` isolates label semantics; `targeted_reset_no_replay` isolates retention of old competence.",
            "",
        ]
    )
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition_metrics", type=Path)
    parser.add_argument("round_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.condition_metrics, args.round_metrics)
    write_report(result, args.output_dir)
    if not result["pass"]:
        failed = [name for name, value in result["relations"].items() if not value]
        raise SystemExit(f"Lab 32 analysis failed: {failed}")

    metrics = result["conditions"]
    print("PASS: Lab 32 experience-learning flywheel relations")
    print(
        "final new success targeted/random/success-only/shuffled/reset/no-update = "
        f"{metrics['targeted_failure_mining']['final_new_success']:.3f}/"
        f"{metrics['random_new_data']['final_new_success']:.3f}/"
        f"{metrics['success_only_data']['final_new_success']:.3f}/"
        f"{metrics['shuffled_corrections']['final_new_success']:.3f}/"
        f"{metrics['targeted_reset_no_replay']['final_new_success']:.3f}/"
        f"{metrics['no_update']['final_new_success']:.3f}"
    )
    print(
        "old success targeted/reset = "
        f"{metrics['targeted_failure_mining']['final_old_success']:.3f}/"
        f"{metrics['targeted_reset_no_replay']['final_old_success']:.3f}"
    )


if __name__ == "__main__":
    main()
