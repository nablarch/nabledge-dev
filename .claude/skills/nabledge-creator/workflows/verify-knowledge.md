# Knowledge File Verification Workflow

Verify the quality of generated knowledge files. Run this workflow in a **separate session** from the generation workflow.

**IMPORTANT**: Run this workflow in a **separate session** from the generation workflow. This prevents context bias where generation decisions influence verification judgment.

## Invocation

```
nabledge-creator verify-knowledge {version} --all
```

Where `{version}` is the Nablarch version number (e.g., `6` for v{version}, `5` for v5).

## Progress Checklist Template

```
## nabledge-creator verify-knowledge {version} - Progress

□ Step VK1: Read Input Files
□ Step VK2: Verify All Knowledge Files
□ Step VK3: Verify index.toon Integration
□ Step VK4: Categorize Issues
□ Step VK5: Document Verification Results

**Started:** [timestamp]
**Status:** Not started
```

## Why Separate Session?

The generation session makes decisions about "what to include." The verification session makes decisions about "what is missing." Running both in the same session causes the verification to be biased by generation logic, leading to overlooked issues.

## Workflow Steps

### Step VK1: Read Input Files

Read the following files:

```
.claude/skills/nabledge-creator/output/mapping-v{version}.md       # Source to knowledge file mapping
.claude/skills/nabledge-creator/references/knowledge-schema.md     # JSON schema specification
.claude/skills/nabledge-{version}/knowledge/*.json                 # Generated knowledge files
```

**Note**: Use mapping file as the source of truth for RST file locations and knowledge file paths. knowledge-file-plan.md is for reference only (統合パターンと方針).

### Step VK2: Verify All Knowledge Files (Batch Processing with Task Tool)

**Batch Processing Strategy**: Use Task tool to process files in category-based batches to avoid context overflow.

#### Step VK2.1: Group Files by Category

List generated JSON files grouped by category:

```bash
find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | sort
```

Create batches (same as knowledge Step 2):
- Categories with >60 files: Split into 2 batches
- Categories with ≤60 files: 1 batch per category
- Save to `.tmp/nabledge-creator/verify-knowledge-batches-v{version}.json`

#### Step VK2.2: Launch Task Agents (Parallel)

For each batch, launch a Task agent in parallel:

```
Task (parallel × N batches)
  subagent_type: "general-purpose"
  description: "Verify knowledge: {category} batch {n}"
  prompt: "You are verifying knowledge files for Nablarch v{version} documentation.

## Your Assignment

**Batch ID**: {batch_id}
**Category**: {type}/{category}
**Files**: {count} JSON files

## Input Files

Read these files first:
1. Mapping file: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`
2. Schema: `.claude/skills/nabledge-creator/references/knowledge-schema.md`

Your batch's JSON files (in `.claude/skills/nabledge-{version}/knowledge/`):
{list of JSON file paths}

## Your Task

For each JSON file in your batch:

### 2.1 Read Source RST Documentation

- Locate source RST file(s) from mapping-v{version}.md (Source Path column)
- Read complete RST content from `.lw/nab-official/v{version}/`
- Understand feature/component purpose and usage

### 2.2 Verify Schema Compliance

Check JSON file against knowledge-schema.md:

- **Required fields**: All mandatory fields present (class_name, purpose, usage, etc.)
- **Section structure**: Sections follow schema templates for the category
- **Index hints**: Each section has L1/L2/L3 keywords in index array
- **Content format**: Text uses proper markdown, code blocks formatted correctly

### 2.3 Verify Content Accuracy

Compare JSON content against RST source:

- **Section division**: RST h2 headings → JSON sections (±30% section count acceptable)
- **Content correspondence**: Key information from RST appears in JSON
- **Technical terms**: Class names, properties, annotations accurately extracted
- **Code examples**: Sample code preserved where relevant
- **Specifications**: Directives, properties, exceptions documented

### 2.4 Verify Keyword Coverage

Evaluate index hints quality:

- **L1 keywords** (category/domain level): バッチ, データベース, Web, REST, etc.
- **L2 keywords** (feature/component level): Class names, concepts, technologies
- **L3 keywords** (detail level): Method names, property names, specific terms
- **Minimum requirements**: L1 ≥ 1, L2 ≥ 2 (per knowledge-schema.md)
- **Bilingual mix**: Japanese primary (user queries), English secondary (technical terms)

### 2.5 Verify MD Conversion

- Check MD file exists: Corresponding `.md` file in `docs/` directory
- Verify content preserved (spot check key sections)

### 2.6 Record Result

For each file, record:

