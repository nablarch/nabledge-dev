"""Benchmark report generation: per-scenario and aggregate reports."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_DEEPEVAL_KEYS = ("answer_correctness", "answer_relevancy", "faithfulness")


def _score_value(scores: dict, key: str) -> float | None:
    """Extract float score from scores dict. Handles {score, reason} or None."""
    entry = scores.get(key)
    if entry is None:
        return None
    if isinstance(entry, dict):
        return entry.get("score")
    return float(entry)


def _score_reason(scores: dict, key: str) -> str:
    """Extract reason string from scores dict."""
    entry = scores.get(key)
    if isinstance(entry, dict):
        return entry.get("reason") or ""
    return ""


def format_scenario_report(evaluation: dict) -> str:
    """Generate markdown report for a single scenario evaluation."""
    sid = evaluation["scenario_id"]
    desc = evaluation.get("description", "")
    input_text = evaluation.get("input", "")
    scores = evaluation.get("scores", {})
    diagnostics = evaluation.get("diagnostics", {})
    metrics = evaluation.get("metrics", {})

    def _fmt(v):
        return f"{v:.2f}" if v is not None else "N/A"

    lines = [
        f"## {sid}: {desc}",
        "",
        f"**入力**: {input_text}",
        "",
        "### DeepEval スコア",
        "",
        "| 指標 | スコア | 判定根拠 |",
        "|---|---|---|",
    ]

    for key in _DEEPEVAL_KEYS:
        score = _score_value(scores, key)
        reason = _score_reason(scores, key)
        lines.append(f"| {key} | {_fmt(score)} | {reason} |")

    lines.append("")

    search_sections = diagnostics.get("search_sections", [])
    hearing = diagnostics.get("hearing", {})
    hearing_str = hearing.get("status", "N/A") if hearing else "N/A"
    if hearing and hearing.get("questions"):
        hearing_str += " — " + ", ".join(hearing["questions"])

    lines.extend([
        "### 診断情報",
        "",
        f"- ヒアリング: {hearing_str}",
        f"- 検索セクション: {', '.join(search_sections) if search_sections else 'N/A'}",
        "",
    ])

    duration = metrics.get("duration_ms")
    tokens = metrics.get("total_tokens")
    tool_uses = metrics.get("tool_uses")
    duration_s = f"{duration / 1000:.0f}s" if duration is not None else "N/A"
    tokens_str = f"{tokens:,}" if tokens is not None else "N/A"
    tool_str = str(tool_uses) if tool_uses is not None else "N/A"

    lines.extend([
        "### メトリクス",
        "",
        "| 実行時間 | トークン量 | ツール呼び出し |",
        "|---|---|---|",
        f"| {duration_s} | {tokens_str} | {tool_str} |",
        "",
    ])

    return "\n".join(lines)


def format_summary_report(evaluations: list[dict]) -> str:
    """Generate aggregate summary report."""
    if not evaluations:
        return _empty_summary()

    total = len(evaluations)

    avgs = {}
    for key in _DEEPEVAL_KEYS:
        vals = [
            _score_value(ev.get("scores", {}), key)
            for ev in evaluations
        ]
        vals = [v for v in vals if v is not None]
        avgs[key] = sum(vals) / len(vals) if vals else None

    def _fmt(v):
        return f"{v:.2f}" if v is not None else "N/A"

    threshold_pass = {}
    for key in _DEEPEVAL_KEYS:
        vals = [
            _score_value(ev.get("scores", {}), key)
            for ev in evaluations
        ]
        vals = [v for v in vals if v is not None]
        threshold_pass[key] = sum(1 for v in vals if v >= 0.5)

    lines = [
        "## サマリー",
        "",
        f"総シナリオ数: {total}",
        "",
        "### DeepEval メトリクスサマリー",
        "",
        "| 指標 | 平均スコア | 閾値通過（≥0.5） |",
        "|---|---|---|",
    ]

    for key in _DEEPEVAL_KEYS:
        avg = avgs[key]
        pass_count = threshold_pass[key]
        lines.append(f"| {key} | {_fmt(avg)} | {pass_count}/{total} |")

    lines.append("")

    all_metrics = [ev.get("metrics", {}) for ev in evaluations]

    def _stats(vals: list) -> tuple:
        if not vals:
            return None, None, None, None, None
        s = sorted(vals)
        return sum(s) / len(s), s[len(s) // 2], s[int(len(s) * 0.95)], max(s), sum(s)

    durations     = [m["duration_ms"] for m in all_metrics if m.get("duration_ms")]
    api_durations = [m["duration_api_ms"] for m in all_metrics if m.get("duration_api_ms")]
    num_turns_list = [m["num_turns"] for m in all_metrics if m.get("num_turns")]
    costs         = [m["total_cost_usd"] for m in all_metrics if m.get("total_cost_usd")]
    in_tokens     = [m.get("usage", {}).get("input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("input_tokens")]
    out_tokens    = [m.get("usage", {}).get("output_tokens", 0) for m in all_metrics if m.get("usage", {}).get("output_tokens")]
    cache_read    = [m.get("usage", {}).get("cache_read_input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("cache_read_input_tokens")]

    if durations:
        d_avg, d_p50, d_p95, d_max, _ = _stats([v / 1000 for v in durations])
        da_avg, da_p50, da_p95, da_max, _ = _stats([v / 1000 for v in api_durations]) if api_durations else (None,)*5
        t_avg, t_p50, t_p95, t_max, _ = _stats(num_turns_list) if num_turns_list else (None,)*5
        c_avg, c_p50, c_p95, c_max, c_sum = _stats(costs) if costs else (None,)*5
        in_avg, in_p50, in_p95, in_max, _ = _stats(in_tokens) if in_tokens else (None,)*5
        out_avg, out_p50, out_p95, out_max, _ = _stats(out_tokens) if out_tokens else (None,)*5
        cr_avg, cr_p50, cr_p95, cr_max, _ = _stats(cache_read) if cache_read else (None,)*5

        def _fmt_s(v): return f"{v:.0f}s" if v is not None else "N/A"
        def _fmt_n(v): return f"{v:,.0f}" if v is not None else "N/A"
        def _fmt_c(v): return f"${v:.3f}" if v is not None else "N/A"

        lines.extend([
            "## パフォーマンスサマリー",
            "",
            "| メトリクス | 平均 | P50 | P95 | 最大 | 合計 |",
            "|---|---|---|---|---|---|",
            f"| 実行時間（総合） | {_fmt_s(d_avg)} | {_fmt_s(d_p50)} | {_fmt_s(d_p95)} | {_fmt_s(d_max)} | — |",
            f"| 実行時間（API） | {_fmt_s(da_avg)} | {_fmt_s(da_p50)} | {_fmt_s(da_p95)} | {_fmt_s(da_max)} | — |",
            f"| ターン数 | {_fmt_n(t_avg)} | {_fmt_n(t_p50)} | {_fmt_n(t_p95)} | {_fmt_n(t_max)} | — |",
            f"| 入力トークン | {_fmt_n(in_avg)} | {_fmt_n(in_p50)} | {_fmt_n(in_p95)} | {_fmt_n(in_max)} | — |",
            f"| 出力トークン | {_fmt_n(out_avg)} | {_fmt_n(out_p50)} | {_fmt_n(out_p95)} | {_fmt_n(out_max)} | — |",
            f"| キャッシュ読取 | {_fmt_n(cr_avg)} | {_fmt_n(cr_p50)} | {_fmt_n(cr_p95)} | {_fmt_n(cr_max)} | — |",
            f"| コスト | {_fmt_c(c_avg)} | {_fmt_c(c_p50)} | {_fmt_c(c_p95)} | {_fmt_c(c_max)} | {_fmt_c(c_sum)} |",
            "",
        ])

    return "\n".join(lines)


def _empty_summary() -> str:
    lines = [
        "## サマリー",
        "",
        "総シナリオ数: 0",
        "",
        "### DeepEval メトリクスサマリー",
        "",
        "| 指標 | 平均スコア | 閾値通過（≥0.5） |",
        "|---|---|---|",
    ]
    for key in _DEEPEVAL_KEYS:
        lines.append(f"| {key} | N/A | 0/0 |")
    lines.append("")
    return "\n".join(lines)


def generate_full_report(evaluations: list[dict]) -> str:
    """Generate complete benchmark report."""
    parts = [format_summary_report(evaluations), ""]

    for ev in evaluations:
        parts.append(format_scenario_report(ev))

    return "\n".join(parts)


def _load_evaluations(run_dir: Path) -> list[dict]:
    evaluations = []
    for eval_path in sorted(run_dir.glob("*/evaluation.json")):
        with open(eval_path, encoding="utf-8") as f:
            evaluations.append(json.load(f))
    return evaluations


def format_comparison_report(label_a: str, label_b: str, evals_a: list[dict], evals_b: list[dict]) -> str:
    """Generate comparison report between two run labels."""

    def _avg(evals: list[dict], key: str) -> float | None:
        vals = [
            _score_value(ev.get("scores", {}), key)
            for ev in evals
        ]
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    def _avg_metric(evals: list[dict], key: str) -> float | None:
        vals = [ev.get("metrics", {}).get(key) for ev in evals if ev.get("metrics", {}).get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    def _diff(a, b):
        if a is None or b is None:
            return "N/A"
        return f"{b - a:+.2f}"

    def _pct_change(a, b):
        if a is None or b is None or a == 0:
            return "N/A"
        return f"{(b - a) / a * 100:+.0f}%"

    def _fmt(v, fmt=".2f"):
        return f"{v:{fmt}}" if v is not None else "N/A"

    avgs_a = {k: _avg(evals_a, k) for k in _DEEPEVAL_KEYS}
    avgs_b = {k: _avg(evals_b, k) for k in _DEEPEVAL_KEYS}

    dur_a = _avg_metric(evals_a, "duration_ms")
    dur_b = _avg_metric(evals_b, "duration_ms")
    cost_a = _avg_metric(evals_a, "total_cost_usd")
    cost_b = _avg_metric(evals_b, "total_cost_usd")
    turns_a = _avg_metric(evals_a, "num_turns")
    turns_b = _avg_metric(evals_b, "num_turns")

    lines = [
        f"# ベンチマーク比較: {label_a} vs {label_b}",
        "",
        "## 品質比較",
        "",
        f"| 指標 | {label_a} | {label_b} | 差分 |",
        "|---|---|---|---|",
    ]

    for key in _DEEPEVAL_KEYS:
        a, b = avgs_a[key], avgs_b[key]
        lines.append(f"| {key} | {_fmt(a)} | {_fmt(b)} | {_diff(a, b)} |")

    lines.extend([
        "",
        "## パフォーマンス比較",
        "",
        f"| メトリクス | {label_a} 平均 | {label_b} 平均 | 変化率 |",
        "|---|---|---|---|",
        f"| 実行時間（総合） | {_fmt(dur_a / 1000 if dur_a else None, '.0f')}s | {_fmt(dur_b / 1000 if dur_b else None, '.0f')}s | {_pct_change(dur_a, dur_b)} |",
        f"| コスト | ${_fmt(cost_a, '.3f')} | ${_fmt(cost_b, '.3f')} | {_pct_change(cost_a, cost_b)} |",
        f"| ターン数 | {_fmt(turns_a, '.1f')} | {_fmt(turns_b, '.1f')} | {_pct_change(turns_a, turns_b)} |",
        "",
    ])

    map_a = {ev["scenario_id"]: ev for ev in evals_a}
    map_b = {ev["scenario_id"]: ev for ev in evals_b}
    common_ids = sorted(set(map_a) & set(map_b))

    changed = []
    for sid in common_ids:
        for key in _DEEPEVAL_KEYS:
            sa = _score_value(map_a[sid].get("scores", {}), key)
            sb = _score_value(map_b[sid].get("scores", {}), key)
            if sa is not None and sb is not None and abs(sb - sa) > 0.01:
                changed.append((sid, key, sa, sb))

    if changed:
        lines.extend([
            "## シナリオ別差分（スコアが変化したシナリオ）",
            "",
            f"| シナリオ | 指標 | {label_a} | {label_b} | 差分 |",
            "|---|---|---|---|---|",
        ])
        for sid, key, sa, sb in changed:
            lines.append(f"| {sid} | {key} | {_fmt(sa)} | {_fmt(sb)} | {_diff(sa, sb)} |")
        lines.append("")
    else:
        lines.extend(["## シナリオ別差分", "", "スコアの変化なし", ""])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate benchmark report")
    parser.add_argument("--run-dir", required=True, help="Path to benchmark run directory")
    parser.add_argument("--compare", help="Second run directory for comparison report")
    parser.add_argument("--label-a", help="Label for --run-dir (used in comparison)")
    parser.add_argument("--label-b", help="Label for --compare (used in comparison)")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    evaluations = _load_evaluations(run_dir)

    if args.compare:
        compare_dir = Path(args.compare)
        evals_b = _load_evaluations(compare_dir)
        label_a = args.label_a or run_dir.name
        label_b = args.label_b or compare_dir.name
        report = format_comparison_report(label_a, label_b, evaluations, evals_b)
        report_path = run_dir / f"comparison-{label_b}.md"
    else:
        report = generate_full_report(evaluations)
        report_path = run_dir / "report.md"

    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}", file=sys.stderr)
    print(report)


if __name__ == "__main__":
    main()
