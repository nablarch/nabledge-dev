# Expert Review: Prompt Engineer

**Date**: 2026-03-03
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 4 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured prompts with clear work steps and good attention to detail. The prompts demonstrate strong domain knowledge and provide comprehensive guidance. Minor improvements needed in schema references, error handling guidance, and output format clarity.

---

## Key Issues

### High Priority

1. **Missing JSON Schema Definition in generate.md**
   - **Description**: The prompt references "Output the JSON matching the schema above" (line 339) and describes schema properties (lines 259-325), but lacks a formal, executable JSON schema definition. The schema is embedded within markdown documentation rather than being machine-readable.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (lines 259-339)
   - **Suggestion**: Add a complete, standalone JSON schema block after the property descriptions. Use a format that can be validated programmatically:
     ```markdown
     ### JSON Schema

     ```json
     {
       "$schema": "http://json-schema.org/draft-07/schema#",
       "type": "object",
       "required": ["knowledge", "trace"],
       ...
     }
     ```
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: The current prose-based schema description is sufficient for AI agents to understand the structure. Adding a formal JSON schema would improve machine validation but is not critical for Phase 1 implementation. Can be added when we need automated schema validation.

2. **Ambiguous Schema Reference in content_check.md**
   - **Description**: Line 65 states "Report all findings as JSON matching the provided schema" but no schema is actually provided in the prompt. The agent must infer the output structure.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/content_check.md` (line 65)
   - **Suggestion**: Add explicit output schema definition
   - **Decision**: Defer to Future
   - **Reasoning**: The examples in the prompt (lines 67-175) clearly demonstrate the expected output structure. AI agents can reliably infer the schema from examples. Formal schema can be added if output parsing becomes unreliable.

3. **Missing Schema Reference in fix.md**
   - **Description**: Line 37 mentions "Output the entire corrected knowledge file JSON matching the provided schema" but no schema is provided. The agent must assume it's the same schema as generate.md.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/fix.md` (line 37)
   - **Suggestion**: Either include the complete schema or add explicit reference
   - **Decision**: Implement Now
   - **Reasoning**: This is a simple clarity fix. Adding an explicit reference will eliminate ambiguity without requiring major changes.

4. **Missing Schema Reference in classify_patterns.md**
   - **Description**: Line 52 states "Output the result as JSON matching the provided schema" but no schema is provided in the prompt.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/classify_patterns.md` (line 52)
   - **Suggestion**: Add explicit output schema definition
   - **Decision**: Defer to Future
   - **Reasoning**: The examples in lines 54-61 provide a clear output format. This works for current implementation. Can formalize if needed.

### Medium Priority

5. **Unclear Handling of Edge Cases in generate.md**
   - **Description**: The prompt doesn't specify how to handle edge cases like: empty source files, malformed RST/markdown, sources with no clear title, or sources with duplicate section IDs after kebab-case conversion.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (Work Steps 1-2)
   - **Suggestion**: Add an "Edge Cases" section
   - **Decision**: Defer to Future
   - **Reasoning**: The task spec (doc/nabledge-creator-v2-task.md) treats these as out-of-scope for Phase 1. The 21 test files are pre-validated. Can add edge case handling when processing broader documentation sets.

6. **Inconsistent Instruction About Output Format in generate.md**
   - **Description**: Line 339 says "Output the JSON matching the schema above. No explanation, no markdown fences, no other text." but this contradicts standard practices where JSON is wrapped in code fences for readability.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (line 339)
   - **Suggestion**: Clarify the output format expectation
   - **Decision**: Reject
   - **Reasoning**: The instruction is intentionally strict to ensure parseable JSON output. The consuming Python code uses JSON parsing, not markdown parsing. The "no markdown fences" instruction prevents parsing errors.

7. **Missing Guidance on Trace Log Detail Level**
   - **Description**: Work Step 2 mentions recording decisions in trace.sections, but doesn't specify the expected level of detail for h3_split_reason.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (lines 74-89)
   - **Suggestion**: Add guidance on trace detail level
   - **Decision**: Defer to Future
   - **Reasoning**: The examples provide sufficient guidance. Trace logs are for debugging, not user-facing. Can standardize format if trace analysis becomes important.

8. **Vague Validation Instructions in content_check.md**
   - **Description**: V2 validation says "For each paragraph in knowledge, trace to source" but doesn't specify what constitutes a "paragraph" in JSON-formatted knowledge content.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/content_check.md` (lines 38-46)
   - **Suggestion**: Clarify what constitutes a "paragraph"
   - **Decision**: Defer to Future
   - **Reasoning**: The validation logic is based on semantic review by AI agents who understand context. Over-specifying "paragraph" definition may reduce flexibility. Can clarify if validation quality issues emerge.

