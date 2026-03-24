"""Test Phase V: Quality Evaluation."""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


class TestFactCollection:

    def test_collect_findings_summary(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "handler-a_r1.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical", "location": "s1", "description": "X"},
                {"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}
            ]
        }))
        (findings_dir / "handler-a_r2.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [{"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}]
        }))
        (findings_dir / "handler-a_r3.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [{"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}]
        }))
        (findings_dir / "handler-b_r1.json").write_text(json.dumps({
            "file_id": "handler-b", "status": "clean", "findings": []
        }))
        summary = PhaseVEvaluate.collect_findings_summary(str(findings_dir), max_rounds=2)
        assert summary["rounds"][1]["total"] == 2
        assert summary["rounds"][1]["by_category"]["omission"] == 1
        assert summary["rounds"][2]["total"] == 1
        assert summary["rounds"][3]["total"] == 1
        assert summary["final"]["by_category"]["hints_missing"] == 1

    def test_cross_tabulate(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "handlers-test_r3.json").write_text(json.dumps({
            "file_id": "handlers-test", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical", "location": "s1", "description": "X"}]
        }))
        (findings_dir / "libraries-dao_r3.json").write_text(json.dumps({
            "file_id": "libraries-dao", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical", "location": "s1", "description": "Y"}]
        }))
        catalog = {"files": [
            {"id": "handlers-test", "category": "handlers"},
            {"id": "libraries-dao", "category": "libraries"},
        ]}
        cross = PhaseVEvaluate.cross_tabulate(str(findings_dir), catalog, final_round=3)
        assert cross["handlers"]["omission"] == 1
        assert cross["libraries"]["fabrication"] == 1

    def test_file_concentration(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "big-file_r3.json").write_text(json.dumps({
            "file_id": "big-file", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": f"s{i}", "description": f"X{i}"} for i in range(5)]
        }))
        (findings_dir / "small-file_r3.json").write_text(json.dumps({
            "file_id": "small-file", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical", "location": "s1", "description": "X"}]
        }))
        concentration = PhaseVEvaluate.file_concentration(str(findings_dir), final_round=3, top_n=10)
        assert concentration[0]["file_id"] == "big-file"
        assert concentration[0]["count"] == 5
        assert concentration[1]["file_id"] == "small-file"


class TestPhaseVRun:

    def test_run_with_residual_findings(self, tmp_path):
        """残留 findings → evaluate_file → integrate_proposals の連携を検証。"""
        from run import Context
        from phase_v_evaluate import PhaseVEvaluate

        ctx = Context(version='6', repo=str(tmp_path), concurrency=1, max_rounds=2)
        os.makedirs(ctx.cache_dir, exist_ok=True)
        catalog = {
            "generated_at": "2026-01-01T00:00:00Z", "sources": [],
            "files": [{"id": "handler-a", "source_path": "src/handler.rst",
                        "format": "rst", "type": "component", "category": "handlers",
                        "output_path": "component/handlers/handler-a.json"}]
        }
        with open(ctx.classified_list_path, 'w') as f:
            json.dump(catalog, f)

        os.makedirs(f"{ctx.repo}/src", exist_ok=True)
        with open(f"{ctx.repo}/src/handler.rst", 'w') as f:
            f.write("Handler\n=======\n\nContent.\n")

        kdir = f"{ctx.knowledge_cache_dir}/component/handlers"
        os.makedirs(kdir, exist_ok=True)
        with open(f"{kdir}/handler-a.json", 'w') as f:
            json.dump({"id": "handler-a", "sections": {"s1": "content"}}, f)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        with open(f"{ctx.findings_dir}/handler-a_r3.json", 'w') as f:
            json.dump({
                "file_id": "handler-a", "status": "has_issues",
                "findings": [{"category": "omission", "severity": "critical",
                              "location": "s1", "description": "Missing"}]
            }, f)

        prompts_dir = f"{ctx.repo}/tools/knowledge-creator/prompts"
        os.makedirs(prompts_dir, exist_ok=True)
        real_prompts = os.path.join(os.path.dirname(__file__), '../../prompts')
        for fn in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, fn), os.path.join(prompts_dir, fn))

        eval_result = {
            "file_id": "handler-a", "user_impact": "high",
            "needs_improvement": True, "reason": "Critical omission",
            "findings_assessment": [{"category": "omission", "location": "s1",
                                     "impact": "high", "justification": "Missing warning"}]
        }
        integ_result = {
            "proposals": [{"title": "Fix handler warnings", "purpose": "Prevent wrong implementation",
                           "target_files": ["handler-a"], "user_impact": "Critical",
                           "body": "Add missing warnings"}]
        }
        call_count = {"evaluate": 0, "integrate": 0}

        def mock_v(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            schema_str = json.dumps(json_schema) if json_schema else ""
            if "findings_assessment" in schema_str:
                call_count["evaluate"] += 1
                output = eval_result
            else:
                call_count["integrate"] += 1
                output = integ_result
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(output, ensure_ascii=False), stderr=""
            )

        phase_v = PhaseVEvaluate(ctx, run_claude_fn=mock_v)
        result = phase_v.run(final_round=3)

        assert result["fact_data"]["summary"]["final"]["total"] == 1
        assert call_count["evaluate"] == 1
        assert len(result["file_evaluations"]) == 1
        assert result["file_evaluations"][0]["user_impact"] == "high"
        assert call_count["integrate"] == 1
        assert result["proposals"]["proposals"][0]["title"] == "Fix handler warnings"

