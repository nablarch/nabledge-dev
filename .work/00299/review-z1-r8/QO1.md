# Z-1 r8 Bias-Avoidance QA Review — QO1

**Target**: `tools/rbkc/scripts/verify/verify.py` — `check_json_docs_md_consistency` (QO1 portion) and helpers `_H2_ONLY_RE`, `_H2_OR_H3_RE`, `_strip_atx_close`.
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (QO1).

## Findings

### F1 (Medium) — Order/equality comparison uses `##`-only list, breaking the spec-allowed `###` form

Spec §3-3 QO1 (quoted):

> セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる

The implementation’s top-level equality at verify.py:170:

```
if docs_h2_only_titles != json_sec_titles:
```

compares the JSON section title list against the `##`-only list. When a JSON section title is legitimately rendered at `###` (spec-allowed), `docs_h2_only_titles` omits it, so the equality always fails. Then:

- `missing = [t for t in json_sec_titles if t not in docs_h2_or_h3_titles]` → empty (the title is present at `###`).
- `extra = [t for t in docs_h2_only_titles if t not in json_sec_titles]` → empty.
- Falls through to the `not missing and not extra` branch and emits a spurious
  `section title order differs: JSON=[...] docs=[...]` FAIL.

This directly contradicts the spec clause that permits `##`/`###`. The order check must either (a) compare against the `##`/`###` merged list, or (b) be driven by a per-title presence+position check across the union of heading levels. The current H2-only list is not a valid ordering oracle when the spec sanctions H3.

**Proposed fix**: Replace `docs_h2_only_titles != json_sec_titles` with an order check over `docs_h2_or_h3_titles` (filtered to entries that appear in `json_sec_titles`), and keep the "extra" check on `##`-only. That preserves both r7 intents (no false positive on content `###`; allow spec-sanctioned `###` section titles).

### F2 (Low) — `docs_h2_or_h3_titles` is built from the fenced-code-masked text, but includes `###` subheadings that live inside a section’s content

`_H2_OR_H3_RE.finditer(docs_scan)` captures every `###` in docs MD that is not inside a fenced block — including content-level subheadings. A JSON section title that happens to collide with a content subheading string (e.g. a generic "注記" that also appears as `### 注記` inside another section’s body) will satisfy the `missing` check even when the JSON section itself has no corresponding `##` heading. This is a presence-only check, not a section-title check.

Spec §3-3 QO1 treats `##`/`###` as section-title levels. The current code cannot distinguish content-level `###` (valid CommonMark subheading) from section-title-level `###`. In practice docs.py emits only `##` for section titles, so section-level `###` does not currently occur, but the "missing" direction is still over-permissive for any future emitter or manual-authored case.

**Proposed fix**: Document the assumption in the spec (docs.py emits section titles at `##` only) and narrow the "missing" regex to `##` only, OR require that `###` matches only count when not nested under a section body. Current behaviour silently tolerates mismatches that the spec clause forbids ("JSON 各セクションのタイトルが docs MD の `##`/`###` に存在").

### F3 (Low) — ATX-close stripping covers titles but not headings with trailing hash embedded in text

`_ATX_CLOSE_RE = r'\s+#+\s*$'` requires at least one whitespace before the closing `#`. CommonMark §4.2 requires the closing sequence to be preceded by a space; this is correct. No finding here — included for completeness to confirm r7 F4 was addressed correctly.

## Observations

- `_H2_ONLY_RE` / `_H2_OR_H3_RE` split (r7 F1/F2) correctly eliminates the false-positive on content-level `###` for the *extra* direction and the sections-empty guard (`if not sections and docs_h2_only_titles`). Tests `test_pass_section_with_h3_subheading_in_content` and `test_pass_sections_empty_with_h3_in_top_content` pin this behaviour.
- Fenced-code masking covers both triple-backtick and triple-tilde (`_FENCE_BLOCK_RE`) and is applied before H2 scanning. Tests `test_pass_tilde_fenced_code_block_with_heading_inside` and `test_pass_backtick_fenced_code_block_with_heading_inside` pin this.
- `_strip_atx_close` is applied symmetrically to both docs H1 and docs H2/H3 captures, and `test_pass_atx_closed_heading_title` pins the H1 case. No H2/H3 ATX-close test exists but the code path is the same.
- QO2 top-region bounding uses `_H2_ONLY_RE.search(masked)` (verify.py:205) — correct under the r7 rationale comment, since a content-level `###` must not truncate the top-content region.
- `json_sec_titles` filters out sections with empty titles (`if s.get("title")`). Spec §3-3 does not explicitly sanction title-less sections; verify silently drops them. This is pre-existing behaviour outside r8 scope but worth flagging for a future round.

## Test Coverage Gaps

- No test covers a JSON section title rendered at `###` in docs MD (the scenario exposed by F1). Under the spec’s `##`/`###` clause, this must PASS; current code FAILs with a spurious "order differs" issue.
- No test covers duplicate `###` content-subheadings whose text happens to match a JSON section title (F2 scenario).
- No test covers ATX-close on `##` / `###` headings — only H1 is pinned.
