#!/usr/bin/env python
"""
Generate individual scenario reports and aggregate report from nabledge-test workspace data.

Usage:
    python generate_reports.py \
        --workspace .tmp/nabledge-test/run-20260307-120822 \
        --scenarios .claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json \
        --output-dir .pr/00129/nabledge-test/202603071208/ \
        --report-path .pr/00129/nabledge-test/report-202603071208.md \
        --version 6 \
        --branch 129-measurement-baseline-workflow \
        --commit 15e7eb5 \
        --run-timestamp 20260307-120822 \
        --trials 1
"""

import argparse
import json
import sys
from pathlib import Path
from statistics import median


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


def run_timestamp_to_short(run_timestamp):
    """Convert '20260307-120822' to '202603071208' (YYYYMMDDHHMM)."""
    ts = run_timestamp.replace("-", "")  # '20260307120822'
    return ts[:12]


def run_timestamp_to_display(run_timestamp):
    """Convert '20260307-120822' to '2026-03-07 12:08'."""
    ts = run_timestamp.replace("-", "")  # '20260307120822'
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}"


def count_ca_expectations(expectations):
    """Count CA expectations by section. Returns (total, section_counts dict)."""
    section_order = [
        "overview", "class_diagram", "component_summary",
        "processing_flow", "sequence_diagram", "nablarch_usage", "output",
    ]
    section_display = {
        "overview": "Overview",
        "class_diagram": "ClassDiagram",
        "component_summary": "ComponentSummary",
        "processing_flow": "ProcessingFlow",
        "sequence_diagram": "SequenceDiagram",
        "nablarch_usage": "NablarchUsage",
        "output": "Output",
    }
    counts = {}
    for section in section_order:
        items = expectations.get(section)
        if items is None:
            continue
        if isinstance(items, dict):
            total = sum(len(v) for v in items.values() if isinstance(v, list))
        elif isinstance(items, list):
            total = len(items)
        else:
            total = 0
        counts[section] = total

    total = sum(counts.values())
    parts = [f"{section_display[k]}×{v}" for k, v in counts.items()]
    summary = ", ".join(parts)
    return total, summary


