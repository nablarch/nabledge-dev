# Release Process

This document describes the process for releasing new versions of nabledge skills.

## Overview

Nabledge maintains CHANGELOGs at two levels:
1. **Skill-level**: `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
2. **Marketplace-level**: `.claude/marketplace/CHANGELOG.md`

**Version numbering**: User decides the version number. AI provides suggestions based on change analysis, but the final decision is always the user's.

**Release process** (7 steps):
1. Review Unreleased changes
2. Propose version number (AI suggestion)
3. User decides version number
4. Update skill CHANGELOG
5. Update marketplace CHANGELOG
6. Update JSON metadata files (plugin.json, marketplace.json)
7. Commit and push changes

**Note**: Git tags and GitHub releases are created manually after commit is merged.

## Version Numbering Format

**Nabledge-specific format**: MINOR.PATCH (2-digit)

The skill name already includes the major version (nabledge-6 = version 6.x.x), so version numbers use only MINOR and PATCH components.

**Format**: MINOR.PATCH (e.g., 0.1, 0.2, 0.1.1)

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| **MINOR** | Feature additions (new knowledge, workflows, functionality) | 0.1 → 0.2 |
| **PATCH** | Small fixes and bug fixes only | 0.1 → 0.1.1 |

**Note**: Backward compatibility is not verified in this project. Use MINOR increment for any feature addition, PATCH increment for fixes and small improvements only.

## Release Process Steps

### Step 1: Review Unreleased Changes

**1.1 Check Skill CHANGELOGs**

For each skill with unreleased changes:

```bash
# nabledge-6
cat .claude/skills/nabledge-6/plugin/CHANGELOG.md
```

**1.2 Report to User**

Present unreleased changes in user-friendly format:

```
Unreleased changes for nabledge-6:

