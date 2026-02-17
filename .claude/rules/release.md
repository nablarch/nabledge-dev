# Release Process

## Versioning Rules

**Nabledge-specific rules**:
- Skill name includes major version (nabledge-6 = 6.x.x)
- Version format: **MINOR.PATCH** (2-digit, e.g., 0.1, 0.2, 0.1.1)
- **MINOR UP**: Feature additions (new knowledge, workflows, functionality)
- **PATCH UP**: Fixes and small improvements only
- Backward compatibility is not verified
- **User decides final version number** (AI only suggests)

## Release Steps

### 1. Check Unreleased Changes

Read skill CHANGELOG and report to user:

```bash
cat .claude/skills/nabledge-6/plugin/CHANGELOG.md
```

### 2. Propose Version Number

Analyze changes and suggest version:
- Feature additions → MINOR UP (0.1 → 0.2)
- Fixes only → PATCH UP (0.1 → 0.1.1)

Ask user using AskUserQuestion tool.

### 3. Update CHANGELOGs

**Skill CHANGELOG** (`.claude/skills/nabledge-6/plugin/CHANGELOG.md`):
- Move `[Unreleased]` content to new version section
- Add date (YYYY-MM-DD)
- Add release link at bottom

**Marketplace CHANGELOG** (`.claude/marketplace/CHANGELOG.md`):
- Add row to version table with date and link

### 4. Update JSON Metadata

**Plugin JSON** (`.claude/skills/nabledge-6/plugin/plugin.json`):
```json
{
  "version": "0.1.1"
}
```

**Marketplace JSON** (`.claude/marketplace/.claude-plugin/marketplace.json`):
```json
{
  "metadata": {
    "version": "0.1.1"
  }
}
```

### 5. Commit and Push

Stage 4 files:
```bash
git add .claude/skills/nabledge-6/plugin/CHANGELOG.md
git add .claude/skills/nabledge-6/plugin/plugin.json
git add .claude/marketplace/CHANGELOG.md
git add .claude/marketplace/.claude-plugin/marketplace.json
```

Commit:
```bash
git commit -m "Release nabledge-6 version 0.1.1

Update CHANGELOGs and metadata for version 0.1.1 release.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

Push:
```bash
git push origin main
```

**Note**: Git tags and GitHub releases are created manually as needed.

## Multiple Skills Release

If both nabledge-6 and nabledge-5 changed:
- Update each skill CHANGELOG separately
- Marketplace version = highest version (compare MINOR first, then PATCH)
- Example: nabledge-6 0.2 + nabledge-5 0.1.1 → marketplace 0.2

## Related Documents

- `.claude/rules/changelog.md` - CHANGELOG management during development
