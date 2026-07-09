# add-md-section-links — design notes

Not read at runtime — for whoever maintains the design and needs to judge whether a decision is still
right when requirements change.

## 1. Background & Goals

### 1.1 What is the goal?

Make cited knowledge sections navigable from skill output. Users currently see `参照: libraries-database.json:s29` and must manually open the file and scroll to the section; the goal is to add enough information that users can open the file and find the section immediately.

### 1.2 What goes wrong without this?

Source verification requires extra steps: user must open the file independently, locate the section (whose name they don't know from a bare `:s29` ID), and confirm it supports the cited claim. This friction discourages verification.

### 1.3 What does reaching it require?

1. **Path mapping**: `knowledge/path/file.json` → `docs/path/file.md` (already established in `prefill-template.sh`; same rule applies here).
2. **QA change**: The `参照:` instruction must emit the docs file path (plain text, VS Code auto-detects as clickable) plus the section title as indented text below.
3. **code-analysis change**: The `**詳細**:` instruction must emit a Markdown link to the docs file plus the section title as indented text below.
4. **Cross-version apply**: Same instruction change to all 5 versions.

### 1.4 What is out of scope?

- Anchors (`#section-anchor`): tested in VS Code — `path.md#anchor` breaks VS Code path auto-detection in the terminal, and VS Code editor does not scroll to the anchor even from a preview link. Anchors are not used.
- Changing the knowledge JSON or docs MD files (RBKC-generated, never edited manually).
- Changing `prefill-template.sh` or `read-sections.sh` scripts; the change is purely in workflow instruction text.
- `{{knowledge_base_links}}` in code-analysis template (file-level links in the References section); only `**詳細**:` in Nablarch usage is updated.

## 2. Assumptions & Constraints

### 2.1 What do we take as true?

- Section titles in JSON (`sections[].title`) match the heading text in the corresponding MD file exactly — confirmed by sampling `libraries-database.json`/`.md`.
- VS Code integrated terminal auto-detects bare file paths as clickable links (confirmed via nabledge/nabledge#18). A path ending in `.md` opens the file. A path ending in `.md#anchor` breaks detection — anchor is not used.
- code-analysis output resides in `.nabledge/YYYYMMDD/`; relative path prefix for docs links is already `../../` (established in `prefill-template.sh`).
- The `read-sections.sh` output header format `# Page title > Section title` provides both page title and section title for each read section.

### 2.2 What binds the solution?

- Workflow files are Markdown prompt text interpreted by Claude at runtime; no compiled code.
- Cross-version rule: the change must be identical across all 5 versions (path substitution only).
- RBKC-generated files are off-limits.

## 3. Design overview

### 3.1 What is the core idea, and why does it solve the problem?

The section title and page title are already present in `sections_content` (emitted by `read-sections.sh` as `# Page > Section`). The docs path is deterministic from the JSON path. So the workflow can emit a plain-text path (QA) or Markdown link (code-analysis) plus the section title as readable text — no anchor computation needed, no new data fetching.

### 3.2 What are the pieces, and what is each responsible for?

| Piece | Responsibility |
|-------|---------------|
| QA `qa.md` — `参照:` instruction | Emit page title, plain docs path, indented section title(s) per cited file |
| code-analysis `code-analysis.md` — Step 3 tracking | After reading sections, carry `{file, page_title, section_title}` as `sections_metadata` |
| code-analysis `template-guide.md` — `{{nablarch_usage}}` 詳細 | Specify `[page title](../../docs/path.md)` link + indented section title(s) |
| Path mapping (inline, both workflows) | `knowledge/path/file.json` → `docs/path/file.md`; for QA: prepend `.claude/skills/nabledge-6/docs/`; for code-analysis: use `../../.claude/skills/nabledge-6/docs/` |

### 3.3 How does work move?

**QA flow**:
1. `read-sections.sh` returns `# Page > Section` header + content per section.
2. Step 5 generates answer, citing sections.
3. Step 5 `参照:` block: group cited sections by file; for each file emit page title, plain docs path, then indented section title(s).

**code-analysis flow**:
1. Step 3 reads sections via `read-sections.sh`; extract `{file, page_title, section_title}` from each `# Page > Section` header as `sections_metadata`.
2. Step 4.4 `{{nablarch_usage}}`: for each Nablarch component's knowledge section(s), look up in `sections_metadata`; emit `**詳細**: [page title](../../docs/path.md)` link + indented section title(s).

## 4. Detailed design

### 4.1 Path mapping — what does it guarantee, and how is a breach caught?

**Guarantee**: Given a knowledge JSON path (relative to `knowledge/`), produces the corresponding docs MD path.

**Rule**:
- QA (repo-root-relative): prepend `.claude/skills/nabledge-6/docs/`, change `.json` → `.md`
  - `component/libraries/libraries-database.json` → `.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md`
- code-analysis (relative from `.nabledge/YYYYMMDD/`): prepend `../../.claude/skills/nabledge-6/docs/`, change `.json` → `.md`
  - `component/libraries/libraries-database.json` → `../../.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md`

**Breach detection**: A wrong path means VS Code's quick-open finds no file. Acceptance criterion "links are reachable" catches this.

### 4.2 QA `参照:` format — what does it guarantee, and how is a breach caught?

**Guarantee**: Each cited file is listed with its page title, a clickable plain path, and indented section title(s) — users can open the file and find the section by name.

**Format**:
```
参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  現在のトランザクションとは異なるトランザクションでSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  現在のトランザクションとは異なるトランザクションで実行する
```

- Page title: from `# Page > Section` header (text before `>`)
- Path: plain text, repo-root-relative — VS Code auto-detects as clickable
- Section title(s): indented two spaces, one line each — used to locate the section after the file opens

**Breach detection**: Wrong path → VS Code finds no file. Wrong section title → user cannot locate section. Both are caught by manual verification during the benchmark run.

### 4.3 code-analysis `**詳細**:` format — what does it guarantee, and how is a breach caught?

**Guarantee**: The `**詳細**:` field in each Nablarch usage entry provides a clickable link to the knowledge MD file plus the section title(s) used, so users can open the file and find the relevant section.

**Format** (in `.nabledge/YYYYMMDD/` output file):
```markdown
**詳細**: [ユニバーサルDAO](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md)
  楽観的ロックを行う
```

When multiple sections from the same file are cited:
```markdown
**詳細**: [ユニバーサルDAO](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md)
  楽観的ロックを行う
  現在のトランザクションとは異なるトランザクションで実行する
```

- Markdown link text = page title (from `sections_metadata`); href = `../../docs/path.md` (no `#anchor`)
- Section title(s): indented two spaces below the link line

**Breach detection**: Wrong path → link opens wrong file (or 404). Wrong section title → user cannot locate section. Caught by verification in the benchmark run.

### 4.4 Output sample images

#### QA workflow — `参照:` block

**Before:**
```
参照: component/libraries/libraries-database.json:s29, component/libraries/libraries-universal-dao.json:s20
```

**After:**
```
参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  現在のトランザクションとは異なるトランザクションでSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  現在のトランザクションとは異なるトランザクションで実行する
```

VS Code terminal: clicking the path opens the file via quick-open. User searches for the section title with Ctrl+F.

#### code-analysis workflow — `**詳細**:` field

**Before:**
```markdown
**詳細**: [Libraries Universal_dao](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal_dao.md)
```

**After:**
```markdown
**詳細**: [ユニバーサルDAO](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md)
  楽観的ロックを行う
```

VS Code editor preview: clicking the link opens the file. User searches for the section title.

## 5. Alternatives considered

### 5.1 Why this shape, and not another?

**Alternative A — `path.md#anchor` with GFM anchor generation**: Tested in VS Code — `#anchor` suffix breaks path auto-detection in the terminal (VS Code quick-open does not strip the anchor). In the editor preview, clicking `[text](path.md#anchor)` opens the file but does not scroll to the section. Anchors give no functional benefit in the current tooling and actively harm terminal path detection.

**Alternative B — Markdown link format `[title](path)` in QA output**: QA output is console text; VS Code renders Markdown links only in the editor, not in the terminal. A bare path is more reliable for terminal click-through than a Markdown link that won't render.

**Alternative C — File-level link only, no section title**: Would require users to scroll through the entire file to find the relevant section. The section title adds the navigational value the feature targets.

### 5.2 What did we trade away?

- No one-click section jump: users must open the file and search. This is unavoidable given VS Code's anchor handling; the section title as text is the best available substitute.
- code-analysis does not track which specific sections were cited per Nablarch component (the mapping is inferred by the workflow at output time); a mismatch could list a section title that is not the most relevant one. Mitigated by the benchmark verification step.
