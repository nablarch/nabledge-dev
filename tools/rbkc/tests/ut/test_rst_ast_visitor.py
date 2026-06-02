"""Unit tests for scripts/common/rst_ast_visitor — visit_raw 3-block state machine, visit_image, and visit_container (toctree)."""
from __future__ import annotations

import pytest
import textwrap
from docutils import nodes
from pathlib import Path

from scripts.common.rst_ast_visitor import _MDVisitor, extract_document
from scripts.common.rst_ast import normalise_raw_html, parse
from scripts.common.labels import LabelTarget


# ---------------------------------------------------------------------------
# Fixtures — minimal Handler.js content used by multiple tests
# ---------------------------------------------------------------------------

_HANDLER_JS_SNIPPET = """<script>
var Handler = {
PermissionCheckHandler: {
  name: "認可制御ハンドラ"
, behavior: {
    inbound:  "権限チェックを行う"
  , outbound: "権限情報を設定する"
  , error:    "-"
  }
}
};
</script>"""

_BLOCK2_SCRIPT = """<script>
var Context      = 'handler'
  , HandlerQueue = [
      "PermissionCheckHandler"
    ];
</script>"""

_BLOCK3_BODY = "<html>handler_structure</html>"


def _make_raw(text: str, source: str | None = None) -> nodes.raw:
    n = nodes.raw("", text, format="html")
    if source is not None:
        n["source"] = source
    return n


def _make_visitor() -> _MDVisitor:
    return _MDVisitor()


# ---------------------------------------------------------------------------
# visit_raw 3-block state machine
# ---------------------------------------------------------------------------

class TestVisitRaw3BlockStateMachine:
    def test_block1_alone_returns_empty(self):
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        result = v.visit_raw(block1)
        assert result == ""

    def test_block1_and_2_no_output_yet(self):
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        block2 = _make_raw(_BLOCK2_SCRIPT)
        v.visit_raw(block1)
        result = v.visit_raw(block2)
        assert result == ""

    def test_full_3_block_sequence_renders_table(self):
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        block2 = _make_raw(_BLOCK2_SCRIPT)
        block3 = _make_raw(_BLOCK3_BODY, source="/path/to/fw/architectural_pattern/handler_structure.html")
        v.visit_raw(block1)
        v.visit_raw(block2)
        result = v.visit_raw(block3)
        assert "| ハンドラ |" in result
        assert "認可制御ハンドラ" in result
        assert "権限チェックを行う" in result
        assert "<script>" not in result

    def test_state_resets_after_3_blocks(self):
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        block2 = _make_raw(_BLOCK2_SCRIPT)
        block3 = _make_raw(_BLOCK3_BODY, source="/path/to/fw/architectural_pattern/handler_structure.html")
        v.visit_raw(block1)
        v.visit_raw(block2)
        v.visit_raw(block3)
        # After reset, a new block1 should start fresh
        result = v.visit_raw(block1)
        assert result == ""

    def test_non_handler_raw_passes_through(self):
        v = _make_visitor()
        arbitrary_html = "<p>テスト</p>"
        raw = _make_raw(arbitrary_html)
        result = v.visit_raw(raw)
        # normalise_raw_html result — no script content
        assert "テスト" in result or result == normalise_raw_html(arbitrary_html)

    def test_non_handler_raw_does_not_affect_state(self):
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        arbitrary = _make_raw("<p>other</p>")
        v.visit_raw(block1)
        # Arbitrary raw in between should NOT consume the state
        v.visit_raw(arbitrary)
        # block2 should still follow block1 correctly
        block2 = _make_raw(_BLOCK2_SCRIPT)
        block3 = _make_raw(_BLOCK3_BODY, source="/path/to/fw/architectural_pattern/handler_structure.html")
        v.visit_raw(block2)
        result = v.visit_raw(block3)
        assert "| ハンドラ |" in result

    def test_block3_with_handlerqueue_in_content_renders_table(self):
        """Bug 2: Block 3 HTML containing 'HandlerQueue' must not be consumed as Block 2.

        The actual handler_structure.html file includes a <script> that defines HandlerQueue.
        Block 3 must be detected by source path, not by text content.
        """
        v = _make_visitor()
        block1 = _make_raw(_HANDLER_JS_SNIPPET, source="/path/to/fw/Handler.js")
        block2 = _make_raw(_BLOCK2_SCRIPT)
        # Block 3 HTML that also contains "HandlerQueue" in its content (as the real file does)
        block3_html_with_queue = (
            "<style>#handler_structure{}</style>"
            "<script>var HandlerQueue=['PermissionCheckHandler'];</script>"
            "<table id='handler_structure'></table>"
        )
        block3 = _make_raw(block3_html_with_queue, source="/path/to/fw/architectural_pattern/handler_structure.html")
        v.visit_raw(block1)
        v.visit_raw(block2)
        result = v.visit_raw(block3)
        assert "| ハンドラ |" in result
        assert "認可制御ハンドラ" in result


