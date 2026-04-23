# QC2 Bias-Avoidance Review (Z-1 r8)

Target: `tools/rbkc/scripts/verify/verify.py` QC2 logic (RST / MD / Excel).
Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1.

QC2 is re-derived from spec (§3-1 手順 4, 判定分岐のまとめ, Excel 節 手順 3, 許容構文要素リスト) without relying on prior review rounds.

Spec clauses anchoring this review:

- §3-1 手順 4: "正規化ソース中に当該テキストが一度も出現しなかった → FAIL（QC2: 誤追加）"
- §3-1 判定分岐のまとめ: "JSON テキストが正規化ソースに全く存在せず | QC2"
- §3-1 Excel 節 手順 3: "全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL"
- §3-1 Excel 節 許容構文要素リスト: "テーブル記号 `|`・`---`、強調記号 `**` 等。これらは JSON テキストに残存しても QC2 の対象外とする"

---

## Findings

### F-QC2-1 (Excel `_MD_SYNTAX_RE`): `---` (standalone) is not in the tolerance list

Spec §3-1 Excel 節 explicitly names `---` as an allowed residue:

> 「テーブル記号 `|`・`---`、強調記号 `**` 等。これらは JSON テキストに残存しても QC2 の対象外とする」

`_MD_SYNTAX_RE` (verify.py:903-912) covers `---` **only when surrounded by pipes** via `\|[-:]+\|(?:[-:]+\|)*`. A standalone `---` (e.g. GFM table separator that lost its pipes after stripping, horizontal rule, or a `---` fragment in a cell value that RBKC emits as-is) is not matched.

Empirical check:

```
re.sub(_MD_SYNTAX_RE, ' ', '---') == '---'   # not stripped
```

Consequence: a JSON `content` field containing a table rendered by create's MD emitter whose separator is `---` without flanking pipes (or any `---` hyphen-rule residue) would trigger a false QC2 even though the spec says `---` is tolerable.

Proposed fix: add `---+` (three-or-more hyphens) as an explicit alternative in `_MD_SYNTAX_RE`, independent of the pipe-delimited alternative.

### F-QC2-2 (Excel `_MD_SYNTAX_RE`): MD link / image syntax is not in the tolerance list

Spec §3-1 Excel 節 ends the tolerance list with "等" (etc.). Under ゼロトレランス the stricter read is: any character class the create side can legitimately emit as Markdown syntax when rendering an Excel cell must either (a) be a spec-listed tolerance element, or (b) be covered by a create-side contract that prevents it from appearing.

`_MD_SYNTAX_RE` does not cover `[`, `]`, `(`, `)`, `~~`, `<`, `>` (the MD autolink pair), nor the setext underline `===`. Of these:

- `[`, `]`, `(`, `)` — if the Excel converter emits any MD link/image syntax for a hyperlink-bearing cell (openpyxl cells carry a `hyperlink` attribute), `(url)` residue would be reported as QC2 text `'url'`. Spec does not explicitly sanction link markup as a tolerance element, and create-side docs do not forbid emitting links for hyperlinked cells. Either the tolerance list or the create-side contract must be explicit.

This review flags it as a spec-vs-implementation gap the user must rule on before r8 closes. The stricter default (forbid create side from emitting link markup for Excel → do not extend the tolerance list) preserves ゼロトレランス. The alternative (extend the tolerance list) weakens QC2 detection for Excel and should require an explicit spec amendment.

(Per CLAUDE.md `.claude/rules/rbkc.md` §"Decide from the spec…" — this is a case where the spec is genuinely silent and the direction affects user-visible behaviour, so it is surfaced rather than decided unilaterally.)

---

## Observations

### O-QC2-a: `_classify_missed_unit` QC2 branch for empty unit is unreachable but defensively coded

verify.py:700-701:

```
if not norm_unit:
    return "QC2"
```

The calling paths (`_check_rst_content_completeness`, `_check_md_content_completeness`) only reach `_classify_missed_unit` when `norm_source.find(norm_unit, current_pos) == -1`. For `norm_unit == ""`, Python's `str.find("", start)` returns `start` (not `-1`) as long as `start <= len(norm_source)`, so an empty unit is always "found" and never classified. The defensive branch is harmless, but it means this QC2 code path has no observable behaviour and is not exercised by any test. Not a violation.

### O-QC2-b: RST/MD QC2 classification table matches spec §3-1 decision table

`_classify_missed_unit` (verify.py:679-718) implements the three-way split as:

- no occurrence anywhere → QC2
- every occurrence is consumed → QC3
- at least one unconsumed occurrence earlier than `current_pos` → QC4

This matches §3-1 判定分岐のまとめ verbatim. The "every earlier occurrence consumed" reading (rather than "earliest occurrence consumed") is spec-correct — the docstring cites the spec clause explicitly.

### O-QC2-c: Message label "fabricated" is not a circular test anchor

Tests (`test_fail_qc2_*`) assert on the substring `"QC2"` (spec-derived label) and, in some cases, `"fabricated"` (implementation message text). The `"fabricated"` string originates from the spec's own term "誤追加/捏造" and is used only as a secondary filter to disambiguate QC2 from incidental `"QC2"` occurrences in other messages. The primary assertion is QC2 bucket membership, which is spec-derived. Not a circular test.

### O-QC2-d: Excel QC2 emits one issue per residual whitespace-separated fragment

verify.py:1010-1013 splits `residual_plain` on whitespace and emits one `[QC2]` message per non-empty fragment. This satisfies the "RST one-snippet vs MD all-fragments — All fragments" rule quoted in `.claude/rules/rbkc.md` for the Excel path by symmetry. Not a violation.

### O-QC2-e: RST QC2 uses `_norm(title)` that may equal empty for title-only whitespace

`_build_rst_search_units` (visible at verify.py ~649) appends `(title, _norm(title), sid, False)` whenever `title` is truthy without re-checking `_norm(title)`. A whitespace-only title (post-normalisation empty) would become a zero-length unit; as noted in O-QC2-a, `find("", start)` returns `start`, so it is silently consumed. This is a non-issue for QC2 but worth flagging as a robustness consideration for the author.

### O-QC2-f: Test `test_fail_qc2_one_char_fabrication_detected` correctly pins the spec

The 1-char QC2 test (verify_test line 1733) is spec-derived — it quotes §3-1 Excel 節 手順 3 in its docstring and asserts that a single leftover character FAILs. This directly counters prior "length tolerance" anti-patterns and is a healthy spec-derived oracle.

---

## Horizontal check

- All three format paths (RST `_check_rst_content_completeness`, MD `_check_md_content_completeness`, Excel `_verify_xlsx`) were inspected for QC2 emission sites.
- All consumers of `_classify_missed_unit` were traced to confirm QC2 classification is spec-consistent (no additional silent QC2 downgrade paths).
- `_MD_SYNTAX_RE` is used only in `_verify_xlsx`; no other module references it (confirmed by grep).
- No `pytest.skip` / `importorskip` disables QC2 tests (confirmed).

---

## Summary

Binary verdict: **NOT PASSING** — one Finding (F-QC2-1) is a concrete spec vs. implementation gap (`---` standalone tolerance), and one (F-QC2-2) is an ambiguity the user must close before QC2 can claim ✅. Observations are non-violating.
