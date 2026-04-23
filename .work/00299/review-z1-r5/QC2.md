# QC2 正確性 (Accuracy — no fabrication) — QA Engineer Review (r5)

**Reviewer**: Independent QA Engineer (bias-avoidance; spec authoritative; prior r4 review consulted only after independent evaluation)
**Date**: 2026-04-23
**Scope**: `tools/rbkc/scripts/verify/verify.py` QC2 logic (RST / MD / Excel `.xlsx` + `.xls`) + unit tests (`tests/ut/test_verify.py`) + runtime PASS (`rbkc.sh verify 6`, `pytest`)
**Stance**: `pytest` + `rbkc.sh verify 6` are necessary but not sufficient. v6 source has no `.xls`, so the xlrd branch is exercised only by unit tests — no runtime fallback.

---

## 1. Implementation

### RST — `_check_rst_content_completeness` (`verify.py:529-608`)

Decision tree per search unit (`verify.py:569-588`):

- `norm_source.find(norm_unit, current_pos)` → hit: consume, advance.
- Miss → `norm_source.find(norm_unit)` with no offset (`verify.py:575`).
  - `prev_idx == -1` + title → `[QC2] fabricated title` (`verify.py:578`)
  - `prev_idx == -1` + content → `[QC2] fabricated content` (`verify.py:584`)
  - Otherwise QC3 (in consumed) / QC4 (misplaced).
- `UnknownSyntaxError` surfaces as `[QC1]` (`verify.py:546-548`) — no silent fallback that could mask QC2.
- Top-level `title`/`content` injected as `__top__` units by `_build_rst_search_units` (`verify.py:461, 488, 492`).

### MD — `_check_md_content_completeness` (`verify.py:611-711`)

Symmetric decision tree on `_squash`-normalised text (`verify.py:664-683`):

- Miss + `prev_idx == -1` + title → `[QC2] fabricated title` (`verify.py:673`)
- Miss + `prev_idx == -1` + content → `[QC2] fabricated content` (`verify.py:679`)
- `UnknownSyntaxError` → `[QC1]` (`verify.py:625-627`).
- Top-level injected at `verify.py:640-643`.

### Excel — `_verify_xlsx` (`verify.py:768-830`)

Direction-inverted: source cells deleted from JSON text. QC2 residual emission (`verify.py:821-828`):

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

- **1-char tolerance remains GONE** (r2 H1 fix preserved). Comment cites spec explicitly.
- `_MD_SYNTAX_RE` (`verify.py:718-727`): absorbs `|---|`, `|`, `**`, `*`, `__`, leading `#+`, leading `>`, leading `\d+\.`, backtick. Matches spec §3-1「許容構文要素リスト」.
- `.xls` / `.xlsx` dispatched via extension at `verify.py:732-755` (`_xlsx_source_tokens`). Same delete-pipeline downstream — one QC2 decision point for both.

### Spec conformance (§3-1 手順 4 + Excel 節)

| Spec clause | Location | Status |
|---|---|---|
| 手順 4「正規化ソースに全く存在せず → QC2」 | `verify.py:577, 583, 672, 678` (`prev_idx == -1` branch) | OK |
| 手順 4 QC2 vs QC3 split (never-seen vs consumed) | `_in_consumed` @ `verify.py:579, 585, 674, 680` | OK |
| Excel 手順 3「空白・空行を除く残存 → QC2」 | `verify.py:825` (`.split()` drops whitespace only) | OK |
| Excel「許容構文要素リスト」 | `_MD_SYNTAX_RE` @ `verify.py:718-727` | OK |
| No silent tolerance | No length / count thresholds anywhere in QC2 path | OK |

### Silent-tolerance audit

- RST/MD `_squash` (`verify.py:631-632`) collapses whitespace on both sides — matches spec §3-1 手順 4「空白・改行正規化のみ」. Not a silent tolerance.
- Excel `_MD_SYNTAX_RE` is a **spec-sanctioned** tolerance (手順 3 allowlist). Still not pinned by a regression test — see M2.
- No `try: ... except: pass` or `continue` silently hiding QC2 in any of the three paths. Length comparison (`len>=2`) — absent. Byte / char tolerance — absent.

