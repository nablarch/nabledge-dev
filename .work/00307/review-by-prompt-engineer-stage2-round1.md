# Prompt Engineer Review: Stage 2 Judge (Round 1)

**Date**: 2026-04-22
**Reviewer**: Prompt Engineer subagent (independent context)
**Files Reviewed**:
- `tools/benchmark/prompts/judge_stage2.md`
- `.work/00307/rounds/stage2-round1.md`
- `tools/benchmark/.results/20260422-123225-stage2-sonnet/` (per-scenario stream + result)

## Overall Assessment

**Rating: 4 / 5**

The judge prompt is well-scoped, concise, and the rubric is written with the right priorities (recall-only level 3, not-built-in rule, "judge list as a whole"). All 5 verdicts are defensible from title+path alone. Reasons are informative and consistent. However, a perfect 5/5 round on a 5-scenario sample does not prove calibration — the prompt lacks explicit anti-drift guardrails that would matter on level 2 boundary cases and on ambiguous not-built-in questions.

## Per-scenario defensibility

| id | Verdict defensible from title+path? | Reason quality |
|----|-------------------------------------|----------------|
| review-01 | Yes — "ファイルをDBに登録するバッチの作成" + batch arch files are the canonical answer set | Strong, names specific primary titles |
| review-04 | Yes — libraries-validation + Bean/Nablarch Validation + comparison file is textbook | Strong, explicit primary file list |
| impact-01 | Yes — transaction_management_handler + loop_handler both present | Strong, both primaries named with paths |
| req-02 | Yes — permission_check_handler + permission_check + role_check triad | Strong |
| req-09 | Yes — not-built-in rule applied correctly; handlers + restful-web-service docs are the right near-neighbors | Reason explicitly cites the not-built-in rule — best-in-class traceability |

Req-09 handling is correct per the rubric. The judge identified no exact match exists, invoked the near-neighbor rule, and named what a Nablarch expert would actually open. This is the case the rubric was written for.

## Ambiguity risks not exercised by this sample

The 5 scenarios were all clean recall wins. Cases where the judge could plausibly drift 2→3 or 3→2 are untested:

- A list missing **one of two** required primaries (true level 2). The rubric's tiebreaker says "choose 3 if every primary is present" — but does not say what counts as "primary" when the question has 2+ required files.
- A list with a **plausible-title-but-wrong-topic** file. Current rule "if title fits, assume content fits" is correct for recall, but opens a path to false level 3 if the judge is too generous on title matches.

## Issues

### High Priority

**1. "Primary file" is undefined**
- Description: The rubric relies on "every primary file" without defining primary. On multi-file questions (e.g., review-04 required 3 primaries) the judge invents its own primary set, which is a calibration risk across runs.
- Proposed fix: Add a one-line definition: *"Primary file = a file a domain expert would open to directly answer the question (not context/background). Enumerate them in your reason before deciding the level."* This forces the judge to make its primary-set explicit and auditable.

### Medium Priority

**2. Title-match generosity has no brake**
- Description: "If the title fits the topic, assume the content fits" is correct for recall but could accept coincidental matches and inflate to level 3.
- Proposed fix: Add: *"A title 'fits' only if a Nablarch domain expert, seeing the title, would expect this file to contain the mechanism being asked about. Surface-keyword overlap alone does not qualify."*

**3. No instruction to enumerate expected primaries before verdict**
- Description: Reasons vary in shape (some list primaries, some summarize). Round 1 was fine; drift appears at scale.
- Proposed fix: Require reason format: *"Expected primaries: [...]. Present in list: [...]. Verdict: N."* Keeps within 300 char cap and makes audit trivial.

### Low Priority

**4. Reason-language mismatch**
- Description: One reason JP, four EN, no rule.
- Proposed fix: Add *"Write the reason in the same language as the question."*

**5. No worked example for not-built-in**
- Description: The rule is stated but not demonstrated; req-09-like questions are where judges most often over-penalize.
- Proposed fix: Append one 2-line example inline — question "Nablarch に rate limiting はある？" → level 3 with near-neighbor handlers.

## Positive Aspects

- Recall-only framing ("extra files lower precision but not recall") is correctly encoded and respected by all 5 outputs.
- Tiebreaker "choose 3 if every primary is present" is clear and well-placed.
- Not-built-in rule is concrete (names rate limiting as the exemplar); req-09 verdict proves it works.
- Reasons stay under 300 chars and name specific paths — high audit value.

## Recommendation

Adopt the two High/Medium fixes (define primary, require enumerate-then-verdict) before the prompt is used on a larger scenario set. Round 1's 5/5 is encouraging but does not exercise the 2↔3 boundary — expand with 2–3 synthetic level-2 cases (deliberately drop one required primary) before concluding calibration.
