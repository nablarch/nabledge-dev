"""Tests for verify-only simulation (verification quality evaluation)."""
import json
from pathlib import Path

import pytest

from tools.benchmark.scripts.simulate_verify import (
    aggregate_metrics,
    simulate_all,
    simulate_scenario,
)

DUMMY_METRICS = {
    "duration_ms": 100,
    "duration_api_ms": 90,
    "total_cost_usd": 0.001,
    "usage": {"input_tokens": 500, "output_tokens": 50},
}


def _wrap_llm_response(result, metrics=None):
    return {"result": result, "metrics": metrics or DUMMY_METRICS}


def _make_knowledge_file(title, sections):
    return {
        "title": title,
        "sections": [
            {"id": s["id"], "title": s["title"], "content": s["content"]}
            for s in sections
        ],
    }


def _write_knowledge_file(tmp_path, rel_path, data):
    full_path = tmp_path / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _verify_pass():
    return _wrap_llm_response({
        "result": "PASS",
        "claims": [
            {"claim": "SQLファイルで検索する", "supported": True, "evidence": "libs/dao.json:s3"},
        ],
        "issues": [],
    })


def _verify_fail():
    return _wrap_llm_response({
        "result": "FAIL",
        "claims": [
            {"claim": "SQLファイルで検索する", "supported": True, "evidence": "libs/dao.json:s3"},
            {"claim": "スレッドセーフ", "supported": False, "evidence": ""},
        ],
        "issues": [
            {"claim": "スレッドセーフ", "quote": "スレッドセーフに動作します"},
        ],
    })


class TestAggregateMetrics:
    def test_single_call(self):
        result = aggregate_metrics([DUMMY_METRICS])
        assert result["duration_ms"] == 100
        assert result["total_cost_usd"] == 0.001
        assert result["total_tokens"] == 550
        assert result["call_count"] == 1

    def test_empty_list(self):
        result = aggregate_metrics([])
        assert result["duration_ms"] == 0
        assert result["call_count"] == 0


class TestSimulateScenario:
    @pytest.fixture
    def knowledge_dir(self, tmp_path):
        data = _make_knowledge_file("ユニバーサルDAO", [
            {"id": "s3", "title": "検索", "content": "SQLファイルで検索する"},
        ])
        _write_knowledge_file(tmp_path, "libs/dao.json", data)
        return tmp_path

    @pytest.fixture
    def scenario(self):
        return {
            "id": "test-01",
            "given": {"description": "test"},
            "when": {
                "input": "検索方法は？",
                "hearing_answer": {"processing_type": "Web", "goal": "検索する"},
            },
            "then": {
                "must": [{"fact": "SQLファイルで検索", "section": "libs/dao.json:s3"}],
                "acceptable": [],
            },
        }

    def test_verify_pass(self, scenario, knowledge_dir):
        def mock_llm(prompt, schema):
            return _verify_pass()

        result = simulate_scenario(
            scenario, knowledge_dir, "SQLファイルで検索します", llm_fn=mock_llm,
        )
        assert result["scenario_id"] == "test-01"
        assert result["verify"]["result"] == "PASS"
        assert len(result["verify"]["claims"]) == 1
        assert result["verify"]["issues"] == []

    def test_verify_fail(self, scenario, knowledge_dir):
        def mock_llm(prompt, schema):
            return _verify_fail()

        result = simulate_scenario(
            scenario, knowledge_dir, "スレッドセーフに動作します", llm_fn=mock_llm,
        )
        assert result["verify"]["result"] == "FAIL"
        assert len(result["verify"]["issues"]) == 1

    def test_output_structure(self, scenario, knowledge_dir):
        def mock_llm(prompt, schema):
            return _verify_pass()

        result = simulate_scenario(
            scenario, knowledge_dir, "回答", llm_fn=mock_llm,
        )
        assert "scenario_id" in result
        assert "sections_input" in result
        assert "verify" in result
        assert "metrics" in result
        assert result["metrics"]["call_count"] == 1

    def test_llm_called_once(self, scenario, knowledge_dir):
        call_count = [0]

        def mock_llm(prompt, schema):
            call_count[0] += 1
            return _verify_pass()

        simulate_scenario(scenario, knowledge_dir, "回答", llm_fn=mock_llm)
        assert call_count[0] == 1


