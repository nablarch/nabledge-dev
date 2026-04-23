# QC2 正確性 (Accuracy — no fabrication) — QA Engineer Review (r6)

**Reviewer**: Independent QA Engineer (bias-avoidance; spec authoritative; prior r5 review consulted only after independent evaluation)
**Date**: 2026-04-23
**Scope**: `tools/rbkc/scripts/verify/verify.py` QC2 logic (RST / MD / Excel `.xlsx` + `.xls`) + unit tests (`tests/ut/test_verify.py`) + runtime (`rbkc.sh verify 6`, `pytest tests/ut/test_verify.py`)
**Branch / base**: current branch `299-implement-rbkc`, delta against r5 = commit `d598590ce` ("r5 gaps — tilde fence + Excel test skip cleanup")
**Stance**: `pytest` + `rbkc.sh verify 6` are necessary but not sufficient. v6 sources contain no `.xls`, so the xlrd branch is exercised only by unit tests.

---

## 1. Implementation (unchanged vs r5 at the QC2-logic layer)

### RST — `_check_rst_content_completeness` (`verify.py:530-609`)

QC2 decision points (miss + `prev_idx == -1`):
- title path: `verify.py:579` → `[QC2] section '{sid}': fabricated title`
- content path: `verify.py:585` → `[QC2] section '{sid}': fabricated content`

`UnknownSyntaxError` surfaces as `[QC1]` at `verify.py:544-549`, so no silent fallback masks a would-be QC2. Top-level `title` / `content` are injected as `__top__` units by `_build_rst_search_units` (called at `verify.py:558`).

### MD — `_check_md_content_completeness` (`verify.py:612-712`)

Symmetric structure. QC2 decision points:
- title path: `verify.py:674` → `[QC2] section '{sid}': fabricated title`
- content path: `verify.py:680` → `[QC2] section '{sid}': fabricated content`

`UnknownSyntaxError` → `[QC1]` at `verify.py:624-628`. Top-level `__top__` injection at `verify.py:641-644`.

### Excel — `_verify_xlsx` (`verify.py:769-831`)

Direction-inverted: source cells are deleted from JSON text.

QC2 residual emission (`verify.py:822-829`):

```
# Per spec §3-1 Excel 節 手順 3: anything other than whitespace/empty
# remaining after deleting source cells is QC2 (捏造). No length
# tolerance — a 1-char residue is still a fabrication.
residual_plain = _MD_SYNTAX_RE.sub(" ", residual)
for token in residual_plain.split():
    t = token.strip()
    if t:
        issues.append(f"[QC2] JSON token not found in Excel source: {token!r}")
```

- 1-char tolerance **remains removed** (r2 H1 fix preserved; comment cites spec).
- `_MD_SYNTAX_RE` (`verify.py:719-728`): absorbs `|---|`, `|`, `**`, `*`, `__`, leading `#+`, leading `>`, leading `\d+\.`, backtick. Matches spec §3-1「許容構文要素リスト」.
- `.xls` vs `.xlsx` dispatched by extension in `_xlsx_source_tokens` (`verify.py:731-756`); downstream delete pipeline is shared — one QC2 decision point for both.

### Spec conformance (§3-1 手順 4 + Excel 節)

| Spec clause | Location | Status |
|---|---|---|
| 手順 4「正規化ソースに全く存在せず → QC2」 | `verify.py:578, 584, 673, 679` (`prev_idx == -1` branch) | OK |
| 手順 4 QC2 vs QC3 split (never-seen vs consumed) | `_in_consumed` @ `verify.py:580, 586, 675, 681` | OK |
| Excel 手順 3「空白・空行を除く残存 → QC2」 | `verify.py:826` (`.split()` drops whitespace only) | OK |
| Excel「許容構文要素リスト」 | `_MD_SYNTAX_RE` @ `verify.py:719-728` | OK |
| No silent tolerance (length / count / suppress) | Not present in any QC2 path | OK |
| verify independence from RBKC impl | Verify imports only `scripts/common/rst_normaliser`, `scripts/common/md_normaliser`, `scripts/common/rst_ast`; no `scripts/create/*` import. `common/` is explicitly shared between create & verify per spec §3-1 手順 0 (line 115) — not a circularity violation | OK |

