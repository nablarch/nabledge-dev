#!/usr/bin/env python3
"""report.json を2つ比較して改善効果を表示する。

Usage:
    python tools/knowledge-creator/compare_reports.py \\
        tools/knowledge-creator/reports/20250304T143022.json \\
        tools/knowledge-creator/reports/20250305T091500.json
"""

import json
import sys


def load(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def fmt_diff(before, after, fmt="{:.3f}", unit="", positive_is_good=False):
    """差分を (before_str, after_str, diff_str) でフォーマット。None なら N/A を返す。"""
    if before is None or after is None:
        return "N/A", "N/A", "N/A"
    diff = after - before
    pct = (diff / before * 100) if before != 0 else 0
    sign = "+" if diff > 0 else ""
    good = diff < 0 if not positive_is_good else diff > 0
    arrow = "✅" if good else ("⚠️ " if diff != 0 else "   ")
    return (
        fmt.format(before) + unit,
        fmt.format(after) + unit,
        f"{arrow} {sign}{fmt.format(diff)}{unit} ({sign}{pct:.1f}%)"
    )


def print_row(label, before_str, after_str, diff_str, width=28):
    print(f"  {label:<{width}} {before_str:>16}  {after_str:>16}  {diff_str}")


def main():
    if len(sys.argv) != 3:
        print("Usage: compare_reports.py <before.json> <after.json>")
        sys.exit(1)

    before = load(sys.argv[1])
    after  = load(sys.argv[2])

    b_meta = before.get("meta", {})
    a_meta = after.get("meta", {})

    print("\n=== Knowledge Creator 実行比較レポート ===\n")
    print(f"  Before: {b_meta.get('run_id', 'N/A')}  ({b_meta.get('started_at', '')[:19]})")
    print(f"  After:  {a_meta.get('run_id', 'N/A')}  ({a_meta.get('started_at', '')[:19]})\n")
    print(f"  {'':28} {'Before':>16}  {'After':>16}  {'差分'}")
    print("  " + "-" * 82)

    # Phase B
    b_pb = before.get("phase_b") or {}
    a_pb = after.get("phase_b") or {}
    b_bm = b_pb.get("metrics") or {}
    a_bm = a_pb.get("metrics") or {}
    b_total = b_pb.get("ok", 0) + b_pb.get("error", 0)
    a_total = a_pb.get("ok", 0) + a_pb.get("error", 0)

    print("\n  [Phase B: Generate]")
    if b_total and a_total:
        b_rate = b_pb.get("ok", 0) / b_total
        a_rate = a_pb.get("ok", 0) / a_total
        r = fmt_diff(b_rate, a_rate, fmt="{:.1%}", positive_is_good=True)
        print_row("ok率", r[0], r[1], r[2])
    r = fmt_diff(b_bm.get("cost_usd"), a_bm.get("cost_usd"), fmt="{:.3f}", unit=" USD")
    print_row("コスト", r[0], r[1], r[2])
    r = fmt_diff(b_bm.get("avg_duration_sec"), a_bm.get("avg_duration_sec"), fmt="{:.1f}", unit="s")
    print_row("平均 duration", r[0], r[1], r[2])
    r = fmt_diff(b_bm.get("p95_duration_sec"), a_bm.get("p95_duration_sec"), fmt="{:.1f}", unit="s")
    print_row("p95 duration", r[0], r[1], r[2])
    r = fmt_diff(b_bm.get("avg_turns"), a_bm.get("avg_turns"), fmt="{:.1f}")
    print_row("平均ターン数", r[0], r[1], r[2])

    # Phase C
    b_pc = before.get("phase_c") or {}
    a_pc = after.get("phase_c") or {}
    if b_pc or a_pc:
        print("\n  [Phase C: Structure Check]")
        r = fmt_diff(b_pc.get("pass_rate"), a_pc.get("pass_rate"), fmt="{:.1%}", positive_is_good=True)
        print_row("pass率", r[0], r[1], r[2])

    # Phase D Round 1
    b_d_rounds = before.get("phase_d_rounds") or []
    a_d_rounds = after.get("phase_d_rounds") or []
    b_d = b_d_rounds[0] if b_d_rounds else {}
    a_d = a_d_rounds[0] if a_d_rounds else {}
    if b_d or a_d:
        print("\n  [Phase D: Content Check (Round 1)]")
        r = fmt_diff(b_d.get("clean_rate"), a_d.get("clean_rate"), fmt="{:.1%}", positive_is_good=True)
        print_row("clean率", r[0], r[1], r[2])
        b_crit = (b_d.get("findings") or {}).get("critical")
        a_crit = (a_d.get("findings") or {}).get("critical")
        r = fmt_diff(b_crit, a_crit, fmt="{:.0f}", unit="件")
        print_row("Critical件数", r[0], r[1], r[2])
        r = fmt_diff(
            (b_d.get("metrics") or {}).get("cost_usd"),
            (a_d.get("metrics") or {}).get("cost_usd"),
            fmt="{:.3f}", unit=" USD"
        )
        print_row("コスト", r[0], r[1], r[2])

    # Totals
    b_t = before.get("totals") or {}
    a_t = after.get("totals") or {}
    print("\n  [合計]")
    r = fmt_diff(b_t.get("cost_usd"), a_t.get("cost_usd"), fmt="{:.3f}", unit=" USD")
    print_row("総コスト", r[0], r[1], r[2])
    r = fmt_diff(
        b_meta.get("duration_sec"), a_meta.get("duration_sec"),
        fmt="{:.0f}", unit="s"
    )
    print_row("総実行時間", r[0], r[1], r[2])

    print()


if __name__ == "__main__":
    main()
