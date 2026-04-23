# QC2 正確性 (Accuracy — no fabrication) — QA Engineer Review

**Reviewer**: Independent QA Engineer (no access to prior reviews)
**Date**: 2026-04-23
**Scope**: `tools/rbkc/scripts/verify/verify.py` QC2 logic + unit tests + v6 runtime behaviour
**Bias-avoidance applied**: spec (§3-1 手順 4 / Excel 節) treated as authoritative; fault injection used to confirm behaviour beyond unit tests.

---

## 実装

### RST / MD (`check_content_completeness` → sequential-delete)

- RST branch: `verify.py:671-690`. After sequential `norm_source.find(norm_unit, current_pos)` fails, the code does a second `norm_source.find(norm_unit)` (no start offset). The decision tree is:
  - `prev_idx == -1` and title → **QC2 fabricated title** (verify.py:680)
  - `prev_idx == -1` and content → **QC2 fabricated content** (verify.py:686)
  - otherwise → QC3/QC4
- MD branch: `verify.py:766-785`. Same decision tree on `_squash`-normalized text.
- Top-level `title`/`content` are injected as `__top__` search units (`verify.py:589-594`, `verify.py:742-745`), so top-level fabrications are in scope.

**Spec conformance (§3-1 手順 4)**:
- 「JSON テキストが正規化ソースに全く存在せず → QC2」: matched by `prev_idx == -1` check. ✅
- QC2/QC3 separation (never-appeared vs already-consumed) is correctly implemented via `_in_consumed` (verify.py:667-669, 762-764). ✅
- No silent fallback observed on RST/MD paths. `UnknownSyntaxError` surfaces as `[QC1]` (verify.py:648-650, 727-729) — it does not hide QC2.

### Excel (`_verify_xlsx`)

- Direction-inverted scheme (verify.py:870-929) per spec §3-1 Excel 節.
- QC2 residual emission is at `verify.py:923-927`:
  ```
  residual_plain = _MD_SYNTAX_RE.sub(" ", residual)
  for token in residual_plain.split():
      t = token.strip()
      if t and len(t) >= 2:
          issues.append(f"[QC2] JSON token not found in Excel source: {token!r}")
  ```

**Spec conformance issues**:

1. **🔴 High — `len(t) >= 2` is an undocumented tolerance.** Spec §3-1 Excel 節 手順 3 says "空白・空行を除く" — it does **not** authorize a character-length threshold. A 1-character fabrication (`"X"`, `"値"`, `"#"`, a stray `N`) is silently dropped. This is a verify-weakening that contradicts the quality gate principle in `.claude/rules/rbkc.md` ("Never weaken verify's detection to make RBKC output pass"). **Confirmed by fault injection below.**
2. **🟡 Medium — `_MD_SYNTAX_RE` tolerance is documented in spec §3-1 (「許容構文要素リスト（QC2 残存判定）」)** but the regex enumeration at `verify.py:820-829` silently absorbs any `|`, `**`, `*`, `__`, leading `#`/`>`/digit-dot/backtick. This matches the spec's *spirit* but is a spec-level loophole: an adversarial fabrication consisting solely of `**` or `|` characters passes. Not an impl bug — a spec-level risk.
3. **🟢 Low — `.xls` path uses `xlrd` (verify.py:834-844)**, structurally parallel to `.xlsx`, but zero integration tests exist (grep for `\.xls\b` and `xlrd` in `test_verify.py` returns nothing).

### JSON top-level title/content coverage

✅ Covered via `__top__` synthetic sid in all three paths (RST/MD/Excel). Top-level fabrication fault injection below confirms.

---

## テストカバレッジ

### Present tests (test_verify.py)

| # | Test | Covers |
|---|------|--------|
| `test_fail_qc2_fabricated_title` (L716) | Section title not in source (RST) | Basic QC2 title |
| `test_fail_qc2_fabricated_content` (L724) | Section content not in source (RST) | Basic QC2 content |
| `test_fail_qc2_multiple_fabricated_contents` (L935) | 2 sections both fabricated | Multi-fabrication count |
| `test_fail_qc2_top_level_fabricated_content` (L945) | Top-level content fabricated | `__top__` path |
| `test_fail_qc2_near_miss_one_char_differs` (L952) | `ABCDEFG` vs `ABCXEFG` (ASCII) | Near-miss ASCII |
| Excel `test_fail_qc2_fabricated_content_in_json` (L1067) | Extra `.xlsx` JSON content | Basic Excel QC2 |

