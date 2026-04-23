# Z-1 r8 Review: QC5 (format purity)

**Target**: `tools/rbkc/scripts/verify/verify.py` lines 448–484
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 QC5 (line 197–205)
**Focus**: r7 Findings F1 (`_RST_ROLE_RE` both-backticks) and F2 (`_RST_LABEL_RE` line-anchored)

## Findings

None.

## Observations

**F1 (role regex — both backticks required) — correctly addressed.**

Spec §3-1 line 201 quotes the pattern as `` `:role:\`text\`` `` — both opening and closing backticks are part of the named construct. Implementation:

```
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`[^`\n]+`')
```

requires the closing backtick and forbids newlines inside the text, matching the spec wording exactly. Tests `test_pass_rst_role_name_without_closing_backtick_not_flagged` (line 883) and `test_fail_rst_role_with_both_backticks_flagged` (line 894) cover both directions.

**F2 (label regex — line-anchored) — correctly addressed.**

Spec §3-1 line 201 names the construct `.. _label:`, which per RST explicit-markup grammar must begin at line start. Implementation:

```
_RST_LABEL_RE = re.compile(r'^\.\.\s+_[a-zA-Z0-9_-]+:\s*$', re.MULTILINE)
```

uses `re.MULTILINE` so `^`/`$` anchor to line boundaries, correctly rejecting mid-sentence occurrences while flagging own-line definitions. Tests `test_pass_rst_label_tokens_in_prose_not_flagged` (line 902) and `test_fail_rst_label_on_its_own_line_flagged` (line 912) cover both directions.

**Other QC5 patterns — consistent with spec.**

- `_RST_DIRECTIVE_RE` (line-anchored, MULTILINE): matches spec `.. directive::`.
- `_RST_HEADING_UNDERLINE_RE`: applied only to titles (`is_title=True`), consistent with spec line 202 ("content フィールドではコードブロック内の `===` や `---` が正当に出現しうるため検査しない"). Test `test_pass_rst_code_block_underline_in_content` (line 858 region) confirms.
- `_MD_RAW_HTML_RE` / `_MD_BACKSLASH_ESCAPE_RE`: match spec line 203 enumeration.
- xlsx short-circuit and `_no_knowledge` early return (line 488) match scope: QC5 is RST/MD only.
