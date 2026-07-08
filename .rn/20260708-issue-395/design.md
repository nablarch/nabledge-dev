# add-md-section-links — design notes

Not read at runtime — for whoever maintains the design and needs to judge whether a decision is still
right when requirements change.

## 1. Background & Goals

### 1.1 What is the goal?

Make cited knowledge sections navigable from skill output. Users currently see `参照: libraries-database.json:s29` and must manually open the file and scroll; the goal is a clickable Markdown link that lands on the exact section.

### 1.2 What goes wrong without this?

Source verification requires extra steps: user must open the file independently, locate the section by its title, and confirm it supports the cited claim. This friction discourages verification.

### 1.3 What does reaching it require?

1. **Anchor algorithm**: A function from section title → GitHub Markdown anchor string (deterministic, matching GFM spec).
2. **Path mapping**: `knowledge/path/file.json` → `docs/path/file.md` (already established in `prefill-template.sh`; same rule applies here).
3. **QA change**: The `参照:` line instruction must be updated to emit links instead of bare IDs; section titles are already available in `sections_content` (the `read-sections.sh` output includes `# Page > Section` lines).
4. **code-analysis change**: The `**詳細**:` instruction must specify section-level links; this requires the workflow to carry `{file, section_id, title}` from Step 3 (read-sections) into Step 4 (documentation).
5. **Cross-version apply**: Same instruction change to all 5 versions.

### 1.4 What is out of scope?

- Changing the knowledge JSON or docs MD files (RBKC-generated, never edited manually).
- Adding anchor metadata to knowledge JSON; the anchor is computed from the title at link-generation time.
- Changing `prefill-template.sh` or `read-sections.sh` scripts; the change is purely in workflow instruction text.
- `{{knowledge_base_links}}` in code-analysis template (file-level links in the References section); only `**詳細**:` in Nablarch usage is promoted to section-level.

## 2. Assumptions & Constraints

### 2.1 What do we take as true?

- Section titles in JSON (`sections[].title`) match the heading text in the corresponding MD file exactly — confirmed by sampling `libraries-database.json`/`.md` and `biz-samples-0101-PBKDF2PasswordEncryptor.json`/`.md`.
- GFM anchor generation: lowercase → remove `[^\w -]` (keeping CJK, letters, digits, hyphens, underscores, spaces) → spaces→hyphens. Verified empirically: `現在のトランザクションとは異なるトランザクションでSQLを実行する` → `現在のトランザクションとは異なるトランザクションでsqlを実行する`.
- QA output is rendered as Markdown in Claude Code chat, so `[text](path.md#anchor)` links are clickable.
- code-analysis output resides in `.nabledge/YYYYMMDD/`; relative path prefix for docs links is already `../../` (established in `prefill-template.sh`).

### 2.2 What binds the solution?

- Workflow files are Markdown prompt text interpreted by Claude at runtime; no compiled code.
- The anchor algorithm must be expressible as a plain-language instruction Claude can apply at output time, without scripting.
- Cross-version rule: the change must be identical across all 5 versions (path substitution only).
- RBKC-generated files are off-limits.

## 3. Design overview

### 3.1 What is the core idea, and why does it solve the problem?

The section title is already present in `sections_content` (emitted by `read-sections.sh` as `# Page > Section`) and in the JSON's `sections[].title`. Given the title, the docs path can be computed from the JSON path, and the anchor can be computed from the title by GFM rules. So all the information needed for a clickable link is already in scope at output time — no new data fetching is required.

### 3.2 What are the pieces, and what is each responsible for?

| Piece | Responsibility |
|-------|---------------|
| QA `qa.md` — `参照:` instruction | Emit `[title](docs_path#anchor)` for each cited section |
| code-analysis `code-analysis.md` — Step 3 tracking | After reading sections, carry `{file, section_id, title}` as `sections_metadata` |
| code-analysis `template-guide.md` — `{{nablarch_usage}}` 詳細 | Specify `[file title](docs_path.md) > [section title](docs_path.md#anchor)` link format |
| Anchor algorithm (inline, both workflows) | Deterministic title→anchor: lowercase, remove `[^\w -]`, spaces→hyphens |
| Path mapping (inline, both workflows) | `knowledge/path/file.json` → `docs/path/file.md` using `../../` prefix for code-analysis |

### 3.3 How does work move?

**QA flow**:
1. `read-sections.sh` returns `# Page > Section` header + content per section.
2. Step 5 generates answer, citing sections as `file.json:sN`.
3. Step 5 `参照:` line: for each cited section, look up its title from `sections_content`, compute docs path and anchor, emit Markdown link.

**code-analysis flow**:
1. Step 3 reads sections via `read-sections.sh`; result header includes `# Page > Section` — extract `{file, section_id, title}` per section as `sections_metadata`.
2. Step 4.4 `{{nablarch_usage}}`: for each Nablarch component's knowledge section, look up in `sections_metadata` to get title and anchor; emit `**詳細**: [file title](../../docs/path.md) > [section title](../../docs/path.md#anchor)`.

## 4. Detailed design

### 4.1 Anchor algorithm — what does it guarantee, and how is a breach caught?

**Guarantee**: Given a section title string, produces a string identical to the GitHub Markdown heading anchor for a heading with that text.

**Algorithm** (plain language, for workflow instruction):
1. Lowercase all letters (including ASCII letters in CJK-mixed titles, e.g. `SQL` → `sql`).
2. Remove all characters except: CJK unified ideographs, hiragana, katakana, alphanumeric (`a-z0-9`), hyphens (`-`), underscores (`_`), and spaces.
3. Replace each run of one or more spaces with a single hyphen.
4. Strip leading/trailing hyphens.

