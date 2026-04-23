# QL1 bias-avoidance review (z1-r9)

Target: `check_source_links` in `tools/rbkc/scripts/verify/verify.py` (lines 1094-1325)
Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
Tests: `TestCheckSourceLinks` in `tools/rbkc/tests/ut/test_verify.py` (line 1905)

---

## Findings

### F1. `literal_block` (`.. literalinclude::` 由来) is not checked by QL1

Spec §3-2 QL1 table row:

> | `literal_block` (`.. literalinclude::` 由来) | 参照先コードの本文 (`:lines:` / `:start-after:` / `:end-before:` 考慮) | コード本文が JSON content に含まれているか | コードブロックとして含まれているか |

Implementation explicitly opts out at verify.py:1293-1294:

> `# NOTE: literal_block content is covered by QC1/QC2 (sequential-delete`
> `# across the full JSON content), so we don't re-check it here.`

The spec lists literalinclude as a distinct QL1 row. Delegating to QC1/QC2 is not a sanction the spec grants; QC1/QC2 and QL1 are independent quality dimensions (§3-1 vs §3-2). If QC1 ever changes semantics or literalinclude content is inlined differently, QL1 silently stops enforcing this row. This is a silent-skip of a spec row.

### F2. RST named reference target restricted to `nodes.section`

verify.py:1188:

> `if target is None or not isinstance(target, nodes.section):`
> `    continue`

Spec §3-2 QL1 row 1 says:

> | `reference` (`refid` / `refname`、refuri なし) | label 解決後のタイトル | ... |

Spec does not restrict the target type to `section`. RST `.. _label:` can precede figures, tables, or arbitrary block elements; such targets are silently skipped by the `isinstance(target, nodes.section)` guard. The spec says "label 解決後のタイトル" — for non-section targets the resolver in `label_map` already produces the appropriate string, but this code path short-circuits before consulting `label_map`.

### F3. Cross-document RST named references silently skipped

verify.py:1180-1189: cross-document named references (`` `Foo`_ `` where `.. _foo:` is defined in another file) are not resolved by `doctree.ids` — only same-doc labels live there. The code path `doctree.ids.get(refid)` returns `None` for cross-doc refs, hitting the `continue` at line 1188.

Spec §3-2 explicitly mandates cross-doc resolution:

> label 解決は `scripts/common/labels.py` の `build_label_map` で得た cross-document map を併用する (docutils 単体では cross-doc ref を解決しない)

`label_map` is only consulted inside `_resolve_title_inline` (for embedded refs in a title) and in the `:ref:` role branch. Native named-reference cross-doc resolution through `label_map` is missing.

### F4. Bare `:ref:` label with unknown label is silently skipped

verify.py:1229-1235:

> `if not display and label not in seen_labels:`
> `    seen_labels.add(label)`
> `    title = label_map.get(label)`
> `    if title and title not in json_full:`  ← silent skip when `title` is falsy

When `label_map.get(label)` returns `None` (unresolvable label), the check is silently skipped. Spec §3-2 does not sanction this skip for QL1. (QC5 catches malformed `:ref:` syntax, not unresolvable labels.)

### F5. MD `#anchor` links excluded from QL1 despite spec wording

`scripts/common/md_ast_visitor.py:413`:

> `elif href and not href.startswith(("mailto:", "tel:", "javascript:", "#")):`

Spec §3-2 QL1 Markdown row:

> | Markdown `link_open` (`href` が外部 URL でない) | リンクテキスト | ... |

The spec's exclusion criterion is only "外部 URL でない". In-document anchor links (`#foo`) are internal references whose link text should be checked. Excluding them is not sanctioned by the spec text.

### F6. `:ref:` role detection depends on `inline` node with `role-ref` class

verify.py:1208-1214: only `nodes.inline` with a `role-ref` class is examined. If the docutils / Sphinx shim produces `pending_xref` or a different node type for `:ref:` (depending on parser configuration in `rst_ast.py`), those references are silently skipped. Spec §3-2 does not tie detection to a specific AST shape; it says "ソース AST から内部リンク候補を収集する" and lists `reference` / `refid` semantics.

---

## Observations

### O1. MD image fallback order

verify.py:1318 uses `alt or title or filename`. Spec §3-2 row for Markdown image lists "`alt` / `title` / `src` のファイル名" — the `/` is ambiguous between "any of" and "in priority order". First-match OR is a reasonable reading. Not a finding.

### O2. Dedup by first-seen string

verify.py:1254/1276/1305/1316 dedupe by the check text. Spec is silent on dedup behaviour for QL1; since every unique candidate is still checked, this does not hide gaps. Not a finding.

### O3. `_under_substitution` exclusion for figure/image

verify.py:1237-1251 excludes figure/image under substitution_definition. Spec is silent; `.claude/rules/rbkc.md` records this decision explicitly. Spec-permitted.

### O4. `doctree` parse failure → return empty (line 1166)

verify.py:1161-1166 returns empty on docutils exception, with comment "QC1 will already have flagged it". Spec §3-2 does not grant QL1 a dependency on QC1. This is a silent skip of QL1 on parse failure. Borderline — leaving as observation because QC1 does catch the parse failure condition itself, so no defect escapes the verify suite as a whole. If treated strictly under zero-tolerance, this would be F7.
