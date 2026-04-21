# Notes

## 2026-03-13

### Step 1: Commit Analysis Since v0.5 (2026-03-10)

Base commit: `19e15367` (release: nabledge-6 v0.5)

| Commit | Summary | Deployed? | Reason |
|--------|---------|-----------|--------|
| `0f73f58f` | feat: Generate nabledge-5 knowledge files | YES | `.claude/skills/nabledge-5/docs/`, `knowledge/` |
| `1fd21a11` | fix: use Nablarch 5-specific doc URLs in nabledge-5 templates | YES | `.claude/skills/nabledge-5/assets/` |
| `8b452553` | chore: remove .gitattributes | NO | `.gitattributes` not in sync manifest |
| `3bbabc86` | docs: verify R2 fabrication findings classification | NO | `.claude/rules/`, `.pr/` not in sync manifest |
| `53cd48b6` | test: add full v6 knowledge benchmark results | NO | test files only |
| `974a55d1` | docs: update README to reflect full Nablarch 6 coverage | NO | dev repo README |
| `574d0cac` | fix: convert CRLF to LF in nabledge-6 assets | YES* | `.claude/skills/nabledge-6/assets/` - line ending only, no functional change |
| `52e22145` | fix: fix Phase C failures for 3 knowledge files | YES | `.claude/skills/nabledge-6/docs/`, `knowledge/` |
| `c0902904` | feat: add nabledge-5 plugin infrastructure | YES | `.claude/skills/nabledge-5/` multiple dirs |
| `ce878842` | chore: start work on grand design update | NO | `docs/grand-design/` not in sync manifest |
| `c9eda00a` | feat: add official_doc_urls and hints to browsable markdown | YES | `.claude/skills/nabledge-6/docs/` |
| `e358dcce` | feat: always log CC call IN/OUT in execution logs | NO | `tools/knowledge-creator/` dev tool |
| `92350bdc` | docs: Translate README.md to Japanese | NO | dev repo README |
| `e108ce62` | feat: externalize version-specific RST mappings to JSON files | NO | `tools/knowledge-creator/` dev tool |

### Version Decision

- nabledge-6: v0.6 (MINOR bump — feature addition: official doc URLs)
- nabledge-5: v0.1 (first release)
- marketplace: v0.6 (= max(0.6, 0.1))

### Previous Release PR Comparison (#156)

Required files: 4 core files
- `.claude/skills/nabledge-6/plugin/CHANGELOG.md` ✓
- `.claude/skills/nabledge-6/plugin/plugin.json` ✓
- `.claude/marketplace/.claude-plugin/marketplace.json` ✓
- `.claude/marketplace/CHANGELOG.md` ✓

**Result**: All 4 core files present in PR #196 ✓

This release adds nabledge-5 first release, so also included:
- `.claude/skills/nabledge-5/plugin/CHANGELOG.md` ✓ (add v0.1 entries)
- `.claude/skills/nabledge-5/plugin/plugin.json` — already at 0.1, no change needed ✓

`.claude/rules/release.md` and `.pr/00154/notes.md` in #156 are not release-specific, ignored.
