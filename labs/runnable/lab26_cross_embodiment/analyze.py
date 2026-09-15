#!/usr/bin/env python3
"""Analyze Lab 26 and verify seen-mixture vs held-out morphology claims."""

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
    embodiment_rows: list[dict[str, str]],
    interface_rows: list[dict[str, str]],
) -> dict[str, Any]:
    conditions = {row["condition"]: row for row in condition_rows}
    required_conditions = {
        "raw_shared",
        "canonical_interface_only",
        "seen_robot_lookup",
        "morphology_conditioned",
        "wrong_morphology_tag",
        "wrong_action_semantics",
    }
    if set(conditions) != required_conditions:
        raise ValueError(
            f"Expected {sorted(required_conditions)}, got {sorted(conditions)}"
        )

    by_pair = {
        (row["condition"], row["embodiment"]): row for row in embodiment_rows
    }
    for condition in required_conditions:
        for embodiment in ("A", "B", "C", "D"):
            if (condition, embodiment) not in by_pair:
                raise ValueError(f"Missing embodiment metric: {condition}/{embodiment}")

    for row in condition_rows:
        for key in [
            "seen_success_rate",
            "unseen_success_rate",
            "unseen_interpolation_success_rate",
            "unseen_extrapolation_success_rate",
            "overall_success_rate",
            "mean_final_position_error",
            "mean_integrated_squared_error",
            "mean_force_energy",
            "mean_saturation_fraction",
        ]:
            number(row, key)

    max_state_roundtrip = max(
        number(row, "max_state_roundtrip_error") for row in interface_rows
    )
    max_action_roundtrip = max(
        number(row, "max_action_roundtrip_error") for row in interface_rows
    )

    raw = conditions["raw_shared"]
    canonical = conditions["canonical_interface_only"]
    lookup = conditions["seen_robot_lookup"]
    conditioned = conditions["morphology_conditioned"]
    wrong_tag = conditions["wrong_morphology_tag"]
    wrong_action = conditions["wrong_action_semantics"]

    raw_seen = number(raw, "seen_success_rate")
    raw_unseen = number(raw, "unseen_success_rate")
    canonical_seen = number(canonical, "seen_success_rate")
    canonical_unseen = number(canonical, "unseen_success_rate")
    lookup_seen = number(lookup, "seen_success_rate")
    lookup_unseen = number(lookup, "unseen_success_rate")
    lookup_interp = number(lookup, "unseen_interpolation_success_rate")
    lookup_extra = number(lookup, "unseen_extrapolation_success_rate")
    conditioned_seen = number(conditioned, "seen_success_rate")
    conditioned_unseen = number(conditioned, "unseen_success_rate")
    conditioned_interp = number(conditioned, "unseen_interpolation_success_rate")
    conditioned_extra = number(conditioned, "unseen_extrapolation_success_rate")
    wrong_tag_unseen = number(wrong_tag, "unseen_success_rate")

    b_wrong_action = number(by_pair[("wrong_action_semantics", "B")], "success_rate")
    d_wrong_action = number(by_pair[("wrong_action_semantics", "D")], "success_rate")
    b_raw = number(by_pair[("raw_shared", "B")], "success_rate")
    d_raw = number(by_pair[("raw_shared", "D")], "success_rate")
    c_lookup = number(by_pair[("seen_robot_lookup", "C")], "success_rate")
    d_lookup = number(by_pair[("seen_robot_lookup", "D")], "success_rate")
    d_wrong_tag = number(by_pair[("wrong_morphology_tag", "D")], "success_rate")

    unseen_adaptation = {
        row["condition"]: int(float(row["adaptation_steps_unseen"]))
        for row in condition_rows
    }
    parameter_counts = {
        row["condition"]: int(float(row["policy_parameter_count"]))
        for row in condition_rows
    }

    analysis: dict[str, Any] = {
        "interface_roundtrip_is_exact": (
            max_state_roundtrip < 1e-12 and max_action_roundtrip < 1e-12
        ),
        "canonical_semantics_improve_seen_mixture": canonical_seen - raw_seen >= 0.30,
        "canonical_semantics_improve_held_out_transfer": (
            canonical_unseen - raw_unseen >= 0.35
        ),
        "seen_robot_lookup_handles_seen_bodies": lookup_seen >= 0.99,
        "seen_mixture_is_not_unseen_transfer": (
            lookup_seen - lookup_unseen >= 0.25 and d_lookup <= 0.50
        ),
        "held_out_interpolation_and_extrapolation_are_reported_separately": (
            lookup_interp >= 0.95 and lookup_extra <= 0.50 and c_lookup >= 0.95
        ),
        "morphology_conditioning_preserves_seen_performance": conditioned_seen >= 0.99,
        "morphology_conditioning_zero_shot_transfers": (
            conditioned_unseen >= 0.99
            and conditioned_interp >= 0.99
            and conditioned_extra >= 0.99
        ),
        "continuous_descriptor_beats_seen_robot_lookup_on_unseen": (
            conditioned_unseen - lookup_unseen >= 0.30
        ),
        "morphology_tag_is_causally_used": (
            conditioned_unseen - wrong_tag_unseen >= 0.30 and d_wrong_tag <= 0.50
        ),
        "action_semantics_are_causally_necessary": (
            b_wrong_action <= 0.05 and d_wrong_action <= 0.05
        ),
        "raw_shape_compatibility_is_not_semantic_compatibility": (
            b_raw <= 0.05 and d_raw <= 0.05
        ),
        "held_out_transfer_uses_zero_task_adaptation": all(
            steps == 0 for steps in unseen_adaptation.values()
        ),
        "shared_policy_capacity_is_fixed": (
            len(set(parameter_counts.values())) == 1
            and next(iter(parameter_counts.values())) == 2
        ),
        "metrics": {
            "canonical_seen_gain_over_raw": canonical_seen - raw_seen,
            "canonical_unseen_gain_over_raw": canonical_unseen - raw_unseen,
            "seen_lookup_seen_minus_unseen": lookup_seen - lookup_unseen,
            "conditioned_unseen_gain_over_seen_lookup": conditioned_unseen - lookup_unseen,
            "conditioned_unseen_gain_over_wrong_tag": conditioned_unseen - wrong_tag_unseen,
            "max_state_roundtrip_error": max_state_roundtrip,
            "max_action_roundtrip_error": max_action_roundtrip,
            "lookup_C_success": c_lookup,
            "lookup_D_success": d_lookup,
            "wrong_action_B_success": b_wrong_action,
            "wrong_action_D_success": d_wrong_action,
        },
        "conditions": {
            name: {
                "seen_success_rate": number(row, "seen_success_rate"),
                "unseen_success_rate": number(row, "unseen_success_rate"),
                "unseen_interpolation_success_rate": number(
                    row, "unseen_interpolation_success_rate"
                ),
                "unseen_extrapolation_success_rate": number(
                    row, "unseen_extrapolation_success_rate"
                ),
                "adaptation_steps_unseen": int(float(row["adaptation_steps_unseen"])),
                "policy_parameter_count": int(float(row["policy_parameter_count"])),
            }
            for name, row in conditions.items()
        },
        "embodiments": {
            f"{condition}/{embodiment}": {
                "success_rate": number(row, "success_rate"),
                "mean_final_position_error": number(
                    row, "mean_final_position_error"
                ),
                "mean_integrated_squared_error": number(
                    row, "mean_integrated_squared_error"
                ),
                "adaptation_steps": int(float(row["adaptation_steps"])),
            }
            for (condition, embodiment), row in by_pair.items()
        },
    }
    return analysis


