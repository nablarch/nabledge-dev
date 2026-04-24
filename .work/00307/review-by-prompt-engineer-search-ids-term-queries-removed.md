# Prompt Engineer Review: search_ids.md (term_queries removed)

**Date**: 2026-04-24
**File**: `tools/benchmark/prompts/search_ids.md`
**Trigger**: AI-1 no longer generates `term_queries`; deterministic script extracts them from the question. Index itself now carries section-level keywords (361-term allowlist).

## Rating: 4/5 — Revise (small)

## Key Issues Applied

### High — H1: keyword match weight
`—keyword / keyword / ...` suffix was described as "equal-weight hints" but selection rules still framed matches in title-literal terms. A reader who matched via keyword had no guidance on whether foundational-section rule fires.

**Fix applied**: added explicit "A keyword match counts the same as a title match, both for picking a section and for triggering the foundational-section rule below." Also softened "the section whose title most literally restates the question" → "title or keyword most directly restates".

### Medium — M1: keyword-driven example
All 4 examples picked via title alone; none illustrated the new capability. Added example:
```
Question: "DbConnectionManagementHandler との並び順は？"
→ {"selections": ["handlers-transaction_management_handler|s1",
                   "handlers-transaction_management_handler|s3"]}
(s3's keyword DbConnectionManagementHandler matches even though its title
 is just "制約".)
```

### Medium — M2: foundational over-fire
The old "always add s1+制約" heuristic may crowd out other files when a keyword already surfaces the fact. Added exception: "If a keyword-matched section you picked already carries the specific fact the question asks about, you do not need to add an additional foundational section from the same file."

## Deferred (Low)

- L1 case-sensitivity note — schema pattern is already specific enough.
- L2 em-dash separator clarification — added as part of H1 fix.

## Non-negotiable constraints preserved

- AI-1's ONLY output is `selections` — schema is `additionalProperties: false`, forcing wire-level enforcement.
- Recall-first, 10-item cap, empty-list for out-of-scope — unchanged.
- Keyword ingestion never pushes AI-1 toward term generation; terms come from the deterministic `term_extract` module.

## Positive aspects (from reviewer)

- Clean removal of `term_queries` — no residual references anywhere.
- "How to read the index" accurately describes the new format.
- Cap-precedence rule (drop weakest literal-match before dropping s1) survives index enrichment intact.
- Out-of-scope handling is explicit and unambiguous.
