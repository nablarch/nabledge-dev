# nabledge-dev

## Language Rules

**All content in this repository must be in English**, including:
- Code comments
- Documentation (README, design docs, work logs)
- Commit messages
- Test scenarios and results
- Skill definitions and workflows

**Exception**: nabledge-x skills' user-facing messages should be in Japanese, as they are designed for Nablarch users in Japan.

---

## Overview

This repository contains **nabledge skills** for AI agents to assist with Nablarch development.

- **nabledge-6**: Skill for Nablarch 6 (Jakarta EE 10, Java 17+)
- **nabledge-5**: Skill for Nablarch 5 (Java EE 7/8, Java 8+)

These skills enable AI (Claude Code / GitHub Copilot) to autonomously perform Nablarch development tasks.

---

## Directory Structure

```
nabledge-dev/
├── .claude/
│   ├── rules/                     # Project rules and guidelines
│   └── skills/
│       ├── nabledge-6/            # Nablarch 6 skill (in development)
│       └── nabledge-5/            # Nablarch 5 skill (planned)
│
├── .lw/
│   ├── research/                  # Research & design documents
│   └── nab-official/              # Nablarch official documentation (cloned)
│       ├── v6/                    # Version 6 documentation (main branch)
│       └── v5/                    # Version 5 documentation (v5-main branch)
│
├── .pr/                           # PR-based work notes and artifacts
│   └── xxxxx/                     # PR number (5 digits)
│       ├── notes.md               # Work notes
│       └── postmortem-*.md        # Post-mortem documents (if applicable)
│
├── .tmp/                          # Temporary files and workspaces (gitignored)
│
├── doc/
│   ├── mapping/                   # Documentation mapping files
│   │   ├── mapping-v6.md          # v6 documentation to knowledge file mapping
│   │   ├── mapping-v6.xlsx        # Excel export for human review
│   │   └── mapping-file-design.md # Mapping file design specification
│   ├── nabledge-design.md         # Architecture design
│   └── development-status.md      # Development progress tracking
│
├── scripts/                       # Utility scripts
│   ├── mapping/                   # Mapping file generation scripts
│   │   ├── generate-mapping-v6.py # Generate mapping file
│   │   ├── validate-mapping.py    # Validate mapping file
│   │   └── export-mapping-excel.py # Export to Excel
│   └── setup-6-*.sh               # Setup scripts
│
├── work/                          # Work logs (date-based)
│   └── YYYYMMDD/                  # Daily work logs
│
└── CLAUDE.md                      # This file
```

---

## Nablarch Official Documentation

The `.lw/nab-official/` directory contains cloned Nablarch official repositories for reference when creating knowledge files.

### Repository Versions

| Repository | v6 | v5 | Notes |
|------------|----|----|-------|
| **nablarch-document** | ✓ (main) | ✓ (v5-main) | Official framework documentation |
| **nablarch-single-module-archetype** | ✓ (main) | ✓ (v5-main) | Maven archetype for single-module projects |
| **nablarch-system-development-guide** | ✓ (main) | - | System development guide (latest/v6 only) |

### Note for nabledge-5 Development

When creating knowledge files for **nabledge-5**, use the following sources:
- **Framework docs**: Use `.lw/nab-official/v5/nablarch-document/` (v5-specific)
- **Archetype**: Use `.lw/nab-official/v5/nablarch-single-module-archetype/` (v5-specific)
- **Development guide**: Reference `.lw/nab-official/v6/nablarch-system-development-guide/` (no v5 version exists; v6 guide applies)

---

## Project Rules

The `.claude/rules/` directory contains project guidelines and conventions:

| Rule | Description |
|------|-------------|
| **changelog.md** | CHANGELOG management (Unreleased section only, version control in nablarch/nabledge) |
| **issues.md** | Issue format (user story format with Situation, Pain, Benefit, Success Criteria) |
| **work-notes.md** | Work notes format (focus on why/how, not what - git log shows changes) |
| **postmortem.md** | Post-mortem format for significant incidents |
| **temporary-files.md** | Temporary file policy (use `.tmp/` directory) |
| **permission-settings.md** | Permission settings policy (.claude/settings.json) |
| **release.md** | Release process (managed in nablarch/nabledge repository) |

These rules are enforced through the CLAUDE.md and .claude/rules/ configuration that Claude Code reads automatically.

---

## Documentation Mapping Files

The `doc/mapping/` directory contains mapping files that connect Nablarch official documentation to nabledge knowledge files.

### Purpose

Mapping files enable:
- **Automatic knowledge file generation** from official documentation
- **Category-based filtering** for targeted processing
- **Traceability** from knowledge files back to official sources
- **Automated asset collection** through reference directives

### Key Files

| File | Description |
|------|-------------|
| **mapping-v6.md** | Main mapping file (302 documentation files) with Source Path, Title, Official URL, Type, Category ID, Processing Pattern, Target Path |
| **mapping-v6.xlsx** | Excel export for human review with clickable URLs and filters |
| **mapping-file-design.md** | Design specification for mapping file structure, taxonomy, and usage |

### Usage

**Filter by Processing Pattern** (incremental creation):
```bash
# Extract nablarch-batch specific documentation
grep "nablarch-batch" doc/mapping/mapping-v6.md
```

**Filter by Category ID**:
```bash
# Extract all handlers documentation
grep "| handlers |" doc/mapping/mapping-v6.md
```

**Validation**:
```bash
# Validate mapping file integrity
python3 scripts/mapping/validate-mapping.py doc/mapping/mapping-v6.md
```

**Excel Export** (required for human review):
```bash
# Generate Excel file for stakeholder review
python3 scripts/mapping/export-mapping-excel.py
# Output: doc/mapping/mapping-v6.xlsx
```

See [Mapping File Design](doc/mapping/mapping-file-design.md) for detailed specifications.

---

## Scope

### In Scope

| Item | Description |
|------|-------------|
| **Nablarch Batch (On-demand)** | FILE to DB, DB to DB, DB to FILE patterns |
| **RESTful Web Services** | JAX-RS support, REST API implementation |

### Out of Scope

| Item | Reason |
|------|--------|
| Jakarta Batch | Explicitly excluded in specification |
| Resident Batch (Table Queue) | Explicitly excluded in specification |
| Web Applications (JSP/UI) | Focus on batch & REST only |
| Messaging (MOM) | Out of scope |

---

## Design Documentation

Refer to the detailed design documents:

- [Nabledge Design Document](doc/nabledge-design.md) - Architecture and skill design
- [Mapping File Design](doc/mapping/mapping-file-design.md) - Documentation mapping specification