### Silent-tolerance audit

- RST/MD `_squash` whitespace collapse (`verify.py:632-633`) matches spec §3-1 手順 4「空白・改行正規化のみ」. Not a silent tolerance.
- Excel `_MD_SYNTAX_RE` is a **spec-sanctioned** tolerance (手順 3 allowlist). Still has no regression test pinning the accept/reject matrix — see M2 (carried from r5, unfixed).
- No `try/except pass`, no `continue` hiding QC2, no length / char threshold anywhere on the QC2 path.

---

## 2. Unit tests

### QC2 coverage (`tools/rbkc/tests/ut/test_verify.py`)

| Test | Line | Covers |
|------|------|--------|
| `test_fail_qc2_fabricated_title` | L855 | RST section title not in source |
| `test_fail_qc2_fabricated_content` | L863 | RST section content not in source |
| `test_fail_qc2_multiple_fabricated_contents` | L1097 | 2 sections both fabricated — count assertion |
| `test_fail_qc2_top_level_fabricated_content` | L1107 | Top-level `content` (RST `__top__` path) |
| `test_fail_qc2_near_miss_one_char_differs` | L1114 | ASCII `ABCDEFG` → `ABCXEFG` |
| `test_fail_qc2_fabricated_content_in_json` | L1282 | Excel `.xlsx` QC2 multi-char fabrication |
| `test_fail_qc2_one_char_fabrication_detected` | L1297 | Excel `.xlsx` 1-char fabrication — pins r2 H1 fix |
| `test_pass_xls_cell_in_json` | L1311 | `.xls` PASS via `xlwt` fixture |
| `test_fail_xls_cell_missing_from_json` | L1323 | `.xls` QC1 for missing cell |
| `test_fail_xls_qc2_fabrication` | L1334 | `.xls` QC2 (`捏造` string in JSON not in any cell) |
| `test_fail_xls_numeric_cell_missing_from_json` | L1347 | `.xls` numeric cell (`12345`) not in JSON |
| `test_fail_qc3_duplicate_cell_in_json` | L1361 | Excel `.xlsx` QC3 boundary (separates from QC2) |

### r5 deltas — what r6 actually changed

r5 raised 4 issues (M1–M4). r6 commit `d598590ce` touched exactly two of them:

| r5 issue | r6 status | Evidence |
|---|---|---|
| **M4** silent `try/except ImportError: pytest.skip` for xlwt/xlrd/openpyxl | **CLOSED** | `d598590ce` rewrote all four `.xls` tests and all `.xlsx` tests to bare `import xlwt` / `import openpyxl`. `grep -n "pytest.skip\|importorskip\|ImportError" tests/ut/test_verify.py` → 0 hits. `xlwt`/`xlrd`/`openpyxl` are hard deps via `setup.sh:196-199`. Missing dep now surfaces as `ImportError` at collection time, not a silent skip. Matches `.claude/rules/development.md` "No Test Skipping". |
| **M1** top-level RST QC2 title, CJK near-miss QC2, direct MD QC2 | **still open** | No new tests under `TestCheckContentCompleteness` or `TestVerifyFileExcel`. `grep "top_level_fabricated_title\|near_miss_cjk\|md_fabricated"` → 0 hits. |
| **M2** Excel `_MD_SYNTAX_RE` allowlist regression guard | **still open** | No test enumerates which patterns the regex absorbs vs rejects. Spec-sanctioned tolerance with zero pinning. |
| **M3** `.xls` numeric cell coercion (`1` ↔ `"1.0"`) | **still open** | `test_fail_xls_numeric_cell_missing_from_json` at L1347 only pins "cell absent → QC1". The realistic case — cell `1`, JSON correctly contains `"1"`, xlrd yields `"1.0"` → false QC1 — is still not codified. |