class TestSimulateAll:
    @pytest.fixture
    def setup(self, tmp_path):
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        data = _make_knowledge_file("T", [
            {"id": "s1", "title": "S", "content": "C"},
        ])
        _write_knowledge_file(knowledge_dir, "f.json", data)

        scenarios = {
            "scenarios": [
                {
                    "id": "sc-01",
                    "given": {"description": "d"},
                    "when": {"input": "q1"},
                    "then": {
                        "must": [{"fact": "f", "section": "f.json:s1"}],
                        "acceptable": [],
                    },
                },
                {
                    "id": "sc-02",
                    "given": {"description": "d"},
                    "when": {"input": "q2"},
                    "then": {
                        "must": [{"fact": "f", "section": "f.json:s1"}],
                        "acceptable": [],
                    },
                },
            ],
        }
        scenarios_path = tmp_path / "scenarios.json"
        scenarios_path.write_text(json.dumps(scenarios, ensure_ascii=False), encoding="utf-8")

        answers_dir = tmp_path / "answers"
        (answers_dir / "sc-01").mkdir(parents=True)
        (answers_dir / "sc-02").mkdir(parents=True)
        (answers_dir / "sc-01" / "answer.md").write_text("回答1", encoding="utf-8")
        (answers_dir / "sc-02" / "answer.md").write_text("回答2", encoding="utf-8")

        output_dir = tmp_path / "output"

        return {
            "knowledge_dir": str(knowledge_dir),
            "scenarios_path": str(scenarios_path),
            "answers_dir": str(answers_dir),
            "output_dir": str(output_dir),
        }

    def test_runs_all_scenarios(self, setup):
        call_count = [0]

        def mock_llm(prompt, schema):
            call_count[0] += 1
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["total_scenarios"] == 2
        assert call_count[0] == 2

    def test_scenario_filter(self, setup):
        call_count = [0]

        def mock_llm(prompt, schema):
            call_count[0] += 1
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
            scenario_ids=["sc-01"],
        )
        assert summary["total_scenarios"] == 1
        assert call_count[0] == 1

    def test_writes_output_files(self, setup):
        def mock_llm(prompt, schema):
            return _verify_pass()

        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        assert (out / "sc-01" / "verify.json").exists()
        assert (out / "sc-01" / "metrics.json").exists()
        assert (out / "summary.json").exists()

    def test_summary_structure(self, setup):
        def mock_llm(prompt, schema):
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert "total_scenarios" in summary
        assert "verify_pass" in summary
        assert "verify_fail" in summary
        assert "per_scenario" in summary
        assert "metrics" in summary

    def test_summary_all_pass(self, setup):
        def mock_llm(prompt, schema):
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["verify_pass"] == 2
        assert summary["verify_fail"] == 0

    def test_summary_with_failures(self, setup):
        responses = [_verify_fail(), _verify_pass()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["verify_pass"] == 1
        assert summary["verify_fail"] == 1

    def test_per_scenario_structure(self, setup):
        def mock_llm(prompt, schema):
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        ps = summary["per_scenario"][0]
        assert "id" in ps
        assert "verify_result" in ps
        assert "claims_count" in ps
        assert "issues_count" in ps
        assert "metrics" in ps

    def test_missing_answer_skips_scenario(self, setup):
        Path(setup["answers_dir"], "sc-02", "answer.md").unlink()

        def mock_llm(prompt, schema):
            return _verify_pass()

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["total_scenarios"] == 1
        assert summary["per_scenario"][0]["id"] == "sc-01"

    def test_verify_json_content(self, setup):
        def mock_llm(prompt, schema):
            return _verify_fail()

        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["answers_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        verify_data = json.loads((out / "sc-01" / "verify.json").read_text(encoding="utf-8"))
        assert verify_data["result"] == "FAIL"
        assert len(verify_data["claims"]) == 2
        assert len(verify_data["issues"]) == 1
