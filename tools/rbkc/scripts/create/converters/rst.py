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

from scripts.common.rst_admonition import ADMONITION_LABELS, is_admonition


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
    content: str = ""   # Markdown — text between h1 and the first h2/h3
    sections: list[Section] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Admonition directive names come from scripts.common.rst_admonition — the
# single source of truth. We exclude ``admonition`` (custom-titled) because
# it goes through a separate converter branch that passes the title as the
# inline arg; named admonitions (note/tip/...) use the default label table.
_ADMONITIONS = {n for n in ADMONITION_LABELS if n != "admonition"}

# Directives whose block body is silently skipped
_SKIP_DIRECTIVES = {"include"}

# Characters that RST uses for underlines (Sphinx subset)
_UNDERLINE_CHARS = set("=-~^+#*_.:`!\"'")



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


def _detect_heading_chars(lines: list[str]) -> list[tuple[bool, str]]:
    """Return heading keys in order of first appearance.

    A heading key is a ``(is_overline, char)`` tuple so that Sphinx's rule
    of distinguishing overline+underline from underline-only (even when the
    same underline char is used) is preserved.  Example: ``(True, '-')`` for
    an overline-dash h1 is a different level from ``(False, '-')`` for an
    underline-only dash h2 further down the same file.
    """
    keys: list[tuple[bool, str]] = []
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
            key = (True, line.rstrip()[0])
            if key not in keys:
                keys.append(key)
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
            key = (False, lines[i + 1].rstrip()[0])
            if key not in keys:
                keys.append(key)
            i += 2
            continue
        i += 1
    return keys


# ---------------------------------------------------------------------------
# Section splitter
# ---------------------------------------------------------------------------

def _split_sections(
    lines: list[str],
    heading_keys: list[tuple[bool, str]],
) -> tuple[str, list[str], list[tuple[str, list[str]]]]:
    """Parse *lines* into title + preamble + raw section line groups.

    h1 → title string
    preamble → lines between h1 and first h2/h3 (or all lines when no h1)
    h2/h3 → each starts a new section; content up to next h2/h3 belongs to it.

    ``heading_keys`` is a list of ``(is_overline, char)`` tuples in order of
    first appearance (h1, h2, h3, …).  Using tuples lets Sphinx's rule that
    overline+underline is a distinct level from underline-only apply even when
    both use the same underline character.

    Returns:
        (title, preamble_lines, [(section_title, raw_lines), ...])
    """
    if not heading_keys:
        return "", list(lines), []

    h1_key = heading_keys[0]
    # h2 and h3 (indices 1 and 2) are section boundaries; h4+ stay as sub-headings
    section_keys = set(heading_keys[1:3]) if len(heading_keys) >= 2 else set()

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
            key = (True, line.rstrip()[0])
            text = lines[i + 1].strip()
            if key == h1_key and not found_h1:
                title = text
                found_h1 = True
                preamble_lines = current_lines
                current_lines = []
                i += 3
                continue
            if key in section_keys:
                _flush()
                current_title = text
                i += 3
                continue
            # h4+: keep as sub-heading in current section
            level = heading_keys.index(key) if key in heading_keys else len(heading_keys)
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
            key = (False, lines[i + 1].rstrip()[0])
            if key in heading_keys:
                text = line.strip()
                if key == h1_key and not found_h1:
                    title = text
                    found_h1 = True
                    preamble_lines = current_lines
                    current_lines = []
                    i += 2
                    continue
                if key in section_keys:
                    _flush()
                    current_title = text
                    i += 2
                    continue
                # h4+: keep as sub-heading
                level = heading_keys.index(key)
                current_lines.append(f"{'#' * (level + 1)} {text}")
                i += 2
                continue

        current_lines.append(line)
        i += 1

    _flush()

    return title, preamble_lines, sections


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


