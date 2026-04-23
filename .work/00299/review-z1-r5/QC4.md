# QC4 配置正確性 — Independent QA Review (review-z1-r5)

**Reviewer role**: Independent QA Engineer (bias-avoidance; no code modification)
**Target**: `docs/rbkc-verify-quality-design.md` §3-1 手順 2 — QC4 (placement correctness)
**Scope**: verify implementation (RST + MD) + unit tests
**Verdict**: **PASS with minor gaps** — Rating **4/5**

---

## 1. Specification recap (§3-1 手順 2)

Sequential-delete algorithm over the **normalized source**:

1. JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置より前であれば **FAIL (QC4)**
2. 見つからない → 手順 4 (QC2/QC3)
3. Disambiguation: text exists but position regressed → QC4; text exists but overlaps consumed range → QC3; text never occurs → QC2.

Classification must be deterministic: the same mis-order must not sometimes raise QC3 vs QC4 depending on run.

---

## 2. Implementation review

**RST**: `scripts/verify/verify.py` `_check_rst_content_completeness` (lines 529–608)
**MD**:  `scripts/verify/verify.py` `_check_md_content_completeness` (lines 611–709)

Both share the same three-branch decision tree:

```
idx = norm_source.find(norm_unit, current_pos)   # forward search only
if idx != -1:                                    # PASS, consume
else:
    prev_idx = norm_source.find(norm_unit)       # global search
    if prev_idx == -1:                 → QC2 (fabricated)
    elif _in_consumed(prev_idx, len): → QC3 (duplicate / already consumed)
    else:                              → QC4 (exists earlier, not consumed) = misplaced
```

### Findings

| # | Observation | Assessment |
|---|-------------|-----------|
| I-1 | RST and MD branches are structurally identical (same decision tree, `_in_consumed` helper, `current_pos` advancement). Parity is intentional and spec-aligned. | Good |
| I-2 | `current_pos` advances to `idx + len(norm_unit)` on hit — correct monotonic guard that enforces the §3-1 手順 2 ordering invariant. | Correct |
| I-3 | On miss, `norm_source.find(norm_unit)` (global) is used to disambiguate QC2/QC3/QC4 — matches spec 判定分岐 table (lines 183–185 of spec). | Correct |
| I-4 | `_in_consumed` uses half-open overlap check `pos < e and end > s` — correct for substring overlap detection. | Correct |
| I-5 | Title vs content are reported as separate diagnostics (`misplaced title` / `misplaced content`). Spec does not require this split but it aids triage. | Good |
| I-6 | After a QC4/QC2/QC3 miss, `current_pos` is **not advanced** (loop continues with same cursor). This means subsequent units can still PASS or fail independently — matches "no-drop" principle. | Correct |
| I-7 | Spec §3-1 手順 2 records the *actual delete position* for each unit; implementation only records the *consumed range* via `consumed[]` and advances `current_pos`. Net behavior is equivalent (regression = `find(..., current_pos) == -1 but global find < current_pos`), but the code does not expose the position trace for forensic diagnostics. | Low-priority gap |
| I-8 | Top-level fields `__top__` are included in the unit list for MD (lines 641–643) and for RST via `_build_rst_search_units` (line 557). QC4 can therefore fire on top-level vs section misplacement as well. | Correct |

### Edge-case behavioural checks (manual execution)

I exercised the implementation directly to confirm spec alignment on cases the tests do not cover:

| Case | Input | Expected | Actual |
|------|-------|----------|--------|
| 3-section **circular rotation** (source A/B/C, JSON B/C/A) | — | QC4 on at least one section | `[QC4] s3: 'A'` + `[QC4] s3: 'a'` ✓ |

Circular rotation (non-swap permutation) is detected. See §3 for test-coverage remark.

---

## 3. Test review (`tests/ut/test_verify.py`, `TestCheckContentCompleteness`)

### Coverage matrix vs the requested scenarios

