# Expert Review: Prompt Engineer — Stage 1 Facet (2-axis version)

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**File Reviewed**: `tools/benchmark/prompts/stage1_facet.md` (1 file)

## Overall Assessment

**Rating**: 4/5

**Summary**: The rewrite from 3 axes to 2 axes is a clean, well-reasoned simplification and the prompt is clearly structured, schema-aligned, and substantially shorter than the original. It will very likely produce valid enum-only JSON on the 5 benchmark scenarios. The main weaknesses are (a) inconsistency between the "under-specify" rule and the REST rate-limit example, which currently teaches the model to pad axes on uncertain questions; (b) one internally inconsistent worked example (review-04 category order) that may subtly steer the model; and (c) an under-specified `out_of_scope` instruction that conflicts with the shown empty-array example. None of these threaten recall on the 5 in-scope scenarios, but they put scenario req-09 (uncertain) at risk and could regress on future scenarios.

## Key Issues

### High Priority

1. **"Still emit plausible facets when out_of_scope" contradicts the out_of_scope example**
   - Description: The prose says "If coverage is `out_of_scope`, still emit plausible facets (do not leave empty)", but the final example ("Spring Boot の設定ファイルはどこに置く？") returns `{"type": [], "category": [], "coverage": "out_of_scope"}`. These two instructions disagree, and since the example is the last thing the model sees before the question, the example will win. The constraint says "MUST include coverage so downstream can short-circuit out_of_scope" — which actually argues the empty-array behavior is fine — but then the prose is misleading.
   - Proposed fix: Pick one and make them consistent. Recommended: change the prose to "If coverage is `out_of_scope`, leaving both axes empty is acceptable; downstream will short-circuit on coverage alone." Then the Spring Boot example matches. Reserve "still emit plausible facets" for `uncertain`, not `out_of_scope`.

2. **The `uncertain` example (REST rate limit) directly contradicts the "under-specify" rule**
   - Description: The rate-limit example emits `type: ["component","processing-pattern"]`, `category: ["handlers","restful-web-service"]` — 2 types and 2 categories, one of which (`restful-web-service`) is speculative because the user only mentioned REST as the surface. This is exactly the behavior "Under-specify > over-specify" forbids, and it's the example most structurally similar to req-09 (which is literally the same question in this benchmark). Since the filter is AND, pairing `processing-pattern` with `restful-web-service` will narrow recall; worse, if the real answer lives in `component/handlers/*` only, adding the pattern axis filters it out of any pattern-specific view.
   - Proposed fix: Either (a) change the REST example to `{"type": ["component"], "category": ["handlers"], "coverage": "uncertain"}` to demonstrate the under-specify rule on an uncertain question, or (b) add a concrete sentence: "`uncertain` does not justify additional axis values; apply the same under-specify rule as `in_scope`." Option (a) is preferred because it also aligns with what req-09 should emit.

### Medium Priority

3. **Dual-role of pattern-name categories is explained but not enforced by a rule**
   - Description: The prompt correctly flags that 7 category values double as processing-pattern names, and says "when pattern-specific, pair them with `type: ["processing-pattern"]` (and typically also `component`)." But there is no explicit rule for the *reverse* case: when to use e.g. `web-application` as a plain category without `type: processing-pattern`. In practice the 7 pattern-name categories almost never appear as non-pattern type combinations in `index.toon` (each pattern has its own subtree), so a model that emits `category: ["web-application"]` with `type: ["component"]` will match zero rows. This is latent risk, not a current failure — but it's the kind of silent-zero-result mode that is hard to detect.
   - Proposed fix: Add a short bullet: "The 7 pattern-name categories (`nablarch-batch`, `jakarta-batch`, `restful-web-service`, `http-messaging`, `web-application`, `mom-messaging`, `db-messaging`) are used only with `type: processing-pattern`. For component-level questions, use generic categories like `handlers`, `libraries`, `adapters`."

4. **review-04 example category ordering is inconsistent with the type ordering**
   - Description: Example 2 emits `type: ["component","processing-pattern"]` but `category: ["libraries","web-application"]`. Both are sets (arrays with uniqueItems), so order is semantically irrelevant to the filter — but the prompt consistently lists `component` first and `libraries` first, which is fine. What is confusing is that the first example (review-01) emits `type: ["processing-pattern","component"]` (pattern first) while review-04 emits `component` first. A model that tries to infer a rule from order will see noise.
   - Proposed fix: Pick one ordering convention (e.g., "list the dominant intent first") and apply it consistently across all 5 examples. Recommend: for "how do I build X" questions lead with `processing-pattern`; for mechanism questions lead with `component`. This is minor but cheap to fix.

