"""Tests for benchmark runner: semantic search + answer generation pipeline."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.run import (
    build_answer_prompt,
    format_sections_for_answer,
    parse_answer_response,
    save_scenario_results,
    aggregate_all_metrics,
    run_all,
    run_scenario,
)

DUMMY_METRICS = {
    "duration_ms": 100,
    "duration_api_ms": 90,
    "total_cost_usd": 0.001,
    "usage": {"input_tokens": 500, "output_tokens": 50},
}


def _wrap_llm_response(result, metrics=None):
    return {"result": result, "metrics": metrics or DUMMY_METRICS}


class TestBuildAnswerPrompt:
    def test_includes_question(self):
        prompt = build_answer_prompt("テスト質問", None, "セクション内容")
        assert "テスト質問" in prompt

    def test_includes_hearing_answer(self):
        hearing = {"processing_type": "Web", "goal": "フォームバリデーション"}
        prompt = build_answer_prompt("質問", hearing, "内容")
        assert "Web" in prompt
        assert "フォームバリデーション" in prompt

    def test_no_hearing(self):
        prompt = build_answer_prompt("質問", None, "内容")
        assert "なし" in prompt

    def test_includes_sections_content(self):
        prompt = build_answer_prompt("質問", None, "=== file.json:s1 ===\nコンテンツ")
        assert "file.json:s1" in prompt
        assert "コンテンツ" in prompt

    def test_loads_template(self):
        prompt = build_answer_prompt("質問", None, "内容")
        assert "回答ルール" in prompt
        assert "結論" in prompt

    def test_no_unreplaced_placeholders(self):
        prompt = build_answer_prompt("質問", None, "内容")
        assert "{question}" not in prompt
        assert "{hearing_answer}" not in prompt
        assert "{sections_content}" not in prompt


class TestFormatSectionsForAnswer:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        knowledge_dir = Path(self.tmpdir) / "component" / "libs"
        knowledge_dir.mkdir(parents=True)
        data = {
            "id": "test",
            "title": "テストライブラリ",
            "sections": [
                {"id": "s1", "title": "概要", "content": "概要テキスト", "level": 2},
                {"id": "s2", "title": "使用方法", "content": "使い方テキスト", "level": 2},
                {"id": "s3", "title": "設定", "content": "設定テキスト", "level": 3},
            ],
        }
        (knowledge_dir / "test.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_formats_single_section(self):
        results = [{"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"}]
        content = format_sections_for_answer(self.tmpdir, results)
        assert "component/libs/test.json:s1" in content
        assert "概要" in content
        assert "概要テキスト" in content

    def test_formats_multiple_sections(self):
        results = [
            {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
            {"file": "component/libs/test.json", "section_id": "s2", "relevance": "partial"},
        ]
        content = format_sections_for_answer(self.tmpdir, results)
        assert "概要テキスト" in content
        assert "使い方テキスト" in content

    def test_limits_to_max_sections(self):
        results = [
            {"file": "component/libs/test.json", "section_id": f"s{i}", "relevance": "high"}
            for i in range(1, 4)
        ]
        content = format_sections_for_answer(self.tmpdir, results, max_sections=2)
        assert "概要テキスト" in content
        assert "使い方テキスト" in content
        assert "設定テキスト" not in content

    def test_skips_missing_sections(self):
        results = [
            {"file": "component/libs/test.json", "section_id": "s99", "relevance": "high"},
            {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
        ]
        content = format_sections_for_answer(self.tmpdir, results)
        assert "概要テキスト" in content

    def test_skips_missing_files(self):
        results = [
            {"file": "nonexistent.json", "section_id": "s1", "relevance": "high"},
            {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
        ]
        content = format_sections_for_answer(self.tmpdir, results)
        assert "概要テキスト" in content

    def test_empty_results(self):
        content = format_sections_for_answer(self.tmpdir, [])
        assert content == ""


class TestParseAnswerResponse:
    def test_valid_response(self):
        response = {"answer": "回答テキスト"}
        assert parse_answer_response(response) == "回答テキスト"

    def test_missing_answer_field(self):
        with pytest.raises(ValueError, match="answer"):
            parse_answer_response({"text": "something"})

    def test_empty_answer(self):
        assert parse_answer_response({"answer": ""}) == ""


class TestAggregateAllMetrics:
    def test_three_stages(self):
        s1 = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        s2 = {"duration_ms": 200, "total_cost_usd": 0.02, "usage": {"input_tokens": 1000, "output_tokens": 100}}
        s3 = {"duration_ms": 150, "total_cost_usd": 0.015, "usage": {"input_tokens": 800, "output_tokens": 200}}
        result = aggregate_all_metrics(s1, s2, s3)
        assert result["duration_ms"] == 450
        assert result["total_cost_usd"] == 0.045
        assert result["total_tokens"] == 2650
        assert result["stages"]["stage1"]["duration_ms"] == 100
        assert result["stages"]["stage2"]["duration_ms"] == 200
        assert result["stages"]["answer"]["duration_ms"] == 150

    def test_all_empty(self):
        result = aggregate_all_metrics({}, {}, {})
        assert result["duration_ms"] == 0
        assert result["total_tokens"] == 0


class TestSaveScenarioResults:
    def test_saves_all_files(self):
        tmpdir = tempfile.mkdtemp()
        data = {
            "hearing": {"status": "provided", "processing_type": "Web", "goal": "テスト"},
            "search": {"section_ids": ["file.json:s1", "file.json:s2"]},
            "answer": "回答テキスト",
            "metrics": {"duration_ms": 1000, "total_tokens": 500},
        }
        save_scenario_results(tmpdir, "qa-01", data)

        scenario_dir = Path(tmpdir) / "qa-01"
        assert scenario_dir.is_dir()

        hearing = json.loads((scenario_dir / "hearing.json").read_text(encoding="utf-8"))
        assert hearing["status"] == "provided"
        assert hearing["processing_type"] == "Web"

        search = json.loads((scenario_dir / "search.json").read_text(encoding="utf-8"))
        assert search["section_ids"] == ["file.json:s1", "file.json:s2"]

        answer = (scenario_dir / "answer.md").read_text(encoding="utf-8")
        assert answer == "回答テキスト"

        metrics = json.loads((scenario_dir / "metrics.json").read_text(encoding="utf-8"))
        assert metrics["duration_ms"] == 1000


def _make_test_knowledge(tmpdir):
    """Create test knowledge dir with one file and return (dir, index_content)."""
    knowledge_dir = Path(tmpdir)
    comp_dir = knowledge_dir / "component" / "libs"
    comp_dir.mkdir(parents=True)
    data = {
        "id": "test-lib",
        "title": "テストライブラリ",
        "sections": [
            {"id": "s1", "title": "概要", "content": "概要テキスト", "level": 2},
            {"id": "s2", "title": "使用方法", "content": "使い方の詳細テキスト", "level": 2},
        ],
    }
    (comp_dir / "test.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    index = "# Index\n## component/libs\n### テストライブラリ\npath: component/libs/test.json\n- s1: 概要\n- s2: 使用方法\n"
    return str(knowledge_dir), index


def _make_scenarios_file(tmpdir, scenarios):
    """Write a scenarios JSON file and return its path."""
    path = Path(tmpdir) / "scenarios.json"
    path.write_text(json.dumps({"scenarios": scenarios}, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _make_mock_llm():
    """Create a mock LLM that returns stage1, stage2, and answer responses."""
    call_count = {"n": 0}

    def mock_llm(prompt, schema, model="sonnet"):
        call_count["n"] += 1
        stage = (call_count["n"] - 1) % 3
        if stage == 0:
            return _wrap_llm_response({
                "files": [{"path": "component/libs/test.json", "reason": "テスト"}]
            })
        elif stage == 1:
            return _wrap_llm_response({
                "results": [
                    {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
                ]
            })
        else:
            return _wrap_llm_response({"answer": "テスト回答"})

    return mock_llm


class TestRunAll:
    def setup_method(self):
        self.knowledge_tmpdir = tempfile.mkdtemp()
        self.knowledge_dir, self.index_content = _make_test_knowledge(self.knowledge_tmpdir)
        self.index_path = Path(self.knowledge_tmpdir) / "index.md"
        self.index_path.write_text(self.index_content, encoding="utf-8")
        self.output_dir = tempfile.mkdtemp()
        self.scenarios = [
            {
                "id": "qa-01",
                "when": {"input": "質問1"},
                "then": {"must": [], "acceptable": []},
            },
            {
                "id": "qa-02",
                "when": {"input": "質問2", "hearing_answer": {"processing_type": "Web", "goal": "テスト"}},
                "then": {"must": [], "acceptable": []},
            },
        ]

    def test_writes_summary_json(self):
        scenarios_path = _make_scenarios_file(self.knowledge_tmpdir, self.scenarios)
        import tools.benchmark.scripts.run as run_module
        original = run_module.run_scenario
        run_module.run_scenario = lambda sc, idx, kd, llm_fn=None, model="sonnet": {
            "scenario_id": sc["id"],
            "hearing": {"status": "skipped"},
            "search": {"section_ids": ["component/libs/test.json:s1"]},
            "answer": "テスト回答",
            "metrics": {"duration_ms": 100, "total_tokens": 500, "total_cost_usd": 0.001, "stages": {}},
        }
        try:
            summary = run_all(
                scenarios_path, self.knowledge_dir, self.output_dir,
                index_path=str(self.index_path),
            )
            assert summary["total_scenarios"] == 2
            summary_path = Path(self.output_dir) / "summary.json"
            assert summary_path.exists()
            saved = json.loads(summary_path.read_text(encoding="utf-8"))
            assert saved["total_scenarios"] == 2
            assert len(saved["scenarios"]) == 2
        finally:
            run_module.run_scenario = original

    def test_scenario_id_filtering(self):
        scenarios_path = _make_scenarios_file(self.knowledge_tmpdir, self.scenarios)
        import tools.benchmark.scripts.run as run_module
        original = run_module.run_scenario
        run_module.run_scenario = lambda sc, idx, kd, llm_fn=None, model="sonnet": {
            "scenario_id": sc["id"],
            "hearing": {"status": "skipped"},
            "search": {"section_ids": []},
            "answer": "回答",
            "metrics": {"duration_ms": 50, "total_tokens": 100, "total_cost_usd": 0.0, "stages": {}},
        }
        try:
            summary = run_all(
                scenarios_path, self.knowledge_dir, self.output_dir,
                index_path=str(self.index_path), scenario_ids=["qa-02"],
            )
            assert summary["total_scenarios"] == 1
            assert summary["scenarios"][0]["id"] == "qa-02"
        finally:
            run_module.run_scenario = original

    def test_empty_run(self):
        scenarios_path = _make_scenarios_file(self.knowledge_tmpdir, self.scenarios)
        import tools.benchmark.scripts.run as run_module
        original = run_module.run_scenario
        run_module.run_scenario = lambda sc, idx, kd, llm_fn=None, model="sonnet": None
        try:
            summary = run_all(
                scenarios_path, self.knowledge_dir, self.output_dir,
                index_path=str(self.index_path), scenario_ids=["nonexistent"],
            )
            assert summary["total_scenarios"] == 0
            assert summary["scenarios"] == []
        finally:
            run_module.run_scenario = original


class TestRunScenario:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpdir, self.index_content = _make_test_knowledge(self.tmpdir)

    def test_runs_full_pipeline(self):
        scenario = {
            "id": "qa-test",
            "when": {
                "input": "テスト質問",
                "hearing_answer": {"processing_type": "Web", "goal": "テスト"},
            },
            "then": {
                "must": [{"fact": "テスト事実", "section": "component/libs/test.json:s1"}],
                "acceptable": [],
            },
        }

        call_count = {"n": 0}

        def mock_llm(prompt, schema, model="sonnet"):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _wrap_llm_response({
                    "files": [{"path": "component/libs/test.json", "reason": "テスト"}]
                })
            elif call_count["n"] == 2:
                return _wrap_llm_response({
                    "results": [
                        {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
                    ]
                })
            else:
                return _wrap_llm_response({"answer": "テスト回答"})

        result = run_scenario(scenario, self.index_content, self.tmpdir, llm_fn=mock_llm)

        assert result["scenario_id"] == "qa-test"
        assert result["answer"] == "テスト回答"
        assert len(result["search"]["section_ids"]) == 1
        assert result["search"]["section_ids"][0] == "component/libs/test.json:s1"
        assert result["hearing"]["status"] == "provided"
        assert result["hearing"]["processing_type"] == "Web"
        assert "duration_ms" in result["metrics"]

    def test_scenario_without_hearing(self):
        scenario = {
            "id": "qa-nohear",
            "when": {"input": "テスト質問"},
            "then": {"must": [], "acceptable": []},
        }

        call_count = {"n": 0}

        def mock_llm(prompt, schema, model="sonnet"):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return _wrap_llm_response({
                    "files": [{"path": "component/libs/test.json", "reason": "テスト"}]
                })
            elif call_count["n"] == 2:
                return _wrap_llm_response({
                    "results": [
                        {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
                    ]
                })
            else:
                return _wrap_llm_response({"answer": "回答"})

        result = run_scenario(scenario, self.index_content, self.tmpdir, llm_fn=mock_llm)
        assert result["hearing"]["status"] == "skipped"