# ---------------------------------------------------------------------------
# visit_image — invisible image suppression (Bug 1)
# ---------------------------------------------------------------------------

def _make_image(uri: str, alt: str = "", height: int | str | None = None, width: int | str | None = None) -> nodes.image:
    attrs: dict = {"uri": uri}
    if alt:
        attrs["alt"] = alt
    if height is not None:
        attrs["height"] = height
    if width is not None:
        attrs["width"] = width
    return nodes.image("", **attrs)


class TestVisitImageInvisibleSuppression:
    def test_normal_image_is_rendered(self):
        v = _make_visitor()
        img = _make_image(uri="diagram.png", alt="architecture diagram")
        result = v.visit_image(img)
        assert "diagram.png" in result
        assert "architecture diagram" in result

    def test_invisible_image_height_0_width_0_is_suppressed(self):
        """Bug 1: link.rst injects handler_structure_bg.png/handler_bg.png with height=0, width=0.

        These are invisible spacer images; they must produce empty output.
        """
        v = _make_visitor()
        img = _make_image(uri="handler_structure_bg.png", height=0, width=0)
        result = v.visit_image(img)
        assert result == ""

    def test_invisible_image_height_0_only_is_suppressed(self):
        v = _make_visitor()
        img = _make_image(uri="handler_bg.png", height=0)
        result = v.visit_image(img)
        assert result == ""

    def test_invisible_image_width_0_only_is_suppressed(self):
        v = _make_visitor()
        img = _make_image(uri="bg.png", width=0)
        result = v.visit_image(img)
        assert result == ""

    def test_image_with_nonzero_height_is_rendered(self):
        v = _make_visitor()
        img = _make_image(uri="chart.png", alt="chart", height=100, width=200)
        result = v.visit_image(img)
        assert "chart.png" in result

    def test_invisible_image_string_zero_height_is_suppressed(self):
        """docutils stores height/width as strings; '0' must also be suppressed."""
        v = _make_visitor()
        img = _make_image(uri="handler_structure_bg.png", height="0", width="0")
        result = v.visit_image(img)
        assert result == ""

    def test_invisible_image_string_zero_height_only_is_suppressed(self):
        v = _make_visitor()
        img = _make_image(uri="handler_bg.png", height="0")
        result = v.visit_image(img)
        assert result == ""

    def test_invisible_image_string_zero_width_only_is_suppressed(self):
        """docutils stores width as a string; width='0' must also be suppressed."""
        v = _make_visitor()
        img = _make_image(uri="bg.png", width="0")
        result = v.visit_image(img)
        assert result == ""


# ---------------------------------------------------------------------------
# visit_container — toctree MD link conversion
# ---------------------------------------------------------------------------

def _make_doc_map_entry(title: str, type_: str, category: str, file_id: str) -> LabelTarget:
    return LabelTarget(title=title, file_id=file_id, section_title="", category=category, type=type_)


def _make_toctree_rst(entries: list[str]) -> str:
    entry_lines = "\n".join(f"   {e}" for e in entries)
    return f"Page\n====\n\n.. toctree::\n   :maxdepth: 1\n\n{entry_lines}\n"


