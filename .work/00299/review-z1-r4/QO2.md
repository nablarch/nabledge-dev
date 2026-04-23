# Expert Review: QA Engineer — QO2 docs MD 本文整合性 (R4)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Independent QA Engineer (bias-avoidance, fresh context)
**Scope**: QO2 implementation in `tools/rbkc/scripts/verify/verify.py` (`check_json_docs_md_consistency`, `_apply_asset_link_rewrite`, `_strip_fenced_code`), unit tests in `tools/rbkc/tests/ut/test_verify.py` (`TestCheckJsonDocsMdConsistency_QO2` plus relevant QO1 case), and v6 verify runtime.

## Overall Assessment

**Rating**: 4/5
**Summary**: R3's High-priority positional gap has been fixed — top-level content is now required to appear *between* the `#` heading and the first real `##` heading, with a dedicated FAIL test. Asset-link rewrite is applied symmetrically to both top-level and section content, with PASS+FAIL coverage. Fenced-code blocks are correctly masked in H2 scanning so `##` inside ` ```markdown ` samples does not prematurely terminate the top-region. The main residual concern is a **circular-with-expectation** risk in the symmetric asset-rewrite test (expected rewritten string is hand-coded, not derived from `docs.py`), plus a few narrow detection gaps noted below. v6 verify: `All files verified OK`. Unit tests: **148 passed**.

## Key Issues

### High Priority

_None._ The R3 blocker (positional check missing for top-level content) is fixed at `verify.py:157–177`; `test_fail_top_level_content_below_first_h2_not_directly_under_h1` (`test_verify.py:85–93`) exercises the exact FAIL mode.

### Medium Priority

**[Medium] Symmetric-rewrite PASS test is circular-with-expectation**
- Description: `test_pass_assets_link_rewrite_symmetric` (`test_verify.py:194–215`) hand-codes the expected rewritten string (`../../knowledge/assets/img.png`) in the docs MD fixture rather than deriving it from `scripts/create/docs.py::_rewrite_asset_links`. If both `verify._apply_asset_link_rewrite` and the test fixture drifted in the same direction (e.g., a regex change that stopped matching a legitimate link shape), the test would still pass. The test therefore verifies "verify.py matches a hand-specified transform" rather than "verify.py matches docs.py". Given R3 already flagged this and `verify.py:50, 53-78` (R3 evidence) now lives at `verify.py:68, 71–96`, the same loophole persists.
- Evidence: `test_verify.py:210` hard-codes the rewritten URL; no import of `scripts.create.docs._rewrite_asset_links`.
- Proposed fix: in the PASS case, import `_rewrite_asset_links` from `docs.py` and construct the docs MD fixture by actually calling it on the JSON content. This is exactly what "symmetric" should mean — two independent implementations producing the same string on the same input. Circularity collapses only when the two sides are genuinely cross-checked.

**[Medium] No test for top-level content that *contains* `##` tokens inside a fenced code block**
- Description: `verify.py:167–170` correctly masks fences before locating the first `##` in the docs MD, but there is no test that puts a `## ...` line *inside* `top_content`'s fenced sample. Without this test, a regression that stopped masking (or only masked the outer `docs_md_text` but not the expected content path) would go undetected on the top-level branch. The section-level fence test (`test_pass_section_content_with_fenced_code`, line 249) does not exercise the top-region boundary logic because it only involves section content.
- Proposed fix: add a PASS test where `top_content` contains a fenced block that includes `## inside-fence`, and assert the FAIL path for a copy where the fenced `##` was stripped in docs MD. This locks in the masking contract specifically for the top-region scan.

**[Medium] Empty-content section is silently skipped — policy not captured by any test**
- Description: `verify.py:183–184` — `if not content: continue`. Spec §3-3 wording is "各セクションの `content` が docs MD に完全一致で含まれている"; it does not explicitly authorize skipping empty section content. If an RBKC regression dropped all body text from a section (empty string) but kept the H2 title, QO2 would silently PASS (QO1 title still matches, content skipped). No test in `TestCheckJsonDocsMdConsistency_QO2` exercises `content=""` for a section whose source actually has body text. Whether this is acceptable or a latent-gap is a spec call — but the current code makes the decision implicitly without a test pinning the behaviour.
- Proposed fix: either (a) write "empty content silently passes is by design" into §3-3 and add a test that asserts the current skip, or (b) remove the skip and FAIL empty section content, with a test that asserts the FAIL. Either direction is acceptable; the current undocumented implicit skip is not.

