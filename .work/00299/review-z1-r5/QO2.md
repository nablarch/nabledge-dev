# Expert Review: QA Engineer — QO2 docs MD 本文整合性 (R5)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Independent QA Engineer (bias-avoidance, fresh context)
**Scope**: QO2 implementation in `tools/rbkc/scripts/verify/verify.py` (`check_json_docs_md_consistency`, `_apply_asset_link_rewrite`, `_strip_fenced_code`) and unit tests in `tools/rbkc/tests/ut/test_verify.py` (`TestCheckJsonDocsMdConsistency_QO2` plus the cross-cutting QO1 positional test). Cross-referenced against spec §3-3 (`tools/rbkc/docs/rbkc-verify-quality-design.md` lines 289–297) and the create-side transform at `tools/rbkc/scripts/create/docs.py::_rewrite_asset_links`.

## Overall Assessment

**Rating**: 4/5
**Summary**: Implementation is aligned with spec §3-3: top-level content is verified *between* `#` and the first real `##` (fence-masked so `##` inside fenced code is not a false boundary); section content is required verbatim; asset-link rewrite is applied symmetrically on both top-level and section content; and every explicitly-requested test axis from this task is present — top missing+present, top-below-H2 FAIL, section missing+present, whitespace-only FAIL, fenced-code PASS, MD special-chars PASS, multi-section mid-wrong, asset rewrite PASS+FAIL. v6 runtime: `All files verified OK`. Unit tests: **156 passed**. The same two R4 observations remain open: (1) the symmetric-rewrite PASS test hand-codes the expected rewritten string rather than deriving it from `docs.py::_rewrite_asset_links`, so it is not a true cross-validation; and (2) there is still no test that places `##` tokens inside a *top-level* fenced code block to lock in the fence-masking contract on the top-region branch.

## Key Issues

### High Priority

_None._ The spec §3-3 positional requirement ("top-level content must sit between `#` and first `##`") is enforced at `verify.py:157–177`, and the FAIL path is exercised by `test_fail_top_level_content_below_first_h2_not_directly_under_h1` (`test_verify.py:85–93`). Implementation does not import from `scripts/create/*` (confirmed — `verify.py` imports only `scripts.common.labels`), preserving the verify/create independence invariant mandated by `.claude/rules/rbkc.md`.

### Medium Priority

**[Medium] Symmetric-rewrite PASS test is still circular-with-expectation (R4 carry-over)**
- Description: `test_pass_assets_link_rewrite_symmetric` (`test_verify.py:194–215`) hard-codes `![図](../../knowledge/assets/img.png)` in the docs MD fixture rather than deriving it from `scripts.create.docs._rewrite_asset_links`. `grep` confirms no import of that function in the test file. The test therefore verifies "verify.py matches a hand-specified transform", not "verify.py matches docs.py". If both sides drift in the same direction (e.g., the regex stops matching a link shape and the fixture is manually "fixed" to match), the test still passes. This is precisely the failure mode that "symmetric" is supposed to rule out.
- Evidence: `test_verify.py:210` — `"# T\n\n## 図\n\n![図](../../knowledge/assets/img.png)\n"` is authored by hand; `scripts.create.docs` is never imported.
- Proposed fix: construct the docs MD fixture by calling `_rewrite_asset_links` on the JSON content. That turns the test into a genuine two-implementation cross-check: it PASSes only when `_apply_asset_link_rewrite` in verify and `_rewrite_asset_links` in docs.py produce the same string for the same input. This is a mechanical, low-risk test-only change; it does not touch production code.

**[Medium] No test for top-level content containing `##` inside a fenced code block (R4 carry-over)**
- Description: `verify.py:166–170` re-masks fenced blocks before finding the first H2 specifically on the top-level branch. There is no test exercising that branch with `##` tokens inside top-level fenced content. `grep` confirms the only fenced-code test is `test_pass_section_content_with_fenced_code` (`test_verify.py:249`), which never hits the top-region H2-boundary logic. A regression that dropped the fence mask on the top-level branch (e.g., reusing the already-masked `docs_scan` from line 123, or removing `_FENCE_BLOCK_RE` from the top-level path) would go undetected until it broke real content in production.
- Proposed fix: add `test_pass_top_content_with_fenced_code_containing_h2` where `content` is something like `` "例:\n```markdown\n## 見出し\n```" `` and docs MD wraps it under `# T` with no real `##` following, asserting `issues == []`. Pair it with a negative variant that strips the fence in docs MD so QO2 would re-interpret the `##` as a real section marker, asserting the FAIL.

### Low Priority

**[Low] Top-level PASS with real sections not exercised for the positional rule**
- Description: `test_pass_top_content_in_docs` (line 164) uses `sections: []`, so the first-H2 bound falls through to `len(docs_md_text)` and the positional rule is trivially satisfied. The symmetric PASS — top content present, at least one `##` also present, top content correctly between them — is not locked in. The FAIL side is covered at line 85.
- Proposed fix: add a PASS case `content="トップ。"` with a non-empty `sections` list where `トップ。` appears above the first `##`.

