# Validation Error Analysis - Knowledge Files

**Date**: 2026-02-24
**Issue**: #78
**Files Validated**: 17 knowledge files
**Total Errors**: 10 errors across 9 files

## Executive Summary

The validation found 10 errors in 9 out of 17 knowledge files (53% error rate). All errors fall into 3 distinct patterns, with "section IDs not in index" being the most common (70% of errors). No errors represent fundamental structural issues - all are fixable through targeted corrections.

## Error Patterns Summary

| Error Type | Count | % of Total | Severity | Files Affected |
|------------|-------|------------|----------|----------------|
| Section IDs not in index | 7 | 70% | Medium | 7 files |
| Invalid URL format | 1 | 10% | Low | 1 file |
| ID mismatch with filename | 1 | 10% | High | 1 file |
| Missing overview section | 1 | 10% | High | 1 file |

## Pattern 1: Section IDs Not in Index (7 errors, 70%)

### Description

The `index` array and `sections` object keys do not match 1:1. The validation script checks:
- All IDs in `index` must exist in `sections` (checked at line 98-100)
- All IDs in `sections` must exist in `index` (checked at line 101-103)

This error indicates section IDs present in `sections` but missing from `index`.

### Root Cause Analysis

**From validation script** (lines 92-103):
```python
index_ids = {item['id'] for item in data.get('index', [])}
section_ids = set(data.get('sections', {}).keys())

if index_ids != section_ids:
    missing_in_sections = index_ids - section_ids
    missing_in_index = section_ids - index_ids
    if missing_in_sections:
        print(f"ERROR: index IDs not in sections: {missing_in_sections}")
    if missing_in_index:
        print(f"ERROR: section IDs not in index: {missing_in_index}")
```

**From schema** (lines 22-28):
```markdown
**必須ルール**:
- `index`と`sections`のキーは1:1対応
- `sections`には`overview`を含める
```

**Root causes:**
1. **Content generation inconsistency**: Agent created sections in `sections` object but forgot to add corresponding entries to `index` array
2. **Template structure mismatch**: Some sections (like `tips`, `configuration`, `extensions`) may have been added to `sections` following category templates, but their `index` entries were not generated
3. **Missing hint extraction**: For sections that should have index entries, the hint extraction step was skipped or incomplete

### Affected Files

1. **checks/security.json** - `tips` section missing from index
2. **features/adapters/slf4j-adapter.json** - `limitations`, `configuration` sections missing
3. **features/handlers/batch/data-read-handler.json** - `max_count` section missing
4. **features/libraries/business-date.json** - `tips` section missing
5. **features/libraries/database-access.json** - `extensions` section missing
6. **features/libraries/universal-dao.json** - 6 sections missing: `extensions`, `tips`, `limitations`, `bean-data-types`, `configuration`, `jpa-annotations`
7. **features/tools/ntf-batch-request-test.json** - `file_data` section missing

### Category-Specific Analysis

| Category | Files | Missing Sections | Pattern |
|----------|-------|------------------|---------|
| libraries | 3 | tips, configuration, extensions, limitations, bean-data-types, jpa-annotations | Most affected - reference sections |
| checks | 1 | tips | Supplementary section |
| adapters | 1 | limitations, configuration | Setup-related sections |
| handlers | 1 | max_count | Detail section |
| tools | 1 | file_data | Data structure section |

**Observation**: Libraries category has the most errors (3 files, 9 missing sections), suggesting library knowledge files have more complex structures with reference sections that are prone to index omission.

### General Fix Strategy

**For each affected file:**

1. **Identify missing sections**: Compare `sections` keys with `index` IDs
2. **Extract hints**: For each missing section, extract 3-8 hints following schema rules (lines 88-99):
   - Priority 1: Section heading (Japanese and English)
   - Priority 2: Class names, interface names in section
   - Priority 3: Property names, configuration keys
   - Priority 4: Annotation names
   - Priority 5: Related technical terms
3. **Add index entries**: Insert entries to `index` array with extracted hints
4. **Verify order**: Ensure `index` order matches logical reading order (typically matches section definition order)

**Example fix** (for universal-dao.json `extensions` section):
```json
{
  "id": "extensions",
  "hints": [
    "拡張",
    "カスタマイズ",
    "DatabaseMetaDataExtractor",
    "convertCountSql",
    "Dialect",
    "件数取得SQL"
  ]
}
```

## Pattern 2: Invalid URL Format (1 error, 10%)

### Description

The `official_doc_urls` array contains a URL that does not start with `http`.

### Root Cause Analysis

