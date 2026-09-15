#!/usr/bin/env python3
"""CPU smoke tests for executable textbook labs.

The smoke suite validates scientific plumbing, not benchmark performance. Heavy
simulator/GPU labs will later register lightweight dry-run checks here.
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB22_DIR = ROOT / "labs" / "runnable" / "lab22_async_execution"
LAB22 = LAB22_DIR / "run.py"
LAB22_ANALYZE = LAB22_DIR / "analyze.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    assert math.isfinite(value), f"{key} is not finite in {row}"
    return value


def test_lab22(tmp: Path) -> None:
    output = tmp / "lab22"
    subprocess.run(
        [sys.executable, str(LAB22), "--quick", "--output", str(output)],
        cwd=ROOT,
        check=True,
    )

    results = output / "results.csv"
    manifest = output / "sweep_manifest.json"
    assert results.is_file(), "Lab 22 did not write results.csv"
    assert manifest.is_file(), "Lab 22 did not write sweep_manifest.json"

    rows = read_rows(results)
    assert len(rows) == 9, f"Expected 3 latencies × 3 modes = 9 conditions, got {len(rows)}"

    keyed: dict[tuple[float, str], dict[str, str]] = {}
    for row in rows:
        latency = float(row["latency_s"])
        mode = row["mode"]
        keyed[(latency, mode)] = row
        for metric in ["rmse", "mae", "max_abs_error", "success_fraction", "p95_action_age_s"]:
            as_float(row, metric)

        run_dir = output / row["run_dir"]
        for required in ["manifest.json", "steps.csv", "failures.jsonl", "summary.json"]:
            assert (run_dir / required).is_file(), f"Missing {required} for {latency=} {mode=}"

        with (run_dir / "manifest.json").open("r", encoding="utf-8") as handle:
            run_manifest = json.load(handle)
        assert run_manifest["lab_id"] == "lab22_async_execution"
        assert run_manifest["seed"] == 7

    # Mechanism-level positive test: when latency is nonzero, rebasing must
    # actually reduce the temporal staleness variable it claims to address.
    for latency in [0.1, 0.25]:
        queue_age = as_float(keyed[(latency, "async_queue")], "p95_action_age_s")
        rebase_age = as_float(keyed[(latency, "async_rebase")], "p95_action_age_s")
        assert rebase_age + 0.04 < queue_age, (
            f"Latency-aware rebase did not materially reduce p95 action age at {latency}s: "
            f"queue={queue_age:.4f}, rebase={rebase_age:.4f}"
        )

    # Negative control: at zero inference latency, queue and rebase should have
    # essentially the same action-age distribution.
    queue_zero = as_float(keyed[(0.0, "async_queue")], "p95_action_age_s")
    rebase_zero = as_float(keyed[(0.0, "async_rebase")], "p95_action_age_s")
    assert abs(queue_zero - rebase_zero) <= 1e-9, (
        f"Zero-latency negative control failed: queue={queue_zero}, rebase={rebase_zero}"
    )

    # Turn raw metrics into a derived, machine-readable scientific interpretation.
    subprocess.run(
        [sys.executable, str(LAB22_ANALYZE), str(results), "--output-dir", str(output)],
        cwd=ROOT,
        check=True,
    )
    analysis_json = output / "analysis.json"
    analysis_md = output / "ANALYSIS.md"
    assert analysis_json.is_file(), "Lab 22 analyzer did not write analysis.json"
    assert analysis_md.is_file(), "Lab 22 analyzer did not write ANALYSIS.md"

    with analysis_json.open("r", encoding="utf-8") as handle:
        analysis = json.load(handle)
    assert analysis["zero_latency_negative_control"] is True
    assert analysis["action_age_mechanism_verified"] is True
    # This is not a required universal outcome, but for the current reference
    # configuration it is an intentional teaching result: lowering action age
    # alone does not guarantee better task performance.
    assert analysis["task_performance_improvement_not_guaranteed"] is True

    print(
        "PASS lab22_async_execution: raw logs, manifests, latency intervention "
        "and derived mechanism analysis verified"
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-runnable-labs-") as tmpdir:
        test_lab22(Path(tmpdir))
    print("RUNNABLE LAB SMOKE PASSED")


if __name__ == "__main__":
    main()
