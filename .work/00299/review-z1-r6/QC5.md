# QC5 Format Purity — Independent QA Review (R6)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance pass)
**Scope**: QC5 format purity implementation and tests against spec §3-1
**Target files**:
- `tools/rbkc/scripts/verify/verify.py:316-376`
- `tools/rbkc/tests/ut/test_verify.py:520-693`
- Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md:85, 197-205`

## Overall Assessment

**Rating**: 4 / 5 — Spec-conformant, tests pass (22/22), but two minor gaps vs. strict spec wording.

## Spec Conformance Check

Spec §3-1 QC5 (`rbkc-verify-quality-design.md:201-203`) prescribes:
- RST: `:role:\`text\`` / `.. directive::` / `.. _label:`
- RST titles only: heading underline `====`, `----`, etc. (content exempted due to legit code-block underlines)
- MD: raw HTML `<[a-zA-Z]…>`, backslash escapes `\*` / `\_` etc.

### Regex-by-regex

| Spec element | Implementation (`verify.py`) | Conformant? |
|---|---|---|
| `:role:\`text\`` | `:[a-zA-Z][a-zA-Z0-9_.-]*:\`` (L319) | Yes — matches role+opening backtick; rejects field-list `:name:` (no backtick). Test L619-627 pins this. |
| `.. directive::` | `^\.\.\s+[A-Za-z][\w:-]*::` with `re.MULTILINE` (L320) | Yes — anchored to line start; empirically verified mid-line text does not false-match. |
| `.. _label:` | `\.\.\s+_[a-zA-Z0-9_-]+:` (L322) | Partial — **not line-anchored** (see Issue M-1). |
| Heading underline (title only) | `^[=\-~^"\'\`#*+<>]{4,}\s*$` MULTILINE (L321); invoked with `is_title=True` only (L327, L359, L365) | Yes — content path at L361, L366 does not pass `is_title`, so code-block `====` is not flagged. Test L611-617 pins this. |
| MD raw HTML `<tag>` | `<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>` (L323) | Yes — covers `<br>`, `<br/>`, `<br />`, `<a href='x'>`, `<img/>`. Verified empirically. |
| MD backslash escape | `\\[*_\`\[\](){}#+\-.!|]` (L324) | Yes — covers all CommonMark ASCII punctuation escapes in the spec examples (`\*`, `\_`). |

### Independence (circular-dependency check)

verify.py imports only `scripts.common.labels.build_label_map` at module top (L22) and AST/normaliser helpers inside functions (L393, L406, L458, L544, L622, L936, L1050). **No import from `scripts.converters`, `scripts.resolver`, `scripts.run`**. QC5 block (L315-376) is self-contained — pure regex + dict access. Independence preserved per `.claude/rules/rbkc.md`.

### Scope gating

- `_check_format_purity` early-returns for `xlsx` and `_no_knowledge` (L350). Test L599-607 pins both.
- RST/MD branches iterate title + content + sections uniformly (L358-375). Correct.

## Key Issues

### Medium

**[M-1] RST label regex is not line-anchored**
- **file:line**: `tools/rbkc/scripts/verify/verify.py:322`
- **Description**: `_RST_LABEL_RE = re.compile(r'\.\.\s+_[a-zA-Z0-9_-]+:')` has no `^` and is not MULTILINE. A literal string like `説明: 次項 .. _foo: を参照` mid-line triggers FAIL, but spec §3-1 QC5 describes this as a *label definition* which in RST grammar is line-initial. The directive regex at L320 is correctly anchored; the label regex should mirror it for consistency.
- **Empirical confirmation**: `_RST_LABEL_RE.search('xx .. _foo:')` → `True`.
- **Proposed fix**: Change to `re.compile(r'^\.\.\s+_[a-zA-Z0-9_-]+:', re.MULTILINE)` and add a positive test `test_pass_rst_label_like_text_mid_line` + keep existing `test_fail_rst_label_in_content` (currently L560-565 places it as the sole content, which still passes with anchored regex).
- **Severity rationale**: Low false-positive probability in practice (Japanese content rarely embeds `.. _xxx:`), but spec says "label definition" which is a line-initial construct. Strict spec purity = anchor it.

