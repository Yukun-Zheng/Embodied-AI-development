#!/usr/bin/env python3
"""Deterministic smoke test for Lab 38."""

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
    "independent_no_comm",
    "coordinated_fresh",
    "coordinated_delayed",
    "coordinated_dropout",
    "shuffled_capability_map",
    "failure_no_reallocation",
    "failure_reallocation",
)


def load_metrics(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["condition"]: row for row in csv.DictReader(handle)}


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="lab38_multi_robot_") as tmp:
        output = Path(tmp)
        subprocess.run(
            [sys.executable, str(RUN), "--output", str(output)],
            check=True,
        )

        for filename in ("condition_metrics.csv", "job_metrics.csv", "experiment_summary.json"):
            assert (output / filename).is_file(), f"missing artifact: {filename}"

        run_dirs = sorted((output / "runs").iterdir())
        assert len(run_dirs) == len(CONDITIONS), len(run_dirs)
        for run_dir in run_dirs:
            for filename in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                assert (run_dir / filename).is_file(), f"{run_dir}: missing {filename}"

        experiment = json.loads((output / "experiment_summary.json").read_text(encoding="utf-8"))
        assert experiment["shared_authoritative_task_board"] is True
        assert experiment["robot_status_communicated"] is True
        assert experiment["failure_detection_fixed_in_failure_suite"] is True

        metrics = load_metrics(output / "condition_metrics.csv")
        assert set(metrics) == set(CONDITIONS)

        independent = metrics["independent_no_comm"]
        fresh = metrics["coordinated_fresh"]
        delayed = metrics["coordinated_delayed"]
        dropout = metrics["coordinated_dropout"]
        shuffled = metrics["shuffled_capability_map"]
        failure_no = metrics["failure_no_reallocation"]
        failure_yes = metrics["failure_reallocation"]

        # Raw deterministic reference checks. These are checked before the
        # analyzer so analyze.py cannot certify a malformed raw run.
        assert as_int(fresh, "completed_jobs") == 12
        assert as_float(fresh, "completion_rate") == 1.0
        assert as_int(fresh, "makespan_steps") == 12
        assert as_int(fresh, "capability_mismatch_assignments") == 0

        assert as_int(independent, "completed_jobs") == 9
        assert as_int(independent, "duplicate_claims") == 9
        assert as_int(independent, "blocked_steps") == 18
        assert as_int(independent, "communication_messages_sent") == 0

        assert as_int(delayed, "completed_jobs") == 12
        assert as_int(delayed, "makespan_steps") == 14
        assert as_int(delayed, "stale_idle_steps") == 6
        assert as_int(delayed, "assignment_rejections") == 2

        assert as_int(dropout, "completed_jobs") == 9
        assert as_float(dropout, "communication_delivery_ratio") == 0.25
        assert as_int(dropout, "stale_idle_steps") == 17

        assert as_int(shuffled, "completed_jobs") == 6
        assert as_int(shuffled, "capability_mismatch_assignments") == 6
        assert as_float(shuffled, "communication_delivery_ratio") == 1.0

        assert as_int(failure_no, "completed_jobs") == 7
        assert as_int(failure_no, "interrupted_job_recovered") == 0
        assert as_int(failure_no, "reallocation_count") == 0

        assert as_int(failure_yes, "completed_jobs") == 8
        assert as_int(failure_yes, "interrupted_job_recovered") == 1
        assert as_int(failure_yes, "reallocation_count") == 1
        assert as_int(failure_yes, "recovery_latency_steps") == 6
        assert as_int(failure_no, "interrupted_job_id") == as_int(
            failure_yes, "interrupted_job_id"
        )

        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(output / "condition_metrics.csv"),
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
            "Lab 38 smoke reference: "
            f"fresh={obs['fresh_completion']:.3f}, "
            f"independent={obs['independent_completion']:.3f}, "
            f"delayed={obs['delayed_completion']:.3f}, "
            f"dropout={obs['dropout_completion']:.3f}, "
            f"shuffled={obs['shuffled_completion']:.3f}, "
            f"recovery={obs['failure_reallocation_completion']:.3f}"
        )
        print("PASS: Lab 38 raw artifacts + independent collaboration analysis")


if __name__ == "__main__":
    main()