**Breach detection**: A broken anchor means the link lands at the top of the page rather than the section. The acceptance criterion "links are reachable" catches this — if the anchor is wrong, following the link does not open the correct section.

**Edge cases handled**:
- `（）` parentheses → removed (step 2). Example: `データベースアクセス(JDBCラッパー)` → `データベースアクセスjdbcラッパー` — parentheses and their content are not removed; only the chars `(`, `)` are removed, content stays.
- Mixed CJK+ASCII: `like検索を行う` → `like検索を行う` (no change; all kept).
- Long titles: no truncation; GFM anchors are not truncated.

### 4.2 QA `参照:` link format — what does it guarantee, and how is a breach caught?

**Guarantee**: Each cited section in the `参照:` line is presented as a Markdown link `[section title](docs_path.md#anchor)` pointing to the exact section in the knowledge MD file.

**Format**:
```
参照: [セクションタイトル](../../.claude/skills/nabledge-6/docs/category/file.md#anchor), [...]
```

Wait — QA output is chat text, not a file in `.nabledge/`. The path must be relative to the **repo root** or use an absolute-like path that is clickable in Claude Code chat. In Claude Code chat, relative paths in Markdown links are resolved relative to the repository root. So the path should be `.claude/skills/nabledge-6/docs/path/file.md#anchor` (no `../../` prefix).

**Path computation** (from `file.json:sN` in `sections_content`):
- Input: `component/libraries/libraries-database.json` (relative to `knowledge/`)
- Output: `.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md` (relative to repo root)
- Rule: prepend `.claude/skills/nabledge-6/docs/`, change `.json` → `.md`

**Breach detection**: A wrong path returns 404 (file not found). A wrong anchor lands at page top. Acceptance criterion "links are reachable" covers both.

### 4.3 code-analysis `**詳細**:` link format — what does it guarantee, and how is a breach caught?

**Guarantee**: The `**詳細**:` field in each Nablarch usage entry links to both the knowledge MD file and the specific section used.

**Format** (in `.nabledge/YYYYMMDD/` output file, using `../../` prefix):
```
**詳細**: [ファイルタイトル](../../.claude/skills/nabledge-6/docs/category/file.md) > [セクションタイトル](../../.claude/skills/nabledge-6/docs/category/file.md#anchor)
```

**Section tracking**: After Step 3 (`read-sections.sh`), the output contains lines like:
```
=== component/libraries/libraries-database.json : s29 ===
# データベースアクセス(JDBCラッパー) > 現在のトランザクションとは異なるトランザクションでSQLを実行する
```
The workflow extracts from the `# Page > Section` header: file path, section ID, page title (before `>`), section title (after `>`). This becomes `sections_metadata` used in Step 4.

**Breach detection**: Same as §4.2 — broken path or anchor means the link does not reach the target section.

## 4.4 Output sample images

### QA workflow — `参照:` line

**Before:**
```
参照: component/libraries/libraries-database.json:s29, component/libraries/libraries-universal-dao.json:s20
```

**After:**
```
参照: [現在のトランザクションとは異なるトランザクションでSQLを実行する](.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#現在のトランザクションとは異なるトランザクションでsqlを実行する), [現在のトランザクションとは異なるトランザクションで実行する](.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#現在のトランザクションとは異なるトランザクションで実行する)
```

Path derivation:
- Input: `component/libraries/libraries-database.json:s29`
- File path: `.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md`
- Section title (from `sections_content`): `現在のトランザクションとは異なるトランザクションでSQLを実行する`
- Anchor: `現在のトランザクションとは異なるトランザクションでsqlを実行する`
  (lowercase: SQL → sql; `[^\w -]` stripped: none here; spaces→hyphens: none here)

### code-analysis workflow — `**詳細**:` field in Nablarch usage

**Before:**
```markdown
**詳細**: [データバインド知識ベース](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md)
```

**After:**
```markdown
**詳細**: [データバインド](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md) > [Java Beansオブジェクトの内容をデータファイルに書き込む](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md#java-beansオブジェクトの内容をデータファイルに書き込む)
```

Path derivation (from `sections_metadata` built after Step 3):
- Input from `read-sections.sh` header: `=== component/libraries/libraries-data-bind.json : s8 ===`
- Header line: `# データバインド > Java Beansオブジェクトの内容をデータファイルに書き込む`
- File path: `../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md`
- Page title (before `>`): `データバインド`
- Section title (after `>`): `Java Beansオブジェクトの内容をデータファイルに書き込む`
- Anchor: `java-beansオブジェクトの内容をデータファイルに書き込む`
  (lowercase: Java → java, Beans → beans; `(`, `)` removed; spaces→hyphens)

## 5. Alternatives considered

### 5.1 Why this shape, and not another?

**Alternative A — Add anchor field to knowledge JSON (RBKC change)**: Would store pre-computed anchors in JSON, making link generation trivial. Rejected because: (1) RBKC-generated files are off-limits, (2) anchors can be computed on-the-fly from titles, so the extra field adds complexity without necessity.

**Alternative B — Add a script `resolve-section-link.sh`**: A shell script that takes `file.json:sN` and outputs the Markdown link. Rejected because: the change is in workflow instructions (Markdown text), not in script code — introducing a new script adds infrastructure for a computation Claude can perform inline with a plain-language rule.

**Alternative C — File-level link only for code-analysis (not section-level)**: Would avoid the need to track `sections_metadata`. Rejected by user's explicit choice: section-level links are wanted for code-analysis too.

### 5.2 What did we trade away?

- No compile-time verification of anchor correctness; if a section title contains unusual characters, the anchor may silently differ from GitHub's rendering. Mitigated by empirical testing during the benchmark run.
- code-analysis workflow instruction grows slightly more complex (section tracking step added to Step 3); this is the cost of providing section-level precision.
