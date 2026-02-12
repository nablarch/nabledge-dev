# GitHub Action Design: Plugin Distribution for Nabledge

## Overview

This document describes the GitHub Action design for automatically converting and syncing the nabledge-6 skill from development format (nabledge-dev) to distribution format (nabledge) as a Claude Code Plugin.

## Repository Roles

| Repository | Purpose | Structure | Users |
|-----------|---------|-----------|-------|
| **nabledge-dev** | Development, testing, demo | `.claude/skills/nabledge-6/` | Developers |
| **nabledge** | Distribution, user installation | Claude Code Plugin format | End users |

## Current vs Distribution Structure

### Development (nabledge-dev)

```
nabledge-dev/
├── .claude/
│   └── skills/
│       └── nabledge-6/
│           ├── SKILL.md
│           ├── workflows/
│           │   ├── keyword-search.md
│           │   ├── section-judgement.md
│           │   └── code-analysis.md
│           ├── assets/
│           │   ├── code-analysis-template.md
│           │   ├── code-analysis-template-guide.md
│           │   └── code-analysis-template-examples.md
│           ├── knowledge/
│           │   ├── index.toon
│           │   ├── features/
│           │   ├── checks/
│           │   └── releases/
│           ├── docs/
│           │   ├── features/
│           │   ├── checks/
│           │   └── releases/
│           └── plugin/
│               ├── plugin.json
│               ├── README.md
│               ├── LICENSE
│               └── CHANGELOG.md
```

**Characteristics**:
- ✅ Immediate testing with `/nabledge-6`
- ✅ Easy demo and dogfooding
- ✅ Fast edit-test-debug cycle
- ❌ Not installable as plugin

### Distribution (nabledge)

```
nabledge/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   └── nabledge-6/
│       └── SKILL.md             # Main skill definition
├── workflows/
│   ├── keyword-search.md
│   ├── section-judgement.md
│   └── code-analysis.md
├── assets/
│   ├── code-analysis-template.md
│   ├── code-analysis-template-guide.md
│   └── code-analysis-template-examples.md
├── knowledge/
│   ├── index.toon
│   ├── features/
│   ├── checks/
│   └── releases/
├── docs/
│   ├── features/
│   ├── checks/
│   └── releases/
├── README.md                    # Installation & usage
├── LICENSE                      # Apache 2.0 or MIT
└── CHANGELOG.md                 # Version history
```

**Characteristics**:
- ✅ Installable via `/plugin marketplace add nablarch/nabledge`
- ✅ Automatic updates for users
- ✅ Standard plugin structure
- ✅ Proper versioning with plugin.json

## File Mapping

| Source (nabledge-dev) | Destination (nabledge) | Action |
|----------------------|------------------------|--------|
| `.claude/skills/nabledge-6/SKILL.md` | `skills/nabledge-6/SKILL.md` | Move |
| `.claude/skills/nabledge-6/workflows/` | `workflows/` | Move to root |
| `.claude/skills/nabledge-6/assets/` | `assets/` | Move to root |
| `.claude/skills/nabledge-6/knowledge/` | `knowledge/` | Move to root |
| `.claude/skills/nabledge-6/docs/` | `docs/` | Move to root |
| `.claude/skills/nabledge-6/plugin/plugin.json` | `.claude-plugin/plugin.json` | Move |
| `.claude/skills/nabledge-6/plugin/README.md` | `README.md` | Move |
| `.claude/skills/nabledge-6/plugin/LICENSE` | `LICENSE` | Move |
| `.claude/skills/nabledge-6/plugin/CHANGELOG.md` | `CHANGELOG.md` | Move and update |

## GitHub Action Design

### Current Workflow (sync-to-nabledge.yml)

**File**: `.github/workflows/sync-to-nabledge.yml`

**Trigger**: Push to `dummy-from` branch

**Current behavior**:
1. Checkout nabledge-dev repository
2. Checkout nabledge repository (dummy-to branch)
3. Copy `.claude/skills/nabledge-6` to `nabledge-repo/.claude/skills/nabledge-6`
4. Commit and push to nabledge repository

**Issue**: Copies development structure, not plugin format

### Updated Workflow Design

**New behavior**:
1. Checkout nabledge-dev repository
2. Checkout nabledge repository (dummy-to branch)
3. **Transform to plugin structure**:
   - Create `.claude-plugin/` directory
   - Move `SKILL.md` to `skills/nabledge-6/SKILL.md`
   - Move `workflows/`, `assets/`, `knowledge/`, `docs/` to root
   - Move `plugin/plugin.json` to `.claude-plugin/plugin.json`
   - Move `plugin/README.md` to root
   - Move `plugin/LICENSE` to root
   - Move `plugin/CHANGELOG.md` to root and update with sync info
