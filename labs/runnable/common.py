#!/usr/bin/env python3
"""Shared recording utilities for executable textbook labs.

The harness deliberately uses only the Python standard library so hosted CI,
student laptops, simulator machines and real-robot computers can emit the same
run schema without pulling in a logging framework.
"""

from __future__ import annotations

import csv
import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


@dataclass
class RunRecorder:
    """Collect raw steps, failures and a reproducibility manifest for one run."""

    output_root: Path
    lab_id: str
    condition: str
    seed: int
    config: dict[str, Any]
    repo_root: Path
    command: list[str] | None = None
    started_wall: float = field(default_factory=time.time)
    started_utc: str = field(default_factory=_utc_now)
    steps: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        safe_condition = "".join(c if c.isalnum() or c in "-_." else "_" for c in self.condition)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        self.run_dir = self.output_root / f"{stamp}_{self.lab_id}_{safe_condition}_seed{self.seed}"
        self.run_dir.mkdir(parents=True, exist_ok=False)

    def log_step(self, **values: Any) -> None:
        self.steps.append(values)

    def log_failure(self, *, category: str, step: int, time_s: float, details: dict[str, Any]) -> None:
        self.failures.append(
            {
                "category": category,
                "step": step,
                "time_s": time_s,
                "details": details,
            }
        )

    def finalize(self, summary: dict[str, Any]) -> Path:
        ended_wall = time.time()
        manifest = {
            "schema_version": 1,
            "lab_id": self.lab_id,
            "condition": self.condition,
            "seed": self.seed,
            "git_commit": _git_commit(self.repo_root),
            "started_utc": self.started_utc,
            "ended_utc": _utc_now(),
            "wall_seconds": ended_wall - self.started_wall,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "command": self.command or sys.argv,
            "config": self.config,
            "environment": {
                "CI": os.environ.get("CI"),
                "GITHUB_ACTIONS": os.environ.get("GITHUB_ACTIONS"),
            },
        }
        write_json(self.run_dir / "manifest.json", manifest)
        write_csv(self.run_dir / "steps.csv", self.steps)
        with (self.run_dir / "failures.jsonl").open("w", encoding="utf-8") as handle:
            for event in self.failures:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        write_json(self.run_dir / "summary.json", summary)
        return self.run_dir
