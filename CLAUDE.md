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
├── work/                          # Work logs (daily)
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

## Scope

For detailed scope definition, see [Nabledge Design Document Section 1.5](doc/nabledge-design.md#15-スコープ).

---

## Design Documentation

Refer to the detailed architecture design:

- [Nabledge Design Document](doc/nabledge-design.md)
