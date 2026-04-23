# QC3 Bias-Avoidance Review (Z-1 r9)

Scope: `_classify_missed_unit` + QC3 branches in `_check_rst_content_completeness`,
`_check_md_content_completeness`, and `_verify_xlsx` in
`tools/rbkc/scripts/verify/verify.py`; QC3-labelled tests in
`tools/rbkc/tests/ut/test_verify.py`. Authoritative spec:
`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1.

Each finding quotes the spec clause it alleges is violated. Observations are
spec-silent notes with no binding clause.

---

## Findings

### F1. Excel QC3 classifier uses earliest occurrence only — diverges from spec's "既消費領域と重複" semantics

Spec clause (§3-1 Excel 節 手順 4, verify.py path `_verify_xlsx`):

> 4. **QC3（重複）**: ソーストークンが見つかったが、その位置が既消費領域と重複していた → FAIL

Implementation (`verify.py` L1016–1023):

```
prev_idx = json_text.find(token)
if prev_idx == -1:
    issues.append(f"[QC1] Excel cell value missing from JSON: {token!r}")
elif _in_consumed(prev_idx, len(token)):
    issues.append(f"[QC3] Excel cell value duplicated in JSON: {token!r}")
else:
    issues.append(f"[QC1] Excel cell value missing from JSON: {token!r}")
```

The classifier picks **only the earliest** occurrence (`json_text.find(token)`
from offset 0). The RST/MD path deliberately does not do this — see the
docstring of `_classify_missed_unit` (L728–732):

> The spec's "先行削除済み" requires *every* earlier occurrence to be
> consumed. A naive `find(unit)` that picks only the earliest
> occurrence misclassifies the case where the earliest is consumed
> but a middle occurrence is still unconsumed…

The Excel QC3 path has the mirror-image bug. Build JSON text such that the
token occurs at p1 (consumed) **and** at p2 (unconsumed, p2 < search_start).
Spec §3-1 Excel 節 手順 4 says "その位置が既消費領域と重複" — the token
**is** found at a consumed position (p1), which is sufficient for QC3 under
the spec wording. The current code reports QC3 correctly here because
`find` returns p1. But swap the order: p1 unconsumed (leftover from a
skipped-over region), p2 consumed. `find` returns p1, `_in_consumed(p1)` is
False, verdict is QC1 "missing" — yet the token was in fact found at a
consumed position p2. The spec's condition "見つかった **かつ** 既消費領域と
重複" is satisfied by the **existence** of such a position, not by the
earliest one.

No test exercises this ordering. `test_fail_qc3_duplicate_cell_in_json`
only pins the single-occurrence case (JSON has "同じ" once, source has it
twice) where the earliest-only shortcut happens to coincide with the spec.

Proposed fix: replace the earliest-only `find` with an enumeration (as
`_classify_missed_unit` does for RST/MD) — iterate every occurrence of
`token` in `json_text`, and report QC3 if any occurrence lies inside
`consumed`, QC1 only if no occurrence does. Add a test where the first
occurrence is unconsumed residue and a later one is consumed.

### F2. `_classify_missed_unit` empty-unit branch returns QC2, contradicting spec §3-1 判定分岐

Spec clause (§3-1 判定分岐のまとめ):

> | JSON テキストが正規化ソースに全く存在せず | QC2 |

An empty string is not "JSON テキストが正規化ソースに全く存在せず" — an
empty string is present at every offset by definition (`"abc".find("") == 0`).
Code L734–735:

```
if not norm_unit:
    return "QC2"
