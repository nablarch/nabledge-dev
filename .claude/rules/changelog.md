# CHANGELOG Management

## Location

- **File**: `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
- **Format**: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Structure

```markdown
# Changelog

All notable changes to the nabledge-6 plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- New features

### Changed
- Changes in existing functionality

### Fixed
- Bug fixes

## [0.2] - 2026-XX-XX

### Added
- Released features

## [0.1] - 2026-02-13

### Added
- Initial release content
```

## Development Flow

### 1. During Development

Add changes under `## [Unreleased]` section:

```markdown
## [Unreleased]

### Added
- New batch processing feature

### Fixed
- Knowledge search accuracy improvement
```

### 2. Before Release

1. Replace `[Unreleased]` with version number and date
2. Create new empty `[Unreleased]` section at top

**Before**:
```markdown
## [Unreleased]

### Added
- New feature X
```

**After**:
```markdown
## [Unreleased]

## [0.2] - 2026-02-20

### Added
- New feature X

## [0.1] - 2026-02-13
...
```

### 3. Initial Release

For initial release (0.1), **do not include** `[Unreleased]` section.

Start adding `[Unreleased]` section only when next development begins.

## Change Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Added** | New features | New knowledge search functionality |
| **Changed** | Changes in existing functionality | Updated command syntax |
| **Deprecated** | Soon-to-be removed features | Old API marked as deprecated |
| **Removed** | Removed features | Deleted unused workflow |
| **Fixed** | Bug fixes | Fixed search accuracy |
| **Security** | Security fixes | Fixed XSS vulnerability |

## Version Update Rule

CHANGELOG must be updated when:
- Adding new features (Added)
- Modifying existing features (Changed)
- Fixing bugs (Fixed)
- Removing features (Removed)

Infrastructure changes (GitHub Actions, transform scripts) do not require CHANGELOG updates.
