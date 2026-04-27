# Prompt Engineer Review: search_ids.md (recall-first rewrite)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Prompt Engineer
**File**: `tools/benchmark/prompts/search_ids.md`
**Input to review**: impact-01 real smoke output attached

## Rating: 4/5 — Approve with M1 + M2 folded in

Strong adherence to the stated design intent (recall-first). Real output
shows the intended behavior: TMH s1 / s3 now pulled alongside the literal
match. The "Why foundational sections matter" subsection provides a
causal model, not just a rule. L1 verdict on impact-01 is attributable
to AI-3 actor choice, not search recall.

## Issues applied

### M1: Cap precedence
Added: when hitting 10-item cap, drop weakest literal-match before
dropping any file's s1.

### M2: Cap foundational sections per file
Added: at most 2 foundational sections per file (s1 + one structural).
Restricted foundational rule to files already selected.

### Deferred (Low)
- L1: example 3 item count mismatch with smoke output — cosmetic.
- L2: subsumed by M2 scoping.

## Non-negotiable constraints preserved

- AI-1 remains title-only (no body reads).
- 10-item cap, empty-list rule, schema, `file_id|sid` format unchanged.

## Smoke output attached

Previous (precision-first): 5 selections, TMH s1/s3 missing — judge L1.
New (recall-first): 10 selections, TMH s1/s3 included — judge still L1
due to AI-3 actor-choice issue (separate problem).
