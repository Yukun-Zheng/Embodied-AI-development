"""Learned dynamics + CEM/MPC on a nonlinear 1-D point mass.

Run:
    python code/minimal/world_model_mpc.py

This mirrors Part 30 / DERIVATIONS D19-D20:
    real transitions -> learned action-conditioned model -> imagined rollouts
    -> action-sequence search -> execute first action -> observe -> replan.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn


torch.set_num_threads(2)
DT = 0.1
ACTION_LIMIT = 2.0


def true_step(state: np.ndarray, action: float) -> np.ndarray:
    """Nonlinear ground-truth dynamics. state=[position, velocity]."""
    x, v = float(state[0]), float(state[1])
    u = float(np.clip(action, -ACTION_LIMIT, ACTION_LIMIT))
    acceleration = u - 0.1 * v - 0.2 * np.sin(x)
    v_next = v + DT * acceleration
    x_next = x + DT * v_next
    return np.array([x_next, v_next], dtype=np.float32)


def make_dataset(n: int = 20_000, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    rng = np.random.default_rng(seed)
    states = np.column_stack(
        [rng.uniform(-2.5, 2.5, n), rng.uniform(-1.5, 1.5, n)]
    ).astype(np.float32)
    actions = rng.uniform(-ACTION_LIMIT, ACTION_LIMIT, size=(n, 1)).astype(np.float32)
    next_states = np.stack([true_step(states[i], actions[i, 0]) for i in range(n)])

    inputs = torch.tensor(np.concatenate([states, actions], axis=1))
    targets = torch.tensor(next_states)
    return inputs, targets


class DynamicsModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.delta = nn.Sequential(
            nn.Linear(3, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 2),
        )

    def forward(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """state [B,2], action [B,1] -> predicted next state [B,2]."""
        dx = self.delta(torch.cat([state, action], dim=-1))
        return state + dx


def train_world_model(seed: int = 0, steps: int = 1200) -> DynamicsModel:
    torch.manual_seed(seed)
    inputs, targets = make_dataset(seed=seed)
    model = DynamicsModel()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    for _ in range(steps):
        ids = torch.randint(0, len(inputs), (256,))
        state = inputs[ids, :2]
        action = inputs[ids, 2:]
        pred = model(state, action)
        loss = torch.mean((pred - targets[ids]) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()

    return model


@torch.no_grad()
def one_step_rmse(model: DynamicsModel, seed: int = 123) -> float:
    inputs, targets = make_dataset(n=4000, seed=seed)
    pred = model(inputs[:, :2], inputs[:, 2:])
    return float(torch.sqrt(torch.mean((pred - targets) ** 2)).item())


@torch.no_grad()
def cem_action(
    model: DynamicsModel,
    state: np.ndarray,
    *,
    target: float = 2.0,
    horizon: int = 20,
    population: int = 512,
    elite: int = 64,
    iterations: int = 4,
    seed: int = 0,
) -> float:
    """Search an action sequence under the learned model, return only action[0]."""
    torch.manual_seed(seed)
    mean = torch.zeros(horizon)
    std = torch.ones(horizon)
    state0 = torch.tensor(state, dtype=torch.float32)

    for _ in range(iterations):
        actions = (mean[None, :] + std[None, :] * torch.randn(population, horizon)).clamp(
            -ACTION_LIMIT, ACTION_LIMIT
        )
        imagined = state0[None, :].repeat(population, 1)
        cost = torch.zeros(population)

        for t in range(horizon):
            u = actions[:, t : t + 1]
            imagined = model(imagined, u)
            cost += (imagined[:, 0] - target) ** 2
            cost += 0.03 * imagined[:, 1] ** 2
            cost += 0.002 * actions[:, t] ** 2

        cost += 5.0 * (imagined[:, 0] - target) ** 2 + 0.1 * imagined[:, 1] ** 2
        elite_ids = torch.topk(cost, elite, largest=False).indices
        elite_actions = actions[elite_ids]
        mean = elite_actions.mean(dim=0)
        std = elite_actions.std(dim=0).clamp_min(0.08)

    return float(mean[0].clamp(-ACTION_LIMIT, ACTION_LIMIT).item())


def rollout_mpc(model: DynamicsModel, *, target: float = 2.0, steps: int = 50) -> np.ndarray:
    """Receding-horizon control in the *real* dynamics."""
    state = np.array([-1.5, 0.0], dtype=np.float32)
    log = [state.copy()]

    for t in range(steps):
        action = cem_action(model, state, target=target, seed=t)
        # Important: execute only the first planned action in the real dynamics.
        state = true_step(state, action)
        log.append(state.copy())

    return np.stack(log)


def open_loop_from_model(model: DynamicsModel, *, target: float = 2.0, steps: int = 50) -> np.ndarray:
    """A deliberately weaker baseline: plan once, then execute without replanning.

    We obtain a CEM sequence using the learned model but do not refresh the plan
    from real observations. This makes model drift visible.
    """
    state0 = np.array([-1.5, 0.0], dtype=np.float32)
    horizon = steps

    # A larger one-shot search. Keep this implementation explicit for teaching.
    torch.manual_seed(77)
    population, elite, iterations = 1024, 96, 5
    mean = torch.zeros(horizon)
    std = torch.ones(horizon)
    s0 = torch.tensor(state0, dtype=torch.float32)

    with torch.no_grad():
        for _ in range(iterations):
            actions = (mean[None, :] + std[None, :] * torch.randn(population, horizon)).clamp(
                -ACTION_LIMIT, ACTION_LIMIT
            )
            imagined = s0[None, :].repeat(population, 1)
            cost = torch.zeros(population)
            for t in range(horizon):
                u = actions[:, t : t + 1]
                imagined = model(imagined, u)
                cost += 0.3 * (imagined[:, 0] - target) ** 2 + 0.002 * actions[:, t] ** 2
            cost += 8.0 * (imagined[:, 0] - target) ** 2 + 0.2 * imagined[:, 1] ** 2
            ids = torch.topk(cost, elite, largest=False).indices
            selected = actions[ids]
            mean = selected.mean(dim=0)
            std = selected.std(dim=0).clamp_min(0.08)

    state = state0.copy()
    log = [state.copy()]
    for action in mean.cpu().numpy():
        state = true_step(state, float(action))
        log.append(state.copy())
    return np.stack(log)


def main() -> None:
    model = train_world_model()
    rmse = one_step_rmse(model)
    print(f"held-out one-step RMSE: {rmse:.6f}")

    target = 2.0
    mpc = rollout_mpc(model, target=target)
    open_loop = open_loop_from_model(model, target=target)

    mpc_error = abs(float(mpc[-1, 0]) - target)
    open_error = abs(float(open_loop[-1, 0]) - target)
    print("MPC final state:      ", np.round(mpc[-1], 4), "position error:", mpc_error)
    print("open-loop final state:", np.round(open_loop[-1], 4), "position error:", open_error)

    assert rmse < 0.02
    assert mpc_error < 0.08

    print(
        "World-model MPC test passed. The important mechanism is receding-horizon "
        "replanning from real observations, not merely generating a plausible future."
    )


if __name__ == "__main__":
    main()
