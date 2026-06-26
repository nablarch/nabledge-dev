# Path Coverage: qa.md workflow

**Date**: 2026-06-25
**Workflow**: `.claude/skills/nabledge-6/workflows/qa.md`
**Scenarios run**: pre-03, pre-01, pre-02, oos-qa-01

## Results Table

| Scenario | BM25 terms | BM25 hits | check-answerable | semantic ran | verify | regenerated |
|---|---|---|---|---|---|---|
| pre-03 | `UniversalDao` | 20 | OK | No | PASS | No |
| pre-01 | `requestPath` | 17 | OK | No | PASS | No |
| pre-02 | (none) | 0 | NG | Yes (8 hits) | PASS | No |
| oos-qa-01 | `WebSocket` | 1 | NG | Yes (0 hits) | N/A | No |

## Path Coverage

| Path | Description | Observed | Scenario |
|---|---|---|---|
| Path A | BM25 hits + check-answerable OK (no semantic) | YES | pre-03, pre-01 |
| Path B | BM25 hits + check-answerable NG → semantic ran | YES (partial) | oos-qa-01 (BM25 found 1 marginal hit, check-answerable=NG, semantic returned empty) |
| Path C | No BM25 terms → semantic ran | YES | pre-02 (bm25_terms=[], semantic returned 8 hits) |
| Path D | verify FAIL → regeneration | NOT OBSERVED | None of the 4 scenarios triggered this |

## Notes

### Path B detail
`oos-qa-01` had 1 BM25 hit (WebSocket mention in a migration doc), but check-answerable correctly
judged NG (insufficient content to answer). Semantic search then ran but found 0 sections.
The workflow correctly stopped (step5 sections_used=[], verify=N/A — not regenerated or answered).
This covers the "semantic fallback returns empty → stop" sub-path of step 4.

### Path D not covered
None of the 4 scenarios produced a verify FAIL. To exercise Path D, a scenario would need to
generate an answer that fails the verify check — likely requires a question where the selected
sections are marginally relevant and the generated answer makes claims not backed by the content.

### check-answerable behavior
- pre-02: `bm25_terms=[]` (no extractable identifiers) → check-answerable correctly returns NG
- oos-qa-01: `bm25_sections=1` (only a migration doc mention) → check-answerable correctly returns NG
  The step 3 check is doing the right thing: not just counting hits, but evaluating whether
  the content is sufficient to answer the question.

## Assessment: Is qa.md behaving correctly?

**Yes, for the paths exercised.**

1. **Step 2 (BM25)**: Correctly extracts concrete identifiers (`UniversalDao`, `requestPath`, `WebSocket`) and returns empty terms for abstract Japanese questions (`バリデーション`).
2. **Step 3 (check-answerable)**: Correctly distinguishes between sufficient BM25 content (pre-03: 20 hits on the right docs → OK) and insufficient (oos-qa-01: 1 marginal hit → NG).
3. **Step 4 (semantic fallback)**: Correctly triggered on NG; returns content for in-scope abstract question (pre-02); returns empty for out-of-scope (oos-qa-01).
4. **Step 5/6 (generate + verify)**: Answers pass verify in all cases where content was available. Workflow correctly skips generate+verify when sections_used is empty (oos-qa-01 verify=N/A).
5. **Stop path (oos-qa-01)**: Out-of-scope question correctly terminates with no answer rather than hallucinating.

**Gap**: Path D (verify FAIL → regeneration) was not exercised. This path exists in the workflow
but was not triggered by any of these 4 scenarios.
