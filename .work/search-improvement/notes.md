# Notes

## 2026-05-11

### Investigation 1-1: Knowledge File Structure

#### File Structure (consistent across all 5 versions)

Standard keys: `id`, `title`, `content`, `no_knowledge_content`, `sections`
Excel P1 adds: `sheet_type`, `columns`, `data_rows`
Excel P2 adds: `sheet_type` + various `p2_*` keys
Section keys: `id` (always `sN` format), `title`, `content`, `level` (2-5, absent for Excel-derived)

#### Scale per version

| Version | Files | Sections | Total content |
|---------|-------|----------|---------------|
| v6 | 353 | 2,586 | 1.8M chars |
| v5 | 534 (+3 broken JSON) | 4,061 | 2.5M chars |
| v1.4 | 489 | 3,277 | 2.3M chars |
| v1.3 | 327 | 2,227 | 1.7M chars |
| v1.2 | 321 | 2,229 | 1.7M chars |

v5 has 3 broken JSON files in `assets/etl-etl/`.

#### Content storage patterns (v6)

- **100 files** with 0 sections → all content at file level (content field)
- **220 files** with sections AND file-level content → file content is TOC listing section titles
- **33 files** with sections but no file-level content

File-level content median: 404 chars. Section content median: 320 chars.
Section content p90: 1,535 chars, p95: 2,251 chars.

#### Section titles — search implications

- 2,586 total sections in v6
- **375 (14.5%) have short titles (<5 chars)** — generic like "概要", "注意点", "NG例"
- **241 unique titles appear in multiple files** — "モジュール一覧" (100x), "アプリケーションフレームワーク" (87x), "使用方法" (48x)
- These generic titles are meaningless without parent file context

**Critical for index.md**: Section entries must include file title for disambiguation. A section titled "使用方法" under "ユニバーサルDAO" vs "データベースアクセス" means completely different things.

#### Section hierarchy (level field)

RST-derived files have level 2-5 hierarchy. Excel-derived sections lack level field.
Distribution (v6): L2=1,043, L3=911, L4=214, L5=43, N/A=375

The hierarchy reflects RST heading structure: L2 = top-level sections, L3 = subsections, etc.

#### Categories (v6, 9 subdirectories)

| Category | Files | Sections | Notes |
|----------|-------|----------|-------|
| component | 130 | 996 | Core framework docs — libraries + handlers |
| processing-pattern | 79 | 186 | App type specific (web, batch, REST, messaging) |
| development-tools | 55 | 524 | Testing framework, toolbox |
| setup | 34 | 260 | Blank project, cloud-native, config |
| about | 20 | 78 | Overview, architecture, migration |
| guide | 18 | 167 | Patterns, samples |
| releases | 13 | 319 | Release notes (Excel-derived) |
| check | 4 | 56 | Security checklist (Excel-derived) |

#### Current search infrastructure

- `index.toon`: File-level index (356 lines). Fields: title, type, category, processing_patterns, path. **No section-level info.**
- `full-text-search.sh`: Keyword OR search across all sections, returns top 15 scored matches
- `read-sections.sh`: Bulk section reader by `file:sectionId`
- No `index.md` or `terms.json` yet

#### Current search flow

1. Keywords → full-text-search.sh → section hits
2. If hits → section judgment (AI reads content, classifies High/Partial/None)
3. If no hits → file selection from index.toon (AI) → enumerate sections → section judgment

### Investigation 1-2: Index Analysis

#### Current index.toon

356 lines, file-level only. Fields: title, type, category, processing_patterns, path.
No section-level info. AI must guess files, then read all sections.

#### Token budget for different index granularities

| Granularity | v6 entries | v6 tokens | v5 tokens | v1.4 tokens |
|-------------|-----------|-----------|-----------|-------------|
| File-level only | 353 | ~6K | ~8K | ~7K |
| L2 sections only | 1,152 | ~31K | ~40K | ~33K |
| All sections | 2,686 | ~74K | ~100K+ | ~82K+ |

L2 index is the only option that provides section-level selection without being prohibitively large.
All sections is too big (~74K tokens for v6 alone). File-level misses the search target.

#### Key observations for index.md design