### Gaps

| # | Missing coverage | Severity | Evidence |
|---|------------------|----------|----------|
| G1 | **Excel QC2 single-char fabrication not FAIL — actually a BUG, not just missing test** | 🔴 High | Fault-injection (below) shows `"X"` fabricated content is silently accepted. No test pins down the `len(t) >= 2` behaviour either as intentional or as regression trap. |
| G2 | **`.xls` format has zero tests** (any QC, not just QC2) | 🔴 High | `grep -n "\.xls\b\|xlrd" test_verify.py` → empty. Spec §3-1 Excel 節「`.xlsx` と `.xls` の両形式に対応する」. The `xlrd` branch at verify.py:834-844 is untested. If xlrd returns numeric cells as `"1.0"` vs `"1"`, fab may go undetected. |
| G3 | **QC2 top-level fabricated _title_** test missing | 🟡 Medium | L945 covers top-level fabricated *content*; the title branch on the `__top__` path (different `is_content=False` branch, verify.py:680 vs 686) is only exercised for section-level titles. |
| G4 | **Near-miss in CJK** not tested | 🟡 Medium | L952 is ASCII only. CJK lacks word-break tokenization so near-miss behaviour differs. Fault-injection (below) confirms it works — but it is not pinned. |
| G5 | **Cross-boundary fabrication** (JSON text spans two source blocks where each individually exists but not contiguously) not tested | 🟡 Medium | Fault-injection confirms current impl flags it as QC2 via `\s+` collapse; but no regression guard. |
| G6 | **MD fabrication test** missing entirely in TestVerifyFile (only RST path tested for QC2) | 🟡 Medium | L766-785 MD branch is covered only transitively via QC3/QC4 MD tests. Directly asserting QC2 on MD is absent. Fault-injection confirms MD branch fires. |
| G7 | **Excel QC3-vs-QC2 distinction test** — near-miss 1-char cell | 🟢 Low | Current Excel tests do not test the full never-vs-already-consumed split of the original spec at 手順 3/4. |
| G8 | **Adversarial MD-syntax-only fabrication in Excel** (pure `"** ** **"`) | 🟢 Low | `_MD_SYNTAX_RE` absorbs these; no test codifies the intended tolerance. This is a *documentation* test, not a functional gap. |

### Circular-test check

Reviewed all QC2 tests: each constructs source + JSON independently and asserts on issue *kind* substring (`"QC2"`, `"fabricated"`). None import internal functions other than `check_content_completeness` / `verify_file` (public boundary). **No circular tests detected.**

---

## v6 実行

```
cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
→ 0
cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | tail -3
→ All files verified OK
cd tools/rbkc && python3 -m pytest tests/ 2>&1 | tail -3
→ 190 passed in 2.75s
```

### Fault injection (bias-avoidance)

v6 passing is weak evidence on its own (could be that RBKC never fabricates, OR that verify misses fabrications). I injected 13 adversarial JSONs through `check_content_completeness` / `verify_file` (not the cache; synthetic inputs). Results:

| # | Scenario | Detected? | Notes |
|---|----------|-----------|-------|
| 1 | RST ASCII 1-char diff (`ABCDEFG`→`ABCXEFG`) | ✅ QC2 | |
| 2 | RST CJK 1-char diff (`あいうえお`→`あいXえお`) | ✅ QC2 | New evidence |
| 3 | RST multi-fab (2 sections) | ✅ 3×QC2 | |
| 4 | RST top-level fabricated title | ✅ QC2 | verify.py:680 `__top__` branch |
| 5 | RST top-level fabricated content | ✅ QC2 | verify.py:686 `__top__` branch |
| 6 | RST cross-boundary (`えお` + `かき` across newline) | ✅ QC2 | `\s+` collapse treats newline as delim |
| 7 | MD fabricated content | ✅ QC2 | MD branch fires |
| 8 | RST whitespace-only diff (`AAA BBB`→`AAA  BBB`) | ✖ not flagged | Spec-compliant: §3-1 手順 1 explicitly normalizes `\s+→` single space. Not a bug. |
| 9 | **Excel 1-char fab (`"X"`)** | **✖ NOT flagged** | **BUG — violates spec §3-1 Excel 節 手順 3** |
| 10 | Excel 2-char fab (`"YZ"`) | ✅ QC2 | |
| 11 | Excel CJK fab (`"捏造内容"`) | ✅ QC2 | |
| 12 | Excel pure pipe `"\|"` fab | ✖ not flagged | Spec-compliant (許容構文要素) |
| 13 | Excel ASCII near-miss (`ABC` cell, `ABD` JSON title) | ✅ QC1+QC2 | |

