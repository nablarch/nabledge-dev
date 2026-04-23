# QO4 Review (Round 3) — index.toon 網羅性

**Reviewer**: QA Engineer (independent; bias-avoidance mode — spec authoritative; v6-passing = weak evidence)
**Date**: 2026-04-23
**Scope**: `check_index_coverage` vs spec §3-3 QO4 (4 FAIL conditions, incl. zero-tolerance parse)
**Sources**:
- Spec: `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (lines 279, 293-300)
- Impl: `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 201-266)
- Tests: `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 234-346)

## Overall Assessment

**Rating**: 4 / 5
**Summary**: The r2 High-priority finding (silent skip on broken JSON) has been addressed — broken JSON is now emitted as `[QO4] ...: JSON parse failed: ...` per spec §3-3 point 4, and the previously-flagged circular test has been replaced by a spec-driven test. All four spec FAIL classes are implemented and covered. Residual gaps are in index.toon parser robustness (malformed header / row-count sanity / quoted-path), none of which trip against the v6 corpus today but could mask future corruption. v6 clean; 197/197 tests green.

## Spec Conformance Matrix (§3-3, 4 FAIL classes)

| # | Spec requirement | Implemented | Tested | Reference |
|---|---|---|---|---|
| 1 | index.toon missing → every content JSON listed as FAIL (no_knowledge excluded) | Yes | Yes | verify.py:227-235 / test_verify.py:295-307 |
| 2 | JSON on disk not in index.toon → FAIL | Yes | Yes | verify.py:256-259 / test_verify.py:260-267 |
| 3 | index.toon lists path without JSON on disk (dangling) → FAIL | Yes | Yes | verify.py:261-264 / test_verify.py:309-320 |
| 4 | JSON parse 失敗 → QO4 FAIL (no silent skip, zero-tolerance) | **Yes (new)** | **Yes (new)** | verify.py:218-222 / test_verify.py:336-346 |

All four spec-required FAIL classes satisfied. The previous r2 High finding ("broken JSON silently skipped") is resolved.

## Key Issues

### High Priority

None. The zero-tolerance requirement (§3-3 point 4) is now honoured in code and pinned by test `test_fail_broken_json_surfaces_qo4`.

### Medium Priority

**[Medium] Malformed / missing index.toon header is silently coerced to "empty index"**
- Description: `verify.py:243-254` enters table mode only when a line strictly matches `startswith("files[") and endswith(":")`. If the header is malformed (typo, BOM-prefixed, truncated before header, wrong brackets), `in_table` stays False and `indexed_paths` stays empty. QO4 then reports every content JSON as "not registered" — which fails loudly in the current v6 shape, but misdiagnoses the root cause. If the file has an unrecognised header *and* there are legitimately zero content JSONs, QO4 returns `[]` (false pass).
- Proposed fix: after the read loop, if the file exists, is non-empty, and `in_table` was never set, emit `[QO4] index.toon header not recognised: <path>`. Add a test covering `files[0]{...}` missing trailing `:`, and BOM-prefixed header.
- Severity rationale: Medium, not High — the current corpus always has content JSONs, so a malformed header produces a loud (if misattributed) failure. Zero-tolerance still demands diagnosis of the real cause.

**[Medium] Declared row count (`files[N,]`) is not validated against parsed rows**
- Description: Spec treats TOON as a structured format with an explicit row count in the header. `verify.py:237-254` ignores N entirely. A truncated index file (e.g. editor crash mid-write) where N rows were declared but M<N rows were serialised will parse cleanly and yield M indexed_paths; if those M happen to cover every JSON on disk, QO4 passes. The mismatch is undetectable by QO4 today.
- Proposed fix: parse `N` from `files[N,]...`, count rows added to `indexed_paths`, and if `parsed != N` emit `[QO4] index.toon declared N rows but parsed M`. Cheap (single regex on header line) and catches silent truncation.
- Tests to add: `test_fail_row_count_mismatch`.

**[Medium] Path field extraction assumes path contains no commas**
- Description: `verify.py:251-254` uses `stripped.rfind(",")` to split the path off the end of the row. If a path legitimately contains a comma (unusual but not prohibited on POSIX), it is mis-parsed — only the suffix after the last comma is treated as the path. Converse: a title or category field *preceded* by the path would break the assumption that path is the last column. Neither case occurs in v6, but the spec does not exclude them.
- Proposed fix: either (a) document that TOON paths must not contain `,` and add a detector that FAILs such rows, or (b) switch to column-count-based parsing using the header column list (`files[N,]{title,type,category,processing_patterns,path}`). Option (a) is cheap and sufficient for the Nablarch corpus.
- Tests to add: `test_fail_path_with_comma_detected`.

### Low Priority

**[Low] `no_knowledge_content` is tested via truthy semantics, not schema-strict boolean**
- Description: `verify.py:223` uses `d.get("no_knowledge_content")`. A JSON where the key is present as the string `"false"` evaluates truthy and excludes the file from QO4. This mirrors r2's finding, unchanged.
- Proposed fix: compare with `is True`. Minor; depends on whether the emitter schema promises boolean.
- Tests to add: `test_fail_no_knowledge_string_false_is_not_excluded` (optional).

**[Low] Empty table body (header present, zero rows) not distinguished from missing index**
- Description: `files[0,]{...}:` with no rows is valid TOON but user-hostile — QO4 reports every JSON as "not registered in index.toon" without noting the header/count context. Diagnosability only.
- Proposed fix: include declared N in the first FAIL line when N==0.

## Unit Test Coverage Review

| Case | Covered | Location |
|---|---|---|
| All indexed PASS | Yes | test_verify.py:252-258 |
| JSON not in index FAIL | Yes | test_verify.py:260-267 |
| `no_knowledge_content: true` excluded | Yes | test_verify.py:269-275 |
| Nested path indexed | Yes | test_verify.py:277-284 |
| Missing index file FAIL | Yes | test_verify.py:286-291 |
| Missing index → every content JSON listed | Yes | test_verify.py:295-307 |
| Dangling index entry FAIL | Yes | test_verify.py:309-320 |
| Empty knowledge dir + missing index = PASS | Yes | test_verify.py:322-326 |
| CJK filename | Yes | test_verify.py:328-334 |
| **Broken JSON → QO4 FAIL (spec point 4)** | **Yes (new, non-circular)** | test_verify.py:336-346 |
| Malformed / missing header | Missing | — |
| Row-count mismatch vs `files[N,]` | Missing | — |
| Path containing comma | Missing | — |
| `no_knowledge_content` as string `"false"` | Missing | — |

### Circularity Audit

Previously-flagged circular test `test_broken_json_silently_skipped` has been **removed** and replaced with `test_fail_broken_json_surfaces_qo4`, which asserts against spec §3-3 point 4 (not against implementation). No remaining circular tests detected in `TestCheckIndexCoverage`. The happy-path tests use a `_write_toon` helper that models the real emitter format — this is shared test-input shaping, not circularity (the assertion target is the bidirectional compare result, which is spec-defined).

### Non-Negotiable Constraints Check

- verify does not import from RBKC implementation modules — verified (verify.py imports only stdlib + `pathlib`, `json`, `re`).
- verify logic is derivable from source format spec alone — yes; QO4 uses JSON + TOON + filesystem, not RBKC internals.
- No weakening to make v6 pass — the spec point 4 tightening was applied despite adding a FAIL surface; v6 happens to pass on real data.
- 100% coverage target — the four spec FAIL classes are all covered; the three Medium gaps above are parser robustness, not coverage dilution.

## Runtime Verification (v6)

- **Unit tests (QO4 suite)**: `pytest tools/rbkc/tests/ut/test_verify.py::TestCheckIndexCoverage -v` → **10 passed** (0.05s).
- **Full pytest**: `pytest tools/rbkc/tests/` → **197 passed** (2.98s).
- **v6 live run**: `check_index_coverage('.claude/skills/nabledge-6/knowledge', '.../index.toon')` → **0 issues**. Bidirectional compare clean on live corpus.

Bias-avoidance note: v6 passing cleanly is weak evidence of correctness. The three Medium gaps (header robustness, row-count, comma-in-path) would not surface on v6 because v6 is emitted by a well-behaved writer — they are future-regression detectors.

## Positive Aspects

- **r2 High finding resolved end-to-end**: broken JSON now surfaces as QO4 FAIL (verify.py:218-222) and is pinned by a spec-driven test (test_verify.py:336-346). The previously-pinned permissive behaviour has been inverted — correct direction.
- **Bidirectional compare matches spec §3-3 exactly** (forward at verify.py:256-259, reverse at 261-264).
- **"index.toon missing" handler correctly enumerates every content JSON** rather than collapsing to a single summary (verify.py:232-234) — fail-loud behaviour preferred.
- **CJK filename test preserved** (test_verify.py:328-334) — defensive coverage retained.
- **_write_toon helper** models the actual emitter format, so happy-path tests exercise the parser against format-accurate input, not hand-crafted strings.

## Recommendations

1. **Add parser robustness tests** (Medium, do now): malformed/missing header, row-count mismatch vs `files[N,]`, comma-in-path. Small effort, closes the remaining spec-to-parser gap.
2. **Enforce `files[N,]` row-count sanity** in the parser (Medium). Cheap (one regex, one counter, one comparison) and catches silent truncation that QO4 otherwise cannot detect.
3. **Tighten `no_knowledge_content` check to `is True`** (Low). Removes a schema-drift risk with near-zero cost.
4. Consider documenting (in the spec, not in verify) that TOON path fields must not contain commas, or switch to column-count parsing using the header's column list declaration.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 198-266) — QO4 source
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 230-346) — QO4 tests
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (lines 279, 293-300) — spec
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/knowledge/index.toon` — v6 runtime data
- `/home/tie303177/work/nabledge/work2/.work/00299/review-z1-r2/QO4.md` — prior round for delta tracking
