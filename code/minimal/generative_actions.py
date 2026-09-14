"""Regression vs Diffusion vs Flow Matching on a multimodal action distribution.

Run:
    python code/minimal/generative_actions.py

Toy task:
    condition c in [-1, 1]
    valid action has two modes around 0.4*c +/- 1.5

A deterministic MSE regressor tends to average the modes near an invalid action.
Diffusion and flow matching can represent both modes.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn


torch.set_num_threads(2)


def sample_data(batch: int) -> tuple[torch.Tensor, torch.Tensor]:
    c = torch.rand(batch, 1) * 2.0 - 1.0
    mode = torch.where(torch.rand(batch, 1) > 0.5, torch.ones(batch, 1), -torch.ones(batch, 1))
    action = 0.4 * c + 1.5 * mode + 0.05 * torch.randn(batch, 1)
    return c, action


class MLP(nn.Module):
    def __init__(self, input_dim: int, output_dim: int = 1) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.SiLU(),
            nn.Linear(64, 64),
            nn.SiLU(),
            nn.Linear(64, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def train_regression(seed: int = 0, steps: int = 800) -> MLP:
    torch.manual_seed(seed)
    model = MLP(1)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)
    for _ in range(steps):
        c, action = sample_data(256)
        pred = model(c)
        loss = torch.mean((pred - action) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


class FlowNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = MLP(3)

    def forward(self, x: torch.Tensor, t: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        return self.net(torch.cat([x, t, c], dim=-1))


def train_flow(seed: int = 1, steps: int = 2000) -> FlowNet:
    torch.manual_seed(seed)
    model = FlowNet()
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)

    for _ in range(steps):
        c, x1 = sample_data(256)
        x0 = torch.randn_like(x1)
        t = torch.rand_like(x1)
        xt = (1.0 - t) * x0 + t * x1
        target_velocity = x1 - x0
        pred_velocity = model(xt, t, c)
        loss = torch.mean((pred_velocity - target_velocity) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()

    return model


@torch.no_grad()
def sample_flow(model: FlowNet, condition: float, n: int = 2000, steps: int = 40) -> np.ndarray:
    x = torch.randn(n, 1)
    c = torch.full((n, 1), float(condition))
    dt = 1.0 / steps

    # Euler integration of dx/dt = v_theta(x,t,c).
    for i in range(steps):
        t = torch.full_like(x, (i + 0.5) / steps)
        x = x + dt * model(x, t, c)
    return x[:, 0].cpu().numpy()


class DiffusionNet(nn.Module):
    def __init__(self, timesteps: int = 40) -> None:
        super().__init__()
        self.timesteps = timesteps
        self.net = MLP(3)

    def forward(self, x: torch.Tensor, k: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        t = k.float().reshape(-1, 1) / (self.timesteps - 1)
        return self.net(torch.cat([x, t, c], dim=-1))


def diffusion_schedule(timesteps: int = 40) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    beta = torch.linspace(1e-4, 0.08, timesteps)
    alpha = 1.0 - beta
    alpha_bar = torch.cumprod(alpha, dim=0)
    return beta, alpha, alpha_bar


def train_diffusion(seed: int = 2, steps: int = 2500, timesteps: int = 40) -> tuple[DiffusionNet, tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
    torch.manual_seed(seed)
    model = DiffusionNet(timesteps)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)
    schedule = diffusion_schedule(timesteps)
    _, _, alpha_bar = schedule

    for _ in range(steps):
        c, x0 = sample_data(256)
        k = torch.randint(0, timesteps, (256,))
        eps = torch.randn_like(x0)
        ab = alpha_bar[k].reshape(-1, 1)
        xk = torch.sqrt(ab) * x0 + torch.sqrt(1.0 - ab) * eps
        pred_eps = model(xk, k, c)
        loss = torch.mean((pred_eps - eps) ** 2)
        opt.zero_grad()
        loss.backward()
        opt.step()

    return model, schedule


@torch.no_grad()
def sample_diffusion(
    model: DiffusionNet,
    schedule: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    condition: float,
    n: int = 2000,
) -> np.ndarray:
    beta, alpha, alpha_bar = schedule
    timesteps = len(beta)
    x = torch.randn(n, 1)
    c = torch.full((n, 1), float(condition))

    for k in range(timesteps - 1, -1, -1):
        kk = torch.full((n,), k, dtype=torch.long)
        eps = model(x, kk, c)
        a = alpha[k]
        ab = alpha_bar[k]
        b = beta[k]
        mean = (x - (b / torch.sqrt(1.0 - ab)) * eps) / torch.sqrt(a)

        if k > 0:
            ab_prev = alpha_bar[k - 1]
            posterior_var = b * (1.0 - ab_prev) / (1.0 - ab)
            x = mean + torch.sqrt(posterior_var) * torch.randn_like(x)
        else:
            x = mean

    return x[:, 0].cpu().numpy()


def summarize(name: str, samples: np.ndarray) -> None:
    q = np.quantile(samples, [0.1, 0.25, 0.5, 0.75, 0.9])
    print(
        f"{name:10s}: mean={samples.mean():+.3f}, std={samples.std():.3f}, "
        f"P(|a|>0.8)={np.mean(np.abs(samples) > 0.8):.3f}, q={np.round(q, 3)}"
    )


def main() -> None:
    condition = 0.0

    regression = train_regression()
    with torch.no_grad():
        reg_action = float(regression(torch.tensor([[condition]])).item())
    print(f"MSE regression action at c=0: {reg_action:+.3f}")

    flow = train_flow()
    flow_samples = sample_flow(flow, condition)
    summarize("flow", flow_samples)

    diffusion, schedule = train_diffusion()
    diffusion_samples = sample_diffusion(diffusion, schedule, condition)
    summarize("diffusion", diffusion_samples)

    # At c=0 the two valid modes are around +/-1.5. MSE regression should average
    # them near zero, while both generative models should preserve broad/multimodal
    # mass away from zero.
    assert abs(reg_action) < 0.4
    assert np.std(flow_samples) > 1.0
    assert np.mean(np.abs(flow_samples) > 0.8) > 0.9
    assert np.std(diffusion_samples) > 1.0
    assert np.mean(np.abs(diffusion_samples) > 0.8) > 0.9

    print("Generative-action test passed.")


if __name__ == "__main__":
    main()