def _collect_substitutions(lines: list[str]) -> dict[str, str]:
    """Collect substitution definitions.

    For now, extract URLs from ``.. |name| raw:: html`` blocks so that
    references like ``|name|_`` resolve to something visible in the JSON.
    Returns {name: resolved_text}.
    """
    subs: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        m = re.match(r"\.\.\s+\|([^|]+)\|\s+([a-z_-]+)::(.*)", stripped)
        if not m:
            i += 1
            continue
        name = m.group(1).strip()
        directive = m.group(2).lower()
        # Directive arg on same line (e.g. .. |name| replace:: text)
        inline_arg = m.group(3).strip()
        # Body (indented block)
        block, i = _read_block(lines, i + 1)

        # For ``raw::`` the inline_arg is the output format (e.g. "html") — not
        # body content. For all other directives treat both inline_arg and
        # block as body.
        parts: list[str] = []
        if directive != "raw" and inline_arg:
            parts.append(inline_arg)
        for b in block:
            s = b.strip()
            if s:
                parts.append(s)
        body = " ".join(parts)

        if directive == "replace":
            subs[name] = body
        elif directive == "raw":
            # Extract URL from <a href="..."> if present; else drop the body
            # (``<br />`` etc. have no useful text equivalent).
            m_url = re.search(r'href="([^"]+)"', body)
            if m_url:
                # Prefer link text if present
                m_text = re.search(r'<a[^>]*>([^<]+)</a>', body)
                text = m_text.group(1).strip() if m_text else m_url.group(1)
                subs[name] = f"[{text}]({m_url.group(1)})"
            else:
                subs[name] = ""
        else:
            subs[name] = body
    return subs


# ---------------------------------------------------------------------------
# Inline markup converter
# ---------------------------------------------------------------------------

def _convert_inline(
    text: str,
    file_id: str = "",
    targets: dict[str, str] | None = None,
    label_map: dict[str, str] | None = None,
    substitutions: dict[str, str] | None = None,
) -> str:
    """Convert RST inline markup to Markdown."""

    # |name|_ or |name| substitution reference
    if substitutions:
        def _resolve_subst(m: re.Match) -> str:
            name = m.group(1).strip()
            return substitutions.get(name, m.group(0))
        text = re.sub(r"\|([^|]+)\|_?", _resolve_subst, text)

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

    # :role:`text <target>` → text  (catch-all for roles with a target, e.g.
    # ``:javadoc_url:`Name <path>``` → ``Name``). Must run before the simpler
    # ``:role:`text``` pattern so the target segment is discarded.
    text = re.sub(r":[a-zA-Z][a-zA-Z0-9_.:-]*:`([^<`]+?)\s*<[^>]+>`", lambda m: m.group(1).strip(), text)
    # :任意ロール:`text`  →  text (catch-all for other roles)
    text = re.sub(r":[a-zA-Z][a-zA-Z0-9_.:-]*:`([^`]+)`", r"\1", text)

    # ``code``  →  `code`
    text = re.sub(r"``(.+?)``", r"`\1`", text)

    # External hyperlink: `text (label) <url>`_  →  [text](url)
    text = re.sub(
        r"`([^`<]+?)\s*<(https?://[^>]+)>`_+",
        lambda m: f"[{m.group(1).strip()}]({m.group(2)})",
        text,
    )

    # Anonymous hyperlink reference: `text`__  →  text. The trailing ``__``
    # must be followed by a word boundary so spans like ``(`_`)`` don't match.
    text = re.sub(r"`([^`]+?)`__(?=\s|$|[^\w])", r"\1", text)

    # Hyperlink reference: `text`_  →  [text](url) if target known, else plain text.
    # Trailing ``_`` must be followed by a word boundary (space, end-of-line,
    # or non-word/non-backtick punctuation) — otherwise an isolated backtick
    # code span whose text ends in ``_`` (e.g. ``(`_`)``) is mistakenly
    # parsed as a reference and its body is discarded.
    _REF_SUFFIX = r"(?=\s|$|[^\w_`])"
    if targets:
        def _resolve_named_ref(m: re.Match) -> str:
            name = m.group(1)
            url = targets.get(name) or targets.get(name.lower())
            return f"[{name}]({url})" if url else name
        text = re.sub(r"`([^`]+?)`_" + _REF_SUFFIX, _resolve_named_ref, text)
    else:
        text = re.sub(r"`([^`]+?)`_" + _REF_SUFFIX, r"\1", text)

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
            # Preserve newlines so downstream cell processing can strip
            # per-line RST constructs (labels, nested directives, etc.).
            current_row.append("\n".join(l.rstrip() for l in current_cell_lines))

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


