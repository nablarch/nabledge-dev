# Test Execution Strategy

## Test Objectives

Validate nabledge-creator tool functionality through targeted testing that covers:
1. **End-to-end flow** - All 6 steps execute successfully
2. **Input variation** - All source formats and categories processed correctly
3. **Concurrency** - Parallel processing works without conflicts
4. **Error handling** - Graceful failure and recovery
5. **Resume capability** - Skip existing files and continue from failure point
6. **Differential updates** - Handle file additions, updates, deletions

## Test Coverage Matrix

### 1. Source Format Coverage

| Format | Example File | Purpose |
|--------|-------------|---------|
| RST | `batch/getting_started.rst` | Most common format |
| MD | `pattern-collection/batch-async.md` | Pattern documentation |
| Excel | `security-check-table.xlsx` | Structured data |

### 2. Type/Category Coverage

| Type | Category | Example | Purpose |
|------|----------|---------|---------|
| processing-pattern | nablarch-batch | `batch/getting_started.rst` | Core pattern |
| processing-pattern | jakarta-batch | `jakarta-batch/architecture.rst` | Alternative pattern |
| processing-pattern | web-application | `web/getting_started.rst` | Different pattern type |
| component | handlers | `handlers/common/db_connection.rst` | Component type |
| component | libraries | `libraries/database_access.rst` | Different component |
| development-tools | testing | `testing/unit_test.rst` | Tools type |
| setup | blank-project | `setup/blank_project.rst` | Setup type |
| about | nablarch | `about/architecture.rst` | About type |

### 3. Edge Cases Coverage

| Case | Test File | Expected Behavior |
|------|-----------|-------------------|
| Very long file (>10,000 lines) | Large RST file | Section splitting at 2000 chars |
| Minimal file (<100 lines) | Small RST file | Single section output |
| Complex nested sections | Multi-level RST | Proper h2/h3 handling |
| Missing title | Malformed RST | Error handling |
| Special characters in filename | File with spaces/symbols | Path handling |
| Cross-references | File with :ref: links | Reference resolution |

### 4. Concurrency Test

| Scenario | Files | Concurrency | Purpose |
|----------|-------|-------------|---------|
| Parallel generation | 8 files | 4 workers | No race conditions |
| Parallel classification | 20 files | 4 workers | Correct categorization |
| Parallel validation | 10 files | 4 workers | Independent validation |

### 5. Resume Test

| Scenario | Initial State | Action | Expected |
|----------|---------------|--------|----------|
| Partial completion | 5 files generated, 3 remaining | Rerun Step 3 | Skip 5, generate 3 |
| After error | Failed on file 6 | Fix and rerun | Skip 1-5, retry 6 |
| Complete re-run | All files exist | Rerun Step 3 | Skip all |

### 6. Differential Update Test

| Scenario | Change | Action | Expected |
|----------|--------|--------|----------|
| New source added | Add new RST file | Rerun pipeline | Generate only new file |
| Source updated | Modify existing RST | Delete JSON, rerun | Regenerate updated file |
| Source deleted | Remove RST file | Rerun pipeline | Skip deleted source |

## Test Mode Design

### Command Interface

```bash
# Production mode (default): Process all 252 files
python run.py --version 6

# Test mode: Process curated file set covering all validation scenarios
python run.py --version 6 --test-mode
```

### Implementation Strategy (Single Point of Change)

**Principle**: Modify only Step 2 output. All other steps remain unchanged.

**Why this works**:
- Step 3-6 read `classified.json` to determine what files to process
- Filtering `classified.json` in Step 2 automatically limits downstream processing
- No test-mode logic scattered across multiple files
- Maintainable and simple

**Implementation Location**: `steps/step2_classify.py` (end of file only)

```python
# At the end of step2_classify.py, before writing classified.json

if ctx.test_mode:
    classified_list = filter_for_test(classified_list)
    log_info(f"Test mode: Filtered to {len(classified_list)} files")

# Write output (same for both modes)
write_json(ctx.classified_list_path, result)
```

**Filter function**:
```python
def filter_for_test(classified: List[dict]) -> List[dict]:
    """Filter file list for test mode using predefined test file set"""
    test_file_ids = load_test_file_ids()  # Load from test-files.json
    return [f for f in classified if f['id'] in test_file_ids]
```

