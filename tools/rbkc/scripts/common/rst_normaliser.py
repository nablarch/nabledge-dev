"""RST source normaliser (tokenizer) — Phase 21-X.

Converts RST source text into an MD-equivalent normalised form so that
verify can substring-delete JSON content from the normalised source.

Spec: rbkc-verify-quality-design.md §3-1 手順 0.

Pure RST-spec logic; shared between create (indirectly) and verify
(scripts/verify/verify.py). Must not depend on RBKC implementation.

Public API:
    normalise_rst(text, *, label_map=None, source_path=None, strict_unknown=False) -> str

Exceptions:
    UnknownSyntaxError — unknown directive / undefined substitution / syntax
"""
from __future__ import annotations

import re
from pathlib import Path

from scripts.common.rst_substitutions import (
    collect_substitutions,
    expand_substitutions,
    UndefinedSubstitutionError,
)
from scripts.common.rst_include import expand_includes


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class UnknownSyntaxError(Exception):
    """Raised when normaliser encounters an unknown RST construct."""


# ---------------------------------------------------------------------------
# Closed sets (from Phase 21-X X-2 scan)
# ---------------------------------------------------------------------------

# Known role names: ref, doc, java:extdoc, download, javadoc_url.
# Unknown roles are not hard-failed here because verify may be called on
# sections or snippets where the role list isn't fully validated.

# Directive groups
_FENCED_CODE_DIRECTIVES = {"code-block", "sourcecode", "literalinclude"}
_ADMONITION_DIRECTIVES = {
    "note", "tip", "warning", "important", "attention",
    "hint", "admonition", "caution", "danger", "error", "seealso",
    "deprecated", "versionadded", "versionchanged",
}

# Labels emitted by the converter as the admonition header:
#   "> **<Label>:** <body>"
# Match the converter's formatting so normalised source substring-matches JSON.
_ADMONITION_LABELS = {
    "note": "Note",
    "tip": "Tip",
    "warning": "Warning",
    "important": "Important",
    "attention": "Attention",
    "hint": "Hint",
    "admonition": "Note",  # default when no arg
    "caution": "Caution",
    "danger": "Danger",
    "error": "Error",
    "seealso": "See Also",
    "deprecated": "Deprecated",
    "versionadded": "Version Added",
    "versionchanged": "Version Changed",
}
_TABLE_DIRECTIVES = {"list-table", "table", "csv-table"}
_FIGURE_DIRECTIVES = {"figure"}
_IMAGE_DIRECTIVES = {"image"}
_INCLUDE_DIRECTIVES = {"include"}
_DROP_DIRECTIVES = {
    "toctree", "contents", "raw", "class", "rubric",
    "function", "java:method",
    # Less common but observed
    "only", "ifconfig", "sectnum", "header", "footer", "meta",
    "highlight", "default-role",
}

_KNOWN_DIRECTIVES = (
    _FENCED_CODE_DIRECTIVES
    | _ADMONITION_DIRECTIVES
    | _TABLE_DIRECTIVES
    | _FIGURE_DIRECTIVES
    | _IMAGE_DIRECTIVES
    | _INCLUDE_DIRECTIVES
    | _DROP_DIRECTIVES
)


# Heading underline characters (per docutils § Sections).
_HEADING_CHARS = set('=-~^"\'`#*+<>:._')
_HEADING_UNDERLINE_RE = re.compile(r"^([=\-~^\"'`#*+<>:._])\1{2,}\s*$")

# Directive header: `.. name:: args` (also tolerate typo `.. name ::` with
# extra space before the trailing ``::``).
_DIRECTIVE_HEAD_RE = re.compile(r"^(?P<indent>\s*)\.\.\s+(?P<name>[A-Za-z][A-Za-z0-9_:-]*)\s*::(?P<args>.*)$")

# Substitution definition header (collected separately; skipped in tokenizer body)
_SUBST_DEF_HEAD_RE = re.compile(r"^\s*\.\.\s+\|([^|]+)\|\s+[a-z_-]+::.*$")

# Label definition: `.. _label:` (may stack before a heading)
# Label definition: allow `.` in label name (RST accepts).
_LABEL_DEF_RE = re.compile(r"^\s*\.\.\s+_[A-Za-z0-9_.-]+:\s*$")

# Footnote / citation definition: `.. [#name] text` or `.. [1] text`
# The text (and any indented continuation body) is emitted as prose.
_FOOTNOTE_DEF_RE = re.compile(r"^\s*\.\.\s+\[([0-9]+|\*|#[A-Za-z0-9_-]*)\]\s*(.*)$")

