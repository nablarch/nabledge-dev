# Duplicate Grouping Summary

**Date**: 2026-02-18T13:46:33+09:00

## Grouping Strategy

Identical .config files (same MD5 hash) are grouped together:
- **Representative**: The alphabetically first file in each group
- **Alternatives**: All other files in the group (tracked but not separately mapped)

This reduces redundancy while maintaining full traceability.

## Results

### Nablarch v6

Before grouping: 605 files
After grouping: 525 files
Reduction: 80 files

See: grouping-report-v6.md

### Nablarch v5

Before grouping: 544 files
After grouping: 460 files
Reduction: 84 files

See: grouping-report-v5.md

## Impact on Mapping

- Mapping entries will be created only for representative files
- `source_file_alternatives` field will list duplicate files
- Total mapping entries reduced while maintaining full coverage