**[M-2] RST role regex accepts an unbalanced opening backtick only**
- **file:line**: `tools/rbkc/scripts/verify/verify.py:319`
- **Description**: Spec wording is `:role:\`text\`` (closing backtick present). Regex `:[a-zA-Z][a-zA-Z0-9_.-]*:\`` matches any string with an opening backtick after `:role:`. Example: plain prose `処理時間: 約5秒\`（参考）` — the pattern `:秒:\`` would need a leading ASCII word char so this specific case is safe, but contrived content like `前提: ASCII word ex :s:\`something without close` would FAIL despite no role being present.
- **Empirical confirmation**: `_RST_ROLE_RE.search(':ref:\`x')` (no close) → `True`.
- **Proposed fix**: Either (a) require closing backtick: `:[a-zA-Z][a-zA-Z0-9_.-]*:\`[^\`]+\`` — more spec-literal; or (b) document in verify.py comment that the opening-backtick form is intentional (catches truncated roles too). Option (a) is safer because it aligns with spec example and avoids false positives on heredoc-style content containing raw backticks.
- **Severity rationale**: Real-world Japanese RST source almost never produces `:ident:\`…` without a close, so false-positive risk is low, but spec fidelity is the concern flagged for this review.

### Low

**[L-1] MD backslash escape set does not include all CommonMark punctuation**
- **file:line**: `tools/rbkc/scripts/verify/verify.py:324`
- **Description**: Set is `[*_\`\[\](){}#+\-.!|]` (13 chars). CommonMark allows escape of `~`, `:`, `;`, `"`, `'`, `<`, `>`, `=`, `?`, `@`, `/`, `\\`, `$`, `%`, `&`, `,`. Of these, `~` (strikethrough in GFM) and `\\` (literal backslash) are plausible converter outputs worth catching. Spec §3-1 says "`\*`・`\_` 等" (etc.), so strict spec conformance is already satisfied by the current list for the cited examples, but defensive coverage is incomplete.
- **Proposed fix**: Add `~` and `\\` at minimum: `[*_\`\[\](){}#+\-.!|~\\]`. Add test `test_fail_md_escaped_tilde` and `test_fail_md_escaped_backslash`.
- **Severity rationale**: `\*` and `\_` are by far the dominant cases; other escapes are rare. Low priority.

## Edge-Test Coverage (QA lens)

Reviewed test class `TestVerifyFileQC5` (`test_verify.py:526-693`).

**Positive coverage** (PASS cases, 6):
- Clean RST content (L572)
- Clean MD content (L593)
- xlsx format gated out (L599)
- no_knowledge gated out (L605)
- RST code-block underline in content (L611) — Z-1 gap fill
- RST field-list `:name:` (L619) — Z-1 gap fill
- Japanese punctuation not confused with role (L629) — Z-1 gap fill

**Negative coverage** (FAIL cases, 16):
- RST role/directive/label/title-underline (L546-570)
- MD raw HTML: `<details>`, `<summary>`, `<br>`, `<a>`, `<br/>`, `<hr/>`, `<img/>` (L579-693)
- MD backslash: `\*`, `\_`, `\[`, `\]` (L586, L654, L660)
- Raw HTML inside inline code (L666) — explicitly pinned as FAIL

**Coverage gaps** (not blocking, catalog for completeness):
1. No test covering title field for MD (L368) — all MD fail-tests place content in sections. Add `test_fail_md_raw_html_in_title`.
2. No test for top-level `content` (non-section) path (L361, L370). All FAIL tests target sections. Add `test_fail_rst_role_in_top_level_content`.
3. No test for RST section *title* underline (L365 with `is_title=True`). Current title test at L567 uses top-level title only.
4. Circular / self-reference: no test ensures verify.py does not import from RBKC impl modules. Recommend a metadata test `test_verify_module_has_no_rbkc_impl_imports` parsing verify.py's AST and asserting imports are restricted to `scripts.common.*` / stdlib.

## Positive Aspects

- TDD principle visible: Z-1 gap fills (L611-634) are pinned with explicit spec citations in docstrings.
- Independence-by-construction: QC5 block uses only stdlib `re`; no RBKC impl leak.
- Correct use of `is_title` flag to avoid false positives on code-block content underlines (spec §3-1 L202).
- Self-closing HTML variants `<br/>`, `<hr/>`, `<img/>` all covered (L677-693) — rare but catches converter bugs.
- Raw HTML inside backticks intentionally FAILs (L666-675) — aligns with verify's role as an independent gate.

## Recommendations

1. **Adopt M-1 fix** (anchor label regex). Low-risk, spec-aligned, adds defensive robustness.
2. **Decide M-2 direction** with the user before modifying — requires a project call on whether to be literal-spec strict or catch truncated roles.
3. **Add L-1 coverage** opportunistically (one-line regex change, two tests).
4. **Add coverage-gap tests 1-4** — mechanical, improves detection against converter regressions.
5. **pytest status**: `TestVerifyFileQC5` 22/22 GREEN (verified on this branch).

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py:316-376` (implementation)
- `tools/rbkc/tests/ut/test_verify.py:520-693` (tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md:85, 197-205` (spec §3-1 QC5)