def generate_individual_report(sc, metrics, grading, workspace, run_timestamp):
    """Generate individual scenario report markdown."""
    sc_id = sc["id"]
    question = sc["question"]
    sc_type = sc.get("type", "qa")
    expectations = sc.get("expectations", [])

    ts_display = run_timestamp_to_display(run_timestamp)

    # Type display
    is_ca = sc_type == "code-analysis"
    type_label = "Code-Analysis" if is_ca else "QA"

    # Expectations display
    if is_ca:
        exp_total, exp_summary = count_ca_expectations(expectations)
        exp_display = f"({exp_total} items): {exp_summary}"
    else:
        # QA object format: count items (OR groups count as 1)
        total = sum(len(items) for items in expectations.values())
        flat = []
        for items in expectations.values():
            for item in items:
                if isinstance(item, list):
                    flat.append(f"`{'`|`'.join(item)}`")
                else:
                    flat.append(f"`{item}`")
        exp_display = f"({total}): " + ", ".join(flat)

    # Detection items
    detection_lines = []
    for item in grading.get("detection_items", []):
        mark = "\u2713" if item["detected"] else "\u2717"
        detection_lines.append(f"- {mark} {item['text']}")
        evidence = item.get("evidence", "")
        if evidence:
            detection_lines.append(f"  Evidence: {evidence}")

    # Metrics
    duration = metrics.get("total_duration_seconds", 0)
    total_tool_calls = metrics.get("total_tool_calls", 0)
    response_chars = metrics.get("response_chars", 0)
    total_tokens, in_tokens, out_tokens = compute_tokens(metrics)

    # Detection summary
    detected = grading["summary"]["detected"]
    total = grading["summary"]["total"]
    rate = grading["summary"]["detection_rate"]
    rate_pct = f"{rate * 100:.1f}"

    # Step breakdown
    step_rows = []
    for s in metrics.get("steps", []):
        step_num = s.get("step", "")
        step_name = s.get("name", "")
        step_dur = s.get("duration_seconds", 0)
        step_in = s.get("in_tokens_estimate", 0)
        step_out = s.get("out_tokens_estimate", 0)
        step_rows.append(f"| {step_num} | {step_name} | {step_dur}\u79d2 | {step_in} | {step_out} |")

    # 目視判定 rows (CA uses 図の品質 instead of コード例の品質)
    if is_ca:
        visual_rows = [
            "| \u56de\u7b54\u306e\u6b63\u78ba\u6027 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u56de\u7b54\u306e\u7db2\u7f85\u6027 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u56f3\u306e\u54c1\u8cea | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u65e5\u672c\u8a9e\u306e\u81ea\u7136\u3055 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
        ]
    else:
        visual_rows = [
            "| \u56de\u7b54\u306e\u6b63\u78ba\u6027 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u56de\u7b54\u306e\u7db2\u7f85\u6027 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u30b3\u30fc\u30c9\u4f8b\u306e\u54c1\u8cea | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
            "| \u65e5\u672c\u8a9e\u306e\u81ea\u7136\u3055 | \u25ef / \u25b3 / \u2717 | \uff08\u624b\u52d5\u8a18\u5165\uff09 |",
        ]

    # Files section
    ws = str(workspace).rstrip("/")
    files_lines = [
        f"- **Response**: {ws}/{sc_id}/response.md",
        f"- **Metrics**: {ws}/{sc_id}/metrics.json",
        f"- **Grading**: {ws}/{sc_id}/grading.json",
    ]
    # Add output files for CA scenarios
    if is_ca:
        output_dir = Path(workspace) / sc_id / "output"
        if output_dir.exists():
            for f in sorted(output_dir.iterdir()):
                files_lines.append(f"- **Output**: {ws}/{sc_id}/output/{f.name}")

    lines = [
        f"# Test: {sc_id}",
        "",
        f"**Date**: {ts_display}",
        f"**Question**: {question}",
        "",
        "## Scenario",
        f"- **Type**: {type_label}",
        f"- **Expectations** {exp_display}",
        "",
        "## Detection Results",
        "",
        f"**Detection Rate**: {detected}/{total} ({rate_pct}%)",
        "",
        "### Detection Items",
        *detection_lines,
        "",
        "## Metrics",
        f"- **Duration**: {duration}\u79d2",
        f"- **Tool Calls**: {total_tool_calls}",
        f"- **Response Length**: {response_chars:,} chars",
        f"- **Tokens (estimate)**: {total_tokens:,} (IN: {in_tokens:,} / OUT: {out_tokens:,})",
        "",
        "### Step Breakdown",
        "| Step | Name | Duration | IN Tokens | OUT Tokens |",
        "|------|------|----------|-----------|------------|",
        *step_rows,
        "",
        "## \u76ee\u8996\u5224\u5b9a",
        "",
        "| \u89b3\u70b9 | \u5224\u5b9a | \u30e1\u30e2 |",
        "|------|------|------|",
        *visual_rows,
        "",
        "## Files",
        *files_lines,
        "",
    ]
    return "\n".join(lines)


