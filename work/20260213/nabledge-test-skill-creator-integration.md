# Nabledge-Test + Skill-Creator Integration

**Date**: 2026-02-13
**Branch**: issue-15
**PR**: https://github.com/nablarch/nabledge-dev/pull/17

## Summary

Refactored test framework from monolithic nabledge-6-test to layered architecture: nabledge-test (interface) + skill-creator (engine).

## Changes

### 1. Added skill-creator (Claude.ai version)

**Source**: Downloaded from Claude.ai environment (not GitHub version)
**Location**: `.claude/skills/skill-creator/`
**Size**: 762 lines SKILL.md, 4 agent files, 4 reference files, 8 scripts

**Key files**:
- `agents/executor.md` - Execute eval with skill
- `agents/grader.md` - Evaluate expectations
- `agents/analyzer.md` - Pattern analysis
- `references/eval-mode.md` - Eval workflow
- `references/benchmark-mode.md` - Benchmark workflow

**Why Claude.ai version?**
- GitHub version (anthropics/skills) lacks eval/benchmark functionality
- Claude.ai version has production-tested evaluation agents
- Complete feature set for skill testing

### 2. Refactored nabledge-6-test → nabledge-test

**Renamed**: `.claude/skills/nabledge-6-test/` → `.claude/skills/nabledge-test/`

**New structure**:
```
nabledge-test/
├── SKILL.md                         # New: unified interface
├── scenarios/
│   ├── nabledge-6/scenarios.json   # Moved from nabledge-6/tests/
│   └── nabledge-5/                  # Future
├── scripts/convert_scenario.py     # New: scenario → eval conversion
└── templates/                       # Preserved
```

### 3. Updated command syntax

**Before**:
```
/nabledge-6-test execute handlers-001
```

**After**:
```
/nabledge-test 6 handlers-001
```

**Future**:
```
/nabledge-test 5 libraries-001
```

### 4. Updated settings.json

```diff
  "allow": [
-   "Skill(nabledge-6-test)"
+   "Skill(nabledge-test)",
+   "Skill(skill-creator)"
  ]
```

## Architecture

### Before (Monolithic)

```
nabledge-6-test
  ├── Execute workflow manually
  ├── Evaluate manually
  └── Generate reports
```

### After (Layered)

```
nabledge-test (Interface)
  ├── Load scenarios
  ├── Convert to eval format
  └── Generate nabledge reports
          ↓ delegates to
skill-creator (Engine)
  ├── Executor agent
  ├── Grader agent
  └── Analyzer agent
```

## Workflow

```
1. Load scenario
   scenarios/nabledge-6/scenarios.json

2. Convert to eval format
   scripts/convert_scenario.py
   {
     "prompt": "...",
     "expectations": [...]
   }

3. Execute via skill-creator
   - Executor: Run nabledge-6 with prompt
   - Grader: Evaluate expectations

4. Generate report
   work/YYYYMMDD/test-*.md
```

## Benefits

1. **Avoids reinventing the wheel**: Uses Anthropic's proven evaluation framework
2. **Unified testing**: Single interface for nabledge-6 and nabledge-5
3. **Clear separation**: Interface layer vs evaluation engine
4. **Future-proof**: skill-creator updates automatically benefit us
5. **Advanced features**: Benchmark mode, A/B comparison, variance analysis

## Migration Impact

### Preserved

- ✅ 30 test scenarios (handlers, libraries, tools, processing, adapters, code-analysis)
- ✅ Report format (nabledge-specific)
- ✅ Evaluation criteria (6-8 criteria)

### Changed

- ❌ Command syntax: `nabledge-6-test execute` → `nabledge-test 6`
- ❌ Internal workflow: Manual → skill-creator agents

## Test Results

Pre-refactoring test (handlers-001) validated approach:
- 5/6 criteria passed (83%)
- Identified token optimization opportunity
- Confirmed workflow execution

## Next Steps

1. Test new architecture with handlers-001 scenario
2. Verify convert_scenario.py works correctly
3. Execute full test suite (--all)
4. Add nabledge-5 scenarios when nabledge-5 skill is ready

## Files

- `.claude/skills/nabledge-test/` - New unified framework
- `.claude/skills/skill-creator/` - Evaluation engine
- `.claude/settings.json` - Updated permissions
- Removed: `.claude/skills/nabledge-6-test/`

## Commits

1. `464d7ba` - Add nabledge-6-test skill and execute first test scenario
2. `15a4a54` - Refactor test framework: nabledge-test + skill-creator integration
