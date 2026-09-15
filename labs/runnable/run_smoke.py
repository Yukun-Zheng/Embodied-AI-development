#!/usr/bin/env python3
"""CPU smoke tests for executable textbook labs.

The smoke suite validates scientific plumbing and mechanism interventions, not
benchmark performance. Heavy simulator/GPU labs will later register lightweight
dry-run checks here.
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
LAB29_DIR = ROOT / "labs" / "runnable" / "lab29_world_model_mpc"
LAB29 = LAB29_DIR / "run.py"
LAB29_HORIZON = LAB29_DIR / "horizon_probe.py"
LAB29_ANALYZE = LAB29_DIR / "analyze.py"


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

    for latency in [0.1, 0.25]:
        queue_age = as_float(keyed[(latency, "async_queue")], "p95_action_age_s")
        rebase_age = as_float(keyed[(latency, "async_rebase")], "p95_action_age_s")
        assert rebase_age + 0.04 < queue_age, (
            f"Latency-aware rebase did not materially reduce p95 action age at {latency}s: "
            f"queue={queue_age:.4f}, rebase={rebase_age:.4f}"
        )

    queue_zero = as_float(keyed[(0.0, "async_queue")], "p95_action_age_s")
    rebase_zero = as_float(keyed[(0.0, "async_rebase")], "p95_action_age_s")
    assert abs(queue_zero - rebase_zero) <= 1e-9, (
        f"Zero-latency negative control failed: queue={queue_zero}, rebase={rebase_zero}"
    )

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
    assert analysis["task_performance_improvement_not_guaranteed"] is True

    print(
        "PASS lab22_async_execution: raw logs, manifests, latency intervention "
        "and derived mechanism analysis verified"
    )


def test_lab29(tmp: Path) -> None:
    output = tmp / "lab29"
    subprocess.run(
        [sys.executable, str(LAB29), "--quick", "--output", str(output)],
        cwd=ROOT,
        check=True,
    )

    metrics_path = output / "model_metrics.csv"
    manifest_path = output / "experiment_manifest.json"
    models_path = output / "models.json"
    for path in [metrics_path, manifest_path, models_path]:
        assert path.is_file(), f"Lab 29 missing {path.name}"

    rows = read_rows(metrics_path)
    assert len(rows) == 3, f"Expected 3 world-model conditions, got {len(rows)}"
    keyed = {row["model"]: row for row in rows}
    assert set(keyed) == {"action_aware", "action_blind", "wrong_action_sign"}

    for row in rows:
        for metric in [
            "one_step_rmse",
            "counterfactual_sensitivity_error",
            "closed_loop_position_rmse",
            "final_position_error",
            "realized_control_cost",
        ]:
            as_float(row, metric)
        run_dir = output / row["run_dir"]
        for required in ["manifest.json", "steps.csv", "failures.jsonl", "summary.json"]:
            assert (run_dir / required).is_file(), f"Lab 29 missing {required} for {row['model']}"

    aware = keyed["action_aware"]
    blind = keyed["action_blind"]
    wrong = keyed["wrong_action_sign"]

    # Observational prediction can look numerically good even when the causal
    # action interface is unusable for planning.
    assert as_float(blind, "one_step_rmse") < 0.005
    assert as_float(wrong, "one_step_rmse") < 0.01
    assert as_float(aware, "counterfactual_sensitivity_error") < 0.01
    assert as_float(blind, "counterfactual_sensitivity_error") > 0.10
    assert as_float(wrong, "counterfactual_sensitivity_error") > 0.20

    # Closed-loop falsification: only the action-aware model should reach the
    # target under the same MPC search and receding-horizon feedback.
    assert as_float(aware, "final_position_error") < 0.10
    assert as_float(blind, "final_position_error") > 0.80
    assert as_float(wrong, "final_position_error") > 2.0

    # The second layer makes model bias an explicit independent variable and
    # asks whether longer imagined rollouts compound that bias.
    subprocess.run(
        [sys.executable, str(LAB29_HORIZON), "--quick", "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    horizon_path = output / "horizon_sweep.csv"
    horizon_manifest = output / "horizon_probe_manifest.json"
    assert horizon_path.is_file(), "Lab 29 horizon probe did not write horizon_sweep.csv"
    assert horizon_manifest.is_file(), "Lab 29 horizon probe did not write its manifest"

    horizon_rows = read_rows(horizon_path)
    assert [int(row["planning_horizon"]) for row in horizon_rows] == [1, 4, 16, 32]
    for row in horizon_rows:
        for metric in [
            "rollout_prediction_rmse",
            "terminal_prediction_rmse",
            "realized_control_cost",
            "final_position_error",
        ]:
            as_float(row, metric)

    first_terminal = as_float(horizon_rows[0], "terminal_prediction_rmse")
    last_terminal = as_float(horizon_rows[-1], "terminal_prediction_rmse")
    assert last_terminal > 3.0 * first_terminal, (
        "Injected action-gain bias did not compound over the planning horizon: "
        f"h1={first_terminal:.4f}, h32={last_terminal:.4f}"
    )

    costs = [as_float(row, "realized_control_cost") for row in horizon_rows]
    assert costs[-1] > 1.15 * min(costs), (
        "Longest biased planning horizon did not become measurably worse than an intermediate horizon: "
        f"costs={costs}"
    )

    subprocess.run(
        [sys.executable, str(LAB29_ANALYZE), str(output)],
        cwd=ROOT,
        check=True,
    )
    analysis_json = output / "analysis.json"
    analysis_md = output / "ANALYSIS.md"
    assert analysis_json.is_file(), "Lab 29 analyzer did not write analysis.json"
    assert analysis_md.is_file(), "Lab 29 analyzer did not write ANALYSIS.md"
    with analysis_json.open("r", encoding="utf-8") as handle:
        analysis = json.load(handle)
    assert analysis["observational_prediction_is_insufficient"] is True
    assert analysis["counterfactual_direction_matters"] is True
    assert analysis["horizon_prediction_error_accumulates"] is True
    assert analysis["long_horizon_control_not_monotonic"] is True

    print(
        "PASS lab29_world_model_mpc: passive prediction, counterfactual action sensitivity, "
        "closed-loop utility and horizon-dependent model-bias amplification were separated"
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-runnable-labs-") as tmpdir:
        tmp = Path(tmpdir)
        test_lab22(tmp)
        test_lab29(tmp)
    print("RUNNABLE LAB SMOKE PASSED")


if __name__ == "__main__":
    main()
