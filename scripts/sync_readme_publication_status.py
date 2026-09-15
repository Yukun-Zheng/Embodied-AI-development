#!/usr/bin/env python3
"""Synchronize README facts with the current publication-quality gates.

This is intentionally narrow and idempotent: it updates only stable status lines
whose truth is enforced by CI, avoiding a second hand-maintained source of facts.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "README.md"

REPLACEMENTS = {
    "- **Textbook QA** — Part 0–50 连续性、TOC、关键资产、本地链接，以及 51/51 Chapter 的 6/6 publication baseline；":
        "- **Textbook QA** — Part 0–50 连续性、TOC、关键资产、本地链接、51/51 Chapter 的 6/6 publication baseline，以及 Class-A local primary-evidence gate；",
    "v1.x 将继续重点推进：**高可核查 claim 的就地 primary-source attribution、simulator-level executable labs、真实/仿真实验结果回填、更多源码级解剖、跨章交叉引用与出版编辑**。":
        "v1.x 将继续重点推进：**simulator-level executable labs、真实/仿真实验结果回填、更多源码级解剖、跨章交叉引用、citation provenance 与出版编辑**。",
}

STATUS_ANCHOR = "- **51/51 Chapter 结构基线 6/6**：equation + dataflow/code + failure + experiment + research questions + source evidence；"
EVIDENCE_STATUS = "- **Class-A 前沿/历史事实：100% local primary evidence（CI hard gate）**；Class B 工程量化示例保持 advisory；"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    changed = False

    for old, new in REPLACEMENTS.items():
        if new in text:
            continue
        if old not in text:
            raise SystemExit(f"README status anchor drifted; expected text not found: {old}")
        text = text.replace(old, new, 1)
        changed = True

    if EVIDENCE_STATUS not in text:
        if STATUS_ANCHOR not in text:
            raise SystemExit("README 6/6 publication-baseline anchor not found")
        text = text.replace(STATUS_ANCHOR, STATUS_ANCHOR + "\n" + EVIDENCE_STATUS, 1)
        changed = True

    if changed:
        PATH.write_text(text, encoding="utf-8")
        print("README publication status synchronized.")
    else:
        print("README publication status already synchronized.")


if __name__ == "__main__":
    main()
