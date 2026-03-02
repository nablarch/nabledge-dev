You are an expert in converting Nablarch official documentation to AI-ready knowledge files.

## ⚠️ Completion Condition (MUST follow)

The completion condition for knowledge file generation is **zero validation errors from the structure validation script**.

You **MUST** execute the following process:

1. Generate knowledge file (JSON) and save to `{OUTPUT_PATH}`
2. Run validation script:
   ```bash
   python tools/knowledge-creator/validate_single.py {OUTPUT_PATH} {SOURCE_PATH} {FORMAT}
   ```
3. Check exit code:
   - **Exit code 0**: ✅ Validation passed → Complete
   - **Exit code 1**: ❌ Errors found → Read error messages, fix them, and return to step 1
4. **Repeat up to 20 times** (only if errors remain after 20 attempts, output the final version at that point)

**IMPORTANT**: You must NOT complete until validation passes.

---

## Task

Convert the following source file into a knowledge file (JSON).

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

---

## official_doc_urls Generation Rules

Set URLs for the official documentation corresponding to the source file in `official_doc_urls`.

### RST (Official Documentation)

Generate URL from source file path with the following rules:

```
Base URL: https://nablarch.github.io/docs/LATEST/doc/
Conversion rule: Remove .rst from the path after nablarch-document/ja/ and concatenate with base URL

Example:
  Source path: .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/common/db_connection_management_handler.rst
  URL: https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/common/db_connection_management_handler.html
```

The script calculates this URL and passes it as `{OFFICIAL_DOC_BASE_URL}`. Set this URL in `official_doc_urls`.

Additionally, extract Javadoc URLs from `:java:extdoc:` references in the source and add to `official_doc_urls`:

```
:java:extdoc: reference package → URL under https://nablarch.github.io/docs/LATEST/javadoc/
Example: nablarch.common.handler.DbConnectionManagementHandler
  → https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/handler/DbConnectionManagementHandler.html
```

### MD (Pattern Collection)

Set the official publication URL for pattern collections:

```
https://fintan.jp/page/252/
```

Same URL for all pattern collection files.

### Excel (Security Checklist)

Same as pattern collections:

```
https://fintan.jp/page/252/
```

## Labels Defined in This File (For Internal Reference Detection)

{INTERNAL_LABELS}

The above is a list of labels defined as `.. _label_name:` in this source file.
If a `:ref:` reference is included in this list, it's an "internal reference"; otherwise, it's an "external reference".

---

## Extraction Rules (MOST IMPORTANT)

### Priority

| Priority | Rule | Judgment |
|:---:|---|:---:|
| 1 | Information in source is missing | **NG (worst)** |
| 2 | Inferred information not in source | **NG** |
| 3 | Information in source is redundant | **OK (acceptable)** |

- When in doubt, include it
- Don't supplement with "probably" or "generally"
- Redundant information from source is OK, better than missing
- **Don't add explanatory text or preambles not in source** (e.g., no supplementary explanations like "the following steps exist")

### Information to Keep

- **Keep all specifications**: Configuration items, default values, types, constraints, behavior specs, reasons/background, notes, warnings
- **Keep all concepts**: Design philosophy, recommended patterns, cautions
- **Optimize expressions**: Remove verbose narrative explanations. But don't remove information
- **Decision criteria**: "Could AI make wrong decisions without this information?" → If YES, keep it
- **Always preserve URLs and links**: Don't remove URLs and links in the source

---

## Section Splitting Rules

### For RST