def _rows_to_md_table(rows: list[list[str]], header_count: int, file_id: str = "", targets=None, substitutions=None) -> list[str]:
    """Convert parsed rows to Markdown table lines."""
    if not rows:
        return []

    # Determine column count from widest row
    ncols = max(len(r) for r in rows) if rows else 0

    # Patterns that RST cells can carry but must not survive into Markdown cells
    _CELL_STRIP_RE = re.compile(
        r"^\s*("
        r"\.\.\s+_[a-zA-Z0-9_.-]+:"             # .. _label:
        r"|\.\.\s+_`[^`]+`:"                      # .. _`label with spaces`:
        r"|\.\.\s+\[[^\]]+\]"                     # .. [#footnote]
        r"|\.\.\s+[a-z][a-z_:-]*\s*::.*"          # nested directive (.. note::, .. java:method:: ..)
        r")\s*$"
    )

    def _cell(text: str) -> str:
        # Remove RST constructs that have no meaningful single-cell rendering.
        # Body-holding directives (code-block, note, tip, ...) encountered
        # inside a table cell drop the rest of the cell, because rendering a
        # multi-line code block inside a single Markdown table cell is not
        # well-defined and would anyway leak directive syntax.
        lines = text.split("\n")
        kept: list[str] = []
        skip_rest = False
        for l in lines:
            if skip_rest:
                continue
            if _CELL_STRIP_RE.match(l):
                stripped = l.strip()
                # If this is a standalone label/footnote line, skip only it;
                # if it introduces a directive (``.. name::``), drop the rest
                # of the cell to avoid leaking body content.
                if re.match(r"^\s*\.\.\s+[a-z][a-z_:-]*\s*::", l):
                    skip_rest = True
                continue
            kept.append(l)
        joined = " ".join(l.strip() for l in kept if l.strip())
        return _convert_inline(joined, file_id, targets, substitutions=substitutions).replace("|", "\\|")

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

def _parse_simple_table_cjk(block: list[str], file_id: str = "", targets=None, substitutions=None) -> list[str]:
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

    # Directive inside a simple-table cell (e.g. ``.. tip::`` / ``.. important::``).
    # Drop just the directive header line but keep body text so the readable
    # content of the cell is preserved.
    _CELL_DIRECTIVE_RE = re.compile(r'^\s*\.\.\s+[a-z][a-z_:-]*\s*::')

    # Pre-scan: count how many separator lines exist in total. If there are
    # exactly 2 (top + bottom), the table has no header row; if there are
    # 3 or more, the second one is the mid-separator marking the header.
    total_seps = sum(
        1 for line in block
        if line.strip() and all(c in "= " for c in line.strip())
    )

    # Group body lines by row. A new row starts when the first column has
    # non-whitespace content; subsequent lines that only fill later columns
    # (continuation) get merged into that row's cells. Separator lines
    # trigger header-count detection and reset skip state.
    grouped_rows: list[list[list[str]]] = []  # rows -> cells -> list of text fragments
    sep_count = 0
    head_count: int | None = None

    for line in block:
        s = line.rstrip()
        if not s:
            continue
        stripped = s.lstrip()
        if stripped and all(c in "= " for c in stripped):
            sep_count += 1
            # Only treat a mid-separator as a header marker when the table
            # actually has 3+ separators (top + mid + bottom).
            if sep_count == 2 and head_count is None and total_seps >= 3:
                head_count = len(grouped_rows)
            continue
        # Drop the directive header line itself but keep its body on
        # subsequent lines.
        if _CELL_DIRECTIVE_RE.match(s):
            continue
        cells = split_row(s)
        first_col_has_text = bool(cells[0].strip()) if cells else False
        if first_col_has_text or not grouped_rows:
            grouped_rows.append([[c] if c else [] for c in cells])
        else:
            # Continuation: append each non-empty cell's text to the previous
            # row's corresponding cell.
            for ci, c in enumerate(cells):
                if ci < len(grouped_rows[-1]) and c:
                    grouped_rows[-1][ci].append(c)

    rows: list[list[str]] = [
        [" ".join(frag for frag in cell if frag) for cell in row]
        for row in grouped_rows
    ]

    if head_count is None:
        head_count = 0

    return _rows_to_md_table(rows, head_count, file_id, targets, substitutions)


