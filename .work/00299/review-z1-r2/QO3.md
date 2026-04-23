# QO3 docs MD 存在確認 — Independent QA Review (Z-1 r2)

**Reviewer**: QA Engineer (independent, has not seen prior reviews)
**Date**: 2026-04-23
**Target**: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` + `TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3

## Overall Assessment

**Rating**: 4/5 — Implementation aligns with the spec's 1:1 existence requirement, all 8 tests pass, v6 runtime is clean. One medium-priority concern about circular/redundant test coverage, and one low-priority concern about the README page-count check being under-specified relative to spec (§3-3 defines QO3 only as "JSON に対応する docs MD が存在しない"; the page-count check is an extra coherence check, authorised by the test-mapping table at line 327).

## Implementation review

### Does it walk all JSON files and check a mirrored `.md`?

Yes. `verify.py:130-136`:

```
for json_path in sorted(kdir.rglob("*.json")):
    rel = json_path.relative_to(kdir).with_suffix(".md")
    docs_md_path = ddir / rel
    if not docs_md_path.exists():
        issues.append(f"[QO3] docs MD missing for JSON: expected {rel} ...")
```

- `rglob("*.json")` — full tree walk (nested paths covered)
- `.with_suffix(".md")` — preserves directory structure; ensures mirrored path
- `sorted(...)` — deterministic output
- Covers CJK filenames (Python `Path` handles Unicode natively; test at line 389 confirms)

No special-casing for `no_knowledge_content` JSONs — per `docs.py` they still emit a stub docs MD, so requiring a matching MD is correct (spec §3-3: "JSON は docs MD の人間可読レンダリング").

### README page-count — is this still QO3 per spec?

**Mixed**: The spec's QO3 definition row (line 278) mentions only per-file existence. The "旧 QO3 (目次ページの除外)" note (line 281) explicitly *removes* the old TOC-exclusion aspect and redirects it to QC1/QC2. Neither explicitly authorises a README page-count check.

However, the test-mapping table at line 327 lists QO3 as `TestCheckDocsCoverage (JSON↔MD 1:1 存在確認 + README ページ数)` — so the page-count check is documented as belonging to QO3. This is internally consistent but the spec §3-3 body prose does not mention it. The README check uses `[QO3]` label which may cause operators to think it's part of existence validation.

**Recommendation (Low priority)**: Either (a) add one line in §3-3 body explicitly calling out the README coherence check as a bonus sanity check under QO3, or (b) tag the issue differently (e.g. `[QO3-README]`). Current state is not wrong but slightly spec-drifted.

## Unit-test review (`TestCheckDocsCoverage`, test_verify.py:320-411)

| Case | Present | File:line | Notes |
|---|---|---|---|
| 1:1 match PASS | ✅ | test_verify.py:343 | |
| JSON without matching MD → FAIL | ✅ | test_verify.py:352 | |
| `no_knowledge_content` JSON still requires docs MD | ✅ | test_verify.py:361 | Good — pins docs.py stub contract |
| Nested dir path preservation | ✅ | test_verify.py:378 | Uses `a/b/c.json` with wrong-location MD at top level — confirms mirroring requirement |
| CJK filename | ✅ | test_verify.py:389 | |
| Empty knowledge dir | ✅ | test_verify.py:397 | |
| README missing FAIL | ✅ | test_verify.py:370 | |
| README page-count mismatch FAIL | ✅ | test_verify.py:403 | |

### Circular-test check

**No circular tests detected.** All assertions are derived from the spec (1:1 path mirroring from `.json` → `.md`; README `N ページ` declared count equals actual `.md` count excluding README). Tests write files and assert verify output — they do not invoke any converter/resolver/run code to produce the fixture. `_write_md` writes opaque `"content"`, not the output of a docs generator, so there is no circular "RBKC-output-feeds-its-own-check" pattern.

### Coverage gaps and medium-priority concerns

