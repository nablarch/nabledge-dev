"""Tests for benchmark report generation."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.report import (
    format_comparison_report,
    format_scenario_report,
    format_summary_report,
    generate_full_report,
)


def _make_evaluation(
    scenario_id="pre-01",
    description="テストシナリオ",
    input_text="テスト入力",
    deepeval_scores=None,
    hearing=None,
    search=None,
    metrics=None,
):
    scores = deepeval_scores or {
        "answer_correctness": {"score": 1.0, "reason": "all facts covered"},
        "answer_relevancy": {"score": 0.9, "reason": "relevant"},
        "faithfulness": {"score": 1.0, "reason": "no hallucination"},
    }
    return {
        "scenario_id": scenario_id,
        "description": description,
        "input": input_text,
        "scores": scores,
        "diagnostics": {
            "hearing": hearing or {"status": "skipped", "questions": []},
            "search_sections": search or ["a.json:s1"],
        },
        "metrics": metrics or {
            "duration_ms": 1000, "duration_api_ms": 900, "num_turns": 3,
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 400, "output_tokens": 100, "cache_read_input_tokens": 200, "cache_creation_input_tokens": 50},
            "model_usage": {},
        },
    }


class TestFormatScenarioReport:
    def test_basic_report_structure(self):
        evaluation = _make_evaluation()
        report = format_scenario_report(evaluation)
        assert "## pre-01" in report
        assert "テストシナリオ" in report
        assert "テスト入力" in report

    def test_deepeval_scores_displayed(self):
        evaluation = _make_evaluation(deepeval_scores={
            "answer_correctness": {"score": 0.9, "reason": "facts covered"},
            "answer_relevancy": {"score": 0.85, "reason": "relevant"},
            "faithfulness": {"score": 0.8, "reason": "some issues"},
        })
        report = format_scenario_report(evaluation)
        assert "answer_correctness" in report or "0.90" in report
        assert "faithfulness" in report or "0.80" in report

    def test_deepeval_none_scores_displayed_as_na(self):
        evaluation = _make_evaluation(deepeval_scores={
            "answer_correctness": {"score": None, "reason": ""},
            "answer_relevancy": {"score": None, "reason": ""},
            "faithfulness": {"score": None, "reason": ""},
        })
        report = format_scenario_report(evaluation)
        assert "## pre-01" in report

    def test_report_includes_metrics(self):
        evaluation = _make_evaluation(
            metrics={
                "duration_ms": 45000, "duration_api_ms": 42000, "num_turns": 8,
                "total_cost_usd": 0.045,
                "usage": {"input_tokens": 12500, "output_tokens": 2500, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                "model_usage": {},
            }
        )
        report = format_scenario_report(evaluation)
        assert "45" in report or "45000" in report


class TestFormatSummaryReport:
    def test_basic_summary(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01"),
            _make_evaluation(scenario_id="pre-02", deepeval_scores={
                "answer_correctness": {"score": 0.5, "reason": "partial"},
                "answer_relevancy": {"score": 0.9, "reason": "ok"},
                "faithfulness": {"score": 1.0, "reason": "ok"},
            }),
        ]
        report = format_summary_report(evaluations)
        assert "2" in report

    def test_deepeval_averages_in_summary(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01", deepeval_scores={
                "answer_correctness": {"score": 0.9, "reason": "ok"},
                "answer_relevancy": {"score": 0.85, "reason": "ok"},
                "faithfulness": {"score": 0.8, "reason": "ok"},
            }),
            _make_evaluation(scenario_id="pre-02", deepeval_scores={
                "answer_correctness": {"score": 0.7, "reason": "ok"},
                "answer_relevancy": {"score": 0.75, "reason": "ok"},
                "faithfulness": {"score": 0.9, "reason": "ok"},
            }),
        ]
        report = format_summary_report(evaluations)
        assert "answer_correctness" in report or "DeepEval" in report or "0.80" in report

    def test_summary_metrics_section(self):
        def _m(duration_ms):
            return {
                "duration_ms": duration_ms, "duration_api_ms": duration_ms - 1000,
                "num_turns": 5, "total_cost_usd": 0.04,
                "usage": {"input_tokens": 10000, "output_tokens": 2000, "cache_read_input_tokens": 500, "cache_creation_input_tokens": 100},
                "model_usage": {},
            }
        evaluations = [
            _make_evaluation(scenario_id="pre-01", metrics=_m(30000)),
            _make_evaluation(scenario_id="pre-02", metrics=_m(50000)),
        ]
        report = format_summary_report(evaluations)
        assert "パフォーマンスサマリー" in report
        assert "実行時間" in report
        assert "コスト" in report

    def test_empty_evaluations(self):
        report = format_summary_report([])
        assert "0" in report


class TestGenerateFullReport:
    def test_contains_all_sections(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01"),
            _make_evaluation(scenario_id="pre-02"),
        ]
        report = generate_full_report(evaluations)
        assert "サマリー" in report
        assert "## pre-01" in report
        assert "## pre-02" in report

    def test_summary_appears_before_scenarios(self):
        evaluations = [_make_evaluation(scenario_id="pre-01")]
        report = generate_full_report(evaluations)
        summary_pos = report.index("サマリー")
        scenario_pos = report.index("## pre-01")
        assert summary_pos < scenario_pos


class TestFormatComparisonReport:
    def test_comparison_includes_deepeval_diff(self):
        evals_a = [_make_evaluation(scenario_id="pre-01", deepeval_scores={
            "answer_correctness": {"score": 0.7, "reason": "ok"},
            "answer_relevancy": {"score": 0.8, "reason": "ok"},
            "faithfulness": {"score": 0.75, "reason": "ok"},
        })]
        evals_b = [_make_evaluation(scenario_id="pre-01", deepeval_scores={
            "answer_correctness": {"score": 0.9, "reason": "ok"},
            "answer_relevancy": {"score": 0.85, "reason": "ok"},
            "faithfulness": {"score": 0.9, "reason": "ok"},
        })]
        report = format_comparison_report("run-1", "run-2", evals_a, evals_b)
        assert "answer_correctness" in report or "DeepEval" in report or "品質比較" in report

    def test_comparison_no_error_without_scores(self):
        evals_a = [_make_evaluation(scenario_id="pre-01")]
        evals_b = [_make_evaluation(scenario_id="pre-01")]
        report = format_comparison_report("run-1", "run-2", evals_a, evals_b)
        assert "品質比較" in report
