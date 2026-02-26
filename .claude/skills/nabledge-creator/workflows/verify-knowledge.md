# Knowledge File Verification Workflow

Verify the quality of generated knowledge files. Run this workflow in a **separate session** from the generation workflow.

**IMPORTANT**: Run this workflow in a **separate session** from the generation workflow. This prevents context bias where generation decisions influence verification judgment.

## Invocation

```
nabledge-creator verify-knowledge {version} --all
```

Where `{version}` is the Nablarch version number (e.g., `6` for v{version}, `5` for v5).

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

### Step VK2: Verify All Knowledge Files

**Verification scope**: All knowledge files must be verified. Use Task tool with batch processing if needed to handle large volume efficiently.

For each knowledge file:

**2.1 Read Source RST Documentation**

- Locate source RST file(s) from mapping-v{version}.md (Source Path column)
- Read the complete RST content from `.lw/nab-official/v{version}/`
- Understand the feature/component purpose and usage

**2.2 Verify Schema Compliance**

Check the JSON file against knowledge-schema.md:

- **Required fields**: All mandatory fields present (class_name, purpose, usage, etc.)
- **Section structure**: Sections follow schema templates for the category
- **Index hints**: Each section has L1/L2/L3 keywords in index array
- **Content format**: Text uses proper markdown, code blocks formatted correctly

**2.3 Verify Content Accuracy**

Compare JSON content against RST source:

- **Section division**: RST h2 headings → JSON sections (±30% section count acceptable)
- **Content correspondence**: Key information from RST appears in JSON
- **Technical terms**: Class names, properties, annotations accurately extracted
- **Code examples**: Sample code preserved where relevant
- **Specifications**: Directives, properties, exceptions documented

**2.4 Verify Keyword Coverage**

Evaluate index hints quality:

- **L1 keywords** (category/domain level): バッチ, データベース, Web, REST, etc.
- **L2 keywords** (feature/component level): Class names, concepts, technologies
- **L3 keywords** (detail level): Method names, property names, specific terms
- **Minimum requirements**: L1 ≥ 1, L2 ≥ 2 (per knowledge-schema.md)
- **Bilingual mix**: Japanese primary (user queries), English secondary (technical terms)

**2.5 Record Result**

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

Overall Status: ✓ PASS / ⚠ PASS WITH WARNINGS / ✗ FAIL
Issues: {list critical issues}
```

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
