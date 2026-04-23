# QC1 — r9

## Summary

0 Findings — shippable. QC1 implementation in `tools/rbkc/scripts/verify/verify.py`
matches `rbkc-verify-quality-design.md` §3-1 for RST, MD, and Excel paths. Each
spec-mandated failure mode (未対応 node / 未対応 role / 未解決 reference / parse
error / 残存テキスト) maps to a corresponding `[QC1]` issue emission with a
matching unit test. No silent fallbacks were found, and residue reporting enumerates
every non-whitespace fragment (no truncated-snippet hiding).

## Findings

(none)

## Observations

1. **Residue fragment display is truncated at 50 chars** (`verify.py:831`, `verify.py:928`)
   - Each emitted `[QC1] ... {frag[:50]!r}` truncates long CJK residue (no internal
     whitespace) to the first 50 characters. Detection is unaffected — a fragment is
     still reported one-to-one — but the operator-visible message loses the tail.
   - Spec does not mandate a message format, so this is not a Finding.
   - Suggestion: append `... (truncated)` when `len(frag) > 50` so consumers know
     the residue is longer than printed. Non-blocking.

2. **Excel out-of-order-but-present tokens are labelled QC1 rather than a distinct
   verdict** (`verify.py:1017–1023`)
   - When a token exists in JSON but only at a position before `search_start`
     (i.e. a position regression) and that earlier slot is *not* consumed, the
     code emits `[QC1] Excel cell value missing from JSON`. Strictly the token is
     present, just out of order.
   - Spec §3-1 Excel table lists QC4 as "—" for Excel, so no dedicated verdict
     exists. Spec §3-1 Excel 手順 1–2 also defines search as sequential from the
     last delete position, so "not found sequentially" is the spec's operational
     definition of QC1-missing. This is spec-silent on labelling, so not a Finding.
   - Suggestion (non-blocking): rename the message to `missing-or-misordered` for
     operator clarity. No behavioural change.

3. **`find("", current_pos)` edge case for whitespace-only units**
   - `_build_rst_search_units` guards with `if norm:` before appending content
     units, but the MD path (`_check_md_content_completeness`, lines 864–877)
     does not filter by the post-squash value — it filters by the *raw* `title`
     and `content`. A field that is non-empty but whitespace-only would pass the
     `if content:` guard, be squashed to `""`, and `norm_source.find("", cp)` would
     return `cp`, consuming zero bytes. The resulting `consumed` entry is a
     zero-length interval, harmless to the residue check.
   - No detection bug results, but the asymmetry between RST and MD guard styles
     is worth aligning for readability. Non-blocking.

4. **`_norm`/`_squash` duplication between RST and MD paths**
   - `_build_rst_search_units._norm` and `_check_md_content_completeness._squash`
     are identical `re.sub(r'\s+', ' ', t).strip()` implementations. Not a spec
     issue; minor DRY opportunity.

## Positive Aspects

- **Every spec-mandated QC1 failure mode has a dedicated test** (`test_verify.py`
  lines 1300, 1309, 1469, 1493, 1502, 1511): residual content, all-fragments
  reporting, MD unknown token, RST unresolved substitution, RST parse error
  (level ≥ 3), RST unknown role. This matches §3-1 判定分岐のまとめ rows 1–4.
- **No silent fallback**: Visitor-level errors propagate through
  `UnknownSyntaxError` from `scripts.common.rst_normaliser` / `md_normaliser`
  and are caught exactly once at the QC1 boundary (`verify.py:772`, `verify.py:850`),
  producing a `[QC1]` issue. This honours §3-1b 原則 "silent drop しない".
- **Residue reporting enumerates every fragment** — `remaining.split()` with a
  per-fragment `[QC1]` emission (`verify.py:829`, `verify.py:926`), aligning
  with `.claude/rules/rbkc.md` "RST one-snippet vs MD all-fragments — All
  fragments" and the explicit regression test at line 1309.
- **`_classify_missed_unit` correctly separates QC2 / QC3 / QC4** per §3-1
  判定分岐 rows 5–7 using the "every earlier occurrence consumed" rule, not the
  naive `find()` that would misclassify mixed-consumption cases (docstring lines
  727–733 call this out explicitly).
- **No tolerance list in the residue check** — spec §3-1 "残存判定の基準" mandates
  no exception list; the code honours this: the only filter is
  `if remaining.strip():`, nothing else.
