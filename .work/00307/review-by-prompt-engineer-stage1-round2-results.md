# Prompt Engineer Review — Stage 1 Round 2 Results

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Artifact**: `tools/benchmark/prompts/stage1_facet.md`
**Measurement**: `.work/00307/rounds/stage1-round2.md` and Sonnet run `.results/20260422-121151-stage1-sonnet/`

## Overall Assessment

**Rating**: 4/5

Sonnet average overall score 0.839, type Jaccard 0.767, category Jaccard 0.750, coverage 100%. The prompt is structurally sound: schema compliance is perfect, `out_of_scope` handling is never triggered incorrectly, and the three-valued `coverage` is robust. Of the three sub-perfect scenarios on Sonnet:

- **review-04**: **effectively perfect** (overall 1.0). My round summary table carried forward an outdated "sub-perfect" tag — the final output matches expected exactly; the set was reordered (`[component, processing-pattern]` vs `[processing-pattern, component]`) but Jaccard is set-based.
- **review-01**: over-specification (adds `component`/`libraries`). Recall preserved; precision cost at Stage 2.
- **req-02**: under-specification on the pattern side (misses `processing-pattern` / `web-application`) plus drift into `check` / `security-check`. **Recall loss** — `feature_details#s14` is unreachable under the type×category AND filter because `processing-pattern` is not emitted.

So there is **one genuine recall miss out of five** on the chosen model (req-02). review-01 is a precision-only concern, review-04 is clean.

## Thinking Traces (Sonnet)

The stream-json extended-thinking content is the decisive evidence:

**req-02** — the model never considered the pattern axis:
> "It could relate to `check` type for security checks / `component` for the actual mechanism... Since it mentions '画面' (screens), it has a web application angle, **but the question is more about the mechanism itself rather than building a web app**"
> Final: `type=[component, check], category=[security-check, handlers]`

Two prompt-level problems are exposed:
1. The "mechanism vs. pattern" disambiguation rule is being read as "if the question names a mechanism, drop the pattern axis." Our rule says `processing-pattern` is added when the question is pattern-entry or clearly scoped to one pattern — but "画面を制限したい" *is* scoped to web-application. The model's self-justification ("question is about the mechanism, not building a web app") shows the heuristic is too binary.
2. `check` vs `component` for authorization is unclear. The enum line `check — security checklist` does not tell the model that the security-check files are a compliance checklist, not the runtime authorization mechanism. The model reasonably read `check`+`security-check` as "this fits authorization."

**review-01** — the model made a conscious over-specification:
> "processing-pattern question about nablarch-batch, **and also involves component knowledge (libraries for file reading, DB access)**"

The "Under-specify over over-specify" rule is in the prompt, but the examples teach the opposite: example 1 ("ファイル明細 → DB") emits `[processing-pattern, component] × [nablarch-batch, libraries]` — **exactly** what Sonnet produced. Expected facets for review-01 in the scenario are `[processing-pattern] × [nablarch-batch]` only. **The canonical example contradicts the expected_facets of the scenario with near-identical wording.** This is a scenario-vs-prompt inconsistency, not a model failure.

**review-04** — thinking shows the model correctly reasoned "include both web-application context and component mechanism," matching expected.

## Key Issues

### High Priority

1. **Example 1 contradicts review-01 expected_facets**
   - Description: Prompt example 1 and scenario review-01 use near-identical Japanese ("ファイル明細 → DB夜間バッチ / 推奨構成"). Example says emit `[processing-pattern, component] × [nablarch-batch, libraries]`; scenario expects `[processing-pattern] × [nablarch-batch]`. The model obediently followed the example and was scored as wrong.
   - Proposed fix: Pick one. Recommended: **tighten the scenario's expected_facets to match the example** — i.e., accept `libraries` / `component` for review-01. "推奨構成を知りたい" legitimately wants libraries coverage (file I/O lib, data-bind lib). Alternatively, rewrite example 1 to emit only `[processing-pattern] × [nablarch-batch]` — but that weakens the "include both axes when a pattern-scoped question also wants the cross-cutting lib" signal that helped review-04 and was the design intent.

2. **req-02 pattern-side miss — rule wording allows the wrong read**
   - Description: The rule says include `processing-pattern` when the question is "how do I build a ___" style. "権限で画面を制限したい" is read as mechanism-question, not pattern-question, so pattern is dropped. Result: `feature_details#s14` becomes unreachable at Stage 2.
   - Proposed fix: Add a third trigger to the `processing-pattern` inclusion rule: **"…or when the question names a UI/runtime surface (画面/REST/バッチ/メッセージ) even as a modifier."** Example: "画面" → include `web-application`; "REST/API" → include `restful-web-service`; "バッチ" → include `nablarch-batch` or `jakarta-batch`. One-line rule + one extra example covering req-02's wording pattern would likely fix it.

