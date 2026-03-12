# タスク: Findings履歴管理（ラウンド番号付きファイル）

## 目的

Phase D/Eの検証→修正ループでfindingsの履歴を保持する。現状はPhase Eが修正後にfindingsファイルを削除（`os.remove`）するため、どのラウンドで何が検出され、何が修正されたかの追跡ができない。

## 設計

**ファイル名規則**: `{file_id}_r{round_num}.json`

- Phase D（検証）: `findings_dir/{file_id}_r1.json` を出力
- Phase E（修正）: `findings_dir/{file_id}_r1.json` を読む。**削除しない**
- Round 2: Phase D → `_r2.json` 出力、Phase E → `_r2.json` を読む
- 全ラウンドのfindingsファイルが残る

**ラウンド番号**: run.pyのD/Eループの`round_num`をそのまま使う。

## 前提

- ブランチ: `153-verify-r2-fabrication` を `origin/main` にリベースして作業
- 作業ディレクトリ: `tools/knowledge-creator/`
- ベースライン: 154 passed, 7 skipped
- **実行順**: Task 1 → 2 → 3 → 4 → 5 → 6 → 7（順序厳守）

## 変更対象ファイル

| ファイル | 変更内容 |
|---|---|
| `scripts/phase_d_content_check.py` | round_num引数追加、findings_pathにラウンド番号付与 |
| `scripts/phase_e_fix.py` | round_num引数追加、指定ラウンドのfindings読み込み、削除廃止 |
| `scripts/run.py` | Phase D/Eにround_num渡し、_aggregate_findingsをラウンド対応 |
| `scripts/cleaner.py` | findingsファイルのglob対応 |
| `tests/ut/test_findings_rounds.py` | 新規テストファイル |
| `tests/ut/test_cleaner.py` | 既存テストのファイル名パターン更新 |

---

## Task 1: テスト作成（RED）

**ファイル**: `tests/ut/test_findings_rounds.py` を新規作成

