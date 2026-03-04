# nabledge-creator 実装タスク

## ゴール

`tools/knowledge-creator/` 以下に、Nablarch公式ドキュメント（RST/MD/Excel）をAI Readyなナレッジファイル（JSON）に変換するツールを新規作成する。

このドキュメントだけを見て実装とテストを完了すること。既存コードは参照しない。

---

## ブランチ

```bash
git checkout main
git checkout -b 99-nabledge-creator-v2
```

---

## 完成時のファイル構成

```
tools/knowledge-creator/
  run.py
  requirements.txt
  steps/
    __init__.py
    common.py
    step1_list_sources.py
    step2_classify.py
    phase_b_generate.py
    phase_c_structure_check.py
    phase_d_content_check.py
    phase_e_fix.py
    phase_f_finalize.py
  prompts/
    generate.md
    content_check.md
    fix.md
    classify_patterns.md
  test-files.json
  pytest.ini
  tests/
    __init__.py
    conftest.py
    fixtures/
      sample_source.rst
      sample_knowledge.json
      sample_classified.json
    test_pipeline.py
    test_phase_c.py
```

---

## アーキテクチャ概要

```
Phase A: 準備 (Python, AI不要)
  ソースファイル一覧取得 → Type/Category分類 → classified.json

Phase B: 生成 (claude -p × N並列)
  classified.json の各エントリ → ナレッジJSON + trace

Phase C: 構造検証 (Python, AI不要)
  ナレッジJSON → 構造チェック (S1-S15) → pass/fail

Phase D: 内容検証 (claude -p × N並列, 別コンテキスト)
  ナレッジJSON + ソース → findings.json (問題特定のみ、修正しない)

Phase E: 修正 (claude -p × N並列, 問題ファイルのみ)
  findings + ナレッジJSON + ソース → 修正版ナレッジJSON

Phase F: 仕上げ (分類はclaude -p, 他はPython)
  処理パターン分類 → index.toon生成 → 閲覧用MD生成 → サマリー
```

Phase C→D→E は `--max-rounds` 回ループできる。

### モック戦略

全 Phase クラスのコンストラクタで `run_claude_fn=None` を受け取る。
`None` の場合は `common.py` の `run_claude` を使い、値がある場合はそれを使う。
テストではモック関数を注入して claude -p なしでパイプライン全体を通す。

```python
# 本番
PhaseBGenerate(ctx).run()

# テスト
PhaseBGenerate(ctx, run_claude_fn=mock_fn).run()
```

---

## 1. requirements.txt

```
openpyxl>=3.0.0,<4.0.0
pytest>=7.0.0
```

---

## 1b. pytest.ini

```ini
[pytest]
pythonpath = tests
```

---

## 2. steps/common.py

```python
"""Common utilities for knowledge-creator steps"""

import json
import subprocess
import os
from typing import Any
from openpyxl import load_workbook


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_excel_as_markdown(path: str) -> str:
    workbook = load_workbook(path, read_only=True, data_only=True)
    markdown_parts = []

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        markdown_parts.append(f"## {sheet_name}\n")
        rows = list(sheet.iter_rows(values_only=True))

        if not rows:
            markdown_parts.append("(Empty sheet)\n")
            continue

        max_cols = max(len(row) for row in rows) if rows else 0
        if max_cols == 0:
            markdown_parts.append("(Empty sheet)\n")
            continue

        for i, row in enumerate(rows):
            padded_row = list(row) + [None] * (max_cols - len(row))
            cells = [str(cell) if cell is not None else "" for cell in padded_row]
            markdown_parts.append("| " + " | ".join(cells) + " |")
            if i == 0:
                markdown_parts.append("| " + " | ".join(["---"] * max_cols) + " |")
        markdown_parts.append("")

    workbook.close()
    return "\n".join(markdown_parts)


def read_file(path: str) -> str:
    if path.endswith('.xlsx'):
        return read_excel_as_markdown(path)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def run_claude(prompt: str, timeout: int = 600, json_schema: dict = None) -> subprocess.CompletedProcess:
    """Run claude -p via stdin.

    Args:
        prompt: Prompt text
        timeout: Timeout in seconds
        json_schema: JSON Schema for structured output (optional)

    Returns:
        CompletedProcess. When json_schema is provided, stdout contains the structured_output JSON.
    """
    cmd = ["claude", "-p"]

    if json_schema:
        cmd.extend(["--output-format", "json"])
        cmd.extend(["--json-schema", json.dumps(json_schema)])

    env = os.environ.copy()
    env.pop('CLAUDECODE', None)

    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=timeout, env=env
    )

    if json_schema and result.returncode == 0:
        try:
            response = json.loads(result.stdout)
            subtype = response.get("subtype", "")

            if subtype == "success":
                structured_output = response.get("structured_output")
                if structured_output is not None:
                    result = subprocess.CompletedProcess(
                        args=result.args, returncode=0,
                        stdout=json.dumps(structured_output, ensure_ascii=False),
                        stderr=""
                    )
                else:
                    result = subprocess.CompletedProcess(
                        args=result.args, returncode=1,
                        stdout="", stderr="structured_output field is missing"
                    )
            elif subtype == "error_max_structured_output_retries":
                error_msg = response.get("result", "Failed to generate valid structured output")
                result = subprocess.CompletedProcess(
                    args=result.args, returncode=1,
                    stdout="", stderr=f"Structured output error: {error_msg}"
                )
            else:
                result = subprocess.CompletedProcess(
                    args=result.args, returncode=1,
                    stdout="", stderr=f"Unknown response subtype: {subtype}"
                )
        except json.JSONDecodeError as e:
            result = subprocess.CompletedProcess(
                args=result.args, returncode=1,
                stdout="", stderr=f"Failed to parse claude response JSON: {e}"
            )

    return result
```

---

## 3. steps/step1_list_sources.py

```python
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
```

---

## 4. steps/step2_classify.py

このファイルは469行あり、RST/MD/Excelのパスパターンによる分類ロジック、大規模ファイルの分割ロジック、テストモードのフィルタロジックを含む。

**このファイルだけは既存ブランチ `99-nabledge-creator-tool` からコピーする。**

```bash
git fetch origin 99-nabledge-creator-tool
git show origin/99-nabledge-creator-tool:tools/knowledge-creator/steps/step2_classify.py \
  > tools/knowledge-creator/steps/step2_classify.py
```

理由: 分類ルール（RST_MAPPING, MD_MAPPING等）は正解データそのものであり、このドキュメント内に全量を転記するのは非現実的。ロジックは安定しており変更不要。

**同様に test-files.json もコピーする:**

```bash
git show origin/99-nabledge-creator-tool:tools/knowledge-creator/test-files.json \
  > tools/knowledge-creator/test-files.json
```

---

## 5. run.py

