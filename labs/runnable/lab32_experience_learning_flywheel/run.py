#!/usr/bin/env python3
"""Lab 32 — experience-learning flywheel with failure-mining controls.

A deterministic context-to-action policy starts perfect on an old task but only
partially correct on a new task. Each learning round first performs autonomous
rollouts, then may add exactly two new-task experience records.

The main controls hold the new-data budget fixed while changing which experience
is selected and whether the corrective label is semantically correct:
- targeted_failure_mining: mine currently failing contexts and attach correct labels;
- random_new_data: same number of labeled contexts, selected from a seeded fixed permutation;
- success_only_data: spend the same budget on already-successful contexts;
- shuffled_corrections: mine true failures but swap their corrective labels;
- targeted_reset_no_replay: use the same targeted corrections but rebuild without
  retaining the old-task mapping, exposing regression.

`no_update` is a zero-update baseline and is not part of the matched-data comparison.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab32_experience_learning_flywheel"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass
class Policy:
    actions: dict[str, str]

    def predict(self, context: str) -> str:
        return self.actions.get(context, "UNKNOWN")

    def copy(self) -> "Policy":
        return Policy(dict(self.actions))


def old_context(index: int) -> str:
    return f"old_{index:02d}"


def new_context(index: int) -> str:
    return f"new_{index:02d}"


def correct_action(context: str) -> str:
    return f"action::{context}"


def build_base_policy(cfg: dict[str, Any]) -> Policy:
    actions: dict[str, str] = {}
    for index in range(int(cfg["old_task_contexts"])):
        context = old_context(index)
        actions[context] = correct_action(context)
    correct_new = int(cfg["base_new_task_correct_contexts"])
    for index in range(int(cfg["new_task_contexts"])):
        context = new_context(index)
        actions[context] = correct_action(context) if index < correct_new else "UNKNOWN"
    return Policy(actions)


def task_accuracy(policy: Policy, contexts: list[str]) -> float:
    return statistics.fmean(
        float(policy.predict(context) == correct_action(context)) for context in contexts
    )


def seeded_pseudorandom_order(count: int, seed: int) -> list[int]:
    """A stable permutation without relying on interpreter RNG implementation details."""
    modulus = count + 1
    multiplier = 7
    offset = seed % modulus
    return sorted(
        range(count),
        key=lambda index: (((multiplier * index) + offset) % modulus, index),
    )


def rollout_new_task(
    *,
    policy: Policy,
    recorder: RunRecorder,
    condition: str,
    round_index: int,
    cfg: dict[str, Any],
) -> tuple[list[int], int, int]:
    failures: list[int] = []
    successes = 0
    total = 0
    repeats = int(cfg["rollouts_per_context"])
    for index in range(int(cfg["new_task_contexts"])):
        context = new_context(index)
        prediction = policy.predict(context)
        target = correct_action(context)
        success = prediction == target
        if not success:
            failures.append(index)
        for repeat in range(repeats):
            total += 1
            successes += int(success)
            recorder.log_step(
                phase="autonomous_rollout",
                round=round_index,
                repeat=repeat,
                task="new",
                context=context,
                prediction=prediction,
                target=target,
                success=int(success),
            )
            if not success:
                recorder.log_failure(
                    category="autonomous_new_task_failure",
                    step=round_index * int(cfg["new_task_contexts"]) * repeats
                    + index * repeats
                    + repeat,
                    time_s=float(round_index),
                    details={
                        "condition": condition,
                        "round": round_index,
                        "context": context,
                        "prediction": prediction,
                        "target": target,
                    },
                )
    return failures, successes, total


def choose_experience(
    *,
    condition: str,
    round_index: int,
    policy: Policy,
    failures: list[int],
    random_order: list[int],
    cfg: dict[str, Any],
) -> list[int]:
    budget = int(cfg["correction_budget_per_round"])
    new_count = int(cfg["new_task_contexts"])

    if condition == "no_update":
        return []

    if condition in {
        "targeted_failure_mining",
        "shuffled_corrections",
        "targeted_reset_no_replay",
    }:
        return failures[:budget]

    if condition == "random_new_data":
        start = round_index * budget
        return [random_order[(start + i) % new_count] for i in range(budget)]

    if condition == "success_only_data":
        successful = [
            index
            for index in range(new_count)
            if policy.predict(new_context(index)) == correct_action(new_context(index))
        ]
        if not successful:
            return []
        start = round_index * budget
        return [successful[(start + i) % len(successful)] for i in range(budget)]

    raise ValueError(f"Unknown condition: {condition}")


def apply_experience(
    *,
    policy: Policy,
    condition: str,
    selected: list[int],
    old_contexts: list[str],
) -> tuple[int, int]:
    """Return (correct_labels_written, wrong_labels_written)."""
    correct_writes = 0
    wrong_writes = 0

    if condition == "targeted_reset_no_replay":
        # Simulate a rebuild from the current new-task buffer without retaining
        # old-task experience. The new-task mapping stays available; old entries do not.
        for context in old_contexts:
            policy.actions[context] = "UNKNOWN"

    if condition == "shuffled_corrections" and selected:
        labels = [correct_action(new_context(index)) for index in selected]
        labels = labels[1:] + labels[:1]
        for index, label in zip(selected, labels):
            context = new_context(index)
            policy.actions[context] = label
            if label == correct_action(context):
                correct_writes += 1
            else:
                wrong_writes += 1
        return correct_writes, wrong_writes

    for index in selected:
        context = new_context(index)
        policy.actions[context] = correct_action(context)
        correct_writes += 1
    return correct_writes, wrong_writes


def run_condition(
    *,
    condition: str,
    cfg: dict[str, Any],
    output: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    rounds = int(cfg["rounds"])
    seed = int(cfg["seed"])
    new_contexts = [new_context(i) for i in range(int(cfg["new_task_contexts"]))]
    old_contexts = [old_context(i) for i in range(int(cfg["old_task_contexts"]))]
    policy = build_base_policy(cfg)
    random_order = seeded_pseudorandom_order(len(new_contexts), seed)

    recorder = RunRecorder(
        output_root=output / "runs",
        lab_id=LAB_ID,
        condition=condition,
        seed=seed,
        config=cfg,
        repo_root=REPO_ROOT,
    )

    round_rows: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    cumulative_examples = 0
    cumulative_selected_failures = 0
    cumulative_unique_corrected: set[int] = set()
    new_curve = [task_accuracy(policy, new_contexts)]
    old_curve = [task_accuracy(policy, old_contexts)]

    for round_index in range(rounds):
        new_before = task_accuracy(policy, new_contexts)
        old_before = task_accuracy(policy, old_contexts)
        failures, rollout_successes, rollout_total = rollout_new_task(
            policy=policy,
            recorder=recorder,
            condition=condition,
            round_index=round_index,
            cfg=cfg,
        )
        selected = choose_experience(
            condition=condition,
            round_index=round_index,
            policy=policy,
            failures=failures,
            random_order=random_order,
            cfg=cfg,
        )

        selected_failures = sum(index in failures for index in selected)
        cumulative_selected_failures += selected_failures
        for index in selected:
            selection_rows.append(
                {
                    "condition": condition,
                    "round": round_index,
                    "context": new_context(index),
                    "was_failure": int(index in failures),
                    "new_success_before": new_before,
                    "old_success_before": old_before,
                }
            )

        correct_writes, wrong_writes = apply_experience(
            policy=policy,
            condition=condition,
            selected=selected,
            old_contexts=old_contexts,
        )
        cumulative_examples += len(selected)
        if condition != "shuffled_corrections":
            cumulative_unique_corrected.update(
                index
                for index in selected
                if policy.predict(new_context(index)) == correct_action(new_context(index))
            )

        new_after = task_accuracy(policy, new_contexts)
        old_after = task_accuracy(policy, old_contexts)
        new_curve.append(new_after)
        old_curve.append(old_after)

        round_rows.append(
            {
                "condition": condition,
                "round": round_index,
                "new_success_before": new_before,
                "new_success_after": new_after,
                "old_success_before": old_before,
                "old_success_after": old_after,
                "autonomous_rollout_success": rollout_successes / rollout_total,
                "failure_contexts_observed": len(failures),
                "examples_added": len(selected),
                "selected_failure_examples": selected_failures,
                "selection_precision": (
                    selected_failures / len(selected) if selected else 0.0
                ),
                "correct_labels_written": correct_writes,
                "wrong_labels_written": wrong_writes,
                "cumulative_examples": cumulative_examples,
                "cumulative_unique_corrected": len(cumulative_unique_corrected),
            }
        )

    base_new = new_curve[0]
    base_old = old_curve[0]
    final_new = new_curve[-1]
    final_old = old_curve[-1]
    matched_budget = int(cfg["rounds"]) * int(cfg["correction_budget_per_round"])
    summary = {
        "condition": condition,
        "base_new_success": base_new,
        "final_new_success": final_new,
        "new_success_gain": final_new - base_new,
        "learning_curve_auc": statistics.fmean(new_curve),
        "base_old_success": base_old,
        "final_old_success": final_old,
        "old_task_regression": base_old - final_old,
        "new_examples_added": cumulative_examples,
        "matched_update_budget": matched_budget,
        "selected_failure_examples": cumulative_selected_failures,
        "selection_precision": (
            cumulative_selected_failures / cumulative_examples if cumulative_examples else 0.0
        ),
        "unique_corrected_contexts": len(cumulative_unique_corrected),
        "gain_per_new_example": (
            (final_new - base_new) / cumulative_examples if cumulative_examples else 0.0
        ),
    }
    recorder.finalize(summary)
    return summary, round_rows, selection_rows


def run_experiment(
    cfg: dict[str, Any], output: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    output.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    rounds: list[dict[str, Any]] = []
    selections: list[dict[str, Any]] = []

    for condition in [str(value) for value in cfg["conditions"]]:
        summary, round_rows, selection_rows = run_condition(
            condition=condition,
            cfg=cfg,
            output=output,
        )
        summaries.append(summary)
        rounds.extend(round_rows)
        selections.extend(selection_rows)

    write_csv(output / "condition_metrics.csv", summaries)
    write_csv(output / "round_metrics.csv", rounds)
    write_csv(output / "selection_events.csv", selections)
    write_json(
        output / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "conditions": summaries,
        },
    )
    return summaries, rounds, selections


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab32"))
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    # Reference config is already lightweight; --quick is kept for a common CLI contract.
    summaries, _, _ = run_experiment(cfg, args.output)
    print("Lab 32 experience-learning flywheel complete")
    for row in summaries:
        print(
            f"{row['condition']:25s} "
            f"new={row['final_new_success']:.3f} "
            f"gain={row['new_success_gain']:.3f} "
            f"auc={row['learning_curve_auc']:.3f} "
            f"old={row['final_old_success']:.3f} "
            f"regress={row['old_task_regression']:.3f} "
            f"examples={row['new_examples_added']} "
            f"precision={row['selection_precision']:.3f}"
        )
    print(f"metrics: {args.output / 'condition_metrics.csv'}")


if __name__ == "__main__":
    main()