**Test file definition**: `tools/knowledge-creator/test-files.json`

```json
{
  "description": "Test file set covering all validation scenarios",
  "coverage": {
    "format": ["rst", "md", "xlsx"],
    "type": ["processing-pattern", "component", "development-tools", "setup", "about"],
    "category": ["nablarch-batch", "web-application", "handlers", "libraries", "testing"],
    "edge_cases": ["large_file", "small_file", "complex_nested"]
  },
  "files": [
    "getting_started",
    "architecture",
    "batch-async",
    "security-check",
    "db_connection_management_handler",
    "database_access",
    "unit_test",
    "blank_project_setup",
    "nablarch_architecture"
  ]
}
```

**Modified Context**:
```python
@dataclass
class Context:
    version: str
    repo: str
    concurrency: int
    test_mode: bool = False  # Add this only
```

### Why This Design is Maintainable

1. **Single point of change**: Only Step 2 knows about test mode
2. **Steps 3-6 unchanged**: They just process whatever is in `classified.json`
3. **Declarative test set**: `test-files.json` is easy to update
4. **No scattered logic**: Test mode doesn't leak into multiple files

## Test Execution Plan

### Single Command Test Execution

```bash
# Run all validation scenarios with one command
python run.py --version 6 --test-mode

# Expected output:
=== Test Mode: Running with curated file set ===

[Step 1] List sources
✓ Found 252 source files

[Step 2] Classify
✓ Classified 252 files
✓ Test mode: Filtered to 25 files covering all test scenarios

[Step 3] Generate (concurrency=4)
✓ Generated 25 knowledge files (0 errors)

[Step 4] Build index
✓ Built index.toon with 25 entries

[Step 5] Generate docs
✓ Generated 25 MD files

[Step 6] Validate
✓ Structure checks: 25/25 passed
✓ Content validation: 25/25 passed

=== Test Summary ===
✅ Format coverage: 3 files (RST, MD, Excel)
✅ Type coverage: 5 types
✅ Category coverage: 10 categories
✅ Edge cases: 5 files
✅ Concurrency: 4 workers, no conflicts
✅ Validation: 100% pass rate

Total time: 3m 15s
```

### Validation Checklist

After test mode execution:

**End-to-end flow**:
- [ ] All 6 steps complete without errors
- [ ] Knowledge files generated in correct paths
- [ ] index.toon contains all test file entries
- [ ] MD files readable and properly formatted

**Format coverage**:
- [ ] RST files processed correctly
- [ ] MD files processed correctly
- [ ] Excel files processed correctly

**Type/Category coverage**:
- [ ] All Type values represented (processing-pattern, component, development-tools, setup, about)
- [ ] All major Category values represented
- [ ] Output paths follow `{type}/{category}/{id}.json` pattern

**Edge cases**:
- [ ] Large files (>10,000 lines) handle section splitting correctly
- [ ] Small files (<100 lines) produce valid output
- [ ] Complex nested sections processed properly

**Concurrency**:
- [ ] No race conditions or file conflicts
- [ ] All concurrent tasks complete successfully
- [ ] Logs show parallel execution

**Validation**:
- [ ] All 17 structure checks pass for all files
- [ ] All 4 content validation aspects pass for all files
- [ ] No false positives or false negatives

### Manual Verification (After Test Mode)

**Resume capability**:
```bash
# Run test mode again (should skip all existing files)
python run.py --version 6 --test-mode

# Expected: All files skipped, no regeneration
```

**Error handling**:
```bash
# Delete one generated file and rerun
rm .claude/skills/nabledge-6/knowledge/processing-pattern/nablarch-batch/getting_started.json
python run.py --version 6 --test-mode

# Expected: Only getting_started.json regenerated, others skipped
```

## Success Criteria

Test execution is successful when:
1. ✅ All 7 test phases pass validation checks
2. ✅ No critical errors in any phase
3. ✅ Performance meets expectations (30 sec/file with concurrency=4)
4. ✅ All edge cases handled gracefully
5. ✅ Feature flags work as documented
6. ✅ Resume capability functions correctly

## Test Artifacts

After testing, save:
- Test execution log: `.pr/00099/test-execution.log`
- Generated knowledge files: `.pr/00099/test-output/`
- Validation results: `.pr/00099/validation-results.json`
- Performance metrics: `.pr/00099/performance-metrics.json`
