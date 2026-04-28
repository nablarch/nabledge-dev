# Tasks: fix: toctree entries rendered as plain text in docs MD instead of links

**PR**: TBD
**Issue**: #317
**Updated**: 2026-04-28

## Not Started

### Task 1: 調査 — toctreeエントリの現在の変換フローを把握する
**Steps:**
- [ ] application_framework/index.rst など純粋toctreeページのJSONを確認し、現状の`content`フィールドを把握する
- [ ] RBKCでtoctreeがどう処理されるかをrst_ast.py / rst_ast_visitor.py / rst.py / docs.pyで追跡する
- [ ] `no_knowledge_content`の判定ロジックを確認する
- [ ] 全バージョン（v6/v5/v1.4/v1.3/v1.2）のtoctree-indexファイルの傾向を調査する

### Task 2: 設計 — toctreeエントリのリンク変換方針を設計書・verify設計書に反映する（ユーザー確認必須）
**Steps:**
- [ ] toctreeエントリをMDリンクに変換する方針を設計する（`no_knowledge_content`設定 vs リンク変換）
- [ ] rbkc-converter-design.md の toctree 対応表エントリを更新する（変更前にユーザー確認）
- [ ] rbkc-verify-quality-design.md に必要な verify 変更があれば記載する（変更前にユーザー確認）
- [ ] ユーザーに設計を提示して承認を得る

### Task 3: 試し変換 — 閲覧用MDの見栄えを確認する（ユーザー確認必須）
**Steps:**
- [ ] 設計承認後、最小限の試験実装を行い v6 の代表的 index ファイルを変換する
- [ ] 生成された docs MD をコミット・プッシュしてユーザーに見栄えを確認してもらう
- [ ] フィードバックを受けて設計を調整する（必要に応じて）

### Task 4: 実装 — verify に新チェックを追加する（TDD: RED）
**Steps:**
- [ ] toctreeエントリがMDリンクとして docs MD / JSON に出力されることを検証する unit test を書く（RED確認）
- [ ] `no_knowledge_content`判定の修正が必要な場合はそのテストも書く

### Task 5: 実装 — RBKCコンバーターを修正する（TDD: GREEN）
**Steps:**
- [ ] rst_ast_visitor.py の toctree (container) ノード処理を修正し、子エントリをMDリンクに変換する
- [ ] `no_knowledge_content`の判定ロジックを修正する（必要に応じて）
- [ ] verify テストがGREENになることを確認する
- [ ] 全バージョン（v6/v5/v1.4/v1.3/v1.2）で create + verify を実行して FAIL 件数を比較する

### Task 6: 横断確認 — 全バージョンで verify FAIL 0 件を確認する
**Steps:**
- [ ] v6 で `bash rbkc.sh create v6 && bash rbkc.sh verify v6` を実行
- [ ] v5, v1.4, v1.3, v1.2 でも同様に実行
- [ ] FAIL件数の変化を記録して `.work/00317/notes.md` に出力する

### Task 7: 変更差分チェック — PRの変更差分が想定通りかを確認する（ユーザー確認必須）
**Steps:**
- [ ] `git diff main...HEAD` を確認して想定外の変更が含まれていないかチェックする
- [ ] 結果を `.work/00317/diff-check.md` に出力する
- [ ] ユーザーに確認を依頼する

### Task 8: PR作成
**Steps:**
- [ ] `/pr create` でPRを作成する

## In Progress

## Done
