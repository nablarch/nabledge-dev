# Expert Review: Prompt Engineer — judge_stage2.md

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**File Reviewed**: `tools/benchmark/prompts/judge_stage2.md`

## Overall Assessment

**Rating**: 3/5
**Summary**: The skeleton is good — 4-level rubric is present, breadth-is-OK rule is stated, output schema is strict. But the rubric has ambiguous 3/2 and 2/1 boundaries, the "not-built-in = level 3" rule is stated too softly and can be missed on the req-09 case, and the telescope limitation (title+path only) is not explicitly named as a judging principle. These gaps risk inter-evaluator drift on exactly the 5 scenarios the benchmark needs to discriminate.

## Key Issues

### High Priority

1. **"Not built-in" rule is buried as an example, not a first-class judging principle**
   - Description: Rule #3 is phrased as "the correct answer is often..." and placed mid-list. A judge reading literally can still reason "the question asks how to do rate limiting, no file says 'rate limit' → level 1." This is the single highest risk for req-09.
   - Proposed fix: Promote to its own labeled rule block AND add a worked example in the rubric itself. Change from narrative to directive: "If the question asks about a feature Nablarch may not provide, do NOT penalize the list for lacking an exact match. Near-neighbor files (handlers, interceptors, filter-like mechanisms) being present = level 3."

2. **3 vs 2 boundary is underspecified**
   - Description: "clearly contains the file(s)" vs "main file(s) are in the list but some supporting material missing" — the judge has no way to know what "supporting material" means when it only sees titles. On review-04 and req-02 (3 expected sections each), a judge could pick 2 if it mentally expects a fourth "glue" file and doesn't see it.
   - Proposed fix: Anchor level 3 to recall only: "If every file a domain expert would open first is present in the list, output 3 — regardless of list size or whether extra 'context' files are missing." Reserve 2 for the case where one of multiple required files is clearly absent.

3. **Telescope limitation (title+path only) not stated as a judging principle**
   - Description: Rule #2 ("title maps to a plausible Nablarch topic") is present, but the judge is not told: "You cannot verify section content; do not downgrade because you are uncertain about content." Without this, a cautious judge defaults to 2 when it should pick 3.
   - Proposed fix: Add: "You cannot read file contents. Judge on title plausibility alone. Uncertainty about inside-the-file content is NOT a reason to downgrade — if the title fits, assume the content fits."

### Medium Priority

4. **No reason-length bound**
   - Description: `reason` string has no constraint; judges may emit long prose that drifts the verdict.
   - Proposed fix: Add `"maxLength": 300` to schema and instruct "one sentence, cite file paths."

5. **No tie-breaking rule between 3 and 2**
   - Description: When close, the rubric does not say which way to lean.
   - Proposed fix: "When between 3 and 2, prefer 3 if all primary files are present."

### Low Priority

6. **"full / partial / insufficient / miss" labels are not tied to recall/precision framing**, making the rubric more subjective than it needs to be. Consider renaming to "recall=all / recall=partial / recall=weak / recall=none."

## Positive Aspects

- Explicit "do not reward long list" + "extra files lower precision but not recall" — clean framing.
- JSON-only, no tool use directive is present and unambiguous.
- Schema uses `additionalProperties: false` and enum-constrained level — strict.
- 4-level scale (not 0-3 with an off-by-one) matches integer enum.

## Recommendations

Apply fixes 1–3 before running the 5 scenarios. Fixes 4–5 are small quality improvements. After changes, dry-run mentally against req-09 and req-02 — those are the two scenarios most likely to expose remaining rubric ambiguity.

## Files Reviewed

- `tools/benchmark/prompts/judge_stage2.md` (prompt)
