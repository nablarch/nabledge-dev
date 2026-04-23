# QA Review: QO2 docs MD 本文整合性

**Reviewer**: Independent QA Engineer (Z-1 R2, no prior-review context)
**Date**: 2026-04-23
**Target**: `check_json_docs_md_consistency` (QO2 portion) + `TestCheckJsonDocsMdConsistency_QO2`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 "QO2 本文整合性"

## Overall Assessment

**Rating**: 2/5

**Summary**: The happy-path tests are solid and v6 verify PASSes, but the implementation contains a silent
skip (`"assets/" in content`) that is **not in the spec** and **not justified by an independence-principle
exception**. The accompanying test (`test_pass_assets_section_skipped`) is a circular test — it asserts the
current implementation's skip behavior as if it were specified, locking in a quality-gate loophole. Per
`CLAUDE.md` / `.claude/rules/rbkc.md`, this is exactly the pattern that must not happen: verify bends to
RBKC's output-rewriting choice (`scripts/create/docs.py`) instead of forcing RBKC to produce matching
output. Without fixing this, QO2's "完全一致" claim is not enforced for any content containing the literal
substring `assets/`.

## Key Issues

### High Priority

**[High] Spec-unauthorized silent skip (`assets/`) in implementation**
- **Description**: `scripts/verify/verify.py:87` and `:95` silently skip any content whose string contains
  `"assets/"`:
  ```
  if top_content and "assets/" not in top_content:
  ...
  if not content or "assets/" in content:
      continue
  ```
  §3-3 QO2 states: "JSON top-level content が docs MD `#` 見出し直下に**完全一致で含まれている**" /
  "JSON sections の content が docs MD に**完全一致で含まれている**". There is no carve-out for
  `assets/`. §2-2 lists exactly one allowed exception class (出力間整合の参照 for QO1/QO2/QO4), and it
  does not license skipping content; new exceptions require the §5 change process.
- **Root cause**: `scripts/create/docs.py` rewrites `assets/...` → `../assets/...` when emitting docs MD.
  Instead of fixing the rewrite in RBKC (or teaching verify to apply the same deterministic rewrite on
  the JSON side before comparing), verify was weakened to drop these sections entirely. This is a
  textbook "verify weakened to make RBKC pass" anti-pattern (per `rbkc.md`).
- **Proposed fix**: Remove the `"assets/" in content` guard. If the relative-path rewrite is a legitimate
  derived-artefact transform, codify it in the spec (§3-3) and implement a deterministic JSON→docs
  normalization (e.g., rewrite `assets/...` to the expected relative form before the `in` check) — do
  **not** bypass the check. Require §5 approval before adding the spec exception.

**[High] Circular test locks in the unauthorized skip**
- **Description**: `test_pass_assets_section_skipped` (test_verify.py:153-161) feeds JSON with
  `![図](assets/img.png)` and docs MD with `![図](../assets/img.png)` — paths that are visibly **not**
  identical — and asserts `== []` (PASS). The test derives its expectation from
  `verify.py`'s skip branch, not from spec §3-3. This is a textbook circular test: it will turn GREEN
  for any RBKC output regardless of whether the asset path is correctly rewritten, missing, or wrong.
  Even a docs MD that entirely omits the image would PASS because the JSON content is never checked.
- **Proposed fix**: Delete this test, or replace it with a spec-derived test: if §3-3 is amended to
  allow path rewriting, write a test that asserts the rewritten form **exactly matches** between JSON
  (after canonical rewrite) and docs MD, and add a FAIL case where the rewrite does not match.

**[High] Silent-skip scope is far too broad (substring match)**
- **Description**: The guard `"assets/" in content` is a raw substring test. It fires on any content
  containing the literal string `assets/` anywhere — including code examples, quoted URL text, prose
  mentioning an `assets/` directory, or unrelated path fragments. None of these are asset image
  references, yet all bypass QO2 verbatim check. This is a silent FAIL-to-PASS loophole that hides
  real content drift.
- **Proposed fix**: If any skip is kept at all (pending §5 approval), scope it to the actual
  construct being rewritten (Markdown image/link tokens whose href starts with `assets/`), detected
  via the common MD AST, not substring.

### Medium Priority

