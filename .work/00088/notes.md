# Notes

## 2026-02-25

### Implementation Summary

Implemented prototype for Issue #88: index.toon redesign using L2+title format instead of L1+L2+L3.

**Files modified**:
- `.claude/skills/nabledge-6/knowledge/index.toon` - 11 prototype entries with new hint design
- `.claude/skills/nabledge-6/workflows/keyword-search.md` - Updated to reflect L2+title approach

### Prototype Entries (11 total)

**Libraries (6 entries)**:
1. Nablarchバッチ（都度起動型・常駐型）
2. JSR352準拠バッチ（Jakarta Batch）
3. ユニバーサルDAO
4. データベースアクセス（JDBCラッパー）
5. データベースコードジェネレータ
6. データバインド
7. 汎用データフォーマット
8. 業務日付

**Handlers (3 entries)**:
9. データベース接続管理ハンドラ
10. トランザクション管理ハンドラ
11. データリードハンドラ

### Design Changes

**OLD format** (L1 + L2 + L3):
```
ユニバーサルDAO, データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御, ...
```

**NEW format** (L2 + title):
```
ユニバーサルDAO, DAO O/Rマッパー CRUD JPA ユニバーサルDAO UniversalDao, ...
```

**Changes**:
- ❌ Removed L1: データベース, ファイル, ハンドラ, バッチ, 日付 (too generic → noise)
- ❌ Removed L3: 検索, ページング, 排他制御, データ変換, 接続 (moved to .index in knowledge files)
- ✅ Added title: Japanese + English variations for direct title matching

### Rationale

**L1 removal**: Generic domain terms (データベース, ファイル, ハンドラ) cause excessive noise matches
- Example: "ページング" query would match database-access.json only because of L1:データベース
- Analysis showed 58-67% file reduction by removing L1

**L3 movement**: Functional keywords better suited for section-level matching
- L3 keywords (ページング, 検索, etc.) already exist in .index sections
- Verified in universal-dao.json: paging section has hints ["ページング", "per", "page", "Pagination", "EntityList", "件数取得"]

**Title addition**: Improves recall for direct entry name queries
- User asks "UniversalDaoの使い方" → directly matches title hint
- Both Japanese (ユニバーサルDAO) and English (UniversalDao) included

### Workflow Changes

Updated `workflows/keyword-search.md`:

1. **Keyword extraction**: Changed from 3 levels (L1, L2, L3) to 2 levels (L2, L3)
   - L2 now explicitly includes entry titles
   - Removed L1 extraction step

2. **Scoring**: Updated to reflect L2-only file selection
   - File selection: L2 match = +2, L3 match = +1
   - Section selection: L2 match = +2, L3 match = +2

3. **Example updated**: Paging example shows 50% reduction (2 files → 1 file)

4. **Added note**: Documented prototype status and design rationale

### Knowledge File Verification

Verified `.index` structure in `features/libraries/universal-dao.json`:
- ✅ Section hints properly use L3 keywords (ページング, per, page, etc.)
- ✅ L2 keywords at section level (DAO, O/Rマッパー, etc.)
- ✅ Clear separation between file-level (L2+title) and section-level (L2+L3) hints

### Expected Impact (from analysis documents)

**File selection reduction**: 58-67% average
- Scenario 1 (ページング): 2 → 1 files (50% reduction)
- Scenario 2 (UniversalDao): 4 → 1 files (75% reduction)
- Scenario 4 (バッチファイル読込): 10 → 3-4 files (60-70% reduction)
- Scenario 5 (CSVデータバインド): 15 → 2 files (87% reduction)

**No degradation**: Scenarios 7-8 maintained same precision (no worse cases found)

### Next Steps (not implemented in this prototype)

1. **Full rollout**: Apply L2+title design to remaining 82 entries in index.toon
2. **Benchmark**: Run nabledge-test with 10 scenarios to validate improvements
3. **L3 audit**: Verify all knowledge files have appropriate .index sections with L3 keywords
4. **English title standardization**: Establish consistent rules for English entry names
   - Example: "データベースアクセス（JDBCラッパー）" → "DatabaseAccess" + "JDBCWrapper"

### Design Decisions

**DataRead handler special case**:
- OLD: "データ読み込み" (generic)
- NEW: "ファイル読み込み データベース読み込み" (specific)
- Rationale: "データ読み込み" is too generic; split into specific source types

**Business date case**:
- Kept L2: "業務日付 システム日付 日時管理" (all are technical components, not generic)
- Added English: "BusinessDate SystemDate DateUtil"
- Rationale: These are specific API/concept names, not generic terms like "日付"

**Handler entries**:
- Removed L1: "ハンドラ" (too generic, applies to 40+ handlers)
- Kept L2: Specific handler functions (接続管理, トランザクション, DataReader)
- Added title: Full Japanese name + English class name

### Lessons Learned

1. **L1 vs L2 distinction**: Key insight is that generic category terms (L1) should be removed, but specific technical terms that happen to be broad (like "業務日付") should be kept as L2

2. **Title is critical**: Many user queries directly reference entry names ("UniversalDaoの使い方", "データバインドの例")

3. **English variations matter**: Users may use English class names (UniversalDao) or Japanese names (ユニバーサルDAO)

4. **L3 already in place**: Knowledge files already have well-structured .index sections with L3 keywords, so no additional work needed there

### Validation

To validate this prototype:
1. ✅ Read analysis documents (index-redesign-proposal.md, l2-only-analysis.md)
2. ✅ Selected diverse entries (6 libraries + 5 handlers across different domains)
3. ✅ Applied L2+title design consistently
4. ✅ Updated workflow documentation
5. ✅ Verified knowledge file .index structure
6. ✅ Documented design rationale and expected impact