**From validation script** (lines 82-89):
```python
if not isinstance(data['official_doc_urls'], list) or len(data['official_doc_urls']) == 0:
    print(f"ERROR: official_doc_urls must be non-empty array")
else:
    for url in data['official_doc_urls']:
        if not url.startswith('http'):
            print(f"ERROR: Invalid URL format: {url}")
```

**From schema** (lines 10-11):
```json
"official_doc_urls": ["string（1つ以上）"]
```

**Root cause:**
- The source document is an Excel file stored in the repository, not a web URL
- Agent directly used the relative file path from the documentation structure
- No URL transformation was applied to convert local paths to official documentation URLs

### Affected Files

**checks/security.json**:
```json
"official_doc_urls": [
  "システム開発ガイド/設計書/Nablarch機能のセキュリティ対応表.xlsx"
]
```

### Fix Strategy

**Option 1: Find the published URL** (Preferred)
- Check if this Excel file is published on the Nablarch documentation site
- If published, use the full HTTPS URL
- Example: `https://nablarch.github.io/docs/6u3/doc/system_design/security_checklist.xlsx`

**Option 2: Use parent documentation URL** (Fallback)
- If the Excel file is not directly accessible via URL, reference the parent documentation page that explains or links to it
- Example: `https://nablarch.github.io/docs/6u3/doc/system_design/security.html`

**Option 3: Construct repository raw URL** (Last resort)
- Use GitHub raw content URL if file is in the documentation repository
- Example: `https://raw.githubusercontent.com/nablarch/nablarch-document/6u3/ja/system_design/security_checklist.xlsx`

**Action required:**
- Investigate the actual location of `Nablarch機能のセキュリティ対応表.xlsx` in published documentation
- Update `official_doc_urls` with valid HTTPS URL

## Pattern 3: ID Mismatch with Filename (1 error, 10%)

### Description

The `id` field does not match the filename (without extension).

### Root Cause Analysis

**From validation script** (lines 70-74):
```python
expected_id = file_path.stem
if data['id'] != expected_id:
    print(f"ERROR: id '{data['id']}' != filename '{expected_id}'")
```

**From schema** (lines 9, 23):
```json
"id": "string（ファイル名 拡張子なし、kebab-case）"
```
```markdown
- `id` = ファイル名（拡張子なし）
```

**Root cause:**
- Filename: `6u3.json`
- ID in JSON: `release-6u3`
- Agent prefixed the ID with `release-` to make it more descriptive, but this violates the strict `id = filename` rule

### Affected Files

**releases/6u3.json**:
```json
{
  "id": "release-6u3",
  "title": "リリースノート 6u3",
  ...
}
```

### Fix Strategy

**Option 1: Rename the file** (Recommended for semantic clarity)
- Rename file from `6u3.json` to `release-6u3.json`
- Keep ID as `release-6u3`
- Pros: More descriptive filename, maintains semantic ID
- Cons: File renaming may break references

**Option 2: Change the ID** (Simpler)
- Keep filename as `6u3.json`
- Change ID to `6u3`
- Pros: Minimal change, follows validation rule strictly
- Cons: Less descriptive ID

**Recommendation**: Option 1 (rename file) because:
- Release notes are special documents that benefit from descriptive filenames
- `release-6u3.json` is clearer than `6u3.json` in a directory listing
- File renaming impact is minimal for newly created files

## Pattern 4: Missing Overview Section (1 error, 10%)

### Description

The `sections` object does not contain the required `overview` section.

### Root Cause Analysis

**From validation script** (lines 105-108):
```python
if 'overview' not in data.get('sections', {}):
    print(f"ERROR: 'overview' section is required")
    errors += 1
```

**From schema** (lines 28, 67-73):
```markdown
- `sections`には`overview`を含める
```
```markdown
### 必ず追加するセクション

rstの見出しに関係なく、以下のセクションは必ず作る：

| セクションID | 内容 | ソース |
|---|---|---|
| `overview` | 全体の位置づけ・目的 | rstの冒頭段落 |
```

**Root cause:**
- The `overview.json` file represents a category overview, not a specific feature/handler/library
- Agent may have interpreted "overview" as the entire document purpose, not requiring a nested `overview` section
- However, the schema mandates all knowledge files must have an `overview` section in `sections`

### Affected Files

**overview.json** (category overview file)

### Fix Strategy

**Create an `overview` section**:
1. Extract the document's purpose and scope
2. Create an `overview` section summarizing what this overview document covers
3. Add corresponding index entry

