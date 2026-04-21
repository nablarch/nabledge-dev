# Notes

## 2026-03-27

### Release v0.7 Analysis

**Commits since v0.6 (2026-03-13) affecting deployed content:**
- `434685a5` feat: generate nabledge-1.4 knowledge files and baseline (#122) (#224) — nabledge-1.4 new plugin
- `fc356bfd` docs: add troubleshooting section to install guides (#211) (#212) — nabledge-6 GUIDE-CC/GHC updated

**Version decisions:**
- nabledge-6: 0.6 → 0.7 (minor: troubleshooting docs added)
- nabledge-5: unchanged at 0.1
- nabledge-1.4: 0.1 (first release, included in marketplace 0.7)
- Marketplace: 0.7 (highest changed plugin version)

**nabledge-1.4 tag link:** Points to `releases/tag/0.7` (the marketplace release where it first appears)

### Comparison with PR #196 (v0.6 release)

Previous release PR #196 updated:
- `.claude/marketplace/.claude-plugin/marketplace.json` ✅
- `.claude/marketplace/CHANGELOG.md` ✅
- `.claude/skills/nabledge-5/plugin/CHANGELOG.md` (nabledge-5 had first release then)
- `.claude/skills/nabledge-6/plugin/CHANGELOG.md` ✅
- `.claude/skills/nabledge-6/plugin/plugin.json` ✅
- `.pr/00195/notes.md` (work log, not release-specific)

This PR updates the same required files plus adds:
- `.claude/skills/nabledge-1.4/plugin/CHANGELOG.md` (nabledge-1.4 first release)

nabledge-5's CHANGELOG/plugin.json not updated because nabledge-5 has no changes since v0.1.