Test count: 156 (r5) → 158 (r6). Both additions are **QO1 tilde-fence regression tests** (`test_pass_tilde_fenced_code_block_with_heading_inside` L152, `test_pass_backtick_fenced_code_block_with_heading_inside` L168) — unrelated to QC2. Zero net QC2 coverage added in r6.

### Circular-test audit

Grep on private QC2 symbols in `tests/ut/test_verify.py`:
```
_build_rst_search_units   → 0 hits
_MD_SYNTAX_RE             → 0 hits
_xlsx_source_tokens       → 0 hits
_xlsx_json_text           → 0 hits
_verify_xlsx              → 0 hits
_norm / _squash           → 0 hits
```
Every QC2 test constructs source + JSON independently and asserts on the public `[QC2]` / `[QC1]` string returned by `verify_file` or `check_content_completeness`. **No circular tests. OK.**

### Bias check: v6 PASS is weak Excel evidence

v6 corpus is RST + MD only (`./rbkc.sh verify 6` exercises neither `.xlsx` nor `.xls`). Runtime evidence for Excel QC2 comes entirely from unit tests. `.xls` will only matter on v1.2 / v1.3 release-note conversions; those are still downstream.

### Adversarial fault-injection (bias-avoidance)

| # | Scenario | Expected | r6 behaviour |
|---|----------|----------|--------------|
| 1 | `.xlsx` 1-char fab | QC2 | OK — pinned L1297 |
| 2 | `.xlsx` bare `"---"` fab | QC2 | OK by inspection — `_MD_SYNTAX_RE` does not match bare `---` (requires leading `|`) |
| 3 | Whitespace-only residue | not flagged | OK — `.split()` drops (L826) |
| 4 | `.xlsx` `"<b>"` fab | QC2 | OK by inspection — not pinned (M2 carryover) |
| 5 | `.xlsx` `"\| malicious \|"` fab | QC2 | Brittle — `_MD_SYNTAX_RE` absorbs `|`, leaving `malicious` → QC2 still fires. OK, not pinned (M2). |
| 6 | RST CJK 1-char near-miss | QC2 | OK by inspection — not pinned (M1 carryover) |
| 7 | RST `__top__` fabricated title | QC2 | OK by inspection — not pinned (M1 carryover) |
| 8 | MD section-level fab content (fmt=md) | QC2 | OK by inspection — not pinned (M1 carryover) |
| 9 | `.xls` QC2 fab | QC2 | OK — pinned L1334 |
| 10 | `.xls` numeric `1` vs JSON `"1"` | ambiguous | Not pinned (M3 carryover). Under r6 code: `str(1.0) == "1.0"` → `json_text.find("1.0") == -1` → **false QC1** on correct JSON. |
| 11 | `.xls` cell missing entirely | QC1 | OK — pinned L1323, L1347 |
| 12 | xlwt/xlrd/openpyxl missing in CI | hard fail | **NOW OK (r6)** — bare `import` raises, no silent skip. |

---

## 3. Runtime

```
$ cd tools/rbkc && ./rbkc.sh verify 6
All files verified OK

$ cd tools/rbkc && pytest tests/ut/test_verify.py -q
158 passed in 0.85s

$ cd tools/rbkc && pytest tests/ut/test_verify.py -q -k "xls or qc2"
14 passed, 144 deselected in 0.39s
```

All green. Runtime weight for Excel QC2 remains unit-tests-only — v6 sources do not exercise any Excel code path.

---

## 4. Overall Rating

**Rating: 4/5 — Good (unchanged from r5).**

