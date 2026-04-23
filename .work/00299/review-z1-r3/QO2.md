# Expert Review: QA Engineer — QO2 docs MD 本文整合性

**Date**: 2026-04-23
**Reviewer**: AI Agent as Independent QA Engineer
**Scope**: QO2 implementation (`scripts/verify/verify.py`), unit tests (`tests/ut/test_verify.py`), v6 runtime.

## Overall Assessment

**Rating**: 3/5
**Summary**: QO2 body-consistency implementation does the right verbatim substring check, symmetric asset-link rewrite is correctly mirrored from `docs.py`, and tests cover the main FAIL/PASS modes including whitespace-only diff, fenced code, MD special chars, multi-section mid-wrong, and both asset-rewrite-match-PASS / rewrite-missing-FAIL. However there is a **specification non-conformance** (positional check missing for top-level content) and a **bias risk** in how the asset-rewrite tests are constructed. v6 verify PASSes and 134 tests PASS — but v6 passing is a weak signal because the spec deviation below would not be caught by any current v6 fixture.

## Key Issues

### High Priority

**[High] Top-level content position not enforced — spec says `#` 見出し直下**
- Description: Spec §3-3 "QO2 本文整合性" requires *"JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている"*. Implementation at `tools/rbkc/scripts/verify/verify.py:130-134` only performs a plain substring check (`if expected not in docs_md_text`). A docs MD where top-level content is incorrectly emitted *below the first `##` section heading* (or after a section) would PASS QO2 despite being structurally wrong.
- Evidence: `tools/rbkc/scripts/verify/verify.py:131-134`:
  ```
  if top_content:
      expected = _apply_asset_link_rewrite(top_content, docs_md_path, knowledge_dir)
      if expected not in docs_md_text:
          issues.append(f"[QO2] {file_id}: top-level content not found verbatim in docs MD")
  ```
  Compare to §3-3 line 290 of `tools/rbkc/docs/rbkc-verify-quality-design.md`.
- No test in `test_verify.py` exercises *"top-level content present but below a `##` heading"* — this is a detection gap.
- Proposed fix: compute position of first `##` heading (or docs end if absent); require the `top_content` substring index to be **below the `#` heading and strictly before the first `##` heading**. Add two tests: (a) PASS when top-level content appears between `#` and first `##`; (b) FAIL when top-level content appears only after the first `##` heading.

### Medium Priority

**[Medium] Asset-link rewrite tests do not cross-validate against the real `docs.py` transform**
- Description: `test_pass_assets_link_rewrite_symmetric` (`tests/ut/test_verify.py:149-170`) hand-writes the expected rewritten string (`../../knowledge/assets/img.png`) rather than deriving it from `docs.py`'s rewrite function. If both `verify._apply_asset_link_rewrite` and the hand-written fixture drifted in the same way (e.g., a regex change that swallowed parentheses), the test would still pass. This is circular-with-expectation — weaker than circular-with-implementation but still a bias risk because the test encodes an assumption about `docs.py`'s output rather than observing it.
- Evidence: `tests/ut/test_verify.py:165` hard-codes `../../knowledge/assets/img.png`; no import of `docs.py`'s rewrite helper.
- Proposed fix: in the symmetric PASS test, import and invoke `scripts.create.docs`'s rewrite helper to generate the docs MD fixture, so any real divergence between the two implementations is caught. (This is acceptable because the test is asserting symmetry between two independent implementations — importing the *other* side is precisely what verifies symmetry.)

**[Medium] No test for `assets/` link where source/URL contains `)` or special chars**
- Description: `_MD_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')` fails on URLs containing `)` (URL-encoded or literal). Not a QO2-introduced defect, but since verify mirrors `docs.py`, any mismatch in handling of edge-case URLs would silently produce identical wrong output on both sides and still PASS QO2 — an invisible consistency bug.
- Proposed fix: add a unit test with a URL containing `%29` / escaped parens to confirm current behaviour is at least symmetric, and document limitation.

**[Medium] Empty-content section is silently skipped**
- Description: `tools/rbkc/scripts/verify/verify.py:140-141` — `if not content: continue`. Spec §3-3 does not explicitly permit empty section content; QO1 allows empty-section presence, but QO2 silently passes an empty-content section with no check. A RBKC bug that dropped all body text from a section would pass QO2 (title passes QO1, empty content silently skipped).
- Evidence: no test in `TestCheckJsonDocsMdConsistency_QO2` covers `content=""` with a section that the source actually has body text for.
- Proposed fix: clarify in spec whether empty section content is permitted by verify; if not, flag empty content as FAIL at QO2 or delegate to a separate check (QC*-content-completeness is the right home). Add explicit test covering the policy decision.

### Low Priority

**[Low] Error messages truncate section `title` — may be confusing for long/multibyte titles**
- Description: `f"[QO2] {file_id}: section '{title}' content not found verbatim in docs MD"` includes the raw title. Long titles or titles containing quote chars render awkwardly.
- Proposed fix: use `{title!r}` consistently (QO1 uses it for title mismatch; QO2 uses plain quotes).

**[Low] `test_fail_whitespace_only_diff` uses a single sentinel — recommend adding second whitespace variant**
- Description: Only tests newline→space. Tabs, double-space, CRLF, and trailing whitespace after code fences are all observed docs-side edits that could cause silent drift. A single case passing does not disprove tolerance elsewhere.
- Proposed fix: parameterize the test with multiple whitespace-only permutations.

## Positive Aspects

- Symmetric rewrite design is correct: `verify.py:50, 53-78` duplicates the exact regex and relpath logic from `scripts/create/docs.py:35-69`. The docstring at `verify.py:53-62` explicitly justifies it as "NOT a tolerance" — good documentation of intent and spec-compliance.
- No silent skip for `assets/` content: `test_fail_assets_link_rewrite_missing_from_docs` (`test_verify.py:172-190`) confirms missing asset-linked content is a FAIL. The asymmetric pair (PASS + FAIL) is the right structure for a rewrite check.
- Multi-section discrimination works: `test_fail_multiple_sections_one_content_wrong` (`test_verify.py:218-227`) verifies the middle-wrong case specifically names section B — ensures the check is per-section, not aggregate.
- Fenced code and MD special chars (`test_verify.py:204-216`) confirm the check is a raw-string substring, not a re-rendered comparison. Good.
- Verify has no import of RBKC converters/resolver/run (confirmed via grep) — satisfies the independence rule from `.claude/rules/rbkc.md`.
- v6 verify: `All files verified OK`. Unit tests: 134 passed.

## Recommendations

1. **Fix the High-priority positional gap** before next release — add the `#`→first-`##` range check and the two missing tests. Without this, a class of RBKC mis-ordering bugs will slip through QO2.
2. **Strengthen symmetry test** (Medium) by importing `docs.py`'s rewrite helper rather than hand-coding the expected rewritten string; this closes a circular-with-expectation loophole.
3. **Decide spec policy on empty section content** and either add a QO2 FAIL or explicitly document that QC-content-completeness is the quality gate there. Silent skip without written policy is a latent bug.
4. v6 PASS here is a weak signal because no current v6 fixture exercises the positional issue (High). Strengthen by seeding a synthetic broken docs MD in a regression-fixture directory and running verify against it as a negative smoke test.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code, lines 42-146 in scope)
- `tools/rbkc/scripts/create/docs.py` (source code, lines 35-69 for symmetry check)
- `tools/rbkc/tests/ut/test_verify.py` (tests, lines 108-227 in scope)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec, §3-3 lines 277-291)
