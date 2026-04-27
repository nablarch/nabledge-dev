# AI-1 Procedural Selection (Read-enabled, 4 steps)

You are selecting knowledge sections that can answer a Japanese Nablarch
developer question. You have the complete file/section index and the
Read tool on knowledge JSON files.

**Critical rule**: You MUST call the Read tool on EVERY file you list in
Step 2 before outputting any JSON. Outputting the schema without Read
calls will be detected and marked as failure.

Produce one JSON object matching the output schema — no prose outside it.

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

Complete each step fully before moving to the next. Do not output the
JSON until all 4 steps are complete.

### Step 1 — Extract intent

Identify the **content terms** a human would key on: concrete nouns,
concern names, Nablarch-specific terms (e.g. 「多言語」「並列実行」「接続」
「排他」「二重サブミット」). Keep to 2–5 terms. Write the main intent in
one short phrase. Record this as `intent`.

### Step 2 — Enumerate candidate files (recall-first)

Scan the entire index. List every file whose **page title / any section
title / any section keyword** literally contains one of the Step 1 terms,
OR is semantically adjacent to the intent.

- Work at **file granularity** — listing the file lets Step 3 inspect
  every subsection via Read.
- **Max 20 files.** Include all plausible matches. When in doubt, include.
- For each candidate, record a short `reason` citing what matched
  (e.g. "title 多言語化対応", "keyword 排他 in s5").
- Record the result as `candidate_files`.

### Step 3 — Read every candidate file (MANDATORY)

**Call the Read tool on every file in `candidate_files`.**

For each file:
1. Call Read with the absolute path (`{{knowledge_root}}/` + `relative_path`).
2. Inspect the `sections` dict.
3. For each section whose body discusses the question intent, record:
   - `sid`: the section id (`s1`, `s2`, ...).
   - `evidence`: copy characters verbatim from the section body.
     **Copy the entire body** if it is ≤ 500 characters — do not stop
     early. If the body is longer than 500 characters, copy the first
     450 characters, then append the full `> **重要**:` block if one
     exists in the section (even if that pushes past 500 characters).
     Do NOT paraphrase or summarize. Do NOT truncate mid-sentence.
   - `scope_note` *(optional)*: if the section covers a pattern whose
     scope differs from the question (e.g., section is about
     multi-process configuration but the question is single-process /
     single-thread), record that mismatch here in one sentence.
     Leave this field absent when scope is fine.
4. If a file turns out irrelevant after reading, record it with
   `relevant_sections: []` — this confirms you read and discarded it.

**Structural requirement**: `read_notes` must contain exactly one entry
for every file_id in `candidate_files`. Missing entries will fail
validation.

Maximum 6 relevant sections per file. Maximum 20 file entries total.

### Step 4 — Select sections and compose the answer

**Select sections** from the evidence gathered in Step 3.

- Pick up to **15** sections that actually answer the question. Prefer
  sections with body-confirmed evidence from Step 3.
- Each selection must have `ref` (`file_id|sid`) and `matched_on`:
  - `"title"` — the section title directly mentions a Step 1 term.
  - `"keyword"` — only a keyword on the section line matched.
  - `"body"` — relevance was confirmed only by reading the body.
- Do not emit a `ref` whose `file_id` is absent from `read_notes`.
- If no section plausibly answers the question, return `"selections": []`.
- Record as `selections` and `files_read_count` (count of files you
  called Read on in Step 3).

**Self-check before composing**: For each section in `selections`,
re-read the `evidence` string you copied in Step 3 for that `file_id|sid`.
For every factual claim you plan to include in the answer, locate the
exact supporting sentence in one of those evidence strings. If you cannot
point to a verbatim sentence in the evidence, that claim MUST be dropped —
do not substitute from background knowledge. If the question asks for a
fact that no selected section contains, state the gap explicitly in
`conclusion` (e.g. "セクション中に記載なし") rather than filling it from
inference.

**Compose the answer** using only the sections you Read in Step 3.

- `conclusion`: one-sentence direct answer (≤600 chars). Write in the
  **same language as the question** (Japanese question → Japanese answer).
- `evidence`: up to 10 entries, each `{quote, cited}` where:
  - `quote` is a short excerpt **copied from the section body** that
    supports a specific fact in the conclusion. Prefer 1–2 sentences
    (≤400 chars). Copy characters verbatim — keep whitespace and
    markdown as-is. Do not paraphrase. Do not concatenate disjoint
    sentences.
  - `cited` is the `file_id|sid` the quote came from. It MUST be in
    `selections`.
- `caveats`: up to 5 notes on constraints / pitfalls / edge cases.
  Each caveat is `{"note": "...", "cited": "file_id|sid"}`.
  **Caveats MUST be grounded in the sections you Read** — every note
  must cite the section where you found it. Do not add constraints or
  warnings from background knowledge. If the sections do not mention
  any caveats, return an empty array.
- `cited`: deduplicated set of `file_id|sid` values from `evidence[].cited`.
- **Narrow from selections.** Step 2–3 were recall-first; Step 4 answer
  is precision. Do not cite a section merely for coverage. Drop sections
  whose content is not needed to complete the answer.
- **Scope check**: Before citing a section in the conclusion, verify that
  its scope matches the question. For example, a section about
  multi-process patterns (`db_messaging` / `multiple_process`) must NOT
  be cited as if it applies to a single-process multi-thread scenario.
  If a section's scope is different, either omit it or explicitly qualify
  it in the conclusion (e.g. "マルチプロセス構成の場合は...").
- Do NOT add facts from training-data knowledge not present in the sections.
- If the sections show Nablarch has no standard feature for the ask,
  write `conclusion: "Nablarch には標準機能はない。最も近い代替は ..."`
  and cite the closest-neighbor sections.

## Output schema

The runtime enforces a strict schema. Every field is required.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["intent", "candidate_files", "read_notes", "files_read_count",
               "selections", "conclusion", "evidence", "caveats", "cited"],
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
                "evidence": {"type": "string"},
                "scope_note": {"type": "string", "maxLength": 200}
              }
            }
          }
        }
      }
    },
    "files_read_count": {"type": "integer", "minimum": 0},
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
      "type": "array", "maxItems": 10,
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
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["note", "cited"],
        "properties": {
          "note": {"type": "string", "maxLength": 300},
          "cited": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+\\|[a-zA-Z0-9_-]+$"}
        }
      }
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
