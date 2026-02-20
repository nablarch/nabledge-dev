# Notes

## 2026-02-20: Phase 1 Testing

### Test Execution Summary

Executed comprehensive testing of the mapping generation workflow (`nabledge-creator mapping`).

**Test Results:**
- ✅ Mapping generation executed successfully
- ✅ All validation checks passed (0 errors)
- ✅ Reproducibility verified (3 identical executions)
- ✅ All output files generated correctly

### Initial Generation Issues and Fixes

**Problems Found:**
1. 42 duplicate target_path errors (multiple files mapping to same path)
2. 2 underscore errors in filenames (should use hyphens)
3. 2 warnings (expected: empty Excel title, missing Japanese file)

**Root Causes:**
- `convert_target_path()` function was too simplistic for `index.rst` files
- Hardcoded filename `'nablarch_batch.md'` violated underscore-to-hyphen rule
- Insufficient path context preservation for disambiguation

**Fixes Applied** (in generate-mapping.py:335-417):
1. Enhanced subdirectory preservation logic for multiple categories
2. Added special handling for `getting_started/`, `feature_details/`, `handlers/batch/`
3. Improved `testing-framework` nested path handling
4. Removed hardcoded filenames and applied consistent conversion rules

### Reproducibility Test Results

Executed mapping generation 3 times and compared outputs:

```
Run 1 MD5: 9b12c9078256ddc3fd1b758a4e8c08e3
Run 2 MD5: 9b12c9078256ddc3fd1b758a4e8c08e3
Run 3 MD5: 9b12c9078256ddc3fd1b758a4e8c08e3
```

**Result:** ✅ Perfect reproducibility - all 3 runs produced identical output

### Validation Results (After Fixes)

```
=== Validation Report ===
Total rows: 270

Structure:     PASS (270/270)
Taxonomy:      PASS (270/270)
Source files:  PASS (en: 270/270, ja: 269/270)
Target paths:  PASS (270 unique, 0 issues)
URL format:    PASS (270/270)
Consistency:   PASS (270/270)

Result: PASSED (0 errors, 2 warnings)
```

**Warnings (Expected):**
- Row 1: Empty title (Excel file has no English title)
- Row 1: Japanese file not found (Excel file has no Japanese equivalent)

### Generated Files

```
references/mapping/mapping-v6.md           # Main mapping table (270 files)
references/mapping/mapping-v6.xlsx         # Excel format for human review
references/mapping/mapping-v6.checklist.md # Verification checklist (93 classification + 123 target path checks)
```

### Review Items

66 files require manual content verification (mainly `index.rst` files and files without clear path-based classification). These will be resolved in future work as needed for knowledge file generation.

### Next Steps

1. **Content verification** - Run `verify-mapping-6` workflow in separate session to verify classification accuracy by reading RST content
2. **Review item resolution** - Resolve the 66 review items by reading content and adding classification rules
3. **Phase 2 implementation** - Begin knowledge file generation workflow

### Decision: Defer Content Verification

Content verification (`verify-mapping-6`) should run in a **separate session** to avoid context bias. Since Phase 1 testing focuses on infrastructure (script execution, validation, reproducibility), detailed content verification is deferred to when actual knowledge file generation begins.

**Rationale:**
- Structural validation passed (0 errors, all paths unique)
- Reproducibility confirmed (deterministic algorithm)
- Content verification can catch classification errors when knowledge files are generated
- Review items (66 files) can be resolved incrementally as needed

### Key Learnings

1. **Path-based classification limitations**: Index files and files in generic directories need content-based rules or manual verification
2. **Importance of uniqueness**: Target path generation must consider full context, not just immediate parent
3. **Deterministic algorithms work**: Reproducibility achieved by avoiding timestamps, random values, or unstable sorting
4. **Validation catches errors**: Multi-layered validation (structure → taxonomy → duplicates → format) caught all issues before manual review
