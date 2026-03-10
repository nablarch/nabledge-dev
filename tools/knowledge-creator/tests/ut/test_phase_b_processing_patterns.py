"""Tests for Phase B: _post_process_knowledge processing_patterns handling."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

from phase_b_generate import PhaseBGenerate


def make_phase_b(ctx):
    """Create a PhaseBGenerate instance with mock."""
    import subprocess

    def mock_run_claude(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")

    return PhaseBGenerate(ctx, run_claude_fn=mock_run_claude)


class TestPostProcessKnowledge:

    def test_post_process_removes_pp_from_sections(self, ctx):
        """When AI output has processing-patterns key in sections dict and no top-level
        processing_patterns, _post_process_knowledge should move it to top level."""
        phase_b = make_phase_b(ctx)
        knowledge = {
            "id": "some-file",
            "title": "Some File",
            "index": [
                {"id": "overview", "title": "Overview", "hints": []},
                {"id": "processing-patterns", "title": "Processing Patterns", "hints": []}
            ],
            "sections": {
                "overview": "Some content.",
                "processing-patterns": "restful-web-service"
            }
        }
        file_info = {"type": "component", "category": "web", "format": "rst"}

        result = phase_b._post_process_knowledge(knowledge, file_info)

        assert "processing-patterns" not in result["sections"], \
            "processing-patterns key should be removed from sections"
        assert result.get("processing_patterns") == ["restful-web-service"], \
            "processing_patterns should be set from sections value"

    def test_post_process_injects_pp_for_processing_pattern_type(self, ctx):
        """When file_info has type=processing-pattern and category=web-application,
        _post_process_knowledge should set processing_patterns: [web-application]."""
        phase_b = make_phase_b(ctx)
        knowledge = {
            "id": "some-file",
            "title": "Some File",
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Some content."
            }
        }
        file_info = {"type": "processing-pattern", "category": "web-application", "format": "rst"}

        result = phase_b._post_process_knowledge(knowledge, file_info)

        assert result.get("processing_patterns") == ["web-application"], \
            "For type=processing-pattern, processing_patterns should always be [category]"

    def test_post_process_adds_empty_pp_if_missing(self, ctx):
        """When AI output has no processing_patterns and file type is not processing-pattern,
        should add processing_patterns: []."""
        phase_b = make_phase_b(ctx)
        knowledge = {
            "id": "some-file",
            "title": "Some File",
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Some content."
            }
        }
        file_info = {"type": "component", "category": "web", "format": "rst"}

        result = phase_b._post_process_knowledge(knowledge, file_info)

        assert "processing_patterns" in result, \
            "processing_patterns field should be added when missing"
        assert result["processing_patterns"] == [], \
            "processing_patterns should be empty list when no value found"

    def test_post_process_removes_pp_index_entry(self, ctx):
        """When AI output has processing-patterns in both sections AND index,
        both should be removed."""
        phase_b = make_phase_b(ctx)
        knowledge = {
            "id": "some-file",
            "title": "Some File",
            "index": [
                {"id": "overview", "title": "Overview", "hints": []},
                {"id": "processing-patterns", "title": "Processing Patterns", "hints": []}
            ],
            "sections": {
                "overview": "Some content.",
                "processing-patterns": "restful-web-service"
            }
        }
        file_info = {"type": "component", "category": "web", "format": "rst"}

        result = phase_b._post_process_knowledge(knowledge, file_info)

        assert "processing-patterns" not in result["sections"], \
            "processing-patterns key should be removed from sections"
        pp_ids = [e["id"] for e in result.get("index", [])]
        assert "processing-patterns" not in pp_ids, \
            "processing-patterns entry should be removed from index"
