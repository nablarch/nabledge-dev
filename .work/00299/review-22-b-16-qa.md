# Expert Review: QA Engineer — Phase 22-B-16

**Date**: 2026-04-23
**Reviewer**: AI Agent as QA Engineer (bias-avoidance subagent)
**Target**: Phase 22-B-16 verify-spec change (QL1 + QO1 strengthening)

## Summary

Proposal is conceptually correct but requires three structural corrections before implementation. Without them, the strengthened checks would either (a) let a class of dangling references silently pass (§3-1 手順0 exception-ban clause), (b) pin docs.py's own slug algorithm (circular-test violation), or (c) import create-side code (§2-2 independence violation).

## Findings

### F1 — Dangling cross-document `:ref:` / `:doc:` currently PASSes silently
- **Violated clause**: 設計書 §3-1 手順0 exception-ban —「未解決 reference / substitution → **FAIL (QC1)**、silent に text を返す fallback は禁止」
- **Description**: `verify.py:1592-1598` and `test_pass_rst_ref_unknown_label_skipped` (line 2016-2020) skip when `label_map` has no entry. Under zero-tolerance this must FAIL (QC1 未解決参照).
- **Fix**: Delete the skip path; convert the case to a FAIL.

### F2 — `:doc:` references are not in current QL1 抽出対象 table (§3-2)
- **Violated clause**: §3-2 QL1 definition list includes `:ref:` and friends, but extraction table omits `:doc:` entirely.
- **Fix**: Spec must be updated first (per rbkc.md: 設計書 → 実装の順序). Add `:doc:` (237 v6) + `:numref:` + `:download:` rows to the extraction table.

### F3 — Docs-MD anchor check as proposed would be circular
- **Violated clause**: rbkc.md "circular tests" + §2-2 independence.
- **Description**: If verify computes expected anchor with the same slug function docs.py uses (shared util), verify only detects util-internal regressions.
- **Fix**: Shared slug lives in `scripts/common/` and is the one independence exception reserved for QO checks. verify must additionally validate that docs MD actually contains a heading whose text maps to the anchor — not trust the anchor string alone.

### F4 — `literalinclude` with missing file path is not verified
- **Violated clause**: §3-1 手順0 exception-ban (same as F1).
- **Description**: Current verify returns `[]` on `Exception` (verify.py:1526-1529). QL1 horizontal class ("dangling reference") is broader than `:ref:` — must cover every AST construct whose target is filesystem/label lookup.
- **Fix**: Cover `:ref:`, `:doc:`, `:download:`, `.. include::`, `.. literalinclude::`, `.. image::`, `.. figure::` in one pass.

## Required test cases (TDD RED, non-optional)

**JSON-side QL1** (10 min):
1. dangling `:ref:` (label absent from label_map) → FAIL (replaces current PASS at test line 2016)
2. dangling `:doc:` (target file absent from source tree) → FAIL
3. `:ref:` resolves, title present in JSON content → PASS
4. `:ref:` title embedded file_id hint missing from JSON content → FAIL
5. `.. image::` with resolvable asset, `assets/{file_id}/name.ext` in JSON content → PASS
6. `.. image::` asset path missing from JSON content → FAIL
7. `.. figure::` caption present, image path present → PASS; either missing → FAIL
8. `:download:` target filename in JSON content → PASS / missing → FAIL
9. `.. literalinclude::` with missing include file → FAIL (QC1 via docutils system_message)
10. Plain prose paragraph, no links → 0 QL1 issues (regression guard)

**Docs-MD-side QL1** (new, 5 min):
11. docs MD `[title](../cat/file_id.md#anchor)` with existing target .md + heading slug match → PASS
12. target .md absent on disk → FAIL (dangling docs link)
13. target .md exists but no heading slug matches anchor → FAIL
14. image link `![](../../knowledge/assets/{file_id}/x.png)` existing → PASS / absent → FAIL
15. End-to-end `:ref:` in both JSON + docs MD paths

Per link-kind matrix: `:ref:` / `:doc:` / `:download:` / image / figure — each gets one PASS + one FAIL for JSON side + same for docs MD. 5 × 2 × 2 = 20 parameterised cases minimum.

