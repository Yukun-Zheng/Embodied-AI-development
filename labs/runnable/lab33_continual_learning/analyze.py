#!/usr/bin/env python3
"""Derive mechanism-level conclusions from runnable Lab 33 outputs.

The analyzer intentionally does not declare a universal winner. Under a fixed
3D→2D shared representation bottleneck it asks whether methods move the
stability–plasticity trade-off in the way their mechanisms predict.
"""

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
    keyed = {row["method"]: row for row in rows}
    expected = {
        "naive_finetune",
        "replay",
        "quadratic_anchor",
        "replay_shuffled_labels",
    }
    if set(keyed) != expected:
        raise ValueError(f"Unexpected continual-learning methods: {sorted(keyed)}")

    naive = keyed["naive_finetune"]
    replay = keyed["replay"]
    anchor = keyed["quadratic_anchor"]
    shuffled = keyed["replay_shuffled_labels"]

    naive_forgets_under_bottleneck = value(naive, "average_old_task_forgetting") > 0.10
    correct_replay_reduces_forgetting = (
        value(replay, "average_old_task_forgetting")
        < 0.35 * value(naive, "average_old_task_forgetting")
    )
    replay_has_plasticity_cost_under_fixed_capacity = (
        value(replay, "mean_current_task_plasticity")
        < value(naive, "mean_current_task_plasticity") - 0.05
    )
    anchor_trades_plasticity_for_stability = (
        value(anchor, "average_old_task_forgetting")
        < 0.50 * value(naive, "average_old_task_forgetting")
        and value(anchor, "mean_current_task_plasticity")
        < value(naive, "mean_current_task_plasticity") - 0.05
    )
    replay_content_is_causal = (
        value(shuffled, "average_old_task_forgetting")
        > value(replay, "average_old_task_forgetting") + 0.15
        and value(shuffled, "final_average_accuracy")
        < value(replay, "final_average_accuracy") - 0.05
    )
    fixed_capacity_no_parameter_growth = all(int(float(row["parameter_growth"])) == 0 for row in rows)
    memory_cost_is_explicit = (
        int(float(naive["extra_method_memory_bytes"])) == 0
        and int(float(replay["extra_method_memory_bytes"])) > 0
        and int(float(anchor["extra_method_memory_bytes"])) > 0
        and int(float(shuffled["extra_method_memory_bytes"])) > 0
    )

    return {
        "naive_forgets_under_bottleneck": naive_forgets_under_bottleneck,
        "correct_replay_reduces_forgetting": correct_replay_reduces_forgetting,
        "replay_has_plasticity_cost_under_fixed_capacity": replay_has_plasticity_cost_under_fixed_capacity,
        "anchor_trades_plasticity_for_stability": anchor_trades_plasticity_for_stability,
        "replay_content_is_causal": replay_content_is_causal,
        "fixed_capacity_no_parameter_growth": fixed_capacity_no_parameter_growth,
        "memory_cost_is_explicit": memory_cost_is_explicit,
        "methods": [
            {
                "method": row["method"],
                "final_average_accuracy": value(row, "final_average_accuracy"),
                "average_old_task_forgetting": value(row, "average_old_task_forgetting"),
                "backward_transfer": value(row, "backward_transfer"),
                "forward_transfer_probe": value(row, "forward_transfer_probe"),
                "mean_current_task_plasticity": value(row, "mean_current_task_plasticity"),
                "final_task_A_accuracy": value(row, "final_task_A_accuracy"),
                "final_task_B_accuracy": value(row, "final_task_B_accuracy"),
                "final_task_C_accuracy": value(row, "final_task_C_accuracy"),
                "extra_method_memory_bytes": int(float(row["extra_method_memory_bytes"])),
                "parameter_growth": int(float(row["parameter_growth"])),
                "final_trunk_drift_from_initial": value(row, "final_trunk_drift_from_initial"),
            }
            for row in rows
        ],
    }


def render_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# Lab 33 Derived Analysis",
        "",
        "| Method | final avg | forgetting | plasticity | BWT | FWT probe | extra memory | parameter growth |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["methods"]:
        lines.append(
            f"| `{row['method']}` | {row['final_average_accuracy']:.3f} | "
            f"{row['average_old_task_forgetting']:.3f} | "
            f"{row['mean_current_task_plasticity']:.3f} | "
            f"{row['backward_transfer']:+.3f} | {row['forward_transfer_probe']:+.3f} | "
            f"{row['extra_method_memory_bytes']} B | {row['parameter_growth']} |"
        )
    lines.extend(
        [
            "",
            f"- Naive sequential learning forgets under the bottleneck: **{analysis['naive_forgets_under_bottleneck']}**",
            f"- Correct replay reduces forgetting: **{analysis['correct_replay_reduces_forgetting']}**",
            f"- Replay pays a plasticity cost under fixed capacity: **{analysis['replay_has_plasticity_cost_under_fixed_capacity']}**",
            f"- Quadratic anchoring trades plasticity for stability: **{analysis['anchor_trades_plasticity_for_stability']}**",
            f"- Replay content, not replay compute alone, is causal: **{analysis['replay_content_is_causal']}**",
            f"- Parameter capacity stays fixed: **{analysis['fixed_capacity_no_parameter_growth']}**",
            f"- Extra memory cost is explicitly accounted for: **{analysis['memory_cost_is_explicit']}**",
            "",
            "## Interpretation",
            "",
            "The experiment is deliberately capacity constrained: three independent task directions must share a two-dimensional trunk. Therefore retention and plasticity compete for the same representation rather than being hidden by unconstrained parameter growth.",
            "",
            "Correct replay should be read as a stability mechanism, not as a promise of a higher final average score in every setting. Under fixed capacity it can preserve old directions while reducing how completely the newest direction is represented. Quadratic anchoring makes the same trade-off through an explicit drift penalty rather than stored examples.",
            "",
            "The shuffled-label replay control is essential. It uses replay memory and replay optimizer work, but corrupts the information stored in memory. If it fails while correct replay retains old tasks, the causal variable is the preserved old-task information rather than simply doing more updates.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path, help="Path to method_metrics.csv")
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
    for key in [
        "naive_forgets_under_bottleneck",
        "correct_replay_reduces_forgetting",
        "replay_has_plasticity_cost_under_fixed_capacity",
        "anchor_trades_plasticity_for_stability",
        "replay_content_is_causal",
        "fixed_capacity_no_parameter_growth",
        "memory_cost_is_explicit",
    ]:
        print(f"{key}: {analysis[key]}")


if __name__ == "__main__":
    main()
