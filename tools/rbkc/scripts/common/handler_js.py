"""Parse Handler.js and render Markdown handler queue tables.

Shared by create-side (rst_ast_visitor) and verify-side (same visitor).
Design reference: tools/rbkc/docs/rbkc-handler-v1x-design.md
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# parse_handler_dict
# ---------------------------------------------------------------------------

# Match a JS string literal (single or double quote), including concatenation.
_STR_PART_RE = re.compile(r"""(?P<q>['"])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)""")
_CONCAT_RE = re.compile(
    r"""(?P<q>['"])(?P<text>(?:\\.|(?!(?P=q)).)*?)(?P=q)\s*\+\s*"""
    r"""(?P<q2>['"])(?P<text2>(?:\\.|(?!(?P=q2)).)*?)(?P=q2)"""
)


def _parse_js_string(value: str) -> str:
    """Extract and join a JS string value (handles concatenation with +)."""
    # Collect all quoted string parts joined by +
    parts: list[str] = []
    for m in _STR_PART_RE.finditer(value):
        parts.append(m.group("text"))
    return "".join(parts).strip()


def _extract_behavior_field(block: str, field: str) -> str | None:
    """Extract a single behavior field value from a behavior block."""
    # Pattern: field: "..." or field: "..." + "..."
    pattern = re.compile(
        r"""\b""" + re.escape(field) + r"""\s*:\s*((?:['"](?:\\.|[^'"\\])*['"]\s*\+\s*)*['"](?:\\.|[^'"\\])*['"])""",
        re.DOTALL,
    )
    m = pattern.search(block)
    if m is None:
        return None
    return _parse_js_string(m.group(1))


def parse_handler_dict(js_text: str) -> dict[str, dict]:
    """Parse Handler.js → { key: {name, behavior: {inbound, outbound, error, callback?}} }"""
    result: dict[str, dict] = {}

    # Find `var Handler = { ... };` using balanced brace matching.
    # The JS file wraps everything in <script>...</script>.
    handler_start = js_text.find("var Handler = {")
    if handler_start == -1:
        return result

    # Find the opening brace of the Handler object.
    brace_pos = js_text.index("{", handler_start)
    depth = 0
    end = brace_pos
    for i in range(brace_pos, len(js_text)):
        c = js_text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    handler_block = js_text[brace_pos + 1:end]

    # Split handler_block into individual handler entries.
    # Each entry starts with: Identifier: {
    entry_re = re.compile(r"""^(\w+)\s*:\s*\{""", re.MULTILINE)
    matches = list(entry_re.finditer(handler_block))

    for idx, m in enumerate(matches):
        key = m.group(1)
        entry_start = m.start()
        entry_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(handler_block)
        entry_text = handler_block[entry_start:entry_end]

        name_val = _extract_behavior_field(entry_text, "name")
        if name_val is None:
            continue

        # Find behavior block
        beh_m = re.search(r"""\bbehavior\s*:\s*\{""", entry_text, re.DOTALL)
        if beh_m is None:
            continue
        beh_start = beh_m.end() - 1  # position of {
        # Find matching }
        depth2 = 0
        beh_end = beh_start
        for j in range(beh_start, len(entry_text)):
            c = entry_text[j]
            if c == "{":
                depth2 += 1
            elif c == "}":
                depth2 -= 1
                if depth2 == 0:
                    beh_end = j
                    break
        beh_block = entry_text[beh_start:beh_end + 1]

        behavior: dict[str, str] = {}
        for field in ("inbound", "outbound", "error", "callback"):
            val = _extract_behavior_field(beh_block, field)
            if val is not None:
                behavior[field] = val

        result[key] = {"name": name_val, "behavior": behavior}

    return result


# ---------------------------------------------------------------------------
# parse_handler_queue
# ---------------------------------------------------------------------------

def parse_handler_queue(script_text: str) -> tuple[str, list[str]]:
    """Parse Block 2 inline <script> → (context, [HandlerKey, ...])"""
    # Extract Context value
    context_m = re.search(r"""Context\s*=\s*['"]([^'"]+)['"]""", script_text)
    context = context_m.group(1).strip() if context_m else ""

    # Extract HandlerQueue array
    queue_m = re.search(r"""HandlerQueue\s*=\s*\[([^\]]*)\]""", script_text, re.DOTALL)
    queue: list[str] = []
    if queue_m:
        array_text = queue_m.group(1)
        for item_m in re.finditer(r"""['"](\w+)['"]""", array_text):
            queue.append(item_m.group(1))

    return context, queue


# ---------------------------------------------------------------------------
# render_handler_table
# ---------------------------------------------------------------------------

_BR_RE = re.compile(r"""<br\s*/?>""", re.IGNORECASE)


def _cell(value: str) -> str:
    """Normalise a behavior value for use in a Markdown table cell."""
    if not value:
        return "-"
    # Replace <br/> with " / " for inline table display
    value = _BR_RE.sub(" / ", value).strip()
    # Strip trailing " / " artefacts
    value = value.rstrip(" /").rstrip()
    return value if value else "-"


def render_handler_table(
    handler_dict: dict[str, dict],
    queue: list[str],
) -> str:
    """Render a Markdown table from queue + handler_dict.

    Returns empty string if queue is empty.
    """
    if not queue:
        return ""

    # Determine whether any handler in queue has a non-"-" callback.
    show_callback = False
    for key in queue:
        h = handler_dict.get(key)
        if h is None:
            continue
        cb = h["behavior"].get("callback", "-")
        if cb and cb != "-":
            show_callback = True
            break

    rows: list[list[str]] = []
    for key in queue:
        h = handler_dict.get(key)
        if h is None:
            name = "(不明)"
            inbound = outbound = error = callback = "-"
        else:
            name = h["name"]
            b = h["behavior"]
            inbound = _cell(b.get("inbound", "-"))
            outbound = _cell(b.get("outbound", "-"))
            error = _cell(b.get("error", "-"))
            callback = _cell(b.get("callback", "-"))

        row = [name, inbound, outbound, error]
        if show_callback:
            row.append(callback)
        rows.append(row)

    if show_callback:
        headers = ["ハンドラ", "往路処理", "復路処理", "例外処理", "コールバック"]
    else:
        headers = ["ハンドラ", "往路処理", "復路処理", "例外処理"]

    col_count = len(headers)
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["---"] * col_count) + "|"
    data_lines = ["| " + " | ".join(row) + " |" for row in rows]

    table = "\n".join([header_line, sep_line] + data_lines)
    return "**ハンドラ処理概要**\n\n" + table
