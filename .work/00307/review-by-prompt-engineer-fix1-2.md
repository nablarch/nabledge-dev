# Expert Review: Prompt Engineer

**Date**: 2026-04-27
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: The prompt is well-structured and handles two significant bugs (self-correction via verify script and timeout via Grep-only KB access) with clear procedural steps. The scoring table is unambiguous and constraints are explicitly stated. A few gaps could lead to agent misbehavior in edge cases.

## Key Issues

### High Priority

1. **Step 4 retry logic underspecified — agent may loop when file has no quote at all**
   - Description: Step 4 says "If the output starts with `mismatch` → the `sid` is wrong. Use Grep to find the correct sid in the same file." But if the quote is not in the file at all, the agent keeps retrying with the same file and exhausts 3 retries before concluding correctly.
   - Proposed fix: Add explicit branch: "If Grep returns no section in `<file>` containing the quote, try searching other files. If no file contains the quote after 3 retries total, change reason to `UNSUPPORTED_KB_VERIFIED`."
   - Decision: **Implement Now**

2. **Step 4 Bash command template lacks shell quoting — silently breaks for Japanese quotes**
   - Description: `{{python}} {{verify_script}} {{knowledge_root_abs}} <file> <sid> <quote>` does not instruct the agent to quote arguments. A quote with spaces or Japanese characters will be incorrectly parsed by the shell, sending wrong args to the script. This is a correctness risk for all Japanese-text claims.
   - Proposed fix: Provide the command with explicit quoting: `"{{python}}" "{{verify_script}}" "{{knowledge_root_abs}}" "<file>" "<sid>" "<quote>"` and add note that all arguments must be double-quoted.
   - Decision: **Implement Now**

### Medium Priority

3. **Step 3 Grep cap interacts with Step 4 retries in unspecified ways**
   - Description: Step 3 caps Grep at 10 calls total. Step 4 also uses Grep. The prompt does not clarify whether Step 4 calls count against the same budget. If they do, an agent using 9 calls in Step 3 has only 1 Grep for all Step 4 retries.
   - Proposed fix: State explicitly: "Step 4 Grep calls do NOT count against the Step 3 budget. Use up to 3 additional Grep calls per claim in Step 4."
   - Decision: **Implement Now**

4. **`PARTIAL` definition lacks clear boundary vs `COVERED`**
   - Description: "the idea is present but incomplete in a way that loses the core point" — the line between `COVERED` and `PARTIAL` is not drawn clearly. Inconsistent application degrades benchmark reliability.
   - Proposed fix: Add decision rule: "If the answer conveys the semantic core of the A-fact fully, even if phrased differently, mark `COVERED`. Mark `PARTIAL` only when a key qualifier or condition stated in the A-fact is absent and its omission materially changes the guidance."
   - Decision: **Implement Now**

5. **Step 2 B-claims are implicitly treated as final with no revision path**
   - Description: Step 2 classifies B and C provisionally, but Step 3 only revises C. B-claim misidentification (e.g., off-topic claim in B) has no correction path.
   - Proposed fix: Add note at end of Step 2: "B-claims are also provisional. If in Step 3 you discover a B-claim is not grounded in KB and not in pre-loaded sections, reclassify it as C and verify per Step 3."
   - Decision: **Implement Now**

### Low Priority

6. **No language fallback for mixed-language questions**
   - Description: "Write reasoning in the same language as the question" is clear for pure Japanese/English but not for mixed questions (common in Nablarch QA with Japanese prose and English identifiers).
   - Proposed fix: Add "If the question is mixed, default to Japanese."
   - Decision: **Implement Now**

## Positive Aspects

- Scoring table is precise and unambiguous — all four level combinations clearly specified.
- `SUPPORTED_BY_KB` (no penalty) vs `UNSUPPORTED_KB_VERIFIED` (penalizing) distinction is well-motivated and prominently stated.
- Grep `output_mode: "content"` instruction is specific and actionable, preventing listing-mode defaults.
- 10-call Grep cap is a concrete, enforceable guardrail against timeout loops.
- Step 4 retry logic (max 3, fallback to UNSUPPORTED_KB_VERIFIED) is the right design: bounds cost while maintaining quality.
- "A retrieval miss is not an answer defect" is an important correctness point preventing valid-answer penalization.

## Recommendations

1. Shell quoting (H-2) is the most likely source of silent failures for Japanese-text claims.
2. Retry-on-wrong-file (H-1) affects any claim where initial file guess is wrong — a common case when Grep returns multi-file hits.
3. Grep budget clarification (M-3) prevents silent degradation to UNSUPPORTED_KB_VERIFIED due to exhausted budget rather than genuine absence.
4. Consider adding a one-sentence worked example for Step 3 showing concrete Grep call and how to extract `file`, `sid`, `quote` from content-mode output.

## Files Reviewed

- `tools/benchmark/prompts/judge.md` (modified — prompt)
