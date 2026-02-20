# Scripts

This directory contains utility scripts for nabledge development and code analysis optimization.

## Script Locations

Scripts are organized by deployment scope:

**Skill-included scripts** (`.claude/skills/nabledge-6/scripts/`):
- `prefill-template.sh`: Pre-fills code analysis template placeholders
- `generate-mermaid-skeleton.sh`: Generates Mermaid diagram skeletons
- These scripts are deployed with the nabledge-6 skill to user environments

**Development-only scripts** (`scripts/`):
- `setup-6-cc.sh`, `setup-6-ghc.sh`: Installation scripts
- `test-*.sh`: Test scripts
- `mapping/*.py`: Documentation mapping tools
- These scripts remain in the development repository only

## Code Analysis Optimization Scripts

These scripts support the code analysis workflow by pre-filling deterministic placeholders and generating diagram skeletons, reducing LLM generation time from ~100 seconds to ~45-55 seconds.

### prefill-template.sh

Pre-fills 8 deterministic placeholders in the code analysis template.

**Parameters**:

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--target-name` | Yes | Target name | "LoginAction" |
| `--target-desc` | Yes | One-line description | "ログイン認証処理" |
| `--modules` | Yes | Affected modules | "proman-web, proman-common" |
| `--source-files` | Yes | Comma-separated source file paths | "src/LoginAction.java,src/LoginForm.java" |
| `--knowledge-files` | Yes | Comma-separated knowledge file paths | "docs/web.md,docs/dao.md" |
| `--output-path` | Yes | Output file path | ".nabledge/20260220/code-analysis-login.md" |
| `--official-docs` | No | Comma-separated documentation URLs | "https://nablarch.github.io/..." |

**Usage**:
```bash
.claude/skills/nabledge-6/scripts/prefill-template.sh \
  --target-name "<name>" \
  --target-desc "<description>" \
  --modules "<modules>" \
  --source-files "<file1.java,file2.java>" \
  --knowledge-files "<knowledge1.md,knowledge2.md>" \
  --output-path ".nabledge/YYYYMMDD/code-analysis-<target>.md" \
  [--official-docs "<url1,url2>"]
```

**Pre-filled placeholders**:
- `{{target_name}}`: Target name
- `{{generation_date}}`: Current date (auto-generated)
- `{{generation_time}}`: Current time (auto-generated)
- `{{target_description}}`: One-line description
- `{{modules}}`: Affected modules
- `{{source_files_links}}`: Source file links with relative paths
- `{{knowledge_base_links}}`: Knowledge base links
- `{{official_docs_links}}`: Official documentation links

**Time saved**: ~25-30 seconds

### generate-mermaid-skeleton.sh

Generates Mermaid diagram skeletons from Java source files.

**Parameters**:

| Parameter | Required | Description | Values/Example |
|-----------|----------|-------------|----------------|
| `--source-files` | Yes | Comma-separated Java source file paths | "src/LoginAction.java,src/LoginForm.java" |
| `--diagram-type` | Yes | Type of diagram to generate | "class" or "sequence" |
| `--main-class` | No | Main class name for sequence diagram | "LoginAction" |

**Usage for class diagram**:
```bash
.claude/skills/nabledge-6/scripts/generate-mermaid-skeleton.sh \
  --source-files "<file1.java,file2.java>" \
  --diagram-type class
```

**Usage for sequence diagram**:
```bash
.claude/skills/nabledge-6/scripts/generate-mermaid-skeleton.sh \
  --source-files "<main-file.java>" \
  --diagram-type sequence \
  --main-class "<MainClass>"
```

**Generated content**:
- Class diagram: class names, basic relationships (extends, implements, uses)
- Sequence diagram: participants, basic flow structure

**LLM refinement needed**:
- Add `<<Nablarch>>` annotations to framework classes
- Add relationship labels (e.g., "validates", "uses")
- Add detailed method calls and error handling

**Time saved**: ~15-20 seconds

## Workflow Integration

These scripts are integrated into `.claude/skills/nabledge-6/workflows/code-analysis.md`:

1. **Step 3.2**: Use `.claude/skills/nabledge-6/scripts/prefill-template.sh` to create template with 8 placeholders filled
2. **Step 3.3**: Use `.claude/skills/nabledge-6/scripts/generate-mermaid-skeleton.sh` to generate diagram skeletons
3. **Step 3.4**: LLM refines skeletons and fills remaining 8 placeholders
4. **Step 3.5**: Write file with all content
5. **Step 5**: Calculate duration and update file with sed

**Expected time savings**: ~40-50 seconds total (from ~100s to ~45-55s)

## Error Handling

All scripts follow consistent error handling practices:

**Exit codes**:
- `0`: Success
- `1`: Error (missing arguments, file not found, invalid input, etc.)

**Error output**:
- All error messages are written to stderr (>&2)
- Errors include context (what failed and why)

**Common errors**:

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required arguments" | Required parameter not provided | Check usage with `--help` |
| "Template file not found" | Template missing or wrong path | Verify `.claude/skills/nabledge-6/assets/` exists |
| "Source file not found" | File path incorrect | Use paths relative to project root |
| "Source file is not readable" | Permission denied | Check file permissions with `ls -l` |
| "Invalid diagram type" | Wrong diagram type value | Use "class" or "sequence" |

**Cleanup**:
- Scripts use trap handlers to clean up temporary files on exit or error
- Temporary files are automatically removed even if script is interrupted

## Setup Scripts

### setup-6-cc.sh / setup-6-ghc.sh

Install nabledge-6 skill for Claude Code or GitHub Copilot.

**Usage**:
```bash
# Claude Code
bash <(curl -fsSL https://raw.githubusercontent.com/nablarch/nabledge/main/scripts/setup-6-cc.sh)

# GitHub Copilot
bash <(curl -fsSL https://raw.githubusercontent.com/nablarch/nabledge/main/scripts/setup-6-ghc.sh)
```

**Features**:
- Downloads nabledge-6 skill from nablarch/nabledge repository
- Installs to `.claude/skills/nabledge-6/`
- Optionally installs jq if not present
- Verifies installation

## Test Scripts

### test-issue-27-reproduce.sh

Tests plugin recognition on first startup (Issue #27).

**Usage**:
```bash
scripts/test-issue-27-reproduce.sh
```

Verifies that nabledge-6 is immediately recognized after setup without restart.

## Mapping Scripts

Scripts in `scripts/mapping/` support the documentation mapping workflow:

- `generate-mapping-v6.py`: Generate mapping files from official docs
- `validate-mapping.py`: Validate mapping file structure
- `export-mapping-excel.py`: Export mapping to Excel format
- `verify-excel-md-match.py`: Verify Excel and Markdown consistency
- `verify-title-match.py`: Verify titles match between sources

See `doc/mapping/mapping-file-design.md` for details.
