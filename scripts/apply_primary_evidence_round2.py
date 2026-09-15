#!/usr/bin/env python3
"""Attach local primary evidence to the remaining high-confidence frontier claims.

This is a curated, idempotent publication edit. Each targeted factual claim gets
one concise primary-evidence line immediately after it. Engineering examples and
methodological statements are intentionally left uncited by this script.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"

# path -> [(exact factual claim, primary-evidence line)]
PATCHES: dict[str, list[tuple[str, str]]] = {
    "01-history-and-lineage.md": [
        (
            "截至本书 2026-09-14 的冻结截面，GR00T N1.7 已进入公开源码主线。本书不把版本号本身当科学进步，而追踪 backbone、action expert、embodiment interface、executor 与 controller 的机制变化。",
            "**Primary evidence:** NVIDIA Isaac-GR00T official repository / current N1.7 documentation — https://github.com/NVIDIA/Isaac-GR00T",
        ),
        (
            "V-JEPA 2/2.1、robot video world models、world-action models 都在探索预测与控制的关系。",
            "**Primary evidence:** Meta V-JEPA 2 official source — https://github.com/facebookresearch/vjepa2  ·  V-JEPA 2.1 — https://arxiv.org/abs/2603.14482",
        ),
    ],
    "20-reinforcement-offline-online.md": [
        (
            "以 Physical Intelligence π*0.6 / 2026 online-RL 路线为代表，foundation policy 提供安全且较强的初始 behavior，RL 不再探索“什么是抓取”，而是优化“怎样更快更准地完成这个特殊任务”。",
            "**Primary evidence:** Physical Intelligence π*0.6 — https://www.pi.website/blog/pistar06  ·  efficient online RL — https://www.pi.website/research/rlt",
        ),
    ],
    "26-robot-data-human-video-cross-embodiment.md": [
        (
            "截至 2025–2026，Figure 和 Physical Intelligence 都公开展示/研究了 human video 到 robot capability transfer 的迹象，但这一方向仍需更严格的数据泄漏与任务重合控制。",
            "**Primary evidence:** Figure, Project Go-Big — https://www.figure.ai/news/project-go-big  ·  Physical Intelligence, Human-to-Robot Transfer — https://www.pi.website/research/human_to_robot",
        ),
    ],
    "28-robot-memory-lifelong-context.md": [
        (
            "2026 年 Physical Intelligence 公布的 Multi-Scale Embodied Memory（MEM）明确把 long-term 与 short-term memory 结合到 VLA 中，用于更长的多阶段任务。",
            "**Primary evidence:** Physical Intelligence, Multi-Scale Embodied Memory — https://www.pi.website/research/memory",
        ),
    ],
    "29-learning-from-experience-deployment.md": [
        (
            "2026 年 Physical Intelligence 公布了针对 precise manipulation 的 efficient online RL 方法，核心动机是：",
            "**Primary evidence:** Physical Intelligence, efficient online RL for precise manipulation — https://www.pi.website/research/rlt",
        ),
    ],
    "30-world-models-predictive-intelligence.md": [
        (
            "V-JEPA 2 将大规模视频自监督表示与 prediction / planning 连接起来。",
            "**Primary evidence:** Meta V-JEPA 2 official source — https://github.com/facebookresearch/vjepa2",
        ),
        (
            "Meta 于 2026-03 发布 V-JEPA 2.1，强调更高质量且时间一致的 dense video features。",
            "**Primary evidence:** V-JEPA 2.1 — https://arxiv.org/abs/2603.14482",
        ),
    ],
    "31-generative-worlds-video-physical-ai.md": [
        (
            "到 2026 年，Cosmos 3 进一步把：",
            "**Primary evidence:** NVIDIA Cosmos 3 research — https://research.nvidia.com/labs/cosmos-lab/cosmos3/",
        ),
        (
            "NVIDIA 官方公开资料将 Cosmos 3 描述为可用于 world simulation、reasoning、synthetic data 和 World Action Model backbone 的开放模型。",
            "**Primary evidence:** NVIDIA Cosmos 3 — https://research.nvidia.com/labs/cosmos-lab/cosmos3/  ·  NVIDIA Cosmos platform — https://www.nvidia.com/en-us/ai/cosmos/",
        ),
    ],
    "35-humanoid-whole-body-intelligence.md": [
        (
            "2026 的 Gemini Robotics 2、Helix 02、GR00T 路线表明 VLA / foundation policy 正从 tabletop 进入 whole-body。",
            "**Primary evidence:** Google DeepMind Gemini Robotics 2 — https://deepmind.google/blog/gemini-robotics-2-brings-whole-body-intelligence-to-robots/  ·  Figure Helix 02 — https://www.figure.ai/news/helix-02  ·  NVIDIA Isaac-GR00T — https://github.com/NVIDIA/Isaac-GR00T",
        ),
    ],
    "37-cross-embodiment-intelligence.md": [
        (
            "2026 的 Gemini Robotics On-Device 2 等公开系统把 few-hour adaptation 作为重要能力，但科学比较需要统一适配预算。",
            "**Primary evidence:** Google DeepMind Gemini Robotics On-Device 2 — https://deepmind.google/models/gemini-robotics/on-device/",
        ),
    ],
}


def patch_file(filename: str, entries: list[tuple[str, str]]) -> int:
    path = CHAPTERS / filename
    text = path.read_text(encoding="utf-8")
    changed = 0
    for claim, evidence in entries:
        marker = claim + "\n\n" + evidence
        if marker in text:
            continue
        if claim not in text:
            raise SystemExit(f"Missing expected claim in {filename}: {claim}")
        text = text.replace(claim, marker, 1)
        changed += 1
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def main() -> None:
    total = 0
    touched: list[str] = []
    for filename, entries in PATCHES.items():
        changed = patch_file(filename, entries)
        total += changed
        if changed:
            touched.append(filename[:2])
    print(f"Local primary evidence round 2: inserted={total}, parts={touched or 'none'}")


if __name__ == "__main__":
    main()
