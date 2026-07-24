# Notes: Release 1.0 (issue #408)

## 2026-07-24

### Commit analysis since marketplace 0.11

Previous release commit: 3c08678f — docs: release marketplace 0.11 — QA/code-analysis output improvements (#399) (#400)

| Commit | Message | User impact | Reason |
|--------|---------|-------------|--------|
| 4068bc85 | docs: add benchmark review report (#392) (#397) | NO | Changes only in `.rn/` and `docs/reports/` — dev-only, not in deployed content scope |
| 850f75c6 | chore: update metrics report (20260719) (#403) | NO | Changes only in `docs/metrics.md` and `tools/metrics/` — dev-only |
| f78935f7 | fix: remove ineffective Write/Glob deny rules from settings.json (#402) | NO | Changes only in `.claude/settings.json` — repository infrastructure, not in deployed content scope |
| 02aead4b | chore: update metrics report (20260712) (#401) | NO | Changes only in `docs/metrics.md` and `tools/metrics/` — dev-only |
| 5a51213a | chore: start session — issue-408 | NO | Changes only in `.rn/` — session tracking, dev-only |
| 750bd16e | chore: update steering.md — align tasks with release.md steps | NO | Changes only in `.rn/` — session tracking, dev-only |
| 989db060 | docs: add release commit analysis for marketplace 1.0 | NO | Changes only in `.work/00408/` — dev-only work log |

**Summary**: 7 commits total, 0 with user impact, 7 dev-only

### Verification against previous release PR

Previous release PR: #400 — docs: release marketplace 0.11 — QA/code-analysis output improvements (#399)

**Previous release files (release-essential only)**:
- `.claude/marketplace/.claude-plugin/marketplace.json`
- `.claude/marketplace/CHANGELOG.md`
- `.claude/skills/nabledge-1.2/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.2/plugin/plugin.json`
- `.claude/skills/nabledge-1.3/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.3/plugin/plugin.json`
- `.claude/skills/nabledge-1.4/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.4/plugin/plugin.json`
- `.claude/skills/nabledge-5/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-5/plugin/plugin.json`
- `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-6/plugin/plugin.json`

(Non-release-essential excluded: `.claude/rules/release.md`, `.rn/`, `.work/00399/`)

**Current release files (release-essential)**:
- `.claude/marketplace/.claude-plugin/marketplace.json`
- `.claude/marketplace/CHANGELOG.md`
- `.claude/skills/nabledge-1.2/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.2/plugin/plugin.json`
- `.claude/skills/nabledge-1.3/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.3/plugin/plugin.json`
- `.claude/skills/nabledge-1.4/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-1.4/plugin/plugin.json`
- `.claude/skills/nabledge-5/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-5/plugin/plugin.json`
- `.claude/skills/nabledge-6/plugin/CHANGELOG.md`
- `.claude/skills/nabledge-6/plugin/plugin.json`

**Comparison**: All required files present — exact match with previous release PR's release-essential set.