- r2 H1 (Excel 1-char tolerance removal) — still fixed, still pinned (`test_fail_qc2_one_char_fabrication_detected` L1297). Comment at `verify.py:822-824` cites spec §3-1 Excel 節 手順 3 directly.
- r4 H1 (`.xls` path untested) — still closed. Four tests at L1311-1359 exercise xlrd end-to-end.
- **r5 M4 (silent skip) — CLOSED in r6.** This was the most serious signal-integrity issue on the QC2 test surface: silent skip of xlwt/xlrd import is now replaced by bare imports that raise on missing deps. This is a genuine improvement and the primary reason the rating is not lower despite the matrix gaps.
- Rating did not rise to 5/5 because:
  1. r5 M1 / M2 / M3 are all still open — no new QC2 assertion added in r6.
  2. Spec-sanctioned tolerances (`_MD_SYNTAX_RE`) remain unpinned. Silent widening of that regex would be invisible to the current test suite.
  3. `.xls` numeric coercion (M3) is a latent false-QC1 risk for v1.2/v1.3 release notes and is still not codified by a test — the closer v1.2 comes, the more this matters.

Independent judgement: M4's closure is worth about half a point; M1/M2/M3 remaining open is worth about half a point in the opposite direction. Net = unchanged at 4/5.

---

## 5. Key Issues (priority + proposed fix)

### 🔴 High Priority

None. r4 H1 closed; r5 had no High; r6 introduced no new High.

### 🟡 Medium Priority

**M1. Fill remaining QC2 matrix gaps** — **CARRIED FROM r4/r5; still unfixed in r6.**

- Description: Three QC2 branches still work by inspection only.
- Proposed fix:
  - `test_fail_qc2_top_level_fabricated_title_rst` — source body present, JSON top-level `title` fabricated; assert `[QC2] ... fabricated title` with `__top__` sid.
  - `test_fail_qc2_near_miss_cjk_one_char` — source `テキスト内容。`, JSON section content `テキスト内宏。`; assert QC2.
  - `test_fail_qc2_md_fabricated_content` — MD source + MD JSON with a section whose content is absent; assert QC2 via `fmt="md"` and `verify_file`.

**M2. Pin the Excel `_MD_SYNTAX_RE` tolerance allowlist** — **CARRIED FROM r4/r5; still unfixed in r6.**

- Description: `verify.py:719-728` is a spec-sanctioned QC2-bypass zone. Silent widening is the highest-leverage regression class on this code path. No test enumerates which patterns are absorbed vs not.
- Proposed fix: Two tests invoking `_verify_xlsx` (or its public dispatch via `verify_file`) with orphan residuals:
  - `test_excel_qc2_md_syntax_tolerance_absorbs` — feed `"**"`, `"|"`, `"|---|"`, `"##"`, `"> "`, `"1. "`, `` "`" `` as orphan residual on the JSON side; assert no QC2 fires.
  - `test_excel_qc2_md_syntax_tolerance_does_not_absorb` — feed `"---"` (bare, no surrounding pipes), `"<b>"`, `"foo"`, `"@ref"`; assert QC2 fires for each.

**M3. `.xls` numeric cell coercion ambiguity** — **CARRIED FROM r5; still not pinned.**

- Description: `str(sheet.cell_value(rx, cx))` on xlrd numeric cells yields `"12345.0"` / `"1.0"` while JSON typically holds `"12345"` / `"1"`. The existing `test_fail_xls_numeric_cell_missing_from_json` (L1347) pins only "entire cell absent → QC1". The realistic case — JSON correctly contains `"1"`, xlrd returns `1.0`, `json_text.find("1.0") == -1` → **false QC1 on correct JSON** — is still not codified. First v1.2/v1.3 `.xls` with a numeric column will collide with this.
- Proposed fix: `test_xls_numeric_cell_integer_in_json` — cell `1` via `xlwt.write(0, 0, 1)`, JSON `{"title": "X", "content": "値は 1 です", ...}`. Assert actual current behaviour. If it raises a false QC1, that is a spec-violation bug (spec does not sanction `.0` coercion) and the fix belongs in `_xlsx_source_tokens` — e.g., integer-valued floats render as `"1"`. If the test passes, behaviour is locked. Either outcome resolves the ambiguity per `.claude/rules/rbkc.md` "surface the ambiguity".

