#!/usr/bin/env python3
r"""Audit and enforce structural depth for all 51 canonical chapters.

Every chapter must contain six publication-baseline dimensions:
1. at least one display equation,
2. at least one code/dataflow block,
3. an explicit failure section,
4. an explicit experiment section,
5. an explicit research-question section,
6. source evidence (authored anchors or canonical source-map fallback).

This gate does not claim all chapters are equally good; it prevents structural
regression so future editing can focus on evidence quality and exposition.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
SOURCE_START = "<!-- CHAPTER-SOURCE-MAP:START -->"
SOURCE_END = "<!-- CHAPTER-SOURCE-MAP:END -->"
SOURCE_MARKERS = [
    "source anchor",
    "source anchors",
    "延伸阅读",
    "references",
    "参考文献",
    "原始来源",
    "primary sources",
]


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
    has_authored_sources: bool
    has_generated_source_map: bool

    @property
    def has_source_evidence(self) -> bool:
        return self.has_authored_sources or self.has_generated_source_map or self.urls > 0

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

    @property
    def missing(self) -> list[str]:
        missing: list[str] = []
        if self.equations == 0:
            missing.append("equation")
        if self.code_blocks == 0:
            missing.append("code/dataflow")
        if not self.has_failure:
            missing.append("failure-section")
        if not self.has_experiment:
            missing.append("experiment-section")
        if not self.has_research:
            missing.append("research-question-section")
        if not self.has_source_evidence:
            missing.append("source-evidence")
        return missing


def count_display_equations(text: str) -> int:
    dollar_blocks = text.count("$$") // 2
    bracket_open = text.count(r"\[")
    bracket_close = text.count(r"\]")
    bracket_blocks = min(bracket_open, bracket_close)
    begin_equation = len(re.findall(r"\\begin\{(?:equation\*?|align\*?|aligned|gather\*?)\}", text))
    return dollar_blocks + bracket_blocks + begin_equation


def all_headings(text: str) -> list[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", text)]


def authored_headings(text: str) -> list[str]:
    authored = re.sub(
        rf"{re.escape(SOURCE_START)}.*?{re.escape(SOURCE_END)}",
        "",
        text,
        flags=re.DOTALL,
    )
    return all_headings(authored)


def inspect(path: Path) -> Row:
    text = path.read_text(encoding="utf-8")
    part = int(path.name[:2])
    h1 = next((line[2:].strip() for line in text.splitlines() if line.startswith("# Part ")), path.stem)
    nonspace_chars = len(re.sub(r"\s+", "", text))
    headings = all_headings(text)
    h2 = len(re.findall(r"(?m)^##\s+", text))
    equations = count_display_equations(text)
    code_blocks = text.count("```") // 2
    urls = len(re.findall(r"https?://", text))

    has_failure = any(("失败" in h) or ("failure" in h) for h in headings)
    has_experiment = any(("实验" in h) or ("experiment" in h) for h in headings)
    has_research = any(
        ("研究问题" in h) or ("research question" in h) or ("开放问题" in h)
        for h in headings
    )

    authored = authored_headings(text)
    has_authored_sources = any(marker in heading for heading in authored for marker in SOURCE_MARKERS)
    has_generated_source_map = SOURCE_START in text and SOURCE_END in text
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
        has_authored_sources,
        has_generated_source_map,
    )


def flag(value: bool) -> str:
    return "Y" if value else "-"


def main() -> None:
    paths = sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md"))
    rows = [inspect(p) for p in paths]
    assert [r.part for r in rows] == list(range(51)), "Part 0–50 must be continuous"

    print("CHAPTER DEPTH AUDIT")
    print("part chars h2 eq code url F E R Auth Gen Src score title")
    for r in rows:
        print(
            f"{r.part:02d} {r.chars:5d} {r.h2:2d} {r.equations:2d} {r.code_blocks:2d} {r.urls:2d} "
            f"{flag(r.has_failure)} {flag(r.has_experiment)} {flag(r.has_research)} "
            f"{flag(r.has_authored_sources)} {flag(r.has_generated_source_map)} {flag(r.has_source_evidence)} "
            f"{r.structure_score}/6 {r.name}"
        )

    print("\nTHINNEST BY NON-WHITESPACE CHARACTERS")
    for r in sorted(rows, key=lambda x: x.chars)[:12]:
        print(f"Part {r.part:02d}: chars={r.chars}, structure={r.structure_score}/6 — {r.name}")

    print("\nLOWEST STRUCTURE COVERAGE")
    for r in sorted(rows, key=lambda x: (x.structure_score, x.chars))[:20]:
        print(f"Part {r.part:02d}: {r.structure_score}/6 missing={','.join(r.missing) or 'none'}")

    print("\nSUMMARY")
    print(f"chapters={len(rows)}")
    print(f"median_chars={int(sorted(r.chars for r in rows)[len(rows)//2])}")
    print(f"with_equations={sum(r.equations > 0 for r in rows)}/51")
    print(f"with_authored_sources={sum(r.has_authored_sources for r in rows)}/51")
    print(f"with_generated_source_map={sum(r.has_generated_source_map for r in rows)}/51")
    print(f"with_source_evidence={sum(r.has_source_evidence for r in rows)}/51")
    print(f"with_failure_section={sum(r.has_failure for r in rows)}/51")
    print(f"with_experiment_section={sum(r.has_experiment for r in rows)}/51")
    print(f"with_research_question_section={sum(r.has_research for r in rows)}/51")

    failures = [r for r in rows if r.structure_score != 6]
    if failures:
        print("\nPUBLICATION BASELINE FAILED")
        for r in failures:
            print(f"Part {r.part:02d}: missing={','.join(r.missing)}")
        raise SystemExit(1)

    print("PUBLICATION BASELINE PASSED: all 51 chapters satisfy 6/6 structural requirements.")


if __name__ == "__main__":
    main()
