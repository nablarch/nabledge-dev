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

**Files**: `mapping-v6.md`, `mapping-v5.md`

Markdown table format with one row per source-to-target mapping:

| Source Path | Title | Title (ja) | Official URL | Type | Category ID | Processing Pattern | Target Path |
|-------------|-------|------------|--------------|------|-------------|-------------------|-------------|
| application_framework/application_framework/handlers/common/global_error_handler.rst | Global Error Handler | グローバルエラーハンドラ | [🔗](https://nablarch.github.io/docs/LATEST/doc/ja/application_framework/application_framework/handlers/common/global_error_handler.html) | component | handlers | | component/handlers/common/global-error-handler.md |
| application_framework/application_framework/handlers/batch/loop_handler.rst | Loop Handler | ループハンドラ | [🔗](https://nablarch.github.io/docs/LATEST/doc/ja/application_framework/application_framework/handlers/batch/loop_handler.html) | component | handlers | nablarch-batch | component/handlers/batch/loop-handler.md |
| application_framework/application_framework/batch/nablarch_batch/architecture.rst | Architecture | アーキテクチャ | [🔗](https://nablarch.github.io/docs/LATEST/doc/ja/application_framework/application_framework/batch/nablarch_batch/architecture.html) | processing-pattern | nablarch-batch | nablarch-batch | processing-pattern/nablarch-batch/architecture.md |
| development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.rst | Request Unit Test (REST) | リクエスト単体テスト (REST) | [🔗](https://nablarch.github.io/docs/LATEST/doc/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_rest.html) | development-tools | testing-framework | restful-web-service | development-tools/testing-framework/RequestUnitTest-rest.md |

**Columns**:
- `Source Path`: Path to official doc file (relative to `.lw/nab-official/v6/nablarch-document/en/` or `.lw/nab-official/v6/nablarch-system-development-guide/`). Plain text format for easy processing.
- `Title`: File title in English (extracted from `.lw/nab-official/v6/nablarch-document/en/{path}.rst` header)
- `Title (ja)`: File title in Japanese (extracted from `.lw/nab-official/v6/nablarch-document/ja/{path}.rst` header)
- `Official URL`: Official Japanese documentation URL (for user reference and traceability). Format: `[🔗](full-url)` as Markdown link
- `Type`: Category type from taxonomy (processing-pattern, component, development-tools, setup, guide, check, about)
- `Category ID`: Category identifier (must exist in categories file)
- `Processing Pattern`: Processing pattern identifier for pattern-specific files (one of: nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging). Empty for generic/shared files.
- `Target Path`: Target knowledge file path following naming conventions

**Key Design Decisions**:
- One row per source-to-target mapping (source files mapping to multiple categories have multiple rows)
- Flat table structure enables easy filtering, sorting, and review
- Human-readable format suitable for both manual editing and programmatic processing
- **Processing Pattern column** enables incremental knowledge file creation by processing pattern, as users typically need documentation for specific patterns (e.g., only nablarch-batch)

## Classification Taxonomy

Category IDs and names follow official Nablarch English documentation terminology.

| Type | Category ID |
|------|-------------|
| processing-pattern | nablarch-batch |
| processing-pattern | jakarta-batch |
| processing-pattern | restful-web-service |
| processing-pattern | http-messaging |
| processing-pattern | web-application |
| processing-pattern | mom-messaging |
| processing-pattern | db-messaging |
| component | handlers |
| component | libraries |
| component | adapters |
| development-tools | testing-framework |
| development-tools | toolbox |
| development-tools | java-static-analysis |
| setup | blank-project |
| setup | configuration |
| setup | setting-guide |
| setup | cloud-native |
| guide | nablarch-patterns |
| guide | business-samples |
| check | security-check |
| about | about-nablarch |
| about | migration |
| about | release-notes |

### Processing Pattern Assignment Rules

The `Processing Pattern` column identifies which processing pattern(s) a file is specific to. This enables incremental knowledge file creation by pattern.

**Rules**:

1. **Processing Pattern categories** (Type = `processing-pattern`):
   - Always set `Processing Pattern` = `Category ID`
   - Example: Category ID = `nablarch-batch` → Processing Pattern = `nablarch-batch`

2. **Component categories** (handlers, libraries, adapters):
   - Check source path for pattern-specific subdirectories:
     - `handlers/batch/*` → `nablarch-batch`
     - `handlers/web/*` → `web-application`
     - `handlers/rest/*` or `handlers/jaxrs/*` → `restful-web-service`
     - `handlers/messaging/*` → `mom-messaging` or `db-messaging`
     - `handlers/common/*` → Empty (generic/shared)
   - Check file content/title for pattern-specific features
   - Leave empty if the component is generic/shared across patterns

3. **Development Tools categories** (testing-framework, toolbox):
   - Check filename/path for pattern indicators:
     - `*_batch*`, `*Batch*` → `nablarch-batch` or `jakarta-batch`
     - `*_rest*`, `*_jaxrs*`, `*REST*` → `restful-web-service`
     - `*_web*`, `*Web*` → `web-application`
   - Leave empty if the tool is generic/shared

4. **Setup categories** (blank-project, configuration, setting-guide):
   - Check filename/path for pattern setup guides:
     - `setup_NablarchBatch*`, `*batch*` → `nablarch-batch`
     - `setup_Jbatch*` → `jakarta-batch`
     - `setup_WebService*`, `*rest*` → `restful-web-service`
     - `setup_Web*` (not WebService) → `web-application`
   - Leave empty for generic configuration files

5. **Guide categories** (nablarch-patterns, business-samples):
   - Usually empty unless the guide is pattern-specific
   - Check content to determine if specific to a pattern

6. **Other categories** (check, about):
   - Typically empty (generic documentation)

**Empty value**: Indicates generic/shared files used across multiple patterns or general documentation not tied to a specific pattern.

### Target Path Rules

Target paths follow the pattern: `{type}/{category-id}/{subdirectories}/{filename}.md`

**Naming conventions**:
- **Type directories**: Use Type value from taxonomy (e.g., `processing-pattern/`, `component/`, `development-tools/`, `setup/`, `guide/`, `check/`, `about/`)
- **Category ID directories**: Use Category ID value from taxonomy (e.g., `nablarch-batch/`, `testing-framework/`, `handlers/`)
- **Subdirectories**: Preserve source directory structure between category directory and filename
  - **component categories** (handlers, libraries, adapters): Preserve subdirectory structure from source
    - Example: `handlers/common/file.rst` → `component/handlers/common/file.md`
    - Example: `libraries/data_io/data_format/file.rst` → `component/libraries/data_io/data_format/file.md`
  - **Other types**: Flat structure (no subdirectories unless needed for organization)
  - Exclude `images/` directories (asset files, not documentation)
- **Filenames**: Based on source filename with `.md` extension
  - Convert underscores to hyphens (e.g., `nablarch_batch` → `nablarch-batch`)
  - Use descriptive names based on content when source filename is generic (e.g., `index.rst` → `overview.md`)
  - May split large source files into multiple target files by subtopic
  - May consolidate related source files into single target file

**Examples**:
- `processing-pattern/nablarch-batch/architecture.md` (flat structure)
- `development-tools/testing-framework/request-unit-test.md` (flat structure)
- `component/handlers/common/global-error-handler.md` (preserves `common/` subdirectory)
- `component/handlers/web/session-store-handler.md` (preserves `web/` subdirectory)
- `component/libraries/authorization/permission-check.md` (preserves `authorization/` subdirectory)
- `component/libraries/data_io/data_format/format-definition.md` (preserves `data_io/data_format/` nested subdirectories)
- `setup/configuration/db-connection.md` (flat structure)
- `guide/nablarch-patterns/api-design.md` (flat structure)

## Source File Scope

### nablarch-document (v6 and v5)

**Base directory**: `.lw/nab-official/v6/nablarch-document/en/`

**Include**: All `.rst` and `.md` files
- Source Path in table: Relative to base directory (e.g., `about_nablarch/concept.rst`)
- Prioritize `en/` directory files when available
- Fallback to `ja/` directory if English version does not exist

**Exclude**:
- `README.md` (root level) - Build and setup instructions
- `.textlint/install.md` - Textlint installation instructions
- `.textlint/test/test.rst` - Textlint test file
- All non-documentation files (`.py`, `.css`, `.js`, `.html`, `.png`, `.jpg`, `.gif`, `.svg`, `.patch`, `.json`, `Makefile`, etc.)

### nablarch-system-development-guide (v6 and v5)

**Base directory**: `.lw/nab-official/v6/nablarch-system-development-guide/`

**Include**:
- v6: `en/Nablarch-system-development-guide/docs/nablarch-patterns/*.md` (exclude README.md)
- v6: `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
- v5: Copy v6 paths as starting point (no v5-specific version exists)
- Source Path in table: Relative to base directory (e.g., `en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md`)

**Note**: v5 mapping uses v6 official documentation paths as source. Content verification and updates for v5-specific features happen during knowledge file creation (see "Considerations for Knowledge File Creation Skill" section).

### nablarch-single-module-archetype

**Exclude**: All files (removed from scope)

## Title Extraction

Titles are extracted from local rst/md file headers in both English and Japanese versions.

### nablarch-document

- **Title (English)**: Extract from `.lw/nab-official/v6/nablarch-document/en/{source_path}` header
- **Title (ja) (Japanese)**: Extract from `.lw/nab-official/v6/nablarch-document/ja/{source_path}` header
  - Replace `en/` with `ja/` in source path
- Headers are typically in the first few lines of rst files (using `===` or `---` underline format)

### nablarch-system-development-guide

- **Title (English)**: Extract from `.lw/nab-official/v6/nablarch-system-development-guide/{source_path}` header (first `#` heading)
- **Title (ja) (Japanese)**: Extract from `.lw/nab-official/v6/nablarch-system-development-guide/{source_path_ja}` header (first `#` heading)
  - Replace `en/Nablarch-system-development-guide/` with `Nablarchシステム開発ガイド/` in source path

## Official URL Generation Rules

Official URLs point to **Japanese documentation** for user reference and traceability.

### nablarch-document

- Source Path: `{path}.rst` (from table, relative to `en/` directory)
- Official URL: `https://nablarch.github.io/docs/{version}/doc/{path}.html`
  - **v6**: `{version}` = `6u3` (current minor version for nabledge-6)
  - **v5**: `{version}` = `5u26` (current minor version for nabledge-5)
- Conversion: Change `.rst` → `.html`, prepend base URL with version

Example (v6):
- Source Path: `application_framework/application_framework/handlers/common/global_error_handler.rst`
- Official URL: `https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/common/global_error_handler.html`

Example (v5):
- Source Path: `application_framework/application_framework/handlers/common/global_error_handler.rst`
- Official URL: `https://nablarch.github.io/docs/5u26/doc/application_framework/application_framework/handlers/common/global_error_handler.html`

### nablarch-system-development-guide

- Source Path: `en/Nablarch-system-development-guide/docs/nablarch-patterns/{file}.md` (from table)
- Official URL: `https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/en/Nablarch-system-development-guide/docs/nablarch-patterns/{file}.md`
- Conversion: Keep source path as-is (English directory structure), prepend base URL

Example:
- Source Path: `en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md`
- Official URL: `https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md`

**URL Format**: Use Markdown link format `[🔗](full-url)` to keep table readable while maintaining programmatic access to URLs.

## Asset Files

Asset files (images, Excel templates, etc.) are **not included in mapping files**. They will be automatically collected during knowledge file creation by parsing asset reference directives in rst/md files.

### Asset Reference Directives

**reStructuredText (.rst)**:
- `.. image:: path/to/image.png` - Image reference
- `.. figure:: path/to/image.png` - Figure (image with caption) reference
- `:download:`text <path/to/file.xlsx>`` - Downloadable file reference

**Markdown (.md)**:
- `![alt](path/to/image.png)` - Image reference

## Alternative Formats

### Excel Export (Optional)

For stakeholder review or offline editing, Markdown tables can be converted to Excel format:

**Conversion**:
- Use pandoc, Python (pandas), or manual import
- Preserve column structure and order
- Convert Official URL column to Excel hyperlinks
- Apply filters to all columns for easy navigation
- Sort by Source Path, then by Category ID

**Output**: `mapping-v6.xlsx`, `mapping-v5.xlsx`

This is optional - the Markdown table is the primary format for both human review and programmatic processing.

## Considerations for Knowledge File Creation Skill

When creating a skill to generate knowledge files from this mapping:

1. **Asset Collection**: Automatically parse asset reference directives in rst/md files and copy referenced assets (images, Excel files, etc.) to `assets/` subdirectory within the same directory as the target knowledge file
   - Target location: `assets/` subdirectory in the same directory as the knowledge file
   - Example: If target file is `.claude/skills/nabledge-6/knowledge/processing-pattern/nablarch-batch/handlers.md`, assets go to `.claude/skills/nabledge-6/knowledge/processing-pattern/nablarch-batch/assets/image.png`
   - Assets are stored alongside knowledge files within the skill's knowledge directory structure for easy reference

2. **Processing Pattern Filtering**: Enable incremental knowledge file creation by processing pattern
   - **Primary use case**: Filter by `Processing Pattern` column to create documentation for specific patterns
   - Example: "Create knowledge files for nablarch-batch" → Filter rows where `Processing Pattern` = "nablarch-batch"
   - This includes:
     - All files in `processing-pattern/nablarch-batch/` (Type = processing-pattern)
     - Pattern-specific handlers (e.g., batch handlers)
     - Pattern-specific testing documentation
     - Pattern-specific setup guides
   - Rows with empty `Processing Pattern` are generic/shared files that may be processed separately or included in all patterns

3. **Category Filtering**: Allow filtering by specific category IDs for alternative workflows
   - Example: "Process all handlers documentation" → Filter rows where `Category ID` = "handlers"
   - Agents filter table rows where `Category ID` column matches desired IDs

4. **Official URL**: Include the Official URL in generated knowledge files for traceability
   - Extract URL from Markdown link format `[🔗](url)` using regex: `\[.*?\]\((https://.*?)\)`
   - Users can navigate from knowledge files back to official documentation

5. **Multiple Mappings**: One source file may appear in multiple table rows when mapped to different categories
   - Process each table row independently
   - Each row produces one target knowledge file

6. **Focus on Conversion**: The skill should focus on content conversion and search hint extraction
   - Asset collection should be automated (not manual)
   - Agents parse directives to find referenced assets

7. **v5 Content Review**: When creating v5 knowledge files from v6 official documentation paths, review content during knowledge file creation to ensure v5-specific terminology and features are accurately reflected
   - v6 official documentation paths are used as the starting point (v5 mapping is created by copying from v6)
   - During content conversion, verify and update references to v5-specific APIs, features, and terminology
   - Example differences: Java EE vs Jakarta EE, javax.* vs jakarta.* packages, Java 8 vs Java 17 features

## Validation

### Validation Script

Create `validate-mapping.sh` to verify:

1. **Category Verification**: Check that all Category IDs in table exist in categories file
2. **Path Verification**: Verify that all Source Path entries exist in both `en/` and `ja/` directories
3. **Title Extraction Verification**:
   - Extract titles from both English and Japanese rst/md file headers
   - Verify both files exist and have valid headers
   - Report files with missing or unparseable headers
4. **URL Verification**: Verify that Official URLs follow conversion rules (optional: check accessibility with HTTP 200 response)
5. **Processing Pattern Verification**: Check that Processing Pattern values are valid (must be one of the processing pattern category IDs or empty)
6. **Target Path Verification**: Verify Target Paths follow naming conventions (subdirectory rules for components, flat structure for others)
7. **Statistics Generation**: Generate category statistics (files per category, mappings per pattern)

### Output

- List of undefined category IDs (if any)
- List of missing source files (if any)
- List of files with missing or unparseable headers (if any)
- List of invalid URLs (if any)
- List of invalid Processing Pattern values (if any)
- List of Target Path naming violations (if any)
- Category and processing pattern statistics table

## Implementation Notes

- Focus on v6 first since nabledge-6 is the primary target
- Use Japanese documentation URLs (Nablarch users are Japanese)
- Markdown table format enables both human review and programmatic processing by AI agents
- When knowledge file creation skill is ready, it will read these mapping tables directly
- Optional Excel export available for stakeholder review if needed
