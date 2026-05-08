"""Unit tests for scripts/common/rst_ast_visitor — visit_raw 3-block state machine, visit_image, and visit_container (toctree)."""
from __future__ import annotations

import pytest
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
