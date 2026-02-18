# Phase 5.5: Scope Filtering Procedure Implementation

**Date**: 2026-02-18
**Related**: Mapping Creation Procedure

## Summary

Added Phase 5.5 to mapping creation procedure to systematically remove out-of-scope entries, ensuring reproducibility of the mapping process.

## Changes Made

### 1. Created Scope Filtering Script

**File**: `doc/mapping-creation-procedure/05.5-apply-scope-filter.sh`

**Functionality**:
- Creates timestamped backup before filtering
- Applies 4 filters sequentially:
  1. Remove archetype-related entries (categories: `archetype`, `check-published-api`)
  2. Remove Sample_Project entries (path contains `Sample_Project`)
  3. Remove textlint test file (path contains `.textlint/test/`)
  4. Remove license file (path ends with `/license.rst`)
- Generates detailed filtering report with counts and rationale

**Results from execution**:
- Before: 345 entries
- After: 343 entries
- Removed: 2 entries (textlint test + license)

Note: Archetype and Sample_Project entries were already removed in previous ad-hoc filtering.

### 2. Updated Procedure Documentation

**File**: `doc/mapping-creation-procedure/mapping-creation-procedure.md`

**Updates**:
1. Added Phase 5.5 to phase summary table (line 198-199)
2. Added complete Phase 5.5 section after Phase 5 (line 476+)
   - Script execution instructions
   - Filter descriptions with rationale table
   - Validation commands
   - Manual verification queries
3. Updated Scope Definition section (line 38-43)
   - Added `.textlint/test/` exclusion
   - Added `license.rst` exclusion
   - Noted Phase 5.5 as filtering phase

### 3. Regenerated Excel File

**File**: `doc/mapping-creation-procedure/mapping-v6.xlsx`

- Updated from 345 to 343 entries
- Reflects scope-filtered mappings

## Verification

All verification queries returned 0 (correct):
```bash
# Archetype entries: 0
jq '[.mappings[] | select(.categories | contains(["archetype"]) or contains(["check-published-api"]))] | length' mapping-v6.json

# Sample_Project entries: 0
jq '[.mappings[] | select(.source_file | contains("Sample_Project"))] | length' mapping-v6.json

# Textlint test entries: 0
jq '[.mappings[] | select(.source_file | contains(".textlint/test/"))] | length' mapping-v6.json

# License entries: 0
jq '[.mappings[] | select(.source_file | endswith("/license.rst"))] | length' mapping-v6.json
```

## Files Changed

1. `doc/mapping-creation-procedure/05.5-apply-scope-filter.sh` - Created
2. `doc/mapping-creation-procedure/mapping-creation-procedure.md` - Updated
3. `doc/mapping-creation-procedure/mapping-v6.json` - Filtered (343 entries)
4. `doc/mapping-creation-procedure/mapping-v6.xlsx` - Regenerated
5. `doc/mapping-creation-procedure/tmp/scope-filtering-report.md` - Generated
6. `doc/mapping-creation-procedure/tmp/mapping-v6-backup-before-scope-filter-*.json` - Backup

## Rationale

### Why Phase 5.5 (after categorization)?

- Requires category information to filter archetype-related entries
- Can use both category and path-based filtering
- Logical position: after content analysis, before target definition

### Why these specific exclusions?

| Exclusion | Rationale |
|-----------|-----------|
| Archetype entries | Static analysis available via spotbugs/checkstyle configs |
| Sample_Project | Project-specific patterns (proman/climan), not framework-level |
| .textlint/test/ | Documentation tooling test with intentional errors |
| license.rst | Legal information only, no technical knowledge/know-how |

## Reproducibility

The procedure is now fully reproducible:
1. Anyone can run phases 1-8 sequentially
2. Phase 5.5 automatically applies scope filtering
3. Result: 343 entries (framework-level knowledge only)

## Next Steps

No further action required. The procedure is complete and documented.
