# Z-1 r8 Review — QC3 (duplicate content)

Scope: `tools/rbkc/scripts/verify/verify.py` QC3 logic + `_classify_missed_unit`; tests in `tools/rbkc/tests/ut/test_verify.py`.

Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1.

## Findings

### F1. QC3 tests still use OR-substring assertions instead of label-exact `[QC3]`

Spec §3-1 (L184):

> | JSON テキストが正規化ソースに存在するが先行削除済み | QC3 |

The spec distinguishes QC3 from QC2/QC4 by the exact classifier label. Three QC3 tests assert with bare `"QC3"` substring, which passes even if the emitted label is actually `[QC2]` or `[QC4]` (both strings also happen to contain `QC`-prefixed tokens under other formulations, and more importantly, a loose `"QC3" in i` does not prove QC3 was raised to the exclusion of QC2/QC4 — a message containing `not QC3` / `QC3/QC4` discussion in any future debug text would also match). The r7 objective was to adopt `"[QC3]" in i` with a negative assertion excluding `[QC2]`/`[QC4]`, as already done for the rst/md/top-level cases at lines 1484–1485, 1519–1520, 1529–1530.

Still loose at:

- `test_fail_qc3_duplicate_title` (line 1215): `assert any("QC3" in i for i in issues)` — no `[` bracket, no QC2/QC4 exclusion.
- `test_fail_qc3_duplicate_title_md` (line 1494): `assert any("QC3" in i for i in issues)` — same.
- `test_pass_qc3_short_cjk_repeated_in_source_and_json` (line 1507): `assert not any("QC3" in i and "概要" in i for i in issues)` — negative guard uses substring `"QC3"` not `"[QC3]"`.

Proposed fix: change to `"[QC3]" in i` (and in the negative case, `"[QC3]" in i`), and for the two positive cases add the exclusion `assert not any("[QC2]" in i or "[QC4]" in i for i in issues)` to match the r7 pattern used elsewhere in the same test class.

### F2. `_classify_missed_unit` test coverage relies on `_check` integration; no direct unit test pins the three-way branch

Spec §3-1 判定分岐 (L184):

> | JSON テキストが正規化ソースに存在するが先行削除済み | QC3 |

and (L185):

> | 削除位置が JSON 順より前に逆行 | QC4 |

The helper encodes the spec's "全ての先行出現が消費済み" rule (verify.py L694–L698 docstring). The rule is exercised only through the full `check_content_completeness` pipeline. `test_fail_qc4_not_qc3_when_middle_occurrence_is_unconsumed` (L1627) is the only test that stresses the mixed-consumption case, and it goes via `fmt="md"` end-to-end. A direct unit test on `_classify_missed_unit(norm_source, norm_unit, consumed, in_consumed)` covering the three return values (no-occurrence → QC2, all-earlier-consumed → QC3, any-earlier-unconsumed → QC4) would prevent regressions that preserve end-to-end output while breaking the helper's contract (e.g., reintroducing a `find(unit)` shortcut that only inspects the earliest occurrence).

Proposed fix: add a dedicated `TestClassifyMissedUnit` suite with three cases driving the helper directly.

### F3. QC3 RST path and MD path are structurally duplicated — only one horizontal bug fix updates both

verify.py L762–L770 (RST) and L860–L868 (MD) are identical dispatch blocks over `_classify_missed_unit`. Any future spec change to the QC3 message format (e.g., spec adds "JSON 順 n 番目" to the emitted string) must be applied twice. This is not a spec violation today — the message wording in both paths matches — but it is a horizontal-maintenance trap.

Proposed fix: extract the dispatch into a small helper `_emit_miss(verdict, sid, label, orig_unit) -> str` shared by both `_check_rst_content_completeness` and `_check_md_content_completeness`.

## Observations

- `_classify_missed_unit` correctly implements spec L184 "先行削除済み = ALL earlier occurrences consumed", not the common-off-by-one "earliest earlier occurrence consumed" reading. The docstring (verify.py L694–L698) is explicit about this, and `test_fail_qc4_not_qc3_when_middle_occurrence_is_unconsumed` (L1627) pins the distinction with an explicit fixture. Both are good.
- Excel QC3 (verify.py L978–L985, test L1797) uses the same "earliest occurrence, check consumption" pattern. For Excel the token set is cell values and `consumed` regions are disjoint substrings — the simpler check is spec-sound for xlsx because the Excel QC3 spec (§3-1 Excel 節) does not require the full multi-occurrence sweep the RST/MD QC3 needs. No finding.
- `test_fail_qc3_duplicate_content_rst` (L1484), `test_fail_qc3_top_level_and_section_content_duplicated` (L1519), and `test_fail_qc3_duplicate_content_md` (L1529) already use `[QC3]` + QC2/QC4 exclusion — this is the pattern the three loose tests in F1 should match.
- The Excel QC3 test at L1811 correctly uses `[QC3]` label-exact plus `[QC1]`/`[QC2]` exclusion.
