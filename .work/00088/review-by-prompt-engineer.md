# Expert Review: Prompt Engineer

**Date**: 2026-02-25
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4.5/5
**Summary**: Excellent workflow clarity and structure with comprehensive examples. The L2+title redesign is well-documented and logically sound. Minor improvements needed in agent behavior guidance and error handling edge cases.

## Key Issues

### High Priority

None identified. All critical aspects of the workflow are clear and actionable.

### Medium Priority

#### 1. **Ambiguous Keyword Extraction Guidance**
   - **Description**: Step 1 states "Extract keywords from the user request at two levels" but doesn't provide clear guidelines for HOW to extract them. The agent might struggle with ambiguous queries like "データを処理したい" (no obvious L2 keywords).
   - **Location**: `keyword-search.md` lines 43-59
   - **Suggestion**: Add explicit extraction heuristics:
     ```markdown
     **Extraction process**:
     1. Identify technical nouns (API names, framework terms, file formats)
     2. Expand with synonyms (DAO → O/Rマッパー, CSV → TSV)
     3. Include both Japanese and English variations
     4. If no L2 keywords found, fall back to intent-search workflow
     ```
   - **Decision**: Implement Now
   - **Reasoning**: Clear extraction rules prevent agent confusion and improve consistency across different queries.

#### 2. **Batch Script Variable Initialization Missing**
   - **Description**: Lines 122-126 show bash script using `l2_keywords` and `l3_keywords` arrays but these are only mentioned in a note after the script. An agent unfamiliar with bash might not understand they need to be defined first.
   - **Location**: `keyword-search.md` lines 84-126
   - **Suggestion**: Move the variable definition note BEFORE the script or integrate it into the script example:
     ```bash
     # Define keywords from Step 1
     l2_keywords=("DAO" "UniversalDao" "O/Rマッパー")
     l3_keywords=("ページング" "paging" "per" "page" "limit" "offset")

     # Batch extract .index from all selected files
     for file in knowledge/features/libraries/universal-dao.json \
     ...
     ```
   - **Decision**: Implement Now
   - **Reasoning**: Prevents execution errors and makes the script self-contained and immediately usable.

#### 3. **Section-Level Scoring Inconsistency**
   - **Description**: Lines 107-109 show L3 scoring as "+2 points" in the bash script, but line 130 text says "+2 points" for L3. However, line 222 in the scoring strategy table says L3 should be "+2" at section level. This is actually consistent, but the comment at line 107 says "+2 points each" which could be clearer about why L3 is weighted equally to L2 at section level.
   - **Location**: `keyword-search.md` lines 107-109, 128-136
   - **Suggestion**: Add clarification in the script comments:
     ```bash
     # L3 keywords matching (+2 points each at section level - equal to L2)
     # Rationale: At section level, functional terms are as specific as technical terms
     ```
   - **Decision**: Implement Now
   - **Reasoning**: Prevents confusion about scoring strategy and makes the rationale explicit in the code.

#### 4. **Error Handling Incomplete**
   - **Description**: Error handling section (lines 179-186) covers "no matches" and "too many candidates" but doesn't address what happens if jq fails (malformed JSON) or if a knowledge file is missing.
   - **Location**: `keyword-search.md` lines 179-186
   - **Suggestion**: Add error handling guidance:
     ```markdown
     **JSON parsing errors**: If jq fails, skip the file and log warning. Continue with remaining files.

     **Missing files**: If a file in index.toon doesn't exist, log error and notify user to report the issue.
     ```
   - **Decision**: Implement Now
   - **Reasoning**: Real-world robustness requires handling file system and parsing errors gracefully.

### Low Priority

#### 5. **Example Execution Could Show Full Flow**
   - **Description**: The example execution (lines 188-208) shows stages separately but doesn't demonstrate the complete end-to-end flow including what the user receives as final output.
   - **Location**: `keyword-search.md` lines 188-208
   - **Suggestion**: Add a final "User receives" section showing the actual answer format:
     ```markdown
     **User receives**:
     Based on ユニバーサルDAO's paging section:
     - API: `EntityList<Entity> entities = universalDao.page(1).per(20).findAll();`
     - Explanation: 検索結果のページングは...
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: While helpful for completeness, the workflow focuses on search mechanics. User-facing output format may belong in a separate documentation section.

#### 6. **Index.toon Prototype Comment Verbosity**
   - **Description**: The prototype section in `index.toon` (lines 3-21) has extensive comments explaining the format change. While helpful for understanding, this adds visual noise for agents reading the file during execution.
   - **Location**: `index.toon` lines 3-21
   - **Suggestion**: Consider moving detailed design explanation to a separate document (like the existing `index-redesign-proposal.md`) and keeping only a brief reference comment:
     ```
     # PROTOTYPE: L2+title hint design (11 entries)
     # See doc/mapping/index-redesign-proposal.md for design rationale
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: Current verbosity aids human reviewers during prototype phase. Can be cleaned up during full migration.