---

## 2. Unit tests

### QC2 coverage (`tools/rbkc/tests/ut/test_verify.py`)

| Test | Line | Covers |
|------|------|--------|
| `test_fail_qc2_fabricated_title` | L821 | RST section title not in source |
| `test_fail_qc2_fabricated_content` | L829 | RST section content not in source |
| `test_fail_qc2_multiple_fabricated_contents` | L1063 | 2 sections both fabricated — count assertion |
| `test_fail_qc2_top_level_fabricated_content` | L1073 | Top-level `content` (RST `__top__` path) |
| `test_fail_qc2_near_miss_one_char_differs` | L1080 | ASCII `ABCDEFG` → `ABCXEFG` |
| `test_fail_qc2_fabricated_content_in_json` | L1257 | Excel `.xlsx` QC2 multi-char fabrication |
| `test_fail_qc2_one_char_fabrication_detected` | L1275 | **Excel `.xlsx` 1-char fabrication** — pins r2 H1 fix |
| `test_pass_xls_cell_in_json` | L1292 | **NEW r5** — `.xls` PASS via xlwt fixture |
| `test_fail_xls_cell_missing_from_json` | L1308 | **NEW r5** — `.xls` QC1 for missing cell |
| `test_fail_xls_qc2_fabrication` | L1322 | **NEW r5** — `.xls` QC2 (`捏造` string in JSON not in any cell) |
| `test_fail_xls_numeric_cell_missing_from_json` | L1338 | **NEW r5** — `.xls` numeric cell (`12345`) not in JSON |

### QC2 vs QC3 distinction
- RST: `test_fail_qc3_duplicate_content_rst` (L1088), `test_fail_qc3_duplicate_title_md` (L1097), `test_fail_qc3_duplicate_content_md` (L1130), `test_fail_qc3_top_level_and_section_content_duplicated` (L1119)
- Excel: `test_fail_qc3_duplicate_cell_in_json` (L1355)

Both branches (never-seen vs consumed) are exercised on RST, MD, and Excel `.xlsx`. OK.

### `.xls` path (r4 gap G1) — CLOSED

The four new tests (L1292-1353) exercise the `xlrd` branch at `verify.py:732-742` end-to-end:

- PASS case (L1292): `xlwt.Workbook` → `.xls` on disk → `_xlsx_source_tokens` via `ext == ".xls"` → `xlrd.open_workbook` → cell `"Hello"` matched in JSON title.
- QC1 case (L1308): cell `"必須セル値"` absent from JSON → `[QC1]` emitted.
- QC2 case (L1322): JSON contains `捏造` with no corresponding cell → residual-delete pipeline emits `[QC2]`. This is the primary pin for the `.xls` QC2 branch.
- Numeric case (L1338): `ws.write(0, 0, 12345)` → `str(sheet.cell_value(...))` produces `"12345.0"` under xlrd, JSON has no `12345` at all → `[QC1]` fires on `"12345.0"`. Confirms numeric cells are tokenised. Does NOT pin the `"1"` vs `"1.0"` *coercion ambiguity* (see M3).

Fixtures are generated at test time via `xlwt` — no binary fixture committed. `pytest.importorskip`-style silent skip pattern is used (`try: import xlwt, xlrd; except ImportError: pytest.skip(...)`). **Per `.claude/rules/development.md` "No Test Skipping", this is acceptable only if `xlwt`/`xlrd` are genuinely optional.** `xlrd` is a production dependency (required by `verify.py:733` for the `.xls` branch); `xlwt` is test-time only. If either is missing the tests silently skip — meaning an environment without `xlwt` gets **zero `.xls` coverage with zero signal**. See M4.

### Circular-test audit

Every QC2 test (including the 4 new `.xls` tests) constructs source + JSON independently and asserts on the public `[QC2]` / `[QC1]` issue string. No test imports `_build_rst_search_units`, `_MD_SYNTAX_RE`, `_norm`, `_squash`, `_xlsx_source_tokens`, or `_verify_xlsx` (grep on `tests/ut/test_verify.py` returns zero matches for any of these private names). Only public entry point `verify_file` is used. **No circular tests introduced in r5.** OK.

