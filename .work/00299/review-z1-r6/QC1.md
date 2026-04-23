# QC1 完全性 — Independent QA Review (Z1-R6)

**Reviewer role**: Independent QA Engineer (bias-avoidance)
**Spec of record**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (QC1–QC5 共通手順 0/1–4 + 残存判定 + Excel 節)
**Note on §3-1b**: the spec does not contain a literally numbered §3-1b; the §3-1 "手順 0 / 原則" subsections codify the zero-exception principles referenced by the RBKC implementation as "§3-1b" in code comments. This review treats those as part of §3-1.
**Principle**: spec is authoritative; v6 passing is weak evidence (circular if tests simply mirror current output).

---

## 1. Implementation vs spec

### 1a. RST path (`_check_rst_content_completeness`, `verify.py:530-609`)

| Spec requirement | Implementation | Assessment |
|---|---|---|
| Zero-exception: unknown node / role / unresolved ref / parse error → QC1 FAIL (spec §3-1 手順 0 原則 + 対応表原則 3) | `rst_normaliser.normalise_rst(..., strict_unknown=True)` raises `UnknownSyntaxError`; `verify.py:547-549` catches and emits `[QC1] RST parse/visitor error`. No silent fallback to children/text. | ✅ Spec-conformant |
| No silent drop of information | `rst_normaliser.py:58-67` re-raises on any docutils warning `(ERROR/3|4)` line or Visitor exception. | ✅ |
| Residue check: "空白・改行・タブ以外のテキストが残れば FAIL" with no tolerance list (§3-1 手順 3 + 残存判定の基準) | `verify.py:596-607` performs sequential delete of JSON units from `norm_source` then `residue.strip()` check with no allow-list. | ✅ |
| Sequential delete in JSON order (§3-1 手順 1-4) | `verify.py:570-589` — uses `find(.., current_pos)` for forward scan and raises QC3 if the match lies inside a consumed span (`_in_consumed`), QC4 for position regression, QC2 for absent. | ✅ |

**⚠️ Observation (Medium)**: Between `norm_source_raw` (visitor output) and the consumed-residue comparison, `verify.py:551-557` applies **extra post-processing** that is not part of the visitor: image-markup stripping (`![…](…)` removed to empty), link-text collapse (`[t](u)` → `t`), and `\s+` → single-space. The spec §3-1 残存判定の基準 states:
> "Visitor が出力する正規化ソースと、JSON 側の MD は**完全に同じ記法で揃っている**前提で sequential-delete を行う"
> "許容構文要素リスト・許容残存パターンといった例外リストは**設けない**"
>
> "**JSON content の MD 記法も create 側が `scripts/common/rst_ast_visitor.py` 経由で出力し、verify 側の正規化ソースと同じヘルパー (`scripts/common/rst_ast.py` の `escape_cell_text` / `normalise_raw_html` / `fill_merged_cells`) を使う**"

The image-removal + link-text-collapse step is effectively a verify-side post-normaliser that the spec does not authorise. If the JSON side does not go through the same normalisation, matching hides a true gap; if it does, the post-processing should live in the shared helper per the 原則. This is a latent violation of 2-2 (独立性: 片側ヘルパー依存).

**⚠️ Observation (Low)**: RST residue reporting (`verify.py:605-607`) emits only **one truncated snippet**, while the MD path (`verify.py:706-710`) iterates all non-whitespace fragments. An operator reading a FAIL sees a single 80-char excerpt even if multiple content gaps exist. Not a correctness bug but a detection-surface asymmetry.

### 1b. MD path (`_check_md_content_completeness`, `verify.py:612-712`)

| Spec requirement | Implementation | Assessment |
|---|---|---|
| Zero-exception on unknown markdown-it token | `md_normaliser.normalise_md(..., strict_unknown=True)` → raises `UnknownSyntaxError`; `verify.py:626-628` emits `[QC1] markdown parse/visitor error`. | ✅ |
| Residue = 空白以外 → FAIL, no tolerance | `verify.py:686-710` merges consumed spans, computes remainder, reports every non-empty fragment. | ✅ |
| Sequential delete order | `verify.py:665-684`: JSON-order scan with `find(unit, current_pos)`, position-regression → QC4, consumed-overlap → QC3, absent → QC2. | ✅ |

