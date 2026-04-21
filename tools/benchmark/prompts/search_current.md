# Search Task (Current Flow — with AI section-judgement)

You are executing the **current** nabledge-6 search flow. Answer the user's question using ONLY information retrieved from the knowledge base.

## Available tools

- `Bash(bash .claude/skills/nabledge-6/scripts/full-text-search.sh "kw1" "kw2" ...)` — full-text search (returns `file|section_id` lines, BM25-scored)
- `Bash(bash .claude/skills/nabledge-6/scripts/get-hints.sh "file:s1" ...)` — get hints (for section-judgement pre-filter)
- `Bash(bash .claude/skills/nabledge-6/scripts/read-sections.sh "file:s1" ...)` — read section content

## Steps

1. **Keyword extraction**: extract 3-10 Japanese/English keywords from the question.
2. **Full-text search**: call `full-text-search.sh` with the keywords.
3. **Section judgement**: for each candidate (up to 20), fetch hints and read content, then judge relevance (high / partial / none). Keep only high/partial.
4. **Answer generation**: read the high/partial sections and generate an answer in Japanese.

## Output

Return the structured JSON specified by the schema:
- `keywords`: extracted keywords (array of strings)
- `matched_sections`: final relevant sections as `{file, section_id, relevance}` list
- `answer`: Japanese answer (or "この情報は知識ファイルに含まれていません。" if no match)

## Question

{{question}}
