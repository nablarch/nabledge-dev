"""Test final verification after CDE loop."""
import json
import os
import subprocess
import shutil
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


def _setup_ctx_with_knowledge(tmp_path):
    """テスト用の Context + catalog + source + knowledge を準備する。"""
    from run import Context
    ctx = Context(version='6', repo=str(tmp_path), concurrency=1, max_rounds=2)
    os.makedirs(ctx.cache_dir, exist_ok=True)
    catalog = {
        "generated_at": "2026-01-01T00:00:00Z", "sources": [],
        "files": [{
            "id": "test-handler", "source_path": "src/test.rst",
            "format": "rst", "type": "component", "category": "handlers",
            "output_path": "component/handlers/test-handler.json",
        }]
    }
    with open(ctx.classified_list_path, 'w') as f:
        json.dump(catalog, f)
    os.makedirs(os.path.dirname(f"{ctx.repo}/src/test.rst"), exist_ok=True)
    with open(f"{ctx.repo}/src/test.rst", 'w') as f:
        f.write("Title\n=====\n\nContent here.\n")
    kdir = f"{ctx.knowledge_cache_dir}/component/handlers"
    os.makedirs(kdir, exist_ok=True)
    knowledge = {
        "id": "test-handler", "title": "Test Handler", "no_knowledge_content": False,
        "official_doc_urls": ["https://example.com"],
        "index": [{"id": "s1", "title": "Content", "hints": ["TestHandler", "テスト", "設定"]}],
        "sections": {"s1": "Content here with enough characters to pass minimum length check."}
    }
    with open(f"{kdir}/test-handler.json", 'w') as f:
        json.dump(knowledge, f)
    prompts_dir = os.path.join(ctx.repo, "tools/knowledge-creator/prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    real_prompts = os.path.join(os.path.dirname(__file__), '../../prompts')
    if os.path.exists(real_prompts):
        for fn in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, fn), os.path.join(prompts_dir, fn))
    return ctx


class TestFinalVerification:

    def test_phase_c_only(self, tmp_path):
        """Phase C のみ指定 → phase_c 結果が返り、round = max_rounds + 1。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)
        result = _run_final_verification(ctx, max_rounds=2, phases="C")
        assert result["round"] == 3
        assert result["phase_c"]["total"] == 1
        assert result["phase_c"]["pass"] == 1

    def test_phase_cd_clean(self, tmp_path):
        """C→D 実行。Phase D が clean を返す場合、has_issues == 0。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)

        mock_findings = {"file_id": "test-handler", "status": "clean", "findings": []}

        def mock_cc(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(mock_findings, ensure_ascii=False), stderr=""
            )

        with patch("phase_d_content_check._default_run_claude", mock_cc):
            result = _run_final_verification(ctx, max_rounds=2, phases="CD")

        assert result["round"] == 3
        assert "phase_c" in result
        assert "phase_d" in result
        assert result["phase_d"]["has_issues"] == 0

    def test_phase_cd_with_findings(self, tmp_path):
        """C→D 実行。Phase D が findings を返す場合、findings が集計される。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)

        mock_findings = {
            "file_id": "test-handler", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "Missing warning"}
            ]
        }

        def mock_cc(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(mock_findings, ensure_ascii=False), stderr=""
            )

        with patch("phase_d_content_check._default_run_claude", mock_cc):
            result = _run_final_verification(ctx, max_rounds=2, phases="CD")

        assert result["phase_d"]["has_issues"] == 1
        assert result["phase_d"]["findings"]["total"] >= 1
