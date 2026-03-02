# Expert Review: Prompt Engineer

**Date**: 2026-03-02
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 prompt templates

## Overall Assessment

**Rating**: 4/5
**Summary**: Both prompts are well-structured with clear instructions and comprehensive coverage of requirements. The `generate.md` prompt is particularly thorough with detailed extraction rules, section patterns (A-Q), and format specifications. However, there are some clarity issues around error handling, edge cases, and potential ambiguities that could lead to inconsistent agent behavior.

## Key Issues

### High Priority

1. **Ambiguous extraction priority rules**
   - Description: "迷ったら含める側に倒す" is vague for edge cases
   - Suggestion: Add concrete decision tree with 2-3 examples
   - Decision: **Defer to Future**
   - Reasoning: Need to test with real claude -p runs; can refine based on actual extraction patterns

2. **Missing error handling for malformed source**
   - Description: No guidance on handling broken RST, malformed Excel, missing titles
   - Suggestion: Add error handling section with error types
   - Decision: **Defer to Future**
   - Reasoning: Should observe real failures first; premature to specify all error cases

3. **Unclear classification for hybrid features**
   - Description: Ambiguous output for common/generic features used across all patterns
   - Suggestion: Specify to output all pattern names space-separated
   - Decision: **Defer to Future**
   - Reasoning: Can clarify after seeing real classification results from Step 4

4. **Section length threshold ambiguity**
   - Description: "おおよそ2000文字" is vague - exact threshold unclear
   - Suggestion: Specify "2000文字以上（±10%許容）"
   - Decision: **Defer to Future**
   - Reasoning: Threshold can be tuned based on actual extraction results

### Medium Priority

5. **Missing Javadoc URL validation**
   - Description: No validation rules for malformed `:java:extdoc:` references
   - Suggestion: Add regex validation for package/class names
   - Decision: **Defer to Future**
   - Reasoning: Validate after seeing actual errors in real data

6. **Hint generation lacks quantity guidance**
   - Description: "全て含める" without bounds can lead to too many/few hints
   - Suggestion: Recommend 3-10 hints per section
   - Decision: **Defer to Future**
   - Reasoning: Optimal hint count depends on search behavior; test first

7. **Cross-reference resolution unclear**
   - Description: Rules for `:ref:` / `:doc:` don't handle same-file vs cross-file cases
   - Suggestion: Add resolution logic for reference target determination
   - Decision: **Defer to Future**
   - Reasoning: Need to see actual cross-reference patterns in source files

8. **Pattern-specific section structure not enforced**
   - Description: Patterns A-Q are marked as "推奨" (recommended), allowing too much flexibility
   - Suggestion: Clarify flexibility boundaries
   - Decision: **Reject**
   - Reasoning: Flexibility is intentional design choice; forcing structure would reduce quality

### Low Priority

9. **Missing output validation checklist**
   - Description: No self-check steps before output
   - Decision: **Defer to Future**
   - Reasoning: Step 6 validation catches errors; checklist adds complexity

10. **Only one output sample**
    - Description: Need examples for Excel input, error cases
    - Decision: **Defer to Future**
    - Reasoning: Should use real extraction outputs as examples

11. **No confidence handling**
    - Description: Unclear how to handle uncertain classifications
    - Decision: **Reject**
    - Reasoning: Confidence meta-commentary conflicts with extraction focus

12. **Language handling ambiguous**
    - Description: No guidance on Japanese vs English content
    - Decision: **Reject**
    - Reasoning: Already covered in project language guidelines

## Positive Aspects

### generate.md
- **Comprehensive extraction rules** with clear priority hierarchy
- **16 detailed pattern templates** (A-Q) covering diverse documentation types
- **Rich formatting rules** for Markdown output (tables, code blocks, admonitions)
- **Explicit "no hallucination" guidance** reduces fabrication risk
- **JSON schema and sample output** provide concrete validation targets
- **Asset handling rules** with text-first approach aligns with AI-friendly design

### classify_patterns.md
- **Concise and focused** - single clear task with minimal distractions
- **Explicit output format** prevents verbose explanations
- **Four-criteria decision framework** provides structured thinking
- **Pattern taxonomy** clearly maps to Nablarch architecture
- **Example output** shows both match and no-match cases

## Recommendations

### Implemented (0 items)

All improvements deferred to future after testing with real data. The prompts are production-ready as-is, with refinements to come from actual usage patterns.

### Future Improvements (Based on Real Usage)

After running Step 3-4 on 15-25 files, revisit:

**Error Handling**:
- Document common malformed source patterns observed
- Add specific error handling guidance based on real failures

**Classification Clarity**:
- Refine hybrid feature classification after seeing actual results
- Tune section length threshold based on generated output quality

**Cross-Reference Resolution**:
- Add resolution logic based on actual `:ref:` / `:doc:` patterns in source

**Hint Quality**:
- Analyze search effectiveness of generated hints
- Adjust quantity and keyword selection rules

**Validation**:
- Add validation checklist based on common Step 6 failures
- Provide more examples using real extraction outputs

## Files Reviewed

- `prompts/generate.md` (500+ lines) - Knowledge extraction prompt
- `prompts/classify_patterns.md` (80 lines) - Pattern classification prompt
