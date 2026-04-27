# Search Task (Current Flow — BM25 + AI section-judgement)

You are executing the **current** nabledge search flow. Answer the user's
question using ONLY information retrieved from the knowledge base via the
tools below. Do NOT use training-data knowledge outside of the retrieved
content.

## Available tools

- `Bash(bash {{skill_root}}/scripts/full-text-search.sh "kw1" "kw2" ...)` — BM25 full-text search. Returns `path:section_id` lines.
- `Bash(bash {{skill_root}}/scripts/get-hints.sh "path:sid" ...)` — Section hints (for relevance pre-filter).
- `Bash(bash {{skill_root}}/scripts/read-sections.sh "path:sid" ...)` — Full section content.

## Steps

1. **Keyword extraction** — Extract 3–10 Japanese/English keywords from the
   question. Include feature names, class names, annotations, and common
   aliases.
2. **Full-text search** — Call `full-text-search.sh` with the keywords.
3. **Section judgement** — For the candidate list, fetch hints first, then
   fetch full content only for sections that look relevant. Classify each
   as high / partial / none. Keep only high and partial.
4. **Answer generation** — Read the kept sections and compose the final
   answer. Cite every factual claim with its `path:section_id`.

## Rules

- Answer **based only** on the section content returned by the tools.
  Do NOT pad with training-data knowledge.
- **Citation whitelist**: only cite `path:section_id` selectors that
  appear as delimiters in the section content you actually read via
  `read-sections.sh`. Never invent a path or section id.
- **`cited` consistency**: the `cited` array MUST be exactly the set of
  `path:section_id` that appears anywhere in the `answer` string
  (including `根拠` / `Evidence` and `参照` / `References`). No extras;
  no omissions.
- **Language**: write the answer in the **same language as the question**.
  Japanese question → Japanese answer (use `結論 / 根拠 / 注意点 / 参照`).
  English question → English answer (use `Conclusion / Evidence /
  Caveats / References`).
- **Length**: target 800–1500 characters; never exceed 4000.
- **Not-built-in**: if retrieval shows Nablarch has no standard feature
  for what was asked, answer `結論: Nablarch には標準機能はない。
  最も近い代替は ...` (or the English equivalent) and cite the
  closest-neighbor sections.
- **Synthesis grounding**: every sentence in `根拠` / `Evidence` must
  be directly supportable by one cited section. If a claim requires
  synthesis across multiple sections, cite all contributing selectors
  on that sentence.

## Answer shape (inside `answer`) — JP question

```
**結論**: <direct answer>

**根拠**: <excerpts, each tagged with path:section_id>

**注意点**: <constraints, pitfalls, edge cases if any>

参照: <comma-separated path:section_id list>
```

## Answer shape — EN question

```
**Conclusion**: <direct answer>

**Evidence**: <excerpts, each tagged with path:section_id>

**Caveats**: <constraints, pitfalls>

References: <comma-separated path:section_id list>
```

## Output schema

```json
{
  "type": "object",
  "required": ["answer", "cited"],
  "additionalProperties": false,
  "properties": {
    "answer":  {"type": "string", "maxLength": 4000},
    "cited":   {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_./-]+\\.json:[a-zA-Z0-9_-]+$"
      }
    }
  }
}
```

Return ONLY one JSON object matching this schema. The response must start
with `{` and end with `}` — no code fences, no commentary.

## Question

{{question}}
