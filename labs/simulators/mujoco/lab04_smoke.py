#!/usr/bin/env python3
"""Headless MuJoCo smoke test for Lab 04 numerical IK."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "lab04_ik.py"


def read_rows(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row[key]: row for row in csv.DictReader(handle)}


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-mujoco-lab04-") as tmp:
        output = Path(tmp) / "lab04"
        subprocess.run(
            [sys.executable, str(RUN), "--output", str(output)],
            check=True,
        )

        tracking_path = output / "tracking_metrics.csv"
        probe_path = output / "singularity_probe.csv"
        summary_path = output / "experiment_summary.json"
        for path in (tracking_path, probe_path, summary_path):
            if not path.is_file() or path.stat().st_size == 0:
                raise AssertionError(f"Missing or empty MuJoCo Lab 04 artifact: {path}")

        tracking = read_rows(tracking_path, "condition")
        if set(tracking) != {"dls_correct", "frame_mismatch"}:
            raise AssertionError(f"Unexpected tracking conditions: {sorted(tracking)}")
        dls = tracking["dls_correct"]
        bad = tracking["frame_mismatch"]

        for row in tracking.values():
            if int(float(row["finite"])) != 1:
                raise AssertionError("Non-finite MuJoCo IK rollout")
            for key in (
                "initial_error",
                "final_error",
                "late_mean_error",
                "max_qvel_norm",
                "max_torque_norm",
                "min_sigma",
            ):
                if not math.isfinite(f(row, key)):
                    raise AssertionError(f"Non-finite tracking metric: {key}")

        if f(dls, "final_error") >= 0.08:
            raise AssertionError("DLS controller did not reach the Cartesian target")
        if f(dls, "late_mean_error") >= 0.10:
            raise AssertionError("DLS controller did not remain near the target")
        if f(dls, "final_error") >= 0.20 * f(dls, "initial_error"):
            raise AssertionError("DLS did not substantially reduce task-space error")
        if f(bad, "final_error") <= max(0.20, 3.0 * f(dls, "final_error")):
            raise AssertionError("Frame-mismatch negative control did not degrade tracking")

        with probe_path.open("r", encoding="utf-8", newline="") as handle:
            probe = next(csv.DictReader(handle))
        sigma_min = f(probe, "sigma_min")
        pinv_norm = f(probe, "pinv_qvel_norm")
        dls_norm = f(probe, "dls_qvel_norm")
        condition_number = f(probe, "condition_number")

        if sigma_min >= 0.01:
            raise AssertionError("Near-singularity probe is no longer near singular")
        if condition_number <= 100.0:
            raise AssertionError("Near-singularity Jacobian condition number is too small")
        if pinv_norm <= 10.0:
            raise AssertionError("Undamped pseudoinverse no longer exposes velocity amplification")
        if dls_norm >= 1.0:
            raise AssertionError("DLS did not regularize the singular velocity request")
        if pinv_norm <= 20.0 * dls_norm:
            raise AssertionError("DLS and pseudoinverse are no longer clearly separated")

        run_dirs = sorted((output / "runs").glob("*"))
        if len(run_dirs) != 2:
            raise AssertionError(f"Expected two IK rollout directories, got {len(run_dirs)}")
        for run_dir in run_dirs:
            for name in ("manifest.json", "steps.csv", "failures.jsonl", "summary.json"):
                if not (run_dir / name).is_file():
                    raise AssertionError(f"Missing IK simulator artifact: {run_dir / name}")

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary.get("lab_id") != "sim_mujoco_lab04_ik":
            raise AssertionError("Unexpected Lab 04 summary lab_id")

        print(
            "MuJoCo Lab 04 smoke: "
            f"DLS final={f(dls, 'final_error'):.4f}, "
            f"frame-mismatch final={f(bad, 'final_error'):.4f}; "
            f"sigma_min={sigma_min:.6f}, pinv={pinv_norm:.3f}, dls={dls_norm:.3f}"
        )
        print("PASS: MuJoCo Lab 04 Jacobian/DLS tracking + singularity controls")


if __name__ == "__main__":
    main()
