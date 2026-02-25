# Improvement Evaluation

**Date**: 2026-02-25
**Evaluator**: Developer (AI Agent)
**Context**: PR #88 - index.toon redesign prototype (11/93 entries)

## Summary

- **Implement Now**: 5 issues
- **Defer to Future**: 6 issues
- **Reject**: 0 issues

## Detailed Decisions

### Prompt Engineer Issues

#### PE-1: Ambiguous Keyword Extraction Guidance (Medium)
- **Suggestion**: Add explicit heuristics for L2/L3 extraction (technical nouns, synonyms, fallback to intent-search)
- **Decision**: **Implement Now**
- **Reasoning**: Valid suggestion. The extraction process is currently implicit, which could lead to inconsistent behavior. Adding explicit heuristics (4-5 lines) improves agent clarity without scope creep. The fallback to intent-search is especially valuable for truly ambiguous queries. Low effort, high impact on consistency.

#### PE-2: Batch Script Variable Initialization Missing (Medium)
- **Suggestion**: Move variable definition note before the script or integrate into script example
- **Decision**: **Implement Now**
- **Reasoning**: Valid. Current script shows usage of `l2_keywords` and `l3_keywords` arrays without initialization, which is confusing. Adding 2-3 lines of initialization makes the script immediately executable. This is documentation clarity, not feature addition. Minimal effort, prevents copy-paste errors.

#### PE-3: Section-Level Scoring Inconsistency (Medium)
- **Suggestion**: Add clarification in script comments explaining why L3 weighted equal to L2 at section level
- **Decision**: **Implement Now**
- **Reasoning**: Valid. The scoring is actually consistent, but the comment could be clearer about the rationale. Adding 1-2 lines of clarification (why L3=2 at section level) improves maintainability. This is a documentation fix, not logic change. Trivial effort.

#### PE-4: Error Handling Incomplete (Medium)
- **Suggestion**: Add error handling guidance for JSON parsing errors and missing files
- **Decision**: **Implement Now**
- **Reasoning**: Valid and important. Real-world robustness requires handling jq failures and missing files. Adding 2-3 sentences to error handling section (lines 179-186) is appropriate for this prototype PR. These are documented guidelines, not complex implementation. The workflow already has an error handling section, this extends it naturally.

#### PE-5: Example Execution Could Show Full Flow (Low)
- **Suggestion**: Add "User receives" section showing actual answer format
- **Decision**: **Defer to Future**
- **Reasoning**: Valuable but out of scope. The workflow focuses on search mechanics (finding relevant content). User-facing output format belongs in the main SKILL.md or a separate response formatting workflow. This prototype validates search accuracy, not output formatting. Future work can address end-to-end user journey documentation.

#### PE-6: Index.toon Prototype Comment Verbosity (Low)
- **Suggestion**: Move detailed design explanation to separate document, keep brief reference comment
- **Decision**: **Defer to Future**
- **Reasoning**: Current verbosity is intentional for prototype phase. The extensive comments (lines 3-21) aid human reviewers understanding the OLD→NEW transformation. Once full migration is complete (all 93 entries), cleanup makes sense. Premature optimization for this prototype. Defer until full migration PR.

#### PE-7: Scoring Threshold Documentation Could Be Clearer (Low)
- **Suggestion**: Clarify threshold logic more mathematically (≥2 could be 1 L2 OR 2 L3 OR mixed)
- **Decision**: **Defer to Future**
- **Reasoning**: Current explanation (lines 230-232) is functional and accurate enough for prototype validation. The suggested mathematical precision ("typical: 1 L2 match, or 2 L3 matches, or mixed") is valuable but not critical for this PR. Low priority documentation polish. Defer to documentation consolidation task (see SE Low-1).

### Software Engineer Issues

#### SE-High-1: Incomplete Prototype Coverage (High)
- **Suggestion**: Complete migration of all 93 entries to ensure consistent search behavior
- **Decision**: **Defer to Future**
- **Reasoning**: **This is the prototype validation PR**. Success criteria explicitly states:
  - [x] Prototype created: 5-10 entries redesigned (DONE: 11 entries)
  - [ ] Full migration: All 93 entries (separate work)

  The benchmark validates the design with zero false positives. The purpose of THIS PR is to validate the approach before committing to full migration effort (82 remaining entries). Full migration is tracked as separate task and should be a separate PR after this prototype is approved. Completing all 93 entries here would be scope creep and defeats the incremental validation strategy.

