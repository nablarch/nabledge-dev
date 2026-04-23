"""Generate sheet-classification.md — Phase 22-B-9.

Walks all Excel sources across every supported version and records the
verify-side P1/P2 classification (independent from converter, per spec
§8-2).  Flags sheets where the auto-detection is likely to need human
review.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools/rbkc"))

from scripts.verify.verify import (  # noqa: E402
    _detect_header_row,
    _read_sheet_matrix,
    _useful_width,
    _find_body_start,
    _run_length,
)
from scripts.create.converters.xlsx_common import list_sheet_names  # noqa: E402


VERSIONS = ["6", "5", "1.4", "1.3", "1.2"]


def _classify(path: Path, sheet_name: str) -> tuple[str, str, int, int, int]:
    """Return (class, reason, rows, cols, data_row_count)."""
    rows = _read_sheet_matrix(str(path), sheet_name)[0]
    nrows = len(rows)
    ncols = max((len(r) for r in rows), default=0)
    body_start = _find_body_start(rows)
    uw = _useful_width(rows, body_start)
    if uw <= 2:
        return "P2", f"useful_width={uw} ≤ 2", nrows, ncols, 0
    detected = _detect_header_row(rows)
    if detected is None:
        # find max run length to record why it failed
        max_rl = max((_run_length(r) for r in rows[body_start:body_start + 20]), default=0)
        return "P2", f"no header detected (max run_length={max_rl})", nrows, ncols, 0
    header_start, data_start, columns = detected
    data_rows = sum(1 for r in rows[data_start:] if any(c for c in r))
    return (
        "P1",
        f"header row={header_start + 1}, data_start={data_start + 1}, cols={len(columns)}",
        nrows,
        ncols,
        data_rows,
    )


def _collect_xlsx_files(version: str) -> list[Path]:
    """All xlsx/xls files that RBKC would classify for this version."""
    from scripts.create.scan import scan_sources
    sources = scan_sources(version, REPO)
    return [s.path for s in sources if s.format == "xlsx"]


def main() -> None:
    lines: list[str] = [
        "# Excel シート分類結果 (Phase 22-B-9)",
        "",
        "converter と verify は §8-2 header 検出規則を独立実装している。",
        "このファイルは **verify 側** の判定結果を出力する (converter と同じ",
        "アルゴリズムから独立に導出されたもの)。",
        "",
        "- **P1 (表)**: ヘッダ行 (連続非空セル ≥ 3) + データ行 ≥ 2 + 列数 > 2",
        "- **P2 (段落)**: 上記いずれか不成立",
        "",
        "",
    ]

    totals: dict[str, dict[str, int]] = {}
    for version in VERSIONS:
        lines.append(f"## Version {version}")
        lines.append("")
        try:
            files = _collect_xlsx_files(version)
        except FileNotFoundError as e:
            lines.append(f"_skipped: {e}_")
            lines.append("")
            continue
        if not files:
            lines.append("_no xlsx sources_")
            lines.append("")
            continue

        lines.append("| ファイル | シート | 判定 | 理由 | rows | cols | data rows |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        v_totals = {"P1": 0, "P2": 0}
        for path in sorted(files):
            rel = path.relative_to(REPO)
            sheets = list_sheet_names(path)
            for sh in sheets:
                klass, reason, nrows, ncols, data_rows = _classify(path, sh)
                v_totals[klass] += 1
                lines.append(
                    f"| `{rel.name}` | `{sh}` | **{klass}** | {reason} | "
                    f"{nrows} | {ncols} | {data_rows if klass == 'P1' else '—'} |"
                )
        totals[version] = v_totals
        lines.append("")
        lines.append(f"計: P1 = {v_totals['P1']}, P2 = {v_totals['P2']}")
        lines.append("")

    lines.append("## 全体計")
    lines.append("")
    lines.append("| version | P1 | P2 | 合計 |")
    lines.append("| --- | --- | --- | --- |")
    grand_p1 = grand_p2 = 0
    for v, t in totals.items():
        lines.append(f"| {v} | {t['P1']} | {t['P2']} | {t['P1'] + t['P2']} |")
        grand_p1 += t["P1"]
        grand_p2 += t["P2"]
    lines.append(f"| **total** | **{grand_p1}** | **{grand_p2}** | **{grand_p1 + grand_p2}** |")
    lines.append("")

    out = Path(__file__).with_name("sheet-classification.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
