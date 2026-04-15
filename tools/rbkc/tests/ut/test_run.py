"""Unit tests for run.py — _hints_index exception handling."""
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from scripts.run import _hints_index


# ---------------------------------------------------------------------------
# _hints_index — exception handling
# ---------------------------------------------------------------------------

class TestHintsIndexExceptionHandling:
    def test_file_not_found_returns_empty_dict(self, tmp_path):
        """FileNotFoundError (cache absent) → return {} silently."""
        result = _hints_index(tmp_path, "99")
        assert result == {}

    def _make_cache(self, tmp_path, version="6"):
        """Create the knowledge cache directory structure under tmp_path."""
        knowledge_dir = (
            tmp_path / "tools/knowledge-creator/.cache" / f"v{version}" / "knowledge"
        )
        knowledge_dir.mkdir(parents=True)
        return knowledge_dir

    def test_json_decode_error_reraises(self, tmp_path):
        """JSONDecodeError (corrupt cache) → re-raise after warning."""
        knowledge_dir = self._make_cache(tmp_path)
        (knowledge_dir / "bad.json").write_text("NOT JSON", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            _hints_index(tmp_path, "6")

    def test_json_decode_error_prints_warning(self, tmp_path, capsys):
        """JSONDecodeError → warning message is printed to stderr."""
        knowledge_dir = self._make_cache(tmp_path)
        (knowledge_dir / "bad.json").write_text("NOT JSON", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            _hints_index(tmp_path, "6")

        captured = capsys.readouterr()
        assert "Warning" in captured.err
        assert "hints" in captured.err.lower()

    def test_valid_cache_returns_dict(self, tmp_path):
        """Valid KC cache → returns non-empty hints index."""
        knowledge_dir = self._make_cache(tmp_path)
        kc_data = {
            "id": "some-guide",
            "title": "ガイド",
            "no_knowledge_content": False,
            "index": [{"id": "s1", "title": "概要", "hints": ["HintA"]}],
            "sections": {},
        }
        (knowledge_dir / "guide.json").write_text(
            json.dumps(kc_data, ensure_ascii=False), encoding="utf-8"
        )
        result = _hints_index(tmp_path, "6")
        assert isinstance(result, dict)
        assert len(result) > 0