```python
#!/usr/bin/env python3
"""
Knowledge Creator - Main Entry Point

Converts Nablarch official documentation to AI-ready JSON knowledge files.
"""

import argparse
import sys
import os
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))


@dataclass
class Context:
    version: str
    repo: str
    concurrency: int
    test_mode: bool = False
    max_rounds: int = 1

    def __post_init__(self):
        if not os.path.isdir(self.repo):
            raise ValueError(f"Repository path does not exist: {self.repo}")

    @property
    def source_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/sources.json"

    @property
    def classified_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/classified.json"

    @property
    def knowledge_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/knowledge"

    @property
    def docs_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/docs"

    @property
    def index_path(self) -> str:
        return f"{self.knowledge_dir}/index.toon"

    @property
    def log_dir(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}"

    @property
    def findings_dir(self) -> str:
        return f"{self.log_dir}/validate/findings"

    @property
    def trace_dir(self) -> str:
        return f"{self.log_dir}/generate/trace"


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Creator - Convert Nablarch documentation to AI-ready JSON"
    )
    parser.add_argument("--version", required=True, choices=["6", "5", "all"])
    parser.add_argument("--phase", type=str, default=None,
                        help="Phases to run (e.g. 'B', 'CD', 'BCDEF'). Default: all")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--repo", default=os.getcwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--max-rounds", type=int, default=1,
                        help="Max D->E->C loop iterations (default: 1)")

    args = parser.parse_args()
    versions = ["6", "5"] if args.version == "all" else [args.version]

    for v in versions:
        print(f"\n{'='*60}")
        print(f"Processing version: {v}")
        print(f"{'='*60}\n")

        ctx = Context(
            version=v, repo=args.repo, concurrency=args.concurrency,
            test_mode=args.test_mode, max_rounds=args.max_rounds
        )
        os.makedirs(ctx.log_dir, exist_ok=True)
        phases = args.phase or "ABCDEF"

        # Phase A
        if "A" in phases:
            print("\n--- Phase A: Prepare ---")
            from steps.step1_list_sources import Step1ListSources
            from steps.step2_classify import Step2Classify
            sources = Step1ListSources(ctx, dry_run=args.dry_run).run()
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources).run()

        # Phase B
        if "B" in phases:
            print("\n--- Phase B: Generate ---")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run()

        # Phase C/D/E loop
        for round_num in range(1, ctx.max_rounds + 1):
            print(f"\n--- Round {round_num}/{ctx.max_rounds} ---")

            c_result = None
            if "C" in phases:
                print("\n--- Phase C: Structure Check ---")
                from steps.phase_c_structure_check import PhaseCStructureCheck
                c_result = PhaseCStructureCheck(ctx).run()
                if c_result["error_count"] > 0:
                    print(f"構造エラー {c_result['error_count']}件。"
                          f"詳細: {ctx.log_dir}/structure-check.json")

            if "D" in phases:
                print("\n--- Phase D: Content Check ---")
                from steps.phase_d_content_check import PhaseDContentCheck
                pass_ids = c_result.get("pass_ids") if c_result else None
                d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                    target_ids=pass_ids
                )

                if d_result["issues_count"] == 0:
                    print(f"Round {round_num}: 内容検証パス（問題なし）")
                    break

                if "E" in phases:
                    print("\n--- Phase E: Fix ---")
                    from steps.phase_e_fix import PhaseEFix
                    PhaseEFix(ctx, dry_run=args.dry_run).run(
                        target_ids=d_result["issue_file_ids"]
                    )
                else:
                    break
            else:
                break

        # Phase F
        if "F" in phases:
            print("\n--- Phase F: Finalize ---")
            from steps.phase_f_finalize import PhaseFFinalize
            PhaseFFinalize(ctx, dry_run=args.dry_run).run()

        print(f"\n{'='*60}")
        print(f"Completed version: {v}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
```

---

## 6. steps/phase_b_generate.py

```python
"""Phase B: Generate Knowledge Files

Generate JSON knowledge files from source documentation using claude -p.
"""

import os
import re
import json
import shutil
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude


class PhaseBGenerate:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/generate.md"
        )
        self.json_schema = self._extract_json_schema()

    def _extract_json_schema(self) -> dict:
        """Extract JSON Schema from the first ```json block in the prompt."""
        match = re.search(
            r'```json\s*\n(\{[^`]+\})\s*\n```',
            self.prompt_template, re.DOTALL
        )
        if not match:
            raise ValueError("JSON Schema not found in prompt template")
        schema = json.loads(match.group(1))
        schema.pop("$schema", None)
        return schema

    def _extract_assets(self, source_path, source_content, source_format,
                        assets_dir_abs, assets_dir_rel):
        """Extract images and attachments from source file."""
        assets = []
        source_dir = os.path.dirname(f"{self.ctx.repo}/{source_path}")

        if source_format == "rst":
            for ref in re.findall(r'\.\.\s+(?:image|figure)::\s+(.+)', source_content):
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        shutil.copy2(src, os.path.join(assets_dir_abs, os.path.basename(ref)))
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

            for ref in re.findall(r':download:`[^<]*<([^>]+)>`', source_content):
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        shutil.copy2(src, os.path.join(assets_dir_abs, os.path.basename(ref)))
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

        return assets

    def _compute_official_url(self, file_info):
        if file_info["format"] == "rst":
            path = file_info["source_path"]
            marker = "nablarch-document/ja/"
            idx = path.find(marker)
            if idx >= 0:
                relative = path[idx + len(marker):].replace(".rst", ".html")
                return f"https://nablarch.github.io/docs/LATEST/doc/{relative}"
        elif file_info["format"] in ("md", "xlsx"):
            return "https://fintan.jp/page/252/"
        return ""

    def _extract_rst_labels(self, source_content):
        return re.compile(r'^\.\.\s+_([a-z0-9_-]+):', re.MULTILINE).findall(source_content)

    def _build_prompt(self, file_info, source_content, assets):
        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
        prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", self._compute_official_url(file_info))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

        if file_info["format"] == "rst":
            labels = self._extract_rst_labels(source_content)
            prompt = prompt.replace("{INTERNAL_LABELS}", json.dumps(labels, ensure_ascii=False))
        else:
            prompt = prompt.replace("{INTERNAL_LABELS}", "[]")

        if assets:
            section = "\n## 画像・添付ファイル一覧\n\n"
            section += "| ソース内パス | assetsパス |\n|---|---|\n"
            for a in assets:
                section += f"| {a['original']} | {a['assets_path']} |\n"
            prompt = prompt.replace("{ASSETS_SECTION}", section)
        else:
            prompt = prompt.replace("{ASSETS_SECTION}", "")

        return prompt

    def _extract_json(self, output):
        """Extract knowledge and trace from output. Returns (knowledge, trace)."""
        parsed = json.loads(output.strip())
        knowledge = parsed.get("knowledge")
        trace = parsed.get("trace")
        if not knowledge:
            raise ValueError("No 'knowledge' field in output")
        return knowledge, trace

    def _extract_section_range(self, content, section_range):
        lines = content.splitlines()
        return '\n'.join(lines[section_range['start_line']:section_range['end_line']])

    def generate_one(self, file_info):
        file_id = file_info["id"]
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"
        output_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        log_path = f"{self.ctx.log_dir}/generate/{file_id}.json"

        if os.path.exists(output_path):
            print(f"  [SKIP] {file_id}")
            return {"status": "skip", "id": file_id}

        print(f"  [GEN] {file_id}")
        source_content = read_file(source_path)

        if 'section_range' in file_info:
            source_content = self._extract_section_range(source_content, file_info['section_range'])

        assets_dir_rel_full = file_info['assets_dir']
        assets_dir_abs = f"{self.ctx.knowledge_dir}/{assets_dir_rel_full}"
        json_dir = os.path.dirname(file_info['output_path'])
        assets_dir_rel = os.path.relpath(assets_dir_rel_full, json_dir) + "/"

        assets = self._extract_assets(
            file_info['source_path'], source_content,
            file_info['format'], assets_dir_abs, assets_dir_rel
        )
        prompt = self._build_prompt(file_info, source_content, assets)
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=self.json_schema)
        except subprocess.TimeoutExpired:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": "timeout"})
            return {"status": "error", "id": file_id, "error": "timeout"}

        if result.returncode != 0:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": result.stderr})
            return {"status": "error", "id": file_id, "error": result.stderr}

        try:
            knowledge_json, trace_json = self._extract_json(result.stdout)
        except (json.JSONDecodeError, ValueError) as e:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": str(e)})
            return {"status": "error", "id": file_id, "error": str(e)}

        if not self.dry_run:
            write_json(output_path, knowledge_json)

            if trace_json and trace_json.get("sections"):
                write_json(f"{self.ctx.trace_dir}/{file_id}.json", {
                    "file_id": file_id,
                    "generated_at": started_at,
                    "sections": trace_json["sections"]
                })

        finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        duration = (datetime.fromisoformat(finished_at.rstrip("Z"))
                    - datetime.fromisoformat(started_at.rstrip("Z"))).seconds

        if not self.dry_run:
            write_json(log_path, {
                "file_id": file_id, "status": "ok",
                "started_at": started_at, "finished_at": finished_at,
                "duration_sec": duration
            })

        return {"status": "ok", "id": file_id}

    def _merge_split_files(self):
        """Merge split knowledge files into single files.

        Files with split_info.is_split=true are parts of a larger file.
        Group by original_id, merge, save as {original_id}.json,
        delete part files, update classified_list.json.
        """
        classified = load_json(self.ctx.classified_list_path)

        split_groups = {}
        for fi in classified["files"]:
            if "split_info" in fi and fi["split_info"].get("is_split"):
                oid = fi["split_info"]["original_id"]
                split_groups.setdefault(oid, []).append(fi)

        if not split_groups:
            return

        print(f"\n--- Merging Split Files ---")
        merged_groups = {}

        for original_id, parts in split_groups.items():
            parts.sort(key=lambda p: p["split_info"]["part"])

            part_paths = []
            all_exist = True
            for part in parts:
                pp = f"{self.ctx.knowledge_dir}/{part['output_path']}"
                if os.path.exists(pp):
                    part_paths.append(pp)
                else:
                    all_exist = False
                    break

            if not all_exist:
                print(f"  [SKIP] {original_id}: not all parts generated")
                continue

            print(f"  [MERGE] {original_id}: {len(parts)} parts")
            part_jsons = [load_json(pp) for pp in part_paths]

            merged = {
                "id": original_id,
                "title": part_jsons[0].get("title", ""),
            }

            # Merge official_doc_urls (deduplicate, preserve order)
            seen_urls = set()
            urls = []
            for pj in part_jsons:
                for url in pj.get("official_doc_urls", []):
                    if url not in seen_urls:
                        seen_urls.add(url)
                        urls.append(url)
            merged["official_doc_urls"] = urls

            # Merge index
            index_map = {}
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in index_map:
                        index_map[sid] = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                    else:
                        existing = set(index_map[sid]["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing:
                                index_map[sid]["hints"].append(h)
                                existing.add(h)
            merged["index"] = list(index_map.values())

            # Merge sections
            merged["sections"] = {}
            for i, pj in enumerate(part_jsons):
                part_id = parts[i]["id"]
                for sid, content in pj.get("sections", {}).items():
                    content = content.replace(f"assets/{part_id}/", f"assets/{original_id}/")
                    if sid not in merged["sections"]:
                        merged["sections"][sid] = content
                    else:
                        merged["sections"][sid] += "\n\n" + content

            type_ = parts[0]["type"]
            category = parts[0]["category"]
            merged_path = f"{self.ctx.knowledge_dir}/{type_}/{category}/{original_id}.json"

            try:
                write_json(merged_path, merged)

                # Consolidate assets
                merged_assets = f"{self.ctx.knowledge_dir}/{type_}/{category}/assets/{original_id}/"
                for part in parts:
                    part_assets = f"{self.ctx.knowledge_dir}/{part['assets_dir']}"
                    if os.path.exists(part_assets):
                        os.makedirs(merged_assets, exist_ok=True)
                        for af in os.listdir(part_assets):
                            src = os.path.join(part_assets, af)
                            dst = os.path.join(merged_assets, af)
                            if os.path.isfile(src) and not os.path.exists(dst):
                                shutil.move(src, dst)
                        try:
                            os.rmdir(part_assets)
                        except OSError:
                            pass

                for pp in part_paths:
                    os.remove(pp)

                merged_groups[original_id] = parts
            except Exception as e:
                print(f"    ERROR: {original_id}: {e}")

        # Update classified_list
        if merged_groups:
            part_ids = set()
            for parts in merged_groups.values():
                for p in parts:
                    part_ids.add(p["id"])

            new_files = [fi for fi in classified["files"] if fi["id"] not in part_ids]
            for oid, parts in merged_groups.items():
                base = parts[0].copy()
                base["id"] = oid
                base["output_path"] = f"{base['type']}/{base['category']}/{oid}.json"
                base["assets_dir"] = f"{base['type']}/{base['category']}/assets/{oid}/"
                base.pop("split_info", None)
                base.pop("section_range", None)
                new_files.append(base)

            new_files.sort(key=lambda f: (f["type"], f["category"], f["id"]))
            classified["files"] = new_files
            write_json(self.ctx.classified_list_path, classified)

    def run(self):
        classified = load_json(self.ctx.classified_list_path)

        if self.dry_run:
            print(f"Would generate {len(classified['files'])} knowledge files")
            return

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.generate_one, fi) for fi in classified["files"]]
            results = {"ok": 0, "error": 0, "skip": 0}
            for future in as_completed(futures):
                r = future.result()
                results[r["status"]] += 1
                if r["status"] == "error":
                    print(f"    ERROR: {r['id']}: {r.get('error', '')}")

        print(f"\nGeneration: OK={results['ok']}, Skip={results['skip']}, Error={results['error']}")

        if not self.dry_run:
            self._merge_split_files()
```

---

## 7. steps/phase_c_structure_check.py

```python
"""Phase C: Structure Check

