"""Minimal control examples: PID, impedance, discrete LQR.

Run:
    python code/minimal/control.py

No simulator dependency: the goal is to connect Part 10 / DERIVATIONS D8-D9 to
small numerical systems whose trajectories can be inspected directly.
"""

from __future__ import annotations

import numpy as np


class PID:
    def __init__(self, kp: float, ki: float, kd: float, dt: float, integral_limit: float = 10.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.integral_limit = integral_limit
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self) -> None:
        self.integral = 0.0
        self.prev_error = 0.0

    def step(self, target: float, x: float) -> float:
        e = target - x
        self.integral = np.clip(
            self.integral + e * self.dt,
            -self.integral_limit,
            self.integral_limit,
        )
        de = (e - self.prev_error) / self.dt
        self.prev_error = e
        return float(self.kp * e + self.ki * self.integral + self.kd * de)


def impedance_force(
    x: np.ndarray,
    xd: np.ndarray,
    x_des: np.ndarray,
    xd_des: np.ndarray,
    kp: np.ndarray,
    kd: np.ndarray,
) -> np.ndarray:
    """Task-space virtual spring-damper force."""
    return kp * (x_des - x) + kd * (xd_des - xd)


def dlqr(A: np.ndarray, B: np.ndarray, Q: np.ndarray, R: np.ndarray, *, iters: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """Solve infinite-horizon discrete LQR by Riccati iteration.

    Returns K, P for control u = -K x.
    """
    P = Q.copy()
    for _ in range(iters):
        S = R + B.T @ P @ B
        K = np.linalg.solve(S, B.T @ P @ A)
        P_new = Q + A.T @ P @ A - A.T @ P @ B @ K
        if np.max(np.abs(P_new - P)) < 1e-12:
            P = P_new
            break
        P = P_new
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    return K, P


def simulate_mass(
    controller,
    *,
    mass: float = 1.0,
    damping: float = 0.2,
    dt: float = 0.002,
    horizon: float = 3.0,
    disturbance_time: float = 1.0,
    disturbance_impulse: float = 1.5,
) -> np.ndarray:
    """1-D mass plant. state = [x, velocity]."""
    steps = int(horizon / dt)
    x = 0.0
    v = 0.0
    log = np.zeros((steps, 4))  # time, x, v, u

    for i in range(steps):
        t = i * dt
        u = float(controller(t, x, v))
        if abs(t - disturbance_time) < dt / 2.0:
            v += disturbance_impulse / mass

        acc = (u - damping * v) / mass
        v += acc * dt
        x += v * dt
        log[i] = [t, x, v, u]

    return log


def self_test() -> None:
    print("[1] PID on a 1-D mass")
    dt = 0.002
    pid = PID(kp=30.0, ki=1.0, kd=8.0, dt=dt)
    log_pid = simulate_mass(lambda _t, x, _v: pid.step(1.0, x), dt=dt)
    print("    final x:", log_pid[-1, 1])
    assert abs(log_pid[-1, 1] - 1.0) < 0.08

    print("[2] Impedance controller")
    kp = np.array([40.0])
    kd = np.array([2.0 * np.sqrt(40.0)])  # near critical damping for m=1

    def imp(_t: float, x: float, v: float) -> float:
        return float(
            impedance_force(
                np.array([x]),
                np.array([v]),
                np.array([1.0]),
                np.array([0.0]),
                kp,
                kd,
            )[0]
        )

    log_imp = simulate_mass(imp, dt=dt)
    print("    final x:", log_imp[-1, 1])
    assert abs(log_imp[-1, 1] - 1.0) < 0.03

    print("[3] Discrete LQR")
    # Double integrator: [position, velocity].
    h = 0.02
    A = np.array([[1.0, h], [0.0, 1.0]])
    B = np.array([[0.5 * h**2], [h]])
    Q = np.diag([10.0, 1.0])
    R = np.array([[0.1]])
    K, P = dlqr(A, B, Q, R)
    print("    K:", K)
    print("    Riccati P eigenvalues:", np.linalg.eigvalsh(P))
    assert np.all(np.linalg.eigvalsh(P) > 0.0)

    x = np.array([1.0, 0.0])
    for _ in range(400):
        u = -K @ x
        x = A @ x + (B @ u).reshape(-1)
    print("    final state:", x)
    assert np.linalg.norm(x) < 1e-3

    print("All control tests passed.")


if __name__ == "__main__":
    self_test()
