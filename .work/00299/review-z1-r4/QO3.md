# QO3 docs MD 存在確認 — Independent QA Review (Z-1 r4)

**Reviewer**: QA Engineer (independent context; bias-avoidance — spec is the authority; v6 PASS alone is weak evidence; circular tests explicitly checked for)
**Date**: 2026-04-23
**Target**: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` + `TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (line 278 QO3 definition; lines 283-287 README 下位チェック; line 334 test-map entry)

## Overall Assessment

**Rating**: 4/5

The implementation is a direct, faithful realisation of spec §3-3 QO3 ("JSON に対応する docs MD が存在しない") plus the explicitly listed README 下位チェック (existence, `N ページ` declaration, declared-vs-actual count match). Per-file JSON↔MD mirroring uses `rglob` + `relative_to` + `.with_suffix(".md")`, which preserves nested paths and handles CJK natively. The test class covers every documented FAIL mode plus the key edges (nested-path, CJK, empty dir, `no_knowledge_content`, README missing, README `N ページ` missing, README count mismatch). No circular tests — MD fixtures are hand-written opaque strings, not products of any RBKC converter. Full v6 run is clean (341 JSON files, verify PASS, 211 pytest passed).

Open items are test-assertion tightness and a few contract-pinning gaps highlighted in earlier r3; none blocks Z-1 closure, and they remain unimplemented in this revision.

## Three-condition evaluation (as requested)

### 1. Implementation — per-file JSON↔MD mirror + README sub-check

- `verify.py:199-239` `check_docs_coverage(knowledge_dir, docs_dir)`.
- `verify.py:219` `for json_path in sorted(kdir.rglob("*.json")):` walks the entire knowledge tree, including nested dirs, deterministic order.
- `verify.py:220` `rel = json_path.relative_to(kdir).with_suffix(".md")` preserves directory layout exactly (`a/b/c.json` → `a/b/c.md`); Unicode filenames (CJK) handled natively by `Path`.
- `verify.py:221-225` `if not docs_md_path.exists(): issues.append("[QO3] docs MD missing for JSON: expected {rel} (from {json})")` — authoritative per-file existence check.
- `verify.py:213-216` README existence check (FAIL + early return when missing).
- `verify.py:228-238` README page-count coherence: counts `*.md` files excluding `README.md`, compares to the number captured by `_README_COUNT_RE = ^(\d+)\s*ページ` (MULTILINE). Emits `missing 'N ページ' declaration` and `count mismatch` FAILs.
- No special-case for `no_knowledge_content` — correct per spec (docs renderer emits a stub MD unconditionally; verify must require it).
- Zero imports from create-side modules; `.claude/rules/rbkc.md` independence rule upheld.

**Verdict**: ✅ Implementation matches spec §3-3 exactly for both the 1:1 mirror and the README sub-check.

### 2. Tests — required cases

| Required case | Present | Location | Notes |
|---|---|---|---|
| 1:1 match PASS | ✅ | test_verify.py:417 `test_pass_each_json_has_docs_md` | |
| JSON without matching MD → FAIL | ✅ | test_verify.py:426 `test_fail_json_without_matching_docs_md` | Loose assertion (see below) |
| `no_knowledge_content` still requires docs MD | ✅ | test_verify.py:435 `test_pass_no_knowledge_json_still_requires_docs_md` | Pins docs.py stub contract |
| Nested dir path preservation | ✅ | test_verify.py:452 `test_fail_docs_md_at_wrong_nested_path` | Tight assertion — pins `a/b/c.md` |
| CJK filename | ✅ | test_verify.py:463 `test_pass_cjk_filename` | |
| Empty knowledge dir | ✅ | test_verify.py:471 `test_pass_empty_knowledge_dir` | |
| README missing → FAIL | ✅ | test_verify.py:444 `test_fail_readme_missing` | |
| README page-count mismatch → FAIL | ✅ | test_verify.py:477 `test_fail_readme_page_count_mismatch` | Loose assertion (see below) |
| README missing `N ページ` declaration → FAIL | ✅ | test_verify.py:118 `test_fail_readme_missing_page_declaration` (in `TestCheckJsonDocsMdConsistency_QO1`) | Oddly located but asserts correctly |

