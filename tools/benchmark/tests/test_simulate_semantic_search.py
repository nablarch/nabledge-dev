"""Tests for 2-stage semantic search simulation."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.simulate_semantic_search import (
    _aggregate_stage_metrics,
    build_stage1_prompt,
    build_stage2_prompt,
    compare_results,
    format_file_content,
    format_files_content,
    format_hearing_answer,
    parse_stage1_response,
    parse_stage2_response,
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


class TestAggregateStageMetrics:
    def test_combines_two_stages(self):
        s1 = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        s2 = {"duration_ms": 200, "total_cost_usd": 0.02, "usage": {"input_tokens": 1000, "output_tokens": 100}}
        result = _aggregate_stage_metrics(s1, s2)
        assert result["total_duration_ms"] == 300
        assert result["total_cost_usd"] == 0.03
        assert result["total_input_tokens"] == 1500
        assert result["total_output_tokens"] == 150

    def test_both_empty(self):
        assert _aggregate_stage_metrics({}, {}) == {}

    def test_missing_fields_default_to_zero(self):
        result = _aggregate_stage_metrics({"duration_ms": 50}, {"duration_ms": 30})
        assert result["total_duration_ms"] == 80
        assert result["total_cost_usd"] == 0.0
        assert result["total_input_tokens"] == 0
        assert result["total_output_tokens"] == 0


class TestFormatHearingAnswer:
    def test_none(self):
        assert format_hearing_answer(None) == "なし"

    def test_empty_dict(self):
        assert format_hearing_answer({}) == "なし"

    def test_both_axes(self):
        ha = {"processing_type": "Web", "goal": "バリデーションする"}
        result = format_hearing_answer(ha)
        assert "処理方式: Web" in result
        assert "やりたいこと: バリデーションする" in result

    def test_null_processing_type(self):
        ha = {"processing_type": None, "goal": "テストを書く"}
        result = format_hearing_answer(ha)
        assert "処理方式" not in result
        assert "やりたいこと: テストを書く" in result

    def test_goal_only(self):
        ha = {"goal": "テストを書く"}
        result = format_hearing_answer(ha)
        assert "処理方式" not in result
        assert "やりたいこと: テストを書く" in result


class TestBuildStage1Prompt:
    def test_substitutes_all_placeholders(self):
        ha = {"processing_type": "Web", "goal": "回答文"}
        prompt = build_stage1_prompt("質問文", ha, "インデックス内容")
        assert "質問文" in prompt
        assert "処理方式: Web" in prompt
        assert "やりたいこと: 回答文" in prompt
        assert "インデックス内容" in prompt

    def test_no_hearing_answer(self):
        prompt = build_stage1_prompt("質問文", None, "インデックス内容")
        assert "なし" in prompt
        assert "{hearing_answer}" not in prompt

    def test_empty_hearing_answer(self):
        prompt = build_stage1_prompt("質問文", {}, "インデックス内容")
        assert "なし" in prompt

    def test_no_unreplaced_placeholders(self):
        ha = {"processing_type": "REST API", "goal": "登録する"}
        prompt = build_stage1_prompt("Q", ha, "I")
        assert "{question}" not in prompt
        assert "{hearing_answer}" not in prompt
        assert "{index_content}" not in prompt


class TestBuildStage2Prompt:
    def test_substitutes_all_placeholders(self):
        ha = {"processing_type": "Nablarchバッチ", "goal": "回答文"}
        prompt = build_stage2_prompt("質問文", ha, "ファイル内容")
        assert "質問文" in prompt
        assert "処理方式: Nablarchバッチ" in prompt
        assert "やりたいこと: 回答文" in prompt
        assert "ファイル内容" in prompt

    def test_no_hearing_answer(self):
        prompt = build_stage2_prompt("質問文", None, "ファイル内容")
        assert "なし" in prompt

    def test_no_unreplaced_placeholders(self):
        ha = {"processing_type": "Web", "goal": "検索する"}
        prompt = build_stage2_prompt("Q", ha, "C")
        assert "{question}" not in prompt
        assert "{hearing_answer}" not in prompt
        assert "{files_content}" not in prompt


class TestFormatFileContent:
    def test_basic_format(self):
        data = {
            "id": "test",
            "title": "テストファイル",
            "sections": [
                {"id": "s1", "title": "概要", "content": "概要の内容", "level": 2},
                {"id": "s2", "title": "詳細", "content": "詳細の内容", "level": 3},
            ],
        }
        result = format_file_content("component/test.json", data)
        assert "## component/test.json" in result
        assert "テストファイル" in result
        assert "### s1: 概要" in result
        assert "概要の内容" in result
        assert "### s2: 詳細" in result
        assert "詳細の内容" in result

    def test_empty_sections(self):
        data = {"id": "test", "title": "空", "sections": []}
        result = format_file_content("test.json", data)
        assert "## test.json" in result
        assert "空" in result

    def test_missing_content(self):
        data = {
            "id": "test",
            "title": "タイトル",
            "sections": [{"id": "s1", "title": "セクション"}],
        }
        result = format_file_content("test.json", data)
        assert "### s1: セクション" in result

    def test_section_ids_are_present(self):
        data = {
            "id": "test",
            "title": "T",
            "sections": [
                {"id": "s5", "title": "A", "content": "text"},
                {"id": "s12", "title": "B", "content": "text"},
            ],
        }
        result = format_file_content("test.json", data)
        assert "### s5: A" in result
        assert "### s12: B" in result


class TestFormatFilesContent:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        subdir = Path(self.tmpdir) / "component" / "libs"
        subdir.mkdir(parents=True)
        data = {
            "id": "test",
            "title": "テスト",
            "sections": [{"id": "s1", "title": "概要", "content": "内容"}],
        }
        (subdir / "test.json").write_text(json.dumps(data, ensure_ascii=False))

    def test_loads_and_formats(self):
        result = format_files_content(
            self.tmpdir, ["component/libs/test.json"]
        )
        assert "component/libs/test.json" in result
        assert "テスト" in result
        assert "内容" in result

    def test_multiple_files(self):
        subdir = Path(self.tmpdir) / "other"
        subdir.mkdir()
        data = {"id": "t2", "title": "二番目", "sections": []}
        (subdir / "t2.json").write_text(json.dumps(data, ensure_ascii=False))

        result = format_files_content(
            self.tmpdir,
            ["component/libs/test.json", "other/t2.json"],
        )
        assert "component/libs/test.json" in result
        assert "other/t2.json" in result

    def test_nonexistent_file_skipped(self):
        result = format_files_content(
            self.tmpdir,
            ["component/libs/test.json", "nonexistent.json"],
        )
        assert "component/libs/test.json" in result
        assert "nonexistent.json" not in result


class TestParseStage1Response:
    def test_valid_response(self):
        response = {
            "files": [
                {"path": "a/b.json", "reason": "理由1"},
                {"path": "c/d.json", "reason": "理由2"},
            ]
        }
        result = parse_stage1_response(response)
        assert len(result) == 2
        assert result[0]["path"] == "a/b.json"
        assert result[1]["path"] == "c/d.json"

    def test_empty_files(self):
        result = parse_stage1_response({"files": []})
        assert result == []

    def test_missing_files_key(self):
        with pytest.raises(ValueError, match="files"):
            parse_stage1_response({})

    def test_files_not_a_list(self):
        with pytest.raises(ValueError, match="must be a list"):
            parse_stage1_response({"files": "not a list"})

    def test_files_not_a_list_dict(self):
        with pytest.raises(ValueError, match="must be a list"):
            parse_stage1_response({"files": {"path": "a.json"}})

    def test_exactly_10_files(self):
        files = [{"path": f"f{i}.json", "reason": "r"} for i in range(10)]
        result = parse_stage1_response({"files": files})
        assert len(result) == 10

    def test_max_10_files(self):
        files = [{"path": f"f{i}.json", "reason": "r"} for i in range(12)]
        result = parse_stage1_response({"files": files})
        assert len(result) == 10


class TestParseStage2Response:
    def test_valid_response(self):
        response = {
            "results": [
                {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
                {"file": "a/b.json", "section_id": "s3", "relevance": "partial"},
            ]
        }
        result = parse_stage2_response(response)
        assert len(result) == 2
        assert result[0]["relevance"] == "high"

    def test_empty_results(self):
        result = parse_stage2_response({"results": []})
        assert result == []

    def test_missing_results_key(self):
        with pytest.raises(ValueError, match="results"):
            parse_stage2_response({})

    def test_results_not_a_list(self):
        with pytest.raises(ValueError, match="must be a list"):
            parse_stage2_response({"results": "not a list"})

    def test_invalid_relevance(self):
        with pytest.raises(ValueError, match="relevance"):
            parse_stage2_response({
                "results": [{"file": "a.json", "section_id": "s1", "relevance": "low"}]
            })

    def test_exactly_30_results(self):
        results = [
            {"file": "a.json", "section_id": f"s{i}", "relevance": "high"}
            for i in range(30)
        ]
        result = parse_stage2_response({"results": results})
        assert len(result) == 30

    def test_max_30_results(self):
        results = [
            {"file": "a.json", "section_id": f"s{i}", "relevance": "high"}
            for i in range(35)
        ]
        result = parse_stage2_response({"results": results})
        assert len(result) == 30


class TestCompareResults:
    def test_all_must_hit(self):
        results = [
            {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
            {"file": "a/b.json", "section_id": "s2", "relevance": "partial"},
        ]
        must = [
            {"fact": "fact1", "section": "a/b.json:s1"},
            {"fact": "fact2", "section": "a/b.json:s2"},
        ]
        comparison = compare_results(results, must, [])
        assert comparison["must_hit"] == 2
        assert comparison["must_miss"] == 0
        assert comparison["hit_rate"] == 1.0

    def test_partial_hit(self):
        results = [
            {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
        ]
        must = [
            {"fact": "f1", "section": "a/b.json:s1"},
            {"fact": "f2", "section": "a/b.json:s3"},
        ]
        comparison = compare_results(results, must, [])
        assert comparison["must_hit"] == 1
        assert comparison["must_miss"] == 1
        assert comparison["hit_rate"] == 0.5

    def test_all_miss(self):
        results = [
            {"file": "x/y.json", "section_id": "s9", "relevance": "high"},
        ]
        must = [{"fact": "f1", "section": "a/b.json:s1"}]
        comparison = compare_results(results, must, [])
        assert comparison["must_hit"] == 0
        assert comparison["must_miss"] == 1
        assert comparison["hit_rate"] == 0.0

    def test_empty_results(self):
        must = [{"fact": "f1", "section": "a/b.json:s1"}]
        comparison = compare_results([], must, [])
        assert comparison["must_miss"] == 1
        assert comparison["hit_rate"] == 0.0

    def test_empty_must(self):
        results = [{"file": "a.json", "section_id": "s1", "relevance": "high"}]
        comparison = compare_results(results, [], [])
        assert comparison["must_hit"] == 0
        assert comparison["hit_rate"] == 1.0

    def test_acceptable_tracking(self):
        results = [
            {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
            {"file": "a/b.json", "section_id": "s5", "relevance": "partial"},
        ]
        must = [{"fact": "f1", "section": "a/b.json:s1"}]
        acceptable = [
            {"section": "a/b.json:s5"},
            {"section": "a/b.json:s9"},
        ]
        comparison = compare_results(results, must, acceptable)
        assert comparison["acceptable_hits"] == ["a/b.json:s5"]
        assert len(comparison["acceptable_hits"]) == 1

    def test_duplicate_must_sections(self):
        results = [
            {"file": "a/b.json", "section_id": "s29", "relevance": "high"},
        ]
        must = [
            {"fact": "fact1", "section": "a/b.json:s29"},
            {"fact": "fact2", "section": "a/b.json:s29"},
        ]
        comparison = compare_results(results, must, [])
        assert comparison["must_hit"] == 2
        assert comparison["must_miss"] == 0

    def test_must_hit_details(self):
        results = [
            {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
        ]
        must = [
            {"fact": "f1", "section": "a/b.json:s1"},
            {"fact": "f2", "section": "c/d.json:s2"},
        ]
        comparison = compare_results(results, must, [])
        assert "a/b.json:s1" in comparison["must_hits"]
        assert "c/d.json:s2" in comparison["must_misses"]

    def test_stage1_file_coverage(self):
        results = [
            {"file": "a/b.json", "section_id": "s1", "relevance": "high"},
            {"file": "c/d.json", "section_id": "s2", "relevance": "partial"},
        ]
        must = [
            {"fact": "f1", "section": "a/b.json:s1"},
            {"fact": "f2", "section": "e/f.json:s3"},
        ]
        comparison = compare_results(results, must, [])
        assert comparison["must_file_hit"] == 1
        assert comparison["must_file_miss"] == 1


class TestSimulateScenario:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        subdir = Path(self.tmpdir) / "component" / "libs"
        subdir.mkdir(parents=True)
        data = {
            "id": "test",
            "title": "テスト",
            "sections": [
                {"id": "s1", "title": "概要", "content": "内容A", "level": 2},
                {"id": "s2", "title": "詳細", "content": "内容B", "level": 2},
            ],
        }
        (subdir / "test.json").write_text(json.dumps(data, ensure_ascii=False))

    def test_full_pipeline(self):
        scenario = {
            "id": "test-01",
            "when": {
                "input": "テスト質問",
                "hearing_answer": {"processing_type": "Web", "goal": "回答"},
            },
            "then": {
                "must": [{"fact": "f1", "section": "component/libs/test.json:s1"}],
                "acceptable": [],
            },
        }
        stage1_response = {"files": [{"path": "component/libs/test.json", "reason": "理由"}]}
        stage2_response = {
            "results": [
                {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
            ]
        }
        call_count = 0

        def mock_llm(prompt, schema, model="sonnet"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _wrap_llm_response(stage1_response)
            return _wrap_llm_response(stage2_response)

        result = simulate_scenario(
            scenario, "index content", self.tmpdir, llm_fn=mock_llm
        )
        assert result["scenario_id"] == "test-01"
        assert result["comparison"]["must_hit"] == 1
        assert result["comparison"]["hit_rate"] == 1.0
        assert len(result["stage1"]["files"]) == 1
        assert len(result["stage2"]["results"]) == 1
        assert "metrics" in result["stage1"]
        assert "metrics" in result["stage2"]
        assert result["metrics"]["total_duration_ms"] == 200
        assert result["metrics"]["total_cost_usd"] == 0.002

    def test_no_hearing_answer(self):
        scenario = {
            "id": "test-02",
            "when": {"input": "質問"},
            "then": {
                "must": [{"fact": "f", "section": "component/libs/test.json:s1"}],
                "acceptable": [],
            },
        }
        call_count = 0

        def mock_llm(prompt, schema, model="sonnet"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                assert "なし" in prompt
                return _wrap_llm_response({"files": [{"path": "component/libs/test.json", "reason": "r"}]})
            return _wrap_llm_response({"results": [{"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"}]})

        result = simulate_scenario(scenario, "idx", self.tmpdir, llm_fn=mock_llm)
        assert result["comparison"]["must_hit"] == 1

    def test_stage1_returns_nonexistent_file(self):
        scenario = {
            "id": "test-03",
            "when": {"input": "質問"},
            "then": {
                "must": [{"fact": "f", "section": "component/libs/test.json:s1"}],
                "acceptable": [],
            },
        }
        call_count = 0

        def mock_llm(prompt, schema, model="sonnet"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _wrap_llm_response({"files": [
                    {"path": "nonexistent.json", "reason": "r"},
                    {"path": "component/libs/test.json", "reason": "r2"},
                ]})
            return _wrap_llm_response({"results": []})

        result = simulate_scenario(scenario, "idx", self.tmpdir, llm_fn=mock_llm)
        assert result["stage1"]["files"][0]["path"] == "nonexistent.json"

    def test_output_structure(self):
        scenario = {
            "id": "test-04",
            "when": {"input": "Q", "hearing_answer": {"processing_type": "Web", "goal": "A"}},
            "then": {"must": [], "acceptable": []},
        }

        def mock_llm(prompt, schema, model="sonnet"):
            if "インデックス" in prompt or "index" in prompt.lower():
                return _wrap_llm_response({"files": []})
            return _wrap_llm_response({"results": []})

        result = simulate_scenario(scenario, "idx", self.tmpdir, llm_fn=mock_llm)
        assert "scenario_id" in result
        assert "stage1" in result
        assert "stage2" in result
        assert "comparison" in result
        assert "metrics" in result
        assert "files" in result["stage1"]
        assert "metrics" in result["stage1"]
        assert "results" in result["stage2"]
        assert "metrics" in result["stage2"]


class TestSimulateAll:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        subdir = Path(self.tmpdir) / "component" / "libs"
        subdir.mkdir(parents=True)
        data = {
            "id": "test",
            "title": "テスト",
            "sections": [
                {"id": "s1", "title": "概要", "content": "内容", "level": 2},
            ],
        }
        (subdir / "test.json").write_text(json.dumps(data, ensure_ascii=False))

        self.scenarios_path = Path(self.tmpdir) / "scenarios.json"
        self.scenarios_path.write_text(json.dumps({
            "description": "test",
            "schema_version": "1.0",
            "scenarios": [
                {
                    "id": "s-01",
                    "when": {"input": "質問1", "hearing_answer": {"processing_type": "Web", "goal": "回答1"}},
                    "then": {
                        "must": [{"fact": "f1", "section": "component/libs/test.json:s1"}],
                        "acceptable": [],
                    },
                },
                {
                    "id": "s-02",
                    "when": {"input": "質問2"},
                    "then": {
                        "must": [{"fact": "f2", "section": "component/libs/test.json:s1"}],
                        "acceptable": [],
                    },
                },
            ],
        }, ensure_ascii=False))

    def _mock_llm(self, prompt, schema, model="sonnet"):
        if "インデックス" in prompt or "index" in prompt.lower():
            return _wrap_llm_response({"files": [{"path": "component/libs/test.json", "reason": "r"}]})
        return _wrap_llm_response({"results": [
            {"file": "component/libs/test.json", "section_id": "s1", "relevance": "high"},
        ]})

    def test_writes_output_files(self):
        from unittest.mock import patch
        with patch(
            "tools.benchmark.scripts.simulate_semantic_search.call_llm",
            side_effect=self._mock_llm,
        ):
            summary = simulate_all(
                str(self.scenarios_path),
                self.tmpdir,
                "index content",
                self.output_dir,
            )

        out = Path(self.output_dir)
        assert (out / "s-01" / "stage1.json").exists()
        assert (out / "s-01" / "stage2.json").exists()
        assert (out / "s-01" / "comparison.json").exists()
        assert (out / "s-01" / "metrics.json").exists()
        assert (out / "s-02" / "stage1.json").exists()
        assert (out / "summary.json").exists()

        with open(out / "summary.json") as f:
            saved_summary = json.load(f)
        assert saved_summary["total_scenarios"] == 2
        assert saved_summary["overall_hit_rate"] == 1.0
        assert "metrics" in saved_summary
        assert saved_summary["metrics"]["total_duration_ms"] == 400
        assert saved_summary["metrics"]["avg_duration_ms"] == 200
        assert saved_summary["per_scenario"][0]["metrics"]["total_duration_ms"] == 200

    def test_scenario_id_filtering(self):
        from unittest.mock import patch
        with patch(
            "tools.benchmark.scripts.simulate_semantic_search.call_llm",
            side_effect=self._mock_llm,
        ):
            summary = simulate_all(
                str(self.scenarios_path),
                self.tmpdir,
                "index content",
                self.output_dir,
                scenario_ids=["s-01"],
            )

        assert summary["total_scenarios"] == 1
        assert summary["per_scenario"][0]["id"] == "s-01"
        assert not (Path(self.output_dir) / "s-02").exists()

    def test_empty_run_summary(self):
        from unittest.mock import patch
        with patch(
            "tools.benchmark.scripts.simulate_semantic_search.call_llm",
            side_effect=self._mock_llm,
        ):
            summary = simulate_all(
                str(self.scenarios_path),
                self.tmpdir,
                "index content",
                self.output_dir,
                scenario_ids=["nonexistent"],
            )

        assert summary["total_scenarios"] == 0
        assert summary["overall_hit_rate"] == 1.0
        assert summary["per_scenario"] == []
