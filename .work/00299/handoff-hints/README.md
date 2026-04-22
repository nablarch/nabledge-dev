# Hints Handoff — for Follow-up Issue

This directory preserves the hints assets developed during PR #304 (Issue #299)
before they are removed from RBKC. The follow-up issue will review, curate, and
merge these as AI-generated hints.

## Background

During PR #304 we attempted to generate `hints` mechanically from source
(RST/MD/Excel) and carry them through RBKC's create → verify pipeline.

**What we learned:**

1. **Mechanically-extracted hints have low marginal value.** Anything we can pull
   from source text is already discoverable by body-text search. Real hint value
   lives in *aliases, abbreviations, and synonyms that are not in the body* —
   those can only come from an AI / human curator, not a rule-based extractor.

2. **Granularity mismatch between KC catalog and RBKC converter.**
   - KC catalog: sections down to `h4`
   - RBKC converter: sections at `h2` / `h3` only
   - This mismatch caused a persistent hints-consistency failure through
     Phases 21-D, 21-H, and 21-J (139 FAILs at session 38).

3. **Scope decision (session 38).** RBKC's responsibility was narrowed to
   "rule-based generation of content (title + body) only." Hints are out of scope
   for RBKC and belong to a separate, AI-driven flow.

## Contents

| File | Description |
|------|-------------|
| `v1.2.json` / `v1.3.json` / `v1.4.json` / `v5.json` / `v6.json` | Generated hints files for each Nablarch version (schema: R1〜R6 rules, array values to support duplicate headings). |
| `generate_hints.py` | Script that produced the JSON files above from KC cache + source RST/MD. Implements the R1〜R6 resolution rules. |
| `extract_hints.py` | Earlier extraction helper (Stage 1 / Stage 2). Kept for reference. |

## Handoff Scope for the Follow-up Issue

The follow-up issue should:

1. Treat these JSON files as **input candidates**, not authoritative output.
2. Design a human/AI review flow that adds the hints lacking in source text
   (aliases, abbreviations, colloquial names).
3. Define how the curated hints plug back into the knowledge consumption layer
   — **not** into RBKC's create/verify pipeline.
4. Consider whether the R1〜R6 rule set and the granularity-mismatch problem
   still matter once hints become AI-curated (they may not).

## Non-Goals (do NOT re-introduce into RBKC)

- Mechanical hints extraction inside RBKC converters
- `<details><summary>keywords</summary>` blocks in docs MD
- JSON `hints` field in knowledge files
- Three-way hints consistency check in verify

These were removed in Phase 21-K (see `.work/00299/tasks.md`).
