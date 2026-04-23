# Expert Review: QA Engineer — QO2 docs MD 本文整合性 (R6)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Independent QA Engineer (bias-avoidance, fresh context)
**Scope**: QO2 implementation in `tools/rbkc/scripts/verify/verify.py` (`check_json_docs_md_consistency`, `_apply_asset_link_rewrite`, `_strip_fenced_code`), unit tests in `tools/rbkc/tests/ut/test_verify.py` (`TestCheckJsonDocsMdConsistency_QO2` plus QO1 cross-class top-level case), `scripts/create/docs.py::_rewrite_asset_links` as the symmetry reference, and v6 runtime verification.

## Overall Assessment

**Rating**: 4/5
**Summary**: QO2 implementation is spec-compliant for the three §3-3 clauses it must enforce (top-level content between `#` and first `##`; each section content verbatim; symmetric asset-link rewrite). Fenced-code masking is correctly applied on both H2 scanning and the top-region boundary search. v6 production run: `All files verified OK`. Unit-test suite: **158 passed** (up from 148 at R4; the delta is in other quality IDs, not in `TestCheckJsonDocsMdConsistency_QO2`, which is unchanged at 10 tests). All three R4 Medium items remain **unaddressed in the QO2 test class** — the symmetric-rewrite circularity, top-region fence-masking coverage gap, and the undocumented empty-section-content skip policy — so they are carried forward here with evidence. None rise to blocker because the production path is presently correct and covered by existing FAIL tests on adjacent code paths, but each is a latent-regression loophole.

## Key Issues

### High Priority

_None._ The spec §3-3 positional rule for top-level content is enforced at `verify.py:158-178` and has a dedicated FAIL test at `test_verify.py:85-93` (`test_fail_top_level_content_below_first_h2_not_directly_under_h1`). The independence invariant (`verify` must not import RBKC create-side modules) holds: `verify.py:22` only imports `scripts.common.labels`.

### Medium Priority

**[Medium] Symmetric-rewrite PASS test is circular-with-expectation**
- Description: `test_pass_assets_link_rewrite_symmetric` (`test_verify.py:228-249`) hard-codes the rewritten docs MD URL (`../../knowledge/assets/img.png` at `test_verify.py:244`) rather than deriving it by invoking `scripts.create.docs._rewrite_asset_links` on the JSON content. The test therefore asserts "`_apply_asset_link_rewrite` matches a hand-specified transform", not "`_apply_asset_link_rewrite` matches `docs.py` output". If both sides drifted in the same direction (e.g., `_MD_LINK_RE` at `verify.py:69` and at `docs.py:36` were both changed to stop matching a legitimate link shape), the test would still pass. This loophole was raised in R3, noted as unresolved in R4, and remains unresolved in R5/R6.
- Evidence: `test_verify.py:244` hand-codes rewritten URL; no import of `scripts.create.docs._rewrite_asset_links` anywhere in `test_verify.py`. The two regexes `_MD_LINK_RE` at `verify.py:69` and `docs.py:36` are byte-identical duplicates — a single-source-of-truth refactor would mechanically collapse the drift risk.
- Proposed fix: in the PASS test, construct the docs MD fixture by calling `scripts.create.docs._rewrite_asset_links(data["sections"][0]["content"], docs_md_path, kdir)` and embedding the result in the surrounding MD template. True symmetry = two independent implementations cross-checked on the same input.

**[Medium] No test for fenced `##` inside top-level content**
- Description: `verify.py:166-175` masks `_FENCE_BLOCK_RE` before locating the first real `##` in `docs_md_text`, so a ` ```markdown ` sample containing `## ...` inside the top content does not prematurely terminate the top region. No test in `TestCheckJsonDocsMdConsistency_QO2` exercises this specific combination (fence containing `##` placed inside `top_content`). The existing fence-masking QO1 tests (`test_verify.py:152-169, 171-184`) only exercise the H2-scan branch, and the QO2 fenced-content PASS test (`test_verify.py:283-288`) uses a fenceless `##` case in a *section*, not in top content. A regression that removed masking on the top-region branch (`verify.py:171`) would not be caught.
- Proposed fix: add `test_pass_top_content_with_fenced_double_hash` where `top_content = "概要\n\n```md\n## fake\n```"` and assert `issues == []`. Pair with a FAIL variant where docs MD has the fenced `##` stripped out to confirm the comparison is still strict.

**[Medium] Empty section content is silently skipped — no test or spec clause authorises it**
- Description: `verify.py:184-185` — `if not content: continue` — unconditionally exits the section-content check when JSON content is `""`. Spec §3-3 line 297 requires "JSON 各セクションの `content` が docs MD に完全一致で含まれている" without explicit empty-string exemption. If an RBKC regression emitted a section with the H2 title preserved but the body dropped to `""`, QO1 would pass (title matches) and QO2 would silently pass (empty string skip). No test in `TestCheckJsonDocsMdConsistency_QO2` pins the current behaviour either way. This is an undocumented implicit policy exactly of the kind `.claude/rules/rbkc.md` forbids ("Never weaken verify's detection to make RBKC output pass").
- Proposed fix: decide the policy explicitly. Preferred direction: drop the skip and treat empty section content as a FAIL *unless* the source legitimately has no body (which should then set `no_knowledge_content: true` or be collapsed into parent section). Add a test asserting the chosen direction. If the skip is kept, §3-3 must document the exemption and a test must lock in the skip.

### Low Priority

