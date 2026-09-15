#!/usr/bin/env python3
"""Lab 33 — sequential continual learning under a shared representation bottleneck.

Three binary tasks A→B→C share a 2-D input and a tiny shared representation,
while each task has its own classification head. Sequential learning therefore
changes a representation that old heads depend on, making representational
forgetting observable without changing the meaning of old labels.

Methods:
- naive_finetune: current-task data only;
- replay: current-task data + correctly labelled old samples;
- quadratic_anchor: penalize drift of the shared trunk from the previous phase;
- replay_shuffled_labels: replay the same old samples with deliberately wrong
  labels, a mechanism negative control for replay.

The experiment records the full performance matrix R[i,j] after each learning
phase and a separate frozen-representation probe matrix for forward transfer.
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab33_continual_learning"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


def set_deterministic(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def make_task_dataset(
    *,
    task_index: int,
    angle_deg: float,
    samples: int,
    seed: int,
    label_noise_std: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed + 1009 * task_index)
    x = torch.randn(samples, 2, generator=generator)
    angle = math.radians(angle_deg)
    direction = torch.tensor([math.cos(angle), math.sin(angle)], dtype=torch.float32)
    noise = label_noise_std * torch.randn(samples, generator=generator)
    y = ((x @ direction + noise) > 0.0).long()
    return x, y


class ContinualNet(torch.nn.Module):
    def __init__(self, *, hidden_dim: int, task_count: int) -> None:
        super().__init__()
        # A deliberately small shared bottleneck. The task-specific heads prevent
        # label-semantic conflict; forgetting comes from trunk drift.
        self.trunk = torch.nn.Linear(2, hidden_dim, bias=False)
        self.heads = torch.nn.ModuleList(
            [torch.nn.Linear(hidden_dim, 2) for _ in range(task_count)]
        )

    def forward(self, x: torch.Tensor, task_index: int) -> torch.Tensor:
        z = self.trunk(x)
        return self.heads[task_index](z)


def accuracy(model: ContinualNet, dataset: tuple[torch.Tensor, torch.Tensor], task: int) -> float:
    model.eval()
    x, y = dataset
    with torch.no_grad():
        pred = model(x, task).argmax(dim=1)
    return float((pred == y).float().mean().item())


def evaluate_all(model: ContinualNet, datasets: list[tuple[torch.Tensor, torch.Tensor]]) -> list[float]:
    return [accuracy(model, dataset, task) for task, dataset in enumerate(datasets)]


def trunk_snapshot(model: ContinualNet) -> list[torch.Tensor]:
    return [parameter.detach().clone() for parameter in model.trunk.parameters()]


def trunk_drift(model: ContinualNet, anchor: list[torch.Tensor]) -> float:
    total = 0.0
    with torch.no_grad():
        for parameter, reference in zip(model.trunk.parameters(), anchor):
            total += float(torch.sum((parameter - reference) ** 2).item())
    return math.sqrt(total)


def tensor_bytes(tensor: torch.Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def replay_memory_bytes(memory: dict[int, tuple[torch.Tensor, torch.Tensor]]) -> int:
    return sum(tensor_bytes(x) + tensor_bytes(y) for x, y in memory.values())


def parameter_bytes(parameters: list[torch.Tensor]) -> int:
    return sum(tensor_bytes(parameter) for parameter in parameters)


def sample_replay_memory(
    *,
    dataset: tuple[torch.Tensor, torch.Tensor],
    task_index: int,
    count: int,
    seed: int,
    shuffle_labels: bool,
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = dataset
    generator = torch.Generator().manual_seed(seed + 6007 * task_index)
    permutation = torch.randperm(len(x), generator=generator)[:count]
    replay_x = x[permutation].clone()
    replay_y = y[permutation].clone()
    if shuffle_labels:
        label_generator = torch.Generator().manual_seed(seed + 9001 * task_index + 17)
        replay_y = replay_y[
            torch.randperm(len(replay_y), generator=label_generator)
        ]
    return replay_x, replay_y


def fit_linear_probe(
    *,
    model: ContinualNet,
    train_dataset: tuple[torch.Tensor, torch.Tensor],
    test_dataset: tuple[torch.Tensor, torch.Tensor],
    train_samples: int,
    steps: int,
    learning_rate: float,
    seed: int,
) -> float:
    """Measure representation transfer with a fresh task head on a frozen trunk."""
    model.eval()
    train_x, train_y = train_dataset
    test_x, test_y = test_dataset
    with torch.no_grad():
        train_z = model.trunk(train_x[:train_samples]).detach()
        test_z = model.trunk(test_x).detach()

    probe = torch.nn.Linear(train_z.shape[1], 2)
    torch.nn.init.zeros_(probe.weight)
    torch.nn.init.zeros_(probe.bias)
    optimizer = torch.optim.SGD(probe.parameters(), lr=learning_rate)
    generator = torch.Generator().manual_seed(seed)
    batch_size = min(64, train_samples)
    for _ in range(steps):
        indices = torch.randint(train_samples, (batch_size,), generator=generator)
        loss = F.cross_entropy(probe(train_z[indices]), train_y[:train_samples][indices])
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        prediction = probe(test_z).argmax(dim=1)
    return float((prediction == test_y).float().mean().item())


def evaluate_representation_probes(
    *,
    model: ContinualNet,
    train_sets: list[tuple[torch.Tensor, torch.Tensor]],
    test_sets: list[tuple[torch.Tensor, torch.Tensor]],
    cfg: dict[str, Any],
    phase_seed: int,
) -> list[float]:
    return [
        fit_linear_probe(
            model=model,
            train_dataset=train_sets[task],
            test_dataset=test_sets[task],
            train_samples=int(cfg["probe_train_samples"]),
            steps=int(cfg["probe_steps"]),
            learning_rate=float(cfg["probe_learning_rate"]),
            seed=phase_seed + 97 * task,
        )
        for task in range(len(train_sets))
    ]


def train_phase(
    *,
    model: ContinualNet,
    task_index: int,
    train_sets: list[tuple[torch.Tensor, torch.Tensor]],
    replay_memory: dict[int, tuple[torch.Tensor, torch.Tensor]],
    method: str,
    anchor: list[torch.Tensor] | None,
    initial_trunk: list[torch.Tensor],
    cfg: dict[str, Any],
    recorder: RunRecorder,
    global_step_start: int,
) -> int:
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=float(cfg["learning_rate"]))
    steps = int(cfg["train_steps_per_task"])
    batch_size = int(cfg["batch_size"])
    replay_weight = float(cfg["replay_loss_weight"])
    anchor_lambda = float(cfg["anchor_lambda"])
    x, y = train_sets[task_index]
    generator = torch.Generator().manual_seed(int(cfg["seed"]) + 101 * task_index)

    global_step = global_step_start
    for local_step in range(steps):
        indices = torch.randint(len(x), (batch_size,), generator=generator)
        current_loss = F.cross_entropy(model(x[indices], task_index), y[indices])
        replay_loss = torch.tensor(0.0)
        regularization_loss = torch.tensor(0.0)

        if method in {"replay", "replay_shuffled_labels"} and replay_memory:
            losses: list[torch.Tensor] = []
            per_task_batch = max(1, batch_size // len(replay_memory))
            for old_task, (replay_x, replay_y) in replay_memory.items():
                replay_indices = torch.randint(
                    len(replay_x),
                    (per_task_batch,),
                    generator=generator,
                )
                losses.append(
                    F.cross_entropy(
                        model(replay_x[replay_indices], old_task),
                        replay_y[replay_indices],
                    )
                )
            replay_loss = torch.stack(losses).mean()

        if method == "quadratic_anchor" and anchor is not None:
            penalty = torch.tensor(0.0)
            for parameter, reference in zip(model.trunk.parameters(), anchor):
                penalty = penalty + torch.sum((parameter - reference) ** 2)
            regularization_loss = anchor_lambda * penalty

        total_loss = current_loss + replay_weight * replay_loss + regularization_loss
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()

        recorder.log_step(
            step=global_step,
            time_s=float(global_step),
            phase=task_index,
            current_task=task_index,
            local_step=local_step,
            current_loss=float(current_loss.detach().item()),
            replay_loss=float(replay_loss.detach().item()),
            regularization_loss=float(regularization_loss.detach().item()),
            total_loss=float(total_loss.detach().item()),
            replay_tasks=len(replay_memory),
            replay_samples=sum(len(memory[0]) for memory in replay_memory.values()),
            trunk_drift_from_initial=trunk_drift(model, initial_trunk),
            trunk_drift_from_phase_anchor=(
                trunk_drift(model, anchor) if anchor is not None else 0.0
            ),
        )
        global_step += 1

    return global_step


def compute_metrics(
    *,
    performance: np.ndarray,
    probes: np.ndarray,
) -> dict[str, float]:
    # performance rows: initial, after A, after B, after C.
    task_count = performance.shape[1]
    final = performance[-1]
    diagonal = np.array([performance[task + 1, task] for task in range(task_count)])

    old_task_forgetting: list[float] = []
    backward_transfer: list[float] = []
    for task in range(task_count - 1):
        best_after_learning = float(np.max(performance[task + 1 :, task]))
        old_task_forgetting.append(max(0.0, best_after_learning - float(final[task])))
        backward_transfer.append(float(final[task] - performance[task + 1, task]))

    # Probe-based FWT avoids conflating representation transfer with random,
    # untrained task-specific heads.
    forward_transfer: list[float] = []
    for task in range(1, task_count):
        before_learning = probes[task, task]  # after previous phase; row task
        initial = probes[0, task]
        forward_transfer.append(float(before_learning - initial))

    return {
        "final_average_accuracy": float(np.mean(final)),
        "average_old_task_forgetting": float(np.mean(old_task_forgetting)),
        "backward_transfer": float(np.mean(backward_transfer)),
        "forward_transfer_probe": float(np.mean(forward_transfer)),
        "mean_current_task_plasticity": float(np.mean(diagonal)),
        "final_task_accuracy": float(final[-1]),
        "final_task_A_accuracy": float(final[0]),
        "final_task_B_accuracy": float(final[1]),
        "final_task_C_accuracy": float(final[2]),
    }


def run_method(
    *,
    method: str,
    cfg: dict[str, Any],
    train_sets: list[tuple[torch.Tensor, torch.Tensor]],
    test_sets: list[tuple[torch.Tensor, torch.Tensor]],
    output_root: Path,
    command: list[str],
) -> dict[str, Any]:
    seed = int(cfg["seed"])
    set_deterministic(seed)
    task_count = len(train_sets)
    model = ContinualNet(hidden_dim=int(cfg["hidden_dim"]), task_count=task_count)
    initial_trunk = trunk_snapshot(model)
    initial_parameter_count = sum(parameter.numel() for parameter in model.parameters())

    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=method,
        seed=seed,
        config={**cfg, "condition": {"method": method}},
        repo_root=REPO_ROOT,
        command=command,
    )

    performance_rows: list[list[float]] = [evaluate_all(model, test_sets)]
    probe_rows: list[list[float]] = [
        evaluate_representation_probes(
            model=model,
            train_sets=train_sets,
            test_sets=test_sets,
            cfg=cfg,
            phase_seed=seed + 3000,
        )
    ]
    replay_memory: dict[int, tuple[torch.Tensor, torch.Tensor]] = {}
    anchor: list[torch.Tensor] | None = None
    global_step = 0

    for task_index in range(task_count):
        global_step = train_phase(
            model=model,
            task_index=task_index,
            train_sets=train_sets,
            replay_memory=replay_memory,
            method=method,
            anchor=anchor,
            initial_trunk=initial_trunk,
            cfg=cfg,
            recorder=recorder,
            global_step_start=global_step,
        )

        performance_rows.append(evaluate_all(model, test_sets))
        probe_rows.append(
            evaluate_representation_probes(
                model=model,
                train_sets=train_sets,
                test_sets=test_sets,
                cfg=cfg,
                phase_seed=seed + 3000 + 211 * (task_index + 1),
            )
        )

        if method in {"replay", "replay_shuffled_labels"}:
            replay_memory[task_index] = sample_replay_memory(
                dataset=train_sets[task_index],
                task_index=task_index,
                count=int(cfg["replay_samples_per_task"]),
                seed=seed,
                shuffle_labels=(method == "replay_shuffled_labels"),
            )

        if method == "quadratic_anchor":
            anchor = trunk_snapshot(model)

    performance = np.asarray(performance_rows, dtype=np.float64)
    probes = np.asarray(probe_rows, dtype=np.float64)
    metrics = compute_metrics(performance=performance, probes=probes)

    forgetting_threshold = float(cfg["forgetting_event_threshold"])
    for task in range(task_count - 1):
        learned_accuracy = float(performance[task + 1, task])
        final_accuracy = float(performance[-1, task])
        loss = learned_accuracy - final_accuracy
        if loss > forgetting_threshold:
            recorder.log_failure(
                category="catastrophic_forgetting",
                step=task,
                time_s=float(task),
                details={
                    "task": task,
                    "accuracy_after_learning": learned_accuracy,
                    "final_accuracy": final_accuracy,
                    "accuracy_loss": loss,
                    "threshold": forgetting_threshold,
                    "method": method,
                },
            )

    task_names = [str(task["name"]) for task in cfg["tasks"]]
    performance_csv_rows: list[dict[str, Any]] = []
    probe_csv_rows: list[dict[str, Any]] = []
    phase_names = ["initial"] + [f"after_{name}" for name in task_names]
    for phase, phase_name in enumerate(phase_names):
        performance_csv_rows.append(
            {
                "phase": phase,
                "phase_name": phase_name,
                **{
                    f"task_{task_names[task]}_accuracy": float(performance[phase, task])
                    for task in range(task_count)
                },
            }
        )
        probe_csv_rows.append(
            {
                "phase": phase,
                "phase_name": phase_name,
                **{
                    f"task_{task_names[task]}_probe_accuracy": float(probes[phase, task])
                    for task in range(task_count)
                },
            }
        )

    write_csv(recorder.run_dir / "performance_matrix.csv", performance_csv_rows)
    write_csv(recorder.run_dir / "probe_matrix.csv", probe_csv_rows)

    final_parameter_count = sum(parameter.numel() for parameter in model.parameters())
    replay_bytes = replay_memory_bytes(replay_memory)
    anchor_bytes = parameter_bytes(anchor or [])
    summary = {
        "method": method,
        "seed": seed,
        **metrics,
        "replay_memory_samples": sum(len(memory[0]) for memory in replay_memory.values()),
        "replay_memory_bytes": replay_bytes,
        "anchor_memory_bytes": anchor_bytes,
        "extra_method_memory_bytes": replay_bytes + anchor_bytes,
        "parameter_count": final_parameter_count,
        "parameter_growth": final_parameter_count - initial_parameter_count,
        "final_trunk_drift_from_initial": trunk_drift(model, initial_trunk),
        "optimizer_steps": global_step,
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_experiment(cfg: dict[str, Any], *, output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    tasks = cfg["tasks"]
    train_sets = [
        make_task_dataset(
            task_index=index,
            angle_deg=float(task["angle_deg"]),
            samples=int(cfg["train_samples_per_task"]),
            seed=int(cfg["seed"]) + 10_000,
            label_noise_std=float(cfg["label_noise_std"]),
        )
        for index, task in enumerate(tasks)
    ]
    test_sets = [
        make_task_dataset(
            task_index=index,
            angle_deg=float(task["angle_deg"]),
            samples=int(cfg["test_samples_per_task"]),
            seed=int(cfg["seed"]) + 20_000,
            label_noise_std=float(cfg["label_noise_std"]),
        )
        for index, task in enumerate(tasks)
    ]

    rows = [
        run_method(
            method=str(method),
            cfg=cfg,
            train_sets=train_sets,
            test_sets=test_sets,
            output_root=output_root,
            command=command,
        )
        for method in cfg["methods"]
    ]
    write_csv(output_root / "method_metrics.csv", rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "task_order": [str(task["name"]) for task in tasks],
            "methods": [str(method) for method in cfg["methods"]],
            "shared_capacity": {
                "input_dim": 2,
                "hidden_dim": int(cfg["hidden_dim"]),
                "task_specific_heads": len(tasks),
            },
            "results_file": "method_metrics.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use a smaller deterministic CI setting.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = copy.deepcopy(cfg)
        cfg["test_samples_per_task"] = min(int(cfg["test_samples_per_task"]), 2000)
        cfg["probe_train_samples"] = min(int(cfg["probe_train_samples"]), 120)
        cfg["probe_steps"] = min(int(cfg["probe_steps"]), 60)

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_experiment(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 33 complete: {len(rows)} continual-learning methods")
    print(f"metrics: {output_root / 'method_metrics.csv'}")
    for row in rows:
        print(
            f"{row['method']:<24} final-avg={row['final_average_accuracy']:.3f} "
            f"forget={row['average_old_task_forgetting']:.3f} "
            f"plasticity={row['mean_current_task_plasticity']:.3f} "
            f"BWT={row['backward_transfer']:+.3f} "
            f"memory={row['extra_method_memory_bytes']}B"
        )


if __name__ == "__main__":
    main()
