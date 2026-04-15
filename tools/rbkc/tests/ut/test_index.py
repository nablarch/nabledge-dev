"""Unit tests for index.py — TOON format generation."""
import json
import pytest
from pathlib import Path
from scripts.index import _collect_hints, generate_index


# ---------------------------------------------------------------------------
# _collect_hints — comma sanitization
# ---------------------------------------------------------------------------

class TestCollectHintsCommaSanitization:
    def _data(self, hints: list[str]) -> dict:
        return {"sections": [{"hints": hints}]}

    def test_hint_with_comma_is_sanitized(self):
        """A hint containing a comma must have the comma replaced so the TOON
        field boundary is preserved."""
        data = self._data(["foo,bar"])
        result = _collect_hints(data)
        assert "," not in result

    def test_hint_with_comma_content_preserved(self):
        """After sanitizing the comma, the surrounding text must still appear."""
        data = self._data(["foo,bar"])
        result = _collect_hints(data)
        assert "foo" in result
        assert "bar" in result

    def test_hints_without_comma_unchanged(self):
        """Hints that have no commas should pass through as-is."""
        data = self._data(["alpha", "beta"])
        result = _collect_hints(data)
        assert "alpha" in result
        assert "beta" in result

    def test_multiple_hints_space_joined(self):
        """Multiple hints should be space-joined (no commas between them)."""
        data = self._data(["A", "B", "C"])
        result = _collect_hints(data)
        assert result == "A B C"


# ---------------------------------------------------------------------------
# generate_index — TOON field count per line
# ---------------------------------------------------------------------------

class TestGenerateIndexToonFieldCount:
    def _make_knowledge_dir(self, tmp_path, hint: str) -> Path:
        kd = tmp_path / "knowledge" / "component" / "handlers"
        kd.mkdir(parents=True)
        data = {
            "id": "test-file",
            "title": "Test",
            "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "S1", "content": "c", "hints": [hint]}],
        }
        (kd / "test.json").write_text(json.dumps(data), encoding="utf-8")
        return tmp_path / "knowledge"

    def test_toon_line_has_exactly_five_fields(self, tmp_path):
        """Each data line must have exactly 5 comma-separated fields.

        A hint that contains a comma would split the processing_patterns field
        into multiple parts, giving more than 5 fields.
        """
        hint_with_comma = "foo,bar"
        kd = self._make_knowledge_dir(tmp_path, hint_with_comma)
        out = tmp_path / "index.toon"
        generate_index(kd, "6", out)

        content = out.read_text(encoding="utf-8")
        # Find the data line (starts with "  ")
        data_lines = [ln for ln in content.splitlines() if ln.startswith("  ")]
        assert data_lines, "No data lines found in index.toon"
        for line in data_lines:
            fields = line.strip().split(", ")
            assert len(fields) == 5, (
                f"Expected 5 fields but got {len(fields)}: {fields!r}"
            )
