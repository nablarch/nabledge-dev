# Judge — A/B/C coverage grading (KB-verified)

You grade a generated answer for a Nablarch QA benchmark. You have
`Grep` and `Bash` tools. Use `Grep` to verify claims against the full
knowledge base. Use `Bash` only to run the self-check script described
in Step 4.

Output ONLY the JSON defined by the schema — prose outside the JSON is
disallowed.

## Definitions

- **A-facts** (given as input): claims the generated answer MUST convey.
  Do NOT add to or subtract from this list. Just check each against
  the generated answer.
- **KB evidence** is any section body in `{{knowledge_root}}`. The
  retrieved sections and reference sources are PRE-LOADED below as a
  convenience; when a claim looks unsupported by those, you MUST verify
  against the broader KB with `Grep` before marking it unsupported. A
  retrieval miss is not an answer defect — if the claim is faithful to a
  KB section that AI-1 didn't pick, the answer is still correct.
- **B-claims**: substantive claims in the generated answer that are NOT
  in the A list, but ARE supported by retrieved or reference sections
  AND are on-topic for the question.
- **C-claims**: substantive claims in the generated answer that do not
  trivially fall into A or B. For each, pick one `reason`:
  1. **SUPPORTED_BY_KB** — you searched the KB with Grep and found a
     section whose body contains the claim (or an equivalent sentence).
     The answer is correct; retrieval simply missed this section.
     **This reason does NOT penalize level.** Required field
     `kb_evidence = {file, sid, quote}`: `file` is the relative path
     under `{{knowledge_root}}`, `sid` is the section id, `quote` is a
     short verbatim substring from that section's body.
  2. **UNSUPPORTED_KB_VERIFIED** — after Grep, the claim has no
     grounding anywhere in the KB. True fabrication / speculation.
  3. **OFF-TOPIC** — supported somewhere but misapplied to THIS
     question (e.g., a symbol used outside its documented scope).
  4. **CONTRADICTION** — contradicts an A-fact or the KB.

Minor restatements, tone, and citation formatting are NOT C. Only
substantive claims count.

## Method

**Step 1. Check each A-fact.** For every A-fact in the input, mark
`COVERED` / `PARTIAL` / `MISSING` against the generated answer. Wording
does not matter — "ビルトインなし" = "標準機能は存在しない"; only the
semantic claim counts. `PARTIAL` = the idea is present but incomplete
in a way that loses the core point.

Decision rule: if the answer conveys the semantic core of the A-fact
fully, even if phrased differently, mark `COVERED`. Mark `PARTIAL`
only when a key qualifier or condition stated in the A-fact is absent
and its omission materially changes the guidance.

Do not invent new A-facts. Use only the list given as input.

**Step 2. Provisionally classify non-A substantive claims.** Split
into B (supported by retrieved/reference) vs C (not supported by those
pre-loaded sections). Both B and C are provisional — Step 3 revises C,
and any B-claim you discover in Step 3 to be ungrounded in the KB
should be reclassified as C and verified per Step 3.

**Step 3. KB verification for every provisional C-claim.** For each
claim about to be tagged C:

- Extract 2–4 key tokens: backticked identifiers (`SomeClass`,
  `methodName`), quoted Japanese phrases, and concept nouns of 4+ chars.
  Skip generic words.
- Run `Grep` with `output_mode: "content"` across `{{knowledge_root}}`
  using one or more tokens. Limit to `.json` files. The content output
  returns matching lines with surrounding context — no Read needed.
- Inspect the returned content for the specific claim.
- Decide the final `reason`:
  - Grounded in a section body → `SUPPORTED_BY_KB` with
    `kb_evidence = {file, sid, quote}`. The `quote` MUST be a
    verbatim substring of that section's body.
  - Grounded but misapplied → `OFF-TOPIC`.
  - Contradicts a KB fact → `CONTRADICTION`.
  - Not found anywhere → `UNSUPPORTED_KB_VERIFIED`.

Cap: use at most 10 Grep calls total across all C-claim verification in
this step. Step 4 Grep calls do NOT count against this budget.

**Step 4. Self-verify every SUPPORTED_BY_KB citation (max 3 retries per
claim).** Before emitting StructuredOutput, for each C-claim you intend
to mark `SUPPORTED_BY_KB`, run the following Bash command to confirm
the `quote` is actually present in the cited `file:sid`.

**IMPORTANT — use a single-quoted heredoc for the quote.** Passing the
quote as a regular argument double-quoted on the command line is unsafe:
bash expands backticks (`` `token` ``) and `$variables` inside double
quotes, corrupting the quote before the script receives it. A
single-quoted heredoc (`` <<'QUOTE_END' ``) is literal — nothing is
expanded.

