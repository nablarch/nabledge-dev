# QC2 正確性 (Accuracy — no fabrication) — QA Engineer Review (r3)

**Reviewer**: Independent QA Engineer (bias-avoidance; spec as authoritative; prior r2 review not consulted during evaluation)
**Date**: 2026-04-23
**Scope**: `tools/rbkc/scripts/verify/verify.py` QC2 logic + unit tests + v6 runtime behaviour
**Stance**: v6 PASS treated as weak evidence; fault injection used to confirm.

---

## 1. Implementation

### RST / MD — `check_content_completeness`

- RST branch (`tools/rbkc/scripts/verify/verify.py:679-758`)
  - Sequential `norm_source.find(norm_unit, current_pos)` fails → second `norm_source.find(norm_unit)` with no offset (verify.py:725).
  - `prev_idx == -1` + title → `[QC2] fabricated title` (verify.py:728)
  - `prev_idx == -1` + content → `[QC2] fabricated content` (verify.py:734)
  - Otherwise QC3 (in consumed) / QC4 (misplaced).
  - `UnknownSyntaxError` surfaces as `[QC1]` (verify.py:696-698) — no silent fallback hiding QC2.
- MD branch (`verify.py:761-861`)
  - Same decision tree on `_squash`-normalised text (verify.py:814-833).
  - `UnknownSyntaxError` → `[QC1]` (verify.py:775-777).
- Top-level `title`/`content` injected as `__top__` search units (verify.py:638-642 for RST via `_build_rst_search_units`; verify.py:791-793 for MD). Top-level fabrications are in scope.

**Spec conformance (§3-1 手順 4)**
- 「JSON テキストが正規化ソースに全く存在せず → QC2」: matched via `prev_idx == -1`. ✅
- QC2 vs QC3 split (never-appeared vs consumed) via `_in_consumed` (verify.py:715-717, 810-812). ✅
- No length tolerance, no silent drops on this path. ✅

### Excel — `_verify_xlsx`

- Direction-inverted scheme (verify.py:918-980).
- QC2 residual emission (verify.py:974-978):
  ```
  residual_plain = _MD_SYNTAX_RE.sub(" ", residual)
  for token in residual_plain.split():
      t = token.strip()
      if t:
          issues.append(f"[QC2] JSON token not found in Excel source: {token!r}")
  ```
- **1-char tolerance is GONE.** Explicit comment at verify.py:972-973 states「No length tolerance — a 1-char residue is still a fabrication.」This closes the r2 H1 finding.
- `_MD_SYNTAX_RE` (verify.py:868-877) still absorbs MD markup residue (`|`, `**`, `#`, `>`, backtick, digit-dot, `|---|`). This matches spec §3-1 Excel 節「許容構文要素リスト」.

**Spec conformance (§3-1 Excel 節)**
- 手順 1 (削除) / 手順 2 (QC1) / 手順 4 (QC3): ✅
- 手順 3 (QC2 残存)「空白・空行を除く」: ✅ (length tolerance removed)
- 「許容構文要素リスト」(`|`, `---`, `**` 等): ✅ regex at verify.py:868-877

**Remaining concerns**
- 🟡 **Medium — `.xls` path untested.** verify.py:881-892 (`xlrd` branch) has zero integration tests. v6 source corpus contains no `.xls` so v6 PASS provides **no evidence** of correctness on this branch. v1.2/v1.3 sources (planned versions) contain .xls release-note files — the branch will be exercised without a regression guard.
- 🟡 **Medium — numeric cell coercion on .xls is untested.** `xlrd` returns numbers as floats; the code does `str(sheet.cell_value(rx, cx)).strip()`, which can produce `"1.0"` for a cell displaying `1`. If RBKC JSON contains `"1"`, a false QC1 + false QC2 residue pair can arise. No test pins this.
- 🟢 **Low — `_MD_SYNTAX_RE` acts as a non-trivial spec-level tolerance.** An adversarial JSON payload consisting solely of `"** ** |"` is silently absorbed. This is spec-intended but no test codifies the exact allowlist, so any regex edit will not be caught by tests.

---

## 2. Unit tests

### Present coverage (`tools/rbkc/tests/ut/test_verify.py`)

| Test | Line | Covers |
|------|------|--------|
| `test_fail_qc2_fabricated_title` | L765 | RST section title not in source |
| `test_fail_qc2_fabricated_content` | L773 | RST section content not in source |
| `test_fail_qc2_multiple_fabricated_contents` | L989 | 2 sections both fabricated — count assertion |
| `test_fail_qc2_top_level_fabricated_content` | L999 | Top-level `content` fabricated (`__top__` path) |
| `test_fail_qc2_near_miss_one_char_differs` | L1006 | `ABCDEFG`→`ABCXEFG` (ASCII near-miss) |
| `test_fail_qc2_fabricated_content_in_json` | L1121 | Excel QC2 multi-char fabrication |
| `test_fail_qc2_one_char_fabrication_detected` | L1139 | **Excel 1-char fabrication** — pins r2 H1 fix |

