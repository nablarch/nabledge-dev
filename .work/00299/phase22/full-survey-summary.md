# Full Survey Summary (22-B-12 refactoring preparation)

Exhaustive, not sampled.  All counts are absolute across the entire corpus.

## Excel (212 sheets across 76 files)

| metric | value |
|---|---|
| loaded | 212 / 212 (100 %) |
| P1 classification | 95 |
| P2 classification | 117 |
| P1 with non-empty preamble | 90 / 95 (**94.7 %**) |
| Preamble cells per sheet | 1 (58) / 2 (10) / 3 (8) / 4 (6) / 5 (5) / 6 (2) / 7 (1) |
| Total preamble chars | 7 608 |
| Longest preamble | 757 chars (v5 security matrix checklist) |
| P1 header-row count | 1 row: 94 / 2 rows: **1** |
| True 2-row header sheet | `v5/nablarch5u1-releasenote.xlsx :: 別紙_テスト用APIの移動内容` (only) |
| Composed-column duplicates (span-inherit algo) | **0 / 95** |
| Raw column cells containing ` / ` (separator collision) | **0 / all header rows** |

**Conclusions**:

1. Preamble is a universal feature of Excel P1 sheets, not a sample.
2. True multi-row header is one sheet; the algorithm must still be general, but the corpus does not have 3-row cases.
3. ` / ` (space-slash-space) never appears in any existing column cell — zero collision risk with the proposed separator.
4. Span-inherit composition (parent cell spans rightward until the next non-empty cell) yields zero duplicates across all 95 P1 sheets.

## RST `:ref:` / label resolution (5 versions)

| version | corpus rst | RBKC rst | RBKC refs | A resolvable | B outside-RBKC | C true-dangling |
|---|---|---|---|---|---|---|
| v6   | 334 | 334 | 2 921 | 2 315 | **0** | 606 |
| v5   | 431 | 431 | 3 155 | 2 557 | **0** | 598 |
| v1.4 | 464 | 127 (27 %) |   284 |   235 | **15** |  34 |
| v1.3 | 380 | 309 (81 %) | 1 202 |   940 | **0** | 262 |
| v1.2 | 298 | 297 |1 282 | 1 019 | **0** | 263 |

**Conclusions**:

1. Class B (corpus-defined but RBKC-excluded) is **non-zero only in v1.4 (15 refs, all in `glossary.rst`)** — a consequence of v1.4 mapping adoption being only 27 %.
2. Class C (true dangling) totals **1 763 across all versions** — Sphinx-parity display-text fallback is a mandatory operational feature, not an exception.
3. create-side already implements display-text fallback correctly.  Verify-side is the bug: it FAILs on Class C refs that create legitimately handled.
4. Option A (treat all unresolved refs as PASS): passes the 15 v1.4 Class-B cases silently.  This masks the real semantic: "a label exists in the corpus but RBKC did not ingest the defining file".  The 15 cases are in glossary.rst, a meta-document explaining terms defined elsewhere — the refs pointing to out-of-RBKC files are an *input-scope* decision.
5. Option C (verify builds a corpus-wide label_map): distinguishes "truly dangling" from "mapping-excluded" but requires mapping-scope decisions to be visible in verify's oracle.

Decision implication: treat mapping-excluded refs (B) the same as truly-dangling refs (C) at verify-time (both PASS with display text), because both are legitimate input-scope outcomes.  The distinction that Option C originally addressed (create-internal resolve failure) is covered if verify independently re-scans the corpus — if create emitted display text *and* the label is in the corpus-wide label_map, verify should FAIL (label exists, create missed it).

## `literalinclude` / `include` usage

| directive | v6 | v5 | v1.4 | v1.3 | v1.2 |
|---|---|---|---|---|---|
| literalinclude | 0 | 0 | 12 | 12 | 19 |
| include | 0 | 0 | 67 | 60 | 58 |

