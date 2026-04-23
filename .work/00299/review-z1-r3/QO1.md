# Expert Review: QA Engineer — QO1 (docs MD structure consistency)

**Date**: 2026-04-23
**Reviewer**: AI Agent as QA Engineer (independent, bias-avoidance stance)
**Scope**: QO1 check only — `check_json_docs_md_consistency` title/section structure logic

## Overall Assessment

**Rating**: 4/5
**Summary**: QO1 implementation matches spec §3-3 bullets on the happy path and on the explicitly tested failure modes (title mismatch, missing section, reversed order, extra H2 with empty sections, H1 missing, empty-vs-nonempty title). Tests are non-circular — they construct docs MD strings by hand rather than running RBKC converters, so verify is exercised as an independent gate. Residual concerns are two spec-edge gaps in the section-order matcher and one regex looseness.

v6 runtime:
- `./rbkc.sh verify 6` → `All files verified OK`
- `pytest` (197 tests) → all pass

Because RBKC produces 1:1 derivations, v6 passing confirms absence of *gross* mismatches but does not exercise adversarial H2 patterns — the unit tests must carry that weight.

## Key Issues

### High Priority

None. The Z-1 gap-fill tests cover the spec bullets that were previously missing (H1 absent, empty-title-vs-nonempty-H1, special-character titles, multi-H1).

### Medium Priority

1. **Section-order matcher is greedy, accepts out-of-order docs when duplicates exist**
   - Description: `tools/rbkc/scripts/verify/verify.py:119-128` advances `pos` on first match and never revisits. If JSON section titles are `[A, B]` and docs MD H2 sequence is `[B, A, B]`, the matcher finds `A` at index 1 and `B` at index 2, reports no issue. Spec line 287 requires the docs MD sequence to appear "in the same order as JSON" — a docs MD that leads with a spurious `## B` before `## A` violates that.
   - Proposed fix: Reject a match unless the JSON section titles match the filtered docs H2 sequence position-by-position (not greedy substring). Alternatively, if duplicates across docs H2 are not expected, assert `docs_h2_titles == json_sec_titles` directly when `sections` is non-empty (or at minimum require `docs_h2_titles[i] == json_sec_titles[i]` for each i).
   - Test to add: `test_fail_duplicate_h2_hides_order_violation` with JSON `[A, B]`, docs `## B\n## A\n## B\n` expecting a QO1 FAIL.

2. **Extra H2 allowed when JSON has any section**
   - Description: `verify.py:115-128` only flags "extra H2" when `not sections`. When JSON sections = `[A]` and docs MD has `## A` and `## Extra`, no issue is raised. Spec §3-3 line 287 implies the section titles *are* the docs H2 set — an extra H2 means the renderer emitted content the JSON doesn't describe, which is what QO1 is supposed to catch.
   - Proposed fix: After the order loop, also verify `len(docs_h2_titles) == len(json_sec_titles)` (or that every docs H2 appears in JSON). At minimum, add a test expressing the intended behavior so the policy is explicit.
   - Test to add: `test_fail_extra_h2_when_json_has_sections` — JSON `[{title:"A"}]`, docs `# T\n## A\n## Extra\n` — expected: issue flagged.

3. **`_H2_RE = r'^#{2,}\s+(.+)$'` matches H2–H6 uniformly**
   - Description: `verify.py:47`. Spec mentions `##` / `###` explicitly (line 287). Matching `####+` as a section heading is loose — a deeper subsection under a section body would be counted as a top-level section for order-checking, potentially producing false FAILs or false PASSes depending on ordering.
   - Proposed fix: Either restrict to `^#{2,3}\s+` to match spec literally, or document and test the current wider behavior. Given spec text, restricting is safer.
   - Test to add: `test_h4_not_treated_as_section_heading` and/or `test_h3_treated_as_section_heading`.

### Low Priority

4. **No code-fence awareness in H1/H2 regex**
   - Description: `verify.py:46-47` scans line-anchored without skipping fenced code blocks. A `# comment` or `## heading` inside a ```` ``` ```` block would be treated as a structural heading.
   - Proposed fix: Strip fenced code blocks before heading extraction, or document non-issue if JSON content is guaranteed not to contain such lines at column 0 (current converters may satisfy this, but verify should not assume RBKC internals — see `.claude/rules/rbkc.md`).
   - Test to add: `test_hash_inside_fenced_code_block_ignored`.

5. **Empty title + H1 absent is silently accepted**
   - Description: When `no_knowledge_content` is not set and both JSON title and docs H1 are empty strings, `verify.py:107-109` reports no issue. Spec says title must exist and match; a JSON knowledge record with a genuinely empty title is unusual outside the `no_knowledge_content` short-circuit.
   - Proposed fix: If `_no_knowledge` is false, also FAIL on empty `json_title`.
   - Test to add: `test_fail_empty_title_without_no_knowledge_flag`.

## Positive Aspects

- **Non-circular tests**: each case constructs docs MD as a literal string — verify is tested against the spec, not against its own converter output (satisfies `.claude/rules/rbkc.md` independence).
- **Z-1 gap-fill tests** (test_verify.py:77-105) directly target the previously missing spec bullets (H1 missing, empty title, special chars, multi-H1) and are each paired with a precise assertion on the issue string (`"title mismatch"`).
- Failure assertions check both the prefix `QO1` and a substring of the message (`title`, `title mismatch`) — this catches regressions where the wrong check fires.
- `_no_knowledge` short-circuit is covered (test_pass_no_knowledge_content_skipped).

## Recommendations

- Add the four Medium-priority tests above; they are cheap and fill concrete spec gaps.
- After tightening the section-order matcher and H2 regex, rerun `./rbkc.sh verify 6` to confirm no regression on real v6 output.
- Do not treat "v6 verify passes" as sufficient evidence for QO1 correctness. v6 output is produced by a cooperating RBKC — adversarial inputs must come from unit tests. This is the independence principle in `.claude/rules/rbkc.md`.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 42–146) — source code
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 11–105) — tests
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 lines 270–291 — spec

## Runtime Verification

- `./rbkc.sh verify 6` → All files verified OK
- `pytest` (tools/rbkc) → 197 passed
- `pytest tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO1` → 11/11 passed
