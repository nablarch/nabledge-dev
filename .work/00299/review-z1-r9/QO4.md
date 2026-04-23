# QO4 Bias-Avoidance Review (Z-1 r9)

Target: `check_index_coverage` + `_parse_toon_index` in
`tools/rbkc/scripts/verify/verify.py` vs spec §3-3 (QO4),
tests in `tools/rbkc/tests/ut/test_verify.py :: TestCheckIndexCoverage`.

## Findings

### F1 — Quoted-field detector over-flags rows with a literal quote that is not ambiguous

Spec §3-3:

> "いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。"

(Zero-tolerance applies to TOON parse drift only when the drift can cause
a silent mis-parse — not to every stray byte.)

Description: the detector at verify.py:381 is `if '"' in stripped:`. It
fires on ANY double-quote anywhere in the row. Under the last-comma-split
rule the row is ambiguous only when a quoted cell contains an embedded
comma (e.g. `"A, B"`). A row like `  A"B, , , , a.json` has exactly one
path candidate after the last comma and is not ambiguous, yet it is
reported as "quoted field (ambiguous path parse)" AND the path is then
dropped from `paths`, which causes the JSON to be reported downstream
as "not registered in index.toon". One benign literal quote in a title
produces two FAILs whose cause is invisible to the operator.

Proposed fix: restrict the detector to rows where a quote actually makes
the split ambiguous — e.g. detect a quoted cell containing a comma
(`re.search(r'"[^"]*,[^"]*"', stripped)`) or parse via `csv.reader` and
flag only when field count deviates from `len(columns)` due to quoting.
Add a negative test: a title containing `"` without an embedded comma
must not trigger QO4.

Test pinning gap: `test_fail_toon_quoted_field_ambiguous_path` uses
`"A, B"` (genuinely ambiguous) and asserts only `any("quoted" in i)`, so
it cannot expose the over-broad detector.

### F2 — Schema check short-circuits and skips every subsequent structural error

Spec §3-3:

> "いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。"

> "4. **JSON parse 失敗**: … (silent skip 禁止。ゼロトレランスに基づき、壊れたファイルは検出対象とする)"

Description: when the header's last column is not `path`, the parser
returns immediately (`return paths, errors` at verify.py:370). Any
structural drift that appears later in the same file — a second
`files[]` header, a malformed row, a dangling-entry scenario —
is silently suppressed. The operator fixes the schema, reruns verify,
and discovers a second structural error that was present all along.
This is the exact silent-skip pattern the spec clause above forbids.

Proposed fix: accumulate the schema error, mark the parser as "path
column unknown", and continue scanning so every subsequent structural
error is still enumerated. Rows cannot be mapped to paths under a
broken schema, so treat every row as a structural error ("row under
broken schema"); do not emit the "JSON not registered" messages that
would cascade if `paths` were simply empty.

Test pinning gap: `test_fail_toon_header_schema_without_path_last_column`
asserts only `any("schema" in i)`. It does not probe whether errors
below the header are still surfaced.

### F3 — Row indentation pinned to exactly two spaces; a four-space or tab indent terminates the table silently

Spec §3-3 does not pin TOON row indentation. The zero-tolerance clause
in `rbkc.md` (Decide from the spec) applies:

> "Silent skip candidates: every `continue` / `if X: return []` / early-return in the affected module"

Description: `_parse_toon_index` ends the table on any non-empty line
that does not start with two spaces (`raw.startswith("  ")` at
verify.py:335). A TOON file indented with four spaces or a tab is
treated as "table terminated after the header", `paths` is empty, and
every content JSON is reported downstream as "not registered". The
structural drift (unsupported indent) is masked as a forward-coverage
FAIL cascade — operator has no signal that the real cause is indentation.
This is the same failure pattern r7 F1/F2 fixed for no_knowledge and
broken JSON (distinct-message principle) but has regressed for indent.

Proposed fix: when the post-header line begins with whitespace but not
exactly two spaces, emit a distinct "row indentation unexpected (expected
2 spaces)" QO4 error and either stop or continue under a documented
indent-tolerance rule. Do not fall through silently to
`in_table = False`.

Test pinning gap: no test exercises any indent other than 2 spaces.

### F4 — `splitlines()` + dependence on physical newlines loses the last row when the file has no trailing newline

Spec §3-3:

> "いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。"

Description: `text.splitlines()` handles no-trailing-newline correctly
— the final line is returned whether or not it ends with `\n`. However,
the row-count check `expected_rows != row_count` depends on the final
row being recognised as a row. If the final line is `  A, , , , a.json`
(no trailing newline) the code path is fine; but combined with F3 above,
a file written with CRLF line endings passes `splitlines()` (which
strips `\r`) yet any TOON writer that emits a trailing `\r` on a row
line would leave the content unchanged — not actually a bug. Verified
by reading the code. No finding.

(Retained as an observation so the reader knows this was checked.)

### F5 — `_parse_toon_index` silently accepts rows whose path field is empty

Spec §3-3:

> "3. **dangling entry**: index.toon に列挙されている相対パスに対応する JSON が存在しなければ FAIL"

Description: a row `  A, , , , ` passes the column-count check
(`len(fields) == len(columns)`), `fields[-1].strip()` becomes `""`, and
`""` is appended to `paths`. Downstream, `"" not in content_jsons` and
`"" not in broken_jsons` and `"" not in no_knowledge_jsons`, so the
reverse loop emits `[QO4] index.toon lists missing JSON: ` — an error
message with an empty path. The operator cannot locate the offending
row without re-reading the file. The spec's bidirectional-integrity
clause is satisfied in the sense that a FAIL fires, but the message
does not identify the defect clearly; under zero tolerance a row with
an empty path is a structural defect (not a dangling-entry defect) and
should be reported as such.

