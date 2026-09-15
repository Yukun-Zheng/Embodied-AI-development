#!/usr/bin/env python3
"""MuJoCo S-layer adapter for Lab 06 feedback control.

This is intentionally small: a 1-DOF slider with real MuJoCo integration,
actuator saturation, joint limits and an injected external disturbance. The goal
is to verify that the M-layer feedback claim survives a physics-engine boundary.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import mujoco

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, write_csv, write_json  # noqa: E402

LAB_ID = "sim_mujoco_lab06_control"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "lab06_slider.xml"


def controller(condition: str, target: float, q: float, qd: float) -> float:
    kp = 20.0
    kd = 7.0
    error = target - q
    if condition == "no_feedback":
        return 0.0
    if condition == "pd_feedback":
        return kp * error - kd * qd
    if condition == "wrong_sign_feedback":
        return -kp * error + kd * qd
    raise ValueError(condition)


def run_condition(condition: str, output: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    dt = float(model.opt.timestep)
    target = 1.0
    duration = 2.5
    steps = int(duration / dt)
    disturbance_start = 0.80
    disturbance_end = 0.95
    disturbance_force = -8.0
    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "mass_body")

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition=condition,
        seed=6,
        config={
            "model": str(MODEL_PATH.relative_to(REPO_ROOT)),
            "target": target,
            "duration_s": duration,
            "dt_s": dt,
            "disturbance_start_s": disturbance_start,
            "disturbance_end_s": disturbance_end,
            "disturbance_force_n": disturbance_force,
            "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        },
        repo_root=REPO_ROOT,
    )

    trajectory: list[dict[str, Any]] = []
    control_energy = 0.0
    saturated = 0
    disturbance_end_error: float | None = None
    pre_disturbance_error: float | None = None
    peak_abs_position = 0.0

    for step in range(steps):
        time_s = float(data.time)
        q = float(data.qpos[0])
        qd = float(data.qvel[0])
        raw_u = controller(condition, target, q, qd)
        u = max(-20.0, min(20.0, raw_u))
        saturated += int(abs(raw_u) > 20.0)
        data.ctrl[0] = u

        disturbance = (
            disturbance_force
            if disturbance_start <= time_s < disturbance_end
            else 0.0
        )
        data.xfrc_applied[:, :] = 0.0
        data.xfrc_applied[body_id, 0] = disturbance

        error = target - q
        if pre_disturbance_error is None and time_s >= disturbance_start:
            pre_disturbance_error = abs(error)
        if disturbance_end_error is None and time_s >= disturbance_end:
            disturbance_end_error = abs(error)

        row = {
            "condition": condition,
            "step": step,
            "time_s": time_s,
            "q": q,
            "qd": qd,
            "target": target,
            "error": error,
            "raw_ctrl": raw_u,
            "ctrl": u,
            "disturbance_force": disturbance,
        }
        trajectory.append(row)
        recorder.log_step(**row)
        control_energy += u * u * dt
        peak_abs_position = max(peak_abs_position, abs(q))

        mujoco.mj_step(model, data)

    final_q = float(data.qpos[0])
    final_qd = float(data.qvel[0])
    final_error = abs(target - final_q)
    disturbance_end_error = disturbance_end_error if disturbance_end_error is not None else math.nan
    pre_disturbance_error = pre_disturbance_error if pre_disturbance_error is not None else math.nan

    post_window = [
        abs(float(row["error"]))
        for row in trajectory
        if float(row["time_s"]) >= 1.50
    ]
    late_mean_error = sum(post_window) / len(post_window)

    summary = {
        "condition": condition,
        "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        "final_q": final_q,
        "final_qd": final_qd,
        "final_error": final_error,
        "pre_disturbance_error": pre_disturbance_error,
        "disturbance_end_error": disturbance_end_error,
        "late_mean_error": late_mean_error,
        "control_energy": control_energy,
        "saturation_fraction": saturated / steps,
        "peak_abs_position": peak_abs_position,
        "finite": int(
            all(
                math.isfinite(value)
                for value in (
                    final_q,
                    final_qd,
                    final_error,
                    control_energy,
                    late_mean_error,
                )
            )
        ),
    }
    recorder.finalize(summary)
    return summary


def run_all(output: Path) -> list[dict[str, Any]]:
    output.mkdir(parents=True, exist_ok=True)
    summaries = [
        run_condition(condition, output)
        for condition in ("no_feedback", "pd_feedback", "wrong_sign_feedback")
    ]
    write_csv(output / "condition_metrics.csv", summaries)
    write_json(
        output / "experiment_summary.json",
        {"lab_id": LAB_ID, "conditions": summaries},
    )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/mujoco-lab06"))
    args = parser.parse_args()
    summaries = run_all(args.output)
    print(f"MuJoCo version: {getattr(mujoco, '__version__', 'unknown')}")
    for row in summaries:
        print(
            f"{row['condition']:20s} final-error={row['final_error']:.4f} "
            f"late-mean={row['late_mean_error']:.4f} "
            f"sat={row['saturation_fraction']:.3f} "
            f"peak|q|={row['peak_abs_position']:.3f}"
        )
    print(f"metrics: {args.output / 'condition_metrics.csv'}")


if __name__ == "__main__":
    main()
