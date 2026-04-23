# QO4 Review — index.toon 網羅性

**Reviewer**: QA Engineer (independent, no prior review seen)
**Date**: 2026-04-23
**Scope**: `check_index_coverage` vs spec §3-3 QO4 (bidirectional compare)

## Overall Assessment

**Rating**: 4 / 5
**Summary**: All three spec-required FAIL conditions are implemented and covered by
tests. TOON parsing is adequate for the current index format but has a few silent-
skip paths that should be tightened to meet the zero-tolerance quality bar.

## Spec Conformance Matrix

| Spec §3-3 condition | Implemented | Tested | Reference |
|---|---|---|---|
| 1. index.toon missing → every content JSON listed FAIL | Yes | Yes | verify.py:179-187 / test_verify.py:266-278 |
| 2. JSON on disk not in index.toon → FAIL | Yes | Yes | verify.py:208-211 / test_verify.py:231-238 |
| 3. Index path with no JSON on disk (dangling) → FAIL | Yes | Yes | verify.py:213-216 / test_verify.py:280-291 |

Spec bidirectional requirement is satisfied.

## Key Issues

### High Priority

**[High] Broken / unreadable JSON is silently skipped**
- Description: `verify.py:170-173` catches any `Exception` on
  `json.loads(jf.read_text(...))` and continues. A file that is present on disk
  but unparseable is dropped from `content_jsons`. Downstream effect: if such a
  file happens to also be listed in index.toon, that index row still passes
  (the path is present in `content_jsons`? — no, it is not, so it would be
  reported as dangling). However, if it is *not* listed in the index, verify
  reports nothing at all, even though the file clearly exists and would be
  user-visible corruption.
