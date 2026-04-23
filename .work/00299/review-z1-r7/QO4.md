# QA Review — QO4 (index.toon 網羅性)

**Scope**: `check_index_coverage` in `tools/rbkc/scripts/verify/verify.py`
against `rbkc-verify-quality-design.md` §3-3 QO4 and
`tests/ut/test_verify.py::TestCheckIndexCoverage`.

Review style: binary (ゼロトレランス). Findings block; observations for
spec-permitted behaviour.

---

## Findings

### F1. `no_knowledge_content` JSON listed in index.toon is mis-reported as "dangling"

Spec §3-3 bullet 3 — dangling entry definition:

> index.toon に列挙されている相対パスに対応する JSON が存在しなければ FAIL
> (検索でヒットした後にファイルが見つからず 404 になる状態を防ぐ)

The spec's "dangling" condition is "JSON does not exist on disk". The
current implementation compares the index path against `content_jsons`,
which excludes `no_knowledge_content: true` files. If a TOC JSON (file
exists, but `no_knowledge_content: true`) is erroneously listed in
index.toon, verify emits:

    [QO4] index.toon lists missing JSON: <path>

but the file is **not** missing — the defect is "index.toon lists a
non-content JSON". Message misattributes the failure mode; operator will
waste time looking for a file that is in fact on disk. Spec §3-3 implies
two distinct fault classes ("未登録 JSON" and "dangling entry");
listing a no-knowledge JSON is a third class that is silently folded
into "dangling".

- Fix: track content JSON paths and `no_knowledge_content` paths
  separately; when an index entry matches a no-knowledge JSON, emit a
  distinct FAIL (e.g. "index.toon lists no_knowledge JSON: …").
- Horizontal check required: every other place where `dict.get("no_knowledge_content")`
  is used to skip items silently.

### F2. Broken JSON listed in index.toon produces double FAIL with misleading second message

Spec §3-3 bullet 4 requires parse failure to be reported as QO4 FAIL
(no silent skip). Current code:

1. emits `[QO4] broken.json: JSON parse failed: …`, and
2. removes `broken.json` from `content_jsons`, so if index.toon lists
   `broken.json`, the reverse loop emits `[QO4] index.toon lists
   missing JSON: broken.json`.

The second message is factually wrong — the file exists, it is just
unparseable. No test (`test_fail_broken_json_surfaces_qo4` does not
place the broken JSON in the index) covers this case, so the double
report ships silently.

- Fix: add the broken-JSON path to a "known on disk" set so the reverse
  check does not false-flag it as missing.
- Add unit test: broken JSON present **and** listed in index.toon →
  expect exactly one FAIL (the parse-failure line), not "lists missing
  JSON".

### F3. TOON parser accepts ANY `files[…]:` header — no termination, no schema check

Spec §3-3 says the check must be "index.toon の内容と JSON ファイル群が完全に一致する". The parser currently:

- enters the table state on the first `files[…]:` line, and **never
  leaves it** — any subsequent indented line anywhere in the file (even
  after a blank line or after a non-table section is started) is parsed
  as a row and its last comma-separated token is taken as a path;
- does not validate that the header's column schema ends in `path` —
  any schema whose last column is not the path would cause every row's
  last field to be mis-read as a path, and every content JSON would be
  reported as "not registered" (a silent false-positive class).

Both are fragile: a future TOON writer change (different column order,
a second `files[...]:` table, or trailing sections with indented
content) would corrupt the parse without any diagnostic. Spec's
zero-tolerance posture (§2-1) requires that "close enough" parsers be
replaced with ones that fail loudly on unexpected shape.

- Fix options:
  - Validate header column list ends with `path`; FAIL with a clear
    "[QO4] index.toon header schema unexpected: …" when it does not.
  - Terminate table parsing on the first line that is neither indented
    nor blank after the header, or enforce `files[N,]` row count and
    FAIL on mismatch.
- Unit tests required:
  - header whose last column is `title` (not `path`) — expect explicit
    FAIL, not silent mass "not registered".
  - indented text after the table — expect parser to stop, not ingest
    it as rows.
  - row count mismatch against the `N` in `files[N,…]` — expect FAIL.

### F4. Path-field comma handling assumes the path never contains commas and is never quoted

