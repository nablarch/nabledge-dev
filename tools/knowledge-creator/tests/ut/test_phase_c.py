"""Phase C structure validation unit tests. No AI, runs fast."""
import os
import json
import pytest
from conftest import load_fixture


def write_knowledge(ctx, knowledge):
    path = os.path.join(
        ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)

    # Create dummy asset files if referenced in knowledge
    file_id = knowledge.get("id", "handlers-sample-handler")
    assets_dir = os.path.join(ctx.knowledge_dir, f"component/handlers/assets/{file_id}")
    import re
    for section_content in knowledge.get("sections", {}).values():
        # Find asset references like assets/file-id/filename (including nested paths)
        asset_refs = re.findall(r'assets/' + re.escape(file_id) + r'/([^\)]+)', section_content)
        if asset_refs:
            os.makedirs(assets_dir, exist_ok=True)
            for asset_file in asset_refs:
                asset_path = os.path.join(assets_dir, asset_file)
                # Create parent directories for nested paths
                os.makedirs(os.path.dirname(asset_path), exist_ok=True)
                # Create dummy file if not exists
                if not os.path.exists(asset_path):
                    with open(asset_path, "w", encoding="utf-8") as af:
                        af.write("dummy asset content")

    return path


class TestStructureValidation:

    def test_valid_passes(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        assert PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst") == []

    def test_s3_index_without_section(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["overview"]
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S3" in e for e in errors)

    def test_s4_section_without_index(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["orphan"] = "content"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S4" in e for e in errors)

    def test_s5_non_kebab(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["index"].append({"id": "badCamel", "title": "Bad", "hints": ["x"]})
        k["sections"]["badCamel"] = "content"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S5" in e for e in errors)

    def test_s6_empty_hints(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S6" in e for e in errors)

    def test_s7_empty_section(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = ""
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S7" in e for e in errors)

    def test_s8_id_mismatch(self, ctx):
        from phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["id"] = "wrong-id"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S8" in e for e in errors)

    def test_s17_empty_knowledge_rejected(self, ctx):
        """S17: no_knowledge_content=False with empty index+sections must fail."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = {
            "id": "handlers-sample-handler",
            "title": "サンプルハンドラ",
            "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [],
            "sections": {}
        }
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S17" in e for e in errors)

    def test_s17_no_knowledge_content_true_not_affected(self, ctx):
        """S17 must not trigger when no_knowledge_content=True."""
        from phase_c_structure_check import PhaseCStructureCheck
        k = {
            "id": "handlers-sample-handler",
            "title": "サンプルハンドラ",
            "no_knowledge_content": True,
            "official_doc_urls": ["https://example.com"],
            "index": [],
            "sections": {}
        }
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert not any("S17" in e for e in errors)
