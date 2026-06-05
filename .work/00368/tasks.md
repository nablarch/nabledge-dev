# Tasks: classes.md generation for class-name-based page selection (#368)

**PR**: #369
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

## Not Started

### Task 1: 設計書更新 — classes.md 生成仕様を RBKC 設計書に追記
**Artifact**: `tools/rbkc/docs/rbkc-converter-design.md` または新規設計書
**Steps:**
- [ ] 設計書に classes.md の仕様（対象カテゴリ・フォーマット・クラス名抽出ルール）を追記
- [ ] verify 設計書 (`rbkc-verify-quality-design.md`) に classes.md の検証仕様を追記
- [ ] 設計書をコミット・プッシュ
- [ ] PR 上でユーザーに設計確認を依頼

### Task 2: TDD — test_classes.py を作成 (RED)
**Artifact**: `tools/rbkc/tests/ut/test_classes.py`
**Steps:**
- [ ] `generate_classes_md()` の単体テストを作成（対象カテゴリのみ・クラス名抽出・フォーマット検証）
- [ ] RED であることを確認: `pytest tools/rbkc/tests/ut/test_classes.py -x`
- [ ] コミット・プッシュ

### Task 3: TDD — verify の classes.md coverage 検証テストを作成 (RED)
**Artifact**: `tools/rbkc/tests/ut/test_verify.py` 追記
**Steps:**
- [ ] `check_classes_coverage()` のテストを作成
- [ ] RED であることを確認
- [ ] コミット・プッシュ

### Task 4: 実装 — `scripts/create/classes.py` を作成 (GREEN)
**Artifact**: `tools/rbkc/scripts/create/classes.py`
**Contents**:
- `generate_classes_md(knowledge_dir, output_path)` 関数（`generate_index_md` と対）
- 対象カテゴリ: `component`, `processing-pattern`, `development-tools`
- クラス名抽出: Javadoc リンクパターン `[text](../../javadoc/javadoc-*.json)` の `text` 部分を抽出
  - `text` に `#` が含まれる場合（例 `JaxRsMethodBinderFactory#handlerList`）は `#` 以降を除去しクラス名のみ採用
  - 同一ページ内の重複は除去（dedup）。出現順を保持
- 掲載対象: **クラス名が1件以上抽出されたページのみ** classes.md に出力する。クラス名ゼロのページは掲載しない
- `no_knowledge_content: true` はスキップ
- フォーマット: `index.md` と同形式 (H2=category, H3=title, `path:` 行, クラス名は `- ClassName` 行)。出力例（1ページ分）:
  ```
  ## component

  ### Jakarta RESTful Web Servicesアダプタ
  path: component/adapters/adapters-jaxrs-adaptor.json
  - Jackson2BodyConverter
  - JaxbBodyConverter
  - FormUrlEncodedConverter
  ```
**Steps:**
- [ ] `classes.py` を実装
- [ ] `pytest tools/rbkc/tests/ut/test_classes.py -x` が GREEN になることを確認
- [ ] 全テスト pass: `pytest tools/rbkc/tests/ -x`
- [ ] コミット・プッシュ

### Task 5: 実装 — verify に `check_classes_coverage()` を追加 (GREEN)
**Artifact**: `tools/rbkc/scripts/verify/verify.py`
**Contents**:
- `check_classes_coverage(knowledge_dir, classes_path)` 関数（`check_index_coverage` と対）
- 照合ルール: 対象3カテゴリの JSON のうち **クラス名（javadocリンク）を1件以上含むページ** が classes.md の `path:` エントリに存在することを照合
  - クラス名ゼロのページは classes.md 非掲載が正なので、coverage 対象から除外（FAILにしない）
  - `no_knowledge_content: true` はスキップ、`javadoc/` `assets/` もスキップ
  - 対象3カテゴリ以外は照合対象外
**Steps:**
- [ ] `verify.py` に `check_classes_coverage()` を追加
- [ ] `pytest tools/rbkc/tests/ut/test_verify.py -x` が GREEN になることを確認
- [ ] コミット・プッシュ

### Task 6: 実装 — `run.py` に classes.md 生成・verify を統合
**Artifact**: `tools/rbkc/scripts/run.py`
**Contents**:
- `from scripts.create.classes import generate_classes_md` を追加
- `from scripts.verify.verify import ... check_classes_coverage` を追加
**Steps:**
- [ ] `create()` 内 264行 `generate_index_md(output_dir, output_dir / "index.md")` の直後に `generate_classes_md(output_dir, output_dir / "classes.md")` を追加
- [ ] `update()` 内 315行 `generate_index_md(...)` の直後に同様に追加
- [ ] `delete()` 内 357行 `generate_index_md(...)` の直後に同様に追加
- [ ] `verify()` 内 444行 `check_index_coverage` ループの直後に `check_classes_coverage(output_dir, output_dir / "classes.md")` のループを追加（`files is None` の場合のみ）
- [ ] `pytest tools/rbkc/tests/ -x` が全 pass であることを確認
- [ ] コミット・プッシュ

