# Post-mortem: Knowledge Base Links Broken in Code Analysis Output

**Related Issue**: #91
**Date**: 2026-02-26
**Severity**: High

## Incident Summary

Knowledge base links in code analysis output were broken for all users installing nabledge-6 via marketplace plugin (the primary installation method) and were also broken for local installations when output was in `.nabledge/YYYYMMDD/` directories. Users could not access documentation from generated analysis files, defeating the purpose of integrated documentation references. The issue affected both Claude Code and GitHub Copilot users.

## Timeline

**2026-02-26 07:43** - Root cause identified: marketplace plugin installations use different directory structure (~/.claude/plugins/cache/) than assumed by relative paths

**2026-02-26 07:43** - First fix deployed: Added installation path detection and absolute `file://` URL generation for marketplace plugins

**2026-02-26 08:12** - Second fix deployed: Corrected relative path level calculation bug for local installations

**2026-02-26 11:01** - Expert reviews completed (DevOps Engineer 4/5, Technical Writer 4/5)

## Root Cause Analysis

### Immediate Causes

Two distinct but related issues:

1. **Marketplace plugin incompatibility**: The script generated relative paths (e.g., `../../.claude/skills/nabledge-6/docs/`) assuming a project-local skill installation, but marketplace plugins install to `~/.claude/plugins/cache/nabledge/nabledge-6/{version}/` which is in a completely different directory tree from the output location `.nabledge/YYYYMMDD/` in the project directory.

2. **Relative path calculation error**: Line 115 calculated `LEVEL_COUNT` as the number of slashes in the output directory path, but should be slashes + 1 to account for the output directory itself. Example: `.nabledge/20260220` has 1 slash but represents 2 directory levels, requiring `../../` not `../`.

### Contributing Factors

- **Assumption about installation location**: Original design assumed skill would be in `.claude/skills/nabledge-6/` relative to project root
- **Multiple installation methods**: No mechanism to detect whether skill was installed via marketplace, setup script, or local development
- **Off-by-one error**: Counting slashes rather than directory components led to insufficient `../` prefixes

### Systemic Issues

- **Lack of installation-aware configuration**: Scripts didn't detect or adapt to different installation contexts
- **Insufficient testing across deployment scenarios**: Issue went undetected because testing focused on local development setup
- **No validation of generated links**: Script didn't verify that generated paths would actually resolve

## Resolution

### Approach Chosen

Implemented dual-strategy link generation based on automatic installation detection:

1. **Marketplace plugin installations**: Generate absolute `file://` URLs pointing to plugin cache directory
2. **Local installations**: Use corrected relative paths (backward compatible)
3. **Environment override**: Support `CLAUDE_SKILL_BASE_PATH` for custom installations

### Changes Made

**`.claude/skills/nabledge-6/scripts/prefill-template.sh`** (lines 115, 139-186):
- Fixed relative path calculation: `LEVEL_COUNT=$(( $(echo "$OUTPUT_DIR" | tr -cd '/' | wc -c) + 1 ))`
- Added installation path detection logic checking script location
- Implemented absolute `file://` URL generation for marketplace plugins
- Maintained relative path generation for local installations
- Added environment variable override support

**`.claude/skills/nabledge-6/workflows/code-analysis.md`** (lines 257-278):
- Documented automatic path detection behavior
- Explained marketplace vs local installation handling
- Provided examples of both link formats
- Added environment variable override documentation

### Why This Approach

**Advantages**:
- Works for all installation methods without user configuration
- Automatic detection requires no user intervention
- Backward compatible with existing local installations
- Absolute paths for marketplace plugins are guaranteed to work from any output location
- Environment variable provides escape hatch for edge cases

**Trade-offs**:
- More complex logic in script (detection + two path generation strategies)
- Absolute `file://` URLs are less portable if files are moved
- Relies on script path detection which could theoretically fail in unusual environments

### Alternatives Considered

1. **Always use absolute paths**: Rejected because it breaks portability for local development and shared repositories
2. **Fix relative path calculation only**: Insufficient because it doesn't solve the fundamental marketplace plugin problem where output and skill are in different directory trees
3. **Require user configuration**: Rejected because it adds friction and most users would get it wrong or not configure it

## Horizontal Check

**Method**: Search all shell scripts in `.claude/skills/nabledge-6/scripts/` for similar path calculation or link generation patterns

**Checked**: All scripts in scripts directory for path manipulation logic

**Key Findings**:
- `prefill-template.sh`: ✅ Fixed in this PR (both issues addressed)
- Other scripts: ✅ No similar path calculation issues found - other scripts don't generate cross-directory links

**Details**: See `.pr/00091/horizontal-check-path-calculation.md`

## Prevention Measures

1. **Documentation** - Added clear documentation of automatic path detection behavior in workflow guide, explaining different installation scenarios and link generation strategies

2. **Code comments** - Added explanatory comments in script explaining the level calculation formula and detection logic

3. **Future testing** - Recommend creating test cases for different installation scenarios (marketplace, local, custom) to verify path generation in future work

4. **Design principle** - Established pattern: detect installation context and adapt behavior rather than assuming single deployment model

## Lessons Learned

### What Went Well

- Quick identification of root cause by analyzing installation directory structures
- Expert review process caught terminology inconsistencies and validated approach
- Backward compatibility maintained for existing users
- Solution handles multiple scenarios without requiring user configuration

### What Could Improve

- Earlier consideration of marketplace plugin installation during initial design
- Test coverage across different installation methods before initial release
- Could add validation that generated paths actually exist (deferred as low priority)

### Technical Insights

- Shell path manipulation requires careful handling of directory levels (count components, not delimiters)
- Installation-agnostic scripts should detect context rather than making assumptions
- Absolute `file://` URLs provide reliability when relative paths are impractical
- `$BASH_REMATCH` is safer than capturing external command output for regex extraction

### Process Improvements

- When designing scripts that reference external files, consider all deployment scenarios
- Test with realistic installation methods (marketplace, not just local development)
- For path-dependent logic, validate against multiple directory structures
- Consider adding optional debug output for troubleshooting installation-specific issues

## Update: Final Implementation (2026-02-26)

After initial implementation with marketplace plugin support, the solution was **simplified to support only setup script installation**:

**Reason**: Current deployment only uses setup script installation method (documented in installation guides). Marketplace plugin support was not needed.

**Final changes**:
- Removed installation location detection logic (45 lines)
- Removed absolute `file://` URL generation
- Kept only relative path calculation with the `+1` fix

**Benefits of simplification**:
- Simpler code (58 lines removed, 4 lines added)
- Easier to understand and maintain
- No unnecessary complexity for unused features
- Can add marketplace support later if needed

**Final solution**: Only the directory level calculation fix (`LEVEL_COUNT = slashes + 1`) is required for current deployment needs.