**QO1 level** (6 min):
16. JSON `level:2/3/4` matches docs MD `##/###/####` → PASS
17. JSON `level:2` but docs MD emits `###` → FAIL
18. JSON `level:3` but docs MD emits `##` → FAIL
19. level field missing → FAIL (schema violation)
20. Empty section (title only) at level 3 → must appear as `###` in docs MD
21. Top-level only, no sections, no `##` → PASS (regression guard)

## Independence verdict

**Not §2-2 compliant as proposed. Two corrections**:

1. Label-resolution map must extend to `label → (title, file_id, section_id)`. Extend inside `common/` — within §2-2 exception: "ソースフォーマット仕様由来の共通ロジックは create と verify の両方から利用してよい". Do NOT put in `scripts/create/`.

2. Docs-MD anchor algorithm. GitHub's slug rules (lowercase ASCII, hyphenate whitespace, preserve non-ASCII, `-1`/`-2` dedup) are a spec, not a create choice. Codify in `scripts/common/github_slug.py` as pure function with GitHub docs URL citation. verify derives expected anchor using this common function, then checks existence in target .md. §2-2 compliant because function is spec-derived. Critical: verify must **also** cross-check that anchor in link matches slug of an actual heading in target .md, not just that .md exists.

If shared slug module is derived empirically from docs.py output rather than GitHub spec, that is a circular test — reject and re-derive.

## Horizontal class: "dangling reference"

Root-cause class for F1/F4 is **"silent skip on unresolvable reference"**. Full enumeration in verify.py today:
- `verify.py:1526-1529` — docutils parse exception returns `[]` (may hide literalinclude failure)
- `verify.py:1548-1549` — auto-id refs skipped (legitimate if behind allowlist with spec cite)
- `verify.py:1592-1598` — bare `:ref:` with unknown label: silent PASS (F1)
- `labels.py:36-66` — labels failing heading-pattern match silently dropped from map

22-B-16 fix must address **all four** in one pass, documented in commit message per `.claude/rules/review-feedback.md`.

Also confirm by audit that `:doc:`, `:download:`, `include`, external URL resolution each either (a) emit FAIL on dangling, or (b) have a spec clause citing why they cannot dangle.

## Circular-test risk flags

- Test asserting verify's anchor string equals docs.py's emitted anchor (both via same shared function) pins function output, not correctness. Required: assertion must reference independent expected value — hand-written anchor string from GitHub slug rule, or result of parsing docs MD's actual heading and running shared slugify. Latter acceptable only if separate test pins slugify against GitHub's documented rule using fixtures (`"コード値の選択" → "コード値の選択"`, `"Foo Bar" → "foo-bar"`, duplicate → `-1`).
- `test_pass_rst_ref_unknown_label_skipped` (test_verify.py:2016-2020) is circular opposite direction: pins "verify is lenient" rather than "spec says lenient". Must be deleted/inverted per F1.
- QO1 level tests must assert level values against hand-authored docs MD fixture, not what docs.py produces from JSON under test (otherwise pins docs.py's level-to-`#` mapping).

## Test class organisation recommendation

**Split** into `TestCheckSourceLinks_JsonSide` and `TestCheckSourceLinks_DocsMdSide`; update §4 test table. Different oracles, failure modes, fixtures. Unified class obscures which side failed.

Mirror split for QO1: keep `TestCheckJsonDocsMdConsistency_QO1` but add `_Level` suffix subclass for new level-alignment tests.

## Relevant files (absolute paths)

- `tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-2, §3-3, §4, §5 — update before code per rbkc.md 設計書→実装の順序)
- `tools/rbkc/scripts/verify/verify.py` (`check_source_links` lines 1501-1688, silent-skip sites at 1526-1529, 1592-1598)
- `tools/rbkc/scripts/common/labels.py` (extend to return file_id + section_id; spec-derived)
- `tools/rbkc/tests/ut/test_verify.py` (`TestCheckSourceLinks` line 1978; delete test at 2016-2020; split class)
- `.work/00299/tasks.md` (22-B-16 entry — add sub-steps before converter changes)
