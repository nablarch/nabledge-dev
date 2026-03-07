"""Tests for steps/cleaner.py"""
import os
import pytest
from common import write_json, load_json
from cleaner import clean_phase_artifacts, _list_phase_b_artifacts, _list_phase_d_artifacts


class TestListPhaseDAllFiles:
    """_list_phase_d_artifacts: target_ids=None のケース"""

    def test_returns_findings_dir_when_exists(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a.json", {})
        result = _list_phase_d_artifacts(ctx, target_ids=None)
        assert ctx.findings_dir in result

    def test_returns_empty_when_no_findings_dir(self, ctx):
        result = _list_phase_d_artifacts(ctx, target_ids=None)
        assert result == []


class TestListPhaseDWithTarget:
    """_list_phase_d_artifacts: target_ids 指定"""

    def test_returns_target_file_only(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target.json", {})
        write_json(f"{ctx.findings_dir}/other.json", {})
        result = _list_phase_d_artifacts(ctx, target_ids=["target"])
        assert len(result) == 1
        assert result[0].endswith("target.json")

    def test_returns_empty_for_nonexistent_target(self, ctx):
        result = _list_phase_d_artifacts(ctx, target_ids=["nonexistent"])
        assert result == []


class TestListPhaseBWithTarget:
    """_list_phase_b_artifacts: target_ids 指定"""

    def test_returns_knowledge_json_and_trace(self, ctx):
        # knowledge JSON
        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})
        # trace
        os.makedirs(ctx.trace_dir, exist_ok=True)
        write_json(f"{ctx.trace_dir}/handlers-sample-handler.json", {})

        result = _list_phase_b_artifacts(ctx, target_ids=["handlers-sample-handler"])
        assert len(result) == 2
        assert any("handlers-sample-handler.json" in p for p in result)


class TestListPhaseBAllFiles:
    """_list_phase_b_artifacts: target_ids=None のケース"""

    def test_returns_all_knowledge_from_classified(self, ctx):
        """classified.json の output_path を元に全件列挙する。"""
        classified = {
            "version": "6", "generated_at": "2026-01-01T00:00:00Z",
            "files": [{
                "id": "handlers-sample-handler",
                "output_path": "component/handlers/handlers-sample-handler.json",
                "source_path": "tests/fixtures/sample_source.rst",
                "format": "rst", "filename": "sample.rst",
                "type": "component", "category": "handlers",
                "assets_dir": "component/handlers/assets/handlers-sample-handler/"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})

        result = _list_phase_b_artifacts(ctx, target_ids=None)
        assert any("handlers-sample-handler.json" in p for p in result)


class TestCleanPhaseArtifacts:
    """clean_phase_artifacts の統合テスト"""

    def test_clean_d_all_removes_findings_dir(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a.json", {})
        write_json(f"{ctx.findings_dir}/b.json", {})

        clean_phase_artifacts(ctx, "D", target_ids=None, yes=True)
        assert not os.path.isdir(ctx.findings_dir)

    def test_clean_d_target_preserves_others(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target.json", {})
        write_json(f"{ctx.findings_dir}/keep.json", {})

        clean_phase_artifacts(ctx, "D", target_ids=["target"], yes=True)
        assert not os.path.exists(f"{ctx.findings_dir}/target.json")
        assert os.path.exists(f"{ctx.findings_dir}/keep.json")

    def test_clean_bd_removes_both_phases(self, ctx):
        """BD 指定で Phase B と D 両方の成果物を削除。"""
        # classified.json（Phase B 全件クリアに必要）
        classified = {
            "version": "6", "generated_at": "2026-01-01T00:00:00Z",
            "files": [{
                "id": "handlers-sample-handler",
                "output_path": "component/handlers/handlers-sample-handler.json",
                "source_path": "tests/fixtures/sample_source.rst",
                "format": "rst", "filename": "sample.rst",
                "type": "component", "category": "handlers",
                "assets_dir": "component/handlers/assets/handlers-sample-handler/"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        # Phase B artifact
        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})

        # Phase D artifact
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/handlers-sample-handler.json", {})

        clean_phase_artifacts(ctx, "BD", target_ids=None, yes=True)
        assert not os.path.exists(json_path)
        assert not os.path.isdir(ctx.findings_dir)

    def test_no_targets_prints_message(self, ctx, capsys):
        clean_phase_artifacts(ctx, "D", target_ids=None, yes=True)
        captured = capsys.readouterr()
        assert "削除対象なし" in captured.out
