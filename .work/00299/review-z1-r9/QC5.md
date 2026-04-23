# Z-1 r9 QC5 Bias-Avoidance Review

Scope: `_RST_ROLE_RE`, `_RST_LABEL_RE`, `_RST_DIRECTIVE_RE`, `_RST_HEADING_UNDERLINE_RE`, `_MD_RAW_HTML_RE`, `_MD_BACKSLASH_ESCAPE_RE` in `tools/rbkc/scripts/verify/verify.py` (lines 486–518) against `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 QC5 and `TestVerifyFileQC5` in `tools/rbkc/tests/ut/test_verify.py`.

Spec clauses quoted verbatim from the design doc:

- L85 (table row): `**QC5** | 形式純粋性 | フォーマット固有の構文記法が JSON に残留している（RST: `:role:`・`.. directive::` 等、MD: raw HTML・エスケープ文字等）`
- L201: `**RST**: `:role:\`text\`` パターン、`.. directive::` パターン、`.. _label:` ラベル定義`
- L202: `**RST（title フィールドのみ）**: 見出しアンダーライン（`====`、`----` 等）。content フィールドではコードブロック内の `===` や `---` が正当に出現しうるため検査しない`
- L203: `**MD**: `<[a-zA-Z]` で始まる raw HTML タグ（`<details>`、`<summary>`、`<br>` 等）、`\*`・`\_` 等のバックスラッシュエスケープ`
- L205: `いずれかのパターンが検出された場合 → **FAIL（QC5）**`

## Findings

### F1 — `_MD_BACKSLASH_ESCAPE_RE` character class is narrower than the MD escape set that the spec's "等" (etc.) references

Violated clause (L203): ``**MD**: ... `\*`・`\_` 等のバックスラッシュエスケープ``.

The spec names `\*` and `\_` as exemplars (`等` = "etc.") of "backslash escape"; the referent is the CommonMark ASCII-punctuation escape set (`!"#$%&'()*+,-./:;<=>?@[\]^_\`{|}~`). The current class `[*_\`\[\](){}#+\-.!|]` omits `"`, `$`, `%`, `&`, `'`, `,`, `/`, `:`, `;`, `<`, `=`, `>`, `?`, `@`, `\`, `^`, `~`. A JSON fragment containing `\~`, `\<`, `\>`, `\"`, `\\`, or `\:` is a backslash escape that survived into output, but QC5 does not FAIL, contradicting L205's `いずれかのパターンが検出された場合 → FAIL`.

### F2 — `_MD_RAW_HTML_RE` does not match bare closing tags `</tag>`

Violated clause (L85 / L203): ``MD: raw HTML ... （`<details>`、`<summary>`、`<br>` 等）``.

The spec lists `<summary>` as a raw HTML tag whose residue must FAIL. The regex anchors on `<[a-zA-Z]`, which is the spec's opening-tag character class (L203 uses `<[a-zA-Z] で始まる`). A JSON content fragment containing only the closing half of a tag pair — e.g. `内容</summary>残り` with no matching `<summary>` in the same JSON field — is still raw-HTML residue (`形式固有の構文記法が JSON に残留` per L85), but QC5 does not FAIL because the regex never matches `</…>`. Test `test_fail_md_summary_tag` only pins the paired form.

### F3 — `_RST_HEADING_UNDERLINE_RE` character class omits valid RST adornment characters

Violated clause (L202): `見出しアンダーライン（`====`、`----` 等）`. The `等` (etc.) references the full RST adornment-character set. RST (`docutils` spec) permits any of `! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ \` { | } ~` as title-adornment characters. The regex class `[=\-~^"'\`#*+<>]` covers 11 of these and omits `!`, `$`, `%`, `&`, `(`, `)`, `,`, `.`, `/`, `:`, `;`, `?`, `@`, `[`, `\`, `]`, `_`, `{`, `|`, `}`. A JSON `title` field emitted as `!!!!!` or `~~~~` (the latter is covered, but e.g. `@@@@@` is not) is RST heading-underline residue that does not FAIL QC5.

### F4 — `_RST_HEADING_UNDERLINE_RE` minimum length `{4,}` is stricter than any spec-stated bound

Violated clause (L202): `見出しアンダーライン（`====`、`----` 等）`. The spec's exemplars are 4-character runs but state no minimum. RST itself requires the underline to be at least as long as the title (minimum 1 character for a 1-character title). A 3-character residue such as `===` in a title field is a heading-underline residue by the spec's plain reading, but the `{4,}` quantifier prevents QC5 from failing on it. There is no spec clause that sanctions a 4-character floor.

### F5 — `_MD_RAW_HTML_RE` does not match HTML comments, CDATA, or processing instructions

Observation, not a finding: the spec clause L203 literally restricts MD raw-HTML matching to `<[a-zA-Z] で始まる` tags. `<!-- … -->`, `<![CDATA[ … ]]>`, and `<?…?>` begin with `<!` / `<?` and are therefore outside the spec's named pattern. The regex's behaviour aligns with the spec wording. Recording only so that future reviewers do not re-raise this as a gap.

## Observations (spec-silent)

### O1 — `_RST_ROLE_RE` has no line anchoring

The spec pattern `:role:\`text\`` is inline by nature, and the regex correctly does not anchor. Noted only because inline matching means a pathological mid-sentence sequence like `text:name:\`x\`` — where `:name:\`x\`` is coincidentally formed from adjacent tokens — would FAIL QC5. Under ゼロトレランス this bias is in the safe direction (prefer FAIL to miss).

### O2 — `_RST_LABEL_RE` does not match the backtick-quoted label form `.. _\`label with spaces\`:`

The spec quotes `.. _label:` as the named pattern. Docutils also recognises the backtick-quoted form for labels with non-word characters. Spec is silent on whether the quoted form is in-scope; current regex does not detect it.

### O3 — `_RST_DIRECTIVE_RE` accepts `:` inside directive names via `[\w:-]`

This is correct for domain-prefixed directives (`.. py:function::`) and matches no spec clause negatively. Noted.

### O4 — `_MD_RAW_HTML_RE` tag-name class `[a-zA-Z][a-zA-Z0-9]*` rejects hyphenated custom elements

A custom element like `<my-widget>` starts with `<[a-zA-Z]` (satisfies L203's stated start) but its full name contains `-`. The regex requires the remainder to be `[a-zA-Z0-9]*`, so the match terminates early at `<my` followed by `-widget>`. Because `<my` alone is still matched (the regex permits `<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>` and `>` need not close immediately if `\s[^>]*` matches — but there is no whitespace here), actually `<my-widget>` is NOT matched at all by this regex (no `>` reached after the truncated tag name, and no whitespace to enter the attribute branch). Spec is silent on custom-element tags; L203 names only standard tags.

### O5 — `test_pass_rst_field_list_syntax_is_not_qc5_role` relies on the role regex requiring a backtick-delimited argument

This is consistent with the rbkc.md "Decide from the spec" entry (`Yes. Spec §3-1 QC5 writes :role:\`text\` (both backticks)`). Recorded for completeness; no finding.
