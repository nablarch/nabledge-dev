# Z-1 r7 Bias-Avoidance Review: QC5 (format purity)

**Target**: `tools/rbkc/scripts/verify/verify.py` lines 316–346
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 QC5 (lines 197–205)

## Spec clauses

> §3-1 QC5 (line 201):
> **RST**: `:role:\`text\`` パターン、`.. directive::` パターン、`.. _label:` ラベル定義

> §3-1 QC5 (line 202):
> **RST（title フィールドのみ）**: 見出しアンダーライン（`====`、`----` 等）。content フィールドではコードブロック内の `===` や `---` が正当に出現しうるため検査しない

> §3-1 QC5 (line 203):
> **MD**: `<[a-zA-Z]` で始まる raw HTML タグ（`<details>`、`<summary>`、`<br>` 等）、`\*`・`\_` 等のバックスラッシュエスケープ

> `.claude/rules/rbkc.md` — "Decide from the spec":
> "`:role:` regex — must the closing backtick be required per spec wording?"
> → "Yes. Spec §3-1 QC5 writes `:role:\`text\`` (both backticks)."

---

## Findings

### F1. `_RST_ROLE_RE` does not require the closing backtick — Finding

Current:

```
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`')
```

Spec quotes `:role:\`text\`` — the closing backtick is part of the pattern, and the rbkc ruleset (quoted above) explicitly records the decision that "both backticks" are required.

The regex matches only `:name:` + one opening backtick. It does not require `text` nor the closing backtick. Any line that contains the literal sequence `:foo:\`` with no closing backtick (for example a malformed code sample or docstring fragment) will be flagged as an unprocessed role, even though it is not the pattern the spec names. Conversely, the regex does not prove that a real role (with closing backtick) is present — it accepts a strict subset that omits the closing delimiter.

Per the project rule "Spec §3-1 QC5 writes `:role:\`text\`` (both backticks)", the closing backtick must be in the regex. Missing = spec drift.

**Proposed fix**:

```python
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`[^`\n]+`')
```

(require at least one non-backtick character, then the closing backtick; `\n` excluded so a single unterminated backtick spanning lines is not silently absorbed).

Add a bug-revealing test: `:foo:` followed by a single backtick and no closing backtick must NOT FAIL QC5 (not a role per spec); `:foo:\`bar\`` must FAIL.

---

### F2. `_RST_LABEL_RE` is not line-anchored — Finding

Current:

```
_RST_LABEL_RE = re.compile(r'\.\.\s+_[a-zA-Z0-9_-]+:')
```

Spec writes `.. _label:` as the RST **label definition** form. RST label definitions are explicit-markup constructs that by the reStructuredText specification must begin at the start of a line (optionally after block indentation), never mid-sentence. The regex has no `^` and no `re.MULTILINE` flag, so it matches `.. _foo:` anywhere in a line — including inside prose, code fences, or residue from MD conversion (e.g. a sentence containing `see .. _foo: below`).

This produces false positives: a content string that legitimately contains the literal tokens `.. _x:` mid-line (not as a label definition) will be FAILed. The QC5 check is meant to flag residue of the structured construct, not the character sequence.

Compare to `_RST_DIRECTIVE_RE` on the next line, which **is** correctly anchored with `^` + `re.MULTILINE`. The label regex should follow the same treatment.

**Proposed fix**:

```python
_RST_LABEL_RE = re.compile(r'^\.\.\s+_[a-zA-Z0-9_-]+:\s*$', re.MULTILINE)
```

(anchor both ends; a label definition ends the line — no inline trailer).

Add a bug-revealing test: `"text with .. _foo: embedded in sentence"` must NOT FAIL QC5 (not a label definition); a line that IS `.. _foo:` must FAIL.

---

## Observations (non-blocking, spec-silent)

- **O1** `_RST_ROLE_RE` also has no left-side boundary, so `abc:role:\`x\`` matches. RST roles in practice only follow whitespace or line start, but the spec does not quote a boundary requirement, so this is not a Finding — only a note for possible precision hardening alongside F1.
- **O2** `_MD_BACKSLASH_ESCAPE_RE` and `_MD_RAW_HTML_RE` match the spec §3-1 line 203 examples directly and are not anchored (correctly — MD residue can appear mid-line).
- **O3** `_RST_DIRECTIVE_RE` and `_RST_HEADING_UNDERLINE_RE` are both anchored with `^` + `re.MULTILINE` and match the spec wording. No Finding.

---

## Summary

Two Findings, both spec-drift:
- F1: `_RST_ROLE_RE` is missing the closing backtick required by §3-1 line 201 + rbkc.md decision.
- F2: `_RST_LABEL_RE` is not line-anchored, accepting non-label character sequences as label definitions.

Both are fixable with minimal regex changes plus one added bug-revealing test each.
