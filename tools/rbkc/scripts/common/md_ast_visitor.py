"""markdown-it-py token → Markdown Visitor (shared by create and verify).

Produces a :class:`DocumentParts` from a markdown-it-py token stream.
create uses it to build JSON sections; verify concatenates it into the
single normalised-MD string consumed by sequential-delete.

Design reference: rbkc-converter-design.md §7
Quality reference: rbkc-verify-quality-design.md §2-2 / §3-2

Zero-exception: unknown token types raise :class:`UnknownTokenError`.
There is no silent fallback — new token types are added through the
design spec change process (§5 of the verify-quality spec).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from markdown_it.token import Token

from . import rst_ast  # reuse normalise_raw_html / escape_cell_text


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class VisitorError(Exception):
    """Base class for Visitor-raised structural errors."""


class UnknownTokenError(VisitorError):
    """A markdown-it-py token type is not listed in the token → MD mapping."""


# ---------------------------------------------------------------------------
# Output containers (shape matches scripts/common/rst_ast_visitor.py)
# ---------------------------------------------------------------------------


@dataclass
class Section:
    title: str
    content: str


@dataclass
class DocumentParts:
    title: str = ""
    content: str = ""
    sections: list[Section] = field(default_factory=list)
    # QL extraction buckets (filled during walk so verify does not re-walk)
    external_urls: list[str] = field(default_factory=list)
    internal_links: list[tuple[str, str]] = field(default_factory=list)  # (text, href)
    images: list[tuple[str, str, str]] = field(default_factory=list)  # (alt, src, title)


# ---------------------------------------------------------------------------
# Token handlers
# ---------------------------------------------------------------------------


# Block tokens that open a container; the closing counterpart is ``<name>_close``.
_BLOCK_CONTAINERS = {
    "paragraph_open",
    "bullet_list_open",
    "ordered_list_open",
    "list_item_open",
    "blockquote_open",
    "table_open",
    "thead_open",
    "tbody_open",
    "tr_open",
    "th_open",
    "td_open",
    "heading_open",
}

# Inline tokens we recognise. ``_INLINE_KNOWN_LEAVES`` are self-closing.
_INLINE_KNOWN_LEAVES = {
    "text",
    "code_inline",
    "softbreak",
    "hardbreak",
    "image",
    "html_inline",
}

_INLINE_KNOWN_CONTAINERS = {
    "link_open",
    "em_open",
    "strong_open",
    "s_open",
}


def _iter_block(tokens: list[Token]) -> Iterator[Token]:
    return iter(tokens)


# ---------------------------------------------------------------------------
# Visitor
# ---------------------------------------------------------------------------


class _MDVisitor:
    def __init__(self) -> None:
        self.title: str = ""
        self.top_content_parts: list[str] = []
        self.sections: list[Section] = []
        self.external_urls: list[str] = []
        self.internal_links: list[tuple[str, str]] = []
        self.images: list[tuple[str, str, str]] = []

        # Current open section (None before first h2+ heading)
        self._current_section: Section | None = None
        self._current_section_parts: list[str] = []

    # ------------------------------------------------------------------ walk
    def walk(self, tokens: list[Token]) -> DocumentParts:
        idx = 0
        n = len(tokens)
        while idx < n:
            tok = tokens[idx]
            idx = self._handle_block(tokens, idx)
        self._close_section()
        content = "\n".join(self.top_content_parts).strip()
        return DocumentParts(
            title=self.title,
            content=content,
            sections=self.sections,
            external_urls=self.external_urls,
            internal_links=self.internal_links,
            images=self.images,
        )

    # -------------------------------------------------------------- sections
    def _emit_block(self, text: str) -> None:
        """Append a finished block of MD to either top-level or current section."""
        if self._current_section is None:
            self.top_content_parts.append(text)
        else:
            self._current_section_parts.append(text)

    def _close_section(self) -> None:
        if self._current_section is None:
            return
        self._current_section.content = "\n".join(self._current_section_parts).strip()
        self.sections.append(self._current_section)
        self._current_section = None
        self._current_section_parts = []

    def _open_section(self, title: str) -> None:
        self._close_section()
        self._current_section = Section(title=title, content="")
        self._current_section_parts = []

    # ----------------------------------------------------------- block walk
    def _handle_block(self, tokens: list[Token], idx: int) -> int:
        """Process tokens[idx] (and any matching close). Returns next index."""
        tok = tokens[idx]
        t = tok.type

        # Leaf / no-children block tokens
        if t == "hr":
            self._emit_block("-----")
            return idx + 1
        if t == "fence":
            info = (tok.info or "").strip()
            fence = "```" + info
            body = tok.content.rstrip("\n")
            self._emit_block(f"{fence}\n{body}\n```")
            return idx + 1
        if t == "code_block":
            # Indented code block (4-space). Render as fenced for symmetry.
            body = tok.content.rstrip("\n")
            self._emit_block(f"```\n{body}\n```")
            return idx + 1
        if t == "html_block":
            self._emit_block(rst_ast.normalise_raw_html(tok.content).rstrip("\n"))
            return idx + 1

        # Container-pair block tokens — find matching close and render
        if t == "heading_open":
            # Find matching inline + heading_close
            inline_tok = tokens[idx + 1]
            close_tok = tokens[idx + 2]
            assert inline_tok.type == "inline", inline_tok
            assert close_tok.type == "heading_close", close_tok
            title_text = self._render_inline(inline_tok).strip()
            level = int(tok.tag[1]) if tok.tag and tok.tag[0] == "h" else 1
            if level == 1:
                self.title = title_text
            else:
                self._open_section(title_text)
            return idx + 3

        if t == "paragraph_open":
            inline_tok = tokens[idx + 1]
            close_tok = tokens[idx + 2]
            assert inline_tok.type == "inline"
            assert close_tok.type == "paragraph_close"
            self._emit_block(self._render_inline(inline_tok).rstrip())
            return idx + 3

        if t == "bullet_list_open":
            return self._render_list(tokens, idx, ordered=False)

        if t == "ordered_list_open":
            return self._render_list(tokens, idx, ordered=True)

        if t == "blockquote_open":
            return self._render_blockquote(tokens, idx)

        if t == "table_open":
            return self._render_table(tokens, idx)

        # Unknown block token — zero-exception
        raise UnknownTokenError(
            f"Unknown markdown-it block token: {t!r} "
            f"(tag={tok.tag!r}, info={tok.info!r})"
        )

    # ---------------------------------------------------------- lists
    def _render_list(self, tokens: list[Token], idx: int, *, ordered: bool) -> int:
        """Render bullet_list or ordered_list and return index after <_close>."""
        open_tok = tokens[idx]
        close_type = "ordered_list_close" if ordered else "bullet_list_close"
        i = idx + 1
        lines: list[str] = []
        counter = 1
        while tokens[i].type != close_type:
            if tokens[i].type != "list_item_open":
                raise UnknownTokenError(
                    f"Unexpected token inside list: {tokens[i].type!r}"
                )
            j = i + 1
            depth = 1
            # Gather item's inner tokens until matching list_item_close
            inner_start = j
            while depth:
                tt = tokens[j].type
                if tt == "list_item_open":
                    depth += 1
                elif tt == "list_item_close":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            inner_tokens = tokens[inner_start:j]
            # Render the item's children with a fresh visitor context
            item_md = self._render_block_group(inner_tokens).rstrip()
            # Prefix each line. First line gets the marker; continuation lines
            # get 2-space indent.
            marker = f"{counter}." if ordered else "*"
            counter += 1
            item_lines = item_md.splitlines() or [""]
            lines.append(f"{marker} {item_lines[0]}")
            for cont in item_lines[1:]:
                lines.append(f"  {cont}")
            i = j + 1  # skip list_item_close
        # Skip close token
        self._emit_block("\n".join(lines))
        return i + 1

    def _render_block_group(self, tokens: list[Token]) -> str:
        """Render a sequence of block tokens (inside a list item / quote) to MD."""
        sub = _MDVisitor()
        # Reuse QL buckets so nested structures still contribute to extraction
        sub.external_urls = self.external_urls
        sub.internal_links = self.internal_links
        sub.images = self.images
        parts = sub.walk(tokens)
        # If the group produced top_content only (no sections — lists shouldn't
        # contain headings), just return that.
        return parts.content

    # ---------------------------------------------------------- blockquote
    def _render_blockquote(self, tokens: list[Token], idx: int) -> int:
        i = idx + 1
        depth = 1
        while depth:
            tt = tokens[i].type
            if tt == "blockquote_open":
                depth += 1
            elif tt == "blockquote_close":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        inner = tokens[idx + 1 : i]
        inner_md = self._render_block_group(inner)
        quoted = "\n".join(f"> {line}" for line in inner_md.splitlines())
        self._emit_block(quoted)
        return i + 1

    # ---------------------------------------------------------- tables
    def _render_table(self, tokens: list[Token], idx: int) -> int:
        """Render a GFM table (no merged cells — CommonMark spec)."""
        i = idx + 1
        rows_header: list[list[str]] = []
        rows_body: list[list[str]] = []
        current_rows = rows_body
        while tokens[i].type != "table_close":
            tt = tokens[i].type
            if tt == "thead_open":
                current_rows = rows_header
                i += 1
                continue
            if tt == "thead_close":
                current_rows = rows_body
                i += 1
                continue
            if tt == "tbody_open" or tt == "tbody_close":
                i += 1
                continue
            if tt == "tr_open":
                row: list[str] = []
                i += 1
                while tokens[i].type != "tr_close":
                    if tokens[i].type in ("th_open", "td_open"):
                        inline_tok = tokens[i + 1]
                        assert inline_tok.type == "inline"
                        cell = self._render_inline(inline_tok).strip()
                        row.append(rst_ast.escape_cell_text(cell))
                        # skip inline + th_close/td_close
                        i += 3
                    else:
                        raise UnknownTokenError(
                            f"Unexpected token inside tr: {tokens[i].type!r}"
                        )
                current_rows.append(row)
                i += 1
                continue
            raise UnknownTokenError(
                f"Unexpected token inside table: {tt!r}"
            )
        # Emit GFM table
        all_rows = rows_header + rows_body
        if not all_rows:
            return i + 1
        header = rows_header[0] if rows_header else rows_body[0]
        body = rows_body if rows_header else rows_body[1:]
        n_cols = len(header)
        def _fmt(row: list[str]) -> str:
            padded = row + [""] * (n_cols - len(row))
            return "| " + " | ".join(padded[:n_cols]) + " |"
        lines = [_fmt(header), "| " + " | ".join(["---"] * n_cols) + " |"]
        for r in body:
            lines.append(_fmt(r))
        self._emit_block("\n".join(lines))
        return i + 1

    # ---------------------------------------------------------- inline
    def _render_inline(self, inline_tok: Token) -> str:
        children = inline_tok.children or []
        return self._render_inline_children(children)

    def _render_inline_children(self, children: list[Token]) -> str:
        out: list[str] = []
        i = 0
        n = len(children)
        while i < n:
            c = children[i]
            t = c.type
            if t == "text":
                out.append(c.content)
                i += 1
                continue
            if t == "code_inline":
                out.append(f"`{c.content}`")
                i += 1
                continue
            if t == "softbreak":
                out.append(" ")
                i += 1
                continue
            if t == "hardbreak":
                out.append("\n")
                i += 1
                continue
            if t == "html_inline":
                out.append(rst_ast.normalise_raw_html(c.content))
                i += 1
                continue
            if t == "image":
                alt = c.content or ""
                src = c.attrGet("src") or ""
                title = c.attrGet("title") or ""
                self.images.append((alt, src, title))
                out.append(f"![{alt}]({src})")
                i += 1
                continue
            if t == "link_open":
                href = c.attrGet("href") or ""
                # Find matching link_close
                depth = 1
                j = i + 1
                while j < n and depth:
                    tt = children[j].type
                    if tt == "link_open":
                        depth += 1
                    elif tt == "link_close":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                inner_children = children[i + 1 : j]
                text = self._render_inline_children(inner_children)
                if href.startswith(("http://", "https://")):
                    self.external_urls.append(href)
                elif href and not href.startswith(("mailto:", "tel:", "javascript:", "#")):
                    # Internal link = relative path / sibling document. Schemed
                    # URIs (mailto/tel/javascript) and in-document anchors (`#x`)
                    # are not document-to-document links and do not belong in
                    # QL1's JSON-content-contains-link-text check.
                    self.internal_links.append((text, href))
                out.append(f"[{text}]({href})")
                i = j + 1
                continue
            if t == "em_open":
                depth = 1
                j = i + 1
                while j < n and depth:
                    if children[j].type == "em_open":
                        depth += 1
                    elif children[j].type == "em_close":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                inner = self._render_inline_children(children[i + 1 : j])
                out.append(f"*{inner}*")
                i = j + 1
                continue
            if t == "strong_open":
                depth = 1
                j = i + 1
                while j < n and depth:
                    if children[j].type == "strong_open":
                        depth += 1
                    elif children[j].type == "strong_close":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                inner = self._render_inline_children(children[i + 1 : j])
                out.append(f"**{inner}**")
                i = j + 1
                continue
            if t == "s_open":
                depth = 1
                j = i + 1
                while j < n and depth:
                    if children[j].type == "s_open":
                        depth += 1
                    elif children[j].type == "s_close":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                inner = self._render_inline_children(children[i + 1 : j])
                out.append(f"~~{inner}~~")
                i = j + 1
                continue
            # Unknown inline token — zero-exception
            raise UnknownTokenError(
                f"Unknown markdown-it inline token: {t!r} "
                f"(tag={c.tag!r}, content={c.content!r})"
            )
        return "".join(out)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def extract_document(tokens: list[Token]) -> DocumentParts:
    """Walk *tokens* (a markdown-it-py token stream) into `DocumentParts`."""
    v = _MDVisitor()
    return v.walk(tokens)


__all__ = [
    "DocumentParts",
    "Section",
    "UnknownTokenError",
    "VisitorError",
    "extract_document",
]
