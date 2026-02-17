# Release Process

This document describes the process for releasing new versions of nabledge skills.

## Overview

Nabledge maintains CHANGELOGs at two levels:
1. **Skill-level**: `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
2. **Marketplace-level**: `.claude/marketplace/CHANGELOG.md`

**Version numbering**: User decides the version number. AI provides suggestions based on change analysis, but the final decision is always the user's.

## Version Proposal Guidelines (Reference Only)

Semantic Versioning 2.0.0 is used as a **reference for proposals**, but not mandatory:

**Format**: MAJOR.MINOR.PATCH (e.g., 1.2.3)

| Component | Suggested When | Example |
|-----------|----------------|---------|
| **MAJOR** | Breaking changes (incompatible API changes) | Knowledge structure change requiring skill updates |
| **MINOR** | New features (backward-compatible) | New knowledge added, new workflows |
| **PATCH** | Bug fixes (backward-compatible) | Documentation fixes, knowledge corrections |

**Note**: Users may choose any version number format they prefer (e.g., 0.1, 1.0.0, 2024.02, v1-alpha). The proposal logic provides suggestions only.

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

Provide version suggestion based on semantic versioning guidelines (if applicable):

| Changes Include | Suggestion | Rationale |
|----------------|------------|-----------|
| **Breaking changes** | Example: 0.1 → 1.0 or 0.2 | Major change |
| **New features** | Example: 0.1 → 0.2 | New functionality |
| **Only bug fixes** | Example: 0.1 → 0.1.1 | Bug fixes only |
| **Documentation only** | Example: No release | Non-functional changes |

**2.3 Present Suggestion to User**

```
Current version: 0.1
Unreleased changes: Bug fixes (Fixed section only)

Suggested version: 0.1.1
Rationale: Based on semantic versioning - patch increment for bug fixes.
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
- "0.1.1" - Use suggested version (based on semantic versioning)
- "0.2" - Alternative version
- "Custom" - Specify your own version number
```

**User provides version number**: Accept any format the user specifies.

**Validation** (minimal):
- Version should be different from current version (warn if same)
- No other format restrictions - user decides

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
- If multiple skills changed: Use highest version number
- If breaking change in any skill: Increment MAJOR

### Step 6: Commit and Tag

**6.1 Create Release Commit**

```bash
git add .claude/skills/nabledge-6/plugin/CHANGELOG.md
git add .claude/marketplace/CHANGELOG.md

git commit -m "$(cat <<'EOF'
Release nabledge-6 version 0.1.1

Update CHANGELOGs for nabledge-6 version 0.1.1 release.

Changes:
- Move Unreleased section to version 0.1.1
- Update marketplace version table

See CHANGELOG.md for detailed changes.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

**6.2 Create Git Tag**

```bash
git tag -a 0.1.1 -m "nabledge-6 version 0.1.1

Bug fixes:
- Claude Code setup script first-startup recognition (Issue #27)

See CHANGELOG.md for full details."

git push origin main --tags
```

### Step 7: Create GitHub Release

**7.1 Use gh CLI**

```bash
gh release create 0.1.1 \
  --title "nabledge-6 v0.1.1" \
  --notes "$(cat <<'EOF'
## nabledge-6 v0.1.1

### 修正

- Claude Codeのセットアップスクリプトがマーケットプレイス設定ではなく `.claude/skills/` ディレクトリへ直接スキルをインストールするように変更し、初回起動時に再起動なしで即座に認識されるようになりました ([#27](https://github.com/nablarch/nabledge-dev/issues/27))

### インストール

**Claude Code**:
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/0.1.1/setup-6-cc.sh | bash
\`\`\`

**GitHub Copilot**:
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/nablarch/nabledge/0.1.1/setup-6-ghc.sh | bash
\`\`\`

---

**Full Changelog**: https://github.com/nablarch/nabledge/compare/0.1...0.1.1
EOF
)"
```

**7.2 Release Notes Template**

Required sections:
- Version heading
- Changes (in Japanese, from CHANGELOG)
- Installation instructions
- Full changelog link

## Pre-Release Checklist

Before starting release process:

- [ ] All PRs merged to main branch
- [ ] All tests passing
- [ ] CHANGELOG Unreleased section complete
- [ ] Documentation up to date
- [ ] No known critical bugs

## Post-Release Tasks

After release:

1. **Verify Release**
   - Test installation from release tag
   - Verify setup scripts work with new version

2. **Announce**
   - Update project README if needed
   - Notify team/users if breaking changes

3. **Start Next Development**
   - Ensure Unreleased section exists in CHANGELOGs
   - Update version in development if needed

## Special Cases

### Multiple Skills Release

When releasing multiple skills simultaneously:

1. Update each skill CHANGELOG separately
2. Use highest version for marketplace version
3. Create single tag for marketplace version
4. Release notes include all skill changes

**Example**:
- nabledge-6: 0.1.0 → 0.2.0 (new features)
- nabledge-5: 0.1.0 → 0.1.1 (bug fixes)
- Marketplace: 0.1.0 → 0.2.0 (use highest)

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
git tag -a 0.2.0-rc.1 -m "Release candidate 1 for version 0.2.0"

# Mark as pre-release in GitHub
gh release create 0.2.0-rc.1 --prerelease
```

## Version Numbering Examples (Reference Only)

These are examples of how semantic versioning **could** be applied, but users may choose any numbering scheme:

| Current | Changes | Suggested | Alternative Valid Choices |
|---------|---------|-----------|---------------------------|
| 0.1 | Bug fixes only | 0.1.1 | 0.2, 2026.02, 0.1-patch1 |
| 0.1.1 | New knowledge added | 0.2.0 or 0.2 | 1.0, 0.1.2, next |
| 0.9.0 | First stable release | 1.0.0 or 1.0 | 2026.1, stable, v1 |
| 1.2.3 | Breaking workflow change | 2.0.0 | 1.3, next-major, 2.0 |

**Note**: AI suggests versions based on semantic versioning guidelines, but accepts any version number the user specifies.

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
