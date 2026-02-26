# Index Verification Workflow

Verify the quality of hints and search functionality in the generated index.toon.

**IMPORTANT**: Run this workflow in a **separate session** from the generation workflow. This prevents context bias where the same hint extraction logic used in generation would blind the verification.

## Invocation

```
nabledge-creator verify-index-6
```

## Workflow Steps

### Step VI1: Read Input Files

Read the following files:

```
.claude/skills/nabledge-6/knowledge/index.toon                     # Generated index
.claude/skills/nabledge-creator/references/index-schema.md         # Schema specification
.claude/skills/nabledge-creator/references/knowledge-file-plan.md  # Knowledge file plan
```

### Step VI2: Verify Basic Structure

Check that the index file follows the TOON schema:

1. **Header format**:
   - Verify header: `files[{count},]{title,hints,path}:`
   - Count should match total entries in file
   - Count should match expected entries from knowledge-file-plan.md

2. **Entry completeness**:
   - All entries have non-empty title (Japanese)
   - All entries have hints (minimum 3 keywords)
   - All entries have path (either "not yet created" or valid .json path)
   - No duplicate titles

3. **Sorting**:
   - Entries are sorted by title in Japanese lexical order

**Record issues**: If any structural issues found, note them and skip to Step VI6.

### Step VI3: Verify Hint Quality (All Entries)

Verify hint quality for all entries in the index. Use Task tool with batch processing if needed to handle large volume efficiently.

**Verification scope**: All entries must be verified. Process in batches if needed (e.g., 50 entries per batch).

**For each entry**:

1. **Read source documentation**:
   - Look up the entry in knowledge-file-plan.md to find source RST files
   - Read the first 50-100 lines of the source RST file
   - Understand what the feature/component does

2. **Evaluate hint coverage**:
   - Do hints cover the main concepts from the documentation?
   - Are L1 keywords present (category/domain level: バッチ, データベース, Web, etc.)?
   - Are L2 keywords present (feature/component level: class names, concepts, technologies)?
   - Are important technical terms included?

3. **Evaluate hint quality**:
   - **Japanese hints**: Proper kanji/hiragana (not English transliteration)
     - Good: データベース, バッチ, ハンドラ
     - Bad: dētabēsu, batchi, handorā
   - **English hints**: Proper technical terms (not Japanese romanization)
     - Good: DAO, CRUD, handler
     - Bad: データベース written as "database" in hints meant for Japanese
   - **Bilingual mix**: Japanese primary (user queries), English secondary (technical terms)
   - **Sufficient coverage**: 3-8 hints per entry (as per schema)

4. **Record result**:
   - Mark ✓ if hints are sufficient and high quality
   - Mark ✗ if hints are insufficient, low quality, or incorrect
   - Note specific issues: missing keywords, wrong language, too few/many hints

**Hint sufficiency criteria**:
- ✓ Excellent: 5-8 hints covering L1+L2, bilingual, searchable for expected queries
- ✓ Good: 4-5 hints covering main concepts, mostly searchable
- ⚠ Acceptable: 3-4 hints, basic coverage, some search gaps
- ✗ Insufficient: <3 hints, missing critical keywords, poor search coverage

### Step VI4: Test Search Functionality

Test if hints enable expected search behavior with sample queries.

**Prepare test queries** covering different categories:

```
Japanese queries:
- データベース接続 (database connection)
- バッチ処理 (batch processing)
- REST API
- ログ出力 (log output)
- ハンドラ (handler)
- バリデーション (validation)
- メッセージング (messaging)
- ファイルアップロード (file upload)

English queries:
- universal dao
- handler
- validation
- jsr352
- jakarta batch
- doma
```

**For each query**:

1. **Simulate search**:
   - Read index.toon entries
   - Identify entries where hints match the query (search in hints field only, not title)
   - Use case-insensitive substring matching (e.g., query "データベース" matches hints "データベース接続 DAO CRUD")
   - Count how many entries match

2. **Evaluate search results**:
   - Are relevant entries found?
   - Are irrelevant entries excluded?
   - Do bilingual hints enable both Japanese and English queries?
   - Is coverage reasonable (not too few, not too many matches)?

3. **Record results**:
   ```
   Query: "データベース接続"
   Matches: 3 entries
   - ユニバーサルDAO (relevant ✓)
   - データベースアクセス (relevant ✓)
   - データベース接続管理ハンドラ (relevant ✓)

   Evaluation: ✓ All relevant, no false positives
   ```

**Search quality criteria**:
- ✓ Excellent: All relevant entries found, no false positives, bilingual queries work
- ✓ Good: Most relevant entries found, few false positives
- ⚠ Acceptable: Some relevant entries found, some search gaps
- ✗ Poor: Many relevant entries missed or many false positives

### Step VI5: Check Created vs Uncreated Status

Verify that path field accurately reflects knowledge file creation status:

1. **List all entries with actual paths** (not "not yet created"):
   - Read index.toon and extract entries with .json paths
   - Count how many entries show as created

2. **Verify files exist**:
   - For each path, verify the file exists in `.claude/skills/nabledge-6/knowledge/`
   - Check that path is relative from knowledge/ directory

3. **Check for missing entries**:
   - Scan `.claude/skills/nabledge-6/knowledge/` directory for .json files
   - Verify all existing knowledge files have corresponding index entries
   - Flag any knowledge files not in index (orphaned files)

4. **Record results**:
   - Number of created entries in index: X
   - Number of actual .json files: Y
   - Discrepancies: Z files (list them)

**Phase 2 expectation**: All entries should show "not yet created" (no knowledge files yet)

**Phase 3-4 expectation**: Created entries should match actual .json files