# Comment: `.. ` followed by anything that's NOT a directive (handled during
# directive parsing; leftover comments caught here).
_COMMENT_RE = re.compile(r"^\s*\.\.\s+(?![A-Za-z][A-Za-z0-9_:-]*::)\S.*$|^\s*\.\.\s*$")

# Field list line: `:name: value` (value may be empty)
_FIELD_LIST_RE = re.compile(r"^(?P<indent>\s*):(?P<name>[A-Za-z][^:\n]*):\s*(?P<value>.*)$")

# Simple-table separator: `=== ===` or `- -` etc.
_SIMPLE_TABLE_SEP_RE = re.compile(r"^\s*=+(?: +=+)+\s*$")

# Grid-table separator: `+---+---+` or `+===+===+`
_GRID_TABLE_SEP_RE = re.compile(r"^\s*\+[-=]+(?:\+[-=]+)+\+\s*$")

# Line block: line starting with `|` followed by space or end.
_LINE_BLOCK_RE = re.compile(r"^\s*\|\s?(.*)$")

# Bullet list markers
_BULLET_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[*+\-])\s+(?P<body>\S.*)$")
_ENUM_RE = re.compile(
    r"^(?P<indent>\s*)(?P<marker>"
    r"\(?[0-9]+[\.\)]|\(?[A-Za-z][\.\)]|#\."
    r")\s+(?P<body>\S.*)$"
)


# ---------------------------------------------------------------------------
# Inline transforms
# ---------------------------------------------------------------------------

# Sentinels protect emitted backticks from the later interpreted-text regex
# which strips bare backticks. Each sentinel is a *single* ASCII character
# that never appears in RST prose, so that simple-table column splitting
# (which uses display width) aligns with the original `` ``...`` `` span:
# two opening/closing backticks of display width 2 match two single-char
# sentinels of display width 2.
_SENT_L = "\x02\x02"
_SENT_R = "\x03\x03"


def _apply_inline_transforms(text: str, label_map: dict[str, str]) -> str:
    """Apply inline transforms in a specific, non-order-sensitive way.

    Inline substitutions operate on disjoint syntactic forms whose regexes
    are designed to match distinct constructs. Apply each once, from most
    specific to most general.
    """

    # 1. Role with target — match converter behaviour exactly:
    #   - :ref:`text <label>`   → visible text
    #   - :doc:`text <path>`    → visible text
    #   - :java:extdoc:`Name <fqn>` → `Name` (code-quoted)
    #   - :javadoc_url:`text <path>` → [text](path)
    #   - :download:`text <path>`   → [text](path) (converter rewrites asset dir; URL strip aligns both sides)
    def _role_target(m: re.Match) -> str:
        role, text, target = m.group(1), m.group(2).strip(), m.group(3).strip()
        if role == "java:extdoc":
            return f"{_SENT_L}{text or target}{_SENT_R}"
        if role == "javadoc_url":
            return f"[{text or target}]({target})"
        if role == "download":
            return f"[{text or target}]({target})"
        # :ref: / :doc: / unknown → visible text only
        return text or target

    text = re.sub(
        r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`<>]*)<([^`<>]+)>`",
        _role_target,
        text,
    )

    # 2. Role simple (no target):
    #   - :ref:`label`       → resolved section title (or label if unknown)
    #   - :doc:`path`        → path
    #   - :java:extdoc:`N`   → `N` (code-quoted)
    #   - default            → inner text
    def _role_simple(m: re.Match) -> str:
        role, inner = m.group(1), m.group(2)
        if role == "java:extdoc":
            return f"{_SENT_L}{inner}{_SENT_R}"
        if role == "ref":
            return label_map.get(inner, inner)
        return inner

    text = re.sub(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`]+)`", _role_simple, text)

    # 3. External link: `text <url>`_ / __ → [text](url)
    def _ext_link(m: re.Match) -> str:
        return f"[{m.group(1).strip()}]({m.group(2).strip()})"

    text = re.sub(r"`([^`<]+?)\s*<([^`<>]+)>`_+", _ext_link, text)

    # 4. Double-backtick literal: ``code`` → sentinel+content+sentinel, so
    #    later single-backtick-stripping (interpreted text) leaves it alone.
    text = re.sub(r"``([^`]+?)``", lambda m: _SENT_L + m.group(1) + _SENT_R, text)

    # 5. Named reference: `text`_ → text
    text = re.sub(r"(?<![`:])`([^`<>\n]+?)`_(?!_)", r"\1", text)

    # 6. Interpreted text (bare single backtick): RST default role passes
    # through to converter as `text` (MD inline code). Keep backticks.
    # (No change needed; text is already in MD form.)

    return text


