# Expert Review: Prompt Engineer — Step 6 H-1 through L-2

**Date**: 2026-04-27
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: `tools/benchmark/prompts/search_ids.md`, `tools/benchmark/bench/search_ids.py`

## Overall Assessment

**Rating**: 3/5
**Summary**: The prompt has strong structural intent (4-step Read-first procedure, evidence
grounding, scope checks) but several clarity and reliability issues undermine consistent
execution. Key findings: `caveats` lacked a `cited` field (schema/prompt mismatch), schema
field name collision between Step 3 internal notes and Step 4 output, and the precision
mandate was buried at the end of Step 4 rather than leading it.

## Key Issues

### High Priority

1. **H-1: `caveats` schema — missing `cited` field**
   - Description: `caveats` was defined as `string[]` in the schema but the prompt
     instructed the model to ground caveats in read sections. No `cited` field existed
     to record the source, making the grounding instruction unverifiable.
   - Suggestion: Change schema to `{note: string, cited: file_id|sid}[]` and update
     the prompt to require `cited` for every caveat entry.
   - Decision: Implement Now
   - Reasoning: Without a `cited` field, hallucinated caveats cannot be detected.
     Committed `22d866850`.

2. **H-2: `scope_note` placement — defined in output schema, needed in Step 3**
   - Description: `scope_note` was a field on `selections[]` items but the intent was
     to capture scope mismatches at Read time (Step 3) before selection. Placing it in
     `selections` makes it a post-hoc annotation rather than a read-time check.
   - Suggestion: Move `scope_note` to `read_notes[].relevant_sections[]` so the model
     records scope mismatches at the point of reading, not at the point of selecting.
   - Decision: Implement Now
   - Reasoning: Scope mismatches should be caught during reading, not rationalised after
     selection. Committed `3f5b0f6dc`.

3. **H-3: No self-verification substep before composing the answer**
   - Description: The model moved directly from selecting sections to composing the
     answer without a mandatory check that every factual claim was grounded in the
     body excerpts.
   - Suggestion: Add an explicit "Self-check before composing" substep: for each
     selection, re-read the evidence and locate a verbatim supporting sentence for
     every claim. Drop unsupported claims.
   - Decision: Implement Now
   - Reasoning: C-claim hallucinations (ThreadContext, INSERT前TRUNCATE) traced to
     answer composition without grounding check. Committed `5b09afd0e`.

### Medium Priority

4. **M-1: `candidate_files` / `read_notes` maxItems 20 — inconsistent with 12-file cap**
   - Description: Step 2 prose said "Max 12 files" but the schema allowed 20 items,
     creating an inconsistency that could confuse schema-aware models.
   - Suggestion: Lower both `maxItems` to 12 to match the prose constraint.
   - Decision: Implement Now
   - Reasoning: Schema and prose must agree. Committed `22704ce47`.

5. **M-2: Precision mandate buried at end of Step 4**
   - Description: "Narrow from selections. Step 2–3 were recall-first; Step 4 answer
     is precision." appeared as the last bullet in Step 4 — easy to miss. Models tend
     to follow the first instruction they encounter in a step.
   - Suggestion: Promote this to the Step 4 heading and opening paragraph. Remove the
     duplicated trailing bullet.
   - Decision: Implement Now
   - Reasoning: Precision-first framing for Step 4 is central to avoiding over-reach.

6. **M-3: Naming collision — `evidence` used for both Step 3 body excerpt and Step 4 output**
   - Description: `read_notes[].relevant_sections[].evidence` (body excerpt) and
     `evidence[]` (output quotes) share the name `evidence`. Instructions referring
     to "the evidence" are ambiguous about which field is meant.
   - Suggestion: Annotate the Step 3 field as "body excerpt" in the prose. The schema
     field name remains `evidence` (no schema change needed) but the prose disambiguates.
   - Decision: Implement Now
   - Reasoning: Ambiguous field names contribute to self-check instructions being
     misapplied to the wrong field.

7. **M-4: Execution model not explicitly stated**
   - Description: The Procedure section said "Complete each step fully before moving to
     the next" but did not state that steps must be executed sequentially one at a time.
     The Read-mandatory rule was in Step 3 but the sequential model was implicit.
   - Suggestion: Add explicit sequential-execution framing to the Procedure intro:
     "Execute steps one at a time, in order. Complete each step in full before starting
     the next."
   - Decision: Implement Now
   - Reasoning: Implicit sequential model led to AI skipping Read calls when index
     scanning felt sufficient.

### Low Priority

8. **L-1: `matched_on` — no tiebreak rule when multiple values apply**
   - Description: A section discovered via body read may also have a matching title.
     The prompt did not specify which `matched_on` value to use in such cases.
   - Suggestion: Add tiebreak rule: when multiple values apply, use the
     highest-confidence one (`"title"` > `"keyword"` > `"body"`).
   - Decision: Implement Now
   - Reasoning: Consistent `matched_on` values improve downstream analysis of recall
     vs. precision signal.

9. **L-2: No guidance for Read errors**
   - Description: If a file listed in `candidate_files` could not be read (file missing,
     permission error), the prompt gave no instruction. The structural requirement
     ("one entry per file_id") would be violated.
   - Suggestion: Add instruction: "If Read returns an error, record the entry with
     `relevant_sections: []` and `read_error: true`." Add `read_error: boolean` (optional)
     to the schema.
   - Decision: Implement Now
   - Reasoning: Defensive handling prevents schema validation failures on file errors.

## Positive Aspects

- The 4-step procedure is well-structured and clearly separates recall (Steps 2-3)
  from precision (Step 4).
- The `scope_note` concept is sound — capturing scope mismatches at read time prevents
  later rationalisation.
- The Read-attestation evidence verification approach (prefix check) is pragmatic and
  correctly avoids false positives for benign whitespace/markdown drift.
- The `matched_on` field provides valuable signal for diagnosing recall vs. precision
  failures.

## Recommendations

- After implementing H-1 through L-2, run 3 benchmark cases (req-05, review-01,
  review-08) to verify no regression and that review-08 reaches L3.
- Consider adding a `files_skipped_due_to_error` count field to `steps` for monitoring.
- Long-term: if C-claim hallucinations persist after these fixes, investigate whether
  the self-check substep is being executed — add a diagnostic field to capture which
  claims were dropped.

## Files Reviewed

- `tools/benchmark/prompts/search_ids.md` (AI prompt)
- `tools/benchmark/bench/search_ids.py` (schema definition + execution logic)