**Key finding**: case #9 exposes a real gap — the `len(t) >= 2` threshold at `verify.py:926` silently tolerates 1-char fabrication. v6 passes partly because no 1-char fab happens to exist, not because verify would detect one.

---

## 総合

**Rating: 3/5 — Acceptable with High-priority fix required**

- RST / MD QC2 logic matches spec §3-1 手順 4 exactly; fault injection confirms robust detection across near-miss, CJK, cross-boundary, multi-fab, top-level.
- Excel QC2 has one concrete implementation bug (length threshold) and one material test-coverage gap (`.xls` untested).
- Test suite is non-circular but MD-QC2 and `.xls` regions are blind. v6 runtime green is not sufficient evidence of quality gate strength on these paths.

---

## 改善案

### 🔴 High Priority

**H1. Remove `len(t) >= 2` threshold in Excel QC2** (verify.py:926)

- **Description**: Spec §3-1 Excel 節 手順 3 authorizes only 空白・空行 exclusion and the explicit MD 許容構文要素リスト. A 2-character minimum is an undocumented verify weakening. Fault injection case #9 confirms 1-char fabrication passes silently.
- **Proposed fix**: Change `if t and len(t) >= 2:` to `if t:`. Add unit test `test_fail_qc2_excel_single_char_fabrication`. If the threshold is genuinely needed to suppress noise (e.g., orphan punctuation after MD-syntax stripping), document the exact noise source in `rbkc-verify-quality-design.md` §3-1 Excel 節 and restrict the suppression to named characters — not arbitrary 1-char text.
- **Gate**: per `.claude/rules/rbkc.md`, verify changes require user approval. This is a *strengthening* change (removes a tolerance) and is the acceptable category.

**H2. Add `.xls` format coverage tests**

- **Description**: The `xlrd` branch at verify.py:834-844 is untested. `.xls` handling differs from `.xlsx` in cell type coercion (numeric → float string). A cell with value `1` might round-trip as `"1.0"` in the xls branch and `"1"` in JSON — leading to both QC1 (source missing from JSON) and QC2 (JSON `"1"` not in source) false positives OR silent drops depending on stripping.
- **Proposed fix**: Add `test_pass_real_xls` and `test_fail_qc2_fabricated_content_in_xls` mirroring the existing `.xlsx` tests. Use `xlwt` or a checked-in fixture `.xls` file. Include at least one numeric-cell test.

### 🟡 Medium Priority

**M1. Add missing QC2 happy-case tests**

- Description: G3/G4/G5/G6 — top-level QC2 title (RST), CJK near-miss, cross-boundary, MD QC2 content all work in fault injection but have no regression guard.
- Proposed fix: Add 4 tests:
  - `test_fail_qc2_top_level_fabricated_title`
  - `test_fail_qc2_near_miss_cjk_one_char`
  - `test_fail_qc2_cross_boundary_fabrication`
  - `test_fail_qc2_md_fabricated_content`

**M2. Document (or remove) `_MD_SYNTAX_RE` tolerance semantics**

- Description: The regex at verify.py:820-829 is a documented-by-spec tolerance but the regex itself is not linked to the spec. An adversarial fabrication consisting only of MD markup passes. Either (a) narrow the regex to known RBKC output patterns, or (b) add a test that asserts exactly which patterns are tolerated, so any drift is caught.
- Proposed fix: Add `test_excel_qc2_md_syntax_tolerance_allowlist` enumerating the tolerated patterns, and link verify.py:820 back to spec §3-1 Excel 節 「許容構文要素リスト」.

### 🟢 Low Priority

**L1. Add Excel QC2 vs QC3 near-miss test** (G7) — clarifies never-vs-already-consumed split on the Excel path (currently only generic structure is tested).

---

## Files reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (verify.py:570-710, 713-814, 820-929)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L710-1005, L1009-1102)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1 including Excel 節, L159-226)
