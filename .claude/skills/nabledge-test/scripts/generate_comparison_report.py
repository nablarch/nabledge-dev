#!/usr/bin/env python3
"""
Generate comparison report between two baseline runs.

Usage:
    # With previous baseline:
    python generate_comparison_report.py \
        --current .claude/skills/nabledge-test/baseline/20260307-120822 \
        --previous .claude/skills/nabledge-test/baseline/20260306-151806 \
        --output .claude/skills/nabledge-test/baseline/20260307-120822/comparison-report.md

    # Initial baseline (no previous):
    python generate_comparison_report.py \
        --current .claude/skills/nabledge-test/baseline/20260307-120822 \
        --output .claude/skills/nabledge-test/baseline/20260307-120822/comparison-report.md
"""

import argparse
import json
import sys
from pathlib import Path


def load_json(path):
    """Load JSON file, return None if missing or parse error."""
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: JSON parse error in {path}: {e}", file=sys.stderr)
        return None


def compute_tokens(metrics):
    """Compute (total, in, out) token estimates from metrics."""
    in_total = sum(s.get("in_tokens_estimate", 0) for s in metrics.get("steps", []))
    out_total = sum(s.get("out_tokens_estimate", 0) for s in metrics.get("steps", []))
    return in_total + out_total, in_total, out_total


def load_baseline_data(baseline_dir):
    """
    Load meta and per-scenario data from a baseline directory.

    Returns (meta, scenarios_dict) where scenarios_dict maps
    scenario_id -> {duration, total_tokens, detected, total_items, rate, type}.
    """
    meta = load_json(baseline_dir / "meta.json")
    if meta is None:
        return None, {}

    all_ids = (
        meta.get("scenarios", {}).get("qa", []) +
        meta.get("scenarios", {}).get("code-analysis", [])
    )

    scenarios = {}
    for sc_id in all_ids:
        sc_dir = baseline_dir / sc_id
        metrics = load_json(sc_dir / "metrics.json")
        grading = load_json(sc_dir / "grading.json")
        if metrics and grading:
            total_tokens, _, _ = compute_tokens(metrics)
            scenarios[sc_id] = {
                "duration": metrics.get("total_duration_seconds", 0),
                "total_tokens": total_tokens,
                "detected": grading["summary"]["detected"],
                "total_items": grading["summary"]["total"],
                "rate": grading["summary"]["detection_rate"],
                "type": "code-analysis" if sc_id.startswith("ca-") else "qa",
            }

    return meta, scenarios


def change_mark_detection(prev_det, prev_total, curr_det, curr_total):
    """Return change mark for detection: more not-detected = worse."""
    prev_miss = prev_total - prev_det
    curr_miss = curr_total - curr_det
    if curr_miss < prev_miss:
        return "\U0001f7e2"   # improved
    elif curr_miss > prev_miss:
        return "\U0001f534"   # worse
    return "\u2192"


def change_mark_numeric(prev, curr, higher_is_worse=True):
    """Return change mark for time/tokens where higher is worse by default."""
    if prev == 0:
        return "\u2192"
    pct = (curr - prev) / prev
    threshold = 0.10
    if higher_is_worse:
        if pct < -threshold:
            return "\U0001f7e2"   # reduced = better
        elif pct > threshold:
            return "\U0001f534"   # increased = worse
    else:
        if pct > threshold:
            return "\U0001f7e2"
        elif pct < -threshold:
            return "\U0001f534"
    return "\u2192"


def format_time_diff(prev, curr):
    """Format time difference string like '↓6秒' or '↑12秒'."""
    diff = curr - prev
    if diff == 0:
        return "\u2192"
    arrow = "\u2193" if diff < 0 else "\u2191"
    return f"{arrow}{abs(diff)}\u79d2"


def format_token_diff(prev, curr):
    """Format token difference string like '↓519' or '↑1,200'."""
    diff = curr - prev
    if diff == 0:
        return "\u2192"
    arrow = "\u2193" if diff < 0 else "\u2191"
    return f"{arrow}{abs(diff):,}"


