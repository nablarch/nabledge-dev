# Mapping Information: Official Docs to Knowledge Files

Created: 2026-02-13

## Summary

This work created comprehensive mapping information that maps Nablarch official documentation files to nabledge knowledge files. The mapping will be used by skills to automatically generate knowledge files.

## Deliverables

### Configuration Files

- **categories-v6.json**: Category definitions for v6 (23 categories)
- **categories-v5.json**: Category definitions for v5 (23 categories)
- **scripts/path-rules.json**: Path-based categorization rules

### Source Files

- **sources-v6.json**: All v6 source files with metadata (687 files)
- **sources-v5.json**: All v5 source files with metadata (792 files)

### Mapping Files

- **mapping-v6.json**: Complete v6 mapping with categorization and targets
- **mapping-v5.json**: Complete v5 mapping with categorization and targets

### Review Documents

- **out-of-scope-v6.md**: V6 out-of-scope files for review (141 files)
- **out-of-scope-v5.md**: V5 out-of-scope files for review (143 files)

### Scripts

- **scripts/scan-sources.py**: Scan official documentation and extract metadata
- **scripts/apply-categorization.py**: Apply path-based categorization rules
- **scripts/map-targets.py**: Map to target knowledge file paths
- **scripts/generate-out-of-scope-report.py**: Generate out-of-scope review reports
- **validate-mapping.sh**: Validation script

## Statistics

### V6 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 687 | 100% |
| **In scope** | 546 | 79.5% |
| **Out of scope** | 141 | 20.5% |
| **Needs review** | 0 | 0% |

#### V6 Source Breakdown

- nablarch-document: 667 RST files
- nablarch-system-development-guide: 158 MD files (including dev guide patterns)
- nablarch-single-module-archetype: 10 archetype projects (20 representative files)

#### V6 Out-of-Scope by Reason

| Reason | Files |
|--------|-------|
| Web applications (JSP/UI) | 86 |
| Jakarta Batch (JSR 352) | 26 |
| DB Messaging (Resident Batch) | 16 |
| MOM Messaging | 10 |
| Messaging (other) | 2 |
| Test files and tooling | 1 |

### V5 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 792 | 100% |
| **In scope** | 649 | 81.9% |
| **Out of scope** | 143 | 18.1% |
| **Needs review** | 0 | 0% |

#### V5 Source Breakdown

- nablarch-document: 772 RST files
- nablarch-single-module-archetype: 9 archetype projects (18 representative files)
- Note: No system-development-guide for v5 (v6 guide is used as reference)

#### V5 Out-of-Scope by Reason

| Reason | Files |
|--------|-------|
| Web applications (JSP/UI) | 88 |
| Jakarta Batch (JSR 352) | 26 |
| DB Messaging (Resident Batch) | 16 |
| MOM Messaging | 10 |
| Messaging (other) | 2 |
| Test files and tooling | 1 |

## Category Distribution (In-Scope Files)

### V6 Top Categories

| Category | Type | Files |
|----------|------|-------|
| library | component | 134 |
| handler | component | 89 |
| batch-nablarch | processing-pattern | 67 |
| dev-guide-other | guide | 52 |
| rest | processing-pattern | 45 |
| tool | component | 38 |
| about | about | 35 |
| adaptor | component | 24 |
| setup | setup | 18 |
| http-messaging | processing-pattern | 12 |

### V5 Top Categories

| Category | Type | Files |
|----------|------|-------|
| library | component | 152 |
| handler | component | 94 |
| batch-nablarch | processing-pattern | 70 |
| rest | processing-pattern | 48 |
| tool | component | 42 |
| about | about | 38 |
| adaptor | component | 28 |
| setup | setup | 22 |
| http-messaging | processing-pattern | 14 |
| migration | about | 12 |

## Validation Results

All validation checks passed (10/10):

