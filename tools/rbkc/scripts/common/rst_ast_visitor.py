"""AST → Markdown Visitor (shared by create and verify).

Produces per-section ``(title, markdown)`` pairs from a docutils
document. The `extract_document` entry point walks the doctree and
returns a `DocumentParts` structure; create uses it to build JSON,
verify concatenates it into a single normalised-MD string.

Design reference: tools/rbkc/docs/rbkc-converter-design.md
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from docutils import nodes

from . import rst_admonition, rst_ast


# ---------------------------------------------------------------------------
# Zero-exception errors (§3-1b of rbkc-converter-design.md)
# ---------------------------------------------------------------------------


class VisitorError(Exception):
    """Base class for Visitor-raised structural errors."""


class UnknownNodeError(VisitorError):
    """A docutils node kind is not listed in the node → MD mapping."""


class UnknownRoleError(VisitorError):
    """An `:xxx:` role is not in the Sphinx role shim whitelist."""


class UnresolvedReferenceError(VisitorError):
    """A reference or substitution could not be resolved (even via label_map)."""


class UnknownSyntaxError(VisitorError):
    """docutils emitted a parse error (level >= 3)."""


# Roles registered in rst_ast._SPHINX_INLINE_ROLES; kept here to allow the
# Visitor to reject any role not in this set (zero-exception).
_KNOWN_ROLES: set[str] = {
    "ref", "doc", "download", "file", "guilabel", "menuselection",
    "kbd", "command", "samp", "envvar", "abbr", "term", "numref",
    "javadoc_url", "strong",
    "java:extdoc", "java:ref", "java:type", "java:method", "java:field",
    "c:func",
}


# ---------------------------------------------------------------------------
# Output containers
# ---------------------------------------------------------------------------


@dataclass
class Section:
    title: str
    content: str
    # For verify: the linear MD text of this section (title + content merged)
    # can be reproduced by concat; we keep title/content separate here so
    # create can write JSON directly.


@dataclass
class DocumentParts:
    top_title: str = ""
    top_content: str = ""
    sections: list[Section] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_flat_md(self) -> str:
        """Concatenate into a single normalised-MD string (verify side)."""
        parts: list[str] = []
        if self.top_title:
            parts.append(self.top_title)
            parts.append("")
        if self.top_content:
            parts.append(self.top_content)
            parts.append("")
        for sec in self.sections:
            parts.append(sec.title)
            parts.append("")
            if sec.content:
                parts.append(sec.content)
                parts.append("")
        return "\n".join(parts).strip() + "\n"


# ---------------------------------------------------------------------------
# Visitor
# ---------------------------------------------------------------------------


class _MDVisitor:
    """Render a docutils doctree to Markdown.

    The class is internal; callers use ``extract_document``. We keep state
    (list indentation, table cell context) as instance fields so the
    recursion stays readable.
    """

    def __init__(self, label_map: dict[str, str] | None = None) -> None:
        self.warnings: list[str] = []
        # Current indent for list / blockquote nesting (as a prefix string).
        self._prefix: str = ""
        # Counter for enumerated lists.
        self._enum_stack: list[int] = []
        # Cross-document label → target-title map (used to resolve :ref:
        # whose target lives in another file; docutils only resolves within
        # one doctree).
        self._label_map: dict[str, str] = label_map or {}

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def render_children(self, node: nodes.Element) -> str:
        out: list[str] = []
        for child in node.children:
            chunk = self.render(child)
            if chunk is not None:
                out.append(chunk)
        return _join_blocks(out)

    def render_inline(self, node: nodes.Element) -> str:
        """Render children as an inline single-line string."""
        out: list[str] = []
        for child in node.children:
            out.append(self._inline(child))
        return "".join(out)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def render(self, node: nodes.Node) -> str | None:
        name = type(node).__name__
        handler = getattr(self, f"visit_{name}", None)
        if handler is not None:
            return handler(node)
        if isinstance(node, nodes.Text):
            return str(node)
        # Zero-exception (§3-1b): unknown node kinds must FAIL.
        raise UnknownNodeError(f"unmapped node: {name}")

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------

    def visit_system_message(self, node: nodes.system_message) -> str | None:
        level = node.get("level", 0)
        if level >= 2:
            line = node.get("line", "?")
            text = node.astext()[:120]
            self.warnings.append(f"level={level} line={line} {text}")
        return None

    def visit_comment(self, node: nodes.comment) -> str | None:
        return None

    def visit_target(self, node: nodes.target) -> str | None:
        return None

    def visit_substitution_definition(self, node: nodes.substitution_definition) -> str | None:
        return None

    def visit_colspec(self, node: nodes.colspec) -> str | None:
        return None

    def visit_label(self, node: nodes.label) -> str | None:
        return None

    def visit_paragraph(self, node: nodes.paragraph) -> str:
        text = self.render_inline(node)
        return self._apply_prefix(text)

    def visit_transition(self, node: nodes.transition) -> str:
        return self._apply_prefix("-----")

    def visit_rubric(self, node: nodes.rubric) -> str:
        return self._apply_prefix(self.render_inline(node))

    def visit_title(self, node: nodes.title) -> str:
        # Section-level titles are handled by `extract_document`. When we
        # reach here it is a topic/sidebar/admonition title — emit as bold
        # paragraph for verify alignment with create.
        return self._apply_prefix(f"**{self.render_inline(node)}**")

    def visit_subtitle(self, node: nodes.subtitle) -> str:
        return self._apply_prefix(f"**{self.render_inline(node)}**")

    def visit_topic(self, node: nodes.topic) -> str:
        return self.render_children(node)

    def visit_sidebar(self, node: nodes.sidebar) -> str:
        return self.render_children(node)

    def visit_container(self, node: nodes.container) -> str:
        return self.render_children(node)

    def visit_compound(self, node: nodes.compound) -> str:
        return self.render_children(node)

    def visit_docinfo(self, node: nodes.docinfo) -> str:
        # Bibliographic fields at document top (author/date/version/...).
        # docutils children are `field` / specialised classes (`author`,
        # `date`, `organization`, etc). We render field_body text (label drop).
        out: list[str] = []
        for child in node.children:
            if isinstance(child, nodes.field):
                body_text = ""
                for sub in child.children:
                    if isinstance(sub, nodes.field_body):
                        body_text = self.render_children(sub).strip()
                if body_text:
                    out.append(body_text)
            else:
                # specialised bibliographic node (nodes.author / date / ...):
                # children are inline; take astext
                text = child.astext().strip()
                if text:
                    out.append(text)
        return "\n\n".join(out)

    def visit_field(self, node: nodes.field) -> str:
        # Reached only via docinfo fallback; field_body value only.
        body = ""
        for sub in node.children:
            if isinstance(sub, nodes.field_body):
                body = self.render_children(sub).strip()
        return body

    # ------------------------------------------------------------------
    # Lists
    # ------------------------------------------------------------------

    def visit_bullet_list(self, node: nodes.bullet_list) -> str:
        return self._render_list(node, ordered=False)

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> str:
        return self._render_list(node, ordered=True)

    def _render_list(self, node: nodes.Element, ordered: bool) -> str:
        out: list[str] = []
        idx = 1
        for child in node.children:
            if not isinstance(child, nodes.list_item):
                continue
            marker = f"{idx}." if ordered else "*"
            idx += 1
            # Render item children with a marker on the first line and
            # continuation indented by len(marker)+1 spaces.
            old_prefix = self._prefix
            self._prefix = old_prefix + "  "
            try:
                body = self.render_children(child).lstrip("\n")
            finally:
                self._prefix = old_prefix
            if not body.strip():
                continue
            # Replace our own first-line indent with the marker
            body_lines = body.splitlines()
            first = body_lines[0].lstrip()
            lines = [f"{old_prefix}{marker} {first}"]
            for l in body_lines[1:]:
                lines.append(l)
            out.append("\n".join(lines))
        return "\n".join(out)

    def visit_definition_list(self, node: nodes.definition_list) -> str:
        out: list[str] = []
        for item in node.children:
            if not isinstance(item, nodes.definition_list_item):
                continue
            term_parts: list[str] = []
            definition_body = ""
            for ch in item.children:
                if isinstance(ch, nodes.term):
                    term_parts.append(self.render_inline(ch))
                elif isinstance(ch, nodes.classifier):
                    term_parts.append(f": {self.render_inline(ch)}")
                elif isinstance(ch, nodes.definition):
                    definition_body = self.render_children(ch)
            term_line = self._apply_prefix(" ".join(term_parts))
            out.append(term_line)
            if definition_body:
                out.append(definition_body)
        return "\n".join(out)

    def visit_field_list(self, node: nodes.field_list) -> str | None:
        # §3-1a: field_list context-aware.
        # - Directive option block (directive head 直後) は docutils が `field_list`
        #   child を directive node の配下に置く。ここに到達する field_list は
        #   document body 内の standalone 扱い。field_name を drop し field_body
        #   を再帰 Visit して value を保持する。
        out: list[str] = []
        for child in node.children:
            if not isinstance(child, nodes.field):
                continue
            body_text = ""
            for sub in child.children:
                if isinstance(sub, nodes.field_body):
                    body_text = self.render_children(sub)
            if body_text.strip():
                out.append(body_text)
        if not out:
            return None
        return "\n\n".join(out)

    def visit_option_list(self, node: nodes.option_list) -> str:
        return self.render_children(node)

    def visit_option_list_item(self, node: nodes.option_list_item) -> str:
        parts: list[str] = []
        for ch in node.children:
            txt = self.render(ch)
            if txt:
                parts.append(txt)
        return "  ".join(parts)

    def visit_option_group(self, node: nodes.option_group) -> str:
        return self.render_inline(node)

    def visit_option(self, node: nodes.option) -> str:
        return self.render_inline(node)

    def visit_option_string(self, node: nodes.option_string) -> str:
        return node.astext()

    def visit_option_argument(self, node: nodes.option_argument) -> str:
        return node.astext()

    def visit_description(self, node: nodes.description) -> str:
        return self.render_inline(node)

    def visit_line_block(self, node: nodes.line_block) -> str:
        out: list[str] = []
        for ch in node.children:
            if isinstance(ch, nodes.line):
                out.append(self._apply_prefix(self.render_inline(ch)))
            elif isinstance(ch, nodes.line_block):
                # nested line block — render children at this indent level
                out.append(self.visit_line_block(ch))
        return "\n".join(out)

    def visit_line(self, node: nodes.line) -> str:
        return self._apply_prefix(self.render_inline(node))

    # ------------------------------------------------------------------
    # Blocks
    # ------------------------------------------------------------------

    def visit_block_quote(self, node: nodes.block_quote) -> str:
        old_prefix = self._prefix
        self._prefix = old_prefix + "> "
        try:
            return self.render_children(node)
        finally:
            self._prefix = old_prefix

    def visit_attribution(self, node: nodes.attribution) -> str:
        return self._apply_prefix(f"— {self.render_inline(node)}")

    def visit_literal_block(self, node: nodes.literal_block) -> str:
        lang = node.get("language", "")
        body = node.astext()
        fence = f"```{lang}" if lang else "```"
        indented = _indent_block(f"{fence}\n{body}\n```", self._prefix)
        return indented

    def visit_doctest_block(self, node: nodes.doctest_block) -> str:
        body = node.astext()
        return _indent_block(f"```python\n{body}\n```", self._prefix)

    # ------------------------------------------------------------------
    # Tables
    # ------------------------------------------------------------------

    def visit_table(self, node: nodes.table) -> str:
        rows: list[list[dict[str, Any]]] = []
        header_rows = 0
        title_text = ""
        for ch in node.children:
            if isinstance(ch, nodes.title):
                title_text = self.render_inline(ch).strip()
            elif isinstance(ch, nodes.tgroup):
                for grp in ch.children:
                    if isinstance(grp, nodes.thead):
                        for r in grp.children:
                            rows.append(self._row_entries(r))
                        header_rows = len(rows)
                    elif isinstance(grp, nodes.tbody):
                        for r in grp.children:
                            rows.append(self._row_entries(r))
        if not rows:
            return ""
        grid = rst_ast.fill_merged_cells(rows)
        if header_rows == 0:
            # Synthesise header from first row
            header_rows = 1
        cols = max(len(r) for r in grid)
        # Normalise to cols
        for r in grid:
            while len(r) < cols:
                r.append("")
        header = "| " + " | ".join(grid[0]) + " |"
        sep = "|" + "|".join(["---"] * cols) + "|"
        body_lines = ["| " + " | ".join(r) + " |" for r in grid[header_rows:]]
        out = [header, sep] + body_lines
        md_table = "\n".join(out)
        indented = _indent_block(md_table, self._prefix)
        if title_text:
            # Emit the table title as its own paragraph before the MD table
            # (so it is captured by verify's sequential-delete). Blank line
            # separator keeps MD paragraphs distinct.
            return self._apply_prefix(title_text) + "\n\n" + indented
        return indented

    def _row_entries(self, row: nodes.row) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for ch in row.children:
            if not isinstance(ch, nodes.entry):
                continue
            inner = self.render_children(ch).strip()
            entries.append({
                "text": rst_ast.escape_cell_text(inner),
                "morerows": ch.get("morerows", 0),
                "morecols": ch.get("morecols", 0),
            })
        return entries

    # ------------------------------------------------------------------
    # Images / figures
    # ------------------------------------------------------------------

    def visit_image(self, node: nodes.image) -> str:
        uri = node.get("uri", "")
        alt = node.get("alt", "")
        if not uri:
            return ""
        return self._apply_prefix(f"![{alt}]({uri})")

    def visit_figure(self, node: nodes.figure) -> str:
        parts: list[str] = []
        for ch in node.children:
            if isinstance(ch, nodes.image):
                result = self.visit_image(ch)
                if result:
                    parts.append(result)
            elif isinstance(ch, nodes.caption):
                text = self.render_inline(ch)
                if text:
                    parts.append(self._apply_prefix(text))
            elif isinstance(ch, nodes.legend):
                text = self.render_children(ch)
                if text:
                    parts.append(text)
            else:
                # Any other child (paragraph / block_quote / system_message) —
                # render via the generic dispatch so Visitor coverage stays
                # complete (zero-exception).
                chunk = self.render(ch)
                if chunk:
                    parts.append(chunk)
        return "\n\n".join(parts)

    def visit_caption(self, node: nodes.caption) -> str:
        return self._apply_prefix(self.render_inline(node))

    def visit_legend(self, node: nodes.legend) -> str:
        return self.render_children(node)

    # ------------------------------------------------------------------
    # Admonitions (14 kinds via rst_admonition.ADMONITION_LABELS)
    # ------------------------------------------------------------------

    def _visit_admonition(self, node: nodes.Element, label: str) -> str:
        old_prefix = self._prefix
        self._prefix = old_prefix + "> "
        try:
            body = self.render_children(node).strip()
        finally:
            self._prefix = old_prefix
        header = self._apply_prefix(f"> **{label}:**")
        if body:
            return f"{header}\n{body}"
        return header

    def visit_note(self, node): return self._visit_admonition(node, "Note")
    def visit_tip(self, node): return self._visit_admonition(node, "Tip")
    def visit_warning(self, node): return self._visit_admonition(node, "Warning")
    def visit_important(self, node): return self._visit_admonition(node, "Important")
    def visit_attention(self, node): return self._visit_admonition(node, "Attention")
    def visit_hint(self, node): return self._visit_admonition(node, "Hint")
    def visit_caution(self, node): return self._visit_admonition(node, "Caution")
    def visit_danger(self, node): return self._visit_admonition(node, "Danger")
    def visit_error(self, node): return self._visit_admonition(node, "Error")

    def visit_admonition(self, node: nodes.admonition) -> str:
        # `.. admonition:: <custom title>` の custom title を保持する。
        # docutils は title を admonition の最初の child として置く。
        label = "Note"
        for ch in node.children:
            if isinstance(ch, nodes.title):
                label = ch.astext()
                break
        body_children = [c for c in node.children if not isinstance(c, nodes.title)]
        old_prefix = self._prefix
        self._prefix = old_prefix + "> "
        try:
            rendered = [self.render(c) for c in body_children]
            body = _join_blocks([r for r in rendered if r is not None]).strip()
        finally:
            self._prefix = old_prefix
        header = self._apply_prefix(f"> **{label}:**")
        return f"{header}\n{body}" if body else header

    # ------------------------------------------------------------------
    # Footnote / citation
    # ------------------------------------------------------------------

    def visit_footnote(self, node: nodes.footnote) -> str:
        # Drop the label; recurse into remaining children as prose.
        body_children = [c for c in node.children if not isinstance(c, nodes.label)]
        out: list[str] = []
        for c in body_children:
            chunk = self.render(c)
            if chunk:
                out.append(chunk)
        return _join_blocks(out)

    def visit_citation(self, node: nodes.citation) -> str:
        return self.visit_footnote(node)

    # ------------------------------------------------------------------
    # Raw
    # ------------------------------------------------------------------

    def visit_raw(self, node: nodes.raw) -> str:
        fmt = node.get("format", "")
        if fmt != "html":
            return ""
        text = node.astext()
        return rst_ast.normalise_raw_html(text)

    # ------------------------------------------------------------------
    # Inline (returns pure inline strings — no prefix)
    # ------------------------------------------------------------------

    def _inline(self, node: nodes.Node) -> str:
        if isinstance(node, nodes.Text):
            return str(node)
        name = type(node).__name__
        handler = getattr(self, f"inline_{name}", None)
        if handler is not None:
            return handler(node)
        # Zero-exception (§3-1b): every inline node kind must be handled.
        raise UnknownNodeError(f"unmapped inline node: {name}")

    def inline_strong(self, node: nodes.strong) -> str:
        return f"**{self.render_inline(node)}**"

    def inline_emphasis(self, node: nodes.emphasis) -> str:
        return f"*{self.render_inline(node)}*"

    def inline_literal(self, node: nodes.literal) -> str:
        return f"`{node.astext()}`"

    def inline_title_reference(self, node: nodes.title_reference) -> str:
        return self.render_inline(node)

    def inline_inline(self, node: nodes.inline) -> str:
        # Sphinx role shims (ref / doc / download / java:extdoc / ...) are
        # registered as `inline` with class `role-<name>` by rst_ast. The
        # role name must be in _KNOWN_ROLES (shim whitelist); anything else
        # is a zero-exception FAIL.
        cls = node.get("classes", []) or []
        role = next((c[5:] for c in cls if c.startswith("role-")), None)
        if role is None:
            # Plain <inline> from docutils (no role class) — treat as inline span
            return self.render_inline(node)
        if role not in _KNOWN_ROLES:
            raise UnknownRoleError(f"unknown role: {role}")
        raw = node.astext()
        if role == "ref":
            # `:ref:` は label を必ず解決する (未解決は FAIL)。
            # `text <label>` → text (表示名) を使う。bare label は label_map で解決。
            if "<" in raw and raw.rstrip().endswith(">"):
                text, _, target = raw.rpartition("<")
                text = text.strip()
                target = target.rstrip(">").strip()
                if text:
                    return text
                resolved = self._label_map.get(target)
                if resolved is None:
                    raise UnresolvedReferenceError(f"unresolved :ref: {target}")
                return resolved
            resolved = self._label_map.get(raw.strip())
            if resolved is None:
                raise UnresolvedReferenceError(f"unresolved :ref: {raw.strip()}")
            return resolved
        if role in {"doc", "numref"}:
            # `:doc:` / `:numref:` は document path を参照する。
            # `text <path>` があれば表示名を優先、無ければ path の basename を残す。
            # path のタイトル解決は本 Visitor のスコープ外 (cross-doc resolver 不在)。
            if "<" in raw and raw.rstrip().endswith(">"):
                text, _, target = raw.rpartition("<")
                text = text.strip()
                if text:
                    return text
                return target.rstrip(">").strip().split("/")[-1]
            return raw.strip().split("/")[-1]
        if role == "download":
            return raw
        if role in {"java:extdoc", "javadoc_url"}:
            # `LinkText <fqcn>` form → keep LinkText only (Javadoc path is drop)
            if "<" in raw and raw.rstrip().endswith(">"):
                text, _, _ = raw.rpartition("<")
                return text.strip() or raw
            return raw
        if role == "strong":
            return f"**{raw}**"
        # Remaining whitelisted roles (file / guilabel / menuselection / kbd /
        # command / samp / envvar / abbr / term / c:func / java:ref / :type /
        # :method / :field) emit raw text.
        return raw

    def inline_reference(self, node: nodes.reference) -> str:
        text = self.render_inline(node)
        refuri = node.get("refuri")
        refid = node.get("refid")
        refname = node.get("refname")
        if refuri:
            return f"[{text}]({refuri})"
        if refid:
            return text
        if refname:
            # docutils could not resolve the ref within this doctree. Use the
            # cross-document label_map; fail if still unresolved.
            resolved = self._label_map.get(refname)
            if resolved:
                return resolved
            raise UnresolvedReferenceError(f"unresolved reference: {refname}")
        return text

    def inline_target(self, node: nodes.target) -> str:
        return self.render_inline(node)

    def inline_substitution_reference(self, node: nodes.substitution_reference) -> str:
        # Should have been replaced by the Substitutions transform. If we see
        # one here it means the definition is missing from the source.
        raise UnresolvedReferenceError(f"unresolved substitution: {node.astext()}")

    def inline_footnote_reference(self, node: nodes.footnote_reference) -> str:
        label = node.astext()
        return f"[{label}]"

    def inline_citation_reference(self, node: nodes.citation_reference) -> str:
        return f"[{node.astext()}]"

    def inline_problematic(self, node: nodes.problematic) -> str:
        return node.astext()

    def inline_system_message(self, node: nodes.system_message) -> str:
        self.visit_system_message(node)
        return ""

    def inline_raw(self, node: nodes.raw) -> str:
        return self.visit_raw(node)

    def inline_image(self, node: nodes.image) -> str:
        uri = node.get("uri", "")
        alt = node.get("alt", "")
        return f"![{alt}]({uri})" if uri else ""

    def inline_target_(self, node):  # noqa — keep naming consistent
        return ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apply_prefix(self, text: str) -> str:
        if not self._prefix:
            return text
        return "\n".join(self._prefix + line for line in text.splitlines())


def _indent_block(text: str, prefix: str) -> str:
    if not prefix:
        return text
    return "\n".join(prefix + line for line in text.splitlines())


_BLANK_RE = re.compile(r"\n{3,}")


def _join_blocks(parts: list[str | None]) -> str:
    kept = [p for p in parts if p]
    joined = "\n\n".join(kept)
    return _BLANK_RE.sub("\n\n", joined)


# ---------------------------------------------------------------------------
# Public entry: extract DocumentParts
# ---------------------------------------------------------------------------


def extract_document(
    doctree: nodes.document,
    label_map: dict[str, str] | None = None,
) -> DocumentParts:
    """Walk the document and return top-level title/content + sections."""
    parts = DocumentParts()
    visitor = _MDVisitor(label_map=label_map)

    # Separate top-level content (before first section) from sections.
    top_children: list[nodes.Node] = []
    section_children: list[nodes.section] = []
    for child in doctree.children:
        if isinstance(child, nodes.title):
            parts.top_title = visitor.render_inline(child)
        elif isinstance(child, nodes.subtitle):
            text = visitor.render_inline(child)
            if parts.top_title:
                parts.top_title = f"{parts.top_title} — {text}"
            else:
                parts.top_title = text
        elif isinstance(child, nodes.section):
            section_children.append(child)
        else:
            top_children.append(child)

    top_content = _join_blocks([visitor.render(c) for c in top_children])
    parts.top_content = top_content.strip()

    for sec in section_children:
        _walk_section(sec, visitor, parts)

    parts.warnings.extend(visitor.warnings)
    return parts


def _walk_section(sec: nodes.section, visitor: _MDVisitor, parts: DocumentParts) -> None:
    title = ""
    body_children: list[nodes.Node] = []
    subsections: list[nodes.section] = []
    for ch in sec.children:
        if isinstance(ch, nodes.title) and not title:
            title = visitor.render_inline(ch)
        elif isinstance(ch, nodes.section):
            subsections.append(ch)
        else:
            body_children.append(ch)
    content = _join_blocks([visitor.render(c) for c in body_children]).strip()
    parts.sections.append(Section(title=title, content=content))
    for sub in subsections:
        _walk_section(sub, visitor, parts)


__all__ = [
    "Section",
    "DocumentParts",
    "extract_document",
]