```
File: {filename}
Source: {RST paths}

Schema Compliance: ✓/✗
- Required fields: ✓/✗ ({missing fields if any})
- Section structure: ✓/✗ ({issues if any})
- Index hints: ✓/✗ ({issues if any})

Content Accuracy: ✓/⚠/✗
- Section division: ✓/⚠ ({RST h2 count} → {JSON section count})
- Content correspondence: ✓/⚠/✗ ({missing key concepts if any})
- Technical terms: ✓/✗ ({inaccuracies if any})

Keyword Coverage: ✓/⚠/✗
- L1 keywords: {count} ({list})
- L2 keywords: {count} ({list})
- L3 keywords: {count} ({list})
- Missing important keywords: {list if any}

MD Conversion: ✓/✗
- MD file exists: ✓/✗
- Content preserved: ✓/✗ ({missing content if any})

Overall Status: ✓ PASS / ⚠ PASS WITH WARNINGS / ✗ FAIL
Issues: {list critical issues}
```

## Output

After completing all files in your batch:

**Report completion**:
```
Batch {batch_id} complete:
- Files verified: {count}/{count}
- PASS: {pass_count}
- PASS WITH WARNINGS: {warning_count}
- FAIL: {fail_count}
- Schema violations: {schema_violations}
- Content accuracy issues: {content_issues}
- Keyword coverage issues: {keyword_issues}
```

**Update progress file**:
Write to `.tmp/nabledge-creator/verify-knowledge-progress-v{version}.json`:
```json
{
  \"batch_id\": \"{batch_id}\",
  \"status\": \"complete\",
  \"verified\": {count},
  \"pass\": {pass_count},
  \"warnings\": {warning_count},
  \"fail\": {fail_count},
  \"schema_violations\": [{\"file\": \"path\", \"issue\": \"description\"}],
  \"content_issues\": [{\"file\": \"path\", \"issue\": \"description\"}],
  \"keyword_issues\": [{\"file\": \"path\", \"issue\": \"description\"}]
}
```

## Important Notes

- Verify ALL files in your batch
- Read complete RST source for accurate verification
- Focus on user perspective: Can users find what they need?
- Schema violations are critical - must be fixed
- Keyword coverage affects search functionality
"
  run_in_background: false
```

Launch all batches in parallel (use multiple Task calls in one message).

#### Step VK2.3: Run MD Conversion Verification (After All Batches)

After all Task agents complete, run automated MD conversion check:

```bash
python scripts/verify-json-md-conversion.py .claude/skills/nabledge-{version}/knowledge/ .claude/skills/nabledge-{version}/docs/
```

#### Step VK2.4: Verify Completion

```bash
# Count total JSON files
TOTAL=$(find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | wc -l)

# Sum verified from progress files
VERIFIED=$(jq -s 'map(.verified) | add' .tmp/nabledge-creator/verify-knowledge-progress-v{version}.json)

# Count issues
SCHEMA_VIOLATIONS=$(jq -s 'map(.schema_violations | length) | add' .tmp/nabledge-creator/verify-knowledge-progress-v{version}.json)
CONTENT_ISSUES=$(jq -s 'map(.content_issues | length) | add' .tmp/nabledge-creator/verify-knowledge-progress-v{version}.json)

echo "Total JSON files: $TOTAL"
echo "Files verified: $VERIFIED"
echo "Schema violations: $SCHEMA_VIOLATIONS"
echo "Content accuracy issues: $CONTENT_ISSUES"
```

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Total JSON files | [count from knowledge dir] | [find ... \| wc -l] | ✓ |
| Files verified | [total JSON files] | [sum from progress files] | ✓/✗ |
| Task agents launched | [batches count] | [count] | ✓ |
| All batches complete | Yes | [check progress files] | ✓/✗ |
| Schema violations | 0 | [sum from progress files] | ✓/✗ |
| Content accuracy | All pass | [issues count] | ✓/✗ |
| MD conversion | All pass | [verify-json-md exit code] | ✓/✗ |

**How to measure:**
- Total JSON files: `find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | wc -l`
- Files verified: Sum of "verified" from all progress files
- All batches complete: All progress files have "status": "complete"
- Issues: Sum from all progress files by category
- MD conversion: Exit code from verify-json-md-conversion.py (0=pass, 1=fail)

### Step VK3: Verify index.toon Integration

Verify that knowledge files are properly integrated into index.toon.

#### VK3.1 File-Level Hints Verification

For each verified knowledge file:

1. **Read JSON index arrays**
   - Collect all hints from `index[].hints` across all sections
   - Identify L1/L2/L3 keywords present

2. **Find corresponding index.toon entry**
   - Search index.toon by title (should match JSON title)
   - Verify entry exists

3. **Compare hints**
   - index.toon hints should be aggregation of JSON index hints
   - Verify L1/L2 coverage in index.toon hints
   - Check bilingual mix (Japanese + English technical terms)

4. **Verify path field**
   - path should be actual file path (e.g., `features/libraries/universal-dao.json`)
   - Should NOT be "not yet created" for verified files

5. **Record issues**:
   ```
   File: {filename}
   index.toon entry: FOUND / MISSING
   Hints aggregation: ✓ / ⚠ / ✗
   - Missing L1 keywords: {list}
   - Missing L2 keywords: {list}
   - Poor bilingual mix: {details}
   Path field: ✓ CORRECT / ✗ INCORRECT ({actual value})
   ```

#### VK3.2 index.toon Format Validation

Run format validation:

```bash
python scripts/validate-index.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

