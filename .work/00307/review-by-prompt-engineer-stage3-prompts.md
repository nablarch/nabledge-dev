# Prompt Engineer Review: Stage 3 Prompts (pre-Round 1)

**Date**: 2026-04-22
**Reviewer**: Prompt Engineer subagent (independent context)
**Files Reviewed**:
- `tools/benchmark/prompts/stage3_section_select.md`
- `tools/benchmark/prompts/stage3_answer.md`
- `tools/benchmark/prompts/judge_stage3.md`

## Overall Ratings

| Prompt | Initial Rating |
|--------|----------------|
| stage3_section_select.md | 3.5 / 5 |
| stage3_answer.md         | 3.5 / 5 |
| judge_stage3.md          | 4.0 / 5 |

All three were functional on the impact-01 smoke test (judge=3). Review found
material gaps around grounding whitelist, citation consistency, language
fallthrough, and judge 2↔3 boundary. All High/Medium issues were fixed
before Round 1.

## Applied fixes

### stage3_section_select.md
- **Schema pattern tightened** to `^[a-zA-Z0-9_./-]+\.json:[a-zA-Z0-9_-]+$`
  to reject malformed paths.
- **Whitelist grounding rule**: every selector's `path` and `section_id`
  MUST appear verbatim in the candidate list. No inventions.
- **≥1 primary mandatory** softened to "unless no candidate plausibly
  fits, then return `[]`" — resolves the contradiction with
  out-of-scope handling.
- **Candidate-list format spec added** so the model knows what shape to
  parse.
- **Two worked examples added**: one typical batch question, one
  not-built-in (rate limiting).
- **Typical range 3–7 selectors** floor added.

### stage3_answer.md
- **Language rule**: answer in the same language as the question. JP
  uses `結論/根拠/注意点/参照`; EN uses `Conclusion/Evidence/Caveats/
  References`. Both shapes documented.
- **Citation whitelist**: only cite selectors that appear as delimiters
  in the supplied section content.
- **`cited` consistency rule**: `cited` array must equal the set of
  `path:section_id` mentioned in `answer`, no extras or omissions.
- **Length guidance**: target 800–1500 chars; never exceed 4000.
- **Not-built-in path spec**: explicit `結論: Nablarch には標準機能は
  ない。最も近い代替は ...` template with closest-neighbor citations.
- **Schema pattern tightened** (same as section_select).

### judge_stage3.md
- **"Material detail" defined**: only downgrade 3→2 when the user
  cannot act correctly without the missing detail.
- **Grounding signals added for the judge**:
  - Empty `cited` + specific API/class names claimed → ≤ 1.
  - Obviously unrelated `cited` paths → at least one level downgrade.
  - `cited` vs `answer`-text mismatch → one-level downgrade.
- **Worked not-built-in example** inlined (rate limiting → handlers +
  restful-web-service).
- **Reason format** now requires `Expected core:` before `Verdict:` —
  forces judge to commit to the correct-answer shape before rating,
  reducing 1↔2 drift.

## Decision

Ready for Stage 3 Round 1 on 5 scenarios.