### Step VI6: Document Verification Results

Create verification results document at `.pr/00078/index-verification-results.md`:

```markdown
# Index Verification Results

**Date**: YYYY-MM-DD
**Index File**: .claude/skills/nabledge-6/knowledge/index.toon
**Phase**: Phase 2 (Initial Generation from Mapping)

## Summary

**Overall Status**: ✓ PASS / ⚠ PASS WITH WARNINGS / ✗ FAIL

**Entry Count**: {actual} / {expected} entries
**Structural Issues**: {count} issues found
**Hint Quality Issues**: {count} issues found
**Search Quality**: {rating} (Excellent/Good/Acceptable/Poor)

## Structural Verification

- [✓/✗] Header format correct
- [✓/✗] Entry count matches expected count from knowledge-file-plan.md
- [✓/✗] All entries have non-empty title
- [✓/✗] All entries have sufficient hints (≥3)
- [✓/✗] All entries have path field
- [✓/✗] No duplicate titles
- [✓/✗] Entries sorted by title

**Issues Found**:
{List any structural issues}

## Hint Quality Verification

**Total Entries Verified**: {count} entries (100% coverage)

**Summary**:
- ✓ Excellent quality: {count} entries
- ✓ Good quality: {count} entries
- ⚠ Acceptable quality: {count} entries
- ✗ Insufficient quality: {count} entries

**Sample Results** (showing problematic entries only):

| Title | Hints Count | Coverage | Quality | Status |
|-------|-------------|----------|---------|--------|
| {title} | {count} | L1+L2 / L1 only / Basic | Bilingual / JP only / EN only | ✓/⚠/✗ |
| ... | ... | ... | ... | ... |

**Issues Found**:
1. **{Entry title}**: {Issue description}
   - Current hints: {current hints}
   - Missing keywords: {suggested additions}
   - Reasoning: {why these keywords are important}

## Search Functionality Testing

| Query | Language | Matches | Relevant | False Positives | Status |
|-------|----------|---------|----------|-----------------|--------|
| データベース接続 | JP | 3 | 3 | 0 | ✓ |
| バッチ処理 | JP | 5 | 4 | 1 | ⚠ |
| universal dao | EN | 1 | 1 | 0 | ✓ |
| ... | ... | ... | ... | ... | ... |

**Search Quality**: {Excellent/Good/Acceptable/Poor}

**Issues Found**:
1. **Query "{query}"**: {Issue description}
   - Expected entries: {list}
   - Actual matches: {list}
   - Problem: {missing keywords / false positives / language mismatch}

## Created vs Uncreated Status

- **Entries with paths**: {count}
- **Entries "not yet created"**: {count}
- **Actual .json files**: {count}
- **Orphaned files**: {count} (list them if any)

**Issues Found**:
{List any discrepancies}

## Recommendations

### High Priority
{Issues requiring immediate fix}

### Medium Priority
{Issues that should be improved}

### Low Priority / Future Improvements
{Nice-to-have improvements}

## Next Steps

{Choose one}:

**If PASS or PASS WITH WARNINGS**:
- Phase 2 Part B verification complete
- Index structure validated, ready for Phase 3
- Address medium/low priority issues in future updates

**If FAIL**:
1. Fix issues in `.claude/skills/nabledge-creator/scripts/generate-index.py`
2. Re-run index generation (Phase 2 Part A)
3. Re-run this verification in a new session (Phase 2 Part B)
```

### Step VI7: Update or Exit

Based on verification results:

**If verification PASSED (with or without warnings)**:
1. Save verification results document
2. Mark Phase 2 Part B as complete in tasks.md
3. Proceed to Phase 3 (pilot knowledge file generation)

**If verification FAILED**:
1. Save verification results document with detailed issues
2. **Exit this verification session** (critical - don't fix in same session)
   - Output clear summary: "Verification FAILED - {X} critical issues found. See detailed results in index-verification-results.md."
   - Stop here and do not attempt fixes in this session
3. **In a new generation session**:
   - Analyze issues and update `generate-index.py` script
   - Update hint extraction logic
   - Update keyword mappings if needed
4. Re-run index generation (Phase 2 Part A)
5. **Start a fresh verification session** (Phase 2 Part B) after regeneration

**Do NOT** proceed with failed index. Session separation ensures that verification remains unbiased by generation logic.

## Verification Complete

When verification passes, Phase 2 Part B is complete. The index structure is validated and ready for Phase 3 (pilot knowledge file generation).

## Why Separate Session?

The generation session uses hint extraction logic based on titles and categories. If we verify in the same session, we unconsciously apply the same patterns and miss hint quality issues. By reading actual documentation and testing search in a fresh session, we catch cases where:
- Important keywords were missed
- Hints are not searchable for expected queries
- Language mix is incorrect (too much English in Japanese hints, etc.)
- Technical terms are missing

## Notes

1. **Focus on hint quality**: Structural validation is automated (validate-index.py), this workflow focuses on semantic quality
2. **Full verification**: All entries must be verified for mission-critical quality requirements
3. **Search-first perspective**: Evaluate hints from user search perspective, not generation logic
4. **Bilingual validation**: Japanese primary (user queries), English secondary (technical terms)
5. **Phase-specific expectations**: Phase 2 has all "not yet created", Phase 3-4 have mix
6. **Iterative improvement**: Verification results inform hint extraction improvements
7. **Batch processing**: Use Task tool to process entries in batches for efficiency

## References

- Schema specification: `references/index-schema.md`
- Generation workflow: `workflows/index.md`
- Validation script: `scripts/validate-index.py`
- Knowledge file plan: `references/knowledge-file-plan.md`
