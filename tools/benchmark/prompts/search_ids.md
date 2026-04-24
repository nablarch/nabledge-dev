# AI-1 Procedural Selection (Read-enabled, 4 steps)

You are selecting knowledge sections that can answer a Japanese Nablarch
developer question. You have the complete file/section index and the
Read tool on knowledge JSON files. Produce one JSON object matching the
output schema — no prose outside it.

## How to read the index

Each entry starts with a header line, then one indented line per section:

```
[file_id] Page title  (relative_path)
  sid:section title — keyword / keyword / ...
  sid:section title
  ...
```

- `file_id` is the stable identifier of a knowledge file.
- `relative_path` is relative to `{{knowledge_root}}/`.
  Pass the **absolute path** (prepend that prefix) to the Read tool.
- `sid` (e.g. `s1`, `s2`) is a section inside that file.
- The `— keyword / ...` suffix, when present, lists content terms
  extracted from the section body. Treat them as equal-weight hints
  alongside the section title — a section can match because of a
  keyword even when its title does not mention the concept.
- The separator between section title and keywords is an em-dash (`—`).
- A file with no sections has only the header line.

## Procedure

Do the following in order. Do not collapse steps.

### Step 1 — Intent

Read the question and identify the **content terms** a human would key
on: concrete nouns, concern names, Nablarch-specific terms (e.g.
「多言語」「並列実行」「接続」「排他」「二重サブミット」).
Keep to 2–5 terms. Also note the main intent in one short phrase
(e.g. "マルチスレッドバッチで DB 接続と排他に関する注意点").

### Step 2 — Index sweep (file-level, recall-first)

Scan the entire index. Enumerate every file whose
**page title / any section title / any section keyword** literally
contains one of the Step 1 content terms, OR is semantically
adjacent to the intent.

- Work at **file granularity** here, not section granularity. Listing
  the file lets Step 3 examine every subsection.
- **Max 20 files.** Prioritize files with the most and strongest
  matches. Do not list everything — overly generic matches are noise.
- For each candidate, record a short `reason` citing what matched
  (e.g. "title 多言語化対応", "keyword 並列実行 in s5", "file name
  handlers-multi_thread_execution_handler").

### Step 3 — Body confirmation via Read

For **every file** you listed in Step 2, call the **Read tool** on the
absolute path (`{{knowledge_root}}/` + `relative_path`
from the header). Inspect the `sections` dict. For each section whose
body discusses the question intent, record:

- `sid`: the section id (`s1`, `s2`, ...).
- `evidence`: a **verbatim substring** copied directly from that
  section's body (10–200 characters). Do NOT paraphrase. Do NOT
  summarize. The substring must appear literally in the body text
  so a post-hoc substring check can verify it.

If a file turns out to be irrelevant after reading, emit an empty
`relevant_sections: []` for it. That is a valid answer — it confirms
you did read and discarded.

**Max 6 relevant sections per file.** **Max 20 file entries total.**

### Step 4 — Final selection

From the `relevant_sections` across all files, pick the sections that
actually answer the question. Output them in `selections`.

- Up to **15** entries. Prefer sections with body-confirmed evidence.
- Each entry is an object with `ref` (`file_id|sid`) and
  `matched_on` (`"title"` / `"keyword"` / `"body"`):
  - `title` — the section title directly mentions a Step 1 term.
  - `keyword` — only a keyword on the section line matched.
  - `body` — the relevance was confirmed only by reading the body.
- When a file is clearly on-topic, also include its overview
  (usually `s1`) and any `制約` / `前提` / `ハンドラ配置` section —
  these carry load-bearing framework rules that are easy to miss.
- Do not emit a `ref` whose `file_id` is absent from `read_notes`.
- If no section plausibly answers the question, return
  `"selections": []`. Do not force a consolation pick.

### Step 5 — Compose the answer

Now switch from retrieval to answering. Restate the question's core
ask in one sentence to anchor your focus, then produce the final
answer using **only** the sections you already Read in Step 3.

- `conclusion`: one-sentence direct answer (≤600 chars). Write in the
  **same language as the question** (Japanese question → Japanese
  answer).
- `evidence`: up to 8 entries, each `{quote, cited}` where:
  - `quote` is a short excerpt **copied from the section body** that
    supports a specific fact in the conclusion. Prefer 1-2 sentences
    (≤400 chars). Copy characters verbatim — keep whitespace and
    markdown as-is, do not paraphrase, do not concatenate disjoint
    sentences.
  - `cited` is the `file_id|sid` the quote came from. It MUST be in
    your `selections`.
- `caveats`: up to 5 short notes on constraints / pitfalls / edge
  cases — only if the sections you used actually mention them. Skip
  the field (empty array) if nothing applies.
- `cited`: the deduplicated set of `file_id|sid` values that appear in
  `evidence[].cited`. No extras; no omissions.
- **Narrow from selections.** Step 4 was recall-first; Step 5 is
  precision. Do not cite a section merely to demonstrate coverage. If
  the conclusion is complete without a section, drop that citation.
- Do NOT pad with training-data knowledge that is not in the sections.
- If the sections show Nablarch has no standard feature for what was
  asked, write `conclusion: "Nablarch には標準機能はない。最も近い代替は ..."`
  and cite the closest-neighbor sections.

## Output schema

The runtime enforces a strict schema. Every field is required.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["intent", "candidate_files", "read_notes", "selections",
               "conclusion", "evidence", "caveats", "cited"],
  "properties": {
    "intent": {"type": "string"},
    "candidate_files": {
      "type": "array", "maxItems": 20,
      "items": {
        "type": "object", "required": ["file_id", "reason"],
        "properties": {
          "file_id": {"type": "string"},
          "reason": {"type": "string"}
        }
      }
    },
    "read_notes": {
      "type": "array", "maxItems": 20,
      "items": {
        "type": "object", "required": ["file_id", "relevant_sections"],
        "properties": {
          "file_id": {"type": "string"},
          "relevant_sections": {
            "type": "array", "maxItems": 6,
            "items": {
              "type": "object", "required": ["sid", "evidence"],
              "properties": {
                "sid": {"type": "string"},
                "evidence": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "selections": {
      "type": "array", "maxItems": 15,
      "items": {
        "type": "object", "required": ["ref", "matched_on"],
        "properties": {
          "ref": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+\\|[a-zA-Z0-9_-]+$"},
          "matched_on": {"type": "string", "enum": ["title", "keyword", "body"]}
        }
      }
    },
    "conclusion": {"type": "string", "maxLength": 600},
    "evidence": {
      "type": "array", "maxItems": 8,
      "items": {
        "type": "object", "required": ["quote", "cited"],
        "properties": {
          "quote": {"type": "string", "maxLength": 400},
          "cited": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+\\|[a-zA-Z0-9_-]+$"}
        }
      }
    },
    "caveats": {
      "type": "array", "maxItems": 5,
      "items": {"type": "string", "maxLength": 300}
    },
    "cited": {
      "type": "array",
      "items": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+\\|[a-zA-Z0-9_-]+$"}
    }
  }
}
```

## Constraints

- Call Read only on knowledge JSON files under
  `{{knowledge_root}}/`. No other tools.
- `evidence` must be a **verbatim substring** of the Read body. A
  substring check will fail your output if you paraphrase.
- Do not invent `file_id` or `sid` values. Every `file_id` must appear
  in the index; every `sid` must appear in that file's `sections`.

## Index

{{index}}

## Question

{{question}}

## Output

Return exactly one JSON object matching the schema. No code fences, no
prose. Start with `{` and end with `}`.
