#!/usr/bin/env python3
"""Lab 22 — asynchronous policy execution on a controlled physical toy system.

The experiment uses a noisy double-integrator plant and an action-chunk policy.
It explicitly models policy request time, inference completion time, chunk source
time and control execution time. Three executors are compared:

- sync_hold: block on inference and hold the previous command;
- async_queue: keep moving while inference runs, then execute the new chunk from
  index 0 even though it was planned from an older state;
- async_rebase: keep moving while inference runs, then skip actions whose intended
  timestamps are already in the past (a minimal latency-aware/RTC-like mechanism).

This is a mechanism experiment, not a reproduction of any proprietary RTC method.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.runnable.common import RunRecorder, load_json, write_csv, write_json  # noqa: E402

LAB_ID = "lab22_async_execution"
DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "default.json"


@dataclass
class PendingChunk:
    observation_time: float
    ready_time: float
    chunk: np.ndarray


@dataclass
class ActiveChunk:
    observation_time: float
    chunk: np.ndarray
    index: int = 0


def target_state(t: float, cfg: dict[str, Any]) -> tuple[float, float]:
    target_cfg = cfg["target"]
    amplitude = float(target_cfg["amplitude"])
    frequency = float(target_cfg["frequency_hz"])
    omega = 2.0 * math.pi * frequency
    position = amplitude * math.sin(omega * t)
    velocity = amplitude * omega * math.cos(omega * t)
    if t >= float(target_cfg["step_time_s"]):
        position += float(target_cfg["step_offset"])
    return position, velocity


def generate_chunk(
    position: float,
    velocity: float,
    observation_time: float,
    cfg: dict[str, Any],
) -> np.ndarray:
    """Roll a simple model-based PD policy forward to produce an action chunk."""
    dt = float(cfg["dt"])
    horizon = int(cfg["chunk_horizon"])
    controller = cfg["controller"]
    kp = float(controller["kp"])
    kd = float(controller["kd"])
    limit = float(controller["u_limit"])
    damping = float(controller["plant_damping"])

    q = float(position)
    v = float(velocity)
    actions = np.empty(horizon, dtype=np.float64)
    for k in range(horizon):
        tk = observation_time + k * dt
        q_ref, v_ref = target_state(tk, cfg)
        u = np.clip(kp * (q_ref - q) + kd * (v_ref - v), -limit, limit)
        actions[k] = u

        # Policy-side rollout model. It intentionally excludes process noise;
        # deployment therefore still has model/state mismatch even at zero latency.
        acceleration = u - damping * v
        v = v + acceleration * dt
        q = q + v * dt
    return actions


def _finite_percentile(values: list[float], q: float) -> float:
    finite = np.asarray([x for x in values if math.isfinite(x)], dtype=np.float64)
    if finite.size == 0:
        return float("nan")
    return float(np.percentile(finite, q))


def simulate_condition(
    *,
    mode: str,
    latency_s: float,
    cfg: dict[str, Any],
    output_root: Path,
    seed: int,
    command: list[str],
) -> dict[str, Any]:
    if mode not in {"sync_hold", "async_queue", "async_rebase"}:
        raise ValueError(f"Unknown executor mode: {mode}")

    dt = float(cfg["dt"])
    duration = float(cfg["duration_s"])
    policy_period = float(cfg["policy_period_s"])
    horizon = int(cfg["chunk_horizon"])
    controller = cfg["controller"]
    damping = float(controller["plant_damping"])
    u_limit = float(controller["u_limit"])
    failure_threshold = float(cfg["failure_threshold"])
    success_tolerance = float(cfg["success_tolerance"])

    if dt <= 0 or duration <= 0 or policy_period <= 0:
        raise ValueError("dt, duration_s and policy_period_s must be positive")
    if latency_s < 0:
        raise ValueError("latency must be non-negative")
    if horizon <= 0:
        raise ValueError("chunk_horizon must be positive")

    rng = np.random.default_rng(seed)
    recorder = RunRecorder(
        output_root=output_root,
        lab_id=LAB_ID,
        condition=f"{mode}_latency{latency_s:.3f}s",
        seed=seed,
        config={**cfg, "condition": {"mode": mode, "latency_s": latency_s}},
        repo_root=REPO_ROOT,
        command=command,
    )

    q = 0.0
    v = 0.0
    last_u = 0.0
    last_action_source_time: float | None = None
    active: ActiveChunk | None = None
    pending: PendingChunk | None = None
    next_request_time = 0.0

    missed_requests = 0
    discarded_chunks = 0
    delivered_chunks = 0
    saturation_steps = 0
    tracking_failure_active = False

    errors: list[float] = []
    action_ages: list[float] = []
    controls: list[float] = []

    def activate_ready_chunk(now: float, ready: PendingChunk) -> ActiveChunk | None:
        nonlocal discarded_chunks, delivered_chunks
        delivered_chunks += 1
        start_index = 0
        if mode == "async_rebase":
            elapsed = max(0.0, now - ready.observation_time)
            start_index = int(math.floor(elapsed / dt + 1e-9))
            if start_index >= len(ready.chunk):
                discarded_chunks += 1
                return None
        return ActiveChunk(
            observation_time=ready.observation_time,
            chunk=ready.chunk,
            index=start_index,
        )

    n_steps = int(round(duration / dt))
    for step in range(n_steps):
        t = step * dt

        # Deliver an asynchronous inference result before selecting this control.
        if pending is not None and pending.ready_time <= t + 1e-12:
            active = activate_ready_chunk(t, pending)
            pending = None

        # Request policy inference at its own rate. Only one request may be in
        # flight; skipped requests are a measurable system-level consequence.
        if t + 1e-12 >= next_request_time:
            while t + 1e-12 >= next_request_time:
                request_time = next_request_time
                next_request_time += policy_period
                if pending is not None:
                    missed_requests += 1
                    continue
                chunk = generate_chunk(q, v, request_time, cfg)
                candidate = PendingChunk(
                    observation_time=request_time,
                    ready_time=request_time + latency_s,
                    chunk=chunk,
                )
                if candidate.ready_time <= t + 1e-12:
                    active = activate_ready_chunk(t, candidate)
                else:
                    pending = candidate

        use_chunk = active is not None and active.index < len(active.chunk)
        if mode == "sync_hold" and pending is not None:
            # Blocking inference: the plant keeps receiving the previous command.
            u = last_u
        elif use_chunk:
            assert active is not None
            planned_index = active.index
            u = float(active.chunk[planned_index])
            last_action_source_time = active.observation_time + planned_index * dt
            active.index += 1
        else:
            u = last_u

        u = float(np.clip(u, -u_limit, u_limit))
        if abs(u) >= u_limit - 1e-9:
            saturation_steps += 1
        last_u = u

        if last_action_source_time is None:
            action_age = float("nan")
        else:
            action_age = max(0.0, t - last_action_source_time)
        action_ages.append(action_age)

        # Paired process noise: every executor/latency condition uses the same
        # seed so condition comparisons are not dominated by different noise.
        disturbance = float(rng.normal(0.0, 0.035))
        acceleration = u - damping * v + disturbance
        v = v + acceleration * dt
        q = q + v * dt

        t_next = (step + 1) * dt
        q_ref, _ = target_state(t_next, cfg)
        error = q - q_ref
        abs_error = abs(error)
        errors.append(error)
        controls.append(u)

        if abs_error > failure_threshold and not tracking_failure_active:
            recorder.log_failure(
                category="tracking_error",
                step=step,
                time_s=t_next,
                details={
                    "abs_error": abs_error,
                    "threshold": failure_threshold,
                    "mode": mode,
                    "latency_s": latency_s,
                    "action_age_s": action_age,
                },
            )
            tracking_failure_active = True
        elif abs_error < 0.8 * failure_threshold:
            tracking_failure_active = False

        recorder.log_step(
            step=step,
            time_s=t_next,
            target_position=q_ref,
            position=q,
            velocity=v,
            action=u,
            tracking_error=error,
            abs_tracking_error=abs_error,
            action_age_s=action_age,
            pending_inference=int(pending is not None),
            active_chunk_index=(-1 if active is None else active.index),
            missed_requests=missed_requests,
            process_disturbance=disturbance,
        )

    error_array = np.asarray(errors, dtype=np.float64)
    control_array = np.asarray(controls, dtype=np.float64)
    finite_ages = [x for x in action_ages if math.isfinite(x)]
    summary = {
        "mode": mode,
        "latency_s": latency_s,
        "seed": seed,
        "rmse": float(np.sqrt(np.mean(error_array**2))),
        "mae": float(np.mean(np.abs(error_array))),
        "max_abs_error": float(np.max(np.abs(error_array))),
        "success_fraction": float(np.mean(np.abs(error_array) <= success_tolerance)),
        "mean_action_age_s": (float(np.mean(finite_ages)) if finite_ages else float("nan")),
        "p95_action_age_s": _finite_percentile(action_ages, 95.0),
        "mean_control_energy": float(np.mean(control_array**2)),
        "saturation_fraction": saturation_steps / n_steps,
        "missed_policy_requests": missed_requests,
        "delivered_chunks": delivered_chunks,
        "discarded_chunks": discarded_chunks,
        "failure_events": len(recorder.failures),
    }
    run_dir = recorder.finalize(summary)
    return {**summary, "run_dir": str(run_dir.relative_to(output_root))}


def run_sweep(cfg: dict[str, Any], output_root: Path, command: list[str]) -> list[dict[str, Any]]:
    seed = int(cfg["seed"])
    rows: list[dict[str, Any]] = []
    for latency in cfg["latencies_s"]:
        for mode in cfg["modes"]:
            rows.append(
                simulate_condition(
                    mode=str(mode),
                    latency_s=float(latency),
                    cfg=cfg,
                    output_root=output_root,
                    seed=seed,
                    command=command,
                )
            )
    write_csv(output_root / "results.csv", rows)
    write_json(
        output_root / "sweep_manifest.json",
        {
            "lab_id": LAB_ID,
            "conditions": len(rows),
            "seed": seed,
            "config": cfg,
            "results_file": "results.csv",
        },
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Short deterministic sweep for CI/smoke testing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_json(args.config)
    if args.quick:
        cfg = dict(cfg)
        cfg["duration_s"] = 2.5
        cfg["latencies_s"] = [0.0, 0.1, 0.25]
        cfg["target"] = dict(cfg["target"])
        cfg["target"]["step_time_s"] = 1.25

    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_root = Path(__file__).resolve().parent / "runs" / stamp
    else:
        output_root = args.output
    output_root.mkdir(parents=True, exist_ok=True)

    rows = run_sweep(cfg, output_root=output_root, command=sys.argv)
    print(f"Lab 22 sweep complete: {len(rows)} conditions")
    print(f"results: {output_root / 'results.csv'}")
    for row in rows:
        print(
            f"latency={row['latency_s']:.3f}s mode={row['mode']:<13} "
            f"rmse={row['rmse']:.4f} p95_age={row['p95_action_age_s']:.4f}s "
            f"success_fraction={row['success_fraction']:.3f} missed={row['missed_policy_requests']}"
        )


if __name__ == "__main__":
    main()
