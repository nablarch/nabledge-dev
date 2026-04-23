# QO3 Bias-Avoidance Review (r7)

**Target**: `tools/rbkc/scripts/verify/verify.py` — `check_docs_coverage`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (QO3)
**Tests**: `tools/rbkc/tests/ut/test_verify.py::TestCheckDocsCoverage`

---

## Findings

### F1. MD→JSON direction (dangling docs MD) is not checked

Spec §3-3 Z-2 対応テスト表 (line 334) defines QO3's scope as:

> QO3 | `TestCheckDocsCoverage` (**JSON↔MD 1:1 存在確認** + README ページ数)

The arrow `↔` specifies bidirectionality — both JSON→MD and MD→JSON must
be checked to assert a 1:1 mapping. Spec §3-3 QO4 establishes the same
pattern explicitly for the sibling index.toon check:

> 3. **dangling entry**: index.toon に列挙されている相対パスに対応する JSON が存在しなければ FAIL (検索でヒットした後にファイルが見つからず 404 になる状態を防ぐ)
> いずれも「index.toon の内容と JSON ファイル群が**完全に一致する**」ことを双方向で確認する。

QO3 is the docs-MD analogue of QO4, and the spec prose for QO3 (line 289)
says "JSON の人間可読レンダリングであるため、両者は**完全に一致しなければならない**"
— the symmetric obligation applies.

`check_docs_coverage` at verify.py:220-226 only iterates
`kdir.rglob("*.json")` and checks for a corresponding MD. It never
iterates `ddir.rglob("*.md")` to detect MDs whose JSON source was
deleted / renamed / never generated. A dangling docs MD (MD exists,
JSON missing) is silently accepted — the direct analogue of the QO4
"dangling entry" case the spec explicitly forbids.

The README page-count sub-check (verify.py:228-239) does not cover this
gap reliably: it only fires if the README's declared count happens to
disagree with the filesystem total. If RBKC writes README based on the
MD-on-disk count (not the JSON count), a dangling MD inflates both
`declared` and `actual` equally and the mismatch never surfaces. Under
ゼロトレランス this indirect check cannot substitute for the direct
MD→JSON enumeration required by "JSON↔MD 1:1".

No clause in §3-3 sanctions skipping the MD→JSON direction.

**Fix**: add a second pass — for each `ddir.rglob("*.md")` (excluding
`README.md`), require a corresponding JSON at the mirrored relative
path under `kdir`; otherwise emit `[QO3] dangling docs MD: …`.

### F2. Test suite does not exercise the dangling-MD case

`TestCheckDocsCoverage` covers JSON-without-MD (`test_fail_json_without_matching_docs_md`),
wrong-path MD (`test_fail_docs_md_at_wrong_nested_path`), README missing,
and CJK filenames. There is no test asserting FAIL when a docs MD has
no corresponding JSON. Per `.claude/rules/rbkc.md` TDD rule ("Every new
check added to verify requires a corresponding test before
implementation"), the MD→JSON direction must be added as a RED test
before/with the implementation fix for F1.

### F3. README sub-check: `declared == 0` + zero MDs passes trivially

`test_fail_json_without_matching_docs_md` (test_verify.py:465) writes
`"0ページ\n"` with zero actual MDs, so the README count check passes
while QO3 still catches the missing MD via the per-file loop. This is
fine as a test-fixture choice, but note that a real RBKC output with
`0ページ` declared and `0` MDs produced would trivially pass this
sub-check even though the 0-page corpus itself is almost certainly a
bug in a different verify layer. Not a QO3 defect — observation only.

---

## Observations

- The JSON→MD loop (verify.py:220-226) is correct: it uses
  `with_suffix(".md")` on the full relative path, so the wrong-nested-path
  case is caught. Good.
- CJK filename handling works because `Path` operations are
  encoding-agnostic on the supported platforms; the explicit test is
  appropriate defensive coverage.
- The README count regex `^(\d+)\s*ページ` is anchored to line start
  with `re.MULTILINE` — acceptable for the spec wording "`N ページ\n` 形式の行".
- `check_docs_coverage` returns early on `README.md missing`, which
  means any JSON→MD or (future) MD→JSON findings are suppressed when
  README is absent. Spec §3-3 lists README existence as a sub-check of
  QO3, not a gate for the primary 1:1 check; under ゼロトレランス the
  early return should be removed so all failures are reported in one
  run. Flagging as a secondary observation tied to F1 — the MD→JSON
  pass will have to skip this early return too.

---

## Summary

QO3 implementation enforces JSON→MD only; the MD→JSON direction
required by the spec's bidirectional "JSON↔MD 1:1" wording (and by
symmetry with QO4's explicit dangling-entry clause) is missing, with
no corresponding test. Dangling docs MDs pass verify silently —
ゼロトレランス violation.