Check:
- Schema compliance (header, field structure)
- Entry completeness (no empty titles/hints)
- No duplicates
- Japanese lexical sorting

#### VK3.3 index.toon Status Consistency

Run status consistency check:

```bash
python scripts/verify-index-status.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

Verify:
- All indexed files exist (paths in index.toon → actual .json files)
- All actual files are indexed (actual .json files → entries in index.toon)
- No orphaned files or missing entries

#### VK3.4 Record index.toon Results

```
index.toon Verification Results:

Format Validation: ✓ PASS / ✗ FAIL
- Schema: ✓/✗
- Completeness: ✓/✗
- Duplicates: ✓/✗ ({count} if any)
- Sorting: ✓/✗

Status Consistency: ✓ PASS / ✗ FAIL
- Indexed files exist: ✓/✗ ({missing count} if any)
- All files indexed: ✓/✗ ({orphaned count} if any)

Hints Integration: ✓/⚠/✗
- Files with proper hints aggregation: {count}/{total}
- Files with missing L1 keywords: {count}
- Files with missing L2 keywords: {count}
- Files with poor bilingual mix: {count}

Overall: ✓ PASS / ⚠ PASS WITH WARNINGS / ✗ FAIL
```

### Step VK4: Categorize Issues

Group all issues found across all files by type:

**Schema Violations** (Critical - must fix):
- Missing required fields
- Invalid section structure
- Missing index arrays

**Content Gaps** (High Priority):
- Important RST content not reflected in JSON
- Missing technical terms or specifications
- Insufficient section coverage

**Keyword Deficiencies** (Medium Priority):
- Below minimum L1/L2 keyword count
- Missing important search terms
- Poor bilingual mix

**MD Conversion Issues** (Medium Priority):
- JSON content missing in MD files
- Incomplete conversion

**index.toon Integration Issues** (High Priority):
- Missing index.toon entries for knowledge files
- Incorrect path fields (orphaned or missing files)
- Poor hints aggregation (L1/L2 keywords missing)

### Step VK5: Document Verification Results

Create comprehensive verification report at `.pr/{issue_number}/knowledge-verification-results.md`:

```markdown
# Knowledge File Verification Results

**Date**: YYYY-MM-DD
**Files Verified**: All files (100% coverage)
**Verification Scope**: All knowledge files

## Summary

**Overall Status**: ✓ PASS / ⚠ PASS WITH WARNINGS / ✗ FAIL

**File-Level Results**:
- ✓ PASS: {count} files (no issues)
- ⚠ PASS WITH WARNINGS: {count} files (minor issues)
- ✗ FAIL: {count} files (critical issues)

**Issue Summary**:
- Schema violations: {count} files
- Content gaps: {count} files
- Keyword deficiencies: {count} files
- MD conversion issues: {count} files
- Search problems: {count} files

## Schema Compliance Verification

**Files with Schema Violations**: {count}

| File | Missing Fields | Structure Issues | Index Issues |
|------|----------------|------------------|--------------|
| {filename} | {list} | {description} | {description} |
| ... | ... | ... | ... |

## Content Accuracy Verification

**Files with Content Gaps**: {count}

| File | Section Coverage | Missing Content | Technical Term Issues |
|------|------------------|-----------------|----------------------|
| {filename} | {RST h2: X → JSON: Y} | {list} | {list} |
| ... | ... | ... | ... |

**Examples of Content Gaps**:

1. **{filename}**:
   - RST h2 "設定" discusses properties X, Y, Z
   - JSON missing property Z documentation
   - Impact: Users cannot find information about property Z

## Keyword Coverage Verification

**Files with Keyword Deficiencies**: {count}

| File | L1 Count | L2 Count | L3 Count | Missing Keywords |
|------|----------|----------|----------|------------------|
| {filename} | {count} | {count} | {count} | {list} |
| ... | ... | ... | ... | ... |

**Examples of Keyword Issues**:

1. **{filename}**:
   - Current L1 keywords: {list}
   - Current L2 keywords: {list}
   - Missing important terms: {list}
   - Reasoning: {why these keywords matter}

## MD Conversion Verification

