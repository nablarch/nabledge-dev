# Expert Review: Software Engineer

**Date**: 2026-04-27
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 3 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The implementation is solid and well-targeted. `verify_kb_evidence.py` has a clean, narrow CLI contract; `compute_level` logic is correct; and the test suite covers the primary paths. Two issues require attention: `compute_level` has no unit tests despite being the scoring engine, and the `_NORM_MD` regex applied to LLM-supplied quotes can produce false positives that silently confirm wrong citations.

## Key Issues

### High Priority

1. **`compute_level` has zero unit tests**
   - Description: `compute_level` is the scoring engine — every benchmark result flows through it. The function has no tests at all; the only coverage is the end-to-end judge call in `run()`, which requires a live LLM. Project quality standard requires tests here.
   - Specific gaps: PARTIAL-only case → level 1 untested. 50/50 boundary (`1 > 1.0` is False → NOT level 0) is non-obvious and untested. SUPPORTED_BY_KB in c_claims lifting level to 3 with empty b_claims untested.
   - Proposed fix: Add `TestComputeLevel` class covering: all-COVERED no-C → level 2; all-COVERED with B → level 3; all-COVERED with SUPPORTED_BY_KB C-claim → level 3; any-PARTIAL → level 1; any-penalizing-C with all-COVERED → level 1; majority-MISSING → level 0; 50% MISSING → level 1; empty a_facts → level 0.
   - Decision: **Implement Now**

2. **`_NORM_MD` regex strips `__` from LLM-provided quotes, creating false positives**
   - Description: `__` alternative strips Markdown bold underscores from KB body AND from the LLM-supplied quote. If LLM quotes `__constant__`, normalization converts both to `constant`, and substring check returns `match` even if KB body only contains `constant`. A wrong citation is confirmed as correct.
   - Concrete example: `quote = "__constant__"`, `body = "The constant value"` → verbatim check fails (correct), normalized check passes (wrong: `match`).
   - Proposed fix: Apply `_NORM_MD` only to the KB body, not to the quote. For the quote, apply whitespace-only normalization (`_NORM_WS` only).
   - Decision: **Implement Now**

### Medium Priority

3. **`_make_kb` helper fails on second call with same `tmp_path`**
   - Description: `kb_root.mkdir()` without `exist_ok=True` raises `FileExistsError` if called twice in one test.
   - Proposed fix: Change to `kb_root.mkdir(exist_ok=True)`.
   - Decision: **Implement Now**

4. **`test_mismatch_file_not_found` naming slightly misleading**
   - Description: The directory exists; only the file is absent. Add a docstring clarifying the intent.
   - Proposed fix: Add `"""File missing within an existing knowledge root."""`
   - Decision: **Implement Now**

### Low Priority

5. **Schema inconsistency: `a_facts.items.fact.maxLength` = 200 in Python, 300 in `judge.md`**
   - Description: If a fact between 200–300 chars is produced, Python validation could reject it while the prompt allowed it.
   - Proposed fix: Align both to 300 (prompt is authoritative).
   - Decision: **Implement Now**

6. **`REPO_ROOT` imported in `test_llm_tools.py` but never used**
   - Description: Dead code.
   - Proposed fix: Remove the unused `REPO_ROOT` assignment.
   - Decision: **Implement Now**

## Positive Aspects

- CLI contract is clean and stable: 4 positional args, always prints to stdout, error messages machine-parseable.
- `verify()` is pure and directly testable; separation from `main()` is well-done.
- Error handling in `verify()` is comprehensive: FileNotFoundError, JSONDecodeError, OSError, empty quote, missing sid, empty body all produce distinct `mismatch:` messages.
- `compute_level` matches specification: docstring, judge prompt table, and code are all consistent.
- Judge prompt and Python schema are in sync: `_C_REASONS`, schema structure, and reason definitions all agree.
- `allowed_tools=["Grep", "Bash"]` change is correct and necessary for the verify script call.

## Recommendations

1. Add `TestComputeLevel` unit tests before merging (required by quality standard).
2. Fix `__` false-positive in normalize (two-line change).
3. Align `maxLength` for `a_facts.fact` between Python schema and prompt.
4. Future improvement: add a path traversal guard in `verify_kb_evidence.py` to ensure `kb_path` stays within `knowledge_root`.

## Files Reviewed

- `tools/benchmark/llm_tools/verify_kb_evidence.py` (new — source code)
- `tools/benchmark/bench/judge.py` (modified — source code)
- `tools/benchmark/tests/test_llm_tools.py` (new — test code)
