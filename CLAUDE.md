# nabledge-dev

Development repository for nabledge skills - AI assistants for Nablarch framework development.

## Language

**All content must be in English** (code, docs, commits, tests).

**Exception**: nabledge-x skills' user-facing messages are in Japanese for Nablarch users in Japan.

## Overview

This repository develops **nabledge skills** for AI agents:
- **nabledge-6**: Nablarch 6 (Jakarta EE 10, Java 17+)
- **nabledge-5**: Nablarch 5 (Java EE 7/8, Java 8+) - planned

## Scope

**In Scope**: Nablarch Batch (on-demand), RESTful Web Services

**Out of Scope**: Jakarta Batch, Resident Batch, Web Applications (JSP/UI), Messaging (MOM)

## Key Resources

- **Design**: `doc/nabledge-design.md` - Architecture and skill design
- **Mapping**: `doc/mapping/` - Documentation to knowledge file mappings (302 files for v6)
- **Official Docs**: `.lw/nab-official/v6/` and `.lw/nab-official/v5/` - Cloned Nablarch repositories
- **Project Rules**: `.claude/rules/` - Workflow conventions (changelog, issues, work notes, etc.)

## Important Notes

1. **Mapping Files** (`doc/mapping/mapping-v6.md`, `mapping-v6.xlsx`):
   - Enable category-based filtering for incremental knowledge file creation
   - Connect official docs to knowledge files via Source Path → Target Path
   - See `doc/mapping/mapping-file-design.md` for details

2. **Official Documentation Sources**:
   - v6: `nablarch-document` (main), `nablarch-system-development-guide` (main)
   - v5: `nablarch-document` (v5-main), no separate system-development-guide

3. **Work Organization**:
   - Work notes: `.pr/xxxxx/notes.md` (focus on decisions and context, not change lists)
   - Temporary files: `.tmp/` (gitignored, safe to delete)
   - Daily logs: `work/YYYYMMDD/` (project-specific work logs)