**[Low] Whitespace-only FAIL covers one variant only**
- Description: `test_fail_whitespace_only_diff` (line 239) tests `\n` → space. Tabs, CRLF, double-space, and trailing whitespace after fence close are plausible silent-drift vectors; one passing case does not rule out tolerance elsewhere.
- Proposed fix: parameterize with 2–3 additional permutations.

**[Low] Error message quoting inconsistency**
- Description: QO1 uses `!r` for titles (`verify.py:131, 147, 150, 154`); the QO2 section-content message (`verify.py:187`) uses plain single quotes around `{title}`. For titles containing backticks, quotes, or leading/trailing whitespace, the rendering is ambiguous. Cosmetic only.
- Proposed fix: switch to `f"... section {title!r} ..."`.

**[Low] Empty section content silently skipped — policy remains untested**
- Description: `verify.py:183–184` — `if not content: continue`. Spec §3-3 line 297 says "各セクションの `content` が docs MD に完全一致で含まれている"; it does not explicitly authorize skipping empty content. No test pins either direction (silent PASS or FAIL). If an RBKC regression emitted `content=""` for a section whose source has body text, QO2 would silently PASS (QO1 would still catch the title, but the body loss would be invisible on the QO2 axis). This was flagged in R4 and remains unresolved.
- Proposed fix: either document the skip in §3-3 and add an asserting test, or remove the skip and FAIL empty content with a test. The current implicit behaviour is neither specified nor tested.

## Positive Aspects

- **Spec §3-3 positional rule enforced** (`verify.py:157–177`): fence-mask → locate H1 end → locate first real H2 start → assert expected string within that window. Exactly what line 296 prescribes.
- **Asset-rewrite is an independent re-computation, not a tolerance**: `verify.py:71–96` re-derives `rel_prefix` from `docs_md_path` / `knowledge_dir` without importing `docs.py`. The docstring at `verify.py:72–80` makes the intent explicit. Pair-shape (PASS + FAIL) is correct — `test_verify.py:217–235` prevents "both sides wrong in the same way" from being classified as acceptable.
- **Fenced-code masking covers the H2 scan on both branches**: `verify.py:121–123` for section-title enumeration and `verify.py:166–170` for the top-level boundary. Byte-position preservation (spaces for content, newlines preserved) keeps match offsets valid against the original text.
- **Multi-section mid-wrong discrimination** (`test_verify.py:263–272`) — the FAIL message names section "B", proving the check is per-section, not aggregate.
- **MD special-chars and fenced-code PASS tests** (`test_verify.py:249, 256`) confirm the verbatim `in` operator handles backticks, `|`, etc. without any pre-processing that could silently mask drift.
- **verify/create independence**: `verify.py` only imports from `scripts.common.labels`. The asset-rewrite logic is re-derived, not delegated to `docs.py`. Satisfies `.claude/rules/rbkc.md`.
- **Runtime evidence**: `./rbkc.sh verify 6` → `All files verified OK`; `pytest tests/ut/test_verify.py` → 156 passed in 1.08s (up from 148 in R4 — 8 additional tests landed since).

## Recommendations

1. **Close the symmetric-rewrite loophole** (Medium-1): import `scripts.create.docs._rewrite_asset_links` in the PASS test and construct the docs MD fixture by calling it. This is the one change that would convert QO2's asset-rewrite coverage from "independent recomputation that happens to agree with a hand-written fixture" to "independent recomputation that agrees with the *other* implementation on the same input". Mechanical, test-only, low risk.
2. **Add a top-region fenced-`##` test** (Medium-2) to lock in `_FENCE_BLOCK_RE` on the top-level branch. Without it, a regression on the top-level fence mask is only caught when it breaks real content.
3. **Decide the empty-section-content policy** (Low-4) — either allow-and-test, or forbid-and-test. The undocumented implicit skip is a latent-gap signal.
4. **Small regression-fixture harness** — a `tests/fixtures/qo2-broken/` directory with intentionally broken docs MD samples (content below first `##`, whitespace-only diff, missing asset rewrite, empty section content with non-empty source) and a smoke test that runs verify expecting specific FAIL strings. Protects all QO2 checks against future silent weakening even when production v6 content does not exercise them.
5. v6 PASS + 156 green unit tests is a strong-but-not-sufficient signal. The two Medium items above are the last loopholes in QO2; closing them would move the check from "demonstrably works on current v6" to "demonstrably cannot regress without a test breaking".

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` — lines 42–189 (QO1 + QO2 path), confirmed no RBKC converter imports
- `tools/rbkc/scripts/create/docs.py` — lines 36–69 (symmetry reference)
- `tools/rbkc/tests/ut/test_verify.py` — lines 85–93 (top-below-H2 FAIL), 157–272 (QO2 class full)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` — §3-3 lines 289–297 (QO2 spec wording)
- Runtime: `./rbkc.sh verify 6` → `All files verified OK`; `pytest tests/ut/test_verify.py` → 156 passed
