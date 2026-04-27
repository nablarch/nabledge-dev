# Prompt Engineer Review: stage1_ids.md

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: `tools/benchmark/prompts/stage1_ids.md`

## Overall Assessment

**Rating**: 3/5 (initial) → APPROVE WITH CHANGES (all applied)
**Summary**: Sound core design (direct LLM index + `file_id|sid` selection replaces failing facet approach). Gaps were in edge-case framing and end-of-prompt reinforcement, both disproportionately hurting Haiku.

## Key Issues and Decisions

### High Priority — All IMPLEMENTED

1. **No "JSON only" framing at prompt end**
   - Fix: Added `## Output` section after `{{question}}` stating "Return exactly one JSON object... response must start with `{` and end with `}`"
   - Decision: Implement Now — Haiku frequently echoes reasoning without this

2. **No guidance for multi-topic questions**
   - Fix: Added "If the question covers multiple distinct topics, include 1–3 sections per topic (still within the 10-item cap)."
   - Decision: Implement Now

3. **Empty-list case under-specified**
   - Fix: Expanded empty-list guidance with explicit "Do NOT return a best-guess consolation pick"
   - Decision: Implement Now — LLM default to helpfulness breaks this

### Medium Priority — All IMPLEMENTED

1. **Example set too thin (2 examples)**
   - Fix: Added 2 more examples: (a) feature_details ToC pattern with Japanese section title match, (b) narrow concrete-term question yielding 1 pick
   - Decision: Implement Now

2. **`file_id|sid` vs `file_id` mismatch with index header**
   - Fix: Added explicit "Always emit full `file_id|sid` form. Do NOT emit bare `file_id`. If a file has no sections in the index, do not select it."
   - Decision: Implement Now

3. **No duplicate protection in schema**
   - Fix: Added `"uniqueItems": true` to both the prompt schema block and `SCHEMA_STAGE1_IDS` in `run.py`
   - Decision: Implement Now

### Low Priority — DEFERRED

- L1 (stricter `s\d+` regex): Current `[a-zA-Z0-9_-]+` works. Stricter pattern would reject valid section ids if the index schema evolves. Defer until we see actual hallucination failures.
- L2 (duplicate "1-10 picks" phrasing): Minor redundancy that reinforces the rule. Keep.

## Positive Aspects

- Clear two-line index format explanation
- Concrete selection heuristics (section title match, Japanese terms, feature_details ToC)
- Schema regex enforces the exact `file_id|sid` shape
- Empty-list case explicitly permitted

## Files Modified

- `tools/benchmark/prompts/stage1_ids.md` — added output-end directive, strengthened empty-list rules, added 2 examples, added duplicate rule
- `tools/benchmark/run.py` — added `uniqueItems: true` to `SCHEMA_STAGE1_IDS`