```python
"""Findings round history tests for Phase D/E."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from conftest import make_mock_run_claude
from common import load_json, write_json


class TestPhaseDRoundOutput:
    """Phase D outputs findings with round number in filename."""

    def test_check_one_writes_round_file(self, ctx):
        """check_one writes {file_id}_r{N}.json, not {file_id}.json."""
        from phase_d_content_check import PhaseDContentCheck

        findings_output = {
            "file_id": "test-file",
            "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "test"}]
        }
        mock = make_mock_run_claude(findings_output=findings_output)
        checker = PhaseDContentCheck(ctx, run_claude_fn=mock)
        checker.round_num = 1

        file_info = {
            "id": "test-file",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/test-file.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("test source")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {"id": "test-file", "title": "Test", "index": [], "sections": {}})

        result = checker.check_one(file_info)

        round_path = f"{ctx.findings_dir}/test-file_r1.json"
        assert os.path.exists(round_path), f"Expected {round_path}"
        old_path = f"{ctx.findings_dir}/test-file.json"
        assert not os.path.exists(old_path), f"Old-style {old_path} should not exist"
        data = load_json(round_path)
        assert data["file_id"] == "test-file"
        assert data["status"] == "has_issues"

    def test_check_one_skips_if_round_file_exists(self, ctx):
        """check_one returns cached result if _r{N}.json already exists."""
        from phase_d_content_check import PhaseDContentCheck

        checker = PhaseDContentCheck(ctx, dry_run=True)
        checker.round_num = 2

        os.makedirs(ctx.findings_dir, exist_ok=True)
        cached = {"file_id": "cached-file", "status": "clean", "findings": []}
        write_json(f"{ctx.findings_dir}/cached-file_r2.json", cached)

        file_info = {"id": "cached-file", "source_path": "x", "output_path": "x", "format": "rst"}
        result = checker.check_one(file_info)
        assert result["status"] == "clean"

    def test_round_2_does_not_reuse_round_1(self, ctx):
        """Round 2 check creates new file even if round 1 exists."""
        from phase_d_content_check import PhaseDContentCheck

        findings_output = {
            "file_id": "multi-round",
            "status": "clean",
            "findings": []
        }
        mock = make_mock_run_claude(findings_output=findings_output)
        checker = PhaseDContentCheck(ctx, run_claude_fn=mock)
        checker.round_num = 2

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/multi-round_r1.json", {
            "file_id": "multi-round", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "old"}]
        })

        file_info = {
            "id": "multi-round",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/multi-round.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("test")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {"id": "multi-round", "title": "T", "index": [], "sections": {}})

        result = checker.check_one(file_info)

        assert os.path.exists(f"{ctx.findings_dir}/multi-round_r1.json")
        assert os.path.exists(f"{ctx.findings_dir}/multi-round_r2.json")
        r1 = load_json(f"{ctx.findings_dir}/multi-round_r1.json")
        assert r1["status"] == "has_issues"


class TestPhaseEPreservesHistory:
    """Phase E reads round-specific findings and does NOT delete them."""

    def test_fix_one_reads_round_file(self, ctx):
        """fix_one reads {file_id}_r{N}.json."""
        from phase_e_fix import PhaseEFix

        fixed_output = {
            "id": "fix-target", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": [], "index": [], "sections": {"s1": "fixed content here that is long enough"}
        }
        mock = make_mock_run_claude(fix_output=fixed_output)
        fixer = PhaseEFix(ctx, run_claude_fn=mock)
        fixer.round_num = 1

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/fix-target_r1.json", {
            "file_id": "fix-target", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": "s1", "description": "missing info"}]
        })

        file_info = {
            "id": "fix-target",
            "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
            "output_path": "component/handlers/fix-target.json",
            "format": "rst",
        }
        src = f"{ctx.repo}/{file_info['source_path']}"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write("source content")
        kpath = f"{ctx.knowledge_cache_dir}/{file_info['output_path']}"
        os.makedirs(os.path.dirname(kpath), exist_ok=True)
        write_json(kpath, {
            "id": "fix-target", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": [], "index": [], "sections": {"s1": "original content here that is long enough"}
        })

        result = fixer.fix_one(file_info)
        assert result["status"] == "fixed"
        assert os.path.exists(f"{ctx.findings_dir}/fix-target_r1.json")

    def test_fix_one_skips_if_no_round_file(self, ctx):
        """fix_one returns skip if _r{N}.json does not exist."""
        from phase_e_fix import PhaseEFix

        fixer = PhaseEFix(ctx, dry_run=True)
        fixer.round_num = 1

        file_info = {"id": "no-findings", "source_path": "x", "output_path": "x", "format": "rst"}
        result = fixer.fix_one(file_info)
        assert result["status"] == "skip"


class TestCleanerRoundFiles:
    """Cleaner handles round-numbered findings files."""

    def test_list_d_artifacts_with_rounds(self, ctx):
        """list_d_artifacts finds _r{N}.json files for target."""
        from cleaner import list_d_artifacts

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target_r1.json", {})
        write_json(f"{ctx.findings_dir}/target_r2.json", {})
        write_json(f"{ctx.findings_dir}/other_r1.json", {})

        result = list_d_artifacts(ctx, target_ids=["target"])
        assert len(result) == 2
        assert all("target_r" in p for p in result)

    def test_list_d_artifacts_returns_dir_when_no_target(self, ctx):
        """list_d_artifacts returns dir itself when target_ids is None."""
        from cleaner import list_d_artifacts

        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a_r1.json", {})

        result = list_d_artifacts(ctx, target_ids=None)
        assert len(result) == 1
        assert result[0] == ctx.findings_dir


class TestAggregateFindings:
    """_aggregate_findings collects findings for a specific round."""

    def test_aggregate_specific_round(self, ctx):
        """Aggregates only the specified round's findings."""
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/file-a_r1.json", {
            "file_id": "file-a", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "r1 finding"}]
        })
        write_json(f"{ctx.findings_dir}/file-a_r2.json", {
            "file_id": "file-a", "status": "clean", "findings": []
        })
        write_json(f"{ctx.findings_dir}/file-b_r1.json", {
            "file_id": "file-b", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor",
                          "location": "s2", "description": "r1 finding"}]
        })

        sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))
        from run import _aggregate_findings
        result = _aggregate_findings(ctx, round_num=1)
        assert result["total"] == 2
        assert result["critical"] == 1
        assert result["minor"] == 1

        result2 = _aggregate_findings(ctx, round_num=2)
        assert result2["total"] == 0

    def test_aggregate_without_round_uses_latest(self, ctx):
        """Without round_num, aggregates latest round per file."""
        os.makedirs(ctx.findings_dir, exist_ok=True)
        # file-a: r1 has issues, r2 clean → latest is r2 (clean)
        write_json(f"{ctx.findings_dir}/file-a_r1.json", {
            "file_id": "file-a", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical",
                          "location": "s1", "description": "old"}]
        })
        write_json(f"{ctx.findings_dir}/file-a_r2.json", {
            "file_id": "file-a", "status": "clean", "findings": []
        })
        # file-b: only r1 with issues → latest is r1
        write_json(f"{ctx.findings_dir}/file-b_r1.json", {
            "file_id": "file-b", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "minor",
                          "location": "s2", "description": "still there"}]
        })

        from run import _aggregate_findings
        result = _aggregate_findings(ctx)
        # file-a r2 is clean (0 findings), file-b r1 has 1 finding → total 1
        assert result["total"] == 1
        assert result["minor"] == 1
```

