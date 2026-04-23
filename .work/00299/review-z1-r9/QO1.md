# Z-1 r9 — QO1 bias-avoidance review

**Target**: `check_json_docs_md_consistency` (QO1 portion), `_H2_ONLY_RE`, `_H2_OR_H3_RE`, `_strip_atx_close`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3
**Tests**: `TestCheckJsonDocsMdConsistency_QO1` in `tools/rbkc/tests/ut/test_verify.py`

---

## Findings

### F1. Top-content region end-boundary misses sections rendered at `###`

Spec §3-3 QO1 clause (exact quote):

> セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる

Spec §3-3 QO2 clause (exact quote):

> JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている

The implementation accepts a section title rendered at `##` *or* `###` (QO1), and
the QO1 test `test_pass_section_title_rendered_at_h3` locks this in. However, the
QO2 top-content region bound uses `_H2_ONLY_RE` only:

    h2_match = _H2_ONLY_RE.search(masked)
    ...
    end = h2_match.start() if h2_match else len(docs_md_text)

When the first section title is rendered at `###` (spec-sanctioned per the QO1
clause above), `h2_match` is None (or points to a later `##`), so `end` extends
past the first section. Top-content that actually appears *after* the first
section heading is then falsely "contained" in the top_region slice. The
top-region bound must use the same `##`/`###` union the QO1 section check uses,
otherwise the two checks disagree on where "`#` 見出し直下" ends.

Horizontal: `_H2_ONLY_RE` is also used at line 167 for the "JSON has no sections
but docs has `##` headings" guard. That use is symmetric with docs.py's current
emitter (which only emits `##` as section markers), but under the spec wording
"`##`/`###` に存在" a section rendered at `###` with `sections=[]` in JSON
would escape both the `docs_h2_only_titles` extra-check and the no-sections
guard. The spec clause above permits `###` for section titles, so the
no-sections guard must also consider `###`.

### F2. Section-title count mismatch not detected when titles duplicate

Spec §3-3 QO1 clause (exact quote):

> セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる

"JSON と同じ順序で並んでいる" — ordered list equality implies list equality
(same elements, same count, same order). The current implementation uses
membership (`in`) for missing/extra:

    missing = [t for t in json_sec_titles if t not in docs_h2_or_h3_titles]
    extra   = [t for t in docs_h2_only_titles if t not in json_sec_titles]

and an equality compare on the filtered list:

    filtered = [t for t in docs_h2_or_h3_titles if t in json_sec_titles]
    if not missing and not extra and filtered != json_sec_titles: ...

With JSON `sections=[A, A]` (duplicate titles) and docs with only one `## A`:
`A in [A]` is True, so `missing=[]`; `extra=[]`; `filtered=[A]` vs
`json_sec_titles=[A, A]` → "order differs" is reported, but with a misleading
message (it is a count mismatch, not an order mismatch). The detection happens
by accident; the message channel is wrong. More importantly, if docs has `## A`
three times and JSON `sections=[A, A]`, `filtered=[A,A,A]` ≠ `[A,A]` — again
detected but mis-labelled. The clause requires list equality; the check must be
list-equality on the filtered list, and the error message should distinguish
count vs order.

### F3. `extra` direction uses `##` only; a stray `###` title not in JSON is not flagged

Spec §3-3 QO1 clause (exact quote):

> セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる

The spec treats `##` and `###` symmetrically as section-title levels. The
implementation comment justifies the asymmetric `extra` check as follows:

    # The "extra direction" check must therefore use `##` only to avoid
    # false-positives.