### Bias check: v6 PASS is weak evidence

v6 corpus contains RST + MD only. The Excel `.xls` / `.xlsx` code paths receive **zero runtime exercise from v6**; `pytest` is the sole safety net there. The r5 xls tests close the only serious hole, but unit tests remain the entire safety net for v1.2/v1.3 `.xls` release-note sources.

### Delta vs r4 — which gaps did r5 close?

Test count: 148 (r4) → 156 (r5). All 8 new tests are real QC2/QC1 coverage additions (no refactors disguised as tests).

| r4 gap | r5 status | Evidence |
|---|---|---|
| G1 `.xls` path untested | **CLOSED** | 4 new xlwt tests (L1292, L1308, L1322, L1338) |
| G7 `.xls` numeric cell coercion | **PARTIALLY CLOSED** | L1338 pins "numeric cell missing → QC1" but does not pin `1` ≠ `"1"` coercion ambiguity (xlrd returns `1.0`, JSON holds `"1"`) |
| G2 top-level fabricated **title** (RST `__top__`) | still open | Only `__top__` content case covered |
| G3 QC2 near-miss in **CJK** | still open | L1080 is ASCII only |
| G4 QC2 on **MD** fabricated content/title (direct) | still open | MD QC2 lines only transitively hit |
| G5 QC2 cross-boundary fabrication | still open | No test codifies `\s+` collapse behaviour |
| G6 Excel `_MD_SYNTAX_RE` allowlist | still open | Spec-sanctioned tolerance with no regression guard |

### Adversarial fault-injection (bias-avoidance)

QC2 logic is byte-identical to r4 for RST/MD/xlsx. The only code actually exercised for the first time is the `.xls` branch; the logic there flows through the same `_verify_xlsx` downstream. Re-running the r3/r4 scenario matrix mentally:

| # | Scenario | Expected | Behaviour by inspection + tests |
|---|----------|----------|--------------------------------|
| 1 | `.xlsx` 1-char fab | QC2 | OK (pinned L1275) |
| 2 | `.xlsx` `"---"` standalone fab | QC2 | OK (`_MD_SYNTAX_RE` does not match bare `---`) |
| 3 | Whitespace-only residue | not flagged | OK (`.split()` drops) |
| 4 | `.xlsx` `"<b>"` fab | QC2 | OK — not pinned (G6) |
| 5 | `.xlsx` `"\| malicious \|"` fab | QC2 | OK — brittle (G6) |
| 6 | RST CJK 1-char near-miss | QC2 | OK — not pinned (G3) |
| 7 | RST `__top__` fabricated title | QC2 | OK — not pinned (G2) |
| 8 | MD section-level fab content | QC2 | OK — not pinned (G4) |
| 9 | `.xls` any QC2 case | QC2 | **NOW PINNED (r5)** — L1322 |
| 10 | `.xls` numeric cell `1` vs JSON `"1"` | *ambiguous* | Not pinned — M3 |
| 11 | `.xls` cell missing entirely | QC1 | **NOW PINNED (r5)** — L1308, L1338 |

---

## 3. v6 runtime + pytest

```
$ cd tools/rbkc && ./rbkc.sh verify 6
All files verified OK

$ cd tools/rbkc && pytest tests/ut/test_verify.py -q
156 passed in 1.15s

$ pytest tests/ut/test_verify.py -q -k xls
7 passed, 149 deselected in 0.33s
```

All green. The 7 matches on `-k xls` include the 3 pre-existing `.xlsx` tests that substring-match and the 4 new `.xls` tests — all run in this environment (xlwt + xlrd both present). **Weight**: `pytest` PASS is stronger than r4 because the `.xls` branch now has runtime evidence. `rbkc.sh verify 6` remains weak for Excel (v6 has no Excel sources).

---

## 4. Overall Rating

