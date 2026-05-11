# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev20)

## In Progress

（なし）

## Not Started

### Task 22: 横並びチェック・再生成・差分確認・PR 更新
**Steps:**
- [ ] 横並びチェック: 同クラスのバグが他バージョン / 他ファイルに残っていないか確認
- [ ] 全5バージョン再生成（`bash rbkc.sh create <v>`）
- [ ] **差分確認**: `git diff main` で全リンク変化を確認（起点は main）
  - `git diff main | grep '^-.*\[' | grep -v '^\-\-\-'` でリンク削除行がゼロであることを確認
  - Task 19/20 で期待した改善（平文 → MDリンク）が含まれているかサンプル確認
- [ ] 全5バージョン verify（`bash rbkc.sh verify <v>`）、0 FAIL 確認
- [ ] エキスパートレビュー（SE + QA）実施
- [ ] PR #330 更新（Success Criteria・Expert Review 更新）

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
  - リバート理由: verify が「リンク先存在チェック」のみで「意図したリンクか」を検証しておらず、
    RBKC の heading 修正が正しいリンクを壊しても FAIL しなかった
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
- [x] Task 16: verify check_source_links() cross-doc 実装 — SE: 1 Finding fixed, QA: 0 Findings
- [x] Task 17: `_scan_rst_labels` docutils AST 化 + subtitle sections[0] 修正 — 全5バージョン 0 FAIL、SE: 0 Findings、QA: 2 Findings fixed
- [x] Task 17 完了: 設計書 §4 QL1 マトリクス ✅、PR #330 Success Criteria 全4項目 ✅ Met
- [x] 設計書 P2-4 記述を復元 — ブランチ分岐点が #327 マージ前だったため消えていた — `21fd36c59`
- [x] Task 18: 横並びチェック完了 — docutils 不使用の RST 構造解析なし（修正不要）
- [x] 最終エキスパートレビュー完了 — SE: 0 Findings、QA: 0 Findings — PR #330 Expert Review 更新済み — `f9b694bf5`
- [x] Task 19: Bug 1 修正 — label_map lookup の case normalization — `rst_ast_visitor.py` / `verify.py` に `.lower()` 追加、全5バージョン 0 FAIL
- [x] Task 20: Bug 2 修正 — `_next_section_for_node` の multi-level climb — iterative climb 実装（document root で停止）、全5バージョン 0 FAIL
- [x] Task 21: Bug 3 修正 — `check_ql1_link_targets` の anchor 検証実装 — `seen` を4-tuple 化、anchor 非空時に `_heading_slugs_from_md` で slug 照合、JSON side + docs MD side 両方に適用、全5バージョン 0 FAIL
