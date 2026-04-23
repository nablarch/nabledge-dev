# QO3 docs MD 存在確認 — Independent QA Review (Z-1 r3)

**Reviewer**: QA Engineer (independent context; bias-avoidance — spec is authoritative, v6 PASS alone is weak evidence, circular tests flagged)
**Date**: 2026-04-23
**Target**: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` + `TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (line 278), test map line 328

## Overall Assessment

**Rating**: 4/5

Implementation is a direct, faithful realisation of spec §3-3 QO3 ("JSON に対応する docs MD が存在しない"). Per-file 1:1 mirroring is correct. Tests cover the documented FAIL modes and key edges (nested path, CJK, empty dir, `no_knowledge_content`, README missing, README count mismatch). Full v6 run: `bash rbkc.sh verify 6` → `All files verified OK` (341 JSON files); `pytest tests/` → 197 passed. No circular tests. Remaining concerns are test-assertion tightness and a handful of contract-pinning edge cases — nothing blocks Z-1 closure.

## Implementation review

### 1:1 mirroring at relative path

`verify.py:156-194` — implementation shape:

- `verify.py:176` `for json_path in sorted(kdir.rglob("*.json")):` — walks the entire knowledge tree, including nested dirs
- `verify.py:177` `rel = json_path.relative_to(kdir).with_suffix(".md")` — preserves directory structure exactly (`a/b/c.json` → `a/b/c.md`)
- `verify.py:178-182` `if not (ddir / rel).exists(): issues.append("[QO3] docs MD missing ...")`
- `sorted(...)` yields deterministic ordering → stable diagnostics
- `rglob` filter is `*.json`, so non-JSON files (stray `.toon`, `.yaml`, backup files) are correctly ignored
- Python `Path` handles Unicode natively → CJK filenames work

No special-casing for `no_knowledge_content` JSONs. This is correct: per spec §3-3, docs MD is JSON's human-readable rendering, and `docs.py` emits a stub MD even for `no_knowledge_content` entries. Therefore requiring the MD unconditionally is the right invariant. `verify.py:156-182` contains zero references to `_no_knowledge`, which is the desired behaviour for QO3.

**Verdict**: per-file 1:1 existence check matches spec §3-3 exactly. No implementation gap.

### README page-count check role

`verify.py:170-173` (README existence) and `verify.py:184-193` (page-count match).

The README check has two parts:

1. **README missing → `[QO3] README.md missing`** and *early return* (line 173). If README is absent, per-file checks are skipped. This is a design choice — it means a developer who deletes README will get one-line output until they restore it. Acceptable but noteworthy: the per-file existence check, which is the authoritative QO3 scope per spec, is gated behind a README existence check that is not itself part of spec §3-3's QO3 definition (line 278). **In practice README is always present in v6, so this has no operational impact, but a README regression masks per-file regressions.**

2. **README page-count mismatch → `[QO3] README.md count mismatch`** (line 192). Spec §3-3 prose (lines 283-291) defines QO3 only as per-file existence; however the test-mapping table at `rbkc-verify-quality-design.md:328` explicitly lists `TestCheckDocsCoverage (JSON↔MD 1:1 存在確認 + README ページ数)`. So the page-count check is authorised by the test map but absent from the prose — internally consistent but minor spec drift on labelling.

**Verdict**: Role is coherent; two minor concerns for follow-up (README-early-return masking; `[QO3]` tag vs prose). Neither blocks Z-1.

## Unit-test review (`TestCheckDocsCoverage`, test_verify.py:349-440)

| Case | File:line | Present | Notes |
|---|---|---|---|
| 1:1 match PASS | test_verify.py:372 | ✅ | |
| JSON without matching MD → FAIL | test_verify.py:381 | ✅ | Loose assertion (see below) |
| `no_knowledge_content` JSON still requires docs MD | test_verify.py:390 | ✅ | Pins the docs.py stub contract |
| Nested dir path preservation | test_verify.py:407 | ✅ | `a/b/c.json` with wrong-location `c.md` at top level |
| CJK filename | test_verify.py:418 | ✅ | `about/日本語.json` ↔ `about/日本語.md` |
| Empty knowledge dir | test_verify.py:426 | ✅ | |
| README missing → FAIL | test_verify.py:399 | ✅ | |
| README page-count mismatch → FAIL | test_verify.py:432 | ✅ | |

