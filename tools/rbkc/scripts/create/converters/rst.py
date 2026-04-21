"""RST → structured Markdown converter for RBKC.

Converts Nablarch official RST documentation into section-split Markdown
suitable for knowledge JSON files.  No AI, no external API calls.

Public API:
    convert(source: str, file_id: str = "") -> RSTResult
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from docutils.parsers.rst.tableparser import SimpleTableParser
from docutils.statemachine import StringList


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Section:
    title: str
    content: str   # Markdown


@dataclass
class RSTResult:
    title: str
    no_knowledge_content: bool
    sections: list[Section] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Standard admonition directive names
_ADMONITIONS = {
    "note", "warning", "important", "tip", "caution",
    "attention", "danger", "error", "hint", "seealso",
    "deprecated", "versionadded", "versionchanged",
}

# Directives whose block body is silently skipped
_SKIP_DIRECTIVES = {"include"}

# Characters that RST uses for underlines (Sphinx subset)
_UNDERLINE_CHARS = set("=-~^+#*_.:`!\"'")

# Preamble section title (content between h1 and first section heading)
_PREAMBLE_TITLE = "概要"


# ---------------------------------------------------------------------------
# Underline / heading helpers
# ---------------------------------------------------------------------------

def _is_underline(line: str) -> bool:
    """Return True if *line* is a valid RST underline (all same char, ≥ 3)."""
    s = line.rstrip("\n").rstrip()
    if len(s) < 3:
        return False
    c = s[0]
    if c not in _UNDERLINE_CHARS:
        return False
    return all(x == c for x in s)


def _detect_heading_chars(lines: list[str]) -> list[str]:
    """Return heading underline characters in order of first appearance.

    Both overline (char + text + char) and underline-only (text + char) styles
    are recognised, matching Sphinx behaviour.
    """
    chars: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Overline style: underline / title / underline
        if (
            i + 2 < len(lines)
            and _is_underline(line)
            and lines[i + 1].strip()
            and not _is_underline(lines[i + 1])
            and _is_underline(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            c = line.rstrip()[0]
            if c not in chars:
                chars.append(c)
            i += 3
            continue
        # Underline-only style: title / underline (but not the underline of overline)
        if (
            i + 1 < len(lines)
            and line.strip()
            and not _is_underline(line)
            and _is_underline(lines[i + 1])
            # Exclude: this title line is itself preceded by an overline
            and not (i > 0 and _is_underline(lines[i - 1])
                     and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0])
        ):
            c = lines[i + 1].rstrip()[0]
            if c not in chars:
                chars.append(c)
            i += 2
            continue
        i += 1
    return chars


# ---------------------------------------------------------------------------
# Section splitter
# ---------------------------------------------------------------------------

def _split_sections(
    lines: list[str],
    heading_chars: list[str],
) -> tuple[str, list[tuple[str, list[str]]]]:
    """Parse *lines* into title + raw section line groups.

    h1 → title string
    h2/h3 → each starts a new section; content up to next h2/h3 belongs to it.
    Preamble (between h1 and first h2/h3) → section titled _PREAMBLE_TITLE.

    Returns:
        (title, [(section_title, raw_lines), ...])
    """
    if not heading_chars:
        return "", [(_PREAMBLE_TITLE, lines)]

    h1_char = heading_chars[0]
    # h2 and h3 (indices 1 and 2) are section boundaries; h4+ stay as sub-headings
    section_chars = set(heading_chars[1:3]) if len(heading_chars) >= 2 else set()

    title = ""
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    preamble_lines: list[str] = []
    found_h1 = False

    def _flush():
        nonlocal current_title, current_lines, preamble_lines
        if current_title is not None:
            sections.append((current_title, current_lines))
        elif current_lines:
            # Content before first section title → h1〜h2 preamble (extend so pre-h1 content is preserved)
            preamble_lines.extend(current_lines)
        current_title = None
        current_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- Overline heading ---
        if (
            i + 2 < len(lines)
            and _is_underline(line)
            and lines[i + 1].strip()
            and not _is_underline(lines[i + 1])
            and _is_underline(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            c = line.rstrip()[0]
            text = lines[i + 1].strip()
            if c == h1_char and not found_h1:
                title = text
                found_h1 = True
                preamble_lines = current_lines
                current_lines = []
                i += 3
                continue
            if c in section_chars:
                _flush()
                current_title = text
                i += 3
                continue
            # h4+: keep as sub-heading in current section
            level = heading_chars.index(c) if c in heading_chars else len(heading_chars)
            current_lines.append(f"{'#' * (level + 1)} {text}")
            i += 3
            continue

        # --- Underline-only heading ---
        if (
            i + 1 < len(lines)
            and line.strip()
            and not _is_underline(line)
            and _is_underline(lines[i + 1])
            and not (i > 0 and _is_underline(lines[i - 1])
                     and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0])
        ):
            c = lines[i + 1].rstrip()[0]
            if c in heading_chars:
                text = line.strip()
                if c == h1_char and not found_h1:
                    title = text
                    found_h1 = True
                    preamble_lines = current_lines
                    current_lines = []
                    i += 2
                    continue
                if c in section_chars:
                    _flush()
                    current_title = text
                    i += 2
                    continue
                # h4+: keep as sub-heading
                level = heading_chars.index(c)
                current_lines.append(f"{'#' * (level + 1)} {text}")
                i += 2
                continue

        current_lines.append(line)
        i += 1

    # Save remaining content before flushing
    trailing_lines = list(current_lines)
    _flush()

    # If no h2/h3 sections were found, treat all post-title content as one section
    if not sections and trailing_lines:
        sections = [(_PREAMBLE_TITLE, trailing_lines)]
    else:
        # Prepend preamble as first section (if non-empty after stripping)
        preamble_content = [l for l in preamble_lines if l.strip()]
        if preamble_content:
            sections.insert(0, (_PREAMBLE_TITLE, preamble_lines))

    return title, sections


# ---------------------------------------------------------------------------
# Handler.js parser (v1.x raw :file: support)
# ---------------------------------------------------------------------------

def _extract_js_strings(text: str) -> str:
    """Join concatenated JS string literals: "a" + "b" -> "ab"."""
    parts = re.findall(r'"([^"]*)"', text)
    return "".join(parts).strip()


# Matches one or more quoted JS strings optionally joined by +
_JS_QUOTED_VALUE_RE = re.compile(r'"[^"]*"(?:\s*\+\s*"[^"]*")*')


def _extract_js_field(entry: str, field: str) -> str:
    """Extract the quoted string value for *field* from a JS object entry."""
    idx = entry.find(f"{field}:")
    if idx < 0:
        return ""
    m = _JS_QUOTED_VALUE_RE.search(entry, idx + len(field) + 1)
    return _extract_js_strings(m.group(0)) if m else ""


def _parse_handler_js(js_content: str, handler_stem: str) -> list[dict]:
    """Extract handler behavior entries from Handler.js content.

    Finds all entries whose key starts with *handler_stem* (exact or with _suffix).
    Returns list of dicts with keys: key, name, package, inbound, outbound, error.
    """
    results = []
    pattern = re.compile(
        r"^(" + re.escape(handler_stem) + r"(?:_\w+)?)\s*:\s*\{",
        re.MULTILINE,
    )
    for m in pattern.finditer(js_content):
        key = m.group(1)
        # Extract the entry block by counting braces
        depth = 0
        start = m.end() - 1  # points at opening {
        i = start
        while i < len(js_content):
            if js_content[i] == "{":
                depth += 1
            elif js_content[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        entry = js_content[start : i + 1]

        name = _extract_js_field(entry, "name")
        pkg = _extract_js_field(entry, "package")

        # Extract behavior block
        bm = re.search(r"behavior:\s*\{(.*?)\}", entry, re.DOTALL)
        behavior_text = bm.group(1) if bm else ""

        def _get_field(field: str) -> str:
            # Stop at next field (comma at start of line) or closing brace
            fm = re.search(
                field + r":\s*(.*?)(?=\n\s*,\s*(?:outbound|error|inbound)|\s*\})",
                behavior_text,
                re.DOTALL,
            )
            if not fm:
                return ""
            return _extract_js_strings(fm.group(1))

        results.append({
            "key": key,
            "name": name,
            "package": pkg,
            "inbound": _get_field("inbound"),
            "outbound": _get_field("outbound"),
            "error": _get_field("error"),
        })

    return results


# ---------------------------------------------------------------------------
# Hyperlink target collector
# ---------------------------------------------------------------------------

def _collect_targets(lines: list[str]) -> dict[str, str]:
    """Collect named hyperlink target definitions from RST lines.

    Returns {name: url} for lines like:
        .. _Name: https://...
        .. _`Name with spaces`: https://...
    """
    targets: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        # Backtick-quoted name: .. _`Name`: url
        m = re.match(r"\.\.\s+_`([^`]+)`:\s*(https?://\S+)", stripped)
        if m:
            targets[m.group(1)] = m.group(2)
            continue
        # Plain name: .. _Name: url
        m = re.match(r"\.\.\s+_([A-Za-z0-9][^:]*?):\s*(https?://\S+)", stripped)
        if m:
            targets[m.group(1).strip()] = m.group(2)
    return targets


# ---------------------------------------------------------------------------
# Inline markup converter
# ---------------------------------------------------------------------------

def _convert_inline(
    text: str,
    file_id: str = "",
    targets: dict[str, str] | None = None,
    label_map: dict[str, str] | None = None,
) -> str:
    """Convert RST inline markup to Markdown."""

    # :java:extdoc:`ClassName <fqcn>`  →  `ClassName`
    text = re.sub(
        r":java:extdoc:`([^<`]+?)\s*<[^>]+>`",
        lambda m: f"`{m.group(1).strip()}`",
        text,
    )
    # :java:extdoc:`ClassName`  →  `ClassName`
    text = re.sub(r":java:extdoc:`([^`]+)`", r"`\1`", text)

    # :ref:`display text <label>`  →  display text
    text = re.sub(r":ref:`([^<`]+?)\s*<[^>]+>`", lambda m: m.group(1).strip(), text)
    # :ref:`label`  →  resolved section title (or label if not in map)
    def _resolve_ref(m: re.Match) -> str:
        label = m.group(1).strip()
        if label_map:
            return label_map.get(label, label)
        return label
    text = re.sub(r":ref:`([^`]+)`", _resolve_ref, text)

    # :doc:`text <path>`  →  text
    text = re.sub(r":doc:`([^<`]+?)\s*<[^>]+>`", lambda m: m.group(1).strip(), text)
    # :doc:`path`  →  path
    text = re.sub(r":doc:`([^`]+)`", r"\1", text)

    # :download:`text <path>`  →  [text](assets/{file_id}/filename)
    def _download(m: re.Match) -> str:
        label = m.group(1).strip()
        path = m.group(2).strip()
        filename = PurePosixPath(path).name
        return f"[{label}](assets/{file_id}/{filename})" if file_id else f"[{label}]({filename})"

    text = re.sub(r":download:`([^<`]+?)\s*<([^>]+)>`", _download, text)

    # :任意ロール:`text`  →  text (catch-all for other roles)
    text = re.sub(r":[a-z_-]+:`([^`]+)`", r"\1", text)

    # ``code``  →  `code`
    text = re.sub(r"``(.+?)``", r"`\1`", text)

    # External hyperlink: `text (label) <url>`_  →  [text](url)
    text = re.sub(
        r"`([^`<]+?)\s*<(https?://[^>]+)>`_+",
        lambda m: f"[{m.group(1).strip()}]({m.group(2)})",
        text,
    )

    # Anonymous hyperlink reference: `text`__  →  text
    text = re.sub(r"`([^`]+)`__", r"\1", text)

    # Hyperlink reference: `text`_  →  [text](url) if target known, else plain text
    if targets:
        def _resolve_named_ref(m: re.Match) -> str:
            name = m.group(1)
            url = targets.get(name) or targets.get(name.lower())
            return f"[{name}]({url})" if url else name
        text = re.sub(r"`([^`]+)`_(?!_)", _resolve_named_ref, text)
    else:
        text = re.sub(r"`([^`]+)`_", r"\1", text)

    return text


# ---------------------------------------------------------------------------
# Block reading helper
# ---------------------------------------------------------------------------

def _read_block(lines: list[str], start: int) -> tuple[list[str], int]:
    """Read indented block starting at *start* (after blank lines).

    Returns (block_lines, next_i) where next_i points to the first line
    that does not belong to the block.
    """
    # Skip blank lines
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1

    if i >= len(lines) or not lines[i].startswith(" "):
        return [], i

    # Determine indent of first non-blank line
    indent = len(lines[i]) - len(lines[i].lstrip())
    block: list[str] = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            block.append("")
            i += 1
        elif len(line) - len(line.lstrip()) >= indent:
            block.append(line[indent:].rstrip("\n"))
            i += 1
        else:
            break

    # Strip trailing blanks
    while block and not block[-1].strip():
        block.pop()

    return block, i


def _read_options(lines: list[str], start: int, directive_indent: int) -> tuple[list[str], int]:
    """Read RST directive option lines only (lines starting with ':' and indented > directive).

    Stops at the first non-blank line that is not a directive option or is not more
    indented than the directive itself.  Used for image directives to avoid consuming
    sibling content as block body.

    Note: only single-line option values are supported; multi-line continuations are
    not present in the Nablarch v6 corpus so this limitation is acceptable.

    Returns (option_lines, next_i).
    """
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1

    options: list[str] = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= directive_indent:
            break
        stripped = line.strip()
        if not stripped.startswith(":"):
            break
        options.append(stripped)
        i += 1

    return options, i


# ---------------------------------------------------------------------------
# List-table / csv-table parser
# ---------------------------------------------------------------------------

def _parse_list_table(lines: list[str], start: int) -> tuple[list[list[str]], int, int]:
    """Parse list-table body.  Returns (rows, header_count, next_i).

    rows[i] is a list of cell texts.
    header_count is the number of header rows (from :header-rows:).
    """
    block, next_i = _read_block(lines, start)

    header_rows = 0
    # First, gather options: lines before the first "* -"
    option_lines: list[str] = []
    body_start = 0
    for idx, bl in enumerate(block):
        if bl.startswith("* -") or bl.startswith("*-"):
            body_start = idx
            break
        option_lines.append(bl)

    for opt in option_lines:
        m = re.match(r":header-rows:\s*(\d+)", opt.strip())
        if m:
            header_rows = int(m.group(1))

    # Parse rows: each row starts with "* -", subsequent cells start with "  -"
    rows: list[list[str]] = []
    current_row: list[str] | None = None
    current_cell_lines: list[str] = []

    def _flush_cell():
        if current_row is not None:
            current_row.append(" ".join(l.strip() for l in current_cell_lines if l.strip()))

    for bl in block[body_start:]:
        if bl.startswith("* -") or bl.startswith("*-"):
            # New row
            if current_row is not None:
                _flush_cell()
                rows.append(current_row)
            current_row = []
            current_cell_lines = [bl[3:].lstrip() if bl.startswith("* -") else bl[2:].lstrip()]
        elif re.match(r"^\s{0,2}-\s", bl) or bl.startswith("  -"):
            # New cell in current row
            _flush_cell()
            current_cell_lines = [re.sub(r"^\s{0,2}-\s?", "", bl)]
        else:
            # Continuation of current cell
            if current_cell_lines is not None:
                current_cell_lines.append(bl)

    if current_row is not None:
        _flush_cell()
        rows.append(current_row)

    return rows, header_rows, next_i


def _rows_to_md_table(rows: list[list[str]], header_count: int, file_id: str = "") -> list[str]:
    """Convert parsed rows to Markdown table lines."""
    if not rows:
        return []

    # Determine column count from widest row
    ncols = max(len(r) for r in rows) if rows else 0

    def _cell(text: str) -> str:
        return _convert_inline(text, file_id).replace("|", "\\|")

    md: list[str] = []
    for ri, row in enumerate(rows):
        cells = [_cell(row[ci] if ci < len(row) else "") for ci in range(ncols)]
        md.append("| " + " | ".join(cells) + " |")
        if ri == max(header_count - 1, 0):
            md.append("|" + "|".join(["---"] * ncols) + "|")

    return md


# ---------------------------------------------------------------------------
# Simple table parser (via docutils, with CJK-safe fallback)
# ---------------------------------------------------------------------------

def _parse_simple_table_cjk(block: list[str], file_id: str = "") -> list[str]:
    """CJK-safe simple table parser using display-width column splitting.

    Fallback for when docutils SimpleTableParser fails due to CJK characters
    whose display width (2) mismatches their Python string length (1).
    """
    if not block:
        return []

    import unicodedata

    def _dw(c: str) -> int:
        return 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1

    # Find first separator line to determine column boundaries.
    # = and space are each 1 display column, so char positions == display positions.
    first_sep = next(
        (ln.rstrip() for ln in block if ln.strip() and all(c in "= " for c in ln.strip())),
        None,
    )
    if not first_sep:
        return ["```"] + block + ["```"]

    # Column 2, 3, ... start at the display position of the first = after a gap.
    col_starts: list[int] = []  # display positions where each column (except first) begins
    in_eq = True
    disp = 0
    for c in first_sep:
        if c == "=" and not in_eq:
            col_starts.append(disp)
            in_eq = True
        elif c == " ":
            in_eq = False
        disp += 1  # = and space are 1 display column each

    if not col_starts:
        return ["```"] + block + ["```"]

    ncols = len(col_starts) + 1

    def split_row(line: str) -> list[str]:
        cells: list[list[str]] = [[] for _ in range(ncols)]
        d = 0
        ci = 0
        for ch in line:
            if ci < len(col_starts) and d >= col_starts[ci]:
                ci += 1
            cells[ci].append(ch)
            d += _dw(ch)
        return ["".join(cell).strip() for cell in cells]

    rows: list[list[str]] = []
    sep_count = 0
    head_count: int | None = None

    for line in block:
        s = line.rstrip()
        if not s:
            continue
        stripped = s.lstrip()
        if stripped and all(c in "= " for c in stripped):
            sep_count += 1
            if sep_count == 2 and head_count is None:
                head_count = len(rows)
        else:
            cells = split_row(s)
            # Skip rows that are entirely empty (e.g., option-only cells like :ref: refs)
            if any(c for c in cells):
                rows.append(cells)

    if head_count is None:
        head_count = 0

    return _rows_to_md_table(rows, head_count, file_id)


def _parse_simple_table(block: list[str], file_id: str = "") -> list[str]:
    """Convert RST simple table to Markdown table using docutils SimpleTableParser."""
    if not block:
        return []

    try:
        sl = StringList(block)
        parser = SimpleTableParser()
        tabledata = parser.parse(sl)
    except Exception:
        return _parse_simple_table_cjk(block, file_id)

    colspecs, headrows, bodyrows = tabledata

    def _to_rows(rows_raw) -> list[list[str]]:
        out = []
        for row in rows_raw:
            cells = []
            for cell in row:
                # cell format: [morerows, morecols, offset, StringList]
                content = cell[3] if len(cell) >= 4 else []
                text_parts = [line.strip() for line in content if line.strip()]
                cells.append(" ".join(text_parts))
            out.append(cells)
        return out

    head_rows = _to_rows(headrows)
    body_rows = _to_rows(bodyrows)
    all_rows = head_rows + body_rows
    return _rows_to_md_table(all_rows, len(head_rows), file_id)


# ---------------------------------------------------------------------------
# Grid table parser (custom — CJK-safe)
# ---------------------------------------------------------------------------

def _parse_grid_table(block: list[str], file_id: str = "") -> list[str]:
    """Convert RST grid table to HTML table.

    Uses ``|`` splitting to extract cell text — works correctly with CJK
    characters, which break docutils GridTableParser due to display-width
    vs code-point-width mismatch.

    Supports rowspan detection: a cell continuation row (``|      |``) where
    a sub-separator (``+----+``) appears in the same column indicates row
    merging; the continuation cell text is merged into the preceding cell.
    """
    if not block:
        return []

    def _is_sep(line: str) -> bool:
        s = line.rstrip()
        return bool(s) and s[0] == "+" and all(c in "+-=|" for c in s)

    def _is_header_sep(line: str) -> bool:
        return _is_sep(line) and "=" in line

    def _split_cells(line: str) -> list[str]:
        """Split a table content line on '|', discarding first/last empty."""
        parts = line.split("|")
        # parts[0] is before first |, parts[-1] is after last |
        return [p.strip() for p in parts[1:-1]] if len(parts) >= 3 else []

    # Collect row groups between separator lines.
    # A group is a HEADER group if it is terminated by the header separator (+=====+).
    # Each group: (is_header, [line, ...])
    groups: list[tuple[bool, list[str]]] = []
    current_content: list[str] = []

    for line in block:
        if _is_sep(line):
            if current_content:
                # The separator that terminates this group determines if it's a header
                groups.append((_is_header_sep(line), current_content))
                current_content = []
        else:
            if line.strip().startswith("|"):
                current_content.append(line)

    if current_content:
        groups.append((False, current_content))

    if not groups:
        return []

    # Build rows: each group's content lines → one or more rows.
    # A group may span multiple visual rows (continuation lines).
    # Detect continuation: a content line where some cells are empty AND
    # the previous separator had sub-dividers (+----+) — simplify: just
    # accumulate multi-line cells by checking if all cells in a line are empty
    # (pure continuation) or only some are empty (new sub-row).

    # Simplified approach: each content line with at least one non-empty cell
    # is treated as a row; empty cells in continuation lines are merged up.
    html: list[str] = ["<table>"]
    body_open = False  # track whether <tbody> is currently open

    for is_header, content_lines in groups:
        if not content_lines:
            continue

        rows: list[list[str]] = []
        for cl in content_lines:
            cells = _split_cells(cl)
            if not cells:
                continue
            if not rows or any(c for c in cells):
                rows.append(cells)
            else:
                # All cells empty → continuation; merge into last row
                for ci, c in enumerate(cells):
                    if ci < len(rows[-1]) and c:
                        rows[-1][ci] = (rows[-1][ci] + " " + c).strip()

        if not rows:
            continue

        if is_header:
            # Close any open body section before emitting header
            if body_open:
                html.append("</tbody>")
                body_open = False
            html.append("<thead>")
        else:
            # Open body section only once (multiple body groups share one <tbody>)
            if not body_open:
                html.append("<tbody>")
                body_open = True

        tag = "th" if is_header else "td"
        ncols = max(len(r) for r in rows)

        for row in rows:
            html.append("<tr>")
            for ci in range(ncols):
                text = _convert_inline(row[ci] if ci < len(row) else "", file_id)
                html.append(f"  <{tag}>{text}</{tag}>")
            html.append("</tr>")

        if is_header:
            html.append("</thead>")

    if body_open:
        html.append("</tbody>")

    html.append("</table>")
    return html


# ---------------------------------------------------------------------------
# Content converter
# ---------------------------------------------------------------------------

def _convert_content(raw_lines: list[str], file_id: str = "", targets: dict[str, str] | None = None, source_dir: "Path | None" = None) -> str:
    """Convert RST content lines to Markdown."""
    lines = [l.rstrip("\n") for l in raw_lines]
    output: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line
        if not stripped:
            output.append("")
            i += 1
            continue

        # RST label: .. _label:
        if re.match(r"\.\.\s+_[a-zA-Z0-9_.-]+:", stripped):
            i += 1
            continue

        # RST anonymous target: __
        if stripped == "__":
            i += 1
            continue

        # RST hyperlink target: .. _`text`: url  or  .. target_: url
        if re.match(r"\.\.\s+_", stripped) and ":" in stripped:
            i += 1
            continue

        # RST footnote / citation target — extract inline text + block body
        m_fn = re.match(r"\.\.\s+\[(?:[0-9]+|\*|#[a-z_]*)\]\s+(.*)", stripped)
        if m_fn:
            inline_text = m_fn.group(1).strip()
            block, i = _read_block(lines, i + 1)
            fn_lines = ([inline_text] if inline_text else []) + [b for b in block if b.strip()]
            output.extend(fn_lines)
            continue

        # Directive: .. name::
        m = re.match(r"(\s*)\.\.\s+([a-z_-]+)::(.*)", line)
        if m:
            indent_str, directive, inline_arg = m.group(1), m.group(2), m.group(3).strip()
            directive = directive.lower()

            # --- toctree ---
            if directive == "toctree":
                block, i = _read_block(lines, i + 1)
                # Do not output anything (no-knowledge-content detection handled elsewhere)
                continue

            # --- contents ---
            if directive == "contents":
                block, i = _read_block(lines, i + 1)
                continue

            # --- raw directive ---
            if directive == "raw":
                block, i = _read_block(lines, i + 1)
                # Check for :file: option pointing to Handler.js
                file_opt = next(
                    (b.strip()[len(":file:"):].strip() for b in block if b.strip().startswith(":file:")),
                    None,
                )
                if file_opt and file_opt.endswith(".js") and source_dir is not None:
                    js_path = (source_dir / file_opt).resolve()
                    if js_path.exists():
                        handler_stem = file_id.split("-")[-1] if "-" in file_id else file_id
                        entries = _parse_handler_js(js_path.read_text(encoding="utf-8"), handler_stem)
                        for entry in entries:
                            if entry["name"]:
                                output.append(f"**{entry['name']}** ({entry['package']})")
                            for field in ("inbound", "outbound", "error"):
                                val = entry[field]
                                if val:
                                    output.append(f"{field}: {val}")
                continue

            # --- skip directives ---
            if directive in _SKIP_DIRECTIVES:
                block, i = _read_block(lines, i + 1)
                continue

            # --- class directive — output block as plain text ---
            if directive == "class":
                block, i = _read_block(lines, i + 1)
                for bl in block:
                    if bl.strip():
                        output.append(bl)
                continue

            # --- code-block / code / sourcecode ---
            if directive in ("code-block", "code", "sourcecode"):
                lang = inline_arg or ""
                block, i = _read_block(lines, i + 1)
                # Strip known RST code-block option lines (:linenos: etc.).
                # Use a whitelist of known Sphinx code-block options to avoid
                # stripping code content that starts with ':' (e.g. YAML tags).
                _CODE_OPT_RE = re.compile(
                    r"^:(?:linenos|emphasize-lines|caption|name|force|"
                    r"number-lines|dedent|tab-width|encoding|"
                    r"start-after|end-before|start-at|end-at|"
                    r"language|class|linenothreshold)(?::\s.*|:\s*$|\s*$)"
                )
                content_lines = [_l for _l in block if not _CODE_OPT_RE.match(_l.strip())]
                # Strip leading/trailing blank lines from block
                while content_lines and not content_lines[0].strip():
                    content_lines.pop(0)
                while content_lines and not content_lines[-1].strip():
                    content_lines.pop()
                output.append(f"```{lang}")
                output.extend(content_lines)
                output.append("```")
                continue

            # --- literalinclude ---
            if directive == "literalinclude":
                block, i = _read_block(lines, i + 1)
                lang = ""
                for bl in block:
                    lm = re.match(r":language:\s*(\w+)", bl.strip())
                    if lm:
                        lang = lm.group(1)
                output.append(f"```{lang}")
                # literalinclude reads from a file; emit placeholder
                output.append(f"# (literalinclude: {inline_arg})")
                output.append("```")
                continue

            # --- admonition (named) ---
            if directive in _ADMONITIONS:
                block, i = _read_block(lines, i + 1)
                label = directive.capitalize()
                if directive == "versionadded":
                    label = "Version Added"
                elif directive == "versionchanged":
                    label = "Version Changed"
                elif directive == "seealso":
                    label = "See Also"
                body_parts = []
                if inline_arg:
                    body_parts.append(inline_arg)
                _FIELD_RE = re.compile(r"^:([^:]+):\s*(.*)")
                for l in block:
                    stripped = l.strip()
                    if not stripped:
                        continue
                    m = _FIELD_RE.match(stripped)
                    if m:
                        # Field list entry: preserve value part (drop bare option-only lines)
                        value = m.group(2).strip()
                        if value:
                            body_parts.append(value)
                    else:
                        body_parts.append(stripped)
                body = " ".join(body_parts)
                body = _convert_inline(body, file_id, targets)
                output.append(f"> **{label}:** {body}")
                continue

            # --- admonition (custom title) ---
            if directive == "admonition":
                block, i = _read_block(lines, i + 1)
                label = inline_arg or "Note"
                _FIELD_RE = re.compile(r"^:([^:]+):\s*(.*)")
                body_parts = []
                for l in block:
                    stripped = l.strip()
                    if not stripped:
                        continue
                    m = _FIELD_RE.match(stripped)
                    if m:
                        value = m.group(2).strip()
                        if value:
                            body_parts.append(value)
                    else:
                        body_parts.append(stripped)
                body = " ".join(body_parts)
                body = _convert_inline(body, file_id, targets)
                output.append(f"> **{label}:** {body}")
                continue

            # --- image ---
            if directive == "image":
                path = inline_arg
                directive_indent = len(indent_str)
                options, i = _read_options(lines, i + 1, directive_indent)
                filename = PurePosixPath(path).name
                alt = ""
                for opt in options:
                    am = re.match(r":alt:\s*(.+)", opt)
                    if am:
                        alt = am.group(1).strip()
                asset_path = f"assets/{file_id}/{filename}" if file_id else filename
                output.append(f"![{alt}]({asset_path})")
                continue

            # --- figure ---
            if directive == "figure":
                path = inline_arg
                directive_indent = len(indent_str)
                # Use _read_block for figure: caption may be non-option indented text
                block, i = _read_block(lines, i + 1)
                filename = PurePosixPath(path).name
                # Caption is the first non-option line in the block
                caption = ""
                for bl in block:
                    if bl.strip() and not bl.strip().startswith(":"):
                        caption = bl.strip()
                        break
                asset_path = f"assets/{file_id}/{filename}" if file_id else filename
                output.append(f"![{caption}]({asset_path})")
                continue

            # --- list-table ---
            if directive == "list-table":
                rows, header_rows, i = _parse_list_table(lines, i + 1)
                md_lines = _rows_to_md_table(rows, header_rows, file_id)
                output.extend(md_lines)
                continue

            # --- csv-table ---
            if directive == "csv-table":
                # Parse similar to list-table; simplified: just read block
                block, i = _read_block(lines, i + 1)
                rows: list[list[str]] = []
                header_rows = 0
                for bl in block:
                    if bl.strip().startswith(":"):
                        hm = re.match(r":header-rows:\s*(\d+)", bl.strip())
                        if hm:
                            header_rows = int(hm.group(1))
                        continue
                    # CSV line
                    cells = [c.strip().strip('"') for c in bl.split(",")]
                    if any(cells):
                        rows.append(cells)
                md_lines = _rows_to_md_table(rows, header_rows, file_id)
                output.extend(md_lines)
                continue

            # --- table (contains inner RST simple/grid table) ---
            if directive == "table":
                block, i = _read_block(lines, i + 1)
                # Strip option lines
                content = [l for l in block if not l.strip().startswith(":")]
                while content and not content[0].strip():
                    content.pop(0)
                if content and content[0].rstrip().startswith("+"):
                    md_lines = _parse_grid_table(content, file_id)
                else:
                    md_lines = _parse_simple_table(content, file_id)
                output.extend(md_lines)
                continue

            # --- function ---
            if directive == "function":
                block, i = _read_block(lines, i + 1)
                sig = inline_arg or ""
                output.append("```")
                output.append(sig)
                output.append("```")
                # Preserve body (param/return descriptions) as prose
                for bl in block:
                    stripped = bl.strip()
                    if not stripped:
                        continue
                    # Strip RST field list marker: :param type name: desc → desc
                    m = re.match(r"^:[^:]+:\s*(.*)", stripped)
                    if m:
                        desc = m.group(1).strip()
                        if desc:
                            output.append(desc)
                    else:
                        output.append(stripped)
                continue

            # --- rubric ---
            if directive == "rubric":
                block, i = _read_block(lines, i + 1)
                title = _convert_inline(inline_arg, file_id, targets)
                output.append(f"**{title}**")
                continue

            # --- Unknown directive: skip block with warning ---
            block, i = _read_block(lines, i + 1)
            import sys
            print(
                f"Warning: unknown RST directive {directive!r} skipped"
                f" in file_id={file_id!r}",
                file=sys.stderr,
            )
            continue

        # Simple table (starts with === ===)
        if re.match(r"^={3,}(\s+={3,})+\s*$", stripped):
            # Collect table block.  A blank line after a separator row ends the table.
            table_block = [line]
            j = i + 1
            last_was_sep = True  # first line is a separator
            while j < len(lines):
                tl = lines[j]
                ts = tl.strip()
                is_sep = bool(ts) and all(c in "= " for c in ts) and ts.startswith("=")
                if is_sep:
                    table_block.append(tl)
                    last_was_sep = True
                    j += 1
                elif not ts:
                    if last_was_sep:
                        # Blank line after separator = end of table
                        break
                    table_block.append(tl)
                    j += 1
                else:
                    table_block.append(tl)
                    last_was_sep = False
                    j += 1
            i = j
            # Strip leading indent
            min_indent = min((len(l) - len(l.lstrip()) for l in table_block if l.strip()), default=0)
            stripped_block = [l[min_indent:] for l in table_block]
            output.extend(_parse_simple_table(stripped_block, file_id))
            continue

        # Grid table (starts with +---)
        if re.match(r"^\+[-=+]+", stripped):
            table_block = [line]
            j = i + 1
            while j < len(lines) and (lines[j].strip().startswith("+") or lines[j].strip().startswith("|")):
                table_block.append(lines[j])
                j += 1
            i = j
            min_indent = min((len(l) - len(l.lstrip()) for l in table_block if l.strip()), default=0)
            stripped_block = [l[min_indent:] for l in table_block]
            output.extend(_parse_grid_table(stripped_block, file_id))
            continue

        # Regular paragraph / list item / other content
        converted = _convert_inline(stripped, file_id, targets)
        output.append(converted)
        i += 1

    return "\n".join(output).strip()


# ---------------------------------------------------------------------------
# No-knowledge-content detection
# ---------------------------------------------------------------------------

def _detect_no_knowledge_content(sections: list[Section]) -> bool:
    """Return True if no section has any meaningful content.

    A file is no-knowledge-content when all its sections (after directive
    processing) contain only whitespace.  Typical cases: toctree-only files,
    navigation indices, label-only stub pages.
    """
    return all(not s.content.strip() for s in sections)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert(source: str, file_id: str = "", extra_targets: dict[str, str] | None = None, source_path: "Path | None" = None, label_map: dict[str, str] | None = None) -> RSTResult:
    """Convert RST *source* to :class:`RSTResult`.

    Args:
        source: Full RST file content.
        file_id: Knowledge file id (used for asset paths).  May be empty.
        extra_targets: Additional named hyperlink targets (e.g. from included link.rst).
            Maps {name: url}.  Merged with targets found in *source*.
        source_path: Path to the RST source file.  Used to resolve relative
            :file: references (e.g. Handler.js) in raw directives.
        label_map: Cross-file RST label→title map from build_label_map().  When
            provided, bare :ref:`label` references are pre-resolved to their
            section titles before tokenising.

    Returns:
        :class:`RSTResult` with title, no_knowledge_content flag, and sections.

    Raises:
        ValueError: An unknown RST directive is encountered.
    """
    from pathlib import Path as _Path
    source_dir = source_path.parent if source_path is not None else None

    # Pre-resolve :ref:`label` using label_map before tokenizing
    if label_map:
        def _presolve_ref(m: re.Match) -> str:
            inner = m.group(1)
            # Display-form :ref:`text <label>` — keep as-is; handled by _convert_inline
            if "<" in inner:
                return m.group(0)
            label = inner.strip()
            return label_map.get(label, label)
        source = re.sub(r":ref:`([^`]+)`", _presolve_ref, source)

    lines = source.splitlines(keepends=True)
    heading_chars = _detect_heading_chars([l.rstrip("\n") for l in lines])
    title, raw_sections = _split_sections([l.rstrip("\n") for l in lines], heading_chars)

    # Collect named hyperlink targets from the whole source (first pass)
    targets = _collect_targets([l.rstrip("\n") for l in lines])
    if extra_targets:
        targets.update(extra_targets)

    sections: list[Section] = []
    for sec_title, sec_lines in raw_sections:
        md = _convert_content(sec_lines, file_id, targets or None, source_dir)
        sections.append(Section(title=sec_title, content=md))

    no_knowledge = _detect_no_knowledge_content(sections)

    return RSTResult(
        title=title,
        no_knowledge_content=no_knowledge,
        sections=sections,
    )
