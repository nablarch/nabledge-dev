"""Benchmark report generation: per-scenario and aggregate reports."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def format_scenario_report(evaluation: dict) -> str:
    """Generate markdown report for a single scenario evaluation."""
    sid = evaluation["scenario_id"]
    desc = evaluation.get("description", "")
    input_text = evaluation.get("input", "")
    claims = evaluation.get("claim_verdicts", [])
    hallucination = evaluation.get("hallucination", {})
    scores = evaluation.get("scores", {})
    diagnostics = evaluation.get("diagnostics", {})
    metrics = evaluation.get("metrics", {})
    needs_review = evaluation.get("needs_human_review", False)

    accuracy = scores.get("accuracy")
    h_score = scores.get("hallucination")

    accuracy_display = f"{accuracy:.2f}" if accuracy is not None else "N/A"
    h_display = str(h_score) if h_score is not None else "N/A"

    present_count = sum(1 for c in claims if c["verdict"] == "PRESENT")
    uncertain_count = sum(1 for c in claims if c["verdict"] == "UNCERTAIN")
    absent_count = sum(1 for c in claims if c["verdict"] == "ABSENT")

    accuracy_auto = []
    if present_count:
        accuracy_auto.append(f"{present_count} PRESENT")
    if absent_count:
        accuracy_auto.append(f"{absent_count} ABSENT")
    if uncertain_count:
        accuracy_auto.append(f"{uncertain_count} UNCERTAIN")
    accuracy_auto_str = ", ".join(accuracy_auto) if accuracy_auto else "N/A"

    accuracy_review = "要レビュー" if (uncertain_count or absent_count) else "-"
    h_review = "要レビュー" if hallucination.get("verdict") in ("FAIL", "UNCERTAIN") else "-"

    def _fmt_score(v):
        return f"{v:.2f}" if v is not None else "N/A"

    ac_display = _fmt_score(scores.get("answer_correctness"))
    ar_display = _fmt_score(scores.get("answer_relevancy"))
    fa_display = _fmt_score(scores.get("faithfulness"))
    has_deepeval = any(k in scores for k in ("answer_correctness", "answer_relevancy", "faithfulness"))

    lines = [
        f"## {sid}: {desc}",
        "",
        f"**入力**: {input_text}",
        "",
        "### 評価結果",
        "",
        "| 軸 | 自動判定 | 人間判定 | スコア |",
        "|---|---|---|---|",
        f"| 回答精度 | {accuracy_auto_str} | {accuracy_review} | {accuracy_display} |",
        f"| ハルシネーション | {hallucination.get('verdict', 'N/A')} | {h_review} | {h_display} |",
    ]

    if has_deepeval:
        lines.extend([
            f"| answer_correctness (DeepEval) | — | — | {ac_display} |",
            f"| answer_relevancy (DeepEval) | — | — | {ar_display} |",
            f"| faithfulness (DeepEval) | — | — | {fa_display} |",
        ])

    lines.append("")

    if claims:
        lines.extend([
            "### 回答精度詳細",
            "",
            "| # | fact | 判定 | 理由 |",
            "|---|------|------|------|",
        ])
        for i, c in enumerate(claims):
            verdict_str = c["verdict"]
            if verdict_str in ("UNCERTAIN", "ABSENT"):
                verdict_str = f"{verdict_str} **要レビュー**"
            lines.append(f"| {i + 1} | {c['fact']} | {verdict_str} | {c.get('reason', '')} |")
        lines.append("")

    hearing = diagnostics.get("hearing", {})
    search_sections = diagnostics.get("search_sections", [])
    hearing_str = hearing.get("status", "N/A")
    if hearing.get("questions"):
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

    accuracy_scores = []
    accuracy_uncertain = 0
    h_scores = []
    h_uncertain = 0

    for ev in evaluations:
        scores = ev.get("scores", {})
        a = scores.get("accuracy")
        h = scores.get("hallucination")

        if a is not None:
            if ev.get("needs_human_review", False):
                accuracy_uncertain += 1
            else:
                accuracy_scores.append(a)
        # N/A accuracy scenarios are excluded entirely

        if h is not None:
            h_scores.append(h)
        else:
            h_uncertain += 1

    total_with_accuracy = len([
        ev for ev in evaluations if ev.get("scores", {}).get("accuracy") is not None
    ])
    total_h = len(evaluations)

    acc_confirmed = len(accuracy_scores)
    acc_avg = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
    acc_min = min(accuracy_scores) if accuracy_scores else 0
    acc_pass = sum(1 for s in accuracy_scores if s == 1.0)

    h_confirmed = len(h_scores)
    h_avg = sum(h_scores) / len(h_scores) if h_scores else 0
    h_min = min(h_scores) if h_scores else 0
    h_pass = sum(1 for s in h_scores if s == 1)

    lines = [
        "## サマリー",
        "",
        "| 軸 | 対象件数 | 確定件数 | 未確定 | 平均スコア | 最低スコア | 全PASS率 |",
        "|---|---|---|---|---|---|---|",
    ]

    if total_with_accuracy > 0:
        lines.append(
            f"| 回答精度 | {total_with_accuracy} | {acc_confirmed} | {accuracy_uncertain} "
            f"| {acc_avg:.2f} | {acc_min:.2f} | {acc_pass}/{acc_confirmed} |"
        )
    else:
        lines.append("| 回答精度 | 0 | 0 | 0 | N/A | N/A | N/A |")

    lines.append(
        f"| ハルシネーション | {total_h} | {h_confirmed} | {h_uncertain} "
        f"| {h_avg:.2f} | {h_min} | {h_pass}/{h_confirmed} |"
    )

    lines.extend([
        "",
        "※ 未確定 = 人間レビュー未完了（UNCERTAIN含む）。平均・PASS率は確定分のみで計算。",
        "",
    ])

    deepeval_keys = ("answer_correctness", "answer_relevancy", "faithfulness")
    deepeval_avgs = {}
    for key in deepeval_keys:
        vals = [
            ev["scores"][key]
            for ev in evaluations
            if ev.get("scores", {}).get(key) is not None
        ]
        deepeval_avgs[key] = sum(vals) / len(vals) if vals else None

    if any(v is not None for v in deepeval_avgs.values()):
        def _dfmt(v):
            return f"{v:.2f}" if v is not None else "N/A"
        lines.extend([
            "## DeepEval メトリクスサマリー",
            "",
            "| 指標 | 平均スコア |",
            "|---|---|",
            f"| answer_correctness | {_dfmt(deepeval_avgs['answer_correctness'])} |",
            f"| answer_relevancy | {_dfmt(deepeval_avgs['answer_relevancy'])} |",
            f"| faithfulness | {_dfmt(deepeval_avgs['faithfulness'])} |",
            "",
        ])

    all_metrics = [ev.get("metrics", {}) for ev in evaluations]

    def _stats(vals: list) -> tuple:
        if not vals:
            return None, None, None, None, None
        s = sorted(vals)
        return sum(s) / len(s), s[len(s) // 2], s[int(len(s) * 0.95)], max(s), sum(s)

    durations    = [m["duration_ms"] for m in all_metrics if m.get("duration_ms")]
    api_durations = [m["duration_api_ms"] for m in all_metrics if m.get("duration_api_ms")]
    num_turns_list = [m["num_turns"] for m in all_metrics if m.get("num_turns")]
    costs        = [m["total_cost_usd"] for m in all_metrics if m.get("total_cost_usd")]
    in_tokens    = [m.get("usage", {}).get("input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("input_tokens")]
    out_tokens   = [m.get("usage", {}).get("output_tokens", 0) for m in all_metrics if m.get("usage", {}).get("output_tokens")]
    cache_read   = [m.get("usage", {}).get("cache_read_input_tokens", 0) for m in all_metrics if m.get("usage", {}).get("cache_read_input_tokens")]

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
    return "\n".join([
        "## サマリー",
        "",
        "| 軸 | 対象件数 | 確定件数 | 未確定 | 平均スコア | 最低スコア | 全PASS率 |",
        "|---|---|---|---|---|---|---|",
        "| 回答精度 | 0 | 0 | 0 | N/A | N/A | N/A |",
        "| ハルシネーション | 0 | 0 | 0 | N/A | N/A | N/A |",
        "",
    ])


def format_human_review_list(evaluations: list[dict]) -> str:
    """Generate list of items needing human review."""
    review_scenarios = [
        ev for ev in evaluations if ev.get("needs_human_review", False)
    ]
    if not review_scenarios:
        return "人間レビュー対象: なし\n"

    lines = ["## 人間レビュー対象", ""]
    for ev in review_scenarios:
        sid = ev["scenario_id"]
        items = ev.get("human_review_items", [])
        lines.append(f"### {sid}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def generate_full_report(evaluations: list[dict]) -> str:
    """Generate complete benchmark report."""
    parts = [format_summary_report(evaluations), ""]

    review_list = format_human_review_list(evaluations)
    parts.extend([review_list, ""])

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
    """Generate comparison report between two run labels (design spec: 比較レポート)."""

    def _avg_accuracy(evals: list[dict]) -> float | None:
        scores = [ev["scores"]["accuracy"] for ev in evals if ev.get("scores", {}).get("accuracy") is not None]
        return sum(scores) / len(scores) if scores else None

    def _hallucination_pass(evals: list[dict]) -> tuple[int, int]:
        scores = [ev["scores"]["hallucination"] for ev in evals if ev.get("scores", {}).get("hallucination") is not None]
        return sum(1 for s in scores if s == 1), len(scores)

    def _avg_metric(evals: list[dict], key: str) -> float | None:
        vals = [ev.get("metrics", {}).get(key) for ev in evals if ev.get("metrics", {}).get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    def _avg_nested(evals: list[dict], outer: str, inner: str) -> float | None:
        vals = [ev.get("metrics", {}).get(outer, {}).get(inner) for ev in evals]
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    def _diff(a, b):
        if a is None or b is None:
            return "N/A"
        d = b - a
        return f"{d:+.2f}" if isinstance(d, float) else f"{d:+}"

    def _fmt(v, fmt=".2f"):
        return f"{v:{fmt}}" if v is not None else "N/A"

    acc_a, acc_b = _avg_accuracy(evals_a), _avg_accuracy(evals_b)
    hp_a, ht_a = _hallucination_pass(evals_a)
    hp_b, ht_b = _hallucination_pass(evals_b)

    dur_a = _avg_metric(evals_a, "duration_ms")
    dur_b = _avg_metric(evals_b, "duration_ms")
    cost_a = _avg_metric(evals_a, "total_cost_usd")
    cost_b = _avg_metric(evals_b, "total_cost_usd")
    turns_a = _avg_metric(evals_a, "num_turns")
    turns_b = _avg_metric(evals_b, "num_turns")

    def _pct_change(a, b):
        if a is None or b is None or a == 0:
            return "N/A"
        return f"{(b - a) / a * 100:+.0f}%"

    def _avg_deepeval(evals: list[dict], key: str) -> float | None:
        vals = [
            ev.get("scores", {}).get(key)
            for ev in evals
            if ev.get("scores", {}).get(key) is not None
        ]
        return sum(vals) / len(vals) if vals else None

    deepeval_keys = ("answer_correctness", "answer_relevancy", "faithfulness")
    deepeval_a = {k: _avg_deepeval(evals_a, k) for k in deepeval_keys}
    deepeval_b = {k: _avg_deepeval(evals_b, k) for k in deepeval_keys}
    has_deepeval = any(v is not None for v in {**deepeval_a, **deepeval_b}.values())

    lines = [
        f"# ベンチマーク比較: {label_a} vs {label_b}",
        "",
        "## 品質比較",
        "",
        f"| 軸 | {label_a} | {label_b} | 差分 |",
        "|---|---|---|---|",
        f"| 回答精度（平均） | {_fmt(acc_a)} | {_fmt(acc_b)} | {_diff(acc_a, acc_b)} |",
        f"| ハルシネーション（PASS率） | {hp_a}/{ht_a} | {hp_b}/{ht_b} | {hp_b - hp_a:+} |",
    ]

    if has_deepeval:
        for k in deepeval_keys:
            da, db = deepeval_a[k], deepeval_b[k]
            lines.append(f"| {k} (DeepEval) | {_fmt(da)} | {_fmt(db)} | {_diff(da, db)} |")

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

    # シナリオ別差分: accuracy scoreが変化したシナリオ
    map_a = {ev["scenario_id"]: ev for ev in evals_a}
    map_b = {ev["scenario_id"]: ev for ev in evals_b}
    common_ids = sorted(set(map_a) & set(map_b))

    changed = []
    for sid in common_ids:
        sa = map_a[sid].get("scores", {}).get("accuracy")
        sb = map_b[sid].get("scores", {}).get("accuracy")
        if sa != sb:
            changed.append((sid, sa, sb))

    if changed:
        lines.extend([
            "## シナリオ別差分（精度スコアが変化したシナリオ）",
            "",
            f"| シナリオ | {label_a} | {label_b} | 差分 |",
            "|---|---|---|---|",
        ])
        for sid, sa, sb in changed:
            lines.append(f"| {sid} | {_fmt(sa)} | {_fmt(sb)} | {_diff(sa, sb)} |")
        lines.append("")
    else:
        lines.extend(["## シナリオ別差分", "", "精度スコアの変化なし", ""])

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
