# Stage 3 Judge (v2 — fact-coverage grading)

You are grading a generated answer against a reference answer for a
Nablarch QA benchmark. Score 0–3 based ONLY on fact coverage.
Output ONLY the JSON defined by the schema — no tools, no prose outside JSON.

## Inputs

- **Question** — the user's ask
- **Reference answer** — the authoritative answer. This defines the set
  of facts that a correct answer MUST convey (the "required facts").
- **Reference sources** — the Nablarch knowledge sections the reference
  answer cites. These define the "evidence boundary" — the set of facts
  Nablarch actually supports for this question.
- **Generated answer** — the answer to score.

## Method (follow in order)

**Step 1. Extract required facts from the reference answer.**
List each atomic claim as a bullet. Examples:
- "no built-in rate limiting exists"
- "closest mechanism is a custom Handler"
- "`ServiceAvailabilityCheckHandler` is NOT a rate limiter — it is an
  availability on/off switch" (only if the reference explicitly says so)

**Step 2. For each required fact, check the generated answer.**
Mark COVERED / PARTIAL / MISSING / CONTRADICTED.
Wording does not matter — "ビルトインなし" = "標準機能は存在しない".
Only the semantic claim matters.

**Step 3. Detect over-reach.**
For each substantive claim in the generated answer that is NOT in the
required-facts list:
- If the claim is in the reference sources AND is on-topic for the
  question: NEUTRAL (not penalized).
- If the claim is in the reference sources BUT addresses a different
  concern than the question (e.g., proposing
  `ServiceAvailabilityCheckHandler` for rate limiting, but the sources
  describe it as a service on/off switch): OVER-REACH.
- If the claim is NOT in the reference sources at all: HALLUCINATION.

**Step 4. Score.**
- **3** — All required facts COVERED. No CONTRADICTED. No OVER-REACH.
  No HALLUCINATION. (Extra on-topic detail is fine.)
- **2** — All required facts COVERED or PARTIAL, AND at most one
  OVER-REACH or one minor HALLUCINATION. No CONTRADICTED on a core
  fact.
- **1** — At least one required fact MISSING or CONTRADICTED, OR a
  substantive OVER-REACH that would mislead the reader (e.g.,
  proposing a mechanism that does not solve the asked problem).
- **0** — Majority of required facts missing, OR the central claim
  contradicts the reference, OR the answer is essentially a non-answer
  (e.g., "参照可能なセクションがありません").

## Critical rules

- If the reference answer says "no built-in X exists; closest is Y", an
  answer that proposes Z instead of Y is **at most level 1**, even if Z
  is a real Nablarch class. Proposing the wrong mechanism for the asked
  problem is a substantive OVER-REACH.
- A class/handler name appearing in the Nablarch knowledge base does
  NOT license using it as an answer. It must be supported by the
  reference sources **as an answer to THIS question**.
- Do not reward fluency, citation count, or length. Only fact coverage
  and absence of over-reach.

## Output schema

```json
{
  "type": "object",
  "required": ["required_facts", "over_reach", "level", "reasoning"],
  "additionalProperties": false,
  "properties": {
    "required_facts": {
      "type": "array",
      "maxItems": 15,
      "items": {
        "type": "object",
        "required": ["fact", "status"],
        "additionalProperties": false,
        "properties": {
          "fact": {"type": "string", "maxLength": 200},
          "status": {"enum": ["COVERED","PARTIAL","MISSING","CONTRADICTED"]}
        }
      }
    },
    "over_reach": {
      "type": "array",
      "maxItems": 10,
      "items": {
        "type": "object",
        "required": ["claim", "type", "why"],
        "additionalProperties": false,
        "properties": {
          "claim": {"type": "string", "maxLength": 200},
          "type": {"enum": ["OVER-REACH","HALLUCINATION"]},
          "why": {"type": "string", "maxLength": 200}
        }
      }
    },
    "level": {"type": "integer", "enum": [0,1,2,3]},
    "reasoning": {"type": "string", "maxLength": 600}
  }
}
```

Write `reasoning` in the **same language as the question** (Japanese
questions → Japanese reasoning).

## Question

{{question}}

## Reference answer

{{reference_answer}}

## Reference sources

{{reference_sources}}

## Generated answer

{{generated_answer}}

## Generated citations

{{generated_cited}}
