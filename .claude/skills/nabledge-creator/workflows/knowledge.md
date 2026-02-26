# knowledge workflow

Generate knowledge files (JSON + Markdown) from mapping files and official documentation.

**IMPORTANT**: Follow ALL steps in this workflow file exactly as written. Do not skip steps or use summary descriptions from SKILL.md or other files. Read and execute each step according to the detailed instructions provided here.

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

### Step 2: Generate Knowledge Files (Batch Processing with Task Tool)

**Batch Processing Strategy**: Use Task tool to process files in category-based batches to avoid context overflow.

#### Step 2.1: Group Targets by Category

Read mapping file and group targets by `Type / Category`:

```bash
grep "^|" .claude/skills/nabledge-creator/output/mapping-v{version}.md | tail -n +3 | \
  awk -F'|' '{print $5 "/" $6}' | sed 's/^ *//;s/ *$//' | sort | uniq -c
```

Create batches:
- Categories with >60 files: Split into 2 batches (~30 files each)
- Categories with ≤60 files: 1 batch per category
- Save batch definitions to `.tmp/nabledge-creator/knowledge-batches-v{version}.json`

#### Step 2.2: Launch Task Agents (Parallel)

For each batch, launch a Task agent in parallel:

```
Task (parallel × N batches)
  subagent_type: "general-purpose"
  description: "Generate knowledge: {category} batch {n}"
  prompt: "You are generating knowledge files for Nablarch v{version} documentation.

## Your Assignment

**Batch ID**: {batch_id}
**Category**: {type}/{category}
**Files**: {count} files

## Input Files

Read these files first:
1. Mapping file: `.claude/skills/nabledge-creator/output/mapping-v{version}.md`
2. Schema: `.claude/skills/nabledge-creator/references/knowledge-schema.md`

Extract your batch's file list from the mapping file (rows where Type={type} AND Category={category}).

## Your Task

For each file in your batch:

### 2a. Read Sources

- Read RST file(s) from `.lw/nab-official/v{version}/` (Source Path column)
- Read Japanese version (`en/` → `ja/`) for terminology verification

### 2b. Determine Section IDs

- Follow 'Section Division Rules' in knowledge-schema.md
- Derive from RST heading structure (h2 → sections)

### 2c. Extract Hints

**Section-level hints** (.index[].hints, 3-8 items):
1. **L2 functional keywords** - What can be done (e.g., \"ページング\", \"検索\", \"登録\")
2. **Section headings** - h2 text in Japanese and English
3. **Technical elements** - Class names, properties, annotations

**File-level hints** (for index.toon, 5-8 items):
1. **L1 technical components** - Main classes, interfaces, technical terms (e.g., \"DAO\", \"JDBC\", \"UniversalDao\")
2. **Entry titles** - Both Japanese and English
3. **Class names** - Full class names
4. **Bilingual terms** - Japanese + English for L1 keywords

**Exclude from file-level hints**:
- Generic domain terms (データベース, ファイル, ハンドラ, バッチ, 日付, ログ)
- Functional keywords (ページング, 検索, 登録, 更新, 削除) - section-level only

### 2d. Convert to JSON

- Follow category templates in knowledge-schema.md
- Keep all specifications and concepts
- Optimize expression (remove verbose explanations, use bullet points)
- Criterion: \"Would lack of this information cause AI to make incorrect decisions?\" → If YES, keep it

### 2e. Output JSON

- Write to `.claude/skills/nabledge-{version}/knowledge/{Target Path from mapping}`
- Ensure parent directories exist

## Output

After completing all files in your batch:

**Report completion**:
```
Batch {batch_id} complete:
- Files processed: {count}/{count}
- JSON files generated: {count}
- Success: {success_count}
- Errors: {error_count}
```

**Update progress file**:
Write to `.tmp/nabledge-creator/knowledge-progress-v{version}.json`:
```json
{
  \"batch_id\": \"{batch_id}\",
  \"status\": \"complete\",
  \"processed\": {count},
  \"success\": {success_count},
  \"errors\": [{\"file\": \"path\", \"reason\": \"message\"}]
}
```

## Important Notes

- Process ALL files in your batch
- Read both English and Japanese RST for comprehensive understanding
- Quality over speed - ensure hints are accurate and comprehensive
- If you encounter errors, record them but continue with remaining files
"
  run_in_background: false
```

Launch all batches in parallel (use multiple Task calls in one message).

#### Step 2.3: Verify Completion

After all Task agents complete:

```bash
# Count targets from Step 1
TARGETS=[count from Step 1]

# Count generated JSON files
GENERATED=$(find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | wc -l)

echo "Targets: $TARGETS"
echo "Generated: $GENERATED"
echo "Match: $(if [ $TARGETS -eq $GENERATED ]; then echo 'YES ✓'; else echo 'NO ✗'; fi)"
```

