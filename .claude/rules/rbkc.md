# RBKC Development Rules

## verify is the quality gate

verify is the final quality assurance mechanism for RBKC output. It must be kept completely independent from RBKC implementation concerns.

- verify checks whether the generated output is correct, using only the source and the output — it does not need to know how RBKC works internally
- verify must never import from or depend on RBKC implementation modules (converters, resolver, run, etc.)
- verify's logic must be derivable from source format specifications (RST, Markdown, Excel) alone — not from how RBKC happens to work
- When verify reports a FAIL, the fix belongs in RBKC, not in verify
- Never weaken verify's detection to make RBKC output pass

## Scope: content only

RBKC generates **content only** — titles and body text derived from source (RST/Markdown/Excel).

- `hints` (keyword index) is **out of scope for RBKC**. RBKC JSON must not contain a `hints` field, and docs MD must not contain a `<details><summary>keywords</summary>` block.
- AI-driven hints curation is handled by a separate issue (see `.work/00299/handoff-hints/` for the handoff assets and rationale).
- verify therefore does not check hints consistency; any hints-related check in verify should be considered a bug and removed.

## Test coverage policy

**verify (scripts/verify/verify.py)**
- All logic must have unit tests.
- Every new check added to verify requires a corresponding test before implementation (TDD).

**create-side (converters, resolver, run, etc.)**
- No tests needed. verify passing is sufficient — it is the quality gate for output correctness.

**CLI layer (rbkc.sh, run.py argument parsing, command dispatch)**
- Tests required only here, because verify does not exercise CLI code paths.
- Examples: argument validation, command routing, error handling for missing files or invalid input.

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

## Decide from the spec and quality standard — do not punt to the user

The `rbkc-verify-quality-design.md` spec plus the ゼロトレランス quality
standard (§2-1: 1% のリスクも許容しない) already determine the answer to
most design / review questions. Derive that answer yourself and implement
it. Do not ask the user to pick between options the standard has ruled out.

**Examples the standard already decides:**

- "1-char Excel residue — tolerate or FAIL?" → FAIL. Spec §3-1 Excel
  節 says any residue other than whitespace is QC2.
- "JSON section with empty content — skip or match?" → Match. Spec §3-3
  requires verbatim containment.
- "`:role:` regex — must the closing backtick be required per spec wording?"
  → Yes. Spec §3-1 QC5 writes `:role:\`text\`` (both backticks).
- "QL1 substitution-body image — include or exclude?" → Exclude, by spec
  symmetry with QL2's explicit substitution-body URL exclusion.
- "QC1 residue reporting — RST one-snippet vs MD all-fragments — which
  is correct?" → All fragments. The one-snippet form hides gaps, which
  ゼロトレランス forbids.

**Ask the user only when:**

1. The spec is silent and the quality standard does not force a direction, AND
2. Multiple directions all pass the standard but affect user-visible behaviour
   (output format, API shape, process) that the user owns.

In that case, state the spec gap, propose the stricter direction (default
under ゼロトレランス), and ask for confirmation — not an open-ended menu.

## Review findings — default is fix, not triage

All Medium and higher findings from a bias-avoidance QA review are
blocking unless the spec / standard says otherwise. "Low impact in v6"
is not a valid defer reason — ゼロトレランス forbids accepting risk
just because the corpus happens not to exercise it right now.

Acceptable defer reasons:
- The finding names behaviour the spec explicitly sanctions (with the
  clause quoted), and the reviewer missed that sanction.
- The finding is Low-severity cosmetic drift that cannot cause a spec
  violation (e.g. message formatting, docstring wording).

Any other deferral needs the user's explicit approval with the spec
clause that permits the deferral quoted inline.
