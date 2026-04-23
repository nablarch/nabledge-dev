# QO3 Review (Z-1 r8, bias-avoidance)

Scope: `check_docs_coverage` in `tools/rbkc/scripts/verify/verify.py` against
`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (QO3), plus
`TestCheckDocsCoverage` in `tools/rbkc/tests/ut/test_verify.py`.

Focus: r7 findings — MD→JSON direction and README-missing short-circuit removal.

---

## Findings

None.

### r7 F1/F2 — MD→JSON direction (resolved)

Spec §3-3 table row for QO3 states the verification direction as
"JSON↔MD 1:1 存在確認" (testing matrix row, line 334):

> | QO3 | `TestCheckDocsCoverage` (JSON↔MD 1:1 存在確認 + README ページ数) |

Implementation now walks `ddir.rglob("*.md")` (verify.py:265) excluding
`README.md` (verify.py:266) and reports `[QO3] dangling docs MD without
matching JSON: <rel>` (verify.py:270-272). Set membership against
`json_rel_paths` (built at verify.py:252-255 with `.with_suffix(".md")`)
is exact path-equality, satisfying the 1:1 requirement symmetrically
with the JSON→MD direction.

Test `test_fail_dangling_docs_md_without_matching_json` (test_verify.py:715-729)
asserts both substrings "QO3", "dangling", and the orphan filename —
this is a content-checked assertion, not a mere "non-empty issues" check.

### r7 — README-missing short-circuit (resolved for QO3 FAIL enumeration)

Spec §3-3 (lines 281-287) treats README existence, page-count declaration
presence, and count coherence as three distinct sub-checks. ゼロトレランス
(§2-1) + the "review findings — default is fix" rule (rbkc.md) require
that all applicable failures surface in one pass.

Implementation:
- JSON→MD check (verify.py:251-260) runs unconditionally.
- MD→JSON dangling check (verify.py:262-272) runs unconditionally.
- README-missing `return issues` (verify.py:274-275) now guards **only**
  the page-count coherence block (verify.py:277-288), which is correct —
  without a README file, `readme.read_text()` would raise and the declared
  count check is not well-defined.

This is the minimum-necessary short-circuit: the two 1:1 existence
checks (the core QO3 behaviour) both run regardless of README presence,
matching spec §3-3 intent.

---

## Observations

1. **README-missing + content: sub-checks not run.** When README is
   absent, the "declaration present" and "count matches" sub-checks
   (spec §3-3 lines 285-287) are skipped by design because there is no
   file to parse. The single `[QO3] README.md missing` issue signals
   the root cause; the user fixes README, reruns verify, and the
   page-count check then applies. This matches the spec's implicit
   ordering (existence precedes parsing) and does not hide failures —
   the parent file itself is already reported as FAIL.

2. **Test coverage of the r7 fix.** `TestCheckDocsCoverage` covers:
   - forward direction (test_fail_json_without_matching_docs_md),
   - reverse direction (test_fail_dangling_docs_md_without_matching_json),
   - wrong-location variant (test_fail_docs_md_at_wrong_nested_path),
   - non-ASCII path (test_pass_cjk_filename),
   - empty-knowledge edge case (test_pass_empty_knowledge_dir),
   - README missing (test_fail_readme_missing),
   - README count mismatch (test_fail_readme_page_count_mismatch).

   Dangling assertion pins three substrings ("QO3", "dangling",
   "orphan") — independent of implementation wording changes to the
   surrounding message, so not a circular test.

3. **Symmetry with QO4.** QO4 (spec §3-3 lines 299-304) uses the same
   bidirectional model ("dangling entry" for the reverse direction).
   QO3 now mirrors this, and the commit/fix note in verify.py:262-264
   cites both the spec and the symmetry explicitly.

4. **README.md exclusion from dangling walk** (verify.py:266) uses
   `md_path.name == "README.md"` rather than path equality with
   `readme`. This correctly excludes README at docs root; it would also
   exclude a nested `README.md` if RBKC ever emitted one at
   `docs/subdir/README.md`. Since RBKC only emits `docs/README.md` per
   spec, the name-based filter is not risky today. Not a finding, but
   worth noting if docs structure ever evolves.

5. **Sorted iteration** (`sorted(ddir.rglob("*.md"))` at verify.py:265)
   gives deterministic issue ordering across platforms — good for
   snapshot/golden tests and for diff-friendly CI output.

---

## Verdict

No findings. r7 F1/F2 are fully addressed: bidirectional 1:1 existence
is implemented, tested with content-checked assertions, and the
README-missing short-circuit is correctly scoped to only the page-count
coherence block it must guard.
