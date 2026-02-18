# Mapping Creation Procedure

**Version**: 3.0
**Purpose**: Create source-to-target mapping JSON for Nablarch knowledge file generation

---

## Overview

Create a JSON mapping file that links Nablarch official documentation to target knowledge files.

**Goal**: Classify each source file into one or more categories defined in `categories-v{version}.json`, then generate appropriate target file paths.

The official documentation consists of 3 directories:
1. `nablarch-document` (main documentation, called "nab-doc")
2. `nablarch-*-archetype` (Maven archetypes)
3. `nablarch-system-development-guide` (development guide, v6 only)

**Categorization Strategy**:
- Load category definitions from `categories-v{version}.json` (e.g., `handler`, `library`, `batch`, `rest`, `security-check`)
- **Multiple categories allowed**: A file can belong to multiple categories (e.g., `["handler", "batch"]`)
- **Rule-based first**: Apply path pattern rules to auto-categorize most files
- **AI judgment for unclear cases**: Read content and manually assign categories for files without clear path patterns
- **Target paths based on categories**: Use assigned categories to determine target directory structure

---

## Inputs

- **version**: Target version (e.g., "6", "5")
- **source_base**: Base directory (e.g., `.lw/nab-official/v6/`)
- **output_file**: Output path (e.g., `doc/mapping-creation/mapping-v6.json`)

---

## Procedure

### Step 1: Process Development Guide Files

**Source**: `nablarch-system-development-guide` (Japanese version only)

**Note**:
- v5 does not have its own dev guide. Use v6 dev guide for v5 mapping.
- Archetype files (`nablarch-*-archetype`) are **excluded** from mapping.

#### 1.1: Nablarch Patterns

Find pattern files (Japanese):
```bash
find {source_base}/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns \
  -type f \( -name "*.md" -o -name "*.adoc" \) \
  -not -name "README.md"
```

Add to mapping with categories based on filename:
- Filename contains `アンチパターン` or `anti-pattern`: `["dev-guide-anti"]`
- Otherwise: `["dev-guide-pattern"]`
- Target: `guides/patterns/{filename-in-kebab-case}.json`

#### 1.2: Security Matrix

Find security matrix file (Japanese):
```bash
find {source_base}/nablarch-system-development-guide/Sample_Project/設計書 \
  -name "*セキュリティ対応表.xlsx"
```

Expected file: `Nablarch機能のセキュリティ対応表.xlsx`

Add to mapping with:
- Category: `["dev-guide-other"]`
- Target: `guides/patterns/nablarch-security-matrix.json`

---

### Step 2: Extract Nab-Doc File Paths

List all documentation files:
```bash
find {source_base}/nablarch-document -type f \
  \( -name "*.rst" -o -name "*.md" -o -name "*.xml" \) \
  -not -path "*/.git/*"
```

Apply language priority (English over Japanese):
```python
paths_by_name = {}
for path in all_paths:
    if '/en/' in path:
        key = path.replace('/en/', '/')
        paths_by_name[key] = path  # English priority
    elif '/ja/' in path:
        key = path.replace('/ja/', '/')
        if key not in paths_by_name:  # Only if no English
            paths_by_name[key] = path

final_paths = list(paths_by_name.values())
```

---

### Step 3: Apply Category Rules to Files

**Goal**: Categorize files using rule-based path pattern matching against defined categories.

**Input**:
- List of nab-doc file paths (from Step 2)
- Category definitions from `doc/mapping-creation/categories-v{version}.json`

**Process**:

1. **Load category definitions**: Read `categories-v{version}.json` to get all valid category IDs
   - Example: `handler`, `library`, `adaptor`, `tool`, `batch`, `rest`, `web`, `security-check`, `setup`, `configuration`, `about`, `migration`
   - These IDs are the **target vocabulary** - the only valid values for categorization

2. **Implement path pattern matching rules**: Create rules that analyze file paths and assign appropriate category IDs

   **Component categories** (from path structure):
   - `handler`: `/handlers/` in path
   - `library`: `/libraries/` in path
   - `adaptor`: `/adaptors/` in path
   - `tool`: `/development_tools/` or `/tools/` in path
   - `security-check`: `/authorization/` or `permission` or `security` in path

   **Processing pattern categories** (from path structure):
   - `batch`: `/batch/` in path
   - `rest`: `/rest/` or `/jaxrs/` in path
   - `web`: `/web/` in path (but not if `/messaging/` also present)
   - `messaging`: `/messaging/` in path

   **Document type categories** (from path structure):
   - `setup`: `/blank_project/` or `/getting_started/` or `setup` in path
   - `configuration`: `/configuration/` or `config` in path
   - `about`: `/about_nablarch/` or `/nablarch/` (architecture, policy docs)
   - `migration`: `/migration/` in path

3. **Apply all rules to each file**: For every file, check ALL category rules
   - A file can match multiple categories (e.g., both `handler` and `batch`)
   - Collect all matching category IDs for each file
   - Example: `handlers/batch/loop_handler.rst` → `["handler", "batch"]`

