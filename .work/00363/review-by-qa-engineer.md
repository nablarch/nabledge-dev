# Expert Review: QA Engineer

**Date**: 2026-06-04
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: test_javadoc.py, test_javadoc_fqcn.py, test_verify.py, test_rst_ast_visitor.py, test_run.py + implementation files

## Summary

3 Findings — not shippable

## Findings

### Finding 1: Q5 quadrant (FQCN absent entirely from JSON) has no unit test

- **Violated clause**: `.claude/rules/rbkc.md` § "All logic must have unit tests. Every new check added to verify requires a corresponding test before implementation (TDD)." Also `.claude/rules/development.md` § "Bug-revealing cases: Input that exercises each specific failure mode."
- **Description**: `TestCheckSourceLinks_JsonSide_Extdoc` docstring explicitly declares "Q5: FQCN absent from JSON content entirely → FAIL (QL1)" as a required quadrant. The spec distinguishes Q2 (display text present, link absent) from Q5 (neither display text nor MD link in JSON — complete data loss). No test exercises `content=""`. The existing `test_fail_q2_display_text_only` uses `content="UniversalDao"` (display text present) — Q2, not Q5.
- **Fix**: Add to `TestCheckSourceLinks_JsonSide_Extdoc`:
  ```python
  def test_fail_q5_fqcn_absent_entirely(self, tmp_path):
      """Q5: javadoc JSON exists but FQCN absent from JSON entirely → FAIL (QL1)."""
      file_id = "javadoc-nablarch-common-dao-UniversalDao"
      self._write_javadoc_json(tmp_path, file_id)
      src = ":java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`\n"
      data = self._data(content="")  # empty — neither display text nor MD link
      issues = self._check(src, data, knowledge_dir=str(tmp_path))
      assert any("QL1" in i and "extdoc" in i.lower() for i in issues), issues
  ```

### Finding 2: `javax.*` scope-out branch in `check_source_links` has no unit test

- **Violated clause**: `.claude/rules/rbkc.md` § "All logic must have unit tests."
- **Description**: `verify.py` line 2542 checks `startswith(("java.", "jakarta.", "javax."))` — a 3-member tuple. Tests exist for `java.*` and `jakarta.*` but not `javax.*`. If `javax.` were removed from the tuple, no test would catch the regression.
- **Fix**: Add to `TestCheckSourceLinks_JsonSide_Extdoc`:
  ```python
  def test_pass_javax_skipped(self, tmp_path):
      """javax.* FQCN → external JDK, skip → PASS."""
      src = ":java:extdoc:`Servlet <javax.servlet.Servlet>`\n"
      data = self._data(content="Servlet")
      issues = self._check(src, data, knowledge_dir=str(tmp_path))
      assert issues == [], issues
  ```

### Finding 3: Step 3 `else` branch in `class_fqcn` (uppercase-initial before `(`) has no unit test

- **Violated clause**: `.claude/rules/rbkc.md` § "All logic must have unit tests." Also `.claude/rules/development.md` § "Bug-revealing cases: Input that exercises each specific failure mode."
- **Description**: `javadoc_fqcn.py` lines 50–53: when the segment before `(` is uppercase-initial (inner class constructor syntax without `.<init>`), the `else` branch keeps `prefix` unchanged. Every existing Step 3 test goes through `islower()=True` path. A bug in the `else` branch (e.g. returning `None`) would go undetected.
- **Fix**: Add to `TestClassFqcn` in `test_javadoc_fqcn.py`:
  ```python
  def test_inner_class_constructor_dot_args(self):
      # Inner class constructor syntax without .<init>:
      # nablarch.fw.Result.Error(java.lang.String)
      # Step 3: 'Error' is uppercase → else: fqcn = prefix
      # Step 4: Result + Error both uppercase → strip → nablarch.fw.Result
      assert self._fn(
          "nablarch.fw.Result.Error(java.lang.String)"
      ) == "nablarch.fw.Result"
  ```

## Observations

- `test_javadoc.py` `TestClassFqcn` duplicates `test_javadoc_fqcn.py` with 3 overlapping tests. Not a violation; could be removed for clarity.
- `test_javadoc.py` does not test `_parse_javadoc_md` with empty-body (heading-only) MD. Not a current risk but would improve coverage.
- `test_run.py` `test_convert_and_write_passes_javadoc_map_to_rst_convert` checks `call_args[1]` (kwargs only). If implementation ever passes `javadoc_map` positionally, the test would false-pass.

## Positive Aspects

- `test_javadoc_fqcn.py` provides excellent FQCN normalisation coverage with realistic Nablarch FQCNs across all 5 steps.
- `TestCheckSourceLinks_JsonSide_Extdoc` systematically covers Q1, Q2, Q3(a), Q3(b) with spec citations.
- TDD discipline is evident: test class docstrings explicitly cite spec clauses and quadrant numbers.
- `TestVerifyFile_ExtdocQC_Symmetrised` proves QC1/QC2 false-positive elimination without pinning implementation details.
- `_build_javadoc_map` tests cover all boundary cases: None input, missing directory, single file, multiple files, non-prefixed files.

## Files Reviewed

- tools/rbkc/tests/ut/test_javadoc.py (test)
- tools/rbkc/tests/ut/test_javadoc_fqcn.py (test)
- tools/rbkc/tests/ut/test_verify.py (test)
- tools/rbkc/tests/ut/test_rst_ast_visitor.py (test)
- tools/rbkc/tests/ut/test_run.py (test)
- tools/rbkc/scripts/common/javadoc_fqcn.py (source)
- tools/rbkc/scripts/verify/verify.py (source)