class TestExtractDocumentSubtitle:
    """extract_document: DocTitle-promoted subtitle must become sections[0]."""

    def test_subtitle_only_file_produces_section(self):
        """h1+h2 only RST: subtitle must appear in sections[], not merged into top_title."""
        source = (
            "====\n"
            "ドキュメントタイトル\n"
            "====\n\n"
            "-------\n"
            "サブセクション\n"
            "-------\n\n"
            "本文テキスト。\n"
        )
        doctree, _ = parse(source)
        parts = extract_document(doctree)
        assert parts.top_title == "ドキュメントタイトル"
        assert len(parts.sections) == 1
        assert parts.sections[0].title == "サブセクション"
        assert parts.sections[0].level == 2
        assert "本文テキスト" in parts.sections[0].content

    def test_subtitle_with_subsequent_sections(self):
        """subtitle + multiple h2 sections: subtitle becomes sections[0], others follow."""
        source = (
            "====\n"
            "タイトル\n"
            "====\n\n"
            "-------\n"
            "セクション1\n"
            "-------\n\n"
            "前文。\n\n"
            "セクション2\n"
            "==========\n\n"
            "後文。\n"
        )
        doctree, _ = parse(source)
        parts = extract_document(doctree)
        assert parts.top_title == "タイトル"
        assert len(parts.sections) == 2
        assert parts.sections[0].title == "セクション1"
        assert "前文" in parts.sections[0].content
        assert parts.sections[1].title == "セクション2"
        assert "後文" in parts.sections[1].content

    def test_subtitle_without_body_produces_empty_content(self):
        """subtitle with no doc-level body: sections[0] exists with empty content."""
        source = (
            "利用規約\n"
            "========\n\n"
            "概要\n"
            "----\n\n"
        )
        doctree, _ = parse(source)
        parts = extract_document(doctree)
        assert parts.top_title == "利用規約"
        assert len(parts.sections) == 1
        assert parts.sections[0].title == "概要"
        assert parts.sections[0].level == 2
        assert parts.sections[0].content == ""

    def test_no_subtitle_is_unchanged(self):
        """RST without DocTitle subtitle produces no section from subtitle."""
        source = (
            "タイトル\n"
            "========\n\n"
            "前文。\n\n"
            "セクション1\n"
            "----------\n\n"
            "内容。\n"
        )
        doctree, _ = parse(source)
        parts = extract_document(doctree)
        assert "—" not in parts.top_title
        assert len(parts.sections) == 1
        assert parts.sections[0].title == "セクション1"


class TestVisitContainerToctree:
    def test_toctree_resolved_entries_become_md_links(self):
        """toctree entries that resolve via doc_map are emitted as MD bullet links."""
        source = _make_toctree_rst(["handlers/index"])
        source_path = Path("/repo/ja/application_framework/index.rst")
        doc_map = {
            "application_framework/handlers/index.rst": _make_doc_map_entry(
                "ハンドラ一覧", "component", "handlers", "handlers-handlers"
            )
        }
        doctree, _ = parse(source, source_path=source_path)
        parts = extract_document(doctree, doc_map=doc_map, source_path=source_path)
        assert "[ハンドラ一覧](../../component/handlers/handlers-handlers.md)" in parts.top_content
        assert parts.top_content.startswith("*")

    def test_toctree_unresolved_entries_become_code_spans(self):
        """toctree entries that cannot be resolved emit a code span fallback."""
        source = _make_toctree_rst(["unknown/path"])
        source_path = Path("/repo/ja/index.rst")
        doc_map: dict = {}
        doctree, _ = parse(source, source_path=source_path)
        parts = extract_document(doctree, doc_map=doc_map, source_path=source_path)
        assert "`unknown/path`" in parts.top_content
        assert parts.top_content.startswith("*")

    def test_toctree_multiple_entries_all_rendered(self):
        """Multiple toctree entries across paragraphs are merged into one list."""
        source = _make_toctree_rst(["web/index", "batch/index"])
        source_path = Path("/repo/ja/application_framework/index.rst")
        doc_map = {
            "application_framework/web/index.rst": _make_doc_map_entry(
                "ウェブ編", "processing-pattern", "web-application", "web-application-web"
            ),
            "application_framework/batch/index.rst": _make_doc_map_entry(
                "バッチ編", "processing-pattern", "nablarch-batch", "nablarch-batch-batch"
            ),
        }
        doctree, _ = parse(source, source_path=source_path)
        parts = extract_document(doctree, doc_map=doc_map, source_path=source_path)
        assert "[ウェブ編]" in parts.top_content
        assert "[バッチ編]" in parts.top_content
        # Both must appear as bullet items
        assert parts.top_content.count("* ") == 2

    def test_non_toctree_container_recurses_children(self):
        """Containers with directive_name != 'toctree' render children as usual."""
        source = "Page\n====\n\n.. function:: foo()\n\n   This is a function.\n"
        source_path = Path("/repo/ja/api.rst")
        doctree, _ = parse(source, source_path=source_path)
        parts = extract_document(doctree, source_path=source_path)
        assert "This is a function." in parts.top_content
        assert "[" not in parts.top_content  # no link syntax

    def test_toctree_page_has_content_not_empty(self):
        """A page consisting only of a toctree must NOT be no_knowledge_content=True after fix."""
        from scripts.create.converters.rst import convert as rst_convert
        source = _make_toctree_rst(["handlers/index"])
        source_path = Path("/repo/ja/application_framework/index.rst")
        doc_map = {
            "application_framework/handlers/index.rst": _make_doc_map_entry(
                "ハンドラ一覧", "component", "handlers", "handlers-handlers"
            )
        }
        result = rst_convert(
            source,
            file_id="app-framework-index",
            source_path=source_path,
            doc_map=doc_map,
        )
        assert result.no_knowledge_content is False
        assert result.content.strip() != ""


