# Claude Code Plugin Structure Design for Nabledge

## Problem Statement

The current nabledge-6 skill is structured for local development (`.claude/skills/nabledge-6/`) but does not conform to Claude Code Plugin distribution specification. According to the official specification, plugins must have:

1. Plugin root directory at top level (not inside `.claude/`)
2. `.claude-plugin/plugin.json` manifest at plugin root
3. Component directories (`skills/`, `commands/`, etc.) at plugin root level
4. Distribution package structure for marketplace or git-based installation

## Claude Code Plugin Specification Summary

### Required Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Manifest (ONLY file in .claude-plugin/)
├── skills/                  # At root, NOT inside .claude-plugin/
├── commands/                # At root
├── agents/                  # At root
├── hooks/                   # At root
├── .mcp.json               # At root
├── README.md
├── LICENSE
└── CHANGELOG.md
```

### Key Rules

- **Component directories must be at plugin root**, not inside `.claude-plugin/`
- **Only plugin.json goes inside `.claude-plugin/`**
- Plugin name uses kebab-case (e.g., `nabledge-6`)
- Skills are namespaced: `/plugin-name:skill-name`
- Distribution via Git repository or marketplace catalog

### Distribution Methods

1. **Git Repository** (Recommended): Users run `/plugin marketplace add owner/repo`
2. **Marketplace Catalog**: Define `marketplace.json` listing multiple plugins
3. **Local Development**: Use `claude --plugin-dir ./plugin-name`

## Current Structure (Development)

```
nabledge-dev/
└── .claude/
    └── skills/
        └── nabledge-6/
            ├── SKILL.md
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
            └── docs/
                ├── features/
                ├── checks/
                └── releases/
```

**Issues**:
- ❌ No plugin.json manifest
- ❌ Skill is in `.claude/skills/` (local project structure)
- ❌ Not distributable as standalone plugin

## Proposed Structure (Distribution)

### Option 1: Dedicated Plugin Repository

Create separate repository for distribution:

```
nabledge-6/                        # Plugin root (new repo)
├── .claude-plugin/
│   └── plugin.json                # Manifest
├── skills/
│   └── nabledge-6/
│       └── SKILL.md               # Main skill definition
├── workflows/                     # Supporting files at root
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
├── docs/                          # Human-readable docs
│   ├── features/
│   ├── checks/
│   └── releases/
├── README.md                      # Installation & usage
├── LICENSE
└── CHANGELOG.md
```

**Installation**: `claude plugin add github:owner/nabledge-6`

### Option 2: Monorepo with Distribution Directory

Keep development in `nabledge-dev`, add distribution build:

```
nabledge-dev/
├── .claude/
│   └── skills/
│       └── nabledge-6/            # Development version (local testing)
│           └── [same structure]
│
└── dist/                          # Distribution build
    └── nabledge-6/                # Plugin root (for distribution)
        ├── .claude-plugin/
        │   └── plugin.json
        ├── skills/
        │   └── nabledge-6/
        │       └── SKILL.md
        ├── workflows/
        ├── assets/
        ├── knowledge/
        ├── docs/
        ├── README.md
        ├── LICENSE
        └── CHANGELOG.md
```

**Installation**: `claude plugin add github:owner/nabledge-dev/dist/nabledge-6`

### Option 3: GitHub Actions Build Pipeline

Keep source in `.claude/skills/nabledge-6/`, build distribution package via CI:

```
nabledge-dev/
├── .claude/
│   └── skills/
│       └── nabledge-6/            # Source
│
├── .github/
│   └── workflows/
│       └── build-plugin.yml       # Build dist/ on push
│
└── dist/                          # Built by CI (gitignored or committed)
    └── nabledge-6/
