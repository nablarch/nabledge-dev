# nabledge-dev

Development repository for nabledge skills - AI assistants for Nablarch framework development.

## Language

**Developer content**: English (code, issues, PRs, commits, docs)

**End-user interface**: Japanese (user guides, questions, output, errors)

**AI conversations**: English by default; request Japanese when needed

See `.claude/rules/language.md` for detailed guidelines and examples.

## Overview

This repository develops **nabledge skills** for AI agents:
- **nabledge-6**: Nablarch 6 (Jakarta EE 10, Java 17+)
- **nabledge-5**: Nablarch 5 (Java EE 7/8, Java 8+) - planned

## Key Resources

- **Design**: `docs/nabledge-design.md` - Architecture, scope, and skill design
- **Mapping**: `docs/mapping/` - Documentation to knowledge file mappings (302 files for v6)
- **Official Docs**: `.lw/nab-official/` - Cloned Nablarch repositories (v6 and v5)
- **Project Rules**: `.claude/rules/` - Workflow conventions (auto-loaded)

## Quality Standard

Nablarch is a mission-critical enterprise framework used in large-scale financial systems and other critical infrastructure. Nabledge, which provides knowledge about Nablarch, is held to the same quality standard.

**There is no room for compromise on baseline quality.**

- If there is even a 1% risk, eliminate it — do not accept it
- "Good enough" does not exist; quality is binary: correct or not correct
- verify is the quality gate for RBKC output. When verify reports a FAIL, fix RBKC — never weaken verify to make output pass
- 100% content coverage is the target across all source formats (RST, Markdown, Excel). If a content token is missing from JSON, that is an RBKC bug to fix, not a reason to lower the threshold

## Important Notes

**Mapping Files** enable category-based filtering for incremental knowledge file creation. See `docs/mapping/mapping-file-design.md` for details.
