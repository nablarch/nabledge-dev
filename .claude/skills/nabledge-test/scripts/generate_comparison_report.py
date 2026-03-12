#!/usr/bin/env python
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
import math
import sys
from pathlib import Path
from statistics import mean as stat_mean, stdev


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


def ci_95(rates):
    """Compute (mean, std, ci_low, ci_high) for a list of detection rates (0-1)."""
    n = len(rates)
    m = stat_mean(rates)
    if n < 2:
        return m, 0.0, m, m
    s = stdev(rates)
    # t critical values for 95% CI (two-tailed), df = n-1
    t_crit = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
              6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
    t = t_crit.get(n - 1, 1.960)
    margin = t * s / math.sqrt(n)
    return m, s, max(0.0, m - margin), min(1.0, m + margin)


def change_mark_benchmark(prev_ci_low, prev_ci_high, curr_ci_low, curr_ci_high):
    """Return change mark based on CI overlap. Non-overlap = significant change."""
    if curr_ci_low > prev_ci_high:
        return "\U0001f7e2"   # clear improvement
    elif curr_ci_high < prev_ci_low:
        return "\U0001f534"   # clear regression
    return "\u2192"           # CIs overlap = within noise


def load_benchmark_data(baseline_dir):
    """Load benchmark.json for each benchmark scenario in a baseline dir."""
    result = {}
    for item in sorted(baseline_dir.iterdir()):
        if not item.is_dir():
            continue
        bm_path = item / "benchmark.json"
        if bm_path.exists():
            data = load_json(bm_path)
            if data:
                result[item.name] = data
    return result


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


def generate_initial_report(curr_meta, curr_run_id, curr_branch, curr_commit,
                             curr_scenarios=None, curr_benchmark=None):
    """Generate initial baseline report showing current baseline values."""
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
        "*\u521d\u56de\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u306e\u305f\u3081\u524d\u56de\u3068\u306e\u6bd4\u8f03\u306f\u3042\u308a\u307e\u305b\u3093\u3002"
        "\u6b21\u56de `--baseline` \u5b9f\u884c\u6642\u306b\u3053\u306e\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u3068\u306e\u6bd4\u8f03\u30ec\u30dd\u30fc\u30c8\u304c\u751f\u6210\u3055\u308c\u307e\u3059\u3002*",
        "",
        "---",
        "",
    ]

    # Benchmark baseline values
    if curr_benchmark:
        bm_ids = sorted(curr_benchmark.keys(),
                        key=lambda x: (0 if x.startswith("qa") else 1, x))
        bm_rows = []
        for sc_id in bm_ids:
            bm = curr_benchmark[sc_id]
            m, s = bm["mean"], bm["std"]
            cl, ch = bm["ci_95_low"], bm["ci_95_high"]
            rates_str = ", ".join(f"{r*100:.1f}%" for r in bm.get("detection_rates", []))
            bm_rows.append(
                f"| {sc_id} | {m*100:.1f}% \u00b1{s*100:.1f}%"
                f" | [{cl*100:.1f}%-{ch*100:.1f}%]"
                f" | {rates_str} |"
            )
        lines += [
            "## \u30d9\u30f3\u30c1\u30de\u30fc\u30af\u57fa\u6e96\u5024\uff08\u540410\u8a66\u884c\uff09",
            "",
            "*\u6b21\u56de\u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u5b9f\u884c\u6642\u306b\u3053\u306e\u5024\u3068\u6bd4\u8f03\u3055\u308c\u308b\u3002*",
            "",
            "| Scenario | mean\u00b1SD | 95%CI | \u8a66\u884c\u5225\u691c\u51fa\u7387 |",
            "|----------|---------|-------|--------------|",
            *bm_rows,
            "",
            "---",
            "",
        ]
    else:
        lines += [
            "## \u30d9\u30f3\u30c1\u30de\u30fc\u30af\u57fa\u6e96\u5024",
            "",
            "*\u30d9\u30f3\u30c1\u30de\u30fc\u30af\u30c7\u30fc\u30bf\u306a\u3057\u3002\u30d9\u30f3\u30c1\u30de\u30fc\u30af\u30b7\u30ca\u30ea\u30aa\uff08`\"benchmark\": true`\uff09\u304c\u672a\u8a2d\u5b9a\u306e\u305f\u3081\u3002*",
            "",
            "---",
            "",
        ]

    # Wide coverage baseline
    if curr_scenarios:
        sc_ids = sorted(curr_scenarios.keys(),
                        key=lambda x: (0 if x.startswith("qa") else 1, x))
        sc_rows = []
        for sc_id in sc_ids:
            sc = curr_scenarios[sc_id]
            det = sc["detected"]
            total = sc["total_items"]
            rate = sc["rate"] * 100
            mark = " \u2b50" if sc["rate"] == 1.0 else ""
            sc_rows.append(f"| {sc_id} | {det}/{total} ({rate:.1f}%){mark} |")
        lines += [
            "## \u5e83\u57df\u30ab\u30d0\u30ec\u30c3\u30b8\u57fa\u6e96\u5024\uff08\u5404\u30b7\u30ca\u30ea\u30aa\u00d71\u8a66\u884c\uff09",
            "",
            "| Scenario | \u691c\u51fa\u7387 |",
            "|----------|--------|",
            *sc_rows,
            "",
            "---",
            "",
        ]

    lines.append(
        f"*Generated by nabledge-test v2 baseline mode | Initial baseline | Commit: {curr_commit}*"
    )
    lines.append("")
    return "\n".join(lines)