**Circular-test check**: None. Fixtures are hand-written:
- `_write_json` (test_verify.py:405-409) writes `{"title": "t"}` — a minimal hand-crafted JSON, not produced by any RBKC converter.
- `_write_md` (test_verify.py:411-415) writes the opaque string `"content"` — not produced by any RBKC docs renderer.
- Assertions are derived from spec (1:1 path mirroring, README declared==actual count), not from a re-run of the implementation.
- No imports from RBKC create-side modules.

**Verdict**: ✅ Required cases are all present. Tightness issues remain (see Key Issues).

### 3. verify + pytest runtime

- `bash rbkc.sh verify 6` → `All files verified OK`
- v6 JSON count: `find .claude/skills/nabledge-6/knowledge -name "*.json" | wc -l` → **341 files**
- `pytest tests/` (full suite) → **211 passed in 3.59s** (this iteration)
- `pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v` → **8 passed in 0.03s**

Bias-avoidance note: v6 PASS alone does not prove QO3 correctness — it only proves the current snapshot is 1:1 consistent. The FAIL-mode unit tests are the ones that actually validate detection; two of them are loose (see below).

## Key Issues

### [Medium] Loose FAIL-case assertions (carried over from r3; not fixed)

- **Description**: `test_fail_json_without_matching_docs_md` (test_verify.py:432) asserts only `any("QO3" in i for i in issues)`. It does not pin the expected path `about/nablarch/a.md` nor the issue count. A regression that emitted a spurious extra `[QO3]` message, or that emitted the issue for the wrong file, would still pass. Likewise `test_fail_readme_page_count_mismatch` (test_verify.py:484) asserts only `any("count mismatch" in i)` — does not pin `99` (declared) or `2` (actual). The sibling `test_fail_docs_md_at_wrong_nested_path` (test_verify.py:461) already demonstrates the correct tight-assertion pattern (`"QO3" in i and "a/b/c.md" in i`).
- **Proposed fix**: Tighten both to the `test_fail_docs_md_at_wrong_nested_path` pattern, e.g. `assert any("QO3" in i and "about/nablarch/a.md" in i for i in issues) and len([i for i in issues if "QO3" in i]) == 1` and `assert any("count mismatch" in i and "99" in i and "2" in i for i in issues)`. Mechanical change (<10 LOC, no spec discussion).

### [Medium] README with no `N ページ` line — test lives in wrong class (minor), but present

- **Observation**: `test_fail_readme_missing_page_declaration` at test_verify.py:118 is currently defined inside `TestCheckJsonDocsMdConsistency_QO1`, not `TestCheckDocsCoverage`. Functionally it asserts the right invariant (missing `N ページ` → `[QO3]` FAIL), but its location splits the QO3 test surface across two classes and weakens discoverability for maintainers who grep by class name.
- **Proposed fix**: Move the test into `TestCheckDocsCoverage` (e.g. as `test_fail_readme_missing_page_count_declaration`) to keep the QO3 surface contiguous. No behaviour change.

### [Medium] Multiple `N ページ` declarations — first-match-wins untested

- **Description**: `_README_COUNT_RE` is MULTILINE and returns the first match (`verify.py:230`). If a README ever contains two declarations (e.g. `3ページ\nうち2ページは ...`), the first wins silently. Current behaviour is deterministic but unpinned by test.
- **Proposed fix**: Add `test_readme_multiple_page_declarations_first_wins` that writes a README with two declarations and pins the currently-expected behaviour. Alternatively, if spec owner prefers stricter handling, convert to `findall` and FAIL on multiple matches. Either way, lock the contract.

### [Low] README early-return masks per-file checks

