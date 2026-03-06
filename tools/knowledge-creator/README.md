# Knowledge Creator

Converts Nablarch official documentation (RST/MD/Excel) to AI-ready knowledge files (JSON).

## Overview

Multi-phase pipeline for knowledge file generation with automated validation and fix cycles:

```mermaid
flowchart TD
    Start([Start]) --> A[Phase A: Preparation]
    A --> |List & Classify Sources<br/>Split large files| B[Phase B: Generation]
    B --> |Generate Knowledge JSON| C[Phase C: Structure Check]
    C --> |S1-S15 Validation| PassC{Structure<br/>Errors?}
    PassC --> |Yes| StructWarn[⚠️ Skip files with errors<br/>Continue with valid files]
    PassC --> |No| D[Phase D: Content Check]
    StructWarn --> D
    D --> |AI Validation<br/>Valid files only| PassD{Content<br/>Issues?}
    PassD --> |No| CheckStruct{Structure<br/>Errors<br/>Remain?}
    CheckStruct --> |Yes| RerunB([🔄 Re-run Phase B])
    CheckStruct --> |No| M[Phase M: Finalization]
    PassD --> |Yes| Round{Rounds<br/>Left?}
    Round --> |Yes| E[Phase E: Fix]
    Round --> |No| RerunCDE([🔄 Re-run Phase CDE<br/>with more rounds])
    E --> |AI Fix<br/>Content issues only| C
    M --> |1. Merge Split Files<br/>2. Resolve RST Links<br/>3. Generate Docs| Complete([✨ Complete])

    style Start fill:#e1f5e1
    style Complete fill:#e1f5e1
    style RerunB fill:#fff3cd
    style RerunCDE fill:#fff3cd
    style StructWarn fill:#fff3cd
    style M fill:#e1e5ff
```

### Phase Details

| Phase | Description | Type | Parallelized |
|-------|-------------|------|--------------|
| **A** | Preparation | List source files, classify by type/category, split large files | Python | No |
| **B** | Generation | Generate knowledge JSON from sources using Claude API | AI | Yes |
| **C** | Structure Check | Validate JSON structure with S1-S15 checks | Python | No |
| **D** | Content Check | Validate content accuracy against sources using Claude API | AI | Yes |
| **E** | Fix | Automatically fix issues found in Phase D using Claude API | AI | Yes |
| **M** | Finalization | Merge split files → Resolve RST links → Generate index & browsable docs | Hybrid | No |

**Loop Behavior**: Phase C→D→E can repeat up to `--max-rounds` times (default: 1, max: 10) until all files pass Phase D or maximum rounds reached.

**Split File Handling**: RST files with multiple h2 sections (≥2) are automatically split into per-section parts during Phase A, processed independently through Phases B-E, then merged in Phase M to prevent context overflow.

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

### Quick Start with kc.sh

The `kc.sh` wrapper script provides a simple interface for common workflows:

```bash
cd tools/knowledge-creator

# UC1: Initial full generation (clean + generate all phases)
./kc.sh gen 6

# UC2: Resume interrupted generation (no clean)
./kc.sh gen 6 --resume

# UC3: Regenerate files with changed sources (auto-detect)
./kc.sh regen 6

# UC4: Regenerate specific file
./kc.sh regen 6 --target handlers-request-handler

# UC5: Quality improvement (re-validate all files)
./kc.sh fix 6

# UC6: Fix specific file
./kc.sh fix 6 --target handlers-request-handler
```

**Available Options**:
- `--resume`: Skip cleanup (for gen command only)
- `--target FILE_ID`: Process specific file (repeatable for multiple files)
- `--yes`: Skip confirmation prompts
- `--dry-run`: Dry run without file writes
- `--max-rounds N`: Max Phase C→D→E iterations (default: 1)
- `--concurrency N`: Parallel execution count (default: 4)
- `--test FILE`: Use test configuration file

### Test Mode - Smallest (3 files)

Validate with 3 smallest files (minimal processing time):

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-smallest3.json
```

### Test Mode - Largest (3 files)

Validate with 3 largest files (split into sections for processing):

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-largest3.json
```

### Test Mode (Comprehensive - 17 files)

