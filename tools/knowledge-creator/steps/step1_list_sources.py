"""Step 1: List source files from official documentation."""

import os
from .utils import write_json, utcnow_iso, log_info


def run(ctx):
    """Execute Step 1: List source files.

    Args:
        ctx: Context object with version and repo path
    """
    log_info(f"Scanning source files for version {ctx.version}")

    sources = []

    # 1. Official documentation (RST)
    rst_base = f"{ctx.repo}/.lw/nab-official/v{ctx.version}/nablarch-document/ja/"
    if os.path.exists(rst_base):
        log_info(f"Scanning RST files in {rst_base}")
        for root, dirs, files in os.walk(rst_base):
            # Exclude directories starting with _
            dirs[:] = [d for d in dirs if not d.startswith("_")]

            for f in files:
                if f.endswith(".rst") and f != "index.rst":
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, ctx.repo)
                    sources.append({
                        "path": rel_path,
                        "format": "rst",
                        "filename": f
                    })
    else:
        log_info(f"RST directory not found: {rst_base}")

    # 2. Pattern collection (MD) - always use v6 path
    pattern_dir = f"{ctx.repo}/.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/"
    target_files = [
        "Nablarchバッチ処理パターン.md",
        "Nablarchでの非同期処理.md",
        "Nablarchアンチパターン.md"
    ]

    if os.path.exists(pattern_dir):
        log_info(f"Scanning MD pattern files in {pattern_dir}")
        for f in target_files:
            filepath = os.path.join(pattern_dir, f)
            if os.path.exists(filepath):
                rel_path = os.path.relpath(filepath, ctx.repo)
                sources.append({
                    "path": rel_path,
                    "format": "md",
                    "filename": f
                })
            else:
                log_info(f"Pattern file not found: {f}")
    else:
        log_info(f"Pattern directory not found: {pattern_dir}")

    # 3. Security check table (Excel) - always use v6 path
    xlsx_path = f"{ctx.repo}/.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
    if os.path.exists(xlsx_path):
        log_info(f"Found security check table: {xlsx_path}")
        rel_path = os.path.relpath(xlsx_path, ctx.repo)
        sources.append({
            "path": rel_path,
            "format": "xlsx",
            "filename": "Nablarch機能のセキュリティ対応表.xlsx"
        })
    else:
        log_info(f"Security check table not found: {xlsx_path}")

    # Prepare output
    output = {
        "version": ctx.version,
        "generated_at": utcnow_iso(),
        "sources": sources
    }

    # Write output
    if not ctx.dry_run:
        write_json(ctx.source_list_path, output)
        log_info(f"Wrote {len(sources)} source files to {ctx.source_list_path}")
    else:
        log_info(f"[DRY-RUN] Would write {len(sources)} source files to {ctx.source_list_path}")
        print(f"\nSample sources (first 5):")
        for source in sources[:5]:
            print(f"  - {source['format']:4s} {source['filename']}")

    log_info(f"Step 1 completed: {len(sources)} source files found")
