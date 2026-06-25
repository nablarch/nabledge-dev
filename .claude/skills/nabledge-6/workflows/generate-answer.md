# Generate Answer Workflow

Reads selected sections and generates a Japanese answer.

## Input

- `{question}`: User's question (natural Japanese text).
- `{processing_type}`: Processing type (one of the 7 processing types, or null).
- `{selected_sections}`: Array of section pointers in `{"file": "...", "section_id": "...", "relevance": "..."}` format.
- `{excluded_claims}`: (Optional) List of claim strings to exclude from the answer. If not provided or empty, no exclusions apply.

## Output

- `answer_text`: Generated answer string.

---

## Step 1: Read section content

From `selected_sections`, select sections to read:
1. All `high` sections first (body sections and Javadoc together)
2. Then `partial` sections to fill remaining slots
3. Maximum 20 entries total, counting body sections and Javadoc together

Build the argument list: for each selected section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

If `selected_sections` is empty, set `sections_content = ""`.

---

## Step 2: Generate answer

If `sections_content` is empty, output immediately:
```
この情報は知識ファイルに含まれていません。
```
and stop.

Otherwise, generate a Japanese answer following the steps below.

1. Read all sections in `sections_content`.
2. If `processing_type` is not null, focus on approaches that match that type.
3. Identify the information that directly answers the question. For any gap in the sections, write "この情報は知識ファイルの対象範囲外です" — do not infer.
4. If `{excluded_claims}` is provided and non-empty, do not include any of the following claims in the answer: `{excluded_claims}`.
5. Write the answer in the format below. Stay within 500 tokens (up to 800 for complex questions).

**Answer format**:

**結論**: Direct answer to the question (1–2 sentences)
- Include specific method names, class names, and approaches
- Do not parrot back the question

**根拠**: Code examples, configuration examples, or spec information that backs the conclusion
- Show code/config examples in code blocks
- Priority: implementation example > configuration example > API spec > conceptual explanation
- If using multiple sections, organize along the implementation flow
- Quote code examples from sections verbatim (do not modify)

**注意点**: Constraints, resource management, common mistakes
- Omit this section if nothing applies

参照: Only sections actually cited in the answer (file.json:sN format, omit category path)

Note: General Java/programming knowledge (try-catch, Bean, getter/setter, etc.) may be used alongside knowledge sections.

Save as `answer_text`.