### Distinction QC2 vs QC3
- RST: `test_fail_qc3_duplicate_title` (L783), `test_fail_qc3_duplicate_content_rst` (L1014), `test_fail_qc3_duplicate_title_md` (L1023), `test_fail_qc3_duplicate_content_md` (L1032)
- Excel: `test_fail_qc3_duplicate_cell_in_json` (L1156)
The QC2 ↔ QC3 branching (never-seen vs already-consumed) is exercised by both sides. ✅

### Circular-test check
Each test builds source + JSON independently and asserts on the issue kind string (`"QC2"`, `"fabricated"`). Tests call only the public entry points `check_content_completeness` / `verify_file`. No test imports internal helpers or reuses verify.py private constants. **No circular tests.** ✅

### Gaps (confirmed by grep; r2 M1 items still open)

| # | Missing | Severity | Evidence |
|---|---------|----------|----------|
| G1 | `.xls` path: **no test** | 🔴 High | `grep "xls\|xlrd"` in test_verify.py → only `xlsx` matches. verify.py:881-892 branch has 0 lines of test coverage. Same finding as r2 H2 — **still unfixed**. |
| G2 | QC2 top-level fabricated **title** (RST) | 🟡 Medium | Only `fabricated content` top-level case is covered (L999). The title branch at verify.py:728 on `__top__` sid is unpinned. |
| G3 | QC2 near-miss in **CJK** | 🟡 Medium | L1006 is ASCII only. CJK differs (no whitespace tokenisation). Fault-injection below confirms it works, but no regression guard. |
| G4 | QC2 on **MD** fabricated content | 🟡 Medium | The MD branch QC2 lines (verify.py:823, 829) are only transitively hit by QC3/QC4 MD tests. No direct QC2 MD assertion. Fault-injection below fires it. |
| G5 | QC2 **cross-boundary** fabrication (JSON spans two non-contiguous source blocks) | 🟢 Low | Current impl (via `\s+` collapse) flags it; no test codifies. |
| G6 | Excel `_MD_SYNTAX_RE` allowlist not pinned | 🟢 Low | Regex edits silently change which payloads pass. No enumeration test. |
| G7 | Excel .xls numeric cell coercion | 🟡 Medium | `"1" → "1.0"` drift between xls and xlsx untested; tied to G1. |

### Edge-case matrix summary

| Edge case | Tested? | Fault-injection result |
|-----------|---------|------------------------|
| Whitespace-only residue (Excel) | Implicitly via pass cases | ✅ not flagged (spec-correct) |
| Whitespace-only JSON unit (RST) | No | Degrades to QC1 (content empty after squash); spec-acceptable |
| CJK 1-char diff (RST) | No (G3) | ✅ QC2 fires |
| MD QC2 content | No (G4) | ✅ QC2 fires |
| Top-level RST fabricated title | No (G2) | ✅ QC2 fires |
| Excel 1-char fabrication | **✅ L1139** | ✅ QC2 fires |

---

## 3. v6 runtime

```
cd tools/rbkc && ./rbkc.sh verify 6
→ "All files verified OK"

cd tools/rbkc && pytest tests/ut/test_verify.py -q
→ 134 passed in 1.18s
```

**Bias note**: v6 PASS is weak evidence. v6 corpus contains no `.xls` files, so the `xlrd` branch (verify.py:881-892) receives zero runtime exercise. v6 PASS tells us only:
(a) the RST/MD QC2 paths do not fire on current RBKC output, AND/OR
(b) RBKC current output happens not to fabricate.
It does NOT tell us the Excel-`.xls` path is correct.

### Fault injection (adversarial, bias-avoidance)

Direct probes against `check_content_completeness` / `verify_file` with synthesised inputs (not the cache):

| # | Scenario | Detected? |
|---|----------|-----------|
| 1 | Excel 1-char fab (`"ABC"` cell, JSON `"ABC Y"`) | ✅ `[QC2] 'Y'` — **r2 H1 gap closed** |
| 2 | Excel MD-syntax `"---"` fab (no pipes) | ✅ `[QC2] '---'` — standalone `---` not absorbed |
| 3 | Excel whitespace-only residue | ✅ not flagged (spec-correct) |
| 4 | RST CJK 1-char near-miss | ✅ QC2 fires (`テキスト内宏。` vs `テキスト内容。`) |
| 5 | RST whitespace-only fabricated content (`"   "`) | Degrades to QC1 residue — acceptable |
| 6 | `.xls` any case | — **NOT EXERCISED** (no test, no v6 source) |

