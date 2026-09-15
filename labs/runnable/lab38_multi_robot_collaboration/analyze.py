#!/usr/bin/env python3
"""Independent mechanism analysis for Lab 38."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

NUMERIC_FLOAT = {
    "completion_rate",
    "throughput_jobs_per_step",
    "communication_delivery_ratio",
    "avg_status_age_steps",
}
NUMERIC_INT = {
    "completed_jobs",
    "total_jobs",
    "all_complete",
    "makespan_steps",
    "duplicate_claims",
    "blocked_steps",
    "stale_idle_steps",
    "assignment_rejections",
    "capability_mismatch_assignments",
    "work_steps",
    "idle_steps",
    "communication_messages_sent",
    "communication_messages_transmitted",
    "communication_bytes_transmitted",
    "reallocation_count",
    "interrupted_job_id",
    "interrupted_job_recovered",
    "recovery_latency_steps",
}


def load_metrics(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, Any] = dict(raw)
            for key in NUMERIC_FLOAT:
                row[key] = float(row[key])
            for key in NUMERIC_INT:
                row[key] = int(float(row[key]))
            rows[str(row["condition"])] = row
    if not rows:
        raise ValueError(f"No condition rows in {path}")
    return rows


def analyze(metrics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    required = {
        "independent_no_comm",
        "coordinated_fresh",
        "coordinated_delayed",
        "coordinated_dropout",
        "shuffled_capability_map",
        "failure_no_reallocation",
        "failure_reallocation",
    }
    missing = required - set(metrics)
    if missing:
        raise AssertionError(f"Missing conditions: {sorted(missing)}")

    independent = metrics["independent_no_comm"]
    fresh = metrics["coordinated_fresh"]
    delayed = metrics["coordinated_delayed"]
    dropout = metrics["coordinated_dropout"]
    shuffled = metrics["shuffled_capability_map"]
    failure_no = metrics["failure_no_reallocation"]
    failure_yes = metrics["failure_reallocation"]

    relations = {
        "fresh_coordination_finishes_full_queue": (
            fresh["completion_rate"] == 1.0
            and fresh["all_complete"] == 1
            and fresh["capability_mismatch_assignments"] == 0
        ),
        "coordination_outperforms_no_communication": (
            fresh["completion_rate"] - independent["completion_rate"] >= 0.20
            and fresh["makespan_steps"] < independent["makespan_steps"]
        ),
        "no_communication_creates_duplicate_claims": (
            independent["communication_messages_sent"] == 0
            and independent["duplicate_claims"] >= 6
            and independent["blocked_steps"] >= independent["duplicate_claims"]
        ),
        "delay_costs_time_before_it_costs_success": (
            delayed["completion_rate"] == fresh["completion_rate"]
            and delayed["makespan_steps"] > fresh["makespan_steps"]
            and delayed["stale_idle_steps"] > 0
            and delayed["avg_status_age_steps"] > fresh["avg_status_age_steps"]
        ),
        "dropout_degrades_fresh_coordination": (
            dropout["completion_rate"] < fresh["completion_rate"]
            and dropout["communication_delivery_ratio"] <= 0.30
            and dropout["stale_idle_steps"] > delayed["stale_idle_steps"]
        ),
        "correct_capability_metadata_is_causally_needed": (
            shuffled["completion_rate"] <= 0.60
            and shuffled["completion_rate"] < fresh["completion_rate"]
            and shuffled["capability_mismatch_assignments"] >= 4
            and shuffled["communication_delivery_ratio"]
            == fresh["communication_delivery_ratio"]
        ),
        "reallocation_recovers_interrupted_work": (
            failure_yes["completion_rate"] == 1.0
            and failure_yes["interrupted_job_recovered"] == 1
            and failure_yes["reallocation_count"] >= 1
            and failure_yes["recovery_latency_steps"] > 0
        ),
        "without_reallocation_interrupted_work_remains_stuck": (
            failure_no["completion_rate"] < failure_yes["completion_rate"]
            and failure_no["interrupted_job_recovered"] == 0
            and failure_no["reallocation_count"] == 0
        ),
        "failure_comparison_holds_detection_constant": (
            failure_no["interrupted_job_id"] == failure_yes["interrupted_job_id"]
            and failure_no["interrupted_job_id"] >= 0
        ),
    }

    failed = [name for name, passed in relations.items() if not passed]
    if failed:
        raise AssertionError(
            "Lab 38 mechanism relations failed:\n"
            + json.dumps(
                {"failed": failed, "metrics": metrics},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )

    return {
        "status": "pass",
        "relations": relations,
        "metrics": metrics,
        "reference_observations": {
            "fresh_completion": fresh["completion_rate"],
            "fresh_makespan": fresh["makespan_steps"],
            "independent_completion": independent["completion_rate"],
            "independent_duplicate_claims": independent["duplicate_claims"],
            "independent_blocked_steps": independent["blocked_steps"],
            "delayed_completion": delayed["completion_rate"],
            "delayed_makespan": delayed["makespan_steps"],
            "delayed_stale_idle_steps": delayed["stale_idle_steps"],
            "dropout_completion": dropout["completion_rate"],
            "dropout_delivery_ratio": dropout["communication_delivery_ratio"],
            "dropout_stale_idle_steps": dropout["stale_idle_steps"],
            "shuffled_completion": shuffled["completion_rate"],
            "shuffled_mismatch_assignments": shuffled[
                "capability_mismatch_assignments"
            ],
            "failure_no_reallocation_completion": failure_no["completion_rate"],
            "failure_reallocation_completion": failure_yes["completion_rate"],
            "failure_recovery_latency": failure_yes["recovery_latency_steps"],
        },
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    obs = result["reference_observations"]
    lines = [
        "# Lab 38 Analysis",
        "",
        "All deterministic collaboration mechanism relations passed.",
        "",
        "## Normal collaboration suite",
        "",
        f"- coordinated fresh: completion **{obs['fresh_completion']:.3f}**, makespan **{obs['fresh_makespan']}**",
        f"- independent/no-comm: completion **{obs['independent_completion']:.3f}**, duplicate claims **{obs['independent_duplicate_claims']}**, blocked steps **{obs['independent_blocked_steps']}**",
        f"- delayed status: completion **{obs['delayed_completion']:.3f}**, makespan **{obs['delayed_makespan']}**, stale-idle **{obs['delayed_stale_idle_steps']}**",
        f"- dropout: completion **{obs['dropout_completion']:.3f}**, delivery ratio **{obs['dropout_delivery_ratio']:.3f}**, stale-idle **{obs['dropout_stale_idle_steps']}**",
        f"- shuffled capability metadata: completion **{obs['shuffled_completion']:.3f}**, mismatch assignments **{obs['shuffled_mismatch_assignments']}**",
        "",
        "## Single-agent failure suite",
        "",
        f"- no reallocation completion: **{obs['failure_no_reallocation_completion']:.3f}**",
        f"- reallocation completion: **{obs['failure_reallocation_completion']:.3f}**",
        f"- interrupted-job recovery latency: **{obs['failure_recovery_latency']} steps**",
        "",
        "The failure comparison holds failure detection fixed; it isolates release/reallocation of interrupted work.",
        "",
    ]
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("condition_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    result = analyze(load_metrics(args.condition_metrics))
    write_outputs(result, args.output_dir)
    obs = result["reference_observations"]
    print("PASS: Lab 38 multi-robot collaboration relations")
    print(
        "normal completion fresh/independent/delayed/dropout/shuffled = "
        f"{obs['fresh_completion']:.3f}/"
        f"{obs['independent_completion']:.3f}/"
        f"{obs['delayed_completion']:.3f}/"
        f"{obs['dropout_completion']:.3f}/"
        f"{obs['shuffled_completion']:.3f}"
    )
    print(
        "failure completion no-reallocation/reallocation = "
        f"{obs['failure_no_reallocation_completion']:.3f}/"
        f"{obs['failure_reallocation_completion']:.3f}"
    )


if __name__ == "__main__":
    main()