def compute_stats(scenarios):
    """Compute aggregate statistics for a set of scenario results."""
    if not scenarios:
        return {}
    vals = list(scenarios.values())
    qa = {k: v for k, v in scenarios.items() if v["type"] == "qa"}
    ca = {k: v for k, v in scenarios.items() if v["type"] == "code-analysis"}

    total_det = sum(v["detected"] for v in vals)
    total_items = sum(v["total_items"] for v in vals)
    total_rate = total_det / total_items * 100 if total_items > 0 else 0.0

    qa_det = sum(v["detected"] for v in qa.values())
    qa_items = sum(v["total_items"] for v in qa.values())
    qa_rate = qa_det / qa_items * 100 if qa_items > 0 else 0.0

    ca_det = sum(v["detected"] for v in ca.values())
    ca_items = sum(v["total_items"] for v in ca.values())
    ca_rate = ca_det / ca_items * 100 if ca_items > 0 else 0.0

    avg_dur = sum(v["duration"] for v in vals) / len(vals)
    qa_avg_dur = sum(v["duration"] for v in qa.values()) / len(qa) if qa else 0
    ca_avg_dur = sum(v["duration"] for v in ca.values()) / len(ca) if ca else 0

    avg_tok = sum(v["total_tokens"] for v in vals) / len(vals)

    return {
        "total_rate": total_rate,
        "qa_rate": qa_rate,
        "ca_rate": ca_rate,
        "avg_dur": avg_dur,
        "qa_avg_dur": qa_avg_dur,
        "ca_avg_dur": ca_avg_dur,
        "avg_tok": avg_tok,
    }


def generate_initial_report(curr_meta, curr_run_id, curr_branch, curr_commit):
    """Generate initial baseline comparison report (no previous baseline)."""
    lines = [
        "# \u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u6bd4\u8f03\u30ec\u30dd\u30fc\u30c8",
        "",
        "## \u6982\u8981",
        "",
        "| \u9805\u76ee | \u5024 |",
        "|------|-----|",
        f"| \u4eca\u56de | {curr_run_id} |",
        "| \u524d\u56de | \uff08\u521d\u56de\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\uff09 |",
        f"| Branch | {curr_branch} |",
        f"| Commit | {curr_commit} |",
        "",
        "---",
        "",
        "\u521d\u56de\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u306e\u305f\u3081\u3001\u6bd4\u8f03\u30c7\u30fc\u30bf\u306f\u3042\u308a\u307e\u305b\u3093\u3002",
        "\u6b21\u56de `--baseline` \u5b9f\u884c\u6642\u306b\u3001\u3053\u306e\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u3068\u306e\u6bd4\u8f03\u30ec\u30dd\u30fc\u30c8\u304c\u751f\u6210\u3055\u308c\u307e\u3059\u3002",
        "",
        f"*Generated by nabledge-test v2 baseline mode | Initial baseline | Commit: {curr_commit}*",
        "",
    ]
    return "\n".join(lines)