class TestRefRoleCaseInsensitiveLookup:
    """:ref: role with mixed-case label names must resolve via label_map.

    Bug 1 (Issue #320): docutils normalises target names to lowercase in
    names[], so label_map keys are always lowercase.  Callers must look up
    labels with .lower() — otherwise mixed-case labels like
    ``NablarchServletContextListener`` fall through to the UNRESOLVED branch
    and are emitted as plain text instead of MD links.

    These tests are RED before the fix (rst_ast_visitor uses original-case
    lookup) and GREEN after the fix (.lower() applied at lookup site).
    """

    def _make_label_map_with_mixed_case(self):
        """Build a label_map that mirrors what build_label_map returns:
        keys are lowercase (docutils normalisation), values are LabelTarget.
        """
        return {
            "nablarchservletcontextlistener": LabelTarget(
                title="NablarchServletContextListener",
                file_id="libraries-servlet-context-listener",
                section_title="",
                category="libraries",
                type="component",
                anchor="nablarchservletcontextlistener",
            ),
            "sqllog": LabelTarget(
                title="SqlLog",
                file_id="libraries-sql-log",
                section_title="",
                category="libraries",
                type="component",
                anchor="sqllog",
            ),
        }

    def test_mixed_case_ref_resolves_to_md_link(self):
        """:ref:`NablarchServletContextListener` must emit a MD link, not plain text."""
        from scripts.common.rst_ast import parse
        from scripts.common.rst_ast_visitor import extract_document

        label_map = self._make_label_map_with_mixed_case()
        source = textwrap.dedent("""\
            Title
            =====

            See :ref:`NablarchServletContextListener`.
            """)
        doctree, _ = parse(source, source_path=Path("/repo/ja/test.rst"))
        parts = extract_document(doctree, label_map=label_map, source_path=Path("/repo/ja/test.rst"))
        # After fix: must contain a MD link, not bare text
        assert "[NablarchServletContextListener]" in parts.top_content or \
               "NablarchServletContextListener" in parts.top_content
        # The key assertion: a MD link bracket must appear (fix) vs plain text (bug)
        assert "[NablarchServletContextListener](" in parts.top_content, (
            "Expected MD link but got plain text — case-insensitive lookup not applied"
        )

    def test_mixed_case_ref_with_display_text_resolves_to_md_link(self):
        """:ref:`display text <SqlLog>` must emit a MD link, not plain text."""
        from scripts.common.rst_ast import parse
        from scripts.common.rst_ast_visitor import extract_document

        label_map = self._make_label_map_with_mixed_case()
        source = textwrap.dedent("""\
            Title
            =====

            See :ref:`SQLログ <SqlLog>`.
            """)
        doctree, _ = parse(source, source_path=Path("/repo/ja/test.rst"))
        parts = extract_document(doctree, label_map=label_map, source_path=Path("/repo/ja/test.rst"))
        assert "[SQLログ](" in parts.top_content, (
            "Expected MD link but got plain text — case-insensitive lookup not applied"
        )


