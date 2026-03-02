Closes #99

## Approach

Implement nabledge-creator tool to automate conversion of Nablarch official documentation (RST/MD/Excel) into AI-searchable knowledge files (JSON). The tool follows a 6-step pipeline design:

1. **List sources** - Scan official documentation files
2. **Classify** - Categorize by Type/Category based on directory structure
3. **Generate** - Extract knowledge with claude -p using "nothing missed, nothing added" principle
4. **Build index** - Aggregate metadata from all knowledge files
5. **Generate docs** - Convert JSON to human-readable Markdown
6. **Validate** - Verify structure (17 items) and content (4 aspects)

**Technical choices:**
- Python 3 with standard library (concurrent.futures for parallelism)
- Claude Sonnet 4.5 for all AI-powered steps
- JSON Schema for structured output
- Resume capability for cost-efficient reruns

**Quality assurance:**
- 17 structural checks (JSON format, required fields, URL validity, hints coverage)
- 4 content validation aspects (information completeness, no hallucination, section splitting, search hint quality)
- All checks must pass before completion

## Tasks

- [x] Delete existing knowledge files (clean slate)
- [x] Create project structure (tools/knowledge-creator/)
- [x] Implement run.py (CLI entry point)
- [x] Implement Step 1 (list_sources.py: source file scanning)
- [x] Implement Step 2 (classify.py: Type/Category classification)
- [x] Implement Step 3 (generate.py: knowledge file generation with concurrency)
- [x] Implement Step 4 (build_index.py: index.toon generation)
- [x] Implement Step 5 (generate_docs.py: Markdown documentation)
- [x] Implement Step 6 (validate.py: validation framework)
- [x] Create prompt templates (generate.md, classify_patterns.md, validate.md)
- [x] Create comprehensive documentation (README.md)
- [x] Apply expert review improvements (path validation, error handling, documentation clarity)

## Expert Review

Three AI expert reviews were conducted on the implementation:

- [Software Engineer Review](./.pr/00099/review-by-software-engineer.md) - Rating: 4/5
  - Overall: Well-structured with good separation of concerns
  - Improvements: Path validation added, minor issues deferred to future

- [Prompt Engineer Review](./.pr/00099/review-by-prompt-engineer.md) - Rating: 4/5
  - Overall: Clear instructions with comprehensive validation rules
  - Improvements: Error handling added, thresholds clarified, validation criteria defined

- [Technical Writer Review](./.pr/00099/review-by-technical-writer.md) - Rating: 4/5
  - Overall: Comprehensive documentation with clear structure
  - Improvements: File paths standardized, terminology made consistent, heading hierarchy fixed

**9 high-value improvements implemented**, including path validation, error handling documentation, threshold clarification, and documentation consistency fixes.

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Delete all existing knowledge files before starting implementation | ✅ Done | All docs/knowledge files removed in commit 7169525 |
| nabledge-creator tool is created and functional | ✅ Done | Implemented at `tools/knowledge-creator/` with complete 6-step pipeline |
| Implementation follows design document | ✅ Done | Follows `doc/99-nabledge-creator-tool/knowledge-creator-design.md` specifications |
| Tool supports nabledge-6 and nabledge-5 | ✅ Done | Supports `--version 6/5/all` parameter |
| Tool provides clear error messages | ✅ Done | Per-file logging at `logs/v{version}/` with success/error tracking |
| Documentation includes usage examples | ✅ Done | README.md with usage examples, CLI help, troubleshooting guide |
| All knowledge files recreated using tool | ⬜ Pending | Tool ready, will be executed separately to generate 252 knowledge files for v6 |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
