"""Benchmark report generation: per-scenario and aggregate reports."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_DEEPEVAL_KEYS = ("answer_correctness", "answer_relevancy", "faithfulness")
_DEEPEVAL_THRESHOLDS = {
    "answer_correctness": 0.99,
    "answer_relevancy": 0.95,
    "faithfulness": 0.99,
}


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


def _perf_stats(vals: list) -> tuple:
    """Return (avg, p50, p95, max, sum) for a list of numeric values."""
    if not vals:
        return None, None, None, None, None
    s = sorted(vals)
    return sum(s) / len(s), s[len(s) // 2], s[int(len(s) * 0.95)], max(s), sum(s)


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
        threshold_pass[key] = sum(1 for v in vals if v >= _DEEPEVAL_THRESHOLDS[key])

    lines = [
        "## サマリー",
        "",
        f"総シナリオ数: {total}",
        "",
        "### DeepEval メトリクスサマリー",
        "",
        "| 指標 | 平均スコア | 閾値通過 |",
        "|---|---|---|",
    ]

    for key in _DEEPEVAL_KEYS:
        avg = avgs[key]
        pass_count = threshold_pass[key]
        thr = _DEEPEVAL_THRESHOLDS[key]
        lines.append(f"| {key} | {_fmt(avg)} | {pass_count}/{total}（≥{thr}） |")

    lines.append("")

    all_metrics = [ev.get("metrics", {}) for ev in evaluations]

    durations     = [m["duration_ms"] for m in all_metrics if m.get("duration_ms")]
    api_durations = [m["duration_api_ms"] for m in all_metrics if m.get("duration_api_ms")]
    num_turns_list = [m["num_turns"] for m in all_metrics if m.get("num_turns")]
    costs         = [m["total_cost_usd"] for m in all_metrics if m.get("total_cost_usd")]
    in_tokens     = [m.get("usage", {}).get("input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("input_tokens")]
    out_tokens    = [m.get("usage", {}).get("output_tokens", 0) for m in all_metrics if m.get("usage", {}).get("output_tokens")]
    cache_read    = [m.get("usage", {}).get("cache_read_input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("cache_read_input_tokens")]

    if durations:
        d_avg, d_p50, d_p95, d_max, _ = _perf_stats([v / 1000 for v in durations])
        da_avg, da_p50, da_p95, da_max, _ = _perf_stats([v / 1000 for v in api_durations]) if api_durations else (None,)*5
        t_avg, t_p50, t_p95, t_max, _ = _perf_stats(num_turns_list) if num_turns_list else (None,)*5
        c_avg, c_p50, c_p95, c_max, c_sum = _perf_stats(costs) if costs else (None,)*5
        in_avg, in_p50, in_p95, in_max, _ = _perf_stats(in_tokens) if in_tokens else (None,)*5
        out_avg, out_p50, out_p95, out_max, _ = _perf_stats(out_tokens) if out_tokens else (None,)*5
        cr_avg, cr_p50, cr_p95, cr_max, _ = _perf_stats(cache_read) if cache_read else (None,)*5

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
        "| 指標 | 平均スコア | 閾値通過 |",
        "|---|---|---|",
    ]
    for key in _DEEPEVAL_KEYS:
        thr = _DEEPEVAL_THRESHOLDS[key]
        lines.append(f"| {key} | N/A | 0/0（≥{thr}） |")
    lines.append("")
    return "\n".join(lines)


def generate_full_report(evaluations: list[dict]) -> str:
    """Generate complete benchmark report."""
    parts = [format_summary_report(evaluations), ""]

    for ev in evaluations:
        parts.append(format_scenario_report(ev))

    return "\n".join(parts)


def format_crossrun_summary(runs: list[list[dict]]) -> str:
    """Generate cross-run aggregate report from N run evaluation lists."""
    baseline = build_baseline(runs)
    global_stats = baseline["global"]
    scenarios = baseline["scenarios"]

    all_evals = [ev for run in runs for ev in run]
    total_scenarios = len(scenarios)

    def _fmt(v, fmt=".3f"):
        return f"{v:{fmt}}" if v is not None else "N/A"

    lines = [
        "# 3run横断集約レポート",
        "",
        f"run数: {len(runs)} / シナリオ数: {total_scenarios}",
        "",
        "## スコアサマリー（3run × 全シナリオ）",
        "",
        "| 指標 | 平均 | 閾値通過率 |",
        "|---|---|---|",
    ]

    for key in _DEEPEVAL_KEYS:
        g = global_stats.get(key, {})
        mean = g.get("mean")
        thr = _DEEPEVAL_THRESHOLDS[key]
        pass_count = sum(
            1 for ev in all_evals
            if (_score_value(ev.get("scores", {}), key) or 0) >= thr
        )
        total_evals = sum(
            1 for ev in all_evals
            if _score_value(ev.get("scores", {}), key) is not None
        )
        lines.append(f"| {key} | {_fmt(mean)} | {pass_count}/{total_evals} |")

    lines.extend([
        "",
        "## シナリオ別 3run集約",
        "",
        "| scenario | corr mean±sd | rel mean±sd | faith mean±sd | flaky |",
        "|---|---|---|---|---|",
    ])

    for sid in sorted(scenarios):
        sc = scenarios[sid]
        flaky_mark = "⚠️" if sc.get("flaky") else ""

        def _ms(key):
            m = sc.get(key, {})
            mv, sv = m.get("mean"), m.get("stddev")
            if mv is None:
                return "N/A"
            return f"{mv:.3f}±{sv:.3f}"

        lines.append(
            f"| {sid} | {_ms('answer_correctness')} | {_ms('answer_relevancy')} "
            f"| {_ms('faithfulness')} | {flaky_mark} |"
        )

    lines.append("")

    all_metrics = [ev.get("metrics", {}) for ev in all_evals]
    durations    = [m["duration_ms"] for m in all_metrics if m.get("duration_ms")]
    num_turns_list = [m["num_turns"] for m in all_metrics if m.get("num_turns")]
    costs        = [m["total_cost_usd"] for m in all_metrics if m.get("total_cost_usd")]
    cache_create = [
        m.get("usage", {}).get("cache_creation_input_tokens", 0)
        for m in all_metrics if m.get("usage", {}).get("cache_creation_input_tokens")
    ]
    cache_read   = [
        m.get("usage", {}).get("cache_read_input_tokens", 0)
        for m in all_metrics if m.get("usage", {}).get("cache_read_input_tokens")
    ]

    def _fmt_s(v): return f"{v:.0f}s" if v is not None else "N/A"
    def _fmt_n(v): return f"{v:,.0f}" if v is not None else "N/A"
    def _fmt_c(v): return f"${v:.3f}" if v is not None else "N/A"

    d_avg, d_p50, d_p95, d_max, _ = _perf_stats([v / 1000 for v in durations]) if durations else (None,)*5
    t_avg, t_p50, t_p95, t_max, _ = _perf_stats(num_turns_list) if num_turns_list else (None,)*5
    c_avg, c_p50, c_p95, c_max, c_sum = _perf_stats(costs) if costs else (None,)*5
    cc_avg, cc_p50, cc_p95, cc_max, _ = _perf_stats(cache_create) if cache_create else (None,)*5
    cr_avg, cr_p50, cr_p95, cr_max, _ = _perf_stats(cache_read) if cache_read else (None,)*5

    lines.extend([
        "## パフォーマンス横断集約（3run × 全シナリオ）",
        "",
        "| メトリクス | 平均 | P50 | P95 | 最大 | 合計 |",
        "|---|---|---|---|---|---|",
        f"| 実行時間 | {_fmt_s(d_avg)} | {_fmt_s(d_p50)} | {_fmt_s(d_p95)} | {_fmt_s(d_max)} | — |",
        f"| コスト | {_fmt_c(c_avg)} | {_fmt_c(c_p50)} | {_fmt_c(c_p95)} | {_fmt_c(c_max)} | {_fmt_c(c_sum)} |",
        f"| ターン数 | {_fmt_n(t_avg)} | {_fmt_n(t_p50)} | {_fmt_n(t_p95)} | {_fmt_n(t_max)} | — |",
        f"| cache_creation | {_fmt_n(cc_avg)} | {_fmt_n(cc_p50)} | {_fmt_n(cc_p95)} | {_fmt_n(cc_max)} | — |",
        f"| cache_read | {_fmt_n(cr_avg)} | {_fmt_n(cr_p50)} | {_fmt_n(cr_p95)} | {_fmt_n(cr_max)} | — |",
        "",
        "> 注: 平均はばらつきを隠すため、必ず P50・最大も確認すること。",
        "",
    ])

    return "\n".join(lines)


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


def build_baseline(runs: list[list[dict]]) -> dict:
    """Build a baseline dict from N run evaluation lists.

    Returns a dict with per-scenario and global stats (mean, stddev, pass_rate)
    and a flaky flag per scenario (flaky=True when any metric pass_rate < 1.0).
    """
    scenario_ids: set[str] = set()
    for evals in runs:
        for ev in evals:
            scenario_ids.add(ev["scenario_id"])

    scenarios: dict[str, dict] = {}
    for sid in scenario_ids:
        entry: dict = {}
        any_flaky = False
        for key in _DEEPEVAL_KEYS:
            scores_per_run = []
            for evals in runs:
                ev = next((e for e in evals if e["scenario_id"] == sid), None)
                if ev is None:
                    continue
                v = _score_value(ev.get("scores", {}), key)
                if v is not None:
                    scores_per_run.append(v)
            n = len(scores_per_run)
            if n == 0:
                entry[key] = {"mean": None, "stddev": None, "pass_rate": None}
                continue
            mean = sum(scores_per_run) / n
            variance = sum((x - mean) ** 2 for x in scores_per_run) / n
            stddev = math.sqrt(variance)
            pass_rate = sum(1 for v in scores_per_run if v >= _DEEPEVAL_THRESHOLDS[key]) / n
            entry[key] = {"mean": mean, "stddev": stddev, "pass_rate": pass_rate}
            if pass_rate < 1.0:
                any_flaky = True
        entry["flaky"] = any_flaky
        scenarios[sid] = entry

    # global averages across all scenarios and all runs
    global_stats: dict[str, dict] = {}
    for key in _DEEPEVAL_KEYS:
        all_scores = []
        for evals in runs:
            for ev in evals:
                v = _score_value(ev.get("scores", {}), key)
                if v is not None:
                    all_scores.append(v)
        n = len(all_scores)
        if n == 0:
            global_stats[key] = {"mean": None, "stddev": None}
        else:
            mean = sum(all_scores) / n
            variance = sum((x - mean) ** 2 for x in all_scores) / n
            global_stats[key] = {"mean": mean, "stddev": math.sqrt(variance)}

    return {
        "num_runs": len(runs),
        "thresholds": dict(_DEEPEVAL_THRESHOLDS),
        "global": global_stats,
        "scenarios": scenarios,
    }


def compare_against_baseline(evaluations: list[dict], baseline: dict) -> dict:
    """Compare a single run's evaluations against a baseline dict.

    Returns a result dict with:
      verdict: "CLEAN" or "REGRESSION DETECTED"
      regressions: list of regression dicts (non-flaky scenarios only)
      flaky_regressions: regressions on flaky scenarios (informational)
      new_scenarios: scenario IDs present in run but absent from baseline
    """
    k_factor = 2.0  # flag when score < mean - k*stddev
    regressions = []
    flaky_regressions = []
    new_scenarios = []
    bl_scenarios = baseline.get("scenarios", {})

    for ev in evaluations:
        sid = ev["scenario_id"]
        if sid not in bl_scenarios:
            new_scenarios.append(sid)
            continue
        bl_sc = bl_scenarios[sid]
        is_flaky = bl_sc.get("flaky", False)
        for key in _DEEPEVAL_KEYS:
            bl_metric = bl_sc.get(key, {})
            bl_mean = bl_metric.get("mean")
            bl_std = bl_metric.get("stddev")
            if bl_mean is None:
                continue
            current = _score_value(ev.get("scores", {}), key)
            if current is None:
                continue
            threshold = bl_mean - k_factor * (bl_std or 0.0)
            if current < threshold:
                rec = {
                    "scenario_id": sid,
                    "metric": key,
                    "baseline_mean": bl_mean,
                    "baseline_stddev": bl_std,
                    "current_score": current,
                    "delta": current - bl_mean,
                }
                if is_flaky:
                    flaky_regressions.append(rec)
                else:
                    regressions.append(rec)

    verdict = "REGRESSION DETECTED" if regressions else "CLEAN"
    return {
        "verdict": verdict,
        "regressions": regressions,
        "flaky_regressions": flaky_regressions,
        "new_scenarios": new_scenarios,
    }


def format_regression_report(result: dict) -> str:
    """Render compare_against_baseline result as markdown."""
    verdict = result["verdict"]
    regressions = result.get("regressions", [])
    flaky_regressions = result.get("flaky_regressions", [])
    new_scenarios = result.get("new_scenarios", [])

    lines = [
        f"## 退行チェック結果: **{verdict}**",
        "",
    ]

    if regressions:
        lines.extend([
            "### 退行シナリオ（ベースライン平均 − 2σ を下回る）",
            "",
            "| シナリオ | 指標 | ベースライン平均 | 現在スコア | 差分 |",
            "|---|---|---|---|---|",
        ])
        for r in regressions:
            lines.append(
                f"| {r['scenario_id']} | {r['metric']} "
                f"| {r['baseline_mean']:.3f}±{r['baseline_stddev']:.3f} "
                f"| {r['current_score']:.3f} | {r['delta']:+.3f} |"
            )
        lines.append("")
    else:
        lines.extend(["退行なし（全シナリオがベースライン範囲内）", ""])

    if flaky_regressions:
        lines.extend([
            "### フラグ対象（Flaky シナリオ — 参考情報）",
            "",
            "| シナリオ | 指標 | ベースライン平均 | 現在スコア | 差分 |",
            "|---|---|---|---|---|",
        ])
        for r in flaky_regressions:
            lines.append(
                f"| {r['scenario_id']} | {r['metric']} "
                f"| {r['baseline_mean']:.3f}±{r['baseline_stddev']:.3f} "
                f"| {r['current_score']:.3f} | {r['delta']:+.3f} |"
            )
        lines.append("")

    if new_scenarios:
        lines.extend([
            "### 新規シナリオ（ベースライン未登録）",
            "",
            ", ".join(new_scenarios),
            "",
        ])

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate benchmark report")
    parser.add_argument("--run-dir", help="Path to benchmark run directory")
    parser.add_argument("--compare", help="Second run directory for comparison report")
    parser.add_argument("--label-a", help="Label for --run-dir (used in comparison)")
    parser.add_argument("--label-b", help="Label for --compare (used in comparison)")
    parser.add_argument(
        "--baseline-runs", nargs="+", metavar="RUN_DIR",
        help="Two or more run directories to build baseline.json from",
    )
    parser.add_argument(
        "--save-baseline", metavar="FILE",
        help="Path to save baseline.json (used with --baseline-runs)",
    )
    parser.add_argument(
        "--compare-baseline", metavar="FILE",
        help="Path to baseline.json for regression check (used with --run-dir)",
    )
    parser.add_argument(
        "--crossrun-dir", metavar="DIR",
        help="Directory containing run-* subdirs; generates crossrun-summary.md",
    )
    args = parser.parse_args()

    if args.crossrun_dir:
        crossrun_dir = Path(args.crossrun_dir)
        run_dirs = sorted(crossrun_dir.glob("run-*"))
        if len(run_dirs) < 2:
            print(f"Error: --crossrun-dir requires at least 2 run-* subdirectories, found {len(run_dirs)}", file=sys.stderr)
            sys.exit(1)
        runs = [_load_evaluations(d) for d in run_dirs]
        report = format_crossrun_summary(runs)
        report_path = crossrun_dir / "crossrun-summary.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"Cross-run summary written to {report_path}", file=sys.stderr)
        print(report)
        return

    if args.baseline_runs:
        # Build baseline.json from multiple run dirs
        runs = [_load_evaluations(Path(d)) for d in args.baseline_runs]
        baseline = build_baseline(runs)
        save_path = Path(args.save_baseline) if args.save_baseline else Path(args.baseline_runs[0]).parent / "baseline.json"
        save_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Baseline saved to {save_path}", file=sys.stderr)
        return

    if not args.run_dir:
        parser.error("--run-dir is required unless --baseline-runs is specified")

    run_dir = Path(args.run_dir)
    evaluations = _load_evaluations(run_dir)

    if args.compare_baseline:
        # Regression check against saved baseline
        baseline = json.loads(Path(args.compare_baseline).read_text(encoding="utf-8"))
        result = compare_against_baseline(evaluations, baseline)
        report = format_regression_report(result)
        report_path = run_dir / "regression-check.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"Regression report written to {report_path}", file=sys.stderr)
        print(report)
        if result["verdict"] == "REGRESSION DETECTED":
            sys.exit(1)
    elif args.compare:
        compare_dir = Path(args.compare)
        evals_b = _load_evaluations(compare_dir)
        label_a = args.label_a or run_dir.name
        label_b = args.label_b or compare_dir.name
        report = format_comparison_report(label_a, label_b, evaluations, evals_b)
        report_path = run_dir / f"comparison-{label_b}.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"Report written to {report_path}", file=sys.stderr)
        print(report)
    else:
        report = generate_full_report(evaluations)
        report_path = run_dir / "report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"Report written to {report_path}", file=sys.stderr)
        print(report)


if __name__ == "__main__":
    main()