#### SE-High-2: Hard-coded Scoring Logic in Workflow (High)
- **Suggestion**: Extract scoring configuration to separate JSON file or workflow header section
- **Decision**: **Defer to Future**
- **Reasoning**: Valid architectural suggestion but over-engineering for current needs. The scoring weights (+2/+1 for L2, +2 for L3 at section level) are stable design decisions validated by benchmark. No evidence of need for A/B testing or frequent tuning. Adding configuration infrastructure (JSON file, parsing logic) adds complexity without proven benefit. If scoring needs to change in future (based on production data), this can be refactored then. YAGNI principle applies.

#### SE-Med-1: Bash Script Robustness (Medium)
- **Suggestion**: Add explicit initialization example and error handling (array declaration, keyword validation)
- **Decision**: **Implement Now**
- **Reasoning**: Same as PE-2. Adding `declare -a` initialization and basic validation (`if [ ${#l2_keywords[@]} -eq 0 ]`) makes the script self-contained and executable. This is workflow documentation improvement, not feature change. The error check prevents silent failures when keyword extraction fails. Low effort, high value for real-world robustness.

#### SE-Med-2: Inconsistent English Title Conventions (Medium)
- **Suggestion**: Establish and document English title convention rules (PascalCase, compound terms)
- **Decision**: **Implement Now**
- **Reasoning**: Valid and timely. Adding 3-5 lines to index.toon header documenting conventions (PascalCase for classes, clear word boundaries) improves consistency NOW before migrating remaining 82 entries. This is preventive documentation that pays off during full migration. Minimal effort, scales impact across future entries.

#### SE-Med-3: Missing Validation Test Suite (Medium)
- **Suggestion**: Create validation script to enforce L2+title format and detect regressions
- **Decision**: **Defer to Future**
- **Reasoning**: Valuable but premature. With only 11 prototype entries, manual review is sufficient. The validation script becomes valuable during/after full migration (93 entries). Creating test infrastructure now adds effort without immediate benefit. Defer until full migration PR where it can be built alongside the migration work and immediately provide value.

#### SE-Low-1: Documentation Redundancy (Low)
- **Suggestion**: Consolidate scoring strategy rationale in one authoritative document
- **Decision**: **Defer to Future**
- **Reasoning**: Valid DRY principle but low priority. Current redundancy (workflow, notes.md, comparison.md) reflects organic development where design rationale appeared in natural contexts. Consolidation is valuable cleanup but not critical for prototype validation. This is documentation refactoring that can be done post-merge or during full migration PR.

#### SE-Low-2: Example Scenario Coverage (Low)
- **Suggestion**: Add edge case scenarios (lowercase, typos, English-only, Japanese-only queries)
- **Decision**: **Defer to Future**
- **Reasoning**: Valid but out of scope for prototype validation. The 8 existing scenarios validate core design (zero false positives achieved). Edge case testing (typos, case sensitivity) is valuable for production hardening but not required to validate the L2+title design approach. Defer to post-migration testing phase or separate robustness improvement task.

#### SE-Low-3: Performance Metrics Missing (Low)
- **Suggestion**: Add timing measurements to benchmark (execution time, memory usage)
- **Decision**: **Defer to Future**
- **Reasoning**: Valid but not critical. The tool call reduction (10-15 → 1) is already documented and qualitatively significant. Quantitative timing/memory benchmarks are valuable for optimization discussions but don't affect prototype validation decision. The design is sound based on precision metrics. Performance profiling can be done post-merge if performance issues emerge in production.

## Implementation Plan

### Implement Now (5 issues)

#### 1. PE-1: Keyword Extraction Heuristics
**Files**: `.claude/skills/nabledge-6/workflows/keyword-search.md`
**Location**: Add after line 59 (in Step 1 section)
**Changes**:
```markdown
**Extraction process**:
1. **Technical terms**: Identify API names, framework components, file formats (e.g., DAO, CSV, 二重サブミット防止)
2. **Synonyms**: Expand with known variations (DAO → O/Rマッパー, CSV → TSV)
3. **Language variations**: Include both Japanese and English terms (ページング, paging)
4. **Fallback**: If no clear L2 keywords found, use intent-search workflow instead
```
**Effort**: 5 minutes

#### 2. PE-2 + SE-Med-1: Batch Script Initialization (Combined)
**Files**: `.claude/skills/nabledge-6/workflows/keyword-search.md`
**Location**: Lines 84-86 (before script begins)
**Changes**:
```bash
# Initialize keyword arrays from Step 1
declare -a l2_keywords=("DAO" "UniversalDao" "O/Rマッパー")
declare -a l3_keywords=("ページング" "paging" "per" "page" "limit" "offset")

# Validate keywords exist
if [ ${#l2_keywords[@]} -eq 0 ] && [ ${#l3_keywords[@]} -eq 0 ]; then
  echo "Error: No keywords extracted. Check Step 1." >&2
  exit 1
fi

# Batch extract .index from all selected files
for file in knowledge/features/libraries/universal-dao.json \
...
```
**Effort**: 5 minutes

