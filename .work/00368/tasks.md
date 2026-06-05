# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: TBD
**Issue**: #368
**Updated**: 2026-06-05

## Rules

- 1コミット = 1タスク
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- SCを満たすようタスクを分割し、タスクリストを作業記録に出力する
- タスクリストをコミットし、PRを作成する
- PR上でIssueの目的とタスクリストの対応関係を示し、ユーザーに確認を依頼する
- 承認後、1コミット = 1タスクで各タスクを実装する
- RBKCのcreate/verifyを変更するため: 実装前に設計を行い、設計書・verify設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## In Progress

### Task 0: タスクリスト作成・PR作成・ユーザー確認
**Steps:**
- [x] Issue #368 の内容を理解する
- [x] 現状調査 (classes.md 未存在、対象カテゴリ 264 ファイル中 135 ファイルにクラス名あり)
- [x] タスクリストを `.work/00368/tasks.md` に作成する
- [ ] tasks.md をコミット・プッシュする
- [ ] PR を作成し、ユーザーに確認依頼する

## Not Started

### Task 1: 設計書更新 — classes.md 生成仕様を RBKC 設計書に追記
**Artifact**: `tools/rbkc/docs/rbkc-converter-design.md` または新規設計書
**Steps:**
- [ ] 設計書に classes.md の仕様（対象カテゴリ・フォーマット・クラス名抽出ルール）を追記
- [ ] verify 設計書 (`rbkc-verify-quality-design.md`) に classes.md の検証仕様を追記
- [ ] 設計書をコミット・プッシュ
- [ ] PR 上でユーザーに設計確認を依頼

### Task 2: TDD — test_classes_index.py を作成 (RED)
**Artifact**: `tools/rbkc/tests/ut/test_classes_index.py`
**Steps:**
- [ ] `generate_classes_md()` の単体テストを作成（対象カテゴリのみ・クラス名抽出・フォーマット検証）
- [ ] RED であることを確認: `pytest tools/rbkc/tests/ut/test_classes_index.py -x`
- [ ] コミット・プッシュ

### Task 3: TDD — verify の classes.md coverage 検証テストを作成 (RED)
**Artifact**: `tools/rbkc/tests/ut/test_verify.py` 追記
**Steps:**
- [ ] `check_classes_coverage()` のテストを作成
- [ ] RED であることを確認
- [ ] コミット・プッシュ

### Task 4: 実装 — `scripts/create/classes_index.py` を作成 (GREEN)
**Artifact**: `tools/rbkc/scripts/create/classes_index.py`
**Contents**:
- `generate_classes_md(knowledge_dir, output_path)` 関数
- 対象カテゴリ: `component`, `processing-pattern`, `development-tools`
- Javadoc リンクパターン `[ClassName](../../javadoc/javadoc-*.json)` からクラス名抽出
- フォーマット: `index.md` と同形式 (H2=category, H3=title, `path:`, `- ClassName`)
- `no_knowledge_content: true` はスキップ
**Steps:**
- [ ] `classes_index.py` を実装
- [ ] `pytest tools/rbkc/tests/ut/test_classes_index.py -x` が GREEN になることを確認
- [ ] 全テスト pass: `pytest tools/rbkc/tests/ -x`
- [ ] コミット・プッシュ

### Task 5: 実装 — verify に `check_classes_coverage()` を追加 (GREEN)
**Artifact**: `tools/rbkc/scripts/verify/verify.py`
**Contents**:
- `check_classes_coverage(knowledge_dir, classes_path)` 関数
- 対象カテゴリ JSON の有無と `classes.md` の path: エントリを照合
- No_knowledge_content はスキップ、javadoc/assets もスキップ
**Steps:**
- [ ] `verify.py` に `check_classes_coverage()` を追加
- [ ] `pytest tools/rbkc/tests/ut/test_verify.py -x` が GREEN になることを確認
- [ ] コミット・プッシュ

### Task 6: 実装 — `run.py` に classes.md 生成・verify を統合
**Artifact**: `tools/rbkc/scripts/run.py`
**Steps:**
- [ ] `create()` に `generate_classes_md()` 呼び出しを追加
- [ ] `update()` / `delete()` にも `generate_classes_md()` を追加（index.md と同様）
- [ ] `verify()` に `check_classes_coverage()` を追加（`files is None` の場合のみ）
- [ ] `pytest tools/rbkc/tests/ -x` が全 pass であることを確認
- [ ] コミット・プッシュ

### Task 7: RBKC 実行 — v6 の classes.md を生成
**Steps:**
- [ ] `bash tools/rbkc/rbkc.sh create v6` を実行
- [ ] `bash tools/rbkc/rbkc.sh verify v6` で FAIL 0 を確認
- [ ] `.claude/skills/nabledge-6/knowledge/classes.md` が生成されていることを確認
- [ ] `Jackson2BodyConverter` が classes.md に含まれることを確認
- [ ] コミット・プッシュ

### Task 8: 全バージョン RBKC 確認 (v5/v1.4/v1.3/v1.2)
**Steps:**
- [ ] 各バージョンで `bash tools/rbkc/rbkc.sh create <v> && bash tools/rbkc/rbkc.sh verify <v>` を実行
  - v5: 対象カテゴリ有無を確認、classes.md 生成を確認
  - v1.4 / v1.3 / v1.2: 対象カテゴリ有無を確認、classes.md 生成を確認
- [ ] 全バージョン FAIL 0 を確認
- [ ] コミット・プッシュ (生成された classes.md ファイルを含む)

### Task 9: semantic-search.md を更新 — classes.md を使用した 2 段階検索
**Artifact**: `.claude/skills/nabledge-6/workflows/semantic-search.md` (全バージョン共通)
**Steps:**
- [ ] Step 1 を「Read index.md AND classes.md」に変更
- [ ] Step 2 に classes.md からの候補追加ロジックを追記（クラス名マッチ）
- [ ] 全バージョンに同じ変更を適用 (nabledge-5/1.4/1.3/1.2)
- [ ] コミット・プッシュ

### Task 10: ベンチマーク実行 — qa-05 pass と全体回帰確認
**Steps:**
- [ ] qa-05 シングル実行でクラス名が選択・回答に含まれることを確認
  - `bash tools/rbkc/rbkc.sh verify v6` で FAIL 0 確認後
- [ ] HOW-TO-RUN.md の手順に従い全ベンチマーク実行
- [ ] 結果を `.work/00368/benchmark-results.md` に記録
- [ ] ベースラインと比較して regression なし (≥ 95.9%) を確認

## Done

- [x] 現状調査 (classes.md 未存在, 対象カテゴリ 264 ファイル中 135 ファイルにクラス名あり)
