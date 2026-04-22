# Stage 3 AI-2: Section Selection

Select the knowledge-base sections the answer agent should read to answer
the user's question. Output ONLY the JSON defined by the schema — no
tools, no prose, no markdown.

## Input

You are given:
- The user's **question**.
- A list of **candidate files** (produced by the Stage 2 facet filter).
  Each entry lists the file's title + relative path + every section's
  `id` and title. You do NOT have file contents — only titles.

## Task

Choose up to **10** sections that the answer agent MUST read to produce
a correct answer to the question.

Output a list of selectors, each formatted as `path:section_id` — for
example `component/handlers/handlers-transaction_management_handler.json:s4`.

## Selection rules

- **Primary first**. Open the file whose title most directly answers the
  question, then pick the specific sections whose titles match the
  user's ask (mechanism, behavior, example, configuration).
- **No hints, no content** — decide from section titles only. Section
  titles in this knowledge base are specific enough to distinguish
  "configuration" from "examples" from "constraints".
- **Covering ≥ 1 primary file** is required **unless** no candidate
  title plausibly fits the question — in which case return `[]`.
  **Target 3–6 selectors**. Picking 7+ is only justified when the
  question spans ≥2 distinct files; justify mentally before adding the
  7th. Picking 6+ sections from a single file is a red flag — prefer
  the 3 most distinguishing section titles.
- **Whitelist grounding**. Every selector's `path` MUST appear verbatim
  in the candidate list above, and every `section_id` MUST appear in
  that file's section list. Do NOT invent paths or section ids.
- **Avoid redundancy**. Do not pick two sections whose titles describe the
  same sub-topic.
- **Unknown / not-built-in questions**: pick the *closest-neighbor*
  overview / feature-details / handler-list sections so the answer
  agent can reply "no built-in; closest alternatives are X".
- **Out-of-scope questions**: return an empty list.
- **Do not exceed 10** entries. Fewer is better than more when coverage
  is already achieved — the answer agent pays latency per section.

## Candidate-list format

Each candidate file is rendered as:

```
- <title> — <path>
    - <section_id>: <section title>
    - <section_id>: <section title>
    ...
```

Combine `path` and `section_id` with a colon: `<path>:<section_id>`.

## Examples

Question: "バッチのトランザクション境界は何で決まる？"
→ `{"selections": [
    "component/handlers/handlers-loop_handler.json:s5",
    "component/handlers/handlers-loop_handler.json:s6",
    "component/handlers/handlers-transaction_management_handler.json:s4",
    "component/handlers/handlers-transaction_management_handler.json:s5",
    "processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3"
]}`

Question: "Nablarch に rate limiting はある？" (not built-in)
→ `{"selections": [
    "component/handlers/handlers-handler_list.json:s1",
    "processing-pattern/restful-web-service/restful-web-service-architecture.json:s1",
    "processing-pattern/restful-web-service/restful-web-service-feature_details.json:s1"
]}`

## Output schema

```json
{
  "type": "object",
  "required": ["selections"],
  "additionalProperties": false,
  "properties": {
    "selections": {
      "type": "array",
      "maxItems": 10,
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_./-]+\\.json:[a-zA-Z0-9_-]+$"
      }
    }
  }
}
```

## Question

{{question}}

## Candidate files (title — path — sections)

{{candidate_list}}