- **Description**: At `verify.py:214-216` a missing README causes `return issues` before the per-file JSON↔MD check runs. A repo state with both "README deleted" AND "one JSON missing its MD" only surfaces one FAIL until README is restored. Spec §3-3 prose does not mandate this ordering.
- **Proposed fix**: Either (a) remove the early return so per-file checks run regardless of README presence; or (b) add an explicit test pinning current early-return behaviour (double-issue repo state → only README FAIL reported) with a code comment explaining why. Recommend option (a) for defence-in-depth; spec owner's call.

### [Low] Orphan docs MD (MD without matching JSON) not flagged

- **Description**: Spec §3-3 QO3 is strictly JSON-driven. An orphan `.md` in `docs_dir/` (no matching JSON, not README) will not be flagged. Stale docs can persist silently — QA-visible gap, strictly out of spec scope.
- **Proposed fix**: Out of Z-1 scope. If spec owner widens QO3, add a symmetric `for md_path in ddir.rglob("*.md")` check skipping `README.md`; until then, no action.

### [Low] Label/prose drift — `[QO3]` used for README sub-check

- **Description**: Spec §3-3 body prose (line 278) defines QO3 only as per-file existence; lines 283-287 explicitly assign the README sub-checks to QO3, and test-map line 334 names it `QO3 ... 1:1 存在確認 + README ページ数`. The implementation emits all four FAIL variants under `[QO3]`. Internally consistent but two-source labelling (line 278 vs 283-287).
- **Proposed fix**: No code change required; add one sentence to §3-3 body prose to make the README sub-check explicit at line 278. Optional cosmetic: `[QO3-README]` tag for the three README-related FAIL messages. Non-blocking.

### [Low] Stray-file scoping contracts implicit

- **Description**: `rglob("*.json")` correctly ignores `index.toon`, `.yaml`, backup files; `rglob` on `kdir` correctly ignores files in `ddir`. Both contracts depend on implicit test-fixture isolation rather than explicit assertions.
- **Proposed fix**: Two small negative tests — `test_stray_non_json_in_knowledge_dir_ignored` and `test_stray_json_in_docs_dir_ignored`. Locks the scoping contract.

## Positive Aspects

- Per-file 1:1 check (`verify.py:219-225`) is a direct, auditable realisation of spec §3-3 — no source-format knowledge in verify, fully respecting the `.claude/rules/rbkc.md` independence rule.
- `no_knowledge_content` case (test_verify.py:435) correctly pins the "stub MD is required too" contract — defends against an obvious but wrong "optimisation" of skipping stubs.
- Nested-path test (test_verify.py:452) asserts the exact expected path `a/b/c.md`, the strongest pattern in the class.
- CJK (test_verify.py:463) and empty-dir (test_verify.py:471) edges are tested.
- Fixtures are opaque and hand-written (`"content"`, `{"title": "t"}`) — no circular dependency on upstream RBKC output.
- Deterministic ordering via `sorted(...)` — stable CI diagnostics.
- v6 runtime clean (341 JSONs, verify PASS); full pytest suite green (211/211).

## Recommendations

1. **Now (Z-1 polish)**: Tighten the two loose FAIL-case assertions (Medium #1). Mechanical, <10 LOC, no spec discussion required.
2. **Now (hygiene)**: Move `test_fail_readme_missing_page_declaration` from `TestCheckJsonDocsMdConsistency_QO1` to `TestCheckDocsCoverage` (Medium #2).
3. **Now (cheap hardening)**: Add `test_readme_multiple_page_declarations_first_wins` to pin regex-first-match behaviour (Medium #3).
4. **Follow-up issue**: Decide on README-early-return masking (Low #1) and orphan-MD policy (Low #2) with spec owner; update §3-3 prose accordingly.
5. **Optional cosmetic**: Amend spec §3-3 prose at line 278 to state the README sub-check explicitly, or rename tag to `[QO3-README]`.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 193-239, source)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 395-485, QO3 tests; line 118 misplaced test)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-3 lines 270-306; test-map line 334)
