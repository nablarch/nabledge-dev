"""Tests for benchmark report generation."""
import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.report import (
    format_human_review_list,
    format_scenario_report,
    format_summary_report,
    generate_full_report,
)


def _make_evaluation(
    scenario_id="pre-01",
    description="テストシナリオ",
    input_text="テスト入力",
    claim_verdicts=None,
    hallucination=None,
    accuracy=1.0,
    hallucination_score=1,
    needs_review=False,
    review_items=None,
    hearing=None,
    search=None,
    metrics=None,
):
    return {
        "scenario_id": scenario_id,
        "description": description,
        "input": input_text,
        "claim_verdicts": claim_verdicts or [{"fact": "fact1", "verdict": "PRESENT", "reason": "ok"}],
        "hallucination": hallucination or {"verdict": "PASS", "claims": [], "reason": "ok"},
        "scores": {"accuracy": accuracy, "hallucination": hallucination_score},
        "needs_human_review": needs_review,
        "human_review_items": review_items or [],
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
        assert "PRESENT" in report

    def test_report_with_review_items(self):
        evaluation = _make_evaluation(
            claim_verdicts=[
                {"fact": "f1", "verdict": "PRESENT", "reason": "ok"},
                {"fact": "f2", "verdict": "UNCERTAIN", "reason": "unclear"},
            ],
            accuracy=0.5,
            needs_review=True,
            review_items=["claim[1]: UNCERTAIN — f2"],
        )
        report = format_scenario_report(evaluation)
        assert "UNCERTAIN" in report
        assert "要レビュー" in report

    def test_report_with_none_accuracy(self):
        evaluation = _make_evaluation(accuracy=None, claim_verdicts=[])
        report = format_scenario_report(evaluation)
        assert "N/A" in report

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
            _make_evaluation(scenario_id="pre-01", accuracy=1.0, hallucination_score=1),
            _make_evaluation(scenario_id="pre-02", accuracy=0.5, hallucination_score=1),
        ]
        report = format_summary_report(evaluations)
        assert "回答精度" in report
        assert "ハルシネーション" in report
        assert "2" in report  # 対象件数

    def test_summary_with_uncertain(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01", accuracy=1.0, hallucination_score=1),
            _make_evaluation(
                scenario_id="pre-02", accuracy=0.5, hallucination_score=None,
                needs_review=True,
            ),
        ]
        report = format_summary_report(evaluations)
        assert "未確定" in report

    def test_summary_with_none_accuracy(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01", accuracy=None, hallucination_score=1),
        ]
        report = format_summary_report(evaluations)
        assert "| 回答精度 | 0 | 0 | 0 | N/A | N/A | N/A |" in report

    def test_absent_only_scenario_counted_as_unconfirmed(self):
        evaluations = [
            _make_evaluation(
                scenario_id="pre-01",
                claim_verdicts=[{"fact": "f1", "verdict": "ABSENT", "reason": "not found"}],
                accuracy=0.0,
                needs_review=True,
                review_items=["claim[0]: ABSENT — f1"],
            ),
        ]
        report = format_summary_report(evaluations)
        assert "| 回答精度 | 1 | 0 | 1" in report

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


class TestFormatHumanReviewList:
    def test_no_reviews_needed(self):
        evaluations = [_make_evaluation()]
        report = format_human_review_list(evaluations)
        assert "なし" in report or report.strip() == ""

    def test_reviews_needed(self):
        evaluations = [
            _make_evaluation(
                scenario_id="pre-01",
                needs_review=True,
                review_items=["claim[0]: ABSENT — fact1"],
            ),
        ]
        report = format_human_review_list(evaluations)
        assert "pre-01" in report
        assert "ABSENT" in report

    def test_multiple_scenarios_need_review(self):
        evaluations = [
            _make_evaluation(
                scenario_id="pre-01",
                needs_review=True,
                review_items=["claim[0]: UNCERTAIN — f1"],
            ),
            _make_evaluation(scenario_id="pre-02"),
            _make_evaluation(
                scenario_id="pre-03",
                needs_review=True,
                review_items=["hallucination: FAIL — fake claim"],
            ),
        ]
        report = format_human_review_list(evaluations)
        assert "pre-01" in report
        assert "pre-03" in report
        assert "pre-02" not in report


class TestGenerateFullReport:
    def test_contains_all_sections(self):
        evaluations = [
            _make_evaluation(scenario_id="pre-01"),
            _make_evaluation(
                scenario_id="pre-02",
                needs_review=True,
                review_items=["claim[0]: ABSENT — f1"],
            ),
        ]
        report = generate_full_report(evaluations)
        assert "サマリー" in report
        assert "人間レビュー対象" in report
        assert "## pre-01" in report
        assert "## pre-02" in report

    def test_summary_appears_before_scenarios(self):
        evaluations = [_make_evaluation(scenario_id="pre-01")]
        report = generate_full_report(evaluations)
        summary_pos = report.index("サマリー")
        scenario_pos = report.index("## pre-01")
        assert summary_pos < scenario_pos