4. **Store results**:
   - Files with 1+ matched categories: Store with category list
   - Files with 0 matched categories: Mark for AI judgment (Step 4)

**Key principles**:
- Files can have MULTIPLE categories (not just one)
- All category rules must be checked for every file
- Rules are based on path patterns, using category definitions as the target vocabulary
- Component + Processing pattern combinations are common (e.g., `handler` + `rest`)
- When path matches multiple rules, include ALL matched categories

---

### Step 4: AI Judgment for Remaining Files

**Goal**: Categorize files that didn't match any path rules by reading content and mapping to defined categories.

**Input**:
- Files with no matched categories from Step 3
- Category definitions from `doc/mapping-creation/categories-v{version}.json`

**Process**:

1. **Check if navigation-only**:
   - Read file content (first 50-100 lines)
   - If contains ONLY navigation (toctree directives, link lists) without technical content:
     - Set `_no_content: true` with reason
     - Skip to next file

2. **Determine categories from content**: Read file content and match to defined categories

   **Use category definitions** (`categories-v{version}.json`) as the vocabulary:
   - Available category IDs: `handler`, `library`, `adaptor`, `tool`, `security-check`, `batch`, `rest`, `web`, `messaging`, `setup`, `configuration`, `about`, `migration`, `dev-guide-pattern`, `dev-guide-anti`, `dev-guide-other`

   **Content indicators** → Category mapping:
   - Handler class/interface definitions → `handler`
   - Library/utility functions → `library`
   - Third-party integration → `adaptor`
   - Testing tools, analysis tools → `tool`
   - Authentication, authorization, permission → `security-check`
   - Batch processing concepts → `batch`
   - REST API concepts → `rest`
   - Web UI concepts → `web`
   - Messaging concepts → `messaging`
   - Project setup, installation → `setup`
   - Configuration settings → `configuration`
   - Framework overview, architecture → `about`
   - Version migration → `migration`

3. **Assign categories** (multiple allowed):
   - A file can have multiple categories if it covers multiple aspects
   - Example: A file about REST handlers → `["handler", "rest"]`
   - Example: Security library documentation → `["library", "security-check"]`
   - Prefer fewer categories when uncertain (avoid over-categorization)

4. **Store results**:
   - Files with categories: Store with category ID list
   - Navigation-only files: Mark with `_no_content: true`

---

### Step 5: Generate Target File Names

For each file with categories (not `_no_content`):

#### 5.1: Generate Base Name

```python
filename = source_path.split('/')[-1]
name = filename.rsplit('.', 1)[0]  # Remove extension
name = name.lower()
name = name.replace('_', '-')
```

#### 5.2: Add Prefix if Needed

Generic names need parent directory prefix:
```python
generic_names = ['index', 'overview', 'main', 'introduction', 'readme']
if name in generic_names:
    parent_dir = source_path.split('/')[-2]
    name = f"{parent_dir}-{name}"
```

#### 5.3: Determine Directory by Category

Map categories to target directory structure. Use the **first category** as primary, additional categories for context:

**Category → Directory mapping**:
- `handler` + processing pattern → `features/handlers/{pattern}/` (e.g., `batch`, `rest`, `web`)
- `handler` (alone) → `features/handlers/common/`
- `library` → `features/libraries/`
- `adaptor` → `features/adaptors/`
- `tool` → `features/tools/`
- `security-check` → `features/security/`
- `batch` (no component) → `features/batch/`
- `rest` (no component) → `features/rest/`
- `web` (no component) → `features/web/`
- `messaging` (no component) → `features/messaging/`
- `setup` → `guides/setup/`
- `configuration` → `guides/configuration/`
- `about` → `guides/about/`
- `migration` → `guides/migration/`
- `dev-guide-pattern`, `dev-guide-anti`, `dev-guide-other` → `guides/patterns/`

**Logic**:
1. If first category is component type (`handler`, `library`, `adaptor`, `tool`, `security-check`):
   - Use component-based directory
   - For `handler`: check second category for processing pattern subdirectory
2. If first category is processing pattern (`batch`, `rest`, `web`, `messaging`):
   - Use pattern-based directory under `features/`
3. If first category is document type (`setup`, `configuration`, `about`, `migration`, `dev-guide-*`):
   - Use guide-based directory

Create target path: `{directory}/{name}.json`

#### 5.4: Handle Conflicts

If target name already exists:
1. Add category prefix: `{category}-{name}.json`
2. Add parent directory: `{parent}-{name}.json`
3. Add numeric suffix: `{name}-2.json`

---

### Step 6: Extract Titles

For RST files (`.rst`):
```python
# Look for:
# Title
# =====
for i, line in enumerate(lines[:20]):
    if i+1 < len(lines) and (lines[i+1].startswith('===') or lines[i+1].startswith('---')):
        title = line.strip()
        break
else:
    title = filename_to_title(filename)
```

