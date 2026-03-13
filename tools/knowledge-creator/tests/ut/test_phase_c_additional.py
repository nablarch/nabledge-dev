"""Test additional Phase C checks (A1-A3)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from phase_c_structure_check import PhaseCStructureCheck


def _make_checker():
    return PhaseCStructureCheck.__new__(PhaseCStructureCheck)


class TestHintsMinimum:

    def test_hints_below_3_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a1 = [w for w in warnings if w.startswith("A1:")]
        assert len(a1) == 1
        assert "s1" in a1[0]

    def test_hints_3_or_more_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A1:")]) == 0


class TestHintsJapanese:

    def test_no_japanese_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["Handler", "Config", "Setup"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A2:")]) == 1

    def test_with_japanese_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["Handler", "ハンドラ", "Config"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A2:")]) == 0


class TestFileSizeAnomaly:

    def test_too_small_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge, separators=(',', ':')))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a3 = [w for w in warnings if w.startswith("A3:")]
        if os.path.getsize(str(json_path)) < 300:
            assert len(a3) == 1

    def test_normal_size_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 500}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge, indent=2))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a3 = [w for w in warnings if w.startswith("A3:")]
        if os.path.getsize(str(json_path)) >= 300:
            assert len(a3) == 0
