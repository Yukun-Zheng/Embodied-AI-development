#!/usr/bin/env python3
"""Repository-wide QA for the living textbook.

Checks:
1. Part 0-50 chapter sequence is complete and unique.
2. Every chapter's top-level heading matches its file number.
3. Required textbook assets exist.
4. Local Markdown links resolve to real files/directories.
5. book/TOC.md is exactly what scripts/generate_toc.py would generate.
6. No obvious TODO/TBD/placeholder markers remain in manuscript/reference Markdown.

Only Python stdlib is required.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "book" / "chapters"

REQUIRED = [
    "README.md",
    "BOOK_PLAN.md",
    "AUTHORING_GUIDE.md",
    "book/README.md",
    "book/TOC.md",
    "book/APPENDICES.md",
    "book/GLOSSARY.md",
    "book/NOTATION_AND_CONVENTIONS.md",
    "book/DERIVATIONS.md",
    "book/EXERCISES.md",
    "book/SOLUTION_SKETCHES.md",
    "book/SYLLABUS_36_WEEKS.md",
    "book/CONCEPT_INDEX.md",
    "book/DEPENDENCY_GRAPH.md",
    "figures/CORE_DIAGRAMS.md",
    "labs/LABS.md",
    "labs/EXPERIMENT_PROTOCOL.md",
    "references/REFERENCES.md",
    "references/READING_MAP.md",
    "references/SOURCE_CODE_ATLAS.md",
    "references/MODEL_ATLAS.md",
    "references/DATASET_ATLAS.md",
    "references/HARDWARE_ATLAS.md",
    "references/BENCHMARK_ATLAS.md",
    "references/FAILURE_ATLAS.md",
    "references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md",
    "case-studies/README.md",
]

# Scan Markdown that is part of the textbook/source layer. We deliberately do not
# scan generated build output or third-party/vendor directories.
SCAN_DIRS = [
    ROOT,
    ROOT / "book",
    ROOT / "figures",
    ROOT / "labs",
    ROOT / "references",
    ROOT / "case-studies",
    ROOT / "code",
]

SKIP_DIR_NAMES = {
    ".git",
    ".github",
    ".venv",
    "site",
    "__pycache__",
    "node_modules",
}

LOCAL_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
PART_FILE_RE = re.compile(r"^(\d+)-.*\.md$")
TOP_HEADING_RE = re.compile(r"^#\s+Part\s+(\d+)(?:\D|$)")
BAD_MARKER_RE = re.compile(r"\b(?:TODO|TBD|PLACEHOLDER)\b", re.IGNORECASE)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def iter_markdown_files() -> list[Path]:
    # ROOT/*.md plus recursive content under selected subdirectories.
    files: set[Path] = set(ROOT.glob("*.md"))
    for base in SCAN_DIRS[1:]:
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            files.add(path)
    return sorted(files)


def check_required(errors: list[str]) -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            fail(errors, f"missing required asset: {rel}")


def chapter_number(path: Path) -> int:
    m = PART_FILE_RE.match(path.name)
    if not m:
        raise ValueError(path)
    return int(m.group(1))


def check_chapters(errors: list[str]) -> None:
    chapters = sorted(
        [p for p in CHAPTER_DIR.glob("[0-9][0-9]-*.md") if PART_FILE_RE.match(p.name)],
        key=chapter_number,
    )
    actual = [chapter_number(p) for p in chapters]
    expected = list(range(51))
    if actual != expected:
        fail(errors, f"Part sequence must be 0..50 exactly; got {actual}")

    seen: set[int] = set()
    for path in chapters:
        n = chapter_number(path)
        if n in seen:
            fail(errors, f"duplicate Part number: {n} ({path.relative_to(ROOT)})")
        seen.add(n)

        first_heading = None
        in_fence = False
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.rstrip()
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if line.startswith("# "):
                first_heading = line
                break
        if first_heading is None:
            fail(errors, f"chapter lacks top-level heading: {path.relative_to(ROOT)}")
            continue
        m = TOP_HEADING_RE.match(first_heading)
        if not m or int(m.group(1)) != n:
            fail(
                errors,
                f"chapter heading/file mismatch: {path.relative_to(ROOT)} -> {first_heading!r}",
            )


def strip_link_target(raw: str) -> str:
    target = raw.strip()
    # Markdown permits optional title after a URL. Handle the common quoted form.
    if ' "' in target:
        target = target.split(' "', 1)[0]
    if " '" in target:
        target = target.split(" '", 1)[0]
    # Strip optional angle brackets.
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    target = unquote(target)
    return target.strip()


def check_links(errors: list[str]) -> None:
    for md in iter_markdown_files():
        text = md.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for raw_target in LOCAL_LINK_RE.findall(line):
                target = strip_link_target(raw_target)
                if not target:
                    continue
                lower = target.lower()
                if lower.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                    continue
                # Ignore GitHub/Jekyll template-ish links rather than guessing.
                if target.startswith(("{{", "${")):
                    continue

                resolved = (md.parent / target).resolve()
                try:
                    resolved.relative_to(ROOT.resolve())
                except ValueError:
                    fail(
                        errors,
                        f"local link escapes repository: {md.relative_to(ROOT)}:{line_no} -> {target}",
                    )
                    continue

                if not resolved.exists():
                    fail(
                        errors,
                        f"broken local link: {md.relative_to(ROOT)}:{line_no} -> {target}",
                    )


def check_markers(errors: list[str]) -> None:
    # Dummy/example source code may legitimately contain TODO comments, so only
    # manuscript/reference Markdown is scanned for publication placeholders.
    allowed = {"code/minimal/README.md"}
    for md in iter_markdown_files():
        rel = md.relative_to(ROOT).as_posix()
        if rel in allowed:
            continue
        for line_no, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
            if BAD_MARKER_RE.search(line):
                fail(errors, f"unfinished marker in {rel}:{line_no}: {line.strip()}")


def check_toc(errors: list[str]) -> None:
    generator = ROOT / "scripts" / "generate_toc.py"
    toc = ROOT / "book" / "TOC.md"
    if not generator.exists() or not toc.exists():
        return

    original = toc.read_text(encoding="utf-8")
    # The generator writes book/TOC.md in place. Run it, compare, then restore
    # the original bytes even if the comparison fails.
    try:
        proc = subprocess.run(
            [sys.executable, str(generator)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            fail(errors, f"TOC generator failed:\n{proc.stdout}\n{proc.stderr}")
            return
        generated = toc.read_text(encoding="utf-8")
        if generated != original:
            fail(errors, "book/TOC.md is stale; run: python scripts/generate_toc.py")
    finally:
        toc.write_text(original, encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    check_required(errors)
    check_chapters(errors)
    check_links(errors)
    check_markers(errors)
    check_toc(errors)

    if errors:
        print("BOOK QA FAILED")
        for i, err in enumerate(errors, start=1):
            print(f"{i:03d}. {err}")
        return 1

    chapter_count = len(list(CHAPTER_DIR.glob("[0-9][0-9]-*.md")))
    md_count = len(iter_markdown_files())
    print(f"BOOK QA PASSED: {chapter_count} chapters, {md_count} Markdown files checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
