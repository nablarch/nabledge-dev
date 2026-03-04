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
