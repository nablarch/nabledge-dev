# QA Review: QO3 — docs MD 存在確認 (Phase 21-Z R6)

**Reviewer**: Independent QA Engineer (bias-avoidance: reviewed without consulting prior R1–R5 conclusions)
**Date**: 2026-04-23
**Scope**: Spec §3-3 QO3 — per-file 1:1 JSON↔MD existence mirror + README existence / `N ページ` declaration / page count

## Verdict

**Overall rating**: 4 / 5 — PASS with one Medium recommendation. Implementation faithfully covers all QO3 requirements enumerated in spec §3-3, tests are non-circular, and v6 output currently passes. One partial coverage gap (dangling docs MD) is indirectly caught via the README page-count sub-check but not explicitly surfaced as a QO3 FAIL message.

## Items Audited

### 1. Spec §3-3 QO3 mandatory checks vs. implementation

Spec file: `tools/rbkc/docs/rbkc-verify-quality-design.md:278, 283-287`

| Spec requirement | Implementation | Status |
| --- | --- | --- |
| JSON に対応する docs MD が存在しない → FAIL | `scripts/verify/verify.py:220-226` (iterates `kdir.rglob("*.json")`, maps `.json → .md`, emits `[QO3] docs MD missing for JSON: ...`) | ✅ Met |
| README.md 自体が存在すること | `scripts/verify/verify.py:214-217` (early return with `[QO3] README.md missing`) | ✅ Met |
| README に `N ページ\n` 形式の行が存在 | `scripts/verify/verify.py:197, 231-233` (regex `^(\d+)\s*ページ` MULTILINE + explicit FAIL) | ✅ Met |
| 宣言ページ数 == 実 .md ファイル数 (README 除外) | `scripts/verify/verify.py:229, 235-239` | ✅ Met |

### 2. Per-file 1:1 mirror correctness

`scripts/verify/verify.py:220-226`:
- Uses `json_path.relative_to(kdir).with_suffix(".md")` — preserves nested directory structure (`a/b/c.json → a/b/c.md`).
- Test `test_fail_docs_md_at_wrong_nested_path` (`tests/ut/test_verify.py:486-495`) proves a top-level `c.md` does **not** satisfy a nested `a/b/c.json`. Good.
- CJK filename handling covered (`tests/ut/test_verify.py:497-503`).

### 3. Circular test check (v6 + pytest)

- verify.py imports only `json`, `re`, `pathlib`, and `scripts.common.labels` (`scripts/verify/verify.py:18-22`). **No imports from `scripts.create.*`** (converters / docs generator / resolver). ✅ verify is independent per `.claude/rules/rbkc.md` ("verify must never import from ... RBKC implementation modules").
- Tests `tests/ut/test_verify.py:432-519` construct JSON/MD fixtures **by hand** via `_write_json`/`_write_md`; they do **not** invoke `generate_docs` or any converter. ✅ Non-circular.
- Live pytest run (`pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v`): **8/8 PASSED** (0.03s).
- Live v6 check on `.claude/skills/nabledge-6/knowledge` + `../docs`: **0 issues** (executed inline via `check_docs_coverage(kdir, ddir)`). Consistent with the Phase 21-Y v6 FAIL=0 result recorded in recent commits.

### 4. Positive aspects

- README page-count check kept in QO3 — matches spec §3-3 line 286-287 verbatim.
- Clear FAIL messages include both the expected `.md` path and the source `.json` path (`scripts/verify/verify.py:224-226`), aiding debugging.
- Tests cover empty knowledge dir (`tests/ut/test_verify.py:505-509`) and declared/actual mismatch (`:511-519`).

## Issues

### Medium — Dangling docs MD not explicitly flagged as QO3

**Description**: Spec §3-3 line 205 (code comment) and line 283-287 collectively describe a **1:1 mapping**. QO3 currently checks only the `JSON → MD` direction (`scripts/verify/verify.py:220-226`). A stale `.md` with no backing `.json` would slip through the per-file loop. The README page-count sub-check (`verify.py:235-239`) catches it **indirectly** only when the README declaration becomes stale; if a writer regenerates the README to match the new (inflated) count, the orphan docs MD becomes invisible. Compare QO4, which explicitly emits a `dangling` FAIL (`verify.py:253`, design doc line 303).

**Proposed fix**: Add a complementary loop that enumerates `ddir.rglob("*.md")` (excluding `README.md`), maps each to its expected JSON via `.md → .json`, and emits `[QO3] docs MD without matching JSON: <rel>` when absent. Add one RED test:

```
test_fail_docs_md_without_matching_json:
  knowledge/a.json + docs/a.md + docs/orphan.md + README "2ページ"
  → expect any("QO3" in i and "orphan.md" in i for i in issues)
```

**Evidence**: `scripts/verify/verify.py:200-240` (no reverse-direction loop); `tests/ut/test_verify.py:432-519` (no dangling-MD test).

**Priority**: Medium — the gap is currently shielded by the count mismatch check, but a single `.md` added while README is simultaneously updated would be invisible to QO3, which contradicts the spec's "JSON と docs MD の 1:1 対応" intent.

### Low — `_README_COUNT_RE` accepts lines with only whitespace between digits and `ページ` but not full-width digits

**Description**: Regex at `scripts/verify/verify.py:197` is `^(\d+)\s*ページ`. `\d+` only matches ASCII digits. If a generator ever emits `３ページ` (full-width), verify silently reports "missing 'N ページ' declaration". Today's generator emits ASCII digits, but the check is locale-fragile.

**Proposed fix**: Either keep ASCII-only (documented as a contract with `docs.py`) or widen to `[\d０-９]+` with a NFKC normalisation before parsing. Low priority because current generator output is deterministic.

**Evidence**: `scripts/verify/verify.py:197`; no test covers full-width digit input.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py:194-240` (QO3 implementation, source)
- `tools/rbkc/tests/ut/test_verify.py:118-128, 429-519` (QO3 unit tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md:270-297, 334` (spec §3-3, matrix)
- `tools/rbkc/scripts/run.py:374-375` (verify entry that wires `check_docs_coverage`)
- `.claude/skills/nabledge-6/knowledge/**` + `.claude/skills/nabledge-6/docs/**` (live v6 data — executed inline, 0 issues)

## Summary

QO3 implementation meets spec §3-3 on every explicitly enumerated sub-check, tests are bias-free and non-circular, pytest is green, and v6 live data passes. The only substantive gap is the one-way mirror: add a reverse-direction "orphan docs MD" check (Medium) to fully realise the "1:1 mapping" wording already present in the code comment (`verify.py:205`) and prevent silent stale-file retention.