The parser takes `stripped[last_comma+1:]` as the path. If a future
index.toon ever quotes fields containing commas (`"a,b", "x,y", path`)
or if a path itself contains a comma, `rfind(",")` returns the last
comma regardless of quoting — the "path" returned is a suffix of the
real path, or a tail of a quoted field. The test suite uses paths like
`sub/b.json` and `sub/日本語.json` only; no test exercises a quoted
field or a comma inside a field.

ゼロトレランス requires behaviour to be derivable from the format spec,
not from "what the writer currently emits". Either TOON is defined to
forbid commas/quoting in `path`, in which case verify must FAIL on
encountering them (not silently truncate), or it must honour quoting.

- Fix: either document+enforce "path field is bare, no commas, no
  quotes" with an explicit FAIL on detection, or use a TOON-aware
  parser.
- Unit tests required: row with a quoted field containing a comma; row
  whose path field starts/ends with a quote.

### F5. OS path separator normalisation is one-sided

`content_jsons` keys are normalised to forward slash:
`rel = str(jf.relative_to(kdir)).replace("\\", "/")`.
`indexed_paths` are stored as-is from index.toon. If any index.toon
writer (now or in future, on Windows) emits backslash paths, the
forward/reverse set comparison will diverge silently — every content
JSON becomes "not registered" and every index entry becomes "missing
JSON". Spec §3-3 does not sanction this silent mass-FAIL shape; the
spec defines the check as a bidirectional equality, and the equality
must be against a canonical path form.

- Fix: apply `.replace("\\", "/")` to `indexed_paths` entries as well
  (or normalise both via `PurePosixPath`).
- Unit test: index row with a backslash separator must either PASS
  against the equivalent forward-slash JSON on disk or FAIL with an
  explicit "non-canonical path separator" message — not the current
  silent double-error.

### F6. `in_table` flag can re-enter silently on a second `files[…]:` header

If index.toon ever contains two `files[…]:` blocks (e.g. a future
split by category), the parser treats the second header line as a
non-indented line, stays `in_table = True`, and then its rows are
parsed mixed with the first table. No error is raised. This is the
same class as F3 (parser does not fail on unexpected structure).

- Fix: FAIL explicitly on a second header, or reset/accumulate per
  header.

### F7. Test `test_fail_missing_index_file` is circular — does not pin the spec's listing requirement

The test asserts only `any("QO4" in i for i in issues)`. Spec §3-3
point 1 requires that **every** content JSON be listed as FAIL when
index.toon is absent. A regression that reports only the header
("index.toon missing") and drops the per-file enumeration would still
pass this test. `test_fail_missing_index_lists_every_content_json`
covers this case separately, but the older test should be tightened or
removed to avoid masking future regressions.

- Fix: in `test_fail_missing_index_file`, also assert the per-file
  FAIL line is present; or delete the redundant test in favour of the
  Z-1-gap-fill version which already asserts enumeration.

---

## Observations (spec-permitted)

- Using `rfind(",")` to isolate the path is sound **for the current
  TOON writer** (path is the last column, unquoted). Covered by F4 as
  a robustness concern, not a present defect.
- Excluding `no_knowledge_content: true` JSONs from the forward check
  matches spec §3-3 bullet 2 ("`no_knowledge_content: true` でない JSON …").
- Reporting index.toon absence as a single header line plus per-file
  FAIL lines satisfies spec §3-3 point 1 ("全 JSON を QO4 FAIL として
  列挙する") — covered by `test_fail_missing_index_lists_every_content_json`.
- Broken-JSON FAIL surfaces per spec §3-3 point 4 (no silent skip),
  covered by `test_fail_broken_json_surfaces_qo4`. The combined case
  with index listing is the gap (F2).
- Empty knowledge dir + missing index returning `[]` is consistent
  with spec (no content JSON ⇒ no search coverage required).

---

## Summary

7 findings. All are blocking under ゼロトレランス:

- F1, F2: misleading / double FAIL messages (operator impact).
- F3, F4, F5, F6: TOON parser assumes current writer behaviour;
  silently mass-FAILs or mis-parses on any shape drift.
- F7: circular / weak test that would not catch a real regression.

Fix scope: adjust `check_index_coverage` to (a) distinguish
"no_knowledge JSON listed", "broken JSON listed", and "truly dangling
JSON" reverse cases, (b) make the TOON parser fail loudly on
unexpected header/shape/path, (c) normalise path separators on both
sides. Tighten or remove the weak test in QO4's unit suite and add
the missing cases listed under each finding.
