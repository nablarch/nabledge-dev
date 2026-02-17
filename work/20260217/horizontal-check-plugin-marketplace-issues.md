# Horizontal Check: Plugin/Marketplace Issues

**Date**: 2026-02-17
**Related Issue**: #27 - nabledge-6 plugin recognition on first startup
**Scope**: Systematic examination of repository for similar marketplace/plugin configuration issues

## Check Method

Performed systematic search for marketplace/plugin patterns across repository:

1. **File pattern search**: `grep -r "marketplace" --include="*.sh" --include="*.md"`
2. **Settings.json search**: `find . -name "settings.json" -o -name ".claude/settings.json"`
3. **Script comparison**: Manual diff between setup-6-cc.sh and setup-6-ghc.sh
4. **Documentation review**: Manual inspection of all GUIDE-*.md files
5. **Workflow analysis**: Examination of `.github/workflows/` for marketplace references

## Check Results

### 1. Setup Scripts

| File | Method Used | Status | Notes |
|------|-------------|--------|-------|
| `scripts/setup-6-cc.sh` | Marketplace configuration via settings.json | ❌ **ISSUE FOUND** | Root cause of Issue #27 |
| `scripts/setup-6-ghc.sh` | Direct skill copy to .claude/skills/ | ✅ Correct | Working pattern to follow |

**Analysis**:
- setup-6-cc.sh (lines 14-112): Configures marketplace in settings.json, but Claude Code doesn't copy skills on first startup due to race condition
- setup-6-ghc.sh (lines 18-41): Downloads with git sparse-checkout, copies to .claude/skills/ directly - works reliably

### 2. Settings.json Usage in Development Repository

| Location | Purpose | Status | Notes |
|----------|---------|--------|-------|
| `.claude/settings.json` (project root) | Development settings | ✅ OK | Used for nabledge-dev project itself, not distributed |
| Template in setup-6-cc.sh | User project configuration | ❌ **ISSUE FOUND** | Creates settings.json with marketplace config |

**Analysis**:
- Project's own settings.json is fine (development use only)
- Template generation in setup-6-cc.sh needs to be replaced with direct copy approach

### 3. Documentation References

| File | Reference Type | Line(s) | Status | Action Required |
|------|----------------|---------|--------|-----------------|
| `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` | Plugin installation prompts | 22 | ❌ **ISSUE FOUND** | Remove marketplace/plugin references |
| `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` | settings.json team sharing | 18-22 | ❌ **ISSUE FOUND** | Change to .claude/skills/ directory |
| `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` | Version update instructions | 59-82 | ❌ **ISSUE FOUND** | Update paths from settings.json to .claude/skills/ |
| `.claude/skills/nabledge-6/plugin/GUIDE-GHC.md` | Direct skill copy | - | ✅ Correct | Already uses correct approach |
| `README.md` | General setup links | - | ✅ OK | No marketplace references |

**Analysis**:
- GUIDE-CC.md has multiple references to marketplace/plugin mechanism
- All need updating to reflect direct skill copy approach
- GUIDE-GHC.md is already correct (references .claude/skills/ directory)

### 4. GitHub Actions Workflows

| Workflow File | Marketplace References | Status | Notes |
|---------------|------------------------|--------|-------|
| `.github/workflows/distribute-nabledge-6.yml` | None | ✅ OK | Uses plugin directory structure correctly |
| `.github/workflows/check-branch.yml` | None | ✅ OK | No marketplace references |

**Analysis**:
- CI/CD workflows don't reference marketplace mechanism
- Distribution workflow correctly organizes files in plugins/nabledge-6/ structure

### 5. Other Files

| File Pattern | Files Checked | Issues Found |
|--------------|---------------|--------------|
| `*.sh` scripts | All in scripts/ directory | Only setup-6-cc.sh has issue |
| `*.md` documentation | All README, GUIDE, design docs | Only GUIDE-CC.md has issue |
| `.claude/rules/*.md` | All rule files | No marketplace references |
| `work/` logs | Previous work logs | No issues (informational only) |

## Resolution Status

### Addressed in This Issue (#27)

| Finding | Resolution | Files Changed |
|---------|------------|---------------|
| setup-6-cc.sh uses marketplace config | Switch to direct skill copy (following setup-6-ghc.sh pattern) | `scripts/setup-6-cc.sh` |
| GUIDE-CC.md references plugin prompts | Remove marketplace references, update to direct skill installation | `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` |
| GUIDE-CC.md references settings.json sharing | Change to .claude/skills/ directory sharing | `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` |

### Not Requiring Action

| Finding | Reason No Action Needed |
|---------|-------------------------|
| Project's own .claude/settings.json | Development environment only, not distributed |
| setup-6-ghc.sh | Already uses correct pattern |
| GUIDE-GHC.md | Already correct |
| GitHub Actions workflows | No marketplace references |
| Other documentation | No marketplace references |

## Follow-up Actions

### Immediate (This Issue)

- [x] Update setup-6-cc.sh to use direct skill copy
- [x] Update GUIDE-CC.md to reflect direct skill installation
- [x] Create test script to verify fix
- [x] Document in post-mortem

### Future Considerations

1. **Pattern Documentation**: Document direct skill copy as preferred pattern for both Claude Code and GitHub Copilot
2. **Setup Script Unification**: Consider unified setup script that detects AI tool and configures appropriately
3. **Testing**: Add CI test for first-startup skill recognition (currently manual test only)
4. **Knowledge Sharing**: Add ADR (Architecture Decision Record) documenting why direct copy preferred over marketplace

## Lessons from Horizontal Check

### What Worked Well

- Systematic search patterns caught all marketplace references
- Script comparison (cc vs ghc) quickly identified working pattern
- Documentation review found all affected user-facing content

### What Could Improve

- Earlier horizontal check during initial implementation would have prevented issue
- Automated tests for first-startup scenarios would catch this type of issue
- Pattern library documenting preferred approaches for different AI tools

### Process Improvements

- Make horizontal check standard step in bug investigation (now documented in `.claude/rules/issues.md`)
- Create architecture decision records (ADRs) for integration patterns
- Add horizontal check results to post-mortem template

## Summary

**Total Files Checked**: 50+ (scripts, documentation, workflows, configurations)

**Issues Found**: 2 files with marketplace-related issues
- scripts/setup-6-cc.sh (root cause)
- .claude/skills/nabledge-6/plugin/GUIDE-CC.md (documentation)

**Resolution**: Both addressed in Issue #27 by switching to direct skill copy pattern

**Similar Issues Elsewhere**: None found - issue isolated to Claude Code setup path

**Prevention**: Test script added, documentation updated, standards established