### 🟢 Low Priority

**L1. Cross-boundary fabrication guard** (carryover from r5 L1) — `test_fail_qc2_cross_boundary_fabrication`: two non-contiguous source blocks, JSON unit that only appears if the two are concatenated under `\s+` collapse; assert behaviour (spec-correct is currently flagging it).

---

## 6. Positive aspects

- **r5 M4 closed decisively.** Commit `d598590ce` eliminates the `try/except ImportError: pytest.skip` pattern from all 11 Excel tests — bare imports raise on missing dep, matching `.claude/rules/development.md` "No Test Skipping". The rationale is documented in the commit body with the exact rule citation. `setup.sh:196-199` confirms xlwt/xlrd/openpyxl are hard dev deps, so the bare-import approach has no false-failure risk.
- r2 H1 fix still present and still pinned (`test_fail_qc2_one_char_fabrication_detected` L1297). Code comment at `verify.py:822-824` durably documents the spec rationale.
- Zero-exception principle upheld across all three paths: unknown RST role, unknown MD token, RST parse error all surface as `[QC1]`, never a silent pass that could mask QC2.
- QC2 ↔ QC3 ↔ QC4 branching structurally symmetric across RST (`verify.py:575-589`) and MD (`verify.py:670-684`) — easy to audit for spec conformance.
- Top-level `title`/`content` treated as first-class `__top__` search units across RST, MD, and Excel — no special-case skip that could hide fabrication at document level.
- No circular tests introduced in r6; all QC2 tests assert on the public `[QC2]` / `[QC1]` issue string via `verify_file`, never on private helpers.
- verify's dependency surface respects the spec's independence principle: imports only `scripts/common/*` (shared by design per §3-1 手順 0) and never `scripts/create/*`. Fully consistent with `.claude/rules/rbkc.md`.
- `_MD_SYNTAX_RE` remains isolated to the Excel path; RST/MD share no tolerance list with Excel, so a future widening of one cannot silently leak into the other.

---

## 7. Recommendations

1. **Close M3 before the first v1.2/v1.3 `.xls` RBKC run.** The numeric-coercion false-QC1 is virtually certain to appear in release-note spreadsheets with numeric columns. One added test, ~10 lines — either pins current behaviour or forces a coercion fix. Highest urgency of the three carried-over mediums.
2. **Close M2 as the cheapest leverage win.** Two regex-allowlist tests pin a spec-sanctioned tolerance zone that is silent-by-design and therefore deserves a stronger regression guard than ordinary logic. Lowest cost, highest per-LOC value of anything on this list.
3. **Close M1 opportunistically.** The three missing matrix tests together are ~30 lines and convert "works by inspection" into "pinned by assertion" for the top-level RST QC2 title, CJK QC2 near-miss, and direct MD QC2 branches.
4. **Once M1/M2/M3 are pinned, the QC2 surface can credibly move to 5/5.** At that point every QC2 decision point in `verify.py` has either a direct test or an adversarial probe, and the only spec-sanctioned tolerance has an allow/reject matrix pinned.

---

## 8. Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L461-506, L509-712, L716-831, L838-858)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L149-183 for r6 QO1 deltas, L820-1200, L1233-1376)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1 手順 0-4, Excel 節 L207-226, L326-329)
- `/home/tie303177/work/nabledge/work2/.claude/rules/rbkc.md` (verify independence, scope, change rules)
- `/home/tie303177/work/nabledge/work2/.claude/rules/development.md` (No Test Skipping — basis for M4 closure verification)
- `/home/tie303177/work/nabledge/work2/setup.sh` (L196-199 — xlwt/xlrd/openpyxl hard-dep evidence)
- `/home/tie303177/work/nabledge/work2/.work/00299/review-z1-r5/QC2.md` (consulted only after independent evaluation)
- Commit `d598590ce` (the only r5→r6 delta touching QC2 test surface)