That justification relies on docs.py's current behaviour ("docs.py only emits
sections at `##`"). verify must be derivable from the source-format spec alone
(per `.claude/rules/rbkc.md`: "verify's logic must be derivable from source
format specifications alone — not from how RBKC happens to work"). Under the
spec wording, a `###` heading in docs MD that does not correspond to any JSON
section title is spec-invalid (it is a section-title-level heading for a
section that does not exist in JSON). The implementation silently accepts it.
The spec §3-3 QO1 "sections が空で top-level content のみの場合: docs MD に `##`
見出しが出現しない" is written only for `##` — but by symmetry with the
`##`/`###` union clause above, a `###` used as a section title in a
sections=[] JSON is equally a structure mismatch. The `extra` check and the
no-sections guard both need the union form, not `##` only.

### F4. `_strip_atx_close` regex requires leading whitespace; heading with no space before closing `#` is not stripped

Spec §3-3 QO1 requires title equality; CommonMark §4.2 defines the ATX heading
form the spec inherits. `_ATX_CLOSE_RE = re.compile(r'\s+#+\s*$')` requires at
least one whitespace before the closing `#` sequence. This matches
CommonMark §4.2 wording ("optional closing sequence of `#` characters,
preceded by a space"), so the form `# Title#` (no space) is *not* a valid
closing sequence and the trailing `#` is part of the title. That is spec-
correct. No finding on the regex itself.

However, the regex permits `\s*$` after the closing `#` sequence but not
non-`#` characters. CommonMark §4.2 also requires that the closing sequence
"may be followed by spaces only". The regex allows `\s*$`, which with
re.MULTILINE where `$` = end-of-line, is correct. No issue.

---

## Observations (spec-silent)

### O1. Fenced code block regex does not handle 4+ character fences

`_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)`
matches only exactly three backticks/tildes as opener. CommonMark §4.5 allows
fences of four or more characters (closing fence must be ≥ opening length).
A heading inside a 4-backtick fence would leak through as a section title.
Spec §3-3 does not mention fences — this is a CommonMark compliance concern,
not a direct spec clause violation, so it is an observation.

### O2. Headings with 1–3 leading spaces not detected

`_H1_RE`, `_H2_ONLY_RE`, `_H2_OR_H3_RE` all anchor on `^` (with MULTILINE =
line start), requiring the `#` at column 0. CommonMark §4.2 allows up to 3
leading spaces on an ATX heading. If docs MD contains `   ## Title`, the
regex misses it. Spec §3-3 does not enumerate CommonMark indentation rules —
observation.

### O3. Setext headings (`Title\n===` / `Title\n---`) not recognised

CommonMark §4.3 defines an alternate heading form. The regex battery only
recognises ATX. Spec §3-3 does not enumerate heading forms — observation.

### O4. Sections with empty JSON title are silently dropped

Line 165:

    json_sec_titles = [s.get("title", "") for s in sections if s.get("title")]

A JSON section with `title=""` is removed from the comparison list entirely,
hiding the fact that docs MD may or may not have a corresponding heading. Spec
§3-3 does not define behaviour for empty-title sections — observation, but
worth flagging because silent-skip is listed as an anti-pattern in
`.claude/rules/rbkc.md` ("silent skip without spec backing").

### O5. `_H2_OR_H3_RE` comment says "2-3" but docstring context should note that `####` is intentionally excluded

`_H2_OR_H3_RE = re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE)` correctly
excludes `####` (H4) because `#{2,3}` followed by `\s+` cannot match a 4-hash
line. This is the desired behaviour but is not documented — an H4 in docs MD
would be treated as content (acceptable, since the spec reserves `##`/`###`
for section titles). Observation only.

### O6. Ordering check short-circuits when missing/extra is non-empty

    if not missing and not extra and filtered != json_sec_titles:
        issues.append(... "section title order differs" ...)

When `missing` or `extra` is non-empty, the order-check is suppressed. This
means a user sees "missing X" but not "order also wrong"; they fix the
missing title and the order mismatch surfaces only on the next run. Spec
§3-3 does not require reporting all distinct failures in one pass —
observation on UX, not a spec violation.

---

## Files reviewed

- `tools/rbkc/scripts/verify/verify.py` (lines 42–193)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3
- `tools/rbkc/tests/ut/test_verify.py` `TestCheckJsonDocsMdConsistency_QO1`
