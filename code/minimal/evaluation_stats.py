"""Minimal evaluation statistics for robot success experiments.

Run:
    python code/minimal/evaluation_stats.py

Includes:
- Wilson confidence interval for a Bernoulli success rate
- bootstrap confidence interval for paired success-rate differences
- Brier score
- Expected Calibration Error (ECE)

The point is to make Part 44 executable: a demo video is not a denominator.
"""

from __future__ import annotations

from statistics import NormalDist

import numpy as np


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    if not 0 <= successes <= trials or trials <= 0:
        raise ValueError("require 0 <= successes <= trials and trials > 0")
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    p = successes / trials
    denom = 1.0 + z**2 / trials
    center = (p + z**2 / (2.0 * trials)) / denom
    half = z * np.sqrt(p * (1.0 - p) / trials + z**2 / (4.0 * trials**2)) / denom
    return float(max(0.0, center - half)), float(min(1.0, center + half))


def brier_score(probabilities: np.ndarray, outcomes: np.ndarray) -> float:
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if p.shape != y.shape:
        raise ValueError("probabilities and outcomes must have identical shapes")
    if np.any((p < 0.0) | (p > 1.0)):
        raise ValueError("probabilities must lie in [0, 1]")
    return float(np.mean((p - y) ** 2))


def expected_calibration_error(
    probabilities: np.ndarray,
    outcomes: np.ndarray,
    bins: int = 10,
) -> float:
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if p.shape != y.shape:
        raise ValueError("probabilities and outcomes must have identical shapes")

    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    n = len(p)
    for i in range(bins):
        lo, hi = edges[i], edges[i + 1]
        if i == bins - 1:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        if not np.any(mask):
            continue
        confidence = float(np.mean(p[mask]))
        accuracy = float(np.mean(y[mask]))
        ece += np.sum(mask) / n * abs(accuracy - confidence)
    return float(ece)


def paired_bootstrap_difference(
    outcomes_a: np.ndarray,
    outcomes_b: np.ndarray,
    *,
    samples: int = 20_000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, tuple[float, float]]:
    """Paired bootstrap for mean(success_B - success_A).

    Use paired trials when both methods are evaluated on the same randomized
    scenario instances. Pairing can reduce variance caused by task difficulty.
    """
    a = np.asarray(outcomes_a, dtype=float)
    b = np.asarray(outcomes_b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("paired outcome arrays must be 1-D and have equal length")

    diff = b - a
    rng = np.random.default_rng(seed)
    ids = rng.integers(0, len(diff), size=(samples, len(diff)))
    boot = np.mean(diff[ids], axis=1)
    alpha = (1.0 - confidence) / 2.0
    interval = tuple(np.quantile(boot, [alpha, 1.0 - alpha]).tolist())
    return float(np.mean(diff)), (float(interval[0]), float(interval[1]))


def main() -> None:
    print("[1] Wilson interval")
    successes, trials = 78, 100
    low, high = wilson_interval(successes, trials)
    print(f"    {successes}/{trials} = {successes/trials:.3f}; 95% CI [{low:.3f}, {high:.3f}]")
    assert low < successes / trials < high

    print("[2] Calibration")
    probabilities = np.array([0.1, 0.2, 0.3, 0.45, 0.55, 0.7, 0.8, 0.9, 0.95, 0.99])
    outcomes = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    bs = brier_score(probabilities, outcomes)
    ece = expected_calibration_error(probabilities, outcomes, bins=5)
    print(f"    Brier={bs:.4f}; ECE={ece:.4f}")
    assert 0.0 <= bs <= 1.0
    assert 0.0 <= ece <= 1.0

    print("[3] Paired policy comparison")
    # Same 40 scenario instances; B rescues several cases A failed.
    a = np.array([1] * 25 + [0] * 15, dtype=float)
    b = a.copy()
    b[[25, 27, 29, 31, 33, 35]] = 1.0
    effect, ci = paired_bootstrap_difference(a, b, seed=7)
    print(f"    mean paired improvement={effect:+.3f}; bootstrap CI={np.round(ci, 3)}")
    assert effect > 0.0

    print("Evaluation-statistics tests passed.")


if __name__ == "__main__":
    main()
