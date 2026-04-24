# Stage 1 (IDs variant): Direct knowledge selection

Given a user question and the complete knowledge index for Nablarch 6,
identify the sections that are likely to answer the question.

Output ONLY the JSON defined by the schema — no tools, no prose, no markdown.

## How to read the index

Each entry starts with a header line, then one indented line per section:

```
[file_id] Page title
  sid:section title — keyword / keyword / ...
  sid:section title
  ...
```

- `file_id` is the stable identifier of a knowledge file.
- Each `sid` (e.g., `s1`, `s2`) is a section inside that file.
- The `— keyword / ...` suffix, when present, lists extra terms that
  appear in the section body. Treat them as equal-weight hints alongside
  the section title — a section can match because of a keyword even when
  its title does not mention the concept.
- A keyword match counts the same as a title match, both for picking a
  section and for triggering the foundational-section rule below.
- The separator between section title and keywords is an em-dash (`—`),
  not a hyphen.
- A file with no sections has only the header line.

## Selection task — recall-first

Return a list of `file_id|sid` strings that point to the sections that
could contain the answer.

**Your job is to maximize recall, not precision.** A downstream stage
will read the section bodies and drop the irrelevant ones. Missing a
required section is far worse than including an extra on-scope section.

- Pick up to 10 sections. Err on the side of including a plausibly
  relevant section rather than dropping it.
- Always emit the full `file_id|sid` form. Do NOT emit bare `file_id`.
  If a file has no sections in the index, do not select it.
- Each `file_id|sid` must appear at most once.
- When you identify a file that matches the question topic, do not pick
  only the section whose title or keyword most directly restates the
  question. **Also include that file's foundational sections** — the
  overview / concept / class-name section (usually `s1`) and any section
  whose title signals constraints, placement, or prerequisites
  (e.g. "制約", "前提", "ハンドラ配置"). These sections carry the
  core facts even when their titles look generic.
  - Apply this rule only to files you already picked a match (via title
    or keyword) from. Do not add foundational sections from adjacent
    files you did not otherwise select.
  - Cap: at most 2 foundational sections per file (typically `s1` plus
    one structural section). Do not pull 3+ structural sections from a
    single file at the expense of crowding out another relevant file.
  - If a keyword-matched section you picked already carries the specific
    fact the question asks about, you do not need to add an additional
    foundational section from the same file just to satisfy the rule.
- **Cap precedence** when you hit the 10-item limit: drop the
  weakest literal-match section before dropping any file's `s1`. The
  foundational section is what tells the downstream reader whether the
  file is truly on-topic.
- When multiple files look equally relevant, include sections from
  each of them rather than picking one file.
- The `feature_details` page of a processing pattern often has a
  per-concern section table of contents. Those sections frequently
  serve as the correct entry-point for pattern-specific questions.
- If the question covers multiple distinct topics, include 1–3 sections
  per topic (still within the 10-item cap).
- If no section in the index plausibly answers the question (e.g., a
  Spring Boot configuration question, a general Java question), return
  `{"selections": []}`. Do NOT return a best-guess consolation pick —
  an empty list is the correct answer for out-of-scope questions.

### Why foundational sections matter

Section titles in this index often describe **document structure**
("制約", "ハンドラクラス名", "前提") rather than content. The body of
`s3` titled "制約" typically contains the handler's placement rules
against other handlers — information that is essential for any
question about that handler's behavior or configuration. Do not skip
such sections just because their titles look abstract.

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
→ `{"selections": ["nablarch-batch-architecture|s1", "nablarch-batch-architecture|s3", "nablarch-batch-feature_details|s1", "nablarch-batch-feature_details|s2"]}`

Question: "画面の入力値チェックの書き方を知りたい"
→ `{"selections": ["web-application-feature_details|s2", "libraries-bean_validation|s1", "libraries-bean_validation|s8", "libraries-bean_validation|s13"]}`
(include foundational `s1` plus the specific sections whose titles name the concern.)

Question: "Nablarch のトランザクション境界はどこで決まる？"
→ `{"selections": ["handlers-transaction_management_handler|s1", "handlers-transaction_management_handler|s3", "handlers-transaction_management_handler|s4"]}`
(Even when one section title looks like the direct answer, pull in
s1 (handler overview — contains the actual boundary definition) and
s3 "制約" (placement rule) from the same file.)

Question: "DbConnectionManagementHandler との並び順は？"
→ `{"selections": ["handlers-transaction_management_handler|s1", "handlers-transaction_management_handler|s3"]}`
(`s3`'s keyword `DbConnectionManagementHandler` matches even though its title is just "制約". A keyword match counts the same as a title match.)

Question: "Spring Boot の設定ファイルはどこに置く？"
→ `{"selections": []}`

## Index

{{index}}

## Question

{{question}}

## Output

Return exactly one JSON object matching the schema. The only key is
`selections`. No code fences, no commentary. The response must start with
`{` and end with `}`.