### Low Priority

5. **Schema does not enforce minItems when coverage is not out_of_scope**
   - Description: The JSON schema allows `type: []` and `category: []` for any coverage, so a lazy model could emit empty arrays with `coverage: "in_scope"` and pass validation. This is extremely unlikely given the examples, but the constraint "MUST use enum-only values drawn from the actual index.toon" implies we actually want at least one value when coverage ≠ out_of_scope.
   - Proposed fix: Optional. Add "When `coverage` is `in_scope` or `uncertain`, at least one of `type` or `category` must be non-empty." Schema-level enforcement via `if/then` adds complexity; a prose rule is sufficient.

6. **`development-tools` vs `testing-framework` category mapping is not illustrated**
   - Description: `development-tools` (type) and `testing-framework` (category) are both listed but no example shows the pairing, nor any example shows `guide` or `setup`. A future scenario about "how do I write a repository test for a batch action" could cause the model to guess.
   - Proposed fix: Optional. Not needed for the 5-scenario benchmark; consider adding a 6th example covering dev-tools before scaling scenarios.

## Positive Aspects

- Clean, compact structure — Context → Axes → Coverage → Rules → Schema → Examples → Question — easy for the model to parse.
- Axis enumerations are embedded directly and the schema re-enforces them; the "never invent axis values" instruction is explicit.
- The rationale for making processing-pattern not-an-axis is clearly captured in the Context section, which prevents a model from trying to reconstruct the old axis.
- The "under-specify > over-specify" rule is stated prominently and with a concrete counter-example (バリデーション → do NOT add web-application).
- The cross-cutting vs pattern-specific distinction is the right framing; it matches what the index.toon actually supports.
- Examples cover: pattern-entry (batch), pattern + mechanism (validation), cross-cutting (transaction), uncertain (REST), out_of_scope (Spring Boot) — good span.

## Predicted Behavior on the 5 Benchmark Scenarios

Assuming the two High issues are fixed (make REST example under-specified, align out_of_scope prose with empty-array example). Without the fixes, req-09 is at risk.

- **review-01 (nightly batch)** — Expect `{"type":["processing-pattern","component"], "category":["nablarch-batch","libraries"], "coverage":"in_scope"}`. Directly mirrors example 1; very low risk.
- **review-04 (input validation)** — Expect `{"type":["component","processing-pattern"], "category":["libraries","web-application"], "coverage":"in_scope"}`. Directly mirrors example 2; very low risk. (Potential minor risk: model may omit `processing-pattern`+`web-application` if it reads the under-specify rule too strictly — acceptable, since expected_sections include `component/libraries/*`.)
- **impact-01 (transaction)** — Expect `{"type":["component"], "category":["handlers"], "coverage":"in_scope"}`. Matches example 3 exactly; very low risk. This is the cross-cutting case the prompt handles best.
- **req-02 (authorization)** — Expect `{"type":["component","processing-pattern"], "category":["handlers","libraries","web-application"], "coverage":"in_scope"}` (3 categories, within maxItems=4). Small risk the model omits `libraries` (permission_check lives there) because the user did not name Bean Validation / UniversalDao-style concrete mechanism. The prompt's Rule 2 ("when the user names a concrete mechanism") is a negative signal here — the user only said 権限チェック, which is a *type* of mechanism but not a Nablarch-specific name. Consider whether a future prompt tweak should say "for security-flavored mechanisms (auth, authz, CSRF, rate limit), default to including `libraries` alongside `handlers`".
- **req-09 (REST rate limit)** — With current prompt, model will copy example 4 and emit `{"type":["component","processing-pattern"], "category":["handlers","restful-web-service"], "coverage":"uncertain"}`. If expected_sections is empty, this still works (downstream returns no match) — but it wastes Stage 2 tokens on false candidates. With the proposed fix (example 4 → under-specified), model will emit `{"type":["component"], "category":["handlers"], "coverage":"uncertain"}` or similar, which is cleaner.

## Recommendations Before Running the Benchmark

1. **Must do**: Resolve the prose-vs-example contradiction for `out_of_scope` (Issue 1).
2. **Strongly recommended**: Rewrite the REST rate-limit example to demonstrate under-specify (Issue 2). This directly affects req-09's Stage 2 token cost and is the example most likely to be imitated on uncertain questions.
3. **Nice to have**: Add the dual-role enforcement bullet (Issue 3) to prevent future silent-zero bugs.
4. After the fixes, run once against all 5 scenarios and diff the emitted facets against the predictions above; any deviation beyond the noted risks should be investigated before reporting benchmark numbers.

## Files Reviewed

- `tools/benchmark/prompts/stage1_facet.md` (prompt)