def _parse_simple_table(block: list[str], file_id: str = "", targets=None, substitutions=None) -> list[str]:
    """Convert RST simple table to Markdown table using docutils SimpleTableParser.

    For blocks containing CJK characters, skip docutils and use the
    CJK-safe display-width parser directly, because docutils
    SimpleTableParser splits by code-point index and gets column boundaries
    wrong when cell content mixes CJK (width 2) with ASCII (width 1).
    """
    if not block:
        return []

    # If any block line contains a CJK char outside the separator rows,
    # prefer the CJK-safe parser.
    import unicodedata
    def _has_wide(s: str) -> bool:
        return any(unicodedata.east_asian_width(c) in ("W", "F") for c in s)
    if any(_has_wide(ln) for ln in block):
        return _parse_simple_table_cjk(block, file_id, targets=targets, substitutions=substitutions)

    try:
        sl = StringList(block)
        parser = SimpleTableParser()
        tabledata = parser.parse(sl)
    except Exception:
        return _parse_simple_table_cjk(block, file_id, targets=targets, substitutions=substitutions)

    colspecs, headrows, bodyrows = tabledata

    _CELL_DIRECTIVE_RE = re.compile(r'^\s*\.\.\s+[a-z][a-z_:-]*\s*::')

    def _to_rows(rows_raw) -> list[list[str]]:
        out = []
        for row in rows_raw:
            cells = []
            for cell in row:
                # cell format: [morerows, morecols, offset, StringList]
                content = cell[3] if len(cell) >= 4 else []
                # Drop directive header lines (``.. tip::`` / ``.. code-block::``
                # etc.) but keep their body text so the content that readers
                # see is preserved. Code-block bodies are flattened as plain
                # prose to fit one table cell.
                kept = []
                for line in content:
                    if _CELL_DIRECTIVE_RE.match(line):
                        continue
                    kept.append(line)
                text_parts = [line.strip() for line in kept if line.strip()]
                cells.append(" ".join(text_parts))
            out.append(cells)
        return out

    head_rows = _to_rows(headrows)
    body_rows = _to_rows(bodyrows)
    all_rows = head_rows + body_rows
    return _rows_to_md_table(all_rows, len(head_rows), file_id, targets, substitutions)


# ---------------------------------------------------------------------------
# Grid table parser (custom — CJK-safe)
# ---------------------------------------------------------------------------

