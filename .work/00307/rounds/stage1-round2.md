# Stage 1 Round 2 — Facet Extraction (2-axis)

**Date**: 2026-04-22
**Scenarios**: 5 (qa-v6-sample5.json — review-01, review-04, impact-01, req-02, req-09)
**Prompt**: `tools/benchmark/prompts/stage1_facet.md` (2-axis: type, category, coverage)
**Scoring**: per-axis Jaccard on `type` and `category`, exact match on `coverage`
**Design review**: `.work/00307/review-by-prompt-engineer-stage1-facet-2axis.md`

## Conditions

| Item | Value |
|------|-------|
| AI-1 tools | none (`--tools ""`) |
| max-turns | 2 |
| permission-mode | bypassPermissions |
| prompt pass | stdin |
| output-format | stream-json (full log captured per scenario) |

## Results

### Haiku — `.results/20260422-121151-stage1-haiku/`

- mean Jaccard(type):     **0.700**
- mean Jaccard(category): **0.667**
- coverage match rate:    **100%**
- mean overall score:     **0.789**
- mean cost (USD):        **$0.0697**
- mean wall (s):          **16.1s**

| id | type (got → want) | cat (got → want) | cov | J(t) | J(c) | cost | wall |
|----|-------------------|------------------|-----|------|------|------|------|
| review-01 | processing-pattern,component → processing-pattern | nablarch-batch,libraries → nablarch-batch | ✅ in_scope | 0.50 | 0.50 | $0.068 | 18.2s |
| review-04 | component → processing-pattern,component | libraries → web-application,libraries | ✅ in_scope | 0.50 | 0.50 | $0.071 | 16.6s |
| impact-01 | component → component | handlers → handlers | ✅ in_scope | 1.00 | 1.00 | $0.078 | 12.5s |
| req-02 | component → processing-pattern,component | handlers → web-application,handlers,libraries | ✅ in_scope | 0.50 | 0.33 | $0.067 | 21.8s |
| req-09 | component → component | handlers → handlers | ✅ uncertain | 1.00 | 1.00 | $0.064 | 11.7s |

### Sonnet — `.results/20260422-121151-stage1-sonnet/`

- mean Jaccard(type):     **0.767**
- mean Jaccard(category): **0.750**
- coverage match rate:    **100%**
- mean overall score:     **0.839**
- mean cost (USD):        **$0.1393**
- mean wall (s):          **18.6s**

| id | type (got → want) | cat (got → want) | cov | J(t) | J(c) | cost | wall |
|----|-------------------|------------------|-----|------|------|------|------|
| review-01 | processing-pattern,component → processing-pattern | nablarch-batch,libraries → nablarch-batch | ✅ in_scope | 0.50 | 0.50 | $0.146 | 9.6s |
| review-04 | component,processing-pattern → processing-pattern,component | libraries,web-application → web-application,libraries | ✅ in_scope | 1.00 | 1.00 | $0.107 | 18.6s |
| impact-01 | component → component | handlers → handlers | ✅ in_scope | 1.00 | 1.00 | $0.227 | 22.2s |
| req-02 | component,check → processing-pattern,component | security-check,handlers → web-application,handlers,libraries | ✅ in_scope | 0.33 | 0.25 | $0.108 | 21.0s |
| req-09 | component → component | handlers → handlers | ✅ uncertain | 1.00 | 1.00 | $0.109 | 21.5s |

## Observations

- Coverage exact match 10/10 across both models — the three-valued coverage
  scheme is well-understood.
- Both models converge to identical output on **impact-01** (pure transaction /
  handlers) and **req-09** (rate limit / uncertain). The two cross-cutting
  extremes are robust.
- Both models agree on **review-01** → miss the same way: they add `component`
  /`libraries` alongside the expected `processing-pattern`/`nablarch-batch`.
  This is over-specification but not fatal — Stage 2 filter will OR these,
  so recall stays 1.0; precision (candidate-set width) is the thing to
  measure at Stage 2.
- **review-04** separates the two models: Sonnet emits the full
  `{processing-pattern,component} × {web-application,libraries}`; Haiku drops
  `processing-pattern` and `web-application`. Both cover the 3 expected
  sections (`feature_details` has `type=processing-pattern`, the other two
  have `type=component`), so Haiku's answer loses recall at Stage 2.
- **req-02** is the weakest spot. Both models miss `processing-pattern` and
  `web-application`. Sonnet also drifts to `check`/`security-check`, probably
  triggered by the word "権限" pulling security vocabulary. Haiku stays in
  `component`/`handlers` — narrower but more defensible. This is the
  scenario to watch at Stage 2.

## Recall vs the filter (preview)

Since the mechanical filter is a simple type×category AND, the practical
impact of each miss is:

| id | Haiku loses? | Sonnet loses? | Why |
|----|--------------|---------------|-----|
| review-01 | no | no | `processing-pattern ∧ nablarch-batch` covers all 3 expected sections |
| review-04 | yes | no | Haiku missed `processing-pattern/web-application` |
| impact-01 | no | no | handlers is correct |
| req-02 | yes | yes | Both miss the pattern side of `feature_details#s14` |
| req-09 | (no expected) | (no expected) | `uncertain` → Stage 2 surfaces near-neighbors |

## Model decision

**Sonnet is strictly better on this sample**:
- +0.067 type Jaccard, +0.083 category Jaccard, +0.050 overall
- Does not lose recall on review-04 (Haiku does)
- 2× cost ($0.139 vs $0.070) but absolute is tiny ($0.70/10k runs)
- Comparable wall (18.6s vs 16.1s)

Moving to **Sonnet** for all downstream stages.

## Next Round gaps to watch

1. **review-01 over-specification** (`component,libraries` added). If Stage 2
   candidate set balloons, tighten the "include component only when the user
   names a concrete mechanism" rule.
2. **req-02 pattern-side miss**. The question "権限に応じて、アクセスできる
   画面を制限したい" does name a pattern (画面 = web-application) but neither
   model picked it up. Either strengthen that signal in the prompt, or accept
   it and rely on AI-2 to bridge via the handlers/libraries files that
   reference `feature_details#s14`.
3. **Sonnet's security-check drift on req-02**. Isolated — one-shot noise or a
   signal that "権限" lexical association to security is too loose. Revisit at
   Round 3 if it recurs.

## Decision for next step

Per Prompt Engineer post-Round 2 review
(`.work/00307/review-by-prompt-engineer-stage1-round2-results.md`): Round 2 had
one genuine recall miss (req-02), fixable by 3 targeted prompt edits + one
scenario fix. Run Round 3 before Stage 2 so Stage 2 numbers are interpretable.

See `.work/00307/rounds/stage1-round3.md` for Round 3 results.

No back-propagation of `processing_patterns` column is needed — design-level
simulation and this Round 2 measurement both confirm 2 axes are sufficient.
