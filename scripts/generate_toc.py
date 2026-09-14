#!/usr/bin/env python3
"""Generate book/TOC.md from the actual Part 0-50 chapter manuscripts.

The chapter files are the source of truth. This prevents the detailed TOC from
silently drifting away from the independently maintained manuscript.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
OUTPUT = ROOT / "book" / "TOC.md"

VOLUMES = [
    (0, 1, "Volume 0　导论：智能为什么必须进入物理世界"),
    (2, 5, "Volume I　数学与计算语言"),
    (6, 11, "Volume II　机器人身体、几何、力学与控制"),
    (12, 17, "Volume III　感知、状态与世界表示"),
    (18, 21, "Volume IV　机器人学习的基础范式"),
    (22, 26, "Volume V　机器人基础模型：从 VLM 到 VLA"),
    (27, 31, "Volume VI　VLA 之后：推理、记忆、经验学习与世界模型"),
    (32, 36, "Volume VII　操作、导航、灵巧与人形"),
    (37, 39, "Volume VIII　持续学习、跨本体与发展型智能"),
    (40, 43, "Volume IX　仿真、数据基础设施与系统工程"),
    (44, 45, "Volume X　评测、可靠性与安全"),
    (46, 50, "Volume XI　研究方法、理论前沿与下一代具身智能"),
]

FRONT_MATTER = """# Complete Table of Contents

# 《具身智能：从物理世界到通用机器人》
## Embodied Intelligence: From Physical Principles to General-Purpose Robots

> **Curriculum baseline: v1.0 — knowledge frontier frozen at 2026-09-14.**
>
> 本目录由 `book/chapters/00-*.md` 到 `50-*.md` 的真实标题自动生成，**Chapter 是唯一真源**。不要手工维护一份会与正文漂移的平行目录。
>
> 主线：**物理世界 → 身体 → 感知 → 状态 → 决策 → 控制 → 学习 → 基础模型 → 预测与推理 → 泛化 → 经验学习 → 持续发展。**
>
> 模型会过时，知识结构不能随热点漂移。RT、Octo、OpenVLA、π、GR00T、Gemini Robotics、Helix、V-JEPA 等只作为历史节点和案例进入统一框架。

---
"""

APPENDIX = """
---

# Appendices　附录系统

- [Appendix A–Z：公式、系统、平台、Atlas 与 Checklists](./APPENDICES.md)
- [中英术语表](./GLOSSARY.md)
- [符号、坐标系与 Action Convention](./NOTATION_AND_CONVENTIONS.md)
- [30 组核心推导](./DERIVATIONS.md)
- [204 道章末题](./EXERCISES.md)
- [解题要点](./SOLUTION_SKETCHES.md)
- [36 周系统课程](./SYLLABUS_36_WEEKS.md)
- [概念索引](./CONCEPT_INDEX.md)
- [知识依赖图](./DEPENDENCY_GRAPH.md)

---

# 目录维护规则

1. `book/chapters/` 是正文与编号的唯一真源；
2. `book/TOC.md` 由 `scripts/generate_toc.py` 自动生成；
3. 新模型原则上进入现有 Part 的案例 / Atlas，而不是自动新增 Part；
4. 只有出现新的基本数学对象、训练范式或 physical-system interface，才考虑改变 Part 级骨架；
5. 每次前沿更新保留明确 snapshot 日期。
"""


def part_number(path: Path) -> int:
    m = re.match(r"(\d+)-", path.name)
    if not m:
        raise ValueError(f"chapter filename lacks numeric prefix: {path}")
    return int(m.group(1))


def volume_for(part: int) -> str:
    for lo, hi, title in VOLUMES:
        if lo <= part <= hi:
            return title
    raise ValueError(f"No volume mapping for Part {part}")


def extract_headings(path: Path) -> list[tuple[int, str]]:
    """Return Markdown #/## headings outside fenced code blocks."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,2})\s+(.+?)\s*$", line)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2)
        # Do not duplicate generic end matter into the detailed TOC.
        if level == 2 and text in {"Source anchors", "本章结论", "最小实验"}:
            continue
        out.append((level, text))
    return out


def main() -> None:
    chapters = sorted(
        [p for p in CHAPTER_DIR.glob("[0-9][0-9]-*.md")],
        key=part_number,
    )
    actual = [part_number(p) for p in chapters]
    expected = list(range(51))
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise SystemExit(f"Part sequence mismatch. missing={missing}, extra={extra}, actual={actual}")

    lines = [FRONT_MATTER.rstrip(), ""]
    current_volume: str | None = None

    for path in chapters:
        part = part_number(path)
        volume = volume_for(part)
        if volume != current_volume:
            if current_volume is not None:
                lines.extend(["", "---", ""])
            lines.extend([f"# {volume}", ""])
            current_volume = volume

        headings = extract_headings(path)
        if not headings or headings[0][0] != 1:
            raise SystemExit(f"{path}: missing top-level Part heading")

        top = headings[0][1]
        if not re.match(rf"Part\s+{part}(?:\D|$)", top):
            raise SystemExit(f"{path}: top heading does not match Part {part}: {top!r}")

        rel = path.relative_to(ROOT / "book").as_posix()
        lines.append(f"# [{top}](./{rel})")
        lines.append("")
        for level, text in headings[1:]:
            if level == 2:
                lines.append(f"## {text}")
        lines.append("")

    lines.append(APPENDIX.strip())
    lines.append("")

    text = "\n".join(lines)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"generated {OUTPUT} from {len(chapters)} chapters ({len(text)} chars)")


if __name__ == "__main__":
    main()
