# Knowledge File Generation Patterns

**Date**: 2026-02-24
**Context**: Lessons learned from fixing validation errors in 17 knowledge files
**Purpose**: Document patterns to improve knowledge generation workflow

Based on errors analyzed in [validation-error-analysis.md](./validation-error-analysis.md).

## Common Error Patterns

### Pattern 1: Section IDs Not in Index (70% of errors)

**Symptom**: Sections exist in `sections` object but missing from `index` array

**Root Cause**: Content generation workflow inconsistency
- Agent creates sections in `sections` first
- Agent adds main content
- Agent forgets to create corresponding `index` entries for supplementary sections (tips, configuration, extensions, limitations, etc.)

**Categories Most Affected**:
- **Libraries** (100% error rate): Most complex templates with many reference sections
- **Checks, Releases** (100% error rate): Small sample size, special structure
- **Adapters, Tools** (50% error rate): Moderate complexity
- **Handlers** (20% error rate): Simpler structure

**Prevention Strategy**:
1. Generate `sections` and `index` together, not separately
2. After creating each section, immediately create its index entry
3. Use checklist: "For each key in `sections`, verify entry exists in `index`"
4. Run validation immediately after generation to catch missing entries

**Fix Template**:
```json
{
  "id": "section-id",
  "hints": [
    "主要キーワード（日本語）",
    "English keyword",
    "ClassName",
    "propertyName",
    "関連用語"
  ]
}
```

**Hint Extraction Priority**:
1. Section heading (Japanese + English)
2. Class/interface names in section content
3. Property names, configuration keys
4. Annotation names
5. Related technical terms

**Hint Count**: 3-8 hints per section (optimal: 5-6)

### Pattern 2: Invalid URL Format (10% of errors)

**Symptom**: `official_doc_urls` contains relative paths or non-HTTP URLs

**Root Cause**: Source document is local file (Excel, PDF) not published on web

**Example**:
```json
"official_doc_urls": [
  "システム開発ガイド/設計書/Nablarch機能のセキュリティ対応表.xlsx"
]
```

**Schema Rule**: URLs must start with `http://` or `https://`

**Fix Strategy**:
1. **Check published docs** (preferred): Find official web URL
2. **Use GitHub raw URL**: If file in GitHub repo, use `raw.githubusercontent.com` URL
3. **Use parent page URL** (fallback): Link to page that references the file

**Example Fix**:
```
システム開発ガイド/設計書/Nablarch機能のセキュリティ対応表.xlsx
↓
https://raw.githubusercontent.com/Fintan-contents/nablarch-system-development-guide/master/Sample_Project/%E8%A8%AD%E8%A8%88%E6%9B%B8/Nablarch%E6%A9%9F%E8%83%BD%E3%81%AE%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3%E5%AF%BE%E5%BF%9C%E8%A1%A8.xlsx
```

**Prevention**: Validate URL format during generation

### Pattern 3: ID Mismatch with Filename (10% of errors)

**Symptom**: `id` field in JSON doesn't match filename (without extension)

**Root Cause**: Agent adds descriptive prefix to make ID more semantic

**Example**:
- Filename: `6u3.json`
- ID in JSON: `release-6u3` ← Mismatch!

**Schema Rule**: `id` must equal filename (without .json extension)

**Fix Options**:
1. **Rename file** (preferred): `6u3.json` → `release-6u3.json`
2. **Change ID**: `release-6u3` → `6u3`

**Prevention**: Always derive ID directly from filename, don't add prefixes

### Pattern 4: Missing Overview Section (10% of errors)

**Symptom**: Required `overview` section not present in `sections` object

**Root Cause**: Misunderstanding that category overview files still need nested `overview` section

**Schema Rule**: Every knowledge file MUST have `overview` section, regardless of file purpose

**Fix Template**:
```json
"overview": {
  "description": "このファイルの内容を1-2文で説明",
  "purpose": "利用者がこの情報で何を理解・実現できるか"
}
```

**Prevention**: Check for `overview` section existence before completing generation

## Acceptable Warnings

### Size Warnings (86% of warnings)

**Types**:
- Section too small (<100 tokens)
- Section too large (>1500 tokens)

**Assessment**: Quality suggestions, not schema violations

**Action**: No immediate fix required. Consider:
- Small sections: May be consolidated or acceptable for reference sections
- Large sections: May need splitting for better granularity

### Hint Count Warnings (7% of warnings)

**Type**: Section has 9 hints when maximum 8 recommended

**Assessment**: Acceptable if all hints are relevant

**Action**: Review and remove least important hint if possible

### Missing Optional Fields (7% of warnings)

**Types**:
- `purpose` missing in check/tool overview
- `modules` missing in library overview
- `class_name` missing in adapter overview

**Assessment**: Optional fields, not required

