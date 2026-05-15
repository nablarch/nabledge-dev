"""Unit tests for index.py — processing_patterns semantics (Phase 21-K).

processing_patterns is derived from the mapping-assigned type/category:
- type == "processing-pattern" → category (e.g. "nablarch-batch")
- any other type → ""

This matches KC's semantics (phase_f_finalize.py:303).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.create.index import generate_index


@dataclass
class _FakeFI:
    """Minimal FileInfo stand-in for index tests."""
    file_id: str
    type: str
    category: str
    output_path: str
    source_path: Path = Path(".")
    format: str = "rst"


def _write_json(knowledge_dir: Path, output_path: str, data: dict) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _read_entries(index_path: Path) -> list[list[str]]:
    """Parse TOON data lines into list of fields per entry."""
    lines = index_path.read_text(encoding="utf-8").splitlines()
    entries: list[list[str]] = []
    for line in lines:
        if line.startswith("  "):
            fields = [f.strip() for f in line[2:].split(",")]
            entries.append(fields)
    return entries


class TestProcessingPatternsSemantics:
    """processing_patterns column reflects mapping-assigned type/category."""

    def test_processing_pattern_type_uses_category_as_pp(self, tmp_path):
        """type == 'processing-pattern' → processing_patterns == category."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "processing-pattern/nablarch-batch/nablarch-batch-intro.json", {
            "id": "nablarch-batch-intro",
            "title": "Nablarch Batch 概要",
            "no_knowledge_content": False,
            "sections": [],
        })
        fi = _FakeFI(
            file_id="nablarch-batch-intro",
            type="processing-pattern",
            category="nablarch-batch",
            output_path="processing-pattern/nablarch-batch/nablarch-batch-intro.json",
        )
        idx = tmp_path / "index.toon"
        n = generate_index([fi], kn, "6", idx)
        assert n == 1
        entries = _read_entries(idx)
        assert len(entries) == 1
        title, type_, category, pp, path = entries[0]
        assert type_ == "processing-pattern"
        assert category == "nablarch-batch"
        assert pp == "nablarch-batch"  # pp == category

    def test_non_processing_pattern_type_has_empty_pp(self, tmp_path):
        """Any non-processing-pattern type → processing_patterns == ''."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/handlers/handlers-error.json", {
            "id": "handlers-error",
            "title": "Error Handler",
            "no_knowledge_content": False,
            "sections": [],
        })
        fi = _FakeFI(
            file_id="handlers-error",
            type="component",
            category="handlers",
            output_path="component/handlers/handlers-error.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        assert entries[0][1] == "component"
        assert entries[0][2] == "handlers"
        assert entries[0][3] == ""  # pp empty

    def test_about_type_has_empty_pp(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "about/release-notes/rn.json", {
            "id": "rn", "title": "RN",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI(
            file_id="rn", type="about", category="release-notes",
            output_path="about/release-notes/rn.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        assert entries[0][1] == "about"
        assert entries[0][2] == "release-notes"
        assert entries[0][3] == ""

    def test_no_hints_field_injected_into_pp(self, tmp_path):
        """Even if JSON contains a stray 'hints' field, it must NOT leak into pp.

        Regression guard for the pre-Phase-21-K bug where _collect_hints(data)
        aggregated JSON hints into processing_patterns.
        """
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib",
            "hints": ["stray-top-keyword"],
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "S", "content": "c", "hints": ["stray-sec-keyword"]},
            ],
        })
        fi = _FakeFI(
            file_id="lib", type="component", category="libraries",
            output_path="component/libraries/lib.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        # All mapping-derived columns must stay clean — not just pp
        assert entries[0][1] == "component"
        assert entries[0][2] == "libraries"
        assert entries[0][3] == ""
        assert "stray-top-keyword" not in idx.read_text(encoding="utf-8")
        assert "stray-sec-keyword" not in idx.read_text(encoding="utf-8")


class TestGenerateIndexEdgeCases:
    def test_empty_file_infos_yields_header_only(self, tmp_path):
        """Empty file_infos → header with 0-count, no data rows."""
        kn = tmp_path / "knowledge"
        kn.mkdir()
        idx = tmp_path / "index.toon"
        n = generate_index([], kn, "6", idx)
        assert n == 0
        text = idx.read_text(encoding="utf-8")
        assert "files[0,]" in text
        assert _read_entries(idx) == []

    def test_entries_sorted_by_path(self, tmp_path):
        """Input order is not significant — output is sorted by path for determinism."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "z/z/last.json", {
            "id": "last", "title": "Last",
            "no_knowledge_content": False, "sections": [],
        })
        _write_json(kn, "a/a/first.json", {
            "id": "first", "title": "First",
            "no_knowledge_content": False, "sections": [],
        })
        # Pass in reverse alphabetical order
        fis = [
            _FakeFI("last", "z", "z", "z/z/last.json"),
            _FakeFI("first", "a", "a", "a/a/first.json"),
        ]
        idx = tmp_path / "index.toon"
        generate_index(fis, kn, "6", idx)
        entries = _read_entries(idx)
        paths = [e[-1] for e in entries]
        assert paths == ["a/a/first.json", "z/z/last.json"]


class TestNoKnowledgeContentExcluded:
    def test_no_knowledge_content_file_omitted(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "a/b/keep.json", {
            "id": "keep", "title": "Keep",
            "no_knowledge_content": False, "sections": [],
        })
        _write_json(kn, "a/b/skip.json", {
            "id": "skip", "title": "Skip",
            "no_knowledge_content": True, "sections": [],
        })
        keep = _FakeFI("keep", "a", "b", "a/b/keep.json")
        skip = _FakeFI("skip", "a", "b", "a/b/skip.json")
        idx = tmp_path / "index.toon"
        n = generate_index([keep, skip], kn, "6", idx)
        assert n == 1
        entries = _read_entries(idx)
        assert len(entries) == 1
        assert entries[0][0] == "Keep"


class TestMissingJsonSkipped:
    def test_file_info_without_json_is_skipped(self, tmp_path):
        """FileInfo whose JSON was not written (e.g. failed conversion) is skipped, not crashed."""
        kn = tmp_path / "knowledge"
        fi = _FakeFI("nonexistent", "component", "handlers", "component/handlers/nonexistent.json")
        idx = tmp_path / "index.toon"
        n = generate_index([fi], kn, "6", idx)
        assert n == 0


class TestTitleCommaEscape:
    def test_comma_in_title_replaced_with_japanese_comma(self, tmp_path):
        """TOON field separator is ASCII comma — commas in title would break the format."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "a/b/comma.json", {
            "id": "comma", "title": "Title, with, commas",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI("comma", "a", "b", "a/b/comma.json")
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        text = idx.read_text(encoding="utf-8")
        assert "Title、 with、 commas" in text
        # Confirm no ASCII commas bleed into the title field
        assert "Title, with" not in text
