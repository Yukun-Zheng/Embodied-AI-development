"""Run every minimal textbook example as a regression suite.

Usage from repository root:
    python code/minimal/run_all.py

Each script contains its own numerical assertions. A non-zero exit code means the
textbook's executable companion has drifted out of sync with its acceptance test.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent

SCRIPTS = [
    "se3.py",
    "planar_arm.py",
    "control.py",
    "kalman_filter.py",
    "active_perception.py",
    "bc_dagger.py",
    "generative_actions.py",
    "world_model_mpc.py",
    "continual_metrics.py",
    "evaluation_stats.py",
]


def main() -> None:
    failures: list[str] = []
    total_start = time.perf_counter()

    for name in SCRIPTS:
        path = HERE / name
        print("\n" + "=" * 80)
        print(f"RUN {name}")
        print("=" * 80)
        start = time.perf_counter()
        result = subprocess.run([sys.executable, str(path)], check=False)
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            failures.append(name)
            print(f"FAIL {name} ({elapsed:.2f}s, exit={result.returncode})")
        else:
            print(f"PASS {name} ({elapsed:.2f}s)")

    total = time.perf_counter() - total_start
    print("\n" + "=" * 80)
    if failures:
        print("FAILED:", ", ".join(failures))
        raise SystemExit(1)

    print(f"ALL {len(SCRIPTS)} MINIMAL EXAMPLES PASSED in {total:.2f}s")


if __name__ == "__main__":
    main()
