"""Tests: no_knowledge_content handling in Phase C and Phase F."""
import os
import json
import pytest
from conftest import load_fixture


def _write_knowledge(ctx, knowledge, file_id="handlers-sample-handler"):
    path = os.path.join(ctx.knowledge_dir, f"component/handlers/{file_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    return path


class TestPhaseCNoContent:
    def test_no_content_true_with_empty_passes(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [], "index": [], "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert errors == []

    def test_no_content_true_with_non_empty_index_fails_s16(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [],
            "index": [{"id": "x", "title": "X", "hints": ["h"]}],
            "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S16" in e for e in errors)

    def test_no_content_true_with_non_empty_sections_fails_s16(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "no_knowledge_content": True,
            "official_doc_urls": [],
            "index": [], "sections": {"x": "content"}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S16" in e for e in errors)

    def test_no_content_missing_fails_s2(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        jp = _write_knowledge(ctx, {
            "id": "handlers-sample-handler", "title": "一覧",
            "official_doc_urls": [], "index": [], "sections": {}
        })
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, "", "rst")
        assert any("S2" in e and "no_knowledge_content" in e for e in errors)

    def test_existing_valid_knowledge_still_passes(self, ctx):
        """Regression: existing knowledge files with no_knowledge_content: false still pass."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        # After fixture update, k has no_knowledge_content: false
        jp = _write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        # Only verify no S2/S16 errors (S15 asset errors are expected in temp dir)
        assert not any("S2" in e or "S16" in e for e in errors)
