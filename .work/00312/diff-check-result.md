# Diff Check Result: PR #315 (Issue #312)

**Date**: 2026-04-28
**Branch**: `312-fix-handler-docs-raw-html` vs `origin/main`
**Script**: `.work/00312/diff-check.py`

## Result

**PASS** — All 771 changed files are in expected categories. Counts match. No unexpected content changes.

## Change Categories

| Cat | Files | Description |
|-----|-------|-------------|
| A | 136 | Handler docs (MD) — Handler.js script → Markdown table |
| B | 136 | Handler knowledge JSON — regenerated from A |
| C | 26 | Processing-pattern/library docs (MD) — same Handler.js → Markdown table |
| D | 26 | Processing-pattern/library JSON — regenerated from C |
| E | 248 | Other docs (MD) — Bug 3 blank-line fix + invisible image removal only |
| F | 179 | Other knowledge JSON — regenerated from E |
| G | 20 | Tool/work/index files — RBKC source, tests, design docs, tasks |
| **Total** | **771** | |

## Why Each Category Changed

### Categories A + B: Handler docs (main purpose of this PR)

136 handler documentation files (v1.2/v1.3/v1.4, about 45 handlers per version) contained a ~34KB JavaScript block (`Handler.js`) as raw HTML in an RST `.. raw:: html` directive. This JavaScript rendered a clickable handler flow diagram in the old HTML documentation site, but it is meaningless content in knowledge files (plain text).

This PR converts that JavaScript block to a Markdown table listing the handler's class name, input type, and return type — the same information the JavaScript would have rendered.

**How each handler file changed:**
- The `<script>...</script>` block (about 1,450 lines of JavaScript) was removed
- A Markdown table with class name, input type, and return type was added
- Invisible placeholder images (`handler_structure_bg.png`, `handler_bg.png` with height=0/width=0) were removed (these were CSS spacers with no visible content)
- Blank lines were added after `**bold headings**` for correct Markdown rendering (Bug 3 fix)

The JSON knowledge files in category B were regenerated from these updated docs — no independent change.

### Categories C + D: Processing-pattern / library docs (same Handler.js removal)

26 processing-pattern and library documentation files also embedded the same Handler.js JavaScript block. These files describe how handlers are assembled into processing pipelines, and they embed the handler flow diagram using the same mechanism.

**Files involved (by type):**
- `processing-pattern/nablarch-batch/` — batch processing pipeline descriptions
- `processing-pattern/mom-messaging/` — messaging processing pipeline descriptions
- `processing-pattern/web-application/` — web application pipeline description
- `component/libraries/libraries-messaging-sending-batch.md` — messaging sending batch library
- `component/libraries/libraries-enterprise-messaging*.md` — enterprise messaging libraries (v1.4 only)

The same conversion was applied: JavaScript block removed, Markdown table added.

The JSON knowledge files in category D were regenerated from these updated docs — no independent change.

### Category E: Other docs — Bug 3 blank-line fix and/or invisible image removal only

248 other documentation files changed, but with only two types of whitespace/formatting corrections. These files contain no Handler.js JavaScript blocks.

**Change type 1 — Invisible placeholder image removal (Bug 1 fix):**

Some docs had `handler_structure_bg.png` and `handler_bg.png` at the top, but with `:height: 0` and `:width: 0` CSS properties — they were invisible spacers that produced `![...]()` Markdown image tags pointing to non-existent assets. These tags were removed. No visible content was lost.

Example files affected: `readers-ResumeDataReader.md`, `about-nablarch-architectural-pattern-concept.md`, and similar files that referenced the handler flow diagram even though they are not handler descriptions.

**Change type 2 — Blank line after bold heading (Bug 3 fix):**

RST uses `**bold text**` followed by a newline to create a visual sub-heading. In Markdown, this renders correctly only when a blank line follows the bold text. RBKC now adds that blank line, improving readability in knowledge files.

Example: `**クラス名**\nnablarch.fw.reader.ResumeDataReader` becomes `**クラス名**\n\nnablarch.fw.reader.ResumeDataReader`

The content (class name text) is unchanged — only a blank line is added for correct Markdown rendering.

**Special case — `about-nablarch-link.md`:**

This file contained only invisible placeholder images and nothing else. After removing the images, the file became empty. The corresponding JSON (`about-nablarch-link.json`) now shows `no_knowledge_content: true` and is removed from `index.toon`. The knowledge file count in `index.toon` decreases by 1 per version (321→320 for v1.2, 327→326 for v1.3, 488→487 for v1.4). This is correct behavior — a file with no content should not appear in the knowledge index.

### Category F: Other knowledge JSON — regenerated from E

These JSON files were regenerated from the category E docs. No independent changes.

### Category G: Tool / work / index files

Source code changes (RBKC converter, verify), unit tests, design documentation, and work log files. These are not deployed to end users.

## Verify Result

All 5 versions passed `verify` with 0 FAILs before and after this change (confirmed in Task 3 of `tasks.md`).

## How the Check Was Performed

The diff-check script (`.work/00312/diff-check.py`) classifies every changed file by path pattern and checks that:

1. All 771 files fall into one of the 7 expected categories
2. The count per category matches the expected number exactly
3. No category-E file (non-handler, non-processing-pattern) contains a `<script>` removal (which would indicate unexpected Handler.js removal)

Run: `python3 .work/00312/diff-check.py` from the repository root.