**Action**: Add if information is available and useful

## Category-Specific Patterns

### Libraries (Most Complex)

**Characteristics**:
- 8-12 sections per file
- Many reference sections: tips, configuration, extensions, limitations
- Highest error rate (100% in initial generation)

**Success Pattern**:
- Create overview, main content sections first
- Then create reference sections with index entries together
- Validate after each section category

**Representative Files** (0 errors after fix):
- ✅ database-access.json
- ✅ data-bind.json
- ✅ file-path-management.json

### Handlers (Simplest)

**Characteristics**:
- 4-6 sections per file
- Standard structure: overview, processing, configuration, constraints
- Lowest error rate (20% in initial generation)

**Success Pattern**:
- Follow handler template strictly
- Main sections are usually sufficient

**Representative Files** (0 errors):
- ✅ db-connection-management-handler.json
- ✅ transaction-management-handler.json

### Tools (Moderate)

**Characteristics**:
- 5-8 sections per file
- Standard + usage-specific sections
- Moderate error rate (50% in initial generation)

**Success Pattern**:
- Overview + test patterns + assertions structure
- Watch for data structure sections (file_data, etc.)

**Representative Files** (0 errors):
- ✅ ntf-overview.json
- ✅ ntf-test-data.json
- ✅ ntf-assertion.json

### Processing (Standard)

**Characteristics**:
- 6-10 sections per file
- Architecture + configuration + patterns
- Low error rate after following template

**Representative Files** (0 errors):
- ✅ nablarch-batch.json

### Adapters (Configuration-Heavy)

**Characteristics**:
- 6-8 sections per file
- Setup, configuration, usage, limitations pattern
- Watch for missing configuration/limitations sections

**Improvement Needed**: slf4j-adapter.json had missing sections

### Checks (Special Structure)

**Characteristics**:
- Overview + check_items + tips structure
- Often references external resources (Excel, PDFs)
- Watch for URL format issues

**Improvement Needed**: security.json had URL format issue

## Process Improvements

### Immediate Validation

**Before** (error-prone):
```
1. Generate all sections
2. Add to sections object
3. Maybe add index entries
4. Commit without validation
```

**After** (error-resistant):
```
1. Generate section content
2. Add to sections object
3. Immediately create index entry
4. Validate after each section
5. Run full validation before commit
```

### Workflow Enhancement

Add to knowledge generation workflow:

```markdown
#### 2f. Verify Index Completeness

Run validation to verify index completeness:
```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-6/knowledge/{file}.json
```

If errors found:
- Section IDs not in index: Add missing index entries with hints
- Other errors: Fix according to error message
- Re-run validation until 0 errors
```

### Checklist Integration

Add to knowledge generation checklist:

```markdown
- [ ] All sections have corresponding index entries
- [ ] All URLs start with http:// or https://
- [ ] id field matches filename (without .json)
- [ ] overview section exists
- [ ] Validation passes with 0 errors
```

## Scaling Strategy

To generate remaining 137 knowledge files (17 → 154):

### Phase 1: Complete Each Category (Type-by-Type)

**Priority order** (based on complexity and error patterns):

1. **Handlers** (lowest complexity, proven patterns)
   - Generate all remaining handler files
   - Use proven templates from successful files
   - Expected: Minimal errors

2. **Processing** (standard structure)
   - Complete processing pattern files
   - Follow nablarch-batch.json pattern

3. **Tools** (moderate complexity)
   - Complete NTF tool documentation
   - Standard test framework patterns

4. **Adapters** (configuration-heavy)
   - Watch for configuration/limitations sections
   - Verify all index entries created

5. **Libraries** (highest complexity)
   - Generate carefully, validate frequently
   - Use successful patterns from database-access, data-bind

6. **Checks** (special structure)
   - Research URLs before generation
   - Verify external resource links

### Phase 2: Batch Validation

After generating each category:
1. Run validation on all files in category
2. Fix any errors immediately
3. Document any new patterns discovered
4. Update templates if needed

### Phase 3: Final Validation

After all 154 files generated:
1. Full validation run
2. Address any cross-file issues
3. Final quality check on hints and structure

## Success Metrics

**Current State** (17 files):
- 0 errors
- 56 warnings (acceptable)
- 100% schema compliance

**Target State** (154 files):
- 0 errors across all files
- Warnings <5% of total checks
- Reproducible generation process
- Complete knowledge coverage

## Key Takeaways

1. **Index-section synchronization is critical** - 70% of errors stem from this
2. **Libraries need extra attention** - Most complex structure, highest error rate
3. **Immediate validation catches errors early** - Don't generate all files then validate
4. **Category-by-category approach reduces risk** - Learn patterns, apply to similar files
5. **Warnings are acceptable** - Focus on zero errors, warnings are quality suggestions