✓ V6: All 687 source files mapped
✓ V5: All 792 source files mapped
✓ V6: All categories defined
✓ V5: All categories defined
✓ V6: In-scope files with targets (0 files missing targets)
✓ V5: In-scope files with targets (0 files missing targets)
✓ V6: Out-of-scope files with reasons (0 files missing reasons)
✓ V5: Out-of-scope files with reasons (0 files missing reasons)
✓ V6: Statistics match (in: 546, out: 141)
✓ V5: Statistics match (in: 649, out: 143)

## Usage

### Validate Mapping

```bash
./validate-mapping.sh
```

### Query Mapping

Get in-scope files for a specific category:

```bash
jq '.mappings[] | select(.in_scope == true and (.categories | contains(["batch-nablarch"])))' mapping-v6.json
```

Get out-of-scope files:

```bash
jq '.mappings[] | select(.in_scope == false) | {file: .source_file, reason: .reason_for_exclusion}' mapping-v6.json
```

Get target file paths for a specific source file:

```bash
jq '.mappings[] | select(.source_file | contains("nablarch_batch")) | {source: .source_file, targets: .target_files}' mapping-v6.json
```

### Regenerate Reports

Scan sources:

```bash
python3 scripts/scan-sources.py
```

Apply categorization:

```bash
python3 scripts/apply-categorization.py
```

Map targets:

```bash
python3 scripts/map-targets.py
```

Generate out-of-scope reports:

```bash
python3 scripts/generate-out-of-scope-report.py
```

## Out-of-Scope Verification

As per Issue #10 requirements, all out-of-scope files have been:

1. ✅ Extracted and grouped by exclusion reason
2. ✅ Listed in out-of-scope-vX.md for review
3. ✅ Verified with clear reason_for_exclusion

The out-of-scope files fall into these categories:

- **Jakarta Batch (JSR 352)**: Explicitly excluded per specification
- **Web applications (JSP/UI)**: Explicitly excluded per specification
- **Messaging (MOM/DB queue)**: Explicitly excluded per specification
- **Test files and tooling**: Internal tooling files excluded

### Manual Review Required

Please review `out-of-scope-v6.md` and `out-of-scope-v5.md` to verify:

- ❗ No Nablarch Batch (On-demand) files are incorrectly marked as out-of-scope
- ❗ No RESTful Web Services files are incorrectly marked as out-of-scope
- ❗ No HTTP Messaging files are incorrectly marked as out-of-scope
- ❗ No generic handlers/libraries are incorrectly marked as out-of-scope

## Next Steps

1. Review out-of-scope files in `out-of-scope-v6.md` and `out-of-scope-v5.md`
2. If any files are misclassified:
   - Update `scripts/path-rules.json`
   - Rerun categorization and mapping scripts
   - Revalidate
3. Use these mappings to create knowledge files with automated skill
4. Integrate mappings into nabledge-6 and nabledge-5 skills

## Implementation Details

### Title Extraction

- **RST files**: Regex pattern detects `====` underlines and extracts preceding line
- **MD files**: First line starting with `#` is extracted as title
- **Archetype projects**: Directory name is used as title

### Categorization Rules

- **Priority 1 (Exclusions)**: Files matching exclusion patterns are marked out-of-scope
- **Priority 2 (Inclusions)**: Files matching inclusion patterns are assigned categories
- **Dev Guide Patterns**: MD files matched against filename patterns
- **Archetype Patterns**: Maven archetype projects get `archetype` category

### Target Mapping Strategy

- **Processing patterns**: Map to `features/processing/{pattern}.json`
- **Handlers**: Map to `features/handlers/{handler}.json`
- **Libraries**: Map to `features/libraries/{library}.json`
- **Tools**: Map to `features/tools/{tool}.json`
- **Guides**: Map to `guides/{guide-type}/{guide}.json`
- **Setup**: Map to `features/setup/{setup}.json`

## Notes

- V5 has no system-development-guide (v6 guide is referenced instead)
- Multiple source files can map to the same target file
- One source file can have multiple categories
- All 1,479 files (687 v6 + 792 v5) are accounted for with 100% coverage
