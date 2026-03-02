# Knowledge Creator

Converts Nablarch official documentation (RST/MD/Excel) to AI-ready JSON knowledge files.

## Processing Flow

| Step | Process | Method | Description |
|------|---------|--------|-------------|
| 1 | List Source Files | Script | Scans official docs (RST), pattern collections (MD), and security mapping (Excel). Auto-excludes index files and English translations |
| 2 | Classify Files | Script | Determines Type/Category from directory path and sets output paths |
| 3 | Generate Knowledge Files | claude -p | Generates JSON knowledge files (1 session per file) following "nothing missed, nothing added" principle. Supports parallel processing |
| 4 | Build Index | Script + claude -p | Aggregates metadata from all knowledge files to create index.toon. Processing pattern classification uses claude -p |
| 5 | Generate Docs | Script | Converts JSON knowledge files to human-readable Markdown |
| 6 | Validate | Script + claude -p | Validates with structural checks (17 rules) + content validation (4 aspects). Binary pass/fail for all items |

### Step 6: Validation Details

Validation runs in two stages: structural checks (script) and content validation (claude -p). If any check fails, the file must be fixed or regenerated.

**Structural Checks (Script, 17 rules)**

| # | Check |
|---|-------|
| S1 | Valid JSON format |
| S2 | Required fields exist (id, title, official_doc_urls, index, sections) |
| S3 | All index[].id exist in sections keys |
| S4 | All sections keys exist in index[].id |
| S5 | index[].id follows kebab-case |
| S6 | index[].hints is non-empty array |
| S7 | sections values are non-empty strings |
| S8 | id field matches filename |
| S9 | Section count matches source heading count |
| S10 | h3 splitting follows 2000-char rule (RST only) |
| S11 | Official URLs are valid (HTTP 200, title match, Japanese page) |
| S12 | Technical terms in sections are included in hints |
| S13 | Section content is at least 50 characters |
| S14 | Cross-references exist in knowledge base |
| S15 | Asset references exist as files |
| S16 | index.toon line count matches knowledge file count |
| S17 | index.toon processing_patterns use only valid values |

**Content Validation (claude -p, 4 aspects)**

Uses separate claude -p session from generation to avoid bias.

| Aspect | Check |
|--------|-------|
| Missing information | Specs, warnings, code examples missing from knowledge file |
| Fabricated information | Information in knowledge file not found in source |
| Section splitting validity | Deviations from heading-level splitting rules |
| Search hint quality | Missing class names or property names |

## Quality Assurance

Three mechanisms ensure quality:

**Rule-based constraints**: Step 3 prompts embed all extraction rules, section splitting rules, and format guidelines, minimizing AI judgment. Output follows JSON Schema, not free-form text.

**Separation of generation and validation**: AI that generates (Step 3) and AI that validates (Step 6) use separate sessions. Same-session validation would introduce bias.

**Script checks + AI checks**: Section counts, URL validity, hints coverage, and reference integrity are checked by script. Semantic judgments like missing/fabricated information are handled by AI. All items must pass.

## Requirements

- Python 3.x, uv, venv (set up by `setup.sh`)
- `claude` CLI tool installed and configured
- Access to Nablarch documentation in `.lw/nab-official/`

## Usage

### Quick Start (Recommended)

**First-time users: Start with test mode**

```bash
# 1. Run test mode (31 files, 8x faster)
python tools/knowledge-creator/run.py --version 6 --test-mode

# 2. Check generated files
ls .claude/skills/nabledge-6/knowledge/

# 3. If successful, run full generation (252 files)
python tools/knowledge-creator/run.py --version 6
```

See `doc/99-nabledge-creator-tool/TEST-MODE.md` for test mode details.

### Basic Usage

```bash
# Generate all knowledge files for version 6
python tools/knowledge-creator/run.py --version 6

# Generate for version 5
python tools/knowledge-creator/run.py --version 5

# Generate for both v6 and v5
python tools/knowledge-creator/run.py --version all
```

### Options

```bash
# Change concurrency (default: 4)
python tools/knowledge-creator/run.py --version 6 --concurrency 8

# Run specific step only
python tools/knowledge-creator/run.py --version 6 --step 3

# Preview what would be processed (no file output)
python tools/knowledge-creator/run.py --version 6 --dry-run

# Specify repository root explicitly
python tools/knowledge-creator/run.py --version 6 --repo /path/to/repo
```

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--version` | Yes | - | Target version: `6`, `5`, or `all` |
| `--step` | No | All steps | Run specific step only (1-6) |
| `--concurrency` | No | 4 | Number of parallel claude -p sessions |
| `--repo` | No | Current dir | Repository root path |
| `--test-mode` | No | false | Process 31 test files only |
| `--dry-run` | No | false | Preview only, no file output |

### Resume After Interruption

If processing is interrupted, re-run the same command to resume. Step 3 skips already-generated files, so completed work is not re-processed.

### Incremental Updates (2nd run onwards)

The tool auto-detects source file changes:

- **Added**: Generates knowledge files for new source files
- **Updated**: Regenerates knowledge files if source is newer
- **Deleted**: Removes knowledge files, docs, and assets for deleted sources

### Handling Validation Failures

If Step 6 reports failures:

```bash
# Example: some-handler.json failed validation
rm .claude/skills/nabledge-6/knowledge/component/handlers/some-handler.json

# Re-run Step 3 only (regenerates deleted file only)
python tools/knowledge-creator/run.py --version 6 --step 3
```

### Checking Logs

Logs are organized by version with per-file detail:

```
tools/knowledge-creator/logs/v{version}/
  sources.json                      # Source file list
  classified.json                   # Classification results
  generate/                         # Step 3: Generation logs (per file)
    {file_id}.json                  # Success/error details
  classify-patterns/                # Step 4: Pattern classification logs
    {file_id}.json
  validate/                         # Step 6: Validation logs (per file)
    structure/{file_id}.json        # Structural check results
    content/{file_id}.json          # Content validation results
  summary.json                      # Overall summary
```

Check specific file: `cat logs/v6/generate/{file_id}.json`
Check overall status: `cat logs/v6/summary.json`

## Output Structure

| Output | Path |
|--------|------|
| Knowledge files (JSON) | `.claude/skills/nabledge-{6,5}/knowledge/{type}/{category}/` |
| Assets (images, etc.) | `.claude/skills/nabledge-{6,5}/knowledge/{type}/{category}/assets/{id}/` |
| Index | `.claude/skills/nabledge-{6,5}/knowledge/index.toon` |
| Browsable docs (Markdown) | `.claude/skills/nabledge-{6,5}/docs/{type}/{category}/` |