Validate generated knowledge files with structural checks (S1-S15).
Pure Python, no AI needed.
"""

import os
import re
import json
from .common import load_json, write_json, read_file

KEBAB_CASE_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


class PhaseCStructureCheck:
    def __init__(self, ctx):
        self.ctx = ctx

    def count_source_headings(self, content, fmt):
        if fmt == "rst":
            return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
        elif fmt == "md":
            return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
        elif fmt == "xlsx":
            return 1
        return 0

    def validate_structure(self, json_path, source_path, source_format):
        """Perform structural validation checks (S1-S15). Returns list of error strings."""
        errors = []

        # S1: JSON parse
        try:
            knowledge = load_json(json_path)
        except json.JSONDecodeError as e:
            return [f"S1: JSON parse error: {e}"]

        # S2: Required fields
        for field in ["id", "title", "official_doc_urls", "index", "sections"]:
            if field not in knowledge:
                errors.append(f"S2: Missing required field: {field}")

        if "index" not in knowledge or "sections" not in knowledge:
            return errors

        index_ids = [entry["id"] for entry in knowledge.get("index", [])]
        index_id_set = set(index_ids)
        section_keys = set(knowledge.get("sections", {}).keys())

        # S3, S4: index <-> sections consistency
        for iid in index_id_set - section_keys:
            errors.append(f"S3: index[].id '{iid}' has no corresponding section")
        for sk in section_keys - index_id_set:
            errors.append(f"S4: sections key '{sk}' has no corresponding index entry")

        # S5: Kebab-case
        for entry in knowledge.get("index", []):
            if not KEBAB_CASE_PATTERN.match(entry["id"]):
                errors.append(f"S5: Section ID '{entry['id']}' is not kebab-case")

        # S6: Non-empty hints
        for entry in knowledge.get("index", []):
            if not entry.get("hints"):
                errors.append(f"S6: Section '{entry['id']}' has empty hints")

        # S7: Non-empty sections
        for sid, content in knowledge.get("sections", {}).items():
            if not content.strip():
                errors.append(f"S7: Section '{sid}' has empty content")

        # S8: Filename match
        expected_id = os.path.basename(json_path).replace(".json", "")
        if knowledge.get("id") != expected_id:
            errors.append(f"S8: id '{knowledge.get('id')}' != filename '{expected_id}'")

        # S9: Section count
        if os.path.exists(source_path):
            source_content = read_file(source_path)
            expected = self.count_source_headings(source_content, source_format)
            actual = len(knowledge.get("sections", {}))
            if actual < expected:
                errors.append(f"S9: Section count {actual} < source headings {expected}")

        # S11: URL format
        for url in knowledge.get("official_doc_urls", []):
            if not url.startswith("https://"):
                errors.append(f"S11: URL not https: {url}")

        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                errors.append(f"S13: Section '{sid}' too short ({len(stripped)} chars)")

        # S14: Internal reference validation
        internal_ref = re.compile(r'\]\(#([a-z0-9_-]+)\)')
        section_ids = set(knowledge.get("sections", {}).keys())
        for sid, content in knowledge.get("sections", {}).items():
            for m in internal_ref.finditer(content):
                if m.group(1) not in section_ids:
                    errors.append(f"S14: Section '{sid}' refs '#{m.group(1)}' not found")

        # S15: Assets path validation
        json_dir = os.path.dirname(json_path)
        asset_ref = re.compile(r'[!\[]\[?[^\]]*\]\(assets/([^)]+)\)')
        for sid, content in knowledge.get("sections", {}).items():
            for m in asset_ref.finditer(content):
                asset_abs = os.path.join(json_dir, f"assets/{m.group(1)}")
                if not os.path.exists(asset_abs):
                    errors.append(f"S15: Section '{sid}' refs 'assets/{m.group(1)}' not found")

        return errors

    def run(self) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        results = {
            "total": 0, "pass": 0, "error": 0,
            "error_count": 0, "errors": {}, "pass_ids": []
        }

        for fi in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{fi['output_path']}"
            source_path = f"{self.ctx.repo}/{fi['source_path']}"

            if not os.path.exists(json_path):
                continue

            results["total"] += 1
            errs = self.validate_structure(json_path, source_path, fi["format"])

            if errs:
                results["error"] += 1
                results["error_count"] += len(errs)
                results["errors"][fi["id"]] = errs
                print(f"  [FAIL] {fi['id']}: {len(errs)} errors")
            else:
                results["pass"] += 1
                results["pass_ids"].append(fi["id"])

        write_json(f"{self.ctx.log_dir}/structure-check.json", results)
        print(f"\n構造検証: {results['pass']}/{results['total']} pass, "
              f"{results['error']} fail ({results['error_count']} errors)")
        return results
```

---

## 8. steps/phase_d_content_check.py

```python
"""Phase D: Content Check

