# QC4 配置正確性 — Independent QA Review (review-z1-r6)

**Reviewer role**: Independent QA Engineer (bias-avoidance; no code modification)
**Target**: `docs/rbkc-verify-quality-design.md` §3-1 手順 2 — QC4 (placement correctness)
**Scope**: verify RST+MD implementation + unit tests (title/content swap, 3-section middle swap, QC3/QC4 boundary, circular rotation)
**Verdict**: **PASS with residual test-only gaps** — Rating **4/5**

---

## 1. Specification recap (§3-1 手順 2)

From `tools/rbkc/docs/rbkc-verify-quality-design.md`:

- Line 161–163 (手順 2): delete JSON units against the normalised source in JSON order; record each delete offset; *"JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも前であれば FAIL（QC4: 配置ミス）"*.
- Lines 179–186 (判定分岐まとめ): QC4 specifically covers *"削除位置が JSON 順より前に逆行"*, distinct from QC2 (never occurs) and QC3 (occurs but already consumed).

Classification must be deterministic: the same mis-ordered input must not sometimes raise QC3 vs QC4.

---

## 2. Implementation review

**RST**: `tools/rbkc/scripts/verify/verify.py:530-609` (`_check_rst_content_completeness`)
**MD**:  `tools/rbkc/scripts/verify/verify.py:612-709` (`_check_md_content_completeness`)

Both share the same three-branch decision tree:

```
idx = norm_source.find(norm_unit, current_pos)   # forward search only
if idx != -1:                                    # PASS, consume, advance
    current_pos = idx + len(norm_unit)
else:
    prev_idx = norm_source.find(norm_unit)       # global search
    if prev_idx == -1:                 → QC2 (fabricated)
    elif _in_consumed(prev_idx, len):  → QC3 (already consumed)
    else:                              → QC4 (exists earlier, not consumed) = misplaced
```

### Findings

| # | Observation | Location | Assessment |
|---|-------------|----------|-----------|
| I-1 | RST (`verify.py:570-589`) and MD (`verify.py:665-684`) branches are structurally identical. Decision tree, `_in_consumed`, `current_pos` advancement all match. | `verify.py:570-589`, `verify.py:665-684` | Good — intentional parity |
| I-2 | `current_pos` advances to `idx + len(norm_unit)` only on hit (`verify.py:574`, `verify.py:669`). This is the monotonic guard that enforces §3-1 手順 2 ordering. | `verify.py:574`, `verify.py:669` | Correct |
| I-3 | On miss, global `norm_source.find(norm_unit)` (`verify.py:576`, `verify.py:671`) is used to disambiguate QC2/QC3/QC4 — matches spec 判定分岐 table (§3-1 lines 183–186). | `verify.py:576-589`, `verify.py:671-684` | Correct |
| I-4 | `_in_consumed` uses half-open overlap check `pos < e and end > s` (`verify.py:566-568`, `verify.py:661-663`). Correct substring overlap detection. | `verify.py:566-568`, `verify.py:661-663` | Correct |
| I-5 | Title vs content diagnostics are split (`misplaced title` / `misplaced content`). Spec does not require the split but it aids triage. | `verify.py:583,589,678,684` | Good |
| I-6 | On miss, `current_pos` is **not** rolled back or advanced; subsequent units may still PASS. Matches no-drop principle. | `verify.py:570-589` | Correct |
| I-7 | Spec §3-1 手順 2 describes "record each delete position"; implementation uses `current_pos` + `consumed[]` (`verify.py:563-564`, `verify.py:658-659`). Net behaviour is equivalent (regression ⇔ `find(...,current_pos)==-1 AND global find < current_pos AND not _in_consumed`), but position-trace is not exposed in diagnostics. | — | Low-priority gap |
| I-8 | Top-level `title`/`content` are prepended as the first search units (MD: `verify.py:641-644`; RST: via `_build_rst_search_units` ~`verify.py:558`). QC4 can therefore fire on top-vs-section misplacement. | `verify.py:641-644` | Correct |

### Manual spec-conformance exercise (no code modified)

