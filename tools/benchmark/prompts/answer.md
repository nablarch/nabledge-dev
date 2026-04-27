# Stage 3 AI-3: Final Answer

Answer the user's question using **only** information from the provided
section content. Output ONLY the JSON defined by the schema — no tools,
no prose outside JSON.

## Rules

- **Use only what you need** — the supplied sections are a retrieval
  *candidate set*, not a required coverage list. Use a section only
  if it contributes a fact that the answer needs. Skip sections that
  are on an adjacent topic.

  Skip a section when ANY of these apply:
    - It covers a different feature that merely shares a keyword
      (example: the question asks about Bean Validation + DB access;
      a section on SQL injection defense shares "DB" but is a
      different concern — skip).
    - It is background/overview material that the question doesn't
      ask about.
    - The answer is already complete without it and it would only
      add "related context".

  Do NOT skip a section just because it alone doesn't fully answer
  the question. Cross-section synthesis is expected — if section A
  states the mechanism and section B states a constraint on it, and
  both are needed for the 結論, cite both. "Directly answer" means
  **on-scope**, not self-sufficient.

  Prefer fewer citations when the answer is complete. But prefer an
  extra on-scope citation over dropping a fact the question actually
  asks for — a missing required fact is worse than an extra on-scope
  citation.
- Answer **based only** on the supplied section content. Do NOT pad with
  training-data knowledge that is not in the sections. Cite every
  factual claim.
- **Citation whitelist**: only cite `path:section_id` selectors that
  appear as delimiters in the supplied section content. Never invent a
  path or section id.
- **`cited` consistency**: the `cited` array MUST be exactly the set of
  `path:section_id` that appears anywhere in the `answer` string
  (including `根拠` / `Evidence` and `参照` / `References`). No extras;
  no omissions.
- **Language**: write the answer in the **same language as the question**.
  Japanese question → Japanese answer (use `結論 / 根拠 / 注意点 / 参照`).
  English question → English answer (use `Conclusion / Evidence /
  Caveats / References`).
- **Length**: target 800–1500 characters; never exceed 4000.
- **Not-built-in**: if the sections show Nablarch has no standard
  feature for what was asked, answer `結論: Nablarch には標準機能はない。
  最も近い代替は ...` (or the English equivalent) and cite the
  closest-neighbor sections.
- **Synthesis grounding**: every sentence in `根拠` / `Evidence` must
  be directly supportable by one cited section. If a claim requires
  synthesis across multiple sections, cite all contributing selectors
  on that sentence.

## Answer shape (inside `answer`) — JP question

```
**結論**: <direct answer>

**根拠**: <code/config/specification excerpts, each followed by the path:section_id it came from>
(Cite only sections that directly support the 結論. Do NOT cite a
section merely to demonstrate topic coverage or add "related context".)

**注意点**: <constraints, pitfalls, edge cases if any — only if present
in the sections you actually used>

参照: <comma-separated path:section_id list — matches the sections
cited above>
```

## Answer shape — EN question

```
**Conclusion**: <direct answer>

**Evidence**: <excerpts, each tagged with path:section_id>
(Cite only sections that directly support the Conclusion. Do NOT cite
a section merely to demonstrate topic coverage.)

**Caveats**: <constraints, pitfalls — only if present in the sections
you actually used>

References: <comma-separated path:section_id list — matches the sections
cited above>
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

## Question

{{question}}

## Section content

{{sections_text}}
