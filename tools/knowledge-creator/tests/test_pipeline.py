"""End-to-end pipeline tests with mocked claude -p."""
import os
import json
import pytest
from conftest import make_mock_run_claude, load_fixture


class TestPipelineBCD:
    """Phase B -> C -> D pipeline."""

    def test_generate_and_validate_clean(self, ctx, mock_claude):
        """Normal flow: generate -> structure pass -> content clean."""
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_c_structure_check import PhaseCStructureCheck
        from steps.phase_d_content_check import PhaseDContentCheck

        # Phase B
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_path)
        knowledge = json.load(open(knowledge_path, encoding="utf-8"))
        assert knowledge["id"] == "handlers-sample-handler"
        assert len(knowledge["sections"]) == 2
        assert "overview" in knowledge["sections"]
        assert "module-list" in knowledge["sections"]

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
        from steps.phase_b_generate import PhaseBGenerate

        # Phase B: generate
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
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
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_c_structure_check import PhaseCStructureCheck
        from steps.phase_d_content_check import PhaseDContentCheck
        from steps.phase_e_fix import PhaseEFix

        # B: generate
        PhaseBGenerate(ctx, run_claude_fn=make_mock_run_claude()).run()

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
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_f_finalize import PhaseFFinalize

        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()
        PhaseFFinalize(ctx, run_claude_fn=mock_claude).run()

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
