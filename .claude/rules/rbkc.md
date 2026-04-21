# RBKC Development Rules

## verify is the quality gate

verify is the final quality assurance mechanism for RBKC output. It must be kept completely independent from RBKC implementation concerns.

- verify checks whether the generated output is correct, using only the source and the output — it does not need to know how RBKC works internally
- verify must never import from or depend on RBKC implementation modules (converters, resolver, hints, run, etc.)
- verify's logic must be derivable from source format specifications (RST, Markdown, Excel) alone — not from how RBKC happens to work
- When verify reports a FAIL, the fix belongs in RBKC, not in verify
- Never weaken verify's detection to make RBKC output pass

## Test coverage policy

**verify (scripts/verify/verify.py)**
- All logic must have unit tests.
- Every new check added to verify requires a corresponding test before implementation (TDD).

**create-side (converters, resolver, hints, run, etc.)**
- No tests needed. verify passing is sufficient — it is the quality gate for output correctness.

**CLI layer (rbkc.sh, run.py argument parsing, command dispatch)**
- Tests required only here, because verify does not exercise CLI code paths.
- Examples: argument validation, command routing, error handling for missing files or invalid input.

## Hints files

`tools/rbkc/hints/v{version}.json` is a **source file**, not a generated artifact.

- **Generate once**: Run `rbkc hints {version}` once to generate from the KC cache. Verify the output, then never regenerate.
- **Update manually**: After initial generation, edit `hints/v{version}.json` directly when hints need adjustment.
- **Input to create**: `rbkc create` reads `hints/v{version}.json` as its hints source. The KC cache is not required at create time.
- **Verify checks hints consistency**: `rbkc verify` checks that knowledge JSON hints == docs MD hints == `hints/v{version}.json` hints (three-way match).
- **KC cache alignment is a one-time concern**: The `rbkc hints` command produces the initial file from KC cache. Once committed, the KC cache is no longer consulted by create or verify.

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
3. Implement using TDD:
   - Write the verify unit test → confirm RED
   - Implement the verify check → confirm GREEN
   - Implement the RBKC fix → confirm verify GREEN on actual output