def _restore_sentinels(text: str) -> str:
    """Swap backtick sentinels back to single backticks.

    Called after block-level rendering so that column-width measurements
    in simple-tables use the sentinel placeholder (which matches the raw
    RST source width) rather than the narrower single-backtick form.
    """
    return text.replace(_SENT_L, "`").replace(_SENT_R, "`")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def normalise_rst(
    text: str,
    *,
    label_map: dict[str, str] | None = None,
    source_path: Path | str | None = None,
    strict_unknown: bool = True,
) -> str:
    """Normalise RST source text to MD-equivalent form.

    If *source_path* is given, `.. include::` directives are expanded
    before normalisation. Otherwise includes are left in place (and will
    be reported as unknown syntax via their include targets).

    *label_map* resolves `:ref:`label`` to the label's target title.

    *strict_unknown* = True (default) makes unknown directives raise
    UnknownSyntaxError; = False leaves them as-is (useful for diagnostics).
    """
    label_map = label_map or {}

    # Step A: expand includes, if a source_path is provided
    if source_path is not None:
        text = expand_includes(source_path)

    # Step B: collect substitutions BEFORE stripping definitions
    subs = collect_substitutions(text)

    # Step C: strip substitution definition blocks (so the header line isn't
    # processed as a reference later)
    text = _strip_substitution_definitions(text)

    # Step D: strip label definition lines
    text = _strip_label_definitions(text)

    # Step E: line-continuation. RST `\<newline>` escapes the newline. The
    # converter preserves the literal backslash in MD output with a trailing
    # space. Replace only when the next visible char is prose (not a structural
    # separator like =/+/- that would break table/heading detection).
    def _continuation(m: re.Match) -> str:
        tail = m.group(1).lstrip()
        if not tail:
            # Trailing `\` at end of file or before blank → drop the newline
            return r"\ "
        first = tail[0]
        if first in "=+-~^#*<>:._`\"'|":
            # Next line begins with a potential structural marker (table/heading)
            # — keep the newline so detection still works.
            return f"\\\n{m.group(1)}"
        return r"\ " + tail

    text = re.sub(r"\\\n([^\n]*)", _continuation, text)

    # Step F: inline transforms (roles, backticks, links) — must precede the
    # block walker so that constructs like `:ref:`label`` are not misread as
    # standalone field-list lines (`:name: value`).
    text = _apply_inline_transforms(text, label_map)

    # Step G: expand substitution references against the body prose.
    # Non-strict when not enforcing unknown syntax: leave `|x|`-shaped
    # prose that isn't a real substitution (IP addresses, command args) alone.
    try:
        text = expand_substitutions(text, subs, strict=strict_unknown)
    except UndefinedSubstitutionError:
        if strict_unknown:
            raise

    # Step G2: detect section heading levels (by first-appearance order of
    # underline char, matching converter's logic).
    heading_keys = _detect_heading_keys(text)

    # Step H: walk lines, collapsing directives/tables/headings/lists/comments
    normalised = _walk_blocks(
        text, label_map, heading_keys=heading_keys, strict_unknown=strict_unknown
    )

    # Step H2: restore backtick sentinels after block-level work (widths
    # measured for simple-tables used the sentinel placeholder).
    normalised = _restore_sentinels(normalised)

    # Step I: whitespace collapse on each line (preserve newlines)
    out_lines = []
    for line in normalised.split("\n"):
        out_lines.append(re.sub(r"[ \t]+", " ", line).rstrip())
    normalised = "\n".join(out_lines)
    # Collapse 3+ consecutive blanks to 2 for readability, but don't strip.
    normalised = re.sub(r"\n{3,}", "\n\n", normalised)
    return normalised.strip()


# ---------------------------------------------------------------------------
# Definition stripping
# ---------------------------------------------------------------------------

