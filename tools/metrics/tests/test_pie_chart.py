"""Tests for _pie_chart() color consistency in SLOC section."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collect import _pie_chart, PROMPTS_COLOR, render_sloc_section


class TestPieChartWithoutColors:
    def test_no_init_block(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)])
        assert "%%{init" not in result

    def test_zero_value_excluded(self):
        result = _pie_chart("My Chart", [("A", 0), ("B", 20)])
        assert '"A"' not in result
        assert '"B" : 20' in result


class TestPieChartWithColors:
    def test_theme_base_in_init_block(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#111111", "B": "#222222"})
        assert "%%{init:" in result
        assert "'theme': 'base'" in result

    def test_color_assigned_by_size_descending(self):
        # B(20) is larger → pie1; A(10) is smaller → pie2
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#aaaaaa", "B": "#bbbbbb"})
        assert "'pie1': '#bbbbbb'" in result
        assert "'pie2': '#aaaaaa'" in result

    def test_label_order_does_not_affect_color_rank(self):
        # Define A first, but B is larger → B still gets pie1
        result_ab = _pie_chart("Chart", [("A", 5), ("B", 100)],
                               colors={"A": "#aaaaaa", "B": "#bbbbbb"})
        result_ba = _pie_chart("Chart", [("B", 100), ("A", 5)],
                               colors={"A": "#aaaaaa", "B": "#bbbbbb"})
        assert "'pie1': '#bbbbbb'" in result_ab
        assert "'pie1': '#bbbbbb'" in result_ba

    def test_unlisted_label_excluded_from_init(self):
        # Only A has a color; B does not → only pie2 entry emitted (A is smaller)
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#aaaaaa"})
        assert "'pie2': '#aaaaaa'" in result
        assert "'pie1'" not in result

    def test_no_match_produces_no_init_block(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"Z": "#ff0000"})
        assert "%%{init" not in result


class TestSlocChartsPromtsColor:
    """render_sloc_section passes PROMPTS_COLOR to both SLOC pie charts."""

    def _make_current(self, ns, np, kp, kt, kpr):
        return {
            "nabledge": {"scripts": {"dummy": ns}, "prompts": np},
            "kc": {"scripts_prod": {"dummy": kp}, "scripts_test": {"dummy": kt}, "prompts": kpr},
        }

    def test_prompts_color_present_in_both_charts(self):
        current = self._make_current(ns=951, np=1010, kp=4347, kt=5736, kpr=509)
        lines = render_sloc_section(current, {}, [])
        charts = [l for l in lines if "pie title" in l]
        assert len(charts) == 2, "Expected exactly 2 pie charts"
        assert PROMPTS_COLOR in charts[0], "PROMPTS_COLOR missing from v6 chart"
        assert PROMPTS_COLOR in charts[1], "PROMPTS_COLOR missing from KC chart"
