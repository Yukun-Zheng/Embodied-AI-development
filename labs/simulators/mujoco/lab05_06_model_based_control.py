#!/usr/bin/env python3
"""Cross-layer MuJoCo experiment: Lab 05 dynamics -> Lab 06 control.

All conditions track the same smooth 3-joint trajectory in the same MuJoCo arm
and receive the same generalized-force disturbance. The only controlled change
is the controller's dynamics assumption:

- computed_torque_matched: true M, bias and passive forces;
- computed_torque_wrong_mass: 0.6 * M with correct bias/passive terms;
- computed_torque_omit_passive: true M/bias but no passive-force cancellation;
- plain_pd: no dynamics feedforward.

This turns a model-error metric into a physical closed-loop consequence.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import mujoco
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, write_csv, write_json  # noqa: E402

LAB_ID = "sim_mujoco_lab05_06_model_based_control"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "lab04_planar3.xml"


def full_mass_matrix(model: mujoco.MjModel, data: mujoco.MjData) -> np.ndarray:
    M = np.zeros((model.nv, model.nv), dtype=np.float64)
    try:
        mujoco.mj_fullM(model, data, M)
        return M
    except TypeError:
        packed = getattr(data, "qM", None)
        if packed is None:
            packed = data.M
        mujoco.mj_fullM(model, M, packed)
        return M


def desired_state(t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    offset = np.array([0.20, -0.35, 0.25], dtype=np.float64)
    amplitude = np.array([0.55, 0.45, 0.35], dtype=np.float64)
    omega = np.array([1.20, 1.00, 1.35], dtype=np.float64)
    phase = np.array([0.0, 0.6, -0.4], dtype=np.float64)
    angle = omega * t + phase
    q = offset + amplitude * np.sin(angle)
    qd = amplitude * omega * np.cos(angle)
    qdd = -amplitude * (omega**2) * np.sin(angle)
    return q, qd, qdd


def compute_control(
    condition: str,
    *,
    M: np.ndarray,
    bias: np.ndarray,
    passive: np.ndarray,
    q: np.ndarray,
    qd: np.ndarray,
    q_des: np.ndarray,
    qd_des: np.ndarray,
    qdd_des: np.ndarray,
) -> np.ndarray:
    kp = 28.0
    kd = 11.0
    acc_cmd = qdd_des + kp * (q_des - q) + kd * (qd_des - qd)

    if condition == "computed_torque_matched":
        return M @ acc_cmd + bias - passive
    if condition == "computed_torque_wrong_mass":
        return (0.6 * M) @ acc_cmd + bias - passive
    if condition == "computed_torque_omit_passive":
        return M @ acc_cmd + bias
    if condition == "plain_pd":
        return kp * (q_des - q) + kd * (qd_des - qd)
    raise ValueError(condition)


def run_condition(condition: str, output: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    q0, qd0, _ = desired_state(0.0)
    data.qpos[:] = q0
    data.qvel[:] = qd0
    mujoco.mj_forward(model, data)

    dt = float(model.opt.timestep)
    duration = 5.0
    steps = int(duration / dt)
    torque_limits = np.array([10.0, 8.0, 6.0], dtype=np.float64)
    disturbance_start = 2.00
    disturbance_end = 2.18
    disturbance = np.array([-2.5, 1.7, -1.2], dtype=np.float64)

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition=condition,
        seed=506,
        config={
            "model": str(MODEL_PATH.relative_to(REPO_ROOT)),
            "duration_s": duration,
            "dt_s": dt,
            "disturbance_start_s": disturbance_start,
            "disturbance_end_s": disturbance_end,
            "disturbance_generalized_force": disturbance.tolist(),
            "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        },
        repo_root=REPO_ROOT,
    )

    squared_position_error = 0.0
    squared_velocity_error = 0.0
    control_energy = 0.0
    saturated_steps = 0
    max_error = 0.0
    post_disturbance_errors: list[float] = []
    disturbance_end_error: float | None = None

    for step in range(steps):
        t = float(data.time)
        q = np.asarray(data.qpos, dtype=np.float64).copy()
        qd = np.asarray(data.qvel, dtype=np.float64).copy()
        q_des, qd_des, qdd_des = desired_state(t)

        # Refresh MuJoCo force terms at the current state before building the
        # model-based controller.
        data.ctrl[:] = 0.0
        data.qfrc_applied[:] = 0.0
        mujoco.mj_forward(model, data)
        M = full_mass_matrix(model, data)
        bias = np.asarray(data.qfrc_bias, dtype=np.float64).copy()
        passive = np.asarray(data.qfrc_passive, dtype=np.float64).copy()

        raw_tau = compute_control(
            condition,
            M=M,
            bias=bias,
            passive=passive,
            q=q,
            qd=qd,
            q_des=q_des,
            qd_des=qd_des,
            qdd_des=qdd_des,
        )
        tau = np.clip(raw_tau, -torque_limits, torque_limits)
        saturated = bool(np.any(np.abs(raw_tau) > torque_limits + 1e-12))
        saturated_steps += int(saturated)
        data.ctrl[:] = tau

        if disturbance_start <= t < disturbance_end:
            data.qfrc_applied[:] = disturbance
        else:
            data.qfrc_applied[:] = 0.0

        position_error = q_des - q
        velocity_error = qd_des - qd
        error_norm = float(np.linalg.norm(position_error))
        squared_position_error += float(position_error @ position_error)
        squared_velocity_error += float(velocity_error @ velocity_error)
        control_energy += float(tau @ tau) * dt
        max_error = max(max_error, error_norm)

        if disturbance_end_error is None and t >= disturbance_end:
            disturbance_end_error = error_norm
        if t >= 2.80:
            post_disturbance_errors.append(error_norm)

        recorder.log_step(
            condition=condition,
            step=step,
            time_s=t,
            q0=float(q[0]),
            q1=float(q[1]),
            q2=float(q[2]),
            qd0=float(qd[0]),
            qd1=float(qd[1]),
            qd2=float(qd[2]),
            q_des0=float(q_des[0]),
            q_des1=float(q_des[1]),
            q_des2=float(q_des[2]),
            position_error_norm=error_norm,
            velocity_error_norm=float(np.linalg.norm(velocity_error)),
            raw_torque_norm=float(np.linalg.norm(raw_tau)),
            torque_norm=float(np.linalg.norm(tau)),
            saturated=int(saturated),
            disturbance=int(disturbance_start <= t < disturbance_end),
        )
        mujoco.mj_step(model, data)

    position_rmse = math.sqrt(squared_position_error / (steps * model.nq))
    velocity_rmse = math.sqrt(squared_velocity_error / (steps * model.nv))
    late_mean_error = float(np.mean(post_disturbance_errors))
    summary = {
        "condition": condition,
        "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        "position_rmse": position_rmse,
        "velocity_rmse": velocity_rmse,
        "max_position_error_norm": max_error,
        "disturbance_end_error_norm": (
            float(disturbance_end_error) if disturbance_end_error is not None else math.nan
        ),
        "late_mean_error_norm": late_mean_error,
        "control_energy": control_energy,
        "saturation_fraction": saturated_steps / steps,
        "finite": int(np.all(np.isfinite(data.qpos)) and np.all(np.isfinite(data.qvel))),
    }
    recorder.finalize(summary)
    return summary


def run_all(output: Path) -> list[dict[str, Any]]:
    output.mkdir(parents=True, exist_ok=True)
    conditions = (
        "computed_torque_matched",
        "computed_torque_wrong_mass",
        "computed_torque_omit_passive",
        "plain_pd",
    )
    summaries = [run_condition(condition, output) for condition in conditions]
    write_csv(output / "condition_metrics.csv", summaries)
    write_json(output / "experiment_summary.json", {"lab_id": LAB_ID, "conditions": summaries})
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/mujoco-lab05-06"))
    args = parser.parse_args()
    summaries = run_all(args.output)
    print(f"MuJoCo version: {getattr(mujoco, '__version__', 'unknown')}")
    for row in summaries:
        print(
            f"{row['condition']:30s} pos-rmse={row['position_rmse']:.4f} "
            f"late={row['late_mean_error_norm']:.4f} "
            f"energy={row['control_energy']:.2f} sat={row['saturation_fraction']:.3f}"
        )


if __name__ == "__main__":
    main()
