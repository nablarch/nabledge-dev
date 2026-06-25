# Full-Text Search Workflow

BM25 keyword search. Returns matching sections.

## Input

- `{question}`: User's question text.

## Output

```json
{"selected_sections": [...]}
```

or

```json
{"selected_sections": []}
```

Empty array when no BM25 terms found, script returns no hits, or script exits non-zero.

---

## Step 1: Extract BM25 search terms using page title lookup

Use the **Component page title list** below as a translation table to map the question's concepts to Nablarch-specific terms.

**Process**:

1. Read the question and identify its topic (e.g., "バリデーション", "セッション", "DB操作", "ファイル入出力").
2. Scan the page title list and find titles whose terms relate to that topic.
3. From the matching titles, extract BM25 search terms:
   - Use hyphen-separated parts of the title (e.g., `libraries-bean-validation` → `bean-validation`)
   - Or the full filename (e.g., `handlers-SessionStoreHandler` → `SessionStoreHandler`)
4. Also include any concrete identifiers that appear **verbatim** in the question (class name, annotation, method name, configuration file name).

**Do NOT extract** broad words from the question:
- Abstract concepts: `バリデーション`, `トランザクション`, `ハンドラ`, `データ変換`
- General Java terms: `List`, `String`, `Exception`, `try-catch`
- Natural language filler: `使い方`, `方法`, `について`, `実装`

**Examples**:

| Question | Matching titles | BM25 terms to use |
|---|---|---|
| RESTのバリデーション実装を教えて | `libraries-bean-validation`, `handlers-jaxrs-bean-validation-handler` | `bean-validation`, `jaxrs-bean-validation` |
| セッションのストア選択基準を知りたい | `libraries-session-store`, `handlers-SessionStoreHandler` | `session-store`, `SessionStoreHandler` |
| UniversalDaoで検索する方法 | `libraries-universal-dao` (and verbatim: `UniversalDao`) | `universal-dao`, `UniversalDao` |
| ファイル入出力の実装方法 | `libraries-data-format`, `libraries-data-bind`, `libraries-data-io-functional-comparison` | `data-format`, `data-bind` |

**Component page title list**:

```
adapters-adaptors
adapters-doma-adaptor
adapters-jaxrs-adaptor
adapters-jsr310-adaptor
adapters-lettuce-adaptor
adapters-log-adaptor
adapters-mail-sender-freemarker-adaptor
adapters-mail-sender-thymeleaf-adaptor
adapters-mail-sender-velocity-adaptor
adapters-micrometer-adaptor
adapters-redishealthchecker-lettuce-adaptor
adapters-redisstore-lettuce-adaptor
adapters-router-adaptor
adapters-slf4j-adaptor
adapters-web-thymeleaf-adaptor
adapters-webspheremq-adaptor
handlers-HttpErrorHandler
handlers-InjectForm
handlers-ServiceAvailabilityCheckHandler
handlers-SessionStoreHandler
handlers-batch
handlers-body-convert-handler
handlers-common
handlers-cors-preflight-request-handler
handlers-csrf-token-verification-handler
handlers-data-read-handler
handlers-database-connection-management-handler
handlers-dbless-loop-handler
handlers-duplicate-process-check-handler
handlers-file-record-writer-dispose-handler
handlers-forwarding-handler
handlers-global-error-handler
handlers-handlers
handlers-health-check-endpoint-handler
handlers-hot-deploy-handler
handlers-http-access-log-handler
handlers-http-character-encoding-handler
handlers-http-messaging
handlers-http-messaging-error-handler
handlers-http-messaging-request-parsing-handler
handlers-http-messaging-response-building-handler
handlers-http-request-java-package-mapping
handlers-http-response-handler
handlers-http-rewrite-handler
handlers-jaxrs-access-log-handler
handlers-jaxrs-bean-validation-handler
handlers-jaxrs-response-handler
handlers-keitai-access-handler
handlers-loop-handler
handlers-main
handlers-message-reply-handler
handlers-message-resend-handler
handlers-messaging-context-handler
handlers-mom-messaging
handlers-multi-thread-execution-handler
handlers-multipart-handler
handlers-nablarch-tag-handler
handlers-normalize-handler
handlers-on-double-submission
handlers-on-error
handlers-on-errors
handlers-permission-check-handler
handlers-post-resubmit-prevent-handler
handlers-process-resident-handler
handlers-process-stop-handler
handlers-request-handler-entry
handlers-request-path-java-package-mapping
handlers-request-thread-loop-handler
handlers-resource-mapping
handlers-rest
handlers-retry-handler
handlers-secure-handler
handlers-session-concurrent-access-handler
handlers-standalone
handlers-status-code-convert-handler
handlers-thread-context-clear-handler
handlers-thread-context-handler
handlers-transaction-management-handler
handlers-use-token
handlers-web
handlers-web-interceptor
libraries-authorization-permission-check
libraries-bean-util
libraries-bean-validation
libraries-code
libraries-create-example
libraries-data-bind
libraries-data-converter
libraries-data-format
libraries-data-io-functional-comparison
libraries-database
libraries-database-functional-comparison
libraries-database-management
libraries-date
libraries-db-double-submit
libraries-exclusive-control
libraries-failure-log
libraries-file-path-management
libraries-format
libraries-format-definition
libraries-generator
libraries-http-access-log
libraries-http-system-messaging
libraries-jaxrs-access-log
libraries-libraries
libraries-libraries-permission-check
libraries-log
libraries-mail
libraries-message
libraries-messaging-log
libraries-mom-system-messaging
libraries-multi-format-example
libraries-nablarch-validation
libraries-performance-log
libraries-repository
libraries-role-check
libraries-service-availability
libraries-session-store
libraries-sql-log
libraries-stateless-web-app
libraries-static-data-cache
libraries-system-messaging
libraries-tag
libraries-tag-reference
libraries-transaction
libraries-universal-dao
libraries-update-example
libraries-utility
libraries-validation
libraries-validation-functional-comparison
```

Save the extracted terms as `bm25_terms` (list of strings).

**If `bm25_terms` is empty** (no relevant titles found and no verbatim identifiers in the question), return `{"selected_sections": []}` immediately.

---

## Step 2: BM25 search

Execute the BM25 search script with the extracted terms:

```bash
bash scripts/bm25-search.sh <term1> [term2] ...
```

Replace `<term1>`, `[term2]` etc. with the terms from `bm25_terms`.

The script outputs a JSON array. Each element is a section hit with a BM25 score:

```json
[
  {
    "file": "component/libraries/universal-dao.json",
    "section_id": "s3",
    "section_title": "batchUpdateメソッドの使い方",
    "score": 12.45
  },
  ...
]
```

**If the output array is empty** (`[]`), return `{"selected_sections": []}`.

**If the script exits non-zero** for any reason (index build failure, missing dependency, unexpected error), return `{"selected_sections": []}`.

Otherwise, save the array as `bm25_raw`. Take the top 20 entries by score.

Convert to the `selected_sections` format:

```json
[
  {"file": "component/libraries/universal-dao.json", "section_id": "s3", "relevance": "high"}
]
```

All BM25 hits use `"relevance": "high"`.

Return:

```json
{"selected_sections": [...]}
```
