# 教材维护与发布工程

本文件定义《具身智能：从物理世界到通用机器人》的**长期仓库维护规则**。目标不是增加更多自动化，而是保证正文、证据、代码、目录与网站之间始终只有清晰的 canonical source，并让自动化只负责可机械验证的事情。

---

## 1. Canonical source 原则

长期维护遵循以下唯一真源：

```text
book/chapters/                 → Part 0–50 正文唯一真源
references/CHAPTER_SOURCE_ANCHORS.md
                               → 51-Part primary-source map
case-studies/                  → canonical source-level case studies
code/minimal/                  → 最小可执行机制代码
book/TOC.md                    → 由 chapter manuscript 自动生成
.site-src/ + .site-mkdocs.yml → disposable publication view，不提交为正文
```

不要重新建立平行正文、平行目录或第二套 Case Study。任何 derivative view 都必须能够从 canonical source 重建。

---

## 2. 长期保留的 GitHub Actions

仓库只长期保留五条自动化链。

### 2.1 `minimal-code-regression.yml`

职责：执行 [`code/minimal/run_all.py`](../code/minimal/run_all.py)，保证最小机制脚本仍可运行。

当前 suite 覆盖 13 个最小实验，包括 SE(3)、IK、控制、Kalman、BC/DAgger、生成式动作、World Model + MPC、action tokenization、chunk latency 与 cross-embodiment interface。

原则：

- minimal example 必须 CPU 可运行；
- 断言服务于机制正确性，不追求 benchmark 性能；
- 新增脚本后必须接入 `run_all.py`，不能只把文件放进目录。

### 2.2 `book-qa.yml`

职责：教材结构、链接和证据的核心 publication gate。

它依次执行：

```text
scripts/validate_book.py
→ scripts/audit_chapters.py
→ scripts/audit_claim_evidence.py
```

其中：

1. `validate_book.py` 检查 Part 0–50 连续性、generated TOC、关键资产与本地 Markdown 链接；
2. `audit_chapters.py` 强制 **51/51 Chapter = 6/6**；
3. `audit_claim_evidence.py` 强制 Class-A 前沿/历史事实拥有 local primary evidence。

### 2.3 `site-build.yml`

职责：构建 disposable MkDocs publication view，并做关键页面 smoke test。

必须验证：

- 51 Part 动态导航；
- Research Crosswalk；
- 51-Part Primary Source Map；
- Part 0 / 24 / 50；
- ACT / OpenVLA / GR00T N1.7 / V-JEPA 2.1 / World Model case studies；
- Source-Code Atlas；
- MathJax / Mermaid publication stack。

构建 artifact 只用于发布验收，不反向成为正文真源。

### 2.4 `sync-toc.yml`

职责：当 Chapter H1 / section structure 改变时，从真实 manuscript 重建 [`book/TOC.md`](TOC.md)。

目录不允许手工维护成第二套知识结构。

### 2.5 `sync-chapter-sources.yml`

职责：保证每个 Chapter 至少存在 canonical source entry point。

- 已有 authored source section：保留 authored section；
- 没有 authored section：注入指向 [`references/CHAPTER_SOURCE_ANCHORS.md`](../references/CHAPTER_SOURCE_ANCHORS.md) 的 generated fallback；
- 某章后来获得直接来源：移除旧 fallback，避免一章出现两套 source section。

注意：generated source-map fallback 只保证“有来源入口”，**不能替代重要事实 claim 的局部 attribution**。

---

## 3. 51/51 Chapter 的 6/6 publication baseline

每一个 Part 都必须同时满足：

1. **Equation**：至少有一个 display equation；
2. **Dataflow / Code**：至少有一个代码块、数据流或可执行接口视角；
3. **Failure Section**：显式 Markdown failure heading；
4. **Experiment Section**：显式 Markdown experiment heading；
5. **Research Questions**：显式 Markdown research-question heading；
6. **Source Evidence**：authored primary source 或 canonical source-map entry。

这不是“六个关键词”，而是最低教学结构：

```text
formal object
→ executable mechanism
→ where it fails
→ how to test it
→ what remains unknown
→ where the evidence comes from
```