### 1c. Excel path (`_verify_xlsx`, `verify.py:769-831`)

| Spec requirement | Implementation | Assessment |
|---|---|---|
| Delete direction reversed: source cells deleted from JSON text (§3-1 Excel 節) | `verify.py:789-801` — for each cell token, `json_text.find(token, search_start)`. Absent → QC1. Consumed-overlap → QC3. | ✅ Direction correct |
| QC1 欠落: 見つからなかったセル値 → FAIL | `verify.py:797, 801` both emit `[QC1] Excel cell value missing from JSON` (two branches — absent vs. only-in-consumed-region). | ✅ |
| .xls と .xlsx 両対応 | `verify.py:731-756` — xlrd for .xls, openpyxl for .xlsx. Numeric cells via `str(cell)`. | ✅ |
| 空セル除外、行優先・列順 (§3-1 Excel 節 ソーストークン構築) | `verify.py:737-755` iterate rows then cells, `.strip()`, drop empty. | ✅ |

**✅ No silent fallback found** across RST / MD / Excel QC1 paths.

---

## 2. Unit tests — coverage, edges, circularity

**File**: `tools/rbkc/tests/ut/test_verify.py` (class `TestCheckContentCompleteness` L840–1232, class `TestVerifyFileExcel` L1236–1380)

### Spec FAIL-condition coverage

| Spec FAIL condition | Test(s) | Asserts what |
|---|---|---|
| §3-1 判定分岐: 対応表未登録 node/role | `test_fail_qc1_rst_unknown_role_surfaces` (L1087), `test_fail_qc1_md_unknown_token_surfaces` (L1045) | `[QC1]` + "parse/visitor error" |
| §3-1 判定分岐: 未解決 reference / substitution | `test_fail_qc1_rst_unresolved_substitution_surfaces` (L1069) | `[QC1]` + "RST parse/visitor error" |
| §3-1 判定分岐: docutils parse error | `test_fail_qc1_rst_parse_error_level_3` (L1078) | `[QC1]` + parse-error message |
| §3-1 手順 3: 残存テキスト → FAIL | `test_fail_qc1_residual_content` (L895) | `[QC1]` |
| §3-1 Excel 節 手順 2: セル値未出現 → QC1 | `test_fail_cell_missing_from_json` (L1261), `test_fail_xls_cell_missing_from_json` (L1323), `test_fail_xls_numeric_cell_missing_from_json` (L1347) | `QC1` |

**All spec-level QC1 FAIL conditions have at least one assertion.**

### Edge cases

- ✅ `test_fail_qc2_one_char_fabrication_detected` (L1297) — explicitly checks the 1-char residue is NOT silently dropped (guards against regression toward a tolerance list).
- ✅ `test_pass_rst_comment_line_is_syntax` / `test_pass_rst_comment_block_with_indented_body` (L999, L1008) — comment-only residue must PASS (boundary between QC1 residue and RST syntax).
- ✅ `test_pass_rst_field_list_with_separate_value` / `with_inline_value` (L1022, L1031) — field-list visitor output alignment.
- ✅ `test_pass_qc3_short_cjk_repeated_in_source_and_json` (L1140) — short-CJK collision must not over-trigger (prevents false QC3 that would mask a true QC1 elsewhere).
- ✅ `test_pass_rst_ref_label_resolved_text` (L970) — label-resolved ref path.

### Gaps

**⚠️ (Medium) No test for `_no_knowledge(data)` returning early when `no_knowledge_content: true`** on RST/MD content completeness at the QC1 level (there is one for Excel, L1272). A regression that drops the guard on RST/MD would silently pass all no-knowledge files without any QC1 check. Easy gap-fill.

**⚠️ (Medium) No test asserts that RST residue reporting covers multiple fragments.** Given the MD path reports all fragments but RST only one, a test pinning the expected multi-fragment behaviour would prevent silent convergence on single-snippet reports that hide additional gaps.

**⚠️ (Low) No test for the verify.py:551-557 image/link post-normalisation**. If that block is removed or reordered, no assertion catches a regression in either direction (nor documents whether the behaviour is intentional). If the post-processing is necessary per spec alignment, a test should lock it; if it is not, it should be deleted (see Impl observation 1a).

**⚠️ (Low) No QC1 Excel test for `.xls` + residue QC2 only (positive QC1 path is present, but cross-format parity on the 1-char fabrication edge is only tested for .xlsx).**

