# QO2 — Z-1 r8 Bias-Avoidance Review

**Scope**: `check_json_docs_md_consistency` (QO2 portion) in
`tools/rbkc/scripts/verify/verify.py` vs spec
`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (QO2), and
the matching tests in `tools/rbkc/tests/ut/test_verify.py`
(`TestCheckJsonDocsMdConsistency_QO2`).

**Verdict**: **PASS** — r7 findings are addressed; no new blocking
findings; observations only.

---

## Spec clauses checked

§3-3:
> **QO2** docs MD 本文整合性 — JSON 各セクションの content が docs MD に完全一致で含まれていない

§3-3 QO2 detail:
> - JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている
> - JSON 各セクションの `content` が docs MD に完全一致で含まれている

(Unconditional; no allowance for empty-content skip.)

---

## r7 finding disposition

### r7 F — `if not content: continue` must be REMOVED (unconditional verbatim check)

**Status**: **Fixed.**

`verify.py` lines 212–220:

```
# QO2: section content verbatim. Per spec §3-3 QO2 "JSON 各セクション
# の content が docs MD に完全一致で含まれている" — unconditional.
# Empty content satisfies the containment check trivially; no skip.
for s in sections:
    content = s.get("content", "")
    title = s.get("title", "")
    expected = _apply_asset_link_rewrite(content, docs_md_path, knowledge_dir)
    if expected not in docs_md_text:
        issues.append(...)
```

No `continue`; empty content yields `expected == ""`, which is trivially
`in docs_md_text`. This is the spec-correct behaviour (empty substring
containment, not a skip).

### r7 QO2 F1 — asset-link expected must be GENERATED via `docs._rewrite_asset_links`

**Status**: **Fixed.**

`test_verify.py` `test_pass_assets_link_rewrite_symmetric`
(lines 257–290) imports `docs._rewrite_asset_links` and builds the
expected docs body from its output. The expected string is no longer
hand-coded, so drift between the two rewrite copies surfaces here.

### r7 QO2 F4 — `_apply_asset_link_rewrite` vs `_rewrite_asset_links` matrix

**Status**: **Fixed.**

`test_verify_and_docs_rewrite_agree_on_matrix` (lines 292–320) runs both
functions on eight inputs — empty, none, single/multiple/nested, mixed
with external links, literal `assets/` in backticks — and asserts byte
equality. This catches drift in either copy.

**Observation (O1)**: The cases cover the realistic surface, but two
spec-silent edge inputs are not exercised. Leaving as observation, not
a finding, because the spec does not force either direction:

- Link URL containing `)` (current regex `[^)]+` will truncate — both
  copies share the same regex so they stay in sync, but the test does
  not pin this.
- Image with empty alt `![]` — covered (`![](assets/nested/…)` is in the
  matrix). ✓

### r7 QO2 F3 — top content with `##` inside fenced block, PASS + FAIL

**Status**: **Fixed.**

- PASS: `test_pass_top_content_with_fenced_h2_inside_top_region`
  (lines 354–372) — docs MD contains the full fenced block, QO2 passes.
- FAIL: `test_fail_top_content_with_fenced_h2_missing_from_docs`
  (lines 374–387) — fenced block missing from docs MD, QO2 reports.

The region-bounding masking via `_FENCE_BLOCK_RE` (lines 194–198) is
exercised by the PASS test (if the fence were not masked, the in-fence
`##` would truncate the top region and the PASS test would fail).

---

## Findings (r8)

None blocking.

### Observations (non-blocking, spec does not force)

**O1 — matrix does not pin regex pathological inputs.** `_MD_LINK_RE`
uses `[^)]+` for URLs; a URL containing `)` would be truncated by both
copies. Because both copies share the regex verbatim, they stay in
sync, but the matrix test does not pin the behaviour. Spec §3-3 is
silent on URL contents, so this is not a blocker; noting it so a
future regex change in one copy does not silently pass the matrix.

**O2 — `_apply_asset_link_rewrite` docstring correctly notes the
independence constraint.** Lines 89–97 state verify.py computes the
transform independently. The matrix test (F4) is the mechanism that
keeps "independent copies" from drifting — the independence principle
(verify must not import RBKC create-side modules at runtime) is
preserved: the docs import in the test is inside the test function, not
at module scope. ✓

**O3 — empty-content trivially-true containment is not explicitly
pinned by a test.** A section with `content: ""` passes via
`"" in docs_md_text == True`. A targeted test (e.g.
`test_pass_empty_section_content_trivially`) would make the
"no-skip, unconditional containment" decision self-documenting.
Spec §3-3 does not require this test, so this is an observation only.

---

## Files reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py`
  (lines 42–222)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/create/docs.py`
  (lines 43–69, for cross-check)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py`
  (`TestCheckJsonDocsMdConsistency_QO2`, lines 220–412)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md`
  §3-3 (lines 270–307)
