# Test Mode Quick Reference

## Overview

Test mode processes a curated set of 31 files (from 21 unique IDs) instead of all 252 files, enabling fast validation of the knowledge-creator tool.

## Usage

```bash
# Production mode (default): Process all 252 files
python run.py --version 6

# Test mode: Process 31 curated test files
python run.py --version 6 --test-mode

# Test mode with dry-run (show what would happen without execution)
python run.py --version 6 --test-mode --dry-run

# Test mode with specific step
python run.py --version 6 --test-mode --step 3
```

## What Gets Tested

### Full Coverage
- ✅ All 7 types (processing-pattern, component, development-tools, setup, about, guide, check)
- ✅ All 3 formats (RST: 27 files, MD: 3 files, Excel: 1 file)
- ✅ 18 unique categories
- ✅ Edge cases (3 large files, 1 small file)

### Test File Distribution
- 13 processing-pattern files (all pattern categories)
- 5 component files (handlers, libraries, adapters)
- 3 guide files (Japanese pattern documentation)
- 4 setup files (blank-project, cloud-native, setting-guide)
- 3 about files (Nablarch overview)
- 2 development-tools files (testing-framework, toolbox)
- 1 check file (security-check Excel)

## How It Works

1. **Step 1:** Lists all 252 source files (unchanged)
2. **Step 2:** Classifies all 252 files, then filters to 31 test files
3. **Steps 3-6:** Process only the 31 files in filtered classified.json

### Single Point of Change
- Only Step 2 is modified with filter logic
- Steps 3-6 remain completely unchanged
- Test file set defined in `test-files.json`

## Test File Set

Located in: `tools/knowledge-creator/test-files.json`

To modify the test set:
1. Edit `test-files.json` - add/remove file IDs
2. File IDs must match the `id` field in classified.json
3. Changes take effect immediately (no code changes needed)

## Expected Performance

- **Full run:** ~126 minutes (252 files × 30 sec/file)
- **Test run:** ~15 minutes (31 files × 30 sec/file)
- **Speedup:** ~8.4x faster

## Validation

Test mode validates:
- End-to-end pipeline (Steps 1-6)
- All source formats (RST, MD, Excel)
- All file types and categories
- Edge cases (large/small files)
- Concurrency handling
- Error recovery

## Files

- `run.py` - CLI argument handling and Context
- `steps/step2_classify.py` - Filter implementation
- `test-files.json` - Test file set definition

## Design Document

See `.pr/00099/test-strategy.md` for:
- Test objectives and coverage matrix
- Design rationale
- Implementation strategy
- Validation checklist
