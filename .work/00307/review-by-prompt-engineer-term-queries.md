# Prompt Engineer Review: search_ids.md term_queries

**Date**: 2026-04-23
**File**: `tools/benchmark/prompts/search_ids.md`
**Input**: 6 smoke scenarios (review-08, impact-08, req-05, req-01, impact-01, impact-02)

## Rating: 4/5 — Revise (small)

`term_queries` is a low-risk additive supplement, identifier-only framing
is clear, and real outputs show mostly good LLM compliance.

## Key Issues Applied

### High: coverage-gap reasoning
Added an instructional block "How to choose terms (coverage-gap first)":
after drafting selections, ask "what concept/handler/property/annotation
would a complete answer still cite that none of my picked section titles
name?" Emit terms for those gaps. Anti-redundancy rule: do not repeat
terms already visible in picked titles.

### Medium: redundancy from broad class names
Added anti-example: `❌ SimpleDbTransactionManager`, `DbConnectionContext`
— widely referenced class names produce noisy hits. Prefer narrow
identifiers (property/annotation).

## Deferred (Low)
- Japanese domain noun boundary — current examples suffice.
- Cap sizes (3/3/6) — no smoke evidence of cap binding.

## Validation
After revise, re-ran impact-02: raw_selections now includes
`handlers-SessionStoreHandler|s1` and `|s3` (the file the prompt rewrite
was meant to surface). s4 (placement constraints) is still missed — this
suggests a second round of prompt tightening or an orthogonal fix (e.g.
forcing "constraint" titles to be included per file). Out of scope for
this review round.

## Non-negotiable constraints preserved
- AI-1 remains title-only for selections; term grep is script-side.
- 10-item cap + empty-list rule unchanged.
- Recall-first design intact.
