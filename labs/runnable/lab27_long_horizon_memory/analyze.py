#!/usr/bin/env python3
"""Analyze Lab 27 memory claims from episode-level outputs."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    **row,
                    "episode": int(row["episode"]),
                    "distractor_horizon": int(row["distractor_horizon"]),
                    "subtask_count": int(row["subtask_count"]),
                    "context_window": int(row["context_window"]),
                    "task_success": int(row["task_success"]),
                    "query_accuracy": float(row["query_accuracy"]),
                    "retrieval_cost": float(row["retrieval_cost"]),
                    "memory_slots": float(row["memory_slots"]),
                    "memory_bytes": float(row["memory_bytes"]),
                }
            )
    if not rows:
        raise ValueError(f"No episode rows in {path}")
    return rows


def aggregate(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    n = len(rows)
    return {
        "episodes": n,
        "task_success_rate": sum(row["task_success"] for row in rows) / n,
        "query_accuracy": sum(row["query_accuracy"] for row in rows) / n,
        "avg_retrieval_cost": sum(row["retrieval_cost"] for row in rows) / n,
        "avg_memory_slots": sum(row["memory_slots"] for row in rows) / n,
        "avg_memory_bytes": sum(row["memory_bytes"] for row in rows) / n,
    }


def key(condition: str, horizon: int) -> str:
    return f"{condition}@{horizon}"


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["condition"]), int(row["distractor_horizon"]))].append(row)
        by_condition[str(row["condition"])].append(row)

    horizons = sorted({int(row["distractor_horizon"]) for row in rows})
    if len(horizons) != 3:
        raise AssertionError(f"Expected three horizon levels, got {horizons}")
    short_h, medium_h, long_h = horizons

    metrics = {
        key(condition, horizon): aggregate(group)
        for (condition, horizon), group in sorted(grouped.items())
    }
    aggregate_conditions = {
        condition: aggregate(group)
        for condition, group in sorted(by_condition.items())
    }

    required_conditions = {
        "no_memory",
        "frame_context",
        "episodic_log",
        "semantic_memory",
        "shuffled_memory",
        "unrelated_memory",
    }
    missing = required_conditions - set(aggregate_conditions)
    if missing:
        raise AssertionError(f"Missing conditions: {sorted(missing)}")

    def m(condition: str, horizon: int, metric: str) -> float:
        return float(metrics[key(condition, horizon)][metric])

    relations = {
        "persistent_memory_solves_long_horizon": all(
            m(condition, horizon, "task_success_rate") > 0.99
            for condition in ("episodic_log", "semantic_memory")
            for horizon in horizons
        ),
        "bounded_context_breaks_after_window": (
            m("frame_context", short_h, "task_success_rate") > 0.99
            and m("frame_context", medium_h, "task_success_rate") < 0.08
            and m("frame_context", long_h, "task_success_rate") < 0.08
        ),
        "no_memory_stays_at_balanced_chance": all(
            m("no_memory", horizon, "task_success_rate") < 0.08
            and 0.20 < m("no_memory", horizon, "query_accuracy") < 0.30
            for horizon in horizons
        ),
        "shuffled_content_falsifies_memory_claim": all(
            m("shuffled_memory", horizon, "task_success_rate") < 0.01
            and m("shuffled_memory", horizon, "query_accuracy") < 0.01
            for horizon in horizons
        ),
        "unrelated_memory_does_not_help": all(
            m("unrelated_memory", horizon, "task_success_rate") < 0.08
            and 0.20 < m("unrelated_memory", horizon, "query_accuracy") < 0.30
            for horizon in horizons
        ),
        "semantic_and_shuffled_capacity_matched": all(
            abs(
                m("semantic_memory", horizon, "avg_memory_slots")
                - m("shuffled_memory", horizon, "avg_memory_slots")
            )
            < 1e-9
            for horizon in horizons
        ),
        "semantic_memory_compresses_long_episode": (
            m("semantic_memory", long_h, "avg_memory_bytes")
            < 0.20 * m("episodic_log", long_h, "avg_memory_bytes")
            and m("semantic_memory", long_h, "avg_retrieval_cost")
            < 0.20 * m("episodic_log", long_h, "avg_retrieval_cost")
        ),
        "episodic_retrieval_cost_scales_with_horizon": (
            m("episodic_log", long_h, "avg_retrieval_cost")
            > 2.0 * m("episodic_log", short_h, "avg_retrieval_cost")
        ),
        "semantic_cost_is_horizon_invariant": (
            abs(
                m("semantic_memory", short_h, "avg_retrieval_cost")
                - m("semantic_memory", long_h, "avg_retrieval_cost")
            )
            < 1e-9
            and abs(
                m("semantic_memory", short_h, "avg_memory_bytes")
                - m("semantic_memory", long_h, "avg_memory_bytes")
            )
            < 1e-9
        ),
    }

    failed = [name for name, passed in relations.items() if not passed]
    if failed:
        details = json.dumps(
            {"failed": failed, "metrics": metrics}, ensure_ascii=False, indent=2
        )
        raise AssertionError(f"Lab 27 mechanism relations failed:\n{details}")

    return {
        "status": "pass",
        "horizons": horizons,
        "relations": relations,
        "condition_horizon_metrics": metrics,
        "condition_metrics": aggregate_conditions,
        "reference_observations": {
            "no_memory_success": aggregate_conditions["no_memory"]["task_success_rate"],
            "frame_context_success": aggregate_conditions["frame_context"]["task_success_rate"],
            "episodic_success": aggregate_conditions["episodic_log"]["task_success_rate"],
            "semantic_success": aggregate_conditions["semantic_memory"]["task_success_rate"],
            "shuffled_success": aggregate_conditions["shuffled_memory"]["task_success_rate"],
            "unrelated_success": aggregate_conditions["unrelated_memory"]["task_success_rate"],
            "long_episodic_memory_bytes": m("episodic_log", long_h, "avg_memory_bytes"),
            "long_semantic_memory_bytes": m("semantic_memory", long_h, "avg_memory_bytes"),
            "long_episodic_retrieval_cost": m("episodic_log", long_h, "avg_retrieval_cost"),
            "long_semantic_retrieval_cost": m("semantic_memory", long_h, "avg_retrieval_cost"),
        },
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "analysis.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    obs = result["reference_observations"]
    lines = [
        "# Lab 27 Analysis",
        "",
        "All deterministic mechanism relations passed.",
        "",
        "## Aggregate task success",
        "",
        f"- no memory: **{obs['no_memory_success']:.3f}**",
        f"- bounded frame context: **{obs['frame_context_success']:.3f}**",
        f"- episodic log: **{obs['episodic_success']:.3f}**",
        f"- semantic memory: **{obs['semantic_success']:.3f}**",
        f"- shuffled memory: **{obs['shuffled_success']:.3f}**",
        f"- unrelated memory: **{obs['unrelated_success']:.3f}**",
        "",
        "## Long-horizon memory cost",
        "",
        f"- episodic bytes: **{obs['long_episodic_memory_bytes']:.1f}**",
        f"- semantic bytes: **{obs['long_semantic_memory_bytes']:.1f}**",
        f"- episodic retrieval scan cost: **{obs['long_episodic_retrieval_cost']:.1f}**",
        f"- semantic retrieval cost: **{obs['long_semantic_retrieval_cost']:.1f}**",
        "",
        "The claim is about state persistence under partial observability, not about language-model memory quality.",
        "",
    ]
    (output_dir / "ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_metrics", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    result = analyze(load_rows(args.episode_metrics))
    write_outputs(result, args.output_dir)

    obs = result["reference_observations"]
    print("PASS: Lab 27 long-horizon memory relations")
    print(
        "success no/frame/episodic/semantic/shuffled/unrelated = "
        f"{obs['no_memory_success']:.3f}/"
        f"{obs['frame_context_success']:.3f}/"
        f"{obs['episodic_success']:.3f}/"
        f"{obs['semantic_success']:.3f}/"
        f"{obs['shuffled_success']:.3f}/"
        f"{obs['unrelated_success']:.3f}"
    )
    print(
        "long memory bytes episodic/semantic = "
        f"{obs['long_episodic_memory_bytes']:.1f}/"
        f"{obs['long_semantic_memory_bytes']:.1f}"
    )


if __name__ == "__main__":
    main()
