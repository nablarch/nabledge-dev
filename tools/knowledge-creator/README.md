# Knowledge Creator

Converts Nablarch official documentation (RST/MD/Excel) to AI-ready JSON knowledge files.

## Overview

This tool processes Nablarch documentation through 6 automated steps:

1. **List Source Files** - Scan documentation directories
2. **Classify Files** - Determine Type/Category based on path patterns
3. **Generate Knowledge Files** - Convert to JSON using claude -p
4. **Build Index** - Create index.toon with processing pattern classification
5. **Generate Docs** - Create browsable Markdown documentation
6. **Validate** - Structural and content validation

## Requirements

- Python 3.x
- `claude` CLI tool installed and configured
- Access to Nablarch documentation in `.lw/nab-official/`

## Quick Start

**First time users: Start with test mode**

Test mode processes 31 carefully selected files (instead of all 252) to validate the tool quickly:

```bash
# 1. Run test mode (processes 31 files)
python tools/knowledge-creator/run.py --version 6 --test-mode

# 2. Check the generated files
ls .claude/skills/nabledge-6/knowledge/

# 3. If test passes, run full generation (processes 252 files)
python tools/knowledge-creator/run.py --version 6
```

**Why use test mode first?**
- ✅ **Fast validation**: 8x faster (31 files vs 252 files)
- ✅ **Lower cost**: ~12% of full generation (claude -p API calls)
- ✅ **Full coverage**: Tests all formats (RST/MD/Excel), types, and edge cases
- ✅ **Risk-free**: Safe to try without committing to full generation

See `doc/99-nabledge-creator-tool/TEST-MODE.md` for details.

## Usage

### All Commands

```bash
# Test mode (recommended for first run)
python tools/knowledge-creator/run.py --version 6 --test-mode

# Production mode (process all 252 files)
python tools/knowledge-creator/run.py --version 6

# Process both versions (v5 and v6)
python tools/knowledge-creator/run.py --version all

# Run specific step only
python tools/knowledge-creator/run.py --version 6 --step 3

# Dry run (preview without execution)
python tools/knowledge-creator/run.py --version 6 --dry-run
```

### Command-Line Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--version` | str | Yes | - | Version to process: `6`, `5`, or `all` |
| `--step` | int | No | - | Run specific step (1-6) |
| `--concurrency` | int | No | 4 | Number of parallel claude -p sessions |
| `--repo` | str | No | current dir | Repository root path |
| `--test-mode` | flag | No | false | Process only 31 curated test files (see `doc/99-nabledge-creator-tool/TEST-MODE.md`) |
| `--dry-run` | flag | No | false | Show what would be processed without execution |

## Processing Steps

### Step 1: List Source Files

Scans documentation directories and generates a list of source files:
- RST files from `nablarch-document/ja/`
- MD files from pattern collections
- Excel files (security mapping table)

Output: `logs/v{version}/sources.json`

### Step 2: Classify Files

Classifies source files into Type/Category based on path patterns:
- **processing-pattern**: batch, web-application, REST, etc.
- **component**: handlers, libraries, adapters
- **development-tools**: testing framework, toolbox
- **setup**: configuration, blank project
- **about**: architecture, migration
- **guide**: pattern collections
- **check**: security check

Output: `logs/v{version}/classified.json`

### Step 3: Generate Knowledge Files

Converts source files to JSON knowledge files using claude -p:
- Extracts content from RST/MD/Excel
- Converts to structured JSON with sections
- Generates search hints
- Copies image assets to `assets/` directories

Output: `.claude/skills/nabledge-{version}/knowledge/{type}/{category}/*.json`

**Concurrency**: Uses ThreadPoolExecutor to process multiple files in parallel (default: 4)

**Resumable**: Skips already generated files on restart

### Step 4: Build Index

Creates `index.toon` with:
- File metadata (title, type, category, path)
- Processing pattern classification using claude -p
- TOON format for efficient loading

Output: `.claude/skills/nabledge-{version}/knowledge/index.toon`

### Step 5: Generate Docs

Converts JSON knowledge files to browsable Markdown documentation.

Output: `.claude/skills/nabledge-{version}/docs/{type}/{category}/*.md`

### Step 6: Validate

Validates generated knowledge files:

**Structural Checks (17 rules)**:
- JSON schema compliance
- Field consistency
- Section naming conventions
- URL validity
- Cross-reference integrity
- Assets file existence

**Content Validation (using claude -p)**:
- Information completeness
- No fabricated content
- Proper section splitting
- Quality of search hints

Output:
- `logs/v{version}/validate/structure/{file_id}.json`
- `logs/v{version}/validate/content/{file_id}.json`
- `logs/v{version}/summary.json`

## Incremental Updates

The tool automatically detects changes:

1. **Added files**: New source files are processed
2. **Deleted files**: Removed knowledge files are cleaned up
3. **Updated files**: Knowledge files are regenerated if source is newer

On subsequent runs:
- Step 1-2 always execute (lightweight)
- Step 3 generates only new/updated files
- Step 4-6 rebuild indexes and validate

## Error Handling

### Generation Errors

If Step 3 fails for a file:
1. Error is logged to `logs/v{version}/generate/{file_id}.json`
2. Processing continues for other files
3. Re-run with same command to retry failed files (or delete specific JSON and re-run)

### Validation Failures

If Step 6 finds issues:
1. Review validation logs in `logs/v{version}/validate/`
2. Check `logs/v{version}/summary.json` for overview
3. Fix issues:
   - Delete failed knowledge file
   - Re-run Step 3 for that file: `python run.py --version 6 --step 3`

## Output Structure

```
.claude/skills/nabledge-6/
  knowledge/
    processing-pattern/
      nablarch-batch/
        *.json
      web-application/
        *.json
    component/
      handlers/
        *.json
        assets/
          {file_id}/
            *.png
      libraries/
        *.json
    index.toon
  docs/
    processing-pattern/
      nablarch-batch/
        *.md
    component/
      handlers/
        *.md

tools/knowledge-creator/
  logs/
    v6/
      sources.json
      classified.json
      generate/
        {file_id}.json
      classify-patterns/
        {file_id}.json
      validate/
        structure/
          {file_id}.json
        content/
          {file_id}.json
      summary.json
```

## Troubleshooting

### "knowledge file not found" during validation

The file wasn't generated in Step 3. Check generation logs:
```bash
cat tools/knowledge-creator/logs/v6/generate/{file_id}.json
```

### Timeout errors

Increase timeout in `steps/common.py` or reduce concurrency:
```bash
python run.py --version 6 --concurrency 2
```

### Classification errors

Check `classified.json` for unmatched files. Update mapping in `steps/step2_classify.py` if needed.

### URL validation failures (S11)

Check if official documentation URLs have changed. Update base URLs in prompt templates if needed.

## Performance

Typical execution times (for v6, ~300 files):
- Step 1-2: < 1 minute
- Step 3: 30-60 minutes (depending on concurrency)
- Step 4: 5-10 minutes
- Step 5: < 1 minute
- Step 6: 20-40 minutes

Total: ~1-2 hours for initial run, much faster for incremental updates.
