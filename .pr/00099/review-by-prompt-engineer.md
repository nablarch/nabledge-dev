# Expert Review: Prompt Engineer

**Date**: 2026-03-02
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 3 prompt template files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured prompts with clear instructions, comprehensive validation rules, and practical examples. They demonstrate strong technical understanding and attention to detail. Minor improvements enhance error prevention and edge case handling.

## Key Issues

### High Priority

1. **Missing Error Handling Instructions in generate.md**
   - Description: Prompt doesn't specify what to do when source content is malformed or unparseable
   - Suggestion: Add "Error Handling" section with guidance for ambiguous structures
   - Decision: Implement Now
   - Reasoning: Critical workflow gap. Users need to know what to do when generation fails.

2. **Ambiguous "~2000 Characters" Threshold**
   - Description: Phrase "おおよそ2000文字を超える場合" lacks precision
   - Suggestion: Provide specific threshold: "2000文字以上の場合"
   - Decision: Implement Now
   - Reasoning: Prevents confusion about splitting decisions. Quick fix with high impact.

3. **Inconsistent Validation Criteria**
   - Description: Binary pass/fail validation uses vague terms like "missing hints"
   - Suggestion: Define minimum criteria for hints
   - Decision: Implement Now
   - Reasoning: Affects quality consistency. Can clarify in validate.md without code changes.

### Medium Priority

4. **No JSON Structure Validation Instruction**
   - Decision: Defer to Future
   - Reasoning: Python code validates JSON. Adding to docs seems redundant unless users request.

5. **Unclear Empty Sections Handling**
   - Description: No specification for minimum section content
   - Suggestion: Add guidance for 50-character minimum
   - Decision: Implement Now
   - Reasoning: Important edge case that will occur. Simple addition prevents confusion.

6. **classify_patterns.md Lacks Edge Cases**
   - Decision: Defer to Future
   - Reasoning: Current examples cover main cases. Add based on actual confusion.

7. **Missing Assets Validation Guidance**
   - Decision: Defer to Future
   - Reasoning: Assets structure is simple. Wait for complexity to justify detailed guidance.

### Low Priority

8. Repetitive information in generate.md
9. validate.md could benefit from priority levels
10. No explicit instruction to preserve source language
   - Decision: Defer to Future for all
   - Reasoning: Minor improvements that don't affect core functionality.

## Positive Aspects

- Comprehensive extraction rules with priority table
- Rich formatting examples for RST directives
- Clear JSON schema definition with samples
- Structured validation approach by category
- Practical cross-reference handling
- Asset handling flexibility balancing AI-readability

## Recommendations

1. Add pre-flight checks section listing prerequisites
2. Include troubleshooting guide with FAQ
3. Consider success criteria metrics (quantitative targets)
4. Enhance classify_patterns.md with negative examples
5. Consider confidence score output for borderline validation cases
