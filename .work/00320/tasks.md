# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-13 (rev30)

## In Progress

（なし）

## Not Started

### Task 24: QL1 アンカー → Markdown 見出し変換の影響調査
**背景**: RST に直接アンカー（`.. _label:`）が付いたノードは Markdown に変換すると見出しがなく、リンク先が親見出し全体になる（精度損失）。  
`libraries-01-FailureLog.md:582` の `#クラス定義` リンクはその典型例。

**調査項目**:
- [ ] 全5バージョン（v6/v5/v1.4/v1.3/v1.2）で「RST アンカーが見出し以外のノード（箇条書き・テーブル行・plain paragraph 等）に付いているケース」を列挙
- [ ] 同一 RST ファイル内で同階層のリストアイテムに複数アンカーが付いているケース（a)〜e) 形式等）を特定
- [ ] 見出し化するなら「アンカーのある行だけ」か「同階層の全アイテム」かを判断
- [ ] 実現可能性の評価（RBKC 生成側の変更コスト、生成物の品質への影響）
- [ ] 全バージョン・全影響ファイル数を定量化

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
