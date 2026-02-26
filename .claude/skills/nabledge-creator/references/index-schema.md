# Index Schema (index.toon)

Knowledge file search index structure and format specification.

## Purpose

nabledge-6's keyword-search reads index.toon first to filter candidate files. Without index, all JSON files must be scanned, consuming massive context. index.toon enables search across entries with ~5-7K tokens.

Including not-yet-created knowledge files allows keyword-search to respond accurately: "This information is not yet available in knowledge files."

## File Format: TOON

TOON (Table-Oriented Object Notation) is a human-readable format designed for LLMs:
- Compact representation
- Easy parsing
- Space-separated values
- Title-sorted entries

## Structure

```toon
# Nabledge-{N} Knowledge Index

files[{count},]{title,hints,path}:
  {title}, {hints}, {path}
  {title}, {hints}, {path}
  ...
```

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| count | integer | Total number of entries | e.g., 154 |
| title | string (Japanese) | Knowledge file title | ユニバーサルDAO |
| hints | space-separated strings | Search keywords (Japanese/English mixed) | データベース DAO O/Rマッパー CRUD JPA |
| path | string | Relative path from knowledge/ directory or "not yet created" | features/libraries/universal-dao.json |

### Constraints

1. **Sorting**: Entries sorted by title (Japanese lexical order)
2. **Completeness**: All knowledge files from knowledge-file-plan.md included
3. **Status tracking**: Created files have path, uncreated files have "not yet created"
4. **Hint quality**: 3-8 hints per file, covering L1+L2 keywords
5. **No duplicates**: Each knowledge file appears exactly once

## Hint Generation Strategy

### For Created Knowledge Files

Extract and aggregate hints from knowledge file's `index[].hints`:

1. **L1 keywords** (category/domain level):
   - バッチ (batch)
   - データベース (database)
   - Web, REST, メッセージング (messaging)

2. **L2 keywords** (feature/component level):
   - Class names: UniversalDao, DataReader
   - Concepts: ページング (paging), 排他制御 (exclusive control)
   - Technologies: JPA, JDBC, JSR352

3. **Deduplication**: Remove duplicate hints across sections

**Example**:
```json
Knowledge file universal-dao.json has sections:
  - overview: hints ["データベース", "DAO", "CRUD"]
  - paging: hints ["ページング", "検索", "Paginator"]
  - search: hints ["検索条件", "SQLBuilder"]

Aggregated hints for index.toon:
  データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御
```

### For Not-Yet-Created Knowledge Files

Estimate hints from knowledge-file-plan.md metadata:

1. **Extract nouns from title**:
   - "Jakarta Batch準拠バッチアプリケーション" → Jakarta Batch, バッチ, アプリケーション

2. **Map tags to L1 keywords**:
   - `batch` → バッチ, 大量データ処理
   - `rest` → REST, Web API
   - `handlers` → ハンドラ, アーキテクチャ

3. **Add standard terms**:
   - 標準仕様, 設定, 実装

**Example**:
```
Plan entry:
  title: JSR352準拠バッチ（Jakarta Batch）
  tags: jakarta-batch

Estimated hints:
  バッチ JSR352 Jakarta Batch Batchlet Chunk 標準仕様
```

## File Location

```
.claude/skills/nabledge-6/knowledge/index.toon
```

## Generation Process

### Phase 2 (Complete): Metadata-based Index

Generated from mapping-v6.md metadata with scope filters:
- Input: Documentation files
- Filters: Coverage scope + Knowledge scope
- Extract: title (Japanese), category, source path
- Hints: Extract keywords from title + category mapping
- Status: All entries marked "not yet created"
- Output: All entries

**Purpose**: Establishes search structure for validation before knowledge generation (Phase 2 complete, ready for Phase 3)

### Phase 3-4: Knowledge-based Index

Update after each knowledge file batch:
1. Scan created knowledge files (.json)
2. Aggregate hints from `index[].hints`
3. Update corresponding entry in index.toon
4. Change path from "not yet created" to actual path

**Purpose**: Provide search functionality during incremental generation

## Validation Rules

### Schema Validation

- [x] Header format: `files[{count},]{title,hints,path}:`
- [x] Entry count matches knowledge-file-plan.md total
- [x] All entries have non-empty title
- [x] All entries have non-empty hints (at least 3)
- [x] Created file paths exist in knowledge/ directory
- [x] No duplicate entries (by title)

### Quality Validation

- [ ] Hints cover L1+L2 keywords for created files
- [ ] Japanese hints use proper kanji/hiragana (not English transliteration)
- [ ] English hints use proper technical terms (not Japanese romanization)
- [ ] Estimated hints for uncreated files are reasonable

### Search Validation

- [ ] Sample queries return expected files
- [ ] All major concepts are searchable
- [ ] No orphaned files (files without searchable hints)

## Evolution Strategy

```
Phase 2: mapping → index (metadata) [COMPLETE]
         ├─ Docs → entries (after filters)
         ├─ Basic hints from titles
         └─ All "not yet created"

Phase 3: Pilot files → index update
         ├─ Pilot entries updated
         ├─ Detailed hints from sections
         └─ Paths updated to .json

Phase 4: All files → complete index
         ├─ All entries updated
         ├─ Full hint coverage
         └─ Search-ready knowledge base
```

## Example

```toon
# Nabledge-6 Knowledge Index

files[{count},]{title,hints,path}:
  Nablarchバッチ（都度起動型・常駐型）, バッチ 都度起動 常駐 大量データ処理 アーキテクチャ ハンドラ DataReader, features/processing/nablarch-batch.json
  JSR352準拠バッチ（Jakarta Batch）, バッチ JSR352 Jakarta Batch Batchlet Chunk 標準仕様, not yet created
  ユニバーサルDAO, データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御, features/libraries/universal-dao.json
  データバインド, ファイル データ変換 CSV TSV 固定長 JavaBeans Map, not yet created
  SLF4Jアダプタ, ログ SLF4J アダプタ log4j logback ロギングフレームワーク, features/adapters/slf4j-adapter.json
```

## Notes

- **Incremental updates**: Index grows with knowledge base
- **Search-first design**: Structure optimized for keyword matching
- **Bilingual hints**: Japanese primary (user queries), English secondary (technical terms)
- **Not yet created tracking**: Enables "not available" responses instead of silence
