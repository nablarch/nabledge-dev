# Expert Review: Software Engineer — Step 2/3 (#307)

**Date**: 2026-04-24
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: `tools/benchmark/classify_terms.py`, `tools/benchmark/build_index.py`

## Overall Assessment

**Rating**: 4/5
**Summary**: Clean replacement of sklearn TF-IDF with section-level TF.
Separation of concerns is clear, frozen params are respected, dedup tokenizer
is correct on verified edge cases. Real correctness bugs around missing
`encoding="utf-8"` in build_index, a resource-leak `open()`, and non-string
body not being coerced before regex.

## Key Issues

### High Priority

1. **build_index.py reads/writes without encoding="utf-8"** (3 call sites).
   - Decision: **Implement Now** — fixed.
2. **json.load(open(fp)) leaks file handle + bare `except Exception`**.
   - Decision: **Implement Now** — fixed (`with open(...)` + JSONDecodeError/OSError).
3. **Malformed section body (list/dict) crashes regex in iter_sections**.
   - Decision: **Implement Now** — fixed with `isinstance(raw_body, str)` guard.

### Medium Priority

- **M1** compute_candidates filter invariant (term-level only) — **Defer** (not a real risk today).
- **M2** Counter ordering docstring clarification — **Defer** (cosmetic).
- **M3** Attrition stats per section — **Defer** (nice-to-have, Step 4 diagnostic).
- **M4** `|` collision guard in section key — **Defer** (no live risk, snake_case ids only).

### Low Priority

- **L1** Duplicated `iter_sections` between modules — **Defer** to follow-up PR.
- **L2** `load_keyword_map` silent entry skip — **Defer**.
- **L3** "alphabetical" docstring wording → "Unicode codepoint order" — **Defer**.
- **L4** `keyword_map` entries with no matching section warning — **Defer**.

## Positive Aspects

- Dedup logic is correct on verified edge cases (pure-katakana, compound, overlapping).
- Clean separation: keyword selection → pure data artifact → rendering.
- Frozen params honored as module-level `DEFAULT_*` constants.
- Deterministic output via sorted glob / sorted secs / `(-tf, term)` sort.
- JAVA_STOPLIST placement documented (used by `bench/term_extract.py`).
- Helpful progress logging in `main()`.

## Recommendations

- H1-H3 fixed in this PR.
- M3 attrition stats, L1 shared helper → tracked as follow-up (out of Step 2/3 scope).
- Step 4 generation of `index-keywords-ja.json` will reuse the same stats path.