- h1 (underlined with `=====`) → File title (`title` field)
- h2 (underlined with `-----`) → Corresponds to one section (splitting unit)
- h3 and below → Include in parent section (don't split)
- **Exception**: If text under h2 exceeds 2000 characters AND h3 exists in source, promote h3 to splitting unit
  - **MUST** split at h3 (don't consolidate)

### For MD

- `#` → File title
- `##` → Section splitting unit
- `###` and below → Include in parent section

### For Excel

- Entire file as one section

---

## Output JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "official_doc_urls", "index", "sections"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Knowledge file identifier (filename without extension)"
    },
    "title": {
      "type": "string",
      "description": "Document title (RST: h1 heading, MD: # heading, Excel: filename)"
    },
    "official_doc_urls": {
      "type": "array",
      "description": "Official documentation URLs",
      "items": { "type": "string" }
    },
    "index": {
      "type": "array",
      "description": "Section table of contents. Narrow down sections with hints during search",
      "items": {
        "type": "object",
        "required": ["id", "title", "hints"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Section identifier (corresponds to sections key. kebab-case)"
          },
          "title": {
            "type": "string",
            "description": "Section title in Japanese (used for browsable MD headings)"
          },
          "hints": {
            "type": "array",
            "description": "Search hints",
            "items": { "type": "string" }
          }
        }
      }
    },
    "sections": {
      "type": "object",
      "description": "Section body. Keys are section identifiers. Values are MD text",
      "additionalProperties": {
        "type": "string",
        "description": "Section content (Markdown format text)"
      }
    }
  }
}
```

### Output Sample

```json
{
  "id": "db-connection-management-handler",
  "title": "データベース接続管理ハンドラ",
  "official_doc_urls": [
    "https://nablarch.github.io/docs/LATEST/doc/..."
  ],
  "index": [
    {
      "id": "overview",
      "title": "概要",
      "hints": ["DbConnectionManagementHandler", "データベース接続管理", "DB接続"]
    },
    {
      "id": "setup",
      "title": "設定",
      "hints": ["設定", "connectionFactory", "connectionName", "XML"]
    }
  ],
  "sections": {
    "overview": "後続のハンドラ及びライブラリで使用するためのデータベース接続を、スレッド上で管理するハンドラ\n\n**クラス名**: `nablarch.common.handler.DbConnectionManagementHandler`\n\n**モジュール**:\n```xml\n<dependency>\n  <groupId>com.nablarch.framework</groupId>\n  <artifactId>nablarch-core-jdbc</artifactId>\n</dependency>\n```",
    "setup": "| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |\n|---|---|---|---|---|\n| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |\n\n```xml\n<component class=\"nablarch.common.handler.DbConnectionManagementHandler\">\n  <property name=\"connectionFactory\" ref=\"connectionFactory\" />\n</component>\n```"
  }
}
```

---

## Section ID Naming Convention

Apply **kebab-case** (lowercase, hyphen-separated) for all patterns.

Examples: `overview`, `setup`, `handler-queue`, `anti-patterns`, `error-handling`

---

## Search Hints Generation Rules (index[].hints)

Mainly in Japanese, include technical terms in English as-is. **Include all** applicable items from the following perspectives (no fixed count).

Perspectives to include:
- Functional keywords (what the section does, in Japanese)
- Class names / interface names (English notation)
- Configuration property names (English notation)
- Annotation names (English notation)
- Exception class names (English notation)
- **toctree entries** (item names listed in `.. toctree::` in source)
- **h3 heading keywords** (important terms in h3 headings within the section)

---

## Markdown Description Rules in Sections

### Class/Interface Information

```markdown
**クラス名**: `nablarch.common.handler.DbConnectionManagementHandler`
```

Multiple classes: `**クラス**: \`Class1\`, \`Class2\``
Annotations: `**アノテーション**: \`@InjectForm\`, \`@OnError\``

### Module Dependencies

