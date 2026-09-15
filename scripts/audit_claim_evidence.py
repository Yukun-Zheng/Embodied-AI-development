#!/usr/bin/env python3
"""Audit checkable manuscript claims for local evidence attribution.

Two classes are intentionally separated:
A) high-confidence historical/frontier factual claims — releases, dated public
   capabilities, version changes, public model/data scale. These are a hard
   publication gate and require local primary-source attribution.
B) quantitative engineering statements — rates, delays, experiment sweep values,
   toy assumptions. These remain advisory review hints, not automatic citation
   obligations.

Evidence is local when it appears either within ±3 lines OR elsewhere in the same
H2 subsection. A chapter-end source-map fallback does not support unrelated H2s.
Research/experiment sections, block-quoted snapshot notes, and generic methodology
statements are excluded from Class A so the metric rewards evidence rather than
link decoration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"

YEAR = re.compile(r"\b(?:19|20)\d{2}(?:[-–/]\d{1,2})?\b")
MODEL_VERSION = re.compile(
    r"\b(?:N1\.\d+|π0\.\d+|π\*0\.\d+|V-JEPA\s*2(?:\.1)?|"
    r"Gemini Robotics(?: On-Device)?\s*\d+(?:\.\d+)?|Helix\s*0?2|Cosmos\s*3)\b",
    re.I,
)
NUMERIC_SYSTEM = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:%|Hz|kHz|MHz|GHz|ms|GB|MB|TB)\b|"
    r"\b\d+(?:\.\d+)?[BbMmKk]\s*(?:parameters?|params?|checkpoint|model)?\b",
    re.I,
)
FRONTIER_VERBS = re.compile(
    r"发布|公布|推出|发布于|进入|标记为|支持|展示|报告|宣称|"
    r"released|published|announced|official|supports?|reported|demonstrated|latest|general availability",
    re.I,
)
FRONTIER_NAMES = re.compile(
    r"Physical Intelligence|NVIDIA|GR00T|Gemini Robotics|Google DeepMind|Figure|Helix|"
    r"V-JEPA|Meta|Cosmos|OpenVLA|Open X-Embodiment|RT-[12X]|Octo|DROID|TouchWorld|T-Rex",
    re.I,
)

DIRECT_EVIDENCE = re.compile(
    r"https?://|\[[^\]]+\]\([^\)]+\)|doi:|arxiv:|\[@[^\]]+\]",
    re.I,
)

SKIP_LINE_PREFIXES = ("#", "```", "|", "- [", "<!--", ">")
QUESTION_PREFIXES = ("为什么", "如何", "是否", "什么", "何时", "能否", "哪", "1.", "2.", "3.", "4.", "5.", "6.")
EXPERIMENT_CONTEXT = re.compile(r"假设|设定|模拟|扫描|注入|例如|例：|实验|比较|取值|sweep", re.I)
NONFACT_SECTION = re.compile(r"实验|练习|研究问题|research questions?|本章结论|结论", re.I)


@dataclass
class Finding:
    category: str
    part: int
    path: str
    line: int
    text: str
    supported: bool


def classification(text: str) -> str | None:
    stripped = text.strip()
    if stripped.startswith(QUESTION_PREFIXES):
        return None

    has_year = bool(YEAR.search(stripped))
    has_version = bool(MODEL_VERSION.search(stripped))
    has_frontier_name = bool(FRONTIER_NAMES.search(stripped))
    has_frontier_verb = bool(FRONTIER_VERBS.search(stripped))
    has_numeric = bool(NUMERIC_SYSTEM.search(stripped))

    # Class A deliberately requires a named contemporary system/organization.
    # This excludes generic methodological statements such as "in 2025–2026 we
    # should distinguish demos from independent reproduction".
    if has_frontier_name and (has_year or has_version) and (has_frontier_verb or has_version):
        return "A"
    if has_frontier_name and has_numeric and has_frontier_verb and not EXPERIMENT_CONTEXT.search(stripped):
        return "A"
    if has_numeric and not EXPERIMENT_CONTEXT.search(stripped):
        return "B"
    return None


def nearby_evidence(lines: list[str], idx: int, radius: int = 3) -> bool:
    lo = max(0, idx - radius)
    hi = min(len(lines), idx + radius + 1)
    return any(DIRECT_EVIDENCE.search(lines[j]) for j in range(lo, hi))


def current_h2(lines: list[str], idx: int) -> str:
    for j in range(idx, -1, -1):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            return lines[j][3:].strip()
    return ""


def h2_section_evidence(lines: list[str], idx: int) -> bool:
    """Evidence anywhere in the current H2 section counts as local attribution."""
    start = 0
    for j in range(idx, -1, -1):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            start = j
            break
    end = len(lines)
    for j in range(idx + 1, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            end = j
            break
    return any(DIRECT_EVIDENCE.search(lines[j]) for j in range(start, end))


def has_local_evidence(lines: list[str], idx: int) -> bool:
    return nearby_evidence(lines, idx) or h2_section_evidence(lines, idx)


def main() -> None:
    findings: list[Finding] = []

    for path in sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md")):
        part = int(path.name[:2])
        lines = path.read_text(encoding="utf-8").splitlines()
        in_code = False
        for idx, raw in enumerate(lines):
            stripped = raw.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code or not stripped:
                continue
            if stripped.startswith(SKIP_LINE_PREFIXES):
                continue
            if stripped.startswith(("\\[", "\\]", "$$")):
                continue
            if NONFACT_SECTION.search(current_h2(lines, idx)):
                continue

            category = classification(stripped)
            if category is None:
                continue
            findings.append(
                Finding(
                    category=category,
                    part=part,
                    path=path.relative_to(ROOT).as_posix(),
                    line=idx + 1,
                    text=stripped[:240],
                    supported=has_local_evidence(lines, idx),
                )
            )

    print("CLAIM → EVIDENCE AUDIT")
    for category, label in [("A", "frontier/historical facts"), ("B", "engineering quantitative statements")]:
        group = [f for f in findings if f.category == category]
        supported = sum(f.supported for f in group)
        missing = len(group) - supported
        rate = supported / len(group) if group else 1.0
        print(
            f"class_{category}_{label.replace(' ', '_')}="
            f"total:{len(group)}, locally_supported:{supported}, needs_review:{missing}, rate:{rate:.1%}"
        )

    high_missing = [f for f in findings if f.category == "A" and not f.supported]
    by_part: dict[int, list[Finding]] = {}
    for f in high_missing:
        by_part.setdefault(f.part, []).append(f)

    print("\nCLASS A — TOP PARTS NEEDING LOCAL PRIMARY EVIDENCE")
    for part, part_findings in sorted(by_part.items(), key=lambda item: (-len(item[1]), item[0]))[:20]:
        print(f"Part {part:02d}: {len(part_findings)}")

    print("\nCLASS A — ALL UNSUPPORTED FINDINGS")
    for f in high_missing:
        print(f"{f.path}:{f.line}: {f.text}")

    print("\nCLASS B — SAMPLE REVIEW HINTS")
    for f in [x for x in findings if x.category == "B" and not x.supported][:30]:
        print(f"{f.path}:{f.line}: {f.text}")

    if high_missing:
        raise SystemExit(
            f"CLASS-A PRIMARY-EVIDENCE GATE FAILED: {len(high_missing)} factual claim(s) lack local primary evidence."
        )

    class_a = [f for f in findings if f.category == "A"]
    print(
        f"\nCLASS-A PRIMARY-EVIDENCE GATE PASSED: {len(class_a)}/{len(class_a)} detected "
        "frontier/historical factual claims have local primary evidence."
    )
    print(
        "Class B remains advisory because many quantitative values are engineering examples, "
        "toy assumptions or experiment settings rather than externally sourced facts."
    )


if __name__ == "__main__":
    main()