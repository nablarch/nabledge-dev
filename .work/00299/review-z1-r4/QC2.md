# QC2 正確性 (Accuracy — no fabrication) — QA Engineer Review (r4)

**Reviewer**: Independent QA Engineer (bias-avoidance; spec as authoritative; prior r3 review consulted only after independent evaluation, for regression comparison)
**Date**: 2026-04-23
**Scope**: `tools/rbkc/scripts/verify/verify.py` QC2 logic + unit tests + v6 runtime behaviour
**Stance**: v6 PASS treated as weak evidence; spec (`rbkc-verify-quality-design.md` §3-1 手順 4 + Excel 節) is authoritative. `pytest` + `rbkc.sh verify 6` are necessary-but-not-sufficient.

---

## 1. Implementation

### RST — `_check_rst_content_completeness` (`verify.py:529-608`)

Decision tree per search unit (`verify.py:569-588`):

- `norm_source.find(norm_unit, current_pos)` → hit: consume, advance.
- Miss → `norm_source.find(norm_unit)` with no offset (`verify.py:575`).
  - `prev_idx == -1` + title → `[QC2] fabricated title` (`verify.py:578`)
  - `prev_idx == -1` + content → `[QC2] fabricated content` (`verify.py:584`)
  - Otherwise QC3 (in consumed) / QC4 (misplaced).
- `UnknownSyntaxError` surfaces as `[QC1]` (`verify.py:546-548`) — no silent fallback hiding QC2.
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

### Spec conformance (§3-1 手順 4 + Excel 節)

| Spec clause | Location | Status |
|---|---|---|
| 手順 4「正規化ソースに全く存在せず → QC2」 | `verify.py:577, 583, 672, 678` (`prev_idx == -1` branch) | ✅ |
| 手順 4 QC2 vs QC3 split (never-seen vs consumed) | `_in_consumed` check at `verify.py:579, 585, 674, 680` | ✅ |
| Excel 手順 3「空白・空行を除く残存 → QC2」 | `verify.py:825` (`.split()` drops whitespace only) | ✅ |
| Excel「許容構文要素リスト」 | `_MD_SYNTAX_RE` @ `verify.py:718-727` | ✅ |
| No silent tolerance | No length / count thresholds anywhere in the QC2 path | ✅ |

### Silent-tolerance audit

- RST/MD `_squash` (`verify.py:631-632`) collapses whitespace on both sides — spec §3-1 手順 4「空白・改行正規化のみ」matches. Not a silent tolerance.
- Excel `_MD_SYNTAX_RE` is a **spec-sanctioned** tolerance (手順 3 allowlist). It is NOT a hidden fudge, but see M2 below — it is not pinned by a regression test.
- No `try: ... except: pass` or `continue` silently hiding QC2 in the three paths.

---

## 2. Unit tests

### Present QC2 coverage (`tools/rbkc/tests/ut/test_verify.py`)

| Test | Line | Covers |
|------|------|--------|
| `test_fail_qc2_fabricated_title` | L821 | RST section title not in source |
| `test_fail_qc2_fabricated_content` | L829 | RST section content not in source |
| `test_fail_qc2_multiple_fabricated_contents` | L1045 | 2 sections both fabricated — count assertion |
| `test_fail_qc2_top_level_fabricated_content` | L1055 | Top-level `content` (RST `__top__` path) |
| `test_fail_qc2_near_miss_one_char_differs` | L1062 | ASCII `ABCDEFG` → `ABCXEFG` |
| `test_fail_qc2_fabricated_content_in_json` | L1239 | Excel QC2 multi-char fabrication |
| `test_fail_qc2_one_char_fabrication_detected` | L1257 | **Excel 1-char fabrication** — pins r2 H1 fix |

### QC2 vs QC3 distinction
- RST: `test_fail_qc3_duplicate_content_rst` (L1070), `test_fail_qc3_duplicate_title_md` (L1079), `test_fail_qc3_duplicate_content_md` (L1112), `test_fail_qc3_top_level_and_section_content_duplicated` (L1101)
- Excel: `test_fail_qc3_duplicate_cell_in_json` (L1274)

Both branches (never-seen vs consumed) are exercised on RST, MD, and Excel. ✅