I ran `_check_rst_content_completeness` and `_check_md_content_completeness` directly against the four requested scenario families:

| Scenario | Input | Expected | Observed |
|----------|-------|----------|----------|
| 2-section title swap (RST) | source `詳細.../概要...`, JSON `概要, 詳細` | QC4 | `[QC4] section 's2': misplaced title: '詳細'` ✓ |
| 2-section content swap (MD) | source `## A/A の内容 / ## B/B の内容`, JSON titles correct but content swapped | QC4 | `[QC4] section 's2': misplaced content` ✓ |
| 3-section middle swap (RST) | source `A/B/C`, JSON `A,C,B` | QC4 on s3 | `[QC4] section 's3': ...` ✓ |
| **3-section circular rotation (RST)** | source `A/B/C`, JSON `B,C,A` | QC4 at end | `[QC4] section 's3': misplaced title: 'A'` + `...misplaced content: 'a'` ✓ |
| **3-section circular rotation (MD)** | source `A/B/C` under `# T`, JSON `B,C,A` | QC4 at end | `[QC4] section 's3': misplaced title: 'A'` + `...misplaced content: 'a'` + `[QC1] source content not captured` ✓ |

All cases classify deterministically as QC4 — not QC3 or QC2. The rotation case is **not** covered by any existing test, even though the code handles it correctly (see T-2).

---

## 3. Test review (`tools/rbkc/tests/ut/test_verify.py`, `TestCheckContentCompleteness` at line 840)

### Coverage matrix vs §3-1 手順 2 scenarios

