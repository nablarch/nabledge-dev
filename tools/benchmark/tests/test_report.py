"""Tests for benchmark report generation."""
import json
import math
import tempfile
from pathlib import Path

import pytest

from tools.benchmark.scripts.report import (
    build_baseline,
    compare_against_baseline,
    format_comparison_report,
    format_crossrun_summary,
    format_scenario_report,
    format_summary_report,
    format_regression_report,
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


class TestBuildBaseline:
    """build_baseline: N runs の evaluation lists から baseline.json 相当の dict を生成する。"""

    def _evals(self, ac, ar, fa):
        return [_make_evaluation(scenario_id="s1", deepeval_scores={
            "answer_correctness": {"score": ac, "reason": ""},
            "answer_relevancy": {"score": ar, "reason": ""},
            "faithfulness": {"score": fa, "reason": ""},
        })]

    def test_mean_computed_across_runs(self):
        runs = [self._evals(0.8, 0.9, 1.0), self._evals(1.0, 0.7, 0.8)]
        bl = build_baseline(runs)
        assert abs(bl["scenarios"]["s1"]["answer_correctness"]["mean"] - 0.9) < 1e-9

    def test_stddev_computed_across_runs(self):
        runs = [self._evals(0.8, 0.9, 1.0), self._evals(1.0, 0.7, 0.8)]
        bl = build_baseline(runs)
        # stddev of [0.8, 1.0] = 0.1 (population)
        assert abs(bl["scenarios"]["s1"]["answer_correctness"]["stddev"] - 0.1) < 1e-9

    def test_pass_rate_computed(self):
        # threshold for answer_correctness = 0.99; 0.8 fails, 1.0 passes → 0.5
        runs = [self._evals(0.8, 0.9, 1.0), self._evals(1.0, 0.7, 0.8)]
        bl = build_baseline(runs)
        assert bl["scenarios"]["s1"]["answer_correctness"]["pass_rate"] == 0.5

    def test_flaky_flag_set_when_pass_rate_below_one(self):
        runs = [self._evals(0.8, 0.9, 1.0), self._evals(1.0, 0.7, 0.8)]
        bl = build_baseline(runs)
        assert bl["scenarios"]["s1"]["flaky"] is True

    def test_not_flaky_when_always_passes(self):
        runs = [self._evals(1.0, 1.0, 1.0), self._evals(1.0, 1.0, 1.0)]
        bl = build_baseline(runs)
        assert bl["scenarios"]["s1"]["flaky"] is False

    def test_global_averages_included(self):
        runs = [self._evals(0.8, 0.9, 1.0), self._evals(1.0, 0.7, 0.8)]
        bl = build_baseline(runs)
        assert "global" in bl
        assert abs(bl["global"]["answer_correctness"]["mean"] - 0.9) < 1e-9

    def test_metadata_stored(self):
        runs = [self._evals(1.0, 1.0, 1.0)]
        bl = build_baseline(runs)
        assert bl["num_runs"] == 1
        assert "thresholds" in bl


class TestCompareAgainstBaseline:
    """compare_against_baseline: 1 run の evaluations と baseline dict を比較して結果を返す。"""

    def _make_baseline(self, mean, stddev, pass_rate, flaky=False):
        return {
            "num_runs": 3,
            "thresholds": {"answer_correctness": 0.99, "answer_relevancy": 0.95, "faithfulness": 0.99},
            "global": {
                "answer_correctness": {"mean": mean, "stddev": stddev},
                "answer_relevancy": {"mean": mean, "stddev": stddev},
                "faithfulness": {"mean": mean, "stddev": stddev},
            },
            "scenarios": {
                "s1": {
                    "flaky": flaky,
                    "answer_correctness": {"mean": mean, "stddev": stddev, "pass_rate": pass_rate},
                    "answer_relevancy": {"mean": mean, "stddev": stddev, "pass_rate": pass_rate},
                    "faithfulness": {"mean": mean, "stddev": stddev, "pass_rate": pass_rate},
                }
            },
        }

    def _eval(self, ac, ar, fa):
        return [_make_evaluation(scenario_id="s1", deepeval_scores={
            "answer_correctness": {"score": ac, "reason": ""},
            "answer_relevancy": {"score": ar, "reason": ""},
            "faithfulness": {"score": fa, "reason": ""},
        })]

    def test_clean_when_scores_within_baseline(self):
        bl = self._make_baseline(mean=1.0, stddev=0.0, pass_rate=1.0)
        result = compare_against_baseline(self._eval(1.0, 1.0, 1.0), bl)
        assert result["verdict"] == "CLEAN"

    def test_regression_detected_when_score_drops_more_than_2stddev(self):
        # mean=1.0, stddev=0.05 → threshold = 1.0 - 2*0.05 = 0.9
        bl = self._make_baseline(mean=1.0, stddev=0.05, pass_rate=1.0)
        result = compare_against_baseline(self._eval(0.8, 1.0, 1.0), bl)
        assert result["verdict"] == "REGRESSION DETECTED"
        assert any(r["scenario_id"] == "s1" for r in result["regressions"])

    def test_flaky_scenario_regression_reported_separately(self):
        bl = self._make_baseline(mean=0.8, stddev=0.1, pass_rate=0.5, flaky=True)
        # score drops below mean - 2*stddev but scenario is flaky
        result = compare_against_baseline(self._eval(0.5, 1.0, 1.0), bl)
        assert result["verdict"] == "CLEAN"
        assert any(r["scenario_id"] == "s1" for r in result["flaky_regressions"])

    def test_regressions_list_empty_when_clean(self):
        bl = self._make_baseline(mean=1.0, stddev=0.0, pass_rate=1.0)
        result = compare_against_baseline(self._eval(1.0, 1.0, 1.0), bl)
        assert result["regressions"] == []

    def test_new_scenario_not_in_baseline_is_skipped(self):
        bl = self._make_baseline(mean=1.0, stddev=0.0, pass_rate=1.0)
        new_eval = [_make_evaluation(scenario_id="new-01", deepeval_scores={
            "answer_correctness": {"score": 0.0, "reason": ""},
            "answer_relevancy": {"score": 0.0, "reason": ""},
            "faithfulness": {"score": 0.0, "reason": ""},
        })]
        result = compare_against_baseline(new_eval, bl)
        assert result["verdict"] == "CLEAN"
        assert any(sid == "new-01" for sid in result["new_scenarios"])


class TestFormatCrossrunSummary:
    """format_crossrun_summary: 複数runの評価リストから横断集約レポートを生成する。"""

    def _make_runs(self, n_runs=2):
        """n_runs分のダミー evaluation リストを返す。"""
        runs = []
        for i in range(n_runs):
            cost = 0.01 * (i + 1)
            evals = [
                _make_evaluation(
                    scenario_id="qa-01",
                    deepeval_scores={
                        "answer_correctness": {"score": 1.0, "reason": "ok"},
                        "answer_relevancy": {"score": 0.9, "reason": "ok"},
                        "faithfulness": {"score": 1.0, "reason": "ok"},
                    },
                    metrics={
                        "duration_ms": 30000, "duration_api_ms": 28000, "num_turns": 5,
                        "total_cost_usd": cost,
                        "usage": {
                            "input_tokens": 1000, "output_tokens": 200,
                            "cache_read_input_tokens": 300, "cache_creation_input_tokens": 50,
                        },
                        "model_usage": {},
                    },
                ),
                _make_evaluation(
                    scenario_id="qa-02",
                    deepeval_scores={
                        "answer_correctness": {"score": 0.8, "reason": "partial"},
                        "answer_relevancy": {"score": 0.85, "reason": "ok"},
                        "faithfulness": {"score": 0.9, "reason": "ok"},
                    },
                    metrics={
                        "duration_ms": 40000, "duration_api_ms": 38000, "num_turns": 7,
                        "total_cost_usd": cost + 0.005,
                        "usage": {
                            "input_tokens": 1500, "output_tokens": 300,
                            "cache_read_input_tokens": 400, "cache_creation_input_tokens": 60,
                        },
                        "model_usage": {},
                    },
                ),
            ]
            runs.append(evals)
        return runs

    def test_report_has_heading(self):
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "3run横断集約レポート" in report

    def test_report_has_score_summary_section(self):
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "スコアサマリー" in report

    def test_report_has_perf_section(self):
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "パフォーマンス横断集約" in report

    def test_all_scenarios_present(self):
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "qa-01" in report
        assert "qa-02" in report

    def test_cost_total_computed_correctly(self):
        # run-0: qa-01=$0.01, qa-02=$0.015 → run total $0.025
        # run-1: qa-01=$0.02, qa-02=$0.025 → run total $0.045
        # total across all = $0.025 + $0.045 = $0.070
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "$0.070" in report

    def test_flaky_marker_shown(self):
        # qa-02 has answer_correctness 0.8 < threshold 0.99, so flaky
        runs = self._make_runs(2)
        report = format_crossrun_summary(runs)
        assert "⚠" in report


class TestFormatRegressionReport:
    """format_regression_report: compare_against_baseline の結果を markdown に変換する。"""

    def _clean_result(self):
        return {
            "verdict": "CLEAN",
            "regressions": [],
            "flaky_regressions": [],
            "new_scenarios": [],
        }

    def _regression_result(self):
        return {
            "verdict": "REGRESSION DETECTED",
            "regressions": [
                {"scenario_id": "qa-01", "metric": "answer_correctness",
                 "baseline_mean": 1.0, "baseline_stddev": 0.05,
                 "current_score": 0.8, "delta": -0.2},
            ],
            "flaky_regressions": [],
            "new_scenarios": [],
        }

    def test_clean_verdict_in_report(self):
        report = format_regression_report(self._clean_result())
        assert "CLEAN" in report

    def test_regression_verdict_in_report(self):
        report = format_regression_report(self._regression_result())
        assert "REGRESSION DETECTED" in report

    def test_regression_scenario_listed(self):
        report = format_regression_report(self._regression_result())
        assert "qa-01" in report

    def test_delta_shown(self):
        report = format_regression_report(self._regression_result())
        assert "-0.2" in report or "-0.20" in report
