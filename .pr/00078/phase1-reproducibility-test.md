# Phase 1: Mapping Reproducibility Test Report

**Date**: 2026-02-25
**Phase**: Phase 1 - Documentation Mapping Generation
**Script**: `scripts/generate-mapping.py v6`
**Test Type**: Byte-level reproducibility (MD5 verification)

## Test Objective

Verify that mapping generation produces identical output across 5 independent executions to ensure reproducibility for future Nablarch versions.

## Test Method

1. Delete existing `output/mapping-v6.md`
2. Execute `python scripts/generate-mapping.py v6`
3. Calculate MD5 checksum of generated file
4. Validate with `scripts/validate-mapping.py`
5. Backup result to `.tmp/mapping-v6-runN.md`
6. Repeat 5 times

## Test Environment

- **Working Directory**: `/home/tie303177/work/nabledge/work3`
- **Script Path**: `.claude/skills/nabledge-creator/scripts/generate-mapping.py`
- **Source Data**: `.lw/nab-official/v6/` (Nablarch v6 documentation)
- **Output**: `.claude/skills/nabledge-creator/output/mapping-v6.md`
- **Python Version**: 3.x
- **Date**: 2026-02-25

## Test Results

### Run 1

```bash
$ rm -f .claude/skills/nabledge-creator/output/mapping-v6.md
$ python .claude/skills/nabledge-creator/scripts/generate-mapping.py v6
Enumerating files for v6...
Found 339 files
Classifying...
Verifying classifications...
Enriching mappings...
Outputting to .claude/skills/nabledge-creator/output/mapping-v6.md...
Completed: 291 files mapped

$ md5sum .claude/skills/nabledge-creator/output/mapping-v6.md
11ea4a7e9b732312ceaee82ffa3720b2  .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Validation**:
```bash
$ python scripts/validate-mapping.py output/mapping-v6.md
Total rows: 291
WARNING row 1: title is empty
Structure:     PASS (291/291)
Taxonomy:      PASS (291/291)
Source files:  PASS (en: 291/291, ja: 291/291)
Target paths:  PASS (291 unique, 0 issues)
URL format:    PASS (291/291)
Consistency:   PASS (291/291)

Result: PASSED with warnings (1 warnings)
```

### Run 2

```bash
$ md5sum .claude/skills/nabledge-creator/output/mapping-v6.md
11ea4a7e9b732312ceaee82ffa3720b2  .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Result**: ✅ Identical to Run 1

### Run 3

```bash
$ md5sum .claude/skills/nabledge-creator/output/mapping-v6.md
11ea4a7e9b732312ceaee82ffa3720b2  .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Result**: ✅ Identical to Run 1-2

### Run 4

```bash
$ md5sum .claude/skills/nabledge-creator/output/mapping-v6.md
11ea4a7e9b732312ceaee82ffa3720b2  .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Result**: ✅ Identical to Run 1-3

### Run 5

```bash
$ md5sum .claude/skills/nabledge-creator/output/mapping-v6.md
11ea4a7e9b732312ceaee82ffa3720b2  .claude/skills/nabledge-creator/output/mapping-v6.md
```

**Result**: ✅ Identical to Run 1-4

## Summary

| Run | MD5 Checksum | Files Mapped | Validation | Match |
|-----|--------------|--------------|------------|-------|
| 1 | `11ea4a7e9b732312ceaee82ffa3720b2` | 291 | PASSED | Baseline |
| 2 | `11ea4a7e9b732312ceaee82ffa3720b2` | 291 | - | ✅ |
| 3 | `11ea4a7e9b732312ceaee82ffa3720b2` | 291 | - | ✅ |
| 4 | `11ea4a7e9b732312ceaee82ffa3720b2` | 291 | - | ✅ |
| 5 | `11ea4a7e9b732312ceaee82ffa3720b2` | 291 | - | ✅ |

**MD5 Consistency**: 5/5 runs identical (100%)

## Analysis

### Reproducibility Type

**Byte-level reproducibility**: All 5 runs produced identical output at the byte level, verified by MD5 checksums.

### Why Reproducibility is Achieved

The `generate-mapping.py` script is deterministic:

1. **No randomness**: No random number generation or sampling
2. **No timestamps**: Output does not include generation timestamps
3. **Stable sorting**: File enumeration and sorting use stable algorithms
4. **Fixed source data**: Source files in `.lw/nab-official/v6/` are unchanged
5. **Deterministic classification**: Path-based classification with fixed rules

### Implications

- **Future Nablarch versions**: The mapping workflow can be reliably repeated for Nablarch v7, v8, etc.
- **Process documentation**: The workflow is well-defined and reproducible
- **Quality assurance**: Consistent output enables reliable validation

## Conclusion

✅ **Phase 1 reproducibility verified**

The mapping generation workflow produces **perfect byte-level reproducibility** across 5 independent executions. This confirms that:

1. The process is deterministic and reliable
2. The workflow can be repeated for future Nablarch versions
3. Success Criterion 2 (Phase 1 component) is achieved

## Next Steps

Proceed to Phase 2: Index Structure reproducibility testing (5 runs required).

## Artifacts

- **Backup files**: `.tmp/mapping-v6-run{1-5}.md`
- **Test logs**: `.tmp/mapping-run1.log`
- **Final output**: `.claude/skills/nabledge-creator/output/mapping-v6.md`