4. Commit and push to nabledge repository

### Workflow Steps Detail

#### Step 1: Checkout repositories

```yaml
- name: Checkout nabledge-dev
  uses: actions/checkout@v4
  with:
    fetch-depth: 0

- name: Checkout nabledge repository
  uses: actions/checkout@v4
  with:
    repository: nablarch/nabledge
    ref: dummy-to
    token: ${{ secrets.NABLEDGE_SYNC_TOKEN }}
    path: nabledge-repo
```

#### Step 2: Clean destination

```yaml
- name: Clean nabledge repository
  run: |
    cd nabledge-repo
    # Remove all files except .git/
    find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
```

#### Step 3: Transform to plugin structure

```yaml
- name: Transform to plugin structure
  run: |
    # Create plugin directories
    mkdir -p nabledge-repo/.claude-plugin
    mkdir -p nabledge-repo/skills/nabledge-6

    # Move SKILL.md to skills/nabledge-6/
    cp .claude/skills/nabledge-6/SKILL.md nabledge-repo/skills/nabledge-6/

    # Move supporting directories to root
    cp -r .claude/skills/nabledge-6/workflows nabledge-repo/
    cp -r .claude/skills/nabledge-6/assets nabledge-repo/
    cp -r .claude/skills/nabledge-6/knowledge nabledge-repo/
    cp -r .claude/skills/nabledge-6/docs nabledge-repo/

    # Move plugin files to root
    cp .claude/skills/nabledge-6/plugin/plugin.json nabledge-repo/.claude-plugin/
    cp .claude/skills/nabledge-6/plugin/README.md nabledge-repo/
    cp .claude/skills/nabledge-6/plugin/LICENSE nabledge-repo/
    cp .claude/skills/nabledge-6/plugin/CHANGELOG.md nabledge-repo/
```

#### Step 4: Update CHANGELOG.md

```yaml
- name: Update CHANGELOG.md
  run: |
    TRIGGER_COMMIT_SHA="${{ github.sha }}"
    TRIGGER_COMMIT_URL="https://github.com/${{ github.repository }}/commit/${TRIGGER_COMMIT_SHA}"
    DATE=$(date +%Y-%m-%d)

    # Append sync entry to CHANGELOG
    sed -i "/^# Changelog/a \\\n## [Unreleased] - ${DATE}\\\n\\\n### Changed\\\n- Synced from: ${TRIGGER_COMMIT_URL}\\\n" nabledge-repo/CHANGELOG.md
```

**Note**: The plugin.json, README.md, LICENSE, and CHANGELOG.md are now stored in the development repository and reviewed during development, rather than being generated each time.

#### Step 5: Commit and push

```yaml
- name: Commit and Push to nabledge
  working-directory: nabledge-repo
  run: |
    git add .

    if git diff --staged --quiet; then
      echo "No changes to commit"
      exit 0
    fi

    TRIGGER_COMMIT_SHA="${{ github.sha }}"
    TRIGGER_COMMIT_URL="https://github.com/${{ github.repository }}/commit/${TRIGGER_COMMIT_SHA}"

    git commit -m "Sync nabledge-6 plugin from nabledge-dev" -m "Triggered by: ${TRIGGER_COMMIT_URL}"

    git push origin dummy-to
```

## README.md Template

The plugin README.md (stored in `.claude/skills/nabledge-6/plugin/README.md`) should include:

- Plugin name and description
- Features (Knowledge Search, Code Analysis)
- Installation instructions (`/plugin marketplace add nablarch/nabledge`)
- Usage examples (`/nabledge-6`, `/nabledge-6 "question"`, `/nabledge-6 code-analysis`)
- Knowledge coverage (batch, REST, handlers, libraries, tools)
- Scope (in/out of scope)
- Version information (Nablarch 6u2/6u3, plugin version)
- License (Apache 2.0)
- Repository links (distribution and development)

See example content in the actual plugin/README.md file in the repository.

## Version Management Strategy

Store `plugin.json` and `CHANGELOG.md` in `.claude/skills/nabledge-6/plugin/` directory.

### CI Validation

Add validation step to fail sync workflow if version files are not updated:

```yaml
- name: Validate version updates
  run: |
    # Check if plugin.json or CHANGELOG.md were modified in the last commit
    if ! git diff HEAD~1 HEAD --name-only | grep -q "plugin/plugin.json\|plugin/CHANGELOG.md"; then
      echo "Error: plugin.json or CHANGELOG.md must be updated before sync"
      exit 1
    fi
```

