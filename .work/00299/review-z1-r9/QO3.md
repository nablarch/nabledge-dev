# QO3 Review (Z-1 r9, bias-avoidance)

Scope: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` against
`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (QO3), plus
`TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`.

Reviewer posture: independent, bias-avoidance. No priority / rating
labels per rule.

---

## Findings

### F1 — README page-count regex admits false-positive declarations

Spec §3-3 (line 286) states the required form exactly:

> README.md に `N ページ\n` 形式の行が存在すること (宣言が無い場合は FAIL)

The regex in verify.py:239 is:

```
_README_COUNT_RE = re.compile(r'^(\d+)\s*ページ', re.MULTILINE)
```

Under `re.MULTILINE` with no right-side anchor, this accepts inputs the
spec clause does not sanction as "N ページ\n 形式の行":

- `42 ページ以上あります` → matches, captures 42 (the spec form is a
  standalone declaration, not a prose fragment starting with a number).
- A Markdown list item `- 1. 構成` with `^1` at line start would not
  match (needs `ページ`), so that variant is safe; however any later
  line such as `12 ページ目の図` in prose would be accepted as a page
  count declaration.

Consequence under ゼロトレランス: a README that omits the declared
page-count line but contains any `\d+\s*ページ…` prose passes the
"declaration present" sub-check and proceeds to the count-mismatch
arithmetic against unrelated prose. That is a silent weakening of the
spec clause, which explicitly names the form `N ページ\n`.

The spec form requires the line to end at `ページ` (followed by newline).
The correct regex anchors the right side, e.g. `^(\d+)\s*ページ\s*$`
with `re.MULTILINE`.

### F2 — `rglob("*.json")` does not exclude non-knowledge JSON

`check_docs_coverage` at verify.py:263 walks `kdir.rglob("*.json")` and
requires a corresponding `.md` in `docs_dir` for every hit. Spec §3-3
(line 289) scopes QO3 to "JSON (knowledge)" ↔ "docs MD". There is no
clause sanctioning inclusion of auxiliary JSON artefacts that may land
under `knowledge_dir` (e.g. cache, sidecar, tool output) as QO3 targets.

If any non-knowledge `.json` file is written under `knowledge_dir` (now
or later), QO3 will emit a spurious `docs MD missing` and also inflate
the count used when comparing against README's declared page count in
`docs.py:116` — note `_generate_readme` counts `entries`, not
`rglob("*.json")`. The two sides of the QO3 check therefore use
different denominators, so a non-knowledge JSON produces both the QO3
"missing docs MD" false positive *and* a false README count mismatch.

Spec §3-3 does not enumerate an allow-list or exclusion rule, so the
safe reading under ゼロトレランス is: QO3 scope = JSON files that are
knowledge artefacts (i.e. the same set docs.py emits from). An explicit
scope contract (e.g. match only files `docs.py` would emit a page for,
or exclude a documented set of sidecar paths) is required to avoid
silent drift.

### F3 — README dangling walk uses name-based exclusion instead of path equality

verify.py:275-277:

```
for md_path in sorted(ddir.rglob("*.md")):
    if md_path.name == "README.md":
        continue
```

Spec §3-3 lines 283-287 define README as `docs_dir/README.md` (single
file at docs root). The implementation excludes every `README.md` at
any depth, not only the root one. If RBKC ever emits a nested
`docs/subdir/README.md` (or a user places one), that file escapes the
dangling check even though no JSON backs it — a silent hole in the
bidirectional 1:1 guarantee.

The spec-aligned exclusion is path equality with `ddir / "README.md"`,
not a basename compare.

### F4 — README page-count denominator uses the same permissive walk

verify.py:288:

```
actual = len([p for p in ddir.rglob("*.md") if p.name != "README.md"])
```

Same basename filter as F3. A `docs/sub/README.md` would be counted as
a content page in `actual`, disagreeing with docs.py's `len(entries)`
producer (which is the spec's referent). The count-mismatch FAIL is
therefore derivable from an unrelated README file rather than from an
actual page-count divergence.

### F5 — Test suite does not exercise the regex boundary or JSON-scope assumptions

`TestCheckDocsCoverage` (test_verify.py:730-833) covers the happy
1:1 path, JSON→MD miss, MD→JSON dangling, wrong-nested-path, CJK,
empty, README missing, README count mismatch. It does not include:

- A README whose only `ページ` occurrence is inside prose (e.g.
  `"12 ページ目の…"`) with no standalone `N ページ` declaration —
  would currently PASS silently (F1).
- A non-knowledge JSON under `knowledge_dir` (F2) to confirm scope.
- A nested `README.md` under `docs_dir` (F3/F4) to confirm the
  dangling check still triggers and the count denominator is correct.

Per rbkc.md "Test writing: required coverage" ("bug-revealing cases … if
a bug can occur, write a test that catches it"), the absence of these
cases means the spec clauses above are not under test.

---

## Observations

1. The r8 fixes for bidirectional 1:1 (MD→JSON dangling) and the
   scoped README short-circuit both survive r9 review — the structural
   direction is correct; F1–F5 are refinements within that structure,
   not a reversion.

2. `test_fail_readme_page_count_mismatch` (test_verify.py:825-833)
   uses `"99ページ\n"` (no space) as input. The current regex accepts
   this because `\s*` allows zero whitespace. Spec wording `N ページ`
   shows a space, but the design text does not explicitly mandate it;
   treating zero-or-one space as equivalent is a defensible
   interpretation. This is an observation, not a finding, because the
   spec is ambiguous on whitespace strictness whereas it is explicit
   on the "line 形式" ending (F1).

3. Deterministic ordering via `sorted(...)` on both walks
   (verify.py:263, 275) is good for diff-stable CI output — unchanged
   from r8.

4. Error messages include relative paths and the triggering JSON
   filename — useful for fix-side triage and independent of
   implementation internals (not circular).

---

## Summary

Five findings, all traceable to explicit spec §3-3 clauses (`N ページ\n`
line form, QO3 scope as knowledge JSON ↔ docs MD, README at
`docs_dir/README.md`). The regex and walk filters in
`check_docs_coverage` are slightly more permissive than the spec, and
the test suite does not close those gaps.
