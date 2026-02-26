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
2. **Completeness**: All knowledge files from mapping-v{version}.md included (dynamically determined)
3. **Status tracking**: Created files have path, uncreated files have "not yet created"
4. **Hint quality**: 3-8 hints per file, covering L1+L2 keywords
5. **No duplicates**: Each knowledge file appears exactly once

## Hint Generation Strategy

File-level hints contain technical components and entry titles.

### For Created Knowledge Files

Extract hints from knowledge file content:

1. **L1 technical components**:
   - Class names: UniversalDao, DataReader, DbConnectionManagementHandler
   - Technologies: DAO, JDBC, JPA, Bean Validation, CSV, NTF
   - Concepts: O/Rマッパー, CRUD, トランザクション

2. **Entry titles** (Japanese + English):
   - ユニバーサルDAO, UniversalDao
   - データベース接続管理ハンドラ, DbConnectionManagementHandler

3. **Not included in index.toon**:
   - Generic domain terms: データベース, ファイル, ハンドラ, バッチ
   - Functional keywords: ページング, 検索, 登録, 更新 (section-level only)

4. **Deduplication**: Remove duplicate hints

**Example**:
```json
Knowledge file universal-dao.json:
  - title: ユニバーサルDAO
  - overview.classes: ["UniversalDao"]
  - Technologies: DAO, JPA, JDBC, CRUD

Aggregated hints for index.toon:
  DAO O/Rマッパー CRUD JPA ユニバーサルDAO UniversalDao
```

### For Not-Yet-Created Knowledge Files

Estimate hints from mapping file metadata:

1. **Extract technical terms from title**:
   - "Jakarta Batch準拠バッチアプリケーション" → Jakarta Batch, JSR352, Batchlet, Chunk

2. **Extract class names from source paths**:
   - Path contains "universal_dao" → UniversalDao
   - Path contains "db_connection" → DbConnectionManagementHandler

3. **Add entry titles** (Japanese + English):
   - From mapping title and title_ja fields

4. **Do not include generic domain terms**:
   - バッチ, データベース, ハンドラ, ファイル

**Example**:
```
Mapping entry:
  title: JSR352準拠バッチ（Jakarta Batch）
  category: jakarta-batch

Estimated hints:
  JSR352 Jakarta Batch Batchlet Chunk JSR352準拠バッチ
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
- [x] Entry count matches mapping-v{version}.md filtered entries (dynamic count)
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
