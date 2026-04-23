# QO4 Review (Round 4) — index.toon 網羅性

**Reviewer**: QA Engineer (independent; bias-avoidance mode — spec authoritative; v6-passing = weak evidence)
**Date**: 2026-04-23
**Scope**: `check_index_coverage` vs spec §3-3 QO4 (4 FAIL conditions)
**Sources**:
- Spec: `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 QO4 (lines 279, 299–306)
- Impl: `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 246–311)
- Tests: `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py::TestCheckIndexCoverage` (lines 276–391)

## Overall Assessment

**Rating**: 4 / 5
**Summary**: All four spec-required FAIL classes (missing index, unregistered JSON, dangling entry, broken JSON) are implemented and each has a dedicated, spec-driven test. Silent-skip for unparseable JSON is removed — r3's High finding stays resolved. verify on v6 = clean; pytest 211/211 green; QO4 suite 10/10 green. Remaining gaps are all in index.toon parser robustness (header recognition, declared row-count validation, comma-in-path ambiguity), none of which break against the current v6 corpus but could mask future corruption. Circular dependency with RBKC impl: none observed (verify parses TOON structurally from the file alone).

## Spec Conformance Matrix (§3-3 QO4, 4 FAIL classes)

| # | Spec requirement | Implemented | Tested | Reference |
|---|---|---|---|---|
| 1 | index.toon 不在 → 全 content JSON を FAIL 列挙 (no_knowledge 除外) | Yes | Yes | verify.py:272–280 / test_verify.py:331–336, 340–352 |
| 2 | 未登録 JSON → FAIL | Yes | Yes | verify.py:301–304 / test_verify.py:305–312 |
| 3 | dangling entry (index にあり・disk にない) → FAIL | Yes | Yes | verify.py:306–309 / test_verify.py:354–365 |
| 4 | JSON parse 失敗 → QO4 FAIL (silent skip 禁止, ゼロトレランス) | Yes | Yes | verify.py:263–267 / test_verify.py:381–391 |

Supporting tests: `no_knowledge_content` exclusion (test_verify.py:314–320, 346, 352), nested path (322–329), CJK filename (373–379), empty-dir no-op (367–371).

## Three Review Conditions

### 1. Implementation

- All four FAIL cases present (see matrix).
- Broken-JSON silent skip removed: `verify.py:263–267` now emits `[QO4] {rel}: JSON parse failed: {exc}` and `continue`s without registering the file in `content_jsons`. The broken file is therefore not double-reported as "not in index" — correct behaviour (one FAIL per broken file, as spec §3-3 point 4 intends).
- index.toon parser (`verify.py:285–299`) is a minimal line-based scan of the TOON `files[N,]{cols}:` table. It works for well-formed input but has three robustness gaps (see Medium below).

### 2. Tests

- 4 FAIL cases: each has a dedicated test.
  - missing index → `test_fail_missing_index_file`, `test_fail_missing_index_lists_every_content_json`
  - unregistered JSON → `test_fail_json_not_in_index`
  - dangling entry → `test_fail_dangling_entry_in_index`
  - broken JSON → `test_fail_broken_json_surfaces_qo4`
- `no_knowledge_content` exclusion: `test_pass_no_knowledge_content_excluded` + negative assertion in `test_fail_missing_index_lists_every_content_json` (the `no.json` must **not** be reported).
- CJK: `test_cjk_filename_indexed` covers `sub/日本語.json`.
- Nested path: `test_pass_nested_path_indexed`.
- Circular dependency: none. Every test constructs input files from scratch (tmp_path) using spec-derived TOON shape (`_write_toon` writes the header + rows per format spec); no test re-uses RBKC `create/index.py` output to verify `check_index_coverage`. Tests are derivable from the source-format spec alone, per `.claude/rules/rbkc.md`.

### 3. verify + pytest

- `./rbkc.sh verify 6` → `All files verified OK`.
- `pytest tools/rbkc` → `211 passed in 2.31s`.
- `pytest tools/rbkc/tests/ut/test_verify.py::TestCheckIndexCoverage` → `10 passed in 0.03s`.

## Key Issues

### High Priority

None. Zero-tolerance for broken JSON is honoured in code and pinned by `test_fail_broken_json_surfaces_qo4`.

### Medium Priority

**[Medium] Malformed / BOM-prefixed index.toon header is silently treated as "empty table"**
- Description: `verify.py:290–293` enters table mode only when a line strictly matches `stripped.startswith("files[") and stripped.endswith(":")`. A BOM on the first line, a typo (`file[...]:`), a dropped trailing colon, or a swapped bracket leaves `in_table=False`; `indexed_paths` stays empty; QO4 then reports every content JSON as "not registered". Today this produces a loud failure (misattributed cause) because v6 has many content JSONs. If the corpus were ever empty or the damage went unnoticed in CI logs, it would mask the real defect (unreadable index file).
- Proposed fix: after the scan, if `idx.exists()` and file is non-empty and `in_table` was never set, emit `[QO4] index.toon header not recognised: {idx}`. Add test `test_fail_unrecognised_header` covering (a) BOM + `files[...]:`, (b) missing trailing `:`.

