#!/usr/bin/env python3
"""Add canonical primary-source entry points to chapters that lack them.

The detailed 51-Part bibliography lives in references/CHAPTER_SOURCE_ANCHORS.md.
Chapters with their own explicit source/reference heading are left untouched.
For the rest, this script appends a small generated source block. It is
idempotent and safe to run repeatedly.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"
SOURCE_MAP = ROOT / "references" / "CHAPTER_SOURCE_ANCHORS.md"

START = "<!-- CHAPTER-SOURCE-MAP:START -->"
END = "<!-- CHAPTER-SOURCE-MAP:END -->"

SOURCE_MARKERS = [
    "source anchor",
    "source anchors",
    "延伸阅读",
    "references",
    "参考文献",
    "原始来源",
    "primary sources",
]


def authored_headings(text: str) -> list[str]:
    """Return Markdown headings outside the generated fallback block."""
    stripped = re.sub(
        rf"{re.escape(START)}.*?{re.escape(END)}",
        "",
        text,
        flags=re.DOTALL,
    )
    return [m.group(1).strip().lower() for m in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", stripped)]


def has_authored_source_section(text: str) -> bool:
    """True only when a real Markdown heading denotes a source/reference section."""
    return any(
        marker in heading
        for heading in authored_headings(text)
        for marker in SOURCE_MARKERS
    )


def generated_block(part: int) -> str:
    anchor = f"part-{part:02d}"
    return f"""

{START}
## Source anchors / 原始来源

本章的 canonical primary-source 入口见：
[`references/CHAPTER_SOURCE_ANCHORS.md — Part {part:02d}`](../../references/CHAPTER_SOURCE_ANCHORS.md#{anchor})。

该 source map 给出 foundation book、primary paper 或官方项目/源码入口；涉及具体数值、版本或能力 claim 时，正文仍应就地标注来源。
{END}
"""


def main() -> None:
    if not SOURCE_MAP.exists():
        raise SystemExit(f"Missing source map: {SOURCE_MAP}")

    changed = 0
    skipped = 0
    for path in sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md")):
        part = int(path.name[:2])
        text = path.read_text(encoding="utf-8")

        if has_authored_source_section(text):
            # If a chapter later gains direct/authored anchors, remove any old
            # generated fallback so there is only one source section.
            cleaned = re.sub(
                rf"\n*{re.escape(START)}.*?{re.escape(END)}\n*",
                "\n",
                text,
                flags=re.DOTALL,
            ).rstrip() + "\n"
            if cleaned != text:
                path.write_text(cleaned, encoding="utf-8")
                changed += 1
            else:
                skipped += 1
            continue

        block = generated_block(part)
        if START in text:
            new_text = re.sub(
                rf"\n*{re.escape(START)}.*?{re.escape(END)}\n*",
                block,
                text,
                flags=re.DOTALL,
            )
        else:
            new_text = text.rstrip() + block

        if not new_text.endswith("\n"):
            new_text += "\n"
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
        else:
            skipped += 1

    print(f"Chapter source sync: changed={changed}, already-authored/unchanged={skipped}")


if __name__ == "__main__":
    main()