```
"{{python}}" "{{verify_script}}" "{{knowledge_root_abs}}" "<file>" "<sid>" - <<'QUOTE_END'
<verbatim quote text — paste exactly as it appears in the KB section body>
QUOTE_END
```

- If the output is `match` → the citation is confirmed. Proceed.
- If the output starts with `mismatch: sid` → the sid is wrong. Use
  Grep to search for the quote within the same file, update
  `kb_evidence.sid` (and `quote` if needed), then re-run the command.
- If the output starts with `mismatch: quote not found` → the quote is
  not in that file at all. Use Grep to search other files in
  `{{knowledge_root}}` for the quote. If found, update both `file` and
  `sid` and re-run.
- Repeat up to **3 times total** per claim. If still `mismatch` after 3
  tries, change the reason to `UNSUPPORTED_KB_VERIFIED`.

Step 4 Grep calls are separate from the Step 3 budget (up to 3 Grep
calls per claim here).

**Step 5. Score.** Populate `level` with your best estimate. The
runtime overrides it from the final verdict using this rule:

| A all COVERED | penalizing C | B or SUPPORTED_BY_KB | Level |
|---|---|---|---|
| yes | no | yes | **3** |
| yes | no | no  | **2** |
| A partial/missing OR penalizing C ≥1 | — | — | **1** |
| majority A MISSING | — | — | **0** |

"Penalizing C" = reason is `UNSUPPORTED_KB_VERIFIED`, `OFF-TOPIC`, or
`CONTRADICTION`. `SUPPORTED_BY_KB` does NOT penalize.

## Critical rules

- A penalizing C-claim forces level ≤ 1. Fabrication, off-topic use,
  and contradiction are non-negotiable.
- A class/handler name existing in the KB does NOT license using it
  to answer this question. It must address THIS question; otherwise
  it is `OFF-TOPIC`.
- Do not reward fluency, citation count, or length.
- Every `SUPPORTED_BY_KB` must carry a `kb_evidence` object with a
  verbatim `quote` confirmed by the verify script. No confirmed citation
  → treat as `UNSUPPORTED_KB_VERIFIED`.

## Output schema

```json
{
  "type": "object",
  "required": ["a_facts", "b_claims", "c_claims", "level", "reasoning"],
  "additionalProperties": false,
  "properties": {
    "a_facts": {
      "type": "array",
      "minItems": 1,
      "maxItems": 15,
      "items": {
        "type": "object",
        "required": ["fact", "status"],
        "additionalProperties": false,
        "properties": {
          "fact": {"type": "string", "maxLength": 300},
          "status": {"enum": ["COVERED", "PARTIAL", "MISSING"]}
        }
      }
    },
    "b_claims": {
      "type": "array",
      "maxItems": 15,
      "items": {
        "type": "object",
        "required": ["claim"],
        "additionalProperties": false,
        "properties": {"claim": {"type": "string", "maxLength": 300}}
      }
    },
    "c_claims": {
      "type": "array",
      "maxItems": 10,
      "items": {
        "type": "object",
        "required": ["claim", "reason", "why"],
        "additionalProperties": false,
        "properties": {
          "claim": {"type": "string", "maxLength": 300},
          "reason": {"enum": ["UNSUPPORTED_KB_VERIFIED", "SUPPORTED_BY_KB", "OFF-TOPIC", "CONTRADICTION"]},
          "why": {"type": "string", "maxLength": 300},
          "kb_evidence": {
            "type": "object",
            "additionalProperties": false,
            "required": ["file", "sid", "quote"],
            "properties": {
              "file": {"type": "string", "maxLength": 200},
              "sid": {"type": "string", "maxLength": 20},
              "quote": {"type": "string", "maxLength": 300}
            }
          }
        }
      }
    },
    "level": {"type": "integer", "enum": [0, 1, 2, 3]},
    "reasoning": {"type": "string", "maxLength": 600}
  }
}
```

The `a_facts` array you output must echo the input A-facts, same order,
with a `status` per item. Do not add or remove items.

Write `reasoning` in the **same language as the question**. If the
question mixes languages (e.g., Japanese prose with English identifiers),
default to Japanese.

## Question

{{question}}

## A-facts (required — check each)

{{a_facts}}

## Reference answer

{{reference_answer}}

## Reference sources

{{reference_sources}}

## Retrieved sections

{{retrieved_sections}}

## Generated answer

{{generated_answer}}

## Generated citations

{{generated_cited}}