### 検証（RED）

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_findings_rounds.py -q --tb=short 2>&1 | tail -20
# 期待: 全テストFAIL（実装がまだないため）
```

---

## Task 2: Phase D — round_num対応

**ファイル**: `scripts/phase_d_content_check.py`

### Step 2-1: `__init__`にround_num追加

L46付近、`self.logger = get_logger()`の後に追加:

```python
        self.round_num = 1  # default; overridden by run()
```

### Step 2-2: `check_one`のfindings_path変更

L99-103を変更:

変更前:
```python
    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        self.logger = get_logger()
        if os.path.exists(findings_path):
            return load_json(findings_path)
```

変更後:
```python
    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num}.json"

        self.logger = get_logger()
        if os.path.exists(findings_path):
            return load_json(findings_path)
```

### Step 2-3: `run()`にround_num引数追加

L140を変更:

変更前:
```python
    def run(self, target_ids=None) -> dict:
```

変更後:
```python
    def run(self, target_ids=None, round_num=1) -> dict:
```

`run()`メソッド内、`os.makedirs(self.ctx.findings_dir, exist_ok=True)` の前に追加:

```python
        self.round_num = round_num
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_findings_rounds.py::TestPhaseDRoundOutput -q --tb=short
# 期待: 3 passed
```

---

## Task 3: Phase E — round_num対応、削除廃止

**ファイル**: `scripts/phase_e_fix.py`

### Step 3-1: `__init__`にround_num追加

L44付近、`self.logger = get_logger()`の後に追加:

```python
        self.round_num = 1  # default; overridden by run()
```

### Step 3-2: `fix_one`のfindings_path変更

L59を変更:

変更前:
```python
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"
```

変更後:
```python
        findings_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num}.json"
```

### Step 3-3: `os.remove(findings_path)` を削除

L100の1行を削除:

```python
                    os.remove(findings_path)  # ← この行を削除
```

### Step 3-4: `run()`にround_num引数追加

L107を変更:

変更前:
```python
    def run(self, target_ids) -> dict:
```

変更後:
```python
    def run(self, target_ids, round_num=1) -> dict:
