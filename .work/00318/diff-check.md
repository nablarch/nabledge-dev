# Diff Check: PR #328

**Base**: `7c6a2de2b` (main at PR creation time)
**HEAD**: `2dbd32f6b`
**Total**: 63 files changed, 191 insertions(+), 142 deletions(-)

## Result: PASS

All changes are expected. No unexpected files.

## File Categories

### Mapping fix (root cause)
- `tools/rbkc/mappings/v5.json` — corrected pattern: `application_framework/setting_guide/` → `application_framework/application_framework/setting_guide/`
- `tools/rbkc/mappings/v6.json` — same fix

### Regenerated knowledge files (nabledge-5)
7 setting-guide JSON files moved from `about/about-nablarch/` → `setup/setting-guide/` (rename)
Other JSON files: minor content updates from re-generation

### Regenerated docs MD (nabledge-5)
7 setting-guide MD files moved from `about/about-nablarch/` → `setup/setting-guide/` (rename)
Other MD files: minor content updates from re-generation

### Regenerated knowledge files (nabledge-6)
7 setting-guide JSON files moved from `about/about-nablarch/` → `setup/setting-guide/` (rename)
Other JSON files: minor content updates from re-generation

### Regenerated docs MD (nabledge-6)
7 setting-guide MD files moved from `about/about-nablarch/` → `setup/setting-guide/` (rename)
Other MD files: minor content updates from re-generation

### Work log
- `.work/00318/tasks.md` — task tracking file

## Unexpected Changes

None. All 63 files are accounted for by:
1. The mapping fix (2 files)
2. Regenerated outputs for v5 and v6 (60 files — setting-guide reclassification + cascading index/README updates)
3. Work log (1 file)
