"""Why a shared padded action tensor is not a universal action space.

This toy mirrors the interface problem behind multi-embodiment policies such as
GR00T: different robots can assign different semantics, scales and dimensions to
raw action coordinates. A model therefore needs an embodiment-aware mapping (or
some other explicit morphology/interface mechanism), not just zero padding.

Run:
    python code/minimal/embodiment_interfaces.py
"""

from __future__ import annotations

import numpy as np

# Canonical task-space intent z = [forward, lateral, gripper].
CANONICAL_DIM = 3
MAX_ACTION_DIM = 5

# Robot A exposes canonical semantics directly in a 3-D action vector.
M_A = np.array(
    [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
)

# Robot B exposes a 5-D actuator/interface vector with different coordinate
# ordering, signs and scales. The mapping is deliberately redundant but full
# column-rank so the same canonical intent is recoverable.
M_B = np.array(
    [
        [0.0, 2.0, 0.0],
        [-0.5, 0.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.5, 0.5, 0.0],
        [0.0, 0.5, 0.0],
    ]
)


def raw_action(z: np.ndarray, embodiment: str) -> np.ndarray:
    matrix = M_A if embodiment == "A" else M_B
    return np.asarray(z) @ matrix.T


def canonicalize(action: np.ndarray, embodiment: str) -> np.ndarray:
    matrix = M_A if embodiment == "A" else M_B
    # For a learned system this role may be played by embodiment-conditioned
    # projectors/encoders. Here the pseudoinverse makes the semantics explicit.
    return np.asarray(action) @ np.linalg.pinv(matrix).T


def pad_action(action: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    padded = np.zeros((*action.shape[:-1], MAX_ACTION_DIM), dtype=np.float64)
    mask = np.zeros_like(padded, dtype=bool)
    d = action.shape[-1]
    padded[..., :d] = action
    mask[..., :d] = True
    return padded, mask


def masked_mse(pred: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    sq = (pred - target) ** 2
    return float(sq[mask].mean())


def main() -> None:
    rng = np.random.default_rng(11)
    z = rng.uniform(-1.0, 1.0, size=(128, CANONICAL_DIM))

    a = raw_action(z, "A")
    b = raw_action(z, "B")
    a_pad, a_mask = pad_action(a)
    b_pad, b_mask = pad_action(b)

    print("canonical intent shape:", z.shape)
    print("robot A raw/padded:   ", a.shape, a_pad.shape)
    print("robot B raw/padded:   ", b.shape, b_pad.shape)
    print("A valid dims:", a_mask[0].astype(int))
    print("B valid dims:", b_mask[0].astype(int))

    # Embodiment-aware mappings recover the same physical/task intent.
    z_a = canonicalize(a, "A")
    z_b = canonicalize(b, "B")
    err_a = float(np.max(np.abs(z_a - z)))
    err_b = float(np.max(np.abs(z_b - z)))
    print(f"canonicalization max error A: {err_a:.3e}")
    print(f"canonicalization max error B: {err_b:.3e}")
    assert err_a < 1e-10
    assert err_b < 1e-10

    # Padding makes shapes equal but NOT semantics equal. If a shared model
    # naively interprets the first 3 coordinates as [forward,lateral,gripper],
    # Robot B is systematically wrong despite having the same [B,5] tensor.
    naive_b_intent = b_pad[:, :3]
    naive_error = float(np.sqrt(np.mean((naive_b_intent - z) ** 2)))
    aware_error = float(np.sqrt(np.mean((z_b - z) ** 2)))
    print(f"naive padded-interface RMSE: {naive_error:.4f}")
    print(f"embodiment-aware RMSE:       {aware_error:.4e}")
    assert naive_error > 0.2
    assert aware_error < 1e-10

    # Action masks are equally important. Errors in padded dimensions should
    # not become learning targets for a lower-dimensional embodiment.
    pred_a = a_pad.copy()
    pred_a[:, 3:] = 10.0  # huge errors only in nonexistent Robot-A dimensions
    unmasked_loss = float(np.mean((pred_a - a_pad) ** 2))
    valid_loss = masked_mse(pred_a, a_pad, a_mask)
    print(f"unmasked padded loss: {unmasked_loss:.2f}")
    print(f"masked valid loss:    {valid_loss:.2f}")
    assert unmasked_loss > 1.0
    assert valid_loss == 0.0

    print("PASS: shape unification != semantic unification; embodiment mapping + masks matter")


if __name__ == "__main__":
    main()
