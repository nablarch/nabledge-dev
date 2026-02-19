# Mapping File Design

This document describes the design of mapping files that connect Nablarch official documentation to nabledge knowledge files.

## Overview

Mapping files provide structured information to enable:
- Automatic knowledge file generation from official documentation
- Category-based filtering for targeted processing
- Traceability from knowledge files back to official sources
- Automated asset collection through reference directives

## File Structure

### Categories File

**Files**: `categories-v6.json`, `categories-v5.json`

Each category entry:

```json
{
  "id": "nablarch-batch",
  "name": "Nablarch Batch Application",
  "description": "Nablarch on-demand batch processing framework",
  "type": "processing-pattern"
}
```

**Fields**:
- `id`: Category identifier (used in mapping files for filtering)
- `name`: Display name (from official Nablarch English documentation)
- `description`: What this category includes
- `type`: Category group (processing-pattern, component, setup, guide, check, about)

### Mapping File

**Files**: `mapping-v6.json`, `mapping-v5.json`

Each mapping entry:

```json
{
  "source_file": "ja/application_framework/application_framework/handlers/index.rst",
  "title": "Handlers",
  "official_url": "https://nablarch.github.io/docs/LATEST/doc/ja/application_framework/application_framework/handlers/index.html",
  "mappings": [
    {
      "category": "handlers",
      "target_file": "handlers/overview.md"
    },
    {
      "category": "nablarch-batch",
      "target_file": "batch/handlers.md"
    }
  ]
}
```

**Fields**:
- `source_file`: Path to official doc file (relative to repository root)
- `title`: File title (from rst/md header or filename)
- `official_url`: Official Japanese documentation URL (for traceability)
- `mappings`: Array of category-to-target-file pairs
  - `category`: Category ID (must exist in categories file)
  - `target_file`: Target knowledge file path

**Key Design Decisions**:
- One source file can map to multiple categories (via mappings array)
- Each category mapping produces a separate target knowledge file
- Mappings array enables flexible filtering by category ID

## Classification Taxonomy

Category IDs and names follow official Nablarch English documentation terminology.

### Processing Patterns (type: processing-pattern)
- `nablarch-batch` - Nablarch Batch Application
- `jakarta-batch` - Jakarta Batch
- `restful-web-service` - RESTful Web Service
- `http-messaging` - HTTP Messaging
- `web-application` - Web Application
- `mom-messaging` - Messaging with MOM
- `db-messaging` - Messaging Using Tables as Queues

### Components (type: component)
- `handlers` - Handlers
- `libraries` - Libraries
- `adapters` - Adapters
- `development-tools` - Development Tools

### Setup (type: setup)
- `blank-project` - Blank Project
- `maven-archetype` - Maven Archetype
- `configuration` - Configuration
- `setting-guide` - Setting Guide

### Development Guides (type: guide)
- `nablarch-patterns` - Nablarch Patterns

### Check Items (type: check)
- `security-check` - Security Check

### About (type: about)
- `about-nablarch` - About Nablarch
- `migration` - Migration
- `release-notes` - Release Notes

## Source File Scope

### nablarch-document (v6 and v5)

**Include**: All `.rst` and `.md` files in `ja/` directory

**Exclude**:
- `README.md` (root level) - Build and setup instructions
- `.textlint/install.md` - Textlint installation instructions
- `.textlint/test/test.rst` - Textlint test file
- All non-documentation files (`.py`, `.css`, `.js`, `.html`, `.png`, `.jpg`, `.gif`, `.svg`, `.patch`, `.json`, `Makefile`, etc.)

**File Counts**:
- v6: 334 Japanese documentation files
- v5: 431 Japanese documentation files

### nablarch-system-development-guide (v6 only)

**Include**:
- `.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/*.md` (exclude README.md)
- `.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`

**File Counts**:
- 3 md files (nablarch-patterns)
- 1 xlsx file (security matrix)

### nablarch-single-module-archetype

