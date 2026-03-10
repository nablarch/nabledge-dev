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
        k["sections"]["overview"] = ""
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S7" in w for w in warnings)

    def test_s9_section_count_less_than_headings(self, checker):
        """S9: Fewer sections than source headings triggers warning."""
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["module-list"]
        k["index"] = [e for e in k["index"] if e["id"] != "module-list"]
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
        k["sections"]["overview"] = "短い"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S13" in w for w in warnings)

    def test_s13_nashi_excluded(self, checker):
        """S13: 'なし。' is allowed even though < 20 chars."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "なし。"
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert not any("S13" in w for w in warnings)

    def test_multiple_warnings(self, checker):
        """Multiple issues produce multiple warnings."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []      # S6
        k["sections"]["overview"] = ""   # S7
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        assert any("S6" in w for w in warnings)
        assert any("S7" in w for w in warnings)

    def test_s6_partial_hints_missing_terms(self, checker):
        """S6: Non-empty hints that are missing PascalCase class names trigger a warning."""
        k = load_fixture("sample_knowledge.json")
        # Remove SampleHandler from overview hints - it IS in the section content
        k["index"][0]["hints"] = ["nablarch.sample.SampleHandler", "ThreadContext", "Jackson"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_warnings = [w for w in warnings if "S6" in w and "missing terms" in w]
        assert len(s6_warnings) == 1
        assert "SampleHandler" in s6_warnings[0]

    def test_s6_at_prefix_hint_matches_content_term(self, checker):
        """S6: '@Entity' in hints matches 'Entity' extracted from content (no warning)."""
        k = load_fixture("sample_knowledge.json")
        # Add @SampleHandler to hints instead of SampleHandler - should still match
        hints = k["index"][0]["hints"]
        hints = ["@SampleHandler" if h == "SampleHandler" else h for h in hints]
        k["index"][0]["hints"] = hints
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w and "overview" in w]
        assert len(s6_missing) == 0

    def test_s6_at_prefix_content_matched_by_base_hint(self, checker):
        """S6: '@Entity' in content matched by 'Entity' in hints (no warning)."""
        k = load_fixture("sample_knowledge.json")
        # Add section content with @annotation that matches base hint name
        k["sections"]["overview"] = "@SampleHandler is the main handler."
        k["index"][0]["hints"] = ["SampleHandler", "ThreadContext", "Jackson"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w and "overview" in w]
        assert len(s6_missing) == 0

    def test_s6_exception_class_detected(self, checker):
        """S6: XxxException class in content not in hints triggers a warning."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "Throws DatabaseException when connection fails."
        k["index"][0]["hints"] = ["SampleHandler"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w]
        assert len(s6_missing) == 1
        assert "DatabaseException" in s6_missing[0]

    def test_s6_generic_terms_excluded(self, checker):
        """S6: Generic Java types like String, Object are not flagged as missing."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "Returns a String value from the Object."
        k["index"][0]["hints"] = ["SampleHandler"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w and "overview" in w]
        assert len(s6_missing) == 0

    def test_s6_empty_hints_no_duplicate_check(self, checker):
        """S6: Empty hints triggers empty warning, not missing terms warning."""
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_empty = [w for w in warnings if "S6" in w and "empty hints" in w]
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w]
        assert len(s6_empty) == 1
        assert len(s6_missing) == 0  # empty hints uses continue, no missing terms check

    def test_s6_url_terms_excluded(self, checker):
        """S6: PascalCase names embedded in URLs are not extracted."""
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = "See https://example.com/SomeHandler for details."
        k["index"][0]["hints"] = ["SampleHandler"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w and "overview" in w]
        assert len(s6_missing) == 0

    def test_s6_multiple_sections_independent(self, checker):
        """S6: Missing terms warning is emitted per section independently."""
        k = load_fixture("sample_knowledge.json")
        # overview: missing SampleHandler; module-list: clean
        k["index"][0]["hints"] = ["ThreadContext", "Jackson"]
        source = load_fixture("sample_source.rst")
        warnings = checker._compute_content_warnings(k, source, "rst", None)
        s6_missing = [w for w in warnings if "S6" in w and "missing terms" in w]
        assert len(s6_missing) == 1
        assert "overview" in s6_missing[0]
        assert "SampleHandler" in s6_missing[0]
