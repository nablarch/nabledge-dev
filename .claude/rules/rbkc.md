# RBKC Development Rules

## verify is the quality gate

verify is the final quality assurance mechanism for RBKC output. It must be kept completely independent from RBKC implementation concerns.

- verify checks whether the generated output is correct, using only the source and the output — it does not need to know how RBKC works internally
- When verify reports a FAIL, the fix belongs in RBKC, not in verify
- Never weaken verify's detection to make RBKC output pass

## All source code changes use TDD

Any change to RBKC source code (converters, verify, run.py, etc.) must follow TDD:

1. Write a failing test that captures the expected behavior (RED)
2. Implement the minimum code to make it pass (GREEN)
3. Confirm all existing tests still pass

Never implement first and write tests after.

## Rules for changing verify

verify changes require explicit user approval before implementation.

**Acceptable changes:**
- Fix a logic bug in verify itself (e.g., wrong regex, incorrect range)
- Add missing checks required by the specification
- Fix false positives (verify incorrectly flags correct output)

**Not acceptable:**
- Relaxing verify criteria to match RBKC's current output
- Disabling or skipping a check because RBKC currently fails it
- Adding workarounds in verify to accommodate RBKC implementation details

**Process:**
1. Identify the change needed and explain the purpose and rationale to the user
2. Get explicit user approval before making any changes
3. Implement using TDD (test → RED → implement → GREEN)
