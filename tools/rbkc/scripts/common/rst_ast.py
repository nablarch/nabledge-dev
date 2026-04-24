"""docutils AST wrapper + shared helpers for RST → normalised Markdown.

Both the RBKC converter (create side) and the verify tokenizer consume
RST by calling this module. Keeping docutils setup, Sphinx shims and
text-normalisation helpers in one place prevents create and verify from
drifting in their RST-spec interpretation.

Design reference:
- tools/rbkc/docs/rbkc-verify-quality-design.md §2-2 / §3-1
- tools/rbkc/docs/rbkc-converter-design.md (the node → MD mapping)
"""
from __future__ import annotations

import html
import io
import re
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import Directive, directives, roles


# ---------------------------------------------------------------------------
# Sphinx / v1.x custom role and directive shims
# ---------------------------------------------------------------------------
# Roles and directives that Sphinx / the Nablarch v1.x corpus use but that
# plain docutils does not know about. We register minimal shims so
# publish_doctree does not emit ERROR system_messages for them. The AST
# Visitor recognises the resulting node kinds (`inline` with class role-X,
# `literal_block` for code directives, `container` for generic bodies).

_SPHINX_INLINE_ROLES: tuple[str, ...] = (
    "ref",
    "doc",
    "download",
    "file",
    "guilabel",
    "menuselection",
    "kbd",
    "command",
    "samp",
    "envvar",
    "abbr",
    "term",
    "numref",
    "javadoc_url",
    "strong",
    "java:extdoc",
    "java:ref",
    "java:type",
    "java:method",
    "java:field",
    "c:func",
)

# Non-docutils directives whose body must be preserved as a literal block
# (the argument is usually a language spec, the body is raw text).
_LITERAL_DIRECTIVES: tuple[str, ...] = (
    "code-block",
    # Phase 22-B-12: Sphinx ``literalinclude`` directive.  v1.x corpus
    # uses it with only the ``:language:`` option (43 occurrences, no
    # other options) — the shim reads the body docutils already
    # expanded (``file_insertion_enabled=True``) and renders it as a
    # ``literal_block``.  See .work/00299/phase22/literalinclude-survey.md.
    "literalinclude",
)

# Non-docutils / custom directives whose body is RST prose; we nested_parse
# so inner block-level structure stays visible to the Visitor.
_CONTAINER_DIRECTIVES: tuple[str, ...] = (
    "toctree",
    "function",
    "class",
    "java:method",
    "java:type",
    "java:field",
)


def _register_roles() -> None:
    def role_shim(name, rawtext, text, lineno, inliner, options=None, content=None):
        node = nodes.inline(rawtext, text, classes=[f"role-{name}"])
        return [node], []

    for name in _SPHINX_INLINE_ROLES:
        roles.register_local_role(name, role_shim)


def _register_directives() -> None:
    class _LiteralDirective(Directive):
        has_content = True
        required_arguments = 0
        optional_arguments = 100
        final_argument_whitespace = True
        option_spec: dict[str, Any] = {}

        def run(self):
            text = "\n".join(self.content) if self.content else ""
            language = self.arguments[0] if self.arguments else ""
            node = nodes.literal_block(text, text)
            if language:
                node["language"] = language
            node["directive_name"] = self.name
            return [node]

    class _ContainerDirective(Directive):
        has_content = True
        required_arguments = 0
        optional_arguments = 100
        final_argument_whitespace = True
        option_spec: dict[str, Any] = {}

        def run(self):
            node = nodes.container(classes=[f"directive-{self.name}"])
            node["directive_name"] = self.name
            if self.content:
                self.state.nested_parse(self.content, self.content_offset, node)
            return [node]

    # Allow any option for shim directives (we don't need option semantics)
    from collections import defaultdict

    _LiteralDirective.option_spec = defaultdict(lambda: directives.unchanged)
    _ContainerDirective.option_spec = defaultdict(lambda: directives.unchanged)

    for name in _LITERAL_DIRECTIVES:
        directives.register_directive(name, _LiteralDirective)
    for name in _CONTAINER_DIRECTIVES:
        directives.register_directive(name, _ContainerDirective)


_SHIMS_REGISTERED = False


def register_shims() -> None:
    """Register Sphinx / v1.x custom roles and directives (idempotent)."""
    global _SHIMS_REGISTERED
    if _SHIMS_REGISTERED:
        return
    _register_roles()
    _register_directives()
    _SHIMS_REGISTERED = True


# ---------------------------------------------------------------------------
# Parse entry point
# ---------------------------------------------------------------------------

# Sphinx-provided substitutions that appear throughout the Nablarch RST
# corpus. docutils by itself does not know about these, so we prepend
# empty-string definitions before parsing. Matches conf.py's rst_prolog.
_SPHINX_SUBSTITUTIONS: tuple[str, ...] = (
    "nablarch_version",
)


_SUBSTITUTION_PLACEHOLDER = "​"  # zero-width space; visually empty