| Requested scenario | Test method | Lines | Status |
|--------------------|-------------|-------|--------|
| Title swap (RST) | `test_fail_qc4_misplaced_title` | `test_verify.py:884-891` | ✓ |
| Title swap (MD) | `test_fail_qc4_misplaced_title_md` | `test_verify.py:1175-1182` | ✓ |
| Content swap (RST) | `test_fail_qc4_misplaced_content_rst` | `test_verify.py:1222-1229` | ✓ |
| Content swap (MD) | `test_fail_qc4_md_content_swap` | `test_verify.py:1196-1204` | ✓ |
| 3-section middle swap (RST) | `test_fail_qc4_three_section_middle_swap` | `test_verify.py:1184-1194` | ✓ |
| QC3/QC4 boundary (disambiguation) | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` | `test_verify.py:1206-1220` | **Weak (T-1)** |
| Circular rotation (A/B/C → B/C/A) | — | — | **Missing (T-2)** |
| 3-section middle swap (MD) | — | — | **Missing (T-5)** |

### Test issues

**[Medium] T-1 — QC3/QC4 boundary test is self-inconsistent.**
- Description: `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` (`test_verify.py:1206-1220`) has a docstring stating *"Must raise QC4 (not QC3)"* (`test_verify.py:1209`), but the actual assertion is only `assert not any("QC3" in i for i in issues)` (`test_verify.py:1220`). The setup intentionally omits `s2` (`test_verify.py:1214`), so only one `note` is consumed and no positional regression occurs — no QC4 can fire in this scenario. The test neither exercises the QC4 path it claims to, nor verifies QC4 is emitted. It is a PASS-negative-only guard with misleading naming.
- Proposed fix: rewrite as two tests.
  (a) PASS boundary: source has `note` in A and B, JSON lists `s1=A/"note"`, `s2=B/"note"` — both consume forward, assert no QC3/QC4.
  (b) QC4-with-duplicate: source has `note` in A and B, JSON lists `s1=B/"note"`, `s2=A/"note"` — second unit regresses, must raise QC4 (not QC3, because the A-position is not in `consumed`). Assert `any("QC4" in i)` explicitly.

**[Medium] T-2 — No 3-section circular rotation test.**
- Description: Only 2-element swaps and a "middle-swap" (effectively a 2-swap of s2/s3) are covered. A true 3-cycle rotation (A/B/C → B/C/A) is structurally different: *every* JSON section is misplaced, but the first two still find forward matches (B from position 0, C after B), and only the third (A) triggers QC4. My §2 manual run confirms this works, but it is not locked in by a regression-preventing test.
- Proposed fix: add `test_fail_qc4_three_section_rotation_rst` and `...rotation_md` with source `A/B/C`, JSON `[B,C,A]`; assert `any("QC4" in i)`. Without this, a future refactor of `current_pos` handling could silently degrade rotation detection.

**[Low] T-3 — No top-level vs section misplacement test.**
- Description: Spec treats top-level `title`/`content` as the leading units in the ordered list (`verify.py:641-644`). No test exercises a misplacement between top-level and section body.
- Proposed fix: add a test where a section's body appears before the top-level body in source; assert QC4 fires on the top-level unit.

**[Low] T-4 — No title-specific message-content assertion.**
- Description: Implementation emits differently-suffixed diagnostics (`misplaced title` vs `misplaced content`) at `verify.py:583,589,678,684`. No test verifies the *title* suffix when only the title swaps — relevant for operator triage.
- Proposed fix: add `test_fail_qc4_title_only_swap_reports_title` asserting `any("misplaced title" in i for i in issues)`.

**[Low] T-5 — No 3-section middle swap for MD.**
- Description: `test_fail_qc4_three_section_middle_swap` (`test_verify.py:1184-1194`) only exercises RST. MD parity is exercised for 2-section swap but not 3-section. Given RST/MD share a decision tree but diverge in normalisation (docutils vs md_ast), MD-side 3-section detection deserves its own test.
- Proposed fix: add an MD-fmt mirror of the three-section middle-swap test.

### Positive aspects

- Both RST and MD code paths exercised for title and content misplacement individually (`test_verify.py:884-891,1175-1204,1222-1229`).
- The three-section middle-swap test (`test_verify.py:1184-1194`) correctly demonstrates that QC4 fires on the *later* regressing unit, not the earlier swap partner — locking in the non-obvious forward-only sequential-delete semantics.
- Related QC3 tests (`test_verify.py:873-880`, and short-CJK tests elsewhere) indirectly guard the QC3/QC4 boundary from the QC3 side.

---

## 4. verify + pytest execution

- `pytest tools/rbkc/tests/ut/test_verify.py -q -k "qc4 or qc3"` → **13 passed, 0 failed, 145 deselected** (0.43s).
- Manual circular-rotation exercise of `_check_rst_content_completeness` and `_check_md_content_completeness` (see §2) → both correctly emit `[QC4]`. No regression signal.

---

## 5. Recommendations

| # | Priority | Recommendation | Suggested disposition |
|---|----------|----------------|-----------------------|
| T-1 | Medium | Fix self-inconsistent QC3/QC4 boundary test; split into PASS-boundary and QC4-with-duplicate cases; use positive QC4 assertion | Implement Now |
| T-2 | Medium | Add 3-section circular rotation tests (RST + MD) to lock in verified behaviour | Implement Now |
| T-3 | Low | Top-level vs section misplacement test | Defer |
| T-4 | Low | Title-only swap message-suffix assertion | Defer |
| T-5 | Low | MD-side mirror of three-section middle swap | Defer |
| I-7 | Low | Enrich diagnostic with offset regression distance (optional) | Defer |

None of the findings weakens verify or indicates a false PASS/FAIL. Implementation faithfully realises §3-1 手順 2 (confirmed via direct function invocation across title swap, content swap, 3-section middle swap, 3-section circular rotation, and QC3/QC4 boundary). The remaining risks are test-only: the code is already correct for scenarios the tests don't explicitly cover, so the risk profile is "future regression goes undetected" rather than "current output is wrong".

---

## 6. Files reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1 手順 2, lines 161–186)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (`_check_rst_content_completeness` 530-609; `_check_md_content_completeness` 612-709)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (`TestCheckContentCompleteness` 840-1229)

## 7. Non-negotiable constraints honoured

- No code modified.
- No recommendation weakens verify; all suggestions add tests or diagnostic richness.
- 100% content coverage upheld — QC4 does not silently PASS a misplaced unit; circular rotation, title swap, content swap, and 3-section middle swap all detected.
- verify stays independent of create internals (only `scripts/common/` shared, per §2-2).