class TestParagraphAnchorSyntheticSection:
    """Issue #320 Task 25: anchor before a bold/italic paragraph inside a section
    body should generate a synthetic subsection in parts.sections.

    Real example (v1.x fw/architectural_pattern/*.rst):
      .. _フローを表示:

      **標準ハンドラ構成** (説明文...)

      .. raw:: html  ← content that belongs to the synthetic section

    The anchor+paragraph pair is lifted out of the parent section body and
    emitted as a separate Section(title='標準ハンドラ構成', ...) entry.
    """

    def _parse_and_extract(self, rst_source: str) -> "DocumentParts":
        from scripts.common.rst_ast import parse
        from scripts.common.rst_ast_visitor import extract_document
        doctree, _ = parse(rst_source, source_path=Path("/repo/test.rst"))
        return extract_document(doctree, label_map={}, source_path=Path("/repo/test.rst"))

    def test_bold_paragraph_anchor_creates_subsection(self):
        """``.. _anchor:`` + ``**Title**`` paragraph → Section(title='Title').

        Uses a 3-level structure so docutils transforms do not collapse
        the h2 section body into the document root.
        """
        source = textwrap.dedent("""\
            Doc Title
            =========

            Parent Section
            --------------

            Grandparent body.

            Sub Section
            ^^^^^^^^^^^

            Body text.

            .. _my_term:

            **用語**

            Definition content.
            """)
        parts = self._parse_and_extract(source)
        titles = [s.title for s in parts.sections]
        assert "用語" in titles, (
            f"Expected synthetic section '用語' in sections, got: {titles}"
        )

    def test_bold_start_paragraph_anchor_creates_subsection(self):
        """``**Term** (extra)`` paragraph → Section(title='Term')."""
        source = textwrap.dedent("""\
            Doc Title
            =========

            Parent Section
            --------------

            Body.

            Sub Section
            ^^^^^^^^^^^

            .. _フローを表示:

            **標準ハンドラ構成** (説明文をクリックすると詳細が表示されます。)

            Inline content.
            """)
        parts = self._parse_and_extract(source)
        titles = [s.title for s in parts.sections]
        assert "標準ハンドラ構成" in titles, (
            f"Expected synthetic section '標準ハンドラ構成' in sections, got: {titles}"
        )

    def test_plain_paragraph_anchor_does_not_create_subsection(self):
        """Plain-text paragraph after anchor stays in parent section body."""
        source = textwrap.dedent("""\
            Doc Title
            =========

            Parent Section
            --------------

            Body.

            Sub Section
            ^^^^^^^^^^^

            Body text.

            .. _my_anchor:

            plain text paragraph

            More content.
            """)
        parts = self._parse_and_extract(source)
        titles = [s.title for s in parts.sections]
        assert "plain text paragraph" not in titles, (
            "Plain-text paragraph must not create a synthetic section"
        )
        assert "Sub Section" in titles

    def test_letter_paren_paragraph_anchor_creates_subsection(self):
        """``\\e) SQL文のロードクラス`` paragraph → Section(title='e) SQL文のロードクラス').

        Real example from v1.x 04_Statement.rst:
            .. _sql-load-class-label:
            \\e) SQL文のロードクラス

        Docutils strips the backslash and parses as 'e) SQL文…' (plain paragraph).
        This Nablarch 1.x letter+paren convention is a structural subsection list
        and must produce a synthetic section like bold/italic paragraphs do.
        """
        source = textwrap.dedent("""\
            Doc Title
            =========

            Parent Section
            --------------

            Body.

            Sub Section
            ^^^^^^^^^^^

            Body text.

            .. _sql-load-class-label:

            \\e) SQL文のロードクラス

            BasicSqlLoader description.
            """)
        parts = self._parse_and_extract(source)
        titles = [s.title for s in parts.sections]
        assert "e) SQL文のロードクラス" in titles, (
            f"Expected synthetic section 'e) SQL文のロードクラス' in sections, got: {titles}"
        )

    def test_digit_paren_paragraph_anchor_creates_subsection(self):
        r"""``\2) Formクラスの精査処理実装`` paragraph → synthetic section.

        Real example from v1.2 guide/05_create_form.rst.
        Without the backslash, docutils treats '2) text' as an enumerated list.
        """
        # Use explicit string concatenation to write the literal backslash + 2
        source = (
            "Doc Title\n=========\n\nParent Section\n--------------\n\nBody.\n\n"
            "Sub Section\n^^^^^^^^^^^\n\n.. _form_validation:\n\n"
            "\\2) Formクラスの精査処理実装\n\nContent.\n"
        )
        parts = self._parse_and_extract(source)
        titles = [s.title for s in parts.sections]
        assert "2) Formクラスの精査処理実装" in titles, (
            f"Expected synthetic section '2) Formクラスの精査処理実装' in sections, got: {titles}"
        )


# ---------------------------------------------------------------------------
# Task 2-G: :java:extdoc: internal link resolution via javadoc_map
# ---------------------------------------------------------------------------

