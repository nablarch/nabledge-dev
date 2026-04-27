---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: TBD
**Issue**: #312
**Updated**: 2026-04-27

## In Progress

### 1. Investigate current structure and propose readable state
**Steps:**
- [x] Read affected MD file (e.g. handlers-PermissionCheckHandler.md) — confirmed `<script>` leak
- [x] Read corresponding RST source — found 3x `.. raw:: html` blocks (Handler.js, inline script, handler_structure.html)
- [x] Identify RBKC conversion code — `rst_ast_visitor.py visit_raw` → `normalise_raw_html` in `rst_ast.py`
- [x] Read verify design spec (`rbkc-verify-quality-design.md`) — QC5 already covers `<[a-zA-Z]` raw HTML
- [x] Analyze knowledge value in Handler.js (behavior.inbound/outbound/error/callback) — full table content confirmed
- [x] Study top 3 complex handlers (MessageResendHandler/RetryHandler/RequestThreadLoopHandler) in depth
- [DECISION: see below] Decide readable state approach for ハンドラ処理概要
- [ ] Propose fix for ハンドラ処理フロー blank-line loss
- [ ] Create design doc at `tools/rbkc/docs/rbkc-handler-v1x-design.md`
- [ ] Present proposals to user and get approval

**Decision needed:** Handler.js behavior data (inbound/outbound/error per handler in queue)

- **Case A**: Parse Handler.js statically in Python → generate Markdown table per handler in HandlerQueue
  - Preserves all behavior text as a table (往路/復路/例外 per row)
  - Requires non-trivial JS-parsing logic in RBKC
- **Case B**: Output HandlerQueue as a bullet list only; drop Handler.js behavior text
  - Per-handler behavior is already covered by each handler's own RST (ハンドラ処理フロー section)
  - Simple to implement, no JS parsing needed

### 2. Propose conversion logic
**Steps:**
- [ ] Design `visit_raw` fix based on approved approach
- [ ] Design blank-line fix for ハンドラ処理フロー (block-quote / definition-list indent handling)
- [ ] Consult Software Engineer expert on design
- [ ] Present to user and get approval

### 3. Implement (after approval)
**Steps:**
- [ ] Follow verify design spec (TDD): write failing verify tests first
- [ ] Write unit tests for converter fix (RED)
- [ ] Implement converter fix (GREEN)
- [ ] Implement verify QC check for script residue
- [ ] Run `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` for all 5 versions
- [ ] Confirm FAIL count diff is as expected
- [ ] Horizontal check: `.. raw:: html` + `:file:` across all 5 versions
- [ ] Write post-mortem at `.work/00312/postmortem-handler-raw-html.md`

## Done

- [x] Issue #312 fetched and branch `312-fix-handler-docs-raw-html` created
- [x] RBKC conversion code identified: `rst_ast_visitor.py:visit_raw` + `rst_ast.py:normalise_raw_html`
- [x] Verify QC5 pattern confirmed: `<[a-zA-Z][a-zA-Z0-9]*...>` already detects opening tags
- [x] Blank-line loss root cause: block-quote/definition-list blank lines collapsed during conversion
