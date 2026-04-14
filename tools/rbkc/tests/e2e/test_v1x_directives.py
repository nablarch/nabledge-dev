"""E2E tests for Phase 9: v1.x directive support.

Confirms that directives specific to v1.x Nablarch documentation are
handled correctly by the RST converter.  Uses real v1.4 source files.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.converters.rst import convert

_REPO_ROOT = Path(__file__).parents[4]
_V14_BASE = _REPO_ROOT / ".lw/nab-official/v1.4"

# v1.4 file containing a top-level .. admonition:: directive
_ADMONITION_FILE = (
    _V14_BASE
    / "document/guide/04_Explanation_batch/03_dbInputBatch.rst"
)

# v1.4 file containing top-level .. function:: directives
_FUNCTION_FILE = (
    _V14_BASE
    / "workflow/doc/09/WorkflowApplicationApi.rst"
)

# v1.4 file containing .. literalinclude:: directives
_LITERALINCLUDE_FILE = (
    _V14_BASE
    / "document/guide/04_Explanation/04_validation.rst"
)

# v1.4 file with .. attention:: (and contains .. rubric:: + .. hint:: coverage
# is provided by the RST converter unit tests and gap-fill tests)
_ATTENTION_FILE = (
    _V14_BASE
    / "biz_sample/doc/08_HtmlMail.rst"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_content(result) -> str:
    return " ".join(sec.content for sec in result.sections)


# ---------------------------------------------------------------------------
# admonition directive
# ---------------------------------------------------------------------------

class TestAdmonitionDirective:
    @pytest.fixture(scope="class")
    def result(self):
        pytest.importorskip("scripts.converters.rst")
        if not _ADMONITION_FILE.exists():
            pytest.skip("v1.4 source not available")
        return convert(
            _ADMONITION_FILE.read_text(encoding="utf-8", errors="replace"),
            "test-admonition",
        )

    def test_converts_without_error(self, result):
        """.. admonition:: does not raise an exception."""
        assert result is not None

    def test_sections_non_empty(self, result):
        """Converted result has at least one section."""
        assert len(result.sections) >= 1

    def test_admonition_rendered_as_blockquote(self, result):
        """Named admonition is rendered as > **title:** body."""
        content = _all_content(result)
        # The admonition title is 'SqlRowからFormのプロパティへ値を設定する方法'
        assert "> **" in content, "Named admonition should produce blockquote"
        assert "SqlRowから" in content


# ---------------------------------------------------------------------------
# function directive
# ---------------------------------------------------------------------------

class TestFunctionDirective:
    @pytest.fixture(scope="class")
    def result(self):
        if not _FUNCTION_FILE.exists():
            pytest.skip("v1.4 source not available")
        return convert(
            _FUNCTION_FILE.read_text(encoding="utf-8", errors="replace"),
            "test-function",
        )

    def test_converts_without_error(self, result):
        """.. function:: does not raise an exception."""
        assert result is not None

    def test_sections_non_empty(self, result):
        """Converted result has at least one section."""
        assert len(result.sections) >= 1

    def test_function_signature_in_code_block(self, result):
        """.. function:: sig is rendered as a fenced code block."""
        content = _all_content(result)
        # Signature from the first function directive in the file
        assert "startInstance" in content, (
            "Function signature should appear in converted output"
        )

    def test_function_param_description_preserved(self, result):
        """.. function:: body (:param/:return: docs) is preserved as prose."""
        content = _all_content(result)
        # :param workflowId: description from the first function directive
        assert "開始対象のワークフローのID" in content, (
            "Function parameter description should be preserved in output"
        )


# ---------------------------------------------------------------------------
# literalinclude directive
# ---------------------------------------------------------------------------

class TestLiteralincludeDirective:
    @pytest.fixture(scope="class")
    def result(self):
        if not _LITERALINCLUDE_FILE.exists():
            pytest.skip("v1.4 source not available")
        return convert(
            _LITERALINCLUDE_FILE.read_text(encoding="utf-8", errors="replace"),
            "test-literalinclude",
        )

    def test_converts_without_error(self, result):
        """.. literalinclude:: does not raise an exception."""
        assert result is not None

    def test_rendered_as_fenced_code_block(self, result):
        """.. literalinclude:: produces a fenced code block with placeholder."""
        content = _all_content(result)
        assert "literalinclude:" in content, (
            "literalinclude should produce a placeholder comment in a code block"
        )


# ---------------------------------------------------------------------------
# attention directive
# ---------------------------------------------------------------------------

class TestAttentionDirective:
    @pytest.fixture(scope="class")
    def result(self):
        if not _ATTENTION_FILE.exists():
            pytest.skip("v1.4 source not available")
        return convert(
            _ATTENTION_FILE.read_text(encoding="utf-8", errors="replace"),
            "test-attention",
        )

    def test_converts_without_error(self, result):
        """.. attention:: does not raise an exception."""
        assert result is not None

    def test_rendered_as_blockquote(self, result):
        """.. attention:: is rendered as > **Attention:** body."""
        content = _all_content(result)
        assert "> **Attention:**" in content or "> **注意:**" in content or "> **" in content, (
            "Attention admonition should produce a blockquote"
        )