**Exclude**: All files (removed from scope)

## Official URL Conversion Rules

### nablarch-document

- Local path: `.lw/nab-official/v6/nablarch-document/ja/{path}.rst`
- Official URL: `https://nablarch.github.io/docs/LATEST/doc/ja/{path}.html`
- Extension: `.rst` → `.html`

### nablarch-system-development-guide

- Local path: `.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/{path}.md`
- Official URL: `https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/Nablarchシステム開発ガイド/{path}.md`
- Extension: Keep `.md`

## Asset Files

Asset files (images, Excel templates, etc.) are **not included in mapping files**. They will be automatically collected during knowledge file creation by parsing asset reference directives in rst/md files.

### Asset Reference Directives

**reStructuredText (.rst)**:
- `.. image:: path/to/image.png` - Image reference
- `.. figure:: path/to/image.png` - Figure (image with caption) reference
- `:download:`text <path/to/file.xlsx>`` - Downloadable file reference

**Markdown (.md)**:
- `![alt](path/to/image.png)` - Image reference

## Excel Export Format

For user review, mapping JSON files are converted to Excel with the following structure:

### Columns

- `source_file`: Path to official doc file
- `title`: File title
- `official_url`: Official documentation URL (hyperlink)
- `category`: Category ID
- `target_file`: Target knowledge file path
- `type`: Category type (processing-pattern, component, etc.)

### Format Rules

- One row per category mapping (source files with multiple mappings have multiple rows)
- Sort by source_file, then by category
- Use Excel hyperlinks for official_url column
- Apply filters to all columns for easy navigation

### Conversion Script

Create `json-to-excel.py` (or shell script with appropriate tools) to:

1. Read mapping JSON files (mapping-v6.json, mapping-v5.json)
2. Read categories JSON files to look up category type
3. Flatten mappings array (one row per category mapping)
4. Generate Excel file with:
   - Column headers: source_file, title, official_url, category, target_file, type
   - Hyperlinks in official_url column
   - Filters on all columns
   - Rows sorted by source_file, then by category
5. Output to mapping-v6.xlsx and mapping-v5.xlsx

## Considerations for Knowledge File Creation Skill

When creating a skill to generate knowledge files from this mapping:

1. **Asset Collection**: Automatically parse asset reference directives in rst/md files and copy referenced assets (images, Excel files, etc.) to the target location

2. **Category Filtering**: Allow filtering by specific category IDs to process only targeted documentation
   - Example: "process only nablarch-batch and restful-web-service files"
   - Agents filter mapping entries where `mappings[].category` matches desired IDs

3. **Official URL**: Include the official_url in generated knowledge files for traceability
   - Users can navigate from knowledge files back to official documentation

4. **Multiple Mappings**: One source file may generate multiple target files
   - Process each entry in the `mappings` array separately
   - Each category mapping produces its own target knowledge file

5. **Focus on Conversion**: The skill should focus on content conversion and search hint extraction
   - Asset collection should be automated (not manual)
   - Agents parse directives to find referenced assets

## Validation

### Validation Script

Create `validate-mapping.sh` to verify:

1. **File Count Verification**: Compare mapped file count with actual files in source directories
2. **Category Verification**: Check that all category IDs in mappings exist in categories file
3. **Path Verification**: Verify that all source_file paths exist
4. **URL Verification**: Verify that official URLs follow conversion rules
5. **Statistics Generation**: Generate category statistics (files per category, mappings per category)

### Output

- File count comparison (expected vs actual)
- List of undefined category IDs (if any)
- List of missing source files (if any)
- List of invalid URLs (if any)
- Category statistics table

## Implementation Notes

- Focus on v6 first since nabledge-6 is the primary target
- Use Japanese documentation URLs (Nablarch users are Japanese)
- Store mapping files in work directory temporarily
- When knowledge file creation skill is ready, it will reference these mappings
- Excel export enables efficient review by non-technical stakeholders