def render_markdown(analysis: dict[str, Any]) -> str:
    metrics = analysis["metrics"]
    lines = [
        "# Lab 26 Analysis — Cross-Embodiment Transfer",
        "",
        "This report separates seen-robot mixture support from zero-shot held-out morphology transfer.",
        "",
        "## Mechanism checks",
        "",
    ]
    for key, value in analysis.items():
        if key in {"metrics", "conditions", "embodiments"}:
            continue
        lines.append(f"- **{key}**: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Derived gaps",
            "",
            f"- Canonical-interface gain on seen bodies: **{metrics['canonical_seen_gain_over_raw']:.3f}**",
            f"- Canonical-interface gain on held-out bodies: **{metrics['canonical_unseen_gain_over_raw']:.3f}**",
            f"- Seen-lookup seen→unseen gap: **{metrics['seen_lookup_seen_minus_unseen']:.3f}**",
            f"- Morphology-conditioned unseen gain over seen lookup: **{metrics['conditioned_unseen_gain_over_seen_lookup']:.3f}**",
            f"- Morphology-conditioned unseen gain over wrong tag: **{metrics['conditioned_unseen_gain_over_wrong_tag']:.3f}**",
            f"- Seen lookup C vs D: **{metrics['lookup_C_success']:.3f} / {metrics['lookup_D_success']:.3f}**",
            "",
            "## Interpretation",
            "",
            "A universal tensor shape or a table of seen robot identities is not sufficient evidence of cross-embodiment generalization. The held-out morphology must be evaluated separately, with action semantics, interface calibration and adaptation budget made explicit.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition_metrics", type=Path)
    parser.add_argument("embodiment_metrics", type=Path)
    parser.add_argument("interface_checks", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = build_analysis(
        read_rows(args.condition_metrics),
        read_rows(args.embodiment_metrics),
        read_rows(args.interface_checks),
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
        if key not in {"metrics", "conditions", "embodiments"} and value is not True
    ]
    if failed:
        raise SystemExit(f"Lab 26 mechanism checks failed: {', '.join(failed)}")
    print("Lab 26 analysis PASS")


if __name__ == "__main__":
    main()