Compare knowledge files against source files to identify issues.
Does NOT fix anything - only reports findings.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

FINDINGS_SCHEMA = {
    "type": "object",
    "required": ["file_id", "status", "findings"],
    "properties": {
        "file_id": {"type": "string"},
        "status": {"type": "string", "enum": ["clean", "has_issues"]},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "severity", "location", "description"],
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["omission", "fabrication", "hints_missing", "section_issue"]
                    },
                    "severity": {"type": "string", "enum": ["critical", "minor"]},
                    "location": {"type": "string"},
                    "description": {"type": "string"},
                    "source_evidence": {"type": "string"}
                }
            }
        }
    }
}


class PhaseDContentCheck:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/content_check.md"
        )

    def _build_prompt(self, file_info, knowledge, source_content):
        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        return prompt

    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        if os.path.exists(findings_path):
            return load_json(findings_path)

        json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"

        if not os.path.exists(json_path) or not os.path.exists(source_path):
            return {"file_id": file_id, "status": "error", "findings": []}

        knowledge = load_json(json_path)
        source = read_file(source_path)
        prompt = self._build_prompt(file_info, knowledge, source)

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=FINDINGS_SCHEMA)
            if result.returncode == 0:
                findings = json.loads(result.stdout)
                if not self.dry_run:
                    write_json(findings_path, findings)
                return findings
        except Exception:
            pass

        return {"file_id": file_id, "status": "error", "findings": []}

    def run(self, target_ids=None) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        files = classified["files"]

        if target_ids is not None:
            target_set = set(target_ids)
            files = [f for f in files if f["id"] in target_set]

        if self.dry_run:
            print(f"Would check {len(files)} files")
            return {"issues_count": 0, "issue_file_ids": []}

        os.makedirs(self.ctx.findings_dir, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = {executor.submit(self.check_one, fi): fi["id"] for fi in files}
            issue_ids = []
            clean = 0
            for future in as_completed(futures):
                r = future.result()
                if r.get("status") == "has_issues":
                    issue_ids.append(r["file_id"])
                    print(f"  [ISSUE] {r['file_id']}: {len(r['findings'])} findings")
                elif r.get("status") == "clean":
                    clean += 1

        print(f"\n内容検証: {clean} clean, {len(issue_ids)} with issues")
        return {"issues_count": len(issue_ids), "issue_file_ids": issue_ids}
```

---

## 9. steps/phase_e_fix.py

```python
"""Phase E: Fix

Apply fixes to knowledge files based on validation findings.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

KNOWLEDGE_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "official_doc_urls", "index", "sections"],
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "official_doc_urls": {"type": "array", "items": {"type": "string"}},
        "index": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "hints"],
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "hints": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "sections": {"type": "object", "additionalProperties": {"type": "string"}}
    }
}


class PhaseEFix:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/fix.md"
        )

    def _build_prompt(self, findings, knowledge, source_content, fmt):
        prompt = self.prompt_template
        prompt = prompt.replace("{FINDINGS_JSON}",
                                json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FORMAT}", fmt)
        return prompt

    def fix_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        if not os.path.exists(findings_path):
            return {"status": "skip", "id": file_id}

        findings = load_json(findings_path)
        knowledge = load_json(f"{self.ctx.knowledge_dir}/{file_info['output_path']}")
        source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")

        prompt = self._build_prompt(findings, knowledge, source, file_info["format"])

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=KNOWLEDGE_SCHEMA)
            if result.returncode == 0:
                fixed = json.loads(result.stdout)
                if not self.dry_run:
                    write_json(
                        f"{self.ctx.knowledge_dir}/{file_info['output_path']}", fixed
                    )
                    os.remove(findings_path)
                return {"status": "fixed", "id": file_id}
        except Exception as e:
            return {"status": "error", "id": file_id, "error": str(e)}

        return {"status": "error", "id": file_id}

    def run(self, target_ids) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        target_set = set(target_ids)
        targets = [f for f in classified["files"] if f["id"] in target_set]

        print(f"Fixing {len(targets)} files...")

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.fix_one, fi) for fi in targets]
            fixed = 0
            for future in as_completed(futures):
                r = future.result()
                if r["status"] == "fixed":
                    fixed += 1
                    print(f"  [FIXED] {r['id']}")
                elif r["status"] == "error":
                    print(f"  [ERROR] {r['id']}: {r.get('error','')}")

        print(f"\n修正完了: {fixed}/{len(targets)}")
        return {"fixed": fixed, "total": len(targets)}
```

---

## 10. steps/phase_f_finalize.py

```python
"""Phase F: Finalize

Build index.toon, generate browsable docs, create summary.
"""

import os
import json
import subprocess
from glob import glob
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, write_file, run_claude as _default_run_claude

CLASSIFY_PATTERNS_SCHEMA = {
    "type": "object",
    "required": ["patterns", "reasoning"],
    "properties": {
        "patterns": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "nablarch-batch", "jakarta-batch", "restful-web-service",
                    "http-messaging", "web-application", "mom-messaging", "db-messaging"
                ]
            }
        },
        "reasoning": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["pattern", "matched", "evidence"],
                "properties": {
                    "pattern": {"type": "string"},
                    "matched": {"type": "boolean"},
                    "evidence": {"type": "string"}
                }
            }
        }
    }
}

VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


class PhaseFFinalize:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/classify_patterns.md"
        )

    def _classify_patterns(self, file_info, knowledge) -> str:
        file_id = file_info["id"]
        log_path = f"{self.ctx.log_dir}/classify-patterns/{file_id}.json"

        if os.path.exists(log_path):
            return load_json(log_path).get("patterns", "")

        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{TITLE}", knowledge.get("title", ""))
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=CLASSIFY_PATTERNS_SCHEMA)
            if result.returncode == 0:
                parsed = json.loads(result.stdout)
                patterns = " ".join(parsed.get("patterns", []))
                reasoning = parsed.get("reasoning", [])
                if not self.dry_run:
                    write_json(log_path, {
                        "file_id": file_id, "patterns": patterns, "reasoning": reasoning
                    })
                return patterns
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

        if not self.dry_run:
            write_json(log_path, {"file_id": file_id, "patterns": "", "error": "failed"})
        return ""

    def _build_index_toon(self):
        classified = load_json(self.ctx.classified_list_path)
        entries = []
        to_classify = []

        for fi in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{fi['output_path']}"
            if not os.path.exists(json_path):
                entries.append({
                    "title": fi["id"], "type": fi["type"], "category": fi["category"],
                    "processing_patterns": "", "path": "not yet created"
                })
                continue

            knowledge = load_json(json_path)
            title = knowledge.get("title", fi["id"])

            if fi["type"] == "processing-pattern":
                patterns = fi["category"]
            else:
                to_classify.append((fi, knowledge))
                patterns = None

            entries.append({
                "title": title, "type": fi["type"], "category": fi["category"],
                "processing_patterns": patterns, "path": fi["output_path"],
                "_fi": fi, "_knowledge": knowledge
            })

        if to_classify and not self.dry_run:
            print(f"  Classifying {len(to_classify)} files...")
            with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
                futures = {}
                for fi, knowledge in to_classify:
                    future = executor.submit(self._classify_patterns, fi, knowledge)
                    futures[future] = fi["id"]

                for future in as_completed(futures):
                    fid = futures[future]
                    patterns = future.result()
                    for e in entries:
                        if e.get("_fi", {}).get("id") == fid:
                            e["processing_patterns"] = patterns
                            break

        # Clean up temp fields and write
        for e in entries:
            e.pop("_fi", None)
            e.pop("_knowledge", None)
            if e["processing_patterns"] is None:
                e["processing_patterns"] = ""

        lines = [f"# Nabledge-{self.ctx.version} Knowledge Index", ""]
        lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")
        for e in entries:
            title = e["title"].replace(",", "、")
            fields = [title, e["type"], e["category"], e["processing_patterns"], e["path"]]
            lines.append(f"  {', '.join(fields)}")
        lines.append("")

        if not self.dry_run:
            write_file(self.ctx.index_path, '\n'.join(lines))
            print(f"  Wrote: {self.ctx.index_path} ({len(entries)} entries)")

    def _generate_docs(self):
        classified = load_json(self.ctx.classified_list_path)
        generated = 0

        for fi in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{fi['output_path']}"
            if not os.path.exists(json_path):
                continue

            knowledge = load_json(json_path)
            md_lines = [f"# {knowledge['title']}", ""]
            for entry in knowledge.get("index", []):
                sid = entry["id"]
                md_lines.append(f"## {entry['title']}")
                md_lines.append("")
                md_lines.append(knowledge.get("sections", {}).get(sid, ""))
                md_lines.append("")

            md_path = f"{self.ctx.docs_dir}/{fi['type']}/{fi['category']}/{fi['id']}.md"
            if not self.dry_run:
                write_file(md_path, "\n".join(md_lines))
            generated += 1

        print(f"  Generated {generated} docs")

    def _generate_summary(self):
        log_dir = self.ctx.log_dir

        gen_dir = f"{log_dir}/generate"
        gen_results = []
        if os.path.exists(gen_dir):
            for f in sorted(os.listdir(gen_dir)):
                fp = os.path.join(gen_dir, f)
                if f.endswith(".json") and os.path.isfile(fp):
                    gen_results.append(load_json(fp))

        findings_dir = self.ctx.findings_dir
        total_findings = 0
        files_with_issues = 0
        if os.path.exists(findings_dir):
            for f in sorted(os.listdir(findings_dir)):
                if f.endswith(".json"):
                    data = load_json(os.path.join(findings_dir, f))
                    n = len(data.get("findings", []))
                    total_findings += n
                    if n > 0:
                        files_with_issues += 1

        summary = {
            "version": self.ctx.version,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generate": {
                "total": len(gen_results),
                "ok": sum(1 for r in gen_results if r.get("status") == "ok"),
                "error": sum(1 for r in gen_results if r.get("status") == "error"),
            },
            "content_check": {
                "files_with_issues": files_with_issues,
                "total_findings": total_findings,
            },
        }

        if not self.dry_run:
            write_json(f"{log_dir}/summary.json", summary)
            print(f"  Summary: {log_dir}/summary.json")

    def run(self):
        print("  Building index.toon...")
        self._build_index_toon()

        print("  Generating docs...")
        self._generate_docs()

        print("  Generating summary...")
        self._generate_summary()
```

---

## 11. prompts/generate.md

以下の内容をそのまま `prompts/generate.md` に書き込む。

````markdown
You are an expert in converting Nablarch official documentation to AI-ready knowledge files.

## Task

Convert the source file below into a knowledge file (JSON) by following Work Steps 1–7 in order. Record your decisions in the trace log as you go.

## Source File Information

- File ID: `{FILE_ID}`
- Format: `{FORMAT}` (rst/md/xlsx)
- Type: `{TYPE}`
- Category: `{CATEGORY}`
- Output Path: `{OUTPUT_PATH}`
- Assets Directory: `{ASSETS_DIR}`
- Official Doc Base URL: `{OFFICIAL_DOC_BASE_URL}`

## Source File Content

```
{SOURCE_CONTENT}
```

{ASSETS_SECTION}

## Labels Defined in This File

{INTERNAL_LABELS}

The above lists labels defined as `.. _label_name:` in this source file.
A `:ref:` target is "internal" if it appears in this list; otherwise it is "external."

---

## Work Step 1: Identify the title

Read the source and extract the document title.

- RST: The first heading underlined with `=====`
- MD: The first `#` heading
- Excel: Use the filename as title

Set this as the `title` field.

---

## Work Step 2: Build the section list

Scan the source and create a complete list of sections.

### 2-1. Count split-level headings

| Format | Split-level heading | How to count |
|---|---|---|
| RST | h2 | Text line followed by `-----` underline (3+ dashes) |
| MD | ## | Lines starting with `## ` (not `###` or deeper) |
| Excel | (none) | Entire file = 1 section |

### 2-2. Apply h3 promotion rule (RST only)

For each h2 section, estimate the plain text character count. Exclude code blocks (between `.. code-block::` and next unindented line), directive lines (`.. xxx::`), indented directive body, heading underlines, and blank lines.

| Condition | Action |
|---|---|
| h2 plain text ≥ 2000 chars AND h3 headings (`~~~~~` underline) exist in source | Split at h3. Each h3 becomes a separate section. |
| h2 plain text ≥ 2000 chars AND no h3 headings exist | Keep as one section. Do NOT invent sub-sections. |
| h2 plain text < 2000 chars | Keep as one section. Include h3 content inside the parent. |

### 2-3. Assign section IDs

- Use kebab-case: lowercase, hyphen-separated
- Derive from heading text (e.g., "モジュール一覧" → `module-list`)
- Examples: `overview`, `setup`, `handler-queue`, `error-handling`

### Trace log for Step 2

Record in `trace.sections`:
```json
[
  {
    "section_id": "overview",
    "source_heading": "概要",
    "heading_level": "h2",
    "h3_split": false,
    "h3_split_reason": "plain text 800 chars < 2000 threshold"
  }
]
```
For h3-promoted sections, set `"h3_split": true` and explain the reason (char count).

---

## Work Step 3: Extract section content

For each section from Step 2, extract the corresponding source content and convert to Markdown.

### Extraction priority (MOST IMPORTANT)

| Priority | Rule | Judgment |
|:---:|---|:---:|
| 1 | Information in source is missing from output | **NG (worst)** |
| 2 | Information NOT in source is added to output | **NG** |
| 3 | Information from source is included redundantly | **OK (acceptable)** |

When in doubt, **include it**. Redundant is better than missing.

### What to keep — ALL of these

- Specifications: config items, default values, types, constraints, behavior specs, reasons/background
- Warnings and notes: content of `important`, `warning`, `tip`, `note` directives
- Design philosophy, recommended patterns, cautions
- Code examples and configuration examples (every code block in source)
- Class names, interface names, annotation names
- URLs and links: preserve exactly as they appear in source

### Forbidden — Do NOT do any of these

- Do NOT add explanatory preambles not in source (e.g., "以下の手順があります：", "以下の〜が用意されています：")
- Do NOT infer default values, constraints, or behavior not stated in source
- Do NOT add code examples not in source
- Do NOT remove or modify URLs from source
- Do NOT add "一般的には〜" or "通常は〜" style generalizations

Decision criterion: "Can I point to a specific passage in the source for this sentence?" If NO → do not include it.

### Markdown conversion rules

**Classes/interfaces:**
`**クラス名**: \`nablarch.common.handler.DbConnectionManagementHandler\``
Multiple: `**クラス**: \`Class1\`, \`Class2\``
Annotations: `**アノテーション**: \`@InjectForm\`, \`@OnError\``

**Module dependencies:**
```
**モジュール**:
\```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-jdbc</artifactId>
</dependency>
\```
```

**Property tables:**
```
| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |
```
○ = required, empty = optional. Empty default = no default.

**Alert directives:**
| RST directive | Markdown |
|---|---|
| `.. important::` | `> **重要**: text` |
| `.. tip::` | `> **補足**: text` |
| `.. warning::` | `> **警告**: text` |
| `.. note::` | `> **注意**: text` |

**Process flow:** Use numbered list.

**Handler configuration table:**
```
| No. | ハンドラ | 往路処理 | 復路処理 | 例外処理 |
|---|---|---|---|---|
| 1 | ステータスコード変換ハンドラ | — | ステータスコード変換 | — |
```

**Feature comparison table:**
Legend: ◎ = defined in spec, ○ = provided, △ = partially, × = not provided, — = N/A
Footnotes immediately after the table: `[1] text`

**Image handling:**
| Image type | Action |
|---|---|
| Flow diagrams | Text alternative (numbered list) |
| Architecture/configuration diagrams | Text alternative (definition list) |
| Screen captures | Text alternative (step descriptions) |
| Cannot be replaced with text | `![description](assets/{FILE_ID}/filename.png)` |

Office attachments → reference in `assets/{FILE_ID}/`.

---

## Work Step 4: Convert cross-references

Scan each section's content and convert all RST references using this decision flow:

```
For each reference found in source:

1. Is it :java:extdoc:`...` ?
   → Extract the fully-qualified class name.
   → Convert to Javadoc URL: https://nablarch.github.io/docs/LATEST/javadoc/{package/path/ClassName}.html
   → Add this URL to official_doc_urls (collected in Step 6).
   → In section text, keep only the class name as inline code: `ClassName`

2. Is it an external URL (http:// or https://) ?
   → Keep as-is in Markdown link format: [text](url)

3. Is it :ref:`label` or :ref:`display<label>` ?
   → Is `label` in {INTERNAL_LABELS} ?
     YES (internal reference):
       → Convert to: [display_text](#section-id)
       → section-id = the kebab-case ID from Step 2 that this label points to
     NO (external reference):
       → Convert to: [display_text](@label)

4. Is it :doc:`path` or :doc:`display<path>` ?
   → Convert to: [display_text](@knowledge-file-id)
   → knowledge-file-id = the filename portion of path without extension

5. Is it :download:`display<path>` ?
   → If file was extracted to assets: [display](assets/{FILE_ID}/filename)
   → If not extracted: describe the file in text
```

---

## Work Step 5: Generate search hints

For each section, extract hints by following substeps 5-1 through 5-7. Only include items that actually exist in that section.

### 5-1. Class/interface names
Scan for backtick-wrapped text matching `nablarch.xxx.XxxClass` (package-qualified) or PascalCase names (2+ words, e.g., `DbConnectionManagementHandler`). Add each to hints.

### 5-2. Annotation names
Scan for `@AnnotationName` patterns. Add each to hints.

### 5-3. Exception class names
Scan for names ending in `Exception`. Add each to hints.

### 5-4. Property names
From property tables (rows under `| プロパティ名 |` header), extract the first column values. Add each to hints.

### 5-5. Functional keywords (Japanese)
Write 2–5 Japanese keywords describing what this section enables. (e.g., "データベース接続管理", "トランザクション制御", "バリデーション")

### 5-6. Toctree entries
If the source section contains `.. toctree::` items, add each item name to hints.

### 5-7. h3 heading keywords
If this section contains consolidated h3 subsections (not split), extract key terms from h3 headings and add to hints.

---

## Work Step 6: Build official_doc_urls

1. Start with `{OFFICIAL_DOC_BASE_URL}` as the first URL.
2. Collect all Javadoc URLs extracted in Step 4.
3. Combine into a single array, deduplicated, preserving order.

---

## Work Step 7: Assemble and output JSON

Combine all results from Steps 1–6 into the output JSON.


### Output JSON Schema

```json
{
  "type": "object",
  "required": ["knowledge", "trace"],
  "properties": {
    "knowledge": {
      "type": "object",
      "required": ["id", "title", "official_doc_urls", "index", "sections"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Knowledge file identifier. Must equal FILE_ID."
        },
        "title": {
          "type": "string",
          "description": "Document title from Step 1"
        },
        "official_doc_urls": {
          "type": "array",
          "description": "Official documentation URLs from Step 6",
          "items": { "type": "string" }
        },
        "index": {
          "type": "array",
          "description": "Section table of contents with search hints",
          "items": {
            "type": "object",
            "required": ["id", "title", "hints"],
            "properties": {
              "id": { "type": "string" },
              "title": { "type": "string" },
              "hints": { "type": "array", "items": { "type": "string" } }
            }
          }
        },
        "sections": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        }
      }
    },
    "trace": {
      "type": "object",
      "required": ["sections"],
      "properties": {
        "sections": {
          "type": "array",
          "description": "Section list decisions from Step 2",
          "items": {
            "type": "object",
            "required": ["section_id", "source_heading", "heading_level"],
            "properties": {
              "section_id": { "type": "string" },
              "source_heading": { "type": "string" },
              "heading_level": { "type": "string" },
              "h3_split": { "type": "boolean" },
              "h3_split_reason": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### Final self-checks before output

- [ ] `id` equals `{FILE_ID}`
- [ ] Every `index[].id` has a matching key in `sections` and vice versa
- [ ] All section IDs are kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`)
- [ ] No section content is empty or under 50 characters (unless genuinely "なし")
- [ ] No hints array is empty
- [ ] All internal references `(#section-id)` point to existing section IDs in this file
- [ ] No raw RST markup remains unconverted
- [ ] No information was added that is not in the source
- [ ] All URLs from source are preserved

Output the JSON matching the schema above. No explanation, no markdown fences, no other text.
````

---

## 12. prompts/content_check.md

以下の内容をそのまま `prompts/content_check.md` に書き込む。

````markdown
You are a validator for Nablarch knowledge files.
Your role is to IDENTIFY problems only. Do NOT fix anything.

Compare the knowledge file against the source file and report all findings.

## Source File

- Path: `{SOURCE_PATH}`
- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Knowledge File

- ID: `{FILE_ID}`

```json
{KNOWLEDGE_JSON}
```

---

## Validation Checklist

### V1: Information Omissions (severity: critical)

Scan the source file systematically. For each item found in source, check if it exists in the knowledge file. Report every missing item.

- Property tables: find all rows with プロパティ名, type, default. Check each exists.
- Code blocks: count in source vs knowledge. Report any missing.
- Warning/important/tip/note directives: check each exists.
- Fully-qualified class names and @Annotation names: check each exists.
- URLs (http://, https://): check each preserved.

### V2: Information Fabrication (severity: critical)

For each paragraph in knowledge, trace to source. Flag if no corresponding source passage exists.

Common fabrication patterns:
- "以下の手順があります：", "以下の〜が用意されています："
- Default values not stated in source
- Explanatory sentences not in source

Decision: "Can I point to a specific passage in the source?" If NO → fabrication.

### V3: Section Issues (severity: minor)

- Count split-level headings in source (RST: h2=text+------, MD: ##). Compare with knowledge section count.
- Check if any section has < 50 characters.
- For RST: if h2 has >= 2000 chars plain text AND h3 exists but knowledge doesn't split → report.

### V4: Hints Completeness (severity: minor)

For each section, check hints include:
- PascalCase class names from content
- @Annotation names
- Property names from tables (first column)
- XxxException names

---

## Output

Report all findings as JSON matching the provided schema.
If no issues found, set status to "clean" with empty findings array.
Do NOT attempt to fix anything. Only identify and describe.
````

---

## 13. prompts/fix.md

以下の内容をそのまま `prompts/fix.md` に書き込む。

````markdown
You are a fixer for Nablarch knowledge files.
Apply fixes based on the validation findings below.

## Findings

```json
{FINDINGS_JSON}
```

## Source File

- Format: `{FORMAT}`

```
{SOURCE_CONTENT}
```

## Current Knowledge File

```json
{KNOWLEDGE_JSON}
```

## Instructions

For each finding, apply the fix:
- **omission**: Find the missing information in the source and add it to the correct section.
- **fabrication**: Remove the content that has no corresponding source passage.
- **hints_missing**: Add the missing terms to the section's hints array.
- **section_issue**: Fix the section structure as described in the finding.

After all fixes, verify:
- Every index[].id has a matching key in sections and vice versa
- All section IDs are kebab-case
- No section content is empty

Output the entire corrected knowledge file JSON matching the provided schema.
````

---

## 14. prompts/classify_patterns.md

以下の内容をそのまま `prompts/classify_patterns.md` に書き込む。

````markdown
You are an expert in classifying Nablarch processing patterns.

## Task

Read the knowledge file content below and determine which processing patterns are relevant. Record your reasoning for each pattern decision.

## Work Steps

### Step 1: Read the knowledge file

Read the knowledge file content. Focus on:
- Which processing architectures are mentioned (batch, web, REST, messaging, etc.)
- Which handler queues or request paths are described
- Whether the content is specific to one pattern or applies across multiple

### Step 2: Match against valid patterns

Check the content against each valid pattern using these indicators:

| Pattern | Match if content mentions... |
|---|---|
| nablarch-batch | Nablarchバッチ, 都度起動, 常駐型, BatchAction, DataReader, nablarch.fw.action.BatchAction |
| jakarta-batch | Jakarta Batch, JSR 352, jBatch, Batchlet, Chunk, javax.batch |
| restful-web-service | RESTful, JAX-RS, REST API, @Produces, @Consumes, JaxRsMethodBinder |
| http-messaging | HTTPメッセージング, HTTP受信, メッセージ同期応答, HttpMessagingRequestParsingHandler |
| web-application | Webアプリケーション, サーブレット, JSP, HttpRequest, セッション管理 |
| mom-messaging | MOMメッセージング, MQ, キュー, 非同期メッセージ, MomMessagingAction |
| db-messaging | DB連携メッセージング, テーブルキュー, 電文, DatabaseRecordReader |

For each pattern, record whether it matched and what evidence was found (or why it did not match).

### Step 3: Apply classification rules

1. If the content explicitly mentions a pattern from Step 2 → include it.
2. If the content is a generic library (e.g., Universal DAO, database access) used across multiple patterns → include ONLY patterns that are explicitly mentioned in the content. Do NOT assume all patterns apply.
3. If no pattern is mentioned at all → return empty array.
4. Do NOT infer patterns not written in the content.

## Knowledge File Information

- ID: `{FILE_ID}`
- Title: `{TITLE}`
- Type: `{TYPE}`
- Category: `{CATEGORY}`

## Knowledge File Content

```json
{KNOWLEDGE_JSON}
```

Output the result as JSON matching the provided schema.
````

---

## 15. テスト

### tests/fixtures/sample_source.rst

```rst
.. _sample-label:

サンプルハンドラ
==========================================

概要
-----

サンプルハンドラは、データベース接続を管理するハンドラである。

.. important::
   本ハンドラはハンドラキューの先頭付近に配置すること。

**クラス**: `nablarch.sample.SampleHandler`

モジュール一覧
---------------

.. code-block:: xml

   <dependency>
     <groupId>com.nablarch.framework</groupId>
     <artifactId>nablarch-sample</artifactId>
   </dependency>

.. list-table::
   :header-rows: 1

   * - プロパティ名
     - 型
     - 必須
     - デフォルト値
     - 説明
   * - sampleProperty
     - String
     - ○
     -
     - サンプルプロパティ
   * - timeout
     - int
     -
     - 30
     - タイムアウト(秒)
```

### tests/fixtures/sample_knowledge.json

```json
{
  "id": "handlers-sample-handler",
  "title": "サンプルハンドラ",
  "official_doc_urls": [
    "https://nablarch.github.io/docs/LATEST/doc/application_framework/handlers/sample.html"
  ],
  "index": [
    {
      "id": "overview",
      "title": "概要",
      "hints": ["SampleHandler", "nablarch.sample.SampleHandler", "データベース接続管理"]
    },
    {
      "id": "module-list",
      "title": "モジュール一覧",
      "hints": ["nablarch-sample", "sampleProperty", "timeout"]
    }
  ],
  "sections": {
    "overview": "サンプルハンドラは、データベース接続を管理するハンドラである。\n\n> **重要**: 本ハンドラはハンドラキューの先頭付近に配置すること。\n\n**クラス**: `nablarch.sample.SampleHandler`",
    "module-list": "```xml\n<dependency>\n  <groupId>com.nablarch.framework</groupId>\n  <artifactId>nablarch-sample</artifactId>\n</dependency>\n```\n\n| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |\n|---|---|---|---|---|\n| sampleProperty | String | ○ | | サンプルプロパティ |\n| timeout | int | | 30 | タイムアウト(秒) |"
  }
}
```

### tests/fixtures/sample_classified.json

```json
{
  "version": "6",
  "generated_at": "2026-01-01T00:00:00Z",
  "files": [
    {
      "source_path": "tests/fixtures/sample_source.rst",
      "format": "rst",
      "filename": "sample.rst",
      "type": "component",
      "category": "handlers",
      "id": "handlers-sample-handler",
      "output_path": "component/handlers/handlers-sample-handler.json",
      "assets_dir": "component/handlers/assets/handlers-sample-handler/"
    }
  ]
}
```

### tests/conftest.py

```python
import os
import sys
import json
import shutil
import pytest
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOL_DIR)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f) if name.endswith(".json") else f.read()


def make_mock_run_claude(generate_output=None, findings_output=None,
                         fix_output=None, classify_output=None):
    """Generate a mock run_claude function.

    Determines which Phase is calling by inspecting json_schema content.
    Returns the corresponding mock output.
    """
    default_knowledge = load_fixture("sample_knowledge.json")

    _generate = generate_output or {
        "knowledge": default_knowledge,
        "trace": {
            "sections": [
                {"section_id": "overview", "source_heading": "概要",
                 "heading_level": "h2", "h3_split": False,
                 "h3_split_reason": "800 chars < 2000"},
                {"section_id": "module-list", "source_heading": "モジュール一覧",
                 "heading_level": "h2", "h3_split": False,
                 "h3_split_reason": "600 chars < 2000"}
            ]
        }
    }
    _findings = findings_output or {
        "file_id": "handlers-sample-handler",
        "status": "clean",
        "findings": []
    }
    _fix = fix_output or default_knowledge
    _classify = classify_output or {
        "patterns": [],
        "reasoning": [
            {"pattern": "nablarch-batch", "matched": False,
             "evidence": "No batch content"}
        ]
    }

    def mock_fn(prompt, timeout=600, json_schema=None):
        schema_str = json.dumps(json_schema) if json_schema else ""
        if "trace" in schema_str:
            output = _generate
        elif "findings" in schema_str:
            output = _findings
        elif "reasoning" in schema_str:
            output = _classify
        else:
            output = _fix

        return subprocess.CompletedProcess(
            args=["claude", "-p"], returncode=0,
            stdout=json.dumps(output, ensure_ascii=False), stderr=""
        )

    return mock_fn


@pytest.fixture
def test_repo(tmp_path):
    """Build a temporary repo with classified.json and source file."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Source file
    src_dir = repo / "tests" / "fixtures"
    src_dir.mkdir(parents=True)
    shutil.copy(os.path.join(FIXTURES_DIR, "sample_source.rst"), src_dir / "sample_source.rst")

    # classified.json
    log_dir = repo / "tools" / "knowledge-creator" / "logs" / "v6"
    log_dir.mkdir(parents=True)
    classified = load_fixture("sample_classified.json")
    with open(log_dir / "classified.json", "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    # knowledge directory
    (repo / ".claude" / "skills" / "nabledge-6" / "knowledge" / "component" / "handlers").mkdir(parents=True)

    # prompts directory - copy real prompts
    prompts_dir = repo / "tools" / "knowledge-creator" / "prompts"
    prompts_dir.mkdir(parents=True)
    real_prompts = os.path.join(TOOL_DIR, "prompts")
    if os.path.exists(real_prompts):
        for f in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, f), prompts_dir / f)

    return str(repo)