**[Low] Top-level PASS path with real `##` present is not locked in**
- Description: `test_pass_top_content_in_docs` (`test_verify.py:198-201`) uses `sections: []`, so the positional rule at `verify.py:172-175` reduces to `end = len(docs_md_text)` — the window is the entire document and the "between `#` and first `##`" invariant is not actually exercised on the PASS side. The FAIL side is covered (`test_verify.py:85-93`) but the PASS side for the same rule is not.
- Proposed fix: add `test_pass_top_content_between_h1_and_first_h2` with `content="トップ。"` and one or more real sections, asserting `issues == []` when top content appears in the correct window.

**[Low] Whitespace-only FAIL coverage is single-variant**
- Description: `test_fail_whitespace_only_diff` (`test_verify.py:273-281`) only exercises newline→space. Tabs, CRLF, double-space-to-single, and trailing-whitespace-after-fence-close are all plausible silent-drift vectors. One passing variant does not rule out tolerance elsewhere in the compare path (there is no tolerance in the code — it is a raw `in` check at `verify.py:177, 187` — but the test suite does not prove that across common whitespace-drift shapes).
- Proposed fix: parametrise with 3–4 whitespace permutations (`\n`→` `, `\n\n`→`\n`, tab vs 4-space indentation inside a code fence, CRLF vs LF).

**[Low] Section-content FAIL message uses plain quotes, inconsistent with QO1 `!r` formatting**
- Description: QO1 messages use `!r` consistently (`verify.py:132, 148, 151, 155`); QO2 section-content message at `verify.py:188` uses `'{title}'`. For titles containing apostrophes, multibyte quoting, or trailing whitespace, the rendering is ambiguous and harder to grep in CI logs. Cosmetic only — does not affect detection — but makes debugging slower on failure.
- Proposed fix: change `verify.py:188` from `f"[QO2] {file_id}: section '{title}' content not found ..."` to `f"[QO2] {file_id}: section {title!r} content not found ..."`.

## Positive Aspects

- **Spec §3-3 positional rule is correctly enforced on both sides**: `verify.py:158-178` computes the `[h1_end, first_h2_start)` window using fence-masked offsets against the original text and asserts the rewritten expected string appears inside — exact match to spec §3-3 line 296. `test_verify.py:85-93` covers the FAIL case.
- **Asset-link rewrite is a documented symmetric transform, not a tolerance**: `verify.py:72-81` docstring explicitly frames the rewrite as an independent re-application of the same algorithm on the verify side, not a looseness. Pair-shape coverage (PASS + FAIL) at `test_verify.py:228-249, 251-269` blocks the "both sides rewrite consistently wrong" silent-pass failure mode.
- **Fenced-code masking is length-preserving**: the `_mask` lambda at `verify.py:64-65, 168-170` substitutes spaces (keeping newlines) so match offsets remain valid against the original `docs_md_text`. This is the subtle correctness property that makes `h2_match.start()` directly usable as a slice bound at `verify.py:175`.
- **Per-section FAIL discrimination**: `test_verify.py:297-306` confirms the middle section's title is named in the FAIL message — QO2 is truly per-section, not aggregate, so downstream triage knows which section to look at.
- **Independence invariant intact**: `grep "from scripts.create"` in `verify.py` → no matches. `verify.py:22` only imports `scripts.common.labels`. Matches `.claude/rules/rbkc.md` requirement that verify never import create-side modules.
- **Runtime + unit evidence**: `./rbkc.sh verify 6` → `All files verified OK`; `pytest tests/ut/test_verify.py` → **158 passed, 0 failed, 0 skipped** (no `pytest.mark.skip` anywhere).

## Recommendations

1. **Close the symmetry loophole (Medium-1)** by importing `scripts.create.docs._rewrite_asset_links` in `test_pass_assets_link_rewrite_symmetric` and deriving the docs MD fixture from it. This is the one change that moves the test from "verifies a transform" to "cross-validates two independent transforms". Rated highest because it is the only item where the *gate-role* of verify (cross-check, not re-state) is currently weakened by test construction.
2. **Add the fenced `##`-in-top-content test (Medium-2)** to lock in the masking contract on the top-region branch. Without it, `verify.py:171` can regress silently.
3. **Resolve the empty-section-content policy (Medium-3)** — pick a direction, update §3-3, and add a test. Carrying an undocumented silent skip in a quality-gate check is against `.claude/rules/rbkc.md`.
4. **Add the Low-1 PASS case** so the positional rule is pinned on both sides.
5. **Optional** (deferred, not R6-blocking): introduce a regression-fixture directory (`tests/fixtures/qo2_break_cases/`) with hand-constructed broken docs MD samples (content below first `##`, whitespace-drift, missing rewritten asset link, empty section) and a smoke test that runs `check_json_docs_md_consistency` expecting a named FAIL on each. This raises the cost of future weakening beyond the current v6 PASS signal, which is a weak invariant (v6 data may simply not exercise a broken branch).

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` — lines 42-190 (QO1/QO2 scope), 22 (imports)
- `tools/rbkc/scripts/create/docs.py` — lines 35-69 (symmetry reference for asset rewrite)
- `tools/rbkc/tests/ut/test_verify.py` — lines 85-93 (top-region FAIL test in QO1 class), 191-306 (QO2 class, 10 tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` — §3-3 lines 270-297 (spec), line 333 (QO2 ↔ test mapping), lines 337-342 (✅ criteria)
- `.work/00299/review-z1-r4/QO2.md` — prior round findings (carried forward)
- Runtime: `./rbkc.sh verify 6` → `All files verified OK`
- Unit: `pytest tests/ut/test_verify.py` → 158 passed, 0 failed, 0 skipped
