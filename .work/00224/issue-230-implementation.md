# Issue #230 Implementation Guide

## Background

Split logic in `step2_classify.py` has two bugs that prevent proper splitting of RST files:

1. Overline format (`------\nTitle\n------`) is detected twice, creating a phantom section
2. `=====` is excluded from h3 detection, so large sections with `=====` subsections cannot be split

Rather than fixing these individually, the root cause is that split mode requires 2+ h2 sections (`SPLIT_SECTION_THRESHOLD=2`). Removing this threshold solves both problems at once.

## Code Changes (tools/knowledge-creator/scripts/step2_classify.py)

### 1. Remove SPLIT_SECTION_THRESHOLD — treat all RST files as split candidates

`should_split_file()` currently gates on `len(sections) >= 2`. Remove this check and always run split logic for RST files.

Files with 0 sections or 1 resulting group → single entry (no `--s1` suffix).

### 2. Recognize `=====` as h3

In `analyze_rst_h3_subsections()`, the h3 pattern excludes `=` and `-`:
```python
if h3_pattern.match(next_line) and not re.match(r'^[-=]{5,}$', next_line):
```
Remove `=` from the exclusion (keep `-` excluded to avoid h2 confusion):
```python
if h3_pattern.match(next_line) and not re.match(r'^-{5,}$', next_line):
```

Also expand `h3_pattern` to include `=`:
```python
h3_pattern = re.compile(r'^[\^~+*.=]{5,}$')
```

### 3. Handle 0-section / 1-group case

When split logic produces 0 groups or 1 group, return a single entry without `--s1` suffix (same as non-split behavior).

## Additional Changes (run.py + cleaner.py)

### 4. Delete stale cache files after Phase A

After Phase A produces a new catalog, delete any `.cache/knowledge/**/*.json` whose stem (filename without `.json`) is not in the catalog IDs.

```python
catalog_ids = {f["id"] for f in catalog["files"]}
for json_file in glob(".cache/knowledge/**/*.json", recursive=True):
    if Path(json_file).stem not in catalog_ids:
        os.remove(json_file)
```

Add this as a step in `_run_pipeline()` immediately after Phase A completes.

### 5. Resolve --target after Phase A (not before)

Currently `--target base_name` is resolved to split IDs using the OLD catalog before Phase A runs.
Move this resolution to AFTER Phase A so it uses the new catalog.

In `_run_pipeline()`, move the target resolution block to after the Phase A section.

### 6. kc regen: keep source paths, resolve after Phase A

`detect_changed_files()` currently returns file IDs from the old catalog.
Change it to return source paths instead. After Phase A, map source paths to new IDs from the new catalog.

## Impact on Existing Cache

After code changes, run `kc regen` on each generated version:

| Version | Affected entries | Action |
|---------|-----------------|--------|
| v5 | 0 | No action needed |
| v6 | 3 | `kc regen` auto-handles |
| v1.4 | regenerate in full | #230 must be merged before v1.4 generation |

The stale cleanup (change 4) handles deletion automatically during `kc regen`.

## Tests

Run existing tests after changes:
```bash
cd tools/knowledge-creator
pytest
```

Fix any failures. The split behavior change will likely require updates to E2E test expected values.
