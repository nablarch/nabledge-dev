# Mapping Creation Procedure

**Purpose**: Create comprehensive mapping files that link official Nablarch documentation to target knowledge files.

**Target Output**:
- `mapping-v6.json` - Nablarch 6 mapping (all official files)
- `mapping-v5.json` - Nablarch 5 mapping (all official files)

---

## Design Philosophy

### Mapping Scope
**Mapping includes ALL official documentation files** (.rst, .md, selected .xml)

- Mapping = Structured representation of entire official documentation
- Scope = Priority/target range for knowledge file generation
- Scope determination is managed by `default_in_scope` in `categories-v*.json`

### Benefits
1. **Zero false negatives** - All files are mapped, nothing is missed
2. **Flexibility** - Scope changes only require updating category definitions
3. **Traceability** - All files are tracked with categorization

See [Design Document Section 1.5](nabledge-design.md#15-スコープ) for scope definition.

---

## Mapping Entry Schema

```json
{
  "id": "v6-0001",
  "source_file": "nab-official/v6/nablarch-document/en/index.rst",
  "title": "Nablarch",
  "categories": ["about"],
  "target_files": ["about/overview.json"]
}
```

**Fields**:
- `id`: Unique identifier (format: `v{version}-{sequential-number}`)
- `source_file`: Relative path from repository root (no `.lw/` prefix)
- `title`: Document title (from rst header or filename)
- `categories`: Array of category IDs (from `categories-v*.json`)
- `target_files`: Array of target knowledge file paths (relative to `knowledge/` directory)

### Edge Cases and Decision Rules

This section clarifies how to handle ambiguous situations during mapping creation.

#### Multiple Categories

**When to use**:
- File covers multiple aspects (e.g., a handler that's specific to batch processing)
- Content spans multiple category types

**Rules**:
- Maximum 3 categories per entry
- Always include at least one processing-pattern OR component category
- Processing patterns are mutually exclusive (choose only ONE: batch-nablarch, rest, web, etc.)
- Components CAN combine with processing patterns

**Examples**:
- Batch-specific handler: `["handler", "batch-nablarch"]`
- REST library: `["library", "rest"]`
- Development guide about batch patterns: `["dev-guide-pattern", "batch-nablarch"]`
- General-purpose library (no specific processing pattern): `["library"]`

#### Empty target_files Array

**When to use** (rare, < 5% of entries):
- Build configuration files (pom.xml for parent projects)
- Test sample data files
- Non-documentation content (README with no technical content)

**When NOT to use**:
- Documentation files (even if currently out of scope)
- Any file with technical content
- Files that might be useful in the future

**Requirement**: Document reason in work log when using empty target_files

#### Category Conflicts

**Scenario**: File could belong to multiple processing patterns

**Resolution**:
- Read the file carefully to determine primary focus
- Choose the ONE most specific processing pattern
- If truly covers multiple patterns equally (rare), choose the first one mentioned

**Example**:
- File discussing batch AND REST → Choose based on which is primary focus
- If 80% batch, 20% REST → Use `batch-nablarch`
- If sections are equal → Use the processing pattern of the first major section

#### Ambiguous Category Assignment

**Scenario**: Unclear whether file is handler, library, or tool

**Resolution Guide**:
| If file describes... | Then use category... |
|---------------------|----------------------|
| Request/response processing flow | `handler` |
| Reusable functionality/utilities | `library` |
| Development/testing support | `tool` |
| Third-party integration | `adaptor` |

**When still unclear**: Use `library` as default (most general component category)

#### Target File Naming Uncertainty

**Scenario**: Multiple possible names for target file

**Resolution**:
- Prefer descriptive over concise: `db-connection-management-handler.json` > `db-handler.json`
- Match existing patterns in `.claude/skills/nabledge-6/knowledge/` directory
- Use source filename as basis, converted to kebab-case

**Naming Priority**:
1. Official Nablarch name (if file has one): `UniversalDao` → `universal-dao.json`
2. Primary function description: "Database connection management" → `db-connection-management.json`
3. Source filename: `jdbc_util.rst` → `jdbc-util.json`

#### One-to-Many Mapping (One source → Multiple targets)

**When to use**:
- Large source file covering multiple distinct topics
- Each topic warrants separate knowledge file

**Example**:
- Source: Comprehensive handler guide covering 5 different handlers
- Targets: 5 separate handler knowledge files

**Guideline**: Only split if each target would be > 200 lines of JSON knowledge

#### Many-to-One Mapping (Multiple sources → One target)

**When to use**:
- Multiple small source files about same topic
- Content naturally combines into single knowledge file

**Example**:
- Sources: 3 files about same handler (overview, examples, troubleshooting)
- Target: 1 comprehensive handler knowledge file

**Guideline**: Combine if total content < 500 lines of JSON knowledge

---

## Procedure Overview

| Phase | Task | Method | Output |
|-------|------|--------|--------|
| 1 | Initialize mapping files | Script | Empty JSON structure |
| 2 | Collect all source files | Script | File list with metadata |
| 3 | Apply language priority | Script | Filtered file list (en/ja) |
| 4 | Generate initial mappings | Script | Basic mapping entries |
| 5 | Categorize entries | AI Agent | Mappings with categories |
| 6 | Define target files | AI Agent | Complete mappings |
| 7 | Validate mappings | Script | Validation report |

---

## Phase 1: Initialize Mapping Files

**Script**: `doc/scripts/01-init-mapping.sh`

**Execution**:
```bash
doc/scripts/01-init-mapping.sh
```

**Output**:
- `work/YYYYMMDD/mapping/mapping-v6.json` - Empty structure
- `work/YYYYMMDD/mapping/mapping-v5.json` - Empty structure

**Validation**:
- JSON files are valid
- Schema version is set
- Mappings array is empty

---

## Phase 2: Collect All Source Files

**Script**: `doc/scripts/02-collect-files.sh`

**Execution**:
```bash
doc/scripts/02-collect-files.sh
```

**What it does**:
1. Find all `.rst`, `.md`, `.xml` files in official documentation
2. Extract file metadata (path, type, language)
3. Generate file list

**Output**:
- `work/YYYYMMDD/mapping/files-v6.txt` - All v6 files
- `work/YYYYMMDD/mapping/files-v5.txt` - All v5 files
- `work/YYYYMMDD/mapping/stats.md` - File count statistics

**Validation**: Run `doc/scripts/02-validate-files.sh`
- File counts match expected ranges
- All files exist

---

## Phase 3: Apply Language Priority

**Script**: `doc/scripts/03-filter-language.sh`

**Language Priority**: English (`/en/`) first, Japanese (`/ja/`) if English not available

**What it does**:
1. Group files by path (language-agnostic)
2. Select `/en/` version if exists
3. Select `/ja/` version if `/en/` does not exist
4. Filter by file type:
   - `.rst` - All files
   - `.md` - All files from dev guide
   - `.xml` - Only archetype `pom.xml` files (exclude build configs)

**Execution**:
```bash
doc/scripts/03-filter-language.sh
```

**Output**:
- `work/YYYYMMDD/mapping/files-v6-filtered.txt`
- `work/YYYYMMDD/mapping/files-v5-filtered.txt`
- `work/YYYYMMDD/mapping/language-selection.md` - Selection report

**Validation**: Run `doc/scripts/03-validate-language.sh`
- No duplicate paths (language-agnostic)
- English preferred over Japanese
- File type filtering applied correctly

---

## Phase 4: Generate Initial Mappings

**Script**: `doc/scripts/04-generate-mappings.sh`

**What it does**:
1. Read filtered file list
2. Generate mapping entry for each file:
   - `id`: Auto-generated (v6-0001, v6-0002, ...)
   - `source_file`: Path without `.lw/` prefix
   - `title`: Extracted from file or set as "TBD"
   - `categories`: Empty array `[]`
   - `target_files`: Empty array `[]`

**Execution**:
```bash
doc/scripts/04-generate-mappings.sh
```

**Output**:
- `work/YYYYMMDD/mapping/mapping-v6.json` - Mappings with id, source_file, title
- `work/YYYYMMDD/mapping/mapping-v5.json` - Mappings with id, source_file, title

**Validation**: Run `doc/scripts/04-validate-mappings.sh`
- JSON schema is valid
- All source_file paths exist
- IDs are sequential and unique
- Entry count matches filtered file count

---

## Phase 5: Categorize Entries (AI Agent Work)

**Method**: AI agent reads each source_file and assigns categories

**Input Files** (read these first before starting work):
1. **Mapping file**: `work/YYYYMMDD/mapping/mapping-v6.json` (replace YYYYMMDD with today's date)
2. **Category definitions**: `work/20260213/create-mapping-info/categories-v6.json`
3. **Scope definition**: `doc/nabledge-design.md` (lines 58-109)

**Agent Prompt**:
```
You are categorizing Nablarch official documentation files.

STEP 0: Setup
1. Read category definitions file: work/20260213/create-mapping-info/categories-v6.json
   - Extract category IDs, names, descriptions, and **TYPE field** (processing-pattern, component, setup, guide, check, about)
   - Example: {"id": "batch-nablarch", "type": "processing-pattern", "default_in_scope": true}
2. Understand category types:
   - **processing-pattern**: Mutually exclusive (choose only ONE per entry)
   - **component**: Can combine with processing patterns
   - **setup, guide, check, about**: Can combine with others
3. Read scope definition: doc/nabledge-design.md (lines 58-109)
4. Check total entry count: jq '.mappings | length' work/YYYYMMDD/mapping/mapping-v6.json
5. Create progress tracker: echo "Phase 5 Progress" > work/YYYYMMDD/mapping/progress-phase5.txt

For each mapping entry (process in batches of 50):
1. Read the source_file content (.lw/ prefix must be added to source_file path)
2. Determine the appropriate categories based on content
3. Update the categories array with category IDs from categories-v6.json
4. Multiple categories are allowed if applicable (see rules below)

Category Selection Rules:
- **Processing patterns** (mutually exclusive - select only ONE):
  - batch-nablarch: On-demand batch processing
  - rest: RESTful web services
  - messaging-db: DB messaging (resident batch, table queue)
  - batch-jsr352: Jakarta Batch (JSR 352)
  - http-messaging: HTTP messaging
  - web: Web applications (JSP/UI)
  - messaging-mom: MOM messaging

- **Components** (can combine with processing patterns):
  - handler: Request handlers
  - library: Framework libraries
  - tool: Development/testing tools
  - adaptor: Third-party integration adaptors

- **Documentation** (can combine with others):
  - about: Framework overview, concepts
  - setup, archetype, configuration: Project setup
  - dev-guide-pattern, dev-guide-anti, dev-guide-project, dev-guide-other: Development guides
  - check-published-api, check-deprecated, check-security: Check items
  - migration: Migration guides

Category Selection Examples:
- Handler for batch: ["handler", "batch-nablarch"]
- REST library: ["library", "rest"]
- Development guide about batch patterns: ["dev-guide-pattern", "batch-nablarch"]
- Framework concept document: ["about"]

Error Handling:
- If source_file cannot be read: Assign ["about"] and note in work log
- If content is unclear: Use most general applicable category
- If unsure between two categories: Include both (max 3 categories per entry)

Work in batches of 50 entries:
1. **BACKUP**: Create backup before processing
   ```bash
   cp work/YYYYMMDD/mapping/mapping-v6.json work/YYYYMMDD/mapping/mapping-v6-backup-batch-N.json
   ```
2. Process entries (e.g., entries 1-50)
3. **VALIDATE JSON**: Before saving, verify JSON syntax
   ```bash
   jq empty work/YYYYMMDD/mapping/mapping-v6.json
   ```
   If syntax error, restore from backup and retry
4. Save progress: Update mapping-v6.json with jq
5. Log progress: echo "Batch 1-50: COMPLETED" >> work/YYYYMMDD/mapping/progress-phase5.txt
6. Run validation: bash doc/scripts/05-validate-categories.sh
7. If validation fails:
   a. Read validation error output carefully
   b. Common errors:
      - "Unknown category": Check category ID spelling against categories-v6.json
      - "No categories": Find entries with empty categories array, re-categorize
   c. Fix specific errors mentioned
   d. Re-run validation until it passes
   e. **If unable to fix**: Restore from backup and retry batch more carefully
8. When validation passes, proceed to next batch (51-100, 101-150, etc.)

Total entries: [Check with: jq '.mappings | length' work/YYYYMMDD/mapping/mapping-v6.json]
Progress tracking: cat work/YYYYMMDD/mapping/progress-phase5.txt
```

**Process**:
1. Agent processes entries in batches of 50
2. For each entry:
   - Read source_file content
   - Analyze content to determine category
   - Update categories array
3. Save progress after each batch
4. Validate after each batch

**Validation**: Run `doc/scripts/05-validate-categories.sh` after each batch
- All categories exist in categories-v*.json
- At least one category assigned per entry
- Categories are appropriate for content (spot check 10%)

**Output**:
- `work/YYYYMMDD/mapping/mapping-v6.json` - Mappings with categories filled
- `work/YYYYMMDD/mapping/mapping-v5.json` - Mappings with categories filled
- `work/YYYYMMDD/mapping/categorization-log.md` - Work log

---

## Phase 6: Define Target Files (AI Agent Work)

**Method**: AI agent determines target knowledge file paths based on categories

**Input Files** (read these first before starting work):
1. **Mapping file**: `work/YYYYMMDD/mapping/mapping-v6.json` (with categories filled)
2. **Design document**: `doc/nabledge-design.md` (lines 276-347 for directory structure and category mapping table)

**Agent Prompt**:
```
You are defining target knowledge file paths for Nablarch documentation mappings.

STEP 0: Setup
1. Read design document: doc/nabledge-design.md (lines 276-347)
2. Extract category → directory mapping table (lines 333-347)
3. Check total entry count: jq '.mappings | length' work/YYYYMMDD/mapping/mapping-v6.json
4. Create progress tracker: echo "Phase 6 Progress" > work/YYYYMMDD/mapping/progress-phase6.txt

Category Type → Directory Mapping Reference (from Design Doc Section 2.4):

| Category Type | Directory | Example |
|--------------|-----------|---------|
| processing-pattern | features/processing/ | nablarch-batch.json |
| component (handler) | features/handlers/{batch,common,rest}/ | data-read-handler.json |
| component (library) | features/libraries/ | universal-dao.json |
| component (adaptor) | features/adapters/ | slf4j-adapter.json |
| component (tool) | features/tools/ | ntf-overview.json |
| setup | setup/ | blank-project.json |
| guide | guides/ | dev-guide-pattern.json |
| check | checks/ | security.json |
| about | about/ | framework-concept.json |
| about (migration) | migration/ | v5-to-v6.json |

For each mapping entry (process in batches of 50):
1. Read the entry's categories array
2. Determine target directory based on category type:
   - Processing pattern (batch-nablarch, rest, etc.) → features/processing/
   - **handler** → features/handlers/{subdirectory}/ where subdirectory is determined by:
     * IF entry has "handler" AND "batch-nablarch" OR "batch-jsr352" OR "messaging-db" → features/handlers/batch/
     * ELSE IF entry has "handler" AND "rest" → features/handlers/rest/
     * ELSE IF entry has "handler" but NO processing pattern → features/handlers/common/
     * ELSE IF entry has "handler" AND "web" → features/handlers/common/ (web handlers not in scope but map to common)
   - library → features/libraries/
   - tool → features/tools/
   - adaptor → features/adapters/
   - about → about/
   - migration → migration/
   - setup, archetype, configuration → setup/
   - dev-guide-* → guides/
   - check-* → checks/
3. Create descriptive kebab-case filename based on source content
4. Update target_files array (format: "directory/filename.json")

Naming Rules:
- Use kebab-case (lowercase with hyphens): "universal-dao.json" NOT "UniversalDAO.json"
- Be descriptive: "db-connection-management-handler.json" NOT "db-handler.json"
- Use .json extension always
- For handlers, include handler type: "data-read-handler.json" NOT "data-read.json"

Multiple Target Files:
- Use when one source document maps to multiple distinct knowledge files
- Example: Large document covering multiple handlers → multiple target files

Empty Target Files:
- ONLY use for: build configs, sample data files, non-documentation content
- Must be rare (< 5% of entries)
- Document reason in work log

Error Handling:
- If category has no clear directory: Use features/ as default and note in work log
- If target path unclear: Use source filename as basis (convert to kebab-case)
- If validation fails: See error recovery steps below

Work in batches of 50 entries:
1. **BACKUP**: Create backup before processing
   ```bash
   cp work/YYYYMMDD/mapping/mapping-v6.json work/YYYYMMDD/mapping/mapping-v6-backup-phase6-batch-N.json
   ```
2. Process entries (e.g., entries 1-50)
3. **VALIDATE JSON**: Before saving, verify JSON syntax
   ```bash
   jq empty work/YYYYMMDD/mapping/mapping-v6.json
   ```
   If syntax error, restore from backup and retry
4. Save progress: Update mapping-v6.json with jq
5. Log progress: echo "Batch 1-50: COMPLETED" >> work/YYYYMMDD/mapping/progress-phase6.txt
6. Run validation: bash doc/scripts/06-validate-targets.sh
7. If validation fails:
   a. Read validation error output carefully
   b. Common errors:
      - "Target without .json": Add .json extension
      - "Invalid naming": Convert to kebab-case (lowercase with hyphens)
      - "Wrong directory": Check category → directory mapping table
   c. Fix specific errors mentioned
   d. Re-run validation until it passes
   e. **If unable to fix**: Restore from backup and retry batch more carefully
8. When validation passes, proceed to next batch (51-100, 101-150, etc.)

Total entries: [Check with: jq '.mappings | length' work/YYYYMMDD/mapping/mapping-v6.json]
Progress tracking: cat work/YYYYMMDD/mapping/progress-phase6.txt
```

**Process**:
1. Agent processes entries in batches of 50
2. For each entry:
   - Determine target directory from category mapping table
   - Define filename based on content
   - Update target_files array
3. Save progress after each batch
4. Validate after each batch

**Validation**: Run `doc/scripts/06-validate-targets.sh` after each batch
- All target paths follow directory structure
- Filenames use kebab-case
- Paths match category type → directory mapping
- No duplicate target files across different source files

**Output**:
- `work/YYYYMMDD/mapping/mapping-v6.json` - Complete mappings
- `work/YYYYMMDD/mapping/mapping-v5.json` - Complete mappings
- `work/YYYYMMDD/mapping/target-definition-log.md` - Work log

---

## Error Recovery Examples

This section provides specific examples of common errors and their solutions for Phase 5 and 6.

### Phase 5 Errors (Categorization)

#### Error: "Unknown category in v6: batch-pattern"

**Cause**: Typo in category ID

**Fix**:
1. Search mapping file for the incorrect category:
   ```bash
   jq '.mappings[] | select(.categories[] == "batch-pattern") | .id' work/YYYYMMDD/mapping/mapping-v6.json
   ```
2. Check correct category ID in `work/20260213/create-mapping-info/categories-v6.json`
3. Correct to "batch-nablarch":
   ```bash
   jq '(.mappings[] | select(.id == "v6-0123").categories) |= map(if . == "batch-pattern" then "batch-nablarch" else . end)' work/YYYYMMDD/mapping/mapping-v6.json > temp.json && mv temp.json work/YYYYMMDD/mapping/mapping-v6.json
   ```
4. Re-run validation: `bash doc/scripts/05-validate-categories.sh`

#### Error: "25 v6 entries have no categories"

**Cause**: Processing incomplete or errors during categorization

**Fix**:
1. List entries without categories:
   ```bash
   jq '.mappings[] | select(.categories == []) | {id, source_file}' work/YYYYMMDD/mapping/mapping-v6.json
   ```
2. For each entry:
   - Read source_file content (add `.lw/` prefix to path)
   - Determine appropriate categories
   - Update categories array
3. Save changes
4. Re-run validation

#### Error: "Entry has both batch-nablarch and rest categories"

**Cause**: Processing pattern categories should be mutually exclusive

**Fix**:
1. Find the entry:
   ```bash
   jq '.mappings[] | select((.categories | contains(["batch-nablarch"])) and (.categories | contains(["rest"])))' work/YYYYMMDD/mapping/mapping-v6.json
   ```
2. Read source_file content
3. Determine correct processing pattern (only one)
4. Update categories to remove incorrect processing pattern
5. Re-run validation

### Phase 6 Errors (Target Files)

#### Error: "Target without .json extension: features/libraries/universal-dao"

**Cause**: Missing .json extension

**Fix**:
1. Find entries with incorrect extension:
   ```bash
   jq '.mappings[] | select(.target_files[] | endswith(".json") | not) | {id, target_files}' work/YYYYMMDD/mapping/mapping-v6.json
   ```
2. Add .json extension to each target_files entry
3. Re-run validation

#### Error: "Invalid naming: features/libraries/UniversalDAO.json"

**Cause**: Not using kebab-case (contains uppercase)

**Fix**:
1. Convert to kebab-case: `UniversalDAO.json` → `universal-dao.json`
2. Update mapping:
   ```bash
   jq '(.mappings[] | select(.id == "v6-0123").target_files) |= map(gsub("UniversalDAO"; "universal-dao"))' work/YYYYMMDD/mapping/mapping-v6.json > temp.json && mv temp.json work/YYYYMMDD/mapping/mapping-v6.json
   ```
3. Re-run validation

#### Error: "Target in wrong directory: about/nablarch-batch.json for category batch-nablarch"

**Cause**: Category type → directory mapping not followed

**Fix**:
1. Check category in entry
2. Refer to category → directory mapping table in Design Doc Section 2.4
3. Correct directory: `batch-nablarch` (processing-pattern) → `features/processing/`
4. Update target_files: `features/processing/nablarch-batch.json`
5. Re-run validation

### General Error Recovery Tips

1. **Always read validation output carefully** - It tells you exactly what's wrong
2. **Fix one error at a time** - Don't try to fix everything at once
3. **Re-run validation after each fix** - Confirm the fix worked before proceeding
4. **Use jq for precise edits** - Avoid manual JSON editing which can introduce syntax errors
5. **Keep work log** - Document issues encountered and solutions for future reference

### Emergency Recovery

If you get stuck and validation keeps failing:

1. **Backup current work**:
   ```bash
   cp work/YYYYMMDD/mapping/mapping-v6.json work/YYYYMMDD/mapping/mapping-v6-backup.json
   ```

2. **Identify the last known good state** - Check progress tracker to see which batch completed successfully

3. **Restore from backup if needed**:
   ```bash
   cp work/YYYYMMDD/mapping/mapping-v6-backup.json work/YYYYMMDD/mapping/mapping-v6.json
   ```

4. **Resume from last good batch** - Re-process the failed batch more carefully

---

## Phase 7: Final Validation

**Script**: `doc/scripts/07-final-validation.sh`

**What it checks**:
1. **Completeness**:
   - All fields populated (no empty categories or target_files)
   - Entry count matches source file count
2. **Consistency**:
   - All source_file paths exist
   - All categories defined in categories-v*.json
   - All target paths follow directory structure
3. **Quality**:
   - No duplicate IDs
   - No duplicate source files
   - Target file naming conventions followed

**Execution**:
```bash
doc/scripts/07-final-validation.sh
```

**Output**:
- `work/YYYYMMDD/mapping/validation-report.md` - Detailed validation results
- Exit code 0 if all validations pass, 1 if errors found

**If validation passes**:
- Mappings are ready for review
- Generate summary statistics

**If validation fails**:
- Review validation-report.md
- Fix issues
- Re-run validation

---

## Success Criteria

### Mapping Quality
- [ ] All official documentation files are mapped
- [ ] Language priority applied correctly (en first, ja fallback)
- [ ] All entries have valid categories
- [ ] All entries have appropriate target_files
- [ ] All validations pass

### Coverage
- [ ] v6: ~330-340 .rst files (en only)
- [ ] v6: ~160-170 .md files (dev guide)
- [ ] v6: ~10-20 .xml files (archetype pom.xml)
- [ ] v5: Similar numbers for v5 sources

### Traceability
- [ ] Work logs document the process
- [ ] Validation reports saved
- [ ] Progress tracked at each phase

---

## Notes

### File Type Inclusion Rules
- **`.rst` files**: All documentation files
- **`.md` files**: All from development guide
- **`.xml` files**: Only `pom.xml` from archetypes (exclude build configs, parent poms not relevant to users)

### Language Priority Rationale
English documentation is the primary source for knowledge files (nabledge will communicate in Japanese but use English docs as source). Japanese fallback ensures complete coverage for files not yet translated.

### Category Assignment Guidelines
- Multiple categories allowed (e.g., a handler can be both `handler` and `batch-nablarch`)
- Processing pattern categories should be mutually exclusive (only one of batch-nablarch, rest, etc.)
- Component categories can combine with processing patterns

### Target File Naming
- Use descriptive, clear names (e.g., `universal-dao.json` not `dao.json`)
- Follow existing patterns in `.claude/skills/nabledge-6/knowledge/`
- Group related content (e.g., multiple handler docs → one handler knowledge file if closely related)

---

## Troubleshooting

### Issue: File count mismatch
**Symptom**: Script reports different count than expected
**Solution**:
1. Run `doc/scripts/02-validate-files.sh` to identify discrepancy
2. Check for new/deleted files in official docs
3. Check file type filtering rules

### Issue: Category validation fails
**Symptom**: Unknown category ID in mappings
**Solution**:
1. Check categories-v*.json for typos
2. Verify category ID matches exactly (case-sensitive)
3. Update categories-v*.json if new category needed

### Issue: Target path validation fails
**Symptom**: Path doesn't match directory structure
**Solution**:
1. Review Design Doc Section 2.4 for correct directory
2. Check category type → directory mapping table
3. Fix target_files path format

---

## Reference Documents

- [Design Document](nabledge-design.md)
  - [Section 1.5: Scope](nabledge-design.md#15-スコープ)
  - [Section 2.4: File Structure](nabledge-design.md#24-ファイル構成)
- [Category Definitions](../work/20260213/create-mapping-info/categories-v6.json)
- [Validation Procedure](mapping-validation-procedure.md) (for content validation after creation)
