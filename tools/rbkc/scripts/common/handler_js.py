"""Parse Handler.js and render Markdown handler queue tables.

Shared by create-side (rst_ast_visitor) and verify-side (same visitor).
Design reference: tools/rbkc/docs/rbkc-handler-v1x-design.md
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# Match a JS string literal (single or double quote), including concatenation.
_STR_PART_RE = re.compile(r"""(?P<q>['"])(?P<text>(?:\\.|(?!(?P=q)).)*)(?P=q)""")


def _parse_js_string(value: str) -> str:
    """Extract and join a JS string value (handles concatenation with +)."""
    parts: list[str] = []
    for m in _STR_PART_RE.finditer(value):
        parts.append(m.group("text"))
    return "".join(parts).strip()


def _extract_string_field(block: str, field: str) -> str | None:
    """Extract a single string field value from a JS object block."""
    pattern = re.compile(
        r"""\b""" + re.escape(field) + r"""\s*:\s*((?:['"](?:\\.|[^'"\\])*['"]\s*\+\s*)*['"](?:\\.|[^'"\\])*['"])""",
        re.DOTALL,
    )
    m = pattern.search(block)
    if m is None:
        return None
    return _parse_js_string(m.group(1))


def _find_js_block(js_text: str, var_name: str) -> str | None:
    """Extract the content of `var {var_name} = { ... };` using balanced-brace matching."""
    start = js_text.find(f"var {var_name} = {{")
    if start == -1:
        return None
    brace_pos = js_text.index("{", start)
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
    return js_text[brace_pos + 1:end]


def _split_js_entries(block: str) -> list[tuple[str, str]]:
    """Split a JS object block into (key, entry_text) pairs.

    Each entry starts with: Identifier: {
    """
    entry_re = re.compile(r"""^(\w+)\s*:\s*\{""", re.MULTILINE)
    matches = list(entry_re.finditer(block))
    entries: list[tuple[str, str]] = []
    for idx, m in enumerate(matches):
        key = m.group(1)
        entry_start = m.start()
        entry_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
        entry_text = block[entry_start:entry_end]
        entries.append((key, entry_text))
    return entries


# ---------------------------------------------------------------------------
# parse_api_dict
# ---------------------------------------------------------------------------

def parse_api_dict(js_text: str) -> dict[str, dict]:
    """Parse Handler.js → { key: {name} } for the Api dictionary."""
    result: dict[str, dict] = {}
    block = _find_js_block(js_text, "Api")
    if block is None:
        return result
    for key, entry_text in _split_js_entries(block):
        name_val = _extract_string_field(entry_text, "name")
        if name_val is None:
            continue
        result[key] = {"name": name_val}
    return result


# ---------------------------------------------------------------------------
# parse_handler_dict
# ---------------------------------------------------------------------------

_API_REF_RE = re.compile(r"""Api\.(\w+)""")


def _resolve_type_field(entry_text: str, field: str, api_dict: dict[str, dict]) -> str | None:
    """Resolve a type field (argument or returns) from an entry block.

    Returns the Api entry name, or None if null / not found / Api key unknown.
    """
    pattern = re.compile(
        r"""\b""" + re.escape(field) + r"""\s*:\s*([^\n,}]+)""",
    )
    m = pattern.search(entry_text)
    if m is None:
        return None
    value = m.group(1).strip().rstrip(",").strip()
    if value == "null":
        return None
    api_m = _API_REF_RE.match(value)
    if api_m:
        api_key = api_m.group(1)
        entry = api_dict.get(api_key)
        if entry is None:
            return None
        return entry["name"]
    return None


def parse_handler_dict(js_text: str, api_dict: dict[str, dict] | None = None) -> dict[str, dict]:
    """Parse Handler.js → { key: {name, package?, type?: {argument, returns}, behavior: {...}} }

    api_dict is used to resolve Api.* references in type fields.
    If omitted, type fields will not be populated.
    """
    if api_dict is None:
        api_dict = {}

    result: dict[str, dict] = {}
    block = _find_js_block(js_text, "Handler")
    if block is None:
        return result

    for key, entry_text in _split_js_entries(block):
        name_val = _extract_string_field(entry_text, "name")
        if name_val is None:
            continue

        # Find behavior block
        beh_m = re.search(r"""\bbehavior\s*:\s*\{""", entry_text, re.DOTALL)
        if beh_m is None:
            continue
        beh_start = beh_m.end() - 1
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
            val = _extract_string_field(beh_block, field)
            if val is not None:
                behavior[field] = val

        entry: dict = {"name": name_val, "behavior": behavior}

        # Optional package field
        pkg_val = _extract_string_field(entry_text, "package")
        if pkg_val is not None:
            entry["package"] = pkg_val

        # Optional type block (argument / returns resolved via api_dict)
        type_m = re.search(r"""\btype\s*:\s*\{""", entry_text, re.DOTALL)
        if type_m is not None:
            argument = _resolve_type_field(entry_text[type_m.start():], "argument", api_dict)
            returns = _resolve_type_field(entry_text[type_m.start():], "returns", api_dict)
            entry["type"] = {"argument": argument, "returns": returns}

        result[key] = entry

    return result


# ---------------------------------------------------------------------------
# parse_handler_queue
# ---------------------------------------------------------------------------

def parse_handler_queue(script_text: str) -> tuple[str, list[str]]:
    """Parse Block 2 inline <script> → (context, [HandlerKey, ...])"""
    context_m = re.search(r"""Context\s*=\s*['"]([^'"]+)['"]""", script_text)
    context = context_m.group(1).strip() if context_m else ""

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

_BR_RE = re.compile(r"""</?\s*br\s*/?>""", re.IGNORECASE)


def _cell(value: str) -> str:
    """Normalise a behavior value for use in a Markdown table cell."""
    if not value:
        return "-"
    value = _BR_RE.sub(" / ", value).strip()
    value = value.rstrip(" /").rstrip()
    return value if value else "-"


def render_handler_table(
    handler_dict: dict[str, dict],
    queue: list[str],
) -> str:
    """Render a Markdown table from queue + handler_dict.

    Columns: ハンドラ, クラス名, 入力型, 結果型, 往路処理, 復路処理, 例外処理 [, コールバック]
    Returns empty string if queue is empty.
    """
    if not queue:
        return ""

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
            class_name = "-"
            arg_type = result_type = "-"
            inbound = outbound = error = callback = "-"
        else:
            name = h["name"]
            pkg = h.get("package")
            class_name = f"{pkg}.{key}" if pkg else "-"
            type_info = h.get("type")
            if type_info is not None:
                arg_type = type_info.get("argument") or "-"
                result_type = type_info.get("returns") or "-"
            else:
                arg_type = result_type = "-"
            b = h["behavior"]
            inbound = _cell(b.get("inbound", "-"))
            outbound = _cell(b.get("outbound", "-"))
            error = _cell(b.get("error", "-"))
            callback = _cell(b.get("callback", "-"))

        row = [name, class_name, arg_type, result_type, inbound, outbound, error]
        if show_callback:
            row.append(callback)
        rows.append(row)

    if show_callback:
        headers = ["ハンドラ", "クラス名", "入力型", "結果型", "往路処理", "復路処理", "例外処理", "コールバック"]
    else:
        headers = ["ハンドラ", "クラス名", "入力型", "結果型", "往路処理", "復路処理", "例外処理"]

    col_count = len(headers)
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join(["---"] * col_count) + "|"
    data_lines = ["| " + " | ".join(row) + " |" for row in rows]

    table = "\n".join([header_line, sep_line] + data_lines)
    return table
