# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev5)

## In Progress

### Task 17: `_scan_rst_labels` を docutils AST ベースに置き換え

**調査結果（事実）:**
- v6 FAIL 701件 = すべて QL1
  - 692件: `section_title not found in sections[]`（JSON side）
  - 9件: `anchor` 不一致（docs MD side）
- **共通の根本原因**: `_scan_rst_labels` の自作行スキャンが docutils 準拠でない
  - `_is_heading_underline` は「全文字が HEADING_CHARS」でチェックするが、docutils は**同一文字の繰り返し**を要求
  - これにより `-->` (JSP コメント終端) や `}` (Java コード) を heading underline として誤認
  - `tag-double_submission_server_side` 等9件: 誤認 heading から誤った `title`/`anchor` が生成される → create 側リンクも壊れている
  - `universal_dao` 等692件: h1 直前ラベルは docutils AST では `parent=document` → `section_title=""` が正しいが、自作スキャンは enclosing section title を返す
- **修正方針**: `_scan_rst_labels` を廃止し docutils AST (`rst_ast.parse`) で実装し直す
  - `nodes.target` を走査、`parent` が `nodes.document` → `section_title=""`、`nodes.section` → enclosing section の title
  - docutils は既に依存に含まれており、他の RST 解析箇所（`verify.py`、`rst_ast_visitor.py`）は全て docutils AST を使用済み

**Steps:**
- [x] TDD: `_scan_rst_labels` の docutils AST ベース実装に対するテスト追加（RED）
- [x] `_scan_rst_labels` を docutils AST ベースに書き直し（GREEN） — `51381d507`
- [x] 全テスト PASS 確認（514 tests passed）
- [x] インプット→アウトプット確認（JSON/MD 両方）:
  - `universal_dao`（h1ラベル）: `section_title=""`, `title="ユニバーサルDAO"` ✅, MD アンカー実在 ✅
  - `tag-double_submission_server_side`（-->誤認ケース）: `section_title="二重サブミットを防ぐ"` ✅, MD アンカー実在 ✅
  - 元々 PASS していた h2 ラベル（`universal_dao-sql_file`）: JSON section 実在 ✅, MD アンカー実在 ✅
- [ ] v1.4 残り2 FAIL 修正 — RBKC create バグ（`SampleApplicationExtension.rst` の h2 が `sections[]` に出ない）
  - FAIL: `customize_flow_proceed_condition` → `section_title='進行先ノードの判定制御ロジックの実装'` が JSON sections[] に存在しない
  - 原因: RBKC create が h1+h2 1つだけの RST ファイルで h2 を `sections[]` に出力せず、title に「h1 — h2」として折り畳む
  - 修正方針: create 側コードを特定して修正（未着手）
- [ ] 全5バージョン verify 実行、FAIL diff 確認（全バージョン0 FAIL になること）
- [x] 設計書整合確認・修正 — `f453cdf78`
  - §3-2-1: LabelTarget フィールド定義更新（type/anchor 追加、section_title h1空文字仕様明記、build_label_doc_map シグネチャ修正）
  - §3-2-3: 経緯記述を削除し現在の実装仕様のみ記述
  - §4 QL1 ノート: 現状のみ記述（履歴・タスク参照を除去）
- [ ] Expert review（Software Engineer + QA Engineer）
- [ ] 設計書 §4 マトリクス QL1 を ✅ に更新（全バージョン 0 FAIL かつ Expert review 通過後）
- [ ] PR 最終確認（Success Criteria チェック）

**現在の FAIL カウント（Task 17 実装後）:**
| Version | Task16後 | Task17後 | 残り |
|---------|---------|---------|------|
| v6      | 701     | 0       | 0 ✅ |
| v5      | 688     | 0       | 0 ✅ |
| v1.4    | 125     | 2       | 2 ❌ |
| v1.3    | 113     | 0       | 0 ✅ |
| v1.2    | 126     | 0       | 0 ✅ |

**v1.4 残り2 FAIL 詳細:**
```
FAIL SampleApplicationDesign.rst: QL1 :ref:`customize_flow_proceed_condition`
  section_title '進行先ノードの判定制御ロジックの実装' not found in
  workflow-SampleApplicationExtension.json sections[]
FAIL SampleApplicationDesign.rst: QL1 :ref:`customize_flow_proceed_condition`
  anchor '進行先ノードの判定制御ロジックの実装' not found in
  workflow-SampleApplicationExtension.md headings
```
- RST: h1「ゲートウェイの進行先ノード判定ロジックを変更する方法」+ h2「進行先ノードの判定制御ロジックの実装」
- labels.py は正しく `section_title='進行先ノードの判定制御ロジックの実装'` を返す（新旧両方）
- JSON: `sections[]` が空、`title` が「h1 — h2」で結合されている
- MD: h2 が独立した `##` 見出しでなくファイルタイトルに折り畳まれている
- Task 16 後の 125 FAIL に含まれていた既存 RBKC create バグ（labels.py 変更とは無関係）
- RBKC create 側で単一 h2 ファイルの扱いを修正する必要あり

### Task 16: 実装（完了）

**Steps（完了済み）:**
- [x] TDD: `TestCheckSourceLinks_JsonSide` テスト追加（RED）
- [x] `verify.py` — `_section_titles_from_json()` + cross-doc JSON side 実装（GREEN）
- [x] TDD: `TestCheckSourceLinks_DocsMdSide` テスト追加（RED）
- [x] `verify.py` — `_heading_slugs_from_md()` + cross-doc docs MD side 実装（GREEN）
- [x] `run.py` に `knowledge_dir`, `docs_dir` 引数追加
- [x] 全5バージョン verify 実行、FAIL diff 確認・記録（v6:683, v5:688, v1.4:125, v1.3:113, v1.2:126）
- [x] Expert review (Software Engineer + QA Engineer) — SE: 1 Finding fixed（json_key dedup バグ）, QA: 0 Findings
- [x] 設計書 §4 マトリクス QL1 状態ノート追加（⚠️ 維持 — 条件3: RBKC fix 未完）
- [x] CHANGELOG 更新不要（verify 内部改善、エンドユーザー向け変化なし）

## Not Started

### Task 18: 横並びチェック — docutils を使わない RST 構造解析が他にないか

**背景:**
- `_scan_rst_labels` の自作行スキャンが今回の問題の原因
- 同様の問題が他にないか確認し、あれば修正する
- **調査済みの事実（本タスク着手不要の確認済み箇所）:**
  - `verify.py` の `check_source_links` / `check_external_urls` → docutils AST 使用済み ✅
  - `rst_ast_visitor.py` → docutils AST を基盤とする設計 ✅
  - `verify.py` の `_RST_HEADING_UNDERLINE_RE` (QC5) → 目的が「RST 残存チェック」であり構造解析ではない（docutils 不要）✅
  - `_scan_rst_labels` → Task 17 で修正済み ✅

**Steps:**
- [ ] `scripts/` 全体を grep して、RST ファイルを読み込んで自作 regex / 行スキャンで構造（heading / label / section）を解析している箇所を列挙
- [ ] 各箇所について「docutils AST で代替すべきか」を判断
- [ ] 要修正箇所があれば TDD で修正
- [ ] 要修正なければ「なし」と記録して完了

### Task 19: PR 最終確認・マージ

**Steps:**
- [ ] PR #330 の Success Criteria チェック
- [ ] PR 更新（Expert Review リンク追加）

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
  - リバート理由: verify が「リンク先存在チェック」のみで「意図したリンクか」を検証しておらず、
    RBKC の heading 修正が正しいリンクを壊しても FAIL しなかった
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