- Options used on `literalinclude`: **only `:language:`** (39 of 43 occurrences carry it; the rest have no options).
- `:lines:`, `:dedent:`, `:start-after:`, `:end-before:`, `:emphasize-lines:`, `:caption:` — **0 occurrences corpus-wide**.
- All 185 `include` directive targets resolve on disk — docutils built-in works; no shim needed.
- `literalinclude` shim: `literal_block(body, language=arg0 or options[':language:'])` is corpus-complete.

## Top-level `content` field (v6 knowledge JSON, 353 files)

| metric | value |
|---|---|
| non-empty content | 320 / 353 (90.7 %) |
| length <50 chars | 14 |
| 50–199 | 89 |
| 200–499 | 77 |
| 500–1999 | 126 |
| ≥2000 | 14 |
| max length | 8 548 chars |

`content` already holds free-form preamble text under the h1, with newlines and inline Markdown.  Excel preamble (7 608 chars corpus-total, 757 chars longest sheet) sits well inside the existing shape — no schema strain.

## Derived decisions (from corpus facts, independent of expert recommendation)

### D1: Excel preamble placement → top-level `content` field

Contract: `content` is "title and first section の間の free-form preamble" — a format-independent semantic already established by RST/MD.  Excel preamble fits that contract exactly.  Alternative (new `preamble` field) would introduce format-conditional schema without semantic justification.

QC1 containment: preamble cells joined by `\n` on `content` satisfies JSON ⊇ Excel-cells-in-preamble for all 90 sheets (verified by survey coverage).

QO2 (JSON ⊂ docs MD): docs.py renders `content` under h1.  Zero renderer change.

### D2: Multi-row header column composition → span-inherit + ` / ` separator

Algorithm: for each parent row above the leaf, a non-empty cell's value is inherited rightward until the next non-empty cell.  Leaf row is verbatim.  Composed = SEP.join(non-empty inherited parents + leaf).

QP: composed-column uniqueness verified on 95 / 95 P1 sheets (zero duplicates).

Separator: ` / ` has zero existing-column collisions corpus-wide.  Choice is cosmetic; correctness is carried by the span-inherit algorithm, not by the separator character.  Specify the separator as a constant in `rbkc-converter-design.md` §8 and reference it from verify.

### D3: QL1 verify oracle → corpus-wide label scan, FAIL only on "defined-in-corpus, missing-in-create-output"

Verify builds its own corpus-wide label_map by independent regex scan (no dependency on create/labels.py).  Rules:

- `:ref:` target in JSON → PASS
- `:ref:` target absent from JSON, display text in JSON, label not in corpus-wide map → PASS (Sphinx-parity dangling)
- `:ref:` target absent from JSON, display text in JSON, label IS in corpus-wide map → **FAIL** (create-internal resolve bug)
- `:ref:` target absent from JSON, display text also absent → FAIL (data loss)

v1.4 Class B (15 refs) then:
- display text is emitted by create
- labels ARE in corpus-wide map
- therefore under these rules → **FAIL**

This is the right semantic under zero-tolerance: "corpus knows the label, RBKC did not ingest the defining file" is a scope gap that must be visible, not silently absorbed.

**Consequence for v1.4**: either (a) extend v1.4 mapping to include the fw/ rst files so refs resolve, or (b) accept the FAIL until mapping is extended.  This is an input-design decision, not a verify-weakening decision.

### D4: `literalinclude` shim → add to _LITERAL_DIRECTIVES with `:language:` option support

Shim body: read `self.content`, emit `literal_block(body, body)`, set `.language` from `self.arguments[0]` or `options.get('language', '')`.

Corpus-complete: covers 43 / 43 occurrences.

## Open items (settled by facts)

- No 3-row header exists in corpus — algorithm must handle it in principle, pinned by a unit test using a synthetic 3-row fixture
- No `:language:`-less literalinclude option usage — shim need not parse other options
- v1.4 mapping coverage (27 %) is a **scope decision**, not a verify-weakening — surface it as FAIL and defer the mapping extension to the user
