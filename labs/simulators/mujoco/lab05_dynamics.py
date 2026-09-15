#!/usr/bin/env python3
"""MuJoCo S-layer adapter for Lab 05 rigid-body dynamics.

For several nontrivial q / qdot / generalized-force states, the script rebuilds
MuJoCo forward acceleration from the engine's mass matrix, bias force, passive
force and applied generalized force:

    M(q) qdd = qfrc_applied + qfrc_passive + qfrc_actuator - qfrc_bias

It then injects two model errors while holding the physical state/force fixed:
- wrong_mass_scale: use 0.6 * M;
- omit_passive: omit qfrc_passive (joint damping).
"""

from __future__ import annotations

import argparse
import json
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

LAB_ID = "sim_mujoco_lab05_dynamics"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "lab04_planar3.xml"

PROBES = [
    ([0.30, -0.60, 0.40], [1.20, -0.80, 0.50], [1.00, -0.50, 0.30]),
    ([1.00, -1.20, 0.70], [-1.50, 1.00, -0.70], [2.00, -1.00, 0.40]),
    ([-0.80, 0.50, -0.40], [2.00, -1.20, 0.90], [-1.50, 0.80, -0.60]),
    ([0.20, 0.30, -0.90], [-2.50, 0.60, 1.40], [0.50, 1.20, -0.80]),
    ([1.50, -0.50, 0.20], [1.80, 1.10, -1.30], [-2.00, 0.60, 1.00]),
]


def full_mass_matrix(model: mujoco.MjModel, data: mujoco.MjData) -> np.ndarray:
    """Expand MuJoCo's packed joint-space inertia across binding versions.

    The C/API documentation traditionally calls this packed field `qM`; the
    current 3.13 Python wheel used by hosted CI exposes it as `M`. Supporting
    both keeps the textbook adapter compatible across MuJoCo 3.x bindings.
    """
    M = np.zeros((model.nv, model.nv), dtype=np.float64)
    packed = getattr(data, "qM", None)
    if packed is None:
        packed = data.M
    mujoco.mj_fullM(model, M, packed)
    return M


def predict_acceleration(
    M: np.ndarray,
    applied: np.ndarray,
    actuator: np.ndarray,
    passive: np.ndarray,
    bias: np.ndarray,
) -> np.ndarray:
    rhs = applied + actuator + passive - bias
    return np.linalg.solve(M, rhs)


def run_experiment(output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output.mkdir(parents=True, exist_ok=True)
    model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
    data = mujoco.MjData(model)

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition="dynamics_identity",
        seed=5,
        config={
            "model": str(MODEL_PATH.relative_to(REPO_ROOT)),
            "probe_count": len(PROBES),
            "wrong_mass_scale": 0.6,
            "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        },
        repo_root=REPO_ROOT,
    )

    variants = ("matched", "wrong_mass_scale", "omit_passive")
    errors: dict[str, list[float]] = {name: [] for name in variants}
    truth_values: list[float] = []
    rows: list[dict[str, Any]] = []
    residuals: list[float] = []
    symmetry_errors: list[float] = []
    min_eigenvalues: list[float] = []

    for probe_id, (q, qd, tau) in enumerate(PROBES):
        data.qpos[:] = np.asarray(q, dtype=np.float64)
        data.qvel[:] = np.asarray(qd, dtype=np.float64)
        data.ctrl[:] = 0.0
        data.qfrc_applied[:] = np.asarray(tau, dtype=np.float64)
        mujoco.mj_forward(model, data)

        M = full_mass_matrix(model, data)
        applied = np.asarray(data.qfrc_applied, dtype=np.float64).copy()
        actuator = np.asarray(data.qfrc_actuator, dtype=np.float64).copy()
        passive = np.asarray(data.qfrc_passive, dtype=np.float64).copy()
        bias = np.asarray(data.qfrc_bias, dtype=np.float64).copy()
        truth = np.asarray(data.qacc, dtype=np.float64).copy()

        matched = predict_acceleration(M, applied, actuator, passive, bias)
        wrong_mass = predict_acceleration(0.6 * M, applied, actuator, passive, bias)
        no_passive = predict_acceleration(
            M,
            applied,
            actuator,
            np.zeros_like(passive),
            bias,
        )
        predictions = {
            "matched": matched,
            "wrong_mass_scale": wrong_mass,
            "omit_passive": no_passive,
        }

        rhs = applied + actuator + passive - bias
        residual = float(np.linalg.norm(M @ truth - rhs))
        residuals.append(residual)
        symmetry_error = float(np.max(np.abs(M - M.T)))
        symmetry_errors.append(symmetry_error)
        eig_min = float(np.min(np.linalg.eigvalsh(0.5 * (M + M.T))))
        min_eigenvalues.append(eig_min)

        for joint in range(model.nv):
            truth_values.append(float(truth[joint]))
            for name, prediction in predictions.items():
                err = float(prediction[joint] - truth[joint])
                errors[name].append(err)
                row = {
                    "probe_id": probe_id,
                    "joint": joint,
                    "variant": name,
                    "q": float(data.qpos[joint]),
                    "qvel": float(data.qvel[joint]),
                    "applied_force": float(applied[joint]),
                    "passive_force": float(passive[joint]),
                    "bias_force": float(bias[joint]),
                    "truth_qacc": float(truth[joint]),
                    "predicted_qacc": float(prediction[joint]),
                    "error": err,
                    "mass_matrix_symmetry_error": symmetry_error,
                    "mass_matrix_min_eigenvalue": eig_min,
                    "dynamics_residual_norm": residual,
                }
                rows.append(row)
                recorder.log_step(**row)

    truth_rms = float(np.sqrt(np.mean(np.square(truth_values))))
    metrics: list[dict[str, Any]] = []
    for name in variants:
        values = np.asarray(errors[name], dtype=np.float64)
        rmse = float(np.sqrt(np.mean(values**2)))
        metrics.append(
            {
                "variant": name,
                "rmse": rmse,
                "relative_rmse": rmse / max(truth_rms, 1e-12),
                "max_abs_error": float(np.max(np.abs(values))),
                "truth_rms": truth_rms,
                "mean_dynamics_residual": float(np.mean(residuals)),
                "max_mass_matrix_symmetry_error": float(max(symmetry_errors)),
                "min_mass_matrix_eigenvalue": float(min(min_eigenvalues)),
                "finite": int(np.all(np.isfinite(values))),
            }
        )

    write_csv(output / "probe_rows.csv", rows)
    write_csv(output / "model_metrics.csv", metrics)
    summary = {
        "lab_id": LAB_ID,
        "mujoco_version": getattr(mujoco, "__version__", "unknown"),
        "metrics": metrics,
    }
    write_json(output / "experiment_summary.json", summary)
    recorder.finalize(summary)
    return metrics, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("/tmp/mujoco-lab05"))
    args = parser.parse_args()
    metrics, _ = run_experiment(args.output)
    print(f"MuJoCo version: {getattr(mujoco, '__version__', 'unknown')}")
    for row in metrics:
        print(
            f"{row['variant']:18s} rmse={row['rmse']:.8f} "
            f"rel-rmse={row['relative_rmse']:.5f} "
            f"max-error={row['max_abs_error']:.6f}"
        )
    print(
        "mass-matrix checks: "
        f"symmetry={metrics[0]['max_mass_matrix_symmetry_error']:.3e} "
        f"lambda_min={metrics[0]['min_mass_matrix_eigenvalue']:.6f} "
        f"residual={metrics[0]['mean_dynamics_residual']:.3e}"
    )


if __name__ == "__main__":
    main()