def generate_step_table(results, type_name):
    """Generate step breakdown table lines for given scenario type results."""
    if not results:
        return []

    # Group steps by step number, collect stats
    step_data = {}   # step_num -> {durations, in_tokens, out_tokens}
    step_names = {}  # step_num -> name (first seen)

    for r in results:
        for step in r["metrics"].get("steps", []):
            sn = step.get("step", 0)
            # Normalize string step keys to int to prevent TypeError in sorted()
            if isinstance(sn, str):
                try:
                    sn = int(sn)
                except (ValueError, TypeError):
                    sn = 0
            if sn not in step_data:
                step_data[sn] = {"durations": [], "in_tokens": [], "out_tokens": []}
                step_names[sn] = step.get("name", f"Step {sn}")
            step_data[sn]["durations"].append(step.get("duration_seconds", 0))
            step_data[sn]["in_tokens"].append(step.get("in_tokens_estimate", 0))
            step_data[sn]["out_tokens"].append(step.get("out_tokens_estimate", 0))

    if not step_data:
        return []

    avg_total_dur = sum(r["duration"] for r in results) / len(results)

    # Build rows
    rows = []
    for sn in sorted(step_data.keys()):
        data = step_data[sn]
        durations = data["durations"]
        avg_dur = sum(durations) / len(durations)
        med_dur = median(durations)
        min_dur = min(durations)
        max_dur = max(durations)
        pct = avg_dur / avg_total_dur * 100 if avg_total_dur > 0 else 0

        avg_in = sum(data["in_tokens"]) / len(data["in_tokens"])
        avg_out = sum(data["out_tokens"]) / len(data["out_tokens"])

        rows.append({
            "step": sn,
            "name": step_names[sn],
            "avg": avg_dur,
            "med": med_dur,
            "min": min_dur,
            "max": max_dur,
            "pct": pct,
            "avg_in": avg_in,
            "avg_out": avg_out,
        })

    # Mark bottleneck (step with highest avg percentage)
    if rows:
        max_row = max(rows, key=lambda r: r["pct"])
        max_row["bottleneck"] = True

    # Format table rows
    table_rows = []
    bottleneck_name = None
    bottleneck_pct = 0
    for row in rows:
        is_bn = row.get("bottleneck", False)
        bn_mark = " \U0001f525" if is_bn else ""
        if is_bn:
            bottleneck_name = row["name"]
            bottleneck_pct = row["pct"]
        table_rows.append(
            f"| {row['step']} | {row['name']} | {row['avg']:.0f}\u79d2 | {row['med']:.0f}\u79d2 "
            f"| {row['pct']:.0f}% | {row['min']:.0f}-{row['max']:.0f}\u79d2 "
            f"| {row['avg_in']:.0f}/{row['avg_out']:.0f} |{bn_mark}"
        )

    bn_line = ""
    if bottleneck_name:
        bn_line = f"\u30dc\u30c8\u30eb\u30cd\u30c3\u30af: {bottleneck_name} \u304c\u6642\u9593\u306e{bottleneck_pct:.0f}%\u3092\u5360\u3081\u308b \U0001f525"

    header_row = "| \u30b9\u30c6\u30c3\u30d7 | \u540d\u79f0 | \u5e73\u5747 | \u4e2d\u9593\u5024 | \u5272\u5408 | \u7bc4\u56f2 | \u63a8\u5b9a\u30c8\u30fc\u30af\u30f3 (IN/OUT) |"
    separator_row = "|----------|------|------|--------|------|------|-----------------------|"

    if type_name == "QA":
        return [
            "### QA: \u30b9\u30c6\u30c3\u30d7\u5225\u5e73\u5747\u6642\u9593",
            "",
            header_row,
            separator_row,
            *table_rows,
            "",
            bn_line,
        ]
    else:
        return [
            "<details>",
            "<summary>Code-Analysis: \u30b9\u30c6\u30c3\u30d7\u5225\u8a73\u7d30</summary>",
            "",
            header_row,
            separator_row,
            *table_rows,
            "",
            bn_line,
            "",
            "</details>",
        ]