def _parse_grid_table(block: list[str], file_id: str = "", targets=None, substitutions=None) -> list[str]:
    """Convert RST grid table to Markdown table.

    Uses display-width column boundaries from the first ``+---+`` separator
    so that inline ``|`` (e.g. line-block markers inside a cell) is not
    mistaken for a column divider. Works correctly with CJK characters,
    which break docutils GridTableParser due to display-width vs
    code-point-width mismatch.

    The output is a standard MD table so that docs/ rendering and
    verify's tokenizer-based normalisation both see a single canonical
    form.
    """
    if not block:
        return []

    def _is_sep(line: str) -> bool:
        s = line.rstrip()
        return bool(s) and s[0] == "+" and all(c in "+-=|" for c in s)

    def _is_header_sep(line: str) -> bool:
        return _is_sep(line) and "=" in line

    # Column boundaries (in display width, not code points) from the first
    # separator line. Only ``|`` whose display-width position matches a ``+``
    # in the separator is a cell border; pipes at other positions are inline
    # text (e.g. ``|br|`` substitution references).
    import unicodedata

    def _dw(c: str) -> int:
        return 2 if unicodedata.east_asian_width(c) in ("F", "W") else 1

    def _display_positions(line: str) -> list[int]:
        """Return display-width position of each character's start."""
        pos = [0] * (len(line) + 1)
        for i, c in enumerate(line):
            pos[i + 1] = pos[i] + _dw(c)
        return pos

    boundaries_w: list[int] = []
    for line in block:
        if _is_sep(line):
            pos = _display_positions(line)
            boundaries_w = [pos[i] for i, c in enumerate(line) if c == "+"]
            break

    def _split_cells(line: str) -> list[str]:
        """Split a content row at display-width column boundaries. Pipes
        inside a cell (e.g. ``|br|`` substitutions) are preserved as inline
        text because they sit at positions that aren't cell borders."""
        if not boundaries_w or len(boundaries_w) < 2:
            parts = line.split("|")
            return [p.strip() for p in parts[1:-1]] if len(parts) >= 3 else []
        # Map each character's display-width start position.
        pos = _display_positions(line)
        # For each boundary width, find the code-point index at that width
        # (or just past the line end). A trailing row can be shorter than the
        # separator — in that case the remaining cells are empty.
        def _idx_at_width(w: int) -> int:
            # position array: pos[i] = width before char i. We want smallest
            # i such that pos[i] >= w. Characters wider than 1 can straddle a
            # boundary; treat the straddling char as belonging to the cell on
            # the left (i.e. pick i where pos[i] >= w is first true).
            for i, p in enumerate(pos):
                if p >= w:
                    return i
            return len(line)
        cells: list[str] = []
        for i in range(len(boundaries_w) - 1):
            left_w = boundaries_w[i]
            right_w = boundaries_w[i + 1]
            # Cell content sits between the two boundaries. Use code-point
            # indices inferred from display positions.
            left_idx = _idx_at_width(left_w) + 1  # skip the pipe itself
            right_idx = _idx_at_width(right_w)
            if left_idx > len(line):
                cells.append("")
                continue
            chunk = line[left_idx:right_idx]
            cells.append(chunk.strip())
        return cells

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

    # Collect header and body rows from all groups as flat lists.
    header_rows_raw: list[list[str]] = []
    body_rows_raw: list[list[str]] = []

    _CELL_DIRECTIVE_RE = re.compile(r'^\s*\.\.\s+[a-z][a-z_:-]*\s*::')

    def _is_sub_separator(cells: list[str]) -> bool:
        non_empty = [c for c in cells if c]
        if not non_empty:
            return False
        return all(set(c) <= set("-=+ ") for c in non_empty)

    for is_header, content_lines in groups:
        if not content_lines:
            continue

        rows: list[list[str]] = []
        for cl in content_lines:
            cells = _split_cells(cl)
            if not cells:
                continue
            if _is_sub_separator(cells):
                rows.append(["" for _ in cells])
                continue
            if not rows or any(c for c in cells):
                if rows and not any(r for r in rows[-1]):
                    rows[-1] = cells
                else:
                    rows.append(cells)
            else:
                for ci, c in enumerate(cells):
                    if ci < len(rows[-1]) and c:
                        rows[-1][ci] = (rows[-1][ci] + " " + c).strip()

        rows = [r for r in rows if any(c for c in r)]
        if not rows:
            continue

        # Drop rows that leak RST directive syntax.
        rows = [r for r in rows if not any(_CELL_DIRECTIVE_RE.match(c) for c in r if c)]
        if not rows:
            continue

        if is_header:
            header_rows_raw.extend(rows)
        else:
            body_rows_raw.extend(rows)

    all_rows = header_rows_raw + body_rows_raw
    if not all_rows:
        return []

    return _rows_to_md_table(
        all_rows,
        len(header_rows_raw),
        file_id,
        targets,
        substitutions,
    )


# ---------------------------------------------------------------------------
# Content converter
# ---------------------------------------------------------------------------

# RST field-list entry inside an admonition: ``:name: value``. Require at
# least one whitespace after the closing ``:`` so that inline roles like
# ``:java:extdoc:`Name``` (no space before the role target) are not mis-read
# as field-list entries.
_FIELD_RE_ADMON = re.compile(r"^:([^:\s]+):\s+(.*)")


def _render_admonition_body(
    label: str,
    inline_arg: str,
    block: list[str],
    file_id: str,
    targets,
    source_dir,
    substitutions=None,
) -> list[str]:
    """Render an admonition as '> **label:** ...' + converted body.

    Nested directives (code-block, lists, tables, etc.) are preserved by
    recursively running the body through _convert_content.
    """
    # 1) Split block into leading prose lines (flowing text) and a tail that
    #    may contain nested structure. A tail starts at the first line that
    #    introduces a nested directive *or* a structural construct such as a
    #    bullet list, enumerated list, or definition list — flattening them
    #    into a single prose blockquote loses the list structure.
    directive_start = re.compile(r"^\.\.\s+\S")
    bullet_start = re.compile(r"^[*+\-][ \t]+\S")
    enum_start = re.compile(r"^\d+\.[ \t]+\S")
    prose_parts: list[str] = []
    if inline_arg:
        prose_parts.append(inline_arg)

    tail_start = None
    for idx, l in enumerate(block):
        s = l.strip()
        if not s:
            # blank line — keep searching; do not commit to prose yet
            continue
        if directive_start.match(s) or bullet_start.match(s) or enum_start.match(s):
            tail_start = idx
            break
        m = _FIELD_RE_ADMON.match(s)
        if m:
            value = m.group(2).strip()
            if value:
                prose_parts.append(value)
        else:
            prose_parts.append(s)

    result: list[str] = []
    body = " ".join(prose_parts).strip()
    if body or not prose_parts:
        body_md = _convert_inline(body, file_id, targets, substitutions=substitutions) if body else ""
        result.append(f"> **{label}:** {body_md}")
    if tail_start is not None:
        tail = block[tail_start:]
        nested = _convert_content(tail, file_id, targets, source_dir, substitutions=substitutions)
        if nested.strip():
            result.append("")
            result.append(nested)
    return result


