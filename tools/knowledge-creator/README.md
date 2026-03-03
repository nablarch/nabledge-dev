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

Run `setup.sh` from repository root. This installs all system tools, Python dependencies (including knowledge-creator), and clones Nablarch official repositories:

```bash
cd /path/to/nabledge-dev
./setup.sh
```

After setup completes, restart your shell or run:

```bash
source ~/.bashrc
```

## Usage

**Important**: Run commands from repository root directory.

### Test Mode (3 files)

Validate with 3 largest files (8 files after splitting):

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-top3.json
```

### Test Mode (Comprehensive - 21 files)

Cover all formats, types, and categories:

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-comprehensive.json
```

### Production Mode (All files)

Generate all v6 source files (252 sources → 262 files after splitting):

```bash
python tools/knowledge-creator/run.py --version 6
```

Generate both v5 and v6:

```bash
python tools/knowledge-creator/run.py --version all
```

### Run Specific Phases

```bash
# Phase B (generation) only
python tools/knowledge-creator/run.py --version 6 --phase B

# Phase C,D,E (validation & fix) only
python tools/knowledge-creator/run.py --version 6 --phase CDE

# Phase G,F (link resolution & finalization) only
python tools/knowledge-creator/run.py --version 6 --phase GF
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Version (6, 5, all) | **Required** |
| `--phase` | Phases to run (combination of A, B, C, D, E, G, F) | `ABCDEFG` |
| `--test` | Test mode: specify test file (e.g., `test-files-top3.json`) | `None` |
| `--concurrency` | Parallel execution count (Phase B, D, E) | `4` |
| `--max-rounds` | Max Phase C→D→E loop iterations | `1` |
| `--dry-run` | Dry run (no file writes) | `False` |
| `--repo` | Repository root path (advanced) | `os.getcwd()` |

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
tools/knowledge-creator/clean.sh
```

## Test File Configuration

Test files define which source files to process in test mode:

- **test-files-top3.json**: 3 largest files (for SC validation)
- **test-files-comprehensive.json**: 21 files (comprehensive test coverage)

Specify test file with `--test` option (no need to copy files):

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-top3.json
python tools/knowledge-creator/run.py --version 6 --test test-files-comprehensive.json
```

## Troubleshooting

### `FileNotFoundError: .lw/nab-official/v6/`

→ Run commands from repository root directory (not `tools/knowledge-creator/`).

### `claude: command not found`

→ Install Claude CLI. Use `--dry-run` option to test without AI calls.

### Tests fail

```bash
# Run unit tests from repository root
python -m pytest tools/knowledge-creator/tests/ -v

# Or from tools/knowledge-creator directory
cd tools/knowledge-creator
python -m pytest tests/ -v
```

## Related Documentation

- **Task Specification**: `doc/nabledge-creator-v2-task.md`
- **Mapping Files**: `doc/mapping/` (302 files)
- **Issue**: #106
- **PR**: #107
