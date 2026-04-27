---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: #315
**Issue**: #312
**Updated**: 2026-04-28

## In Progress

### 1. Investigate and design readable state
**Steps:**
- [x] Read affected MD file (e.g. handlers-PermissionCheckHandler.md) — confirmed `<script>` leak
- [x] Read corresponding RST source — found 3x `.. raw:: html` blocks (Handler.js, inline script, handler_structure.html)
- [x] Identify RBKC conversion code — `rst_ast_visitor.py visit_raw` → `normalise_raw_html` in `rst_ast.py`
- [x] Read verify design spec (`rbkc-verify-quality-design.md`) — QC1-QC4 = sequential-delete, QC5 = regex
- [x] Analyze knowledge value: Handler.js `behavior.inbound/outbound/error/callback` = 実データ（日本語説明文）
- [x] Study top 3 complex handlers: MessageResendHandler(5), RetryHandler(4), RequestThreadLoopHandler(3)
- [x] Decide output approach: **Case A** — parse Handler.js, render Markdown table per HandlerQueue
- [x] Agree on architecture: `scripts/common/handler_js.py` 共通モジュール (create + verify 両側から利用)
- [x] Create design doc at `tools/rbkc/docs/rbkc-handler-v1x-design.md`
- [x] Propose fix for ハンドラ処理フロー blank-line loss (definition_list間の改行)
- [ ] Present full design to user and get approval

**Agreed design (this session):**
- 共通モジュール `scripts/common/handler_js.py` に3関数:
  - `parse_handler_dict(js_text)` → `{ HandlerName → {name, behavior: {inbound, outbound, error, callback}} }`
  - `parse_handler_queue(script_text)` → `(Context, [HandlerName, ...])`
  - `render_handler_table(handler_dict, context, queue)` → Markdown テーブル文字列
- create の `visit_raw`: 3ブロック状態機械で呼ぶ
- verify の normalizer: 同じ `raw` ノードで呼んで正規化ソースに含める → QC1-QC4 sequential-delete がそのまま機能
- verify は Handler.js を独立ロードしない（§2-2 独立性原則: common モジュール経由でよい）
- `handler_js.py` のユニットテスト: 文字列連結、`<br/>`変換、`-`値、callbackあり/なし、サフィックス付きキー

### 2. Prototype: verify output with 3 complex handlers (after design approval)

対象: MessageResendHandler (5), RetryHandler (4), RequestThreadLoopHandler (3) — HandlerQueue 数が多い上位3ファイル

**Steps:**
- [ ] TDD: write unit tests for `handler_js.py` (RED)
- [ ] Implement `handler_js.py` (GREEN)
- [ ] Write converter unit tests for `visit_raw` 3-block state machine (RED)
- [ ] Implement `visit_raw` fix (GREEN)
- [ ] Fix ハンドラ処理フロー blank-line loss in `visit_definition_list`
- [ ] Run `bash rbkc.sh create v1.4` for v1.4 only (prototype scope)
- [ ] Output 3 target docs files to `.tmp/handler-prototype/` for user review
- [ ] [DECISION: ユーザー確認] 生成 MD の内容・フォーマットを確認 → OK なら Task 3 へ

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