### Low Priority

**[Low] Top-level PASS test does not assert content appears *above* the first `##`**
- Description: The existing `test_pass_top_content_in_docs` (line 164–167) uses a JSON with `sections: []`, so there is no first `##` at all — the test passes because `end = len(docs_md_text)`. The symmetric positive case of the new positional rule (top content present, at least one `##` also present, top content correctly sits between them) is not directly exercised. The FAIL case (line 85) covers the violation, but no test locks in the PASS branch when a `##` exists.
- Proposed fix: add `test_pass_top_content_between_h1_and_first_h2` with `content="トップ。"` and a non-empty `sections` list, asserting `issues == []`.

**[Low] Whitespace-only FAIL test covers one variant**
- Description: `test_fail_whitespace_only_diff` (line 239–247) only tests "newline replaced by space". Tabs, CRLF, double-space, and trailing whitespace after code fences are all plausible silent drift vectors that verify must still catch. One passing case does not rule out tolerance elsewhere.
- Proposed fix: parameterize with 2–3 whitespace permutations (`\n`→` `, `\n\n`→`\n`, trailing space after fence close).

**[Low] Error message formatting inconsistency vs QO1**
- Description: QO1 uses `!r` for titles (`verify.py:131, 147, 150, 154`), QO2 section-content message uses plain single quotes (`verify.py:187`). For multibyte or quote-containing titles, the QO2 rendering can be ambiguous. Cosmetic only.
- Proposed fix: switch `f"... section '{title}' ..."` to `f"... section {title!r} ..."` for consistency.

## Positive Aspects

- **Spec §3-3 positional rule now enforced**: `verify.py:157–177` masks fenced blocks, finds the H1 end and first real H2 start, and asserts the expected string appears inside that window — the exact behaviour spec §3-3 line 296 prescribes. R3 blocker resolved.
- **Asset-rewrite symmetric, not a tolerance**: the docstring at `verify.py:72–80` explicitly calls out that this is a like-for-like independent re-application of the same transform, not a looseness — this matches the quality-gate discipline in `.claude/rules/rbkc.md`.
- **FAIL-path coverage for the rewrite** (`test_verify.py:217–235`) prevents the "both sides rewrite consistently wrong" failure mode from being silently classified as a rewrite feature. Pair shape (PASS + FAIL) is correct.
- **Multi-section mid-wrong discrimination** (`test_verify.py:263–272`) — section "B" is named in the FAIL message, so the check is truly per-section, not aggregate.
- **Fenced-code masking applies to H2 scanning** (`verify.py:121–123, 167–170`) — prevents `## ` inside ` ```markdown ` samples from spuriously terminating the top region. This is exactly the kind of edge case that would produce mysterious verify drift in real content.
- **No RBKC converter imports in `verify.py`**: grepped — satisfies the `.claude/rules/rbkc.md` independence invariant.
- **Runtime evidence**: v6 `./rbkc.sh verify 6` → `All files verified OK`; `pytest tests/ut/test_verify.py` → 148 passed.

## Recommendations

1. **Close the remaining symmetry loophole** (Medium-1) by importing `docs.py::_rewrite_asset_links` in the PASS test. This is the single change that would move QO2 from "independently re-applies the same transform" to "cross-validated against docs.py output" — catching any real divergence between the two sides.
2. **Add the top-region fence masking test** (Medium-2) to lock in the `_FENCE_BLOCK_RE` contract on the top-level branch, not only on section content.
3. **Decide and document the empty-section-content policy** (Medium-3). Silent skip without a spec clause or a test is a latent bug; pick either direction and pin it.
4. **Add a PASS test for top content with real sections present** (Low-1) so the new positional rule is locked in on both sides (PASS + FAIL).
5. v6 PASS remains a weak signal on its own — recommend adding a small regression-fixture directory with intentionally broken docs MD samples (content below first `##`, whitespace-only diff, missing asset-rewrite) and a smoke test that runs verify against it expecting FAILs. This protects against future weakening of the checks even if production content happens not to exercise them.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` — lines 42–189 (in scope)
- `tools/rbkc/scripts/create/docs.py` — lines 35–69 (symmetry reference)
- `tools/rbkc/tests/ut/test_verify.py` — lines 85–93 (QO1 class, top-region FAIL test), 157–272 (QO2 class)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` — §3-3 lines 270–297 (spec)
- Runtime: `./rbkc.sh verify 6` → OK; `pytest tests/ut/test_verify.py` → 148 passed