#### 7. **Scoring Threshold Documentation Could Be Clearer**
   - **Description**: Lines 230-232 explain thresholds (≥2 for file, ≥2 for section) but the rationale "ensures at least 1 L2 match" is slightly misleading since L3 could also contribute to reaching threshold 2.
   - **Location**: `keyword-search.md` lines 230-232
   - **Suggestion**: Clarify the logic:
     ```markdown
     **Threshold settings**:
     - File selection: ≥2 points (typical: 1 L2 match, or 2 L3 matches, or mixed)
     - Section selection: ≥2 points (same logic)
     - Rationale: Prevents pure single-keyword noise matches
     ```
   - **Decision**: Defer to Future
   - **Reasoning**: Current explanation is functional but could be mathematically more precise. Low priority as it doesn't affect execution.

## Positive Aspects

### 1. Excellent Structure and Clarity
The workflow document follows a clear, logical progression:
- Table of Contents with anchor links
- Overview section with role, input/output, and tool expectations
- Step-by-step process with tool specifications
- Error handling and examples
- Comprehensive notes section

**Strength**: Agent can quickly navigate and understand their role.

### 2. Concrete, Executable Examples
The workflow provides specific examples:
- Line 52: Concrete query example with extracted keywords
- Lines 84-120: Full bash script with actual file paths
- Lines 188-208: Step-by-step execution trace

**Strength**: Agent can copy and adapt examples directly, reducing ambiguity.

### 3. Design Rationale Documented
The workflow doesn't just say "do this" but explains WHY:
- Line 73-74: Why L2 weighted higher than L3
- Lines 217-228: Full scoring strategy rationale table
- Lines 230-232: Threshold reasoning
- Lines 235-238: Why L2+title design chosen

**Strength**: Agent (and future maintainers) understand the intent, enabling better decision-making in edge cases.

### 4. Multi-Stage Validation
The prototype underwent rigorous validation:
- 8 test scenarios with detailed results (comparison.md)
- Zero false positives demonstrated
- 81.8% prototype entry coverage verified
- Clear metrics: 58-67% file reduction

**Strength**: High confidence in design quality before full rollout.

### 5. Tool Usage Optimization
The workflow explicitly mentions tool call reduction:
- Line 31: "3-5 calls (reduced from 10-15 via batch processing)"
- Lines 141-143: Key advantages of batch processing listed
- Lines 84-120: Single batch script replacing multiple calls

**Strength**: Performance-conscious design that will improve user experience.

### 6. Error Handling Guidance
Clear guidance on what to do when things go wrong:
- Lines 179-186: Three error scenarios covered
- Line 185: Explicit "DO NOT answer from LLM training data" warning

**Strength**: Prevents common failure modes and maintains knowledge fidelity.

### 7. Prototype Implementation Strategy
Smart incremental approach:
- 11 entries as prototype (not all 93)
- Diverse selection across categories (libraries, handlers, batch)
- Clear documentation of OLD vs NEW format for each entry

**Strength**: Low-risk validation before full migration.

## Recommendations

### For Immediate Implementation

1. **Add keyword extraction heuristics** (Medium Priority #1)
   - Prevents agent confusion on ambiguous queries
   - Improves consistency

2. **Fix batch script variable initialization** (Medium Priority #2)
   - Ensures script is immediately executable
   - Prevents runtime errors

3. **Clarify section-level scoring rationale** (Medium Priority #3)
   - Makes scoring strategy fully transparent
   - Aids debugging

4. **Expand error handling coverage** (Medium Priority #4)
   - Handles real-world failure cases
   - Improves robustness

### For Future Consideration

1. **Add end-to-end example** (Low Priority #5)
   - Shows complete user journey
   - Could be separate documentation

2. **Clean up index.toon comments post-migration** (Low Priority #6)
   - Reduces visual noise
   - Appropriate after validation

3. **Refine threshold documentation** (Low Priority #7)
   - Mathematical precision
   - Low impact on execution

### Testing and Validation

Before full migration to 93 entries:
1. Test all 4 medium-priority improvements with existing scenarios
2. Add 2-3 additional test cases focusing on:
   - Ambiguous queries (no clear L2 keywords)
   - Error conditions (missing files, malformed JSON)
   - Edge case scoring (L3-only matches)

### Documentation

Consider creating a companion guide:
- "How to write effective index.toon hints"
- "Keyword extraction best practices"
- "Troubleshooting search accuracy issues"

This would help maintainers add new knowledge files with consistent quality.

## Conclusion

This is a high-quality workflow redesign with strong prompt engineering fundamentals:
- Clear instructions that guide agent behavior effectively
- Concrete examples that reduce ambiguity
- Well-reasoned design decisions with documented rationale
- Comprehensive validation with measurable metrics

The medium-priority issues are primarily about edge case handling and clarity improvements. None are blockers for the prototype phase. Implementing the 4 medium-priority suggestions will bring this to a 5/5 rating and ensure robustness for production use.

**Recommendation**: Proceed with prototype validation after addressing medium-priority issues. Full migration approved pending successful test results.