### Circular-test audit
Every QC2 test constructs source + JSON independently and asserts on the public `[QC2]` issue string. No test imports `_build_rst_search_units`, `_MD_SYNTAX_RE`, `_norm`, or `_squash`. No test echoes a production constant. **No circular tests.** ✅

### Bias check: v6 PASS is weak evidence

v6 corpus contains RST + MD only. The Excel `.xls` / `.xlsx` code paths receive **zero runtime exercise from v6**; `pytest` is the sole safety net there. Consequently any gap in unit tests is a gap in the total quality gate.

### Delta vs r3 — which r3 gaps did r4 close?

Test count: 134 (r3) → 148 (r4). The 14 new tests are **not** in the QC2 gap set identified by r3: grep of the test file confirms no new `xls\b`, `xlwt`, `cjk_near_miss`, `md_fabricated`, `top_level_fabricated_title`, `_syntax_tolerance_allowlist`, `cross_boundary`, or `numeric_cell_coercion` tests. The 7 r3 QC2 gaps are **all still open**.

### Gap matrix (r4)

| # | Missing | Severity | Evidence | r3 status |
|---|---------|----------|----------|-----------|
| G1 | `.xls` path: **no test** | 🔴 High | `grep "\.xls\b\|xlrd\|xlwt"` on test_verify.py → 0 matches. `verify.py:732-742` (`xlrd` branch) has 0 coverage. | r3 G1 — unfixed |
| G2 | QC2 top-level fabricated **title** (RST `__top__` branch) | 🟡 Medium | Only `__top__` content case is covered (L1055). Title branch at `verify.py:578` with `sid == "__top__"` unpinned. | r3 G2 — unfixed |
| G3 | QC2 near-miss in **CJK** | 🟡 Medium | L1062 is ASCII only. CJK normalisation differs (no word boundaries). | r3 G3 — unfixed |
| G4 | QC2 on **MD** fabricated content/title (direct assertion) | 🟡 Medium | `verify.py:673, 679` (MD QC2 lines) only transitively hit via top-level MD tests; no direct MD QC2 test constructs a section-level fabrication and asserts `[QC2]` on the MD path. | r3 G4 — unfixed |
| G5 | QC2 **cross-boundary** fabrication | 🟢 Low | `\s+` collapse could mask fabrications that span block boundaries; no test codifies. | r3 G5 — unfixed |
| G6 | Excel `_MD_SYNTAX_RE` allowlist not pinned | 🟡 Medium (raised from 🟢 Low) | `verify.py:718-727` is a spec-level tolerance. No test enumerates which patterns are absorbed vs not. A regex edit silently changes scope; no regression guard. | r3 G6 — unfixed |
| G7 | Excel `.xls` numeric cell coercion (`1` → `"1.0"`) | 🟡 Medium | `str(sheet.cell_value(...))` on xlrd floats can produce `"1.0"`; no test pins. Tied to G1. | r3 G7 — unfixed |

**Severity escalation on G6**: I am promoting G6 from 🟢 Low (r3) to 🟡 Medium because `_MD_SYNTAX_RE` is a spec-sanctioned tolerance — i.e. a zone where verify deliberately does NOT raise QC2. Any silent widening of this allowlist (e.g. a maintainer adding `<.*?>` to tolerate HTML) would permit real fabrications to slip through with zero test failure. Spec-sanctioned tolerances deserve regression tests even more than ordinary logic.

### Adversarial fault-injection (bias-avoidance, logic unchanged from r3)

Since QC2 logic is byte-identical to r3 (same line numbers for the decision tree when offset for insertions, same branches, same regex), the r3 fault-injection results carry over:

| # | Scenario | Expected from spec | Code behaviour (by inspection) |
|---|----------|--------------------|--------------------------------|
| 1 | Excel 1-char fab (`"ABC"` cell, JSON `"ABC Y"`) | QC2 | ✅ (pinned by L1257) |
| 2 | Excel `"---"` standalone fab (no pipes) | QC2 | ✅ (`_MD_SYNTAX_RE` only matches `\|[-:]+\|...`, not bare `---`) |
| 3 | Excel whitespace-only residue | not flagged | ✅ (`.split()` drops) |
| 4 | Excel `"<b>"` fab | QC2 | ✅ (not in allowlist) — **but not pinned** (G6) |
| 5 | Excel `"| malicious |"` fab | partially absorbed | ⚠️ `\|` and `** **` absorbed, `malicious` remains → QC2. OK but brittle. |
| 6 | RST CJK 1-char near-miss (`テキスト内宏。` vs `テキスト内容。`) | QC2 | ✅ — `find` on distinct string fails, `prev_idx == -1` → QC2. Not pinned (G3). |
| 7 | RST `__top__` fabricated title | QC2 | ✅ — `_build_rst_search_units` emits `("__top__", False)`; QC2 fires. Not pinned (G2). |
| 8 | MD section-level fab content | QC2 | ✅ — `verify.py:679`. Not pinned as direct MD QC2 (G4). |
| 9 | `.xls` any case | unknown | ❌ **NOT EXERCISED** — no test, no v6 source. |

---

## 3. v6 runtime + pytest

```
$ cd tools/rbkc && ./rbkc.sh verify 6
All files verified OK

$ cd tools/rbkc && pytest tests/ut/test_verify.py -q
148 passed in 1.26s
```

Both green. **Weight**: v6 PASS is weak because (a) v6 has no `.xls`, and (b) v6 RBKC current output happens not to fabricate — PASS tells us only that the path does not false-alarm. Pytest PASS is stronger but only as strong as the unit tests' coverage — and the Excel `.xls` path has zero unit test coverage.

---

## 4. Overall Rating

**Rating: 4/5 — Good (unchanged from r3).**

- r2 H1 (Excel 1-char tolerance) is **still fixed and still pinned** (`test_fail_qc2_one_char_fabrication_detected` L1257). Comment at `verify.py:821-823` explicitly states the spec rationale — future maintainers cannot re-introduce tolerance by accident.
- QC2 spec conformance on RST/MD/.xlsx is correct and independently verifiable without consulting RBKC internals.
- **Rating did not improve to 5/5** because the 7 QC2 test gaps identified in r3 are **all still open** in r4. None threaten current v6, but they are real regression-guard holes for .xls sources (v1.2/v1.3 release notes) and for the CJK / MD / top-level-title matrix cells.

---

## 5. Key Issues (priority + proposed fix)

### 🔴 High Priority

**H1. `.xls` path has zero test coverage** (`verify.py:732-742`) — **CARRIED FROM r2 H2 / r3 H1; still unfixed.**

- **Description**: The `xlrd` branch is entirely untested. v1.2/v1.3 sources contain `.xls` release-note files. Numeric-cell coercion (`1` → `"1.0"`), encoding, and sheet-iteration differences from `openpyxl` have zero regression guard. v6 PASS provides zero signal here.
- **Proposed fix**: Add two tests mirroring `.xlsx`:
  - `test_pass_real_xls`
  - `test_fail_qc2_fabricated_content_in_xls`

  Generate the fixture at test time using `xlwt` (dev-time dependency; `xlrd` is already in prod deps), OR check in a ≤1KB `.xls` fixture. Include one numeric-cell case (G7).
- **Gate**: test-only — no verify logic change — no spec review needed per `.claude/rules/rbkc.md`.

### 🟡 Medium Priority

**M1. Fill the QC2 matrix gaps with regression guards** (G2, G3, G4) — **CARRIED FROM r3 M1; unfixed.**

- **Description**: Three QC2 branches work by inspection but have no direct test.
- **Proposed fix**: Add:
  - `test_fail_qc2_top_level_fabricated_title_rst` — source body present, JSON `title` fabricated; assert `[QC2] ... fabricated title` with `__top__` or appropriate sid.
  - `test_fail_qc2_near_miss_cjk_one_char` — source `テキスト内容。`, JSON section content `テキスト内宏。`; assert QC2.
  - `test_fail_qc2_md_fabricated_content` — MD source + MD JSON with a section whose content is absent from source; assert QC2 via `fmt="md"`.

**M2. Pin the Excel `_MD_SYNTAX_RE` tolerance allowlist** (G6) — **SEVERITY RAISED FROM r3's 🟢 Low.**

