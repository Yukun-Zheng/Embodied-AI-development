#!/usr/bin/env python3
"""Deterministic smoke test for Lab 27."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "run.py"
ANALYZE = HERE / "analyze.py"
CONDITIONS = (
    "no_memory",
    "frame_context",
    "episodic_log",
    "semantic_memory",
    "shuffled_memory",
    "unrelated_memory",
)
HORIZONS = (4, 10, 16)
EPISODES_PER_HORIZON = 64


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lab27_memory_") as tmp:
        output = Path(tmp)
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            check=True,
        )

        required = [
            output / "episode_metrics.csv",
            output / "condition_metrics.csv",
            output / "horizon_metrics.csv",
            output / "experiment_summary.json",
        ]
        for path in required:
            assert path.is_file(), f"missing artifact: {path}"

        episodes = load_csv(output / "episode_metrics.csv")
        expected_rows = len(CONDITIONS) * len(HORIZONS) * EPISODES_PER_HORIZON
        assert len(episodes) == expected_rows, (len(episodes), expected_rows)

        run_dirs = sorted((output / "runs").iterdir())
        assert len(run_dirs) == len(CONDITIONS), len(run_dirs)
        for run_dir in run_dirs:
            for filename in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                assert (run_dir / filename).is_file(), f"{run_dir}: missing {filename}"

        # Raw-design invariants: paired balanced episodes and no task adaptation.
        summary = json.loads((output / "experiment_summary.json").read_text(encoding="utf-8"))
        assert summary["paired_balanced_missions"] is True
        assert summary["mission_space_size"] == 64
        assert summary["task_adaptation_steps"] == 0
        assert summary["context_window"] == 8

        # Independently check the strongest raw episode-level relations before
        # invoking analyze.py, so the analyzer cannot self-certify a broken run.
        def rows(condition: str, horizon: int) -> list[dict[str, str]]:
            return [
                row
                for row in episodes
                if row["condition"] == condition
                and int(row["distractor_horizon"]) == horizon
            ]

        def success(condition: str, horizon: int) -> float:
            selected = rows(condition, horizon)
            return sum(int(row["task_success"]) for row in selected) / len(selected)

        def query_accuracy(condition: str, horizon: int) -> float:
            selected = rows(condition, horizon)
            return sum(float(row["query_accuracy"]) for row in selected) / len(selected)

        assert success("semantic_memory", 16) == 1.0
        assert success("episodic_log", 16) == 1.0
        assert success("frame_context", 4) == 1.0
        assert success("frame_context", 10) == 1.0 / 64.0
        assert success("frame_context", 16) == 1.0 / 64.0
        assert success("no_memory", 16) == 1.0 / 64.0
        assert query_accuracy("no_memory", 16) == 0.25
        assert success("shuffled_memory", 16) == 0.0
        assert query_accuracy("shuffled_memory", 16) == 0.0
        assert success("unrelated_memory", 16) == 1.0 / 64.0

        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "episode_metrics.csv"),
                "--output-dir",
                str(output),
            ],
            check=True,
        )

        analysis = json.loads((output / "analysis.json").read_text(encoding="utf-8"))
        assert analysis["status"] == "pass"
        assert all(analysis["relations"].values())
        assert (output / "ANALYSIS.md").is_file()

        obs = analysis["reference_observations"]
        print(
            "Lab 27 smoke reference: "
            f"no={obs['no_memory_success']:.6f}, "
            f"frame={obs['frame_context_success']:.6f}, "
            f"episodic={obs['episodic_success']:.6f}, "
            f"semantic={obs['semantic_success']:.6f}, "
            f"shuffled={obs['shuffled_success']:.6f}, "
            f"unrelated={obs['unrelated_success']:.6f}"
        )
        print("PASS: Lab 27 raw artifacts + independent long-horizon memory analysis")


if __name__ == "__main__":
    main()
