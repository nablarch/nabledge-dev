"""Tests for keyword-search benchmark runner."""
import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.benchmark.scripts.run_keyword_search import (
    evaluate_keyword_search,
    run_keyword_search_all,
    run_keyword_search_scenario,
    save_keyword_search_results,
)

SAMPLE_SEARCH_RESULT = [
    {
        "category": "component/libraries",
        "pages": [
            {
                "page_title": "component/libraries/libraries-universal-dao.json",
                "sections": [
                    {
                        "section_id": "component/libraries/libraries-universal-dao.json:s14",
                        "section_title": "排他制御",
                    },
                    {
                        "section_id": "component/libraries/libraries-universal-dao.json:s15",
                        "section_title": "更新",
                    },
                ],
            }
        ],
    }
]

SAMPLE_SCENARIO = {
    "id": "review-01",
    "given": {
        "usecase": "review",
        "category": "db-access",
        "description": "テスト説明",
    },
    "when": {
        "workflow": "keyword-search",
        "input": ["batchUpdate", "UniversalDao"],
    },
    "then": {
        "must": [
            {
                "fact": "batchUpdateでは排他制御処理を行わない",
                "section": "component/libraries/libraries-universal-dao.json:s14",
            },
        ],
        "acceptable": [
            {"section": "component/libraries/libraries-universal-dao.json:s15"},
        ],
    },
}


class TestEvaluateKeywordSearch:
    def _returned(self, *section_ids):
        return set(section_ids)

    def test_must_section_found(self):
        returned = self._returned("component/libraries/libraries-universal-dao.json:s14")
        result = evaluate_keyword_search(SAMPLE_SCENARIO, returned)
        assert result["must"][0]["found"] is True

    def test_must_section_missing(self):
        returned = self._returned()
        result = evaluate_keyword_search(SAMPLE_SCENARIO, returned)
        assert result["must"][0]["found"] is False

    def test_acceptable_section_found(self):
        returned = self._returned(
            "component/libraries/libraries-universal-dao.json:s14",
            "component/libraries/libraries-universal-dao.json:s15",
        )
        result = evaluate_keyword_search(SAMPLE_SCENARIO, returned)
        assert result["acceptable"][0]["found"] is True

    def test_acceptable_section_missing(self):
        returned = self._returned("component/libraries/libraries-universal-dao.json:s14")
        result = evaluate_keyword_search(SAMPLE_SCENARIO, returned)
        assert result["acceptable"][0]["found"] is False

    def test_recall_all_found(self):
        returned = self._returned("component/libraries/libraries-universal-dao.json:s14")
        result = evaluate_keyword_search(SAMPLE_SCENARIO, returned)
        assert result["scores"]["recall"] == 1.0

    def test_recall_none_found(self):
        result = evaluate_keyword_search(SAMPLE_SCENARIO, set())
        assert result["scores"]["recall"] == 0.0

    def test_recall_partial(self):
        scenario = {
            **SAMPLE_SCENARIO,
            "then": {
                "must": [
                    {"fact": "事実1", "section": "file.json:s1"},
                    {"fact": "事実2", "section": "file.json:s2"},
                ],
                "acceptable": [],
            },
        }
        returned = {"file.json:s1"}
        result = evaluate_keyword_search(scenario, returned)
        assert result["scores"]["recall"] == 0.5

    def test_recall_no_must_sections(self):
        scenario = {**SAMPLE_SCENARIO, "then": {"must": [], "acceptable": []}}
        result = evaluate_keyword_search(scenario, set())
        assert result["scores"]["recall"] == 1.0

    def test_includes_scenario_id(self):
        result = evaluate_keyword_search(SAMPLE_SCENARIO, set())
        assert result["scenario_id"] == "review-01"


