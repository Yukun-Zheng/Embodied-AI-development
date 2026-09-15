#!/usr/bin/env python3
"""Audit structural depth of all 51 textbook chapters.

This is a diagnostic, not yet a hard gate. It makes manuscript imbalance visible
without pretending that raw word count alone measures quality.

Equation coverage counts both Markdown/MathJax display styles used by this book:
`$$...$$` and `\[...\]`. Source coverage distinguishes an explicit source section
from any direct URL evidence so historical/frontier chapters are not mislabeled.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"


@dataclass
class Row:
    part: int
    name: str
    chars: int
    h2: int
    equations: int
    code_blocks: int
    urls: int
    has_failure: bool
    has_experiment: bool
    has_research: bool
    has_source_section: bool

    @property
    def has_source_evidence(self) -> bool:
        return self.has_source_section or self.urls > 0

    @property
    def structure_score(self) -> int:
        return sum(
            [
                self.equations > 0,
                self.code_blocks > 0,
                self.has_failure,
                self.has_experiment,
                self.has_research,
                self.has_source_evidence,
            ]
        )


def count_display_equations(text: str) -> int:
    """Count complete display-math blocks in the two canonical book styles."""
    dollar_blocks = text.count("$$") // 2
    bracket_open = text.count(r"\[")
    bracket_close = text.count(r"\]")
    bracket_blocks = min(bracket_open, bracket_close)
    begin_equation = len(re.findall(r"\\begin\{(?:equation\*?|align\*?|aligned|gather\*?)\}", text))
    return dollar_blocks + bracket_blocks + begin_equation


def inspect(path: Path) -> Row:
    text = path.read_text(encoding="utf-8")
    part = int(path.name[:2])
    h1 = next((line[2:].strip() for line in text.splitlines() if line.startswith("# Part ")), path.stem)
    nonspace_chars = len(re.sub(r"\s+", "", text))
    h2 = len(re.findall(r"(?m)^##\s+", text))
    equations = count_display_equations(text)
    code_blocks = text.count("```") // 2
    urls = len(re.findall(r"https?://", text))
    lower = text.lower()
    has_failure = any(key in lower for key in ["常见失败", "failure", "失败模式"])
    has_experiment = any(key in lower for key in ["最小实验", "minimal experiment", "实验：", "实验设计"])
    has_research = any(key in lower for key in ["研究问题", "research question", "开放问题"])
    has_source_section = any(
        key in lower
        for key in [
            "source anchor",
            "source anchors",
            "延伸阅读",
            "references",
            "参考文献",
            "原始来源",
            "primary sources",
        ]
    )
    return Row(
        part,
        h1,
        nonspace_chars,
        h2,
        equations,
        code_blocks,
        urls,
        has_failure,
        has_experiment,
        has_research,
        has_source_section,
    )


def flag(value: bool) -> str:
    return "Y" if value else "-"


def main() -> None:
    paths = sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))
    rows = [inspect(p) for p in paths]
    assert [r.part for r in rows] == list(range(51)), "Part 0–50 must be continuous"

    print("CHAPTER DEPTH AUDIT")
    print("part chars h2 eq code url F E R S Src score title")
    for r in rows:
        print(
            f"{r.part:02d} {r.chars:5d} {r.h2:2d} {r.equations:2d} {r.code_blocks:2d} {r.urls:2d} "
            f"{flag(r.has_failure)} {flag(r.has_experiment)} {flag(r.has_research)} "
            f"{flag(r.has_source_section)} {flag(r.has_source_evidence)} "
            f"{r.structure_score}/6 {r.name}"
        )

    print("\nTHINNEST BY NON-WHITESPACE CHARACTERS")
    for r in sorted(rows, key=lambda x: x.chars)[:12]:
        print(f"Part {r.part:02d}: chars={r.chars}, structure={r.structure_score}/6 — {r.name}")

    print("\nLOWEST STRUCTURE COVERAGE")
    for r in sorted(rows, key=lambda x: (x.structure_score, x.chars))[:15]:
        missing = []
        if r.equations == 0:
            missing.append("equation")
        if r.code_blocks == 0:
            missing.append("code/dataflow")
        if not r.has_failure:
            missing.append("failure")
        if not r.has_experiment:
            missing.append("experiment")
        if not r.has_research:
            missing.append("research-question")
        if not r.has_source_evidence:
            missing.append("source-evidence")
        print(f"Part {r.part:02d}: {r.structure_score}/6 missing={','.join(missing) or 'none'}")

    print("\nSUMMARY")
    print(f"chapters={len(rows)}")
    print(f"median_chars={int(sorted(r.chars for r in rows)[len(rows)//2])}")
    print(f"with_equations={sum(r.equations > 0 for r in rows)}/51")
    print(f"with_source_section={sum(r.has_source_section for r in rows)}/51")
    print(f"with_source_evidence={sum(r.has_source_evidence for r in rows)}/51")
    print(f"with_failure={sum(r.has_failure for r in rows)}/51")
    print(f"with_experiment={sum(r.has_experiment for r in rows)}/51")
    print(f"with_research_question={sum(r.has_research for r in rows)}/51")
    print("Audit is diagnostic only; publication thresholds will be set after inspecting this distribution.")


if __name__ == "__main__":
    main()
