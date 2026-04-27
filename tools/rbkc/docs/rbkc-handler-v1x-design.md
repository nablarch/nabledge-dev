# RBKC Handler.js Design — nabledge-1.x

**Issue**: #312  
**Date**: 2026-04-28  
**Status**: Awaiting approval

---

## 1. Problem

### 1-1. Raw HTML Leak (Primary Issue)

Handler RST files in v1.x use three consecutive `.. raw:: html` blocks to render a
visual handler-queue table:

```rst
.. raw:: html
   :file: ../Handler.js          ← Block 1: loads full Handler dictionary (~867 lines)

.. raw:: html

  <script>
  var Context      = 'handler'
    , HandlerQueue = [
        "ThreadContextClearHandler",
        "ThreadContextHandler_main"];
  </script>                       ← Block 2: per-handler config script

.. raw:: html
   :file: ../architectural_pattern/handler_structure.html   ← Block 3: rendering HTML
```

The current `visit_raw` in `rst_ast_visitor.py` calls `normalise_raw_html()` on each
block, which strips `<br/>` and `&nbsp;` but otherwise passes content through verbatim.
Result: all three blocks — including the full Handler.js dictionary (~867 lines of JS) —
are dumped into the generated knowledge file as raw `<script>` content.

**Scope**: 47 files in v1.4, 43 in v1.3, 43 in v1.2 (133 files total).

### 1-2. ハンドラ処理フロー Blank-Line Loss (Secondary Issue)

The "ハンドラ処理フロー" section uses nested RST definition lists to structure
往路処理 / 復路処理 / 例外処理 steps. `visit_definition_list` currently joins all
items with `"\n".join(out)`, producing no blank line between adjacent list items.

This causes sub-items to run together without visual separation, degrading readability.

---

## 2. Knowledge Value of Handler.js Data

Handler.js contains per-handler behavioral descriptions in Japanese:

```js
PermissionCheckHandler: {
  name: "認可制御ハンドラ"
, behavior: {
    inbound:  "スレッドコンテキスト上のリクエストIDおよびユーザIDを参照し..."
  , outbound: "認可に使用した権限情報をスレッドコンテキスト上に設定する"
  , error:    "-"
  }
}
```

The `HandlerQueue` array in Block 2 defines which handlers are shown in the queue
table for this document. The `Context` value (`'handler'`, `'handler web'`,
`'handler sub_thread data_read'`, etc.) controls display filtering.

This behavioral data (往路処理 / 復路処理 / 例外処理 / コールバック) is **real
knowledge content** — not boilerplate — and must appear in the generated knowledge file.

---

## 3. Proposed Fix

### 3-1. Output Format

Replace the three raw-HTML blocks with a Markdown table showing the handler queue
and behavioral descriptions for the handlers listed in `HandlerQueue`:

```markdown
**ハンドラ処理概要**

| ハンドラ | 往路処理 | 復路処理 | 例外処理 |
|----------|----------|----------|----------|
| スレッドコンテキスト変数削除ハンドラ | - | ThreadContextHandlerで設定したスレッドローカル上の変数を削除する | ThreadContextHandlerで設定したスレッドローカル上の変数を削除する |
| スレッドコンテキスト変数設定ハンドラ(メインスレッド) | 起動引数の内容からリクエストID、ユーザID等のスレッドコンテキスト変数を初期化する。 | - | - |
```

- Column set: ハンドラ (name from Handler.js), 往路処理, 復路処理, 例外処理
- コールバック column: included only when at least one handler in the queue has
  a non-`"-"` callback value
- Handler name: use `handler.name` from Handler.js (Japanese display name)
- `"-"` values: render as-is (they are the canonical "none" marker)
- `<br/>` in multi-line values (e.g. callback): replace with ` / ` for table cell
  compatibility
- String concatenation with `+` in JS (multi-line behavior text): joined before rendering
- Empty string `""` behavior values: render as `-` (RetryHandler pattern)

### 3-2. Common Module: `scripts/common/handler_js.py`

New module shared by both create and verify sides.

```python
def parse_handler_dict(js_text: str) -> dict[str, dict]:
    """Parse Handler.js → { key: {name, behavior: {inbound, outbound, error, callback?}} }"""

def parse_handler_queue(script_text: str) -> tuple[str, list[str]]:
    """Parse Block 2 script → (context, [HandlerKey, ...])"""

def render_handler_table(
    handler_dict: dict[str, dict],
    queue: list[str],
) -> str:
    """Render Markdown table from queue + handler_dict. Returns empty string if queue is empty."""
```

**Parsing strategy for `parse_handler_dict`**:
- Extract the `var Handler = { ... };` block from the JS text using balanced-brace
  matching (not `eval()` — the JS is not valid Python)
- For each entry, extract `name` (string literal) and `behavior` fields
  (`inbound`, `outbound`, `error`, `callback` optional)
- Handle multi-line string concatenation (`"..." + "..."` → joined)
- Handle trailing whitespace in string values (v1.3 has trailing spaces)
- Keys with suffix (`ThreadContextHandler_main`, `DbConnectionManagementHandler_main`):
  kept as-is; `HandlerQueue` uses the suffixed key directly

**Parsing strategy for `parse_handler_queue`**:
- Extract `Context` and `HandlerQueue` from the inline `<script>` block
- `HandlerQueue` is a JS array literal — extract elements with regex
- `Context` is a space-separated string (e.g. `'handler sub_thread data_read'`)

### 3-3. Create Side: `visit_raw` 3-Block State Machine

`rst_ast_visitor.py` `visit_raw` is updated to a 3-block state machine. Since the
three blocks always appear together in sequence, each `visit_raw` call is assigned to
one of three roles based on arrival order within the current section:

