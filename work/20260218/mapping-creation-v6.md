# Mapping Creation for Nablarch v6

**Date**: 2026-02-18
**Status**: Procedure revised, ready to execute

## Summary

Prepared category-driven mapping creation procedure for Nablarch v6 knowledge file generation following `doc/mapping-creation/mapping-creation-prompt.md` (Version 3.0).


## Prompt Revisions

### Revision 1: Category-Driven Approach
- Added `security-check` category to v5 and v6 definitions
- Clarified that category definitions are the target vocabulary
- Step 3: Load categories, apply path pattern rules to assign category IDs
- Step 4: Use category definitions in AI judgment
- Step 5: Map category IDs to target directory structure
- Support multiple categories per file

### Revision 2: Source File Selection
- **Excluded**: All archetype files (`nablarch-*-archetype`)
- **Development Guide**: Japanese version only
  - Nablarch patterns: `Nablarchシステム開発ガイド/docs/nablarch-patterns/` (except README.md)
  - Security matrix: `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
- Security matrix categorized as `dev-guide-other` → `guides/patterns/`

## Next Steps

Execute mapping creation following the revised procedure:
1. Run Step 1: Process dev guide files (Japanese patterns + security matrix)
2. Run Step 2-3: Extract and categorize nab-doc files
3. Run Step 4: AI judgment for uncategorized files
4. Run Step 5-9: Generate targets, validate, output
5. Run Step 10: Export to Excel for review
