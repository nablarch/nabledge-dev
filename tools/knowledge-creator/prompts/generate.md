You are an expert in converting Nablarch official documentation to AI-ready knowledge files.

## Task

Convert the source file below into a knowledge file (JSON) by following Work Steps 1–7 in order. Record your decisions in the trace log as you go.

## Source File Information

- File ID: `{FILE_ID}`
- Format: `{FORMAT}` (rst/md/xlsx)
- Type: `{TYPE}`
- Category: `{CATEGORY}`
- Output Path: `{OUTPUT_PATH}`
- Assets Directory: `{ASSETS_DIR}`
- Official Doc Base URL: `{OFFICIAL_DOC_BASE_URL}`

## Source File Content

```
{SOURCE_CONTENT}
```

{ASSETS_SECTION}

## Labels Defined in This File

{INTERNAL_LABELS}

The above lists labels defined as `.. _label_name:` in this source file.
A `:ref:` target is "internal" if it appears in this list; otherwise it is "external."

---

## Work Step 1: Identify the title

Read the source and extract the document title.

- RST: The first heading underlined with `=====`
- MD: The first `#` heading
- Excel: Use the filename as title

Set this as the `title` field.

---

## Work Step 2: Build the section list

Scan the source and create a complete list of sections.

### 2-1. Count split-level headings

| Format | Split-level heading | How to count |
|---|---|---|
| RST | h2 | Text line followed by `-----` underline (3+ dashes) |
| MD | ## | Lines starting with `## ` (not `###` or deeper) |
| Excel | (none) | Entire file = 1 section |

### 2-2. Apply h3 promotion rule (RST only)

For each h2 section, estimate the plain text character count. Exclude code blocks (between `.. code-block::` and next unindented line), directive lines (`.. xxx::`), indented directive body, heading underlines, and blank lines.

| Condition | Action |
|---|---|
| h2 plain text ≥ 2000 chars AND h3 headings (`~~~~~` underline) exist in source | Split at h3. Each h3 becomes a separate section. |
| h2 plain text ≥ 2000 chars AND no h3 headings exist | Keep as one section. Do NOT invent sub-sections. |
| h2 plain text < 2000 chars | Keep as one section. Include h3 content inside the parent. |

### 2-3. Assign section IDs

- Use kebab-case: lowercase, hyphen-separated
- Derive from heading text (e.g., "モジュール一覧" → `module-list`)
- Examples: `overview`, `setup`, `handler-queue`, `error-handling`

### Trace log for Step 2

Record in `trace.sections`:
```json
[
  {
    "section_id": "overview",
    "source_heading": "概要",
    "heading_level": "h2",
    "h3_split": false,
    "h3_split_reason": "plain text 800 chars < 2000 threshold"
  }
]
```
For h3-promoted sections, set `"h3_split": true` and explain the reason (char count).

---

## Work Step 3: Extract section content

For each section from Step 2, extract the corresponding source content and convert to Markdown.

### Extraction priority (MOST IMPORTANT)

| Priority | Rule | Judgment |
|:---:|---|:---:|
| 1 | Information in source is missing from output | **NG (worst)** |
| 2 | Information NOT in source is added to output | **NG** |
| 3 | Information from source is included redundantly | **OK (acceptable)** |

When in doubt, **include it**. Redundant is better than missing.

### What to keep — ALL of these

- Specifications: config items, default values, types, constraints, behavior specs, reasons/background
- Warnings and notes: content of `important`, `warning`, `tip`, `note` directives
- Design philosophy, recommended patterns, cautions
- Code examples and configuration examples (every code block in source)
- Class names, interface names, annotation names
- URLs and links: preserve exactly as they appear in source

### Forbidden — Do NOT do any of these

- Do NOT add explanatory preambles not in source (e.g., "以下の手順があります：", "以下の〜が用意されています：")
- Do NOT infer default values, constraints, or behavior not stated in source
- Do NOT add code examples not in source
- Do NOT remove or modify URLs from source
- Do NOT add "一般的には〜" or "通常は〜" style generalizations

Decision criterion: "Can I point to a specific passage in the source for this sentence?" If NO → do not include it.

### Markdown conversion rules

**Classes/interfaces:**
`**クラス名**: \`nablarch.common.handler.DbConnectionManagementHandler\``
Multiple: `**クラス**: \`Class1\`, \`Class2\``
Annotations: `**アノテーション**: \`@InjectForm\`, \`@OnError\``

**Module dependencies:**
```
**モジュール**:
\```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-jdbc</artifactId>
</dependency>
\```
```

**Property tables:**
```
| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |
```
○ = required, empty = optional. Empty default = no default.

**Alert directives:**
| RST directive | Markdown |
|---|---|
| `.. important::` | `> **重要**: text` |
| `.. tip::` | `> **補足**: text` |
| `.. warning::` | `> **警告**: text` |
| `.. note::` | `> **注意**: text` |

**Process flow:** Use numbered list.

**Handler configuration table:**
```
| No. | ハンドラ | 往路処理 | 復路処理 | 例外処理 |
|---|---|---|---|---|
| 1 | ステータスコード変換ハンドラ | — | ステータスコード変換 | — |
```