#### 3. PE-3: Section Scoring Rationale Clarification
**Files**: `.claude/skills/nabledge-6/workflows/keyword-search.md`
**Location**: Line 107-109 (in script comments)
**Changes**:
```bash
# L3 keywords matching (+2 points each at section level)
# Rationale: At section level, functional terms (L3) are as specific as technical terms (L2)
# Both equally indicate section relevance, unlike file level where L2 is more discriminative
```
**Effort**: 2 minutes

#### 4. PE-4: Error Handling Extension
**Files**: `.claude/skills/nabledge-6/workflows/keyword-search.md`
**Location**: Lines 179-186 (extend error handling section)
**Changes**:
```markdown
**JSON parsing errors**: If jq fails on a file (malformed JSON), log warning and skip that file. Continue processing remaining files. Report affected file path to user.

**Missing files**: If a file path in index.toon doesn't exist, log error and notify user to report the issue (potential sync problem between index.toon and knowledge/).

**Silent failures**: Never silently ignore errors. All error conditions should produce user-visible messages or logs.
```
**Effort**: 5 minutes

#### 5. SE-Med-2: English Title Conventions
**Files**: `.claude/skills/nabledge-6/knowledge/index.toon`
**Location**: Lines 3-21 (add to header comment section)
**Changes**:
```
# English Title Conventions:
# - PascalCase for class/component names: UniversalDao, DatabaseAccess, SessionStore
# - Clear word boundaries in compounds: JDBCWrapper (not Jdbcwrapper)
# - Match official Nablarch naming where possible
# - Use common English terms for concepts: Transaction, Validation, Handler
```
**Effort**: 3 minutes

### Total Implementation Effort: ~20 minutes

### Defer to Future (6 issues)

#### Post-Merge / Full Migration PR
1. **SE-High-1**: Complete all 93 entries migration
   - Tracking: Already in success criteria as separate task
   - Estimated effort: 4-6 hours (82 remaining entries)
   - Dependencies: Prototype approval (this PR)

2. **SE-Med-3**: Validation test suite
   - Tracking: Create GitHub issue "Add index.toon validation test suite"
   - Implementation: During or after full migration PR
   - Dependencies: Full migration completion (benefits from complete dataset)

3. **PE-6**: Clean up prototype comments
   - Tracking: Part of full migration PR
   - Action: Replace verbose OLD/NEW comments with brief format notes
   - Dependencies: Full migration completion

#### Documentation Improvements
4. **PE-5**: End-to-end example with user output
   - Tracking: Create GitHub issue "Document user-facing output format"
   - Action: Add to SKILL.md or create separate response-formatting workflow
   - Dependencies: None (can be done independently)

5. **SE-Low-1**: Consolidate scoring rationale documentation
   - Tracking: Create GitHub issue "Consolidate search design documentation"
   - Action: Create `doc/search-design.md` as single source of truth
   - Dependencies: None (documentation refactoring)

#### Production Hardening (After Production Use)
6. **SE-Low-2**: Edge case scenario testing
   - Tracking: Create GitHub issue "Add edge case tests for search workflow"
   - Action: Expand benchmark with 5-10 edge cases (typos, case sensitivity, etc.)
   - Dependencies: Real user query data would inform test case selection

#### Performance Optimization (If Needed)
7. **SE-Low-3**: Performance benchmarking
   - Tracking: Create GitHub issue "Measure search workflow performance"
   - Action: Add timing/memory measurements to benchmark suite
   - Dependencies: Production deployment (need real-world data to validate benefit)

#### Architecture (YAGNI Unless Proven)
8. **SE-High-2**: Extract scoring configuration
   - Tracking: Create GitHub issue "Consider scoring configuration externalization"
   - Action: Monitor if scoring needs frequent tuning in production
   - Dependencies: Evidence of need from production usage

## Rejected Issues

None. All suggestions have merit; timing/scope determines Implement vs Defer.

## Next Steps

1. **Implement 5 issues** (estimated 20 minutes)
2. **Run benchmark again** to verify no regressions
3. **Update this document** with implementation results
4. **Create GitHub issues** for deferred items
5. **Proceed to PR creation** per `/hi` workflow
