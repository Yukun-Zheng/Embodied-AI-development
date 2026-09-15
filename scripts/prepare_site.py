#!/usr/bin/env python3
"""Prepare the disposable MkDocs publication view.

Canonical manuscript files stay in their research-friendly repository layout.
This script mirrors them into `.site-src/` and generates `.site-mkdocs.yml` with
navigation derived from the real chapter manuscripts, so the website cannot
drift from Part 0–50.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".site-src"
GENERATED_CONFIG = ROOT / ".site-mkdocs.yml"
SOURCE_CONFIG = ROOT / "mkdocs.yml"

COPY_FILES = [
    "BOOK_PLAN.md",
    "AUTHORING_GUIDE.md",
]

COPY_DIRS = [
    "book",
    "figures",
    "labs",
    "references",
    "case-studies",
    "code",
]

VOLUME_SPECS = [
    ("Volume 0　导论与技术史", "book/volumes/00-introduction.md", 0, 1),
    ("Volume I　数学与计算语言", "book/volumes/01-mathematics.md", 2, 5),
    ("Volume II　机器人身体、几何、力学与控制", "book/volumes/02-robotics-foundations.md", 6, 11),
    ("Volume III　感知、状态与世界表示", "book/volumes/03-perception-state.md", 12, 17),
    ("Volume IV　Robot Learning", "book/volumes/04-robot-learning.md", 18, 21),
    ("Volume V　Robot Foundation Models", "book/volumes/05-foundation-models.md", 22, 26),
    ("Volume VI　Reasoning、Memory 与 World Models", "book/volumes/06-reasoning-world-models.md", 27, 31),
    ("Volume VII　能力层与 Humanoid", "book/volumes/07-capabilities-humanoids.md", 32, 36),
    ("Volume VIII　Cross-Embodiment 与长期发展", "book/volumes/08-cross-embodiment-developmental.md", 37, 39),
    ("Volume IX　Simulation、Data 与 Systems", "book/volumes/09-simulation-data-systems.md", 40, 43),
    ("Volume X　Evaluation 与 Safety", "book/volumes/10-evaluation-safety.md", 44, 45),
    ("Volume XI　研究方法与下一代架构", "book/volumes/11-research-frontiers.md", 46, 50),
]


def copy_file(src_rel: str, dst_rel: str | None = None) -> None:
    src = ROOT / src_rel
    dst = OUT / (dst_rel or src_rel)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_dir(rel: str) -> None:
    src = ROOT / rel
    dst = OUT / rel
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "runs"),
    )


def chapter_catalog() -> dict[int, tuple[str, str]]:
    catalog: dict[int, tuple[str, str]] = {}
    chapter_dir = ROOT / "book" / "chapters"
    for path in sorted(chapter_dir.glob("[0-9][0-9]-*.md")):
        part = int(path.name[:2])
        title = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# Part "):
                title = line[2:].strip()
                break
        if title is None:
            raise RuntimeError(f"Missing '# Part N' H1 in {path.relative_to(ROOT)}")
        catalog[part] = (title, path.relative_to(ROOT).as_posix())

    expected = set(range(51))
    found = set(catalog)
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise RuntimeError(f"Chapter numbering mismatch: missing={missing}, extra={extra}")
    return catalog


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_nav_item(item: tuple[str, str | list], indent: int = 0) -> list[str]:
    label, value = item
    prefix = " " * indent + f"- {q(label)}:"
    if isinstance(value, str):
        return [f"{prefix} {value}"]
    lines = [prefix]
    for child in value:
        lines.extend(render_nav_item(child, indent + 2))
    return lines


def build_nav() -> list[tuple[str, str | list]]:
    chapters = chapter_catalog()

    volume_nav: list[tuple[str, list]] = []
    for volume_title, overview, first_part, last_part in VOLUME_SPECS:
        children: list[tuple[str, str]] = [("卷级通读", overview)]
        for part in range(first_part, last_part + 1):
            title, path = chapters[part]
            children.append((title, path))
        volume_nav.append((volume_title, children))

    return [
        ("首页", "index.md"),
        (
            "开始阅读",
            [
                ("教材入口", "book/README.md"),
                ("完整目录", "book/TOC.md"),
                ("51 章索引", "book/chapters/README.md"),
                ("36 周课程", "book/SYLLABUS_36_WEEKS.md"),
                ("知识依赖图", "book/DEPENDENCY_GRAPH.md"),
                ("Research Crosswalk", "book/RESEARCH_CROSSWALK.md"),
                ("概念索引", "book/CONCEPT_INDEX.md"),
                ("符号、坐标系与 Action Convention", "book/NOTATION_AND_CONVENTIONS.md"),
            ],
        ),
        ("12 卷 · 51 Part 正文", volume_nav),
        (
            "推导、图与习题",
            [
                ("30 组核心长推导", "book/DERIVATIONS.md"),
                ("204 道章末题", "book/EXERCISES.md"),
                ("解题要点", "book/SOLUTION_SKETCHES.md"),
                ("核心机制图", "figures/CORE_DIAGRAMS.md"),
            ],
        ),
        (
            "源码级 Case Studies",
            [
                ("总索引", "case-studies/README.md"),
                ("Action Path Comparison", "case-studies/ACTION_PATH_COMPARISON.md"),
                ("ACT / ALOHA", "case-studies/ACT_SOURCE_WALKTHROUGH.md"),
                ("Diffusion Policy", "case-studies/DIFFUSION_POLICY_SOURCE_WALKTHROUGH.md"),
                ("OpenVLA", "case-studies/OPENVLA_SOURCE_WALKTHROUGH.md"),
                ("SmolVLA + LeRobot", "case-studies/SMOLVLA_LEROBOT_SOURCE_WALKTHROUGH.md"),
                ("GR00T N1.7", "case-studies/GR00T_N17_SOURCE_WALKTHROUGH.md"),
                ("V-JEPA 2 / 2.1", "case-studies/VJEPA2_1_SOURCE_WALKTHROUGH.md"),
                ("World Model + Control", "case-studies/WORLD_MODEL_CONTROL.md"),
            ],
        ),
        (
            "Labs 与实现",
            [
                ("Labs 总入口", "labs/README.md"),
                ("40 Labs + 3 Capstones", "labs/LABS.md"),
                ("Execution Matrix", "labs/EXECUTION_MATRIX.md"),
                (
                    "Runnable Labs",
                    [
                        ("总入口", "labs/runnable/README.md"),
                        ("Lab 13 · Active Perception", "labs/runnable/lab13_active_perception/README.md"),
                        ("Lab 13 · Reference Results", "labs/runnable/lab13_active_perception/REFERENCE_RESULTS.md"),
                        ("Lab 14 · Tactile Reflex", "labs/runnable/lab14_tactile_reflex/README.md"),
                        ("Lab 14 · Reference Results", "labs/runnable/lab14_tactile_reflex/REFERENCE_RESULTS.md"),
                        ("Lab 22 · Async Execution", "labs/runnable/lab22_async_execution/README.md"),
                        ("Lab 26 · Cross-Embodiment", "labs/runnable/lab26_cross_embodiment/README.md"),
                        ("Lab 26 · Reference Results", "labs/runnable/lab26_cross_embodiment/REFERENCE_RESULTS.md"),
                        ("Lab 29 · World Model MPC", "labs/runnable/lab29_world_model_mpc/README.md"),
                        ("Lab 29 · Reference Results", "labs/runnable/lab29_world_model_mpc/REFERENCE_RESULTS.md"),
                        ("Lab 31 · Reasoning Negative Control", "labs/runnable/lab31_reasoning_negative_control/README.md"),
                        ("Lab 31 · Reference Results", "labs/runnable/lab31_reasoning_negative_control/REFERENCE_RESULTS.md"),
                        ("Lab 33 · Continual Learning", "labs/runnable/lab33_continual_learning/README.md"),
                        ("Lab 33 · Reference Results", "labs/runnable/lab33_continual_learning/REFERENCE_RESULTS.md"),
                    ],
                ),
                ("统一实验协议", "labs/EXPERIMENT_PROTOCOL.md"),
                ("最小可执行代码", "code/minimal/README.md"),
            ],
        ),
        (
            "Research Atlas",
            [
                ("51-Part Primary Sources", "references/CHAPTER_SOURCE_ANCHORS.md"),
                ("Source-Code Atlas", "references/SOURCE_CODE_ATLAS.md"),
                ("Model Atlas", "references/MODEL_ATLAS.md"),
                ("Dataset Atlas", "references/DATASET_ATLAS.md"),
                ("Robot / Hardware Atlas", "references/HARDWARE_ATLAS.md"),
                ("Benchmark / Platform Atlas", "references/BENCHMARK_ATLAS.md"),
                ("Failure Atlas", "references/FAILURE_ATLAS.md"),
                ("Model × Data × Hardware × Benchmark", "references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md"),
            ],
        ),
        (
            "参考与写作",
            [
                ("A–Z 附录", "book/APPENDICES.md"),
                ("中英术语表", "book/GLOSSARY.md"),
                ("1948–2026 技术时间线", "references/TIMELINE.md"),
                ("逐 Part Reading Map", "references/READING_MAP.md"),
                ("统一参考文献", "references/REFERENCES.md"),
                ("教材维护与发布工程", "book/MAINTENANCE.md"),
                ("写作与证据规范", "AUTHORING_GUIDE.md"),
                ("全书工程设计", "BOOK_PLAN.md"),
            ],
        ),
    ]


def generate_mkdocs_config() -> None:
    source = SOURCE_CONFIG.read_text(encoding="utf-8")
    nav_lines = ["nav:"]
    for item in build_nav():
        nav_lines.extend(render_nav_item(item, indent=2))
    nav_block = "\n".join(nav_lines)

    pattern = re.compile(r"(?ms)^nav:\n.*?(?=^theme:)")
    if not pattern.search(source):
        raise RuntimeError("Could not locate nav block in mkdocs.yml")
    generated = pattern.sub(nav_block + "\n\n", source)
    GENERATED_CONFIG.write_text(generated, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copy_file("README.md", "index.md")
    for rel in COPY_FILES:
        copy_file(rel)
    for rel in COPY_DIRS:
        copy_dir(rel)

    copy_file("docs-assets/mathjax.js", "javascripts/mathjax.js")
    copy_file("docs-assets/extra.css", "stylesheets/extra.css")

    generate_mkdocs_config()
    print(f"Prepared website source at {OUT}")
    print(f"Generated chapter-driven MkDocs config at {GENERATED_CONFIG}")


if __name__ == "__main__":
    main()