```
State: (handler_js_text, script_text, block_count)

Block 1 (raw with :file: containing "Handler.js"):
  → Store js_text; return ""

Block 2 (raw with inline <script> containing HandlerQueue):
  → Store script_text; return ""

Block 3 (raw with :file: containing "handler_structure.html"):
  → Parse + render table using handler_js.py; return Markdown table
  → Reset state
```

Detection logic:
- Block 1: `node.get("source")` path ends with `Handler.js`
- Block 2: `node.astext()` contains `HandlerQueue`
- Block 3: `node.get("source")` path ends with `handler_structure.html`

Any `raw:: html` block that does not match any of the three roles falls through to
the existing `normalise_raw_html()` path (preserves current behavior for other HTML).

State is stored on the visitor instance (`self._handler_js_state`), reset per document.

### 3-4. Verify Side: Same Common Module

The verify-side normaliser (`rst_normaliser.py` → `rst_ast_visitor.py`) uses the same
`visit_raw` implementation, so the normalised source contains the same Markdown table
that create outputs. QC1–QC4 sequential-delete works unchanged.

Spec §2-2 independence principle: verify imports `handler_js.py` from `scripts/common/`
(RST-spec-derived logic layer), not from `scripts/create/`. This is permitted.

### 3-5. Blank-Line Fix: `visit_definition_list`

Change `"\n".join(out)` to `"\n\n".join(out)` to emit a blank line between definition
list items. This restores the visual paragraph separation between 往路処理 /
復路処理 / 例外処理 steps that the RST source implies.

---

## 4. Handler.js Loading

Block 1's `:file:` directive causes docutils to inline the file content as the `raw`
node's text at parse time. `node.astext()` therefore returns the full Handler.js
content directly — no additional file I/O needed in `visit_raw`.

The `source` attribute on the raw node reflects the `:file:` path. This is used to
detect Block 1 and Block 3 by filename suffix.

---

## 5. Edge Cases

| Case | Handling |
|------|----------|
| Handler key not found in Handler.js | Log warning; render row with `(不明)` as name, `-` for all behavior fields |
| Suffixed key (e.g. `ThreadContextHandler_main`) | Looked up directly; no stripping |
| Empty `""` behavior value | Render as `-` |
| `callback` present and non-`"-"` | Add コールバック column to table |
| `callback: "-"` for all handlers in queue | Omit コールバック column |
| `<br/>` in callback value | Replace with ` / ` |
| JS string concatenation `"a" + "b"` | Join before rendering |
| Trailing whitespace in behavior string | Strip |
| v1.2 / v1.3 / v1.4 Handler.js differences | Handled by per-version file load; same parser |

---

## 6. Verify Impact

- **QC5**: The generated Markdown table contains no `<script>`, no raw HTML tags.
  QC5 FAILs on handler files will be resolved.
- **QC1**: The Markdown table rows are the normalised-source content. Sequential-delete
  will find them at the expected position. No new QC1 FAILs expected.
- **QC2/QC3**: No duplication of handler content. No new FAILs expected.
- **QC4**: Table appears in the same document position as the original 3-block group.
  No order change relative to surrounding sections.

---

## 7. Unit Tests

### `test_handler_js.py` (new)

| Test | Input | Expected |
|------|-------|----------|
| parse_handler_dict — basic entry | Handler.js snippet with inbound/outbound/error | dict with correct values |
| parse_handler_dict — multiline concatenation | `"a" + "b"` | joined string |
| parse_handler_dict — empty string value | `inbound: ""` | `""` in dict |
| parse_handler_dict — callback present | entry with callback | callback in dict |
| parse_handler_dict — dash value | `inbound: "-"` | `"-"` |
| parse_handler_dict — trailing whitespace | `"text  "` | stripped |
| parse_handler_queue — basic | script with Context and HandlerQueue | correct tuple |
| parse_handler_queue — multiline HandlerQueue | array spread over lines | all keys extracted |
| render_handler_table — no callback | queue without callback handlers | 4-column table |
| render_handler_table — with callback | queue with callback handler | 5-column table |
| render_handler_table — br in callback | `"a<br/>b"` | `"a / b"` |
| render_handler_table — unknown key | key not in dict | row with `(不明)` |
| render_handler_table — empty string behavior | `""` → `-` | `-` in cell |

### `test_rst_ast_visitor.py` additions

| Test | Input | Expected |
|------|-------|----------|
| visit_raw 3-block sequence | Handler.js + script + handler_structure.html nodes | Markdown table output |
| visit_raw Block 1 alone | Only Handler.js node | empty string (state stored, no output yet) |
| visit_raw non-handler raw block | arbitrary HTML | normalise_raw_html result (unchanged) |

---

## 8. Files Changed

| File | Change |
|------|--------|
| `tools/rbkc/scripts/common/handler_js.py` | New: parse + render |
| `tools/rbkc/scripts/common/rst_ast_visitor.py` | Update `visit_raw` with state machine |
| `tools/rbkc/scripts/common/rst_ast_visitor.py` | Update `visit_definition_list` blank-line fix |
| `tools/rbkc/tests/ut/test_handler_js.py` | New: unit tests for handler_js |
| `tools/rbkc/tests/ut/test_rst_ast_visitor.py` | Add visit_raw 3-block tests |
| `tools/rbkc/docs/rbkc-handler-v1x-design.md` | This document |

No changes to `scripts/verify/verify.py` or `scripts/create/` converters.

---

## 9. Scope (Out of Scope)

- **v5 / v6**: Do not use `Handler.js`. Not affected.
- **handler_structure.html** and **handler_structure_bg.png** image assets: currently
  copied as image files in knowledge assets — out of scope for this issue.
- Context-based filtering (`'handler sub_thread data_read'`): the rendered table shows
  all handlers in the queue regardless of Context. Context is informational only.
