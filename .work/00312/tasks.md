---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: #315
**Issue**: #312
**Updated**: 2026-04-28

## In Progress

### 2. Prototype: fix bugs and extend to full columns

**Bugs found in prototype review (user feedback):**
1. **Bug 1** — `handler_structure_bg.png` / `handler_bg.png` が先頭に出る
   → 原因: `link.rst` の `.. image::` ブロック（Block 1/3 とは無関係）。image node は現行の `visit_image` で出力されている。handler RST ファイル先頭の `.. include:: ../api/link.rst` 経由で挿入される。これらは height/width=0 の不可視画像なので出力を抑制すべき。
   → 修正方針: `link.rst` の image node は alt なし・uri のみ・不可視フラグ (`height: 0`) → `visit_image` で抑制ルールを追加する、または visit_raw の Block 1 検出前にこれらが出力されないよう確認

2. **Bug 2** — ハンドラ処理概要テーブルが空
   → 原因: Block 3 検出で `node.source` は RST ファイルパスを返し `:file:` パスを返さない。Block 2 後の次の raw node を Block 3 とみなすよう修正が必要。

3. **設計拡張** — テーブルにクラス名（package + key）・入力型・結果型を追加
   → Handler.js の `package` フィールドと `type.argument/returns`（Api オブジェクト参照）を解析して出力
   → `parse_api_dict` を新規追加、`parse_handler_dict` を拡張

**Steps:**
- [x] TDD: write unit tests for `handler_js.py` (RED) — `224c2a669`
- [x] Implement `handler_js.py` (GREEN) — `224c2a669`
- [x] Write converter unit tests for `visit_raw` 3-block state machine (RED) — `224c2a669`
- [x] Implement `visit_raw` fix (GREEN) — `224c2a669`
- [x] Fix ハンドラ処理フロー blank-line loss in `visit_definition_list` — `224c2a669`
- [x] Run prototype, push `.work/00312/prototype-*.md` — `224c2a669`
- [x] Update design doc and tasks.md with bugs and extension
- [x] Fix Bug 1: `visit_image` で height/width=0（文字列含む）の不可視画像を抑制
- [x] Fix Bug 2: Block 3 検出を source path ベースに変更、Block 3 を Block 2 より先に評価
- [x] Fix `</br/>` タグ（Handler.js の誤記）も `_BR_RE` で処理
- [x] Fix duplicate `**ハンドラ処理概要**`: preamble を render_handler_table から削除
- [x] Extend: `parse_api_dict` 追加 + `parse_handler_dict` に package/type 追加
- [x] Extend: `render_handler_table` にクラス名・入力型・結果型列を追加
- [x] Update unit tests for all changes (RED → GREEN) — 423 passed
- [x] Re-run prototype: `python -m scripts.run create 1.4`、`.work/00312/prototype-*.md` を更新
- [x] セルフチェック完了 → 残課題あり（下記 Bug 3）

**Bug 3（セルフチェックで発見）** — 先頭空行2行
- 原因: `docs.py` の `lines = [f"# {title}" if title else "", ""]` で title が空のとき先頭が `""` になる。修正前は link.rst 由来の不可視画像MDが先頭にあり目立たなかったが、Bug 1 修正（画像抑制）で空行が露出。
- 修正方針: `docs.py` で title が空のとき先頭の `""` を出力しない（`if title` ガード）。
- 影響範囲: link.rst を include する v1.x ファイル 98 件（全バージョン共通コードなので共有）

### 2b. Bug 3 fix: 先頭空行除去

**Steps:**
- [ ] TDD: write test for leading blank line suppression in docs.py (RED)
- [ ] Fix `docs.py`: suppress leading empty line when title is empty (GREEN)
- [ ] Re-run prototype: `python -m scripts.run create 1.4`、`.work/00312/prototype-*.md` を更新してプッシュ
- [ ] [DECISION: ユーザー確認] 再生成 MD 確認 → OK なら Task 3 へ

### 3. Full implementation (after prototype approval)
**Steps:**
- [ ] Run `python -m scripts.run create <v> && bash rbkc.sh verify <v>` for all 5 versions (before/after)
- [ ] Confirm FAIL count diff is as expected
- [ ] Horizontal check: `.. raw:: html` + `:file:` across all 5 versions
- [ ] Write post-mortem at `.work/00312/postmortem-handler-raw-html.md`

## Not Started

### 4. PR
**Steps:**
- [ ] Expert review
- [ ] Create PR

## Done

- [x] Issue #312 fetched and branch `312-fix-handler-docs-raw-html` created
- [x] RBKC conversion code identified: `rst_ast_visitor.py:visit_raw` + `rst_ast.py:normalise_raw_html`
- [x] Verify QC5 pattern confirmed: `<[a-zA-Z][a-zA-Z0-9]*...>` already detects opening tags
- [x] Blank-line loss root cause: `visit_definition_list` が全アイテムを `"\n".join` で結合している
- [x] Design approved and implemented (prototype) — `224c2a669`
- [x] Task 1: Investigate and design — completed
