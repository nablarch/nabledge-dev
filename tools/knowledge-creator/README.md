# knowledge-creator

Tool to convert Nablarch official documentation to AI-ready knowledge files (JSON format).

## Overview

This tool processes Nablarch documentation through a 6-step pipeline:

1. **List sources** - Scan RST/MD/Excel files from official documentation
2. **Classify** - Categorize files by Type/Category using mapping rules
3. **Generate** - Convert source files to knowledge JSON using claude -p
4. **Build index** - Create index.toon with processing patterns
5. **Generate docs** - Create browsable markdown documentation
6. **Validate** - Verify structure and content quality

## Usage

### Basic Usage

```bash
# Process all steps for nabledge-6
python tools/knowledge-creator/run.py --version 6

# Process specific step
python tools/knowledge-creator/run.py --version 6 --step 1

# Process both versions
python tools/knowledge-creator/run.py --version all

# Dry-run mode (show what would be processed)
python tools/knowledge-creator/run.py --version 6 --dry-run
```

### Options

| Option | Values | Description |
|--------|--------|-------------|
| `--version` | `6`, `5`, `all` | Nablarch version to process (required) |
| `--step` | `1-6` | Execute specific step only (optional) |
| `--concurrency` | integer | Number of concurrent workers (default: 4) |
| `--repo` | path | Repository root path (default: current directory) |
| `--dry-run` | flag | Show what would be processed without writing files |

## Directory Structure

```
tools/knowledge-creator/
  README.md                 # This file
  run.py                    # Main entry point
  steps/
    __init__.py
    utils.py                # Shared utility functions
    step1_list_sources.py   # Step 1: List source files
    step2_classify.py       # Step 2: Classify by Type/Category
    step3_generate.py       # Step 3: Generate knowledge files
    step4_build_index.py    # Step 4: Build index.toon
    step5_generate_docs.py  # Step 5: Generate browsable docs
    step6_validate.py       # Step 6: Validate knowledge files
  prompts/
    generate.md             # Prompt template for Step 3
    classify_patterns.md    # Prompt template for Step 4
    validate.md             # Prompt template for Step 6
  logs/
    v6/
      sources.json          # Step 1 output
      classified.json       # Step 2 output
      generate/             # Step 3 logs (per file)
      classify-patterns/    # Step 4 logs (per file)
      validate/             # Step 6 logs (per file)
        structure/
        content/
      summary.json          # Overall summary
```

## Implementation Status

### Phase 1: Project Structure and Core Functions ✅

- [x] Directory structure created
- [x] run.py main entry point with argument parsing
- [x] Context object for sharing state across steps
- [x] Utility functions (JSON I/O, file I/O, claude -p wrapper, logging)
- [x] Step 1: List sources (RST, MD, Excel scanning)
- [x] Step 2: Classify (Type/Category mapping with 252/252 files matched)

**Status**: Complete. Steps 1-2 tested and working correctly with 252 source files for v6.

### Phase 2: AI Generation Features (TODO)

- [ ] Create prompt template: `prompts/generate.md`
- [ ] Complete Step 3 implementation:
  - [ ] Assets extraction and copying
  - [ ] Prompt building with placeholders
  - [ ] Concurrent execution with ThreadPoolExecutor
  - [ ] Error handling and logging
  - [ ] Resume capability (skip existing files)
- [ ] Create prompt template: `prompts/classify_patterns.md`
- [ ] Complete Step 4 implementation:
  - [ ] Load classified files and knowledge JSONs
  - [ ] Classify processing patterns with claude -p (concurrent)
  - [ ] Generate index.toon in TOON format
  - [ ] Comma escaping for titles

**Current Status**: Step 3 and 4 have skeletal implementation. Need to:
1. Create prompt templates based on design document
2. Complete assets extraction logic
3. Implement pattern classification with claude -p
4. Implement TOON format writer

### Phase 3: Document Generation and Validation (TODO)

- [ ] Implement Step 5:
  - [ ] Convert knowledge JSON to browsable markdown
  - [ ] Create directory structure for docs
- [ ] Create prompt template: `prompts/validate.md`
- [ ] Implement Step 6:
  - [ ] 17 structure checks (S1-S17)
  - [ ] 4 content validation aspects with claude -p
  - [ ] Summary report generation

**Current Status**: Steps 5 and 6 have placeholder implementation only.

### Phase 4: Testing and Documentation (TODO)

- [ ] Batch test with 15-25 files
- [ ] Verify error handling and resume
- [ ] Verify parallel processing
- [ ] Verify differential updates
- [ ] Update this README with:
  - [ ] Troubleshooting section
  - [ ] Known issues and limitations
  - [ ] Performance characteristics
  - [ ] Examples of output

### Phase 5: Success Criteria Verification (TODO)

- [ ] SC1: Existing knowledge files deleted
- [ ] SC2: nabledge-creator tool functional
- [ ] SC3: Implementation follows design doc
- [ ] SC4: Supports nabledge-6 and nabledge-5
- [ ] SC5: Clear error messages and validation
- [ ] SC6: Documentation complete
- [ ] SC7: Regenerate all knowledge files

## Processing Pipeline Details

### Step 1: List Sources

Scans official documentation directories for source files:
- RST files from `nablarch-document/ja/` (version-specific)
- MD files from pattern collection (v6 only, used for both versions)
- Excel security check table (v6 only, used for both versions)

Excludes: `index.rst`, `_*` directories, `en/` directories, `README.md`

Output: `logs/v{version}/sources.json`

### Step 2: Classify

Maps source files to Type/Category using path-based rules:
- RST: Path matching against mapping table (processing-pattern, component, development-tools, setup, about, guide)
- MD: Filename matching for pattern collection
- Excel: Fixed mapping for security check table

Output: `logs/v{version}/classified.json`

### Step 3: Generate (TODO)

Converts source files to knowledge JSON using claude -p:
- Extracts assets (images, attachments) to knowledge/assets/
- Builds prompt from template with source content
- Executes claude -p via stdin (300s timeout)
- Parses JSON from output
- Saves to `knowledge/{type}/{category}/{id}.json`
- Logs to `logs/v{version}/generate/{id}.json`

Concurrent processing with configurable workers (default: 4).

### Step 4: Build Index (TODO)

Creates `knowledge/index.toon`:
- Loads all knowledge files
- Classifies processing patterns with claude -p (concurrent)
- Generates TOON format with title, type, category, processing_patterns, path

### Step 5: Generate Docs (TODO)

Creates browsable markdown from knowledge JSON:
- Converts to `docs/{type}/{category}/{id}.md`
- Simple format: title + sections with headings

### Step 6: Validate (TODO)

Two-phase validation:
1. Structure checks (17 items, script-based)
2. Content validation (4 aspects, claude -p-based in separate sessions)

Output: `logs/v{version}/validate/` and `logs/v{version}/summary.json`

## Troubleshooting

(TODO: Add troubleshooting guide after testing)

## Development Notes

- Python 3 with standard library (no external dependencies except claude CLI)
- Concurrent processing using `concurrent.futures.ThreadPoolExecutor`
- Model: Sonnet 4.5 (`claude-sonnet-4-5-20250929`) for all steps
- Prompts sent via stdin to avoid command-line length limits
- Resume capability: Steps skip existing output files
- Error logging: Per-file logs for debugging failed conversions

## Design Document

Full design specification: `doc/99-nabledge-creator-tool/knowledge-creator-design.md`
