"""Planar 3R arm: FK, Jacobian, DLS IK, null-space objective.

Run:
    python code/minimal/planar_arm.py

This is the smallest executable mirror of Parts 8-10 and DERIVATIONS D1-D3/D6.
"""

from __future__ import annotations

import numpy as np


def fk(q: np.ndarray, lengths: np.ndarray) -> np.ndarray:
    """End-effector [x, y, theta] for an n-link planar revolute arm."""
    q = np.asarray(q, dtype=float)
    lengths = np.asarray(lengths, dtype=float)
    assert q.shape == lengths.shape

    angles = np.cumsum(q)
    x = np.sum(lengths * np.cos(angles))
    y = np.sum(lengths * np.sin(angles))
    theta = np.sum(q)
    return np.array([x, y, theta])


def jacobian(q: np.ndarray, lengths: np.ndarray) -> np.ndarray:
    """Analytic Jacobian for [x, y, theta] wrt q. Shape [3, n]."""
    q = np.asarray(q, dtype=float)
    lengths = np.asarray(lengths, dtype=float)
    n = len(q)
    angles = np.cumsum(q)

    J = np.zeros((3, n))
    for j in range(n):
        # Joint j affects all links k >= j.
        J[0, j] = -np.sum(lengths[j:] * np.sin(angles[j:]))
        J[1, j] = np.sum(lengths[j:] * np.cos(angles[j:]))
        J[2, j] = 1.0
    return J


def numerical_jacobian(q: np.ndarray, lengths: np.ndarray, eps: float = 1e-7) -> np.ndarray:
    y0 = fk(q, lengths)
    J = np.zeros((3, len(q)))
    for j in range(len(q)):
        qp = q.copy()
        qp[j] += eps
        J[:, j] = (fk(qp, lengths) - y0) / eps
    return J


def dls_step(J: np.ndarray, error: np.ndarray, damping: float) -> np.ndarray:
    """Damped least-squares task-space inverse.

    dq = J^T (J J^T + lambda^2 I)^-1 e
    """
    m = J.shape[0]
    A = J @ J.T + (damping**2) * np.eye(m)
    return J.T @ np.linalg.solve(A, error)


def joint_center_cost(q: np.ndarray, q_min: np.ndarray, q_max: np.ndarray) -> tuple[float, np.ndarray]:
    """Quadratic cost and gradient that prefer the middle of joint ranges."""
    mid = 0.5 * (q_min + q_max)
    half = 0.5 * (q_max - q_min)
    z = (q - mid) / half
    cost = 0.5 * np.sum(z**2)
    grad = z / half
    return float(cost), grad


def wrap_angle(a: float) -> float:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def pose_error(target: np.ndarray, current: np.ndarray) -> np.ndarray:
    e = np.asarray(target, dtype=float) - np.asarray(current, dtype=float)
    e[2] = wrap_angle(e[2])
    return e


def solve_ik(
    q0: np.ndarray,
    target: np.ndarray,
    lengths: np.ndarray,
    q_min: np.ndarray,
    q_max: np.ndarray,
    *,
    damping: float = 0.05,
    step_size: float = 0.6,
    null_gain: float = 0.03,
    max_steps: int = 400,
    tol: float = 1e-5,
) -> tuple[np.ndarray, list[float]]:
    q = np.asarray(q0, dtype=float).copy()
    history: list[float] = []

    for _ in range(max_steps):
        current = fk(q, lengths)
        e = pose_error(target, current)
        err = float(np.linalg.norm(e))
        history.append(err)
        if err < tol:
            break

        J = jacobian(q, lengths)
        dq_primary = dls_step(J, e, damping)

        # DLS analogue of J^+ for the null-space projector.
        m = J.shape[0]
        J_pinv_dls = J.T @ np.linalg.solve(J @ J.T + damping**2 * np.eye(m), np.eye(m))
        N = np.eye(len(q)) - J_pinv_dls @ J

        _, grad_center = joint_center_cost(q, q_min, q_max)
        dq_secondary = -null_gain * (N @ grad_center)

        q += step_size * dq_primary + dq_secondary
        q = np.clip(q, q_min, q_max)

    return q, history


def self_test() -> None:
    lengths = np.array([0.6, 0.45, 0.30])
    q_min = np.deg2rad(np.array([-170.0, -150.0, -150.0]))
    q_max = np.deg2rad(np.array([170.0, 150.0, 150.0]))

    print("[1] Analytic vs numerical Jacobian")
    q = np.array([0.2, -0.6, 0.7])
    Ja = jacobian(q, lengths)
    Jn = numerical_jacobian(q, lengths)
    print("analytic J:\n", Ja)
    print("numerical J:\n", Jn)
    np.testing.assert_allclose(Ja, Jn, atol=2e-6)

    print("[2] DLS IK")
    target = np.array([0.75, 0.55, 0.4])
    q_sol, hist = solve_ik(
        q0=np.array([0.1, 0.1, 0.1]),
        target=target,
        lengths=lengths,
        q_min=q_min,
        q_max=q_max,
    )
    achieved = fk(q_sol, lengths)
    print("target:  ", target)
    print("achieved:", achieved)
    print("q deg:   ", np.rad2deg(q_sol))
    print("steps:   ", len(hist), "final error:", hist[-1])
    assert np.linalg.norm(pose_error(target, achieved)) < 2e-3

    print("[3] Near-singularity counterexample")
    q_sing = np.zeros(3)  # arm fully stretched
    J = jacobian(q_sing, lengths)
    singular_values = np.linalg.svd(J, compute_uv=False)
    print("singular values:", singular_values)

    e = np.array([0.0, 0.02, 0.0])
    dq_dls = dls_step(J, e, damping=0.1)
    print("DLS dq:", dq_dls, "norm:", np.linalg.norm(dq_dls))

    # An undamped inverse is ill-conditioned around singular configurations.
    dq_pinv = np.linalg.pinv(J, rcond=1e-12) @ e
    print("pinv dq:", dq_pinv, "norm:", np.linalg.norm(dq_pinv))

    print("All planar-arm tests passed.")


if __name__ == "__main__":
    self_test()
