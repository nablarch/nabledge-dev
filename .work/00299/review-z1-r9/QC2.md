# QC2 Bias-Avoidance Review (Z-1 r9)

Target: `tools/rbkc/scripts/verify/verify.py` QC2 logic (RST / MD / Excel).
Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1.

Re-derived from spec independently of prior rounds. Anchoring clauses:

- §3-1 手順 4: 「正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**」
- §3-1 判定分岐のまとめ: 「JSON テキストが正規化ソースに全く存在せず | QC2」
- §3-1 Excel 節 手順 3: 「**QC2（捏造）**: 全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL」
- §3-1 Excel 節 許容構文要素リスト: 「テーブル記号 `|`・`---`、強調記号 `**` 等。これらは JSON テキストに残存しても QC2 の対象外とする」
- `.claude/rules/rbkc.md`「Decide from the spec…」example: 「1-char Excel residue — tolerate or FAIL? → FAIL. Spec §3-1 Excel 節 says any residue other than whitespace is QC2.」

RST and MD paths route through `_classify_missed_unit` (verify.py:713–752). Excel path is the residual-text pipeline at verify.py:1011–1051 with tolerance regex `_MD_SYNTAX_RE` (verify.py:937–950).

---

## Findings

### F-QC2-1 — `_MD_SYNTAX_RE` tolerates Markdown constructs beyond the spec tolerance list without a spec clause that sanctions them

Spec §3-1 Excel 節 許容構文要素リスト:

> 「テーブル記号 `|`・`---`、強調記号 `**` 等。これらは JSON テキストに残存しても QC2 の対象外とする」

Spec §3-1 手順 4:

> 「正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**」

`.claude/rules/rbkc.md`:

> 「"1-char Excel residue — tolerate or FAIL?" → FAIL. Spec §3-1 Excel 節 says any residue other than whitespace is QC2.」

Current `_MD_SYNTAX_RE` strips, in addition to the spec-named `|`, `---`, `**`:

- single `*` (verify.py:944 alternative `\*`)
- `__` with word-boundary (verify.py:944 alternatives `__(?![\w])|(?<![\w])__`)
- backtick `` ` `` (verify.py:948)
- heading prefix `^#+\s*` (verify.py:945)
- blockquote prefix `^>\s*` (verify.py:946)
- ordered-list prefix `^\d+\.\s+` (verify.py:947)

The spec's named list is `` `|` ``, `---`, `**`. The trailing 「等」 is non-enumerative; applying ゼロトレランス (§2-1 「1% のリスクも許容しない」) the silence-is-strict reading — identical to the 1-char precedent quoted in `.claude/rules/rbkc.md` — forbids expanding the whitelist without an explicit spec clause.

Empirical consequence: a JSON cell containing the fabricated character `*`, `` ` ``, `__` (at token boundaries), or a fabricated leading `# `, `> `, or `1. ` escapes QC2 detection even when no such character exists in any source cell. This is the exact class of 「1% のリスク」 the quoted rule forbids.

Proposed fix: restrict `_MD_SYNTAX_RE` to the spec-named set (`|`, `---`, `**`). If the Excel converter legitimately emits other Markdown syntax, add an explicit spec amendment naming those elements; do not let the verify whitelist drift ahead of the spec.

### F-QC2-2 — Test `test_fail_qc2_one_char_fabrication_detected` does not pin the tolerance-list boundary

Spec §3-1 Excel 節 手順 3:

> 「**QC2（捏造）**: 全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL」

Spec §3-1 Excel 節 許容構文要素リスト:

> 「テーブル記号 `|`・`---`、強調記号 `**` 等」

