# Change Work Directory Structure to Issue-Based

**Date**: 2026-02-19
**Branch**: change-work-dir-to-issue-based
**Commit**: 65d6772

## Summary

Changed work directory structure from date-based (`work/YYYYMMDD/`) to issue-based (`.issues/xxxxx/`) for better traceability and organization.

## Changed Files

### Rules
- `.claude/rules/work-log.md` - Directory format: `work/yyyymmdd/` → `.issues/xxxxx/`
- `.claude/rules/postmortem.md` - Location and horizontal check paths updated
- `.claude/rules/issues.md` - Post-mortem path reference updated

### Skills
- `.claude/skills/nabledge-6/SKILL.md` - Code analysis output path updated
- `.claude/skills/nabledge-6/workflows/code-analysis.md` - Output path and examples updated
- `.claude/skills/nabledge-6/assets/code-analysis-template-guide.md` - Path references updated
- `.claude/skills/nabledge-6/assets/code-analysis-template-examples.md` - Path references updated
- `.claude/skills/nabledge-test/SKILL.md` - Test result path and workspace location updated

### Infrastructure
- `README.md` - Test result path reference updated
- `.gitignore` - Added `.tmp/` for temporary workspaces

## Key Changes

### Work Log Directory Structure
- **Before**: `work/YYYYMMDD/` (e.g., `work/20260219/`)
- **After**: `.issues/xxxxx/` (e.g., `.issues/00042/`)
- **Format**: 5-digit issue number with zero-padding

### Temporary Workspaces
- **Test workspaces**: `work/YYYYMMDD/nabledge-test/` → `.tmp/nabledge-test/`
- **Purpose**: Separate temporary evaluation outputs from permanent work logs
- **Gitignore**: Added `.tmp/` to prevent tracking temporary files

### Affected Output Locations
1. Work logs (work-log.md rule)
2. Post-mortems and horizontal checks (postmortem.md rule)
3. Test results (nabledge-test skill)
4. Code analysis documentation (nabledge-6 skill)

## Benefits

1. **Better traceability**: All artifacts for an issue grouped together
2. **Easier navigation**: Find all work related to issue #42 in `.issues/00042/`
3. **Clear separation**: Permanent logs (`.issues/`) vs temporary workspaces (`.tmp/`)
4. **Issue-driven workflow**: Aligns with GitHub issue tracking

## Usage for Future Work

### Regular Issues
Use 5-digit issue number: `.issues/00042/`, `.issues/00123/`

### Infrastructure Changes
Use `.issues/00000/` for process improvements without specific issue

## Next Steps

- Create work logs in new format for ongoing work
- Consider migrating existing `work/YYYYMMDD/` directories to `.issues/` if needed
- Update any automation scripts that reference the old directory structure
