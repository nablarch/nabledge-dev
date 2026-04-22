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
from scripts.common.rst_admonition import (
    ADMONITION_DIRECTIVES as _ADMONITION_DIRECTIVES,
    render_header as _render_admonition_header,
)


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
# Admonition directive set comes from scripts.common.rst_admonition (imported
# above). Labels and header rendering are delegated to that module so the
# converter and tokenizer share a single source of truth.
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

# Label definition: `.. _label:` or `.. _`label with spaces`:`.
# Label names allow backtick-quoted forms for labels containing spaces or
# non-identifier characters. Both forms are collected and stripped.
_LABEL_DEF_RE = re.compile(
    r"^\s*\.\.\s+_(?:`[^`]+`|[A-Za-z0-9_.-]+):\s*$"
)

# Footnote / citation definition: `.. [#name] text` or `.. [1] text`
# The text (and any indented continuation body) is emitted as prose.
_FOOTNOTE_DEF_RE = re.compile(r"^\s*\.\.\s+\[([0-9]+|\*|#[A-Za-z0-9_-]*)\]\s*(.*)$")

# Comment: `.. ` followed by anything that's NOT a directive (handled during
# directive parsing; leftover comments caught here).
_COMMENT_RE = re.compile(r"^\s*\.\.\s+(?![A-Za-z][A-Za-z0-9_:-]*::)\S.*$|^\s*\.\.\s*$")

# Field list line: `:name: value` (value may be empty).
# Require whitespace or EOL immediately after the second ``:`` so that inline
# roles (``:ref:\`label\``` — ``:`` followed by a backtick) are not misparsed
# as field lists.
_FIELD_LIST_RE = re.compile(
    r"^(?P<indent>\s*):(?P<name>[A-Za-z][^:\n]*):(?=\s|$)\s*(?P<value>.*)$"
)

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