1. **Generic section titles require parent context**: 375 sections (14.5%) have titles <5 chars ("概要", "注意点"). Must pair with file title.
2. **109 files have no L2 sections** (either 0 sections or only Excel-derived) — these need file-level entries.
3. **L2 section count per file**: median ~4, max 21. Most files have 2-6 L2 sections.
4. **File-level content is TOC** — when sections exist, file content lists section titles hierarchically.
5. **annotate-index.sh** in the search design: script adds ★ annotations to index.md based on query. This allows pre-filtering before AI selection.

## 2026-05-12

### Task 1-5c': Must Section Re-verification

Verified all 24 QA scenarios by reading must section body text from v6 knowledge files.

**Method**: For each scenario, read the question + hearing answer, read the must section content, read other sections in the same file, judged whether the must section is indispensable.

**Result**: 23/24 correct, 1 change.

| Scenario | Change | Rationale |
|----------|--------|-----------|
| qa-13 | s14→s2 | s14 is batchInsert/batchUpdate/batchDelete (bulk perf optimization). Question is about REST single-record registration. s2 describes basic CRUD including single-record insert. |

All other scenarios verified correct — must sections are indispensable for answering each question, and no better alternative exists in the same file.

## 2026-05-12

### 1-5B: Must section re-verification (strict criteria)

4 independent QA agents evaluated all 24 scenarios without seeing simulation results.
Criteria: "Without this section, can the question be answered?" — only indispensable sections are must.

**Result**: 19/24 unchanged, 5 changes applied.

| Scenario | Change | Rationale |
|----------|--------|-----------|
| pre-02 | s8→acceptable, s16→must | Web validation requires InjectForm interceptor (s16), not just annotation syntax (s8) |
| qa-09 | s7 promoted to must | s8 is only 33 chars (API name). s7 has DB table layout and BasicBusinessDateProvider setup — needed for implementation |
| qa-11 | jaxrs:s5 added to must | Question explicitly asks about ログ出力. REST API logging mechanism is in s5, separate from s4 (response) |
| qa-12 | tag:s29→must, jaxrs:s7 added to must | Error message return requires both Web display layer (s29) and REST response body (s7) |
| qa-13 | rest-create:s1 promoted to must | Hearing says REST API. s2 alone (CRUD capability) doesn't give the REST implementation pattern |

## 2026-05-13

### 1-7: Benchmark run-001 (5 scenarios)

First end-to-end benchmark using run.py (semantic search Stage1+2 + answer generation Stage3).

**Scenarios**: pre-01, pre-02, qa-01, qa-05, qa-12a

**Results**:

| Metric | Value |
|--------|-------|
| Must section search HIT | 9/10 (90%) |
| Answer accuracy (auto) | 10/10 PRESENT (100%) |
| Hallucination (auto) | 0/5 PASS (all human review) |
| Avg execution time | 39s |
| Avg cost | ~$0.14/scenario |

**Search miss**: qa-12a — `handlers-HttpErrorHandler.json:s4` not in search results (known structural issue: file doesn't make it into Stage 1 top-10 pages).

**Answer accuracy despite search miss**: qa-12a scored 100% because both must facts were covered via `web-application-error-message.json:s1` and `handlers-on-error.json:s3` which describe the same error handling flow from a different angle.

**Hallucination all-FAIL**: Expected by design. The judge's gold standard is must+acceptable sections only. The answer includes information from other found sections (e.g., `handlers-main.json:s3` in pre-01). These are real knowledge file contents, not fabrications, but the judge can't verify them against its limited gold standard. Human review needed.

### Decision: Hallucination evaluation scope

The current hallucination gold standard (must+acceptable only) is too narrow for the benchmark. When the answer correctly uses information from searched-and-found sections beyond must/acceptable, the auto-judge flags them as hallucinations. This produces 100% false-positive rate, making the auto-judgment useless.

Options considered:
- A: Expand gold standard to include all actually-searched sections → breaks search/hallucination independence
- B: Accept the status quo, rely on human review → every scenario needs review, high manual burden
- C: Use all sections from the same files as must/acceptable → preserves independence while expanding coverage

Decision deferred to user review (1-8).
