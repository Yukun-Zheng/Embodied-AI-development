#!/usr/bin/env python3
"""Report checkable manuscript claims that may need local evidence attribution.

This is deliberately a report-only audit at first. It looks for sentences with
high-verifiability signals (dates, model versions, percentages, frequencies,
parameter/data-scale numbers) and asks whether direct evidence appears nearby.
A canonical chapter source-map fallback is NOT counted as local attribution:
important numeric/frontier claims should eventually cite evidence near the claim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"

# Signals chosen for precision over recall. Ordinary equation numbers and Part
# numbers should not dominate the report.
CHECKABLE_PATTERNS = [
    re.compile(r"\b(?:19|20)\d{2}(?:[-–/]\d{1,2})?\b"),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|Hz|kHz|MHz|GHz|ms|s|GB|MB|TB|B|M|K)\b", re.I),
    re.compile(r"\b\d+(?:\.\d+)?[BbMmKk]\s*(?:parameters?|params?|checkpoint)?\b", re.I),
    re.compile(r"\b(?:N1\.\d+|π0\.\d+|V-JEPA\s*2(?:\.1)?|Gemini Robotics\s*\d+(?:\.\d+)?)\b", re.I),
]

DIRECT_EVIDENCE = re.compile(
    r"https?://|\[[^\]]+\]\([^\)]+\)|doi:|arxiv:|\[@[^\]]+\]",
    re.I,
)

SKIP_LINE_PREFIXES = ("#", "```", "|", "- [", "<!--")


@dataclass
class Finding:
    part: int
    path: str
    line: int
    text: str


def is_checkable(text: str) -> bool:
    return any(p.search(text) for p in CHECKABLE_PATTERNS)


def nearby_evidence(lines: list[str], idx: int, radius: int = 3) -> bool:
    lo = max(0, idx - radius)
    hi = min(len(lines), idx + radius + 1)
    return any(DIRECT_EVIDENCE.search(lines[j]) for j in range(lo, hi))


def main() -> None:
    findings: list[Finding] = []
    total_checkable = 0
    locally_supported = 0

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
            if not is_checkable(stripped):
                continue

            total_checkable += 1
            if nearby_evidence(lines, idx):
                locally_supported += 1
            else:
                findings.append(
                    Finding(
                        part=part,
                        path=path.relative_to(ROOT).as_posix(),
                        line=idx + 1,
                        text=stripped[:220],
                    )
                )

    print("CLAIM → EVIDENCE AUDIT (REPORT ONLY)")
    print(f"checkable_lines={total_checkable}")
    print(f"locally_supported={locally_supported}")
    print(f"needs_review={len(findings)}")
    if total_checkable:
        print(f"local_support_rate={locally_supported / total_checkable:.1%}")

    by_part: dict[int, list[Finding]] = {}
    for f in findings:
        by_part.setdefault(f.part, []).append(f)

    print("\nTOP PARTS NEEDING LOCAL ATTRIBUTION")
    for part, part_findings in sorted(by_part.items(), key=lambda item: (-len(item[1]), item[0]))[:20]:
        print(f"Part {part:02d}: {len(part_findings)}")

    print("\nSAMPLE FINDINGS")
    for f in findings[:80]:
        print(f"{f.path}:{f.line}: {f.text}")

    print(
        "\nNOTE: This audit intentionally over-reports some historical/context lines. "
        "Review findings before turning any rule into a hard gate."
    )


if __name__ == "__main__":
    main()