**Feature comparison table:**
Legend: ◎ = defined in spec, ○ = provided, △ = partially, × = not provided, — = N/A
Footnotes immediately after the table: `[1] text`

**Image handling:**
| Image type | Action |
|---|---|
| Flow diagrams | Text alternative (numbered list) |
| Architecture/configuration diagrams | Text alternative (definition list) |
| Screen captures | Text alternative (step descriptions) |
| Cannot be replaced with text | `![description](assets/{FILE_ID}/filename.png)` |

Office attachments → reference in `assets/{FILE_ID}/`.

---

## Work Step 4: Convert cross-references

Scan each section's content and convert all RST references using this decision flow:

```
For each reference found in source:

1. Is it :java:extdoc:`...` ?
   → Extract the fully-qualified class name.
   → Convert to Javadoc URL: https://nablarch.github.io/docs/LATEST/javadoc/{package/path/ClassName}.html
   → Add this URL to official_doc_urls (collected in Step 6).
   → In section text, keep only the class name as inline code: `ClassName`

2. Is it an external URL (http:// or https://) ?
   → Keep as-is in Markdown link format: [text](url)

3. Is it :ref:`label` or :ref:`display<label>` ?
   → Is `label` in {INTERNAL_LABELS} ?
     YES (internal reference):
       → Convert to: [display_text](#section-id)
       → section-id = the kebab-case ID from Step 2 that this label points to
     NO (external reference):
       → Convert to: [display_text](@label)

4. Is it :doc:`path` or :doc:`display<path>` ?
   → Convert to: [display_text](@knowledge-file-id)
   → knowledge-file-id = the filename portion of path without extension

5. Is it :download:`display<path>` ?
   → If file was extracted to assets: [display](assets/{FILE_ID}/filename)
   → If not extracted: describe the file in text
```

---

## Work Step 5: Generate search hints

For each section, extract hints by following substeps 5-1 through 5-7. Only include items that actually exist in that section.

### 5-1. Class/interface names
Scan for backtick-wrapped text matching `nablarch.xxx.XxxClass` (package-qualified) or PascalCase names (2+ words, e.g., `DbConnectionManagementHandler`). Add each to hints.

### 5-2. Annotation names
Scan for `@AnnotationName` patterns. Add each to hints.

### 5-3. Exception class names
Scan for names ending in `Exception`. Add each to hints.

### 5-4. Property names
From property tables (rows under `| プロパティ名 |` header), extract the first column values. Add each to hints.

### 5-5. Functional keywords (Japanese)
Write 2–5 Japanese keywords describing what this section enables. (e.g., "データベース接続管理", "トランザクション制御", "バリデーション")

### 5-6. Toctree entries
If the source section contains `.. toctree::` items, add each item name to hints.

### 5-7. h3 heading keywords
If this section contains consolidated h3 subsections (not split), extract key terms from h3 headings and add to hints.

---

## Work Step 6: Build official_doc_urls

1. Start with `{OFFICIAL_DOC_BASE_URL}` as the first URL.
2. Collect all Javadoc URLs extracted in Step 4.
3. Combine into a single array, deduplicated, preserving order.

---

## Work Step 7: Assemble and output JSON

Combine all results from Steps 1–6 into the output JSON.


### Output JSON Schema

```json
{
  "type": "object",
  "required": ["knowledge", "trace"],
  "properties": {
    "knowledge": {
      "type": "object",
      "required": ["id", "title", "official_doc_urls", "index", "sections"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Knowledge file identifier. Must equal FILE_ID."
        },
        "title": {
          "type": "string",
          "description": "Document title from Step 1"
        },
        "official_doc_urls": {
          "type": "array",
          "description": "Official documentation URLs from Step 6",
          "items": { "type": "string" }
        },
        "index": {
          "type": "array",
          "description": "Section table of contents with search hints",
          "items": {
            "type": "object",
            "required": ["id", "title", "hints"],
            "properties": {
              "id": { "type": "string" },
              "title": { "type": "string" },
              "hints": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "sections": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        }
      }
    },
    "trace": {
      "type": "object",
      "required": ["sections"],
      "properties": {
        "sections": {
          "type": "array",
          "description": "Section list decisions from Step 2",
          "items": {
            "type": "object",
            "required": ["section_id", "source_heading", "heading_level"],
            "properties": {
              "section_id": { "type": "string" },
              "source_heading": { "type": "string" },
              "heading_level": { "type": "string" },
              "h3_split": { "type": "boolean" },
              "h3_split_reason": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### Final self-checks before output

- [ ] `id` equals `{FILE_ID}`
- [ ] Every `index[].id` has a matching key in `sections` and vice versa
- [ ] All section IDs are kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`)
- [ ] No section content is empty or under 50 characters (unless genuinely "なし")
- [ ] No hints array is empty
- [ ] All internal references `(#section-id)` point to existing section IDs in this file
- [ ] No raw RST markup remains unconverted
- [ ] No information was added that is not in the source
- [ ] All URLs from source are preserved

Output the JSON matching the schema above. No explanation, no markdown fences, no other text.
````

---

## 12. prompts/content_check.md

以下の内容をそのまま `prompts/content_check.md` に書き込む。

````markdown
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
