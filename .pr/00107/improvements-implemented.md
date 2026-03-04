# Improvements Implemented

**Date**: 2026-03-04
**Based on**: Expert review feedback

## Summary

Implemented 2 high-value, low-cost improvements from expert reviews:

1. **--max-rounds validation** (DevOps recommendation)
2. **AWS credential sanitization** (DevOps recommendation)

Both changes improve robustness and security with minimal code changes.

---

## 1. Add --max-rounds Upper Bound Validation

**File**: `tools/knowledge-creator/run.py`

**Change**:
```python
# Before
parser.add_argument("--max-rounds", type=int, default=1,
                    help="Max D->E->C loop iterations (default: 1)")
args = parser.parse_args()

# After
parser.add_argument("--max-rounds", type=int, default=1,
                    help="Max D->E->C loop iterations (default: 1, max: 10)")
args = parser.parse_args()

# Validate --max-rounds range
if args.max_rounds < 1 or args.max_rounds > 10:
    parser.error("--max-rounds must be between 1 and 10")
```

**Benefit**:
- Prevents accidental runaway iterations (e.g., `--max-rounds 999`)
- Saves API costs and time from user errors
- Clear error message guides users to valid range

**Tested**:
```bash
# Invalid values rejected
$ ./run.py --version 6 --max-rounds 0
run.py: error: --max-rounds must be between 1 and 10

$ ./run.py --version 6 --max-rounds 11
run.py: error: --max-rounds must be between 1 and 10

# Valid value accepted
$ ./run.py --version 6 --max-rounds 5 --dry-run
(runs successfully)
```

**Test coverage**: Existing tests pass (test_run_phases.py: 4/4 passed)

---

## 2. Add AWS Credential Sanitization

**File**: `tools/knowledge-creator/steps/common.py`

**Change**:
```python
# Before
env = os.environ.copy()
env.pop('CLAUDECODE', None)

# After
env = os.environ.copy()
env.pop('CLAUDECODE', None)

# Sanitize potentially sensitive cloud credentials
for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
            'AWS_SESSION_TOKEN', 'AWS_DEFAULT_REGION']:
    env.pop(var, None)
```

**Benefit**:
- Defense-in-depth security
- Prevents accidental credential leakage through subprocess environment
- Follows security best practice for subprocess execution
- Zero impact on normal operation (credentials not needed)

**Security rationale**:
- Claude CLI subprocess inherits environment variables
- AWS credentials (if present) are not needed for knowledge generation
- Removing them prevents potential leakage if subprocess behavior changes
- Complements existing CLAUDECODE removal

**Test coverage**:
- Existing tests pass (12/12 tests in test_run_phases + test_split_criteria)
- Manual verification confirms no side effects

---

## Test Results

All tests pass after implementing both improvements:

```
tests/test_run_phases.py::TestPhaseControl::test_default_phases_include_m PASSED
tests/test_run_phases.py::TestPhaseControl::test_explicit_phase_m PASSED
tests/test_run_phases.py::TestPhaseControl::test_phase_bcdem_full_flow PASSED
tests/test_run_phases.py::TestPhaseControl::test_backward_compat_gf_still_works PASSED
tests/test_split_criteria.py (8 tests) PASSED

12 passed in 0.43s
```

---

## Files Modified

1. `tools/knowledge-creator/run.py` (+3 lines)
2. `tools/knowledge-creator/steps/common.py` (+5 lines)

**Total**: 8 lines added, 0 lines removed

---

## Deferred Improvements

See `.pr/00107/split-pipeline-improvements-decisions.md` for full evaluation of all expert suggestions:

- **7 improvements deferred to future** (documentation, testing, operations)
- **7 suggestions rejected** (not worth complexity or already correct)

Deferred items are quality improvements that can be addressed based on operational experience. Current implementation is production-ready.

---

## Rationale for Implementation Decisions

### Why implement these two?

Both changes are:
- **Low cost**: 8 lines of code total, <5 minutes to implement
- **High value**: Prevent user errors and improve security
- **Zero risk**: Simple validations with clear benefits
- **Immediately beneficial**: No need to wait for operational data

### Why defer the rest?

Medium priority suggestions improve:
- Observability (error propagation, metrics)
- Documentation (diagrams, rationale)
- Future-proofing (retry logic, adaptive criteria)

These are valuable but:
- Not urgent for production readiness
- Better prioritized after operational experience
- Would delay PR merge unnecessarily
- Risk over-engineering before real-world validation

---

## Conclusion

Successfully implemented 2 high-value improvements from expert reviews while maintaining production readiness. All tests pass, no regressions introduced. Implementation demonstrates pragmatic engineering: ship what's ready, defer what's not urgent, reject what's not needed.
