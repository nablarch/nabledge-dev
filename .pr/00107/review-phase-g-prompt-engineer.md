# Expert Review: Prompt Engineering

**Date**: 2026-03-03
**Reviewer**: AI Agent as Prompt Engineering Expert
**Files Reviewed**: 2 files (prompts/generate.md, steps/phase_g_resolve_links.py)

## Overall Assessment

**Rating**: 4/5

**Summary**: The changes implement a clear separation between initial RST-to-Markdown conversion (Phase B) and link resolution (Phase G). The approach is sound - preserving original RST syntax during initial conversion and mechanically resolving links afterward. The prompts are mostly clear with good examples, but there are areas where ambiguity could cause agent confusion during execution.

## Key Issues

### High Priority

1. **Inconsistent :java:extdoc: handling between phases**
   - Description: Work Step 4 in Phase B still converts :java:extdoc: to inline code `ClassName`, but Phase G's implementation suggests it should be preserved and resolved later. The prompt says "KEEP THE ORIGINAL RST SYNTAX" but then contradicts this by still doing URL extraction and inline code conversion.
   - Suggestion: Clarify whether :java:extdoc: is handled in Phase B or Phase G. If Phase G should handle it, remove the conversion logic from Phase B Step 4. If Phase B handles it, remove :java:extdoc: from Phase G's scope.
   - Decision: Implement Now (clarify prompt)

2. **Missing guidance on malformed RST syntax**
   - Description: The prompt doesn't tell the agent what to do if RST syntax is malformed, incomplete, or uses unexpected patterns (e.g., :ref:\`label\` without closing backtick, nested references, etc.)
   - Suggestion: Add a fallback rule: "If RST syntax is malformed or unrecognized, preserve it as-is and log a warning. Phase G will report unresolved references."
   - Decision: Implement Now (add fallback rule)

### Medium Priority

3. **Unclear "official_doc_urls" collection timing**
   - Description: Step 4 mentions "collected in Step 6" for official_doc_urls, but Step 6 doesn't exist in the shown context. This forward reference is confusing.
   - Suggestion: Either show Step 6's content, or rephrase to: "Add this URL to the official_doc_urls list (to be collected in the final metadata step)" or remove the parenthetical entirely.
   - Decision: Defer (minor wording issue)

4. **No examples of edge cases in preservation instructions**
   - Description: The prompt shows straightforward examples but doesn't show edge cases like references with multiple angle brackets, special characters in paths, nested or malformed references.
   - Suggestion: Add a subsection "Edge Cases to Preserve" with 2-3 examples of unusual but valid RST patterns to reinforce the "preserve as-is" principle.
   - Decision: Defer (nice-to-have)

5. **Missing context about {INTERNAL_LABELS} data structure**
   - Description: Step 4.3 references `{INTERNAL_LABELS}` but doesn't explain where this comes from, what format it's in, or how it's populated.
   - Suggestion: Add a brief note: "{INTERNAL_LABELS} is the set of label→section-id mappings from Step 2 (section ID normalization). It contains only labels found within the current document."
   - Decision: Defer (context exists elsewhere in prompt)

6. **Ambiguous "section text" terminology**
   - Description: The phrase "In section text, KEEP THE ORIGINAL RST SYNTAX" appears multiple times, but "section text" isn't formally defined.
   - Suggestion: Define at the start of Step 4: "In this step, 'section text' refers to section.content (the body of the section, excluding the title and metadata)."
   - Decision: Defer (clear from context)

### Low Priority

7-9: Formatting consistency, performance notes, verification step - all marked Defer

## Positive Aspects

- Clear separation of concerns: The two-phase approach (preserve then resolve) is architecturally sound and makes the process testable.
- Comprehensive examples: The prompt includes good examples of each RST directive type with realistic Nablarch patterns.
- Explicit preservation principle: The repeated "KEEP THE ORIGINAL RST SYNTAX" makes the intent very clear.
- Test coverage: The companion test file (test_phase_g.py) covers all major link types.
- Handling of label variants: The implementation smartly handles underscore/hyphen variations.
- External URL handling: Clear distinction between external URLs (convert immediately) and internal references (preserve for Phase G).

## Recommendations

1. Add a decision matrix showing "RST Pattern → Phase B Action → Phase G Action" for each directive type
2. Include validation criteria specifying what "successfully resolved" means for each link type
3. Add troubleshooting section with common failure modes
4. Clarify agent roles if this prompt is used by multiple agents
5. Consider adding Phase G examples to Phase B prompt