### Circular-test check

**No circular tests detected.**

- Fixtures are hand-written: `_write_json` writes a hard-coded `{"title": "t"}` stub (test_verify.py:363); `_write_md` writes the opaque string `"content"` (test_verify.py:369).
- The MD file is **not** produced by any RBKC converter/resolver/docs renderer — so verify is not being tested against its own upstream's output.
- Assertions derive from spec (1:1 path mirroring `.json` → `.md`; README `N ページ` declared count equals actual `.md` count).
- Verify imports only `scripts.verify.verify` — no create-side modules imported (`.claude/rules/rbkc.md` independence rule upheld).

### Coverage gaps

**[Medium] Loose FAIL-case assertions.**
- `test_fail_json_without_matching_docs_md` (test_verify.py:388) asserts only `any("QO3" in i for i in issues)` — does not pin the path `about/nablarch/a.md` nor count `issues == 1`. A future bug that emits a spurious extra QO3 issue would still pass this test.
- `test_fail_readme_page_count_mismatch` (test_verify.py:440) asserts only `any("count mismatch" in i)` — does not pin `99` (declared) or `2` (actual).
- `test_fail_docs_md_at_wrong_nested_path` (test_verify.py:416) *does* pin the path `a/b/c.md`. This is the model; replicate for the two cases above.

**Proposed fix**: tighten to e.g. `assert any("QO3" in i and "about/nablarch/a.md" in i for i in issues) and len([i for i in issues if "QO3" in i]) == 1`.

**[Medium] README without `N ページ` line — behaviour not pinned.**
`verify.py:187-193` — `if m:` guard silently allows a README that has no `N ページ` declaration. Spec is silent; current behaviour is lenient PASS. This policy deserves an explicit test to prevent accidental regression.

**Proposed fix**: add `test_pass_readme_without_page_count_declaration` that writes `ddir/README.md` with arbitrary prose (no `ページ`) + one JSON + one MD, and asserts empty issues — locking the current lenient behaviour.

**[Medium] Multiple `N ページ` lines — first-match-wins untested.**
`_README_COUNT_RE` is MULTILINE and picks the first match. If a README ever contains two declarations (e.g. "3ページ\nうち2ページは ..."), the first wins silently. Not critical, but worth a test.

**[Low] Orphan docs MD (MD without JSON) — not checked.**
Spec §3-3 defines QO3 as JSON-driven only ("JSON に対応する docs MD が存在しない"). An orphan `.md` in `ddir` is not flagged. Strictly out of QO3 scope, but a QA-visible gap: stale docs can linger silently. Flagging here as "design point for future, not Z-1 blocker". No fix required unless spec owner widens QO3.

**[Low] README-existence guard early-returns before per-file check.**
If README is deleted, per-file JSON↔MD mismatches are masked. In practice v6 always has README, but no test pins "README missing AND a JSON has missing MD" → this masking is implicit, not spec'd. A test that asserts both issues are reported (i.e. no early return) would harden the contract. Alternative: accept the early return as intentional — but it should be documented.

**[Low] No test for stray JSON outside `kdir`.**
`rglob` is correctly scoped to `kdir`; a JSON file in `ddir` would not be picked up. Implicit in `tmp_path` isolation but an explicit test locks the scoping contract.

**[Low] No test for stray non-JSON inside `kdir`.**
`rglob("*.json")` filter correctly skips `index.toon`, `*.yaml`, etc. Implicit but untested.

### Assertion quality

Mixed. The best pattern is `test_fail_docs_md_at_wrong_nested_path` (test_verify.py:416) which asserts `"QO3" in i and "a/b/c.md" in i`. The other two FAIL tests drop back to bag-of-words checks (see [Medium] above). Uniformly tightening to the `test_fail_docs_md_at_wrong_nested_path` pattern would raise confidence.

## v6 runtime

- `bash rbkc.sh verify 6` → `All files verified OK`
- `find .../nabledge-6/knowledge -name "*.json" | wc -l` → **341 files**
- `pytest tests/` (full suite) → **197 passed in 3.50s**
- `pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v` → **8 passed in 0.03s**

