#!/usr/bin/env python3
"""Derive mechanism-level conclusions from runnable Lab 14 outputs."""

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
    keyed = {row["mode"]: row for row in rows}
    expected = {"slow_policy_only", "fast_tactile_reflex", "delayed_tactile_reflex"}
    if set(keyed) != expected:
        raise ValueError(f"Unexpected tactile modes: {sorted(keyed)}")

    slow = keyed["slow_policy_only"]
    fast = keyed["fast_tactile_reflex"]
    delayed = keyed["delayed_tactile_reflex"]

    fast_reflex_prevents_drops = (
        value(fast, "drop_rate") < 0.05
        and value(slow, "drop_rate") > value(fast, "drop_rate") + 0.25
    )
    fast_reflex_reduces_slip = (
        value(fast, "p95_max_slip_displacement_m")
        < 0.25 * value(slow, "p95_max_slip_displacement_m")
    )
    fast_reflex_reacts_before_slow_loop = (
        value(fast, "mean_reaction_latency_s")
        < 0.20 * value(slow, "mean_reaction_latency_s")
    )
    slow_loop_misses_short_events = (
        value(slow, "slow_event_miss_rate") > 0.20
        and value(slow, "reaction_detection_rate") < 0.90
    )
    delayed_tactile_breaks_fast_reflex = (
        value(delayed, "drop_rate") > value(fast, "drop_rate") + 0.70
        and value(delayed, "mean_reaction_latency_s") > 0.08
        and value(delayed, "p95_max_slip_displacement_m")
        > 4.0 * value(fast, "p95_max_slip_displacement_m")
    )

    return {
        "fast_reflex_prevents_drops": fast_reflex_prevents_drops,
        "fast_reflex_reduces_slip": fast_reflex_reduces_slip,
        "fast_reflex_reacts_before_slow_loop": fast_reflex_reacts_before_slow_loop,
        "slow_loop_misses_short_events": slow_loop_misses_short_events,
        "delayed_tactile_breaks_fast_reflex": delayed_tactile_breaks_fast_reflex,
        "modes": [
            {
                "mode": row["mode"],
                "drop_rate": value(row, "drop_rate"),
                "object_retention_rate": value(row, "object_retention_rate"),
                "p95_max_slip_displacement_m": value(row, "p95_max_slip_displacement_m"),
                "reaction_detection_rate": value(row, "reaction_detection_rate"),
                "mean_reaction_latency_s": value(row, "mean_reaction_latency_s"),
                "mean_peak_grip_force_n": value(row, "mean_peak_grip_force_n"),
                "mean_extra_grip_energy_n2s": value(row, "mean_extra_grip_energy_n2s"),
                "slow_event_miss_rate": value(row, "slow_event_miss_rate"),
            }
            for row in rows
        ],
    }


def render_markdown(analysis: dict[str, Any]) -> str:
    lines = [
        "# Lab 14 Derived Analysis",
        "",
        "| Mode | drop rate | p95 slip (mm) | detection | reaction (ms) | peak grip (N) | residual energy |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["modes"]:
        lines.append(
            f"| `{row['mode']}` | {row['drop_rate']:.3f} | "
            f"{1000.0 * row['p95_max_slip_displacement_m']:.3f} | "
            f"{row['reaction_detection_rate']:.3f} | "
            f"{1000.0 * row['mean_reaction_latency_s']:.1f} | "
            f"{row['mean_peak_grip_force_n']:.2f} | {row['mean_extra_grip_energy_n2s']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"- Fast tactile reflex prevents drops: **{analysis['fast_reflex_prevents_drops']}**",
            f"- Fast tactile reflex reduces slip displacement: **{analysis['fast_reflex_reduces_slip']}**",
            f"- Fast reflex reacts before the slow policy loop: **{analysis['fast_reflex_reacts_before_slow_loop']}**",
            f"- Slow loop misses transient events: **{analysis['slow_loop_misses_short_events']}**",
            f"- Delayed tactile destroys the fast-reflex benefit: **{analysis['delayed_tactile_breaks_fast_reflex']}**",
            "",
            "## Interpretation",
            "",
            "The mechanism is multi-rate feedback, not a claim that tactile input is universally superior to vision or VLA. A short contact event can begin and end between two high-level policy updates. A fast residual loop can still intervene on the same grasp command before slip displacement crosses the drop threshold.",
            "",
            "The delayed-tactile control is essential: running a correction function at 200 Hz does not help if its information is already stale. Sensor rate, timestamp age, controller bandwidth and actuator response must be analyzed together.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path, help="Path to mode_metrics.csv")
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
        "fast_reflex_prevents_drops",
        "fast_reflex_reduces_slip",
        "fast_reflex_reacts_before_slow_loop",
        "slow_loop_misses_short_events",
        "delayed_tactile_breaks_fast_reflex",
    ]:
        print(f"{key}: {analysis[key]}")


if __name__ == "__main__":
    main()
