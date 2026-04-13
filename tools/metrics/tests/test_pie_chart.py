"""Tests for _pie_chart() color consistency in SLOC section."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collect import _pie_chart, PROMPTS_COLOR, render_sloc_section
import re


class TestPieChartWithoutColors:
    def test_no_init_block(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)])
        assert "%%{init" not in result

    def test_basic_output(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)])
        assert result.startswith("```mermaid\npie title My Chart\n")
        assert '"A" : 10' in result
        assert '"B" : 20' in result

    def test_zero_value_excluded(self):
        result = _pie_chart("My Chart", [("A", 0), ("B", 20)])
        assert '"A"' not in result
        assert '"B" : 20' in result


class TestPieChartWithColors:
    def test_init_block_present(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#111111", "B": "#222222"})
        assert "%%{init:" in result

    def test_theme_base_present(self):
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#111111", "B": "#222222"})
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

    def test_labels_without_color_mapping_excluded_from_init(self):
        # Only A has a color; B does not
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"A": "#aaaaaa"})
        assert "'pie2': '#aaaaaa'" in result  # A(10) is smaller → pie2
        assert "'pie1'" not in result          # B has no color entry

    def test_no_match_produces_no_init_block(self):
        # colors dict has no key matching any active slice label
        result = _pie_chart("My Chart", [("A", 10), ("B", 20)],
                            colors={"Z": "#ff0000"})
        assert "%%{init" not in result


class TestPromtsColorConsistency:
    """Verify both SLOC pie charts assign the same color to Prompts (.md)."""

    def _extract_pie_colors(self, chart: str) -> dict[str, str]:
        """Extract {'pie1': '#hex', 'pie2': '#hex', ...} from %%{init}%% block."""
        m = re.search(r"%%\{init:.*?themeVariables.*?\{(.*?)\}", chart)
        if not m:
            return {}
        pairs = re.findall(r"'(pie\d+)':\s*'(#[0-9a-fA-F]+)'", m.group(1))
        return dict(pairs)

    def _find_prompts_pie_rank(self, chart: str) -> str | None:
        """Return the pie# key assigned to Prompts (.md) based on size-descending rank."""
        # Extract slice values from chart body (after the init line)
        slices = re.findall(r'"(.+?)"\s*:\s*(\d+)', chart)
        if not slices:
            return None
        ranked = sorted(slices, key=lambda x: int(x[1]), reverse=True)
        for i, (label, _) in enumerate(ranked):
            if label == "Prompts (.md)":
                return f"pie{i + 1}"
        return None

    def _make_sloc_current(self, ns, np, kp, kt, kpr):
        return {
            "nabledge": {"scripts": {"dummy": ns}, "prompts": np},
            "kc": {"scripts_prod": {"dummy": kp}, "scripts_test": {"dummy": kt}, "prompts": kpr},
        }

    def test_prompts_color_same_in_both_charts(self):
        current = self._make_sloc_current(ns=951, np=1010, kp=4347, kt=5736, kpr=509)
        lines = render_sloc_section(current, {}, [])
        charts = [l for l in lines if "pie title" in l]
        assert len(charts) == 2, "Expected exactly 2 pie charts"

        v6_chart = charts[0]
        kc_chart = charts[1]

        v6_colors = self._extract_pie_colors(v6_chart)
        kc_colors = self._extract_pie_colors(kc_chart)

        v6_rank = self._find_prompts_pie_rank(v6_chart)
        kc_rank = self._find_prompts_pie_rank(kc_chart)

        assert v6_rank is not None, "Prompts (.md) not found in v6 chart"
        assert kc_rank is not None, "Prompts (.md) not found in KC chart"

        v6_prompts_color = v6_colors.get(v6_rank)
        kc_prompts_color = kc_colors.get(kc_rank)

        assert v6_prompts_color == PROMPTS_COLOR, \
            f"v6 Prompts color {v6_prompts_color!r} != PROMPTS_COLOR {PROMPTS_COLOR!r}"
        assert kc_prompts_color == PROMPTS_COLOR, \
            f"KC Prompts color {kc_prompts_color!r} != PROMPTS_COLOR {PROMPTS_COLOR!r}"