- This conflicts with the project quality standard ("if there is even a 1% risk,
  eliminate it"). A corrupt content JSON is a worse defect than a registration
  gap and must not be hidden by QO4 (or another check must claim it).
- Suggested fix: either (a) emit `[QO4] <rel>: JSON parse error: <msg>` on
  exception, or (b) add a QO0 / structural precheck that enumerates unparseable
  JSON files before QO4 runs. Do not weaken QO4 to accept them silently.
- Note: `test_broken_json_silently_skipped` (test_verify.py:307-317) explicitly
  pins the current permissive behaviour — this is a bias-avoidance concern:
  the test locks in behaviour that the spec (§3-3, §"zero-tolerance") does not
  sanction. Treat the test as documenting a known gap, not as evidence of
  correctness.

**[High] Malformed index.toon header is silently ignored**
- Description: `verify.py:192-206` requires a line starting with `files[` and
  ending `:` to enter table mode. If the header is malformed (e.g. typo,
  missing colon, truncated file, BOM before `files[`), `in_table` stays
  `False`, `indexed_paths` stays empty, and QO4 then reports every content
  JSON as "not registered" — which at least fails loudly. But if the header
  is correct and the table body is truncated or reordered, no structural
  complaint is raised.
- More concerning: rows that do not begin with two spaces (`line.startswith("  ")`)
  are skipped (verify.py:201). A malformed row — e.g. tab-indented, single-space
  indented, or indented more than expected — is silently dropped. The file may
  look populated but contribute zero indexed paths for those rows.
- Suggested fix: after parsing, if the header declared `files[N,]` and fewer
  than N rows were absorbed, emit `[QO4] index.toon declared N rows but
  parsed M`. This is a cheap sanity check derivable from the header alone.

### Medium Priority

**[Medium] Path-column extraction assumes path never contains commas**
- Description: `verify.py:203-206` uses `stripped.rfind(",")` to extract the
  last comma-separated field as the path. TOON format as used in v6 appears
  to have no quoting; a path containing `,` (uncommon but valid on POSIX)
  would be mis-parsed — the portion after the final comma is treated as the
  path. No test exercises this.
- Suggested fix: add a test `test_path_with_comma_handled_or_rejected` — and
  depending on whether TOON permits commas in paths, either support quoting or
  explicitly FAIL. Since the Nablarch corpus does not use such filenames, a
  detection test is sufficient; implementation can defer.

**[Medium] `test_broken_json_silently_skipped` is a circular test**
- Description: test_verify.py:307-317 asserts that a broken JSON yields `[]`
  issues. The spec does not state this behaviour — it was derived from the
  implementation's `except Exception: continue`. The docstring says "pin that
  behaviour here so a future strict-parse policy is a conscious spec change".
  Under bias-avoidance rules, this is a circular test: implementation dictates
  spec.
- Suggested fix: remove the test or invert its assertion after the High-priority
  fix above lands. At minimum, file a TODO referencing the spec gap.

**[Medium] Empty index table (header present, zero rows) not distinguished**
- Description: When the header is `files[0,]{...}:` and there are content JSONs
  on disk, QO4 correctly reports every JSON as "JSON not registered in
  index.toon: …" — good. But the user-facing message does not distinguish
  "index.toon exists but is empty" from "index.toon missing". The spec §3-3
  treats these as the same failure class, so this is acceptable, but a log
  hint helps diagnosis.
- Suggested fix: low-cost enhancement — include the declared row count from
  `files[N,]` in the first FAIL line.

### Low Priority

**[Low] `no_knowledge_content` key is assumed truthy/falsy with no schema check**
- Description: verify.py:174 uses `d.get("no_knowledge_content")`. A JSON file
  where the key is present but set to a string `"false"` would be treated as
  truthy and excluded from QO4. This matches Python truthiness, not JSON
  semantics.
- Suggested fix: compare with `is True` if the schema says the field is a
  boolean; otherwise note it in the design doc.

## Unit Test Coverage Review

| Case | Covered | Location |
|---|---|---|
| All indexed PASS | Yes | test_verify.py:223-229 |
| JSON not in index FAIL | Yes | test_verify.py:231-238 |
| `no_knowledge_content` excluded | Yes | test_verify.py:240-246 |
| Nested path indexed | Yes | test_verify.py:248-255 |
| Missing index file FAIL | Yes | test_verify.py:257-262 |
| Missing index enumerates every JSON | Yes | test_verify.py:266-278 |
| Dangling index entry FAIL | Yes | test_verify.py:280-291 |
| Empty dir + missing index = PASS | Yes | test_verify.py:293-297 |
| CJK filename | Yes | test_verify.py:299-305 |
| Broken JSON | Pinned (circular) | test_verify.py:307-317 — see High/Medium above |
| Malformed index header | **Missing** | — |
| Row count mismatch vs `files[N,]` | **Missing** | — |
| Path containing comma | **Missing** | — |
| Empty table body with header present | **Missing** | — |

### Circular Test Flag

`test_broken_json_silently_skipped` pins implementation behaviour rather than
spec behaviour. Flagged.

## Runtime Verification (v6)

- Unit tests: `pytest tools/rbkc/tests/ut/test_verify.py::TestCheckIndexCoverage`
  → **10 passed** (0.02s)
- Actual v6 run: `check_index_coverage` against
  `.claude/skills/nabledge-6/knowledge/` and its `index.toon` (341 entries
  declared in header) → **0 issues**. Bidirectional compare clean on live data.

## Positive Aspects

- Bidirectional compare (forward + reverse) matches spec §3-3 exactly.
- "index.toon missing" handler correctly enumerates every content JSON, not a
  single summary line — this is the expected fail-loud behaviour.
- TOON parser uses `rfind(",")` which is robust to commas in the title field
  (verified by `test_pass_nested_path_indexed`).
- CJK filename test exists — good defensive coverage.
- Tests use a real TOON writer (`_write_toon`), not hand-crafted strings, so
  the happy-path tests exercise the parser on format-accurate input.

## Recommendations

1. **Fix the broken-JSON silent skip** (High). Either surface the parse error as
   a QO4 issue or add a structural precheck. Then delete or invert
   `test_broken_json_silently_skipped`.
2. **Add row-count sanity check** using `files[N,]` header (High-Medium). Cheap
   and catches truncated / malformed index.toon.
3. **Add the three missing tests** (Medium): malformed header, row count
   mismatch, path containing comma.
4. Keep the current CJK test; consider adding a path-with-spaces test for
   symmetry with filesystem-edge-case coverage.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 151-218) — source
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 201-317) — tests
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 — spec
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/knowledge/index.toon` — v6 runtime
