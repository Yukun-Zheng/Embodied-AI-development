#!/usr/bin/env python3
"""Analyze Lab 34 curriculum-selection mechanism outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "learning_progress",
    "uniform",
    "fixed_curriculum",
    "hardest_first",
    "shuffled_progress",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze(strategy_metrics: Path, selection_counts: Path) -> dict[str, Any]:
    rows = read_csv(strategy_metrics)
    by_strategy = {row["strategy"]: row for row in rows}
    if set(by_strategy) != EXPECTED:
        raise AssertionError(
            f"Expected strategies {sorted(EXPECTED)}, got {sorted(by_strategy)}"
        )

    selection = read_csv(selection_counts)
    counts: dict[str, dict[int, int]] = {name: {} for name in EXPECTED}
    for row in selection:
        counts[row["strategy"]][int(row["task"])] = int(row["practice_count"])

    progress = by_strategy["learning_progress"]
    uniform = by_strategy["uniform"]
    fixed = by_strategy["fixed_curriculum"]
    hardest = by_strategy["hardest_first"]
    shuffled = by_strategy["shuffled_progress"]

    relations = {
        "equal_total_practice_budget": all(
            int(float(row["practice_budget"])) == 180 for row in by_strategy.values()
        ),
        "uniform_and_fixed_match_task_counts": all(
            counts["uniform"].get(task, 0) == 20
            and counts["fixed_curriculum"].get(task, 0) == 20
            for task in range(9)
        ),
        "learning_progress_reaches_high_final_competence": f(
            progress, "final_average_success"
        )
        > 0.96,
        "learning_progress_beats_fixed_final_competence": f(
            progress, "final_average_success"
        )
        - f(fixed, "final_average_success")
        > 0.02,
        "learning_progress_beats_fixed_learning_curve_auc": f(
            progress, "learning_curve_auc"
        )
        - f(fixed, "learning_curve_auc")
        > 0.08,
        "fixed_order_matters_even_with_same_task_counts": f(
            fixed, "learning_curve_auc"
        )
        - f(uniform, "learning_curve_auc")
        > 0.15,
        "progress_scheduler_practices_learnable_frontier": f(
            progress, "mean_selected_learnability_after_warmup"
        )
        > 0.89
        and f(progress, "mean_frontier_distance_after_warmup") < 0.055,
        "progress_scheduler_reaches_hard_tasks": int(
            float(progress["mastered_task_count"])
        )
        >= 8
        and f(progress, "max_mastered_difficulty") >= 0.85,
        "uniform_budget_is_less_sample_efficient": f(uniform, "final_average_success")
        < 0.75
        and f(uniform, "learning_curve_auc") < 0.40,
        "hardest_first_is_not_a_curriculum": f(hardest, "final_average_success")
        < 0.10
        and f(hardest, "mean_selected_learnability_after_warmup") < 0.01,
        "correct_progress_task_binding_is_causal": f(
            progress, "final_average_success"
        )
        - f(shuffled, "final_average_success")
        > 0.85
        and f(shuffled, "final_average_success") < 0.10,
        "shuffled_progress_selects_wrong_frontier": f(
            shuffled, "mean_frontier_distance_after_warmup"
        )
        > 0.80
        and f(shuffled, "mean_selected_learnability_after_warmup") < 0.01,
        "adaptive_scheduler_changes_allocation": int(
            float(progress["unique_tasks_after_warmup"])
        )
        >= 7
        and max(counts["learning_progress"].values()) > 60,
    }

    return {
        "pass": all(relations.values()),
        "relations": relations,
        "strategies": {
            strategy: {
                key: float(value)
                for key, value in row.items()
                if key != "strategy" and value != ""
            }
            for strategy, row in by_strategy.items()
        },
        "practice_counts": counts,
    }


def write_report(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Lab 34 Analysis",
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
            "The strongest controls are `uniform` versus `fixed_curriculum` (identical per-task counts, different order) and `learning_progress` versus `shuffled_progress` (same progress magnitudes, wrong task identity). These separate allocation order and correct progress-to-task binding from total practice budget.",
            "",
        ]
    )
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("strategy_metrics", type=Path)
    parser.add_argument("selection_counts", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.strategy_metrics, args.selection_counts)
    write_report(result, args.output_dir)
    if not result["pass"]:
        failed = [name for name, value in result["relations"].items() if not value]
        raise SystemExit(f"Lab 34 analysis failed: {failed}")

    metrics = result["strategies"]
    print("PASS: Lab 34 self-generated curriculum relations")
    print(
        "final average progress/fixed/uniform/hardest/shuffled = "
        f"{metrics['learning_progress']['final_average_success']:.3f}/"
        f"{metrics['fixed_curriculum']['final_average_success']:.3f}/"
        f"{metrics['uniform']['final_average_success']:.3f}/"
        f"{metrics['hardest_first']['final_average_success']:.3f}/"
        f"{metrics['shuffled_progress']['final_average_success']:.3f}"
    )
    print(
        "learning curve AUC progress/fixed/uniform = "
        f"{metrics['learning_progress']['learning_curve_auc']:.3f}/"
        f"{metrics['fixed_curriculum']['learning_curve_auc']:.3f}/"
        f"{metrics['uniform']['learning_curve_auc']:.3f}"
    )


if __name__ == "__main__":
    main()
