#!/usr/bin/env python3
"""Lab 27 — long-horizon memory in a partially observable embodied task.

A mission card is visible only at the beginning of each episode. The robot then
passes through 4/10/16 distractor subtasks before three memory-dependent physical
choices: which object to pick, which gate to traverse, and which destination bin
to use. Later observations deliberately omit the original bindings.

The experiment separates recent-frame context from persistent episodic and
semantic memory, and includes matched-content negative controls.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab27_long_horizon_memory"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"

TARGET_OBJECTS = ("red_block", "blue_block", "green_block", "yellow_block")
ACCESS_GATES = ("north_gate", "east_gate", "south_gate", "west_gate")
DESTINATION_BINS = ("bin_A", "bin_B", "bin_C", "bin_D")
FIELD_VALUES: dict[str, tuple[str, ...]] = {
    "target_object": TARGET_OBJECTS,
    "access_gate": ACCESS_GATES,
    "destination_bin": DESTINATION_BINS,
}


@dataclass(frozen=True)
class Mission:
    target_object: str
    access_gate: str
    destination_bin: str

    def value(self, field: str) -> str:
        return str(getattr(self, field))


def balanced_mission(index: int) -> Mission:
    """Enumerate all 4^3 mission bindings exactly once every 64 episodes."""
    return Mission(
        target_object=TARGET_OBJECTS[index % 4],
        access_gate=ACCESS_GATES[(index // 4) % 4],
        destination_bin=DESTINATION_BINS[(index // 16) % 4],
    )


def json_bytes(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))


class MemoryBase:
    def observe(self, observation: dict[str, Any]) -> None:
        del observation

    def recall(self, field: str, candidates: tuple[str, ...]) -> tuple[str, int, str]:
        return candidates[0], 0, "fallback"

    def bytes_used(self) -> int:
        return 0

    def slots_used(self) -> int:
        return 0


class FrameContextMemory(MemoryBase):
    def __init__(self, window: int) -> None:
        self.events: deque[dict[str, Any]] = deque(maxlen=window)

    def observe(self, observation: dict[str, Any]) -> None:
        self.events.append(dict(observation))

    def recall(self, field: str, candidates: tuple[str, ...]) -> tuple[str, int, str]:
        scanned = 0
        for event in reversed(self.events):
            scanned += 1
            if event.get("type") == "mission_card":
                return str(event[field]), scanned, "frame_context"
        return candidates[0], scanned, "fallback"

    def bytes_used(self) -> int:
        return json_bytes(list(self.events))

    def slots_used(self) -> int:
        return len(self.events)


class EpisodicLogMemory(MemoryBase):
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def observe(self, observation: dict[str, Any]) -> None:
        self.events.append(dict(observation))

    def recall(self, field: str, candidates: tuple[str, ...]) -> tuple[str, int, str]:
        scanned = 0
        for event in reversed(self.events):
            scanned += 1
            if event.get("type") == "mission_card":
                return str(event[field]), scanned, "episodic_log"
        return candidates[0], scanned, "fallback"

    def bytes_used(self) -> int:
        return json_bytes(self.events)

    def slots_used(self) -> int:
        return len(self.events)


class SemanticMemory(MemoryBase):
    def __init__(self, mode: str = "correct") -> None:
        self.mode = mode
        self.facts: dict[str, str] = {}

    def observe(self, observation: dict[str, Any]) -> None:
        if observation.get("type") != "mission_card":
            return

        if self.mode == "correct":
            self.facts = {
                field: str(observation[field])
                for field in ("target_object", "access_gate", "destination_bin")
            }
            return

        if self.mode == "shuffled":
            self.facts = {}
            for field, values in FIELD_VALUES.items():
                value = str(observation[field])
                self.facts[field] = values[(values.index(value) + 1) % len(values)]
            return

        if self.mode == "unrelated":
            # Same number of persistent fact slots as the semantic condition,
            # but none contains mission-relevant information.
            self.facts = {
                "weather": "clear",
                "floor": "dry",
                "battery": "nominal",
            }
            return

        raise ValueError(f"Unknown semantic-memory mode: {self.mode}")

    def recall(self, field: str, candidates: tuple[str, ...]) -> tuple[str, int, str]:
        if field in self.facts:
            return self.facts[field], 1, self.mode
        return candidates[0], 1, "fallback"

    def bytes_used(self) -> int:
        return json_bytes(self.facts)

    def slots_used(self) -> int:
        return len(self.facts)


def make_memory(condition: str, cfg: dict[str, Any]) -> MemoryBase:
    if condition == "no_memory":
        return MemoryBase()
    if condition == "frame_context":
        return FrameContextMemory(int(cfg["frame_context_window"]))
    if condition == "episodic_log":
        return EpisodicLogMemory()
    if condition == "semantic_memory":
        return SemanticMemory("correct")
    if condition == "shuffled_memory":
        return SemanticMemory("shuffled")
    if condition == "unrelated_memory":
        return SemanticMemory("unrelated")
    raise ValueError(f"Unknown condition: {condition}")


def mission_observation(mission: Mission) -> dict[str, Any]:
    return {
        "type": "mission_card",
        "target_object": mission.target_object,
        "access_gate": mission.access_gate,
        "destination_bin": mission.destination_bin,
    }


def distractor_observation(
    *, episode: int, horizon: int, distractor_index: int, cfg: dict[str, Any]
) -> dict[str, Any]:
    rng = random.Random(
        int(cfg["seed"])
        + 100_003 * horizon
        + 1_009 * episode
        + 37 * distractor_index
    )
    return {
        "type": "distractor_subtask",
        "station": rng.randrange(int(cfg["distractor_station_count"])),
        "visual_token": rng.randrange(int(cfg["distractor_token_count"])),
        "subtask_index": distractor_index,
    }


def query_observation(field: str) -> dict[str, Any]:
    return {
        "type": "memory_query",
        "field": field,
        "candidates": list(FIELD_VALUES[field]),
    }


def log_observation(
    recorder: RunRecorder,
    *,
    episode: int,
    horizon: int,
    step: int,
    phase: str,
    observation: dict[str, Any],
    memory: MemoryBase,
    selected: str = "",
    expected: str = "",
    correct: bool | None = None,
    retrieval_cost: int = 0,
    retrieval_source: str = "",
) -> None:
    recorder.log_step(
        episode=episode,
        distractor_horizon=horizon,
        step=step,
        phase=phase,
        observation_type=observation.get("type", ""),
        observation_json=json.dumps(observation, ensure_ascii=False, sort_keys=True),
        selected=selected,
        expected=expected,
        correct="" if correct is None else int(correct),
        retrieval_cost=retrieval_cost,
        retrieval_source=retrieval_source,
        memory_slots=memory.slots_used(),
        memory_bytes=memory.bytes_used(),
    )


def run_episode(
    *,
    condition: str,
    horizon: int,
    episode: int,
    cfg: dict[str, Any],
    recorder: RunRecorder,
) -> dict[str, Any]:
    mission = balanced_mission(episode)
    memory = make_memory(condition, cfg)
    step = 0

    cue = mission_observation(mission)
    memory.observe(cue)
    log_observation(
        recorder,
        episode=episode,
        horizon=horizon,
        step=step,
        phase="mission",
        observation=cue,
        memory=memory,
    )
    step += 1

    for distractor_index in range(horizon):
        observation = distractor_observation(
            episode=episode,
            horizon=horizon,
            distractor_index=distractor_index,
            cfg=cfg,
        )
        memory.observe(observation)
        log_observation(
            recorder,
            episode=episode,
            horizon=horizon,
            step=step,
            phase="distractor",
            observation=observation,
            memory=memory,
        )
        step += 1

    correct_count = 0
    total_retrieval_cost = 0
    sources: list[str] = []

    for field in cfg["decision_fields"]:
        field = str(field)
        observation = query_observation(field)
        # The agent sees the current query before selecting an action. The query
        # never re-exposes the mission binding.
        memory.observe(observation)
        candidates = FIELD_VALUES[field]
        selected, retrieval_cost, source = memory.recall(field, candidates)
        expected = mission.value(field)
        correct = selected == expected
        correct_count += int(correct)
        total_retrieval_cost += retrieval_cost
        sources.append(source)

        log_observation(
            recorder,
            episode=episode,
            horizon=horizon,
            step=step,
            phase=f"decision:{field}",
            observation=observation,
            memory=memory,
            selected=selected,
            expected=expected,
            correct=correct,
            retrieval_cost=retrieval_cost,
            retrieval_source=source,
        )
        if not correct:
            recorder.log_failure(
                category="memory_dependent_decision_error",
                step=step,
                time_s=float(step),
                details={
                    "episode": episode,
                    "distractor_horizon": horizon,
                    "field": field,
                    "selected": selected,
                    "expected": expected,
                    "retrieval_source": source,
                },
            )
        step += 1

    decision_count = len(cfg["decision_fields"])
    return {
        "condition": condition,
        "episode": episode,
        "distractor_horizon": horizon,
        "subtask_count": horizon + decision_count,
        "context_window": int(cfg["frame_context_window"]),
        "task_success": int(correct_count == decision_count),
        "query_accuracy": correct_count / decision_count,
        "correct_decisions": correct_count,
        "decision_count": decision_count,
        "retrieval_cost": total_retrieval_cost,
        "memory_slots": memory.slots_used(),
        "memory_bytes": memory.bytes_used(),
        "retrieval_sources": ";".join(sources),
        "target_object": mission.target_object,
        "access_gate": mission.access_gate,
        "destination_bin": mission.destination_bin,
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, float | int]:
    if not rows:
        raise ValueError("Cannot aggregate empty rows")
    n = len(rows)
    return {
        "episodes": n,
        "task_success_rate": sum(float(row["task_success"]) for row in rows) / n,
        "query_accuracy": sum(float(row["query_accuracy"]) for row in rows) / n,
        "avg_retrieval_cost": sum(float(row["retrieval_cost"]) for row in rows) / n,
        "avg_memory_slots": sum(float(row["memory_slots"]) for row in rows) / n,
        "avg_memory_bytes": sum(float(row["memory_bytes"]) for row in rows) / n,
    }


def run_experiment(cfg: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    all_episode_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []
    horizon_rows: list[dict[str, Any]] = []

    episodes_per_horizon = int(cfg["episodes_per_horizon"])
    horizons = [int(value) for value in cfg["distractor_horizons"]]

    for condition in cfg["conditions"]:
        condition = str(condition)
        recorder = RunRecorder(
            output_root=output_root / "runs",
            lab_id=LAB_ID,
            condition=condition,
            seed=int(cfg["seed"]),
            config=cfg,
            repo_root=REPO_ROOT,
        )
        condition_episode_rows: list[dict[str, Any]] = []

        for horizon in horizons:
            horizon_episode_rows: list[dict[str, Any]] = []
            for episode in range(episodes_per_horizon):
                row = run_episode(
                    condition=condition,
                    horizon=horizon,
                    episode=episode,
                    cfg=cfg,
                    recorder=recorder,
                )
                all_episode_rows.append(row)
                condition_episode_rows.append(row)
                horizon_episode_rows.append(row)

            horizon_rows.append(
                {
                    "condition": condition,
                    "distractor_horizon": horizon,
                    "subtask_count": horizon + len(cfg["decision_fields"]),
                    **aggregate(horizon_episode_rows),
                }
            )

        condition_summary = aggregate(condition_episode_rows)
        condition_rows.append({"condition": condition, **condition_summary})
        recorder.finalize(condition_summary)

    write_csv(output_root / "episode_metrics.csv", all_episode_rows)
    write_csv(output_root / "condition_metrics.csv", condition_rows)
    write_csv(output_root / "horizon_metrics.csv", horizon_rows)
    write_json(
        output_root / "experiment_summary.json",
        {
            "lab_id": LAB_ID,
            "conditions": list(cfg["conditions"]),
            "distractor_horizons": horizons,
            "episodes_per_horizon": episodes_per_horizon,
            "context_window": int(cfg["frame_context_window"]),
            "mission_space_size": 64,
            "paired_balanced_missions": True,
            "task_adaptation_steps": 0,
        },
    )

    print("Lab 27 long-horizon memory experiment complete")
    for row in condition_rows:
        print(
            f"{row['condition']:<20} "
            f"success={float(row['task_success_rate']):.3f} "
            f"query_acc={float(row['query_accuracy']):.3f} "
            f"retrieval={float(row['avg_retrieval_cost']):.1f} "
            f"memory_bytes={float(row['avg_memory_bytes']):.1f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=Path("/tmp/lab27_memory"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["episodes_per_horizon"] = int(cfg["quick_episodes_per_horizon"])

    run_experiment(cfg, args.output)


if __name__ == "__main__":
    main()