def _convert_content(raw_lines: list[str], file_id: str = "", targets: dict[str, str] | None = None, source_dir: "Path | None" = None, substitutions: dict[str, str] | None = None) -> str:
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

        # RST comment: `..` alone, or `..<space>...` not followed by a
        # recognised directive (e.g. `..    .. image:: ...`). Consume the
        # indented block so nested pseudo-directives do not leak.
        if stripped == ".." or (
            stripped.startswith(".. ")
            and not re.match(r"\.\.\s+_", stripped)
            and not re.match(r"\.\.\s+\[[^\]]+\]", stripped)
            and not re.match(r"\.\.\s+[a-z][a-z_:-]*\s*::", stripped)
            and not re.match(r"\.\.\s+\|[^|]+\|", stripped)
        ):
            _, i = _read_block(lines, i + 1)
            continue

        # RST anonymous target: __
        if stripped == "__":
            i += 1
            continue

        # RST hyperlink target: .. _`text`: url  or  .. target_: url
        if re.match(r"\.\.\s+_", stripped) and ":" in stripped:
            i += 1
            continue

        # RST footnote / citation target — extract inline text + block body.
        # Accept both `.. [#name] text` (inline text follows `]`) and
        # `.. [#name]` (no inline text; body on indented continuation lines).
        # Footnote labels allow `-` per docutils (e.g. `#thread-unsafe`).
        m_fn = re.match(r"\.\.\s+\[(?:[0-9]+|\*|#[a-zA-Z0-9_-]*)\](?:\s+(.*))?$", stripped)
        if m_fn:
            inline_text = (m_fn.group(1) or "").strip()
            block, i = _read_block(lines, i + 1)
            fn_lines = ([inline_text] if inline_text else []) + [b for b in block if b.strip()]
            for fl in fn_lines:
                output.append(_convert_inline(fl, file_id, targets, substitutions=substitutions))
            continue

        # Substitution definition: .. |name| directive:: args
        m_subst = re.match(r"\s*\.\.\s+\|[^|]+\|\s+[a-z_-]+::", stripped)
        if m_subst:
            _, i = _read_block(lines, i + 1)
            continue

        # Directive: .. name::  (also tolerate typo `.. name ::` with extra space).
        # Directive names can contain colons in domain-specific RST extensions
        # (e.g. ``.. java:method::``) so we accept ``[a-z][a-z_:-]*``.
        m = re.match(r"(\s*)\.\.\s+([a-z][a-z_:-]*)\s*::(.*)", line)
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
                label = ADMONITION_LABELS[directive]
                output.extend(_render_admonition_body(label, inline_arg, block, file_id, targets, source_dir, substitutions))
                continue

            # --- admonition (custom title) ---
            if directive == "admonition":
                block, i = _read_block(lines, i + 1)
                label = inline_arg or "Note"
                output.extend(_render_admonition_body(label, "", block, file_id, targets, source_dir, substitutions))
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
                md_lines = _rows_to_md_table(rows, header_rows, file_id, targets, substitutions)
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
                md_lines = _rows_to_md_table(rows, header_rows, file_id, targets, substitutions)
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
                    md_lines = _parse_grid_table(content, file_id, targets=targets, substitutions=substitutions)
                else:
                    md_lines = _parse_simple_table(content, file_id, targets=targets, substitutions=substitutions)
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
                title = _convert_inline(inline_arg, file_id, targets, substitutions=substitutions)
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
            output.extend(_parse_simple_table(stripped_block, file_id, targets=targets, substitutions=substitutions))
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
            output.extend(_parse_grid_table(stripped_block, file_id, targets=targets, substitutions=substitutions))
            continue

        # Regular paragraph / list item / other content
        converted = _convert_inline(stripped, file_id, targets, substitutions=substitutions)
        output.append(converted)
        i += 1

    return "\n".join(output).strip()


# ---------------------------------------------------------------------------
# No-knowledge-content detection
# ---------------------------------------------------------------------------

