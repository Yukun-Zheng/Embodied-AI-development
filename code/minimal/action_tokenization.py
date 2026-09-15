"""OpenVLA-style continuous-action tokenization in ~100 lines.

Mirrors the mechanism in openvla/openvla `prismatic/vla/action_tokenizer.py`
without depending on Transformers:

continuous action [-1, 1]
    -> uniform bin index
    -> reserved token id near the end of an LLM vocabulary
    -> bin center
    -> continuous action

Run:
    python code/minimal/action_tokenization.py
"""

from __future__ import annotations

import numpy as np


def make_bins(n_bins: int, low: float = -1.0, high: float = 1.0):
    bins = np.linspace(low, high, n_bins, dtype=np.float64)
    centers = (bins[:-1] + bins[1:]) / 2.0
    return bins, centers


def encode_action(
    action: np.ndarray,
    *,
    n_bins: int = 256,
    vocab_size: int = 32000,
    low: float = -1.0,
    high: float = 1.0,
) -> np.ndarray:
    """Clip, uniformly discretize, then map bins to reserved token ids."""
    bins, _ = make_bins(n_bins, low, high)
    clipped = np.clip(np.asarray(action, dtype=np.float64), low, high)
    discretized = np.digitize(clipped, bins)
    return vocab_size - discretized


def decode_action(
    token_ids: np.ndarray,
    *,
    n_bins: int = 256,
    vocab_size: int = 32000,
    low: float = -1.0,
    high: float = 1.0,
) -> np.ndarray:
    """Map reserved token ids back to continuous bin centers."""
    _, centers = make_bins(n_bins, low, high)
    discretized = vocab_size - np.asarray(token_ids)
    center_index = np.clip(discretized - 1, 0, centers.shape[0] - 1)
    return centers[center_index]


def roundtrip_error(n_bins: int) -> tuple[float, float]:
    actions = np.linspace(-1.0, 1.0, 10001, dtype=np.float64)
    tokens = encode_action(actions, n_bins=n_bins)
    decoded = decode_action(tokens, n_bins=n_bins)
    err = decoded - actions
    return float(np.sqrt(np.mean(err**2))), float(np.max(np.abs(err)))


def main() -> None:
    rng = np.random.default_rng(7)
    batch = rng.uniform(-1.0, 1.0, size=(4, 7))
    tokens = encode_action(batch)
    decoded = decode_action(tokens)

    print("action shape: ", batch.shape)
    print("token shape:  ", tokens.shape)
    print("example action:", np.round(batch[0], 4))
    print("token ids:     ", tokens[0])
    print("decoded:       ", np.round(decoded[0], 4))

    # 256 values define 255 intervals. The worst possible in-range error is
    # half one interval width = 1/(n_bins-1) for [-1, 1].
    rmse_256, maxerr_256 = roundtrip_error(256)
    theoretical_half_step = 1.0 / 255.0
    print(f"256-bin RMSE: {rmse_256:.6f}")
    print(f"256-bin max error: {maxerr_256:.6f}")
    print(f"half-bin bound: {theoretical_half_step:.6f}")
    assert maxerr_256 <= theoretical_half_step + 1e-12

    # Resolution is a real control design variable, not a formatting detail.
    rmses = []
    for n_bins in (32, 64, 256, 1024):
        rmse, maxerr = roundtrip_error(n_bins)
        rmses.append(rmse)
        print(f"n_bins={n_bins:4d}  rmse={rmse:.6f}  max={maxerr:.6f}")
    assert all(a > b for a, b in zip(rmses, rmses[1:]))

    # Out-of-range actions are clipped before tokenization. This is often more
    # dangerous than quantization error because a saturated command can hide a
    # dataset/action-normalization mismatch.
    extreme = np.array([-2.0, -1.2, 0.0, 1.3, 3.0])
    extreme_decoded = decode_action(encode_action(extreme))
    print("clipping demo: ", np.round(extreme_decoded, 4))
    assert extreme_decoded[0] > -1.0 and extreme_decoded[-1] < 1.0
    assert extreme_decoded[0] == extreme_decoded[1]
    assert extreme_decoded[-1] == extreme_decoded[-2]

    print("PASS: action tokenization round-trip and quantization checks")


if __name__ == "__main__":
    main()
