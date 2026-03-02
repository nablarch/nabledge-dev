# Bug Fixes - Knowledge Creator

**Date**: 2026-03-02
**Issue**: #103
**Branch**: 99-nabledge-creator-tool

## Issues Fixed

### 1. Path Duplication Bug (Critical)

**Location**: `steps/step3_generate.py` lines 118, 133

**Problem**: Generated files were created in wrong location with duplicated path:
```
❌ Wrong: /home/.../work3/home/.../work3/.claude/skills/nabledge-6/knowledge/...
✅ Correct: /home/.../work3/.claude/skills/nabledge-6/knowledge/...
```

**Root Cause**: The code incorrectly prefixed `ctx.knowledge_dir` with `ctx.repo`, but `ctx.knowledge_dir` already contains the full path (defined in `run.py` line 60).

**Fix**:
```python
# Before (WRONG):
output_path = f"{self.ctx.repo}/{self.ctx.knowledge_dir}/{file_info['output_path']}"
assets_dir_abs = f"{self.ctx.repo}/{self.ctx.knowledge_dir}/{assets_dir_rel}"

# After (CORRECT):
output_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
assets_dir_abs = f"{self.ctx.knowledge_dir}/{assets_dir_rel}"
```

**Impact**:
- All 30 successfully generated files were in wrong location
- Validation couldn't find any files (json_files=0)
- Created untracked `home/` directory in repository root

### 2. Timeout Too Short

**Location**: `steps/step3_generate.py` line 144

**Problem**: The "tag" file generation timed out at 600 seconds (10 minutes).

**Fix**: Increased timeout from 600 to 900 seconds (15 minutes):
```python
# Before:
result = run_claude(prompt, timeout=600)

# After:
result = run_claude(prompt, timeout=900)
```

**Rationale**: Complex documentation files may need more than 10 minutes for AI processing.

## Verification

### Path Logic Test

Run the included test script:
```bash
cd tools/knowledge-creator
python test_paths.py
```

Expected output:
```
✅ All path construction tests passed!

Path structure is correct:
  - No duplication of '/home/.../work3'
  - Files will be created in correct location
  - Validation will find the generated files
```

### Full Test (Must Run Outside Claude Code)

**IMPORTANT**: The tool uses `claude -p` and **cannot** be run from within a Claude Code session.

To test the fixes:

1. **Exit Claude Code** (or run in separate terminal without CLAUDECODE env var)

2. **Run test mode**:
   ```bash
   cd /home/tie303177/work/nabledge/work3
   python tools/knowledge-creator/run.py --version 6 --test-mode
   ```

3. **Verify success**:
   - All 31 test files should generate successfully (including "tag")
   - Files should be in `.claude/skills/nabledge-6/knowledge/`
   - No `home/` directory should be created
   - Validation should find all 31 files (json_files=31)

## Before/After Comparison

### Before Fixes

```
Generation: 30 OK, 1 Error (timeout)
Validation: json_files=0 (files in wrong location)
Created: work3/home/.../work3/.claude/skills/nabledge-6/knowledge/...
```

### After Fixes

```
Generation: 31 OK, 0 Errors (with longer timeout)
Validation: json_files=31 (files in correct location)
Created: work3/.claude/skills/nabledge-6/knowledge/...
```

## Related Files

- `tools/knowledge-creator/steps/step3_generate.py` - Fixed file
- `tools/knowledge-creator/test_paths.py` - Verification test
- `tools/knowledge-creator/run.py` - Context definitions
