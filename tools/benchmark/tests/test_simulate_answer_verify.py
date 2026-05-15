"""Tests for answer generation + verification simulation."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.simulate_answer_verify import (
    aggregate_metrics,
    build_answer_prompt,
    build_answer_retry_prompt,
    build_verify_prompt,
    format_section_content,
    load_scenario_sections,
    parse_answer_response,
    parse_verify_response,
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
    """Create a knowledge file dict."""
    return {
        "title": title,
        "sections": [
            {"id": s["id"], "title": s["title"], "content": s["content"]}
            for s in sections
        ],
    }


def _write_knowledge_file(tmp_path, rel_path, data):
    """Write a knowledge file to the temp directory."""
    full_path = tmp_path / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestFormatSectionContent:
    def test_basic_format(self):
        result = format_section_content(
            "libs/dao.json", "s3", "ユニバーサルDAO", "検索方法", "SQLファイルを作成して検索する"
        )
        assert "=== libs/dao.json : s3 ===" in result
        assert "# ユニバーサルDAO > 検索方法" in result
        assert "SQLファイルを作成して検索する" in result
        assert "=== END ===" in result

    def test_empty_content(self):
        result = format_section_content("file.json", "s1", "Title", "Section", "")
        assert "=== file.json : s1 ===" in result
        assert "# Title > Section" in result
        assert "=== END ===" in result

    def test_multiline_content(self):
        content = "行1\n行2\nコード例:\n```java\npublic void test() {}\n```"
        result = format_section_content("file.json", "s1", "T", "S", content)
        assert content in result


class TestLoadScenarioSections:
    def test_loads_must_and_acceptable(self, tmp_path):
        data = _make_knowledge_file("DAO", [
            {"id": "s1", "title": "概要", "content": "概要内容"},
            {"id": "s3", "title": "検索", "content": "検索内容"},
        ])
        _write_knowledge_file(tmp_path, "libs/dao.json", data)

        must = [{"fact": "fact1", "section": "libs/dao.json:s3"}]
        acceptable = [{"section": "libs/dao.json:s1"}]
        content, refs = load_scenario_sections(tmp_path, must, acceptable)

        assert "検索内容" in content
        assert "概要内容" in content
        assert refs == ["libs/dao.json:s3", "libs/dao.json:s1"]

    def test_must_before_acceptable(self, tmp_path):
        data = _make_knowledge_file("T", [
            {"id": "s1", "title": "A", "content": "acceptable"},
            {"id": "s2", "title": "M", "content": "must"},
        ])
        _write_knowledge_file(tmp_path, "f.json", data)

        must = [{"fact": "f", "section": "f.json:s2"}]
        acceptable = [{"section": "f.json:s1"}]
        content, refs = load_scenario_sections(tmp_path, must, acceptable)

        must_pos = content.index("must")
        acc_pos = content.index("acceptable")
        assert must_pos < acc_pos

    def test_missing_file_skips(self, tmp_path, capsys):
        must = [{"fact": "f", "section": "nonexistent.json:s1"}]
        content, refs = load_scenario_sections(tmp_path, must, [])
        assert content == ""
        assert refs == []
        assert "WARNING" in capsys.readouterr().err

    def test_missing_section_skips(self, tmp_path, capsys):
        data = _make_knowledge_file("T", [{"id": "s1", "title": "A", "content": "ok"}])
        _write_knowledge_file(tmp_path, "f.json", data)

        must = [{"fact": "f", "section": "f.json:s99"}]
        content, refs = load_scenario_sections(tmp_path, must, [])
        assert content == ""
        assert refs == []
        assert "WARNING" in capsys.readouterr().err

    def test_empty_sections(self, tmp_path):
        content, refs = load_scenario_sections(tmp_path, [], [])
        assert content == ""
        assert refs == []

    def test_multiple_files(self, tmp_path):
        data1 = _make_knowledge_file("File1", [
            {"id": "s1", "title": "T1", "content": "content1"},
        ])
        data2 = _make_knowledge_file("File2", [
            {"id": "s2", "title": "T2", "content": "content2"},
        ])
        _write_knowledge_file(tmp_path, "a.json", data1)
        _write_knowledge_file(tmp_path, "b.json", data2)

        must = [
            {"fact": "f1", "section": "a.json:s1"},
            {"fact": "f2", "section": "b.json:s2"},
        ]
        content, refs = load_scenario_sections(tmp_path, must, [])
        assert "content1" in content
        assert "content2" in content
        assert refs == ["a.json:s1", "b.json:s2"]


class TestBuildAnswerPrompt:
    def test_substitutes_all_placeholders(self):
        prompt = build_answer_prompt("質問文", {"processing_type": "Web", "goal": "回答"}, "セクション内容")
        assert "質問文" in prompt
        assert "処理方式: Web" in prompt
        assert "やりたいこと: 回答" in prompt
        assert "セクション内容" in prompt

    def test_no_hearing_answer(self):
        prompt = build_answer_prompt("質問文", None, "セクション")
        assert "なし" in prompt
        assert "{hearing_answer}" not in prompt

    def test_no_unreplaced_placeholders(self):
        prompt = build_answer_prompt("q", {"processing_type": "Web", "goal": "g"}, "s")
        assert "{question}" not in prompt
        assert "{hearing_answer}" not in prompt
        assert "{sections_content}" not in prompt


class TestBuildAnswerRetryPrompt:
    def test_appends_exclusion_instructions(self):
        base = "original prompt"
        issues = [
            {"claim": "UniversalDaoはスレッドセーフ", "quote": "スレッドセーフに動作します"},
        ]
        result = build_answer_retry_prompt(base, issues)
        assert "original prompt" in result
        assert "除外指示" in result
        assert "UniversalDaoはスレッドセーフ" in result

    def test_multiple_issues(self):
        issues = [
            {"claim": "claim1", "quote": "q1"},
            {"claim": "claim2", "quote": "q2"},
        ]
        result = build_answer_retry_prompt("base", issues)
        assert "claim1" in result
        assert "claim2" in result

    def test_empty_issues_returns_base_unchanged(self):
        result = build_answer_retry_prompt("base", [])
        assert result == "base"


class TestBuildVerifyPrompt:
    def test_substitutes_all_placeholders(self):
        prompt = build_verify_prompt("回答テキスト", "セクション内容")
        assert "回答テキスト" in prompt
        assert "セクション内容" in prompt

    def test_no_unreplaced_placeholders(self):
        prompt = build_verify_prompt("a", "s")
        assert "{answer}" not in prompt
        assert "{sections_content}" not in prompt


class TestParseAnswerResponse:
    def test_valid_response(self):
        result = parse_answer_response({"answer": "回答テキスト", "trace": {"user_intent": "i", "sections": []}})
        assert result == "回答テキスト"

    def test_missing_answer_key(self):
        with pytest.raises(ValueError, match="answer"):
            parse_answer_response({"text": "wrong key"})

    def test_response_without_trace_still_works(self):
        result = parse_answer_response({"answer": "回答テキスト"})
        assert result == "回答テキスト"


class TestParseVerifyResponse:
    def test_valid_pass(self):
        response = {
            "result": "PASS",
            "claims": [
                {"claim": "c1", "supported": True, "evidence": "f.json:s1"},
            ],
            "issues": [],
        }
        result = parse_verify_response(response)
        assert result["result"] == "PASS"
        assert len(result["claims"]) == 1
        assert result["issues"] == []

    def test_valid_fail(self):
        response = {
            "result": "FAIL",
            "claims": [
                {"claim": "c1", "supported": True, "evidence": "f.json:s1"},
                {"claim": "c2", "supported": False, "evidence": ""},
            ],
            "issues": [
                {"claim": "c2", "quote": "original text"},
            ],
        }
        result = parse_verify_response(response)
        assert result["result"] == "FAIL"
        assert len(result["claims"]) == 2
        assert len(result["issues"]) == 1

    def test_invalid_result(self):
        with pytest.raises(ValueError, match="result"):
            parse_verify_response({"result": "MAYBE", "claims": [], "issues": []})

    def test_missing_result_key(self):
        with pytest.raises(ValueError, match="result"):
            parse_verify_response({"claims": [], "issues": []})

    def test_missing_claims_key(self):
        with pytest.raises(ValueError, match="claims"):
            parse_verify_response({"result": "PASS", "issues": []})

    def test_missing_issues_key(self):
        with pytest.raises(ValueError, match="issues"):
            parse_verify_response({"result": "FAIL", "claims": []})

    def test_claims_not_list(self):
        with pytest.raises(ValueError, match="claims"):
            parse_verify_response({"result": "PASS", "claims": "not_list", "issues": []})

    def test_issues_not_list(self):
        with pytest.raises(ValueError, match="issues"):
            parse_verify_response({"result": "PASS", "claims": [], "issues": "not_list"})


class TestAggregateMetrics:
    def test_answer_and_verify_only(self):
        answer = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        verify = {"duration_ms": 80, "total_cost_usd": 0.005, "usage": {"input_tokens": 400, "output_tokens": 30}}
        result = aggregate_metrics(answer, verify)
        assert result["duration_ms"] == 180
        assert result["total_cost_usd"] == 0.015
        assert result["total_tokens"] == 980
        assert "retry" not in result["stages"]

    def test_with_retry(self):
        answer = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        verify = {"duration_ms": 80, "total_cost_usd": 0.005, "usage": {"input_tokens": 400, "output_tokens": 30}}
        retry = {"duration_ms": 90, "total_cost_usd": 0.008, "usage": {"input_tokens": 600, "output_tokens": 60}}
        result = aggregate_metrics(answer, verify, retry)
        assert result["duration_ms"] == 270
        assert result["total_cost_usd"] == 0.023
        assert result["total_tokens"] == 1640
        assert "retry" in result["stages"]

    def test_empty_metrics(self):
        result = aggregate_metrics({}, {})
        assert result["duration_ms"] == 0
        assert result["total_cost_usd"] == 0.0
        assert result["total_tokens"] == 0


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

    def _answer_with_trace(self, answer_text="SQLファイルで検索します"):
        return _wrap_llm_response({
            "answer": answer_text,
            "trace": {
                "user_intent": "検索方法を知りたい",
                "sections": [{"section": "libs/dao.json:s3", "used": True, "extracted": "SQLファイルで検索する", "mapped_to": "結論"}],
            },
        })

    def test_verify_pass_no_retry(self, scenario, knowledge_dir):
        responses = [
            self._answer_with_trace(),
            _wrap_llm_response({
                "result": "PASS",
                "claims": [{"claim": "SQLファイルで検索", "supported": True, "evidence": "libs/dao.json:s3"}],
                "issues": [],
            }),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scenario_id"] == "test-01"
        assert result["answer"] == "SQLファイルで検索します"
        assert result["verify"]["result"] == "PASS"
        assert result["retry_answer"] is None
        assert call_idx[0] == 2

    def test_trace_in_result(self, scenario, knowledge_dir):
        responses = [
            self._answer_with_trace(),
            _wrap_llm_response({"result": "PASS", "claims": [], "issues": []}),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["trace"]["user_intent"] == "検索方法を知りたい"
        assert result["trace"]["sections"][0]["extracted"] == "SQLファイルで検索する"

    def test_verify_fail_triggers_retry(self, scenario, knowledge_dir):
        responses = [
            self._answer_with_trace("スレッドセーフに検索します"),
            _wrap_llm_response({
                "result": "FAIL",
                "claims": [
                    {"claim": "スレッドセーフ", "supported": False, "evidence": ""},
                ],
                "issues": [{"claim": "スレッドセーフ", "quote": "スレッドセーフに"}],
            }),
            self._answer_with_trace("SQLファイルで検索します"),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["verify"]["result"] == "FAIL"
        assert result["retry_answer"] == "SQLファイルで検索します"
        assert call_idx[0] == 3

    def test_output_structure(self, scenario, knowledge_dir):
        responses = [
            self._answer_with_trace("回答"),
            _wrap_llm_response({"result": "PASS", "claims": [], "issues": []}),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert "scenario_id" in result
        assert "sections_input" in result
        assert "answer" in result
        assert "trace" in result
        assert "verify" in result
        assert "retry_answer" in result
        assert "metrics" in result

    def test_verify_fail_empty_issues_no_retry(self, scenario, knowledge_dir):
        responses = [
            self._answer_with_trace("some answer"),
            _wrap_llm_response({
                "result": "FAIL",
                "claims": [{"claim": "c", "supported": False, "evidence": ""}],
                "issues": [],
            }),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["verify"]["result"] == "FAIL"
        assert result["retry_answer"] is None
        assert call_idx[0] == 2

    def test_no_hearing_answer(self, knowledge_dir):
        scenario = {
            "id": "test-02",
            "given": {"description": "test"},
            "when": {"input": "質問"},
            "then": {
                "must": [{"fact": "f", "section": "libs/dao.json:s3"}],
                "acceptable": [],
            },
        }
        responses = [
            self._answer_with_trace("回答"),
            _wrap_llm_response({"result": "PASS", "claims": [], "issues": []}),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        result = simulate_scenario(scenario, knowledge_dir, llm_fn=mock_llm)
        assert result["scenario_id"] == "test-02"


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
        call_idx = [0]
        pass_response = _wrap_llm_response({"result": "PASS", "claims": [], "issues": []})
        answer_response = _wrap_llm_response({
            "answer": "回答",
            "trace": {
                "user_intent": "テストの意図",
                "sections": [{"section": "f.json:s1", "used": True, "extracted": "C", "mapped_to": "結論"}],
            },
        })

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            if i % 2 == 0:
                return answer_response
            return pass_response

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
        assert call_idx[0] == 4

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
        assert call_idx[0] == 2

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
        assert (out / "sc-01" / "verify.json").exists()
        assert (out / "sc-01" / "trace.json").exists()
        assert (out / "sc-01" / "metrics.json").exists()
        assert (out / "summary.json").exists()

    def test_trace_json_content(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        trace = json.loads((out / "sc-01" / "trace.json").read_text(encoding="utf-8"))
        assert "user_intent" in trace
        assert "sections" in trace
        assert trace["sections"][0]["section"] == "f.json:s1"
        assert trace["sections"][0]["used"] is True
        assert trace["sections"][0]["extracted"] == "C"

    def test_summary_structure(self, setup):
        mock_llm, _ = self._mock_llm_factory()
        summary = simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        assert "total_scenarios" in summary
        assert "verify_pass" in summary
        assert "verify_fail" in summary
        assert "retry_count" in summary
        assert "per_scenario" in summary

    def test_retry_writes_retry_answer(self, setup):
        dummy_trace = {"user_intent": "t", "sections": []}
        responses = [
            _wrap_llm_response({"answer": "bad answer", "trace": dummy_trace}),
            _wrap_llm_response({
                "result": "FAIL",
                "claims": [{"claim": "c", "supported": False, "evidence": ""}],
                "issues": [{"claim": "c", "quote": "q"}],
            }),
            _wrap_llm_response({"answer": "good answer", "trace": dummy_trace}),
            _wrap_llm_response({"answer": "answer2", "trace": dummy_trace}),
            _wrap_llm_response({"result": "PASS", "claims": [], "issues": []}),
        ]
        call_idx = [0]

        def mock_llm(prompt, schema):
            i = call_idx[0]
            call_idx[0] += 1
            return responses[i]

        simulate_all(
            setup["scenarios_path"],
            setup["knowledge_dir"],
            setup["output_dir"],
            llm_fn=mock_llm,
        )
        out = Path(setup["output_dir"])
        assert (out / "sc-01" / "retry_answer.md").exists()
        assert (out / "sc-01" / "retry_answer.md").read_text(encoding="utf-8") == "good answer"
        assert not (out / "sc-02" / "retry_answer.md").exists()
