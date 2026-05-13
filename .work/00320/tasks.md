# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-13 (rev32)

## In Progress

（なし）

## Not Started

### Task 25: 非見出しアンカー → 合成見出し生成の実装

**方針（ユーザー承認済み）**:
- Option B: `_walk_section` で非見出しアンカー直後の paragraph を合成セクションとして分割し、JSON sections[] にも追加する
- docs MD の見出し増加は人の閲覧にもポジティブ（原文の意図を正確に反映）
- verify は変更不要 — 既存の anchor/section_title チェックが自動検証

**事前確認が必要なケース**:
- `フローを表示` アンカー (`**標準ハンドラ構成** (説明文をクリックすると...)`) — JavaScript 用アンカーで静的 MD では意味が薄い見出し。当該ファイルが knowledge file の対象かどうか確認してから着手

**実装箇所**:
1. `tools/rbkc/scripts/common/labels.py` — `_scan_rst_labels`: アンカー直後ノードが paragraph の場合、テキストを `title` に採用（bold剥がし・italic剥がし・plain-text）
2. `tools/rbkc/scripts/common/rst_ast_visitor.py` — `_walk_section`: アンカー+paragraph ペアを合成セクションとして分割

**paragraph テキスト → 見出しテキスト変換ルール**:
- `**テキスト**` (bold-only) → `テキスト`（bold マーカー除去）
- `*テキスト*` (italic) → `テキスト`（italic マーカー除去）
- `**テキスト**：その他` (bold-start) → `テキスト`（bold部分のみ抽出）
- plain-text → そのまま
- `|` (table-continuation, 6件) → 変換不可、親見出しフォールバック維持

**Steps:**
- [DECISION: `フローを表示` 系アンカーが付くファイルが knowledge file 対象か確認し、対象なら合成見出し化、対象外ならスキップ] Step 0
- [ ] Step 1: `_scan_rst_labels` に非見出し paragraph テキスト採用ロジック追加 (TDD)
- [ ] Step 2: `_walk_section` に合成セクション分割ロジック追加
- [ ] Step 3: 全5バージョン verify FAIL 0 確認
- [ ] Step 4: SE + QA エキスパートレビュー
- [ ] Step 5: 再生成・差分確認・PR 更新

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
- [x] Task 16: verify check_source_links() cross-doc 実装 — SE: 1 Finding fixed, QA: 0 Findings
- [x] Task 17: `_scan_rst_labels` docutils AST 化 + subtitle sections[0] 修正 — 全5バージョン 0 FAIL
- [x] 設計書 P2-4 記述を復元 — `21fd36c59`
- [x] Task 18: 横並びチェック完了
- [x] 最終エキスパートレビュー完了 — SE: 0 Findings、QA: 0 Findings — `f9b694bf5`
- [x] Task 19: Bug 1 修正 — label_map lookup の case normalization — 全5バージョン 0 FAIL
- [x] Task 20: Bug 2 修正 — `_next_section_for_node` multi-level climb — 全5バージョン 0 FAIL
- [x] Task 21: Bug 3 修正 — anchor 検証実装 — 全5バージョン 0 FAIL — SE: 1 Finding fixed, QA: 2 Findings fixed
- [x] Task 22: 横並びチェック・再生成・差分確認・PR 更新 — 全5バージョン 0 FAIL
- [x] PR #330 レビューFB対応 — コメント4件処理済み `21e4b8fec`
  - #3217245104: `#特殊なリクエスト処理`（手動編集、後に Task 23 で RBKC 修正に置換）
- [x] Task 23: `21e4b8fec` を RBKC create 側修正に置換 — `8d7769977`
  - `_next_section_for_node` で `transition` ノードをスキップして次の section を探すよう修正
  - v1.2/v1.3/v1.4 の `RequestPathJavaPackageMapping` リンク先 → `#リクエストの識別と業務処理の実行`
  - 設計書 §3-2-2 にルール5として transition スキップルールを追記
  - 全5バージョン FAIL 0、532 tests passed
  - PR #330 コメント #3217245104 に返信済み
- [x] Task 24: QL1 アンカー → 非見出しノード調査完了 — 全5バージョン 1,126 非見出しアンカー特定、notes.md に記録
