# Z-1 r9 bias-avoidance QA review — QC4 + `_classify_missed_unit`

**Scope**: `check_content_completeness` QC4 branch (RST + MD), `_classify_missed_unit`
**Target files**:
- `tools/rbkc/scripts/verify/verify.py` lines 713–752, 755–833, 836–920
- `tools/rbkc/tests/ut/test_verify.py` `TestCheckContentCompleteness` (lines 1244–1736)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1

---

## Findings

### F1. QC4 label narrowness vs verify operational definition — spec silent on title-only misplacement

**Spec quote (§3-1 L84)**:
> `**QC4** | 配置正確性 | ソースのセクション A のコンテンツが JSON の異なるセクションに配置されている | 削除手順 → 手順2`

**Spec quote (§3-1 L165–166, 手順2)**:
> `2. **削除と配置チェック（QC4）**: **手順 0 で生成した正規化ソース**を対象に、手順1のリストを JSON 順に削除する。各要素の削除位置（正規化ソース上のオフセット）を記録する。`
> `   - JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも前であれば **FAIL（QC4: 配置ミス）**`

**Spec quote (§3-1 L185)**:
> `| 削除位置が JSON 順より前に逆行 | QC4 |`

**Observation**: L84 restricts QC4 wording to "セクション A のコンテンツ" (content). L165/L185 define QC4 operationally over "JSON 順 i 番目要素" with no title/content distinction, and L161 states the extraction unit set is `top-level title → top-level content → sections[0].title → sections[0].content → …`. The implementation reports QC4 uniformly for any unit (title or content) whose deletion position regresses, consistent with L165/L185. L84's narrower wording is not quoted as excluding title misplacement, so this is consistent with the spec's operational clause.

No violation. Recorded as an observation on a wording asymmetry between L84 and L165/L185.

---

### F2. `_classify_missed_unit` misclassifies when earliest occurrence is consumed but middle is unconsumed — class covered by test, but not by a spec-quoted oracle

**Spec quote (§3-1 L171–173)**:
> `4. **未削除チェック（QC2, QC3）**: 手順2で正規化ソースから削除できなかった JSON テキストをチェックする。`
> `   - 正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**`
> `   - 既に削除済みの領域と重複していた（ソース中に複数回出現し、先行セクションで消費済み） → **FAIL（QC3: 重複）**`

**Observation**: L173 defines QC3 as "先行セクションで消費済み" — implementation docstring (line 728) interprets this as "*every* earlier occurrence to be consumed". Spec wording is "先行セクションで消費済み" which is ambiguous between "at least one earlier occurrence consumed" and "all earlier occurrences consumed". The implementation chose the stricter reading so that a mixed-consumption case falls into QC4 (position regression). `test_fail_qc4_not_qc3_when_middle_occurrence_is_unconsumed` pins this reading.

The spec is silent on the mixed-consumption case. The chosen reading is consistent with L185 "削除位置が JSON 順より前に逆行 | QC4" because an unconsumed earlier occurrence, had it been the correct target, would still represent a position regression relative to `current_pos`. Recorded as a spec-silent implementation decision backed by a test.

---

### F3. `_classify_missed_unit` returns "QC2" for empty `norm_unit` — spec silent

**Spec quote (§3-1 L172)**:
> `   - 正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**`

**Observation**: `_classify_missed_unit` line 734–735: `if not norm_unit: return "QC2"`. Spec does not define behaviour for an empty search unit. The RST builder (`_build_rst_search_units` lines 672–687) suppresses empty normalised units by guarding `if norm:`, so this branch is unreachable on the RST path. The MD path (lines 864–877) guards only `if title:` / `if content:` — an input whose `_squash(title)` collapses to "" (e.g. a whitespace-only or ZWSP-only title) would pass the truthy guard on the raw value and produce an empty `unit`, reaching this branch. No test exercises this case. Spec silent.

---

### F4. Label string hardcodes "content" for any `is_content=True` unit — spec uses role-level labelling

**Spec quote (§3-1 L161)**:
> `1. **抽出**: JSON の top-level `title` / top-level `content` / 各セクション `title` / 各セクション `content` を JSON 順のテキストリストとして抽出する。`

**Observation**: The verify output message at lines 801–802 / 899–900 uses `label = "title" if not is_content else "content"`. Top-level title and top-level content use synthetic `sid = "__top__"` (lines 672, 676, 866, 868); the operator reading a `[QC4] section '__top__': misplaced title: …` report must infer "this is the document-level title". Spec does not mandate a specific message format, so this is not a violation. Recorded as an observation.

---

### F5. QC4 detection relies on `find(unit, current_pos)` — collision risk when unit is a substring of a later unit

**Spec quote (§3-1 L165)**:
> `**削除と配置チェック（QC4）**: **手順 0 で生成した正規化ソース**を対象に、手順1のリストを JSON 順に削除する。`

**Observation**: `_check_rst_content_completeness` line 792 and `_check_md_content_completeness` line 890 use `norm_source.find(norm_unit, current_pos)`. If unit *i* is a substring of the concatenated tail of the source, it can consume bytes that a later, longer unit *j* relied upon, causing *j*'s lookup to fail and be classified by `_classify_missed_unit`. The verdict (QC2/QC3/QC4) then depends on whether those bytes still appear elsewhere. Spec L165 defines the algorithm as "手順1のリストを JSON 順に削除する" with no tie-breaking rule for prefix-collisions. The chosen implementation (greedy forward `find`) is the most natural reading but produces verdicts dependent on JSON-unit ordering and substring relationships. No test pins the resulting verdict for a prefix/substring collision between adjacent JSON units. Spec silent on tie-breaking; recorded as an observation.

