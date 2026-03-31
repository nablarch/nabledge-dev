# Expert Review: QA Engineer

**Date**: 2026-03-31
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 6 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The aspect-based expectations schema is a well-motivated improvement that substantially increases the diagnostic value of scenario results. The empirical grounding (v5-specific keywords for qa-005, LIST_MAP for qa-003, OR conditions for qa-004's @UseToken) is solid, and the SKILL.md documentation update is accurate and clear. There are a few medium-priority concerns, but none are blocking.

## Key Issues

### High Priority

None.

### Medium Priority

1. **OR group item count in header allegedly inflates denominator**
   - Description: Concern that `sum(len(items) for items in expectations.values())` might count OR group members individually. Example: `["elementValueProperty", "elementLabelProperty"]` as a list element.
   - Decision: **Reject** — Not a bug. The OR group `["elementValueProperty", "elementLabelProperty"]` is a single list element in the outer list, so `len(items)` correctly counts it as 1. Verified: `total_current == grading_total` for all observed scenarios.

2. **`general_select_tag` in qa-001 benchmark creates high variance (CI=[19%, 100%])**
   - Description: The skill reliably answers with `n:codeSelect`-focused content; `general_select_tag` items are only detected when the skill spontaneously compares to `n:select`. Makes benchmark non-deterministic.
   - Decision: **Defer to follow-up PR** — Already documented in comparison report analysis. Known issue; requires separate scenario design, out of scope for this PR.

### Low Priority

3. **Step key normalization not in generate_reports.py (only data-level fix existed)**
   - Description: `sorted(step_data.keys())` at line 251 would fail with `TypeError` if string step keys appear mixed with integer keys.
   - Decision: **Implement Now** — Added `isinstance(sn, str)` check to normalize string step keys to int in `generate_step_table()`.

4. **`withNoneOption` consistently undetected**
   - Description: Never detected across trials. May be in knowledge files but skill omits it.
   - Decision: **Defer** — The detection gap is documented in comparison reports. Requires knowledge file investigation in a separate PR.

5. **`Objects.equals` in qa-005 may be fragile**
   - Description: Java stdlib class, not Nablarch-specific; presence may be coincidental.
   - Decision: **No action** — 100% detection confirms it appears reliably in responses. Flag if qa-005 regresses.

## Positive Aspects

- Aspect-based schema correctly models logical structure; failures are immediately diagnostic
- OR conditions accurately model synonym pairs in skill output
- v5-specific qa-005 change is empirically motivated (removes Bean Validation, adds Nablarch Validation terms)
- `LIST_MAP` replacing `expectedStatusCode` in qa-003 is a factual correction of a latent bug
- SKILL.md documentation is updated consistently with implementation; detection pseudocode is internally consistent
- Grading output confirms detection logic works end-to-end (evidence strings captured, OR conditions display correctly)

## Recommendations

1. Investigate `withNoneOption` knowledge file coverage in a follow-up PR
2. Address qa-001 benchmark instability in a follow-up PR (split scenario or adjust expectations)

## Files Reviewed

- `.claude/skills/nabledge-test/scenarios/nabledge-5/scenarios.json` (test scenarios)
- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json` (test scenarios)
- `.claude/skills/nabledge-test/SKILL.md` (prompt/workflow documentation)
- `.claude/skills/nabledge-test/scripts/generate_reports.py` (Python script)
- `.pr/00242/nabledge-test/report-202603311123.md` (v5 test run results)
- `.pr/00242/nabledge-test/202603311123/qa-001.md` (OR condition verification)
