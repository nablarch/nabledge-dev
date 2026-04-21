# Search Task (New Flow — keyword search + direct answer, no AI judgement)

You are executing the **new** nabledge-6 search flow. Answer the user's question using ONLY information retrieved from the knowledge base.

## Available tools

- `Bash(bash .claude/skills/nabledge-6/scripts/keyword-search.sh "kw1" "kw2" ...)` — keyword search (returns `file|section_id` lines, BM25-scored). Also available under its old name `full-text-search.sh`.
- `Bash(bash .claude/skills/nabledge-6/scripts/read-sections.sh "file:s1" ...)` — read section content

## Steps

1. **Keyword extraction**: extract 3-10 Japanese/English keywords from the question.
2. **Keyword search**: call `keyword-search.sh` (or `full-text-search.sh`) with the keywords. Take the top 10 results.
3. **Answer generation**: read the top sections with `read-sections.sh` and generate an answer in Japanese.

**Do NOT perform an explicit section-relevance judgement step.** The keyword search scoring and the answer generation LLM together implicitly filter relevance.

## Output

Return the structured JSON specified by the schema:
- `keywords`: extracted keywords (array of strings)
- `matched_sections`: sections actually used in the answer as `{file, section_id, relevance}` list (relevance = "high" for cited, "partial" for read-but-not-cited)
- `answer`: Japanese answer (or "この情報は知識ファイルに含まれていません。" if no match)

## Question

{{question}}
