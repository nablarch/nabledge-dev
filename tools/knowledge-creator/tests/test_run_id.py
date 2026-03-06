"""Tests for run_id, latest symlink, and report.json generation."""
import json
import os
import subprocess
import sys
import pytest
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOL_DIR)

from run import Context, _aggregate_findings, _compute_totals, _write_report


class TestContext:
    def test_run_id_auto_generated(self, tmp_path):
        """run_id が未指定のとき自動生成される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        assert ctx.run_id is not None
        # フォーマット: YYYYMMDDTHHmmSS
        datetime.strptime(ctx.run_id, "%Y%m%dT%H%M%S")

    def test_run_id_explicit(self, tmp_path):
        """run_id を明示指定すると保持される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.run_id == "20250304T120000"

    def test_log_dir_contains_run_id(self, tmp_path):
        """log_dir に run_id が含まれる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert "20250304T120000" in ctx.log_dir

    def test_version_log_dir_is_parent_of_log_dir(self, tmp_path):
        """version_log_dir は log_dir の親ディレクトリ。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.log_dir.startswith(ctx.version_log_dir)
        assert ctx.log_dir != ctx.version_log_dir

    def test_report_path_inside_log_dir(self, tmp_path):
        """report_path は log_dir 内にある。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.report_path.startswith(ctx.log_dir)
        assert ctx.report_path.endswith("report.json")

    def test_sub_paths_use_run_id(self, tmp_path):
        """classified_list_path 等のサブパスも run_id を含む。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert "20250304T120000" in ctx.classified_list_path
        assert "20250304T120000" in ctx.findings_dir
        assert "20250304T120000" in ctx.phase_b_executions_dir


class TestLatestSymlink:
    def test_latest_created_on_new_run(self, tmp_path):
        """新規実行時に latest シンボリックリンクが作成される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.log_dir, exist_ok=True)

        latest_link = os.path.join(ctx.version_log_dir, "latest")
        if os.path.lexists(latest_link):
            os.remove(latest_link)
        os.symlink(ctx.run_id, latest_link)

        assert os.path.islink(latest_link)
        assert os.readlink(latest_link) == ctx.run_id

    def test_latest_updated_on_second_run(self, tmp_path):
        """2回目の実行で latest が新しい run_id に更新される。"""
        ctx1 = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T100000")
        os.makedirs(ctx1.log_dir, exist_ok=True)
        latest_link = os.path.join(ctx1.version_log_dir, "latest")
        os.symlink(ctx1.run_id, latest_link)

        ctx2 = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T110000")
        os.makedirs(ctx2.log_dir, exist_ok=True)
        if os.path.lexists(latest_link):
            os.remove(latest_link)
        os.symlink(ctx2.run_id, latest_link)

        assert os.readlink(latest_link) == "20250304T110000"

    def test_resume_reuses_run_id_from_latest(self, tmp_path):
        """--resume 時は latest リンクが指す run_id を再利用できる。"""
        original_run_id = "20250304T100000"
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id=original_run_id)
        os.makedirs(ctx.log_dir, exist_ok=True)
        latest_link = os.path.join(ctx.version_log_dir, "latest")
        os.symlink(original_run_id, latest_link)

        resumed_run_id = os.readlink(latest_link)
        ctx_resumed = Context(version="6", repo=str(tmp_path), concurrency=4, run_id=resumed_run_id)

        assert ctx_resumed.run_id == original_run_id
        assert ctx_resumed.log_dir == ctx.log_dir


class TestAggregateFindings:
    def test_empty_dir_returns_zero(self, tmp_path):
        """findings ディレクトリが空でもエラーにならず 0 を返す。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.findings_dir, exist_ok=True)
        result = _aggregate_findings(ctx)
        assert result == {"total": 0, "critical": 0, "minor": 0, "by_category": {}}

    def test_nonexistent_dir_returns_zero(self, tmp_path):
        """findings ディレクトリが存在しなくてもエラーにならない。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        result = _aggregate_findings(ctx)
        assert result["total"] == 0

    def test_aggregate_multiple_findings(self, tmp_path):
        """複数の findings ファイルを正しく集計できる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.findings_dir, exist_ok=True)

        findings1 = {
            "file_id": "file-a", "status": "has_issues",
            "findings": [
                {"category": "omission",    "severity": "critical", "location": "x", "description": "y"},
                {"category": "omission",    "severity": "minor",    "location": "x", "description": "y"},
            ]
        }
        findings2 = {
            "file_id": "file-b", "status": "has_issues",
            "findings": [
                {"category": "fabrication", "severity": "critical", "location": "x", "description": "y"},
            ]
        }
        with open(os.path.join(ctx.findings_dir, "file-a.json"), 'w') as f:
            json.dump(findings1, f)
        with open(os.path.join(ctx.findings_dir, "file-b.json"), 'w') as f:
            json.dump(findings2, f)

        result = _aggregate_findings(ctx)
        assert result["total"] == 3
        assert result["critical"] == 2
        assert result["minor"] == 1
        assert result["by_category"]["omission"] == 2
        assert result["by_category"]["fabrication"] == 1