Bias-avoidance note: v6 PASS alone does not validate QO3. It confirms that the 341 generated JSON/MD pairs happen to be 1:1 consistent in the current snapshot. It does *not* prove verify would catch an injected failure — that is the role of the FAIL-case unit tests, which are present (two loose; one tight).

## Key Issues Summary

**[Medium] Loose FAIL-case assertions**
- Description: `test_fail_json_without_matching_docs_md` (test_verify.py:388) and `test_fail_readme_page_count_mismatch` (test_verify.py:440) assert only on the issue tag substring, not on path/numeric content or issue count. Spurious extra messages would not be caught.
- Proposed fix: Tighten to assert exact path (e.g. `"about/nablarch/a.md"`) and numeric content (declared=99, actual=2), plus `len([i for i in issues if "QO3" in i]) == 1`. Use `test_fail_docs_md_at_wrong_nested_path` as the pattern.

**[Medium] README-without-page-count behaviour not pinned**
- Description: `verify.py:188` `if m:` silently skips the count check when no `N ページ` line exists; spec is silent, behaviour is lenient PASS. No test locks this.
- Proposed fix: Add `test_pass_readme_without_page_count_declaration` writing a README with no `ページ` line plus one JSON and matching MD; assert empty issues.

**[Medium] Multiple `N ページ` declarations — first-match-wins untested**
- Description: Regex picks first line match; ambiguous README content not pinned.
- Proposed fix: Add test with README containing two declarations; pin first-match behaviour or FAIL if spec-owner prefers.

**[Low] README early-return masks per-file checks**
- Description: `verify.py:171-173` early-returns on missing README. A JSON with missing MD is then not reported until README is restored.
- Proposed fix: Decide with spec owner — either (a) continue to per-file check even if README missing (drop the early return), or (b) add an explicit test pinning the current early-return as intentional, with a comment at `verify.py:173` explaining why.

**[Low] `[QO3]` label vs spec prose labelling drift for page-count check**
- Description: Spec §3-3 prose (lines 278, 283-291) defines QO3 only as per-file existence. Page-count check is authorised by test-map line 328 but not called out in body prose. All emitted messages use `[QO3]` tag.
- Proposed fix: Add one sentence to spec §3-3 body prose explicitly noting the README page-count coherence check under QO3, **or** change the tag to `[QO3-README]`. Non-urgent.

**[Low] Orphan docs MD and stray-file scoping contracts untested**
- Description: Orphan MD (MD with no JSON), stray JSON outside `kdir`, stray non-JSON inside `kdir` — all depend on implicit tmp-path isolation and `rglob` filter behaviour.
- Proposed fix: Add three small negative tests to harden contract. Orphan MD may require spec-owner confirmation (likely out of QO3 scope).

## Positive Aspects

- Per-file 1:1 existence check (`verify.py:176-182`) is a direct, auditable realisation of spec §3-3 — no source-format knowledge leaks into verify, preserving verify's independence per `.claude/rules/rbkc.md`.
- Nested-path test at test_verify.py:407 correctly pins the mirroring contract (the one case where a top-level `c.md` must still FAIL for `a/b/c.json`).
- `no_knowledge_content` case (test_verify.py:390) is tested — a critical invariant because docs.py emits stubs and verify must not special-case the flag.
- CJK filename test (test_verify.py:418) and empty-dir test (test_verify.py:426) cover realistic edges.
- Fixtures are hand-written (`_write_md` writes `"content"`, `_write_json` writes `{"title": "t"}`) — no circular dependency on RBKC converter output.
- v6 runtime clean (341 JSONs, 0 issues); full pytest suite green (197/197).
- Deterministic ordering via `sorted(...)` — stable CI diagnostics.

## Recommendations

1. **Now (Z-1 polish)**: Tighten the two loose FAIL-case assertions (Medium #1) and add `test_pass_readme_without_page_count_declaration` (Medium #2). Both are mechanical, <20 LOC, no spec discussion needed.
2. **Next (separate issue)**: Decide on orphan-MD policy with spec owner — either widen QO3 or create separate observation ID. Document decision in §3-3.
3. **Optional**: Tag adjustment `[QO3]` → `[QO3-README]` for page-count check to reduce label/prose drift, or amend spec prose. Pick one.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 150-194, source)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 349-440, tests)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-3 lines 270-300; test map line 328)