**Files with MD Conversion Issues**: {count}

| File | MD File Exists | Missing Content | Status |
|------|----------------|-----------------|--------|
| {filename} | YES/NO | {list if any} | ✓/✗ |
| ... | ... | ... | ... |

**Examples of MD Conversion Issues**:

1. **{filename}**:
   - JSON content: {example text from JSON}
   - MD file: Missing this content
   - Impact: Documentation incomplete for users viewing MD files

## Search Functionality Verification

**Files with Search Problems**: {count}

| File | Expected Query | File Hit | Section Hit | Information |
|------|----------------|----------|-------------|-------------|
| {filename} | "{query}" | YES/NO | YES/NO | Sufficient/Insufficient |
| ... | ... | ... | ... | ... |

**Examples of Search Issues**:

1. **{filename}**:
   - Query: "データベース接続設定"
   - File hit: NO (missing "接続" in file-level hints)
   - Impact: Users searching for connection configuration won't find this file

## Category Breakdown

### Adapters
- ✓ PASS: {count}
- ⚠ WARNINGS: {count}
- ✗ FAIL: {count}
- Key issues: {summary}

### Handlers
- ✓ PASS: {count}
- ⚠ WARNINGS: {count}
- ✗ FAIL: {count}
- Key issues: {summary}

### Libraries
- ✓ PASS: {count}
- ⚠ WARNINGS: {count}
- ✗ FAIL: {count}
- Key issues: {summary}

### Processing Patterns
- ✓ PASS: {count}
- ⚠ WARNINGS: {count}
- ✗ FAIL: {count}
- Key issues: {summary}

### Tools
- ✓ PASS: {count}
- ⚠ WARNINGS: {count}
- ✗ FAIL: {count}
- Key issues: {summary}

## Recommendations

### Critical Fixes (Must Address)
{Schema violations and content gaps that block usage}

### High Priority Improvements
{Keyword and search issues that significantly impact findability}

### Medium Priority Enhancements
{Quality improvements for better user experience}

### Low Priority / Future Work
{Nice-to-have improvements}

## Next Steps

**If PASS or PASS WITH WARNINGS**:
1. Save verification results
2. Mark knowledge verification as complete
3. Address high/medium priority issues in future updates
4. Proceed to v5 compatibility testing

**If FAIL**:
1. Save verification results with detailed issues
2. **Exit this verification session** (critical - don't fix in same session)
3. **In a new generation session**:
   - Fix critical issues in generation logic
   - Regenerate failed files
4. **Start a fresh verification session** after regeneration
```

### Step VK5: Update or Exit

Based on verification results:

**If verification PASSED (with or without warnings)**:
1. Save verification results document
2. Mark Phase 5 content verification as complete in tasks.md
3. Address warnings in future iterations
4. Proceed to v5 compatibility testing

**If verification FAILED**:
1. Save verification results document with detailed issues
2. **Exit this verification session** (critical - don't fix in same session)
   - Output clear summary: "Verification FAILED - {X} files with critical issues. See detailed results in knowledge-verification-results.md."
   - Stop here and do not attempt fixes in this session
3. **In a new generation session**:
   - Analyze failures and update generation logic
   - Fix schema violations, content gaps, keyword issues
   - Regenerate failed files
4. **Start a fresh verification session** after regeneration completes

**Do NOT** proceed with failed files. Session separation ensures verification remains unbiased by generation logic.

## Verification Complete

When all files pass verification (or pass with acceptable warnings), knowledge file verification is complete. The knowledge base is validated and ready for production use.

## Why Separate Session?

The generation session focuses on "what to extract from RST." The verification session focuses on "what is missing or incorrect." Running both in the same session causes verification to be biased by generation logic:
- We assume extracted content is complete
- We overlook missing sections because we didn't think to include them
- We accept keyword coverage without checking if important terms are missing

By verifying in a fresh session, we approach files from the user's perspective: "Can I find what I need? Is the information complete?"

## Notes

1. **Full verification required**: All files must be verified for mission-critical quality requirements
2. **Batch processing**: Use Task tool to process files in batches (e.g., 20-30 files per batch) for efficiency
3. **User perspective**: Evaluate from user search and information needs, not generation logic
4. **Schema first**: Schema violations are critical and must be fixed before content improvements
5. **Category patterns**: Look for systematic issues within categories (e.g., all handler files missing L3 keywords)
6. **Search-driven**: Keyword coverage should enable findability for expected user queries
7. **Bilingual balance**: Japanese primary for user queries, English secondary for technical terms

## References

- Schema specification: `references/knowledge-schema.md`
- Knowledge file plan: `references/knowledge-file-plan.md`
- Generation workflow: `workflows/knowledge.md`
- Validation script: `scripts/validate-knowledge.py`
