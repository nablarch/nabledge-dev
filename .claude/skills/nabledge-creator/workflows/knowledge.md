# knowledge workflow

Generate knowledge files (JSON + Markdown) from mapping files and official documentation.

## Skill Invocation

```
nabledge-creator knowledge {version} [--filter "key=value"]
```

Where `{version}` is the Nablarch version number (e.g., `6` for v6, `5` for v5).

## Progress Checklist Template

```
## nabledge-creator knowledge {version} - Progress

□ Step 1: Identify Targets
□ Step 2: Generate Knowledge Files
□ Step 3: Markdown Conversion
□ Step 4: Validate JSON Files
□ Step 5: Update index.toon
□ Step 6: Validate index.toon
□ Step 7: Generate Verification Checklists

**Started:** [timestamp]
**Status:** Not started
**Filter:** [if provided, else "None - full generation"]
```

## Why This Workflow Matters

Knowledge files are the data source for nabledge-{version} skill's search pipeline. The search operates in 3 stages:

1. **index.toon** hints select files (L1/L2 keywords, threshold ≥2 points)
2. **JSON index array** hints select sections (L2/L3 keywords, threshold ≥2 points)
3. **sections content** is read to judge High/Partial/None relevance

Insufficient hints mean no search hits; coarse section granularity means no High judgments. This workflow's quality directly affects search accuracy.

## Reference Files

- `.claude/skills/nabledge-creator/output/mapping-v{version}.md` - Source documents to Target Path mapping
- `.claude/skills/nabledge-creator/references/knowledge-file-plan.md` - Integration patterns and strategy (reference info)
- `.claude/skills/nabledge-creator/references/knowledge-schema.md` - JSON structure and category templates

## Workflow Steps

### Step 1: Identify Targets

Read `.claude/skills/nabledge-creator/output/mapping-v{version}.md` and retrieve mapping rows matching the filter.

**Dynamic scanning approach**:
- All RST files under `nablarch-document/en/` are included in the mapping file
- File additions/deletions are automatically reflected in the mapping file
- Do not use knowledge-file-plan.md's individual file list (no maintenance needed when files change)

From each mapping row, extract:
- Source Path (RST file paths to read)
- Title, Title (ja)
- Type, Category ID, Processing Pattern
- Target Path (knowledge file path to generate)
- Official URL

**Completion Evidence:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Mapping file read | mapping-v{version}.md | [exists] | ✓ |
| Targets identified | >0 (or all if no filter) | [count] | ✓ |
| Filter applied | [if provided] | [criteria] | ✓ |

**How to measure:**
- Targets count: Count of rows extracted from mapping file after filter
- If no filter: targets = total rows in mapping file
- If filter: targets = rows matching filter criteria

### Step 2: Generate Knowledge Files

Generate each target knowledge file one by one. For each file:

#### 2a. Read Sources

Read all RST files specified in sources. Also refer to Japanese version (`en/` → `ja/`) for terminology verification.

#### 2b. Determine Section IDs

Follow "Section Division Rules" in `.claude/skills/nabledge-creator/references/knowledge-schema.md` to determine section IDs. Derive from RST heading structure.

#### 2c. Extract Hints

Follow "Hint Extraction Rules" in `.claude/skills/nabledge-creator/references/knowledge-schema.md` to extract hints. Extraction sources are determined by RST structural elements.

**Section-level hints (knowledge file .index[].hints, 3-8 items)**:

Include functional keywords in section-level hints:

1. **Functional keywords (L2)** - What can be done in this section (e.g., "ページング", "検索", "登録", "更新", "削除")
2. **Section headings** - h2 heading text (both Japanese and English) (e.g., "ページング", "Paging")
3. **Technical elements** - Class names, property names, annotation names (e.g., "UniversalDao", "maxCount", "@GeneratedValue")

**File-level hints (for index.toon, 5-8 items)**:

Include technical components and titles in file-level hints:

1. **L1 technical components** - Main class names, interface names, technical terms from RST (e.g., "DAO", "JDBC", "Bean Validation", "UniversalDao")
2. **Entry titles** - Both Japanese and English (e.g., "ユニバーサルDAO", "UniversalDao")
3. **Class names** - Full class names (e.g., "DbConnectionManagementHandler")
4. **Bilingual terms** - Include both Japanese and English for L1 keywords