Proposed fix: after `path = fields[-1].strip()`, if `path == ""`, emit a
distinct `[QO4] index.toon row has empty path field at line {line_no}`
error and do NOT append `""` to `paths`.

Test pinning gap: no test covers an empty path cell.

### F6 — Second-header recovery reuses the first header's column schema without checking the second header's declared schema

Spec §3-3 (zero-tolerance, distinct messages):

> "いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。"

Description: verify.py:348-362 handles a second `files[]` header by
appending the structural error and re-entering the table with the
existing `columns` list ("Reuse the existing column schema — a second
block with a different schema would have been flagged above by the
schema check on the first header"). The in-code comment is incorrect:
the schema check on verify.py:366-370 runs only when `header_seen` is
False (on the first header). The second header's `{columns}` block is
never validated. If the second header declares e.g. `{path, title}`
(path first, not last), the rows under it are parsed with the first
block's column layout, producing silently wrong paths that then
cascade as "missing JSON" / "not registered" false positives. The
structural defect is masked by the first-header schema.

Proposed fix: on the second header, parse its `{columns}` and, if it
differs from the first block's `columns`, emit a second structural
error ("second files[] header schema differs from first") and stop
parsing rows under the second block. Do NOT silently reuse the first
schema.

Test pinning gap: `test_fail_toon_second_files_header` and
`test_fail_toon_second_header_does_not_silently_drop_rows` both use
the SAME schema in both headers, so neither can catch schema drift
between the two headers.

### F7 — `had_structural_error` suppresses row-count check after ANY per-row error, including recoverable ones

Spec §3-3 (from the row-count mismatch test's own spec rationale):

> "files[N,] must match actual rows"

Description: the `had_structural_error` gate at verify.py:400-409
suppresses the declared-vs-found row-count mismatch whenever any row
fired a column-count, quoted-field, or second-header error. The r8 fix
(F1) intentionally did this to avoid double-FAIL on a single defect.
However, the gate is too broad: if a file has BOTH a genuinely wrong
declared row count (e.g. `files[10,]` but only 3 physical rows) AND an
unrelated per-row error in one of those 3 rows, the count mismatch is
silently suppressed. The operator fixes the per-row error, reruns, and
then discovers the count mismatch — the two defects are orthogonal but
cannot be reported together.

Proposed fix: narrow the suppression. If `row_count > 0` and exactly
one row fired a structural error, suppress the count mismatch (that is
the r8 scenario). If `row_count` is still off by more than one, or if
the structural errors were second-header / quoted-field (which don't
change the physical row count seen), report the count mismatch
independently. Alternatively: always report both and let the operator
triage — zero-tolerance prefers over-reporting structural drift to
under-reporting.

Test pinning gap: `test_fail_toon_column_count_mismatch_no_spurious_row_count_double_fail`
asserts `rc == []` for the single-defect case, which pins the current
broad suppression; it does not pin the multi-defect case that needs
the narrower rule.

## Observations

- r7/r8 findings (F1 no_knowledge distinct message, F2 broken+indexed
  no double-FAIL, F5 path normalisation, F7 per-file enumeration, r8 F1
  row-count suppression after column-count error, r8 F3 row re-parse
  after second header) are all implemented and pinned by the intended
  tests. The strict-enumeration test
  (`test_fail_missing_index_lists_every_content_json_strict`) uses
  `len(per_file) >= 2` which is the correct anti-regression shape.
- `broken_jsons` / `no_knowledge_jsons` / `content_jsons` disjoint-set
  model makes the reverse-loop decision table exhaustive by
  construction — no fourth unhandled state exists.
- Header regex `^files\[(\d+)(?:,[^]]*)?\]\{([^}]+)\}:\s*$` tolerates
  the observed forms (`files[N]`, `files[N,]`, `files[N,foo]`) and
  rejects whitespace variants. Rejection is fine; the spec does not
  define additional whitespace forms. This is an area where the spec
  is silent rather than a defect.
- Path normalisation (`\\` → `/`) is duplicated between
  `_parse_toon_index` and `check_index_coverage` (r8 F6 observation).
  Still correct today; still not extracted to a helper. Non-blocking.
- TOON grammar is not defined in the spec. All parser behaviour is
  effectively defined by the tests. Findings F3 and F6 above are
  direct consequences of that spec silence combined with ambiguous
  parser recovery choices — fixing the parser is cheaper than
  changing the spec.
- `test_cjk_filename_indexed` pins CJK-in-path behaviour. Good.
- `test_pass_toon_backslash_path_normalised` pins the r7 F5 fix.
- No test covers: empty path cell (F5), 4-space/tab indent (F3),
  literal-quote-without-comma in title (F1), schema drift between
  first and second header (F6), count mismatch coexisting with a
  per-row error (F7). Each of these is a spec-derivable scenario
  that the current tests cannot catch.

## Summary

Core r7/r8 fixes are implemented and pinned. Remaining gaps are all in
the structural parser's error-recovery behaviour (F2 short-circuit, F3
indent silent-terminate, F5 empty-path silent-accept, F6 second-header
schema-reuse, F7 over-broad suppression) plus one detector-precision
issue (F1 over-broad quote check). Each produces either a silent skip
that the spec's zero-tolerance clause forbids, or a FAIL-cascade that
masks the real defect under distinct-message-principle violations.
