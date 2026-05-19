# Verify Workflow

Verifies that all Nablarch-specific claims in the answer are supported by knowledge sections.

## Input

- `{answer}`: Answer text to verify
- `{pointer_json}`: Pointer JSON used to generate the answer

## Output

Verified answer text (possibly with a warning appended if hallucination detected)

## Steps

### Step 1: Read section content

**Tool**: Bash

From `{pointer_json}.results`, select sections to read:
- All sections (up to 15)
- `"high"` first, then `"partial"`

If `pointer_json.results` is empty, set `sections_content = ""` and proceed to Step 2.

Otherwise, build the argument list: for each selected result, `"{file}:{section_id}"`.

Run:
```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

### Step 2: Verify claims

**Tool**: Read + In-memory (LLM generation)

Read `assets/verify.md`.

Replace the following variables and call LLM:
- `{answer}` → the answer text
- `{sections_content}` → output from Step 1

Parse the JSON response. Extract:
- `result`: `"PASS"` or `"FAIL"`
- `issues`: list of unsupported claims (empty if PASS)

### Step 3: Return verified answer

**If `result == "PASS"`**: Return the original answer text unchanged.

**If `result == "FAIL"`**: Append a warning to the answer:

```
---
⚠️ 検証: 以下の主張は知識ファイルで裏付けが取れていません:
- {issue.claim}
```

Return the modified answer text.
