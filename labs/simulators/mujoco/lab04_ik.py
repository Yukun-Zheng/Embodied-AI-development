#!/usr/bin/env python3
"""MuJoCo S-layer adapter for Lab 04 numerical IK.

The experiment uses MuJoCo's own site position and `mj_jacSite` Jacobian inside
a closed-loop Cartesian controller. It also performs a near-singularity probe
that compares an undamped Moore-Penrose pseudoinverse with damped least squares.
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

LAB_ID = "sim_mujoco_lab04_ik"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "lab04_planar3.xml"


def site_xy(model: mujoco.MjModel, data: mujoco.MjData, site_id: int) -> np.ndarray:
    return np.asarray(data.site_xpos[site_id, :2], dtype=np.float64).copy()


def site_jacobian_xy(
    model: mujoco.MjModel, data: mujoco.MjData, site_id: int
) -> np.ndarray:
    jacp = np.zeros((3, model.nv), dtype=np.float64)
    jacr = np.zeros((3, model.nv), dtype=np.float64)
    mujoco.mj_jacSite(model, data, jacp, jacr, site_id)
    return jacp[:2, :].copy()


def dls(J: np.ndarray, velocity: np.ndarray, damping: float) -> np.ndarray:
    eye = np.eye(J.shape[0], dtype=np.float64)
    return J.T @ np.linalg.solve(J @ J.T + (damping**2) * eye, velocity)


def controller_error(condition: str, error: np.ndarray) -> np.ndarray:
    if condition == "dls_correct":
        return error
    if condition == "frame_mismatch":
        # Deliberately interpret a world-frame error as if the Cartesian axes
        # were rotated +90 degrees. The target and all other controller settings
        # remain unchanged.
        bad_R = np.array([[0.0, -1.0], [1.0, 0.0]], dtype=np.float64)
        return bad_R @ error
    raise ValueError(condition)


def run_tracking(condition: str, output: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")

    data.qpos[:] = np.array([0.35, -0.65, 0.45], dtype=np.float64)
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)

    target = np.array([0.86, 0.47], dtype=np.float64)
    dt = float(model.opt.timestep)
    duration = 3.0
    steps = int(duration / dt)
    cartesian_gain = 3.0
    damping = 0.06
    velocity_limit = 3.0
    torque_gain = 5.0
    torque_limits = np.array([10.0, 8.0, 6.0], dtype=np.float64)

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition=condition,
        seed=4,
        config={
            "model": str(MODEL_PATH.relative_to(REPO_ROOT)),
            "target_xy": target.tolist(),
            "duration_s": duration,
            "dt_s": dt,
            "cartesian_gain": cartesian_gain,
            "dls_lambda": damping,
            "joint_velocity_limit": velocity_limit,
            "torque_gain": torque_gain,
            "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        },
        repo_root=REPO_ROOT,
    )

    errors: list[float] = []
    qvel_norms: list[float] = []
    torque_norms: list[float] = []
    min_sigma = math.inf
    saturated_steps = 0

    for step in range(steps):
        position = site_xy(model, data, site_id)
        error = target - position
        used_error = controller_error(condition, error)
        J = site_jacobian_xy(model, data, site_id)
        singular_values = np.linalg.svd(J, compute_uv=False)
        min_sigma = min(min_sigma, float(singular_values[-1]))

        desired_cartesian_velocity = cartesian_gain * used_error
        desired_qvel = dls(J, desired_cartesian_velocity, damping)
        qvel_norm = float(np.linalg.norm(desired_qvel))
        if qvel_norm > velocity_limit:
            desired_qvel *= velocity_limit / qvel_norm
            saturated_steps += 1

        raw_tau = torque_gain * (desired_qvel - np.asarray(data.qvel))
        tau = np.clip(raw_tau, -torque_limits, torque_limits)
        saturated_steps += int(np.any(np.abs(raw_tau) > torque_limits + 1e-12))
        data.ctrl[:] = tau

        error_norm = float(np.linalg.norm(error))
        errors.append(error_norm)
        qvel_norms.append(float(np.linalg.norm(data.qvel)))
        torque_norms.append(float(np.linalg.norm(tau)))
        recorder.log_step(
            condition=condition,
            step=step,
            time_s=float(data.time),
            ee_x=float(position[0]),
            ee_y=float(position[1]),
            target_x=float(target[0]),
            target_y=float(target[1]),
            error_x=float(error[0]),
            error_y=float(error[1]),
            error_norm=error_norm,
            used_error_x=float(used_error[0]),
            used_error_y=float(used_error[1]),
            sigma_min=float(singular_values[-1]),
            q0=float(data.qpos[0]),
            q1=float(data.qpos[1]),
            q2=float(data.qpos[2]),
            qvel_norm=float(np.linalg.norm(data.qvel)),
            desired_qvel_norm=float(np.linalg.norm(desired_qvel)),
            torque_norm=float(np.linalg.norm(tau)),
        )
        mujoco.mj_step(model, data)

    final_position = site_xy(model, data, site_id)
    final_error = float(np.linalg.norm(target - final_position))
    late = errors[int(0.8 * len(errors)) :]
    summary = {
        "condition": condition,
        "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        "initial_error": errors[0],
        "final_error": final_error,
        "late_mean_error": float(np.mean(late)),
        "min_error": float(min(errors)),
        "max_qvel_norm": float(max(qvel_norms)),
        "max_torque_norm": float(max(torque_norms)),
        "min_sigma": min_sigma,
        "saturation_events": saturated_steps,
        "finite": int(
            np.all(np.isfinite(data.qpos))
            and np.all(np.isfinite(data.qvel))
            and math.isfinite(final_error)
        ),
    }
    recorder.finalize(summary)
    return summary


def singularity_probe(output: Path) -> dict[str, Any]:
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")

    # Nearly straight configuration: the Cartesian Jacobian remains full rank,
    # but its smallest singular value is tiny.
    data.qpos[:] = np.array([0.0, 0.01, -0.01], dtype=np.float64)
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)
    J = site_jacobian_xy(model, data, site_id)
    singular_values = np.linalg.svd(J, compute_uv=False)
    request = np.array([-0.1, 0.0], dtype=np.float64)

    pinv_qvel = np.linalg.pinv(J) @ request
    dls_qvel = dls(J, request, 0.05)
    result = {
        "condition": "near_singularity_probe",
        "sigma_max": float(singular_values[0]),
        "sigma_min": float(singular_values[-1]),
        "condition_number": float(singular_values[0] / singular_values[-1]),
        "requested_vx": float(request[0]),
        "requested_vy": float(request[1]),
        "pinv_qvel_norm": float(np.linalg.norm(pinv_qvel)),
        "dls_qvel_norm": float(np.linalg.norm(dls_qvel)),
        "pinv_q0": float(pinv_qvel[0]),
        "pinv_q1": float(pinv_qvel[1]),
        "pinv_q2": float(pinv_qvel[2]),
        "dls_q0": float(dls_qvel[0]),
        "dls_q1": float(dls_qvel[1]),
        "dls_q2": float(dls_qvel[2]),
    }
    write_csv(output / "singularity_probe.csv", [result])
    return result


def run_all(output: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output.mkdir(parents=True, exist_ok=True)
    tracking = [
        run_tracking(condition, output)
        for condition in ("dls_correct", "frame_mismatch")
    ]
    probe = singularity_probe(output)
    write_csv(output / "tracking_metrics.csv", tracking)
    write_json(
        output / "experiment_summary.json",
        {"lab_id": LAB_ID, "tracking": tracking, "singularity_probe": probe},
    )
    return tracking, probe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/mujoco-lab04"))
    args = parser.parse_args()
    tracking, probe = run_all(args.output)
    print(f"MuJoCo version: {getattr(mujoco, '__version__', 'unknown')}")
    for row in tracking:
        print(
            f"{row['condition']:18s} initial={row['initial_error']:.4f} "
            f"final={row['final_error']:.4f} late={row['late_mean_error']:.4f} "
            f"max|qdot|={row['max_qvel_norm']:.3f}"
        )
    print(
        "singularity probe: "
        f"sigma_min={probe['sigma_min']:.6f} "
        f"cond={probe['condition_number']:.1f} "
        f"pinv={probe['pinv_qvel_norm']:.3f} "
        f"dls={probe['dls_qvel_norm']:.3f}"
    )


if __name__ == "__main__":
    main()
