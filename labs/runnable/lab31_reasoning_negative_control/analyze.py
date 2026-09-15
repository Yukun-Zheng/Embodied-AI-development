#!/usr/bin/env python3
"""Analyze Lab 31 reasoning controls and emit machine-readable mechanism claims."""

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


def finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key} for {row.get('condition')}: {value}")
    return value


def optional_float(row: dict[str, str], key: str) -> float | None:
    raw = row.get(key, "")
    if raw in {"", "None", "null"}:
        return None
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key} for {row.get('condition')}: {value}")
    return value


def build_analysis(rows: list[dict[str, str]]) -> dict[str, Any]:
    keyed = {row["condition"]: row for row in rows}
    required = {
        "correct_plan",
        "no_plan",
        "random_plan",
        "fluent_wrong_plan",
        "shuffled_binding",
    }
    if set(keyed) != required:
        raise ValueError(f"Expected conditions {sorted(required)}, got {sorted(keyed)}")

    correct = keyed["correct_plan"]
    no_plan = keyed["no_plan"]
    random_plan = keyed["random_plan"]
    wrong = keyed["fluent_wrong_plan"]
    binding = keyed["shuffled_binding"]

    for row in rows:
        for key in [
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
            finite(row, key)

    correct_success = finite(correct, "success_rate")
    no_plan_success = finite(no_plan, "success_rate")
    random_success = finite(random_plan, "success_rate")
    wrong_success = finite(wrong, "success_rate")
    binding_success = finite(binding, "success_rate")

    correct_locked = finite(correct, "locked_success_rate")
    no_plan_locked = finite(no_plan, "locked_success_rate")
    wrong_locked = finite(wrong, "locked_success_rate")
    no_plan_unlocked = finite(no_plan, "unlocked_success_rate")
    wrong_unlocked = finite(wrong, "unlocked_success_rate")

    correct_validity = finite(correct, "mean_action_validity")
    random_validity = finite(random_plan, "mean_action_validity")
    wrong_validity = finite(wrong, "mean_action_validity")
    binding_validity = finite(binding, "mean_action_validity")
    wrong_model_success = optional_float(wrong, "self_model_success_rate")
    correct_model_success = optional_float(correct, "self_model_success_rate")
    if wrong_model_success is None or correct_model_success is None:
        raise ValueError("Planner conditions must report self_model_success_rate")

    plan_lengths = {
        name: optional_float(keyed[name], "mean_plan_length")
        for name in ["correct_plan", "random_plan", "fluent_wrong_plan", "shuffled_binding"]
    }
    if any(value is None for value in plan_lengths.values()):
        raise ValueError("All plan-based controls must report mean_plan_length")
    plan_values = [float(value) for value in plan_lengths.values() if value is not None]
    matched_plan_budget_delta = max(plan_values) - min(plan_values)

    analysis: dict[str, Any] = {
        "correct_plan_success_is_high": correct_success >= 0.99 and correct_validity >= 0.99,
        "locked_dependency_requires_reasoning": correct_locked >= 0.99 and no_plan_locked <= 0.05,
        "easy_unlocked_cases_do_not_require_reasoning": no_plan_unlocked >= 0.95 and wrong_unlocked >= 0.95,
        "correct_reasoning_has_causal_gain": correct_success - no_plan_success >= 0.65,
        "fluent_wrong_is_internally_coherent": wrong_model_success >= 0.99,
        "fluent_wrong_fails_in_reality": wrong_model_success - wrong_success >= 0.65 and wrong_locked <= 0.05,
        "fluent_wrong_is_not_random_garbage": wrong_validity - random_validity >= 0.25,
        "random_order_control_fails": random_success <= 0.10,
        "binding_control_fails": binding_success <= 0.10,
        "matched_plan_budget": matched_plan_budget_delta <= 1e-9,
        "correct_binding_and_order_are_jointly_necessary": (
            correct_success - max(random_success, binding_success) >= 0.80
        ),
        "metrics": {
            "causal_reasoning_gain_vs_no_plan": correct_success - no_plan_success,
            "causal_reasoning_gain_vs_fluent_wrong": correct_success - wrong_success,
            "wrong_model_reality_gap": wrong_model_success - wrong_success,
            "fluent_wrong_validity_minus_random": wrong_validity - random_validity,
            "correct_validity_minus_wrong": correct_validity - wrong_validity,
            "binding_validity": binding_validity,
            "matched_plan_budget_delta": matched_plan_budget_delta,
            "correct_internal_model_success": correct_model_success,
            "fluent_wrong_internal_model_success": wrong_model_success,
        },
        "conditions": {
            row["condition"]: {
                "success_rate": finite(row, "success_rate"),
                "locked_success_rate": finite(row, "locked_success_rate"),
                "unlocked_success_rate": finite(row, "unlocked_success_rate"),
                "mean_action_validity": finite(row, "mean_action_validity"),
                "mean_final_progress": finite(row, "mean_final_progress"),
                "mean_plan_length": optional_float(row, "mean_plan_length"),
                "self_model_success_rate": optional_float(row, "self_model_success_rate"),
            }
            for row in rows
        },
    }
    return analysis


def render_markdown(analysis: dict[str, Any]) -> str:
    metrics = analysis["metrics"]
    lines = [
        "# Lab 31 Analysis — Reasoning Negative Controls",
        "",
        "This report separates executable causal planning from plan fluency, ordering and entity binding.",
        "",
        "## Mechanism checks",
        "",
    ]
    for key, value in analysis.items():
        if key in {"metrics", "conditions"}:
            continue
        lines.append(f"- **{key}**: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Derived gaps",
            "",
            f"- Correct-plan gain over no-plan: **{metrics['causal_reasoning_gain_vs_no_plan']:.3f}**",
            f"- Correct-plan gain over fluent-wrong: **{metrics['causal_reasoning_gain_vs_fluent_wrong']:.3f}**",
            f"- Fluent-wrong internal-model → real-world gap: **{metrics['wrong_model_reality_gap']:.3f}**",
            f"- Fluent-wrong validity minus random-plan validity: **{metrics['fluent_wrong_validity_minus_random']:.3f}**",
            f"- Plan-budget mean-length delta: **{metrics['matched_plan_budget_delta']:.6f}**",
            "",
            "## Interpretation",
            "",
            "A plan counts as useful reasoning only when its causal model, ordering and entity bindings survive execution in the true environment. Internal coherence or surface plausibility alone is insufficient.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(args.metrics)
    analysis = build_analysis(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "analysis.json").open("w", encoding="utf-8") as handle:
        json.dump(analysis, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    (args.output_dir / "ANALYSIS.md").write_text(render_markdown(analysis), encoding="utf-8")

    failed = [
        key
        for key, value in analysis.items()
        if key not in {"metrics", "conditions"} and value is not True
    ]
    if failed:
        raise SystemExit(f"Lab 31 mechanism checks failed: {', '.join(failed)}")
    print("Lab 31 analysis PASS")


if __name__ == "__main__":
    main()