def generate_comparison_report(curr_meta, curr_scenarios, prev_meta, prev_scenarios):
    """Generate full comparison report with placeholders for analysis."""
    curr_run_id = curr_meta.get("run_id", "unknown")
    curr_branch = curr_meta.get("branch", "unknown")
    curr_commit = curr_meta.get("commit_short", "unknown")
    curr_ts = curr_meta.get("timestamp", "unknown")
    curr_version = curr_meta.get("version", 6)
    curr_full_commit = curr_meta.get("commit", curr_commit)

    prev_run_id = prev_meta.get("run_id", "unknown")
    prev_branch = prev_meta.get("branch", "unknown")
    prev_commit = prev_meta.get("commit_short", "unknown")
    prev_ts = prev_meta.get("timestamp", "unknown")
    prev_version = prev_meta.get("version", 6)
    prev_full_commit = prev_meta.get("commit", prev_commit)

    # Build sorted scenario list (qa first, then ca, sorted by ID)
    all_ids = sorted(
        set(list(curr_scenarios.keys()) + list(prev_scenarios.keys())),
        key=lambda x: (0 if x.startswith("qa") else 1, x),
    )

    # Scenario comparison table rows
    comparison_rows = []
    for i, sc_id in enumerate(all_ids, 1):
        prev = prev_scenarios.get(sc_id)
        curr = curr_scenarios.get(sc_id)

        if prev and curr:
            det_mark = change_mark_detection(
                prev["detected"], prev["total_items"],
                curr["detected"], curr["total_items"],
            )
            time_mark = change_mark_numeric(prev["duration"], curr["duration"])
            tok_mark = change_mark_numeric(prev["total_tokens"], curr["total_tokens"])

            time_diff = format_time_diff(prev["duration"], curr["duration"])
            tok_diff = format_token_diff(prev["total_tokens"], curr["total_tokens"])

            time_change = f"{time_diff} {time_mark}" if time_mark != "\u2192" else "\u2192"
            tok_change = f"{tok_diff} {tok_mark}" if tok_mark != "\u2192" else "\u2192"

            comparison_rows.append(
                f"| {i} | {sc_id} "
                f"| {prev['detected']}/{prev['total_items']} "
                f"| {curr['detected']}/{curr['total_items']} "
                f"| {det_mark} "
                f"| {prev['duration']}\u79d2 "
                f"| {curr['duration']}\u79d2 "
                f"| {time_change} "
                f"| {prev['total_tokens']:,} "
                f"| {curr['total_tokens']:,} "
                f"| {tok_change} | |"
            )
        elif curr:
            comparison_rows.append(
                f"| {i} | {sc_id} | - | {curr['detected']}/{curr['total_items']} "
                f"| NEW | - | {curr['duration']}\u79d2 | - | - | {curr['total_tokens']:,} | - | |"
            )
        else:
            comparison_rows.append(
                f"| {i} | {sc_id} | {prev['detected']}/{prev['total_items']} | - "
                f"| REMOVED | {prev['duration']}\u79d2 | - | - | {prev['total_tokens']:,} | - | - | |"
            )

    # Statistics comparison
    prev_stats = compute_stats(prev_scenarios)
    curr_stats = compute_stats(curr_scenarios)

    def pp_diff(prev_val, curr_val):
        diff = curr_val - prev_val
        sign = "+" if diff > 0 else ""
        return f"{sign}{diff:.1f}pp"

    def dur_diff(prev_val, curr_val):
        diff = curr_val - prev_val
        pct = (diff / prev_val * 100) if prev_val > 0 else 0.0
        sign = "+" if diff > 0 else ""
        pct_sign = "+" if pct > 0 else ""
        return f"{sign}{diff:.0f}\u79d2 ({pct_sign}{pct:.1f}%)"

    def tok_diff_fmt(prev_val, curr_val):
        diff = curr_val - prev_val
        pct = (diff / prev_val * 100) if prev_val > 0 else 0.0
        sign = "+" if diff > 0 else ""
        pct_sign = "+" if pct > 0 else ""
        return f"{sign}{diff:,.0f} ({pct_sign}{pct:.1f}%)"

    stat_rows = [
        f"| \u5168\u4f53\u691c\u51fa\u7387 | {prev_stats['total_rate']:.1f}% "
        f"| {curr_stats['total_rate']:.1f}% | {pp_diff(prev_stats['total_rate'], curr_stats['total_rate'])} |",
        f"| QA\u691c\u51fa\u7387 | {prev_stats['qa_rate']:.1f}% "
        f"| {curr_stats['qa_rate']:.1f}% | {pp_diff(prev_stats['qa_rate'], curr_stats['qa_rate'])} |",
        f"| CA\u691c\u51fa\u7387 | {prev_stats['ca_rate']:.1f}% "
        f"| {curr_stats['ca_rate']:.1f}% | {pp_diff(prev_stats['ca_rate'], curr_stats['ca_rate'])} |",
        f"| \u5e73\u5747\u5b9f\u884c\u6642\u9593 | {prev_stats['avg_dur']:.0f}\u79d2 "
        f"| {curr_stats['avg_dur']:.0f}\u79d2 | {dur_diff(prev_stats['avg_dur'], curr_stats['avg_dur'])} |",
        f"| QA\u5e73\u5747\u5b9f\u884c\u6642\u9593 | {prev_stats['qa_avg_dur']:.0f}\u79d2 "
        f"| {curr_stats['qa_avg_dur']:.0f}\u79d2 | {dur_diff(prev_stats['qa_avg_dur'], curr_stats['qa_avg_dur'])} |",
        f"| CA\u5e73\u5747\u5b9f\u884c\u6642\u9593 | {prev_stats['ca_avg_dur']:.0f}\u79d2 "
        f"| {curr_stats['ca_avg_dur']:.0f}\u79d2 | {dur_diff(prev_stats['ca_avg_dur'], curr_stats['ca_avg_dur'])} |",
        f"| \u5e73\u5747\u30c8\u30fc\u30af\u30f3 | {prev_stats['avg_tok']:,.0f} "
        f"| {curr_stats['avg_tok']:,.0f} | {tok_diff_fmt(prev_stats['avg_tok'], curr_stats['avg_tok'])} |",
    ]

    lines = [
        "# \u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u6bd4\u8f03\u30ec\u30dd\u30fc\u30c8",
        "",
        "## \u6982\u8981",
        "",
        "| \u9805\u76ee | \u524d\u56de | \u4eca\u56de | \u5dee\u5206 |",
        "|------|------|------|------|",
        f"| Run ID | {prev_run_id} | {curr_run_id} | |",
        f"| Branch | {prev_branch} | {curr_branch} | |",
        f"| Commit | {prev_commit} | {curr_commit} | |",
        f"| \u65e5\u6642 | {prev_ts} | {curr_ts} | |",
        "",
        "---",
        "",
        "## \u7dcf\u5408\u8a55\u4fa1",
        "",
        "<!-- AGENT: Evaluate improvement effects from a third-party perspective using the numerical data above. -->",
        "",
        "---",
        "",
        "## \u30b7\u30ca\u30ea\u30aa\u5225\u6bd4\u8f03\u8868",
        "",
        "| # | Scenario | \u691c\u51fa\u7387 (\u524d\u56de) | \u691c\u51fa\u7387 (\u4eca\u56de) | \u5909\u5316 "
        "| \u6642\u9593 (\u524d\u56de) | \u6642\u9593 (\u4eca\u56de) | \u5909\u5316 "
        "| \u30c8\u30fc\u30af\u30f3 (\u524d\u56de) | \u30c8\u30fc\u30af\u30f3 (\u4eca\u56de) | \u5909\u5316 | \u76ee\u8996 |",
        "|---|----------|-------------|-------------|------|-----------|-----------|------|"
        "---------------|---------------|------|------|",
        *comparison_rows,
        "",
        "**\u51e1\u4f8b**:",
        "- \U0001f7e2 \u6539\u5584\uff08\u691c\u51fa\u7387\u2191 or \u6642\u9593/\u30c8\u30fc\u30af\u30f3\u219110%\u8d85\uff09",
        "- \U0001f534 \u52a3\u5316\uff08\u691c\u51fa\u7387\u2193 or \u6642\u9593/\u30c8\u30fc\u30af\u30f3\u219110%\u8d85\uff09",
        "- \u2192 \u5909\u5316\u306a\u3057\uff08\u00b110%\u4ee5\u5185\uff09",
        "- \u76ee\u8996: \u624b\u52d5\u8a18\u5165\u6b04\uff08\u25ef\u6539\u5584 / \u25b3\u5909\u5316\u306a\u3057 / \u2717\u52a3\u5316\uff09",
        "",
        "**\u5909\u5316\u5224\u5b9a\u30eb\u30fc\u30eb**:",
        "- \u691c\u51fa\u7387: 1\u9805\u76ee\u3067\u3082\u6e1b\u5c11 \u2192 \U0001f534\u3001\u5897\u52a0 \u2192 \U0001f7e2\u3001\u540c\u6570 \u2192 \u2192",
        "- \u6642\u9593: \u00b110%\u4ee5\u5185 \u2192 \u2192\u300110%\u8d85\u306e\u77ed\u7e2e \u2192 \U0001f7e2\u300110%\u8d85\u306e\u5897\u52a0 \u2192 \U0001f534",
        "- \u30c8\u30fc\u30af\u30f3: \u00b110%\u4ee5\u5185 \u2192 \u2192\u300110%\u8d85\u306e\u524a\u6e1b \u2192 \U0001f7e2\u300110%\u8d85\u306e\u5897\u52a0 \u2192 \U0001f534",
        "",
        "---",
        "",
        "## \u7d71\u8a08\u6bd4\u8f03",
        "",
        "| \u6307\u6a19 | \u524d\u56de | \u4eca\u56de | \u5909\u5316 |",
        "|------|------|------|------|",
        *stat_rows,
        "",
        "---",
        "",
        "## \u5b9f\u6e2c\u30c7\u30fc\u30bf\u304b\u3089\u306e\u5206\u6790",
        "",
        "<!-- AGENT: Analyze overall trends, type-specific patterns, anomalous scenarios, "
        "step-level changes, and variability. -->",
        "",
        "---",
        "",
        "## \u5206\u6790\u3092\u53d7\u3051\u305f\u4eee\u8aac",
        "",
        "<!-- AGENT: Propose hypotheses based on analysis, with data evidence, "
        "relevant implementation, and predictions. -->",
        "",
        "---",
        "",
        "## \u518d\u73fe\u624b\u9806",
        "",
        "```bash",
        "# \u4eca\u56de\u306e\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u3068\u540c\u3058\u72b6\u614b\u3067\u518d\u8a08\u6e2c",
        f"git checkout {curr_full_commit}",
        f"nabledge-test {curr_version} --baseline",
        "",
        "# \u524d\u56de\u306e\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u3068\u540c\u3058\u72b6\u614b\u3067\u518d\u8a08\u6e2c",
        f"git checkout {prev_full_commit}",
        f"nabledge-test {prev_version} --baseline",
        "```",
        "",
        "---",
        "",
        f"*Generated by nabledge-test v2 baseline mode | "
        f"Compared: {prev_run_id} \u2192 {curr_run_id}*",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate nabledge-test comparison report")
    parser.add_argument("--current", required=True,
                        help="Current baseline directory path")
    parser.add_argument("--previous", default="",
                        help="Previous baseline directory path (omit for initial baseline)")
    parser.add_argument("--output", required=True,
                        help="Output path for comparison-report.md")
    args = parser.parse_args()

    curr_dir = Path(args.current)
    if not curr_dir.exists():
        print(f"Error: Current baseline directory not found: {curr_dir}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    curr_meta, curr_scenarios = load_baseline_data(curr_dir)
    if curr_meta is None:
        print(f"Error: Could not load meta.json from {curr_dir}", file=sys.stderr)
        sys.exit(1)

    curr_run_id = curr_meta.get("run_id", "unknown")
    curr_branch = curr_meta.get("branch", "unknown")
    curr_commit = curr_meta.get("commit_short", "unknown")

    if not args.previous:
        # Initial baseline — no comparison
        content = generate_initial_report(curr_meta, curr_run_id, curr_branch, curr_commit)
    else:
        prev_dir = Path(args.previous)
        if not prev_dir.exists():
            print(f"Error: Previous baseline directory not found: {prev_dir}", file=sys.stderr)
            sys.exit(1)

        prev_meta, prev_scenarios = load_baseline_data(prev_dir)
        if prev_meta is None:
            print(f"Error: Could not load meta.json from {prev_dir}", file=sys.stderr)
            sys.exit(1)

        content = generate_comparison_report(curr_meta, curr_scenarios, prev_meta, prev_scenarios)

    with open(output_path, "w") as f:
        f.write(content)
    print(f"  Generated comparison report: {output_path}")


if __name__ == "__main__":
    main()
