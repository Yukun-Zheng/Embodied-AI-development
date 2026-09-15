#!/usr/bin/env python3
"""Analyze Lab 40 safety/availability and mechanism-specific negative controls."""

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


def number(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key} for {row}: {value}")
    return value


def build_analysis(
    condition_rows: list[dict[str, str]],
    scenario_rows: list[dict[str, str]],
) -> dict[str, Any]:
    conditions = {row["condition"]: row for row in condition_rows}
    required_conditions = {
        "no_shield",
        "static_rules",
        "predictive_no_freshness",
        "predictive_shield",
        "overconservative_shield",
    }
    required_scenarios = {
        "normal",
        "model_timeout",
        "stale_camera",
        "unsafe_joint_target",
        "human_proximity",
    }
    if set(conditions) != required_conditions:
        raise ValueError(
            f"Expected conditions {sorted(required_conditions)}, got {sorted(conditions)}"
        )

    by_pair = {(row["condition"], row["scenario"]): row for row in scenario_rows}
    for condition in required_conditions:
        for scenario in required_scenarios:
            if (condition, scenario) not in by_pair:
                raise ValueError(f"Missing scenario row: {condition}/{scenario}")

    for row in condition_rows:
        for key in [
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
            number(row, key)

    def v(condition: str, scenario: str) -> float:
        return number(by_pair[(condition, scenario)], "violation_rate")

    def intervention(condition: str, scenario: str) -> float:
        return number(by_pair[(condition, scenario)], "intervention_rate")

    def ask(condition: str, scenario: str) -> float:
        return number(by_pair[(condition, scenario)], "ask_human_rate")

    no = conditions["no_shield"]
    static = conditions["static_rules"]
    nofresh = conditions["predictive_no_freshness"]
    predictive = conditions["predictive_shield"]
    conservative = conditions["overconservative_shield"]

    no_fault = number(no, "fault_violation_rate")
    static_fault = number(static, "fault_violation_rate")
    nofresh_fault = number(nofresh, "fault_violation_rate")
    predictive_fault = number(predictive, "fault_violation_rate")
    conservative_fault = number(conservative, "fault_violation_rate")

    predictive_normal_completion = number(predictive, "normal_completion_rate")
    predictive_false_stop = number(predictive, "normal_false_intervention_rate")
    conservative_normal_completion = number(conservative, "normal_completion_rate")
    conservative_false_stop = number(
        conservative, "normal_false_intervention_rate"
    )

    analysis: dict[str, Any] = {
        "faults_are_physically_consequential_without_shield": all(
            v("no_shield", scenario) >= 0.95
            for scenario in required_scenarios - {"normal"}
        ),
        "static_target_rejection_catches_obvious_unsafe_target": (
            v("static_rules", "unsafe_joint_target") <= 0.05
            and intervention("static_rules", "unsafe_joint_target") >= 0.95
            and ask("static_rules", "unsafe_joint_target") >= 0.95
        ),
        "static_rules_are_too_late_for_dynamic_hazards": (
            v("static_rules", "model_timeout") >= 0.90
            and v("static_rules", "stale_camera") >= 0.90
            and v("static_rules", "human_proximity") >= 0.90
        ),
        "predictive_stopping_beats_reactive_human_rule": (
            v("static_rules", "human_proximity")
            - v("predictive_shield", "human_proximity")
            >= 0.80
        ),
        "freshness_check_is_causally_necessary_for_stale_camera": (
            v("predictive_no_freshness", "stale_camera")
            - v("predictive_shield", "stale_camera")
            >= 0.80
        ),
        "model_watchdog_prevents_timeout_runaway": (
            v("static_rules", "model_timeout") >= 0.90
            and v("predictive_shield", "model_timeout") <= 0.05
        ),
        "predictive_shield_prevents_all_injected_fault_violations": all(
            v("predictive_shield", scenario) <= 0.05
            for scenario in required_scenarios - {"normal"}
        ),
        "predictive_shield_intervenes_on_all_fault_classes": all(
            intervention("predictive_shield", scenario) >= 0.95
            for scenario in required_scenarios - {"normal"}
        ),
        "unsafe_target_routes_to_human_review": (
            v("predictive_shield", "unsafe_joint_target") <= 0.05
            and ask("predictive_shield", "unsafe_joint_target") >= 0.95
        ),
        "predictive_shield_preserves_normal_availability": (
            predictive_normal_completion >= 0.95
            and predictive_false_stop <= 0.05
        ),
        "zero_violation_alone_is_not_a_valid_safety_solution": (
            conservative_fault <= 0.05
            and conservative_false_stop >= 0.20
            and predictive_normal_completion - conservative_normal_completion >= 0.20
        ),
        "safety_availability_tradeoff_is_explicit": (
            predictive_fault <= 0.05
            and conservative_fault <= 0.05
            and conservative_false_stop - predictive_false_stop >= 0.20
        ),
        "metrics": {
            "no_shield_fault_violation_rate": no_fault,
            "static_fault_violation_rate": static_fault,
            "predictive_no_freshness_fault_violation_rate": nofresh_fault,
            "predictive_shield_fault_violation_rate": predictive_fault,
            "overconservative_fault_violation_rate": conservative_fault,
            "predictive_normal_completion_rate": predictive_normal_completion,
            "predictive_normal_false_intervention_rate": predictive_false_stop,
            "overconservative_normal_completion_rate": conservative_normal_completion,
            "overconservative_normal_false_intervention_rate": conservative_false_stop,
            "stale_camera_freshness_gain": (
                v("predictive_no_freshness", "stale_camera")
                - v("predictive_shield", "stale_camera")
            ),
            "human_predictive_gain": (
                v("static_rules", "human_proximity")
                - v("predictive_shield", "human_proximity")
            ),
        },
        "conditions": {
            name: {
                "normal_completion_rate": number(row, "normal_completion_rate"),
                "normal_false_intervention_rate": number(
                    row, "normal_false_intervention_rate"
                ),
                "fault_violation_rate": number(row, "fault_violation_rate"),
                "fault_intervention_rate": number(row, "fault_intervention_rate"),
                "unsafe_target_ask_human_rate": number(
                    row, "unsafe_target_ask_human_rate"
                ),
            }
            for name, row in conditions.items()
        },
        "scenarios": {
            f"{condition}/{scenario}": {
                "completion_rate": number(row, "completion_rate"),
                "violation_rate": number(row, "violation_rate"),
                "joint_violation_rate": number(row, "joint_violation_rate"),
                "human_collision_rate": number(row, "human_collision_rate"),
                "intervention_rate": number(row, "intervention_rate"),
                "ask_human_rate": number(row, "ask_human_rate"),
            }
            for (condition, scenario), row in by_pair.items()
        },
    }
    return analysis


def render_markdown(analysis: dict[str, Any]) -> str:
    metrics = analysis["metrics"]
    lines = [
        "# Lab 40 Analysis — Watchdog / Safety Shield",
        "",
        "Safety is evaluated after physical stopping dynamics and is paired with a normal-task availability metric.",
        "",
        "## Mechanism checks",
        "",
    ]
    for key, value in analysis.items():
        if key in {"metrics", "conditions", "scenarios"}:
            continue
        lines.append(f"- **{key}**: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Derived gaps",
            "",
            f"- No-shield fault violation: **{metrics['no_shield_fault_violation_rate']:.3f}**",
            f"- Predictive-shield fault violation: **{metrics['predictive_shield_fault_violation_rate']:.3f}**",
            f"- Freshness gain on stale camera: **{metrics['stale_camera_freshness_gain']:.3f}**",
            f"- Predictive-vs-reactive gain on human approach: **{metrics['human_predictive_gain']:.3f}**",
            f"- Predictive normal completion / false intervention: **{metrics['predictive_normal_completion_rate']:.3f} / {metrics['predictive_normal_false_intervention_rate']:.3f}**",
            f"- Overconservative normal completion / false intervention: **{metrics['overconservative_normal_completion_rate']:.3f} / {metrics['overconservative_normal_false_intervention_rate']:.3f}**",
            "",
            "## Interpretation",
            "",
            "A safety rule is not validated because it fires. It is validated only if the robot remains inside the physical safety envelope after braking, while normal-task availability remains acceptable. Freshness, stopping distance and explicit action rejection are independent mechanisms and should be ablated separately.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition_metrics", type=Path)
    parser.add_argument("scenario_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = build_analysis(
        read_rows(args.condition_metrics), read_rows(args.scenario_metrics)
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "analysis.json").open("w", encoding="utf-8") as handle:
        json.dump(analysis, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    (args.output_dir / "ANALYSIS.md").write_text(
        render_markdown(analysis), encoding="utf-8"
    )

    failed = [
        key
        for key, value in analysis.items()
        if key not in {"metrics", "conditions", "scenarios"} and value is not True
    ]
    if failed:
        raise SystemExit(f"Lab 40 mechanism checks failed: {', '.join(failed)}")
    print("Lab 40 analysis PASS")


if __name__ == "__main__":
    main()
