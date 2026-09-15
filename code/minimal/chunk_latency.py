"""Why action-chunk inference latency is part of the control problem.

This is intentionally NOT an implementation of Physical Intelligence RTC.
It is a minimal executor experiment showing the systems problem RTC/asynchronous
inference is designed to address.

We compare:
1. blocking chunk execution: query only after the old chunk ends; hold while
   inference is running;
2. asynchronous replacement: execution continues while one sequential inference
   job runs, and the newly arrived chunk replaces the old remainder.

Run:
    python code/minimal/chunk_latency.py
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DT = 0.05
HORIZON = 16
INFERENCE_DELAY_STEPS = 4
N_STEPS = 180
KP = 3.0
MAX_SPEED = 1.0


def goal_at(step: int) -> float:
    if step < 60:
        return 1.0
    if step < 120:
        return -0.7
    return 0.5


def policy_chunk(x_snapshot: float, goal_snapshot: float) -> list[float]:
    """Tiny model-predictive P controller used only as a chunk generator."""
    x_pred = x_snapshot
    chunk: list[float] = []
    for _ in range(HORIZON):
        u = float(np.clip(KP * (goal_snapshot - x_pred), -MAX_SPEED, MAX_SPEED))
        chunk.append(u)
        x_pred += DT * u
    return chunk


@dataclass
class Trace:
    state: np.ndarray
    action: np.ndarray
    goal: np.ndarray
    inference_holds: int

    @property
    def mae(self) -> float:
        return float(np.mean(np.abs(self.state - self.goal)))

    @property
    def action_variation(self) -> float:
        return float(np.mean(np.abs(np.diff(self.action))))

    @property
    def transition_mae(self) -> float:
        # Focus on the 30 steps immediately after each goal switch, when stale
        # observations/chunks are most visible.
        idx = np.r_[60:90, 120:150]
        return float(np.mean(np.abs(self.state[idx] - self.goal[idx])))


def run_blocking() -> Trace:
    x = 0.0
    queue: list[float] = []
    pending: tuple[int, list[float]] | None = None
    xs, us, gs = [], [], []
    holds = 0

    for t in range(N_STEPS):
        goal = goal_at(t)

        if pending is not None and pending[0] == t:
            queue = pending[1]
            pending = None

        # Only request the next chunk after the current one is exhausted.
        if not queue and pending is None:
            pending = (t + INFERENCE_DELAY_STEPS, policy_chunk(x, goal))

        if queue:
            u = queue.pop(0)
        else:
            # Conservative blocking baseline: hold while inference runs.
            u = 0.0
            holds += 1

        x += DT * u
        xs.append(x)
        us.append(u)
        gs.append(goal)

    return Trace(np.asarray(xs), np.asarray(us), np.asarray(gs), holds)


def run_async_replacement() -> Trace:
    x = 0.0
    queue: list[float] = []
    pending: list[tuple[int, list[float]]] = []
    xs, us, gs = [], [], []
    holds = 0

    for t in range(N_STEPS):
        goal = goal_at(t)

        # A completed inference replaces the remaining old chunk.
        arrivals = [item for item in pending if item[0] == t]
        pending = [item for item in pending if item[0] != t]
        if arrivals:
            queue = arrivals[-1][1]

        # One sequential inference job every DELAY steps. Prediction and action
        # execution are decoupled, so the robot keeps consuming the old chunk.
        if t % INFERENCE_DELAY_STEPS == 0:
            pending.append((t + INFERENCE_DELAY_STEPS, policy_chunk(x, goal)))

        if queue:
            u = queue.pop(0)
        else:
            u = 0.0
            holds += 1

        x += DT * u
        xs.append(x)
        us.append(u)
        gs.append(goal)

    return Trace(np.asarray(xs), np.asarray(us), np.asarray(gs), holds)


def report(name: str, trace: Trace) -> None:
    print(
        f"{name:22s}  MAE={trace.mae:.4f}  "
        f"switch-MAE={trace.transition_mae:.4f}  "
        f"action-variation={trace.action_variation:.4f}  "
        f"hold-steps={trace.inference_holds}"
    )


def main() -> None:
    blocking = run_blocking()
    async_exec = run_async_replacement()

    print(f"state shape: {blocking.state.shape}")
    print(f"chunk horizon: {HORIZON}")
    print(f"inference delay: {INFERENCE_DELAY_STEPS} control steps")
    report("blocking chunk", blocking)
    report("async replacement", async_exec)

    # Same policy_chunk(), same dynamics, same delay. Only the temporal executor
    # changes. This is the causal point of the experiment.
    assert async_exec.mae < blocking.mae
    assert async_exec.transition_mae < blocking.transition_mae
    assert async_exec.inference_holds < blocking.inference_holds

    print("PASS: temporal execution alone changes closed-loop performance")
    print("NOTE: RTC further addresses continuity/staleness inside the generative chunk itself.")


if __name__ == "__main__":
    main()
