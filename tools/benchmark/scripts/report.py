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
        "",
    ]

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

    all_metrics = [ev.get("metrics", {}) for ev in evaluations]
    durations = [m.get("duration_ms", 0) for m in all_metrics if m.get("duration_ms")]
    tokens = [m.get("total_tokens", 0) for m in all_metrics if m.get("total_tokens")]

    if durations:
        durations_sorted = sorted(durations)
        d_avg = sum(durations) / len(durations) / 1000
        d_p50 = durations_sorted[len(durations_sorted) // 2] / 1000
        d_p95 = durations_sorted[int(len(durations_sorted) * 0.95)] / 1000
        d_max = max(durations) / 1000

        t_avg = sum(tokens) / len(tokens) if tokens else 0
        t_p50 = sorted(tokens)[len(tokens) // 2] if tokens else 0
        t_p95 = sorted(tokens)[int(len(tokens) * 0.95)] if tokens else 0
        t_max = max(tokens) if tokens else 0

        lines.extend([
            "## メトリクスサマリー",
            "",
            "| | 平均 | P50 | P95 | 最大 |",
            "|---|---|---|---|---|",
            f"| 実行時間 | {d_avg:.0f}s | {d_p50:.0f}s | {d_p95:.0f}s | {d_max:.0f}s |",
            f"| トークン量 | {t_avg:,.0f} | {t_p50:,.0f} | {t_p95:,.0f} | {t_max:,.0f} |",
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


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate benchmark report")
    parser.add_argument("--run-dir", required=True, help="Path to benchmark run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    evaluations = []
    for eval_path in sorted(run_dir.glob("*/evaluation.json")):
        with open(eval_path, encoding="utf-8") as f:
            evaluations.append(json.load(f))

    report = generate_full_report(evaluations)
    report_path = run_dir / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}", file=sys.stderr)
    print(report)


if __name__ == "__main__":
    main()
