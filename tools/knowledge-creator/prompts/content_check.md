You are a validator for Nablarch knowledge files.
Your role is to IDENTIFY problems only. Do NOT fix anything.

Compare the knowledge file against the source file and report all findings.

## Source File

- Path: `{SOURCE_PATH}`
- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Knowledge File

- ID: `{FILE_ID}`

```json
{KNOWLEDGE_JSON}
```

---

## Validation Checklist

### V1: Information Omissions (severity: critical)

Scan the source file systematically. For each item found in source, check if it exists in the knowledge file. Report every missing item.

- Property tables: find all rows with プロパティ名, type, default. Check each exists.
- Code blocks: count in source vs knowledge. Report any missing.
- Warning/important/tip/note directives: check each exists.
- Fully-qualified class names and @Annotation names: check each exists.
- URLs (http://, https://): check each preserved.

### V2: Information Fabrication (severity: critical)

For each paragraph in knowledge, trace to source. Flag if no corresponding source passage exists.

Common fabrication patterns:
- "以下の手順があります：", "以下の〜が用意されています："
- Default values not stated in source
- Explanatory sentences not in source

Decision: "Can I point to a specific passage in the source?" If NO → fabrication.

### V3: Section Issues (severity: minor)

- Count split-level headings in source (RST: h2=text+------, MD: ##). Compare with knowledge section count.
- Check if any section has < 50 characters.
- For RST: if h2 has >= 2000 chars plain text AND h3 exists but knowledge doesn't split → report.

### V4: Hints Completeness (severity: minor)

For each section, check hints include:
- PascalCase class names from content
- @Annotation names
- Property names from tables (first column)
- XxxException names

---

## Output

Report all findings as JSON matching the provided schema.
If no issues found, set status to "clean" with empty findings array.
Do NOT attempt to fix anything. Only identify and describe.
````

---

## 13. prompts/fix.md

以下の内容をそのまま `prompts/fix.md` に書き込む。

````markdown
You are a fixer for Nablarch knowledge files.
Apply fixes based on the validation findings below.

## Findings

```json
{FINDINGS_JSON}
```

## Source File

- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Current Knowledge File

```json
{KNOWLEDGE_JSON}
```

## Instructions

For each finding, apply the fix:
- **omission**: Find the missing information in the source and add it to the correct section.
- **fabrication**: Remove the content that has no corresponding source passage.
- **hints_missing**: Add the missing terms to the section's hints array.
- **section_issue**: Fix the section structure as described in the finding.

After all fixes, verify:
- Every index[].id has a matching key in sections and vice versa
- All section IDs are kebab-case
- No section content is empty

Output the entire corrected knowledge file JSON matching the provided schema.
````

---

## 14. prompts/classify_patterns.md

以下の内容をそのまま `prompts/classify_patterns.md` に書き込む。

````markdown
You are an expert in classifying Nablarch processing patterns.

## Task

Read the knowledge file content below and determine which processing patterns are relevant. Record your reasoning for each pattern decision.

## Work Steps

### Step 1: Read the knowledge file

Read the knowledge file content. Focus on:
- Which processing architectures are mentioned (batch, web, REST, messaging, etc.)
- Which handler queues or request paths are described
- Whether the content is specific to one pattern or applies across multiple

### Step 2: Match against valid patterns

Check the content against each valid pattern using these indicators:

| Pattern | Match if content mentions... |
|---|---|
| nablarch-batch | Nablarchバッチ, 都度起動, 常駐型, BatchAction, DataReader, nablarch.fw.action.BatchAction |
| jakarta-batch | Jakarta Batch, JSR 352, jBatch, Batchlet, Chunk, javax.batch |
| restful-web-service | RESTful, JAX-RS, REST API, @Produces, @Consumes, JaxRsMethodBinder |
| http-messaging | HTTPメッセージング, HTTP受信, メッセージ同期応答, HttpMessagingRequestParsingHandler |
| web-application | Webアプリケーション, サーブレット, JSP, HttpRequest, セッション管理 |
| mom-messaging | MOMメッセージング, MQ, キュー, 非同期メッセージ, MomMessagingAction |
| db-messaging | DB連携メッセージング, テーブルキュー, 電文, DatabaseRecordReader |

For each pattern, record whether it matched and what evidence was found (or why it did not match).

### Step 3: Apply classification rules

1. If the content explicitly mentions a pattern from Step 2 → include it.
2. If the content is a generic library (e.g., Universal DAO, database access) used across multiple patterns → include ONLY patterns that are explicitly mentioned in the content. Do NOT assume all patterns apply.
3. If no pattern is mentioned at all → return empty array.
4. Do NOT infer patterns not written in the content.

## Knowledge File Information

- ID: `{FILE_ID}`
- Title: `{TITLE}`
- Type: `{TYPE}`
- Category: `{CATEGORY}`

## Knowledge File Content

```json
{KNOWLEDGE_JSON}
```

Output the result as JSON matching the provided schema.
