# Keyword Search Workflow

Keyword-based search using terms.json inverted index. Returns a category > page > section hierarchy of matching sections.

## Input

Keywords (one or more strings)

## Output

```json
[
  {
    "category": "component/libraries",
    "pages": [
      {
        "page_title": "ユニバーサルDAO",
        "sections": [
          {
            "section_id": "component/libraries/libraries-universal-dao.json:s14",
            "section_title": "バッチ実行(一括登録、更新、削除)を行う"
          }
        ]
      }
    ]
  }
]
```

Returns `[]` if no sections match any keyword.

## Process

### Step 1: Execute keyword search

**Tool**: Bash

```bash
bash .claude/skills/nabledge-1.3/scripts/keyword-search.sh "<keyword1>" "<keyword2>" ...
```

Pass all keywords as separate arguments. The script searches terms.json with 3-stage matching per keyword:

1. **Exact match** in terms.json keys
2. **Case-insensitive match** if exact match fails
3. **Partial match** (substring) if case-insensitive fails and keyword is longer than 5 characters

Sections matching any keyword are included (OR search). Sections matching more keywords rank higher.

**Output**: JSON array in category > page > section hierarchy, sorted by:
1. Category max hit-KW count (desc)
2. Category name (asc)
3. Page hit section count (desc)
4. Page title (asc)
5. Section hit-KW count (desc)
6. Section ID (asc)

Top 30 sections returned.

### Step 2: Return results

Return the JSON array from Step 1 as-is.

If the array is empty (`[]`), return `[]`.
