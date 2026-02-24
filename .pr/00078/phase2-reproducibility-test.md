# Phase 2: Index Structure Reproducibility Test Report

**Date**: 2026-02-25
**Phase**: Phase 2 - Knowledge Index Generation
**Script**: `scripts/generate-index.py v6`
**Test Type**: Byte-level reproducibility (MD5 verification)

## Test Objective

Verify that index generation produces identical output across 5 independent executions to ensure reproducibility for future Nablarch versions.

## Test Method

1. Delete existing `.claude/skills/nabledge-6/knowledge/index.toon`
2. Execute `python scripts/generate-index.py v6 --mapping <path>`
3. Move generated file from relative path to correct location
4. Calculate MD5 checksum of generated file
5. Validate with `scripts/validate-index.py`
6. Backup result to `.tmp/index-runN.toon`
7. Repeat 5 times

## Test Environment

- **Working Directory**: `/home/tie303177/work/nabledge/work3`
- **Script Path**: `.claude/skills/nabledge-creator/scripts/generate-index.py`
- **Source Data**: `.claude/skills/nabledge-creator/output/mapping-v6.md`
- **Output**: `.claude/skills/nabledge-6/knowledge/index.toon`
- **Python Version**: 3.x
- **Date**: 2026-02-25

## Test Results

### Run 1

```bash
$ rm .claude/skills/nabledge-6/knowledge/index.toon
$ cd .claude/skills/nabledge-creator
$ python scripts/generate-index.py v6 --mapping /home/tie303177/work/nabledge/work3/.claude/skills/nabledge-creator/output/mapping-v6.md

Warning: Line 10 has empty title, skipping
Warning: Duplicate titles found in mapping file
Warning: Japanese locale not available, using default sorting
Generating index for version v6...
Mapping file: /home/tie303177/work/nabledge/work3/.claude/skills/nabledge-creator/output/mapping-v6.md
Output file: .claude/skills/nabledge-6/knowledge/index.toon
Successfully generated index: .claude/skills/nabledge-6/knowledge/index.toon
Total entries: 259

Completed with 2 warnings
Some entries may have insufficient hints (< 3 keywords)

$ md5sum .claude/skills/nabledge-6/knowledge/index.toon
2cfc12cdd6f0c8127c757e99de007c78  .claude/skills/nabledge-6/knowledge/index.toon
```

**Validation**:
```bash
$ python scripts/validate-index.py /home/tie303177/work/nabledge/work3/.claude/skills/nabledge-6/knowledge/index.toon

Validating: /home/tie303177/work/nabledge/work3/.claude/skills/nabledge-6/knowledge/index.toon

=== Schema Validation ===
✓ Entry count matches (259 entries)
✓ All entries have non-empty fields
✓ All entries have >= 3 hints

=== File Existence Validation ===
✓ All created file paths exist (0 created files)

=== Quality Validation ===
✓ Hint count within range (3-8)
✓ No duplicate hints within entries
✓ No empty hints
✓ Japanese keywords present in all entries
✓ Entries sorted by title

=== Consistency Validation ===
✓ No duplicate titles
✓ No duplicate paths

=== Summary ===
Total entries: 259
Created files: 0
Not yet created: 259

Result: ALL PASSED
```

### Run 2

```bash
$ md5sum .claude/skills/nabledge-6/knowledge/index.toon
2cfc12cdd6f0c8127c757e99de007c78  .claude/skills/nabledge-6/knowledge/index.toon
```

**Validation**: `Total entries: 259, Result: ALL PASSED`

**Result**: ✅ Identical to Run 1

### Run 3

```bash
$ md5sum .claude/skills/nabledge-6/knowledge/index.toon
2cfc12cdd6f0c8127c757e99de007c78  .claude/skills/nabledge-6/knowledge/index.toon
```

**Validation**: `Total entries: 259, Result: ALL PASSED`

**Result**: ✅ Identical to Run 1-2

### Run 4

```bash
$ md5sum .claude/skills/nabledge-6/knowledge/index.toon
2cfc12cdd6f0c8127c757e99de007c78  .claude/skills/nabledge-6/knowledge/index.toon
```

**Validation**: `Total entries: 259, Result: ALL PASSED`

**Result**: ✅ Identical to Run 1-3

### Run 5

```bash
$ md5sum .claude/skills/nabledge-6/knowledge/index.toon
2cfc12cdd6f0c8127c757e99de007c78  .claude/skills/nabledge-6/knowledge/index.toon
```

**Validation**: `Total entries: 259, Result: ALL PASSED`

**Result**: ✅ Identical to Run 1-4

## Summary

| Run | MD5 Checksum | Entries | Validation | Match |
|-----|--------------|---------|------------|-------|
| 1 | `2cfc12cdd6f0c8127c757e99de007c78` | 259 | ALL PASSED | Baseline |
| 2 | `2cfc12cdd6f0c8127c757e99de007c78` | 259 | ALL PASSED | ✅ |
| 3 | `2cfc12cdd6f0c8127c757e99de007c78` | 259 | ALL PASSED | ✅ |
| 4 | `2cfc12cdd6f0c8127c757e99de007c78` | 259 | ALL PASSED | ✅ |
| 5 | `2cfc12cdd6f0c8127c757e99de007c78` | 259 | ALL PASSED | ✅ |

**MD5 Consistency**: 5/5 runs identical (100%)

## Analysis

### Reproducibility Type

**Byte-level reproducibility**: All 5 runs produced identical output at the byte level, verified by MD5 checksums.

### Why Reproducibility is Achieved

The `generate-index.py` script is deterministic:

1. **No randomness**: No random number generation or sampling
2. **No timestamps**: Output does not include generation timestamps
3. **Stable sorting**: Entries sorted by title using deterministic algorithm
4. **Fixed source data**: Input mapping file (`mapping-v6.md`) is unchanged
5. **Deterministic processing**: Index generation uses fixed rules for hints and paths
6. **Consistent warnings**: Same warnings about Japanese locale and duplicate titles across all runs

### Known Warnings

The script generates consistent warnings across all runs:

1. **Line 10 empty title**: Mapping file has empty title on line 10 (skipped consistently)
2. **Duplicate titles**: Some documentation files have identical titles (handled consistently)
3. **Japanese locale**: System lacks Japanese locale, uses default sorting (consistent fallback)

These warnings do not affect reproducibility as they are handled deterministically.

### Implications

- **Future Nablarch versions**: The index generation workflow can be reliably repeated for Nablarch v7, v8, etc.
- **Process documentation**: The workflow is well-defined and reproducible
- **Quality assurance**: Consistent output enables reliable validation
- **No created files**: All 259 entries are for "not yet created" knowledge files (planned for Phase 3)

## Conclusion

✅ **Phase 2 reproducibility verified**

The index generation workflow produces **perfect byte-level reproducibility** across 5 independent executions. This confirms that:

1. The process is deterministic and reliable
2. The workflow can be repeated for future Nablarch versions
3. Success Criterion 2 (Phase 2 component) is achieved

## Next Steps

Proceed to Phase 3: Knowledge Creation reproducibility testing (5 runs required).

## Artifacts

- **Backup files**: `.tmp/index-run{1-5}.toon`
- **Original backup**: `.tmp/index-backup.toon`
- **Final output**: `.claude/skills/nabledge-6/knowledge/index.toon`
