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

## Writing Guidelines

**Target audience**: End users (Japanese Nablarch developers)

**Writing style**:
- Use user-friendly language - describe what improved, not technical details
- Focus on user impact - what users can now do or what problems were fixed
- Keep entries consistent - use "〜問題を修正しました" format for fixes
- Avoid unnecessary details - no disk space savings, performance metrics, etc.
- Be concise - one sentence per entry

**Examples**:

Good:
- コード分析結果のリンクが正しく遷移しない問題を修正しました
- 知識検索で、より適切なドキュメントが選ばれるようになりました

Bad:
- 相対パス計算のバグを修正しました（技術詳細）
- ディスク容量を節約できます（余計な情報）
- prefill-template.shが絶対パスを処理（ユーザーには無関係）

## Release Workflow (nabledge-dev)

When preparing a release in this repository:
1. Move [Unreleased] content to new version section with date
2. **Remove empty [Unreleased] section** (add it back in next development)
3. Update version in metadata files
4. Create release PR to main
5. After merge, changes sync to nablarch/nabledge:develop
6. In nablarch/nabledge: Create release PR from develop to main, tag and release
