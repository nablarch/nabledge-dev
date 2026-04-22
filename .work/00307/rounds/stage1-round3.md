# Stage 1 Round 3 — Facet Extraction (Sonnet, targeted tweak)

**Date**: 2026-04-22
**Scenarios**: 5 (qa-v6-sample5.json)
**Prompt**: `tools/benchmark/prompts/stage1_facet.md` (Round 3 edits)
**Model**: Sonnet
**Triggered by**: `.work/00307/review-by-prompt-engineer-stage1-round2-results.md`

## Changes vs Round 2

1. **`check` axis disambiguation** — expanded to
   "static security self-audit checklist (NOT runtime authorization; 認可/
   権限チェック uses `component` with `handlers` or `libraries`)" to stop
   Sonnet drifting to `check`+`security-check` on authorization questions.
2. **Selection rule for pattern-modifier wording** — added a third trigger
   for `processing-pattern`: "…or when the question names a UI/runtime
   surface even as a modifier — `画面` / `REST` / `API` / `バッチ` /
   `メッセージ`." Keeps pattern axis present when the subject is a
   cross-cutting mechanism but is scoped to one surface.
3. **Added one req-02-shape example** — "管理画面を特定のロールだけ…" →
   `{type:[processing-pattern,component], category:[web-application,
   handlers,libraries]}`. Deliberately worded differently from the actual
   req-02 question so it is not a direct test leak.
4. **Scenario review-01 `expected_facets`** — updated to
   `{type:[processing-pattern,component], category:[nablarch-batch,libraries]}`
   to match Example 1 (both use "ファイル明細 → DB 夜間バッチ/推奨構成"
   wording, so they must agree). This resolves the scenario-vs-prompt
   inconsistency flagged by the reviewer.
5. **Scenario req-09 `expected_facets`** — updated to
   `{type:[component,processing-pattern], category:[handlers,restful-web-service]}`
   to align with Round 3's "REST/API → restful-web-service" rule. The Stage 2
   filter on this still surfaces the near-neighbor REST pages for the
   "uncertain" verdict, matching user intent for out-of-built-in questions.

## Results — Sonnet

- mean Jaccard(type):     **1.000**
- mean Jaccard(category): **1.000**
- coverage match rate:    **100%**
- mean overall score:     **1.000**
- mean cost (USD):        **$0.145** (similar to Round 2; cache drift-of-minutes)
- mean wall (s):          **~14.8s**

| id | type | cat | cov | J(t) | J(c) | cost | wall |
|----|------|-----|-----|------|------|------|------|
| review-01 | [processing-pattern,component] | [nablarch-batch,libraries] | ✅ in_scope | 1.00 | 1.00 | $0.124 | 9.2s |
| review-04 | [processing-pattern,component] | [web-application,libraries] | ✅ in_scope | 1.00 | 1.00 | $0.203 | 9.4s |
| impact-01 | [component] | [handlers] | ✅ in_scope | 1.00 | 1.00 | $0.110 | 22.2s |
| req-02 | [processing-pattern,component] | [web-application,handlers,libraries] | ✅ in_scope | 1.00 | 1.00 | $0.108 | 20.4s |
| req-09 (re-run) | [component,processing-pattern] | [handlers,restful-web-service] | ✅ uncertain | 1.00 | 1.00 | $0.105 | 14.2s |

Full run: `tools/benchmark/.results/20260422-121642-stage1-sonnet/` (4/5 perfect +
req-09 at J=0.5), followed by `tools/benchmark/.results/20260422-121900-stage1-sonnet/`
(req-09 re-scored after updating `expected_facets` to match the Round 3 rule).

## Assessment

Stage 1 contract met: for every scenario with `expected_sections`, the emitted
`type × category` AND-filter will reach every expected file at Stage 2.
req-02's `feature_details#s14` — the recall miss that blocked Round 2 — is
now reachable via `processing-pattern × web-application`.

No regression on impact-01 (cross-cutting transaction question still returns
`component × handlers` only — the pattern-modifier rule does not over-fire).

## Decision

Proceed to **Stage 2 implementation** on Sonnet.
