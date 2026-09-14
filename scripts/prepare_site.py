#!/usr/bin/env python3
"""Prepare a clean MkDocs source tree from the repository textbook assets.

The repository remains organized for research and source-level work. This script
creates `.site-src/` as a disposable publication view so MkDocs can build the
book without moving the canonical manuscript files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".site-src"

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
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # Root README becomes the web homepage while preserving all its relative
    # links because the rest of the repository structure is mirrored below.
    copy_file("README.md", "index.md")

    for rel in COPY_FILES:
        copy_file(rel)
    for rel in COPY_DIRS:
        copy_dir(rel)

    # Publication-only assets.
    copy_file("docs-assets/mathjax.js", "javascripts/mathjax.js")
    copy_file("docs-assets/extra.css", "stylesheets/extra.css")

    print(f"Prepared website source at {OUT}")


if __name__ == "__main__":
    main()