3. **`check` axis disambiguation is missing**
   - Description: The axis line `check — security checklist` is too terse. Sonnet picked `check` + `security-check` for an authorization question because nothing told it these files are a static compliance checklist, not the runtime auth mechanism.
   - Proposed fix: Expand the `check` line to: `check — static security self-audit checklist (NOT runtime authorization; authorization/認可 uses component + handlers/libraries)`. Add a negative example or a rule line: "認可/権限チェック/アクセス制限 → `component` + `handlers`/`libraries`, NOT `check`."

### Medium Priority

4. **No example covers the "pattern-modifier" shape**
   - Description: Example 2 ("画面項目のチェック") hits this case, but the subject is validation. No example shows authorization or REST-flavor mechanism questions where the pattern is a modifier.
   - Proposed fix: Add one example of the req-02 shape:
     `"ログインユーザーの権限で画面を制限したい" → {type: ["processing-pattern","component"], category: ["web-application","handlers","libraries"], coverage: "in_scope"}`

### Low Priority

5. **Observation table in round2.md overstates review-04 as sub-perfect**
   - Description: review-04 Sonnet scored 1.0 overall. The prose observation treats it as a "separating" case between models, which is true for Haiku but not a Sonnet weakness.
   - Proposed fix: Clarify in the round log that Sonnet review-04 is clean; the comparison is Haiku-specific.

## Positive Aspects

- Schema compliance 100% on both models, 5/5 scenarios. JSON-only output with `--tools ""` works reliably.
- `coverage` axis 100% match across 10 runs. The three-valued definition is tight enough that even `uncertain` (req-09 REST rate limit) is picked correctly.
- "Never invent axis values" + enum lists held — zero hallucinated categories.
- The pattern-category lock rule (category-names-that-double-as-patterns only with `processing-pattern`) held across all 10 runs.
- Extended-thinking traces show the model is *following* the rules as written, not ignoring them. This means prompt edits will translate directly to behavior changes.

## Recommendations

### Verdict: Run ONE Round 3 prompt tweak before Stage 2

Rationale: the Stage 1 contract for the faceted flow is "no expected file unreachable at Stage 2." req-02 currently breaks that contract, and the trace shows it is a **fixable prompt ambiguity**, not task-inherent. Stage 2 numbers measured on a known-lossy Stage 1 will be hard to interpret — we will not know whether Stage 2 under-recalls because Stage 1 missed or because the filter is wrong.

The tweak is small and targeted:

**Single Round 3 change**: edit `stage1_facet.md` only. Three edits, one round:

1. Expand the `check` axis line with the NOT-authorization clarifier (Issue #3).
2. Add a bullet to Selection rules: "Include `processing-pattern` + its category name when the question names a UI/runtime surface (画面/REST/API/バッチ/メッセージ) — even if the subject of the question is a cross-cutting mechanism." (Issue #2)
3. Add one req-02-shaped example (Issue #4).

Do **not** touch Example 1 / review-01 in this round. Instead, **update the scenario's expected_facets for review-01 to include `component`/`libraries`** — the example-driven behavior is the correct one for "推奨構成" questions. This makes the prompt and scenarios consistent (Issue #1 resolved on the scenario side).

Expected Round 3 outcome on this 5-scenario sample:
- review-01: 1.0 (after scenario fix)
- review-04: 1.0 (already)
- impact-01: 1.0 (already)
- req-02: Jaccard ≥ 0.75 on type/category (adds `processing-pattern`/`web-application`, drops `check`/`security-check`)
- req-09: 1.0 (already)

If any regression appears on impact-01 or req-09 after the edits, that is a signal the new rule is too broad — roll back the third bullet.

### Not recommended (out of scope per constraints, noted for completeness)

- Adding a third axis or reintroducing `processing_patterns` — settled.
- Schema changes — settled.

### After Round 3

Proceed to Stage 2 implementation using Sonnet. The cost delta ($0.07 per 5-scenario run) is immaterial.

## Files Reviewed

- `tools/benchmark/prompts/stage1_facet.md` (prompt)
- `.work/00307/rounds/stage1-round2.md` (round summary)
- `tools/benchmark/scenarios/qa-v6-sample5.json` (expected_facets)
- `tools/benchmark/.results/20260422-121151-stage1-sonnet/{review-01,review-04,req-02}/ai1_result.json`
- `tools/benchmark/.results/20260422-121151-stage1-sonnet/{review-01,review-04,req-02}/ai1_facet_extract.stream-json` (extended-thinking traces)