**Do not include in file-level hints**:
- Generic domain terms (データベース, ファイル, ハンドラ, バッチ, 日付, ログ)
- Functional keywords (ページング, 検索, 登録, 更新, 削除, 設定, 管理, 処理) - section-level only

These are used by nabledge-{version} skill's keyword-search workflow (`.claude/skills/nabledge-{version}/workflows/keyword-search.md`). Without sufficient L1 technical components + titles, search will not hit. Check all target file contents and extract L1 keywords.

#### 2d. Convert to JSON

Convert to JSON following category templates in `.claude/skills/nabledge-creator/references/knowledge-schema.md`.

**Conversion criteria**:

- Keep all specifications (configuration items, defaults, types, constraints, behavior specs, rationale/background, notes, warnings)
- Keep all concepts (design philosophy, recommended patterns, precautions)
- Optimize expression (remove introductory text and verbose explanations, use bullet points)
- When in doubt: "Would lack of this information cause AI to make incorrect decisions?" → If YES, keep it

#### 2e. Output JSON

Write to `.claude/skills/nabledge-{version}/knowledge/{path}.json`.

**Completion Evidence for Step 2:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Targets from Step 1 | [count from Step 1] | [count] | ✓ |
| JSON files generated | [targets count] | [ls .claude/skills/nabledge-{version}/knowledge/*.json \| wc -l] | ✓/✗ |
| All targets processed | Yes | [compare counts] | ✓/✗ |

**How to measure:**
- Targets count: From Step 1 completion evidence
- JSON files: Count *.json files in knowledge directory
- Match: JSON file count must equal targets count

### Step 3: Markdown Conversion

Execute the following command:

```bash
python scripts/convert-knowledge-md.py .claude/skills/nabledge-{version}/knowledge/ --output-dir .claude/skills/nabledge-{version}/docs/
```

### Step 4: Validation

Execute the following command:

```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-{version}/knowledge/
```

If failed, read error content, fix JSON, and re-execute from Step 3.

### Step 5: Update index.toon

Update index.toon from generated knowledge files.

#### 5a. Aggregate File-level Hints

For each generated file, aggregate file-level hints (index.toon) from section-level hints (.index[].hints):

1. **Read JSON .index[].hints**
   - Collect hints from all sections
   - Extract L1 technical components (class names, technical terms)
   - Do not include L2 functional keywords (ページング, 検索, etc.) - section-level only

2. **Extract L1 technical components**
   - Main class names from JSON (overview.class_name, overview.classes)
   - Technical terms (DAO, JDBC, JPA, Bean Validation, etc.)
   - Include both Japanese and English forms

3. **Add entry titles**
   - Japanese title (title field)
   - English title (from official_doc_urls or RST)
   - Class names (full qualified names or abbreviated forms)

4. **Aggregate hints**
   - Remove duplicates
   - Narrow down to 5-8 items
   - Do not include generic domain terms (データベース, ファイル, ハンドラ, etc.)
   - Do not include functional keywords (ページング, 検索, 登録, 更新, etc.) - section-level only

5. **Bilingual check**
   - Japanese: technical terms, titles
   - English: class names, technical terms, titles
   - Both are properly balanced

#### 5b. Update index.toon Entries

Update `.claude/skills/nabledge-{version}/knowledge/index.toon`:

1. **Search for matching entry**
   - Search by title (matches mapping's Title (ja))

2. **Update entry**
   - `hints`: aggregated file-level hints
   - `path`: `"not yet created"` → actual file path (e.g., `features/libraries/universal-dao.json`)

3. **For new entries**
   - Add new entry with title, hints, path
   - Insert at sorted position (Japanese lexical order)

4. **Update header**
   - Count total entries
   - Update count in header line `files[{count},]{title,hints,path}:`

#### 5c. Format Validation

```bash
python scripts/validate-index.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

If validation fails, read error content and fix index.toon.

#### 5d. Status Consistency Verification

```bash
python scripts/verify-index-status.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

If inconsistencies exist:
- Actual file exists but not in index → Add entry
- In index but actual file doesn't exist → Change path to "not yet created"

### Step 6: Generate Checklist

Execute the following command:

```bash
python scripts/generate-checklist.py .claude/skills/nabledge-{version}/knowledge/{file}.json --source .lw/nab-official/v{version}/nablarch-document/en/{source-path} --output .claude/skills/nabledge-{version}/knowledge/{file}.checklist.md
```

The script analyzes both RST and JSON to generate a checklist for verification sessions. Generation session completes here. Verification is done in verify workflow (separate session).