Aligned with main branch knowledge files:

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-comprehensive.json
```

### Production Mode (All files)

Generate all v6 source files (252 sources, some split into multiple sections):

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

# Phase C,D,E (validation & fix loop) only
python tools/knowledge-creator/run.py --version 6 --phase CDE

# Phase M (finalization) only
python tools/knowledge-creator/run.py --version 6 --phase M

# Backward compatibility: Phase G,F (old finalization)
python tools/knowledge-creator/run.py --version 6 --phase GF
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Version (6, 5, all) | **Required** |
| `--phase` | Phases to run (combination of A, B, C, D, E, M) | `ABCDEM` |
| `--test` | Test mode: specify test file (e.g., `test-files-largest3.json`) | `None` |
| `--concurrency` | Parallel execution count (Phase B, D, E) | `4` |
| `--max-rounds` | Max Phase C→D→E loop iterations (1-10) | `1` |
| `--clean-phase` | Clean artifacts for specified phases before run (e.g., 'D', 'BD') | `None` |
| `--target` | Target file ID(s) to process (repeatable) | `None` |
| `--yes` | Skip confirmation prompts | `False` |
| `--regen` | Detect source changes and regenerate affected files | `False` |
| `--dry-run` | Dry run (no file writes) | `False` |
| `--repo` | Repository root path (advanced) | `os.getcwd()` |

**Note**: Phases G and F are still available individually for backward compatibility, but Phase M (which combines merge, link resolution, and finalization) is now the default in the standard flow.

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

All intermediate files are stored in `.logs/v6/` (or `.logs/v5/`):

```
tools/knowledge-creator/.logs/v6/
  sources.json                           # Phase A: Source file list
  classified.json                        # Phase A: Classified file list with split info
  source_hashes.json                     # Source file SHA256 hashes (for --regen)
  structure-check.json                   # Phase C: Structure validation results
  execution.log                          # Execution log with timestamps

  phase-b/
    traces/{file-id}.json                # Phase B: Generation traces
    executions/{file-id}_{timestamp}.json # Phase B: Execution metrics

  phase-c/
    results.json                         # Phase C: Validation results per file

  phase-d/
    findings/{file-id}.json              # Phase D: Content validation findings
    executions/{file-id}_{timestamp}.json # Phase D: Execution metrics

  phase-e/
    executions/{file-id}_{timestamp}.json # Phase E: Fix execution metrics

  phase-g/
    resolved/{type}/{category}/{file-id}.json # Phase G: Link-resolved files

  summary.json                           # Overall summary with metrics
```

**Execution Metrics**: Each `executions/` directory contains detailed metrics for AI calls including:
- `num_turns`: Number of agentic turns
- `duration_ms`: Execution time
- `total_cost_usd`: API cost
- `structured_output`: Generated content

## Split File Processing

RST source files with multiple h2 sections are automatically split to prevent context overflow during AI processing:

**Split Criteria (Section-Unit Split)**:
- RST files only (MD and Excel files are not split)
- File has 2 or more h2 sections (`========` underline)
- Each h2 section becomes one independent file

**Split Processing Flow**:
1. Phase A identifies and splits files into per-section parts (e.g., `libraries-tag-1`, `libraries-tag-2`)
2. Phases B-E process each part independently
3. Phase M merges parts back into single files
4. Output contains merged files only (part files are deleted)

**Benefits**:
- Prevents context overflow (each section processed independently)
- Maintains all sections (no data loss)
- Transparent to end users (final output has no split files)
- Simpler logic (one section = one file, no complex threshold tuning)

## Cleanup

Remove generated files for specific version(s):

```bash
# Clean version 6 (with confirmation prompt)
python tools/knowledge-creator/clean.py --version 6

# Clean version 6 (skip confirmation)
python tools/knowledge-creator/clean.py --version 6 --yes

# Clean version 5 only
python tools/knowledge-creator/clean.py --version 5

