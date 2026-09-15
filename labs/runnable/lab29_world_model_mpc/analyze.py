#!/usr/bin/env python3
"""Derive falsifiable conclusions from Lab 29 output artifacts.

The analyzer keeps three statements separate:
1) observational prediction quality;
2) counterfactual/intervention correctness;
3) closed-loop planning utility and horizon-dependent bias amplification.

It writes machine-readable `analysis.json` plus a human-readable `ANALYSIS.md`.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key} in {row}")
    return value


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def analyze(output_dir: Path) -> dict[str, Any]:
    base_path = output_dir / "model_metrics.csv"
    horizon_path = output_dir / "horizon_sweep.csv"
    if not base_path.is_file():
        raise FileNotFoundError(base_path)
    if not horizon_path.is_file():
        raise FileNotFoundError(horizon_path)

    base_rows = read_csv(base_path)
    horizon_rows = read_csv(horizon_path)
    base = {row["model"]: row for row in base_rows}
    expected = {"action_aware", "action_blind", "wrong_action_sign"}
    if set(base) != expected:
        raise ValueError(f"Unexpected base models: {sorted(base)}")
    if len(horizon_rows) < 3:
        raise ValueError("Need at least three planning horizons for a horizon analysis")

    aware = base["action_aware"]
    blind = base["action_blind"]
    wrong = base["wrong_action_sign"]

    observational_prediction_is_insufficient = (
        finite(blind, "one_step_rmse") < 0.005
        and finite(blind, "final_position_error") > 0.8
        and finite(blind, "counterfactual_sensitivity_error") > 0.10
    )
    counterfactual_direction_matters = (
        finite(wrong, "counterfactual_sensitivity_error")
        > 5.0 * finite(aware, "counterfactual_sensitivity_error")
        and finite(wrong, "final_position_error")
        > 20.0 * max(finite(aware, "final_position_error"), 1e-6)
    )

    horizon_rows = sorted(horizon_rows, key=lambda row: int(row["planning_horizon"]))
    first = horizon_rows[0]
    last = horizon_rows[-1]
    first_terminal = finite(first, "terminal_prediction_rmse")
    last_terminal = finite(last, "terminal_prediction_rmse")
    horizon_prediction_error_accumulates = last_terminal > 3.0 * max(first_terminal, 1e-9)

    costs = [(int(row["planning_horizon"]), finite(row, "realized_control_cost")) for row in horizon_rows]
    best_horizon, best_cost = min(costs, key=lambda pair: pair[1])
    last_cost = finite(last, "realized_control_cost")
    long_horizon_control_not_monotonic = last_cost > 1.15 * best_cost

    analysis = {
        "observational_prediction_is_insufficient": observational_prediction_is_insufficient,
        "counterfactual_direction_matters": counterfactual_direction_matters,
        "horizon_prediction_error_accumulates": horizon_prediction_error_accumulates,
        "long_horizon_control_not_monotonic": long_horizon_control_not_monotonic,
        "best_horizon_by_realized_cost": best_horizon,
        "best_realized_control_cost": best_cost,
        "max_horizon": int(last["planning_horizon"]),
        "max_horizon_realized_control_cost": last_cost,
        "min_horizon_terminal_prediction_rmse": first_terminal,
        "max_horizon_terminal_prediction_rmse": last_terminal,
        "terminal_prediction_error_ratio_max_over_min": last_terminal / max(first_terminal, 1e-12),
        "base_models": [
            {
                "model": row["model"],
                "one_step_rmse": finite(row, "one_step_rmse"),
                "counterfactual_sensitivity_error": finite(row, "counterfactual_sensitivity_error"),
                "final_position_error": finite(row, "final_position_error"),
                "realized_control_cost": finite(row, "realized_control_cost"),
            }
            for row in base_rows
        ],
        "horizon_probe": [
            {
                "planning_horizon": int(row["planning_horizon"]),
                "action_gain_scale": finite(row, "action_gain_scale"),
                "rollout_prediction_rmse": finite(row, "rollout_prediction_rmse"),
                "terminal_prediction_rmse": finite(row, "terminal_prediction_rmse"),
                "realized_control_cost": finite(row, "realized_control_cost"),
                "final_position_error": finite(row, "final_position_error"),
            }
            for row in horizon_rows
        ],
    }
    return analysis


def render_markdown(analysis: dict[str, Any]) -> str:
    base_lines = [
        "| Model | one-step RMSE | counterfactual error | final position error | realized control cost |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in analysis["base_models"]:
        base_lines.append(
            f"| `{row['model']}` | {row['one_step_rmse']:.5f} | "
            f"{row['counterfactual_sensitivity_error']:.4f} | "
            f"{row['final_position_error']:.4f} | {row['realized_control_cost']:.4f} |"
        )

    horizon_lines = [
        "| Horizon | action-gain scale | rollout RMSE | terminal RMSE | realized control cost | final error |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["horizon_probe"]:
        horizon_lines.append(
            f"| {row['planning_horizon']} | {row['action_gain_scale']:.2f} | "
            f"{row['rollout_prediction_rmse']:.4f} | {row['terminal_prediction_rmse']:.4f} | "
            f"{row['realized_control_cost']:.4f} | {row['final_position_error']:.4f} |"
        )

    return "\n".join(
        [
            "# Lab 29 Derived Analysis",
            "",
            "This report is generated from raw experiment CSVs. It separates passive prediction, intervention correctness and closed-loop planning utility.",
            "",
            "## Base falsification",
            "",
            *base_lines,
            "",
            f"- Observational prediction is insufficient: **{analysis['observational_prediction_is_insufficient']}**",
            f"- Correct counterfactual direction matters: **{analysis['counterfactual_direction_matters']}**",
            "",
            "## Planning-horizon × model-bias probe",
            "",
            *horizon_lines,
            "",
            f"- Horizon prediction error accumulates: **{analysis['horizon_prediction_error_accumulates']}**",
            f"- Long-horizon control is non-monotonic under the injected bias: **{analysis['long_horizon_control_not_monotonic']}**",
            f"- Best horizon by realized control cost: **{analysis['best_horizon_by_realized_cost']}**",
            f"- Terminal prediction-error ratio (max/min horizon): **{analysis['terminal_prediction_error_ratio_max_over_min']:.2f}×**",
            "",
            "## Interpretation",
            "",
            "A longer planning horizon is useful only when the imagined dynamics remain decision-relevant over that horizon. The bias probe changes only the learned action gain, so growth in rollout error is a controlled demonstration of compounding dynamics error rather than a change in task, optimizer or cost function.",
            "",
            "This does **not** imply that long-horizon MPC is generally worse. It establishes a falsifiable condition: when model error compounds faster than additional look-ahead helps, planning farther can increase realized closed-loop cost.",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="Directory containing Lab 29 CSV outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = analyze(args.output_dir)
    json_path = args.output_dir / "analysis.json"
    md_path = args.output_dir / "ANALYSIS.md"
    write_json(json_path, analysis)
    md_path.write_text(render_markdown(analysis), encoding="utf-8")
    print(f"analysis: {json_path}")
    print(f"report:   {md_path}")
    print(f"observational prediction insufficient: {analysis['observational_prediction_is_insufficient']}")
    print(f"horizon prediction error accumulates: {analysis['horizon_prediction_error_accumulates']}")
    print(f"long-horizon control non-monotonic: {analysis['long_horizon_control_not_monotonic']}")


if __name__ == "__main__":
    main()
