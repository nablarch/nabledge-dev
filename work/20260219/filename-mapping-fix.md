# Filename Mapping Fix - duplicate_form_submission.rst

**Date**: 2026-02-19
**Issue**: Missing Japanese title for duplicate_form_submission.rst
**Status**: ✅ RESOLVED

## Root Cause

**Filename mismatch between English and Japanese versions in v6**

- **EN (v6)**: `duplicate_form_submission.rst` (renamed from v5)
- **JA (v6)**: `double_transmission.rst` (kept old name)

The English filename was changed in v6, but the Japanese version retained the v5 filename.

## Version History

| Version | EN Filename | JA Filename |
|---------|-------------|-------------|
| v5 | double_transmission.rst | double_transmission.rst |
| v6 | duplicate_form_submission.rst | double_transmission.rst |

## Solution

Added filename mapping in `scripts/generate-mapping-v6.py`:

```python
# nablarch-document
if lang == 'ja':
    # Map English filenames to Japanese filenames (for renamed files in v6)
    ja_source_path = source_path
    nablarch_doc_filename_mapping = {
        'duplicate_form_submission.rst': 'double_transmission.rst',
    }

    for en_name, ja_name in nablarch_doc_filename_mapping.items():
        if source_path.endswith(en_name):
            ja_source_path = source_path.replace(en_name, ja_name)
            break

    # Check if ja version exists
    ja_file = NABLARCH_DOC_JA / ja_source_path
    if not ja_file.exists():
        return None, 'missing_file'
    file_path = ja_file
```

## Results

### Before Fix
- Title (EN): ✅ "How to Test Execution of Duplicate Form Submission Prevention Function"
- Title (JA): ❌ Missing (file not found)

### After Fix
- Title (EN): ✅ "How to Test Execution of Duplicate Form Submission Prevention Function"
- Title (JA): ✅ "二重サブミット防止機能のテスト実施方法"

## Validation

```
📋 Column Completeness
  ✅ title: 100.0% (302/302)
  ✅ title_ja: 100.0% (302/302)  ← Fixed!
  ✅ official_url: 100.0% (302/302)
  ✅ type: 100.0% (302/302)
  ✅ category: 100.0% (302/302)
  ✅ target_path: 100.0% (302/302)

======================================================================
SUMMARY
======================================================================
✅ All validations passed!

Automation Success Rate: 100.0%  ← Improved from 99.7%!
Items Needing Manual Review: 0
```

## Files Changed

**Modified**:
- `scripts/generate-mapping-v6.py` - Added nablarch_doc_filename_mapping

**Regenerated**:
- `doc/mapping/mapping-v6.md` - Now 100% complete (302/302)

**Committed**:
- Commit: 659c886
- Branch: 10-create-mapping-info
- Message: "fix: Add filename mapping for duplicate_form_submission.rst"

**Pushed**:
- Remote: origin/10-create-mapping-info
- Status: Up to date

## Pattern for Future Filename Mismatches

If more v6 filename mismatches are discovered:

1. Check v5 and v6 filenames in both EN and JA directories
2. Add mapping to `nablarch_doc_filename_mapping` dictionary
3. Regenerate and validate
4. Commit with clear explanation

## Related Files

- Investigation: `work/20260219/iteration-2-results.md` (lines 56-104)
- Phase 1 report: `work/20260219/phase-1-final-report.md`
- Phase 2 report: `work/20260219/phase-2-execution-complete.md`

## Conclusion

**100% automation achieved** for all 302 documentation files.

The script now handles:
- EN/JA path differences for system-development-guide (3 files)
- EN/JA filename mismatches for nablarch-document (1 file)
- Excel file titles (1 file)
- All other standard rst/md files (297 files)