def generate_comparison_report(curr_meta, curr_scenarios, prev_meta, prev_scenarios,
                               curr_benchmark=None, prev_benchmark=None):
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

    # Build benchmark section
    benchmark_lines = []
    if curr_benchmark and prev_benchmark:
        bm_ids = sorted(
            set(list(curr_benchmark.keys()) + list(prev_benchmark.keys())),
            key=lambda x: (0 if x.startswith("qa") else 1, x),
        )
        bm_rows = []
        for sc_id in bm_ids:
            prev_bm = prev_benchmark.get(sc_id)
            curr_bm = curr_benchmark.get(sc_id)
            if prev_bm and curr_bm:
                pm, ps = prev_bm["mean"], prev_bm["std"]
                pcl, pch = prev_bm["ci_95_low"], prev_bm["ci_95_high"]
                cm, cs = curr_bm["mean"], curr_bm["std"]
                ccl, cch = curr_bm["ci_95_low"], curr_bm["ci_95_high"]
                mark = change_mark_benchmark(pcl, pch, ccl, cch)
                delta = (cm - pm) * 100
                sign = "+" if delta >= 0 else ""
                delta_str = f"{sign}{delta:.1f}pp {mark}"
                bm_rows.append(
                    f"| {sc_id} | {pm*100:.1f}% \u00b1{ps*100:.1f}%"
                    f" | [{pcl*100:.1f}%-{pch*100:.1f}%]"
                    f" | {cm*100:.1f}% \u00b1{cs*100:.1f}%"
                    f" | [{ccl*100:.1f}%-{cch*100:.1f}%]"
                    f" | {delta_str} |"
                )
            elif curr_bm:
                cm, cs = curr_bm["mean"], curr_bm["std"]
                ccl, cch = curr_bm["ci_95_low"], curr_bm["ci_95_high"]
                bm_rows.append(
                    f"| {sc_id} | - | -"
                    f" | {cm*100:.1f}% \u00b1{cs*100:.1f}%"
                    f" | [{ccl*100:.1f}%-{cch*100:.1f}%] | NEW |"
                )
        if bm_rows:
            benchmark_lines = [
                "## \u30d9\u30f3\u30c1\u30de\u30fc\u30af\u6bd4\u8f03\uff08\u54c1\u8cea\u6e2c\u5b9a\uff09",
                "",
                "*\u5404\u30b7\u30ca\u30ea\u30aa10\u8a66\u884c\u306e\u7d71\u8a08\u3002"
                "95%\u4fe1\u983c\u533a\u9593\u304c\u91cd\u306a\u3089\u306a\u3044\u5834\u5408\u306e\u307f\u5909\u5316\u3092\u6709\u610f\u3068\u307f\u306a\u3059\u3002*",
                "",
                "| Scenario | \u524d\u56de mean\u00b1SD | \u524d\u56de 95%CI"
                " | \u4eca\u56de mean\u00b1SD | \u4eca\u56de 95%CI | \u5909\u5316 |",
                "|----------|--------------|-----------|--------------|-----------|------|",
                *bm_rows,
                "",
                "**\u5224\u5b9a**: \U0001f7e2 CI\u975e\u91cd\u8907\u306e\u6539\u5584"
                " / \U0001f534 CI\u975e\u91cd\u8907\u306e\u52a3\u5316"
                " / \u2192 CI\u91cd\u8907\uff08\u8aa4\u5dee\u7bc4\u56f2\u5185\uff09",
                "",
                "---",
                "",
            ]

    lines = [
        "# \u30d9\u30fc\u30b9\u30e9\u30a4\u30f3\u6bd4\u8f03\u30ec\u30dd\u30fc\u30c8",
        "",
        "## \u6982\u8981",
        "",
        "| \u9805\u76ee | \u524d\u56de | \u4eca\u56de |",
        "|------|------|------|",
        f"| Run ID | {prev_run_id} | {curr_run_id} |",
        f"| Branch | {prev_branch} | {curr_branch} |",
        f"| Commit | {prev_commit} | {curr_commit} |",
        f"| \u65e5\u6642 | {prev_ts} | {curr_ts} |",
        "",
        "## \u524d\u56de\u304b\u3089\u306e\u5909\u66f4\u70b9",
        "",
        f"<!-- AGENT: Run `git log --oneline {prev_full_commit}..{curr_full_commit}` and list"
        " user-facing changes as bullet points."
        " Format: `- <change description> (nablarch/nabledge-dev#xx)`."
        " Extract issue/PR numbers from commit messages (e.g. `(#123)` patterns)."
        " Use `(issue\u4e0d\u660e)` if no number found."
        " Skip non-user-facing commits (tests, CI, infra, dev tools). -->",
        "",
        "---",
        "",
        *benchmark_lines,
        "## \u7dcf\u5408\u8a55\u4fa1",
        "",
        "<!-- AGENT: Evaluate improvement effects from a third-party perspective using the numerical data above. -->",
        "",
        "---",
        "",
        "## \u5e83\u57df\u30c1\u30a7\u30c3\u30af\uff08\u5168\u30b7\u30ca\u30ea\u30aa\u00d71\u8a66\u884c\uff09",
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

    curr_benchmark = load_benchmark_data(curr_dir)

    if not args.previous:
        # Initial baseline — show current values without comparison
        content = generate_initial_report(curr_meta, curr_run_id, curr_branch, curr_commit,
                                          curr_scenarios, curr_benchmark)
    else:
        prev_dir = Path(args.previous)
        if not prev_dir.exists():
            print(f"Error: Previous baseline directory not found: {prev_dir}", file=sys.stderr)
            sys.exit(1)

        prev_meta, prev_scenarios = load_baseline_data(prev_dir)
        if prev_meta is None:
            print(f"Error: Could not load meta.json from {prev_dir}", file=sys.stderr)
            sys.exit(1)

        prev_benchmark = load_benchmark_data(prev_dir)
        content = generate_comparison_report(curr_meta, curr_scenarios, prev_meta, prev_scenarios,
                                             curr_benchmark, prev_benchmark)

    with open(output_path, "w") as f:
        f.write(content)
    print(f"  Generated comparison report: {output_path}")


if __name__ == "__main__":
    main()