修正:
- Claude Codeのセットアップスクリプトが初回起動時に再起動なしで
  即座に認識されるようになりました (Issue #27)

[Changes from CHANGELOG.md Unreleased section]
```

### Step 2: Propose Version Number (Suggestion Only)

**2.1 Analyze Change Type**

Analyze unreleased changes to understand what changed:

```bash
# Check categories in Unreleased section
grep -A 20 "## \[Unreleased\]" .claude/skills/nabledge-6/plugin/CHANGELOG.md
```

**2.2 Generate Suggestion**

Provide version suggestion based on nabledge versioning rules:

| Changes Include | Suggestion | Rationale |
|----------------|------------|-----------|
| **Feature additions** | Example: 0.1 → 0.2 | New knowledge, workflows, or functionality added |
| **Only fixes/improvements** | Example: 0.1 → 0.1.1 | Bug fixes or small improvements only |
| **Documentation only** | Example: No release | Non-functional changes (unless affecting deployed docs) |

**2.3 Present Suggestion to User**

```
Current version: 0.1
Unreleased changes: Bug fixes (Fixed section only)

Suggested version: 0.1.1
Rationale: Only fixes and improvements, no new features.
Includes setup script improvement (Issue #27) which fixes
first-startup recognition issue.

What version number would you like to use for this release?
```

**Important**: This is a suggestion only. User may choose any version number.

### Step 3: User Decides Version Number

Use AskUserQuestion tool to let user choose:

```
Question: "What version number for nabledge-6 release?"
Options:
- "0.1.1" - Use suggested version (fixes only)
- "0.2" - Alternative version (if considering as feature addition)
- "Custom" - Specify your own version number
```

**User provides version number**: Accept any format the user specifies.

**Validation** (minimal):
- Version should be different from current version (warn if same)
- Recommended format: MINOR.PATCH (e.g., 0.2, 0.1.1) but user decides

### Step 4: Update Skill CHANGELOG

**4.1 Move Unreleased to Version Section**

```bash
# Before
## [Unreleased]

### 修正
- Claude Codeのセットアップスクリプト... (Issue #27)

## [0.1] - 2026-02-16

# After
## [Unreleased]

## [0.1.1] - 2026-02-17

### 修正
- Claude Codeのセットアップスクリプト... (Issue #27)

## [0.1] - 2026-02-16
```

**4.2 Add Release Link**

At bottom of CHANGELOG:

```markdown
[0.1.1]: https://github.com/nablarch/nabledge/releases/tag/0.1.1
[0.1]: https://github.com/nablarch/nabledge/releases/tag/0.1
```

**4.3 Update Date**

Use today's date in YYYY-MM-DD format.

### Step 5: Update Marketplace CHANGELOG

**5.1 Add Row to Version Table**

```markdown
## バージョン対応表

| マーケットプレイスバージョン | nabledge-6 | nabledge-5 | リリース日 |
|---------------------------|-----------|-----------|----------|
| 0.1.1 | [0.1.1](plugins/nabledge-6/CHANGELOG.md#011---2026-02-17) | - | 2026-02-17 |
| 0.1 | [0.1](plugins/nabledge-6/CHANGELOG.md#01---2026-02-16) | - | 2026-02-16 |
```

**5.2 Marketplace Version**

- If only nabledge-6 changed: Use nabledge-6 version
- If only nabledge-5 changed: Use nabledge-5 version
- If multiple skills changed: Use highest version number (compare MINOR first, then PATCH)

### Step 6: Update JSON Metadata Files

**6.1 Update Plugin JSON**

Update version in `.claude/skills/nabledge-6/plugin/plugin.json`:

```json
{
  "name": "nabledge-6",
  "version": "0.1.1",
  ...
}
```

**6.2 Update Marketplace JSON**

Update version in `.claude/marketplace/.claude-plugin/marketplace.json`:

```json
{
  "name": "nabledge",
  "metadata": {
    "version": "0.1.1",
    ...
  },
  ...
}
```

**Note**: Both JSON files must match the marketplace version determined in Step 5.

### Step 7: Commit Changes

**7.1 Stage All Release Files**

```bash
git add .claude/skills/nabledge-6/plugin/CHANGELOG.md
git add .claude/skills/nabledge-6/plugin/plugin.json
git add .claude/marketplace/CHANGELOG.md
git add .claude/marketplace/.claude-plugin/marketplace.json
```

**7.2 Create Release Commit**

```bash
git commit -m "$(cat <<'EOF'
Release nabledge-6 version 0.1.1

Update CHANGELOGs and version metadata for nabledge-6 version 0.1.1 release.

Changes:
- Move Unreleased section to version 0.1.1 in skill CHANGELOG
- Update marketplace version table
- Update plugin.json version to 0.1.1
- Update marketplace.json version to 0.1.1

See CHANGELOG.md for detailed changes.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

**7.3 Push to Remote**

```bash
git push origin main
```

**Note**: Git tags and GitHub releases are created manually as needed.

## Pre-Release Checklist

Before starting release process:

- [ ] All PRs merged to main branch
- [ ] All tests passing
- [ ] CHANGELOG Unreleased section complete
- [ ] Documentation up to date
- [ ] No known critical bugs

## Post-Release Tasks

After release commit is merged to main:

1. **Verify Changes**
   - Confirm all version numbers updated correctly
   - Test setup scripts work with new version
   - Verify CHANGELOG links are correct

2. **Create Tag and GitHub Release** (Manual)
   - Create git tag: `git tag -a <version> -m "<message>"`
   - Push tag: `git push origin <version>`
   - Create GitHub release with release notes from CHANGELOG

3. **Announce**
   - Update project README if needed
   - Notify team/users if breaking changes

4. **Start Next Development**
   - Ensure Unreleased section exists in CHANGELOGs
   - Ready for next set of changes

## Special Cases

### Multiple Skills Release

When releasing multiple skills simultaneously:

1. Update each skill CHANGELOG separately
2. Use highest version for marketplace version
3. Create single tag for marketplace version
4. Release notes include all skill changes

**Example**:
- nabledge-6: 0.1 → 0.2 (new features)
- nabledge-5: 0.1 → 0.1.1 (bug fixes)
- Marketplace: 0.1 → 0.2 (use highest)

### Hotfix Release

For critical bug fixes on older versions:

1. Create branch from release tag: `git checkout -b hotfix-0.1.2 0.1.1`
2. Fix bug and update CHANGELOG
3. Create new patch version: 0.1.2
4. Merge back to main if applicable

### Pre-release Versions

For testing before official release:

```bash
# Create pre-release tag
git tag -a 0.2-rc.1 -m "Release candidate 1 for version 0.2"

# Mark as pre-release in GitHub
gh release create 0.2-rc.1 --prerelease
```

## Version Numbering Examples

Nabledge uses MINOR.PATCH format. Examples based on change type:

| Current | Changes | Suggested | Rationale |
|---------|---------|-----------|-----------|
| 0.1 | Bug fixes only | 0.1.1 | Patch increment for fixes only |
| 0.1 | Setup script fix (Issue #27) | 0.1.1 | Small improvement, no new features |
| 0.1.1 | New knowledge files added | 0.2 | Feature addition (new knowledge) |
| 0.1.1 | New workflow added | 0.2 | Feature addition (new capability) |
| 0.2 | Documentation improvements only | 0.2.1 | Small fixes without features |
| 0.9 | Major knowledge expansion | 0.10 | Feature addition (MINOR can exceed 9) |

**Note**: AI suggests versions based on nabledge rules, but user has final decision.

## Automation Notes

Future improvement opportunities:

- Automate version proposal based on CHANGELOG categories
- Automated release notes generation from CHANGELOG
- CI/CD integration for release validation
- Automatic tag creation after CHANGELOG update

## Related Documents

- `.claude/rules/changelog.md` - CHANGELOG management during development
- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) - CHANGELOG format
- [Semantic Versioning](https://semver.org/) - Versioning standard
