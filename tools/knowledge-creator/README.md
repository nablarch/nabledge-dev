# Knowledge Creator

Converts Nablarch official documentation (RST/MD/Excel) to AI-ready knowledge files (JSON).

## Overview

Multi-phase pipeline for knowledge file generation:

- **Phase A**: Preparation - List source files, classify by type/category
- **Phase B**: Generation - Generate knowledge JSON via `claude -p` (parallel execution)
- **Phase C**: Structure Check - Validate with S1-S15 checks (Python, no AI)
- **Phase D**: Content Check - Validate content via `claude -p` (parallel execution)
- **Phase E**: Fix - Fix issues via `claude -p` (parallel execution)
- **Phase G**: Link Resolution - Convert RST cross-references to Markdown links
- **Phase F**: Finalization - Classify patterns, generate index.toon, create browsable docs

Phase C→D→E can loop up to `--max-rounds` times.

## Requirements

- Python 3.8+
- Claude CLI (`claude` command available)
- Dependencies: `openpyxl`, `pytest`

## Setup

```bash
cd tools/knowledge-creator

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

Or run `setup.sh` from repository root (includes knowledge-creator dependencies):

```bash
cd /path/to/nabledge-dev
./setup.sh
```

## Usage

### Test Mode (3 files)

Validate with 3 largest files (8 files after splitting):

```bash
cd tools/knowledge-creator
python run.py --version 6 --test-mode --repo /path/to/nabledge-dev
```

**Important**: Specify absolute path to repository root with `--repo`.

### Test Mode (Comprehensive - 21 files)

Cover all formats, types, and categories:

```bash
# Switch test-files.json
cp test-files-comprehensive.json test-files.json

# Run
python run.py --version 6 --test-mode --repo /path/to/nabledge-dev
```

### Production Mode (All files)

Generate all v6 source files (252 sources → 262 files after splitting):

```bash
python run.py --version 6 --repo /path/to/nabledge-dev
```

Generate both v5 and v6:

```bash
python run.py --version all --repo /path/to/nabledge-dev
```

### Run Specific Phases

```bash
# Phase B (generation) only
python run.py --version 6 --phase B --repo /path/to/nabledge-dev

# Phase C,D,E (validation & fix) only
python run.py --version 6 --phase CDE --repo /path/to/nabledge-dev

# Phase G,F (link resolution & finalization) only
python run.py --version 6 --phase GF --repo /path/to/nabledge-dev
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Version (6, 5, all) | **Required** |
| `--phase` | Phases to run (combination of A, B, C, D, E, G, F) | `ABCDEFG` |
| `--test-mode` | Test mode (only files in test-files.json) | `False` |
| `--concurrency` | Parallel execution count (Phase B, D, E) | `4` |
| `--max-rounds` | Max Phase C→D→E loop iterations | `1` |
| `--dry-run` | Dry run (no file writes) | `False` |
| `--repo` | Repository root path | `os.getcwd()` |

## Output Files

### Final Outputs

```
.claude/skills/nabledge-6/
  knowledge/              # Knowledge JSON files
    {type}/{category}/{file-id}.json
    index.toon            # Knowledge file index
  docs/                   # Browsable Markdown files
    {type}/{category}/{file-id}.md
```

### Intermediate Artifacts

```
tools/knowledge-creator/logs/v6/
  sources.json                    # Phase A: Source file list
  classified.json                 # Phase A: Classified file list
  structure-check.json            # Phase C: Structure validation results
  generate/trace/{file-id}.txt    # Phase B: Generation trace
  validate/findings/{file-id}.json # Phase D: Content validation results
  knowledge-resolved/{type}/{category}/{file-id}.json # Phase G: Link-resolved files
```

## Cleanup

Remove all generated files to start fresh:

```bash
cd tools/knowledge-creator
./clean.sh /path/to/nabledge-dev
```

## Test File Configuration

`test-files.json` controls which files are processed in `--test-mode`:

- **test-files-top3.json**: 3 largest files (for SC validation)
- **test-files-comprehensive.json**: 21 files (comprehensive test coverage)

Switch between configurations:

```bash
cp test-files-top3.json test-files.json          # 3-file version
cp test-files-comprehensive.json test-files.json  # 21-file version
```

## Troubleshooting

### `FileNotFoundError: .lw/nab-official/v6/`

→ Specify absolute path to repository root with `--repo` option.

### Nested directory `tools/knowledge-creator/tools/...` created

→ When running from `tools/knowledge-creator/` directory, always specify `--repo`.

### `claude: command not found`

→ Install Claude CLI. Use `--dry-run` option to test without AI calls.

### Tests fail

```bash
# Run unit tests
cd tools/knowledge-creator
python -m pytest tests/ -v
```

## Related Documentation

- **Task Specification**: `doc/nabledge-creator-v2-task.md`
- **Mapping Files**: `doc/mapping/` (302 files)
- **Issue**: #106
- **PR**: #107