def _apply_inline_transforms(text: str, label_map: dict[str, str]) -> str:
    """Apply inline transforms in a specific, non-order-sensitive way.

    Inline substitutions operate on disjoint syntactic forms whose regexes
    are designed to match distinct constructs. Apply each once, from most
    specific to most general.

    The output is the MD-equivalent visible text — widths are not preserved
    (the caller must extract structural elements such as tables from the
    raw source before inline transforms shrink inline markup).
    """

    # 1. Role with target — match converter behaviour exactly:
    #   - :ref:`text <label>`   → visible text
    #   - :doc:`text <path>`    → visible text
    #   - :java:extdoc:`Name <fqn>` → `Name` (code-quoted)
    #   - :javadoc_url:`text <path>` → [text](path)
    #   - :download:`text <path>`   → [text](path)
    def _role_target(m: re.Match) -> str:
        role, txt, target = m.group(1), m.group(2).strip(), m.group(3).strip()
        if role == "java:extdoc":
            return f"`{txt or target}`"
        if role == "javadoc_url":
            return f"[{txt or target}]({target})"
        if role == "download":
            return f"[{txt or target}]({target})"
        # :ref: / :doc: / unknown → visible text only
        return txt or target

    text = re.sub(
        r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`<>]*)<([^`<>]+)>`",
        _role_target,
        text,
    )

    # 2. Role simple (no target).
    def _role_simple(m: re.Match) -> str:
        role, inner = m.group(1), m.group(2)
        if role == "java:extdoc":
            return f"`{inner}`"
        if role == "ref":
            return label_map.get(inner, inner)
        return inner

    text = re.sub(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`]+)`", _role_simple, text)

    # 3. External link: `text <url>`_ / __ → [text](url)
    def _ext_link(m: re.Match) -> str:
        return f"[{m.group(1).strip()}]({m.group(2).strip()})"

    text = re.sub(r"`([^`<]+?)\s*<([^`<>]+)>`_+", _ext_link, text)

    # 4. Double-backtick literal: ``code`` → `code`
    text = re.sub(r"``([^`]+?)``", r"`\1`", text)

    # 5. Named reference: `text`_ → text. Require trailing `_` to be at a
    # word boundary (whitespace, EOL, or non-word/non-backtick punctuation)
    # so that back-to-back inline code spans like `` `%` `` and `` `_` `` are
    # not swept into a single spurious named reference. The text part may
    # contain ``<`` / ``>`` (e.g. Java generics in RST named refs), matching
    # the converter's behaviour.
    text = re.sub(
        r"(?<![`:])`([^`\n]+?)`_(?=\s|$|[^\w_`])",
        r"\1",
        text,
    )

    # 6. Interpreted text (bare single backtick): RST default role passes
    # through to converter as `text` (MD inline code). Keep backticks.
    # (No change needed; text is already in MD form.)

    return text


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

    # Step E: line-continuation. RST ``\<newline>`` escapes the newline.
    # The converter preserves the literal ``\`` + ``\n`` sequence in MD
    # output (both sides see the same raw characters), so the tokenizer
    # leaves it alone — structural detection still works because ``\``
    # is not a heading/table/list marker character.

    # Step F: expand substitution references against the body prose.
    # Non-strict when not enforcing unknown syntax: leave `|x|`-shaped
    # prose that isn't a real substitution (IP addresses, command args) alone.
    try:
        text = expand_substitutions(text, subs, strict=strict_unknown)
    except UndefinedSubstitutionError:
        if strict_unknown:
            raise

    # Step G: detect section heading levels (by first-appearance order of
    # underline char, matching converter's logic).
    heading_keys = _detect_heading_keys(text)

    # Step H: walk lines, collapsing directives/tables/headings/lists/comments.
    # Inline transforms (:ref:, ``code``, `text <url>`_) are applied here
    # per block, after structural elements (tables) have been extracted on
    # raw-width text so column boundaries remain accurate.
    normalised = _walk_blocks(
        text, label_map, heading_keys=heading_keys, strict_unknown=strict_unknown
    )

    # Step I: whitespace collapse on each line (preserve newlines). Lines
    # inside fenced code blocks keep their original indentation so that
    # JSON code-block content (which preserves source indentation) matches.
    out_lines = []
    in_fence = False
    for line in normalised.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out_lines.append(line.rstrip())
            continue
        if in_fence:
            out_lines.append(line.rstrip())
            continue
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

    def _xf(s: str) -> str:
        """Apply inline transforms to a prose string."""
        return _apply_inline_transforms(s, label_map)

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
            title = _xf(lines[i + 1].strip())
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
            title = _xf(line.strip())
            level = _heading_level((False, lines[i + 1].rstrip()[0]))
            out.append("#" * level + " " + title)
            i += 2
            continue

        # Stray underline line — may be an RST transition (horizontal rule).
        # Converter emits the line verbatim in JSON; preserve it here so
        # substring matching succeeds.
        if _HEADING_UNDERLINE_RE.match(line):
            out.append(line.rstrip())
            i += 1
            continue

        # Simple-table start — re-render the whole block as MD table
        if _SIMPLE_TABLE_SEP_RE.match(line):
            rendered, next_i = _render_simple_table(lines, i, label_map=label_map)
            if rendered:
                out.append(rendered)
            i = next_i
            continue

        # Grid-table separator — render the block as MD table
        if _GRID_TABLE_SEP_RE.match(line):
            rendered, next_i = _render_grid_table(lines, i, label_map=label_map)
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
            # Fenced-code directives treat body indent strictly (a line
            # shallower than the first body line ends the block) — matches
            # the converter so substring alignment holds.
            strict_body = name.lower() in _FENCED_CODE_DIRECTIVES
            body_lines, next_i = _collect_directive_body(
                lines, i, header_indent, strict_body_indent=strict_body,
            )
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
                out.append(_xf(" ".join(body_lines)))
            continue

        # Standalone comment line
        if _COMMENT_RE.match(line):
            # Skip the comment and its indented continuation lines. The
            # comment's own indent defines the continuation boundary —
            # only lines indented *deeper* belong to the comment body.
            comment_indent = len(line) - len(line.lstrip())
            i += 1
            while i < n:
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                cur_indent = len(bl) - len(bl.lstrip())
                if cur_indent > comment_indent:
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
            value = _xf(fm.group("value").strip())
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
            out.append(f"{bm.group('indent')}{marker} {_xf(bm.group('body'))}")
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
            out.append(f"{em.group('indent')}{norm_marker} {_xf(em.group('body'))}")
            i += 1
            continue

        # Line block — converter preserves the leading `| ` marker in JSON,
        # so keep it in the normalised source for substring alignment.
        lbm = _LINE_BLOCK_RE.match(line)
        if lbm:
            content = lbm.group(1)
            if content.strip() or line.strip() == "|":
                out.append(f"| {_xf(content)}" if content else "|")
                i += 1
                continue

        # Note: a standalone `| text | text |` line is handled by the
        # table renderer that saw the `+---+` separator upstream, so
        # bare pipes in prose (e.g. `|br|` expansions) pass through.

        out.append(_xf(line))
        i += 1

    return "\n".join(out)


