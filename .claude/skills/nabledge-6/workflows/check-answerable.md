# Check Answerable Workflow

Judges whether the provided sections contain sufficient information to answer the question, without generating an answer.

## Input

- `{question}`: User's question (natural Japanese text).
- `{sections}`: Array of section pointers in `{"file": "...", "section_id": "...", "relevance": "..."}` format.

## Output

```json
{"result": "OK"}
```

or

```json
{"result": "NG"}
```

---

## Step 1: Check for empty sections

If `{sections}` is empty, return `{"result": "NG"}` immediately.

---

## Step 2: Read section content

From `{sections}`, select up to 10 sections to read:
1. All `high` sections first
2. Then `partial` sections to fill remaining slots

Build the argument list: for each selected section, `"{file}:{section_id}"`.

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

Save the output as `sections_content`.

---

## Step 3: Judge answerability

Read `sections_content` and `{question}`.

Judge: Do the sections contain a concrete implementation method, required configuration, or explicit specification that directly answers the question?

**Return `{"result": "OK"}`** if the sections contain sufficient information to write a complete, supported answer to the question.

**Return `{"result": "NG"}`** if:
- The sections are not relevant to the question
- The sections mention the topic but lack the concrete detail needed for a complete answer
- The sections contain only conceptual background without actionable specifics

Do not generate an answer — only judge sufficiency.