**Rating: 4/5 — Good (up from r4's 4/5 on the same scale, though none of the closed gaps were rated High-enough to move the score).**

- r2 H1 (Excel 1-char tolerance) **still fixed and still pinned** (`test_fail_qc2_one_char_fabrication_detected`). Comment at `verify.py:821-823` explicitly cites the spec clause.
- **r4 H1 (.xls path untested) CLOSED** — the most serious r4 gap is gone. The xlrd branch now has PASS/QC1/QC2/numeric coverage.
- **Rating did not improve to 5/5** because:
  1. Five of the seven r4 gaps (G2, G3, G4, G5, G6) remain open — none threaten current v6, but they are regression-guard holes.
  2. The new xls tests use a silent `pytest.skip` fallback on `ImportError`, which can reduce a real quality-gate signal to zero without warning (see M4).
  3. G7 is only partially addressed: the `"1"` vs `"1.0"` coercion ambiguity at the heart of r3 M3 is still unresolved — the new test pins "cell absent → QC1" but does not force the ambiguity to surface.

---

## 5. Key Issues (priority + proposed fix)

### 🔴 High Priority

None. (r4's H1 was the only High and it is now closed.)

### 🟡 Medium Priority

**M1. Fill remaining QC2 matrix gaps** (G2, G3, G4) — **CARRIED FROM r4 M1; unfixed.**

- Description: Three QC2 branches work by inspection but have no direct test.
- Proposed fix:
  - `test_fail_qc2_top_level_fabricated_title_rst` — source body present, JSON top-level `title` fabricated; assert `[QC2] ... fabricated title` with `__top__` sid.
  - `test_fail_qc2_near_miss_cjk_one_char` — source `テキスト内容。`, JSON section content `テキスト内宏。`; assert QC2.
  - `test_fail_qc2_md_fabricated_content` — MD source + MD JSON with a section whose content is absent; assert QC2 via `fmt="md"`.

**M2. Pin the Excel `_MD_SYNTAX_RE` tolerance allowlist** (G6) — **CARRIED FROM r4 M2; unfixed.**

- Description: `verify.py:718-727` is a spec-sanctioned QC2-bypass zone. Silent widening is the most dangerous class of quality-gate regression. No test enumerates which patterns are absorbed vs not.
- Proposed fix: Two tests:
  - `test_excel_qc2_md_syntax_tolerance_allowlist_absorbs` — feed `"**"`, `"|"`, `"|---|"`, `"##"`, `"> "`, `"1. "`, `` "`" `` as orphan residual; assert no QC2 fires.
  - `test_excel_qc2_md_syntax_tolerance_allowlist_does_not_absorb` — feed `"---"` (bare), `"<b>"`, `"foo"`, `"@ref"`; assert QC2 fires for each.

**M3. `.xls` numeric cell coercion ambiguity** (G7) — **ONLY PARTIALLY ADDRESSED IN r5.**

- Description: `str(sheet.cell_value(rx, cx))` on xlrd numeric cells yields `"12345.0"` / `"1.0"` while JSON typically holds `"12345"` / `"1"`. The r5 test `test_fail_xls_numeric_cell_missing_from_json` confirms that an entirely-missing cell fires QC1 — but the harder, more realistic case (cell value `1`, JSON correctly contains `"1"`) is not pinned. Current behaviour is: `_xlsx_source_tokens` yields `"1.0"`, `json_text.find("1.0")` returns `-1`, `[QC1]` fires — **a false alarm on a file where the JSON is in fact correct**. A false alarm here blocks RBKC runs on v1.2/v1.3 release-note `.xls` files with numeric columns.
- Proposed fix: Add `test_xls_numeric_cell_integer_in_json` — cell `1`, JSON `"1"`, and assert the *actual* behaviour so the ambiguity is codified. If the behaviour is a false QC1, that is a bug that should be fixed (spec does not sanction `.0` coercion); if it passes, the test locks the behaviour in. Either way the ambiguity surfaces. Per `.claude/rules/rbkc.md` — surfacing the ambiguity is the correct action.

**M4. Silent `pytest.skip(...)` on `ImportError` for xlwt/xlrd** — **NEW IN r5.**

- Description: Four new `.xls` tests use `try: import xlwt, xlrd; except ImportError: pytest.skip(...)`. `.claude/rules/development.md` says *"Do not use pytest.mark.skip, pytest.mark.skipif, or pytest.importorskip to bypass tests. ... every skip must be treated as a failure to investigate."* The current pattern is functionally equivalent to `importorskip`. In an environment missing `xlwt`, the `.xls` tests quietly become no-ops — a CI pipeline upgrade that drops `xlwt` from the dev deps would silently remove the entire `.xls` quality gate.
- Proposed fix: Either (a) add `xlwt` to a `dev-requirements.txt` / `pyproject.toml [dev]` so it is always present and the try/except is removed, OR (b) check in a tiny binary `.xls` fixture (≤2 KB) and import only `xlrd` (which is a prod dep and always present). Option (b) is simpler and removes the skip entirely. Replace the skip with a hard failure so missing dev deps are caught at `pytest` time, not masked.

### 🟢 Low Priority

**L1. Cross-boundary fabrication guard** (G5) — `test_fail_qc2_cross_boundary_fabrication`: two non-contiguous source blocks, JSON unit that only appears if the two are concatenated under `\s+` collapse; assert behaviour (spec-correct is currently flagging it).

---

## 6. Positive aspects

- **r4 H1 CLOSED cleanly.** Four targeted tests, all using the public `verify_file` entry point, all using on-disk xlwt fixtures generated at test time — no binary blob to review, no internal import. The PASS test (L1292) exercises the happy path, the QC1 tests (L1308, L1338) cover the "cell missing" branch, and the QC2 test (L1322) directly pins the xlrd + residual-delete pipeline for fabrication detection. This is the right shape for a gap closure.
- r2 H1 fix **still present and still pinned** by `test_fail_qc2_one_char_fabrication_detected`. Code comment at `verify.py:821-823` durably documents the spec rationale.
- Zero-exception principle upheld across all three paths: unknown RST role / MD token / RST parse error surfaces as `[QC1]`, never a silent pass.
- QC2 ↔ QC3 ↔ QC4 branching structurally symmetric across RST (`verify.py:574-588`) and MD (`verify.py:669-683`) — easy to audit for spec conformance.
- Top-level `title`/`content` treated as first-class search units (`__top__`) across all three paths — no special-case skip that could hide fabrication.
- New `.xls` tests are not circular: every assertion is on the public issue string. No `_xlsx_source_tokens` / `_verify_xlsx` imports. Future edits to the xlrd branch will be caught by behaviour regressions.
- `_MD_SYNTAX_RE` remains isolated to the Excel path; RST/MD share no tolerance list with Excel.

---

## 7. Recommendations

1. **Treat M4 as the new H-equivalent.** The r5 `.xls` tests are only as strong as the environment they run in. Replace `try/except ImportError: pytest.skip` with a hard dev-dep requirement or a checked-in binary fixture. Otherwise the gap-closure is conditional on an undocumented env contract.
2. **Close M3 before v1.2/v1.3 RBKC runs.** The `1` vs `"1.0"` coercion is virtually certain to appear in release-note `.xls` files. Landing on a false QC1 there costs a debugging cycle with zero unit-test signal. Add one test, accept whatever the current behaviour is, then fix the coercion if the test reveals a false alarm.
3. M2 remains the highest-leverage cheap win: two regex assertions pin a spec-sanctioned tolerance zone. Spec-sanctioned tolerances are silent-by-design and deserve stronger regression guards than ordinary logic.
4. Run `pytest --cov=scripts.verify.verify tests/ut/test_verify.py` to confirm the xlrd branch at `verify.py:732-742` now reports non-zero coverage — this is the concrete evidence for H1 closure.

---

## 8. Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L461-505, L508-711, L718-830, L837-858)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L819-1200, L1202-1373)
- `/home/tie303177/work/nabledge/work2/.work/00299/review-z1-r4/QC2.md` (consulted only after independent evaluation)
- `/home/tie303177/work/nabledge/work2/.claude/rules/development.md` (No Test Skipping clause — basis for M4)
