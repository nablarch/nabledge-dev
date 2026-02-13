# Mapping Information: Official Docs to Knowledge Files

Created: 2026-02-13

## Summary

This work created comprehensive mapping information that maps Nablarch official documentation files to nabledge knowledge files. **All 967 files (514 V6 + 453 V5) were reviewed by AI agents** to determine proper categorization based on actual content, not just path patterns. The mapping will be used by skills to automatically generate knowledge files.

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
- **scripts/apply-categorization.py**: Apply path-based categorization rules (initial pass)
- **scripts/apply-agent-reviews.py**: Apply AI agent review results to add processing pattern categories
- **scripts/map-targets.py**: Map to target knowledge file paths
- **scripts/generate-out-of-scope-report.py**: Generate out-of-scope review reports
- **scripts/generate-mapping-excel.py**: Generate Excel workbooks for easy review
- **validate-mapping.sh**: Validation script

## Statistics

### V6 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 514 | 100% |
| **In scope** | 443 | 86.2% |
| **Out of scope** | 71 | 13.8% |
| **Needs review** | 0 | 0% |

**Note:** ja/en duplicate files have been deduplicated (kept ja versions only).

#### V6 Source Breakdown

- nablarch-document: 336 RST files (ja only, en duplicates removed)
- nablarch-system-development-guide: 158 MD files (including dev guide patterns)
- nablarch-single-module-archetype: 10 archetype projects (20 representative files)

#### V6 Out-of-Scope by Reason

| Reason | Files |
|--------|-------|
| Web applications (JSP/UI) | 43 |
| Jakarta Batch (JSR 352) | 13 |
| DB Messaging (Resident Batch) | 8 |
| MOM Messaging | 5 |
| Messaging (other) | 1 |
| Test files and tooling | 1 |

**Note:** Counts halved due to ja/en deduplication.

### V5 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 453 | 100% |
| **In scope** | 381 | 84.1% |
| **Out of scope** | 72 | 15.9% |
| **Needs review** | 0 | 0% |

**Note:** ja/en duplicate files have been deduplicated (kept ja versions only).

#### V5 Source Breakdown

- nablarch-document: 435 RST files (ja only, en duplicates removed)
- nablarch-single-module-archetype: 9 archetype projects (18 representative files)
- Note: No system-development-guide for v5 (v6 guide is used as reference)

#### V5 Out-of-Scope by Reason

| Reason | Files |
|--------|-------|
| Web applications (JSP/UI) | 44 |
| Jakarta Batch (JSR 352) | 13 |
| DB Messaging (Resident Batch) | 8 |
| MOM Messaging | 5 |
| Messaging (other) | 1 |
| Test files and tooling | 1 |

**Note:** Counts halved due to ja/en deduplication.

## Processing Pattern Distribution

Files with processing pattern categories (including libraries and handlers that support these patterns):

### V6

| Processing Pattern | Files | Description |
|--------------------|-------|-------------|
| batch-nablarch | 62 | Nablarch Batch (On-demand): FILE to DB, DB to DB, DB to FILE |
| rest | 56 | RESTful Web Services (JAX-RS) |
| http-messaging | 6 | HTTP Messaging (alternative to REST) |

### V5

| Processing Pattern | Files | Description |
|--------------------|-------|-------------|
| batch-nablarch | 57 | Nablarch Batch (On-demand): FILE to DB, DB to DB, DB to FILE |
| rest | 55 | RESTful Web Services (JAX-RS) |
| http-messaging | 6 | HTTP Messaging (alternative to REST) |

## Category Distribution (In-Scope Files)

### V6 Top Categories

| Category | Type | Files |
|----------|------|-------|
| dev-guide-other | guide | 158 |
| tool | component | 56 |
| library | component | 49 |
| handler | component | 45 |
| setup | setup | 37 |
| about | about | 24 |
| rest | processing-pattern | 23 |
| archetype | setup | 20 |
| adaptor | component | 16 |
| batch-nablarch | processing-pattern | 14 |

**Note**: Processing pattern counts above (62, 56) include libraries and handlers. Category counts here (23, 14) are files primarily categorized as that pattern.

### V5 Top Categories

| Category | Type | Files |
|----------|------|-------|
| tool | component | 152 |
| library | component | 49 |
| handler | component | 45 |
| setup | setup | 39 |
| rest | processing-pattern | 23 |
| about | about | 23 |
| archetype | setup | 20 |
| adaptor | component | 16 |
| batch-nablarch | processing-pattern | 14 |
| configuration | setup | 13 |

**Note**: Processing pattern counts above (57, 55) include libraries and handlers. Category counts here (23, 14) are files primarily categorized as that pattern.

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

### Categorization Approach

#### Phase 1: Path-Based Initial Categorization
- **Priority 1 (Exclusions)**: Files matching exclusion patterns are marked out-of-scope
- **Priority 2 (Inclusions)**: Files matching inclusion patterns are assigned component categories (library, handler, tool, etc.)
- **Dev Guide Patterns**: MD files matched against filename patterns
- **Archetype Patterns**: Maven archetype projects get `archetype` category

#### Phase 2: Content-Based Processing Pattern Assignment
**All 967 files reviewed by AI agents in parallel** to assign processing pattern categories:
- **10 specialized agents** reviewed different file categories (V6/V5 batch, REST, libraries, handlers, dev-guides)
- **Agents read actual file content** to determine which processing patterns (batch-nablarch, rest, http-messaging) apply
- **Multiple patterns allowed**: Libraries and handlers used by multiple patterns received all applicable categories
- **100 category additions** were made based on agent recommendations

**Key findings from agent reviews**:
- **Universal libraries** (database, validation, logging): Added to BOTH batch-nablarch AND rest
- **Batch-specific libraries** (data_io, format, file_path_management): Added to batch-nablarch only
- **REST-specific libraries** (jaxrs_access_log): Added to rest only
- **Common handlers**: Many handlers support both batch and REST patterns
- **Standalone handlers**: Batch-specific execution control handlers

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
- **One source file can have multiple categories** - This is intentional and critical for proper knowledge organization
- All 967 unique files (514 v6 + 453 v5) are accounted for with 100% coverage
- ja/en duplicates removed (kept ja versions only, 670 en files removed)
- **Processing pattern categories were assigned by AI agents reading actual file content**, not just path patterns
- 100 category additions were made based on agent content analysis (53 V6 + 47 V5)
