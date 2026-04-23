# QC1 — r8

## Summary
0 Findings — shippable.

The three r7 concerns are addressed in the current code:

1. **No image/link post-normalisation in `_norm`.**
   `_build_rst_search_units._norm` (verify.py L628–635) performs only
   whitespace collapse (`re.sub(r'\s+', ' ', t).strip()`), and the
   docstring explicitly records that no verify-side post-normalisation
   is permitted. The only `_MD_LINK_RE` usage (L86–114) is in QO2's
   asset-link rewrite, which is spec-required mirroring of `docs.py`
   and has nothing to do with QC1's residue pipeline.

2. **RST residue is reported per fragment, not as a single snippet.**
   `_check_rst_content_completeness` (L776–797) now merges consumed
   spans, extracts the gap, and iterates `remaining.split()` emitting
   one `[QC1] RST source content not captured: …` issue per fragment,
   exactly mirroring the MD path at L870–894. Spec §3-1 手順 3 plus
   `.claude/rules/rbkc.md` ("RST one-snippet vs MD all-fragments →
   All fragments") are both satisfied.

3. **`_build_rst_search_units._norm` is whitespace-only.**
   The function body is a single `re.sub(r'\s+', ' ', t).strip()`.
   No image strip, no link strip, no markup strip — matching spec
   §3-1 "残存判定の基準" ("Visitor 出力と JSON 側の MD は完全に同じ
   記法で揃っている前提").

The shared `_classify_missed_unit` helper (L679–718) correctly
implements the spec §3-1 判定分岐 for QC2/QC3/QC4 dispatch, including
the non-trivial "先行削除済み" semantics (every earlier occurrence
consumed → QC3, else QC4).

Test `test_fail_qc1_rst_reports_every_residue_fragment`
(test_verify.py L1239–1256) is spec-derived (asserts on the three
named fragments `alpha`/`bravo`/`charlie`), not circular (does not
mirror the implementation's regex or fragment-count constant).

## Findings
_None._

## Observations

- **Reporting cardinality on large residue.** `remaining.split()`
  emits one issue per whitespace-separated token. On a pathological
  input with thousands of uncaptured words, the issues list grows
  linearly. This is the spec-mandated behaviour (no-tolerance +
  all-fragments) and is not a Finding, but callers that render the
  issues list verbatim may want to bucket by SID upstream.

- **Symmetry note.** The MD path (L871–878) sorts `consumed`
  in-place via `consumed.sort()`, while the RST path (L777) uses
  `sorted(consumed)` to preserve the original list (which remains
  unused after this point). Both are correct; the RST version is
  slightly more defensive. No action needed.

## Positive Aspects

- Both RST and MD QC1 residue paths are now structurally identical
  (consumed-span merge → residue extraction → per-fragment emission),
  which is exactly the symmetry the rbkc rule requires.
- Visitor-error paths (parse error, unknown node, unknown role,
  unresolved reference) are all routed to `[QC1]` with explicit
  messages and are covered by dedicated tests (L1397–1447).
- `_classify_missed_unit`'s docstring quotes the spec decision table
  inline, making future maintenance auditable against §3-1.