| Requested scenario | Test | Lines | Status |
|-------------------|------|-------|--------|
| Title swap (RST) | `test_fail_qc4_misplaced_title` | 850–857 | ✓ |
| Title swap (MD) | `test_fail_qc4_misplaced_title_md` | 1141–1148 | ✓ |
| Content swap (RST) | `test_fail_qc4_misplaced_content_rst` | 1188–1195 | ✓ |
| Content swap (MD) | `test_fail_qc4_md_content_swap` | 1162–1170 | ✓ |
| Both RST + MD paths asserted | both above classes asserted via `fmt=` param | — | ✓ |
| 3-section middle swap | `test_fail_qc4_three_section_middle_swap` | 1150–1160 | ✓ (RST) |
| QC3/QC4 boundary | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` | 1172–1186 | **Weak** — see T-1 below |
| Circular (rotation, not 2-swap) | — | — | **Missing** — see T-2 below |

### Test issues

**[Medium] T-1 — QC3/QC4 boundary test is a negative guard, not a positive classifier test.**
- Description: `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` (lines 1172–1186) only asserts `not any("QC3" in i for i in issues)`. The test docstring says *"Must raise QC4 (not QC3)"* but the assertion does not verify QC4 was actually raised, and because `s2` is intentionally omitted, only a single consumption happens — there is in fact no regression in this scenario and no QC4 is expected. The test is internally inconsistent between docstring and setup.
- Proposed fix: split into two tests. (a) A true boundary case: source has "note" in both A and B; JSON lists `s1=A/"note"` then `s2=B/"note"` — should PASS (two distinct occurrences). (b) A misplacement-with-duplicate case: source has "note" in A and B; JSON lists `s1=B/"note"` then `s2=A/"note"` — the second consumption regresses and must raise QC4 (not QC3, because the A-position "note" is not inside the consumed range). Assert `any("QC4" in i)` explicitly.

**[Medium] T-2 — No circular rotation test (A/B/C → B/C/A).**
- Description: Only 2-element swaps and a "middle-swap" (which is still effectively a 2-swap of s2/s3) are covered. A true 3-cycle rotation exercises a different code path because *every* section is misplaced, and only the last unit hits the `current_pos` boundary. My manual run (§2) confirms the implementation handles this — but it is not locked in by a test.
- Proposed fix: add `test_fail_qc4_three_section_rotation` with `src = "A\n=\n\na\n\nB\n=\n\nb\n\nC\n=\n\nc\n"` and JSON sections `[B, C, A]`; assert `any("QC4" in i)`.

**[Low] T-3 — No top-level vs section-content misplacement test.**
- Description: Spec treats top-level `content` as the first unit in the ordered list. A misplacement where a section's content appears *before* the top-level content in source should fire QC4 on the section (because top consumes first and advances past). This is reachable but untested.
- Proposed fix: add a small test where source order places section body before the top-level body; assert QC4 on the top-level unit.

**[Low] T-4 — No title-vs-content cross misplacement test.**
- Description: Implementation flags title and content with different suffixes. No test verifies the *title*-specific message is emitted when only the title is swapped while content is correct — relevant because the split diagnostic is the operator's triage signal.
- Proposed fix: add `test_fail_qc4_title_only_swap_reports_title` asserting the message substring `"misplaced title"`.

### Positive aspects of the existing tests

- Both RST and MD code paths are exercised for title and content misplacement individually.
- The three-section middle-swap test (1150–1160) correctly demonstrates that QC4 triggers on the *second* regressing unit, not on the first swap partner, which is the non-obvious behaviour of a forward-only sequential delete.
- Duplicate-title tests (`test_fail_qc3_duplicate_title_same_section`, `test_pass_qc3_short_cjk_repeated_in_source_and_json`) indirectly guard QC4's boundary with QC3.

---

## 4. verify + pytest execution

- `pytest tests/ut/test_verify.py -q` → **156 passed, 0 failed** (1.04s).
- `pytest tests/ut/test_verify.py -k "qc4 or qc3"` → **13 passed**.
- Manual circular-rotation exercise of `check_content_completeness` → correctly emits `[QC4]`.

No regression signal.

---

## 5. Recommendations (Implement / Defer / Reject suggestion)

| # | Priority | Recommendation | Suggested disposition |
|---|----------|----------------|-----------------------|
| T-1 | Medium | Fix the self-inconsistent QC3/QC4 boundary test; split into true-PASS and true-QC4 cases with explicit positive assertions. | Implement Now |
| T-2 | Medium | Add 3-section rotation test to lock in verified behaviour. | Implement Now |
| T-3 | Low | Top-level vs section misplacement test. | Defer |
| T-4 | Low | Title-only swap message-content test. | Defer |
| I-7 | Low | Optional: enrich diagnostic to include the offset regression distance. | Defer |

None of the findings weaken `verify` or indicate false PASS/FAIL. The implementation faithfully realises §3-1 手順 2. The remaining gaps are test-only: the code is already correct for scenarios the tests do not explicitly cover, so the risk is "future regression goes undetected" rather than "current output is wrong".

---

## 6. Files reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1, lines 75–195)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 508–709)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 803–1196, `TestCheckContentCompleteness`)

## 7. Non-negotiable constraints honoured

- No code was modified.
- No suggestion weakens verify; all recommendations add or correct tests, or add diagnostic richness.
- 100% content coverage principle upheld — QC4 must never PASS a misplaced unit silently; the current implementation does not.
