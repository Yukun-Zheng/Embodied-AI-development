"""Minimal linear Kalman filter with a biased/noisy tracking example.

Run:
    python code/minimal/kalman_filter.py
"""

from __future__ import annotations

import numpy as np


class KalmanFilter:
    def __init__(
        self,
        A: np.ndarray,
        B: np.ndarray,
        H: np.ndarray,
        Q: np.ndarray,
        R: np.ndarray,
        x0: np.ndarray,
        P0: np.ndarray,
    ) -> None:
        self.A = np.asarray(A, dtype=float)
        self.B = np.asarray(B, dtype=float)
        self.H = np.asarray(H, dtype=float)
        self.Q = np.asarray(Q, dtype=float)
        self.R = np.asarray(R, dtype=float)
        self.x = np.asarray(x0, dtype=float).copy()
        self.P = np.asarray(P0, dtype=float).copy()

    def predict(self, u: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self.x = self.A @ self.x + self.B @ np.asarray(u, dtype=float)
        self.P = self.A @ self.P @ self.A.T + self.Q
        return self.x.copy(), self.P.copy()

    def update(self, z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        z = np.asarray(z, dtype=float)
        innovation = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ innovation
        I = np.eye(self.P.shape[0])
        # Joseph form is numerically safer than (I-KH)P alone.
        IKH = I - K @ self.H
        self.P = IKH @ self.P @ IKH.T + K @ self.R @ K.T
        return self.x.copy(), self.P.copy()


def run_demo(seed: int = 0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    dt = 0.05

    # state = [position, velocity]
    A = np.array([[1.0, dt], [0.0, 1.0]])
    B = np.array([[0.5 * dt**2], [dt]])
    H = np.array([[1.0, 0.0]])  # position sensor only

    Q = np.diag([2e-5, 3e-4])
    R = np.array([[0.05**2]])

    kf = KalmanFilter(
        A,
        B,
        H,
        Q,
        R,
        x0=np.array([0.0, 0.0]),
        P0=np.diag([0.5, 0.5]),
    )

    true = np.array([0.0, 0.0])
    n = 300
    truth = np.zeros((n, 2))
    meas = np.zeros(n)
    est = np.zeros((n, 2))
    sigma = np.zeros((n, 2))

    for t in range(n):
        # Piecewise acceleration: the estimator knows the control but not process noise.
        u = np.array([0.8 if t < 70 else (-0.5 if t < 140 else 0.0)])

        process_noise = rng.multivariate_normal(np.zeros(2), Q)
        true = A @ true + B @ u + process_noise
        z = H @ true + rng.normal(0.0, np.sqrt(R[0, 0]), size=1)

        kf.predict(u)
        xhat, P = kf.update(z)

        truth[t] = true
        meas[t] = z[0]
        est[t] = xhat
        sigma[t] = np.sqrt(np.diag(P))

    return {"truth": truth, "measurement": meas, "estimate": est, "sigma": sigma}


def self_test() -> None:
    out = run_demo(seed=4)
    truth = out["truth"]
    meas = out["measurement"]
    est = out["estimate"]
    sigma = out["sigma"]

    rmse_meas = float(np.sqrt(np.mean((meas - truth[:, 0]) ** 2)))
    rmse_est = float(np.sqrt(np.mean((est[:, 0] - truth[:, 0]) ** 2)))
    print("measurement position RMSE:", rmse_meas)
    print("Kalman position RMSE:    ", rmse_est)
    print("final state estimate:    ", est[-1])
    print("final posterior sigma:   ", sigma[-1])

    assert rmse_est < rmse_meas
    assert np.all(np.isfinite(sigma))
    assert np.all(sigma > 0.0)

    print("Kalman filter test passed.")


if __name__ == "__main__":
    self_test()