class TestExtdocRoleResolution:
    """:java:extdoc: resolves to internal javadoc MD link when javadoc_map provided."""

    def _extract(self, rst_source: str, javadoc_map: dict | None = None) -> "DocumentParts":
        from scripts.common.rst_ast import parse
        from scripts.common.rst_ast_visitor import extract_document
        from pathlib import Path
        doctree, _ = parse(rst_source, source_path=Path("/repo/test.rst"))
        return extract_document(
            doctree,
            label_map={},
            source_path=Path("/repo/test.rst"),
            javadoc_map=javadoc_map,
        )

    def test_pass_nablarch_fqcn_in_map_emits_link(self):
        """javadoc_map has nablarch FQCN → MD link emitted."""
        javadoc_map = {"nablarch.common.dao.UniversalDao": "javadoc-nablarch-common-dao-UniversalDao"}
        src = "Title\n=====\n\n:java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`\n"
        parts = self._extract(src, javadoc_map=javadoc_map)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "[UniversalDao](../javadoc/javadoc-nablarch-common-dao-UniversalDao.md)" in content

    def test_pass_nablarch_fqcn_not_in_map_emits_display_text(self):
        """javadoc_map exists but FQCN not in map → display text fallback."""
        javadoc_map = {}  # empty map
        src = "Title\n=====\n\n:java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`\n"
        parts = self._extract(src, javadoc_map=javadoc_map)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "UniversalDao" in content
        assert "](../javadoc/" not in content

    def test_pass_java_std_lib_emits_display_text(self):
        """java.* FQCN → always display text (external JDK)."""
        javadoc_map = {"java.lang.String": "should-never-be-used"}
        src = "Title\n=====\n\n:java:extdoc:`String <java.lang.String>`\n"
        parts = self._extract(src, javadoc_map=javadoc_map)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "String" in content
        assert "](../javadoc/" not in content

    def test_pass_jakarta_emits_display_text(self):
        """jakarta.* FQCN → always display text."""
        javadoc_map = {}
        src = "Title\n=====\n\n:java:extdoc:`HttpServletRequest <jakarta.servlet.http.HttpServletRequest>`\n"
        parts = self._extract(src, javadoc_map=javadoc_map)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "HttpServletRequest" in content
        assert "](../javadoc/" not in content

    def test_pass_method_suffix_resolved_via_class(self):
        """FQCN with method suffix → class FQCN used for map lookup."""
        javadoc_map = {"nablarch.common.dao.UniversalDao": "javadoc-nablarch-common-dao-UniversalDao"}
        # FQCN has #findById suffix
        src = "Title\n=====\n\n:java:extdoc:`findById <nablarch.common.dao.UniversalDao#findById>`\n"
        parts = self._extract(src, javadoc_map=javadoc_map)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "[findById](../javadoc/javadoc-nablarch-common-dao-UniversalDao.md)" in content

    def test_pass_no_javadoc_map_falls_back_to_display_text(self):
        """javadoc_map=None (not provided) → display text fallback (backward compat)."""
        src = "Title\n=====\n\n:java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`\n"
        parts = self._extract(src, javadoc_map=None)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "UniversalDao" in content
        assert "](../javadoc/" not in content


# ---------------------------------------------------------------------------
# Task 2-H: :javadoc_url: external link resolution
# ---------------------------------------------------------------------------

class TestJavadocUrlRoleResolution:
    """:javadoc_url:`LinkText <URL>` resolves to external MD link."""

    def _extract(self, rst_source: str) -> "DocumentParts":
        from scripts.common.rst_ast import parse
        from scripts.common.rst_ast_visitor import extract_document
        from pathlib import Path
        doctree, _ = parse(rst_source, source_path=Path("/repo/test.rst"))
        return extract_document(doctree, label_map={}, source_path=Path("/repo/test.rst"))

    def test_external_link_emitted(self):
        """:javadoc_url:`LinkText <URL>` → [LinkText](URL)."""
        src = (
            "Title\n=====\n\n"
            ":javadoc_url:`Nablarch API <https://nablarch.github.io/docs/>`\n"
        )
        parts = self._extract(src)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "[Nablarch API](https://nablarch.github.io/docs/)" in content

    def test_no_angle_brackets_emits_raw(self):
        """:javadoc_url:`URL` (no angle brackets) → raw text fallback."""
        src = (
            "Title\n=====\n\n"
            ":javadoc_url:`https://example.com/`\n"
        )
        parts = self._extract(src)
        content = parts.top_content + "\n".join(s.content for s in parts.sections)
        assert "https://example.com/" in content
