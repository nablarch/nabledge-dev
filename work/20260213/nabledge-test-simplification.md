# Nabledge-Test Simplification

**Date**: 2026-02-13
**Branch**: issue-15
**Commit**: 38c47bb

## Summary

Drastically simplified nabledge-test by using skill-creator's eval format directly instead of custom scenario format.

## Problem

Initial implementation was **over-engineered**:
- Custom scenario format (question, expected_keywords, expected_sections)
- Conversion script (convert_scenario.py)
- Complex SKILL.md (~300 lines)
- Unnecessary abstraction layer

## Solution

**Use eval format directly**:
- scenarios.json uses skill-creator's native format
- No conversion needed
- Thin wrapper (115 lines SKILL.md)

## Changes

### 1. Converted scenarios.json to eval format

**Before** (custom format):
```json
{
  "id": "handlers-001",
  "question": "データリードハンドラでファイルを読み込むには？",
  "expected_keywords": ["DataReadHandler", "DataReader"],
  "expected_sections": ["overview", "usage"]
}
```

**After** (eval format):
```json
{
  "id": "handlers-001",
  "prompt": "データリードハンドラでファイルを読み込むにはどうすればいいですか？",
  "expectations": [
    "Response includes 'DataReadHandler'",
    "Response includes 'DataReader'",
    "Response mentions 'overview' or 'usage' sections",
    "Token usage is between 5000 and 15000",
    "Tool calls are between 10 and 20"
  ]
}
```

All 30 scenarios converted.

### 2. Removed convert_scenario.py

No longer needed. Scenarios are directly usable by skill-creator.

### 3. Simplified SKILL.md

**Line count**: 300+ → 115 lines (-62%)

**Content**:
- Simple 3-step workflow
- Load → Invoke skill-creator → Save results
- Minimal documentation
- Delegates to skill-creator

## Architecture

### Before (over-engineered)

```
nabledge-test
  ├── Load custom scenarios
  ├── Convert to eval format
  ├── Call skill-creator
  ├── Parse results
  └── Generate custom reports
```

### After (simple)

```
nabledge-test (thin wrapper)
  ├── Load eval-format scenarios
  ├── Call skill-creator
  └── Save results to work/
```

## Benefits

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Format** | Custom | skill-creator native | No conversion |
| **Scripts** | convert_scenario.py | None | -1 file |
| **SKILL.md** | ~300 lines | 115 lines | -62% |
| **Complexity** | High (custom layer) | Low (thin wrapper) | Much simpler |
| **Maintenance** | Custom logic | Delegate to skill-creator | Less code |

## Workflow

```
1. User: nabledge-test 6 handlers-001

2. Load scenario:
   scenarios/nabledge-6/scenarios.json

3. Invoke skill-creator eval mode:
   - Setup workspace
   - Executor agent: Run nabledge-6 with prompt
   - Grader agent: Evaluate expectations

4. Save results:
   work/YYYYMMDD/test-handlers-001-timestamp.md

5. Display summary
```

## Files Changed

- `.claude/skills/nabledge-test/SKILL.md` - Simplified (300+ → 115 lines)
- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json` - Converted to eval format
- `.claude/skills/nabledge-test/scripts/convert_scenario.py` - Deleted

## Line Count Reduction

```
SKILL.md:                -185 lines
convert_scenario.py:     -100 lines (deleted)
scenarios.json:          +277 lines (but simpler format)
──────────────────────────────────
Net change:              -8 lines (but much simpler)
```

## Key Insight

**Don't create abstraction layers when the underlying tool already has the right interface.**

skill-creator's eval format is exactly what we need. Custom formats add complexity without benefit.

## Next Steps

1. Test new simplified workflow
2. Execute handlers-001 scenario
3. Verify results saved to work/
4. Execute full test suite (--all)

## Commits

- 15a4a54 - Refactor test framework: nabledge-test + skill-creator integration
- e5582ad - Remove unnecessary extraKnownMarketplaces
- 38c47bb - Simplify nabledge-test: use eval format directly
