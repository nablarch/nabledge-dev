# Simplify Mapping Procedure with Whitelist Approach

**Date**: 2026-02-18

## Summary

Simplified mapping creation procedure by adopting whitelist approach in Phase 2, eliminating need for Phase 5.5 (blacklist filtering), and adding index.json prohibition rule.

## Problems Identified

### 1. Phase Ordering Issue
- **Current**: Phase 5 (AI categorization) → Phase 5.5 (filtering) → removed 153 entries
- **Problem**: Wasted AI判断 on 153 entries that would be filtered out
- **Solution**: Move filtering to Phase 2 as whitelist collection

### 2. Archetype Content Unnecessarily Included
- **Included**: pom.xml, .config (SpotBugs), config.txt (JSP analysis)
- **Problem**: Archetype content available via static analysis
- **Decision**: Exclude entirely per procedure design ("static analysis available")

### 3. Project-Specific Content Included
- **Included**: Sample_Project/docs/ (UI customization, project setup guides)
- **Problem**: Project-specific, not framework-level knowledge
- **Solution**: Exclude via whitelist (only security mapping needed)

### 4. index.json Problem
- **Problem**: Many index.rst files mapped to index.json, losing specificity
- **Solution**: Prohibit index.json filename, require content-based naming

## Changes Made

### 1. Scope Definition (mapping-creation-procedure.md)

**Before (Blacklist)**:
- Collect everything
- Filter out archetype, Sample_Project, tests, license in Phase 5.5

**After (Whitelist)**:
```markdown
**Included in Mapping (Whitelist Approach)**:
1. ✅ nablarch-document - All .rst, .md, config.txt
2. ✅ nablarch-system-development-guide - nablarch-patterns/*.md only
3. ✅ Security mapping - Nablarch機能のセキュリティ対応表.xlsx only
Excluded: archetype (entire), Sample_Project (except security), docs/, tooling files
```

### 2. Phase 2 Script (02-collect-files.sh)

**Completely rewritten** to whitelist approach:
- nablarch-document: All files
- nablarch-patterns: Only nablarch-patterns/*.md
- Security mapping: Only セキュリティ対応表.xlsx
- Removed: archetype collection, Sample_Project collection

**Expected count**: ~340 files (vs ~600 before)

### 3. Phase 5.5 Deletion

**Removed entire section**: No longer needed with whitelist collection
- Eliminated: Blacklist filtering logic
- Eliminated: Category-based filtering
- Eliminated: Path pattern matching

### 4. Phase 6 - index.json Prohibition

**Added rule**:
```markdown
- **NEVER use "index.json"**: Even for index.rst files, use content-based names
  - ❌ Bad: "features/processing/index.json"
  - ✅ Good: "features/processing/batch-application-overview.json"
  - Read the file content and name based on what it describes
```

### 5. Procedure Overview Table

**Updated** to reflect Phase 5.5 removal:
- Phase 2: "Collect source files (whitelist)"
- Phase 5.5: Deleted row
- Other phases: Renumbering not needed (kept as-is)

### 6. Success Criteria

**Updated coverage expectations**:
- Before: ~345 entries after filtering
- After: ~340 entries from whitelist collection
- Breakdown: ~335 from document, ~4 from patterns, ~1 security mapping

## Benefits

### 1. Efficiency
- Eliminated AI judgment on 153 unnecessary entries
- Phase 2 now explicitly defines what to collect
- No filtering phase needed

### 2. Clarity
- Whitelist approach makes scope explicit
- No ambiguity about what's included/excluded
- Easier to maintain and modify

### 3. Simplicity
- One less phase (5.5 deleted)
- Simpler procedure to follow
- Fewer intermediate files

### 4. Specificity
- index.json prohibition forces meaningful names
- Each knowledge file has descriptive name
- Easier to navigate knowledge base

## Impact on Existing Mapping

The current mapping-v6.json needs to be recreated:
1. Archetypeエントリが含まれている (19 entries)
2. Sample_Projectエントリが含まれている (132 entries)
3. index.jsonターゲットが多数ある (77 entries)

These issues will be resolved by following the updated procedure.

## Files Modified

1. **mapping-creation-procedure.md**:
   - Scope definition (whitelist approach)
   - Phase 2 description
   - Phase 3 description (.xlsx support)
   - Phase 5.5 section deleted
   - Phase 6 index.json prohibition added
   - Procedure overview table
   - Success criteria

2. **02-collect-files.sh**:
   - Complete rewrite for whitelist approach
   - nablarch-document only
   - nablarch-patterns whitelist
   - Security mapping whitelist
   - Updated statistics generation

## Next Steps

When recreating mapping:
1. Run new Phase 2 (whitelist collection)
2. Skip Phase 5.5 (deleted)
3. In Phase 6, avoid index.json names
4. Expect ~340 entries (not ~372)