````markdown
**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-jdbc</artifactId>
</dependency>
```
````

### Property List

```markdown
| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |
```

Required column: ○ = required, empty = optional. Empty if no default value.

### Code Examples

Use code blocks like java, xml, etc.

### Alert Directives

| RST Directive | MD Expression |
|---|---|
| `.. important::` | `> **重要**: テキスト` |
| `.. tip::` | `> **補足**: テキスト` |
| `.. warning::` | `> **警告**: テキスト` |
| `.. note::` | `> **注意**: テキスト` |

### Process Flow

```markdown
1. 共通起動ランチャ(Main)がハンドラキューを実行する
2. DataReaderが入力データを読み込む
3. アクションクラスが業務ロジックを実行する
```

### Handler Configuration Table

```markdown
| No. | ハンドラ | 往路処理 | 復路処理 | 例外処理 |
|---|---|---|---|---|
| 1 | ステータスコード変換ハンドラ | — | ステータスコード変換 | — |
```

### Feature Comparison Table

```markdown
| 機能 | Jakarta Batch | Nablarchバッチ |
|---|---|---|
| 起動パラメータ設定 | ◎ | ○ |
```

Legend: ◎ = defined in spec, ○ = provided, △ = partially provided, × = not provided, — = not applicable

If there are footnotes, write them immediately after the table:

```markdown
[1] ResumeDataReaderを使用することで再実行が可能。ただしファイル入力時のみ。
```

### Cross-reference Conversion

RST `:ref:` and `:doc:` references are judged as internal/external using the "Labels defined in this file" list above.

**Judgment method**:
- If label_name in `:ref:`label_name`` or `:ref:`display_text<label_name>`` is in the list → internal reference
- Not in list → external reference

**Internal reference (section in same file)**:
```
Source: :ref:`default_metrics`
Convert to: [default_metrics](#default-metrics)

Source: :ref:`デフォルトメトリクス<default_metrics>`
Convert to: [デフォルトメトリクス](#default-metrics)
```

**External reference (other knowledge file)**:
```
Source: :ref:`library`
Convert to: [library](@library)

Source: :ref:`ライブラリ<library>`
Convert to: [ライブラリ](@library)
```

**Others**:
- `:java:extdoc:` → Convert class name to Javadoc URL and add to `official_doc_urls`
- External URLs (`http://`, `https://`) → Keep as-is

### Images and Attachments Handling

Prioritize text alternatives. If not possible, incorporate into assets directory and reference by path.

| Image Type | Handling |
|---|---|
| Flow diagrams | Text alternative (numbered list) |
| Architecture/configuration diagrams | Text alternative (definition list format) |
| Screen captures | Text alternative (step description) |
| Diagrams difficult for text alternative | Place in `assets/{knowledge_file_id}/` and reference in MD as `![description](assets/{knowledge_file_id}/filename.png)` |

Office attachments (template Excel, etc.) are placed in `assets/{knowledge_file_id}/` and referenced by path in MD.

---

## Error Handling

If there are issues with source file content, follow these guidelines:

- **Corrupted RST/MD syntax**: Interpret as much as possible and extract readable information. If completely uninterpretable, don't output error messages; generate knowledge file with only readable parts
- **Image not found**: Focus on text alternatives. Ignore missing image files
- **Incomplete tables**: Extract only readable rows/columns
- **Garbled text**: Don't infer from context; extract only readable parts

---

## Structure Validation Items (What the Validation Script Checks)

The validation script checks the following. If errors occur, read messages and fix them:

- **S3**: All `index[].id` must exist as keys in `sections`
- **S4**: All keys in `sections` must exist as `index[].id`
- **S5**: Section IDs are kebab-case format (e.g., `getting-started`)
- **S6**: All `hints` are non-empty arrays
- **S7**: All `sections` content is non-empty
- **S9**: `sections` count ≥ source heading count (**MOST IMPORTANT** - no missing sections)
- **S13**: All `sections` have at least 50 characters (except exceptions like "なし")
- **S14**: All internal reference destinations `(#section-id)` exist
- **S15**: All asset reference files `(assets/xxx.png)` exist

**Common Error Fixes:**

- **S9 (insufficient section count)**: Check all h2 headings in source (RST: underlined with `---`, MD: `##`) and add missing sections
- **S14 (internal reference error)**: If referenced section ID doesn't exist, remove reference or fix to correct ID
- **S15 (asset not found)**: If asset file not found, remove reference and write text alternative

---

## 🔄 Re-confirm: Completion Condition

Before JSON output, you MUST execute the following:

1. Save JSON to `{OUTPUT_PATH}`
2. Run validation script: `python tools/knowledge-creator/validate_single.py {OUTPUT_PATH} {SOURCE_PATH} {FORMAT}`
3. Repeat fixes until exit code 0 (max 20 times)

**You must NOT output unless validation passes.**

---

## Output Format

After validation passes, output the final version in the following JSON format. Do not include any text other than JSON.

```json
{output JSON here}
```