`audit_chapters.py` 已把这套要求设为硬门槛。编辑任何 Chapter 时，不允许为了缩短正文破坏其中任一层。

---

## 4. Claim → Evidence gate

[`scripts/audit_claim_evidence.py`](../scripts/audit_claim_evidence.py) 将可核查陈述分成两类。

### Class A：硬门槛

包括：

- 版本发布；
- 具体发布日期；
- 官方公开能力；
- model / checkpoint scale；
- 明确的前沿系统版本变化。

要求：在 claim 附近或同一 H2 section 内存在**一手来源**，优先使用原始论文、官方项目页、官方仓库/Release、官方技术文档。

当前基线：**所有被审计器识别的 Class-A claim 均有 local primary evidence**。

### Class B：advisory

例如：

- “假设 policy 10 Hz”；
- “注入 500 ms latency”；
- “camera 30 Hz、joint 200 Hz”作为教学设定；
- 实验 sweep / toy parameter。

这些数字可能是实验设计，而不是外部事实，因此只进入 review report，不机械要求 citation。

核心原则：**不要为了漂亮的 citation rate 给教学假设乱贴来源。**

---

## 5. 迁移/补强脚本如何使用

`scripts/` 中保留了一批已经完成历史迁移任务的脚本，例如：

```text
apply_chapter_enrichments.py
apply_chapter_enrichments_round2.py
apply_chapter_enrichments_round3.py
apply_primary_evidence_round1.py
apply_primary_evidence_round2.py
sync_readme_facts.py
sync_readme_publication_status.py
```

这些脚本**保留，但不再拥有常驻自动写回 workflow**。

原因：

1. 它们记录了本版教材如何完成结构补强和证据补强，具有审计价值；
2. 未来需要重放或迁移时可以手工运行；
3. 但长期自动触发会让普通编辑产生意外 bot commit，并扩大 CI 维护面。

使用规则：

```bash
python scripts/<maintenance_script>.py
git diff --check
git diff
python scripts/validate_book.py
python scripts/audit_chapters.py
python scripts/audit_claim_evidence.py
```

确认 diff 符合预期后再提交。

---

## 6. 自动写回的边界

长期只允许**确定性 derived artifact**自动写回：

- TOC；
- generated chapter source fallback。

不应让 CI 自动决定并改写：

- 科学论断；
- 研究问题；
- failure analysis；
- 论文机制解释；
- primary evidence 选择；
- 实验结论。

这些属于作者判断，必须经过人工/智能审读后显式提交。

---

## 7. 发布前最小验收

一次 publication-ready 修改至少应满足：

```text
1. canonical manuscript edited
2. local links valid
3. generated TOC synchronized
4. 51/51 chapter 6/6 gate PASS
5. Class-A primary-evidence gate PASS
6. 13-script minimal regression PASS（若涉及 code/minimal）
7. MkDocs Website Build PASS
8. key-page smoke tests PASS
```

如果修改涉及前沿事实，还应额外确认：

- source 是 primary / official；
- 时间截面仍正确；
- claim 没有把官方 demo 写成 independent evidence；
- model、data、executor、controller 的贡献没有被混成一个品牌结论。

---

## 8. 下一阶段维护重点

当前结构完整性和 Class-A evidence attribution 已经成为硬门槛。后续质量提升重点不应继续机械增加章节，而应进入：

1. **simulator-level executable labs**：把更多 Chapter 的最小实验升级为可运行 Isaac Lab / RoboTwin / 其他物理平台实验；
2. **actual results backfill**：回填真实曲线、失败样例、日志和置信区间；
3. **citation provenance**：从“有来源”继续细化到 paper/version/commit/verified-date；
4. **cross-chapter editing**：消除重复概念、统一术语与 notation；
5. **source-level expansion**：继续增加真正能追到 processor / tensor / loss / executor / controller 的源码案例；
6. **publication editing**：图号、交叉引用、章节摘要、索引、打印/PDF 版式与正式发布流程。

长期目标保持不变：**让教材不仅能读，而且能被运行、验证、质疑和持续演化。**
