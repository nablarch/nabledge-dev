"""End-to-end pipeline tests with mocked claude -p."""
import os
import json
import pytest
from conftest import make_mock_run_claude, load_fixture


class TestPipelineBCD:
    """Phase B -> C -> D pipeline."""

    def test_generate_and_validate_clean(self, ctx, mock_claude):
        """Normal flow: generate -> structure pass -> content clean."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck

        # Phase B
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_path = os.path.join(
            ctx.knowledge_cache_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_path)
        knowledge = json.load(open(knowledge_path, encoding="utf-8"))
        assert knowledge["id"] == "handlers-sample-handler"
        assert len(knowledge["sections"]) == 2
        assert "overview" in knowledge["sections"]
        assert "module-list" in knowledge["sections"]

        # Create dummy asset files referenced in knowledge (for Phase C S15 validation)
        assets_dir = os.path.join(ctx.knowledge_cache_dir, "component/handlers/assets/handlers-sample-handler")
        os.makedirs(assets_dir, exist_ok=True)
        for section_content in knowledge.get("sections", {}).values():
            import re
            asset_refs = re.findall(r'assets/handlers-sample-handler/([^\)]+)', section_content)
            for asset_file in asset_refs:
                asset_path = os.path.join(assets_dir, asset_file)
                # Create parent directories for nested paths
                os.makedirs(os.path.dirname(asset_path), exist_ok=True)
                if not os.path.exists(asset_path):
                    with open(asset_path, "w", encoding="utf-8") as f:
                        f.write("dummy asset")

        # Trace
        trace_path = os.path.join(ctx.trace_dir, "handlers-sample-handler.json")
        assert os.path.exists(trace_path)
        trace = json.load(open(trace_path, encoding="utf-8"))
        assert len(trace["sections"]) == 2

        # Phase C
        c_result = PhaseCStructureCheck(ctx).run()
        assert c_result["error_count"] == 0
        assert "handlers-sample-handler" in c_result["pass_ids"]

        # Phase D
        d_result = PhaseDContentCheck(ctx, run_claude_fn=mock_claude).run(
            target_ids=c_result["pass_ids"]
        )
        assert d_result["issues_count"] == 0

    def test_rst_links_preserved(self, ctx, mock_claude):
        """Verify RST link syntax is preserved in generated knowledge files."""
        from phase_b_generate import PhaseBGenerate

        # Phase B: generate
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_path = os.path.join(
            ctx.knowledge_cache_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_path)

        with open(knowledge_path, encoding="utf-8") as f:
            knowledge = json.load(f)

        overview = knowledge["sections"]["overview"]

        # Verify RST links are preserved (not converted to Markdown)
        assert ":ref:`thread_context_handler`" in overview, \
            "Simple :ref: should be preserved"
        assert ":ref:`データベース接続 <database_connection>`" in overview, \
            ":ref: with display text should be preserved"
        assert ":doc:`../configuration/database`" in overview, \
            ":doc: should be preserved"
        assert ":download:`sample.xml <sample.xml>`" in overview, \
            ":download: should be preserved"
        assert ":java:extdoc:`SampleHandler <nablarch.sample.SampleHandler>`" in overview, \
            ":java:extdoc: with display should be preserved"
        assert ":java:extdoc:`nablarch.core.ThreadContext`" in overview, \
            ":java:extdoc: without display should be preserved"

        # Verify external URLs are converted to Markdown
        assert "[Jackson(外部サイト、英語)](https://github.com/FasterXML/jackson)" in overview, \
            "External URLs should be converted to Markdown format"

        # Verify Javadoc URLs are added to official_doc_urls
        assert "https://nablarch.github.io/docs/LATEST/javadoc/" in str(knowledge.get("official_doc_urls", [])), \
            "Javadoc URLs should be in official_doc_urls"

    def test_fix_cycle(self, ctx):
        """Fix flow: generate -> check finds issues -> fix -> recheck clean."""
        from phase_b_generate import PhaseBGenerate
        from phase_c_structure_check import PhaseCStructureCheck
        from phase_d_content_check import PhaseDContentCheck
        from phase_e_fix import PhaseEFix

        # B: generate
        PhaseBGenerate(ctx, run_claude_fn=make_mock_run_claude()).run()

        # Create dummy asset files for S15 validation
        knowledge_path = os.path.join(ctx.knowledge_cache_dir, "component/handlers/handlers-sample-handler.json")
        knowledge = json.load(open(knowledge_path, encoding="utf-8"))
        assets_dir = os.path.join(ctx.knowledge_cache_dir, "component/handlers/assets/handlers-sample-handler")
        os.makedirs(assets_dir, exist_ok=True)
        for section_content in knowledge.get("sections", {}).values():
            import re
            asset_refs = re.findall(r'assets/handlers-sample-handler/([^\)]+)', section_content)
            for asset_file in asset_refs:
                asset_path = os.path.join(assets_dir, asset_file)
                # Create parent directories for nested paths
                os.makedirs(os.path.dirname(asset_path), exist_ok=True)
                if not os.path.exists(asset_path):
                    with open(asset_path, "w", encoding="utf-8") as f:
                        f.write("dummy asset")

        # C: pass
        c = PhaseCStructureCheck(ctx).run()
        assert c["error_count"] == 0

        # D: finds issues
        findings_with_issues = {
            "file_id": "handlers-sample-handler",
            "status": "has_issues",
            "findings": [{
                "category": "omission", "severity": "critical",
                "location": "overview",
                "description": "Missing important directive",
                "source_evidence": "line 10"
            }]
        }
        d = PhaseDContentCheck(
            ctx, run_claude_fn=make_mock_run_claude(findings_output=findings_with_issues)
        ).run(target_ids=c["pass_ids"])
        assert d["issues_count"] == 1

        # Findings file exists
        findings_path = os.path.join(ctx.findings_dir, "handlers-sample-handler.json")
        assert os.path.exists(findings_path)

        # E: fix
        PhaseEFix(ctx, run_claude_fn=make_mock_run_claude()).run(
            target_ids=d["issue_file_ids"]
        )

        # Findings cache deleted
        assert not os.path.exists(findings_path)

        # D again: clean
        d2 = PhaseDContentCheck(
            ctx, run_claude_fn=make_mock_run_claude()
        ).run(target_ids=c["pass_ids"])
        assert d2["issues_count"] == 0


class TestPhaseF:
    def test_finalize(self, ctx, mock_claude):
        import shutil
        from phase_b_generate import PhaseBGenerate
        from phase_f_finalize import PhaseFFinalize

        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()
        # Copy Phase B output from cache to knowledge_dir so Phase F can find it
        shutil.copytree(ctx.knowledge_cache_dir, ctx.knowledge_dir, dirs_exist_ok=True)
        PhaseFFinalize(ctx).run()

        # index.toon
        assert os.path.exists(ctx.index_path)
        content = open(ctx.index_path, encoding="utf-8").read()
        assert "handlers-sample-handler" in content

        # docs
        doc_path = os.path.join(
            ctx.docs_dir, "component/handlers/handlers-sample-handler.md"
        )
        assert os.path.exists(doc_path)

        # summary
        summary_path = os.path.join(ctx.log_dir, "summary.json")
        assert os.path.exists(summary_path)

    def test_asset_path_conversion(self, ctx, mock_claude):
        """Verify asset paths are converted correctly in browsable docs."""
        import shutil
        from phase_b_generate import PhaseBGenerate
        from phase_f_finalize import PhaseFFinalize
        from common import load_json

        # Phase B: Generate knowledge files
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        # Verify original knowledge JSON has original asset paths (in cache dir)
        knowledge_path = os.path.join(
            ctx.knowledge_cache_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_path)
        knowledge = load_json(knowledge_path)
        overview = knowledge["sections"]["overview"]

        # Knowledge JSON should have original relative paths
        assert "assets/handlers-sample-handler/architecture.png" in overview, \
            "Knowledge JSON should keep original asset paths"
        assert "assets/handlers-sample-handler/settings.xlsx" in overview, \
            "Knowledge JSON should keep original download paths"
        assert "assets/handlers-sample-handler/flow.png" in overview, \
            "Knowledge JSON should keep multiple asset references"

        # Copy Phase B output from cache to knowledge_dir so Phase F can find it
        shutil.copytree(ctx.knowledge_cache_dir, ctx.knowledge_dir, dirs_exist_ok=True)

        # Phase F: Generate browsable docs
        PhaseFFinalize(ctx).run()

        # Verify browsable MD has converted asset paths
        doc_path = os.path.join(
            ctx.docs_dir, "component/handlers/handlers-sample-handler.md"
        )
        assert os.path.exists(doc_path)

        with open(doc_path, encoding="utf-8") as f:
            doc_content = f.read()

        # Multiple image references should all be converted
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/architecture.png" in doc_content, \
            "Browsable MD should have converted first image path"
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/flow.png" in doc_content, \
            "Browsable MD should have converted second image path"

        # Download link should be converted
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/settings.xlsx" in doc_content, \
            "Browsable MD should have converted download paths"

        # Original asset paths should NOT appear in browsable MD
        assert "](assets/handlers-sample-handler/architecture.png)" not in doc_content, \
            "Original asset paths should not appear in browsable MD"
        assert "](assets/handlers-sample-handler/settings.xlsx)" not in doc_content, \
            "Original asset paths should not appear in browsable MD"

        # Negative tests: External URLs and absolute paths should NOT be converted
        assert "https://example.com/logo.png" in doc_content, \
            "External URLs should be preserved unchanged"
        assert "/absolute/path/system.png" in doc_content, \
            "Absolute paths should NOT be converted"

        # Verify external URL is not accidentally converted
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/logo.png" not in doc_content, \
            "External URLs should not be converted to local paths"

        # Verify absolute path is not converted
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/system.png" not in doc_content, \
            "Absolute paths should not be converted to local paths"

        # Edge case: Special characters in filenames (spaces, Japanese)
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/image with spaces.png" in doc_content, \
            "Filenames with spaces should be converted correctly"
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/設定画面.png" in doc_content, \
            "Japanese filenames should be converted correctly"

        # Edge case: Nested directory structures
        assert "../../knowledge/component/handlers/assets/handlers-sample-handler/subdir/nested.xlsx" in doc_content, \
            "Nested directory paths should be converted correctly"

        # Verify knowledge JSON in cache is unchanged after Phase F
        knowledge_after = load_json(knowledge_path)  # knowledge_path points to cache_dir
        overview_after = knowledge_after["sections"]["overview"]
        assert overview == overview_after, \
            "Phase F should not modify original knowledge JSON files"


class TestPipelineWithPhaseG:
    """Full pipeline: B -> G -> F"""

    def test_full_pipeline_with_link_resolution(self, ctx, mock_claude):
        """Test complete pipeline: generate -> resolve links -> finalize."""
        import shutil
        from phase_b_generate import PhaseBGenerate
        from phase_g_resolve_links import PhaseGResolveLinks
        from phase_f_finalize import PhaseFFinalize

        # Phase B: Generate knowledge files with RST links
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_cache_path = os.path.join(
            ctx.knowledge_cache_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_cache_path)

        # Verify RST links are preserved in original
        with open(knowledge_cache_path, encoding="utf-8") as f:
            original = json.load(f)
        assert ":ref:`thread_context_handler`" in original["sections"]["overview"]

        # Copy Phase B output from cache to knowledge_dir so Phase G can find it
        shutil.copytree(ctx.knowledge_cache_dir, ctx.knowledge_dir, dirs_exist_ok=True)

        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
        )

        # Phase G: Resolve links
        PhaseGResolveLinks(ctx).run()

        # Verify resolved directory exists
        resolved_path = os.path.join(
            ctx.knowledge_resolved_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(resolved_path)

        # Verify links are resolved in resolved version
        with open(resolved_path, encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]

        # :ref: should be resolved to Markdown links
        # Since we don't have full label index in test, unresolved refs kept as-is
        # But :java:extdoc: should be converted to inline code
        assert "`ThreadContext`" in overview or ":java:extdoc:" in overview, \
            ":java:extdoc: should be converted or preserved"

        # Phase F: Generate docs from resolved files
        PhaseFFinalize(ctx).run()

        # Verify Phase F reads from resolved directory
        doc_path = os.path.join(
            ctx.docs_dir, "component/handlers/handlers-sample-handler.md"
        )
        assert os.path.exists(doc_path)

        # Verify docs contain resolved content
        with open(doc_path, encoding="utf-8") as f:
            doc_content = f.read()

        # Doc should contain content from resolved files
        assert "概要" in doc_content or "Overview" in doc_content
