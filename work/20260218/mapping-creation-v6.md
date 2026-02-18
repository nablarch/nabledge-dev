# Mapping Creation for Nablarch v6

**Date**: 2026-02-18

## Summary

Created source-to-target mapping JSON for Nablarch v6 knowledge file generation following the procedure in `doc/mapping-creation/mapping-creation-prompt.md` (Version 3.0).

## Process

### 1. Non-Nab-Doc Files (Steps 1.1-1.2)

**Archetype files**: User decision to exclude all 590 files from `nablarch-single-module-archetype`.

**Development guide files**: Selected 4 files from `nablarch-system-development-guide`:
- 3 English nablarch-patterns files (asynchronous operation, anti-pattern, batch processing pattern)
- 1 security matrix Excel file
- Excluded README.md (navigation-only)

### 2. Nab-Doc Files (Steps 2-4)

**Extraction**: Found 338 nab-doc files after applying English priority (from 669 total files).

**Rule-based categorization**: Categorized 292 files using path pattern rules:
- Component types: handler, library, adaptor, tool
- Processing patterns: batch, rest, web, messaging
- Document types: about, configuration, setup

**AI judgment**: Categorized remaining 46 files by reading content:
- 33 categorized with proper categories
- 7 marked as navigation-only
- 6 excluded (meta/development files)

### 3. Target Generation (Step 5)

Generated target filenames with directory structure:
- `features/handlers/{pattern}/` - Handlers by processing pattern
- `features/libraries/` - Library components
- `features/adaptors/` - Adaptor components
- `features/tools/` - Development tools
- `guides/{type}/` - Documentation and guides

### 4. Validation (Step 8)

- ✅ No duplicate target names
- ✅ Valid JSON schema
- ✅ All entries have required fields
- ✅ Target naming conventions followed (lowercase, kebab-case, .json)

## Results

**Final mapping**: `doc/mapping-creation/mapping-v6.json`

**Statistics**:
- Total entries: 336
- With targets: 329
- Navigation-only: 7
- Excluded: 6 (not in mapping)

**Category distribution**:
- handler: 65
- library: 56
- tool: 56
- setup: 52
- web: 43
- batch: 29
- rest: 17
- adaptor: 16
- messaging: 19
- about: 12
- configuration: 9
- example: 8
- dev-guide-pattern: 2
- dev-guide-anti: 1
- dev-guide-other: 1
- migration: 1

**Directory distribution**:
- features/: 265 files
- guides/: 58 files

## Files Created

All work files organized under `doc/mapping-creation/work-v6/`:

1. **work-v6/create-mapping-v6.py** - Initial mapping creation (Steps 1-4)
2. **work-v6/categorize-ai-judgment-v6.py** - AI judgment categorization (Step 4)
3. **work-v6/finalize-mapping-v6.py** - Final merge and validation (Steps 5-9)
4. **work-v6/export-to-excel-v6.py** - Excel export for review (Step 10)
5. **work-v6/mapping-v6.json** - Final mapping output
6. **work-v6/mapping-v6.json.stats.txt** - Statistics summary
7. **work-v6/mapping-v6.xlsx** - Excel file for easy review (336 rows, 4 sheets)
8. **work-v6/needs-ai-judgment-v6.json** - Intermediate file (46 files)
9. **work-v6/categorized-ai-files-v6.json** - AI categorization results
10. **mapping-creation-prompt.md** - Updated with file organization and Excel export

## Next Steps

Use this mapping to generate knowledge files:
- Read source files according to mapping
- Transform content into structured JSON knowledge files
- Place in target paths as specified in `target_files`
