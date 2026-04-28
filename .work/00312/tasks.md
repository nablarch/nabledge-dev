---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: #315
**Issue**: #312
**Updated**: 2026-04-28

## In Progress

### 2. Prototype: fix bugs found in review

対象: MessageResendHandler (5), RetryHandler (4), RequestThreadLoopHandler (3) — HandlerQueue 数が多い上位3ファイル

**Bugs found in prototype review (user feedback):**
1. `handler_structure_bg.png` / `handler_bg.png` の画像参照が先頭に出る → Block 1/3 の `:file:` が image nodeとして別出力されている（要調査・除去）
2. **ハンドラ処理概要** タイトルは出るがテーブルが空 → Block 3 検出ロジックのバグ: `node.source` は RST ファイルパスを返し `:file:` パスを返さない。Block 2 → Block 3 の連携が機能していない（`script_text` が未セットのまま Block 3 に到達）

**Steps:**
- [x] TDD: write unit tests for `handler_js.py` (RED) — committed `224c2a669`
- [x] Implement `handler_js.py` (GREEN) — committed `224c2a669`
- [x] Write converter unit tests for `visit_raw` 3-block state machine (RED) — committed `224c2a669`
- [x] Implement `visit_raw` fix (GREEN) — committed `224c2a669`
- [x] Fix ハンドラ処理フロー blank-line loss in `visit_definition_list` — committed `224c2a669`
- [x] Run `bash rbkc.sh create 1.4` for v1.4 only (prototype scope)
- [x] Output 3 target docs files to `.work/00312/prototype-*.md` for user review — committed `224c2a669`
- [ ] Fix Bug 1: `handler_structure_bg.png` / `handler_bg.png` 画像参照を除去（`:file:` が image として別出力される経路を調査）
- [ ] Fix Bug 2: Block 3 検出ロジック修正 — `node.source` は RST パス。検出方法を再設計（Block 2 後にカウンタで Block 3 を判定、または Block 2 の次の raw を Block 3 とみなす）
- [ ] Re-run prototype after fixes and push updated `.work/00312/prototype-*.md`
- [ ] [DECISION: ユーザー確認] 再生成 MD の確認 → OK なら Task 3 へ

### 3. Full implementation (after prototype approval)
**Steps:**
- [ ] Write verify normalizer tests for `raw` node handling (RED)
- [ ] Implement verify normalizer change (GREEN)
- [ ] Run `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` for all 5 versions (before/after)
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
- [x] Design approved: `handler_js.py` + 3-block state machine — `224c2a669`
- [x] Task 1: Investigate and design — completed
