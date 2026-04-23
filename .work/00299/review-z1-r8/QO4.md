# QO4 Bias-Avoidance Review (Z-1 r8)

Target: `check_index_coverage` + `_parse_toon_index` in
`tools/rbkc/scripts/verify/verify.py` vs spec §3-3 (QO4),
tests in `tools/rbkc/tests/ut/test_verify.py :: TestCheckIndexCoverage`.

## Findings

### F1 (Medium) — Row-count mismatch message fires spuriously when a prior row failed the column-count / quoted-field check

Spec §3-3:
> "4. **JSON parse 失敗**: `knowledge_dir` 配下の JSON が parse 失敗した場合は **QO4 FAIL** とする (silent skip 禁止。ゼロトレランスに基づき、壊れたファイルは検出対象とする)"

(zero-tolerance applies analogously to TOON parse drift that r7 introduced.)

Description: In `_parse_toon_index`, a row that fails the column-count check (or the quoted-field check) is flagged and `continue`d without incrementing `row_count`. The declared-vs-found check at the end (`expected_rows != row_count`) then ALSO fires, because the bad row isn't counted. Result: for a single defect the operator sees two separate QO4 FAILs — the column-count/quote error AND a bogus row-count mismatch that is purely a side-effect of the first error, not an independent defect.

Proposed fix: count a row toward `row_count` whenever it appears in the table body regardless of whether it parsed cleanly (so the declared-vs-found count reflects physical rows present), OR suppress the declared-vs-found check when any per-row error already fired. The first option keeps the checks orthogonal.

No test pins this — `test_fail_toon_quoted_field_ambiguous_path` and `test_fail_toon_row_count_mismatch` assert on `any(...)` so they cannot detect the double-FAIL drift.

### F2 (Medium) — Quoted-field detector fires on unambiguous quotes

Spec rationale (r7 F4, embedded in code comment at verify.py:353-354):
> "A path field containing a comma or quote is ambiguous under the last-comma-split rule and must not be silently truncated."

Description: the check is `if '"' in stripped:` — it flags ANY quote anywhere in the row, including a title field that contains a literal `"` but no comma (e.g. `  A"B, , , , a.json`). Such a row is NOT ambiguous under the last-comma-split rule (there is exactly one path field candidate, no embedded commas). Over-flagging is zero-tolerance-safe but inverts the spec intent of "ambiguous ⇒ flag".

Proposed fix: restrict the quoted-field check to rows that actually contain a quoted CSV cell (e.g. `re.search(r'"[^"]*,[^"]*"', stripped)`), or parse via `csv.reader` and flag only when more fields collapse than `len(columns)` predicts.

Test gap: `test_fail_toon_quoted_field_ambiguous_path` uses `"A, B"` (comma inside quotes — genuinely ambiguous), so it cannot expose the over-broad detector. Add a negative case: a title containing `"` without a comma must NOT trigger QO4.

### F3 (Medium) — Second `files[]` header swallows its rows silently

Spec §3-3 intent (zero-tolerance on structural drift):
> "いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。"

Description: when a second `files[...]{...}:` header is encountered, `_parse_toon_index` appends the error and `continue`s, but `header_seen` remains True and (critically) `in_table` is left False. All rows beneath the second header are therefore silently discarded — they are neither added to `paths` (so JSONs they would have covered are reported as "not registered") nor flagged individually. The operator sees ONE "second files[] header" FAIL plus N misleading "JSON not registered in index.toon" FAILs for files that WERE listed, just under the second header.

Proposed fix: after recording the second-header error, either (a) re-enter the table for the second block so `paths` is populated (and the second-header error alone remains the structural FAIL), or (b) explicitly consume and flag every subsequent non-blank row as "row under second files[] header". Option (a) minimises false-positive forward FAILs.

Test gap: `test_fail_toon_second_files_header` asserts only that the `"second files[] header"` message appears; it does not guard against the follow-on "not registered" false positives.

### F4 (Low) — Header regex is stricter than necessary on whitespace and trailing-comma shape

Spec wording for TOON header syntax is not quoted in `rbkc-verify-quality-design.md`; tests encode the de-facto format `files[N,]{...}:`.

Description: `_TOON_HEADER_RE = r'^files\[(\d+)(?:,[^]]*)?\]\{([^}]+)\}:\s*$'` accepts `files[N]{...}:`, `files[N,]{...}:`, `files[N,foo]{...}:`, but rejects `files[ N ]{...}:`, `files[N] {...}:`, or a CR byte before newline on Windows checkouts (handled by `splitlines`, OK). Not a bug given spec silence; flagged so the spec should pin the exact lexical grammar to prevent future drift.

Proposed fix: add the TOON header grammar (with examples of accepted/rejected forms) to `rbkc-verify-quality-design.md` §3-3, or tighten the regex deliberately and add a comment naming the format owner.

### F5 (Low) — Row indentation hard-coded to two spaces

Description: `raw.startswith("  ")` implicitly defines the TOON row indent as exactly 2 spaces. A 4-space or tab indent would be treated as "table terminated" and every row silently dropped (no error — just an empty `paths` result, surfaced downstream as "every JSON not registered"). Masking a structural drift as a forward-coverage FAIL violates the r7 distinct-message principle.

Proposed fix: detect "indented but not 2 spaces" as a QO4 FAIL (e.g. match `^(\s+)\S`, require `len(match.group(1)) == 2`, else flag).

### F6 (Low) — Path normalisation applied to index side only; JSON side uses a separate literal

Description: `_parse_toon_index` normalises `\` → `/` (verify.py:368), and `check_index_coverage` independently does the same for `rel` (verify.py:400). Correct today, but the two call sites are not named as a single helper — a future maintainer changing one may miss the other. Horizontal-check rule applies.

Proposed fix: extract `_normalise_path(p) -> str` and call from both sites, with a comment referring to r7 F5.

## Observations

- Distinct-message requirement (r7 F1/F2) is implemented correctly and covered by `test_fail_no_knowledge_json_listed_in_index_has_distinct_message` and `test_fail_broken_json_in_index_not_double_reported`. Both tests assert BOTH the positive message presence AND the absence of the misleading "missing JSON" variant — well-designed.
- Broken JSON tracking via `broken_jsons` set + reverse-loop skip (verify.py:436-439) cleanly prevents double-FAIL. Good.
- `test_fail_missing_index_lists_every_content_json_strict` correctly pins the per-file enumeration (spec §3-3 point 1) — protects against regression to "header-only FAIL".
- Path separator normalisation is covered by `test_pass_toon_backslash_path_normalised`.
- Schema check correctly short-circuits (`return paths, errors`) when the last column is not `path`, preventing downstream mis-interpretation.
- `no_knowledge_jsons` / `content_jsons` / `broken_jsons` as disjoint sets is a clean state model that makes the reverse-loop decision table straightforward.
- Empty-dir + missing-index case (`test_empty_knowledge_dir_without_index_passes`) is guarded — avoids a false positive when RBKC hasn't generated anything.

## Summary

Core r7 Findings (F1 distinct no_knowledge message, F2 no double-FAIL for broken+indexed, F5 path normalisation, F7 per-file enumeration) are implemented and tested correctly. Remaining gaps are in the structural parser's error-recovery behaviour (F1/F3 above) and detector precision (F2 above) — all Medium, none masking a spec requirement today but each capable of producing misleading FAIL cascades or false negatives on mildly adversarial TOON input.