def _detect_no_knowledge_content(preamble_content: str, sections: list[Section]) -> bool:
    """Return True if the file has no meaningful content.

    A file is no-knowledge-content when its preamble is empty and every
    section (after directive processing) contains only whitespace.
    Typical cases: toctree-only files, navigation indices, label-only stub pages.
    """
    if preamble_content.strip():
        return False
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

    # Pre-resolve :ref:`label` using label_map before tokenizing. Inside
    # simple-table and grid-table blocks, pad (or truncate) the replacement
    # text to preserve the display-width of the original ``:ref:`` markup so
    # that column boundaries defined by the separator row remain aligned.
    if label_map:
        import unicodedata

        def _disp_width(s: str) -> int:
            return sum(2 if unicodedata.east_asian_width(c) in ("F", "W") else 1 for c in s)

        def _resolve(inner: str) -> str | None:
            if "<" in inner:
                return None
            label = inner.strip()
            return label_map.get(label, label)

        def _presolve_outside_table(line: str) -> str:
            def _sub(m: re.Match) -> str:
                repl = _resolve(m.group(1))
                return repl if repl is not None else m.group(0)
            return re.sub(r":ref:`([^`]+)`", _sub, line)

        def _presolve_in_table(line: str) -> str:
            """Pad/truncate ``:ref:`` replacement to the original display
            width so table column positions do not shift."""
            def _sub(m: re.Match) -> str:
                repl = _resolve(m.group(1))
                if repl is None:
                    return m.group(0)
                orig_width = _disp_width(m.group(0))
                repl_width = _disp_width(repl)
                if repl_width < orig_width:
                    return repl + " " * (orig_width - repl_width)
                return repl
            return re.sub(r":ref:`([^`]+)`", _sub, line)

        lines_in = source.split("\n")
        lines_out: list[str] = []
        i = 0
        while i < len(lines_in):
            line = lines_in[i]
            stripped = line.strip()
            is_simple_sep = bool(re.match(r"^={3,}(\s+={3,})+\s*$", stripped))
            is_grid_sep = bool(re.match(r"^\+[-=+]+", stripped))
            if is_simple_sep or is_grid_sep:
                lines_out.append(line)
                i += 1
                if is_simple_sep:
                    last_was_sep = True
                    while i < len(lines_in):
                        tl = lines_in[i]
                        ts = tl.strip()
                        is_sep = bool(ts) and all(c in "= " for c in ts) and ts.startswith("=")
                        if is_sep:
                            lines_out.append(tl)
                            last_was_sep = True
                            i += 1
                        elif not ts:
                            if last_was_sep:
                                break
                            lines_out.append(tl)
                            i += 1
                        else:
                            lines_out.append(_presolve_in_table(tl))
                            last_was_sep = False
                            i += 1
                else:  # grid
                    while i < len(lines_in):
                        tl = lines_in[i]
                        ts = tl.strip()
                        if ts.startswith("+") or ts.startswith("|"):
                            if ts.startswith("+"):
                                lines_out.append(tl)
                            else:
                                lines_out.append(_presolve_in_table(tl))
                            i += 1
                        else:
                            break
                continue
            lines_out.append(_presolve_outside_table(line))
            i += 1
        source = "\n".join(lines_out)

    lines = source.splitlines(keepends=True)
    heading_keys = _detect_heading_chars([l.rstrip("\n") for l in lines])
    title, preamble_lines, raw_sections = _split_sections(
        [l.rstrip("\n") for l in lines], heading_keys
    )

    # Collect named hyperlink targets from the whole source (first pass)
    targets = _collect_targets([l.rstrip("\n") for l in lines])
    if extra_targets:
        targets.update(extra_targets)
    substitutions = _collect_substitutions([l.rstrip("\n") for l in lines])

    preamble_md = _convert_content(preamble_lines, file_id, targets or None, source_dir, substitutions=substitutions or None)

    sections: list[Section] = []
    for sec_title, sec_lines in raw_sections:
        md = _convert_content(sec_lines, file_id, targets or None, source_dir, substitutions=substitutions or None)
        sections.append(Section(title=sec_title, content=md))

    no_knowledge = _detect_no_knowledge_content(preamble_md, sections)

    return RSTResult(
        title=title,
        no_knowledge_content=no_knowledge,
        content=preamble_md,
        sections=sections,
    )
