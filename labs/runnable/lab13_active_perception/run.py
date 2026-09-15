#!/usr/bin/env python3
"""Lab 13 — task-aware active perception with motion cost and occlusion.

A hidden target occupies one of several scene cells. The camera can move along a
small view rail. Each viewpoint exposes a different subset of cells; occluded
cells still yield weak/noisy evidence. We compare fixed, random and
information-gain view selection under paired environment randomness.

The scientific target is not merely lower belief entropy. We measure whether the
extra sensing motion improves the final task decision enough to justify its cost.
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab13_active_perception"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"
EPS = 1e-12


def normalize(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=np.float64)
    total = float(p.sum())
    if total <= 0.0:
        raise ValueError("probability mass vanished")
    return p / total


def entropy(p: np.ndarray) -> float:
    p = normalize(p)
    return float(-np.sum(p * np.log(p + EPS)))


def bayes_update(prior: np.ndarray, likelihood: np.ndarray) -> np.ndarray:
    return normalize(prior * likelihood)


def make_view_model(
    *,
    n_cells: int,
    visible_cells: list[int],
    visible_accuracy: float,
    occluded_accuracy: float,
) -> np.ndarray:
    """Return M[o, s] = P(observation=o | target cell=s, this viewpoint)."""
    if n_cells <= 1:
        raise ValueError("n_cells must be > 1")
    model = np.empty((n_cells, n_cells), dtype=np.float64)
    visible = set(int(x) for x in visible_cells)
    for state in range(n_cells):
        accuracy = visible_accuracy if state in visible else occluded_accuracy
        wrong = (1.0 - accuracy) / (n_cells - 1)
        model[:, state] = wrong
        model[state, state] = accuracy
    np.testing.assert_allclose(model.sum(axis=0), np.ones(n_cells), atol=1e-12)
    return model


def expected_posterior_entropy(prior: np.ndarray, model: np.ndarray) -> float:
    total = 0.0
    for obs in range(model.shape[0]):
        p_obs = float(np.sum(model[obs] * prior))
        if p_obs <= EPS:
            continue
        posterior = bayes_update(prior, model[obs])
        total += p_obs * entropy(posterior)
    return total


def information_gain(prior: np.ndarray, model: np.ndarray) -> float:
    return entropy(prior) - expected_posterior_entropy(prior, model)


def build_models(cfg: dict[str, Any]) -> list[np.ndarray]:
    n_cells = int(cfg["n_cells"])
    models = [
        make_view_model(
            n_cells=n_cells,
            visible_cells=[int(x) for x in visible],
            visible_accuracy=float(cfg["visible_accuracy"]),
            occluded_accuracy=float(cfg["occluded_accuracy"]),
        )
        for visible in cfg["visible_cells_by_view"]
    ]
    if len(models) != len(cfg["view_positions"]):
        raise ValueError("view_positions and visible_cells_by_view must have the same length")
    return models


def hidden_target(*, base_seed: int, episode: int, n_cells: int) -> int:
    # Paired across policies: target identity depends only on base seed + episode.
    rng = np.random.default_rng(base_seed + 1_000_003 * episode)
    return int(rng.integers(0, n_cells))


def paired_observation(
    *,
    base_seed: int,
    episode: int,
    view: int,
    sensing_step: int,
    hidden: int,
    model: np.ndarray,
) -> int:
    # Potential observation is deterministic for a given (episode, view, step),
    # so two policies choosing the same view see the same environmental draw.
    seed = base_seed * 1_000_003 + episode * 1009 + view * 97 + sensing_step * 17 + hidden * 3
    rng = np.random.default_rng(seed)
    return int(rng.choice(model.shape[0], p=model[:, hidden]))


def choose_information_gain_view(
    *,
    belief: np.ndarray,
    current_view: int,
    scoring_models: list[np.ndarray],
    positions: np.ndarray,
    motion_lambda: float,
) -> tuple[int, list[float], list[float]]:
    gains = [information_gain(belief, model) for model in scoring_models]
    scores = [
        gain - motion_lambda * abs(float(positions[view] - positions[current_view]))
        for view, gain in enumerate(gains)
    ]
    return int(np.argmax(scores)), gains, scores


def run_policy(
    *,
    policy: str,
    cfg: dict[str, Any],
    models: list[np.ndarray],
    output_root: Path,
    command: list[str],
) -> dict[str, Any]:
    policies = {
        "fixed_center",
        "random_view",
        "info_gain",
        "info_gain_shuffled_geometry",
    }
    if policy not in policies:
        raise ValueError(f"Unknown policy: {policy}")

    episodes = int(cfg["episodes"])
    sensing_steps = int(cfg["sensing_steps"])
    n_cells = int(cfg["n_cells"])
    base_seed = int(cfg["seed"])
    initial_view = int(cfg["initial_view"])
    positions = np.asarray(cfg["view_positions"], dtype=np.float64)
    motion_lambda = float(cfg["information_gain_motion_lambda"])
    task_motion_penalty = float(cfg["task_motion_penalty"])
    permutation = [int(x) for x in cfg["shuffled_geometry_permutation"]]
    if sorted(permutation) != list(range(len(models))):
        raise ValueError("shuffled_geometry_permutation must be a permutation of view indices")

    scoring_models = models
    if policy == "info_gain_shuffled_geometry":
        scoring_models = [models[idx] for idx in permutation]

    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=policy,
        seed=base_seed,
        config={**cfg, "condition": {"policy": policy}},
        repo_root=REPO_ROOT,
        command=command,
    )

    correct: list[int] = []
    final_entropies: list[float] = []
    movement_distances: list[float] = []
    utilities: list[float] = []
    unique_views: list[int] = []
    initial_entropy = math.log(n_cells)
    global_step = 0

    for episode in range(episodes):
        hidden = hidden_target(base_seed=base_seed, episode=episode, n_cells=n_cells)
        belief = np.ones(n_cells, dtype=np.float64) / n_cells
        current_view = initial_view
        total_move = 0.0
        visited = {current_view}

        for sensing_step in range(sensing_steps):
            prior_entropy = entropy(belief)
            gains = [float("nan")] * len(models)
            scores = [float("nan")] * len(models)

            if policy == "fixed_center":
                selected_view = initial_view
            elif policy == "random_view":
                random_seed = base_seed + episode * 7919 + sensing_step * 104729 + 17
                selected_view = int(np.random.default_rng(random_seed).integers(0, len(models)))
            else:
                selected_view, gains, scores = choose_information_gain_view(
                    belief=belief,
                    current_view=current_view,
                    scoring_models=scoring_models,
                    positions=positions,
                    motion_lambda=motion_lambda,
                )

            move_distance = abs(float(positions[selected_view] - positions[current_view]))
            total_move += move_distance
            current_view = selected_view
            visited.add(current_view)

            observation = paired_observation(
                base_seed=base_seed,
                episode=episode,
                view=selected_view,
                sensing_step=sensing_step,
                hidden=hidden,
                model=models[selected_view],
            )
            belief = bayes_update(belief, models[selected_view][observation])
            posterior_entropy = entropy(belief)
            guess = int(np.argmax(belief))

            recorder.log_step(
                step=global_step,
                time_s=float(global_step),
                episode=episode,
                sensing_step=sensing_step,
                hidden_cell=hidden,
                selected_view=selected_view,
                view_position=float(positions[selected_view]),
                move_distance=move_distance,
                cumulative_move_distance=total_move,
                observation=observation,
                prior_entropy=prior_entropy,
                posterior_entropy=posterior_entropy,
                realized_entropy_reduction=prior_entropy - posterior_entropy,
                selected_predicted_information_gain=(
                    gains[selected_view] if math.isfinite(gains[selected_view]) else float("nan")
                ),
                selected_score=(scores[selected_view] if math.isfinite(scores[selected_view]) else float("nan")),
                current_guess=guess,
                current_guess_correct=int(guess == hidden),
            )
            global_step += 1

        guess = int(np.argmax(belief))
        is_correct = int(guess == hidden)
        episode_utility = is_correct - task_motion_penalty * total_move
        correct.append(is_correct)
        final_entropies.append(entropy(belief))
        movement_distances.append(total_move)
        utilities.append(episode_utility)
        unique_views.append(len(visited))

        if not is_correct:
            recorder.log_failure(
                category="wrong_target_inference",
                step=episode,
                time_s=float(episode),
                details={
                    "hidden_cell": hidden,
                    "guess": guess,
                    "final_entropy": final_entropies[-1],
                    "movement_distance": total_move,
                    "policy": policy,
                },
            )

    summary = {
        "policy": policy,
        "seed": base_seed,
        "episodes": episodes,
        "sensing_steps": sensing_steps,
        "accuracy": float(np.mean(correct)),
        "mean_final_entropy": float(np.mean(final_entropies)),
        "mean_entropy_reduction": float(initial_entropy - np.mean(final_entropies)),
        "mean_movement_distance": float(np.mean(movement_distances)),
        "mean_unique_views": float(np.mean(unique_views)),
        "mean_task_utility": float(np.mean(utilities)),
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_experiment(cfg: dict[str, Any], *, output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    models = build_models(cfg)
    rows = [
        run_policy(
            policy=str(policy),
            cfg=cfg,
            models=models,
            output_root=output_root,
            command=command,
        )
        for policy in cfg["policies"]
    ]
    write_csv(output_root / "policy_metrics.csv", rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "episodes": int(cfg["episodes"]),
            "sensing_steps": int(cfg["sensing_steps"]),
            "policies": [str(x) for x in cfg["policies"]],
            "paired_randomness": "hidden target and potential observations are paired across policies",
            "results_file": "policy_metrics.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use fewer paired episodes for CI.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["episodes"] = min(int(cfg["episodes"]), 240)

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 13 complete: {len(rows)} view-selection policies")
    print(f"metrics: {output_root / 'policy_metrics.csv'}")
    for row in rows:
        print(
            f"{row['policy']:<30} accuracy={row['accuracy']:.3f} "
            f"entropy={row['mean_final_entropy']:.4f} "
            f"move={row['mean_movement_distance']:.3f} utility={row['mean_task_utility']:.3f}"
        )


if __name__ == "__main__":
    main()