### Task 7: RBKC 実行 — v6 の classes.md を生成
**Steps:**
- [ ] `bash tools/rbkc/rbkc.sh create v6` を実行
- [ ] `bash tools/rbkc/rbkc.sh verify v6` で FAIL 0 を確認
- [ ] `.claude/skills/nabledge-6/knowledge/classes.md` が生成されていることを確認
- [ ] `Jackson2BodyConverter` が classes.md に含まれることを確認
- [ ] コミット・プッシュ

### Task 8: semantic-search.md を更新 — classes.md をページ選択(Step 2)に組み込む

**Artifact**: `.claude/skills/nabledge-6/workflows/semantic-search.md`
**Design note**: Step 4 (Augment with referenced Javadoc) は変更しない。Step 2 がページを選べば Step 4 が当該 Javadoc を補強する（相補関係、機能重複ではない）。

**重要 — バージョン差分**: semantic-search.md は全バージョン同一ではない（v6基準で v5 は2行差、v1.4/1.3/1.2 は32行差）。**共通パッチ前提で適用しない。各バージョンで Step 1 / Step 2 の実テキストを確認してから個別に当てる。** 下記 Before は v6 のもの。

#### パッチ1: Step 1 に classes.md 読込を追加
**Before:**
```
## Step 1: Read index.md

Read `knowledge/index.md` (relative to skill root). Save content as `index_content`.
```
**After:**
```
## Step 1: Read index.md and classes.md

Read `knowledge/index.md` (relative to skill root). Save content as `index_content`.
Read `knowledge/classes.md` (relative to skill root). Save content as `classes_content`.
If `classes.md` does not exist (older versions), set `classes_content` to empty and skip the classes.md step in Step 2.
```

#### パッチ2: Step 2 手順3の直後に手順3bを挿入（index候補と同列でマージ）
**Before（手順3の末尾行）:**
```
   - All other pages → **skip**
4. If a purpose was noted, sort candidates using the priority categories for that purpose: pages in the priority categories come first.
```
**After:**
```
   - All other pages → **skip**
3b. Scan `classes_content`. For each page block, if any class name listed in that block matches a class name or feature name appearing in the question, add that page to candidates (same status as a Step 3 candidate). Deduplicate against candidates already collected in Step 3.
4. If a purpose was noted, sort the merged candidate set (Step 3 + Step 3b) using the priority categories for that purpose: pages in the priority categories come first. Apply the sort once, to the merged set.
```

#### パッチ3: 手順5のトリム規則に classes.md 由来の保護を追加
**Before:**
```
5. Take up to 10 candidates in order. If fewer than 3 candidates exist, do not pad. If no candidates exist, return `{"selected_sections": []}` immediately.
```
**After:**
```
5. Take up to 10 candidates in order. If fewer than 3 candidates exist, do not pad. If no candidates exist, return `{"selected_sections": []}` immediately. When trimming to 10, if a candidate was added in Step 3b because its class name explicitly appears in the question, keep it ahead of index-only candidates that merely match by topic.
```

**Steps:**
- [ ] v6 に パッチ1〜3 を適用
- [ ] v5 の Step 1 / Step 2 実テキストを確認し、差分(2行)を踏まえてパッチ1〜3を適用
- [ ] v1.4 / v1.3 / v1.2 の Step 1 / Step 2 実テキストを確認（32行差あり）、各々の表現に合わせてパッチ1〜3を適用。Before が一致しない場合は当該バージョンの実テキストを Before として記録してから適用する
- [ ] 全バージョンで Step 4 が無変更であることを確認
- [ ] 変更差分を作業記録に出力しユーザーに確認
- [ ] コミット・プッシュ

### Task 9: ベンチマーク実行 — qa-05 pass と全体回帰確認
**Steps:**
- [ ] qa-05 シングル実行でクラス名が選択・回答に含まれることを確認
  - `bash tools/rbkc/rbkc.sh verify v6` で FAIL 0 確認後
  - **qa-05 で対象ページ (`adapters-jaxrs-adaptor`) が選択されなかった場合**: Step 2 の10件トリムで押し出された可能性を調査（選択候補数とソート順を確認）。押し出しが原因なら Task 8 パッチ3 の優先規則を強化（classes.md 由来の質問内クラス名一致候補を上位固定）し、Task 8 を再コミット
- [ ] HOW-TO-RUN.md の手順に従い全ベンチマーク実行
- [ ] 結果を `.work/00368/benchmark-results.md` に記録
- [ ] ベースラインと比較して regression なし (≥ 95.9%) を確認

### Task 10: 全バージョン RBKC 展開 (v5/v1.4/v1.3/v1.2)
**Steps:**
- [ ] 各バージョンで `bash tools/rbkc/rbkc.sh create <v> && bash tools/rbkc/rbkc.sh verify <v>` を実行
  - v5: 対象カテゴリ有無を確認、classes.md 生成を確認
  - v1.4 / v1.3 / v1.2: 対象カテゴリ有無を確認、classes.md 生成を確認
- [ ] 全バージョン FAIL 0 を確認
- [ ] コミット・プッシュ (生成された classes.md ファイルを含む)

## Done

- [x] Task 0: タスクリスト作成・PR作成・ユーザー確認 — committed `b312d3adb`
