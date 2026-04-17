"""Unit tests for run.py — _hints_index exception handling + V0 hints carry-over."""
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from scripts.run import _hints_index, load_existing_hints


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


# ---------------------------------------------------------------------------
# V0: load_existing_hints — read hints from existing RBKC-format JSON files
# ---------------------------------------------------------------------------

class TestLoadExistingHints:
    """load_existing_hints(output_dir) -> {file_id: {section_title: hints}}

    Reads RBKC-format knowledge JSON files (sections as list) and returns
    a nested dict for hints carry-over. KC-format files (sections as dict)
    are skipped.
    """

    def _write_rbkc_json(self, path: Path, file_id: str, sections: list) -> None:
        """Write a RBKC-format knowledge JSON (sections as list of dicts)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "id": file_id,
            "title": "Test",
            "no_knowledge_content": False,
            "sections": sections,
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _write_kc_json(self, path: Path, file_id: str) -> None:
        """Write a KC-format knowledge JSON (sections as dict — old format)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "id": file_id,
            "title": "Old Format",
            "index": [{"id": "s1", "title": "概要", "hints": ["OldHint"]}],
            "sections": {"s1": "section content"},  # dict = KC format
        }
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_single_file_hints_extracted(self, tmp_path):
        """RBKC-format file with hints → hints extracted into nested dict."""
        self._write_rbkc_json(
            tmp_path / "cat" / "guide.json",
            "cat-guide",
            [
                {"id": "s1", "title": "概要", "content": "...", "hints": ["hint1", "hint2"]},
                {"id": "s2", "title": "詳細", "content": "...", "hints": ["hint3"]},
            ],
        )
        result = load_existing_hints(tmp_path)
        assert result["cat-guide"]["概要"] == ["hint1", "hint2"]
        assert result["cat-guide"]["詳細"] == ["hint3"]

    def test_empty_hints_section_preserved(self, tmp_path):
        """Section with empty hints list → preserved as empty list."""
        self._write_rbkc_json(
            tmp_path / "cat" / "guide.json",
            "cat-guide",
            [{"id": "s1", "title": "概要", "content": "...", "hints": []}],
        )
        result = load_existing_hints(tmp_path)
        assert "cat-guide" in result
        assert result["cat-guide"]["概要"] == []

    def test_kc_format_files_skipped(self, tmp_path):
        """KC-format files (sections as dict) are skipped — not included."""
        self._write_kc_json(tmp_path / "cat" / "old.json", "cat-old")
        result = load_existing_hints(tmp_path)
        assert "cat-old" not in result

    def test_multiple_files(self, tmp_path):
        """Multiple RBKC-format files → all extracted with correct hint values."""
        self._write_rbkc_json(
            tmp_path / "cat" / "a.json",
            "cat-a",
            [{"id": "s1", "title": "S1", "content": "...", "hints": ["hintA"]}],
        )
        self._write_rbkc_json(
            tmp_path / "cat" / "b.json",
            "cat-b",
            [{"id": "s1", "title": "S1", "content": "...", "hints": ["hintB"]}],
        )
        result = load_existing_hints(tmp_path)
        assert result["cat-a"]["S1"] == ["hintA"]
        assert result["cat-b"]["S1"] == ["hintB"]

    def test_mixed_format_directory(self, tmp_path):
        """Directory with both RBKC and KC files → only RBKC files extracted."""
        self._write_rbkc_json(
            tmp_path / "cat" / "new.json",
            "cat-new",
            [{"id": "s1", "title": "S1", "content": "...", "hints": ["newHint"]}],
        )
        self._write_kc_json(tmp_path / "cat" / "old.json", "cat-old")
        result = load_existing_hints(tmp_path)
        assert "cat-new" in result
        assert "cat-old" not in result
        assert result["cat-new"]["S1"] == ["newHint"]

    def test_missing_id_file_excluded(self, tmp_path):
        """File with no 'id' field → excluded from result."""
        path = tmp_path / "cat" / "no_id.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "title": "No ID",
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "概要", "content": "...", "hints": ["h1"]}],
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        result = load_existing_hints(tmp_path)
        assert result == {}

    def test_corrupt_json_skipped_others_included(self, tmp_path):
        """Corrupt JSON is silently skipped; valid sibling files are still loaded."""
        (tmp_path / "cat").mkdir(parents=True)
        (tmp_path / "cat" / "corrupt.json").write_text("NOT JSON", encoding="utf-8")
        self._write_rbkc_json(
            tmp_path / "cat" / "good.json",
            "cat-good",
            [{"id": "s1", "title": "S1", "content": "...", "hints": ["ok"]}],
        )
        result = load_existing_hints(tmp_path)
        assert "cat-good" in result
        assert len(result) == 1

    def test_empty_directory_returns_empty_dict(self, tmp_path):
        """No JSON files → returns empty dict."""
        result = load_existing_hints(tmp_path)
        assert result == {}

    def test_nonexistent_directory_returns_empty_dict(self, tmp_path):
        """Non-existent output_dir → returns empty dict (no error)."""
        result = load_existing_hints(tmp_path / "nonexistent")
        assert result == {}

    def test_no_knowledge_content_file_included(self, tmp_path):
        """no_knowledge_content=True files are included if they have sections with hints."""
        path = tmp_path / "cat" / "toc.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "id": "cat-toc",
            "title": "Toc",
            "no_knowledge_content": True,
            "sections": [{"id": "s1", "title": "概要", "content": "", "hints": []}],
        }
        path.write_text(json.dumps(data), encoding="utf-8")
        result = load_existing_hints(tmp_path)
        assert "cat-toc" in result

    def test_lookup_hints_uses_existing(self, tmp_path):
        """After load_existing_hints, lookup_hints returns carry-over hints."""
        from scripts.run import lookup_hints_with_fallback
        self._write_rbkc_json(
            tmp_path / "cat" / "guide.json",
            "cat-guide",
            [{"id": "s1", "title": "Overview", "content": "...", "hints": ["carried"]}],
        )
        existing = load_existing_hints(tmp_path)
        # lookup_hints_with_fallback prefers existing hints over kc_hints_idx
        hints = lookup_hints_with_fallback(existing, {}, "cat-guide", "Overview")
        assert hints == ["carried"]

    def test_lookup_hints_falls_back_to_kc(self, tmp_path):
        """When no existing hints for file, fallback to KC hints index."""
        from scripts.run import lookup_hints_with_fallback
        kc_idx = {"cat-new": {"Overview": ["fromKC"]}}
        hints = lookup_hints_with_fallback({}, kc_idx, "cat-new", "Overview")
        assert hints == ["fromKC"]

    def test_lookup_hints_existing_file_unknown_section_returns_empty(self, tmp_path):
        """File in existing_hints but section title absent → [] (no KC fallback)."""
        from scripts.run import lookup_hints_with_fallback
        existing = {"cat-guide": {"Overview": ["carried"]}}
        kc_idx = {"cat-guide": {"NonExistentSection": ["fromKC"]}}
        hints = lookup_hints_with_fallback(existing, kc_idx, "cat-guide", "NonExistentSection")
        # existing_hints takes precedence — unknown section returns [] not KC hints
        assert hints == []