```

**Pros**: Single source of truth, automated builds
**Cons**: More complex setup

## Recommended Approach: Option 1 (Dedicated Repository)

### Rationale

1. **Clear separation**: Development (nabledge-dev) vs Distribution (nabledge-6)
2. **Simple installation**: Users just add plugin via git URL
3. **Independent versioning**: Plugin releases independent of dev repo
4. **Standard practice**: Aligns with Claude Code plugin ecosystem

### Implementation Plan

1. **Create new repository**: `nabledge-6` (or `claude-plugin-nabledge-6`)
2. **Copy skill structure** from `.claude/skills/nabledge-6/`
3. **Restructure to plugin format**:
   - Create `.claude-plugin/plugin.json`
   - Move SKILL.md to `skills/nabledge-6/SKILL.md`
   - Keep workflows/, assets/, knowledge/, docs/ at root
4. **Add distribution files**:
   - README.md with installation instructions
   - LICENSE (Apache 2.0 / MIT)
   - CHANGELOG.md
5. **Test locally**: `claude --plugin-dir ./nabledge-6`
6. **Publish**: Push to GitHub, users add via `/plugin marketplace add owner/nabledge-6`

### plugin.json Content

```json
{
  "name": "nabledge-6",
  "version": "0.1.0",
  "description": "Nablarch 6 framework knowledge base and code analysis for Claude Code",
  "author": {
    "name": "Nabledge Team",
    "email": "contact@example.com"
  },
  "homepage": "https://github.com/owner/nabledge-6",
  "repository": "https://github.com/owner/nabledge-6",
  "license": "Apache-2.0",
  "keywords": ["nablarch", "nablarch-6", "java", "batch", "rest", "jakarta-ee"]
}
```

### README.md Sections

1. **Installation**: How to add plugin via `/plugin marketplace add`
2. **Usage**: Basic commands (`/nabledge-6`, `/nabledge-6 "question"`, `/nabledge-6 code-analysis`)
3. **Features**: Knowledge search, code analysis
4. **Requirements**: Nablarch 6 project, Claude Code CLI
5. **Documentation**: Link to full documentation
6. **License**: Apache 2.0 / MIT

## Development Workflow

### Development Phase (nabledge-dev)

1. Edit `.claude/skills/nabledge-6/SKILL.md`
2. Test locally: `/nabledge-6` in nabledge-dev project
3. Add/update knowledge files in `knowledge/`
4. Update workflows as needed

### Release Phase (nabledge-6 repo)

1. Copy changes from nabledge-dev to nabledge-6 repo
2. Update version in plugin.json
3. Update CHANGELOG.md
4. Test with `claude --plugin-dir ./nabledge-6`
5. Commit and tag release (e.g., `v0.1.0`)
6. Push to GitHub

### User Installation

```bash
# In Claude Code
/plugin marketplace add owner/nabledge-6

# Enable plugin
/plugin enable nabledge-6

# Use skill
/nabledge-6 "UniversalDaoの使い方"
```

## File Mapping: Development → Distribution

| Development (nabledge-dev) | Distribution (nabledge-6) |
|---------------------------|---------------------------|
| `.claude/skills/nabledge-6/SKILL.md` | `skills/nabledge-6/SKILL.md` |
| `.claude/skills/nabledge-6/workflows/` | `workflows/` (at root) |
| `.claude/skills/nabledge-6/assets/` | `assets/` (at root) |
| `.claude/skills/nabledge-6/knowledge/` | `knowledge/` (at root) |
| `.claude/skills/nabledge-6/docs/` | `docs/` (at root) |
| (not exists) | `.claude-plugin/plugin.json` (new) |
| (not exists) | `README.md` (new) |
| (not exists) | `LICENSE` (new) |
| (not exists) | `CHANGELOG.md` (new) |

## Next Steps

1. **Decide**: Confirm Option 1 (Dedicated Repository) is the right approach
2. **Create plugin.json**: Define metadata
3. **Restructure**: Create nabledge-6 plugin structure
4. **Write README.md**: Installation and usage instructions
5. **Add LICENSE**: Choose Apache 2.0 or MIT
6. **Create CHANGELOG.md**: Version 0.1.0 initial release
7. **Test locally**: Validate plugin structure with `claude --plugin-dir`
8. **Publish**: Push to GitHub repository
9. **Update nabledge-dev**: Add sync workflow to copy changes to distribution repo

## Questions for User

1. **Repository naming**: Prefer `nabledge-6` or `claude-plugin-nabledge-6`?
2. **License**: Apache 2.0 or MIT?
3. **Author info**: Email and homepage for plugin.json?
4. **Marketplace**: Plan to submit to official Claude Code marketplace?
5. **Sync strategy**: Manual sync or automated (GitHub Actions)?

## References

- [Claude Code Plugin Documentation](https://claude.com/docs/plugins)
- [Plugin Manifest Specification](https://claude.com/docs/plugins/manifest)
- [Plugin Distribution Guide](https://claude.com/docs/plugins/distribution)