**[Medium] Missing: MD exists without corresponding JSON (orphan MD).**
The spec §3-3 talks about bi-directional consistency only for QO4 (index.toon dangling entries), and defines QO3 strictly as "JSON に対応する docs MD が存在しない" (JSON-side driven). So orphan MDs are out of QO3's formal scope. However, as a QA matter, an orphan `.md` in docs/ indicates a stale output that should be deleted. Not strictly a QO3 bug, but worth noting that *no* check currently catches it. Not blocking Z-1.

**[Medium] `_README_COUNT_RE` regex edge case untested.**
The regex is `^(\d+)\s*ページ` (MULTILINE). Unit tests cover match-and-mismatch, but not:
- README with **no** `N ページ` line (no match) — falls through silently (`if m:` guard at verify.py:142). Is this intentional PASS, or should missing declaration FAIL? Spec does not say. Current behaviour is lenient; one test pinning this "absent declaration → PASS" behaviour would prevent accidental regression. **Suggestion**: add `test_pass_readme_without_page_count_declaration`.
- Multiple `N ページ` lines — first match wins. Untested.

**[Low] No test for JSON files outside `kdir` (e.g. stray JSON in docs dir).**
`rglob` is correctly scoped to `kdir`, so `docs/stale.json` would not be picked up. Implicit in tmp_path isolation, but an explicit test would harden the contract.

**[Low] No test for non-`.json` files inside kdir** (e.g. `*.toon`, metadata). Current impl correctly filters on `*.json` pattern; an explicit negative test would pin it.

### Assertion quality

Assertions use `any("QO3" in i for i in issues)` (test_verify.py:359, 387, 411). This is correct for existence-of-issue semantics but does not pin exact count. If a future bug causes a spurious extra issue alongside the expected one, the test still passes. For the `test_fail_docs_md_at_wrong_nested_path` case the assertion additionally checks `"a/b/c.md" in i` (line 387) which is good — it pins the *content* of the message, not just the tag. The other two FAIL tests (line 359 `json_without_matching_docs_md`, line 411 `readme_page_count_mismatch`) would benefit from the same treatment.

**[Medium] Recommendation**: Tighten FAIL assertions to check specific path / expected numbers in the message, matching the pattern used at line 387.

## v6 runtime

- `bash rbkc.sh verify 6` → `All files verified OK`
- `pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v` → **8 passed in 0.03s**

## Key Issues Summary

| Priority | Issue | Proposed fix |
|---|---|---|
| Medium | FAIL-case assertions use loose `any("QO3" in i)` without pinning path/number except one case | Tighten `test_fail_json_without_matching_docs_md` and `test_fail_readme_page_count_mismatch` to assert the specific path / declared vs actual counts appear in the issue string |
| Medium | No test pinning behaviour when README has no `N ページ` declaration | Add `test_pass_readme_without_page_count_declaration` to lock current lenient behaviour or switch to FAIL if the spec intends it |
| Medium | No check for orphan docs MD (MD without JSON) — may be out of QO3 formal scope but represents a gap | Decide with spec owner: either add to QO3 or create separate observation. Not blocking Z-1 |
| Low | README page-count check is labelled `[QO3]` but spec §3-3 body prose only describes existence check | Add a sentence to §3-3 explicitly covering the README coherence check, or tag it `[QO3-README]` |
| Low | No explicit tests for stray non-JSON files in kdir or stray JSON in docs | Add negative tests to harden file-filter contract |

## Positive Aspects

- Per-file 1:1 existence check directly derives from spec §3-3; no source-format knowledge required in verify (preserves verify's independence per `.claude/rules/rbkc.md`).
- Nested-path test (`a/b/c.json` with wrong-location `c.md`) correctly pins the mirroring contract.
- `no_knowledge_content` case is tested — important because docs.py emits stubs and verify must not special-case the flag.
- CJK filename test and empty-knowledge-dir test cover realistic edges.
- No circular tests — fixtures are hand-written, not generated by RBKC.
- v6 runtime and unit tests both green.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 103–148, source code)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 320–411, tests)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-3, §4 test-mapping table, spec)