This ensures developers always update version information when making changes that trigger a sync.

## Workflow File Structure

### Recommended Split

**Option A: Single workflow** (simpler)

```
.github/workflows/
└── sync-to-nabledge.yml    # All-in-one: transform + sync
```

**Option B: Separate workflows** (more flexible)

```
.github/workflows/
├── sync-to-nabledge.yml            # Main sync workflow
└── scripts/
    └── transform-to-plugin.sh      # Transformation script
```

### Recommendation

Use **Option B** with separate script for:
- ✅ Easier testing locally
- ✅ Better maintainability
- ✅ Reusable for manual releases

## Testing Strategy

### Local Testing

Before pushing to dummy-from branch, developers can test transformation locally:

```bash
# Run transformation script
.github/scripts/transform-to-plugin.sh

# Test plugin structure
cd /tmp/nabledge-plugin-test
claude --plugin-dir .
```

### CI Validation

Add validation step in workflow:

```yaml
- name: Validate plugin structure
  run: |
    # Check required files exist
    test -f nabledge-repo/.claude-plugin/plugin.json
    test -f nabledge-repo/skills/nabledge-6/SKILL.md
    test -f nabledge-repo/README.md
    test -f nabledge-repo/LICENSE

    # Validate plugin.json format
    jq empty nabledge-repo/.claude-plugin/plugin.json
```

## Deployment Flow

### Development to Distribution

```
Developer
  │
  ├─> Edit .claude/skills/nabledge-6/ in nabledge-dev
  │
  ├─> Test locally: /nabledge-6
  │
  ├─> Commit to dummy-from branch
  │
  ├─> GitHub Action triggered
  │     │
  │     ├─> Transform to plugin structure
  │     ├─> Generate plugin.json, README, etc.
  │     └─> Push to nabledge (dummy-to branch)
  │
  └─> Users: /plugin marketplace add nablarch/nabledge
```

### Release Process

1. **Prepare release** in nabledge-dev:
   - Update `.claude/skills/nabledge-6/plugin/plugin.json` version (e.g., `0.1.0` → `0.2.0`)
   - Update `.claude/skills/nabledge-6/plugin/CHANGELOG.md` with release notes
   - Update docs if needed
   - Test locally

2. **Push to dummy-from**:
   - GitHub Action syncs to nabledge (dummy-to)

3. **Create release** in nabledge repository:
   - Tag release (e.g., `v0.2.0`)
   - Create GitHub release with changelog
   - Users get automatic update or can pin version

## Branch Strategy

### nabledge-dev

- **dummy-from**: Development branch (push triggers sync)
- **main**: Stable branch (not used for sync)

### nabledge

- **dummy-to**: Distribution branch (receives syncs from dummy-from)
- **main**: Could be used for stable releases (optional)

### Future Consideration

When moving from dummy branches to production:

- **nabledge-dev**: `dummy-from` → `main` (trigger branch for sync)
  - `develop` will be used for development → `main` for releases
- **nabledge**: `dummy-to` → `main` (distribution branch)

Update workflow trigger accordingly when transitioning.

## Implementation Checklist

- [ ] Create `.claude/skills/nabledge-6/plugin/` directory in nabledge-dev
- [ ] Create `plugin.json` in plugin directory
- [ ] Create `README.md` in plugin directory
- [ ] Create or copy `LICENSE` to plugin directory
- [ ] Create `CHANGELOG.md` in plugin directory
- [ ] Create transform-to-plugin.sh script
- [ ] Update sync-to-nabledge.yml workflow
  - [ ] Add transformation steps to move plugin files
  - [ ] Add CHANGELOG.md update with sync info
  - [ ] Add validation steps
- [ ] Test locally with transform script
- [ ] Test GitHub Action with dummy-from push
- [ ] Verify nabledge repository structure
- [ ] Test plugin installation: `/plugin marketplace add nablarch/nabledge`
- [ ] Test plugin usage: `/nabledge-6`
- [ ] Document release process
- [ ] Update nabledge-dev README with distribution info

## Future Enhancements

1. **Automated testing**: Run nabledge-6 skill tests before sync
2. **Version bumping**: Auto-increment version based on commit messages
3. **Release automation**: Auto-create GitHub releases with tags
4. **Marketplace submission**: Submit to official Claude Code marketplace
5. **Multi-version support**: Support Nablarch 5 and 6 simultaneously

## References

- [Claude Code Plugin Specification](https://claude.com/docs/plugins)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