class TestComputeTotals:
    def test_all_none_returns_zero(self):
        """全フェーズが None でも合計 0 を返す。"""
        report = {"phase_b": None, "phase_d_rounds": [], "phase_e_rounds": []}
        totals = _compute_totals(report)
        assert totals["cost_usd"] == 0.0
        assert totals["tokens"]["input"] == 0

    def test_sums_all_phases(self):
        """Phase B + D + E のコスト・トークンを正しく合計する。"""
        report = {
            "phase_b": {
                "metrics": {
                    "cost_usd": 4.21,
                    "tokens": {"input": 100, "cache_creation": 10, "cache_read": 5, "output": 20}
                }
            },
            "phase_d_rounds": [{
                "metrics": {
                    "cost_usd": 1.87,
                    "tokens": {"input": 50, "cache_creation": 5, "cache_read": 3, "output": 10}
                }
            }],
            "phase_e_rounds": [{
                "metrics": {
                    "cost_usd": 0.98,
                    "tokens": {"input": 30, "cache_creation": 0, "cache_read": 2, "output": 8}
                }
            }],
        }
        totals = _compute_totals(report)
        assert totals["cost_usd"] == round(4.21 + 1.87 + 0.98, 4)
        assert totals["tokens"]["input"] == 180
        assert totals["tokens"]["cache_creation"] == 15


class TestWriteReport:
    def test_report_json_written(self, tmp_path):
        """report.json が log_dir に書き出される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        os.makedirs(ctx.log_dir, exist_ok=True)

        report = {"meta": {"run_id": ctx.run_id}, "totals": {"cost_usd": 1.23}}
        _write_report(ctx, report)

        assert os.path.exists(ctx.report_path)
        with open(ctx.report_path) as f:
            loaded = json.load(f)
        assert loaded["meta"]["run_id"] == ctx.run_id
        assert loaded["totals"]["cost_usd"] == 1.23

    def test_report_overwrites_existing(self, tmp_path):
        """既存の report.json を上書きできる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        os.makedirs(ctx.log_dir, exist_ok=True)

        _write_report(ctx, {"version": 1})
        _write_report(ctx, {"version": 2})

        with open(ctx.report_path) as f:
            loaded = json.load(f)
        assert loaded["version"] == 2


RUN_PY = os.path.join(TOOL_DIR, "run.py")


class TestPathResolution:
    """run.py はどのディレクトリから実行しても正しいパスに解決される。"""

    def _run_help(self, cwd):
        """指定ディレクトリから run.py --help を実行して成功することを確認する。"""
        result = subprocess.run(
            [sys.executable, RUN_PY, "--help"],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return result

    def test_run_from_tool_dir(self, tmp_path):
        """tools/knowledge-creator ディレクトリから実行できる。"""
        result = self._run_help(TOOL_DIR)
        assert result.returncode == 0, f"--help failed from tool dir: {result.stderr}"

    def test_run_from_repo_root(self, tmp_path):
        """リポジトリルートから実行できる。"""
        repo_root = os.path.dirname(os.path.dirname(TOOL_DIR))
        result = self._run_help(repo_root)
        assert result.returncode == 0, f"--help failed from repo root: {result.stderr}"

    def test_run_from_tmp_dir(self, tmp_path):
        """任意のディレクトリから実行できる。"""
        result = self._run_help(str(tmp_path))
        assert result.returncode == 0, f"--help failed from tmp dir: {result.stderr}"
