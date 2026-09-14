"""Information-gain active perception in a tiny discrete world.

A hidden object is in one of five cells. Each camera viewpoint has a different
confusion matrix. The agent selects a view by expected entropy reduction minus
motion cost.

Run:
    python code/minimal/active_perception.py
"""

from __future__ import annotations

import numpy as np

EPS = 1e-12


def normalize(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    s = p.sum()
    if s <= 0.0:
        raise ValueError("probability mass vanished")
    return p / s


def entropy(p: np.ndarray) -> float:
    p = normalize(p)
    return float(-np.sum(p * np.log(p + EPS)))


def bayes_update(prior: np.ndarray, likelihood_obs_given_state: np.ndarray) -> np.ndarray:
    return normalize(prior * likelihood_obs_given_state)


def expected_posterior_entropy(prior: np.ndarray, obs_model: np.ndarray) -> float:
    """obs_model[o, s] = P(observation=o | hidden state=s)."""
    prior = normalize(prior)
    n_obs, n_states = obs_model.shape
    assert prior.shape == (n_states,)

    total = 0.0
    for o in range(n_obs):
        p_o = float(np.sum(obs_model[o] * prior))
        if p_o < EPS:
            continue
        posterior = bayes_update(prior, obs_model[o])
        total += p_o * entropy(posterior)
    return total


def information_gain(prior: np.ndarray, obs_model: np.ndarray) -> float:
    return entropy(prior) - expected_posterior_entropy(prior, obs_model)


def make_view_model(n: int, visible_cells: list[int], accuracy: float = 0.9) -> np.ndarray:
    """Observation is an estimated cell index.

    A visible state is recognized with high accuracy; an occluded state produces
    a much flatter observation distribution. Columns sum to one.
    """
    M = np.zeros((n, n), dtype=float)
    for s in range(n):
        if s in visible_cells:
            wrong = (1.0 - accuracy) / (n - 1)
            M[:, s] = wrong
            M[s, s] = accuracy
        else:
            M[:, s] = 1.0 / n
    np.testing.assert_allclose(M.sum(axis=0), np.ones(n))
    return M


def choose_view(prior: np.ndarray, models: list[np.ndarray], costs: np.ndarray, lam: float) -> tuple[int, np.ndarray]:
    scores = np.array([information_gain(prior, m) for m in models]) - lam * costs
    return int(np.argmax(scores)), scores


def run_episode(seed: int = 0, active: bool = True) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n = 5
    hidden = int(rng.integers(0, n))
    belief = np.ones(n) / n

    models = [
        make_view_model(n, [0, 1, 2]),
        make_view_model(n, [2, 3, 4]),
        make_view_model(n, [0, 4], accuracy=0.97),
    ]
    costs = np.array([0.2, 0.2, 0.6])
    current_view = 0
    history = []

    for step in range(5):
        if active:
            view, scores = choose_view(belief, models, costs, lam=0.25)
        else:
            view = int(rng.integers(0, len(models)))
            scores = np.full(len(models), np.nan)

        model = models[view]
        p_obs = model[:, hidden]
        obs = int(rng.choice(n, p=p_obs))
        belief = bayes_update(belief, model[obs])

        history.append(
            {
                "step": step,
                "view": view,
                "scores": scores.copy(),
                "observation": obs,
                "belief": belief.copy(),
                "entropy": entropy(belief),
            }
        )
        current_view = view

    guess = int(np.argmax(belief))
    return {"hidden": hidden, "guess": guess, "belief": belief, "history": history, "last_view": current_view}


def benchmark(n_episodes: int = 1000) -> None:
    active_correct = 0
    random_correct = 0
    active_entropy = []
    random_entropy = []

    for seed in range(n_episodes):
        a = run_episode(seed, active=True)
        r = run_episode(seed, active=False)
        active_correct += int(a["hidden"] == a["guess"])
        random_correct += int(r["hidden"] == r["guess"])
        active_entropy.append(entropy(a["belief"]))
        random_entropy.append(entropy(r["belief"]))

    print("active accuracy:", active_correct / n_episodes)
    print("random accuracy:", random_correct / n_episodes)
    print("active final entropy:", np.mean(active_entropy))
    print("random final entropy:", np.mean(random_entropy))

    # This is deliberately a statistical toy, so require only a modest advantage.
    assert np.mean(active_entropy) < np.mean(random_entropy)


if __name__ == "__main__":
    demo = run_episode(seed=3, active=True)
    print("hidden state:", demo["hidden"], "final guess:", demo["guess"])
    for row in demo["history"]:
        print(
            f"step={row['step']} view={row['view']} obs={row['observation']} "
            f"entropy={row['entropy']:.3f} belief={np.round(row['belief'], 3)}"
        )
    print("\nbenchmark")
    benchmark()
