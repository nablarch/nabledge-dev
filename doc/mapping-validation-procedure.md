# Mapping Validation Procedure

**Date**: 2026-02-18
**Target Files**:
- `work/20260213/create-mapping-info/mapping-v6.json` (514 mappings)
- `work/20260213/create-mapping-info/mapping-v5.json` (453 mappings)
- **Total**: 967 mappings

**Purpose**: Validate all mapping entries to ensure accuracy before knowledge file generation

---

## Overview

Mapping files define the relationship between official documentation and target knowledge files. Incorrect mappings will lead to incorrect knowledge file generation. This validation ensures:
- All source files exist and content matches mapping metadata
- Categories are correctly assigned based on content
- Scope determination (in_scope true/false) is correct
- Target file paths follow the correct structure

---

## Prerequisites

### 1. Design Document Reference

**Directory Structure**: Defined in [Design Document Section 2.4](nabledge-design.md#24-ファイル構成)

The design document includes:
- Complete knowledge directory structure (including `about/`, `setup/`, `guides/`, `migration/`)
- Category type → directory mapping table
- Naming conventions for each category

Refer to the design document for the authoritative directory structure and mapping rules.

---

## Validation Scope

For each mapping entry, validate:

### 1. Source File Validation
- ✅ **Existence**: `source_file` path exists
- ✅ **Title Match**: `title` matches actual file title (from rst header)

### 2. Content-Based Validation
- ✅ **Category Assignment**: `categories` are appropriate based on actual content
- ✅ **Scope Determination**: `in_scope` matches scope definition in CLAUDE.md
- ✅ **Exclusion Reason**: If `in_scope: false`, `reason_for_exclusion` is valid

### 3. Target File Path Validation
- ✅ **Directory Structure**: Path follows category type → directory mapping
- ✅ **Naming Convention**: Filename follows kebab-case and category-specific patterns

---

## Mapping Entry Structure

```json
{
  "id": "v6-0001",
  "source_file": "nab-official/v6/nablarch-document/en/index.rst",
  "title": "Nablarch",
  "categories": ["about"],
  "in_scope": true,
  "reason_for_exclusion": null,
  "target_files": ["about/about.json"]
}
```

---

## Validation Process

### Phase 1: Design Document Update ✅ COMPLETED
1. ✅ Created category type → directory mapping table
2. ✅ Defined naming conventions
3. ✅ Updated doc/nabledge-design.md section 2.4
4. Ready for validation execution

### Phase 2: Automated Validation Script
Create Python validation script to check:
- Source file existence
- JSON schema compliance
- Category definitions exist in categories-v*.json
- Required fields present

Output: List of entries with mechanical errors

### Phase 3: AI Content Validation
For each mapping (967 entries):
1. Read source_file content
2. Verify title matches
3. Assess category assignment appropriateness
4. Verify scope determination
5. Check target_file path correctness

Output: Validation checklist with results

### Phase 4: Issue Resolution
- Fix identified issues
- Re-validate changed entries
- Generate final validation report

---

## Validation Output Format

### Checklist Structure
```markdown
## Mapping ID: v6-0001

**Source**: nab-official/v6/nablarch-document/en/index.rst
**Title in mapping**: Nablarch
**Categories**: about
**In Scope**: true
**Target**: about/about.json

### Validation Results
- [x] Source file exists
- [x] Title matches (actual: "Nablarch")
- [x] Category appropriate (Framework overview content)
- [x] Scope correct (Framework fundamentals are in-scope)
- [x] Target path correct (about/ directory for type=about)

**Status**: ✅ PASS

---
```

### Summary Statistics
- Total entries validated: 967
- Passed: XXX
- Failed: XXX
- Issues by category:
  - Source file not found: XX
  - Title mismatch: XX
  - Category mismatch: XX
  - Scope error: XX
  - Target path error: XX

---

## Validation Rules Reference

### Scope Determination (CLAUDE.md)

**In Scope**:
- Nablarch Batch (On-demand) - `batch-nablarch`
- RESTful Web Services - `rest`
- HTTP Messaging - `http-messaging`
- DB Messaging (Resident Batch) - `messaging-db`
- Handlers (all types) - `handler`
- Libraries - `library`
- Adaptors - `adaptor`
- Tools - `tool`
- Setup, Configuration - `setup`, `configuration`, `archetype`
- Development Guides - `dev-guide-*`
- Checks - `check-*`
- About, Migration - `about`, `migration`

**Out of Scope**:
- Jakarta Batch (JSR 352) - `batch-jsr352`
- Web Applications (JSP/UI) - `web`
- MOM Messaging - `messaging-mom`

### Category Type → Directory Mapping

See [Design Document Section 2.4](nabledge-design.md#24-ファイル構成) for the complete mapping table.

Quick reference:

| Category Type | Directory | Example |
|--------------|-----------|---------|
| processing-pattern | features/processing/ | nablarch-batch.json |
| component (handler) | features/handlers/{batch,common,rest}/ | data-read-handler.json |
| component (library) | features/libraries/ | universal-dao.json |
| component (adaptor) | features/adapters/ | slf4j-adapter.json |
| component (tool) | features/tools/ | ntf-overview.json |
| setup | setup/ | blank-project.json |
| guide | guides/ | dev-guide-pattern.json |
| check | checks/ | security.json |
| about | about/ | framework-concept.json |
| about (migration) | migration/ | v5-to-v6.json |

---

## Risk Assessment

### Critical Risks
1. **False Negatives**: In-scope files marked as out-of-scope
   - Impact: Missing essential knowledge in generated files
   - Mitigation: Double-check all `in_scope: false` entries

2. **Category Mismatch**: Wrong category assignment
   - Impact: Knowledge files placed in wrong location, poor searchability
   - Mitigation: Read actual content, not just filenames

3. **Target Path Errors**: Incorrect directory structure
   - Impact: Knowledge generation fails or creates wrong structure
   - Mitigation: Define clear mapping rules in Phase 1

### Validation Quality
- **Manual validation of 967 entries is time-consuming** (estimated 3-5 minutes per entry = 48-80 hours)
- **Fatigue-induced errors are likely** in long validation sessions
- **Recommendation**:
  - Validate in batches (50-100 entries per session)
  - Use automated checks to filter obvious errors first
  - Sample validation (20%) for quality assessment

---

## Next Steps

1. ✅ **Phase 1**: Design document updated with directory structure
2. **Phase 2**: Create automated validation script (optional - mechanical checks)
3. **Phase 3**: Execute AI content validation (967 entries)
4. **Phase 4**: Fix issues and generate final report

**Current Status**: Ready to begin Phase 2 or Phase 3

---

## Notes

- Validation must be thorough as mapping errors propagate to all generated knowledge files
- The mapping is the "source of truth" for knowledge file generation
- Special attention to `in_scope: false` entries (false negatives are most costly)
- Consider sampling validation (20%) if full validation proves impractical