@pytest.fixture
def ctx(test_repo):
    # Import Context from run.py
    sys.path.insert(0, TOOL_DIR)
    from run import Context
    return Context(version="6", repo=test_repo, concurrency=1)


@pytest.fixture
def mock_claude():
    return make_mock_run_claude()
```

### tests/test_pipeline.py

```python
"""End-to-end pipeline tests with mocked claude -p."""
import os
import json
import pytest
from conftest import make_mock_run_claude, load_fixture


class TestPipelineBCD:
    """Phase B -> C -> D pipeline."""

    def test_generate_and_validate_clean(self, ctx, mock_claude):
        """Normal flow: generate -> structure pass -> content clean."""
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_c_structure_check import PhaseCStructureCheck
        from steps.phase_d_content_check import PhaseDContentCheck

        # Phase B
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
        )
        assert os.path.exists(knowledge_path)
        knowledge = json.load(open(knowledge_path, encoding="utf-8"))
        assert knowledge["id"] == "handlers-sample-handler"
        assert len(knowledge["sections"]) == 2
        assert "overview" in knowledge["sections"]
        assert "module-list" in knowledge["sections"]

        # Trace
        trace_path = os.path.join(ctx.trace_dir, "handlers-sample-handler.json")
        assert os.path.exists(trace_path)
        trace = json.load(open(trace_path, encoding="utf-8"))
        assert len(trace["sections"]) == 2

        # Phase C
        c_result = PhaseCStructureCheck(ctx).run()
        assert c_result["error_count"] == 0
        assert "handlers-sample-handler" in c_result["pass_ids"]

        # Phase D
        d_result = PhaseDContentCheck(ctx, run_claude_fn=mock_claude).run(
            target_ids=c_result["pass_ids"]
        )
        assert d_result["issues_count"] == 0

    def test_fix_cycle(self, ctx):
        """Fix flow: generate -> check finds issues -> fix -> recheck clean."""
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_c_structure_check import PhaseCStructureCheck
        from steps.phase_d_content_check import PhaseDContentCheck
        from steps.phase_e_fix import PhaseEFix

        # B: generate
        PhaseBGenerate(ctx, run_claude_fn=make_mock_run_claude()).run()

        # C: pass
        c = PhaseCStructureCheck(ctx).run()
        assert c["error_count"] == 0

        # D: finds issues
        findings_with_issues = {
            "file_id": "handlers-sample-handler",
            "status": "has_issues",
            "findings": [{
                "category": "omission", "severity": "critical",
                "location": "overview",
                "description": "Missing important directive",
                "source_evidence": "line 10"
            }]
        }
        d = PhaseDContentCheck(
            ctx, run_claude_fn=make_mock_run_claude(findings_output=findings_with_issues)
        ).run(target_ids=c["pass_ids"])
        assert d["issues_count"] == 1

        # Findings file exists
        findings_path = os.path.join(ctx.findings_dir, "handlers-sample-handler.json")
        assert os.path.exists(findings_path)

        # E: fix
        PhaseEFix(ctx, run_claude_fn=make_mock_run_claude()).run(
            target_ids=d["issue_file_ids"]
        )

        # Findings cache deleted
        assert not os.path.exists(findings_path)

        # D again: clean
        d2 = PhaseDContentCheck(
            ctx, run_claude_fn=make_mock_run_claude()
        ).run(target_ids=c["pass_ids"])
        assert d2["issues_count"] == 0


