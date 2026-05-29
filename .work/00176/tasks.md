# Tasks: Limit dependency graphs to 15 classes

**PR**: TBD
**Issue**: #176
**Updated**: 2026-05-29 (期待値追加)

## Workflow rules

- 1コミット = 1タスク
- SCを満たすよう実装する（依存グラフが最大15クラス、ビジネスロジックに最関連するクラスに集中）
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## Design decision

**Approach**: LLM (Step 3.4) handles class filtering — not the script.

- `generate-mermaid-skeleton.sh` generates all classes as-is (no change needed)
- Step 3.4 Dependency diagram section in `code-analysis.md` gets new rule:
  "If skeleton has more than 15 classes, reduce to 15 by dropping lowest-priority classes"
- Priority order (LLM judges from code already read in Step 1):
  1. Target class itself
  2. Classes directly called in the main business logic path
  3. Nablarch framework classes central to the feature
  4. Other project classes (helpers, utilities, entities)
  5. Peripheral imports not involved in main flow
- All 5 versions (v6/v5/v1.4/v1.3/v1.2) must be updated (same content)

## In Progress

## Not Started

### T1: Update code-analysis.md Step 3.4 Dependency diagram — v6
**File**: `.claude/skills/nabledge-6/workflows/code-analysis.md`

**Steps:**
- [ ] In Step 3.4 "Dependency diagram" section, add after "Step 2: Refine skeleton":
  - A "Step 3: Limit to 15 classes" block with the priority rule and instructions
- [ ] Verify: section order and wording match the SC exactly
- [ ] Commit: `docs: limit dependency graph to 15 classes in code-analysis workflow (v6) (#176)`
- [ ] **動作確認**: `ImportZipCodeFileDataFormatAction` (v6) を対象にワークフロー実行
  - acceptance: `grep -c "^\s*class " <出力ファイル>` が 15 以下
  - acceptance: 出力 classDiagram の選択クラスが下記期待値と一致すること（目視確認）
- [ ] 動作確認結果を `.work/00176/verification-t1.md` に記録
- [ ] ユーザーに結果を提示して確認

**期待値 — ImportZipCodeFileDataFormatAction (23 imports → 15 classes)**

残す15クラス（ビジネスロジック中心）:

| 優先度 | クラス | 残す理由 |
|--------|--------|----------|
| 1 | `ImportZipCodeFileDataFormatAction` | ターゲット本体 |
| 2 | `FileBatchAction` | extendsの親クラス（処理構造の根幹） |
| 3 | `ZipCodeDataFormatForm` | doData()でデータ展開・バリデーション対象 |
| 4 | `ZipCodeData` | doData()でDB insert対象 |
| 5 | `UniversalDao` | メイン処理のDB操作 |
| 6 | `BeanUtil` | doData()でForm→Entityのデータ変換 |
| 7 | `DataRecord` | 全do*メソッドの入力型 |
| 8 | `ExecutionContext` | 全do*メソッドのパラメータ |
| 9 | `ValidatorUtil` | doData()でBean Validation実行 |
| 10 | `Validator` | バリデーション本体 |
| 11 | `ConstraintViolation` | バリデーション結果処理 |
| 12 | `AppDbConnection` | initialize()のTRUNCATE処理 |
| 13 | `DbConnectionContext` | initialize()のDB接続取得 |
| 14 | `SqlPStatement` | initialize()のTRUNCATEステートメント |
| 15 | `ValidatableFileDataReader` | getValidatorAction()の戻り型 |

落とす7クラス（ロギング・単純ラッパー）:

| クラス | 落とす理由 |
|--------|-----------|
| `Result` | 戻り値の単純ラッパー、処理内容に影響なし |
| `CommandLine` | initialize()のパラメータのみ、処理に影響なし |
| `Message` | ログ出力のみ |
| `MessageLevel` | ログ出力のみ |
| `MessageUtil` | ログ出力のみ |
| `Logger` | ロギングインフラ |
| `LoggerManager` | ロギングインフラ |

### T2: Apply same change to v5/v1.4/v1.3/v1.2
**Files**:
- `.claude/skills/nabledge-5/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.4/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.3/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.2/workflows/code-analysis.md`

**Steps:**
- [ ] Confirm all 4 files have identical content to v6 at the target section (diff check)
- [ ] Apply identical change to all 4 files
- [ ] Verify: diff between v6 and each other version at the changed section is empty
- [ ] Commit: `docs: limit dependency graph to 15 classes in code-analysis workflow (v5/v1.4/v1.3/v1.2) (#176)`

### T3: Expert review + diff check
**Steps:**
- [ ] Run expert review (Prompt Engineer) on changed workflow files
- [ ] Address all Findings
- [ ] Diff check: confirm only the expected sections changed across all 5 versions
- [ ] Output diff check result to `.work/00176/diff-check.md`
- [ ] Present results to user for confirmation

### T4: Create PR
**Steps:**
- [ ] `Skill(skill: "pr", args: "create")`

## Done