### Circularity check

Tests are **not circular** with the RBKC converter:
- They construct hand-written `src` (raw RST/MD/xlsx workbooks) and hand-written `data` dicts, then call `check_content_completeness` / `verify_file` directly.
- FAIL/PASS assertions key off semantic outcomes (`"QC1" in issues`), not implementation-private strings beyond the stable `[QC1]` / `[QC2]` prefixes defined by verify's public contract.
- The zero-exception tests inject an unknown markdown-it `Token` (`test_fail_qc1_md_unknown_token_surfaces`, L1045-1067) — this bypasses the converter entirely and asserts the verify-side strict path. That is the opposite of circular: it exercises a code path the converter can never reach.

---

## 3. v6 runtime

```
cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
→ 0
# tail -3 →
All files verified OK

cd tools/rbkc && python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 221 passed in 2.18s ==============================
```

**Bias-avoidance stance**: v6 FAIL = 0 is consistent with the strict implementation, but **v6 passing alone is weak evidence** for QC1 correctness because v6 could have been tuned until it passes. The unit-test evidence above (spec-level FAIL assertions on parse-error / unknown role / unresolved substitution / residue) is what establishes that the check actually fires, because those tests are independent of what v6 currently looks like.

---

## 4. 総合: ⚠️

QC1 implementation conforms to §3-1's zero-exception and no-tolerance principles across RST / MD / Excel, and tests independently pin the spec FAIL conditions rather than v6 output. However, three medium items prevent a ✅:

1. **RST post-normalisation at `verify.py:551-557`** is not anchored by spec or test. Either move into the shared visitor helper (per 残存判定の基準 last paragraph) or delete and let the visitor be the single source of truth. As-is it is an unmarked verify-side exception path.
2. **RST residue reporting collapses to one snippet** (`verify.py:605-607`) while MD reports all — inconsistent detection surface; a file with multiple content gaps currently surfaces only the first 80 chars of residue.
3. **Missing tests**: no `no_knowledge_content: true` early-return test for RST/MD QC1; no multi-fragment residue test; no lock on the L551-557 post-processing.

Not yet ❌ because each item is a refinement, not a silent-fallback hole. A regression or spec-drift could, however, turn item 1 into a zero-exception bypass.

---

## 5. 改善案

### (Medium) Align RST residue normalisation with spec 残存判定の基準
Move the image/link/whitespace normalisation currently at `verify.py:551-557` into the shared `rst_ast`/`rst_ast_visitor` helper so that both create-side JSON content and verify-side normalised source go through identical code. If the step is redundant once the visitor is authoritative, delete the block. Either path eliminates the current "two-step normalisation with verify owning step 2" which violates 2-2.

### (Medium) Make RST residue reporting symmetric with MD
Change `verify.py:605-607` to iterate `residue.split()` like MD (`verify.py:708-710`) and emit one `[QC1]` per fragment. Add a test: three separate residues → exactly three `[QC1]` entries.

### (Medium) Add no-knowledge guard test for RST/MD QC1
Mirror `test_pass_no_knowledge_content_skipped` (Excel) for RST and MD: a file with `no_knowledge_content: true` must return `[]` from `check_content_completeness` regardless of source residue. Pins `verify.py:511-512`.

### (Low) Lock the post-normalisation behaviour with a test (if kept)
If the L551-557 block stays, add a test with an RST image/link whose MD form would otherwise look like residue, asserting PASS. Currently its behaviour is structurally unobserved.

### (Low) Cross-format Excel parity for 1-char fabrication
Add `.xls` counterpart of `test_fail_qc2_one_char_fabrication_detected` to guard against xlrd-side regressions.

---

## Files cited

- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (L75–226)
- `tools/rbkc/scripts/verify/verify.py` L509–527 (dispatch), L530–609 (RST), L612–712 (MD), L769–831 (Excel)
- `tools/rbkc/scripts/common/rst_normaliser.py` L28, L37–67 (zero-exception)
- `tools/rbkc/scripts/common/md_normaliser.py` L22, L46–61 (zero-exception)
- `tools/rbkc/tests/ut/test_verify.py` L840–1232 (`TestCheckContentCompleteness`), L1236–1380 (`TestVerifyFileExcel`)
