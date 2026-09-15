#!/usr/bin/env python3
"""Lab 34 — self-generated curriculum from measured learning progress.

A single latent skill supports a fixed pool of increasingly difficult practice
goals. Practice is most useful near the agent's current competence frontier:
tasks that are already mastered or far beyond current ability produce little
learning. Every strategy receives exactly the same total practice budget and the
same two-round warmup over every task.

Controls:
- learning_progress: select the task whose measured success changed most over a
  recent probe window;
- uniform: equal task counts in round-robin order;
- fixed_curriculum: the same equal task counts, but easy-to-hard blocks;
- hardest_first: repeatedly train the hardest task after warmup;
- shuffled_progress: preserve the measured progress scores but reverse their task
  identity before selecting, testing whether correct progress-to-task binding is
  causally necessary.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab34_self_generated_curriculum"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


def competence(skill: float, difficulty: float, temperature: float) -> float:
    return 1.0 / (1.0 + math.exp(-(skill - difficulty) / temperature))


def competence_vector(skill: float, cfg: dict[str, Any]) -> list[float]:
    temperature = float(cfg["success_temperature"])
    return [
        competence(skill, float(difficulty), temperature)
        for difficulty in cfg["task_difficulties"]
    ]


def learnability(success_probability: float) -> float:
    """Normalized frontier signal: zero at p=0/1, one at p=0.5."""
    return 4.0 * success_probability * (1.0 - success_probability)


def learning_gain(
    *, skill: float, difficulty: float, success_probability: float, cfg: dict[str, Any]
) -> float:
    challenge_weight = float(cfg["difficulty_gain_base"]) + float(
        cfg["difficulty_gain_scale"]
    ) * difficulty
    remaining_capacity = max(0.0, 1.0 - skill / float(cfg["max_skill"]))
    return (
        float(cfg["learning_rate"])
        * learnability(success_probability)
        * challenge_weight
        * remaining_capacity
    )


def progress_scores(
    current: list[float], history: list[list[float]], window: int
) -> list[float]:
    if len(history) > window:
        previous = history[-(window + 1)]
    else:
        previous = history[0]
    return [current[index] - previous[index] for index in range(len(current))]


def select_task(
    *,
    strategy: str,
    step: int,
    skill: float,
    current: list[float],
    history: list[list[float]],
    cfg: dict[str, Any],
) -> tuple[int, list[float], str]:
    difficulties = [float(value) for value in cfg["task_difficulties"]]
    task_count = len(difficulties)
    warmup_steps = int(cfg["warmup_rounds_per_task"]) * task_count

    measured_progress = progress_scores(
        current, history, int(cfg["progress_window"])
    )

    if step < warmup_steps:
        return step % task_count, measured_progress, "shared_warmup"

    if strategy == "learning_progress":
        index = max(
            range(task_count),
            key=lambda task: (
                measured_progress[task],
                -abs(difficulties[task] - skill),
                -task,
            ),
        )
        return index, measured_progress, "measured_progress"

    if strategy == "shuffled_progress":
        shuffled = list(reversed(measured_progress))
        index = max(
            range(task_count),
            key=lambda task: (
                shuffled[task],
                -abs(difficulties[task] - skill),
                -task,
            ),
        )
        return index, shuffled, "reversed_task_binding"

    if strategy == "uniform":
        return (step - warmup_steps) % task_count, measured_progress, "equal_round_robin"

    if strategy == "fixed_curriculum":
        remaining_steps = int(cfg["practice_budget"]) - warmup_steps
        block_size = remaining_steps // task_count
        index = min(task_count - 1, (step - warmup_steps) // block_size)
        return index, measured_progress, "fixed_easy_to_hard"

    if strategy == "hardest_first":
        return task_count - 1, measured_progress, "hardest_after_warmup"

    raise ValueError(f"Unknown curriculum strategy: {strategy}")


def run_strategy(
    strategy: str, cfg: dict[str, Any], output: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    difficulties = [float(value) for value in cfg["task_difficulties"]]
    budget = int(cfg["practice_budget"])
    warmup_steps = int(cfg["warmup_rounds_per_task"]) * len(difficulties)
    skill = float(cfg["initial_skill"])
    success_history = [competence_vector(skill, cfg)]
    selected_tasks: list[int] = []
    selected_learnability: list[float] = []
    selected_frontier_distance: list[float] = []
    average_success_trajectory: list[float] = []
    skill_gain_trajectory: list[float] = []

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition=strategy,
        seed=int(cfg["seed"]),
        config=cfg,
        repo_root=REPO_ROOT,
    )

    for step in range(budget):
        current = competence_vector(skill, cfg)
        task, scores, selection_reason = select_task(
            strategy=strategy,
            step=step,
            skill=skill,
            current=current,
            history=success_history,
            cfg=cfg,
        )
        difficulty = difficulties[task]
        task_success = current[task]
        frontier_score = learnability(task_success)
        gain = learning_gain(
            skill=skill,
            difficulty=difficulty,
            success_probability=task_success,
            cfg=cfg,
        )
        skill_after = min(float(cfg["max_skill"]), skill + gain)
        after = competence_vector(skill_after, cfg)

        selected_tasks.append(task)
        selected_learnability.append(frontier_score)
        selected_frontier_distance.append(abs(difficulty - skill))
        average_success_trajectory.append(statistics.fmean(current))
        skill_gain_trajectory.append(gain)

        recorder.log_step(
            step=step,
            time_s=float(step),
            strategy=strategy,
            selection_reason=selection_reason,
            selected_task=task,
            selected_difficulty=difficulty,
            skill_before=skill,
            skill_after=skill_after,
            selected_success_before=task_success,
            selected_learnability=frontier_score,
            selected_progress_score=scores[task],
            frontier_distance=abs(difficulty - skill),
            average_success_before=statistics.fmean(current),
            average_success_after=statistics.fmean(after),
            learning_gain=gain,
            progress_scores_json=json.dumps(scores, separators=(",", ":")),
        )

        if step >= warmup_steps and frontier_score < 0.05:
            recorder.log_failure(
                category="low_learnability_practice",
                step=step,
                time_s=float(step),
                details={
                    "strategy": strategy,
                    "selected_task": task,
                    "difficulty": difficulty,
                    "skill": skill,
                    "success_probability": task_success,
                    "learnability": frontier_score,
                },
            )

        skill = skill_after
        success_history.append(after)

    final_success = competence_vector(skill, cfg)
    counts = Counter(selected_tasks)
    mastery_threshold = float(cfg["mastery_threshold"])
    mastered = [
        difficulty
        for difficulty, success in zip(difficulties, final_success)
        if success >= mastery_threshold
    ]

    summary = {
        "strategy": strategy,
        "practice_budget": budget,
        "warmup_steps": warmup_steps,
        "final_skill": skill,
        "final_average_success": statistics.fmean(final_success),
        "learning_curve_auc": statistics.fmean(average_success_trajectory),
        "mean_selected_learnability_after_warmup": statistics.fmean(
            selected_learnability[warmup_steps:]
        ),
        "mean_frontier_distance_after_warmup": statistics.fmean(
            selected_frontier_distance[warmup_steps:]
        ),
        "mean_learning_gain_after_warmup": statistics.fmean(
            skill_gain_trajectory[warmup_steps:]
        ),
        "mastered_task_count": len(mastered),
        "max_mastered_difficulty": max(mastered) if mastered else 0.0,
        "unique_tasks_after_warmup": len(set(selected_tasks[warmup_steps:])),
    }

    selection_rows = [
        {
            "strategy": strategy,
            "task": task,
            "difficulty": difficulties[task],
            "practice_count": counts.get(task, 0),
            "post_warmup_count": selected_tasks[warmup_steps:].count(task),
            "final_success": final_success[task],
        }
        for task in range(len(difficulties))
    ]

    recorder.finalize(summary)
    return summary, selection_rows, recorder.steps


def run_experiment(
    cfg: dict[str, Any], output: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    output.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []

    for strategy in [str(value) for value in cfg["strategies"]]:
        summary, rows, _ = run_strategy(strategy, cfg, output)
        summaries.append(summary)
        selection_rows.extend(rows)

    write_csv(output / "strategy_metrics.csv", summaries)
    write_csv(output / "selection_counts.csv", selection_rows)
    write_json(
        output / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "practice_budget": int(cfg["practice_budget"]),
            "task_difficulties": cfg["task_difficulties"],
            "strategies": summaries,
        },
    )
    return summaries, selection_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab34"))
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["practice_budget"] = min(int(cfg["practice_budget"]), 180)

    summaries, _ = run_experiment(cfg, args.output)
    print("Lab 34 self-generated curriculum experiment complete")
    for row in summaries:
        print(
            f"{row['strategy']:20s} "
            f"final={row['final_average_success']:.3f} "
            f"auc={row['learning_curve_auc']:.3f} "
            f"skill={row['final_skill']:.3f} "
            f"learnability={row['mean_selected_learnability_after_warmup']:.3f} "
            f"frontier-dist={row['mean_frontier_distance_after_warmup']:.3f} "
            f"mastered={row['mastered_task_count']}"
        )
    print(f"metrics: {args.output / 'strategy_metrics.csv'}")


if __name__ == "__main__":
    main()