- **Description**: `verify.py:718-727` is a spec-sanctioned QC2-bypass zone. No test enumerates which MD-syntax patterns are tolerated vs not, so any regex edit silently widens/narrows the tolerance. Silent widening of a tolerance allowlist is the single most dangerous class of quality-gate regression.
- **Proposed fix**: Add two tests:
  - `test_excel_qc2_md_syntax_tolerance_allowlist_absorbs` — enumerate `"**"`, `"|"`, `"|---|"`, `"##"`, `"> "`, `"1. "`, `` "`" `` in isolation; assert each is absorbed (no QC2 fires when cells cover the non-syntax content).
  - `test_excel_qc2_md_syntax_tolerance_allowlist_does_not_absorb` — enumerate `"---"` (bare, no pipes), `"<b>"`, `"foo"`, `"@ref"`; assert each fires QC2.

**M3. `.xls` numeric cell coercion** (G7) — **CARRIED FROM r3 M3; unfixed.**

- **Description**: `str(sheet.cell_value(rx, cx))` on xlrd numeric cells yields `"1.0"` while JSON typically has `"1"`. Without a test, this produces simultaneous false QC1 + false QC2 pairs, or — worse — silent passes.
- **Proposed fix**: After H1 scaffold lands, add `test_xls_numeric_cell_coercion` with cell value `1`, JSON `"1"`; assert expected behaviour. Spec does not explicitly address this, so the test **forces the ambiguity to surface** — which is itself valuable per `.claude/rules/rbkc.md`.

### 🟢 Low Priority

**L1. Cross-boundary fabrication guard** (G5) — `test_fail_qc2_cross_boundary_fabrication`: two non-contiguous source blocks, JSON unit that only appears if the two are concatenated under `\s+` collapse; assert behaviour (spec-correct is currently flagging it).

---

## 6. Positive aspects

- r2 H1 fix is **still present and still pinned** by `test_fail_qc2_one_char_fabrication_detected`. The code comment at `verify.py:821-823` explicitly cites the spec clause — a durable, self-documenting guard against future regression.
- Zero-exception principle upheld in all three paths: unknown RST role / MD token / RST parse error surfaces as `[QC1]`, never as a silent pass that would hide QC2 at a later stage.
- QC2 ↔ QC3 ↔ QC4 branching is structurally symmetric across RST (`verify.py:574-588`) and MD (`verify.py:669-683`) — easy to audit for spec conformance.
- Top-level `title`/`content` treated as first-class search units (`__top__`) across all three paths — no special-case skip that could hide fabrication.
- Tests are not circular: every QC2 assertion is on the public issue string `[QC2] ...`. No test imports `_MD_SYNTAX_RE`, `_build_rst_search_units`, or any normaliser internal. A future bug-introducing edit to these internals will be caught by behaviour regressions, not by a mirror-constant.
- `_MD_SYNTAX_RE` is isolated to the Excel path; the RST/MD paths share no tolerance list with Excel, reducing cross-contamination risk.

---

## 7. Recommendations

1. **Close H1 before v1.2/v1.3 RBKC work begins.** The `.xls` branch will be exercised on real data for the first time when v1.2/v1.3 run through RBKC. Landing on a real regression at that point (with no unit-test guard) means debugging from zero coverage. The fix is ~30 lines of test code.
2. **Treat M2 as a hardening priority even without user-visible impact.** Spec-sanctioned tolerance zones are higher risk than ordinary logic because they are silent-by-design. Pinning them is cheap (pure assertions on regex behaviour) and catches the single most dangerous regression mode (allowlist widening).
3. Consider adding a `conftest.py` helper `make_xlsx(rows)` / `make_xls(rows)` to keep Excel-fixture setup to one line per test — this lowers the barrier for future Excel regression tests.
4. Run `pytest --cov=scripts.verify.verify tests/ut/test_verify.py` once and confirm `_xlsx_source_tokens`'s `ext == ".xls"` branch reports 0 coverage — this is the concrete evidence for H1 and a good sanity check before closing this review cycle.

---

## 8. Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (L461-505, L508-711, L718-830)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (L819-1066, L1181-1300)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-1 手順 1-4 L159-195, Excel 節 L207-226)
- `/home/tie303177/work/nabledge/work2/.work/00299/review-z1-r3/QC2.md` (consulted only after independent evaluation, for regression comparison)
