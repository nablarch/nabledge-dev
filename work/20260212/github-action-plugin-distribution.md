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
│           └── docs/
│               ├── features/
│               ├── checks/
│               └── releases/
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
| (not exists) | `.claude-plugin/plugin.json` | Generate |
| (not exists) | `README.md` | Generate |
| (not exists) | `LICENSE` | Copy or Generate |
| (not exists) | `CHANGELOG.md` | Generate |

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
   - Generate `plugin.json` manifest
   - Move `SKILL.md` to `skills/nabledge-6/SKILL.md`
   - Move `workflows/`, `assets/`, `knowledge/`, `docs/` to root
   - Generate `README.md` if not exists
   - Copy or generate `LICENSE` if not exists
   - Update or generate `CHANGELOG.md`
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
```

#### Step 4: Generate plugin.json

```yaml
- name: Generate plugin.json
  run: |
    cat > nabledge-repo/.claude-plugin/plugin.json <<'EOF'
    {
      "name": "nabledge-6",
      "version": "0.1.0",
      "description": "Nablarch 6 framework knowledge base and code analysis for Claude Code",
      "author": {
        "name": "TIS Inc.",
        "url": "https://github.com/nablarch"
      },
      "homepage": "https://github.com/nablarch/nabledge",
      "repository": "https://github.com/nablarch/nabledge",
      "license": "Apache-2.0",
      "keywords": ["nablarch", "nablarch-6", "java", "batch", "rest", "jakarta-ee"]
    }
    EOF
```

**Note**: Version should be dynamic (extracted from tags or VERSION file)

#### Step 5: Generate README.md

```yaml
- name: Generate README.md
  run: |
    if [ ! -f nabledge-repo/README.md ]; then
      cat > nabledge-repo/README.md <<'EOF'
    # Nabledge-6: Nablarch 6 Plugin for Claude Code

    [Content to be generated - see README Template section below]
    EOF
    fi
```

#### Step 6: Copy LICENSE

```yaml
- name: Copy LICENSE
  run: |
    if [ ! -f nabledge-repo/LICENSE ]; then
      # Copy from nabledge-dev or generate
      if [ -f LICENSE ]; then
        cp LICENSE nabledge-repo/
      else
        # Generate Apache 2.0 license
        cat > nabledge-repo/LICENSE <<'EOF'
        [Apache 2.0 license text]
        EOF
      fi
    fi
```

#### Step 7: Update CHANGELOG.md

```yaml
- name: Update CHANGELOG.md
  run: |
    TRIGGER_COMMIT_SHA="${{ github.sha }}"
    TRIGGER_COMMIT_URL="https://github.com/${{ github.repository }}/commit/${TRIGGER_COMMIT_SHA}"
    DATE=$(date +%Y-%m-%d)

    if [ ! -f nabledge-repo/CHANGELOG.md ]; then
      # Create initial CHANGELOG
      cat > nabledge-repo/CHANGELOG.md <<EOF
    # Changelog

    ## [0.1.0] - ${DATE}

    ### Added
    - Initial release
    - Synced from: ${TRIGGER_COMMIT_URL}
    EOF
    else
      # Append sync entry
      sed -i "/^# Changelog/a \\\n## [Unreleased] - ${DATE}\\\n\\\n### Changed\\\n- Synced from: ${TRIGGER_COMMIT_URL}\\\n" nabledge-repo/CHANGELOG.md
    fi
```

#### Step 8: Commit and push

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

The generated README.md should include:

```markdown
# Nabledge-6: Nablarch 6 Plugin for Claude Code

Structured knowledge base for Nablarch 6 framework with code analysis capabilities.

## Features

- **Knowledge Search**: Query Nablarch 6 APIs, patterns, configurations
- **Code Analysis**: Analyze existing Nablarch code and generate documentation

## Installation

### Prerequisites

- [Claude Code CLI](https://claude.com/claude-code) installed
- Nablarch 6 project

### Install Plugin

```bash
# In Claude Code
/plugin marketplace add nablarch/nabledge

# Enable plugin (if not auto-enabled)
/plugin enable nabledge-6
```

## Usage

### Interactive Mode

```bash
/nabledge-6
```

Shows greeting and lets you choose between knowledge search and code analysis.

### Knowledge Search

```bash
/nabledge-6 "UniversalDaoの使い方"
/nabledge-6 "バッチ処理の実装方法"
```

### Code Analysis

```bash
/nabledge-6 code-analysis
```

Then specify target code (class, feature, or package).

## Knowledge Coverage

- Nablarch batch processing (On-demand)
- RESTful web services (JAX-RS)
- Core handlers (DB connection, transaction, data read)
- Core libraries (UniversalDao, database access, validation, etc.)
- Testing framework (NTF)
- Security checklist

See [docs/](docs/) for detailed knowledge documentation.

## Scope

### In Scope

- Nablarch Batch (On-demand)
- RESTful Web Services

### Out of Scope

- Jakarta Batch
- Resident Batch (Table Queue)
- Web Applications (JSP/UI)
- Messaging (MOM)

## Version

- **Target**: Nablarch 6u2 / 6u3
- **Plugin Version**: 0.1.0

## License

Apache License 2.0 - See [LICENSE](LICENSE)

## Repository

- **Distribution**: https://github.com/nablarch/nabledge
- **Development**: https://github.com/nablarch/nabledge-dev
```

## Version Management Strategy

### Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Incompatible API changes (e.g., SKILL.md structure change)
- **MINOR**: New knowledge files, new features (backward compatible)
- **PATCH**: Bug fixes, knowledge corrections

### Version Sources

**Option 1: Git Tags** (Recommended)

```bash
# Extract version from latest tag
VERSION=$(git describe --tags --abbrev=0)
```

**Option 2: VERSION file**

Create `VERSION` file in nabledge-dev:

```
0.1.0
```

Workflow reads this file and uses it in plugin.json.

**Option 3: Manual in plugin.json template**

Store plugin.json template in nabledge-dev repository, update manually.

### Recommendation

Use **Option 2 (VERSION file)** for simplicity:

1. Create `VERSION` file in nabledge-dev
2. Update version when releasing
3. GitHub Action reads VERSION and generates plugin.json
4. Tag nabledge repository with same version

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
   - Update VERSION file (e.g., `0.1.0` → `0.2.0`)
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

- nabledge-dev: `dummy-from` → `develop` or `main`
- nabledge: `dummy-to` → `main`

Update workflow trigger accordingly.

## Implementation Checklist

- [ ] Create VERSION file in nabledge-dev
- [ ] Create transform-to-plugin.sh script
- [ ] Update sync-to-nabledge.yml workflow
  - [ ] Add transformation steps
  - [ ] Add plugin.json generation
  - [ ] Add README.md generation
  - [ ] Add LICENSE copy
  - [ ] Add CHANGELOG.md update
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