def _substitution_prolog() -> str:
    lines = [
        f".. |{name}| replace:: {_SUBSTITUTION_PLACEHOLDER}"
        for name in _SPHINX_SUBSTITUTIONS
    ]
    return "\n".join(lines) + "\n\n"


def parse(source: str, source_path: Path | None = None) -> tuple[nodes.document, str]:
    """Parse RST source into a doctree.

    Returns ``(doctree, warnings)`` where ``warnings`` is the concatenated
    docutils warning stream (empty string if clean). The caller decides
    whether a warning constitutes a FAIL (verify does; create logs).

    Sphinx-provided substitutions (see _SPHINX_SUBSTITUTIONS) are
    injected as empty replacements so ``|name|`` references do not raise
    "Undefined substitution" errors on plain docutils.
    """
    register_shims()

    warning_stream = io.StringIO()
    overrides: dict[str, Any] = {
        "report_level": 2,  # WARNING and above
        "halt_level": 5,  # never halt
        "warning_stream": warning_stream,
        "input_encoding": "utf-8",
        "file_insertion_enabled": True,  # expand .. include:: / literalinclude
        "raw_enabled": True,
    }
    if source_path is not None:
        overrides["source"] = str(source_path)

    full_source = _substitution_prolog() + source
    doctree = publish_doctree(full_source, settings_overrides=overrides)
    return doctree, warning_stream.getvalue()


# ---------------------------------------------------------------------------
# Shared text helpers (§3-6 of rbkc-converter-design.md)
# ---------------------------------------------------------------------------

def escape_cell_text(text: str) -> str:
    """Escape `|` and newline characters inside a MD table cell.

    Used by both create (JSON output) and verify (normalised MD output).
    Identical behaviour on both sides is a correctness requirement for
    sequential-delete.
    """
    # Replace literal pipe with escaped pipe; collapse newlines to spaces
    # (MD table cells cannot contain raw newlines).
    text = text.replace("\\", "\\\\")
    text = text.replace("|", "\\|")
    text = text.replace("\n", " ")
    return text


_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_NBSP_RE = re.compile(r"&nbsp;", re.IGNORECASE)


def normalise_raw_html(raw: str) -> str:
    """Normalise a `raw:: html` payload to plain text.

    The tags/entities covered here are the ones seen in the Nablarch corpus
    (Y-1 AST probe). Any HTML tag or entity not listed is left verbatim —
    it is MD-legal and sequential-delete will match it against the JSON
    content which also keeps it verbatim.
    """
    text = _BR_RE.sub("\n", raw)
    text = _NBSP_RE.sub(" ", text)
    text = html.unescape(text)  # decode &lt; &gt; &amp; &quot; etc.
    return text


def fill_merged_cells(
    rows: list[list[dict[str, Any]]],
) -> list[list[str]]:
    """Expand grid-table rowspan/colspan into an explicit rectangular grid.

    ``rows`` is a list of rows; each row is a list of entry dicts with keys
    ``text`` (rendered cell text), ``morerows`` (int), ``morecols`` (int).
    The merged content is placed in the top-left cell of the span; all
    other occupied cells are empty strings.

    Returns a rectangular ``list[list[str]]``.
    """
    # Compute column count from the widest row (after merge fill).
    # We use a two-pass algorithm:
    #   Pass 1: walk rows left-to-right, tracking a "pending" map of
    #           (row, col) cells that are occupied by a prior rowspan.
    #   Pass 2: nothing — Pass 1 writes the output directly.
    occupied: dict[tuple[int, int], bool] = {}
    out_rows: list[list[str]] = []

    max_cols = 0
    for r, row in enumerate(rows):
        out_row: list[str] = []
        c = 0
        it = iter(row)
        for entry in it:
            # Skip columns occupied by a prior rowspan.
            while occupied.get((r, c)):
                out_row.append("")
                c += 1
            text = entry.get("text", "")
            morerows = int(entry.get("morerows") or 0)
            morecols = int(entry.get("morecols") or 0)
            # Place the merged content in top-left only.
            out_row.append(text)
            # Fill horizontal continuation cells with empty strings.
            for dc in range(1, morecols + 1):
                out_row.append("")
            # Mark vertical / bottom-right cells as occupied for later rows.
            for dr in range(1, morerows + 1):
                for dc in range(0, morecols + 1):
                    occupied[(r + dr, c + dc)] = True
            c += 1 + morecols
        # Trailing rowspan occupancy at row end
        while occupied.get((r, c)):
            out_row.append("")
            c += 1
        out_rows.append(out_row)
        if c > max_cols:
            max_cols = c

    # Pad short rows to the max column count for a rectangular grid.
    for row in out_rows:
        while len(row) < max_cols:
            row.append("")
    return out_rows


__all__ = [
    "register_shims",
    "parse",
    "escape_cell_text",
    "normalise_raw_html",
    "fill_merged_cells",
]
