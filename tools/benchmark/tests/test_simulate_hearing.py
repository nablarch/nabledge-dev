"""Tests for hearing simulation."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.simulate_hearing import (
    _aggregate_metrics,
    build_classify_prompt,
    build_extract_prompt,
    compare_classification,
    compare_processing_type,
    expected_classification,
    extract_processing_types,
    format_processing_types,
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


SAMPLE_INDEX = """# Knowledge Index

## component/libraries

### ユニバーサルDAO
path: component/libraries/libraries-universal-dao.json
- s2: SQLを書かなくても単純なCRUDができる

## processing-pattern/web-application

### ウェブアプリケーション
path: processing-pattern/web-application/web-application-architecture.json
- s1: アーキテクチャ概要

## processing-pattern/restful-web-service

### RESTfulウェブサービス
path: processing-pattern/restful-web-service/restful-web-service-architecture.json
- s1: アーキテクチャ概要

## processing-pattern/nablarch-batch

### Nablarchバッチ
path: processing-pattern/nablarch-batch/nablarch-batch-architecture.json
- s1: アーキテクチャ概要

## development-tools/testing-framework

### テスティングフレームワーク
path: development-tools/testing-framework/testing-framework-01-Abstract.json
- s1: 概要
"""


class TestExtractProcessingTypes:
    def test_extracts_from_processing_pattern_categories(self):
        types = extract_processing_types(SAMPLE_INDEX)
        assert types == ["ウェブアプリケーション", "RESTfulウェブサービス", "Nablarchバッチ"]

    def test_excludes_non_processing_pattern(self):
        types = extract_processing_types(SAMPLE_INDEX)
        assert "ユニバーサルDAO" not in types
        assert "テスティングフレームワーク" not in types

    def test_empty_index(self):
        assert extract_processing_types("# Knowledge Index\n") == []

    def test_no_processing_pattern_section(self):
        index = "# Knowledge Index\n\n## component/libraries\n\n### DAO\npath: x.json\n"
        assert extract_processing_types(index) == []


class TestFormatProcessingTypes:
    def test_formats_list(self):
        result = format_processing_types(["Web", "REST API"])
        assert result == "- Web\n- REST API"

    def test_empty_list(self):
        assert format_processing_types([]) == "（なし）"


class TestBuildClassifyPrompt:
    def test_substitutes_placeholders(self):
        prompt = build_classify_prompt("テストの質問", "- Web\n- REST API")
        assert "テストの質問" in prompt
        assert "- Web" in prompt
        assert "- REST API" in prompt
        assert "{question}" not in prompt
        assert "{processing_types}" not in prompt

    def test_contains_procedure_steps(self):
        prompt = build_classify_prompt("Q", "- Web")
        assert "手順" in prompt
        assert "skip" in prompt
        assert "ask" in prompt


class TestBuildExtractPrompt:
    def test_substitutes_placeholders(self):
        prompt = build_extract_prompt("テストの質問", "Web")
        assert "テストの質問" in prompt
        assert "Web" in prompt
        assert "{question}" not in prompt
        assert "{user_response}" not in prompt

    def test_contains_goal_constraints(self):
        prompt = build_extract_prompt("Q", "Web")
        assert "動詞句" in prompt


class TestExpectedClassification:
    def test_should_skip(self):
        assert expected_classification("should_skip") == "skip"

    def test_must_ask(self):
        assert expected_classification("must_ask") == "ask"

    def test_nice_to_ask(self):
        assert expected_classification("nice_to_ask") == "ask"


class TestCompareClassification:
    def test_should_skip_skip_pass(self):
        result = compare_classification("skip", "should_skip")
        assert result["result"] == "PASS"

    def test_should_skip_ask_pass_with_note(self):
        result = compare_classification("ask", "should_skip")
        assert result["result"] == "PASS"
        assert "note" in result

    def test_must_ask_ask_pass(self):
        result = compare_classification("ask", "must_ask")
        assert result["result"] == "PASS"

    def test_must_ask_skip_fail(self):
        result = compare_classification("skip", "must_ask")
        assert result["result"] == "FAIL"

    def test_nice_to_ask_ask_pass(self):
        result = compare_classification("ask", "nice_to_ask")
        assert result["result"] == "PASS"

    def test_nice_to_ask_skip_pass_with_note(self):
        result = compare_classification("skip", "nice_to_ask")
        assert result["result"] == "PASS"
        assert "note" in result


class TestCompareProcessingType:
    def test_match(self):
        result = compare_processing_type("Web", "Web")
        assert result["result"] == "MATCH"

    def test_mismatch(self):
        result = compare_processing_type("Web", "REST API")
        assert result["result"] == "MISMATCH"
        assert result["actual"] == "Web"
        assert result["expected"] == "REST API"

    def test_both_none(self):
        result = compare_processing_type(None, None)
        assert result["result"] == "MATCH"

    def test_actual_none(self):
        result = compare_processing_type(None, "Web")
        assert result["result"] == "MISMATCH"


class TestAggregateMetrics:
    def test_combines_classify_and_extract(self):
        c = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        e = {"duration_ms": 200, "total_cost_usd": 0.02, "usage": {"input_tokens": 1000, "output_tokens": 100}}
        result = _aggregate_metrics(c, e)
        assert result["total_duration_ms"] == 300
        assert result["total_cost_usd"] == 0.03
        assert result["total_input_tokens"] == 1500
        assert result["total_output_tokens"] == 150

    def test_classify_only(self):
        c = {"duration_ms": 100, "total_cost_usd": 0.01, "usage": {"input_tokens": 500, "output_tokens": 50}}
        result = _aggregate_metrics(c, {})
        assert result["total_duration_ms"] == 100
        assert result["total_cost_usd"] == 0.01

    def test_both_empty(self):
        assert _aggregate_metrics({}, {}) == {}


class TestSimulateScenario:
    def test_skip_classification(self):
        scenario = {
            "id": "test-01",
            "when": {
                "input": "REST APIでJSONを受け取る方法",
                "expected_hearing": "should_skip",
                "hearing_answer": {
                    "processing_type": "REST API",
                    "goal": "JSONを受け取ってDBに登録する",
                },
            },
        }

        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "skip",
                "hearing_answer": {
                    "processing_type": "REST API",
                    "goal": "JSONを受け取ってDBに登録する",
                },
                "trace": {"reason": "REST APIが明示", "matched_keywords": ["REST API"]},
            })

        result = simulate_scenario(scenario, "- Web\n- REST API", llm_fn=mock_llm)
        assert result["scenario_id"] == "test-01"
        assert result["classify"]["classification"] == "skip"
        assert result["comparison"]["classification"]["result"] == "PASS"
        assert result["comparison"]["processing_type"]["result"] == "MATCH"
        assert result["extract"] is None
        assert result["final_hearing_answer"]["processing_type"] == "REST API"

    def test_ask_classification_with_extraction(self):
        scenario = {
            "id": "test-02",
            "when": {
                "input": "入力チェックの実装方法",
                "expected_hearing": "must_ask",
                "hearing_answer": {
                    "processing_type": "Web",
                    "goal": "入力画面のフォームでバリデーションする",
                },
            },
        }
        call_count = 0

        def mock_llm(prompt, schema, model="sonnet"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _wrap_llm_response({
                    "classification": "ask",
                    "hearing_answer": None,
                    "trace": {"reason": "処理方式が不明", "matched_keywords": []},
                })
            return _wrap_llm_response({
                "hearing_answer": {
                    "processing_type": "Web",
                    "goal": "入力画面のフォームでバリデーションする",
                },
                "trace": {
                    "user_intent": "入力チェックの実装方法を知りたい",
                    "goal_derivation": "Webの文脈で入力画面のバリデーションに具体化",
                },
            })

        result = simulate_scenario(scenario, "- Web\n- REST API", llm_fn=mock_llm)
        assert result["classify"]["classification"] == "ask"
        assert result["extract"] is not None
        assert result["extract"]["hearing_answer"]["processing_type"] == "Web"
        assert result["comparison"]["classification"]["result"] == "PASS"
        assert result["comparison"]["processing_type"]["result"] == "MATCH"
        assert call_count == 2

    def test_must_ask_classified_as_skip_fails(self):
        scenario = {
            "id": "test-03",
            "when": {
                "input": "入力チェックの実装方法",
                "expected_hearing": "must_ask",
                "hearing_answer": {
                    "processing_type": "Web",
                    "goal": "バリデーションする",
                },
            },
        }

        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "skip",
                "hearing_answer": {
                    "processing_type": "Web",
                    "goal": "バリデーションする",
                },
                "trace": {"reason": "推測", "matched_keywords": []},
            })

        result = simulate_scenario(scenario, "- Web", llm_fn=mock_llm)
        assert result["comparison"]["classification"]["result"] == "FAIL"

    def test_cross_cutting_skip_with_null_pt(self):
        scenario = {
            "id": "test-04",
            "when": {
                "input": "多言語化の方法を教えてほしい",
                "expected_hearing": "should_skip",
            },
        }

        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "skip",
                "hearing_answer": {
                    "processing_type": None,
                    "goal": "メッセージやラベルを多言語化する",
                },
                "trace": {"reason": "横断的機能", "matched_keywords": []},
            })

        result = simulate_scenario(scenario, "- Web", llm_fn=mock_llm)
        assert result["comparison"]["classification"]["result"] == "PASS"
        assert result["comparison"]["processing_type"]["result"] == "MATCH"
        assert result["final_hearing_answer"]["processing_type"] is None

    def test_ask_without_ground_truth_warns(self, capsys):
        scenario = {
            "id": "test-warn",
            "when": {
                "input": "入力チェックの方法",
                "expected_hearing": "must_ask",
            },
        }

        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "ask",
                "hearing_answer": None,
                "trace": {"reason": "不明", "matched_keywords": []},
            })

        result = simulate_scenario(scenario, "- Web", llm_fn=mock_llm)
        assert result["final_hearing_answer"] is None
        assert result["extract"] is None
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        assert "test-warn" in captured.err

    def test_nice_to_ask_classified_as_skip_passes(self):
        scenario = {
            "id": "test-05",
            "when": {
                "input": "大量データの検索方法",
                "expected_hearing": "nice_to_ask",
                "hearing_answer": {
                    "processing_type": "Nablarchバッチ",
                    "goal": "10万件のレコードを処理する",
                },
            },
        }

        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "skip",
                "hearing_answer": {
                    "processing_type": "Nablarchバッチ",
                    "goal": "大量データを検索する",
                },
                "trace": {"reason": "大量データはバッチ処理が一般的", "matched_keywords": []},
            })

        result = simulate_scenario(scenario, "- Nablarchバッチ", llm_fn=mock_llm)
        assert result["comparison"]["classification"]["result"] == "PASS"


class TestSimulateAll:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.scenarios = {
            "scenarios": [
                {
                    "id": "s1",
                    "when": {
                        "input": "REST APIの実装",
                        "expected_hearing": "should_skip",
                        "hearing_answer": {
                            "processing_type": "REST API",
                            "goal": "REST APIを実装する",
                        },
                    },
                },
                {
                    "id": "s2",
                    "when": {
                        "input": "入力チェック",
                        "expected_hearing": "must_ask",
                        "hearing_answer": {
                            "processing_type": "Web",
                            "goal": "バリデーションする",
                        },
                    },
                },
            ],
        }
        self.scenarios_path = Path(self.tmpdir) / "scenarios.json"
        self.scenarios_path.write_text(
            json.dumps(self.scenarios, ensure_ascii=False), encoding="utf-8"
        )

    def test_produces_summary(self):
        call_count = 0

        def mock_llm(prompt, schema, model="sonnet"):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _wrap_llm_response({
                    "classification": "skip",
                    "hearing_answer": {"processing_type": "REST API", "goal": "実装する"},
                    "trace": {"reason": "明示", "matched_keywords": ["REST API"]},
                })
            if call_count == 2:
                return _wrap_llm_response({
                    "classification": "ask",
                    "hearing_answer": None,
                    "trace": {"reason": "不明", "matched_keywords": []},
                })
            return _wrap_llm_response({
                "hearing_answer": {"processing_type": "Web", "goal": "バリデーション"},
                "trace": {"user_intent": "入力チェック", "goal_derivation": "Web化"},
            })

        from unittest.mock import patch
        with patch(
            "tools.benchmark.scripts.simulate_hearing.call_llm", side_effect=mock_llm
        ):
            summary = simulate_all(
                str(self.scenarios_path),
                SAMPLE_INDEX,
                self.tmpdir + "/out",
            )

        assert summary["total_scenarios"] == 2
        assert summary["classification_pass"] == 2
        assert summary["processing_type_match"] == 2

    def test_scenario_id_filter(self):
        def mock_llm(prompt, schema, model="sonnet"):
            return _wrap_llm_response({
                "classification": "skip",
                "hearing_answer": {"processing_type": "REST API", "goal": "実装する"},
                "trace": {"reason": "明示", "matched_keywords": ["REST API"]},
            })

        from unittest.mock import patch
        with patch(
            "tools.benchmark.scripts.simulate_hearing.call_llm", side_effect=mock_llm
        ):
            summary = simulate_all(
                str(self.scenarios_path),
                SAMPLE_INDEX,
                self.tmpdir + "/out2",
                scenario_ids=["s1"],
            )

        assert summary["total_scenarios"] == 1
        assert summary["per_scenario"][0]["id"] == "s1"
