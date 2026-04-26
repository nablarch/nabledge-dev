# Expert Review: Prompt Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: The added output format constraints are well-structured and provide clear guidance to control response length and structure. The instructions are actionable and include helpful examples. Minor improvements were needed for clarity around enforcement and edge cases, which have been implemented.

## Key Issues

### High Priority

None identified.

### Medium Priority

1. **Ambiguity in "500 tokens or less" enforcement**
   - Description: The constraint stated "Target length: 500 tokens or less" but didn't clarify whether this is a hard limit or guideline, and what the agent should do if content naturally exceeds this
   - Suggestion: Add explicit guidance with strict limit for simple queries, may extend to 800 tokens for multi-part questions, prioritize 結論 section if exceeding
   - Decision: **Implement Now**
   - Reasoning: This directly impacts the performance goal. Without clear enforcement guidance, the agent may not consistently achieve the 8-second target. Added explicit guidance (strict limit for simple queries, max 800 tokens for multi-part questions with prioritization of 結論 section) to ensure predictable output time reduction.

2. **Section constraint vs. user question mismatch**
   - Description: The required structure (結論、根拠、注意点) may not fit analytical/comparison questions
   - Suggestion: Add flexibility clause to adapt structure for comparison/analysis questions (比較、コード例、まとめ)
   - Decision: **Reject**
   - Reasoning: While theoretically valid, this adds complexity that contradicts the simplification goal. The 3-section structure is intentionally rigid to enforce brevity and reduce generation time. Adding flexibility clauses would weaken constraint enforcement and potentially increase output time. If this becomes a real user complaint after deployment, we can address it in a future iteration with actual usage data.

3. **Interaction with existing "DO NOT supplement" rule**
   - Description: Priority unclear when knowledge files lack sufficient information to meet 500-token structure
   - Suggestion: Add explicit prioritization: Accuracy > Brevity > Completeness
   - Decision: **Implement Now**
   - Reasoning: This is critical for maintaining answer quality while reducing length. The explicit prioritization resolves potential conflict between two competing requirements. Without this clarity, the agent might either pad answers to reach 500 tokens, or omit critical accuracy to stay under limit. This directly supports both performance AND quality goals.

### Low Priority

4. **Japanese section names justification placement**
   - Description: Rationale "since users are Japanese" appears at end as trailing explanation
   - Suggestion: Move justification to parenthetical after first mention
   - Decision: **Defer to Future**
   - Reasoning: This is a minor stylistic improvement that has zero impact on performance or functionality. Moving the justification would make the text flow slightly better, but doesn't warrant delaying testing. Can be refined in documentation polish if needed.

5. **Missing token counting guidance**
   - Description: Agent may struggle with self-monitoring token usage
   - Suggestion: Provide practical proxy (400-500 Japanese characters ≈ 500 tokens)
   - Decision: **Reject**
   - Reasoning: While the suggestion seems helpful, it adds cognitive overhead without clear benefit. Claude models have internal token awareness and can self-monitor token usage effectively. Adding a character-counting heuristic might lead to unnecessary calculation overhead, inaccuracy across different text types, and distraction from content quality. The strict structural constraint (3 sections with 1 code example) is a better indirect mechanism for length control than character counting.

## Positive Aspects

- **Clear structure**: The three-section format (結論/根拠/注意点) is intuitive and maps well to user needs
- **Concrete example**: The knowledge file reference example ("詳しくは knowledge/features/libraries/universal-dao.json#paging を参照") is specific and actionable
- **Performance-driven**: Directly addresses the performance issue (#54) with measurable constraint (500 tokens)
- **User-centric language choice**: Recognizing users are Japanese and using Japanese section names improves UX
- **Fallback strategy**: The detailed/complex topics handling provides clear escalation path
- **Priority guidance**: Added explicit prioritization (Accuracy > Brevity > Completeness) ensures quality is not sacrificed for speed
- **Flexible enforcement**: Token limit now clarifies strict enforcement for simple queries while allowing reasonable extension for complex multi-part questions

## Recommendations

1. **Add validation checkpoint**: After implementing, test with actual user queries from previous conversations to verify format works across question diversity

2. **Consider progressive disclosure**: For complex topics, structure could be: 概要 (Overview - 200 tokens) → 詳細参照 (Reference links) rather than trying to fit everything into 500 tokens

3. **Monitor effectiveness**: Track actual output length and user follow-up rates to validate if 500 tokens achieves desired balance between brevity and completeness

4. **Performance validation required**: Execute minimum 10 simulation runs as specified in issue #54 success criteria to verify:
   - Average LLM output generation ≤ 8 seconds (50% reduction from 17 seconds baseline)
   - LLM output time reduced from 32% to <20% of total time
   - Answer quality maintained across diverse query types

## Files Reviewed

- `.claude/skills/nabledge-6/SKILL.md` (prompt/workflow)