def generate_aggregate_report(args, scenarios_data, workspace, run_timestamp):
    """Generate aggregate report markdown."""
    ts_display = run_timestamp_to_display(run_timestamp)
    ts_short = run_timestamp_to_short(run_timestamp)

    # Load all scenario data from workspace
    results = []
    for sc in scenarios_data["scenarios"]:
        sc_id = sc["id"]
        sc_dir = Path(workspace) / sc_id

        metrics = load_json(sc_dir / "metrics.json")
        grading = load_json(sc_dir / "grading.json")

        if metrics is None or grading is None:
            print(f"Warning: Skipping {sc_id} — missing data files", file=sys.stderr)
            continue

        sc_type = sc.get("type", "qa")
        total_tokens, in_tokens, out_tokens = compute_tokens(metrics)

        results.append({
            "id": sc_id,
            "question": sc["question"],
            "type": sc_type,
            "type_label": "CA" if sc_type == "code-analysis" else "QA",
            "detected": grading["summary"]["detected"],
            "total_items": grading["summary"]["total"],
            "rate": grading["summary"]["detection_rate"],
            "duration": metrics.get("total_duration_seconds", 0),
            "total_tokens": total_tokens,
            "in_tokens": in_tokens,
            "out_tokens": out_tokens,
            "metrics": metrics,
            "grading": grading,
        })

    if not results:
        print("Error: No scenario results found in workspace", file=sys.stderr)
        sys.exit(1)

    # Legend marks
    min_dur = min(r["duration"] for r in results)
    max_dur = max(r["duration"] for r in results)
    max_tok = max(r["total_tokens"] for r in results)

    # Summary table rows
    summary_rows = []
    for i, r in enumerate(results, 1):
        star = " \u2b50" if r["rate"] == 1.0 else ""
        detect_str = f"{r['detected']}/{r['total_items']}{star}"

        time_marks = []
        if r["duration"] == min_dur:
            time_marks.append("\u26a1")
        if r["duration"] == max_dur:
            time_marks.append("\U0001f422")
        time_suffix = " " + "".join(time_marks) if time_marks else ""
        time_str = f"{r['duration']}\u79d2{time_suffix}"

        tok_mark = " \U0001f525" if r["total_tokens"] == max_tok else ""
        tok_str = f"{r['total_tokens']:,}{tok_mark}"

        summary_rows.append(
            f"| {i} | {r['id']} | {r['question']} | {r['type_label']} "
            f"| {detect_str} | {time_str} | {tok_str} |"
        )

    # Statistics
    qa_results = [r for r in results if r["type"] == "qa"]
    ca_results = [r for r in results if r["type"] == "code-analysis"]

    total_det = sum(r["detected"] for r in results)
    total_items = sum(r["total_items"] for r in results)
    total_rate = total_det / total_items * 100 if total_items > 0 else 0.0

    qa_det = sum(r["detected"] for r in qa_results)
    qa_items = sum(r["total_items"] for r in qa_results)
    qa_rate = qa_det / qa_items * 100 if qa_items > 0 else 0.0

    ca_det = sum(r["detected"] for r in ca_results)
    ca_items = sum(r["total_items"] for r in ca_results)
    ca_rate = ca_det / ca_items * 100 if ca_items > 0 else 0.0

    avg_dur = sum(r["duration"] for r in results) / len(results)
    qa_avg_dur = sum(r["duration"] for r in qa_results) / len(qa_results) if qa_results else 0
    ca_avg_dur = sum(r["duration"] for r in ca_results) / len(ca_results) if ca_results else 0

    fastest = min(results, key=lambda r: r["duration"])
    slowest = max(results, key=lambda r: r["duration"])

    avg_tok = sum(r["total_tokens"] for r in results) / len(results)
    min_tok_r = min(results, key=lambda r: r["total_tokens"])
    max_tok_r = max(results, key=lambda r: r["total_tokens"])

    # Performance analysis step tables
    qa_step_table = generate_step_table(qa_results, "QA")
    ca_step_table = generate_step_table(ca_results, "Code-Analysis")

    qa_count = len(qa_results)
    ca_count = len(ca_results)
    total_count = len(results)

    # Individual report links
    detail_links = []
    for r in results:
        rate_pct = r["rate"] * 100
        rate_str = "100% \u2b50" if rate_pct == 100.0 else f"{rate_pct:.1f}%"
        detail_links.append(f"- [{r['id']}]({ts_short}/{r['id']}.md) - {rate_str} - {r['question']}")

    lines = [
        f"# Nabledge-{args.version} Test Run: {ts_display}",
        "",
        "| \u9805\u76ee | \u5024 |",
        "|------|-----|",
        f"| Run ID | {run_timestamp} |",
        f"| Branch | {args.branch} |",
        f"| Commit | {args.commit} |",
        f"| \u5b9f\u884c\u30b7\u30ca\u30ea\u30aa | {total_count} (QA: {qa_count}, CA: {ca_count}) |",
        "| \u5b9f\u884c\u65b9\u5f0f | \u30b5\u30d6\u30a8\u30fc\u30b8\u30a7\u30f3\u30c8\u9010\u6b21\u5b9f\u884c |",
        f"| Trials | {args.trials} |",
        "",
        "---",
        "",
        "## \U0001f4ca \u7d50\u679c\u30b5\u30de\u30ea\u30fc",
        "",
        "| # | Scenario | \u8cea\u554f | Type | \u691c\u51fa | \u6642\u9593 | \u30c8\u30fc\u30af\u30f3 |",
        "|---|----------|------|------|------|------|---------|",
        *summary_rows,
        "",
        "**\u51e1\u4f8b**: \u2b50=100%\u691c\u51fa, \u26a1=\u6700\u901f, \U0001f422=\u6700\u9045, \U0001f525=\u6700\u5927\u30c8\u30fc\u30af\u30f3",
        "",
        "### \u7d71\u8a08",
        f"- **\u30ad\u30fc\u30ef\u30fc\u30c9/\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8\u691c\u51fa**: {total_det}/{total_items} ({total_rate:.1f}%)",
        f"  - QA: {qa_det}/{qa_items} ({qa_rate:.1f}%)",
        f"  - CA: {ca_det}/{ca_items} ({ca_rate:.1f}%)",
        f"- **\u5e73\u5747\u5b9f\u884c\u6642\u9593**: {avg_dur:.0f}\u79d2 (QA: {qa_avg_dur:.0f}\u79d2 / CA: {ca_avg_dur:.0f}\u79d2)",
        f"  - \u6700\u901f: {fastest['id']} ({fastest['duration']}\u79d2) \u26a1",
        f"  - \u6700\u9045: {slowest['id']} ({slowest['duration']}\u79d2) \U0001f422",
        f"- **\u5e73\u5747\u30c8\u30fc\u30af\u30f3**: {avg_tok:,.0f} (\u63a8\u5b9a\u5024)",
        f"  - \u6700\u5c11: {min_tok_r['id']} ({min_tok_r['total_tokens']:,})",
        f"  - \u6700\u591a: {max_tok_r['id']} ({max_tok_r['total_tokens']:,}) \U0001f525",
        "",
        "---",
        "",
        "## \u26a1 \u30d1\u30d5\u30a9\u30fc\u30de\u30f3\u30b9\u5206\u6790",
        "",
        *qa_step_table,
        "",
        *ca_step_table,
        "",
        "\u6ce8: \u30c8\u30fc\u30af\u30f3\u6570\u306f\u63a8\u5b9a\u5024 (\u6587\u5b57\u6570\u00f74)\u3002\u6b63\u78ba\u306a\u6e2c\u5b9a\u306b\u306fClaude API response\u306eusage\u30d5\u30a3\u30fc\u30eb\u30c9\u304c\u5fc5\u8981\u3002",
        "",
        "---",
        "",
        "## \U0001f4a1 \u4e3b\u8981\u306a\u767a\u898b",
        "",
        "<!-- AGENT: Analyze the data above for patterns, anomalies, key findings. Write 2-3 sections. -->",
        "",
        "---",
        "",
        "## \U0001f52c \u4eee\u8aac\u3068\u6539\u5584\u63d0\u6848",
        "",
        "<!-- AGENT: Based on findings above, propose hypotheses with evidence, verification method, and expected outcome. -->",
        "",
        "---",
        "",
        "## \U0001f4ce \u8a73\u7d30\u30c7\u30fc\u30bf",
        "",
        "### \u500b\u5225\u30b7\u30ca\u30ea\u30aa\u30ec\u30dd\u30fc\u30c8",
        *detail_links,
        "",
        "### \u30ef\u30fc\u30af\u30b9\u30da\u30fc\u30b9",
        f"- `.tmp/nabledge-test/run-{run_timestamp}/`",
        "",
        "---",
        "",
        f"*Generated by nabledge-test v2 | Run: {run_timestamp} | Commit: {args.commit}*",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate nabledge-test individual and aggregate reports")
    parser.add_argument("--workspace", required=True,
                        help="Workspace directory (e.g. .tmp/nabledge-test/run-20260307-120822)")
    parser.add_argument("--scenarios", required=True,
                        help="Scenarios JSON file path")
    parser.add_argument("--output-dir", required=True,
                        help="Output directory for individual reports")
    parser.add_argument("--report-path", required=True,
                        help="Output path for aggregate report")
    parser.add_argument("--version", required=True,
                        help="Nabledge version (6 or 5)")
    parser.add_argument("--branch", required=True,
                        help="Git branch name")
    parser.add_argument("--commit", required=True,
                        help="Git commit short SHA")
    parser.add_argument("--run-timestamp", required=True,
                        help="Run timestamp (YYYYMMDD-HHMMSS, e.g. 20260307-120822)")
    parser.add_argument("--trials", type=int, default=1,
                        help="Number of trials per scenario")
    parser.add_argument("--verify", action="store_true",
                        help="Verify computed numbers against source data and print summary")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.exists():
        print(f"Error: Workspace directory not found: {workspace}", file=sys.stderr)
        sys.exit(1)

    scenarios_path = Path(args.scenarios)
    scenarios_data = load_json(scenarios_path)
    if scenarios_data is None:
        print(f"Error: Could not load scenarios: {scenarios_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    run_timestamp = args.run_timestamp

    # Generate individual reports
    errors = 0
    for sc in scenarios_data["scenarios"]:
        sc_id = sc["id"]
        sc_dir = workspace / sc_id

        metrics = load_json(sc_dir / "metrics.json")
        grading = load_json(sc_dir / "grading.json")

        if metrics is None or grading is None:
            print(f"Warning: Skipping {sc_id} — missing data files", file=sys.stderr)
            errors += 1
            continue

        report = generate_individual_report(sc, metrics, grading, workspace, run_timestamp)
        out_path = output_dir / f"{sc_id}.md"
        with open(out_path, "w") as f:
            f.write(report)
        print(f"  Generated: {out_path}")

    # Generate aggregate report
    aggregate = generate_aggregate_report(args, scenarios_data, workspace, run_timestamp)
    with open(report_path, "w") as f:
        f.write(aggregate)
    print(f"  Generated aggregate: {report_path}")

    if args.verify:
        print("\n=== Verification ===")
        total_det = 0
        total_items = 0
        total_tok = 0
        for sc in scenarios_data["scenarios"]:
            sc_id = sc["id"]
            grading = load_json(workspace / sc_id / "grading.json")
            metrics = load_json(workspace / sc_id / "metrics.json")
            if grading and metrics:
                total_det += grading["summary"]["detected"]
                total_items += grading["summary"]["total"]
                tok, _, _ = compute_tokens(metrics)
                total_tok += tok
        n = len(scenarios_data["scenarios"])
        print(f"  Total detection: {total_det}/{total_items} ({total_det/total_items*100:.1f}%)")
        print(f"  Average tokens: {total_tok/n:,.0f}")
        print("  Verification complete")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
