# CHANGELOG Management

**File**: `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
**Format**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Repository Responsibilities

**nabledge-dev** (this repository):
- Maintain `[Unreleased]` section only
- Document changes as they are developed
- Changes sync to nablarch/nabledge:develop automatically

**nablarch/nabledge**:
- Manage version sections (0.1, 0.2, etc.)
- Move [Unreleased] to versioned sections during release
- Create version tags and releases

## Scope

Document only changes to **deployed content** (synced to nablarch/nabledge):

**Include:**
- Plugin content (`.claude/skills/nabledge-6/`)
- Marketplace metadata (`.claude/marketplace/`)
- Setup scripts (`scripts/setup-6-*.sh`)
- Knowledge files, workflows, user-facing docs

**Exclude:**
- GitHub Actions (`.github/workflows/`)
- Development tools, tests, work logs (`work/`)
- Repository infrastructure (`.claude/rules/`, `setup.sh`)

## Development Workflow (nabledge-dev)

1. Add changes to `[Unreleased]` section as you develop
2. Use appropriate category: Added, Changed, Deprecated, Removed, Fixed, Security
3. Changes automatically sync to nablarch/nabledge:develop on merge to main

## Release Workflow (nablarch/nabledge)

Version management happens in nablarch/nabledge repository:
1. Move [Unreleased] content to new version section with date
2. Update version in metadata files
3. Create release PR from develop to main
4. Tag and release after merge
