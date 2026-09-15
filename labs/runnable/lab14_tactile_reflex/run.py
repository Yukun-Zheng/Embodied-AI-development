#!/usr/bin/env python3
"""Lab 14 — multi-rate tactile reflex under a transient friction-loss event.

A gripper holds an object with a commanded normal force. A short friction drop
creates a slip event. We compare:

- slow_policy_only: a 5 Hz high-level loop samples slip and changes grip force;
- fast_tactile_reflex: a 200 Hz tactile residual loop reacts immediately;
- delayed_tactile_reflex: the same 200 Hz residual loop sees tactile data delayed
  by 120 ms.

The experiment isolates timing. Plant, event, controller gains and paired tactile
noise are identical across modes.
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

LAB_ID = "lab14_tactile_reflex"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


def paired_event_start(*, base_seed: int, episode: int, low: float, high: float) -> float:
    rng = np.random.default_rng(base_seed + episode * 1_000_003 + 71)
    return float(rng.uniform(low, high))


def paired_tactile_noise(*, base_seed: int, episode: int, step: int, std: float) -> float:
    rng = np.random.default_rng(base_seed * 10_000_019 + episode * 1009 + step * 97 + 13)
    return float(rng.normal(0.0, std))


def delayed_signal(history: list[float], *, now: float, delay: float, dt: float) -> float:
    if delay <= 0.0:
        return history[-1]
    delayed_time = now - delay
    if delayed_time < 0.0:
        return 0.0
    index = int(math.floor(delayed_time / dt + 1e-9))
    if index < 0 or index >= len(history):
        return 0.0
    return float(history[index])


def simulate_mode(
    *,
    mode: str,
    cfg: dict[str, Any],
    output_root: Path,
    command: list[str],
) -> dict[str, Any]:
    valid_modes = {"slow_policy_only", "fast_tactile_reflex", "delayed_tactile_reflex"}
    if mode not in valid_modes:
        raise ValueError(f"Unknown mode: {mode}")

    seed = int(cfg["seed"])
    episodes = int(cfg["episodes"])
    dt = float(cfg["dt"])
    duration = float(cfg["duration_s"])
    slow_period = float(cfg["slow_policy_period_s"])
    tactile_period = float(cfg["tactile_period_s"])
    base_grip = float(cfg["base_grip_force_n"])
    rescue_grip = float(cfg["rescue_grip_force_n"])
    tau_grip = float(cfg["grip_actuator_time_constant_s"])
    load = float(cfg["object_load_n"])
    mu_nominal = float(cfg["nominal_friction"])
    mu_slip = float(cfg["slip_friction"])
    event_low, event_high = [float(x) for x in cfg["slip_event_start_range_s"]]
    event_duration = float(cfg["slip_event_duration_s"])
    slip_gain = float(cfg["slip_gain"])
    slip_damping = float(cfg["slip_damping"])
    drop_distance = float(cfg["drop_displacement_m"])
    tactile_noise_std = float(cfg["tactile_noise_std"])
    threshold = float(cfg["slip_detection_threshold"])
    tactile_delay = float(cfg["delayed_tactile_s"]) if mode == "delayed_tactile_reflex" else 0.0
    release_hold = float(cfg["release_hold_s"])

    if dt <= 0 or duration <= 0 or slow_period <= 0 or tactile_period <= 0:
        raise ValueError("time scales must be positive")
    if abs(tactile_period - dt) > 1e-12:
        raise ValueError("reference toy implementation currently requires tactile_period_s == dt")
    if event_duration >= slow_period:
        raise ValueError("The reference mechanism requires a slip event shorter than the slow policy period")

    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=mode,
        seed=seed,
        config={**cfg, "condition": {"mode": mode, "effective_tactile_delay_s": tactile_delay}},
        repo_root=REPO_ROOT,
        command=command,
    )

    dropped_flags: list[int] = []
    final_slips: list[float] = []
    max_slips: list[float] = []
    reaction_latencies: list[float] = []
    reaction_detected: list[int] = []
    peak_grip_forces: list[float] = []
    extra_grip_energy: list[float] = []
    event_missed_by_slow_loop: list[int] = []
    global_step = 0

    n_steps = int(round(duration / dt))

    for episode in range(episodes):
        event_start = paired_event_start(
            base_seed=seed,
            episode=episode,
            low=event_low,
            high=event_high,
        )
        event_end = event_start + event_duration

        grip_force = base_grip
        grip_command = base_grip
        slip_displacement = 0.0
        slip_velocity = 0.0
        next_slow_update = 0.0
        tactile_history: list[float] = []
        reaction_time: float | None = None
        slow_saw_event = False
        dropped = False
        peak_force = grip_force
        force_residual_energy = 0.0
        max_slip = 0.0

        for step in range(n_steps):
            t = step * dt
            event_active = event_start <= t < event_end
            friction = mu_slip if event_active else mu_nominal
            friction_capacity = friction * grip_force
            grip_margin = friction_capacity - load
            true_slip_drive = max(-grip_margin, 0.0)

            tactile_noise = paired_tactile_noise(
                base_seed=seed,
                episode=episode,
                step=step,
                std=tactile_noise_std,
            )
            tactile_signal = max(0.0, true_slip_drive + tactile_noise)
            tactile_history.append(tactile_signal)

            # High-level policy: slow periodic update. In slow-only mode it is
            # solely responsible for reacting to slip. In reflex modes it only
            # maintains the nominal grasp command; the fast residual owns slip.
            if t + 1e-12 >= next_slow_update:
                next_slow_update += slow_period
                if mode == "slow_policy_only":
                    if tactile_signal > threshold:
                        grip_command = rescue_grip
                        slow_saw_event = slow_saw_event or event_active
                        if reaction_time is None and t >= event_start:
                            reaction_time = t - event_start
                    else:
                        grip_command = base_grip
                else:
                    grip_command = base_grip

            if mode in {"fast_tactile_reflex", "delayed_tactile_reflex"}:
                reflex_signal = delayed_signal(
                    tactile_history,
                    now=t,
                    delay=tactile_delay,
                    dt=dt,
                )
                if reflex_signal > threshold:
                    grip_command = rescue_grip
                    if reaction_time is None and t >= event_start:
                        reaction_time = t - event_start
                elif t >= event_end + release_hold:
                    grip_command = base_grip
            else:
                reflex_signal = float("nan")

            # First-order gripper force actuator.
            grip_force += (grip_command - grip_force) * dt / tau_grip
            peak_force = max(peak_force, grip_force)
            force_residual_energy += (grip_force - base_grip) ** 2 * dt

            # Slip dynamics. Only insufficient friction can accelerate slip;
            # velocity then decays under damping after contact margin recovers.
            slip_acceleration = slip_gain * true_slip_drive - slip_damping * slip_velocity
            slip_velocity = max(0.0, slip_velocity + slip_acceleration * dt)
            slip_displacement += slip_velocity * dt
            max_slip = max(max_slip, slip_displacement)

            recorder.log_step(
                step=global_step,
                time_s=t,
                episode=episode,
                episode_step=step,
                event_start_s=event_start,
                event_active=int(event_active),
                friction=friction,
                grip_force_n=grip_force,
                grip_command_n=grip_command,
                friction_capacity_n=friction_capacity,
                grip_margin_n=grip_margin,
                tactile_signal=tactile_signal,
                reflex_signal=reflex_signal,
                slip_drive=true_slip_drive,
                slip_velocity_m_s=slip_velocity,
                slip_displacement_m=slip_displacement,
                dropped=int(slip_displacement >= drop_distance),
            )
            global_step += 1

            if slip_displacement >= drop_distance:
                dropped = True
                recorder.log_failure(
                    category="object_drop",
                    step=episode,
                    time_s=t,
                    details={
                        "mode": mode,
                        "event_start_s": event_start,
                        "event_duration_s": event_duration,
                        "slip_displacement_m": slip_displacement,
                        "drop_threshold_m": drop_distance,
                        "reaction_latency_s": reaction_time,
                    },
                )
                break

        dropped_flags.append(int(dropped))
        final_slips.append(slip_displacement)
        max_slips.append(max_slip)
        reaction_detected.append(int(reaction_time is not None))
        if reaction_time is not None:
            reaction_latencies.append(reaction_time)
        peak_grip_forces.append(peak_force)
        extra_grip_energy.append(force_residual_energy)
        event_missed_by_slow_loop.append(int(mode == "slow_policy_only" and not slow_saw_event))

    finite_reaction_mean = (
        float(np.mean(reaction_latencies)) if reaction_latencies else float("nan")
    )
    summary = {
        "mode": mode,
        "seed": seed,
        "episodes": episodes,
        "slow_policy_period_s": slow_period,
        "tactile_period_s": tactile_period,
        "effective_tactile_delay_s": tactile_delay,
        "slip_event_duration_s": event_duration,
        "drop_rate": float(np.mean(dropped_flags)),
        "object_retention_rate": float(1.0 - np.mean(dropped_flags)),
        "mean_final_slip_displacement_m": float(np.mean(final_slips)),
        "p95_max_slip_displacement_m": float(np.percentile(max_slips, 95.0)),
        "reaction_detection_rate": float(np.mean(reaction_detected)),
        "mean_reaction_latency_s": finite_reaction_mean,
        "mean_peak_grip_force_n": float(np.mean(peak_grip_forces)),
        "mean_extra_grip_energy_n2s": float(np.mean(extra_grip_energy)),
        "slow_event_miss_rate": float(np.mean(event_missed_by_slow_loop)),
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_experiment(cfg: dict[str, Any], *, output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    rows = [
        simulate_mode(
            mode=str(mode),
            cfg=cfg,
            output_root=output_root,
            command=command,
        )
        for mode in cfg["modes"]
    ]
    write_csv(output_root / "mode_metrics.csv", rows)
    write_json(
        output_root / "experiment_manifest.json",
        {
            "lab_id": LAB_ID,
            "seed": int(cfg["seed"]),
            "episodes": int(cfg["episodes"]),
            "modes": [str(x) for x in cfg["modes"]],
            "paired_randomness": "slip event phase and tactile noise are paired across modes",
            "results_file": "mode_metrics.csv",
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
    print(f"Lab 14 complete: {len(rows)} multi-rate tactile conditions")
    print(f"metrics: {output_root / 'mode_metrics.csv'}")
    for row in rows:
        print(
            f"{row['mode']:<28} drop={row['drop_rate']:.3f} "
            f"p95-slip={1000.0 * row['p95_max_slip_displacement_m']:.3f}mm "
            f"reaction={1000.0 * row['mean_reaction_latency_s']:.1f}ms "
            f"detect={row['reaction_detection_rate']:.3f}"
        )


if __name__ == "__main__":
    main()
