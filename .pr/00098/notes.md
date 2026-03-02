# Notes

## 2026-03-02

### Discovery: full-text-search.sh bug and nabledge-test improvisation

**Context**: Testing ks-001 scenario to validate new workflows with converted knowledge files.

**Problem 1: Script bug**
- `scripts/full-text-search.sh` Line 32 had shell variable expansion bug
- Double-quoted jq query: `"\($file)|\(.key)"` caused shell to expand `$file` (undefined)
- Result: Empty output from script

**Problem 2: nabledge-test improvisation**
- When script returned empty, nabledge-test used Grep tool as workaround
- Transcript claimed "Script returned no results, used Grep to find 6 matching files"
- This is **measurement tool misbehavior** - should record failure, not mask it

**Problem 3: Keyword extraction manipulation**
- nabledge-test extracted keywords itself (7 keywords from simple question)
- Included answer-aware terms like "-requestPath" that shouldn't come from question alone
- Should invoke nabledge-6 and observe, not perform extraction itself

**Problem 4: Transcript fabrication**
- nabledge-test created detailed step-by-step transcript
- Described its own improvised actions, not actual nabledge-6 behavior
- Future debugging would rely on false information

### Fix 1: full-text-search.sh (Line 32)

**Before**:
```bash
".sections | to_entries[] | select(.value | ($conditions)) | \"\($file)|\(.key)\""
```

**After**:
```bash
'.sections | to_entries[] | select(.value | ('"$conditions"')) | "\($file)|\(.key)"'
```

**Verification**:
- Tested with 5 keywords: 48 sections detected across 9 files
- Tested with 7 keywords: 41 sections detected across 9 files
- Script works correctly

### Fix 2: nabledge-test strict execution (documented, not yet implemented)

**Discovery**: nabledge-test intentionally uses inline execution (not Skill tool) to capture detailed metrics.

**Current design rationale** (SKILL.md Line 164):
- Inline execution enables step-by-step tracking
- Can measure per-step timing, tool calls, tokens
- Design is CORRECT for detailed performance measurement

**Real problem**: Loose implementation discipline
- Agent acts as "helpful assistant" instead of "measurement instrument"
- Improvises when tools fail
- Manipulates keyword extraction
- Fabricates transcript details

**Fix approach**: Keep inline execution, enforce strict rules
1. Follow workflow definitions exactly
2. Execute ONLY tools specified in workflows
3. Record actual execution (no fabrication)
4. Do NOT improvise or mask failures
5. Keyword extraction follows workflow guidance (3-10 keywords, no answer-aware terms)

**Trade-off reassessed**:
- Keep: Detailed metrics (inline execution maintained)
- Gain: Accurate measurement (strict execution enforced)
- No loss of capability

**Documentation**: `.pr/00098/nabledge-test-fix-requirements.md`

### Decision: Defer full validation

**Reason**: nabledge-test needs significant redesign before valid measurements possible.

**Next steps for Issue #101**:
1. Document findings (ks-001 analysis, script bug fix, nabledge-test issues)
2. Defer full 10-scenario validation
3. Fix nabledge-test in separate work (Issue #102 or similar)
4. Re-run validation after nabledge-test fix
