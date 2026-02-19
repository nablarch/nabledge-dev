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
  "title_ja": "ハンドラ",
  "official_url": "https://nablarch.github.io/docs/LATEST/doc/ja/application_framework/application_framework/handlers/index.html",
  "mappings": [
    {
      "category": "handlers",
      "target_file": "component/handlers/overview.md"
    },
    {
      "category": "nablarch-batch",
      "target_file": "processing-pattern/nablarch-batch/handlers.md"
    }
  ]
}
```

**Fields**:
- `source_file`: Path to official doc file (relative to repository root)
- `title`: File title in English (from rst/md header or filename)
- `title_ja`: File title in Japanese (extracted by accessing official_url and parsing page title for validation)
- `official_url`: Official Japanese documentation URL (for traceability and title extraction)
- `mappings`: Array of category-to-target-file pairs
  - `category`: Category ID (must exist in categories file)
  - `target_file`: Target knowledge file path

**Key Design Decisions**:
- One source file can map to multiple categories (via mappings array)
- Each category mapping produces a separate target knowledge file
- Mappings array enables flexible filtering by category ID

## Classification Taxonomy

Category IDs and names follow official Nablarch English documentation terminology.

**Note**: The table below provides structure and rules. Actual source file paths are determined during mapping creation by scanning official documentation directories.

| Type | Category | Source Path Pattern | Pattern Completeness | Target Path | Target Naming Rule |
|------|----------|---------------------|----------------------|-------------|--------------------|
| processing-pattern | nablarch-batch | `**/batch/**/*.{rst,md}` | Partial (requires manual review - processing patterns not determinable from path) | `processing-pattern/nablarch-batch/*.md` | Based on source filename, may split by subtopic |
| processing-pattern | jakarta-batch | `**/batch/jsr352/**/*.{rst,md}` | Complete | `processing-pattern/jakarta-batch/*.md` | Based on source filename |
| processing-pattern | restful-web-service | `**/web_service/**/*.{rst,md}` | Complete | `processing-pattern/restful-web-service/*.md` | Based on source filename |
| processing-pattern | http-messaging | `**/messaging/http/**/*.{rst,md}` | Complete | `processing-pattern/http-messaging/*.md` | Based on source filename |
| processing-pattern | web-application | `**/web/**/*.{rst,md}` (exclude `web_service/`) | Partial (requires manual review) | `processing-pattern/web-application/*.md` | Based on source filename |
| processing-pattern | mom-messaging | `**/messaging/mom/**/*.{rst,md}` | Complete | `processing-pattern/mom-messaging/*.md` | Based on source filename |
| processing-pattern | db-messaging | `**/db_messaging/**/*.{rst,md}` | Complete | `processing-pattern/db-messaging/*.md` | Based on source filename |
| component | handlers | `**/handlers/**/*.{rst,md}` | Partial (handler content also in adapters/libraries) | `component/handlers/*.md` | Based on source filename, may consolidate related handlers |
| component | libraries | `**/library/**/*.{rst,md}` | Partial (scattered across multiple directories) | `component/libraries/*.md` | Based on source filename and function |
| component | adapters | `**/adapters/**/*.{rst,md}` | Partial (scattered across multiple directories) | `component/adapters/*.md` | Based on source filename and integration target |
| component | development-tools | `**/tools/**/*.{rst,md}` | Complete | `component/development-tools/*.md` | Based on source filename |
| setup | blank-project | `**/blank_project/**/*.{rst,md}` | Complete | `setup/blank-project/*.md` | Single consolidated file |
| setup | maven-archetype | `**/archetype/**/*.{rst,md}` | Complete | `setup/maven-archetype/*.md` | Single consolidated file |
| setup | configuration | `**/configuration/**/*.{rst,md}` | Complete | `setup/configuration/*.md` | Based on source filename |
| setup | setting-guide | `**/setting_guide/**/*.{rst,md}` | Complete | `setup/setting-guide/*.md` | Based on source filename |
| guide | nablarch-patterns | `nablarch-patterns/*.md` (from nablarch-system-development-guide) | Complete | `guide/nablarch-patterns/*.md` | Keep original filename |
| check | security-check | `Nablarch機能のセキュリティ対応表.xlsx` (from nablarch-system-development-guide) | Complete | `check/security-check/*.xlsx` | Direct copy with rename |
| about | about-nablarch | `**/about/**/*.{rst,md}` | Complete | `about/about-nablarch/*.md` | Based on source filename |
| about | migration | `**/migration/**/*.{rst,md}` | Complete | `about/migration/*.md` | Based on source filename |
| about | release-notes | `**/releases/**/*.{rst,md}` | Complete | `about/release-notes/*.md` | Based on source filename |

**Pattern Completeness**:
- **Complete**: Path pattern covers all relevant files; automatic mapping possible without manual verification
- **Partial**: Path pattern is incomplete or requires content inspection; manual review mandatory
  - Processing patterns like nablarch-batch may be included in adapter/library content, requiring manual inspection
  - Handlers, libraries, and adapters have content distributed across multiple directories

**Path Pattern Notes**:
- `**` matches any directory depth
- `{rst,md}` matches either .rst or .md extensions
- Actual paths determined by scanning official documentation during mapping creation
- Manual verification required for all "Partial" categories

## Source File Scope

### nablarch-document (v6 and v5)

**Include**: All `.rst` and `.md` files
- Prioritize `en/` directory files when available
- Fallback to `ja/` directory if English version does not exist

**Exclude**:
- `README.md` (root level) - Build and setup instructions
- `.textlint/install.md` - Textlint installation instructions
- `.textlint/test/test.rst` - Textlint test file
- All non-documentation files (`.py`, `.css`, `.js`, `.html`, `.png`, `.jpg`, `.gif`, `.svg`, `.patch`, `.json`, `Makefile`, etc.)

### nablarch-system-development-guide (v6 and v5)

**Include**:
- v6: `.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/*.md` (exclude README.md)
- v6: `.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
- v5: Copy v6 paths as starting point (no v5-specific version exists)

**Note**: v5 mapping uses v6 official documentation paths as source. Content verification and updates for v5-specific features happen during knowledge file creation (see "Considerations for Knowledge File Creation Skill" section).

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
- `title`: File title (English)
- `title_ja`: File title (Japanese)
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
   - Column headers: source_file, title, title_ja, official_url, category, target_file, type
   - Hyperlinks in official_url column
   - Filters on all columns
   - Rows sorted by source_file, then by category
5. Output to mapping-v6.xlsx and mapping-v5.xlsx

## Considerations for Knowledge File Creation Skill

When creating a skill to generate knowledge files from this mapping:

1. **Asset Collection**: Automatically parse asset reference directives in rst/md files and copy referenced assets (images, Excel files, etc.) to `assets/` subdirectory within the same directory as the target knowledge file
   - Target location: `assets/` subdirectory in the same directory as the knowledge file
   - Example: If target file is `.claude/skills/nabledge-6/knowledge/processing-pattern/nablarch-batch/handlers.md`, assets go to `.claude/skills/nabledge-6/knowledge/processing-pattern/nablarch-batch/assets/image.png`
   - Assets are stored alongside knowledge files within the skill's knowledge directory structure for easy reference

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

6. **v5 Content Review**: When creating v5 knowledge files from v6 official documentation paths, review content during knowledge file creation to ensure v5-specific terminology and features are accurately reflected
   - v6 official documentation paths are used as the starting point (v5 mapping is created by copying from v6)
   - During content conversion, verify and update references to v5-specific APIs, features, and terminology
   - Example differences: Java EE vs Jakarta EE, javax.* vs jakarta.* packages, Java 8 vs Java 17 features

## Validation

### Validation Script

Create `validate-mapping.sh` to verify:

1. **Category Verification**: Check that all category IDs in mappings exist in categories file
2. **Path Verification**: Verify that all source_file paths exist
3. **URL Verification**: Verify that official URLs follow conversion rules and are accessible (HTTP 200 response)
4. **Title Verification**: Access each official URL, extract the Japanese page title from HTML `<title>` tag or heading, and verify it matches the `title_ja` field in mapping
   - For nablarch-document: Parse `https://nablarch.github.io/docs/LATEST/doc/ja/{path}.html` and extract title
   - For nablarch-system-development-guide: Parse GitHub page and extract markdown heading
   - Report any mismatches for manual review
   - Japanese titles are required for automated validation and user-facing documentation
5. **Statistics Generation**: Generate category statistics (files per category, mappings per category)

### Output

- List of undefined category IDs (if any)
- List of missing source files (if any)
- List of invalid URLs (if any)
- List of title mismatches between mapping and actual pages (if any)
- Category statistics table

## Implementation Notes

- Focus on v6 first since nabledge-6 is the primary target
- Use Japanese documentation URLs (Nablarch users are Japanese)
- Store mapping files in work directory temporarily
- When knowledge file creation skill is ready, it will reference these mappings
- Excel export enables efficient review by non-technical stakeholders
