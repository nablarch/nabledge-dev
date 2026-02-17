# Release Process

## Version Format

Skill name includes major version (nabledge-6 = 6.x.x). Version format: **MINOR.PATCH** (e.g., 0.1, 0.2, 0.1.1)

- **MINOR**: Feature additions (new knowledge, workflows, functionality)
- **PATCH**: Fixes and improvements only
- **User approval required** - AI suggests, user decides final version

## Release Checklist

1. **Analyze changes** - Read `.claude/skills/nabledge-6/plugin/CHANGELOG.md` [Unreleased] section
2. **Propose version** - Ask user for version approval based on change type
3. **Update CHANGELOGs**:
   - `.claude/skills/nabledge-6/plugin/CHANGELOG.md` - Move [Unreleased] to versioned section with date
   - `.claude/marketplace/CHANGELOG.md` - Add row to version table
4. **Update metadata**:
   - `.claude/skills/nabledge-6/plugin/plugin.json` - Set version field
   - `.claude/marketplace/.claude-plugin/marketplace.json` - Set metadata.version field
5. **Commit and push** - Stage all 4 files, commit with release message, push to main

## Multiple Skills

If both nabledge-6 and nabledge-5 changed, marketplace version = highest skill version (compare MINOR first, then PATCH).