```

`run()`メソッド内、`self.logger.info(f"Fixing ...` の前に追加:

```python
        self.round_num = round_num
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_findings_rounds.py::TestPhaseEPreservesHistory -q --tb=short
# 期待: 2 passed
```

---

## Task 4: run.py — round_num渡しと_aggregate_findings対応

**ファイル**: `scripts/run.py`

### Step 4-1: Phase Dにround_num渡し (L405付近)

変更前:
```python
            d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                target_ids=effective_ids
            )
```

変更後:
```python
            d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                target_ids=effective_ids, round_num=round_num
            )
```

### Step 4-2: _aggregate_findings呼び出しにround_num渡し (L408付近)

変更前:
```python
            findings_summary = _aggregate_findings(ctx)
```

変更後:
```python
            findings_summary = _aggregate_findings(ctx, round_num=round_num)
```

### Step 4-3: Phase Eにround_num渡し (L431付近)

変更前:
```python
                e_result = PhaseEFix(ctx, dry_run=args.dry_run).run(
                    target_ids=d_result["issue_file_ids"]
                )
```

変更後:
```python
                e_result = PhaseEFix(ctx, dry_run=args.dry_run).run(
                    target_ids=d_result["issue_file_ids"], round_num=round_num
                )
```

### Step 4-4: _aggregate_findingsをラウンド対応 (L468付近)

変更前:
```python
def _aggregate_findings(ctx) -> dict:
    """phase-d/findings/*.json を走査して findings サマリーを集計する。"""
    import glob
    findings_dir = ctx.findings_dir
    total = critical = minor = 0
    by_category = {}

    for path in glob.glob(os.path.join(findings_dir, "*.json")):
```

変更後:
```python
def _aggregate_findings(ctx, round_num=None) -> dict:
    """phase-d/findings/*_r{N}.json を走査して findings サマリーを集計する。

    round_num指定時: そのラウンドのファイルのみ集計。
    round_num未指定時: ファイルごとに最新ラウンドのみ集計。
    """
    import glob as _g
    import re as _re
    findings_dir = ctx.findings_dir
    total = critical = minor = 0
    by_category = {}

    if round_num is not None:
        pattern = os.path.join(findings_dir, f"*_r{round_num}.json")
        paths = _g.glob(pattern)
    else:
        # Collect latest round per file_id
        all_paths = _g.glob(os.path.join(findings_dir, "*_r*.json"))
        latest = {}  # file_id -> (round_num, path)
        for path in all_paths:
            m = _re.search(r'_r(\d+)\.json$', path)
            if not m:
                continue
            rn = int(m.group(1))
            base = os.path.basename(path)
            fid = base[:base.rfind(f"_r{rn}")]
            if fid not in latest or rn > latest[fid][0]:
                latest[fid] = (rn, path)
        paths = [path for _, path in latest.values()]

    for path in paths:
```

### Step 4-5: _publish_reportsのfindings glob対応 (L555付近)

変更前:
```python
    # Phase D findings (latest state per file)
    d_findings_map = {}
    for path in _glob.glob(os.path.join(ctx.findings_dir, '*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fdata = json.load(f)
            fid = fdata.get('file_id') or os.path.splitext(os.path.basename(path))[0]
            d_findings_map[fid] = fdata
        except (json.JSONDecodeError, OSError):
            pass
```

変更後:
```python
    # Phase D findings (latest round per file)
    d_findings_map = {}
    import re as _re
    for path in _glob.glob(os.path.join(ctx.findings_dir, '*_r*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fdata = json.load(f)
            # Extract file_id and round number from filename
            base = os.path.splitext(os.path.basename(path))[0]
            m = _re.search(r'^(.+)_r(\d+)$', base)
            if m:
                fid = m.group(1)
                rn = int(m.group(2))
            else:
                fid = fdata.get('file_id', base)
                rn = 0
            # Keep only the latest round per file_id
            if fid not in d_findings_map or rn > d_findings_map[fid][0]:
                d_findings_map[fid] = (rn, fdata)
        except (json.JSONDecodeError, OSError):
            pass
    d_findings_map = {fid: fdata for fid, (_, fdata) in d_findings_map.items()}
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_findings_rounds.py::TestAggregateFindings -q --tb=short
# 期待: 2 passed
```

---

## Task 5: cleaner.py — ラウンドファイル対応

**ファイル**: `scripts/cleaner.py`

L86-89付近を変更:

変更前:
```python
    if target_ids:
        for file_id in target_ids:
            p = f"{ctx.findings_dir}/{file_id}.json"
            if os.path.exists(p):
                paths.append(p)
```

変更後:
```python
    if target_ids:
        import glob
        for file_id in target_ids:
            matches = sorted(glob.glob(f"{ctx.findings_dir}/{file_id}_r*.json"))
            paths.extend(matches)
```

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/test_findings_rounds.py::TestCleanerRoundFiles -q --tb=short
# 期待: 2 passed
```

---

## Task 6: 既存テスト修正

`test_cleaner.py`のfindings関連テストが旧ファイル名`{file_id}.json`を使っている箇所を`{file_id}_r1.json`に更新する。

```bash
cd tools/knowledge-creator
# 全テストを実行して失敗を確認
python -m pytest tests/ut/ -q --tb=short 2>&1 | grep FAILED
```

失敗したテストの`{file_id}.json`を`{file_id}_r1.json`に変更する。具体的な対象箇所:

- `test_cleaner.py` L13: `f"{ctx.findings_dir}/a.json"` → `f"{ctx.findings_dir}/a_r1.json"`
- `test_cleaner.py` L27-28: `target.json`, `other.json` → `target_r1.json`, `other_r1.json`
- `test_cleaner.py` L86-87: `a.json`, `b.json` → `a_r1.json`, `b_r1.json`
- `test_cleaner.py` L93-95: `target.json`, `keep.json` → `target_r1.json`, `keep_r1.json`
- `test_cleaner.py` L98-99: 対応するassertのファイル名も同様に更新
- `test_cleaner.py` L124: `handlers-sample-handler.json` → `handlers-sample-handler_r1.json`

### 検証

```bash
cd tools/knowledge-creator
python -m pytest tests/ut/ -q
# 期待: 154+ passed (既存 + 新規9件), 7 skipped, 0 failed
```

---

## Task 7: 最終検証

```bash
cd tools/knowledge-creator

echo "=== All UT ===" && python -m pytest tests/ut/ -q

echo "=== Findings round tests ===" && python -m pytest tests/ut/test_findings_rounds.py -v

echo "=== verify_integrity ===" && python scripts/verify_integrity.py
```

### 期待結果

- 全UT: 163 passed (既存154 + 新規9), 7 skipped, 0 failed
- test_findings_rounds.py: 9 passed
- verify_integrity.py: 0 FAIL

### コミット

```
feat: preserve findings history with round-numbered files

- Phase D outputs findings as {file_id}_r{round_num}.json
- Phase E reads round-specific findings and does NOT delete them
- _aggregate_findings accepts round_num; without it, uses latest round per file
- _publish_reports uses latest round per file_id (numeric sort)
- cleaner handles round-numbered findings files

All rounds' findings are preserved for tracking D/E loop progress.
Part of #153
```
