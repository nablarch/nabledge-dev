"""Tests for answer-only simulation (answer generation + evaluation)."""
import json
from pathlib import Path

import pytest

from tools.benchmark.scripts.simulate_answer import (
    aggregate_metrics,
    evaluate_answer,
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


def _claim_present(fact="f"):
    return _wrap_llm_response({"verdict": "PRESENT", "reason": "found"})


def _claim_absent(fact="f"):
    return _wrap_llm_response({"verdict": "ABSENT", "reason": "not found"})


def _hallucination_pass():
    return _wrap_llm_response({
        "verdict": "PASS",
        "claims": [{"claim": "c", "supported": True}],
        "reason": "all supported",
    })


def _hallucination_fail():
    return _wrap_llm_response({
        "verdict": "FAIL",
        "claims": [{"claim": "c", "supported": False}],
        "reason": "unsupported claim",
    })


class TestAggregateMetrics:
    def test_single_call(self):
        result = aggregate_metrics([DUMMY_METRICS])
        assert result["duration_ms"] == 100
        assert result["total_cost_usd"] == 0.001
        assert result["total_tokens"] == 550
        assert result["call_count"] == 1

    def test_multiple_calls(self):
        m1 = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        m2 = {"duration_ms": 80, "total_cost_usd": 0.005, "usage": {"input_tokens": 400, "output_tokens": 30}}
        m3 = {"duration_ms": 90, "total_cost_usd": 0.008, "usage": {"input_tokens": 600, "output_tokens": 60}}
        result = aggregate_metrics([m1, m2, m3])
        assert result["duration_ms"] == 270
        assert result["total_cost_usd"] == 0.023
        assert result["total_tokens"] == 1640
        assert result["call_count"] == 3

    def test_empty_metrics(self):
        result = aggregate_metrics([{}, {}])
        assert result["duration_ms"] == 0
        assert result["total_cost_usd"] == 0.0
        assert result["total_tokens"] == 0
        assert result["call_count"] == 2

    def test_empty_list(self):
        result = aggregate_metrics([])
        assert result["duration_ms"] == 0
        assert result["total_cost_usd"] == 0.0
        assert result["total_tokens"] == 0
        assert result["call_count"] == 0


class TestEvaluateAnswer:
    @pytest.fixture
    def knowledge_dir(self, tmp_path):
        data = _make_knowledge_file("DAO", [
            {"id": "s1", "title": "概要", "content": "DAOの概要説明"},
            {"id": "s3", "title": "検索", "content": "SQLファイルで検索する"},
        ])
        _write_knowledge_file(tmp_path, "libs/dao.json", data)
        return tmp_path

    def test_all_present_no_hallucination(self, knowledge_dir):
        must = [{"fact": "SQLファイルで検索", "section": "libs/dao.json:s3"}]
        acceptable = [{"section": "libs/dao.json:s1"}]
        responses = [_claim_present(), _hallucination_pass()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = evaluate_answer("回答テキスト", must, acceptable, knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["accuracy"] == 1.0
        assert result["scores"]["hallucination"] == 1
        assert len(result["claim_verdicts"]) == 1
        assert result["claim_verdicts"][0]["verdict"] == "PRESENT"
        assert result["hallucination"]["verdict"] == "PASS"
        assert call_idx[0] == 2

    def test_some_absent(self, knowledge_dir):
        data2 = _make_knowledge_file("T", [
            {"id": "s1", "title": "T", "content": "content2"},
        ])
        _write_knowledge_file(knowledge_dir, "other.json", data2)

        must = [
            {"fact": "SQLファイルで検索", "section": "libs/dao.json:s3"},
            {"fact": "別の事実", "section": "other.json:s1"},
        ]
        responses = [_claim_present(), _claim_absent(), _hallucination_pass()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = evaluate_answer("回答テキスト", must, [], knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["accuracy"] == 0.5
        assert len(result["claim_verdicts"]) == 2
        assert call_idx[0] == 3

    def test_hallucination_detected(self, knowledge_dir):
        must = [{"fact": "f", "section": "libs/dao.json:s3"}]
        responses = [_claim_present(), _hallucination_fail()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = evaluate_answer("回答テキスト", must, [], knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["hallucination"] == 0
        assert result["hallucination"]["verdict"] == "FAIL"

    def test_no_must_facts(self, knowledge_dir):
        responses = [_hallucination_pass()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = evaluate_answer("回答テキスト", [], [], knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["accuracy"] is None
        assert len(result["claim_verdicts"]) == 0
        assert call_idx[0] == 1

    def test_eval_metrics_collected(self, knowledge_dir):
        must = [{"fact": "f", "section": "libs/dao.json:s3"}]
        m1 = {"duration_ms": 50, "total_cost_usd": 0.002, "usage": {"input_tokens": 300, "output_tokens": 20}}
        m2 = {"duration_ms": 60, "total_cost_usd": 0.003, "usage": {"input_tokens": 400, "output_tokens": 25}}
        responses = [
            _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"}, m1),
            _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"}, m2),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = evaluate_answer("回答テキスト", must, [], knowledge_dir, llm_fn=mock_llm)
        assert len(result["eval_metrics"]) == 2
        assert result["eval_metrics"][0]["duration_ms"] == 50
        assert result["eval_metrics"][1]["duration_ms"] == 60

    def test_custom_section_loader(self, knowledge_dir):
        must = [{"fact": "f", "section": "libs/dao.json:s3"}]
        loader_calls = []

        def mock_loader(kd, ref):
            loader_calls.append(ref)
            return "custom content"

        responses = [_claim_present(), _hallucination_pass()]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        evaluate_answer("回答", must, [], knowledge_dir, llm_fn=mock_llm, section_loader=mock_loader)
        assert "libs/dao.json:s3" in loader_calls


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

    def test_output_structure(self, scenario, knowledge_dir):
        responses = [
            _wrap_llm_response({"answer": "SQLファイルで検索します"}),
            _claim_present(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scenario_id"] == "test-01"
        assert result["answer"] == "SQLファイルで検索します"
        assert "sections_input" in result
        assert "claim_verdicts" in result
        assert "hallucination" in result
        assert "scores" in result
        assert "metrics" in result

    def test_scores_correct(self, scenario, knowledge_dir):
        responses = [
            _wrap_llm_response({"answer": "回答テキスト"}),
            _claim_present(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["accuracy"] == 1.0
        assert result["scores"]["hallucination"] == 1

    def test_llm_call_count(self, scenario, knowledge_dir):
        responses = [
            _wrap_llm_response({"answer": "回答"}),
            _claim_present(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert call_idx[0] == 3

    def test_multiple_must_facts(self, knowledge_dir):
        data2 = _make_knowledge_file("File2", [
            {"id": "s1", "title": "T", "content": "content2"},
        ])
        _write_knowledge_file(knowledge_dir, "other.json", data2)

        scenario = {
            "id": "test-multi",
            "given": {"description": "test"},
            "when": {"input": "質問"},
            "then": {
                "must": [
                    {"fact": "f1", "section": "libs/dao.json:s3"},
                    {"fact": "f2", "section": "other.json:s1"},
                ],
                "acceptable": [],
            },
        }
        responses = [
            _wrap_llm_response({"answer": "回答"}),
            _claim_present(),
            _claim_absent(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scores"]["accuracy"] == 0.5
        assert len(result["claim_verdicts"]) == 2
        assert call_idx[0] == 4

    def test_no_hearing_answer(self, knowledge_dir):
        scenario = {
            "id": "test-no-ha",
            "given": {"description": "test"},
            "when": {"input": "質問"},
            "then": {
                "must": [{"fact": "f", "section": "libs/dao.json:s3"}],
                "acceptable": [],
            },
        }
        responses = [
            _wrap_llm_response({"answer": "回答"}),
            _claim_present(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scenario_id"] == "test-no-ha"

    def test_metrics_aggregated(self, scenario, knowledge_dir):
        m1 = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        m2 = {"duration_ms": 50, "total_cost_usd": 0.002, "usage": {"input_tokens": 300, "output_tokens": 20}}
        m3 = {"duration_ms": 60, "total_cost_usd": 0.003, "usage": {"input_tokens": 400, "output_tokens": 25}}
        responses = [
            _wrap_llm_response({"answer": "回答"}, m1),
            _wrap_llm_response({"verdict": "PRESENT", "reason": "ok"}, m2),
            _wrap_llm_response({"verdict": "PASS", "claims": [], "reason": "ok"}, m3),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["metrics"]["duration_ms"] == 210
        assert result["metrics"]["total_cost_usd"] == 0.015
        assert result["metrics"]["call_count"] == 3


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

        output_dir = tmp_path / "output"

        return {
            "knowledge_dir": str(knowledge_dir),
            "scenarios_path": str(scenarios_path),
            "output_dir": str(output_dir),
        }

    def _mock_llm_factory(self):
        """Create mock LLM that returns answer → claim PRESENT → hallucination PASS."""
        call_idx = [0]
        answer_resp = _wrap_llm_response({"answer": "回答"})
        claim_resp = _claim_present()
        hall_resp = _hallucination_pass()

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            phase = i % 3
            if phase == 0:
                return answer_resp
            elif phase == 1:
                return claim_resp
            else:
                return hall_resp

        return mock_llm, call_idx

    def test_runs_all_scenarios(self, setup):
        mock_llm, call_idx = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["total_scenarios"] == 2
        assert call_idx[0] == 6

    def test_scenario_filter(self, setup):
        mock_llm, call_idx = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
            scenario_ids=["sc-01"],
        )
        assert summary["total_scenarios"] == 1
        assert call_idx[0] == 3

    def test_writes_output_files(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        assert (out / "sc-01" / "answer.md").exists()
        assert (out / "sc-01" / "evaluation.json").exists()
        assert (out / "sc-01" / "metrics.json").exists()
        assert (out / "summary.json").exists()

    def test_summary_structure(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert "total_scenarios" in summary
        assert "scores" in summary
        assert "mean_accuracy" in summary["scores"]
        assert "hallucination_pass_rate" in summary["scores"]
        assert "pass_count" in summary["scores"]
        assert "pass_rate" in summary["scores"]
        assert "per_scenario" in summary
        assert "metrics" in summary

    def test_summary_scores_all_pass(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["scores"]["mean_accuracy"] == 1.0
        assert summary["scores"]["hallucination_pass_rate"] == 1.0
        assert summary["scores"]["pass_count"] == 2
        assert summary["scores"]["pass_rate"] == 1.0

    def test_per_scenario_structure(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        ps = summary["per_scenario"][0]
        assert "id" in ps
        assert "accuracy" in ps
        assert "hallucination" in ps
        assert "must_total" in ps
        assert "must_present" in ps
        assert "metrics" in ps

    def test_summary_with_failures(self, setup):
        responses = [
            _wrap_llm_response({"answer": "回答1"}),
            _claim_absent(),
            _hallucination_fail(),
            _wrap_llm_response({"answer": "回答2"}),
            _claim_present(),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert summary["scores"]["mean_accuracy"] == 0.5
        assert summary["scores"]["hallucination_pass_rate"] == 0.5
        assert summary["scores"]["pass_count"] == 1
        assert summary["scores"]["pass_rate"] == 0.5

    def test_evaluation_json_content(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        eval_data = json.loads((out / "sc-01" / "evaluation.json").read_text(encoding="utf-8"))
        assert "claim_verdicts" in eval_data
        assert "hallucination" in eval_data
        assert "scores" in eval_data

    def test_scenario_with_no_must_facts(self, tmp_path):
        knowledge_dir = tmp_path / "knowledge"
        knowledge_dir.mkdir()
        data = _make_knowledge_file("T", [
            {"id": "s1", "title": "S", "content": "C"},
        ])
        _write_knowledge_file(knowledge_dir, "f.json", data)

        scenarios = {
            "scenarios": [
                {
                    "id": "sc-no-must",
                    "given": {"description": "d"},
                    "when": {"input": "q"},
                    "then": {
                        "must": [],
                        "acceptable": [{"section": "f.json:s1"}],
                    },
                },
            ],
        }
        scenarios_path = tmp_path / "scenarios.json"
        scenarios_path.write_text(json.dumps(scenarios, ensure_ascii=False), encoding="utf-8")
        output_dir = tmp_path / "output"

        responses = [
            _wrap_llm_response({"answer": "回答"}),
            _hallucination_pass(),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        summary = simulate_all(
            str(scenarios_path),
            str(knowledge_dir),
            str(output_dir),
            llm_fn=mock_llm,
        )
        assert summary["scores"]["mean_accuracy"] is None
        assert summary["scores"]["hallucination_pass_rate"] == 1.0
        assert summary["scores"]["pass_count"] == 0
        ps = summary["per_scenario"][0]
        assert ps["accuracy"] is None
        assert ps["must_total"] == 0
