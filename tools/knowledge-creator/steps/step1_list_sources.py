"""Step 1: List Source Files

Scan source directories and generate a list of all documentation files to process.
"""

import os
from datetime import datetime, timezone
from .common import write_json


class Step1ListSources:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run

    def run(self):
        sources = []

        # 1. Official documentation (RST)
        rst_base = f"{self.ctx.repo}/.lw/nab-official/v{self.ctx.version}/nablarch-document/ja/"
        if os.path.exists(rst_base):
            for root, dirs, files in os.walk(rst_base):
                dirs[:] = [d for d in dirs if not d.startswith("_")]
                for f in files:
                    if f.endswith(".rst") and f != "index.rst":
                        rel_path = os.path.relpath(os.path.join(root, f), self.ctx.repo)
                        sources.append({"path": rel_path, "format": "rst", "filename": f})

        # 2. Pattern documents (MD) - always use v6
        pattern_dir = (
            f"{self.ctx.repo}/.lw/nab-official/v6/"
            "nablarch-system-development-guide/"
            "Nablarchシステム開発ガイド/docs/nablarch-patterns/"
        )
        for f in [
            "Nablarchバッチ処理パターン.md",
            "Nablarchでの非同期処理.md",
            "Nablarchアンチパターン.md",
        ]:
            filepath = os.path.join(pattern_dir, f)
            if os.path.exists(filepath):
                rel_path = os.path.relpath(filepath, self.ctx.repo)
                sources.append({"path": rel_path, "format": "md", "filename": f})

        # 3. Security mapping table (Excel) - always use v6
        xlsx_path = (
            f"{self.ctx.repo}/.lw/nab-official/v6/"
            "nablarch-system-development-guide/"
            "Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
        )
        if os.path.exists(xlsx_path):
            rel_path = os.path.relpath(xlsx_path, self.ctx.repo)
            sources.append({
                "path": rel_path, "format": "xlsx",
                "filename": "Nablarch機能のセキュリティ対応表.xlsx"
            })

        output = {
            "version": self.ctx.version,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sources": sources,
        }

        print(f"Found {len(sources)} source files")
        print(f"  RST: {sum(1 for s in sources if s['format'] == 'rst')}")
        print(f"  MD:  {sum(1 for s in sources if s['format'] == 'md')}")
        print(f"  Excel: {sum(1 for s in sources if s['format'] == 'xlsx')}")

        if not self.dry_run:
            write_json(self.ctx.source_list_path, output)
            print(f"\nWrote: {self.ctx.source_list_path}")

        return output