---

### F6. QC4 for Excel excluded — spec-explicit

**Spec quote (§3-1 L84)**:
> `| **QC4** | 配置正確性 | … | 削除手順 → 手順2 | ⚠️ | ⚠️ | — |`

**Observation**: The "—" in the Excel column is the spec's explicit opt-out. `verify_file` Excel path (not in this review's scope) contains no QC4 branch, and `_classify_missed_unit` is never invoked from the Excel path. Consistent with spec. No finding.

---

### F7. Test `test_fail_qc4_misplaced_title` does not pin the label token

**Spec quote (§3-1 L161)**:
> `1. **抽出**: JSON の top-level `title` / top-level `content` / 各セクション `title` / 各セクション `content` を JSON 順のテキストリストとして抽出する。`

**Observation**: Line 1296 asserts `"[QC4]" in i and "s2" in i` but does not assert `"title"` or `"misplaced title"`. A regression that swapped the label to `"content"` for title misses would still pass. MD counterpart `test_fail_qc4_misplaced_title_md` (line 1613) has the same gap. Spec does not mandate a specific label string, so this is not a spec violation — recorded as a test-pinning weakness.

---

### F8. No test pins behaviour when both QC4 and QC1 residue co-occur for the same JSON unit

**Spec quote (§3-1 L169)**:
> `3. **残存チェック（QC1）**: 削除後の正規化ソースの残存テキストをチェックする。**空白文字 / 改行 / タブ以外のテキスト**が残っていれば **FAIL（QC1: 欠落）**。`

**Observation**: When JSON unit *i* is misplaced (QC4-classified), the source region it should have covered remains unconsumed and must surface as QC1 residue in the same run. `test_fail_qc4_misplaced_title` and `test_fail_qc4_misplaced_content_rst` assert the presence of QC4 but neither asserts the corresponding QC1 residue count. Spec L169 requires both to fire independently. Implementation at lines 810–831 / 905–923 does run the residue pass regardless of per-unit verdict, so the behaviour is likely correct, but it is not pinned by a test. Recorded as a test-coverage observation.

---

### F9. `_classify_missed_unit` uses `start = pos + 1` stepping — correct for overlapping occurrences

**Spec quote (§3-1 L172–173)**:
> `   - 正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**`
> `   - 既に削除済みの領域と重複していた（ソース中に複数回出現し、先行セクションで消費済み） → **FAIL（QC3: 重複）**`

**Observation**: Line 747 `start = pos + 1`. For a unit that appears at overlapping positions (e.g. "AAA" in "AAAA"), this enumerates all occurrences correctly. An alternative `start = pos + len(norm_unit)` would miss overlap-starting occurrences and could mis-label QC3 vs QC4 when the overlapping occurrence is unconsumed. Spec does not specify stepping. The chosen implementation is defensive. No test covers an overlap-start case. Recorded as a spec-silent implementation choice.

---

## Observations (spec-silent, not findings)

- **O1**: `_classify_missed_unit` breaks on the first unconsumed earlier occurrence (line 746 `break`). If multiple unconsumed earlier occurrences exist, the function does not report how many — the QC4 issue message contains only the unit text, not the regression distance. Spec L185 does not require regression distance. Acceptable.
- **O2**: `consumed` list is appended in verdict-by-verdict order (line 794) but never updated for missed units. A missed unit that is later classified QC4 does not consume any range. This is consistent with L167 "見つからない場合は手順4 の対象に回す" (it is not consumed).
- **O3**: The `_in_consumed` closure in RST path (line 787–789) and MD path (line 885–887) are duplicated definitions with identical semantics. No spec implication.
- **O4**: `_classify_missed_unit` receives `in_consumed` by closure, not by value — it always reads the `consumed` list of the calling path. Correct but implicit.
- **O5**: Spec §3-1 手順2 L166 phrases the QC4 trigger as "i 番目要素の削除位置が、i-1 番目の削除位置よりも前". The implementation does not compare positions i vs i-1 directly; it uses `current_pos` (which equals the end of the last consumed range) and `find(unit, current_pos)`. These are algorithmically equivalent only if JSON units never consume overlapping ranges in the source. Because `consumed` is built from forward-only `find` results with `current_pos` advancing, the two formulations coincide. Spec silent on equivalence proof.

---

## Horizontal check

Searched for other call sites of `_classify_missed_unit` and other places in `verify.py` that classify QC2/QC3/QC4:

```
grep -n "_classify_missed_unit\|QC2\|QC3\|QC4" scripts/verify/verify.py
```

Found only the two call sites (RST line 797, MD line 895). No third path classifies these codes. `_classify_missed_unit` has a single definition. No horizontal duplication of the classification logic.

Searched for other places that compute sequential-delete position regression:

```
grep -n "current_pos\|consumed" scripts/verify/verify.py
```

Two nearly-identical blocks exist (RST lines 784–804, MD lines 882–902). Identical classification semantics, identical `_in_consumed` closures, identical message formats. No divergence found.

---

## Summary counts

- Findings with spec quote: 0 violations; 9 observations on spec-silent behaviour or test-pinning gaps (F1–F9).
- Spec-silent observations: 5 (O1–O5).
- Horizontal check: no divergent implementation of the classification logic.
