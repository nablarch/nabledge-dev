# Index Generation Workflow

Generate search index (index.toon) from knowledge file plan and existing knowledge files.

## Skill Invocation

```
nabledge-creator index {version}
```

Where `{version}` is the Nablarch version number (e.g., `6` for v{version}, `5` for v5).

## Purpose

nabledge-{version}'s keyword-search workflow requires index.toon to efficiently find knowledge files. Without index, all JSON files must be scanned, consuming massive context. index.toon enables search across entries with ~5-7K tokens.

## When to Execute

Execute this workflow in these scenarios:

1. **Phase 2 (Initial)**: Generate metadata-based index from mapping
   - Input: mapping-v${version}.md (documentation files)
   - Filters: Coverage scope + Knowledge scope
   - Output: index.toon with basic hints, all "not yet created"

2. **Phase 3-4 (Updates)**: Update index after knowledge file batches
   - Input: Created knowledge files (.json) + existing index.toon
   - Output: Updated index.toon with detailed hints and paths

3. **Verification**: After fixing index issues found in verify-index workflow

**Entry count explanation**: Starting from documented features, we apply two filters:
- Coverage scope filter: Removes out-of-scope categories
- Knowledge scope filter: Further refines based on knowledge file plan to produce entries in index.toon

## Prerequisites

- `.claude/skills/nabledge-creator/output/mapping-v${version}.md` exists (for Phase 2)
- For updates: Knowledge files exist in `.claude/skills/nabledge-{version}/knowledge/`
- Optional: `.claude/skills/nabledge-creator/references/knowledge-file-plan.md` (reference for 統合パターンと方針)

## Workflow Steps

### Step 1: Generate Index

Execute the generation script:

```bash
python .claude/skills/nabledge-creator/scripts/generate-index.py v{version}
```

**Parameters** (all optional, use defaults):
- `--knowledge-dir`: Knowledge files directory (default: `.claude/skills/nabledge-{version}/knowledge/`)
- `--plan`: Knowledge file plan reference (default: `.claude/skills/nabledge-creator/references/knowledge-file-plan.md`) - For 統合パターンと方針 only; actual file list from mapping
- `--output`: Output file path (default: `{knowledge-dir}/index.toon`)
- `--mapping`: Mapping file for Phase 2 (default: `.claude/skills/nabledge-creator/output/mapping-v${version}.md`)

**Exit codes**:
- **0**: Success - Index generated with no issues
- **1**: Success with warnings - Index generated but some hints may be insufficient
- **2**: Error - Failed to generate index (invalid input, file not found, etc.)

**Output location**:
```
.claude/skills/nabledge-{version}/knowledge/index.toon
```

### Step 2: Verify Generated Index

Check the generated index.toon:

```bash
cat .claude/skills/nabledge-{version}/knowledge/index.toon | head -20
```

**Verify**:
- [ ] Header shows correct entry count: `files[{count},]{title,hints,path}:`
- [ ] Entries are sorted by title (Japanese lexical order)
- [ ] Each entry has: title, hints (3-8 keywords), path
- [ ] Created files show path (e.g., `features/libraries/universal-dao.json`)
- [ ] Uncreated files show "not yet created"

**Common issues**:
- Empty hints → Re-run with better title extraction
- Wrong count → Check mapping file for expected entries
- Unsorted entries → Check script's sorting logic

### Step 3: Run Validation

Validate index structure and quality:

```bash
python .claude/skills/nabledge-creator/scripts/validate-index.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

**Exit codes**:
- **0**: All validation passed
- **1**: Validation passed with warnings (quality suggestions)
- **2**: Validation failed (schema errors)

**What it checks**:
- Schema compliance (header format, field structure)
- Entry completeness (no empty titles/hints)
- File existence (created file paths are valid)
- No duplicates (each title appears once)
- Hint quality (sufficient coverage, bilingual mix)

If exit code is 2, fix errors and re-run Step 1.

### Step 4: Test Search Functionality (Optional but Recommended)

Test if index enables expected search behavior:

**4.1 Prepare Test Queries**

Create sample queries covering different categories:

```
Japanese queries:
- "データベース接続" (database connection)
- "バッチ処理" (batch processing)
- "REST API" (REST API)
- "ログ出力" (log output)

