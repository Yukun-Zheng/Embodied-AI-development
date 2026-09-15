#!/usr/bin/env python3
"""Analyze Lab 37 shared-object bimanual coordination outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

EXPECTED = {
    "independent_world",
    "midpoint_only",
    "relative_coordinated",
    "wrong_relative_sign",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def analyze(path: Path) -> dict[str, Any]:
    rows = read_csv(path)
    by_condition = {row["condition"]: row for row in rows}
    if set(by_condition) != EXPECTED:
        raise AssertionError(
            f"Expected conditions {sorted(EXPECTED)}, got {sorted(by_condition)}"
        )

    independent = by_condition["independent_world"]
    midpoint = by_condition["midpoint_only"]
    coordinated = by_condition["relative_coordinated"]
    wrong = by_condition["wrong_relative_sign"]

    relations = {
        "coordinated_success_high": number(coordinated, "success_rate") > 0.90,
        "independent_shared_object_failures_visible": number(
            independent, "success_rate"
        ) < 0.70,
        "coordination_improves_success": number(coordinated, "success_rate")
        - number(independent, "success_rate")
        > 0.40,
        "relative_feedback_reduces_relative_rmse": number(
            coordinated, "mean_relative_rmse"
        )
        < 0.60 * number(independent, "mean_relative_rmse"),
        "relative_feedback_reduces_peak_strain": number(
            coordinated, "mean_peak_abs_strain"
        )
        < 0.65 * number(independent, "mean_peak_abs_strain"),
        "relative_feedback_reduces_internal_force": number(
            coordinated, "mean_p95_internal_force"
        )
        < 0.65 * number(independent, "mean_p95_internal_force"),
        "coordination_does_not_trade_away_center_tracking": number(
            coordinated, "mean_center_rmse"
        )
        < number(independent, "mean_center_rmse"),
        "midpoint_tracking_alone_is_insufficient": number(midpoint, "success_rate")
        < 0.15,
        "midpoint_counterexample_has_good_center_but_bad_relative_state": number(
            midpoint, "mean_center_rmse"
        )
        < number(independent, "mean_center_rmse")
        and number(midpoint, "mean_relative_rmse")
        > 1.40 * number(independent, "mean_relative_rmse"),
        "wrong_relative_sign_breaks_coordination": number(wrong, "success_rate")
        < 0.05
        and number(wrong, "mean_peak_abs_strain") > 0.50,
        "wrong_sign_explodes_internal_force": number(wrong, "mean_p95_internal_force")
        > 20.0 * number(coordinated, "mean_p95_internal_force"),
        "gain_is_not_from_large_effort_budget": number(
            coordinated, "mean_total_effort"
        )
        < 1.10 * number(independent, "mean_total_effort"),
    }

    return {
        "pass": all(relations.values()),
        "relations": relations,
        "metrics": {
            condition: {
                key: float(value)
                for key, value in row.items()
                if key not in {"condition"} and value != ""
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
        "# Lab 37 Analysis",
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
            "The central negative control is `midpoint_only`: center tracking can look good while relative separation and shared-object strain are unacceptable. This prevents the lab from defining bimanual success as midpoint motion alone.",
            "",
        ]
    )
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze(args.condition_metrics)
    write_report(result, args.output_dir)
    if not result["pass"]:
        failed = [name for name, value in result["relations"].items() if not value]
        raise SystemExit(f"Lab 37 analysis failed: {failed}")
    print("PASS: Lab 37 bimanual coordination relations")
    metrics = result["metrics"]
    print(
        "success independent/midpoint/coordinated/wrong = "
        f"{metrics['independent_world']['success_rate']:.3f}/"
        f"{metrics['midpoint_only']['success_rate']:.3f}/"
        f"{metrics['relative_coordinated']['success_rate']:.3f}/"
        f"{metrics['wrong_relative_sign']['success_rate']:.3f}"
    )
    print(
        "mean peak strain independent/coordinated = "
        f"{metrics['independent_world']['mean_peak_abs_strain']:.4f}/"
        f"{metrics['relative_coordinated']['mean_peak_abs_strain']:.4f}"
    )


if __name__ == "__main__":
    main()