**Example structure**:
```json
{
  "id": "overview",
  "title": "Nablarch 6 概要",
  "official_doc_urls": ["https://..."],
  "index": [
    {
      "id": "overview",
      "hints": ["概要", "Nablarch", "フレームワーク", "アーキテクチャ"]
    },
    ...
  ],
  "sections": {
    "overview": {
      "description": "Nablarch 6フレームワークの全体像と主要機能の概要",
      "purpose": "Nablarch 6の構成要素と設計思想を理解する"
    },
    ...
  }
}
```

## Category Impact Analysis

### Files by Category

| Category | Total Files | Files with Errors | Error Rate | Most Common Error |
|----------|-------------|-------------------|------------|-------------------|
| libraries | 3 | 3 | 100% | Section IDs not in index (9 instances) |
| features/handlers | ~5 | 1 | ~20% | Section IDs not in index |
| features/adapters | ~2 | 1 | ~50% | Section IDs not in index |
| checks | 1 | 1 | 100% | Invalid URL, Section IDs not in index |
| features/tools | ~2 | 1 | ~50% | Section IDs not in index |
| releases | 1 | 1 | 100% | ID mismatch |
| root | 1 | 1 | 100% | Missing overview |

### Why Libraries Have Most Errors

**Structural complexity**:
- Library knowledge files have the most comprehensive templates (lines 151-177 in schema)
- Required sections include: overview, configuration, anti-patterns, errors
- Optional sections include: extensions, tips, limitations
- Total potential sections: 8-12 sections per file

**Reference-heavy content**:
- Libraries require extensive API documentation sections (bean-data-types, jpa-annotations)
- Configuration sections with detailed property lists
- Extension points for customization
- These supplementary sections are easy to add to `sections` but forget in `index`

**Generation workflow gap**:
- Agent likely generates main content sections first (CRUD, search, etc.)
- Then adds supplementary sections (tips, configuration, extensions)
- Index array may not be updated in the second pass

## Recommendations

### Immediate Actions

1. **Fix Pattern 1 (Section IDs not in index)** - Priority: High
   - Automated approach: Write a script to extract missing section IDs and generate placeholder index entries
   - Manual approach: Review each file and add index entries with proper hints
   - Estimated effort: 2-3 hours

2. **Fix Pattern 3 (ID mismatch)** - Priority: High
   - Rename `6u3.json` to `release-6u3.json`
   - Update any references if needed
   - Estimated effort: 5 minutes

3. **Fix Pattern 4 (Missing overview)** - Priority: High
   - Add overview section to `overview.json`
   - Add corresponding index entry
   - Estimated effort: 15 minutes

4. **Fix Pattern 2 (Invalid URL)** - Priority: Medium
   - Research published URL for security checklist Excel file
   - Update `official_doc_urls` in security.json
   - Estimated effort: 10-30 minutes (depends on URL availability)

### Process Improvements

1. **Knowledge generation workflow enhancement**:
   - Add explicit step: "After creating all sections, verify index completeness"
   - Use checklist: "For each section in `sections`, confirm index entry exists"

2. **Template validation**:
   - Create category-specific checklists for required sections
   - Libraries: overview, configuration, anti-patterns, errors (minimum)
   - Add "verify all template sections have index entries" step

3. **Automated pre-validation**:
   - Run `validate-knowledge.py` immediately after generation
   - Fix errors before committing
   - Consider adding validation as a git pre-commit hook

4. **Agent prompt improvement**:
   - Emphasize: "The index array and sections object must have exactly the same IDs"
   - Add explicit instruction: "After creating sections, iterate through all section IDs and create index entries"
   - Provide example showing index-sections correspondence

### Long-term Considerations

1. **Schema evolution**:
   - Consider allowing optional sections to exist without index entries (mark them as "reference-only")
   - Or enforce stricter validation during generation (real-time validation)

2. **Documentation structure**:
   - Evaluate if all supplementary sections (tips, configuration, extensions) should be first-class indexed sections
   - Some may be better as properties within parent sections

3. **URL management**:
   - Create a mapping file: source file path → published URL
   - Validate URLs against this mapping during generation
   - Handle special cases (Excel files, PDFs) explicitly

## Conclusion

All 10 validation errors are fixable with clear, straightforward corrections. The error distribution reveals systematic issues in the knowledge generation workflow, particularly around index-section synchronization for library files. By implementing the recommended fixes and process improvements, future knowledge file generation can achieve near-zero validation errors.

**Estimated total fix time**: 3-4 hours
**Impact on downstream processes**: None (errors caught before integration)
**Recurrence risk**: Medium (without process improvements), Low (with improvements implemented)
