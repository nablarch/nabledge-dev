# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-11 (rev17)

## In Progress

（なし）

## Not Started

### Task 19: Bug 1 修正 — label_map lookup の case normalization
**原因**: docutils が target node の `names[]` を小文字正規化するが、
`rst_ast_visitor.py` / `verify.py` の `label_map.get()` は RST 元の大文字混じりキーで検索するため、大文字を含むラベル（`NablarchServletContextListener`、`guide_appendix_windowScope`、`SqlLog` 等）がヒットせず UNRESOLVED → 平文フォールバック

**Steps:**
- [ ] TDD: `test_labels.py` に case-insensitive lookup のテスト追加 → RED
- [ ] `rst_ast_visitor.py`: `:ref:` / `:numref:` の `label_map.get(target_label)` を `label_map.get(target_label.lower())` に変更（`_find_label_target` も同様）
- [ ] `verify.py check_source_links()`: `label_map.get(label)` を `label_map.get(label.lower())` に変更
- [ ] GREEN 確認
- [ ] **即時差分確認**: 全5バージョン再生成（`bash rbkc.sh create <v>`）→ `git diff main` でリンク変化を確認
  - 起点は main（バグ修正前の正常状態）。再生成後の差分 = このブランチで意図した変化のみ
  - 平文だったラベルが MD リンクに戻っている行が増えているか
  - `git diff main | grep '^-.*\[' | grep -v '^\-\-\-'` で「リンク削除」がないことを確認
- [ ] 全5バージョン verify FAIL diff 確認

### Task 20: Bug 2 修正 — `_next_section_for_node` の多段 climb
**原因**: `_next_section_for_node` はセクション境界を1段しか遡らない（`is_last_meaningful` の grandparent 探索は1レベルのみ）。深いネスト末尾のラベル（例: `sql-gaibuka-label` が h4 内末尾 → 2段上の h3 を参照）で失敗し、`_enclosing_section_title_for_node` にフォールバック → 誤った section title（`処理概要`）を返す

**Steps:**
- [ ] TDD: 多段ネストのラベル解決テストを追加 → RED
- [ ] `labels.py`: `_next_section_for_node` を iterative multi-level climb に書き換え（段数制限なし、document root で停止）
- [ ] GREEN 確認
- [ ] **即時差分確認**: 全5バージョン再生成（`bash rbkc.sh create <v>`）→ `git diff main` でリンク変化を確認
  - `sql-gaibuka-label` 等が正しいセクション（`推奨するJavaの実装例...`）へのリンクになっているか
  - `git diff main | grep '^-.*\[' | grep -v '^\-\-\-'` で「リンク削除」がないことを確認
- [ ] 全5バージョン verify FAIL diff 確認

### Task 21: Bug 3 修正 — `check_ql1_link_targets` の anchor 検証未実装
**原因**: Issue #320 の本来の目的「ページ内リンクの anchor が意図した heading を指すか」が
MD リンク出力側（`check_ql1_link_targets`）で検証されていない。
`_collect_links()` は anchor を取得しているが `_anchor` として捨てており、
ファイル存在チェックしか行っていない。`処理概要` のような誤アンカーも PASS してしまう。

**修正内容**:
- `seen` dedup を `(type, category, file_id)` → `(type, category, file_id, anchor)` に変更
  （anchor が違えば別チェック対象）
- anchor が空でない場合、`_heading_slugs_from_md` で docs MD の heading slug 照合を追加
  （`_heading_slugs_from_md` はすでに verify.py にモジュールレベルで存在）
- JSON side と docs MD side の両方に適用

**Steps:**
- [ ] TDD: `check_ql1_link_targets` に anchor 検証のテスト追加 → RED
- [ ] `verify.py`: `seen` を `(type, category, file_id, anchor)` に変更し、anchor 非空時に slug 照合を追加
- [ ] GREEN 確認 → 全5バージョン verify FAIL diff 確認（新規 FAIL が出た場合は RBKC バグとして Task 19/20 で対処）

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
