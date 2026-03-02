# Work Notes - PR #103

## 2026-03-02

### Path Duplication Bugs - Critical Issues Fixed

Through comprehensive code tracing from entry point to all steps, discovered and fixed **4 critical path construction bugs** that would cause files to be created in wrong locations or with incorrect references.

#### Bug 1: Path Duplication in generate_one()

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

**Impact**: All 30 successfully generated files were in wrong location, validation couldn't find any files (json_files=0).

#### Bug 2: Path Duplication in extract_assets()

**Location**: `steps/step3_generate.py` lines 36-37, 51-52

**Problem**: Adding repo prefix to already-full-path parameter
```python
# Before (WRONG):
def extract_assets(self, ..., assets_dir: str) -> list:
    # assets_dir is already full path, but code adds repo again:
    os.makedirs(f"{self.ctx.repo}/{assets_dir}", exist_ok=True)
    dst = os.path.join(f"{self.ctx.repo}/{assets_dir}", os.path.basename(ref))
```

**Fix**:
```python
# After (CORRECT):
def extract_assets(self, ..., assets_dir_abs: str, assets_dir_rel: str) -> list:
    # Use absolute path directly for file operations:
    os.makedirs(assets_dir_abs, exist_ok=True)
    dst = os.path.join(assets_dir_abs, os.path.basename(ref))
    # Use relative path for knowledge file references:
    assets.append({
        "original": ref,
        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
    })
```

**Impact**: Assets would be copied to wrong location with duplicated path.

#### Bug 3: Incorrect assets_path in Knowledge Files

**Location**: `steps/step3_generate.py` extract_assets function

**Problem**: Using absolute path instead of relative path in knowledge file references. Knowledge files need relative paths from JSON location to assets, not absolute paths.

**Fix**:
```python
# In generate_one():
json_dir = os.path.dirname(file_info['output_path'])  # "type/category"
assets_dir_rel = os.path.relpath(assets_dir_rel_full, json_dir) + "/"  # "assets/file_id/"

# In extract_assets():
assets.append({
    "original": ref,
    "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
})
# Result: Knowledge file contains relative path "assets/file_id/image.png"
```

**Impact**: Asset references in knowledge files would be broken or contain absolute paths.

#### Bug 4: Manual Path Construction in delete_knowledge()

**Location**: `run.py` line 118

**Problem**: Manually constructing assets path instead of using file_info data
```python
# Before (WRONG):
assets_path = f"{ctx.knowledge_dir}/{file_info['type']}/{file_info['category']}/assets/{file_id}/"

# After (CORRECT):
assets_path = f"{ctx.knowledge_dir}/{file_info['assets_dir']}"
```

**Impact**: Assets deletion might fail or delete wrong directory.

#### Bug 5: Timeout Too Short

**Location**: `steps/step3_generate.py` line 144

**Problem**: The "tag" file generation timed out at 600 seconds (10 minutes).

**Fix**: Increased timeout from 600 to 900 seconds (15 minutes) for complex documentation files.

### Verification Approach

**Automated Tests**: Created comprehensive path logic test (`test_path_logic.py`) covering:
- ✅ Context path properties (knowledge_dir, docs_dir, log_dir)
- ✅ Step 3 path constructions (output, source, assets absolute & relative)
- ✅ Step 4, 5, 6 path constructions
- ✅ delete_knowledge path constructions
- ✅ No path duplication anywhere
- ✅ Assets relative path computation

**Manual Verification** (must run from regular shell, not within Claude Code):
```bash
cd /home/tie303177/work/nabledge/work3
python tools/knowledge-creator/run.py --version 6 --test-mode
```

Expected: All 31 test files generate successfully, files in correct location, no path duplication.

### Root Cause Analysis

**Why These Bugs Occurred**:
1. **Inconsistent Path Conventions**: Mixed use of absolute and relative paths without clear parameter naming
2. **Lack of Type Hints**: Functions didn't clearly indicate whether paths should be absolute or relative
3. **No Path Logic Tests**: No automated tests to catch path construction errors
4. **Code Review Gap**: Pattern of `f"{ctx.repo}/{ctx.property}"` wasn't recognized as bug

**Prevention Measures**:
1. **Clear Naming Convention**:
   - `*_abs`: Absolute paths (full)
   - `*_rel`: Relative paths
   - `ctx.*_dir`: Always absolute paths
   - `file_info.*_path`: Always relative paths

2. **Automated Testing**: `test_path_logic.py` comprehensive path construction tests

3. **Code Review Checklist**:
   - No `f"{ctx.repo}/{ctx.property}"` patterns (ctx properties are already absolute)
   - No manual path construction when file_info contains the path
   - Assets paths use relative references in knowledge files
   - Test script passes before commit

### Lessons Learned

1. **Code Tracing is Essential**: Reading code from entry to all steps revealed bugs that test-mode execution alone wouldn't catch
2. **Path Logic is Subtle**: Absolute vs relative path handling needs explicit design and testing
3. **Test Early**: Path logic tests should be written alongside path-handling code
4. **Naming Matters**: Clear parameter names (`assets_dir_abs` vs `assets_dir_rel`) prevent confusion
