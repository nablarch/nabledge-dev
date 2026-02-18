# Mapping Creation Procedure

**Version**: 3.0
**Purpose**: Create source-to-target mapping JSON for Nablarch knowledge file generation

---

## Overview

Create a JSON mapping file that links Nablarch official documentation to target knowledge files.

The official documentation consists of 3 directories:
1. `nablarch-document` (main documentation, called "nab-doc")
2. `nablarch-*-archetype` (Maven archetypes)
3. `nablarch-system-development-guide` (development guide, v6 only)

**Strategy**:
- **Non-nab-doc**: Use whitelist approach (user approves file list, categories are self-evident)
- **Nab-doc**: Use rule-based categorization for most files, AI judgment for the rest
- **All**: Generate target filenames from source paths

---

## Inputs

- **version**: Target version (e.g., "6", "5")
- **source_base**: Base directory (e.g., `.lw/nab-official/v6/`)
- **output_file**: Output path (e.g., `doc/mapping-creation/mapping-v6.json`)

---

## Procedure

### Step 1: Process Non-Nab-Doc Directories

#### 1.1: Archetype Files

Find archetype directory:
```bash
ls -d {source_base}/nablarch-*-archetype
```

List all files (exclude .git, target/, IDE files, OS files):
```bash
find {archetype_dir} -type f \
  -not -path "*/.git/*" \
  -not -path "*/target/*" \
  -not -path "*/.idea/*" \
  -not -path "*/.vscode/*" \
  -not -name ".DS_Store" \
  -not -name "Thumbs.db"
```

Show whitelist to user:
```
Archetype whitelist: {archetype_name}
Total: {count} files
Examples:
  - pom.xml
  - src/main/resources/entity/User.sql
  - src/main/java/com/example/Sample.java

Approve this whitelist? (Y/N)
```

If approved, add to mapping with:
- Category: `["archetype"]`
- Target: `archetype/{filename-in-kebab-case}.json`

#### 1.2: Development Guide Files

Find dev guide directory:
```bash
# For v6
ls -d {source_base}/nablarch-system-development-guide

# For v5 (use v6 guide)
ls -d .lw/nab-official/v6/nablarch-system-development-guide
```

**Note**: v5 does not have its own dev guide. Use v6 dev guide for v5 mapping.

List documentation files:
```bash
find {dev_guide_dir} -type f \( -name "*.md" -o -name "*.adoc" \)
```

Show whitelist to user (same format as 1.1).

If approved, add to mapping with categories:
- Path contains `patterns/`: `["dev-guide-pattern"]`
- Path contains `anti-pattern`: `["dev-guide-anti"]`
- Otherwise: `["dev-guide-other"]`
- Target: `guides/{filename-in-kebab-case}.json`

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

### Step 3: Discover Path Patterns and Build Categorization Rules

**Task**: Analyze file paths to discover patterns and create categorization rules.

**Input**:
- List of nab-doc file paths (from Step 2)
- Category definitions from `doc/mapping-creation/categories-v{version}.json`

**Process**:

1. **Sample paths**: Examine file paths and identify directory structure patterns
   - Example paths to analyze:
     - `nablarch-document/en/application_framework/application_framework/handlers/web/...`
     - `nablarch-document/en/application_framework/application_framework/libraries/...`
     - `nablarch-document/en/application_framework/application_framework/batch/...`

2. **Discover patterns**: Look for path segments that indicate categories
   - Component types: `/handlers/`, `/libraries/`, `/adaptors/`
   - Processing patterns: `/batch/`, `/rest/`, `/web/`, `/messaging/`
   - Document types: `/development_tools/`, `/migration/`, `/about_nablarch/`

3. **Build rules**: Create path matching rules that map to categories
   - Rules should be deterministic (same path always gives same categories)
   - Rules should handle multiple categories when applicable
   - Example rule format: `if path contains X then assign category Y`

4. **Apply rules**: Run rules on all nab-doc files
   - Store files with assigned categories
   - Store files without matches for AI judgment (Step 4)

**Key principles**:
- Component categories (handler, library, adaptor) are usually clear from path
- Handlers often combine with processing patterns (e.g., rest + handler)
- Adaptors are standalone, NOT libraries
- When in doubt, fewer categories is better than over-categorizing

---

### Step 4: AI Judgment for Remaining Files

For files without rule-based categories, read file content and determine categories.

**Process**:

1. **Check if navigation-only**:
   - Read file content (first 50-100 lines)
   - If contains ONLY navigation (toctree directives, link lists) without technical content:
     - Set `_no_content: true` with reason
     - Skip to next file

2. **Determine categories from content**:
   - Read enough content to understand the file's purpose
   - Look for technical indicators:
     - Class/interface definitions → component type
     - API documentation → component or library
     - Tutorial/guide content → setup or about
     - Configuration examples → configuration
   - Refer to category definitions in `categories-v{version}.json`
   - Assign appropriate categories based on content

3. **Apply category combination rules**:
   - Handlers: Include processing pattern if identifiable
   - Libraries: Include processing pattern only if library is specific to that pattern
   - Setup/Configuration/About: Usually standalone
   - When uncertain: Use fewer categories (don't over-categorize)

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

Design a directory structure that organizes target files by category:
- Component types (handler, library, adaptor, tool) should be grouped
- Handlers may be further subdivided by processing pattern
- Processing patterns without component type get their own location
- Setup, configuration, guides, and other document types get separate locations
- Use a logical hierarchy that makes files easy to find

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
