---
# Tasks: fix handler docs raw HTML in nabledge-1.x

**PR**: TBD
**Issue**: #312
**Updated**: 2026-04-27

## Not Started

### 1. Investigate current structure and propose readable state
**Steps:**
- [x] Read affected MD file (e.g. handlers-PermissionCheckHandler.md) — confirmed `<script>` leak
- [x] Read corresponding RST source — found 3x `.. raw:: html` blocks (Handler.js, inline script, handler_structure.html)
- [x] Identify RBKC conversion code — `rst_ast_visitor.py visit_raw` → `normalise_raw_html` in `rst_ast.py`
- [x] Read verify design spec (`rbkc-verify-quality-design.md`) — QC5 already covers `<[a-zA-Z]` raw HTML
- [ ] Propose readable state for ハンドラ処理概要 (replace script+images with prose or drop)
- [ ] Propose fix for ハンドラ処理フロー blank-line loss
- [ ] Present proposals to user and get approval

### 2. Propose conversion logic
**Steps:**
- [ ] Design `visit_raw` fix: strip `<script>`/`:file:` content entirely (no knowledge value)
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
