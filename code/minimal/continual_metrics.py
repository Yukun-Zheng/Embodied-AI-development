"""Metrics for continual / developmental / self-evolving robot learning.

Run:
    python code/minimal/continual_metrics.py

P[i, j] means performance on task i after learning task j. Entries before a task
has been introduced may be NaN.
"""

from __future__ import annotations

import numpy as np


def final_average_accuracy(P: np.ndarray) -> float:
    P = np.asarray(P, dtype=float)
    return float(np.nanmean(P[:, -1]))


def forgetting_per_task(P: np.ndarray) -> np.ndarray:
    """F_i = best historical performance after task i was learned - final performance."""
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    out = np.full(n, np.nan)
    for i in range(n):
        valid = P[i, i:]
        valid = valid[np.isfinite(valid)]
        if len(valid) == 0 or not np.isfinite(P[i, -1]):
            continue
        out[i] = float(np.max(valid) - P[i, -1])
    return out


def average_forgetting(P: np.ndarray, *, exclude_last: bool = True) -> float:
    f = forgetting_per_task(P)
    if exclude_last and len(f) > 1:
        f = f[:-1]
    return float(np.nanmean(f))


def forward_transfer(P: np.ndarray, scratch_diagonal: np.ndarray) -> tuple[np.ndarray, float]:
    """Compare first performance after learning each task with learning it from scratch."""
    P = np.asarray(P, dtype=float)
    scratch = np.asarray(scratch_diagonal, dtype=float)
    diagonal = np.diag(P)
    if diagonal.shape != scratch.shape:
        raise ValueError("scratch_diagonal must have one value per task")
    ft = diagonal - scratch
    return ft, float(np.nanmean(ft))


def retention(P: np.ndarray) -> float:
    """Final / initial-post-learning performance, averaged over tasks.

    A value near 1 means old capability is retained. Values above 1 are possible
    if later learning improves an old task.
    """
    P = np.asarray(P, dtype=float)
    initial = np.diag(P)
    final = P[:, -1]
    ratio = final / initial
    return float(np.nanmean(ratio))


def growth_efficiency(
    capability_gain: float,
    *,
    compute_gain: float,
    parameter_gain: float,
    data_gain: float,
    lambda_params: float = 1.0,
    mu_data: float = 1.0,
) -> float:
    """A transparent, user-defined efficiency score.

    Units must be normalized before use in a real paper; this toy function is here
    to force the denominator to include resource growth rather than reward free
    expansion of compute/parameters/data.
    """
    denominator = compute_gain + lambda_params * parameter_gain + mu_data * data_gain
    if denominator <= 0.0:
        raise ValueError("resource-growth denominator must be positive")
    return float(capability_gain / denominator)


def autonomy_ratio(total_learning_time: float, human_intervention_time: float) -> float:
    if total_learning_time <= 0.0:
        raise ValueError("total_learning_time must be positive")
    ratio = 1.0 - human_intervention_time / total_learning_time
    return float(np.clip(ratio, 0.0, 1.0))


def main() -> None:
    # Rows: evaluation task. Columns: after finishing training task 0..3.
    P = np.array(
        [
            [0.90, 0.87, 0.84, 0.81],
            [np.nan, 0.88, 0.86, 0.84],
            [np.nan, np.nan, 0.91, 0.89],
            [np.nan, np.nan, np.nan, 0.92],
        ]
    )
    scratch = np.array([0.87, 0.82, 0.85, 0.86])

    f = forgetting_per_task(P)
    ft_each, ft = forward_transfer(P, scratch)
    print("performance matrix:\n", P)
    print("final average accuracy:", final_average_accuracy(P))
    print("forgetting per task:    ", np.round(f, 4))
    print("average forgetting:     ", average_forgetting(P))
    print("forward transfer each:  ", np.round(ft_each, 4))
    print("average forward transfer:", ft)
    print("retention:              ", retention(P))

    ge = growth_efficiency(
        capability_gain=0.20,
        compute_gain=0.08,
        parameter_gain=0.04,
        data_gain=0.10,
        lambda_params=1.5,
        mu_data=0.5,
    )
    ar = autonomy_ratio(total_learning_time=100.0, human_intervention_time=12.0)
    print("growth efficiency:      ", ge)
    print("autonomy ratio:         ", ar)

    assert 0.0 <= final_average_accuracy(P) <= 1.0
    assert np.all(f[np.isfinite(f)] >= -1e-12)
    assert ft > 0.0
    assert 0.0 < retention(P) <= 1.05
    assert ge > 0.0
    assert np.isclose(ar, 0.88)

    print("Continual-learning metric tests passed.")


if __name__ == "__main__":
    main()
