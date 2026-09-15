#!/usr/bin/env python3
"""Insert local primary-source attribution into Part 24 frontier subsections.

The chapter already has a global source list. This script adds concise subsection-
level evidence so dated/versioned capability claims are auditable where they are
made without turning every sentence into a link wall. The operation is idempotent.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "book" / "chapters" / "24-vla-second-stage-2024-2026.md"

EVIDENCE = {
    "## 24.4 π*0.6：从 Demonstration 走向 Experience / RL": (
        "**Primary evidence:** Physical Intelligence, *π*0.6: A VLA That Learns From Experience* — "
        "https://www.pi.website/blog/pistar06"
    ),
    "## 24.5 π0.7：Steerability 与 Emergent Capability": (
        "**Primary evidence:** Physical Intelligence, π0.7 — https://www.pi.website/blog/pi07"
    ),
    "## 24.8 GR00T N1.6：VLM、DiT 与 Loco-Manipulation 扩展": (
        "**Primary evidence:** NVIDIA Research, GR00T N1.6 — "
        "https://research.nvidia.com/labs/gear/gr00t-n1_6/"
    ),
    "## 24.9 GR00T N1.7：新 VLM Backbone、Embodiment Tags 与部署栈": (
        "**Primary evidence:** NVIDIA Isaac-GR00T N1.7 release — "
        "https://github.com/NVIDIA/Isaac-GR00T/releases/tag/n1.7-release  ·  "
        "official source tree / current N1.7 documentation — https://github.com/NVIDIA/Isaac-GR00T"
    ),
    "## 24.10 Gemini Robotics：VLA 与 Embodied Reasoning 分层": (
        "**Primary evidence:** Google DeepMind, Gemini Robotics model family — "
        "https://deepmind.google/models/gemini-robotics/"
    ),
    "## 24.11 Gemini Robotics 1.5：Motion Transfer 与 Embodiment Adaptation": (
        "**Primary evidence:** Google DeepMind, *Gemini Robotics 1.5 brings AI agents into the physical world* — "
        "https://deepmind.google/blog/gemini-robotics-15-brings-ai-agents-into-the-physical-world/"
    ),
    "## 24.12 Gemini Robotics 2：Whole-Body VLA": (
        "**Primary evidence:** Google DeepMind, *Gemini Robotics 2 brings whole body intelligence to robots* — "
        "https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/"
    ),
    "## 24.13 Gemini Robotics On-Device 2：端侧推理与快速适配": (
        "**Primary evidence:** Google DeepMind, Gemini Robotics On-Device 2 — "
        "https://deepmind.google/models/gemini-robotics/on-device/"
    ),
    "## 24.14 Helix：On-Board、Multi-Rate 与 Whole-Body": (
        "**Primary evidence:** Figure, Helix — https://www.figure.ai/news/helix  ·  "
        "Helix 02 — https://www.figure.ai/news/helix-02"
    ),
}


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    changed: list[str] = []
    for heading, evidence in EVIDENCE.items():
        if heading not in text:
            raise SystemExit(f"Missing expected heading: {heading}")
        marker = heading + "\n\n" + evidence
        if marker in text:
            continue
        text = text.replace(heading + "\n", heading + "\n\n" + evidence + "\n", 1)
        changed.append(heading.split("：", 1)[0].replace("## ", ""))

    if changed:
        PATH.write_text(text, encoding="utf-8")
    print(f"Part 24 local primary evidence: changed={changed or 'none'}")


if __name__ == "__main__":
    main()
