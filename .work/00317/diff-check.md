# Diff Check: PR #324 (Issue #317)

**Date**: 2026-05-07

## Non-knowledge file changes (expected for #317)

| File | Reason |
|------|--------|
| `.work/00317/notes.md` | Work log — new |
| `.work/00317/tasks.md` | Task list — updated |
| `tools/rbkc/docs/rbkc-converter-design.md` | Design doc update: container/toctree entry |
| `tools/rbkc/scripts/common/rst_ast_visitor.py` | Implementation: visit_container + _render_toctree |
| `tools/rbkc/tests/ut/test_rst_ast_visitor.py` | Tests: TestVisitContainerToctree (5 tests) |

## Files from previous PR (#312/#315) — included in this branch

These files were introduced by PR #312 (merged into PR #315) and appear in the diff
because this branch diverges from main before #315 was merged:

| File | Reason |
|------|--------|
| `.work/00312/` | Work log for #312 |
| `tools/rbkc/docs/rbkc-handler-v1x-design.md` | Handler v1.x design (#312) |
| `tools/rbkc/docs/rbkc-verify-quality-design.md` | Verify design updates (#312) |
| `tools/rbkc/scripts/common/handler_js.py` | Handler.js converter (#312) |
| `tools/rbkc/scripts/create/docs.py` | docs.py updates (#312) |
| `tools/rbkc/scripts/verify/verify.py` | Verify updates (#312) |
| `tools/rbkc/tests/ut/test_docs.py` | Tests for docs.py (#312) |
| `tools/rbkc/tests/ut/test_handler_js.py` | Tests for handler_js (#312) |
| `tools/rbkc/tests/ut/test_verify.py` | Verify tests (#312) |

## Knowledge files — expected

All 5 versions regenerated via `rbkc.sh create`. The large volume of changes
reflects: (a) toctree pages now contain MD links instead of plain text,
and (b) prior regeneration from #312 was already merged to main but
knowledge files on this branch needed to be regenerated with both changes.

verify FAIL count after regeneration: **0 for all versions**.

## Verdict

All changes are expected. No unexpected files.