---

## 4. Overall Rating

**Rating: 4/5 — Good (improved from r2's 3/5)**

- r2's High-priority finding (Excel `len(t) >= 2` tolerance) is **fixed and pinned by a test**. Implementation now matches spec §3-1 Excel 節 手順 3 exactly for the `.xlsx` path.
- QC2/QC3 distinction is correct and well-tested on RST / MD / Excel paths.
- Remaining gaps are all on the **`.xls` branch** (r2 H2 unfixed) and on secondary matrix cells (top-level title, CJK, MD QC2). None threaten v6 runtime, but the quality gate on future-version (v1.2 / v1.3) .xls sources is untested.

---

## 5. Key Issues (with proposed fixes)

### 🔴 High Priority

**H1. `.xls` path has zero test coverage** (`verify.py:881-892`)

- **Description**: The `xlrd` branch is entirely untested. v1.2/v1.3 sources contain `.xls` release-note files. No regression guard exists for numeric-cell coercion (`1` → `"1.0"`), encoding, or sheet-iteration differences from `openpyxl`. r2 H2 noted this — still open.
- **Proposed fix**: Add `test_pass_real_xls` and `test_fail_qc2_fabricated_content_in_xls` mirroring the `.xlsx` tests. Use `xlwt` to generate the fixture at test time, or check in a tiny `.xls` fixture. Include at least one numeric-cell case to pin the str(float) behaviour.
- **Gate**: per `.claude/rules/rbkc.md`, test-only addition — no verify logic change — needs no spec review.

### 🟡 Medium Priority

**M1. Fill the QC2 matrix gaps with regression guards** (G2, G3, G4)

- **Description**: Three QC2 branches work in fault injection but have no test: (a) RST top-level fabricated title, (b) CJK near-miss on content, (c) direct MD QC2 fabricated content.
- **Proposed fix**: Add three tests:
  - `test_fail_qc2_top_level_fabricated_title_rst`
  - `test_fail_qc2_near_miss_cjk_one_char`
  - `test_fail_qc2_md_fabricated_content` (direct MD path assertion)

**M2. Pin the `_MD_SYNTAX_RE` tolerance allowlist** (G6)

- **Description**: verify.py:868-877 regex is a spec-level tolerance (「許容構文要素リスト」). An adversarial JSON of pure MD markup passes. No test enumerates which patterns are tolerated, so any regex edit silently changes scope.
- **Proposed fix**: Add `test_excel_qc2_md_syntax_tolerance_allowlist` that enumerates the tolerated patterns (`**`, `|`, `|---|`, `##`, `>`, `1.`, `` ` ``) and asserts each is absorbed, and a matching negative test asserting `---` (no pipes), plain text, and `<html>` are NOT absorbed.

**M3. `.xls` numeric cell coercion** (G7)

- **Description**: `str(sheet.cell_value(...))` on numeric cells produces `"1.0"` while JSON typically has `"1"`. Without a test, this produces simultaneous QC1 (cell missing) + QC2 (JSON residue) false positives — or worse, silent passes depending on strip behaviour.
- **Proposed fix**: After H1 test scaffold exists, add `test_xls_numeric_cell_coercion` that writes a cell value `1`, JSON `"1"`, and asserts the expected behaviour (the spec does not explicitly address this — raising the question first is itself valuable).

### 🟢 Low Priority

**L1. Cross-boundary fabrication guard** (G5) — add `test_fail_qc2_cross_boundary_fabrication` using two non-contiguous source blocks and a JSON unit that only appears if the two are concatenated.

---

## 6. Positive aspects

- r2 H1 bug **fixed and pinned** by `test_fail_qc2_one_char_fabrication_detected` at L1139. The comment at verify.py:972-973 explicitly states the no-tolerance rule and cites the spec — future readers cannot accidentally restore the threshold without confronting the intent.
- Zero-exception principle upheld: unknown RST role / MD token / unresolved ref surfaces as `[QC1]`, not as a silent pass that would hide QC2.
- QC2 ↔ QC3 ↔ QC4 branching logic is symmetric across RST and MD paths (verify.py:727-738 vs 822-833).
- Top-level title/content is treated as a first-class search unit in all three paths — not a special case.
- No circular tests; all assertions are against public behaviour (issue strings), not internals.

---

## 7. Files reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L658-676, L679-758, L761-861, L868-980)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L750-1059, L1066-1174)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1 手順 1-4 L159-195, Excel 節 L207-226)
- `/home/tie303177/work/nabledge/work2/.work/00299/review-z1-r2/QC2.md` (consulted only after independent evaluation, for regression comparison)
