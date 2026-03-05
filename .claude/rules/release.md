# Release Process

## Repository Responsibilities

**nabledge-dev** (this repository):
- Development of nabledge skills
- Automatic sync to `nablarch/nabledge:develop` on push to `main`
- No version management or tagging

**nablarch/nabledge**:
- Distribution repository for end users
- `develop` branch: Latest development state (auto-synced from nabledge-dev)
- `main` branch: Stable releases
- Version management, tagging, and release workflow

## Development Workflow (nabledge-dev)

1. Work on feature branches from `main`
2. Create PR and merge to `main` after review
3. Changes automatically sync to `nablarch/nabledge:develop`
4. Users can test unreleased features from develop branch

## Release Workflow (nablarch/nabledge)

Releases are managed in the **nablarch/nabledge** repository, not here.

### Version Format

Skill name includes major version (nabledge-6 = 6.x.x). Version format: **MINOR.PATCH** (e.g., 0.1, 0.2, 0.1.1)

- **MINOR**: Feature additions (new knowledge, workflows, functionality)
- **PATCH**: Fixes and improvements only
- **User approval required** - AI suggests, user decides final version

### Release Checklist (in nablarch/nabledge)

1. **Analyze changes** - Review commits on `develop` branch since last release
2. **Propose version** - Ask user for version approval based on change type
3. **Update CHANGELOGs**:
   - `.claude/skills/nabledge-6/plugin/CHANGELOG.md` - Move [Unreleased] to versioned section with date
   - `.claude/marketplace/CHANGELOG.md` - Add row to version table
4. **Update metadata**:
   - `.claude/skills/nabledge-6/plugin/plugin.json` - Set version field
   - `.claude/marketplace/.claude-plugin/marketplace.json` - Set metadata.version field
5. **Create release PR** - From `develop` to `main` with all updates
6. **Tag and release** - After merge, create Git tag and GitHub release

### Multiple Skills

If both nabledge-6 and nabledge-5 changed, marketplace version = highest skill version (compare MINOR first, then PATCH).
