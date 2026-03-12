"""Phase D _compute_content_warnings unit tests. No AI, runs fast."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from conftest import load_fixture


@pytest.fixture
def checker(ctx):
    from phase_d_content_check import PhaseDContentCheck
    return PhaseDContentCheck(ctx, dry_run=True)


class TestComputeContentWarnings:

    def test_clean_knowledge_returns_no_warnings(self, checker):
        """Valid knowledge file produces no warnings."""
        k = load_fixture("sample_knowledge.json")
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert warnings == []

    def test_s6_empty_hints(self, checker):
        """S6: Empty hints array triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S6" in w for w in warnings)

    def test_s7_empty_section_content(self, checker):
        """S7: Empty section content triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["s1"] = ""
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S7" in w for w in warnings)

    def test_s9_section_count_less_than_headings(self, checker):
        """S9: Fewer sections than source headings triggers warning."""
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["s2"]
        k["index"] = [e for e in k["index"] if e["id"] != "s2"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S9" in w for w in warnings)

    def test_s9_with_split_file_info(self, checker):
        """S9: Uses section_range from file_info for split files."""
        k = load_fixture("sample_knowledge.json")
        # Only 2 sections, but file_info says 5 section headings
        file_info = {
            "section_range": {
                "sections": ["a", "b", "c", "d", "e"]
            }
        }
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", file_info)
        assert any("S9" in w for w in warnings)

    def test_s13_short_section(self, checker):
        """S13: Section shorter than 20 chars triggers warning."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["s1"] = "短い"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S13" in w for w in warnings)

    def test_s13_nashi_excluded(self, checker):
        """S13: 'なし。' is allowed even though < 20 chars."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["s1"] = "なし。"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert not any("S13" in w for w in warnings)

    def test_multiple_warnings(self, checker):
        """Multiple issues produce multiple warnings."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []      # S6
        k["sections"]["s1"] = ""   # S7
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S6" in w for w in warnings)
        assert any("S7" in w for w in warnings)
