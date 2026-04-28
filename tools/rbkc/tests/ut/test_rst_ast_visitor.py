"""Unit tests for scripts/common/rst_ast_visitor — visit_raw 3-block state machine."""
from __future__ import annotations

import pytest
from docutils import nodes

from scripts.common.rst_ast_visitor import _MDVisitor
from scripts.common.rst_ast import normalise_raw_html


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
        assert "**ハンドラ処理概要**" in result
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
        assert "**ハンドラ処理概要**" in result
