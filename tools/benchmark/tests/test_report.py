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
        "metrics": metrics or {"duration_ms": 1000, "total_tokens": 500, "tool_uses": 3},
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
            metrics={"duration_ms": 45000, "total_tokens": 15000, "tool_uses": 8}
        )
        report = format_scenario_report(evaluation)
        assert "45" in report or "45000" in report
        assert "15" in report or "15000" in report


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
        evaluations = [
            _make_evaluation(
                scenario_id="pre-01",
                metrics={"duration_ms": 30000, "total_tokens": 10000, "tool_uses": 5},
            ),
            _make_evaluation(
                scenario_id="pre-02",
                metrics={"duration_ms": 50000, "total_tokens": 20000, "tool_uses": 10},
            ),
        ]
        report = format_summary_report(evaluations)
        assert "メトリクスサマリー" in report
        assert "実行時間" in report
        assert "トークン量" in report

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
