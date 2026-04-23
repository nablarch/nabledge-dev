# Expert Review: QA Engineer — QO1 docs MD 構造整合性

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (no prior-review context)
**Target**: QO1 check in `check_json_docs_md_consistency`

## Overall Assessment

**Rating**: 4/5
**Summary**: QO1 implementation covers the three spec bullets (title, section title order/presence, sections=[] → no ## rule) and all three verify conditions pass (impl present, unit tests RED→GREEN fixed, v6 FAIL 0). Two findings warrant attention: one test intentionally pins impl behaviour that is **not in the spec** (empty title), and the `##` heading detector is broader than the spec (matches `####`+). Both are low-risk but worth documenting.

## Verify Conditions

| Condition | Status | Evidence |
|---|---|---|
| 1. Implementation exists per spec §3-3 | PASS | `scripts/verify/verify.py:50-84` covers title, section order/presence, sections=[] guard |
| 2. Unit tests RED→GREEN for main FAIL + edge cases | PASS | `tests/ut/test_verify.py:15-109` — 11 test methods, all GREEN |
| 3. v6 verify FAIL 0 | PASS | `bash rbkc.sh verify 6` → "All files verified OK" |

Pytest: 11/11 PASS (`TestCheckJsonDocsMdConsistency_QO1`).

## Spec ↔ Implementation Matrix

| Spec bullet (§3-3 line 286-288) | Impl location | Coverage |
|---|---|---|
| Title: JSON top-level `title` == docs MD `#` 見出し | `verify.py:61-65` | Partial — see H2 below |
| Section titles: exist in `##`/`###`, same order | `verify.py:67-84` | Permissive — matches `#{2,}` (any depth) |
| sections=[] → docs MD has no `##` | `verify.py:71-72` | Full |

## Key Issues

### High Priority
None.

### Medium Priority

**[M1] `_H2_RE` broader than spec — matches `####` and deeper**
- Description: `verify.py:47` uses `r'^#{2,}\s+(.+)$'` which matches all heading levels from `##` onward. Spec §3-3 explicitly limits section titles to `##`/`###`. A `####` heading in docs MD would be treated as a JSON section title candidate.
- Impact: Low in practice (docs MD rendering from converters probably never emits deeper than `###`), but specification drift — a future converter change that emits `####` would silently satisfy QO1 when it should not, and the inverse (a stray `####` body element) could create false positive matches.
- Proposed fix: Tighten to `r'^#{2,3}\s+(.+)$'` and add a unit test asserting that a JSON section title appearing only as `####` in docs MD triggers FAIL.
- Decision recommendation: Defer (low real-world impact) OR tighten now with TDD; either is acceptable per spec-faithfulness standard.

**[M2] `test_empty_title_is_not_checked` pins impl behaviour not in spec — borderline circular**
- Description: `tests/ut/test_verify.py:85-97` pins current behaviour where empty `json_title` silently skips the title comparison. Spec §3-3 line 286 states unconditionally: "JSON top-level `title` == docs MD の `#` 見出し". There is no "empty title is exempt" clause.
- The test's own comment acknowledges this: "If this behaviour ever changes, update the spec §3-3 QO1 definition at the same time." That is the textbook definition of a **circular test** — the test is protecting impl, not spec.
- The rationalization ("title-less JSON is only produced by `no_knowledge_content` flag") has a gap: `_no_knowledge` early-returns at `verify.py:52-53`, so in real flow an empty title paired with `no_knowledge_content=False` is already unreachable by construction. If the pre-condition is that empty title is unreachable, the test should assert that pre-condition in the converter layer — not pin permissive verify behaviour.
- Proposed fix: Two options:
  1. **Preferred** — Remove the silent-skip in `verify.py:64` (`if json_title and ...` → `if docs_title != json_title:`) and change the test to expect FAIL for empty JSON title when H1 is non-empty. Aligns impl with spec literal reading.
  2. If the silent-skip is deliberate, add one sentence to spec §3-3 documenting the exemption, and rename the test to `test_empty_title_exempt_per_spec` referencing the spec line.
- Decision recommendation: Consult user — this is the kind of "1% risk" case the project quality standard targets. Either fix the impl or fix the spec, but not leave the test as the sole source of truth.

### Low Priority

**[L1] `test_multiple_h1_in_docs_md_first_wins` documents undefined spec territory**
- Description: `tests/ut/test_verify.py:104-109` pins "first H1 wins". Spec is silent on multiple H1 (typically docs MD should have exactly one H1).
- Proposed fix: Add a sentence to spec §3-3 ("docs MD must have exactly one H1; first `#` is treated as title") OR add a FAIL case for multiple H1s. Current test is a behaviour pin only.

**[L2] Duplicate section titles in JSON not tested**
- Description: If JSON sections contain two entries with identical title (e.g., `["概要", "概要"]`), the `pos`-advancing matcher requires two matching H2s in docs MD at non-overlapping positions. Behaviour is correct but untested.
- Proposed fix: Add a test case with duplicate titles — both a PASS (two H2 present) and a FAIL (only one H2 present) case.

**[L3] Section title with leading/trailing whitespace in JSON**
- Description: `json_sec_titles` uses `s.get("title", "")` without `.strip()`, whereas docs H2 titles are `.strip()`-ed. A JSON title with a trailing space would never match.
- Proposed fix: Either `.strip()` on the JSON side too, or add a test pinning that converters emit already-stripped titles (assertion at converter layer).

## Positive Aspects

- Clean spec-to-test mapping table maintained at §4 line 317-328 of design doc
- All three verify conditions (impl / tests / v6 FAIL 0) are explicitly defined at §4 line 330-333 and met
- `test_fail_section_order_reversed` uses a realistic permutation (B before A) rather than a trivial swap
- `_no_knowledge` early-return at `verify.py:52-53` correctly skips placeholder JSONs
- Test for `test_title_with_markdown_special_chars_exact_match` guards against accidental regex-based title normalization — good defensive coverage
- FAIL messages include `file_id` and offending title, aiding diagnosis

## Recommendations

1. **Resolve M2 this iteration** — the empty-title test is explicitly flagged as "pinning impl, not spec" by its own comment. Leaving it as-is means the spec and tests disagree on what QO1 enforces, which violates the verify-as-quality-gate principle in `.claude/rules/rbkc.md` ("verify's logic must be derivable from source format specifications").
2. **Defer M1** until converters actually emit `####`, then add a test that pins the correct behaviour. Track in tasks.md.
3. **Add L2/L3** as future hardening — not blocking.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (spec, §3-3 + §4)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py:42-100` (impl)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py:11-109` (tests)