**[Medium] Declared row count `files[N,]` is not validated**
- Description: TOON embeds the row count in the header. `verify.py:290–293` parses nothing from the header — `N` is discarded. A truncated index (editor crash mid-write, half-written CI artefact) declaring `N` rows but serialising `M<N` still parses cleanly; if the `M` serialised paths happen to cover every JSON on disk, QO4 returns `[]` — false pass. Verify's quality-gate role requires this be detected from the file alone.
- Proposed fix: parse `N` from `re.match(r'files\[(\d+),', stripped)`; count rows added to `indexed_paths`; if `parsed != N` emit `[QO4] index.toon declared {N} rows but parsed {M}`. Add `test_fail_row_count_mismatch`.

**[Medium] Path extraction assumes no comma in path**
- Description: `verify.py:296–299` uses `stripped.rfind(",")` and takes the suffix as the path. A path containing `,` (unusual but not prohibited on POSIX / not excluded by the TOON spec) is mis-parsed: only the tail after the last comma is registered. A legitimate JSON path with a comma would then appear unregistered — false FAIL; worse, a dangling index entry whose path suffix happens to match a real file could produce a false PASS.
- Proposed fix (cheapest): parse the header's column list `{title,type,category,processing_patterns,path}`, determine the column count C, and split each row into exactly `C-1` fields (splitting on the first `C-1` commas, taking the remainder as path — or using a CSV parser with quote support). Alternative: explicitly forbid `,` in path and FAIL on any row whose path field contains one. Add `test_fail_path_with_comma_detected` and/or `test_pass_column_count_aware_parse`.

### Low Priority

**[Low] `no_knowledge_content` coerced by truthiness, not `is True`**
- Description: `verify.py:268` uses `if d.get("no_knowledge_content")`. A JSON with the string `"false"` (emitter bug) evaluates truthy and excludes the file — false PASS. Low because the current emitter writes booleans and existing tests pin this shape.
- Proposed fix: `if d.get("no_knowledge_content") is True`. Add `test_fail_no_knowledge_string_false_is_not_excluded`.

**[Low] Duplicate rows in index.toon are silently collapsed**
- Description: `indexed_paths` is a `set`; two rows pointing to the same JSON are indistinguishable from one row. Duplicate entries indicate index generation bugs and should surface as QO4 FAIL for diagnosability (spec §3-3 QO4 says "双方向で完全に一致").
- Proposed fix: accumulate into a list; after scan, compute duplicates = `[p for p, c in Counter(list).items() if c > 1]` and FAIL on non-empty. Add `test_fail_duplicate_index_entries`.

**[Low] Empty-table (valid header, zero rows) indistinguishable from no-header in error message**
- Description: `files[0,]{...}:` with no rows is a valid TOON form but user-hostile. QO4 reports "not registered" without noting N=0. Diagnosability only.
- Proposed fix: when `in_table` was set and `len(indexed_paths) == 0`, prefix the "missing" FAIL list with `[QO4] index.toon declares 0 rows but {K} content JSONs exist`.

## Positive Aspects

- All 4 spec FAIL classes are implemented **and** each has a named spec-driven test — direct traceability to `§3-3 QO4` points 1–4.
- `test_fail_broken_json_surfaces_qo4` pins zero-tolerance behaviour; re-introducing silent skip would RED this test immediately.
- Non-circular test design: inputs are synthesised from the TOON format spec in `_write_toon`, not from RBKC's index emitter. Complies with `.claude/rules/rbkc.md` ("verify's logic must be derivable from source format specifications ... alone").
- Coverage beyond the 4 FAIL classes: CJK path, nested path, empty-dir no-op, no_knowledge exclusion (both positive and negative).
- verify green on v6 corpus (weak evidence, but at minimum no regression).

## Recommendations

1. Accept current state as the QO4 spec-conformance baseline — all 4 FAIL classes are covered, the r3 High is still fixed.
2. Address the 3 Medium findings together in a small parser-hardening follow-up: declared-row validation, header recognition, column-count-aware splitting. Each is <10 lines of code and closes an undetectable-corruption path.
3. Low findings are optional; address opportunistically when touching this code.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (lines 246–311) — source
- `tools/rbkc/tests/ut/test_verify.py` (lines 276–391) — tests
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (lines 279, 299–306) — spec
- `tools/rbkc/rbkc.sh` — verify CLI entry
