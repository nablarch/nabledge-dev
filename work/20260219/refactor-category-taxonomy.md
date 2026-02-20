# Refactor Category Taxonomy Structure

**Date**: 2026-02-19
**Branch**: `10-create-mapping-info`
**Commit**: cfb8e88

## Changes

### 1. Mapping Table Structure

Updated `doc/mapping/all-files-mapping-v6.md` to use Type and Category ID columns:

**Before**:
```
| Source Path | Category | Source Path Pattern | Target Path |
```

**After**:
```
| Source Path | Type | Category ID | Source Path Pattern | Target Path |
```

### 2. development-tools as Independent Type

Separated `development-tools` from `component` Type to its own independent Type:

**Before**:
- Type: `component`
- Category ID: `development-tools`
- Target Path: `component/development-tools/*.md`

**After**:
- Type: `development-tools`
- Category IDs:
  - `testing-framework` (41 files)
  - `toolbox` (6 files)
  - `java-static-analysis` (1 file)
- Target Paths: `development-tools/{category-id}/*.md`

### 3. Design Document Simplification

Simplified taxonomy table in `doc/mapping/mapping-file-design.md`:

**Removed columns** (redundant information):
- Source Path Pattern
- Pattern Completeness
- Target Path
- Target Naming Rule

**Added section**: Target Path Rules with:
- Naming conventions
- Examples
- Pattern documentation

**Result**: Clean table showing only Type and Category ID relationships.

## Statistics

### Files by Type
- component: 116 files
- processing-pattern: 75 files
- development-tools: 48 files (newly independent)
- setup: 31 files
- guide: 16 files
- about: 15 files
- check: 1 file

**Total**: 302 files mapped

### development-tools Breakdown
- testing-framework: 41 files
- toolbox: 6 files
- java-static-analysis: 1 file

## Scripts Created

1. `scripts/add-type-column.py` - Adds Type column by extracting from Target Path
2. `scripts/fix-development-tools-type.py` - Separates development-tools entries into correct Type and Category IDs

## Next Steps

Consider reviewing other categories for similar hierarchical structure:
- `component/handlers` - May need subcategories
- `component/libraries` - May need subcategories
- `processing-pattern` - Verify current granularity is appropriate
