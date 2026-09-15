#!/usr/bin/env python3
"""Derive mechanism-level conclusions from runnable Lab 13 outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def value(row: dict[str, str], key: str) -> float:
    x = float(row[key])
    if not math.isfinite(x):
        raise ValueError(f"Non-finite {key} in {row}")
    return x


def analyze(metrics_path: Path) -> dict[str, Any]:
    rows = read_rows(metrics_path)
    keyed = {row["policy"]: row for row in rows}
    expected = {
        "fixed_center",
        "random_view",
        "info_gain",
        "info_gain_shuffled_geometry",
    }
    if set(keyed) != expected:
        raise ValueError(f"Unexpected policies: {sorted(keyed)}")

    fixed = keyed["fixed_center"]
    random = keyed["random_view"]
    active = keyed["info_gain"]
    shuffled = keyed["info_gain_shuffled_geometry"]

    information_gain_reduces_uncertainty = (
        value(active, "mean_final_entropy") < 0.75 * value(random, "mean_final_entropy")
        and value(active, "mean_final_entropy") < 0.50 * value(fixed, "mean_final_entropy")
    )
    active_sensing_improves_task_success = (
        value(active, "accuracy") > value(random, "accuracy") + 0.05
        and value(active, "accuracy") > value(fixed, "accuracy") + 0.20
    )
    active_sensing_is_motion_efficient = (
        value(active, "mean_movement_distance") < 0.60 * value(random, "mean_movement_distance")
        and value(active, "mean_task_utility") > value(random, "mean_task_utility") + 0.10
    )
    correct_view_geometry_is_causal = (
        value(active, "accuracy") > value(shuffled, "accuracy") + 0.10
        and value(shuffled, "mean_final_entropy") > 2.0 * value(active, "mean_final_entropy")
    )

    analysis = {
        "information_gain_reduces_uncertainty": information_gain_reduces_uncertainty,
        "active_sensing_improves_task_success": active_sensing_improves_task_success,
        "active_sensing_is_motion_efficient": active_sensing_is_motion_efficient,
        "correct_view_geometry_is_causal": correct_view_geometry_is_causal,
        "policies": [
            {
                "policy": row["policy"],
                "accuracy": value(row, "accuracy"),
                "mean_final_entropy": value(row, "mean_final_entropy"),
                "mean_movement_distance": value(row, "mean_movement_distance"),
                "mean_task_utility": value(row, "mean_task_utility"),
                "mean_unique_views": value(row, "mean_unique_views"),
            }
            for row in rows
        ],
    }
    return analysis


def render_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# Lab 13 Derived Analysis",
        "",
        "| Policy | accuracy | final entropy | sensing movement | task utility | unique views |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["policies"]:
        lines.append(
            f"| `{row['policy']}` | {row['accuracy']:.3f} | {row['mean_final_entropy']:.4f} | "
            f"{row['mean_movement_distance']:.3f} | {row['mean_task_utility']:.3f} | "
            f"{row['mean_unique_views']:.2f} |"
        )
    lines.extend(
        [
            "",
            f"- Information-gain selection reduces uncertainty: **{analysis['information_gain_reduces_uncertainty']}**",
            f"- Active sensing improves final task success: **{analysis['active_sensing_improves_task_success']}**",
            f"- Active sensing is more motion-efficient than random view changes: **{analysis['active_sensing_is_motion_efficient']}**",
            f"- Correct view geometry is causally required: **{analysis['correct_view_geometry_is_causal']}**",
            "",
            "## Interpretation",
            "",
            "The mechanism claim is stronger than ‘more views help’. The agent must choose views whose expected observation model is informative for the current belief, and must do so while paying physical motion cost. Shuffling the geometry used only for view selection attacks that mechanism while leaving the Bayesian update itself intact.",
            "",
            "A reduction in entropy is still not sufficient by itself: the experiment also requires improved final target inference and reports the sensing motion needed to obtain it.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path, help="Path to policy_metrics.csv")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or args.metrics.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = analyze(args.metrics)
    json_path = output_dir / "analysis.json"
    md_path = output_dir / "ANALYSIS.md"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(analysis, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    md_path.write_text(render_markdown(analysis), encoding="utf-8")
    print(f"analysis: {json_path}")
    print(f"report:   {md_path}")
    print(f"uncertainty mechanism verified: {analysis['information_gain_reduces_uncertainty']}")
    print(f"task success improves: {analysis['active_sensing_improves_task_success']}")
    print(f"correct view geometry required: {analysis['correct_view_geometry_is_causal']}")


if __name__ == "__main__":
    main()