def _strip_substitution_definitions(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _SUBST_DEF_HEAD_RE.match(line):
            header_indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                cur_indent = len(bl) - len(bl.lstrip())
                if cur_indent > header_indent:
                    i += 1
                    continue
                break
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _strip_label_definitions(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n") if not _LABEL_DEF_RE.match(line)
    )


# ---------------------------------------------------------------------------
# Block walker
# ---------------------------------------------------------------------------

def _detect_heading_keys(text: str) -> list[tuple[bool, str]]:
    """First-appearance order of (is_overline, underline_char) tuples.

    Matches the converter's _detect_heading_chars so the normaliser assigns
    the same MD heading levels as the converter.
    """
    keys: list[tuple[bool, str]] = []
    lines = text.split("\n")
    i = 0
    n = len(lines)

    def _underline(s: str) -> bool:
        return _HEADING_UNDERLINE_RE.match(s) is not None

    while i < n:
        line = lines[i]
        # Overline style: underline / title / underline
        if (
            i + 2 < n
            and _underline(line)
            and lines[i + 1].strip()
            and not _underline(lines[i + 1])
            and _underline(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            key = (True, line.rstrip()[0])
            if key not in keys:
                keys.append(key)
            i += 3
            continue
        # Underline-only
        if (
            i + 1 < n
            and line.strip()
            and not _underline(line)
            and _underline(lines[i + 1])
            and not (
                i > 0
                and _underline(lines[i - 1])
                and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0]
            )
        ):
            key = (False, lines[i + 1].rstrip()[0])
            if key not in keys:
                keys.append(key)
            i += 2
            continue
        i += 1
    return keys


def _walk_blocks(
    text: str,
    label_map: dict[str, str],
    *,
    heading_keys: list[tuple[bool, str]] | None = None,
    strict_unknown: bool,
) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    heading_keys = heading_keys or []

    def _heading_level(key: tuple[bool, str]) -> int:
        try:
            # level index (0-based) → H level (1-based, capped at 6)
            return min(heading_keys.index(key) + 1, 6)
        except ValueError:
            return 1  # fallback

    while i < n:
        line = lines[i]

        # Overline heading: underline / title / underline (same char)
        if (
            i + 2 < n
            and _HEADING_UNDERLINE_RE.match(line)
            and lines[i + 1].strip()
            and not _HEADING_UNDERLINE_RE.match(lines[i + 1])
            and _HEADING_UNDERLINE_RE.match(lines[i + 2])
            and line.rstrip()[0] == lines[i + 2].rstrip()[0]
        ):
            title = lines[i + 1].strip()
            level = _heading_level((True, line.rstrip()[0]))
            out.append("#" * level + " " + title)
            i += 3
            continue

        # Underline heading: title / underline
        if (
            i + 1 < n
            and line.strip()
            and not _HEADING_UNDERLINE_RE.match(line)
            and _HEADING_UNDERLINE_RE.match(lines[i + 1])
            and not (
                i > 0
                and _HEADING_UNDERLINE_RE.match(lines[i - 1])
                and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0]
            )
        ):
            title = line.strip()
            level = _heading_level((False, lines[i + 1].rstrip()[0]))
            out.append("#" * level + " " + title)
            i += 2
            continue

        # Stray heading underline (no paired title) — drop
        if _HEADING_UNDERLINE_RE.match(line):
            i += 1
            continue

        # Simple-table start — re-render the whole block as MD table
        if _SIMPLE_TABLE_SEP_RE.match(line):
            rendered, next_i = _render_simple_table(lines, i)
            if rendered:
                out.append(rendered)
            i = next_i
            continue

        # Grid-table separator — render the block as MD table
        if _GRID_TABLE_SEP_RE.match(line):
            rendered, next_i = _render_grid_table(lines, i)
            if rendered:
                out.append(rendered)
            i = next_i
            continue

        # Directive header
        m = _DIRECTIVE_HEAD_RE.match(line)
        if m:
            name = m.group("name").lower()
            args = m.group("args").strip()
            header_indent = len(m.group("indent"))
            body_lines, next_i = _collect_directive_body(lines, i, header_indent)
            i = next_i
            rendered = _render_directive(name, args, body_lines, label_map, strict_unknown=strict_unknown)
            if rendered:
                out.append(rendered)
            continue

        # Footnote / citation definition: emit the inline text and any
        # indented continuation body as prose (converter inlines these).
        fn = _FOOTNOTE_DEF_RE.match(line)
        if fn:
            inline = fn.group(2).strip()
            header_indent = len(line) - len(line.lstrip())
            body_lines: list[str] = []
            if inline:
                body_lines.append(inline)
            j = i + 1
            while j < n:
                bl = lines[j]
                if not bl.strip():
                    j += 1
                    continue
                cur_indent = len(bl) - len(bl.lstrip())
                if cur_indent > header_indent:
                    body_lines.append(bl.strip())
                    j += 1
                    continue
                break
            i = j
            if body_lines:
                out.append(" ".join(body_lines))
            continue

        # Standalone comment line
        if _COMMENT_RE.match(line):
            # Skip the comment and its indented continuation lines
            i += 1
            header_indent = 0
            while i < n:
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                cur_indent = len(bl) - len(bl.lstrip())
                if cur_indent > header_indent:
                    i += 1
                    continue
                break
            continue

        # Standalone field list: converter keeps `:name:` + body as
        # definition-list style text. Emit the field marker so both sides
        # align; the indented continuation body is handled as regular prose.
        fm = _FIELD_LIST_RE.match(line)
        if fm and fm.group("value") is not None:
            name = fm.group("name").strip()
            value = fm.group("value").strip()
            if value:
                out.append(f":{name}: {value}")
            else:
                out.append(f":{name}:")
            i += 1
            continue

        # Bullet list marker — preserve the original marker (*/-/+) and
        # body. Converter passes through MD-compatible bullets.
        bm = _BULLET_RE.match(line)
        if bm:
            marker = bm.group("marker")
            out.append(f"{bm.group('indent')}{marker} {bm.group('body')}")
            i += 1
            continue

        # Enumerated list marker — preserve in MD form (`1. body`).
        em = _ENUM_RE.match(line)
        if em:
            marker = em.group("marker")
            # Normalise (1) / 1) / a. to MD numeric form; keep 1. as-is.
            m_num = re.match(r"\(?(\d+)[\.\)]", marker)
            if m_num:
                norm_marker = f"{m_num.group(1)}."
            else:
                norm_marker = marker  # e.g. "a." or "#."
            out.append(f"{em.group('indent')}{norm_marker} {em.group('body')}")
            i += 1
            continue

        # Line block — converter preserves the leading `| ` marker in JSON,
        # so keep it in the normalised source for substring alignment.
        lbm = _LINE_BLOCK_RE.match(line)
        if lbm:
            content = lbm.group(1)
            if content.strip() or line.strip() == "|":
                out.append(f"| {content}" if content else "|")
                i += 1
                continue

        # Grid-table cell line: `| text | text |` — strip pipes, keep text
        if line.strip().startswith("|") and line.strip().endswith("|"):
            inner = line.strip().strip("|").strip()
            # split on pipes and rejoin with spaces
            cells = [c.strip() for c in inner.split("|")]
            out.append(" ".join(cells))
            i += 1
            continue

        out.append(line)
        i += 1

    return "\n".join(out)


def _collect_directive_body(lines: list[str], start: int, header_indent: int) -> tuple[list[str], int]:
    """Collect the indented body of a directive starting at *start*.

    Returns (body_lines, next_index). Body lines retain their original
    text (relative indentation may be dedented later by the renderer).
    """
    body: list[str] = []
    i = start + 1
    body_indent: int | None = None
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            body.append(line)
            i += 1
            continue
        cur_indent = len(line) - len(line.lstrip())
        if cur_indent <= header_indent:
            break
        if body_indent is None:
            body_indent = cur_indent
        body.append(line)
        i += 1
    # Drop trailing blank lines
    while body and not body[-1].strip():
        body.pop()
    # Dedent — only strip leading whitespace, not content. A line whose
    # leading whitespace is shorter than body_indent is a substitution-
    # expansion artefact (e.g. `|br|` expanded inside a cell to `\n `)
    # that should keep its visible text; strip only the whitespace that
    # is actually whitespace.
    if body_indent is not None and body_indent > 0:
        dedented = []
        for line in body:
            if line.strip():
                leading = len(line) - len(line.lstrip())
                strip_n = min(leading, body_indent)
                dedented.append(line[strip_n:])
            else:
                dedented.append("")
        body = dedented
    return body, i


def _render_simple_table(lines: list[str], start: int) -> tuple[str, int]:
    """Render an RST simple-table (`=== ===` separators) as an MD table.

    Column boundaries come from the separator *display* widths. CJK
    characters occupy two display columns, so we track display width
    rather than raw codepoint index when splitting rows.
    """
    import unicodedata

    def _char_width(c: str) -> int:
        return 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1

    def _display_len(s: str) -> int:
        return sum(_char_width(c) for c in s)

    def _slice_by_display(s: str, col_start: int, col_end: int | None) -> str:
        """Return the substring whose display columns overlap [col_start, col_end)."""
        out = []
        pos = 0
        for c in s:
            w = _char_width(c)
            cstart = pos
            cend = pos + w
            if cend <= col_start:
                pass
            elif col_end is not None and cstart >= col_end:
                break
            else:
                out.append(c)
            pos = cend
        return "".join(out)

    n = len(lines)
    sep_line = lines[start].rstrip()
    # Compute column ranges in display columns
    cols: list[tuple[int, int | None]] = []
    j = 0
    while j < len(sep_line):
        if sep_line[j] == '=':
            col_start = j
            while j < len(sep_line) and sep_line[j] == '=':
                j += 1
            cols.append((col_start, j))
        else:
            j += 1
    if not cols:
        return "", start + 1
    # Extend last column to infinity (accept content overshoot)
    if cols:
        cols[-1] = (cols[-1][0], None)

    def _split_row(ln: str) -> list[str]:
        return [
            _slice_by_display(ln, s, e).strip()
            for (s, e) in cols
        ]

    # Look ahead: count separators between this opening and the table end
    # to determine whether there's a mid-separator (header marker).
    look_seps = 0
    look_i = start + 1
    while look_i < n:
        ln = lines[look_i]
        if _SIMPLE_TABLE_SEP_RE.match(ln):
            look_seps += 1
            look_i += 1
            # After this sep, peek: if the next non-blank line is not
            # indented to the table's first column, we've hit the end.
            k = look_i
            while k < n and not lines[k].strip():
                k += 1
            if k >= n:
                break
            nxt = lines[k]
            nxt_indent = len(nxt) - len(nxt.lstrip())
            if nxt_indent < cols[0][0]:
                break
            continue
        if not ln.strip():
            look_i += 1
            continue
        nxt_indent = len(ln) - len(ln.lstrip())
        if nxt_indent < cols[0][0]:
            break
        look_i += 1
    # look_seps counts mid+closing. If look_seps >= 2 → has mid-sep.
    has_mid_sep = look_seps >= 2

    rows: list[list[str]] = []
    current_row: list[str] | None = None
    i = start + 1
    # Skip optional blank
    while i < n and not lines[i].strip():
        i += 1
    if has_mid_sep:
        # Consume header row(s) until the mid-separator.
        while i < n and not _SIMPLE_TABLE_SEP_RE.match(lines[i]):
            if not lines[i].strip():
                i += 1
                continue
            cells = _split_row(lines[i])
            if cells[0] == "" and rows:
                for idx, c in enumerate(cells):
                    if c:
                        rows[-1][idx] = (rows[-1][idx] + " " + c).strip() if rows[-1][idx] else c
            else:
                rows.append(cells)
            i += 1
        header_count = len(rows)
        # Skip the mid-separator
        if i < n and _SIMPLE_TABLE_SEP_RE.match(lines[i]):
            i += 1
    else:
        header_count = 0

    # Body rows until closing separator (or end). A blank line does NOT
    # end the current row — only a row whose first column is non-empty
    # starts a new row. This matches RST simple-table semantics (multi-
    # paragraph cells are separated by blank lines, continuations start
    # with empty first column).
    while i < n:
        ln = lines[i]
        if _SIMPLE_TABLE_SEP_RE.match(ln):
            if current_row is not None:
                rows.append(current_row)
                current_row = None
            i += 1
            break
        if not ln.strip():
            # Blank line inside a cell — treat as a space continuation
            i += 1
            continue
        cells = _split_row(ln)
        if cells[0] == "" and current_row is not None:
            for idx, c in enumerate(cells):
                if c:
                    current_row[idx] = (current_row[idx] + " " + c).strip() if current_row[idx] else c
        else:
            if current_row is not None:
                rows.append(current_row)
            current_row = cells
        i += 1

    if current_row is not None:
        rows.append(current_row)

    if not rows:
        return "", i

    ncols = len(cols)
    esc_rows = [[c.replace("|", "\\|") for c in r] for r in rows]
    sep = "|" + "|".join(["---"] * ncols) + "|"
    if has_mid_sep and header_count > 0:
        header_md = ["| " + " | ".join(r) + " |" for r in esc_rows[:header_count]]
        body_md = ["| " + " | ".join(r) + " |" for r in esc_rows[header_count:]]
        return "\n".join(header_md + [sep] + body_md), i
    # No mid-separator → all rows, then trailing separator
    all_rows = ["| " + " | ".join(r) + " |" for r in esc_rows]
    return "\n".join(all_rows + [sep]), i


def _render_grid_table(lines: list[str], start: int) -> tuple[str, int]:
    """Render an RST grid-table as an HTML `<table>` block.

    Uses display-width column boundaries from the first `+---+` separator
    so that inline `|` (e.g. line-block markers inside a cell) is not
    mistaken for a column divider.
    """
    import unicodedata as _ud

    def _dw(c: str) -> int:
        return 2 if _ud.east_asian_width(c) in ("W", "F") else 1

    def _display_positions(line: str) -> list[int]:
        pos = [0] * (len(line) + 1)
        for i, c in enumerate(line):
            pos[i + 1] = pos[i] + _dw(c)
        return pos

    n = len(lines)
    # Column boundaries in display width from first separator
    boundaries_w: list[int] = []
    for j in range(start, min(start + 20, n)):
        ln = lines[j]
        if _GRID_TABLE_SEP_RE.match(ln):
            pos = _display_positions(ln)
            boundaries_w = [pos[i] for i, c in enumerate(ln) if c == "+"]
            break

    def _idx_at_width(line: str, w: int) -> int:
        pos = _display_positions(line)
        for i, p in enumerate(pos):
            if p >= w:
                return i
        return len(line)

    def _split_cells(ln: str) -> list[str]:
        if not boundaries_w or len(boundaries_w) < 2:
            parts = ln.split("|")
            return [p.strip() for p in parts[1:-1]] if len(parts) >= 3 else []
        cells = []
        for i in range(len(boundaries_w) - 1):
            left_idx = _idx_at_width(ln, boundaries_w[i]) + 1
            right_idx = _idx_at_width(ln, boundaries_w[i + 1])
            if left_idx > len(ln):
                cells.append("")
                continue
            cells.append(ln[left_idx:right_idx].strip())
        return cells

    rows: list[tuple[bool, list[str]]] = []
    in_header = True
    i = start
    while i < n:
        ln = lines[i]
        if _GRID_TABLE_SEP_RE.match(ln):
            if '=' in ln:
                in_header = False
            i += 1
            if i < n and not (
                _GRID_TABLE_SEP_RE.match(lines[i])
                or (lines[i].strip().startswith("|") and lines[i].strip().endswith("|"))
            ):
                break
            continue
        if ln.strip().startswith("|") and ln.strip().endswith("|"):
            cells = _split_cells(ln)
            # Skip rows where every cell is empty — converter omits these.
            if cells and any(c for c in cells):
                rows.append((in_header, cells))
            i += 1
            continue
        break

    if not rows:
        return "", i

    # Emit HTML
    out = ["<table>"]
    header_rows = [r for hdr, r in rows if hdr]
    body_rows = [r for hdr, r in rows if not hdr]
    if header_rows:
        out.append("<thead>")
        for r in header_rows:
            out.append("<tr>")
            for c in r:
                out.append(f"  <th>{c}</th>")
            out.append("</tr>")
        out.append("</thead>")
    if body_rows:
        out.append("<tbody>")
        for r in body_rows:
            out.append("<tr>")
            for c in r:
                out.append(f"  <td>{c}</td>")
            out.append("</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out), i


def _split_directive_options(body: list[str]) -> tuple[dict[str, str], list[str]]:
    """Separate leading field-list option lines from the rest of the body."""
    options: dict[str, str] = {}
    i = 0
    while i < len(body):
        line = body[i]
        if not line.strip():
            i += 1
            continue
        m = _FIELD_LIST_RE.match(line)
        if not m:
            break
        options[m.group("name").strip().lower()] = m.group("value").strip()
        i += 1
    # Skip the single blank line separating options from body
    while i < len(body) and not body[i].strip():
        i += 1
    return options, body[i:]


# ---------------------------------------------------------------------------
# Directive rendering (7 groups)
# ---------------------------------------------------------------------------

def _render_directive(
    name: str,
    args: str,
    body: list[str],
    label_map: dict[str, str],
    *,
    strict_unknown: bool,
) -> str:
    options, body_rest = _split_directive_options(body)

    # Group A: fenced code
    if name in _FENCED_CODE_DIRECTIVES:
        lang = args.strip()
        body_text = "\n".join(body_rest).rstrip()
        return f"```{lang}\n{body_text}\n```"

    # Group B: admonition — emit MD blockquote with labelled header so the
    # normalised source matches converter output (which renders
    # `.. note::` as `> **Note:** ...`).
    if name in _ADMONITION_DIRECTIVES:
        body_text = "\n".join(body_rest)
        inner = _walk_blocks(body_text, label_map, strict_unknown=strict_unknown)
        inner_flat = re.sub(r'\s+', ' ', inner).strip()
        label = _ADMONITION_LABELS.get(name, name.capitalize())
        title_part = args.strip()
        if title_part and name == "admonition":
            return f"> **{title_part}** {inner_flat}"
        return f"> **{label}:** {inner_flat}"

    # Group C: table — drop argument (converter does not include table
    # title in JSON body; caption presence confirmed 0/100 in v6 empirical
    # scan), reconstruct cells as MD table.
    if name in _TABLE_DIRECTIVES:
        return _render_table_directive(name, body_rest)

    # Group D: figure — converter emits `![caption](assets/{id}/{filename})`.
    # First non-option body line is the caption. Use placeholder URL so
    # verify's URL-strip symmetrically removes both sides.
    if name in _FIGURE_DIRECTIVES:
        caption = ""
        for line in body_rest:
            if line.strip():
                caption = line.strip()
                break
        return f"![{caption}](image)"

    # Group E: image — converter emits `![alt](assets/{id}/{filename})`.
    # We don't know the file_id here; emit a placeholder MD image whose URL
    # will be stripped by the verify layer (both sides reduce to `![alt]`).
    if name in _IMAGE_DIRECTIVES:
        alt = options.get("alt", "")
        return f"![{alt}](image)"

    # Group F: include — should have been expanded already by expand_includes;
    # if seen here, the body was missing or include had no path.
    if name in _INCLUDE_DIRECTIVES:
        return ""

    # Group G: drop-body
    if name in _DROP_DIRECTIVES:
        return ""

    # Unknown directive → FAIL
    if strict_unknown:
        raise UnknownSyntaxError(f"unknown directive: {name}")
    return ""


def _render_table_directive(name: str, body: list[str]) -> str:
    """Extract visible text from a list-table/table/csv-table body as MD table rows.

    Converter emits MD table syntax (`| cell | cell |` with `|---|` separator),
    so the normalised source must match that structure.
    """
    if name == "list-table":
        # Parse rows by indentation: "* -" starts a row, "- " (at row indent)
        # starts a new cell in the same row, everything else is cell
        # continuation. Nested bullet lists (where a sub-list appears inside
        # a cell) must NOT be confused with new cells — detect them by
        # indent level.
        rows: list[list[str]] = []
        current_row: list[str] | None = None
        current_cell_idx = -1
        # Row indent = indent of "* -"; cell indent = indent of "-" (same
        # column as `*`). Sub-content deeper than cell indent is continuation.
        row_indent: int | None = None
        cell_indent: int | None = None
        for line in body:
            if not line.strip():
                continue
            lstrip = len(line) - len(line.lstrip())
            stripped = line.lstrip()
            # "* - cell" or "* -" at the row-indent level starts a new row.
            # Nested bullets deeper than row_indent are cell continuation.
            is_row_marker = (
                (stripped.startswith("* -") or stripped == "*" or stripped.startswith("* "))
                and (row_indent is None or lstrip == row_indent)
            )
            if is_row_marker:
                current_row = []
                rows.append(current_row)
                if row_indent is None:
                    row_indent = lstrip
                    cell_indent = lstrip + 2  # column where `-` sits
                after = stripped[1:].lstrip()
                if after.startswith("- "):
                    current_row.append(after[2:])
                elif after == "-" or after == "":
                    current_row.append("")
                else:
                    current_row.append(after)
                current_cell_idx = len(current_row) - 1
            # "- cell" at cell_indent → new cell in current row
            elif stripped.startswith("- ") and cell_indent is not None and lstrip == cell_indent:
                cell = stripped[2:]
                if current_row is None:
                    current_row = []
                    rows.append(current_row)
                current_row.append(cell)
                current_cell_idx = len(current_row) - 1
            elif stripped == "-" and cell_indent is not None and lstrip == cell_indent:
                if current_row is None:
                    current_row = []
                    rows.append(current_row)
                current_row.append("")
                current_cell_idx = len(current_row) - 1
            else:
                # Continuation of the current cell (may include sub-bullets)
                if current_row is not None and current_cell_idx >= 0:
                    addition = stripped
                    current_row[current_cell_idx] = (
                        current_row[current_cell_idx] + " " + addition
                    ).strip() if current_row[current_cell_idx] else addition
        if not rows:
            return ""
        ncols = max(len(r) for r in rows)
        # Pad short rows
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        # Strip inline label definitions (`.. _xxx:` at cell start) which
        # don't produce visible content.
        _INLINE_LABEL_RE = re.compile(r"^\s*\.\.\s+_[A-Za-z0-9_.-]+:\s*")
        rows = [[_INLINE_LABEL_RE.sub("", c) for c in r] for r in rows]
        # Escape pipes inside cells (converter does this) so embedded
        # line-block content like `| "Nablarch"` doesn't break MD table.
        rows = [[c.replace("|", "\\|") for c in r] for r in rows]
        # Render MD table: first row as header
        header = "| " + " | ".join(rows[0]) + " |"
        sep = "|" + "|".join(["---"] * ncols) + "|"
        body_rows = ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n".join([header, sep] + body_rows)

    if name == "table":
        # body is a simple-table or grid-table. Defer to the same renderers
        # used for bare tables so we get MD table output, matching converter.
        for idx, line in enumerate(body):
            if _SIMPLE_TABLE_SEP_RE.match(line):
                rendered, _ = _render_simple_table(body, idx)
                return rendered
            if _GRID_TABLE_SEP_RE.match(line):
                rendered, _ = _render_grid_table(body, idx)
                return rendered
        return "\n".join(l for l in body if l.strip())

    if name == "csv-table":
        return "\n".join(body)

    return ""
