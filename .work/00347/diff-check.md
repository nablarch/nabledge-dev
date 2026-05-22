# Diff Check: PR #348 (Issue #347)

**Date**: 2026-05-22

## Changed Files vs origin/main

| File | Change | In Scope? |
|------|--------|-----------|
| `.claude/skills/nabledge-5/knowledge/.../security-check-2.チェックリスト.json` | Regenerated — 11 sections (was 50) | ✅ |
| `.claude/skills/nabledge-6/knowledge/.../security-check-2.チェックリスト.json` | Regenerated — 11 sections (was 50) | ✅ |
| `.work/00347/gen_preview.py` | Preview script (work log) | ✅ |
| `.work/00347/notes.md` | Decision notes | ✅ |
| `.work/00347/preview-security-check-2-checklist.json` | Preview output | ✅ |
| `.work/00347/preview-security-check-2-checklist.md` | Preview output | ✅ |
| `.work/00347/review-by-qa-engineer.md` | Expert review result | ✅ |
| `.work/00347/review-by-software-engineer.md` | Expert review result | ✅ |
| `.work/00347/tasks.md` | Task tracking | ✅ |
| `tools/rbkc/docs/rbkc-converter-design.md` | §8-4 P1-merged spec added | ✅ |
| `tools/rbkc/docs/rbkc-json-schema-design.md` | §3-4 P1-merged added | ✅ |
| `tools/rbkc/docs/rbkc-verify-quality-design.md` | P1-merged verify rules added | ✅ |
| `tools/rbkc/docs/xlsx-sheet-mapping.md` | 2.チェックリスト subtype P1→P1-merged | ✅ |
| `tools/rbkc/scripts/create/converters/xlsx_common.py` | P1-merged grouping implementation | ✅ |
| `tools/rbkc/scripts/create/docs.py` | P1-merged docs MD branch added | ✅ |
| `tools/rbkc/scripts/verify/verify.py` | P1-merged verify implementation | ✅ |
| `tools/rbkc/tests/ut/test_docs.py` | 5 new P1-merged tests | ✅ |
| `tools/rbkc/tests/ut/test_verify.py` | 6 new P1-merged tests | ✅ |
| `tools/rbkc/tests/ut/test_xlsx_common.py` | NEW — 16 P1-merged tests | ✅ |

## Assessment

All 19 changed files are within Issue #347 scope.

- No other versions' knowledge files changed (v1.4/v1.3/v1.2 unaffected ✅)
- No rule files outside of RBKC modified ✅
- No CHANGELOG/README/GUIDE (end-user docs) modified ✅