The existing test (test_verify.py:1819–1831) uses residue `"X"` — a plain alphabetic character never stripped by any alternative in `_MD_SYNTAX_RE`. It therefore proves only that alphabetic residue FAILs; it does not prove that residue characters the spec does **not** list (e.g. a fabricated `` ` ``, `*`, `__`, `# `, `> `, `1. `) also FAIL. Under `.claude/rules/rbkc.md` 「Test Writing: Required Coverage … Bug-revealing cases: Input that exercises each specific failure mode」 plus `.claude/rules/development.md` 「What input would make this function produce wrong output? — write that as a test」, the coverage gap is a spec-derived test that is missing, not a cosmetic omission.

Proposed fix: add tests that a JSON residue consisting solely of a non-spec-listed Markdown metacharacter (e.g. `` ` ``, `*`, `__`, `# X`, `> X`, `1. X`) FAILs as QC2 once F-QC2-1 is applied. These are spec-derived (the tolerance list is closed on `|`/`---`/`**`) and serve as the oracle for F-QC2-1.

---

## Observations

### O-QC2-a — RST/MD QC2 classification branch matches spec §3-1 decision table

`_classify_missed_unit` (verify.py:713–752) implements:

- no occurrence anywhere in `norm_source` → QC2
- every earlier occurrence already consumed → QC3
- at least one unconsumed earlier occurrence → QC4

This matches §3-1 判定分岐のまとめ verbatim. The 「every earlier occurrence consumed」 reading (not 「earliest occurrence consumed」) is spec-correct and is documented inline in the docstring.

### O-QC2-b — `_classify_missed_unit` empty-unit QC2 branch is unreachable

verify.py:734–735 returns `"QC2"` when `norm_unit == ""`. Callers reach this function only after `str.find(unit, pos) == -1`; Python's `"".find("", start)` returns `start` (not `-1`) for any valid `start`, so the empty-unit call site never fires. The branch is defensively coded and harmless; not a spec violation.

### O-QC2-c — Excel QC2 reports every residual whitespace-separated fragment

verify.py:1048–1051 splits `residual_plain` on whitespace and emits one `[QC2]` per non-empty fragment. This mirrors the MD/RST all-fragments rule (`.claude/rules/rbkc.md`: 「RST one-snippet vs MD all-fragments → All fragments」) by symmetry and preserves the ゼロトレランス stance. Not a spec violation.

### O-QC2-d — `---+` standalone alternative (r9 addition) is spec-supported

verify.py:943 adds `-{3,}` as an independent alternative, covering a standalone `---` residue (GFM table separator without flanking pipes, horizontal rule fragment). This is directly sanctioned by spec §3-1 Excel 節 许容構文要素リスト naming `---`. Not a violation; resolves r8 F-QC2-1.

### O-QC2-e — RST `_build_rst_search_units` appends zero-length title units for whitespace-only titles

verify.py ≈L672/L683: `(title, _norm(title), sid, False)` is appended whenever `title` is truthy, without re-checking `_norm(title)`. A whitespace-only title normalises to `""`; `find("", start)` returns `start`, so the unit is silently consumed. Harmless for QC2 classification (never reaches `_classify_missed_unit`); flagged as a robustness note, not a finding.

### O-QC2-f — Message literal `"fabricated"` is not a circular test anchor

Tests `test_fail_qc2_*` assert on `"QC2"` (spec bucket) as the primary check; `"fabricated"` is only a disambiguator against incidental QC2 substrings in unrelated messages. The token originates from spec 「誤追加／捏造」. Not a circular test.

### O-QC2-g — `_MD_SYNTAX_RE` is used only in `_verify_xlsx`

Confirmed by grep: no other module references `_MD_SYNTAX_RE`. The tolerance list therefore cannot leak into RST/MD QC2, whose detection runs through the AST-normalised Visitor pipeline, not the Excel regex.

---

## Horizontal check

- All three format paths (RST `_check_rst_content_completeness` L755–833, MD `_check_md_content_completeness` L836–930, Excel `_verify_xlsx` L991–1053) were inspected for QC2 emission sites.
- All call sites of `_classify_missed_unit` were traced; no silent QC2 downgrade paths exist outside the classifier.
- `_MD_SYNTAX_RE` usage traced to the single Excel residue site (L1047); no leakage into RST/MD.
- No `pytest.skip` / `importorskip` disables any QC2 test (confirmed).
- Horizontal scan of tolerance-list candidates against spec §3-1 Excel 節 許容構文要素リスト: every alternative in `_MD_SYNTAX_RE` was cross-checked against the three spec-named elements; gaps enumerated in F-QC2-1.

---

## Summary

Binary verdict: **NOT PASSING** — F-QC2-1 expands the Excel tolerance whitelist beyond what spec §3-1 Excel 節 names, in direct tension with the precedent quoted in `.claude/rules/rbkc.md`; F-QC2-2 is the spec-derived test gap that would have caught F-QC2-1. Observations are non-violating; r9's `---` addition correctly resolves r8 F-QC2-1.
