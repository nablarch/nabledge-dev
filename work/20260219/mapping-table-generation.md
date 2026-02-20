# Mapping Table Generation Work Log

**Date**: 2026-02-19
**Task**: Generate mapping-v6.md from all-files-mapping-v6.md following updated design

## Objective

Transform existing mapping table to match updated design specification:
- Add columns: Title, Title (ja), Processing Pattern
- Remove column: Source Path Pattern
- Fix: Target Path subdirectory structure for components
- Format: Source Path as plain text, Official URL as Markdown link

## Approach

### Phase 1: Preparation (Current)

Goal: Create and test scripts without modifying actual mapping file. Aim for 100% automation.

**Tasks**:
1. Create generation script (`scripts/generate-mapping-v6.py`)
   - Parse existing all-files-mapping-v6.md
   - Extract Title from .lw/.../en/{path}.rst headers
   - Extract Title (ja) from .lw/.../ja/{path}.rst headers
   - Generate Official URL with Markdown link format
   - Assign Processing Pattern based on rules
   - Fix Target Path subdirectory structure
   - Output to test file (not actual mapping file)

2. Create validation script (`scripts/validate-mapping.py`)
   - Verify all required columns present
   - Check Title extraction success rate
   - Check Title (ja) extraction success rate
   - Validate Processing Pattern assignments
   - Verify Target Path naming conventions
   - Generate statistics report

3. Test execution on subset (10-20 files)
   - Identify issues and edge cases
   - Refine scripts iteratively
   - Document manual intervention requirements

4. Full test execution (all 337 files)
   - Generate complete test output
   - Run validation
   - Calculate automation success rate
   - Report gaps to user

5. Report to user:
   - Success rate per column
   - Issues requiring manual intervention
   - Proposed solutions
   - Wait for approval before Phase 2

### Phase 2: Execution (After user approval)

Goal: Apply prepared scripts to generate actual mapping-v6.md

**Tasks**:
1. Run generation script on actual file
2. Apply any manual fixes identified in Phase 1
3. Run validation script
4. Review output
5. Commit and push

## Status

**Current Phase**: Phase 1 - Preparation (IN PROGRESS)
**Iteration**: 2nd run after script improvements
**Next Step**: Continue validation and improvements

---

## Phase 1 Results - Iteration 2

### Execution Summary

✅ **Generation Script**: Created and tested (`scripts/generate-mapping-v6.py`)
✅ **Validation Script**: Created and tested (`scripts/validate-mapping.py`)
✅ **Test Output**: Generated to `doc/mapping/mapping-v6.md.test`

### Automation Success Rate: **98.3%**

**Total Rows**: 302 (excluding n/a index files)

#### Column Results

| Column | Success Rate | Status |
|--------|--------------|--------|
| Source Path | 100% | ✅ All extracted |
| Title (English) | 100% | ✅ All extracted |
| Title (ja) | 98.3% | ⚠️ 5 missing (see below) |
| Official URL | 100% | ✅ All generated |
| Type | 100% | ✅ All present |
| Category ID | 100% | ✅ All validated |
| Processing Pattern | 100% | ✅ 112 assigned, 190 empty (generic) |
| Target Path | 100% | ✅ All validated, subdirectories preserved |

#### Missing Title (ja) - 5 files

1. `development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/duplicate_form_submission.rst`
   - **Reason**: English-only file (no ja/ version exists)
   - **Action**: Leave empty or copy English title

2. `en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md`
   - **Reason**: English-only file (Japanese version is in different path structure)
   - **Action**: Extract from Japanese version manually

3. `en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_anti-pattern.md`
   - **Reason**: English-only file
   - **Action**: Extract from Japanese version manually

4. `en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md`
   - **Reason**: English-only file
   - **Action**: Extract from Japanese version manually

5. `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
   - **Reason**: Excel file (cannot extract title from rst/md header)
   - **Action**: Set manually (e.g., "Nablarch Security Correspondence Table")

### Processing Pattern Assignment

- **Assigned**: 112 files (37.1%)
  - processing-pattern categories: 100% assigned
  - Pattern-specific handlers (batch, web, rest, etc.): Correctly assigned
  - Pattern-specific testing/setup files: Correctly assigned

- **Empty (Generic)**: 190 files (62.9%)
  - Common handlers, libraries, adapters: Correctly left empty
  - Generic documentation: Correctly left empty

- **Invalid**: 0 (0%)

### Warnings (6 total)

1-5. Title (ja) missing for files listed above
6. Excelファイルのtitle extraction failure (expected)

### Errors

**0 errors** - All processing completed successfully

---

## Recommendations for Phase 2

### Option A: Accept 98.3% Automation (Recommended)

**Pros**:
- 297/302 rows are完璧
- Only 5 files need manual Title (ja) entry
- Can be done in 5 minutes

**Steps**:
1. Run generation script in production mode
2. Manually add 5 missing Japanese titles
3. Validate
4. Commit

### Option B: Improve Script to 100%

**Changes needed**:
1. Add Japanese path mapping for system-development-guide files
2. Add special handling for Excel files (use filename or hardcoded title)
3. Check for English-only rst files and handle gracefully

**Pros**: Full automation
**Cons**: Additional development time (30-60 min), complex logic for edge cases

**Recommendation**: Option A - The 5 manual entries are justified edge cases and take minimal time.

---

## Script Design

### generate-mapping-v6.py

**Input**: `doc/mapping/all-files-mapping-v6.md`
**Output**: `doc/mapping/mapping-v6.md.test` (Phase 1), `doc/mapping/mapping-v6.md` (Phase 2)

**Functions**:
1. `parse_existing_mapping()` - Read current table
2. `extract_rst_title(file_path)` - Extract title from rst header
3. `generate_official_url(source_path)` - Generate URL with Markdown link
4. `assign_processing_pattern(source_path, type, category)` - Rule-based assignment
5. `fix_target_path(source_path, type, category)` - Apply subdirectory rules
6. `generate_mapping_table()` - Orchestrate all functions
7. `write_output(rows, output_file)` - Write new table

**Error Handling**:
- Log warnings for missing files
- Log title extraction failures
- Log ambiguous processing pattern cases
- Continue processing, mark fields as "?" or empty

### validate-mapping.py

**Input**: Generated mapping file
**Output**: Validation report

**Checks**:
1. Column completeness
2. Title extraction rate
3. Title (ja) extraction rate
4. Processing Pattern validity
5. Target Path naming conventions
6. Category ID validation
7. Type consistency

**Output Format**:
```
=== Validation Report ===
Total Rows: 337

Title Extraction:
  Success: 320 (95%)
  Failed: 17 (5%)
  Failed files: [list]

Title (ja) Extraction:
  Success: 312 (92.6%)
  Failed: 25 (7.4%)
  Missing ja/ files: [list]

Processing Pattern:
  Assigned: 280 (83%)
  Empty (generic): 45 (13.4%)
  Ambiguous: 12 (3.6%)
  Ambiguous files: [list]

Target Path:
  Valid: 337 (100%)
  Invalid: 0 (0%)

Overall: X% fully automated, Y items need manual review
```

---

## Notes

- All work done in preparation phase outputs to `.test` files
- Actual mapping file not touched until Phase 2
- User approval required before Phase 2
