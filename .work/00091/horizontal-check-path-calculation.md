# Horizontal Check: Path Calculation Issues

**Date**: 2026-02-26
**Issue**: #91
**Scope**: Similar path calculation or link generation issues in other scripts

## Method

Search all shell scripts in `.claude/skills/nabledge-6/scripts/` directory for:
- Path calculation logic (level counting, relative path construction)
- Link generation (relative paths, file:// URLs)
- Similar patterns to the fixed bug in `prefill-template.sh`

## Scripts Checked

### 1. prefill-template.sh

**Status**: ✅ **FIXED** in this PR

**Issues found**:
- Line 115: Relative path level calculation bug (counting slashes instead of directory components)
- Lines 115-136 (before fix): No detection of marketplace plugin installation, always used relative paths

**Actions taken**:
- Fixed level calculation: `LEVEL_COUNT=$(( $(echo "$OUTPUT_DIR" | tr -cd '/' | wc -c) + 1 ))`
- Added installation path detection (lines 139-153)
- Implemented dual-strategy link generation (lines 155-186)

### 2. generate-mermaid-skeleton.sh

**Status**: ✅ **NO ISSUES FOUND**

**Analysis**:
- Purpose: Generate Mermaid diagram skeletons from Java source files
- Path handling: Only uses source file paths passed as arguments (lines 78-90)
- No path calculation logic (no level counting or relative path construction)
- No link generation (outputs Mermaid diagram syntax to stdout)
- No cross-directory references

**Conclusion**: Script does not perform path calculations or link generation, so similar issues cannot occur.

## Key Findings

| Script | Path Calculation | Link Generation | Status | Notes |
|--------|-----------------|-----------------|--------|-------|
| `prefill-template.sh` | YES | YES | ✅ Fixed | Both issues addressed in this PR |
| `generate-mermaid-skeleton.sh` | NO | NO | ✅ Safe | No path calculation or link generation |

## Patterns Identified

**Vulnerable pattern**: Scripts that:
1. Calculate relative paths based on directory depth
2. Generate links to files in different directory structures
3. Assume single installation location

**Safe pattern**: Scripts that:
1. Use paths directly as provided by arguments
2. Don't construct cross-directory references
3. Output data structures rather than file links

## Recommendations

### Immediate Actions

None required. The only script with path calculation and link generation issues was `prefill-template.sh`, which has been fixed.

### Future Prevention

1. **Design guideline**: When creating new scripts that generate file links, always consider multiple installation scenarios (marketplace plugin, local, custom)

2. **Testing checklist**: For scripts with path manipulation:
   - Test with different output directory depths
   - Test with marketplace plugin installation
   - Test with local development installation
   - Verify generated links actually resolve

3. **Code review focus**: Watch for:
   - Directory level counting (ensure counting components, not delimiters)
   - Hardcoded relative paths
   - Assumptions about installation location

4. **Path calculation pattern**: When calculating directory levels, use the formula:
   ```bash
   # Count path components = slashes + 1
   LEVEL_COUNT=$(( $(echo "$path" | tr -cd '/' | wc -c) + 1 ))
   ```
   Not just: `LEVEL_COUNT=$(echo "$path" | tr -cd '/' | wc -c)`

## Conclusion

**Horizontal check result**: ✅ **COMPLETE**

- All shell scripts in scripts directory reviewed
- No additional path calculation issues found
- Only `prefill-template.sh` had relevant issues (fixed in this PR)
- `generate-mermaid-skeleton.sh` does not perform path calculations or link generation

**Risk assessment**: **LOW** - No other scripts exhibit similar patterns that could lead to path calculation bugs.