# Clean both versions
python tools/knowledge-creator/clean.py --version all
```

## Test File Configuration

Test files define which source files to process in test mode:

| File | Files | Description |
|------|-------|-------------|
| **test-files-smallest3.json** | 3 | 3 smallest files — fastest, minimal processing time |
| **test-files-largest3.json** | 3 | 3 largest files (split into 22 sections) — tests split file handling |
| **test-files-comprehensive.json** | 17 | Aligned with main branch knowledge files — broad category coverage |

Specify test file with `--test` option:

```bash
python tools/knowledge-creator/run.py --version 6 --test test-files-smallest3.json
python tools/knowledge-creator/run.py --version 6 --test test-files-largest3.json
python tools/knowledge-creator/run.py --version 6 --test test-files-comprehensive.json
```

## Development

### Running Tests

```bash
# Run all tests from repository root
python -m pytest tools/knowledge-creator/tests/ -v

# Or from tools/knowledge-creator directory
cd tools/knowledge-creator
pytest tests/ -v

# Run specific test file
pytest tests/test_phase_c.py -v

# Run with coverage
pytest tests/ --cov=steps --cov-report=html
```

### Test Categories

- **Unit Tests**: Phase C structure validation, split criteria logic
- **Integration Tests**: Phase C/D/E/M integration, merge logic, pipeline flow
- **E2E Tests**: Full pipeline scenarios with split files, fix cycles

## Troubleshooting

### `kc.sh: permission denied`

→ Make script executable: `chmod +x tools/knowledge-creator/kc.sh`

### `FileNotFoundError: .lw/nab-official/v6/`

→ Run commands from repository root directory (not `tools/knowledge-creator/`).

### `claude: command not found`

→ Install Claude CLI. Use `--dry-run` option to test without AI calls.

### Phase E output too small warning

→ This is a safety guard. If Phase E output shrinks to <50% of input, the fix is rejected to prevent data loss. Check `.logs/v6/phase-e/executions/` for metrics and adjust `--max-rounds` if needed.

### Max rounds reached without all files passing

→ Check `.logs/v6/phase-d/findings/` for persistent issues. Some issues may require manual source document fixes or prompt adjustments.

### Tests fail

```bash
# Run unit tests from repository root
python -m pytest tools/knowledge-creator/tests/ -v

# Or from tools/knowledge-creator directory
cd tools/knowledge-creator
python -m pytest tests/ -v
```

## Architecture

### Design Principles

1. **Separation of Concerns**: Each phase has single responsibility
2. **Split-Aware Processing**: Large files split early, merged late to prevent context overflow
3. **Defensive Programming**: Output size guards, incomplete part detection
4. **Observability**: Detailed metrics and traces for all AI operations
5. **Idempotency**: Safe to re-run phases without side effects

### Key Components

- `kc.sh`: User-friendly wrapper script for common workflows
- `run.py`: Main entry point with phase orchestration
- `clean.py`: Cleanup utility for generated artifacts
- `steps/common.py`: Shared utilities (JSON I/O, Claude API wrapper)
- `steps/cleaner.py`: Phase-specific artifact cleanup
- `steps/source_tracker.py`: Source change detection (SHA256-based)
- `steps/step1_list_sources.py`: Source file discovery
- `steps/step2_classify.py`: File classification and splitting logic
- `steps/phase_b_generate.py`: Knowledge generation via Claude API
- `steps/phase_c_structure_check.py`: Structure validation (S1-S15)
- `steps/phase_d_content_check.py`: Content validation via Claude API
- `steps/phase_e_fix.py`: Automated fix via Claude API
- `steps/phase_m_finalize.py`: Merge → Resolve → Generate (orchestrator)
- `steps/merge.py`: Split file merging logic
- `steps/phase_g_resolve_links.py`: RST→Markdown link conversion
- `steps/phase_f_finalize.py`: Pattern classification, index, docs generation

## Related Documentation

- **Task Specification**: `doc/nabledge-creator-v2-task.md`
- **Split-Aware Pipeline**: `.pr/00107/split-aware-pipeline-tasks.md`
- **Mapping Files**: `doc/mapping/` (302 files)
- **Issue**: #106
- **PR**: #107

## Version History

- **v2.1** (PR #107): Added kc.sh wrapper, source change tracking, target filtering
- **v2.0** (PR #107): Split-aware pipeline with Phase M, context overflow prevention
- **v1.0** (PR #106): Initial implementation with Phases A-G