def _collect_directive_body(
    lines: list[str], start: int, header_indent: int,
    *, strict_body_indent: bool = False,
) -> tuple[list[str], int]:
    """Collect the indented body of a directive starting at *start*.

    When *strict_body_indent* is True, the body ends as soon as a line is
    indented less than the first body line — matching the converter's
    `_read_block` behaviour for fenced-code and other verbatim-body
    directives. For narrative directives (admonition, list-table) the
    default behaviour is used: body runs until a line reaches or falls
    below the directive's header indent.

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
        elif strict_body_indent and cur_indent < body_indent:
            break
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


def _render_simple_table(
    lines: list[str], start: int, *, label_map: dict[str, str] | None = None
) -> tuple[str, int]:
    """Render an RST simple-table (`=== ===` separators) as a standard MD table.

    MD table layout per spec §3-1 (closed set of block constructs):
        | h1 | h2 |
        | --- | --- |
        | a  | b  |

    When no header row is present (no mid-separator), the first data row is
    treated as the header (MD tables require a header).

    Column boundaries come from the separator *display* widths. CJK
    characters occupy two display columns, so we track display width
    rather than raw codepoint index when splitting rows.
    """
    import unicodedata

    label_map = label_map or {}

    def _xf_cell(s: str) -> str:
        return _apply_inline_transforms(s, label_map)

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
    # Strip nested directive header lines from cells (e.g. ``.. tip::``)
    # but keep the body prose so indented body content is preserved.
    _NESTED_DIRECTIVE_LINE_RE = re.compile(r"\.\.\s+[a-z][a-z_:-]*\s*::[^\n]*")

    def _strip_cell_st(s: str) -> str:
        # Remove any ``.. directive::`` occurrences inline in the cell text
        # (simple-table cells are already flattened, so the directive header
        # sits as a run of chars within the cell).
        return _NESTED_DIRECTIVE_LINE_RE.sub("", s).strip()

    rows = [[_strip_cell_st(c) for c in r] for r in rows]
    # Apply inline transforms per cell, then escape pipes.
    xf_rows = [[_xf_cell(c).replace("|", "\\|") for c in r] for r in rows]
    sep = "|" + "|".join(["---"] * ncols) + "|"
    if has_mid_sep and header_count > 0:
        header_md = ["| " + " | ".join(r) + " |" for r in xf_rows[:header_count]]
        body_md = ["| " + " | ".join(r) + " |" for r in xf_rows[header_count:]]
        return "\n".join(header_md + [sep] + body_md), i
    # No mid-separator → first row becomes the header (MD requires one).
    header_md = ["| " + " | ".join(xf_rows[0]) + " |"]
    body_md = ["| " + " | ".join(r) + " |" for r in xf_rows[1:]]
    return "\n".join(header_md + [sep] + body_md), i


def _render_grid_table(
    lines: list[str], start: int, *, label_map: dict[str, str] | None = None
) -> tuple[str, int]:
    """Render an RST grid-table as a standard MD table.

    Output layout:
        | h1 | h2 |
        | --- | --- |
        | a  | b  |

    Uses display-width column boundaries from the first `+---+` separator
    so that inline `|` (e.g. line-block markers inside a cell) is not
    mistaken for a column divider.
    """
    import unicodedata as _ud

    label_map = label_map or {}

    def _xf_cell(s: str) -> str:
        return _apply_inline_transforms(s, label_map)

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

    # Pre-scan: does this grid-table have a header separator `+===+`?
    has_header_sep = False
    scan_i = start
    while scan_i < n:
        ln = lines[scan_i]
        if _GRID_TABLE_SEP_RE.match(ln):
            if '=' in ln:
                has_header_sep = True
            scan_i += 1
            if scan_i < n and not (
                _GRID_TABLE_SEP_RE.match(lines[scan_i])
                or (lines[scan_i].strip().startswith("|") and lines[scan_i].strip().endswith("|"))
            ):
                break
            continue
        if ln.strip().startswith("|") and ln.strip().endswith("|"):
            scan_i += 1
            continue
        break

    rows: list[tuple[bool, list[str]]] = []
    in_header = has_header_sep  # only mark rows as header if separator exists
    i = start

    def _is_cell_line(s: str) -> bool:
        """A cell line starts with ``|`` and ends with either ``|`` or ``+``
        (the latter happens for rowspan continuation rows that embed
        a sub-divider like ``|         +---+``)."""
        st = s.strip()
        if not st.startswith("|"):
            return False
        return st.endswith("|") or st.endswith("+")

    def _is_weird_rowspan_sep(s: str) -> bool:
        """An intermediate line like ``+---+/text/+---+`` — a rowspan
        separator with embedded cell text on the middle column. Treat as
        a divider (skip without breaking the loop)."""
        st = s.strip()
        return st.startswith("+") and st.endswith("+") and "-" in st

    while i < n:
        ln = lines[i]
        if _GRID_TABLE_SEP_RE.match(ln):
            if '=' in ln:
                in_header = False
            i += 1
            if i < n and not (
                _GRID_TABLE_SEP_RE.match(lines[i])
                or _is_cell_line(lines[i])
            ):
                break
            continue
        if _is_cell_line(ln):
            cells = _split_cells(ln)
            # Skip rows where every non-empty cell is only dashes / equals /
            # plus padding — these are rowspan sub-dividers that the
            # converter omits.
            def _is_divider(cs: list[str]) -> bool:
                non_empty = [c for c in cs if c]
                if not non_empty:
                    return False
                return all(set(c) <= set("-=+ ") for c in non_empty)

            if cells and any(c for c in cells) and not _is_divider(cells):
                rows.append((in_header, cells))
            i += 1
            continue
        if _is_weird_rowspan_sep(ln):
            # Rowspan separator carrying partial cell text — the converter
            # treats the embedded text as cell content and merges it into
            # surrounding rows. For alignment, skip without breaking so
            # the next cell line continues the table.
            i += 1
            continue
        break

    if not rows:
        return "", i

    # Determine column count from widest row
    ncols = max(len(r) for _, r in rows)

    # Apply inline transforms to each cell; escape pipes so embedded
    # text like `| pipe |` doesn't break MD table syntax.
    def _cell_md(c: str) -> str:
        return _xf_cell(c).replace("|", "\\|")

    header_rows = [r for hdr, r in rows if hdr]
    body_rows = [r for hdr, r in rows if not hdr]

    # Pad rows to ncols
    def _pad(r: list[str]) -> list[str]:
        return r + [""] * (ncols - len(r))

    md_lines: list[str] = []
    if header_rows:
        # Use first header row as the MD header (MD tables have one header row)
        md_lines.append("| " + " | ".join(_cell_md(c) for c in _pad(header_rows[0])) + " |")
        md_lines.append("|" + "|".join(["---"] * ncols) + "|")
        for r in header_rows[1:] + body_rows:
            md_lines.append("| " + " | ".join(_cell_md(c) for c in _pad(r)) + " |")
    else:
        # No `+===+` header separator — treat first row as the header
        md_lines.append("| " + " | ".join(_cell_md(c) for c in _pad(body_rows[0])) + " |")
        md_lines.append("|" + "|".join(["---"] * ncols) + "|")
        for r in body_rows[1:]:
            md_lines.append("| " + " | ".join(_cell_md(c) for c in _pad(r)) + " |")
    return "\n".join(md_lines), i


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

    # Group B: admonition — emit MD blockquote with labelled header from the
    # shared scripts.common.rst_admonition module (the single source of
    # truth for RST→MD admonition conventions).
    #
    # Converter behaviour (scripts.create.converters.rst._render_admonition_body):
    # split the body at the first line introducing a directive, bullet list,
    # or enumerated list. Prose lines BEFORE that split have their field-list
    # markers (``:name: value``) collapsed to just ``value``. Lines FROM the
    # split onwards are preserved verbatim (field markers intact).
    if name in _ADMONITION_DIRECTIVES:
        # Split the body into prose (before tail) and tail (from first
        # structural marker onward), same as the converter.
        tail_start = None
        directive_start = re.compile(r"^\s*\.\.\s+\S")
        bullet_start = re.compile(r"^\s*[*+\-][ \t]+\S")
        enum_start = re.compile(r"^\s*\d+[.\)][ \t]+\S")
        for idx, l in enumerate(body_rest):
            s = l.strip()
            if not s:
                continue
            if directive_start.match(l) or bullet_start.match(l) or enum_start.match(l):
                tail_start = idx
                break
        if tail_start is None:
            prose_lines = body_rest
            tail_lines: list[str] = []
        else:
            prose_lines = body_rest[:tail_start]
            tail_lines = body_rest[tail_start:]
        # Normalise prose lines: drop ``:name:`` from leading field-list
        # markers (converter behaviour). The regex targets a literal field
        # entry — the ``:name:`` must be followed by whitespace or end of
        # line so that inline roles like ``:java:extdoc:`...``` are not
        # mis-stripped. Field names can be any non-whitespace/non-backtick
        # chars (CJK characters are allowed — e.g. ``:固定長:``).
        prose_text = "\n".join(prose_lines)
        prose_text = re.sub(
            r"(?m)^[ \t]*:(?!\s)([^:\s`]+):(?=[ \t]|$)", "", prose_text
        )
        prose_inner = _walk_blocks(prose_text, label_map, strict_unknown=strict_unknown)
        prose_flat = re.sub(r"\s+", " ", prose_inner).strip()
        header = _render_admonition_header(name, args.strip())
        # Re-walk the tail so nested directives/lists/tables are rendered.
        tail_rendered = ""
        if tail_lines:
            tail_text = "\n".join(tail_lines)
            tail_rendered = _walk_blocks(tail_text, label_map, strict_unknown=strict_unknown).strip()
        if tail_rendered:
            return f"{header} {prose_flat}\n\n{tail_rendered}".rstrip() if prose_flat else f"{header}\n\n{tail_rendered}".rstrip()
        return f"{header} {prose_flat}".rstrip()

    # Group C: table — drop argument (converter does not include table
    # title in JSON body; caption presence confirmed 0/100 in v6 empirical
    # scan), reconstruct cells as MD table.
    if name in _TABLE_DIRECTIVES:
        return _render_table_directive(name, body_rest, label_map)

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


def _render_table_directive(
    name: str, body: list[str], label_map: dict[str, str] | None = None
) -> str:
    """Extract visible text from a list-table/table/csv-table body as MD table rows.

    Converter emits MD table syntax (`| cell | cell |` with `|---|` separator),
    so the normalised source must match that structure.
    """
    label_map = label_map or {}

    def _xf_cell(s: str) -> str:
        return _apply_inline_transforms(s, label_map)
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
        # Nested directives inside a cell: converter behaviour depends on
        # whether the whole cell is just the directive (dropped entirely)
        # or the directive is followed by body prose (directive header
        # dropped, body kept). Applying a line-by-line strip matches both.
        _LIST_NESTED_DIRECTIVE_LINE_RE = re.compile(r"\.\.\s+[a-z][a-z_:-]*\s*::[^\n]*")

        def _strip_cell(s: str) -> str:
            # If the cell IS a directive with a body-holding directive name
            # that produces fenced-code / table output, drop the whole cell
            # (rendering a code-block in a single MD table cell is not
            # well-defined). Otherwise, drop just the directive header line
            # and keep the body text.
            first = s.strip()
            if first.startswith(".."):
                head = re.match(r"\.\.\s+([a-z][a-z_:-]*)\s*::", first)
                if head and head.group(1) in {"code-block", "sourcecode", "literalinclude"}:
                    return ""
            return _LIST_NESTED_DIRECTIVE_LINE_RE.sub("", s).strip()

        rows = [[_strip_cell(c) for c in r] for r in rows]
        # Apply inline transforms and escape pipes so embedded line-block
        # content (e.g. `| "Nablarch"`) doesn't break MD table.
        rows = [[_xf_cell(c).replace("|", "\\|") for c in r] for r in rows]
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
                rendered, _ = _render_simple_table(body, idx, label_map=label_map)
                return rendered
            if _GRID_TABLE_SEP_RE.match(line):
                rendered, _ = _render_grid_table(body, idx, label_map=label_map)
                return rendered
        return "\n".join(_xf_cell(l) for l in body if l.strip())

    if name == "csv-table":
        return "\n".join(body)

    return ""
