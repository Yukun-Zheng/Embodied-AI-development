#!/usr/bin/env python3
"""Deterministic CI mechanism checks for runnable Lab 26."""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB_DIR = Path(__file__).resolve().parent
RUN = LAB_DIR / "run.py"
ANALYZE = LAB_DIR / "analyze.py"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    assert math.isfinite(value), f"{key} is not finite in {row}"
    return value


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="embodied-ai-lab26-") as tmpdir:
        output = Path(tmpdir) / "lab26"
        subprocess.run(
            [sys.executable, str(RUN), "--quick", "--output", str(output)],
            cwd=ROOT,
            check=True,
        )

        condition_path = output / "condition_metrics.csv"
        embodiment_path = output / "embodiment_metrics.csv"
        interface_path = output / "interface_checks.csv"
        manifest_path = output / "experiment_manifest.json"
        for required in [condition_path, embodiment_path, interface_path, manifest_path]:
            assert required.is_file(), f"Lab 26 missing {required.name}"

        conditions = read_rows(condition_path)
        embodiments = read_rows(embodiment_path)
        interfaces = read_rows(interface_path)
        assert len(conditions) == 6
        assert len(embodiments) == 24
        assert len(interfaces) == 4

        keyed = {row["condition"]: row for row in conditions}
        assert set(keyed) == {
            "raw_shared",
            "canonical_interface_only",
            "seen_robot_lookup",
            "morphology_conditioned",
            "wrong_morphology_tag",
            "wrong_action_semantics",
        }
        by_pair = {(row["condition"], row["embodiment"]): row for row in embodiments}

        for row in conditions:
            for metric in [
                "seen_success_rate",
                "unseen_success_rate",
                "unseen_interpolation_success_rate",
                "unseen_extrapolation_success_rate",
                "overall_success_rate",
                "mean_final_position_error",
                "mean_integrated_squared_error",
                "mean_force_energy",
                "mean_saturation_fraction",
            ]:
                finite(row, metric)
            assert int(float(row["adaptation_steps_unseen"])) == 0
            assert int(float(row["policy_parameter_count"])) == 2

            run_dir = output / row["run_dir"]
            for required in [
                "manifest.json",
                "steps.csv",
                "failures.jsonl",
                "summary.json",
                "episodes.csv",
                "embodiment_metrics.csv",
            ]:
                assert (run_dir / required).is_file(), (
                    f"Lab 26 missing {required} for {row['condition']}"
                )
            episode_rows = read_rows(run_dir / "episodes.csv")
            assert len(episode_rows) == 4 * 120
            assert all(int(float(row_["adaptation_steps"])) == 0 for row_ in episode_rows)

        for row in interfaces:
            assert finite(row, "max_state_roundtrip_error") < 1e-12
            assert finite(row, "max_action_roundtrip_error") < 1e-12

        raw = keyed["raw_shared"]
        canonical = keyed["canonical_interface_only"]
        lookup = keyed["seen_robot_lookup"]
        conditioned = keyed["morphology_conditioned"]
        wrong_tag = keyed["wrong_morphology_tag"]

        assert finite(canonical, "seen_success_rate") > finite(raw, "seen_success_rate") + 0.30
        assert finite(canonical, "unseen_success_rate") > finite(raw, "unseen_success_rate") + 0.35
        assert finite(lookup, "seen_success_rate") > 0.99
        assert finite(lookup, "seen_success_rate") > finite(lookup, "unseen_success_rate") + 0.25
        assert finite(lookup, "unseen_interpolation_success_rate") > 0.95
        assert finite(lookup, "unseen_extrapolation_success_rate") < 0.50
        assert finite(conditioned, "seen_success_rate") > 0.99
        assert finite(conditioned, "unseen_success_rate") > 0.99
        assert finite(conditioned, "unseen_interpolation_success_rate") > 0.99
        assert finite(conditioned, "unseen_extrapolation_success_rate") > 0.99
        assert finite(conditioned, "unseen_success_rate") > finite(lookup, "unseen_success_rate") + 0.30
        assert finite(conditioned, "unseen_success_rate") > finite(wrong_tag, "unseen_success_rate") + 0.30

        assert finite(by_pair[("raw_shared", "B")], "success_rate") < 0.05
        assert finite(by_pair[("raw_shared", "D")], "success_rate") < 0.05
        assert finite(by_pair[("wrong_action_semantics", "B")], "success_rate") < 0.05
        assert finite(by_pair[("wrong_action_semantics", "D")], "success_rate") < 0.05
        assert finite(by_pair[("wrong_morphology_tag", "D")], "success_rate") < 0.50

        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        assert manifest["seen_embodiments"] == ["A", "B"]
        assert manifest["held_out_embodiments"] == ["C", "D"]
        assert manifest["held_out_task_adaptation_steps"] == 0
        assert manifest["shared_trial_schedule"] is True
        assert manifest["canonical_policy"]["parameter_count"] == 2

        subprocess.run(
            [
                sys.executable,
                str(ANALYZE),
                str(condition_path),
                str(embodiment_path),
                str(interface_path),
                "--output-dir",
                str(output),
            ],
            cwd=ROOT,
            check=True,
        )
        analysis_path = output / "analysis.json"
        assert analysis_path.is_file()
        assert (output / "ANALYSIS.md").is_file()
        with analysis_path.open("r", encoding="utf-8") as handle:
            analysis = json.load(handle)

        for key in [
            "interface_roundtrip_is_exact",
            "canonical_semantics_improve_seen_mixture",
            "canonical_semantics_improve_held_out_transfer",
            "seen_robot_lookup_handles_seen_bodies",
            "seen_mixture_is_not_unseen_transfer",
            "held_out_interpolation_and_extrapolation_are_reported_separately",
            "morphology_conditioning_preserves_seen_performance",
            "morphology_conditioning_zero_shot_transfers",
            "continuous_descriptor_beats_seen_robot_lookup_on_unseen",
            "morphology_tag_is_causally_used",
            "action_semantics_are_causally_necessary",
            "raw_shape_compatibility_is_not_semantic_compatibility",
            "held_out_transfer_uses_zero_task_adaptation",
            "shared_policy_capacity_is_fixed",
        ]:
            assert analysis[key] is True, f"Lab 26 mechanism assertion failed: {key}"

        print(
            "PASS lab26_cross_embodiment: seen lookup, held-out interpolation/extrapolation, "
            "morphology conditioning, wrong-tag and wrong-action controls verified"
        )


if __name__ == "__main__":
    main()