class TestPhaseF:
    def test_finalize(self, ctx, mock_claude):
        from steps.phase_b_generate import PhaseBGenerate
        from steps.phase_f_finalize import PhaseFFinalize

        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()
        PhaseFFinalize(ctx, run_claude_fn=mock_claude).run()

        # index.toon
        assert os.path.exists(ctx.index_path)
        content = open(ctx.index_path, encoding="utf-8").read()
        assert "handlers-sample-handler" in content

        # docs
        doc_path = os.path.join(
            ctx.docs_dir, "component/handlers/handlers-sample-handler.md"
        )
        assert os.path.exists(doc_path)

        # summary
        summary_path = os.path.join(ctx.log_dir, "summary.json")
        assert os.path.exists(summary_path)
```

### tests/test_phase_c.py

```python
"""Phase C structure validation unit tests. No AI, runs fast."""
import os
import json
import pytest
from conftest import load_fixture


def write_knowledge(ctx, knowledge):
    path = os.path.join(
        ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json"
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    return path


class TestStructureValidation:

    def test_valid_passes(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        assert PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst") == []

    def test_s3_index_without_section(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        del k["sections"]["overview"]
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S3" in e for e in errors)

    def test_s4_section_without_index(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["orphan"] = "content"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S4" in e for e in errors)

    def test_s5_non_kebab(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["index"].append({"id": "badCamel", "title": "Bad", "hints": ["x"]})
        k["sections"]["badCamel"] = "content"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S5" in e for e in errors)

    def test_s6_empty_hints(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["index"][0]["hints"] = []
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S6" in e for e in errors)

    def test_s7_empty_section(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["sections"]["overview"] = ""
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S7" in e for e in errors)

    def test_s8_id_mismatch(self, ctx):
        from steps.phase_c_structure_check import PhaseCStructureCheck
        k = load_fixture("sample_knowledge.json")
        k["id"] = "wrong-id"
        jp = write_knowledge(ctx, k)
        sp = os.path.join(ctx.repo, "tests/fixtures/sample_source.rst")
        errors = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert any("S8" in e for e in errors)
```

---

## 実装順序

```
1. ディレクトリ構造を作る
2. requirements.txt + pytest.ini
3. steps/__init__.py (空)
4. steps/common.py
5. tests/fixtures/ (3ファイル)
6. tests/__init__.py (空)
7. tests/conftest.py
8. run.py
9. step2_classify.py を旧ブランチからコピー
   git fetch origin 99-nabledge-creator-tool
   git show origin/99-nabledge-creator-tool:tools/knowledge-creator/steps/step2_classify.py > ...
10. step1_list_sources.py (本ドキュメントのセクション3)
11. test-files.json を旧ブランチからコピー
    git show origin/99-nabledge-creator-tool:tools/knowledge-creator/test-files.json > ...
12. phase_c_structure_check.py
    → python -m pytest tests/test_phase_c.py -v
13. phase_b_generate.py
14. prompts/generate.md (セクション11の内容をそのまま書き込む)
    → python -m pytest tests/test_pipeline.py::TestPipelineBCD::test_generate_and_validate_clean -v
15. phase_d_content_check.py + prompts/content_check.md
    → python -m pytest tests/test_pipeline.py::TestPipelineBCD -v
16. phase_e_fix.py + prompts/fix.md
    → python -m pytest tests/test_pipeline.py::TestPipelineBCD::test_fix_cycle -v
17. phase_f_finalize.py + prompts/classify_patterns.md
    → python -m pytest tests/test_pipeline.py::TestPhaseF -v
18. 全テスト
    → python -m pytest tests/ -v
```

各ステップの `→` で示したテストがパスしてから次に進むこと。
