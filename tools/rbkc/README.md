# Rule-based Knowledge Creator (RBKC)

Deterministic, rule-based converter that transforms Nablarch official documentation (RST / Markdown / Excel) into structured knowledge files. No AI is involved — every transformation is mechanical and reproducible.

## Motivation

The former Knowledge Creator used AI to generate knowledge files. While effective, it has fundamental problems for a mission-critical framework:

1. **AI hallucinations** — generated content could diverge from the source, and verifying every file by hand does not scale (5 Nablarch versions × 400+ files).
2. **Non-determinism** — the same source could produce different output across runs, making regressions hard to locate.

RBKC replaces the generation step with a pure rule-based pipeline. Same input always produces same output. Quality is enforced by an independent `verify` stage that reads only the source and the output — it does not depend on RBKC's internals.

## Scope

RBKC produces **content only** — titles and body text derived from source. Hints (keyword index) are explicitly out of scope and are handled in a separate pipeline.

## Usage

### Setup

```bash
# From repository root — clones .lw/ (official docs) and installs Python dependencies
./setup.sh
```

### Commands

```bash
# Create — convert all sources, write JSON + docs MD + index
bash tools/rbkc/rbkc.sh create 6

# Verify — check output against source for completeness and correctness
bash tools/rbkc/rbkc.sh verify 6
```

Supported versions: `6`, `5`, `1.4`, `1.3`, `1.2`.

| Command | Behavior |
|---------|----------|
| `create` | Convert every source file, generate JSON + browsable MD + `index.toon` |
| `verify` | Independent quality gate — FAIL if any output diverges from source |

### Optional arguments

| Argument | Purpose |
|----------|---------|
| `--repo-root` | Repository root (default: auto-detected from script location) |
| `--output-dir` | Output root (default: `.claude/skills/nabledge-{v}/`) |

### Output

| Output | Path | Purpose |
|--------|------|---------|
| Knowledge JSON | `.claude/skills/nabledge-{v}/knowledge/{type}/{category}/{id}.json` | Consumed by the nabledge skill's keyword search |
| Browsable MD | `.claude/skills/nabledge-{v}/docs/{type}/{category}/{id}.md` | Human-readable preview |
| Index | `.claude/skills/nabledge-{v}/knowledge/index.toon` | File list for skill retrieval |
| Assets | `.claude/skills/nabledge-{v}/docs/{type}/{category}/assets/{id}/` | Images / downloads referenced by RST |

## Output Schema

```json
{
  "id": "handlers-data_read_handler",
  "title": "データリードハンドラ",
  "content": "Top-level preamble body (before the first h2).",
  "no_knowledge_content": false,
  "sections": [
    {
      "id": "s1",
      "title": "機能概要",
      "content": "Markdown content..."
    }
  ]
}
```

- `sections` is an ordered list (not a dict).
- `no_knowledge_content: true` marks files that are pure navigation (toctree-only, labels only, etc.). Such files are excluded from `index.toon`.
- `hints` is **not** a field — RBKC does not emit hints.

## Design Documents

Detailed rules and rationale live under `tools/rbkc/docs/`:

| Document | Purpose |
|----------|---------|
| `rbkc-converter-design.md` | Per-format conversion rules (RST / MD / Excel) |
| `rbkc-json-schema-design.md` | Output JSON schema and section granularity rules |
| `rbkc-verify-quality-design.md` | verify quality gate specification |
| `rbkc-hints-file-design.md` | Hints handoff (hints generation is a separate pipeline) |
| `evaluation/` | Empirical studies that shaped the design |

## Verify — the Quality Gate

`verify` is the only definition of "correct RBKC output". It checks whether the generated JSON and docs MD cover the source without loss, using only the source file and the output — it does not import anything from the RBKC converters.

Rules:

- verify must never depend on RBKC implementation modules.
- When verify reports a FAIL, the fix belongs in RBKC, not in verify.
- verify changes require explicit user approval; acceptable reasons are spec bugs, missing checks, or false positives — never "relax the check so the current output passes".

See `.claude/rules/rbkc.md` for the full policy, including the requirement to run `create && verify` for **all 5 versions** on every change.

## Testing

Test policy (full detail in `.claude/rules/rbkc.md`):

| Layer | Test coverage |
|-------|---------------|
| verify (`scripts/verify/`) | All logic has unit tests; every new check is TDD |
| create side (converters, resolver, etc.) | No dedicated tests — verify passing is sufficient |
| CLI (`rbkc.sh`, `run.py` dispatch) | Unit tests for argument parsing and routing |

```bash
# Run all tests
cd tools/rbkc
pytest

# E2E only (runs against real .lw sources)
pytest tests/e2e/

# Unit only
pytest tests/ut/
```

E2E tests require `.lw/nab-official/v{v}/` to be present (run `./setup.sh` first). Missing `.lw` causes an explicit failure, not a skip.

## Directory Structure

```
tools/rbkc/
├── README.md                # This file
├── rbkc.sh                  # CLI entry point
├── scripts/
│   ├── run.py               # CLI dispatcher (create / verify)
│   ├── common/              # Shared utilities
│   │   ├── file_id.py               # id generation
│   │   ├── github_slug.py           # GitHub anchor slugifier
│   │   ├── labels.py                # RST label → path map
│   │   ├── linkfmt.py               # Markdown link formatter
│   │   ├── md_ast.py / md_ast_visitor.py / md_normaliser.py
│   │   ├── rst_ast.py / rst_ast_visitor.py / rst_normaliser.py / rst_admonition.py
│   ├── create/              # Create-side pipeline
│   │   ├── scan.py                  # Source discovery
│   │   ├── classify.py              # Type / category classification
│   │   ├── resolver.py              # Cross-reference + asset resolution
│   │   ├── docs.py                  # Browsable MD generation
│   │   ├── index.py                 # index.toon generation
│   │   └── converters/
│   │       ├── rst.py               # RST → JSON / MD
│   │       ├── md.py                # Markdown → JSON / MD
│   │       ├── xlsx_common.py       # Shared Excel helpers
│   │       ├── xlsx_releasenote.py  # Release notes parser
│   │       └── xlsx_security.py     # Security table parser
│   └── verify/
│       └── verify.py                # Independent quality gate
├── mappings/
│   ├── v6.json              # Type / category classification rules
│   ├── v5.json
│   ├── v1.4.json
│   ├── v1.3.json
│   └── v1.2.json
├── docs/                    # Design documents
└── tests/
    ├── e2e/test_cli.py      # CLI E2E (create / verify)
    └── ut/                  # Unit tests (verify + CLI + normalisers)
```

## Dependencies

- Python 3.10+
- `openpyxl` — Excel reading (installed by `setup.sh`)

No AI / API dependencies. No network calls at runtime.