class TestRunKeywordSearchScenario:
    def _make_mock_proc(self, search_result=None, returncode=0):
        out = json.dumps(search_result or SAMPLE_SEARCH_RESULT, ensure_ascii=False)
        return type("P", (), {
            "returncode": returncode,
            "stdout": out if returncode == 0 else "",
            "stderr": "" if returncode == 0 else "Error occurred",
        })()

    def test_returns_scenario_id(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()):
            result = run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        assert result["scenario_id"] == "review-01"

    def test_returns_search_results(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()):
            result = run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        assert result["search"] == SAMPLE_SEARCH_RESULT

    def test_returns_evaluation(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()):
            result = run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        assert "evaluation" in result
        assert "must" in result["evaluation"]
        assert "scores" in result["evaluation"]

    def test_returns_metrics(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()):
            result = run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        assert "duration_ms" in result["metrics"]

    def test_calls_keyword_search_sh_with_keywords(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
            run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        cmd = mock_run.call_args[0][0]
        assert "bash" in cmd
        assert "scripts/keyword-search.sh" in cmd
        assert "batchUpdate" in cmd
        assert "UniversalDao" in cmd

    def test_uses_skill_dir_as_cwd(self):
        with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
            run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")
        call_kwargs = mock_run.call_args[1]
        assert str(call_kwargs.get("cwd", "")) == "/tmp/skill"

    def test_raises_on_nonzero_returncode(self):
        with patch("subprocess.run", return_value=self._make_mock_proc(returncode=1)):
            with pytest.raises(RuntimeError, match="keyword-search.sh"):
                run_keyword_search_scenario(SAMPLE_SCENARIO, "/tmp/skill")

    def test_string_input_also_works(self):
        scenario = {
            **SAMPLE_SCENARIO,
            "when": {**SAMPLE_SCENARIO["when"], "input": "UniversalDao"},
        }
        with patch("subprocess.run", return_value=self._make_mock_proc()) as mock_run:
            run_keyword_search_scenario(scenario, "/tmp/skill")
        cmd = mock_run.call_args[0][0]
        assert "UniversalDao" in cmd


class TestSaveKeywordSearchResults:
    def _make_data(self, **overrides):
        base = {
            "scenario_id": "review-01",
            "search": SAMPLE_SEARCH_RESULT,
            "evaluation": {
                "scenario_id": "review-01",
                "must": [{"section": "file.json:s1", "found": True}],
                "acceptable": [],
                "scores": {"recall": 1.0},
            },
            "metrics": {"duration_ms": 5},
        }
        base.update(overrides)
        return base

    def test_saves_search_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_keyword_search_results(tmpdir, "review-01", self._make_data())
            saved = json.loads((Path(tmpdir) / "review-01" / "search.json").read_text())
            assert saved == SAMPLE_SEARCH_RESULT

    def test_saves_evaluation_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_keyword_search_results(tmpdir, "review-01", self._make_data())
            saved = json.loads((Path(tmpdir) / "review-01" / "evaluation.json").read_text())
            assert saved["scores"]["recall"] == 1.0

    def test_saves_metrics_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_keyword_search_results(tmpdir, "review-01", self._make_data())
            saved = json.loads((Path(tmpdir) / "review-01" / "metrics.json").read_text())
            assert "duration_ms" in saved

    def test_creates_scenario_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            save_keyword_search_results(tmpdir, "review-01", self._make_data())
            assert (Path(tmpdir) / "review-01").is_dir()


class TestRunKeywordSearchAll:
    def _make_mock_proc(self):
        return type("P", (), {
            "returncode": 0,
            "stdout": json.dumps(SAMPLE_SEARCH_RESULT, ensure_ascii=False),
            "stderr": "",
        })()

    def _setup_skill_dir(self, base_dir):
        skill_dir = Path(base_dir) / "skill"
        skill_dir.mkdir()
        return skill_dir

    def _setup_scenarios(self, base_dir, scenarios=None):
        if scenarios is None:
            scenarios = [SAMPLE_SCENARIO]
        path = Path(base_dir) / "scenarios.json"
        path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")
        return path

    def _run_all(self, tmpdir, scenarios=None, scenario_ids=None):
        skill_dir = self._setup_skill_dir(tmpdir)
        scenarios_path = self._setup_scenarios(tmpdir, scenarios)
        output_dir = Path(tmpdir) / "results"
        with patch("subprocess.run", return_value=self._make_mock_proc()):
            summary = run_keyword_search_all(
                str(scenarios_path),
                str(skill_dir),
                output_dir=str(output_dir),
                scenario_ids=scenario_ids,
            )
        return summary, output_dir

    def test_runs_all_scenarios(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary, _ = self._run_all(tmpdir)
            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "review-01"

    def test_filters_by_scenario_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            scenario2 = {**SAMPLE_SCENARIO, "id": "review-02"}
            summary, _ = self._run_all(tmpdir, [SAMPLE_SCENARIO, scenario2], scenario_ids=["review-01"])
            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "review-01"

    def test_saves_summary_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            assert (output_dir / "summary.json").exists()
            summary = json.loads((output_dir / "summary.json").read_text())
            assert summary["total_scenarios"] == 1

    def test_summary_includes_skill_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary = json.loads((output_dir / "summary.json").read_text())
            assert "skill_dir" in summary

    def test_summary_includes_executed_at(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            summary = json.loads((output_dir / "summary.json").read_text())
            assert "executed_at" in summary

    def test_saves_search_json_per_scenario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            assert (output_dir / "review-01" / "search.json").exists()

    def test_saves_evaluation_json_per_scenario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _, output_dir = self._run_all(tmpdir)
            assert (output_dir / "review-01" / "evaluation.json").exists()

    def test_continues_after_error(self):
        scenario1 = {**SAMPLE_SCENARIO, "id": "s1"}
        scenario2 = {**SAMPLE_SCENARIO, "id": "s2"}
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise subprocess.TimeoutExpired(cmd="bash", timeout=30)
            return self._make_mock_proc()

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [scenario1, scenario2])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                summary = run_keyword_search_all(
                    str(scenarios_path), str(skill_dir), output_dir=str(output_dir)
                )

        assert summary["total_scenarios"] == 2
        assert summary["scenarios"][0]["status"] == "error"
        assert summary["scenarios"][1].get("status") != "error"

    def test_error_json_saved_for_failed_scenario(self):
        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="bash", timeout=30)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir, [SAMPLE_SCENARIO])
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_keyword_search_all(
                    str(scenarios_path), str(skill_dir), output_dir=str(output_dir)
                )

            error_path = output_dir / "review-01" / "error.json"
            assert error_path.exists()
            error_data = json.loads(error_path.read_text())
            assert "error" in error_data
            assert "exception_type" in error_data

    def test_summary_written_even_when_all_fail(self):
        def side_effect(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="bash", timeout=30)

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = self._setup_skill_dir(tmpdir)
            scenarios_path = self._setup_scenarios(tmpdir)
            output_dir = Path(tmpdir) / "results"
            with patch("subprocess.run", side_effect=side_effect):
                run_keyword_search_all(
                    str(scenarios_path), str(skill_dir), output_dir=str(output_dir)
                )
            assert (output_dir / "summary.json").exists()


class TestDefaultOutputDir:
    def test_default_output_dir_uses_timestamp(self):
        import re
        from tools.benchmark.scripts.run_keyword_search import default_output_dir
        result = default_output_dir()
        assert re.match(r".*/tools/benchmark/results/\d{8}-\d{6}$", str(result))
