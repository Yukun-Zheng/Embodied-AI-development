#!/usr/bin/env python3
"""Synchronize stable repository facts in README.md.

The README is human-authored, but a few counts/asset links are machine-checkable
and tend to drift as the textbook grows. This script updates only those exact
facts and is safe to rerun.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

REPLACEMENTS = {
    "- **[知识依赖图](book/DEPENDENCY_GRAPH.md)** / **[概念索引](book/CONCEPT_INDEX.md)** — 支持跳读与按概念查找":
        "- **[知识依赖图](book/DEPENDENCY_GRAPH.md)** / **[Research Crosswalk](book/RESEARCH_CROSSWALK.md)** / **[概念索引](book/CONCEPT_INDEX.md)** — 从 prerequisite 跳到实验、源码与研究问题",
    "- **[Model × Data × Hardware × Benchmark Matrix](references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md)**":
        "- **[Model × Data × Hardware × Benchmark Matrix](references/MODEL_DATA_HARDWARE_BENCHMARK_MATRIX.md)**\n- **[51-Part Primary Source Map](references/CHAPTER_SOURCE_ANCHORS.md)** — 每个 canonical Chapter 的 foundation / primary / official-source 入口",
    "- **Textbook QA** — Part 0–50 连续性、TOC、关键资产与本地 Markdown 链接；":
        "- **Textbook QA** — Part 0–50 连续性、TOC、关键资产、本地链接，以及 51/51 Chapter 的 6/6 publication baseline；",
    "- **10** 个最小可执行脚本；":
        "- **13** 个最小可执行脚本 + 一键 regression；",
    "│   ├── DEPENDENCY_GRAPH.md\n":
        "│   ├── DEPENDENCY_GRAPH.md\n│   ├── RESEARCH_CROSSWALK.md\n",
    "│   ├── SOURCE_CODE_ATLAS.md\n":
        "│   ├── CHAPTER_SOURCE_ANCHORS.md\n│   ├── SOURCE_CODE_ATLAS.md\n",
    "- minimal-code / textbook-QA / website-build 三层 CI；":
        "- minimal-code / textbook-QA / website-build 三层 CI；\n- **51/51 Chapter 结构基线 6/6**：equation + dataflow/code + failure + experiment + research questions + source evidence；",
    "v1.x 将继续重点推进：**逐章 primary-source citations、simulator-level executable labs、真实/仿真实验结果回填、更多源码级解剖、跨章交叉引用与出版编辑**。":
        "v1.x 将继续重点推进：**高可核查 claim 的就地 primary-source attribution、simulator-level executable labs、真实/仿真实验结果回填、更多源码级解剖、跨章交叉引用与出版编辑**。",
}


def main() -> None:
    text = README.read_text(encoding="utf-8")
    original = text
    for old, new in REPLACEMENTS.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"README sync anchor missing and replacement absent:\n{old}")

    if text != original:
        README.write_text(text, encoding="utf-8")
        print("README facts synchronized.")
    else:
        print("README facts already synchronized.")


if __name__ == "__main__":
    main()
