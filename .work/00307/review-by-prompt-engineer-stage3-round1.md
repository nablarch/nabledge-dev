# Prompt Engineer Review: Stage 3 Round 1 (Sonnet, 5 scenarios)

**Date**: 2026-04-22
**Reviewer**: Prompt Engineer subagent (independent context)
**Files Reviewed**:
- `tools/benchmark/prompts/stage3_section_select.md`
- `tools/benchmark/prompts/stage3_answer.md`
- `tools/benchmark/prompts/judge_stage3.md`
- `tools/benchmark/.results/20260422-135336-stage3-sonnet/{impact-01,req-09,review-04}/`

## Overall Assessment

All three prompts are production-quality for Round 1. The 5/5 level-3 outcome is real, not inflated: answers are grounded, citations match, selections are tight. Issues flagged will surface at 15–30 scenario scale.

## Verdict defensibility (spot checks)

| id | Judge=3 defensible? | Notes |
|----|---------------------|-------|
| impact-01 | Yes | Both LoopHandler + TransactionManagementHandler named, key properties (`commitInterval`, `transactionName`, `transactionCommitExceptions`), placement constraint vs DbConnectionManagementHandler. `cited` matches `answer` exactly. |
| req-09 | Yes | No-built-in + closest-neighbor shape exactly followed. Cites `ServiceAvailabilityCheckHandler` + RESTful architecture overview. |
| review-04 | Yes | Bean Validation + `@Domain`/`@Required` split on domain-bean, code examples, XML config, String-type caveat. No material detail missing. |

No case should have been level 2.

## AI-2 selection quality

- Tight overall, no obvious redundancy.
- review-04 picked 9 sections (6 from `libraries-bean_validation.json`) — near the 10-cap ceiling, trending redundant. Prompt says "typical 3–7" but Sonnet pushed past that on complex questions.

## Prompt ratings

| Prompt | Rating |
|--------|--------|
| `stage3_section_select.md` | 4/5 |
| `stage3_answer.md`         | 4/5 |
| `judge_stage3.md`          | 4/5 |

## Issues

### High Priority

**1. Judge lacks anti-length-bias check**
- Description: "Extra prose does not raise the level" has no concrete probe. At 15–30 scenarios, verbose-but-thin answers can slip to 3.
- Fix: Add "If the answer is >1200 chars but Expected-core items are unticked, downgrade to ≤2. Map each Expected-core item to a specific sentence in answer before verdict."

**2. Section-select soft upper bound not enforced**
- Description: "Typical 3–7" but cap is 10; review-04 hit 9. Over-selection inflates AI-3 cost and context.
- Fix: Change to "Target 3–6. 7+ requires the question to span ≥2 files; justify mentally before picking the 7th. One file × 6 sections is a red flag — prefer the 3 most distinguishing section titles."

**3. Answer prompt does not forbid partial-synthesis prose**
- Description: Invented paths banned but restating concepts only partially covered in sections is not forbidden. Low risk at 5, material at 30.
- Fix: Add "Every sentence in 根拠/Evidence must be directly supportable by one cited section. If a claim requires synthesis across sections, cite all contributing selectors on that sentence."

### Medium Priority

**4. Judge's "clearly unrelated path" heuristic is brittle for near-neighbor cases**
- Description: Works for handlers vs release-notes but risky at scale.
- Fix: Add examples of clearly-unrelated vs plausibly-related path patterns.

**5. Not-built-in "plausible near-neighbor" undefined**
- Description: req-09 passed cleanly; at scale judge may over-accept tangential neighbors.
- Fix: Add "Near-neighbor must share either the request-processing phase or the architectural concern. Cite the neighbor's own section — not a generic handler-list."

### Low Priority

**6. AI-2 examples only show balanced multi-file picks** — add a tight 3-section single-file example.

**7. Answer length soft target silently ignored** (review-04 ~2600 chars). Fix: raise to 800–2500 or note "code blocks excluded from length target".

## Positive Aspects

- `cited`-consistency rule eliminated the "says X, cites Y" failure in all 5 runs.
- "Expected core" forcing in judge reason produces auditable verdicts.
- req-09 not-built-in handling is exemplary.
- AI-2 whitelist grounding: zero invented paths across 5 runs.

## Recommendation

Ship Round 1 prompts as baseline. Apply the two **High** fixes (judge anti-verbosity + AI-2 soft-cap tightening) before the 15-scenario run.
