# Notes: Issue #335 — verify QC2 MD syntax exemption fix

## 2026-05-13

### Investigation: _MD_SYNTAX_RE spec basis audit

`_MD_SYNTAX_RE` (verify.py:1047–1068) strips the following tokens before QC2 residue check:

| Token | Comment in code | Spec basis |
|-------|-----------------|------------|
| `\|[-:]+\|(?:[-:]+\|)*` | GFM table separator row | **None** — spec §3-1 Excel節 手順3 says any non-whitespace residue → FAIL. No table separator exemption. |
| `\|` | GFM table pipe | **None** — same as above |
| `-{3,}` | `---` explicitly named as allowed residue | **Fabricated** — spec §3-1 makes no such claim. The comment "Spec §3-1 Excel 節 explicitly names `---` as an allowed residue" is a false citation. Verified by reading the full §3-1 text. |
| `\*\*\|\*` | Markdown bold/italic | **None** |
| `__(?![\w])\|(?<![\w])__` | Markdown bold (underscores) | **None** |
| `^#+\s*` | Markdown heading | **None** |
| `^>\s*` | Markdown blockquote | **None** |
| `^\d+\.\s+` | Markdown ordered list | **None** |
| `` ` `` | Markdown inline code | **None** |
| `:` | P1 structural delimiter | **Partial spec basis** — `rbkc-converter-design.md §8-4` defines P1 section.content as `{列名}: {値}` format, so the `:` separator is a JSON schema artifact. **BUT the current implementation applies this to ALL sheets, not just P1.** |

### Spec citation verification

Searched `rbkc-verify-quality-design.md` for: `---`, `tolerance`, `allowed`, `exempt`, `exclude` in §3-1 Excel節 context.

**§3-1 手順3 actual text** (line 243):
> QC2（捏造）: 全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL

No exceptions listed. The spec is unambiguous.

### P1 colon exception — legitimate but scope is wrong

`rbkc-converter-design.md §8-4` specifies that P1 sheet section.content lines follow `{列名}: {値}` format. The `:` separator comes from the JSON schema, not from any Excel cell value. Therefore, a standalone `:` residue in a P1 sheet is a structural artifact and not QC2 fabrication.

However, the current `_MD_SYNTAX_RE` applies `:` exemption to ALL sheets (P1 and P2). For P2 sheets, if `:` appears in JSON but not in any Excel cell, it IS fabrication and must be detected.

### Test test_pass_qc2_standalone_triple_dash_is_tolerance_allowed (line 1839)

This test asserts that `---` in JSON does not trigger QC2. Its docstring says:
> "spec §3-1 Excel 節 lists `---` explicitly as an allowed residue"

This is a fabricated spec citation — the spec makes no such claim. The test verifies incorrect behavior.

### `: ` residue reproduction

The tasks.md notes that P1 colon residue is already reproduced/confirmed. The current `_MD_SYNTAX_RE` removes `:` globally, masking fabrication bugs in P2 sheets.

### Fix design

1. **Remove `_MD_SYNTAX_RE` entirely** — no token in this regex has spec backing for universal exemption
2. **Replace with P1-scoped colon strip** — for `sheet_type == "P1"` only, strip standalone `:` from residual before token-check
3. **Delete `test_pass_qc2_standalone_triple_dash_is_tolerance_allowed`** — fabricated spec citation, incorrect expected behavior
4. **Add `test_fail_qc2_pipe_char_fabrication`** — `|` in JSON without source → FAIL
5. **Add `test_fail_qc2_triple_dash_fabrication`** — `---` in JSON without source → FAIL
6. **Update design spec §3-1** — document P1 colon exception with spec basis

### rbkc-converter-design.md §8-4 reference

```
rbkc-converter-design.md §8-4: P1 JSON スキーマ
section.content: {列名}: {値} 形式（列名はヘッダ行セル値、値はデータ行セル値）
```
This is the **only** legitimate basis for any exemption in Excel QC2.
