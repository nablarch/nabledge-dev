# QO3 docs MD 存在確認 — Independent QA Review (Z-1 r5)

**Reviewer**: QA Engineer (independent context; bias-avoidance — spec is the authority; v6 PASS alone is weak evidence; circular tests explicitly checked for)
**Date**: 2026-04-23
**Target**: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` + `TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (line 278 QO3 definition; lines 283-287 README 下位チェック; line 334 test-map entry)

## Overall Assessment

**Rating**: 4/5

Implementation remains a direct, faithful realisation of spec §3-3 QO3 ("JSON に対応する docs MD が存在しない") plus the explicitly enumerated README 下位チェック (existence, `N ページ` declaration, declared==actual count). The 1:1 JSON↔MD path mirror is computed via `rglob` + `relative_to` + `.with_suffix(".md")`, which preserves nested directories and handles Unicode (CJK) filenames natively. All required FAIL modes and edge cases listed in the review ask are covered by tests. No circular tests — fixtures are hand-written opaque strings rather than products of any RBKC converter. v6 real-data run is clean (341 JSON / 342 MD including README; verify PASS) and the full pytest suite is green (219/219).

The four tightness/hygiene items flagged in r4 (Medium #1, Medium #2, Medium #3, Low items) are still unaddressed in r5. They remain non-blocking for Z-1 closure but continue to represent real QA debt.

## Three-condition evaluation

### 1. Implementation — per-file JSON↔MD mirror + README sub-check

- `verify.py:199-239` `check_docs_coverage(knowledge_dir, docs_dir)`.
- `verify.py:219` `for json_path in sorted(kdir.rglob("*.json")):` — walks the full knowledge tree including nested dirs in deterministic order.
- `verify.py:220` `rel = json_path.relative_to(kdir).with_suffix(".md")` — preserves directory layout exactly (`a/b/c.json` → `a/b/c.md`); CJK paths handled by `Path` natively.
- `verify.py:221-225` — authoritative per-file existence check; message includes both the expected MD rel path and the triggering JSON rel path.
- `verify.py:213-216` — README existence FAIL + early return when missing.
- `verify.py:228-238` — README page-count coherence: counts `*.md` files under `docs_dir` excluding `README.md`, compares to the count captured by `_README_COUNT_RE = ^(\d+)\s*ページ` (MULTILINE, first match wins). Emits distinct `missing 'N ページ' declaration` and `count mismatch` FAILs.
- No special-case for `no_knowledge_content` — correct per spec (docs renderer emits a stub MD unconditionally; verify must require it).
- Zero imports from create-side modules — `.claude/rules/rbkc.md` independence rule upheld.

**Verdict**: ✅ Implementation matches spec §3-3 exactly for both the 1:1 mirror and the README sub-check.

### 2. Tests — required cases

| Required case | Present | Location | Notes |
|---|---|---|---|
| 1:1 match PASS | ✅ | test_verify.py:417 `test_pass_each_json_has_docs_md` | |
| JSON without matching MD → FAIL | ✅ | test_verify.py:426 `test_fail_json_without_matching_docs_md` | Loose assertion (see Issues) |
| `no_knowledge_content` still requires docs MD | ✅ | test_verify.py:435 `test_pass_no_knowledge_json_still_requires_docs_md` | Pins stub-MD requirement |
| Nested dir path preservation | ✅ | test_verify.py:452 `test_fail_docs_md_at_wrong_nested_path` | Tight assertion (`a/b/c.md`) — exemplary |
| CJK filename | ✅ | test_verify.py:463 `test_pass_cjk_filename` | |
| Empty knowledge dir | ✅ | test_verify.py:471 `test_pass_empty_knowledge_dir` | |
| README missing → FAIL | ✅ | test_verify.py:444 `test_fail_readme_missing` | |
| README page-count mismatch → FAIL | ✅ | test_verify.py:477 `test_fail_readme_page_count_mismatch` | Loose assertion (see Issues) |
| README missing `N ページ` declaration → FAIL | ✅ | test_verify.py:118 `test_fail_readme_missing_page_declaration` (in `TestCheckJsonDocsMdConsistency_QO1`) | Misplaced — see Issues |

**Circular-test check**: None.
- `_write_json` (test_verify.py:405-409) writes `{"title": "t"}` — a minimal hand-crafted JSON, not produced by any RBKC converter.
- `_write_md` (test_verify.py:411-415) writes the opaque string `"content"` — not produced by any RBKC docs renderer.
- Assertions derive from spec (1:1 path mirroring, declared==actual page count), not from a re-run of the implementation.
- No imports from create-side modules.

**Verdict**: ✅ Required FAIL cases and edges are present; no circular tests. Assertion-tightness debt remains.

### 3. verify + pytest runtime

- `bash rbkc.sh verify 6` → `All files verified OK`
- v6 JSON count (`.claude/skills/nabledge-6/**/knowledge/**/*.json`): **341**
- v6 docs MD count (`.claude/skills/nabledge-6/**/docs/**/*.md`, incl. README): **342**
- `pytest tests/` (full suite) → **219 passed in 3.63s**
- `pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v` → **8 passed in 0.04s**

Bias-avoidance note: v6 PASS alone only proves the current snapshot is 1:1 consistent. The FAIL-mode unit tests are the actual detection evidence; two remain loose (below).

## Key Issues

### [Medium] Loose FAIL-case assertions (carried over from r3/r4; still not fixed)

- **Description**: `test_fail_json_without_matching_docs_md` (test_verify.py:432) asserts only `any("QO3" in i for i in issues)`; it does not pin the expected MD path `about/nablarch/a.md` nor the issue count. A regression that emitted a spurious extra `[QO3]` message, or that emitted the FAIL for a different file, would still pass. `test_fail_readme_page_count_mismatch` (test_verify.py:484) asserts only `any("count mismatch" in i)` — does not pin the numeric pair (declared `99`, actual `2`). The sibling `test_fail_docs_md_at_wrong_nested_path` (test_verify.py:461) already demonstrates the correct tight pattern.
- **Proposed fix**: Tighten both to the nested-path test's pattern, e.g.
  - `assert any("QO3" in i and "about/nablarch/a.md" in i for i in issues)` plus `assert len([i for i in issues if "QO3" in i and "docs MD missing" in i]) == 1`
  - `assert any("count mismatch" in i and "99" in i and "2" in i for i in issues)`
  Mechanical, <10 LOC, no spec discussion needed.

### [Medium] `README missing 'N ページ' declaration` test in the wrong class

- **Description**: `test_fail_readme_missing_page_declaration` (test_verify.py:118) lives inside `TestCheckJsonDocsMdConsistency_QO1`. It functionally asserts the right QO3 invariant, but splitting the QO3 surface across two classes weakens discoverability for maintainers who grep by class name (e.g. someone extending `TestCheckDocsCoverage` would not see the sibling case).
- **Proposed fix**: Move the test into `TestCheckDocsCoverage` (rename to e.g. `test_fail_readme_missing_page_count_declaration`). Zero behaviour change.

### [Medium] Multiple `N ページ` declarations — first-match-wins behaviour unpinned

- **Description**: `_README_COUNT_RE` is MULTILINE and returns the first match (`verify.py:230`). A README containing two declarations (e.g. `3ページ\nうち2ページは参考資料`) silently takes the first. Behaviour is deterministic but not covered by any test, so a future regex change that switches to last-match or `findall` could go undetected.
- **Proposed fix**: Add `test_readme_multiple_page_declarations_first_wins` in `TestCheckDocsCoverage` that writes two declarations and asserts the first-match decision. If spec owner prefers stricter handling (FAIL on multiple matches), convert to `findall` and test the new contract; either way the contract should be locked.

### [Low] README early-return masks per-file checks

- **Description**: At `verify.py:214-216`, a missing README triggers `return issues` before the per-file JSON↔MD scan runs. A repo state with both "README deleted" AND "JSON without matching MD" therefore reports only the README FAIL until README is restored. Spec §3-3 prose does not mandate this ordering.
- **Proposed fix**: Either (a) drop the early return so per-file checks run regardless, for defence-in-depth; or (b) add a test pinning the current early-return behaviour with a code comment. Recommend (a); spec owner's call.

### [Low] Orphan docs MD (MD without matching JSON) not flagged

- **Description**: QO3 is strictly JSON-driven. An orphan `*.md` in `docs_dir/` (no matching JSON, not README) is never flagged. Stale docs can persist silently — strictly out of spec scope but a QA-visible gap.
- **Proposed fix**: Out of Z-1 scope. If spec owner widens QO3, add a symmetric `for md_path in ddir.rglob("*.md"): if md.name == "README.md": continue; if not (kdir / rel.with_suffix(".json")).exists(): FAIL`.

### [Low] Stray-file scoping contracts implicit

- **Description**: `rglob("*.json")` correctly ignores `index.toon`, YAML, backups; `rglob` on `kdir` correctly excludes files under `ddir` as long as the two are not nested. Both contracts rely on implicit test-fixture isolation rather than explicit assertions.
- **Proposed fix**: Add `test_stray_non_json_in_knowledge_dir_ignored` and `test_stray_json_in_docs_dir_ignored` to lock the scoping contract.

### [Low] Spec-prose drift: `[QO3]` tag used for README sub-check

- **Description**: Spec §3-3 body line 278 defines QO3 as per-file existence only; lines 283-287 then explicitly assign README sub-checks to QO3, and test-map line 334 names it "QO3 ... 1:1 存在確認 + README ページ数". Emitting all four FAIL variants under `[QO3]` is internally consistent but the two-source definition invites future confusion.
- **Proposed fix**: No code change required. Either add one sentence to §3-3 line 278 explicitly rolling the README sub-check under QO3, or differentiate the three README-related FAIL messages with a `[QO3-README]` tag. Non-blocking.

## Positive Aspects

- Per-file 1:1 check (`verify.py:219-225`) is a direct, auditable realisation of spec §3-3 — no source-format knowledge in verify, fully respecting the `.claude/rules/rbkc.md` independence rule.
- `no_knowledge_content` case (test_verify.py:435) correctly pins the "stub MD is required too" contract — defends against an obvious but wrong "optimisation" of skipping stubs.
- Nested-path test (test_verify.py:452) asserts the exact expected path `a/b/c.md` — the strongest assertion pattern in the class and the template other loose tests should follow.
- CJK (test_verify.py:463) and empty-dir (test_verify.py:471) edges are covered.
- Fixtures are opaque and hand-written (`"content"`, `{"title": "t"}`) — zero circular dependency on upstream RBKC output.
- Deterministic ordering via `sorted(...)` — stable CI diagnostics.
- v6 runtime clean: 341 JSON / 342 MD (incl. README), verify PASS; full pytest suite 219/219.

## Recommendations

1. **Now (Z-1 polish)**: Tighten the two loose FAIL-case assertions (Medium #1). Mechanical, <10 LOC, no spec discussion.
2. **Now (hygiene)**: Move `test_fail_readme_missing_page_declaration` from `TestCheckJsonDocsMdConsistency_QO1` to `TestCheckDocsCoverage` (Medium #2).
3. **Now (cheap hardening)**: Add `test_readme_multiple_page_declarations_first_wins` to pin first-match-wins behaviour (Medium #3).
4. **Follow-up issue**: Decide on README early-return masking (Low #1), orphan-MD policy (Low #2), and stray-file scoping tests (Low #3) with spec owner; update §3-3 prose accordingly.
5. **Optional cosmetic**: Amend §3-3 line 278 to make the README sub-check explicit, or rename the three README FAIL tags to `[QO3-README]`.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 193-239, source)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 395-485, QO3 tests; line 118 misplaced test)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-3 lines 270-306; test-map line 334)