**[Medium] Whitespace-only-diff test does not pin down the rule precisely**
- **Description**: `test_fail_whitespace_only_diff` (line 165-173) replaces `\n\n` with a single space
  and asserts FAIL. Good. However, §3-3 says "完全一致" — there is no ambiguity — but the
  implementation uses plain Python `in`, which is byte-exact. The test covers one direction (newline
  → space = FAIL). Missing: trailing-whitespace variants, BOM, NBSP substitution, CRLF vs LF,
  leading-space indent added by docs layout. Without these, a future regression that introduces any
  per-character normalization would still GREEN the suite.
- **Proposed fix**: Add parameterized cases for at least CRLF vs LF, trailing-space addition, NBSP
  (U+00A0) substituted for ASCII space, and leading-indent addition. Each must be FAIL.

**[Medium] No test for top-level content containing fenced code / special chars**
- **Description**: `test_pass_section_content_with_fenced_code` and
  `test_pass_section_content_with_md_special_chars` only exercise the **section** branch
  (verify.py:92-98). The top-level branch (verify.py:86-89) has no equivalent fenced-code or
  special-char PASS test. An asymmetric regression (top-level handler diverging from section handler)
  would not be caught.
- **Proposed fix**: Mirror the fenced-code and pipe/backtick cases for top-level `content`.

**[Medium] No test for multi-occurrence substring pitfall**
- **Description**: `in` returns True on the first match. If JSON section A's content is a substring
  of section B's content (e.g., A="概要", B="概要の詳細説明"), both will find a match, but that does
  not prove each section's content appears **under its own `##` heading**. §3-3 explicitly says
  "JSON 各セクションの `content` が docs MD に完全一致で含まれている" without positional constraint,
  but combined with QO1 (heading order) the intent is clearly per-section placement.
- **Proposed fix**: Either add a test that fails when section content appears under the wrong
  heading (and tighten the check accordingly), or document in the spec that QO2 is a bag-of-strings
  presence check and that positional correctness is wholly owned by QO1 (not currently the case).

### Low Priority

**[Low] Fixture data is synthetic-only; no spec-coverage test from real v6 source**
- **Description**: All QO2 tests use inline hand-crafted dicts. There is no guard against the real
  docs.py output format drifting (e.g., blank-line policy between heading and body). A single
  golden test built from a minimal real JSON + real-docs-MD pair would catch docs.py regressions
  that substring matches miss.
- **Proposed fix**: Add one integration-style test using a JSON + the docs MD produced by
  `scripts/create/docs.py` to ensure verify passes on a legitimate case and fails when the docs
  generator introduces whitespace drift.

## Positive Aspects

- Clear one-class-per-QO layout (`TestCheckJsonDocsMdConsistency_QO2`) matching §4 "対応テスト" table
  entry — good traceability.
- Both PASS and FAIL pairs for the top-level and section branches (line 123-151).
- The Z-1 gap-fill block (line 163-198) correctly adds whitespace-diff FAIL, fenced code PASS,
  MD special chars PASS, and multi-section single-wrong-content FAIL — these are the exact cases the
  spec implies.
- v6 runtime: `./rbkc.sh verify 6` reports `All files verified OK`; all 9 QO2 unit tests GREEN.

## Recommendations

1. **Block the `assets/` skip at the spec level first**, then implement. Either:
   (a) Remove the skip and fix RBKC to emit JSON content that matches docs MD verbatim (preferred —
   aligns with §3-3 as written), or
   (b) Extend §3-3 via the §5 change process to define a precise, AST-based rewrite rule and apply
   it symmetrically on both sides of the `in` check.
   Delete `test_pass_assets_section_skipped` until this is settled — it is actively blocking the
   quality gate.
2. Strengthen the whitespace/normalization FAIL surface (CRLF, NBSP, indent, trailing space).
3. Mirror fenced-code / special-char PASS cases onto the top-level branch.
4. Clarify QO2's positional semantics in the spec (presence-only vs per-heading) and add a
   regression test for the ambiguous case.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 42-100) — source
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 113-198) — tests
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3, §2-2, §5 — spec
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/create/docs.py` (lines 44-70) — cross-reference
  for the `assets/` rewrite origin

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO2 -v` → 9 passed.
- `./rbkc.sh verify 6` → `All files verified OK`.
- Note: v6 PASS does not by itself validate QO2 correctness, because the `assets/` skip silently
  bypasses an unknown fraction of content. Enumerating how many v6 sections hit the skip branch is a
  necessary follow-up before declaring QO2 "✅" in §4.
