#!/usr/bin/env python3
"""Lab 31 — causal reasoning negative controls in an interactive symbolic world.

The planner does not receive reward for producing text or for looking plausible.
It emits executable high-level actions. Those actions are judged only through
state transitions, prerequisites, entity bindings and final task completion.

Core controls:
- correct_plan: shortest valid plan under the true causal model;
- no_plan: myopic target-directed reactive policy with no prerequisite search;
- random_plan: the same correct action multiset randomly reordered;
- fluent_wrong_plan: shortest valid plan under a coherent but wrong key/lock model;
- shuffled_binding: correct action order with key/package/bin bindings swapped.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab31_reasoning_negative_control"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"

LOCATIONS = (
    "start",
    "junction",
    "supply_left",
    "supply_right",
    "cabinet",
    "goal_left",
    "goal_right",
)
GRAPH: dict[str, tuple[str, ...]] = {
    "start": ("junction",),
    "junction": ("start", "supply_left", "supply_right", "cabinet"),
    "supply_left": ("junction",),
    "supply_right": ("junction",),
    "cabinet": ("junction", "goal_left", "goal_right"),
    "goal_left": ("cabinet",),
    "goal_right": ("cabinet",),
}
KEYS = ("red_key", "blue_key")
PACKAGES = ("red_package", "blue_package")
BINS = ("left_bin", "right_bin")
BIN_LOCATION = {"left_bin": "goal_left", "right_bin": "goal_right"}
ITEMS = KEYS + PACKAGES
ITEM_INDEX = {item: index for index, item in enumerate(ITEMS)}

Action = tuple[str, str | None]


@dataclass(frozen=True)
class WorldState:
    robot_location: str
    held_item: str | None
    cabinet_locked: bool
    cabinet_open: bool
    item_locations: tuple[str, ...]


@dataclass(frozen=True)
class EpisodeSpec:
    required_key: str
    key_at_left_supply: str
    target_package: str
    target_bin: str
    locked_initially: bool


def item_location(state: WorldState, item: str) -> str:
    return state.item_locations[ITEM_INDEX[item]]


def set_item_location(state: WorldState, item: str, location: str) -> WorldState:
    locations = list(state.item_locations)
    locations[ITEM_INDEX[item]] = location
    return WorldState(
        robot_location=state.robot_location,
        held_item=state.held_item,
        cabinet_locked=state.cabinet_locked,
        cabinet_open=state.cabinet_open,
        item_locations=tuple(locations),
    )


def initial_state(spec: EpisodeSpec) -> WorldState:
    locations: list[str] = []
    for item in ITEMS:
        if item == spec.key_at_left_supply:
            locations.append("supply_left")
        elif item in KEYS:
            locations.append("supply_right")
        else:
            locations.append("inside_cabinet")
    return WorldState(
        robot_location="start",
        held_item=None,
        cabinet_locked=spec.locked_initially,
        cabinet_open=False,
        item_locations=tuple(locations),
    )


def sample_episode(index: int, *, seed: int, locked_probability: float) -> EpisodeSpec:
    rng = random.Random(seed + 7919 * index)
    return EpisodeSpec(
        required_key=rng.choice(KEYS),
        key_at_left_supply=rng.choice(KEYS),
        target_package=rng.choice(PACKAGES),
        target_bin=rng.choice(BINS),
        locked_initially=rng.random() < locked_probability,
    )


def other_key(key: str) -> str:
    return KEYS[1 - KEYS.index(key)]


def goal_reached(state: WorldState, spec: EpisodeSpec) -> bool:
    return item_location(state, spec.target_package) == f"placed:{spec.target_bin}"


def causal_progress(state: WorldState, spec: EpisodeSpec) -> int:
    """Ordered prerequisite progress; used only for diagnostics, never reward."""
    if goal_reached(state, spec):
        return 5
    if state.held_item == spec.target_package and state.robot_location == BIN_LOCATION[spec.target_bin]:
        return 4
    if state.held_item == spec.target_package:
        return 3
    if state.cabinet_open:
        return 2
    if not state.cabinet_locked:
        return 1
    return 0


def transition(
    state: WorldState,
    action: Action,
    *,
    required_key: str,
    target_package: str,
    target_bin: str,
) -> tuple[WorldState, bool, str | None]:
    verb, argument = action

    if verb == "move":
        if argument in GRAPH[state.robot_location]:
            return (
                WorldState(
                    robot_location=str(argument),
                    held_item=state.held_item,
                    cabinet_locked=state.cabinet_locked,
                    cabinet_open=state.cabinet_open,
                    item_locations=state.item_locations,
                ),
                True,
                None,
            )
        return state, False, "nonadjacent_move"

    if verb == "pickup":
        if state.held_item is not None or argument not in ITEMS:
            return state, False, "pickup_precondition"
        location = item_location(state, str(argument))
        available = location == state.robot_location or (
            location == "inside_cabinet"
            and state.robot_location == "cabinet"
            and state.cabinet_open
        )
        if not available:
            return state, False, "item_unavailable"
        updated = set_item_location(state, str(argument), "held")
        return (
            WorldState(
                robot_location=updated.robot_location,
                held_item=str(argument),
                cabinet_locked=updated.cabinet_locked,
                cabinet_open=updated.cabinet_open,
                item_locations=updated.item_locations,
            ),
            True,
            None,
        )

    if verb == "drop":
        if state.held_item != argument:
            return state, False, "drop_precondition"
        updated = set_item_location(state, str(argument), state.robot_location)
        return (
            WorldState(
                robot_location=updated.robot_location,
                held_item=None,
                cabinet_locked=updated.cabinet_locked,
                cabinet_open=updated.cabinet_open,
                item_locations=updated.item_locations,
            ),
            True,
            None,
        )

    if verb == "unlock":
        if state.robot_location != "cabinet" or not state.cabinet_locked or state.held_item != argument:
            return state, False, "unlock_precondition"
        if argument != required_key:
            return state, False, "wrong_key"
        return (
            WorldState(
                robot_location=state.robot_location,
                held_item=state.held_item,
                cabinet_locked=False,
                cabinet_open=state.cabinet_open,
                item_locations=state.item_locations,
            ),
            True,
            None,
        )

    if verb == "open":
        if state.robot_location == "cabinet" and not state.cabinet_locked and not state.cabinet_open:
            return (
                WorldState(
                    robot_location=state.robot_location,
                    held_item=state.held_item,
                    cabinet_locked=state.cabinet_locked,
                    cabinet_open=True,
                    item_locations=state.item_locations,
                ),
                True,
                None,
            )
        return state, False, "open_precondition"

    if verb == "place":
        if argument is None or "|" not in argument:
            return state, False, "place_precondition"
        package, target = argument.split("|", 1)
        if target not in BINS:
            return state, False, "unknown_bin"
        if state.held_item != package or state.robot_location != BIN_LOCATION[target]:
            return state, False, "place_precondition"
        updated = set_item_location(state, package, f"placed:{target}")
        updated = WorldState(
            robot_location=updated.robot_location,
            held_item=None,
            cabinet_locked=updated.cabinet_locked,
            cabinet_open=updated.cabinet_open,
            item_locations=updated.item_locations,
        )
        violation = None if package == target_package and target == target_bin else "wrong_placement"
        return updated, True, violation

    return state, False, "unknown_action"


def candidate_actions(state: WorldState, *, required_key: str) -> list[Action]:
    actions: list[Action] = [("move", neighbor) for neighbor in GRAPH[state.robot_location]]

    if state.held_item is None:
        for item in ITEMS:
            location = item_location(state, item)
            if location == state.robot_location or (
                location == "inside_cabinet"
                and state.robot_location == "cabinet"
                and state.cabinet_open
            ):
                actions.append(("pickup", item))
    else:
        actions.append(("drop", state.held_item))

    if state.robot_location == "cabinet":
        if state.cabinet_locked and state.held_item == required_key:
            actions.append(("unlock", required_key))
        if not state.cabinet_locked and not state.cabinet_open:
            actions.append(("open", None))

    if state.held_item in PACKAGES:
        for bin_name, location in BIN_LOCATION.items():
            if state.robot_location == location:
                actions.append(("place", f"{state.held_item}|{bin_name}"))

    return actions


def shortest_plan(
    state: WorldState,
    spec: EpisodeSpec,
    *,
    model_required_key: str | None = None,
) -> tuple[list[Action], int]:
    """Breadth-first high-level planner under an explicit causal model."""
    required_key = model_required_key or spec.required_key
    frontier: deque[tuple[WorldState, list[Action]]] = deque([(state, [])])
    visited = {state}
    expanded = 0

    while frontier:
        current, plan = frontier.popleft()
        expanded += 1
        if goal_reached(current, spec):
            return plan, expanded
        for action in candidate_actions(current, required_key=required_key):
            next_state, valid, violation = transition(
                current,
                action,
                required_key=required_key,
                target_package=spec.target_package,
                target_bin=spec.target_bin,
            )
            if not valid or violation == "wrong_placement" or next_state in visited:
                continue
            visited.add(next_state)
            frontier.append((next_state, plan + [action]))

    raise RuntimeError("No plan found for generated episode")


def shortest_next_location(start: str, destination: str) -> str:
    if start == destination:
        return start
    frontier: deque[tuple[str, str | None]] = deque([(start, None)])
    visited = {start}
    while frontier:
        location, first_step = frontier.popleft()
        for neighbor in GRAPH[location]:
            if neighbor in visited:
                continue
            next_first = neighbor if first_step is None else first_step
            if neighbor == destination:
                return next_first
            visited.add(neighbor)
            frontier.append((neighbor, next_first))
    raise RuntimeError(f"No path from {start} to {destination}")


def no_plan_action(state: WorldState, spec: EpisodeSpec) -> Action:
    """One-step target-directed policy with no prerequisite search.

    The policy can exploit an already-unlocked cabinet, but retrieving a key does
    not improve its one-step task progress, so locked episodes expose the planning
    horizon rather than hidden information or motor noise.
    """
    if state.held_item == spec.target_package:
        destination = BIN_LOCATION[spec.target_bin]
        if state.robot_location == destination:
            return "place", f"{spec.target_package}|{spec.target_bin}"
        return "move", shortest_next_location(state.robot_location, destination)

    if state.cabinet_open:
        if state.robot_location == "cabinet":
            return "pickup", spec.target_package
        return "move", shortest_next_location(state.robot_location, "cabinet")

    if not state.cabinet_locked:
        if state.robot_location == "cabinet":
            return "open", None
        return "move", shortest_next_location(state.robot_location, "cabinet")

    if state.robot_location == "cabinet":
        return "open", None
    return "move", shortest_next_location(state.robot_location, "cabinet")


def remap_binding(action: Action) -> Action:
    verb, argument = action
    if argument is None:
        return action
    mapping = {
        "red_key": "blue_key",
        "blue_key": "red_key",
        "red_package": "blue_package",
        "blue_package": "red_package",
        "left_bin": "right_bin",
        "right_bin": "left_bin",
    }
    if verb in {"pickup", "drop", "unlock"}:
        return verb, mapping.get(argument, argument)
    if verb == "place":
        package, bin_name = argument.split("|", 1)
        return verb, f"{mapping.get(package, package)}|{mapping.get(bin_name, bin_name)}"
    return action


def render_action(action: Action) -> str:
    verb, argument = action
    if verb == "move":
        return f"move to {argument}"
    if verb == "pickup":
        return f"pick up {argument}"
    if verb == "drop":
        return f"put down {argument}"
    if verb == "unlock":
        return f"unlock the cabinet with {argument}"
    if verb == "open":
        return "open the cabinet"
    if verb == "place" and argument is not None:
        package, bin_name = argument.split("|", 1)
        return f"place {package} into {bin_name}"
    return f"{verb} {argument or ''}".strip()


def state_fields(state: WorldState, prefix: str) -> dict[str, Any]:
    return {
        f"{prefix}_robot_location": state.robot_location,
        f"{prefix}_held_item": state.held_item or "",
        f"{prefix}_cabinet_locked": int(state.cabinet_locked),
        f"{prefix}_cabinet_open": int(state.cabinet_open),
    }


def execute_actions(
    *,
    initial: WorldState,
    actions: list[Action],
    spec: EpisodeSpec,
    required_key_for_world: str,
    recorder: RunRecorder | None,
    episode: int,
    condition: str,
) -> dict[str, Any]:
    state = initial
    valid_actions = 0
    invalid_actions = 0
    violations = 0
    first_failure: str | None = None
    max_progress = causal_progress(state, spec)
    executed_steps = 0

    for action_step, action in enumerate(actions):
        if goal_reached(state, spec):
            break
        before = state
        progress_before = causal_progress(before, spec)
        state, valid, violation = transition(
            state,
            action,
            required_key=required_key_for_world,
            target_package=spec.target_package,
            target_bin=spec.target_bin,
        )
        progress_after = causal_progress(state, spec)
        max_progress = max(max_progress, progress_after)
        valid_actions += int(valid)
        invalid_actions += int(not valid)
        violations += int(violation is not None)
        if violation is not None and first_failure is None:
            first_failure = violation
        executed_steps += 1

        if recorder is not None:
            recorder.log_step(
                episode=episode,
                action_step=action_step,
                time_s=float(action_step),
                condition=condition,
                locked_initially=int(spec.locked_initially),
                required_key=spec.required_key,
                target_package=spec.target_package,
                target_bin=spec.target_bin,
                action=action[0],
                argument=action[1] or "",
                valid=int(valid),
                violation=violation or "",
                progress_before=progress_before,
                progress_after=progress_after,
                **state_fields(before, "before"),
                **state_fields(state, "after"),
            )

    return {
        "success": goal_reached(state, spec),
        "valid_actions": valid_actions,
        "invalid_actions": invalid_actions,
        "violations": violations,
        "steps": executed_steps,
        "final_progress": causal_progress(state, spec),
        "max_progress": max_progress,
        "first_failure": first_failure,
    }


def execute_no_plan(
    *,
    initial: WorldState,
    spec: EpisodeSpec,
    max_steps: int,
    recorder: RunRecorder,
    episode: int,
    condition: str,
) -> dict[str, Any]:
    state = initial
    actions: list[Action] = []
    for _ in range(max_steps):
        if goal_reached(state, spec):
            break
        action = no_plan_action(state, spec)
        actions.append(action)
        state, _, _ = transition(
            state,
            action,
            required_key=spec.required_key,
            target_package=spec.target_package,
            target_bin=spec.target_bin,
        )

    return execute_actions(
        initial=initial,
        actions=actions,
        spec=spec,
        required_key_for_world=spec.required_key,
        recorder=recorder,
        episode=episode,
        condition=condition,
    )


def failure_category(condition: str) -> str:
    return {
        "correct_plan": "unexpected_correct_plan_failure",
        "no_plan": "missing_prerequisite_reasoning",
        "random_plan": "plan_order_failure",
        "fluent_wrong_plan": "wrong_causal_model",
        "shuffled_binding": "entity_binding_failure",
    }[condition]


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def run_condition(
    *,
    condition: str,
    cfg: dict[str, Any],
    episode_specs: list[EpisodeSpec],
    output_root: Path,
    command: list[str],
) -> dict[str, Any]:
    seed = int(cfg["seed"])
    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=condition,
        seed=seed,
        config={**cfg, "condition": {"name": condition}},
        repo_root=REPO_ROOT,
        command=command,
    )

    episode_rows: list[dict[str, Any]] = []
    plan_rows: list[dict[str, Any]] = []

    for episode, spec in enumerate(episode_specs):
        initial = initial_state(spec)
        correct_plan, correct_nodes = shortest_plan(initial, spec)
        plan: list[Action] | None = None
        planner_required_key: str | None = None
        planner_nodes = 0
        self_model_success: bool | None = None

        if condition == "correct_plan":
            plan = correct_plan
            planner_required_key = spec.required_key
            planner_nodes = correct_nodes
        elif condition == "random_plan":
            plan = list(correct_plan)
            random.Random(seed + 12_345 + episode).shuffle(plan)
            planner_required_key = spec.required_key
        elif condition == "fluent_wrong_plan":
            planner_required_key = other_key(spec.required_key)
            plan, planner_nodes = shortest_plan(
                initial,
                spec,
                model_required_key=planner_required_key,
            )
        elif condition == "shuffled_binding":
            plan = [remap_binding(action) for action in correct_plan]
            planner_required_key = spec.required_key
        elif condition != "no_plan":
            raise ValueError(f"Unknown condition: {condition}")

        if plan is None:
            result = execute_no_plan(
                initial=initial,
                spec=spec,
                max_steps=int(cfg["no_plan_max_steps"]),
                recorder=recorder,
                episode=episode,
                condition=condition,
            )
            plan_length: int | None = None
        else:
            if condition in {"correct_plan", "fluent_wrong_plan"}:
                model_result = execute_actions(
                    initial=initial,
                    actions=plan,
                    spec=spec,
                    required_key_for_world=str(planner_required_key),
                    recorder=None,
                    episode=episode,
                    condition=f"{condition}_internal_model",
                )
                self_model_success = bool(model_result["success"])

            result = execute_actions(
                initial=initial,
                actions=plan,
                spec=spec,
                required_key_for_world=spec.required_key,
                recorder=recorder,
                episode=episode,
                condition=condition,
            )
            plan_length = len(plan)
            plan_rows.append(
                {
                    "episode": episode,
                    "condition": condition,
                    "locked_initially": spec.locked_initially,
                    "true_required_key": spec.required_key,
                    "planner_required_key": planner_required_key,
                    "target_package": spec.target_package,
                    "target_bin": spec.target_bin,
                    "plan_length": plan_length,
                    "planner_nodes": planner_nodes,
                    "self_model_success": self_model_success,
                    "actions": [
                        {"verb": action[0], "argument": action[1], "text": render_action(action)}
                        for action in plan
                    ],
                }
            )

        optimal_length = len(correct_plan)
        action_validity = result["valid_actions"] / max(1, result["steps"])
        episode_row = {
            "episode": episode,
            "condition": condition,
            "locked_initially": int(spec.locked_initially),
            "success": int(result["success"]),
            "steps": result["steps"],
            "valid_actions": result["valid_actions"],
            "invalid_actions": result["invalid_actions"],
            "action_validity": action_validity,
            "violations": result["violations"],
            "final_progress": result["final_progress"],
            "max_progress": result["max_progress"],
            "first_failure": result["first_failure"] or "",
            "plan_length": plan_length if plan_length is not None else "",
            "optimal_plan_length": optimal_length,
            "planner_nodes": planner_nodes,
            "self_model_success": (
                int(self_model_success) if self_model_success is not None else ""
            ),
            "required_key": spec.required_key,
            "target_package": spec.target_package,
            "target_bin": spec.target_bin,
        }
        episode_rows.append(episode_row)

        if not result["success"]:
            recorder.log_failure(
                category=failure_category(condition),
                step=episode,
                time_s=float(episode),
                details={
                    "locked_initially": spec.locked_initially,
                    "required_key": spec.required_key,
                    "target_package": spec.target_package,
                    "target_bin": spec.target_bin,
                    "first_failure": result["first_failure"],
                    "invalid_actions": result["invalid_actions"],
                    "final_progress": result["final_progress"],
                    "condition": condition,
                },
            )

    write_csv(recorder.run_dir / "episodes.csv", episode_rows)
    with (recorder.run_dir / "plans.jsonl").open("w", encoding="utf-8") as handle:
        for row in plan_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    locked_rows = [row for row in episode_rows if int(row["locked_initially"]) == 1]
    unlocked_rows = [row for row in episode_rows if int(row["locked_initially"]) == 0]
    plan_lengths = [float(row["plan_length"]) for row in episode_rows if row["plan_length"] != ""]
    self_model_values = [
        float(row["self_model_success"])
        for row in episode_rows
        if row["self_model_success"] != ""
    ]

    summary = {
        "condition": condition,
        "episodes": len(episode_rows),
        "success_rate": mean([float(row["success"]) for row in episode_rows]),
        "locked_success_rate": mean([float(row["success"]) for row in locked_rows]),
        "unlocked_success_rate": mean([float(row["success"]) for row in unlocked_rows]),
        "mean_action_validity": mean([float(row["action_validity"]) for row in episode_rows]),
        "mean_invalid_actions": mean([float(row["invalid_actions"]) for row in episode_rows]),
        "mean_violations": mean([float(row["violations"]) for row in episode_rows]),
        "mean_steps": mean([float(row["steps"]) for row in episode_rows]),
        "mean_final_progress": mean([float(row["final_progress"]) for row in episode_rows]),
        "mean_max_progress": mean([float(row["max_progress"]) for row in episode_rows]),
        "mean_plan_length": mean(plan_lengths) if plan_lengths else None,
        "mean_optimal_plan_length": mean(
            [float(row["optimal_plan_length"]) for row in episode_rows]
        ),
        "self_model_success_rate": mean(self_model_values) if self_model_values else None,
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_experiment(cfg: dict[str, Any], *, output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    episode_specs = [
        sample_episode(
            episode,
            seed=int(cfg["seed"]),
            locked_probability=float(cfg["locked_probability"]),
        )
        for episode in range(int(cfg["episodes"]))
    ]

    rows = [
        run_condition(
            condition=str(condition),
            cfg=cfg,
            episode_specs=episode_specs,
            output_root=output_root,
            command=command,
        )
        for condition in cfg["conditions"]
    ]
    write_csv(output_root / "condition_metrics.csv", rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "episodes": int(cfg["episodes"]),
            "locked_probability": float(cfg["locked_probability"]),
            "conditions": [str(condition) for condition in cfg["conditions"]],
            "causal_structure": {
                "hidden_dependency": "cabinet unlock requires one of two keys",
                "inventory_capacity": 1,
                "target": "retrieve target package and place it in the correct bin",
                "planner": "breadth-first search over explicit world state transitions",
            },
            "results_file": "condition_metrics.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use deterministic CI episode count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = copy.deepcopy(cfg)
        cfg["episodes"] = int(cfg["quick_episodes"])

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 31 complete: {len(rows)} reasoning controls")
    print(f"metrics: {output_root / 'condition_metrics.csv'}")
    for row in rows:
        model_success = row["self_model_success_rate"]
        model_text = "n/a" if model_success is None else f"{model_success:.3f}"
        print(
            f"{row['condition']:<20} success={row['success_rate']:.3f} "
            f"locked={row['locked_success_rate']:.3f} "
            f"validity={row['mean_action_validity']:.3f} "
            f"self-model={model_text}"
        )


if __name__ == "__main__":
    main()
