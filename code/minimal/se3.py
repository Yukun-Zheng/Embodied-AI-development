"""Minimal SO(3)/SE(3) implementation for the textbook.

Run:
    python code/minimal/se3.py

The point is not to replace scipy.spatial.transform. The point is to make the
matrix objects in Part 7 / DERIVATIONS D4-D5 explicit and numerically testable.
"""

from __future__ import annotations

import numpy as np

EPS = 1e-12


def hat(w: np.ndarray) -> np.ndarray:
    """R^3 -> so(3)."""
    w = np.asarray(w, dtype=float).reshape(3)
    wx, wy, wz = w
    return np.array(
        [
            [0.0, -wz, wy],
            [wz, 0.0, -wx],
            [-wy, wx, 0.0],
        ]
    )


def vee(W: np.ndarray) -> np.ndarray:
    """so(3) -> R^3."""
    W = np.asarray(W, dtype=float).reshape(3, 3)
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def so3_exp(phi: np.ndarray) -> np.ndarray:
    """Exponential map: rotation vector phi -> R in SO(3).

    phi = axis * angle, shape [3].
    """
    phi = np.asarray(phi, dtype=float).reshape(3)
    theta = np.linalg.norm(phi)

    if theta < 1e-8:
        # First terms of exp([phi]x); better behaved than dividing by tiny theta.
        P = hat(phi)
        return np.eye(3) + P + 0.5 * (P @ P)

    axis = phi / theta
    K = hat(axis)
    return np.eye(3) + np.sin(theta) * K + (1.0 - np.cos(theta)) * (K @ K)


def so3_log(R: np.ndarray) -> np.ndarray:
    """Log map: R in SO(3) -> rotation vector phi in R^3.

    This educational implementation handles ordinary rotations and small angles.
    Near pi, production libraries need extra numerical care.
    """
    R = np.asarray(R, dtype=float).reshape(3, 3)
    cos_theta = np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0)
    theta = float(np.arccos(cos_theta))

    if theta < 1e-8:
        return 0.5 * vee(R - R.T)

    if np.pi - theta < 1e-5:
        # Stable-enough educational branch near pi.
        diag = np.maximum((np.diag(R) + 1.0) / 2.0, 0.0)
        axis = np.sqrt(diag)
        # Recover signs from off-diagonal terms.
        axis[0] = np.copysign(axis[0], R[2, 1] - R[1, 2] + EPS)
        axis[1] = np.copysign(axis[1], R[0, 2] - R[2, 0] + EPS)
        axis[2] = np.copysign(axis[2], R[1, 0] - R[0, 1] + EPS)
        n = np.linalg.norm(axis)
        if n < EPS:
            axis = np.array([1.0, 0.0, 0.0])
        else:
            axis /= n
        return axis * theta

    return theta / (2.0 * np.sin(theta)) * vee(R - R.T)


def make_transform(R: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Construct T_AB: coordinates in B -> coordinates in A."""
    R = np.asarray(R, dtype=float).reshape(3, 3)
    p = np.asarray(p, dtype=float).reshape(3)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def transform_inverse(T: np.ndarray) -> np.ndarray:
    """Analytic inverse of an SE(3) transform."""
    T = np.asarray(T, dtype=float).reshape(4, 4)
    R = T[:3, :3]
    p = T[:3, 3]
    T_inv = np.eye(4)
    T_inv[:3, :3] = R.T
    T_inv[:3, 3] = -(R.T @ p)
    return T_inv


def transform_point(T_AB: np.ndarray, p_B: np.ndarray) -> np.ndarray:
    """Transform point coordinates p_B into frame A."""
    p_h = np.concatenate([np.asarray(p_B, dtype=float).reshape(3), [1.0]])
    return (T_AB @ p_h)[:3]


def geodesic_rotation_error(R1: np.ndarray, R2: np.ndarray) -> float:
    """SO(3) geodesic angle between two rotations, in radians."""
    R_delta = R1.T @ R2
    return float(np.linalg.norm(so3_log(R_delta)))


def _check_rotation(R: np.ndarray) -> None:
    np.testing.assert_allclose(R.T @ R, np.eye(3), atol=1e-9)
    np.testing.assert_allclose(np.linalg.det(R), 1.0, atol=1e-9)


def self_test(seed: int = 0) -> None:
    rng = np.random.default_rng(seed)

    print("[1] hat / vee")
    w = rng.normal(size=3)
    np.testing.assert_allclose(vee(hat(w)), w)

    print("[2] SO(3) exp / log round trip")
    for _ in range(1000):
        axis = rng.normal(size=3)
        axis /= np.linalg.norm(axis)
        # Stay slightly away from pi for a simple educational test.
        angle = rng.uniform(-2.8, 2.8)
        phi = axis * angle
        R = so3_exp(phi)
        _check_rotation(R)
        phi_rt = so3_log(R)
        R_rt = so3_exp(phi_rt)
        assert geodesic_rotation_error(R, R_rt) < 1e-8

    print("[3] SE(3) inverse")
    R = so3_exp(np.array([0.2, -0.3, 0.4]))
    p = np.array([0.7, -0.1, 1.2])
    T = make_transform(R, p)
    T_inv = transform_inverse(T)
    np.testing.assert_allclose(T @ T_inv, np.eye(4), atol=1e-9)

    print("[4] frame composition")
    T_AB = make_transform(so3_exp([0.1, 0.0, 0.2]), [1.0, 0.0, 0.0])
    T_BC = make_transform(so3_exp([0.0, -0.2, 0.0]), [0.0, 2.0, 0.0])
    T_AC = T_AB @ T_BC

    p_C = np.array([0.3, 0.4, 0.5])
    p_A_two_steps = transform_point(T_AB, transform_point(T_BC, p_C))
    p_A_one_step = transform_point(T_AC, p_C)
    np.testing.assert_allclose(p_A_two_steps, p_A_one_step, atol=1e-9)

    print("[5] counterexample: adding rotation vectors is not general composition")
    phi1 = np.array([0.8, 0.0, 0.0])
    phi2 = np.array([0.0, 0.8, 0.0])
    R_true = so3_exp(phi1) @ so3_exp(phi2)
    R_wrong = so3_exp(phi1 + phi2)
    err_deg = np.degrees(geodesic_rotation_error(R_true, R_wrong))
    print(f"    geodesic error from naive phi1+phi2: {err_deg:.3f} deg")
    assert err_deg > 1.0

    print("All SE(3) tests passed.")


if __name__ == "__main__":
    self_test()
