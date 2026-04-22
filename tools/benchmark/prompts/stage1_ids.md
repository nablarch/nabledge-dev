# Stage 1 (IDs variant): Direct knowledge selection

Given a user question and the complete knowledge index for Nablarch 6,
identify the sections that are most likely to answer the question.

Output ONLY the JSON defined by the schema — no tools, no prose, no markdown.

## How to read the index

Each entry is two lines:

```
[file_id] Page title
  sid:section title / sid:section title / ...
```

- `file_id` is the stable identifier of a knowledge file.
- Each `sid` (e.g., `s1`, `s2`) is a section inside that file.
- The 2nd line is absent when the file has no sections.

## Selection task

Return a list of `file_id|sid` strings that point to the sections most
likely to contain the answer.

- Pick 0–10 sections. Fewer is better when the question is narrow;
  return the minimum that actually answers the question.
- Always emit the full `file_id|sid` form. Do NOT emit bare `file_id`.
  If a file has no sections in the index, do not select it.
- Each `file_id|sid` must appear at most once.
- Prefer file_ids whose page title or a specific section title matches
  the concrete terms in the question (framework concepts, Japanese
  UI/business terms, concrete class names, etc.).
- When a section title directly names the topic (e.g. "入力値のチェック",
  "Content Security Policy(CSP)対応"), that section is almost certainly
  the right pick.
- When multiple files look equally relevant, include sections from both.
- The `feature_details` page of a processing pattern often has a
  per-concern section table of contents. Those sections frequently serve
  as the correct entry-point for pattern-specific questions.
- If the question covers multiple distinct topics, include 1–3 sections
  per topic (still within the 10-item cap).
- If no section in the index plausibly answers the question (e.g., a
  Spring Boot configuration question, a general Java question), return
  `{"selections": []}`. Do NOT return a best-guess consolation pick —
  an empty list is the correct answer for out-of-scope questions.

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
      "uniqueItems": true,
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_-]+\\|[a-zA-Z0-9_-]+$"
      }
    }
  }
}
```

Each `selections` entry must be of the form `file_id|sid` using the
exact `file_id` and `sid` strings from the index. Do not invent values.

## Examples

Question: "ファイルの明細レコードを読み込んで DB テーブルに取り込む夜間バッチを作りたい。Nablarch での推奨構成を知りたい"
→ `{"selections": ["nablarch-batch-architecture|s1", "nablarch-batch-architecture|s3", "nablarch-batch-feature_details|s1"]}`

Question: "画面の入力値チェックの書き方を知りたい"
→ `{"selections": ["web-application-feature_details|s2", "libraries-bean_validation|s13"]}`
(feature_details section titles have a per-concern table of contents; the
section whose title names the concern — here "入力値のチェック" — is the
right entry-point.)

Question: "Nablarch のトランザクション境界はどこで決まる？"
→ `{"selections": ["handlers-transaction_management_handler|s3"]}`
(a narrow, concrete-term question — one precise section is enough.)

Question: "Spring Boot の設定ファイルはどこに置く？"
→ `{"selections": []}`

## Index

{{index}}

## Question

{{question}}

## Output

Return exactly one JSON object matching the schema. No code fences, no
commentary, no keys other than `selections`. The response must start with
`{` and end with `}`.
