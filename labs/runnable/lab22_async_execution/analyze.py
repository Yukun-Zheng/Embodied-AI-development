#!/usr/bin/env python3
"""Derive mechanism-level conclusions from Lab 22 results.csv.

The analyzer intentionally separates two questions:
1. Did the executor change the intermediate variable it claims to change
   (temporal action staleness / action age)?
2. Did that intervention improve closed-loop task performance?

Those two answers are allowed to disagree. The generated report is therefore a
scientific interpretation of raw metrics, not a leaderboard ranking.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


def read_results(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows in {path}")
    return rows


def finite_float(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key} in row: {row}")
    return value


def classify_performance(delta_rmse: float, tolerance: float = 0.01) -> str:
    """Classify rebase RMSE relative to queue; positive delta means worse."""
    if delta_rmse < -tolerance:
        return "rebase_better"
    if delta_rmse > tolerance:
        return "rebase_worse"
    return "similar"


def analyze(rows: list[dict[str, str]]) -> dict[str, Any]:
    keyed: dict[tuple[float, str], dict[str, str]] = {}
    latencies: set[float] = set()
    for row in rows:
        latency = float(row["latency_s"])
        mode = row["mode"]
        keyed[(latency, mode)] = row
        latencies.add(latency)

    required_modes = {"sync_hold", "async_queue", "async_rebase"}
    derived: list[dict[str, Any]] = []
    for latency in sorted(latencies):
        missing = [mode for mode in required_modes if (latency, mode) not in keyed]
        if missing:
            raise ValueError(f"Missing {missing} at latency={latency}")

        sync = keyed[(latency, "sync_hold")]
        queue = keyed[(latency, "async_queue")]
        rebase = keyed[(latency, "async_rebase")]
        queue_age = finite_float(queue, "p95_action_age_s")
        rebase_age = finite_float(rebase, "p95_action_age_s")
        queue_rmse = finite_float(queue, "rmse")
        rebase_rmse = finite_float(rebase, "rmse")
        age_reduction = queue_age - rebase_age
        rmse_delta = rebase_rmse - queue_rmse

        derived.append(
            {
                "latency_s": latency,
                "sync_rmse": finite_float(sync, "rmse"),
                "sync_p95_action_age_s": finite_float(sync, "p95_action_age_s"),
                "queue_rmse": queue_rmse,
                "queue_p95_action_age_s": queue_age,
                "rebase_rmse": rebase_rmse,
                "rebase_p95_action_age_s": rebase_age,
                "rebase_action_age_reduction_s": age_reduction,
                "rebase_rmse_delta_vs_queue": rmse_delta,
                "performance_class": classify_performance(rmse_delta),
            }
        )

    zero = next((row for row in derived if abs(row["latency_s"]) < 1e-12), None)
    zero_latency_negative_control = bool(
        zero is not None
        and abs(zero["queue_p95_action_age_s"] - zero["rebase_p95_action_age_s"]) <= 1e-9
        and abs(zero["queue_rmse"] - zero["rebase_rmse"]) <= 1e-9
    )

    nonzero = [row for row in derived if row["latency_s"] > 0]
    mechanism_verified = bool(
        nonzero
        and all(row["rebase_action_age_reduction_s"] >= 0.04 for row in nonzero)
    )
    performance_not_guaranteed = any(
        row["performance_class"] == "rebase_worse" for row in nonzero
    )

    return {
        "schema_version": 1,
        "zero_latency_negative_control": zero_latency_negative_control,
        "action_age_mechanism_verified": mechanism_verified,
        "task_performance_improvement_not_guaranteed": performance_not_guaranteed,
        "interpretation": (
            "Latency-aware rebasing changes temporal staleness as intended, but reducing "
            "action age is not sufficient to guarantee better closed-loop tracking. "
            "Trajectory continuity, state-conditioned regeneration and policy/executor "
            "coupling remain separate mechanisms."
        ),
        "conditions": derived,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Lab 22 Derived Analysis",
        "",
        "> Generated from `results.csv`; do not treat this file as raw evidence.",
        "",
        "| latency | sync RMSE | sync p95 age | queue RMSE | queue p95 age | rebase RMSE | rebase p95 age | Δage queue→rebase | ΔRMSE rebase−queue |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["conditions"]:
        lines.append(
            "| {latency_s:.3f}s | {sync_rmse:.4f} | {sync_p95_action_age_s:.3f}s | "
            "{queue_rmse:.4f} | {queue_p95_action_age_s:.3f}s | {rebase_rmse:.4f} | "
            "{rebase_p95_action_age_s:.3f}s | {rebase_action_age_reduction_s:+.3f}s | "
            "{rebase_rmse_delta_vs_queue:+.4f} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Mechanism checks",
            "",
            f"- zero-latency negative control: **{report['zero_latency_negative_control']}**",
            f"- action-age intervention verified: **{report['action_age_mechanism_verified']}**",
            f"- task improvement not guaranteed: **{report['task_performance_improvement_not_guaranteed']}**",
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "",
            "The correct next question is therefore not ‘which executor wins?’, but which additional "
            "mechanism is required after timestamp alignment: state-conditioned regeneration, trajectory "
            "blending/continuity constraints, prediction of the execution-time state, or another temporal "
            "correction mechanism.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="Path to results.csv")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or args.results.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    report = analyze(read_results(args.results))

    json_path = output_dir / "analysis.json"
    markdown_path = output_dir / "ANALYSIS.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"analysis: {json_path}")
    print(f"report:   {markdown_path}")
    print(f"action-age mechanism verified: {report['action_age_mechanism_verified']}")
    print(f"task improvement not guaranteed: {report['task_performance_improvement_not_guaranteed']}")


if __name__ == "__main__":
    main()
