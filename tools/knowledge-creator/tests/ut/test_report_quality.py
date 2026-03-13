"""Test quality evaluation section in reports."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


class TestQualityReportSection:

    def test_render_includes_quality_section(self):
        from run import _render_summary_md, Context
        ctx = Context.__new__(Context)
        ctx.run_id = "test"
        ctx.max_rounds = 2
        report = {
            "meta": {"run_id": "test", "version": "6", "phases": "BCDEMV",
                     "max_rounds": 2, "concurrency": 4, "test_mode": False,
                     "started_at": "2026-01-01T00:00:00Z",
                     "finished_at": "2026-01-01T01:00:00Z",
                     "duration_sec": 3600},
            "phase_d_rounds": [], "phase_e_rounds": [],
            "final_verification": {
                "round": 3,
                "phase_c": {"total": 10, "pass": 10, "fail": 0},
                "phase_d": {"total": 10, "clean": 8, "has_issues": 2,
                            "findings": {"total": 3, "critical": 1, "minor": 2,
                                         "by_category": {"omission": 1, "hints_missing": 2}}},
            },
            "quality_evaluation": {
                "fact_data": {"summary": {"rounds": {
                    1: {"total": 10, "critical": 5, "minor": 5, "by_category": {"omission": 5, "hints_missing": 5}},
                    2: {"total": 6, "critical": 2, "minor": 4, "by_category": {"omission": 2, "hints_missing": 4}},
                    3: {"total": 3, "critical": 1, "minor": 2, "by_category": {"omission": 1, "hints_missing": 2}},
                }, "final": {"total": 3}}},
                "proposals": {"proposals": [{
                    "title": "Fix missing warnings", "purpose": "Prevent wrong implementation",
                    "target_files": ["handler-a"], "user_impact": "Critical", "body": "Details"}]},
            },
        }
        md = _render_summary_md(ctx, report, [])
        assert "品質評価" in md
        assert "改善提案" in md
        assert "omission" in md

    def test_render_without_quality_evaluation(self):
        from run import _render_summary_md, Context
        ctx = Context.__new__(Context)
        ctx.run_id = "test"
        ctx.max_rounds = 2
        report = {
            "meta": {"run_id": "test", "version": "6", "phases": "BCD",
                     "max_rounds": 2, "concurrency": 4, "test_mode": False,
                     "started_at": "2026-01-01T00:00:00Z",
                     "finished_at": "2026-01-01T01:00:00Z",
                     "duration_sec": 3600},
            "phase_d_rounds": [], "phase_e_rounds": [],
        }
        md = _render_summary_md(ctx, report, [])
        assert "品質評価" not in md