For Markdown files (`.md`):
```python
# Look for: # Title
for line in lines[:20]:
    if line.startswith('# '):
        title = line[2:].strip()
        break
else:
    title = filename_to_title(filename)
```

For XML files: Use filename as title.

Filename to title:
```python
def filename_to_title(filename):
    name = filename.rsplit('.', 1)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return name.title()
```

---

### Step 7: Build Mapping JSON

```python
mapping = {
    "schema_version": "1.0",
    "version": version,
    "created_at": datetime.now().isoformat(),
    "mappings": []
}

entry_id = 1
for source_file in all_files:
    entry = {
        "id": f"v{version}-{entry_id:04d}",
        "source_file": relative_path(source_file, source_base),
        "title": extract_title(source_file),
        "categories": get_categories(source_file),
        "target_files": [generate_target_name(source_file)]
    }

    if is_navigation_only(source_file):
        entry["_no_content"] = True
        entry["_no_content_reason"] = get_reason(source_file)
        entry.pop("target_files")

    mapping["mappings"].append(entry)
    entry_id += 1
```

---

### Step 8: Validate

#### 8.1: No Duplicate Targets

```python
targets = [e["target_files"][0] for e in entries if "target_files" in e]
duplicates = find_duplicates(targets)

if duplicates:
    print(f"ERROR: {len(duplicates)} duplicate targets")
    # Apply conflict resolution
```

#### 8.2: Schema Compliance

```python
for entry in entries:
    assert "id" in entry
    assert "source_file" in entry
    assert "title" in entry
    assert "categories" in entry
    assert ("target_files" in entry) or (entry.get("_no_content") == True)

    assert entry["id"].startswith(f"v{version}-")
    if "target_files" in entry:
        for target in entry["target_files"]:
            assert target.endswith(".json")
            assert target == target.lower()
            assert "_" not in target
```

---

### Step 9: Write Output

Write to `{output_file}`:
```python
import json

with open(output_file, 'w') as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"✓ Written: {output_file}")
print(f"  Total entries: {len(mapping['mappings'])}")
print(f"  With targets: {count(entries with target_files)}")
print(f"  Navigation-only: {count(entries with _no_content)}")
```

Create stats file `{output_file}.stats.txt`:
```
Mapping Statistics
==================

Version: {version}
Created: {timestamp}

Totals
------
Total entries: {total}
With targets: {count}
Navigation-only: {count}

By Category
-----------
handler: {count}
library: {count}
adaptor: {count}
(... all categories ...)
```

---

## Output Schema

```json
{
  "schema_version": "1.0",
  "version": "6",
  "created_at": "2026-02-18T10:30:00+09:00",
  "mappings": [
    {
      "id": "v6-0001",
      "source_file": "nablarch-document/en/handlers/common/database_connection_management_handler.rst",
      "title": "Database Connection Management Handler",
      "categories": ["handler"],
      "target_files": ["features/handlers/common/database-connection-management-handler.json"]
    },
    {
      "id": "v6-0002",
      "source_file": "nablarch-document/en/handlers/index.rst",
      "title": "Handlers",
      "categories": ["handler"],
      "_no_content": true,
      "_no_content_reason": "Navigation only (toctree without technical content)"
    }
  ]
}
```

---

## Success Criteria

- ✅ All files processed
- ✅ No duplicate target names
- ✅ Valid JSON schema
- ✅ Stats file created

---

## Step 10: Export to Excel (Optional)

Create an Excel file for easy review of the mapping:

```python
# Using openpyxl to create a spreadsheet with:
# - Summary sheet: Overview statistics
# - Mappings sheet: All entries with source, title, categories, target
# - Stats by Category sheet: Category counts
# - Stats by Directory sheet: Target directory distribution

output_excel = f"{output_file}.xlsx"
```

Excel file format:
- **Summary**: Version, created date, totals
- **Mappings**: Full mapping table with all fields
- **Stats by Category**: Category name and count
- **Stats by Directory**: Target directory and count

---

## File Organization

All work files for a version should be organized under `doc/mapping-creation/work-v{version}/`:

```
doc/mapping-creation/
├── categories-v6.json                    # Category definitions (shared)
├── categories-v5.json                    # Category definitions (shared)
├── mapping-creation-prompt.md            # This procedure document
└── work-v6/                              # Version 6 working directory
    ├── create-mapping-v6.py              # Step 1-4: Initial mapping creation
    ├── categorize-ai-judgment-v6.py      # Step 4: AI judgment categorization
    ├── finalize-mapping-v6.py            # Step 5-9: Final merge and validation
    ├── export-to-excel-v6.py             # Step 10: Excel export (optional)
    ├── mapping-v6.json                   # Final mapping output
    ├── mapping-v6.json.stats.txt         # Statistics summary
    ├── mapping-v6.xlsx                   # Excel export for review
    ├── needs-ai-judgment-v6.json         # Intermediate: Files needing AI judgment
    └── categorized-ai-files-v6.json      # Intermediate: AI categorization results
```

Scripts should output to `doc/mapping-creation/work-v{version}/` directory.