**Completion Evidence for Step 2:**

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Targets from Step 1 | [count from Step 1] | [count] | ✓ |
| JSON files generated | [targets count] | [find ... \| wc -l] | ✓/✗ |
| All targets processed | Yes | [compare counts] | ✓/✗ |
| Task agents launched | [batches count] | [count] | ✓ |
| All batches complete | Yes | [check progress files] | ✓/✗ |

**How to measure:**
- Targets count: From Step 1 completion evidence
- JSON files: `find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | wc -l`
- Match: JSON file count must equal targets count
- All batches complete: All progress files have "status": "complete"

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

### Step 5: Update index.toon (Batch Processing with Task Tool)

**Batch Processing Strategy**: Use Task tool to process files in category-based batches to avoid context overflow.

#### Step 5.1: Group Generated Files by Category

Use the same batches as Step 2 (or re-create from generated JSON files):

```bash
# List generated JSON files grouped by category
find .claude/skills/nabledge-{version}/knowledge -name "*.json" -type f | sort
```

Create batches matching Step 2 batches.
Save to `.tmp/nabledge-creator/index-batches-v{version}.json`

#### Step 5.2: Launch Task Agents (Parallel)

For each batch, launch a Task agent in parallel:

```
Task (parallel × N batches)
  subagent_type: "general-purpose"
  description: "Update index.toon: {category} batch {n}"
  prompt: "You are updating index.toon for Nablarch v{version} knowledge files.

## Your Assignment

**Batch ID**: {batch_id}
**Category**: {type}/{category}
**Files**: {count} JSON files

## Input Files

Your batch's JSON files (in `.claude/skills/nabledge-{version}/knowledge/`):
{list of file paths}

## Your Task

For each JSON file in your batch:

### 5a. Aggregate File-level Hints

1. **Read JSON .index[].hints**
   - Collect hints from all sections
   - Extract L1 technical components (class names, technical terms)
   - Do NOT include L2 functional keywords (ページング, 検索, etc.) - section-level only

2. **Extract L1 technical components**
   - Main class names from JSON (overview.class_name, overview.classes)
   - Technical terms (DAO, JDBC, JPA, Bean Validation, etc.)
   - Include both Japanese and English forms

3. **Add entry titles**
   - Japanese title (title field from JSON)
   - English title (from official_doc_urls or JSON title)
   - Class names (full qualified names or abbreviated)

4. **Aggregate hints**
   - Remove duplicates
   - Narrow down to 5-8 items
   - Do NOT include generic domain terms (データベース, ファイル, ハンドラ, etc.)
   - Do NOT include functional keywords (ページング, 検索, 登録, 更新, etc.) - section-level only

5. **Bilingual check**
   - Japanese: technical terms, titles
   - English: class names, technical terms, titles
   - Both are properly balanced

### 5b. Update index.toon Entries

Update `.claude/skills/nabledge-{version}/knowledge/index.toon`:

1. **Search for matching entry** by title (Japanese title from JSON)

2. **Update entry**:
   - `hints`: aggregated file-level hints (5-8 items)
   - `path`: Update from \"not yet created\" to actual file path (relative to knowledge/)

3. **For new entries** (if not found):
   - Add new entry with title, hints, path
   - Insert at sorted position (Japanese lexical order using Python's sorted())

4. **Do NOT update header count yet** (will be done in Step 5.3)

Use Edit tool to update index.toon for your batch's entries.

## Output

After completing all files in your batch:

**Report completion**:
```
Batch {batch_id} complete:
- Files processed: {count}/{count}
- index.toon entries updated: {updated_count}
- index.toon entries added: {added_count}
```

**Update progress file**:
Write to `.tmp/nabledge-creator/index-progress-v{version}.json`:
```json
{
  \"batch_id\": \"{batch_id}\",
  \"status\": \"complete\",
  \"processed\": {count},
  \"updated\": {updated_count},
  \"added\": {added_count}
}
```

## Important Notes

- Process ALL files in your batch
- File-level hints must have 5-8 items (no more, no less)
- Exclude L2 functional keywords from file-level hints
- Ensure bilingual balance (Japanese + English)
- Maintain Japanese lexical order when adding new entries
"
  run_in_background: false
```

Launch all batches in parallel (use multiple Task calls in one message).

#### Step 5.3: Update Header Count

After all Task agents complete:

```bash
# Count total entries in index.toon
ENTRY_COUNT=$(grep -c '^{' .claude/skills/nabledge-{version}/knowledge/index.toon)

# Update header line
# Replace files[NNN,] with files[$ENTRY_COUNT,]
```

Use Edit tool to update the header line.

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