```

In practice the callers filter empty `norm_unit` before reaching this
branch (RST path guards `if norm:` at L675/686; MD path `_squash` strips
whitespace). But the function is module-level and the guard is not part
of its contract — a future caller that hands in a whitespace-only title
will get a spec-violating QC2. The docstring does not document the
empty-unit contract either.

Proposed fix: either (a) assert `norm_unit` non-empty at entry and push
the guard into the contract, or (b) treat empty-unit as unreachable via a
raise, not a silent mislabel.

### F3. RST top-level duplicate-content case is not covered by tests

Spec clause (§3-1 手順 1):

> 抽出順序は「top-level title → top-level content → sections[0].title
> → sections[0].content → sections[1].title → ...」とする。

Spec clause (§3-1 判定分岐のまとめ, QC3 row):

> JSON テキストが正規化ソースに存在するが先行削除済み | QC3

Every format/position combination in the extraction order must be
reachable by a QC3 test, because the classifier sees them all through the
same code path but the **call site** (RST vs MD) governs
whether `_classify_missed_unit` is invoked with a `__top__` sid. The
existing test matrix has:

- `test_fail_qc3_duplicate_title` — RST section-section title
- `test_fail_qc3_duplicate_content_rst` — RST section-section content
- `test_fail_qc3_duplicate_title_md` — MD section-section title
- `test_fail_qc3_duplicate_content_md` — MD section-section content
- `test_fail_qc3_top_level_and_section_content_duplicated` — **MD** top+section content

No RST fixture exercises the top-level-content + section-content
duplicate (`sid="__top__"` branch of the RST path at L798, L804). The
RST path produces the issue message `section '__top__': duplicate content`,
which is never asserted. A regression that changes the RST top-level
branch (e.g., mis-filtering `__top__` units, or skipping top-level when
sections are present) would pass the test suite.

Proposed fix: add the RST mirror of
`test_fail_qc3_top_level_and_section_content_duplicated`, asserting
`[QC3]` with the top-level-content duplicated by a section content.

### F4. QC3 title duplicate with source-side single occurrence is untested for RST top+section

Spec clause (§3-1 判定分岐のまとめ):

> JSON テキストが正規化ソースに存在するが先行削除済み | QC3

Tests cover:

- section-section title duplication (`test_fail_qc3_duplicate_title` RST,
  `test_fail_qc3_duplicate_title_md` MD)
- top-level-title + section-title duplication: **not tested**.

Example spec-conformant FAIL case (RST): source `タイトル\n====\n\n` +
section `詳細\n=====\n\n詳細内容。\n`; JSON `title="タイトル"`,
`sections=[{id: "s1", title: "タイトル", content: "詳細内容。"}]`. Per
extraction order and §3-1 手順 4, second "タイトル" consumption finds the
sole occurrence already consumed → QC3. No test asserts this branch.

Proposed fix: add the top-title vs section-title duplicate test for both
RST and MD formats.

---

## Observations (spec-silent)

### O1. Issue-message uses the literal string `section '__top__'` for top-level units

Call sites L800/L802/L804 and L898/L900/L902 interpolate `sid` with the
prefix `section`. For `__top__`, the rendered message reads
`section '__top__': duplicate content: ...`. Spec §3-1 does not mandate a
message format, and the `__top__` sentinel is an internal convention, so
this is not a spec violation. It is, however, user-facing reviewer output
and arguably misleads ("section __top__" suggests a real section id).
Renaming the prefix for `__top__` units is a cosmetic improvement only.

### O2. `_classify_missed_unit` early-terminates at the first unconsumed earlier occurrence

Code L744–746 breaks out of the enumeration at the first unconsumed
occurrence. This is correct for the QC3 vs QC4 decision (we only need
*any* unconsumed earlier occurrence to switch verdict to QC4), and the
`test_fail_qc4_not_qc3_when_middle_occurrence_is_unconsumed` test pins
the spec-conformant outcome. No issue — recording the observation because
an auditor reading the loop might wonder whether full enumeration is
needed; it is not, by spec §3-1 L184 which is existential in "every
earlier occurrence consumed".

### O3. QC3 vs QL2 "duplicate URL" — different definitions, clear separation

`test_pass_duplicate_url_reported_once` (QL2) is distinct from QC3
duplicate content. QL2's "duplicate URL in source but JSON contains it
once" is PASS; QC3's "duplicate text in JSON but source contains it
once" is FAIL. The semantic asymmetry is grounded in the differing
delete-directions defined in §3-1 (RST/MD) vs §3-2, so no conflict.
Noted here so future reviewers do not confuse the two.

---

## Files referenced

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py`
  (L692–752, L791–804, L889–902, L991–1053)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py`
  (L1275–1285, L1544–1601, L1664–1727, L1883–1898)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md`
  (§3-1 L75–226, especially L83 QC3 row, L171–184 判定分岐, L219–226 Excel)