### Low Priority

9. **Repetitive Heading Explanation in generate.md**
   - **Description**: Step 2-1 and Step 2-2 repeat RST heading format explanations.
   - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md`
   - **Suggestion**: Add cross-reference instead of repeating
   - **Decision**: Reject
   - **Reasoning**: Repetition ensures each work step is self-contained and can be understood without scrolling. Slight redundancy improves usability.

10. **Missing Example for Complex Cross-Reference Case**
    - **Description**: Work Step 4 covers cross-reference conversion logic well, but lacks an example showing a complex case with nested internal/external references.
    - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (lines 184-215)
    - **Suggestion**: Add example with mixed references
    - **Decision**: Defer to Future
    - **Reasoning**: The current examples cover the most common cases. Complex nested references are rare in Nablarch docs. Can add if needed based on actual conversion results.

11. **No Guidance on Handling Unexpected Patterns**
    - **Description**: classify_patterns.md doesn't specify how to handle documents that mention patterns not in the valid pattern list.
    - **Location**: `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/classify_patterns.md` (lines 16-30)
    - **Suggestion**: Add guidance for unexpected patterns
    - **Decision**: Reject
    - **Reasoning**: The prompt clearly lists valid patterns (line 16). The instruction to "identify which patterns apply" implicitly means only from the valid list. Additional clarification is unnecessary.

12. **Trailing Backticks in Original Files**
    - **Description**: Lines 340, 417, 464, 524 in generate.md show trailing markdown markers that appear to be artifacts.
    - **Location**: Multiple locations in all prompt files
    - **Suggestion**: Clarify whether these are intentional delimiters
    - **Decision**: Reject
    - **Reasoning**: These are not artifacts - they are closing markers for markdown code fences in the examples. They are intentional and necessary for proper markdown formatting.

---

## Positive Aspects

- **Excellent work step decomposition**: The generate.md prompt breaks down a complex conversion task into 7 clear, sequential steps. Each step has a well-defined input and output.

- **Strong priority guidance**: The extraction priority table (lines 96-104 in generate.md) clearly establishes the principle "redundant is better than missing," which is crucial for knowledge extraction quality.

- **Comprehensive validation categories**: content_check.md separates validation into 4 distinct categories (V1-V4) with clear severity levels, making it easy to prioritize fixes.

- **Good use of examples**: generate.md provides concrete examples for markdown conversion patterns (classes, modules, properties, alerts) that eliminate ambiguity.

- **Clear role separation**: Each prompt has a distinct, well-defined role (generator, validator, fixer, classifier) with explicit boundaries (e.g., "Do NOT fix anything" in content_check.md).

- **Practical decision criteria**: The "Can I point to a specific passage in the source?" test (line 123 in generate.md, line 46 in content_check.md) provides a concrete, actionable guideline for avoiding fabrication.

- **Pattern matching table**: classify_patterns.md uses a clear indicator table that makes pattern detection deterministic and auditable.

---

## Recommendations

1. **Schema Management**: Consider extracting all JSON schemas to separate schema files (e.g., `schemas/knowledge-file.schema.json`) and referencing them in prompts. This ensures consistency and enables programmatic validation.

2. **Error Recovery Guidance**: Add sections describing how agents should handle unexpected situations (malformed input, missing metadata, ambiguous content). Current prompts assume well-formed inputs.

3. **Quality Metrics**: Consider adding a section in generate.md that defines quality metrics agents should self-evaluate (e.g., "Aim for 0 fabrications, <5% section size variance from source").

4. **Versioning**: If these prompts will evolve, add version numbers or timestamps to track which prompt version generated which knowledge files.

5. **Cross-Prompt Consistency**: Ensure terminology is consistent across prompts. For example, generate.md uses "section_id" while other prompts might reference "section ID" - standardize formatting.

6. **Testing Guidance**: Consider adding a section with test cases or examples of typical source files agents should practice on before processing real documentation.

---

## Files Reviewed

- `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/generate.md` (documentation conversion prompt - 524 lines)
- `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/content_check.md` (validation prompt - 176 lines)
- `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/fix.md` (fixing prompt - 38 lines)
- `/home/tie303177/work/nabledge/work1/tools/knowledge-creator/prompts/classify_patterns.md` (pattern classification prompt - 53 lines)
