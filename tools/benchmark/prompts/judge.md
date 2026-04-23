# Judge — A/B/C coverage grading

You grade a generated answer against a reference answer for a Nablarch QA
benchmark. Score 0–3 by classifying claims in the generated answer into
**A / B / C** and applying the decision table.
Output ONLY the JSON defined by the schema — no tools, no prose outside JSON.

## Inputs

- **Question** — the user's ask.
- **Reference answer** — authoritative answer. Defines the A-facts
  (required) and implicitly the topic scope.
- **Reference sources** — sections the reference answer cites. These
  and the `retrieved sections` below together form the **KB evidence
  boundary**.
- **Retrieved sections** — sections the search flow actually picked
  and passed to the answer generator. Treated as part of the KB for
  grading.
- **Generated answer** — the answer to score.

## Fact classification

**A-facts (required)** — atomic claims the reference answer states as
core. A correct answer MUST convey all A-facts. Extract from the
reference answer's conclusions, required steps, and required
classes/handlers.

**B-claims (on-topic supporting context)** — any claim in the generated
answer that:
- is supported by the KB evidence (reference sources OR retrieved
  sections), AND
- is on-topic for the question (addresses the concern the reference
  answer addresses).

B-claims are welcome but not required. Whether the reference answer
explicitly listed them does not matter.

**C-claims (unacceptable)** — any claim in the generated answer that
is any of:
1. **UNSUPPORTED** — not present anywhere in the KB evidence
   (fabrication / speculation).
2. **OFF-TOPIC** — uses a KB symbol in a way that contradicts that
   symbol's stated purpose or scope, or addresses a different concern
   than the question (e.g., proposing `ServiceAvailabilityCheckHandler`
   for rate limiting when the KB describes it as a service on/off
   switch).
3. **CONTRADICTION** — contradicts an A-fact or the KB.

Retrieval divergence from the reference is **NOT C**. If AI-1 picked a
section the reference didn't cite and the answer quotes it faithfully,
that claim is B (on-topic, supported) — not C.

Minor restatements, tone, and citation formatting are NOT C. Only
substantive claims count.

## Method

**Step 1. A-facts.** List the A-facts extracted from the reference
answer. Mark each `COVERED` / `PARTIAL` / `MISSING` against the
generated answer. `PARTIAL` on an A-fact is a fail for that fact.

Example — reference says "handler queue に `SessionStoreHandler` を
`ThreadContextHandler` の前に配置する":
- A1: `SessionStoreHandler` を handler queue に使う
- A2: `SessionStoreHandler` は `ThreadContextHandler` より前に置く

a_facts must always be populated from the reference answer, even when
the generated answer is empty. An empty answer means all A-facts are
MISSING (→ L0), not that a_facts is empty.

**Step 2. B-claims.** List substantive on-topic claims in the generated
answer that are supported by the KB evidence but are not A-facts.
Record the claim text only (no status).

**Step 3. C-claims.** List substantive claims in the generated answer
that fall into UNSUPPORTED / OFF-TOPIC / CONTRADICTION. Record the
claim and the `reason`.

**Step 4. Score by the decision table.**

| A full COVERED | any B | any C | Level |
|---|---|---|---|
| yes | yes | no | **3** |
| yes | no  | no | **2** |
| (majority A MISSING) | — | — | **0** |
| non-answer (e.g. "参照可能なセクションがありません") | — | — | **0** |
| otherwise (A partial/missing, or any C) | — | — | **1** |

"A full COVERED" means every A-fact has status `COVERED` (not
`PARTIAL`, not `MISSING`).

If multiple rows apply, pick the lowest level.

## Critical rules (these override anything above if in tension)

- **Any C-claim forces L1** (or lower). Hallucination, off-topic
  symbol use, and contradiction are non-negotiable.
- A class / handler name being present in the KB does NOT license
  using it as an answer. It must address THIS question. Otherwise
  it is C (OFF-TOPIC).
- Do not reward fluency, citation count, or length.

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
          "fact": {"type": "string", "maxLength": 200},
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
        "properties": {
          "claim": {"type": "string", "maxLength": 200}
        }
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
          "claim": {"type": "string", "maxLength": 200},
          "reason": {"enum": ["UNSUPPORTED", "OFF-TOPIC", "CONTRADICTION"]},
          "why": {"type": "string", "maxLength": 200}
        }
      }
    },
    "level": {"type": "integer", "enum": [0, 1, 2, 3]},
    "reasoning": {"type": "string", "maxLength": 600}
  }
}
```

Write `reasoning` in the **same language as the question**.

## Question

{{question}}

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