English queries:
- "universal dao"
- "handler"
- "validation"
```

**4.2 Manual Search Test**

Read index.toon and simulate search:

```bash
grep -i "データベース" .claude/skills/nabledge-{version}/knowledge/index.toon
```

Verify:
- [ ] Returns relevant entries
- [ ] Japanese hints match Japanese queries
- [ ] English hints match English queries
- [ ] Coverage: Major concepts are searchable

**4.3 Document Search Baseline** (for Phase 3-4 comparison)

Record search results for future comparison:

```
Query: "データベース接続"
Results:
  - ユニバーサルDAO (universal-dao.json)
  - データベースアクセス (database-access.json)
  - データベース接続管理ハンドラ (not yet created)

Coverage: 3 entries
```

### Step 5: Commit Index File

If validation passed (exit code 0 or 1), commit the index:

```bash
git add .claude/skills/nabledge-{version}/knowledge/index.toon
git commit -m "feat: Generate knowledge search index (Phase 2)

- Generated index.toon from mapping metadata
- All entries marked 'not yet created' (knowledge files pending)
- Basic hints extracted from titles and categories
- Enables search structure validation before knowledge generation

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push
```

## Phase-Specific Notes

### Phase 2: Initial Generation from Mapping

**Input**: mapping-v${version}.md (documentation files after filters)

**Process**:
1. Apply coverage scope filter (removes out-of-scope categories)
2. Apply knowledge scope filter (based on knowledge file plan)
3. Extract title (Japanese) and category from each filtered entry
4. Generate basic hints from title keywords + category keywords
5. Set all paths to "not yet created"
6. Sort by title

**Output**: index.toon with entries, metadata-only

**Purpose**: Establish index structure and validate search design before knowledge file generation (Phase 2 complete)

**Example entry**:
```
ユニバーサルDAO, データベース DAO データアクセス CRUD, not yet created
```

### Phase 3-4: Updates from Knowledge Files

**Input**: Created knowledge files (.json) in `.claude/skills/nabledge-{version}/knowledge/`

**Process**:
1. Scan knowledge files and extract `index[].hints`
2. Aggregate hints from all sections (L1+L2 keywords)
3. Update corresponding entries in index.toon
4. Change path from "not yet created" to actual file path

**Output**: index.toon with detailed hints for created files

**Purpose**: Provide search functionality as knowledge base grows

**Example entry after update**:
```
ユニバーサルDAO, データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御, features/libraries/universal-dao.json
```

## Error Handling

| Error | Exit Code | Response |
|-------|-----------|----------|
| Missing mapping file | 2 | Verify mapping-v${version}.md exists in output directory |
| Invalid mapping format | 2 | Check mapping file follows expected structure |
| Empty hints generated | 1 (warning) | Review title extraction logic, may need manual hints |
| Created file path doesn't exist | 2 | Verify knowledge file was created correctly |
| Duplicate titles | 2 | Check mapping file for duplicate entries |
| Sorting failed | 2 | Check locale settings for Japanese sorting |

## Next Steps

After successful index generation:

1. **Phase 2**: Proceed to verify-index workflow in separate session (optional)
2. **Phase 3**: Begin pilot knowledge file generation with Index-based verification
3. **Phase 4**: Update index incrementally after each knowledge file batch

## Verification Workflow

For thorough validation of hint quality and search coverage, execute verify-index workflow in a **separate session**:

```
nabledge-creator verify-index-6
```

See `workflows/verify-index.md` for details. Separate session ensures unbiased verification of hint quality.

## Important Notes

1. **Index-first approach**: Index structure must be validated before large-scale knowledge generation
2. **Incremental updates**: After Phase 2, update index after each knowledge file batch
3. **Search-driven design**: Index structure informs knowledge file schema
4. **Bilingual hints**: Japanese primary (user queries), English secondary (technical terms)
5. **Not yet created tracking**: Essential for providing accurate "not available" responses
6. **Title sorting**: Japanese lexical order for human readability
7. **Validation before commit**: Always run validate-index.py before committing

## References

- Schema specification: `references/index-schema.md`
- Script documentation: `scripts/generate-index.py` header comments
- Validation rules: `scripts/validate-index.py` header comments
- Design rationale: `doc/creator/improved-design-index.md`
