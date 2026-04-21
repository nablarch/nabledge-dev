# nc.sh ユースケース対応 実装タスク

## ゴール

`tools/knowledge-creator/` に以下を追加し、ユースケースごとのコマンドで知識ファイルの生成・再生成・品質改善を実行できるようにする。

1. `nc.sh` — ユーザー向けラッパースクリプト
2. `run.py` への新規オプション追加（`--clean-phase`, `--target`, `--yes`, `--regen`）
3. `steps/cleaner.py` — フェーズ別成果物クリーン
4. `steps/source_tracker.py` — ソース変更検知
5. `clean.py` への `--yes` オプション追加

---

## ブランチ

```bash
git checkout 106-nabledge-creator-tool
```

---

## ユースケース一覧（最終形）

| UC | ユースケース | コマンド | nc.shが実行する処理 |
|----|------------|---------|-------------------|
| 1 | 初回の全件生成 | `./nc.sh gen 6` | `clean.py --version 6 --yes` → `run.py --version 6` |
| 2 | 中断からの再開 | `./nc.sh gen 6 --resume` | `run.py --version 6` |
| 3 | ソース変更への追随 | `./nc.sh regen 6` | `run.py --version 6 --regen --yes` |
| 4 | 特定ファイルの再生成 | `./nc.sh regen 6 --target FILE_ID` | `run.py --version 6 --phase BCDEM --clean-phase BD --target FILE_ID --yes` |
| 5 | 品質改善（全件） | `./nc.sh fix 6` | `run.py --version 6 --phase CDEM --clean-phase D --yes` |
| 6 | 品質改善（特定ファイル） | `./nc.sh fix 6 --target FILE_ID` | `run.py --version 6 --phase CDEM --clean-phase D --target FILE_ID --yes` |

---

## 完成時のファイル構成（差分のみ）

```
tools/knowledge-creator/
  nc.sh                          # 新規
  run.py                         # 変更
  clean.py                       # 変更
  steps/
    cleaner.py                   # 新規
    source_tracker.py            # 新規
  tests/
    test_cleaner.py              # 新規
    test_source_tracker.py       # 新規
    test_target_filter.py        # 新規
    test_nc_sh.py                # 新規
```

---

## 実装順序

TDD で進める。各ステップで「テストファイル作成 → テスト実行（RED） → 実装 → テスト実行（GREEN）」の順。

| Step | 内容 | 新規/変更ファイル | テストファイル | 完了条件 |
|------|------|-----------------|--------------|---------|
| 1 | cleaner.py | `steps/cleaner.py` | `tests/test_cleaner.py` | テスト全パス |
| 2 | source_tracker.py | `steps/source_tracker.py` | `tests/test_source_tracker.py` | テスト全パス |
| 3 | Phase B に target_ids 追加 | `steps/phase_b_generate.py` | `tests/test_target_filter.py` | テスト全パス + 既存テスト回帰パス |
| 4 | run.py 新オプション統合 | `run.py` | `tests/test_target_filter.py` に追加 | テスト全パス + 既存テスト回帰パス |
| 5 | clean.py --yes 追加 | `clean.py` | 手動確認 | `clean.py --version 6 --yes` が確認なしで実行される |
| 6 | nc.sh 作成 | `nc.sh` | `tests/test_nc_sh.py` | テスト全パス |
| 7 | 全テスト回帰確認 | - | 全テスト | `python -m pytest tools/knowledge-creator/tests/ -v` 全パス |

---

## Step 1: steps/cleaner.py

### テストファイル: tests/test_cleaner.py

最初にこのファイルを作成し、テストが RED になることを確認してから実装する。

```python
"""Tests for steps/cleaner.py"""
import os
import pytest
from steps.common import write_json, load_json
from steps.cleaner import clean_phase_artifacts, _list_phase_b_artifacts, _list_phase_d_artifacts


class TestListPhaseDAllFiles:
    """_list_phase_d_artifacts: target_ids=None のケース"""

    def test_returns_findings_dir_when_exists(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a.json", {})
        result = _list_phase_d_artifacts(ctx, target_ids=None)
        assert ctx.findings_dir in result

    def test_returns_empty_when_no_findings_dir(self, ctx):
        result = _list_phase_d_artifacts(ctx, target_ids=None)
        assert result == []


class TestListPhaseDWithTarget:
    """_list_phase_d_artifacts: target_ids 指定"""

    def test_returns_target_file_only(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target.json", {})
        write_json(f"{ctx.findings_dir}/other.json", {})
        result = _list_phase_d_artifacts(ctx, target_ids=["target"])
        assert len(result) == 1
        assert result[0].endswith("target.json")

    def test_returns_empty_for_nonexistent_target(self, ctx):
        result = _list_phase_d_artifacts(ctx, target_ids=["nonexistent"])
        assert result == []


class TestListPhaseBWithTarget:
    """_list_phase_b_artifacts: target_ids 指定"""

    def test_returns_knowledge_json_and_trace(self, ctx):
        # knowledge JSON
        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})
        # trace
        os.makedirs(ctx.trace_dir, exist_ok=True)
        write_json(f"{ctx.trace_dir}/handlers-sample-handler.json", {})

        result = _list_phase_b_artifacts(ctx, target_ids=["handlers-sample-handler"])
        assert len(result) == 2
        assert any("handlers-sample-handler.json" in p for p in result)


class TestListPhaseBAllFiles:
    """_list_phase_b_artifacts: target_ids=None のケース"""

    def test_returns_all_knowledge_from_classified(self, ctx):
        """classified.json の output_path を元に全件列挙する。"""
        classified = {
            "version": "6", "generated_at": "2026-01-01T00:00:00Z",
            "files": [{
                "id": "handlers-sample-handler",
                "output_path": "component/handlers/handlers-sample-handler.json",
                "source_path": "tests/fixtures/sample_source.rst",
                "format": "rst", "filename": "sample.rst",
                "type": "component", "category": "handlers",
                "assets_dir": "component/handlers/assets/handlers-sample-handler/"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})

        result = _list_phase_b_artifacts(ctx, target_ids=None)
        assert any("handlers-sample-handler.json" in p for p in result)


class TestCleanPhaseArtifacts:
    """clean_phase_artifacts の統合テスト"""

    def test_clean_d_all_removes_findings_dir(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/a.json", {})
        write_json(f"{ctx.findings_dir}/b.json", {})

        clean_phase_artifacts(ctx, "D", target_ids=None, yes=True)
        assert not os.path.isdir(ctx.findings_dir)

    def test_clean_d_target_preserves_others(self, ctx):
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/target.json", {})
        write_json(f"{ctx.findings_dir}/keep.json", {})

        clean_phase_artifacts(ctx, "D", target_ids=["target"], yes=True)
        assert not os.path.exists(f"{ctx.findings_dir}/target.json")
        assert os.path.exists(f"{ctx.findings_dir}/keep.json")

    def test_clean_bd_removes_both_phases(self, ctx):
        """BD 指定で Phase B と D 両方の成果物を削除。"""
        # classified.json（Phase B 全件クリアに必要）
        classified = {
            "version": "6", "generated_at": "2026-01-01T00:00:00Z",
            "files": [{
                "id": "handlers-sample-handler",
                "output_path": "component/handlers/handlers-sample-handler.json",
                "source_path": "tests/fixtures/sample_source.rst",
                "format": "rst", "filename": "sample.rst",
                "type": "component", "category": "handlers",
                "assets_dir": "component/handlers/assets/handlers-sample-handler/"
            }]
        }
        write_json(ctx.classified_list_path, classified)

        # Phase B artifact
        json_path = f"{ctx.knowledge_dir}/component/handlers/handlers-sample-handler.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        write_json(json_path, {"id": "handlers-sample-handler"})

        # Phase D artifact
        os.makedirs(ctx.findings_dir, exist_ok=True)
        write_json(f"{ctx.findings_dir}/handlers-sample-handler.json", {})

        clean_phase_artifacts(ctx, "BD", target_ids=None, yes=True)
        assert not os.path.exists(json_path)
        assert not os.path.isdir(ctx.findings_dir)

    def test_no_targets_prints_message(self, ctx, capsys):
        clean_phase_artifacts(ctx, "D", target_ids=None, yes=True)
        captured = capsys.readouterr()
        assert "削除対象なし" in captured.out
```

### 実装ファイル: steps/cleaner.py

```python
"""Phase-specific artifact cleaner.

Removes intermediate artifacts for specified phases,
optionally filtered by target file IDs.
"""
import os
import glob
import shutil
from .common import load_json


def clean_phase_artifacts(ctx, phases: str, target_ids: list = None, yes: bool = False):
    """Remove intermediate artifacts for specified phases.

    Args:
        ctx: Context object with path properties
        phases: Phase letters to clean (e.g. "D", "BD")
        target_ids: File IDs to clean (None = all files)
        yes: Skip confirmation prompt if True
    """
    targets = []

    if "B" in phases:
        targets.extend(_list_phase_b_artifacts(ctx, target_ids))
    if "D" in phases:
        targets.extend(_list_phase_d_artifacts(ctx, target_ids))

    if not targets:
        print("   削除対象なし")
        return

    print(f"\n   ⚠️ 以下の {len(targets)} ファイルを削除します:")
    for t in targets[:10]:
        print(f"     - {os.path.relpath(t, ctx.repo)}")
    if len(targets) > 10:
        print(f"     ... 他 {len(targets) - 10} ファイル")

    if not yes:
        answer = input("\n   続行しますか？ [y/N]: ")
        if answer.lower() != "y":
            print("   中止しました")
            return

    for t in targets:
        if os.path.isfile(t):
            os.remove(t)
        elif os.path.isdir(t):
            shutil.rmtree(t)

    print(f"   ✅ {len(targets)} ファイル削除完了")


def _list_phase_b_artifacts(ctx, target_ids):
    """List Phase B artifacts (knowledge JSON + trace).

    When target_ids is None, uses classified.json to find all output files.
    When target_ids is specified, uses glob to find matching files.
    """
    paths = []
    if target_ids:
        for file_id in target_ids:
            pattern = f"{ctx.knowledge_dir}/**/{file_id}.json"
            paths.extend(glob.glob(pattern, recursive=True))
            trace = f"{ctx.trace_dir}/{file_id}.json"
            if os.path.exists(trace):
                paths.append(trace)
    else:
        if os.path.exists(ctx.classified_list_path):
            classified = load_json(ctx.classified_list_path)
            for f in classified["files"]:
                p = f"{ctx.knowledge_dir}/{f['output_path']}"
                if os.path.exists(p):
                    paths.append(p)
        if os.path.isdir(ctx.trace_dir):
            paths.append(ctx.trace_dir)
    return paths


def _list_phase_d_artifacts(ctx, target_ids):
    """List Phase D artifacts (findings JSON).

    When target_ids is None, returns the findings directory itself.
    When target_ids is specified, returns individual finding files.
    """
    paths = []
    if target_ids:
        for file_id in target_ids:
            p = f"{ctx.findings_dir}/{file_id}.json"
            if os.path.exists(p):
                paths.append(p)
    else:
        if os.path.isdir(ctx.findings_dir):
            paths.append(ctx.findings_dir)
    return paths
```

### 完了条件

```bash
python -m pytest tools/knowledge-creator/tests/test_cleaner.py -v
# 全テスト GREEN
```

---

## Step 2: steps/source_tracker.py

### テストファイル: tests/test_source_tracker.py

```python
"""Tests for steps/source_tracker.py"""
import os
import pytest
from steps.common import write_json, load_json
from steps.source_tracker import _compute_hash, save_hashes, detect_changed


def _make_classified(files):
    """Helper to create classified.json structure."""
    return {
        "version": "6", "generated_at": "2026-01-01T00:00:00Z",
        "files": [{
            "id": f["id"],
            "source_path": f["source_path"],
            "format": "rst", "filename": f["id"] + ".rst",
            "type": "component", "category": "handlers",
            "output_path": f"component/handlers/{f['id']}.json",
            "assets_dir": f"component/handlers/assets/{f['id']}/"
        } for f in files]
    }


class TestComputeHash:

    def test_same_content_same_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("hello")
        assert _compute_hash(str(tmp_path / "a.txt")) == _compute_hash(str(tmp_path / "b.txt"))

    def test_different_content_different_hash(self, tmp_path):
        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")
        assert _compute_hash(str(tmp_path / "a.txt")) != _compute_hash(str(tmp_path / "b.txt"))


class TestSaveHashes:

    def test_saves_hash_for_each_file(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("content")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)

        save_hashes(ctx)

        hash_path = f"{ctx.log_dir}/source_hashes.json"
        assert os.path.exists(hash_path)
        data = load_json(hash_path)
        assert "test-file" in data
        assert len(data["test-file"]["hash"]) == 64  # SHA256 hex length


class TestDetectChanged:

    def test_no_hash_file_returns_none(self, ctx):
        """No previous hash file → return None (= treat as all new)."""
        write_json(ctx.classified_list_path, _make_classified([]))
        assert detect_changed(ctx) is None

    def test_unchanged_file_returns_empty(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("content")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        assert detect_changed(ctx) == []

    def test_changed_file_detected(self, ctx):
        src_path = f"{ctx.repo}/src/test.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("original")

        classified = _make_classified([
            {"id": "test-file", "source_path": "src/test.rst"}
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        # Modify source
        with open(src_path, "w") as f:
            f.write("modified")

        assert detect_changed(ctx) == ["test-file"]

    def test_new_file_detected_as_changed(self, ctx):
        """File not in previous hashes → detected as changed."""
        write_json(f"{ctx.log_dir}/source_hashes.json", {})

        src_path = f"{ctx.repo}/src/new.rst"
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        with open(src_path, "w") as f:
            f.write("new content")

        classified = _make_classified([
            {"id": "new-file", "source_path": "src/new.rst"}
        ])
        write_json(ctx.classified_list_path, classified)

        assert detect_changed(ctx) == ["new-file"]

    def test_multiple_files_only_changed_reported(self, ctx):
        """2 files: 1 unchanged, 1 changed → only changed returned."""
        for name, content in [("a", "aaa"), ("b", "bbb")]:
            p = f"{ctx.repo}/src/{name}.rst"
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(content)

        classified = _make_classified([
            {"id": "file-a", "source_path": "src/a.rst"},
            {"id": "file-b", "source_path": "src/b.rst"},
        ])
        write_json(ctx.classified_list_path, classified)
        save_hashes(ctx)

        # Change only file-b
        with open(f"{ctx.repo}/src/b.rst", "w") as f:
            f.write("bbb-changed")

        result = detect_changed(ctx)
        assert result == ["file-b"]
```

### 実装ファイル: steps/source_tracker.py

```python
"""Source change tracker for --regen option.

Records SHA256 hashes of source files after generation.
Detects changed files by comparing current hashes with recorded ones.
"""
import os
import hashlib
from .common import load_json, write_json

HASH_FILE = "source_hashes.json"


def _compute_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_hashes(ctx):
    """Save current source file hashes. Call after Phase B completes."""
    classified = load_json(ctx.classified_list_path)
    hashes = {}
    for fi in classified["files"]:
        src = f"{ctx.repo}/{fi['source_path']}"
        if os.path.exists(src):
            hashes[fi["id"]] = {
                "source_path": fi["source_path"],
                "hash": _compute_hash(src)
            }
    write_json(f"{ctx.log_dir}/{HASH_FILE}", hashes)
    print(f"   💾 ハッシュ保存: {len(hashes)} ファイル")


def detect_changed(ctx) -> list:
    """Compare current source hashes with saved ones.

    Returns:
        list of changed file IDs, or None if no previous hashes exist.
    """
    hash_path = f"{ctx.log_dir}/{HASH_FILE}"
    if not os.path.exists(hash_path):
        print("   ⚠️ 前回のハッシュファイルなし。全ファイル再生成対象になります")
        return None

    old_hashes = load_json(hash_path)
    classified = load_json(ctx.classified_list_path)
    changed = []

    for fi in classified["files"]:
        file_id = fi["id"]
        src = f"{ctx.repo}/{fi['source_path']}"
        if not os.path.exists(src):
            continue
        current_hash = _compute_hash(src)
        old_entry = old_hashes.get(file_id)
        if old_entry is None or old_entry["hash"] != current_hash:
            changed.append(file_id)

    return changed


def detect_and_clean_changed(ctx, yes=False):
    """Detect source changes and clean artifacts for changed files."""
    changed = detect_changed(ctx)

    if changed is None:
        return
    if not changed:
        print("   ✨ ソース変更なし")
        return

    print(f"\n   🔄 ソース変更検知: {len(changed)} ファイル")
    for fid in changed[:10]:
        print(f"     - {fid}")
    if len(changed) > 10:
        print(f"     ... 他 {len(changed) - 10} ファイル")

    from .cleaner import clean_phase_artifacts
    clean_phase_artifacts(ctx, "BD", target_ids=changed, yes=yes)
```

### 完了条件

```bash
python -m pytest tools/knowledge-creator/tests/test_source_tracker.py -v
# 全テスト GREEN
```

---

## Step 3: Phase B に target_ids 追加

### 変更ファイル: steps/phase_b_generate.py

現在の `run()` メソッド（211行目〜）を以下のように変更する。変更は2箇所のみ。

**変更1: シグネチャに `target_ids=None` を追加（211行目）**

```python
# Before:
def run(self):

# After:
def run(self, target_ids=None):
```

**変更2: files のフィルタを追加（212-216行目）**

```python
# Before:
def run(self, target_ids=None):
    classified = load_json(self.ctx.classified_list_path)

    if self.dry_run:

# After:
def run(self, target_ids=None):
    classified = load_json(self.ctx.classified_list_path)
    files = classified["files"]

    if target_ids is not None:
        target_set = set(target_ids)
        files = [f for f in files if f["id"] in target_set]

    if self.dry_run:
        print(f"Would generate {len(files)} knowledge files")
        return
```

**変更3: ThreadPoolExecutor のループで `classified["files"]` を `files` に変更（218行目付近）**

```python
# Before:
    with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
        futures = [executor.submit(self.generate_one, fi) for fi in classified["files"]]

# After:
    with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
        futures = [executor.submit(self.generate_one, fi) for fi in files]
```

### テストファイル: tests/test_target_filter.py

```python
"""Tests for --target filter across phases."""
import json
import os
import subprocess
import pytest
from steps.common import write_json, load_json


def _make_classified_2files(ctx):
    """Helper: create classified.json with 2 source files."""
    for name in ["file-a", "file-b"]:
        src = f"{ctx.repo}/src/{name}.rst"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write(f"{name}\n====\n\nContent for {name}\n")

    classified = {
        "version": "6", "generated_at": "2026-01-01T00:00:00Z",
        "files": [
            {
                "id": name, "source_path": f"src/{name}.rst", "format": "rst",
                "filename": f"{name}.rst", "type": "component", "category": "test",
                "output_path": f"component/test/{name}.json",
                "assets_dir": f"component/test/assets/{name}/"
            }
            for name in ["file-a", "file-b"]
        ]
    }
    write_json(ctx.classified_list_path, classified)
    return classified


class TestPhaseBTargetFilter:

    def test_target_generates_only_specified_file(self, ctx, mock_claude):
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run(target_ids=["file-a"])

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

    def test_no_target_generates_all(self, ctx, mock_claude):
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run(target_ids=None)

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

    def test_existing_run_calls_still_work(self, ctx, mock_claude):
        """Backward compat: run() without args still processes all files."""
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")
```

### 完了条件

```bash
# 新規テスト
python -m pytest tools/knowledge-creator/tests/test_target_filter.py -v

# 既存テスト回帰（Phase B の run() を呼ぶテスト）
python -m pytest tools/knowledge-creator/tests/test_run_flow.py -v
python -m pytest tools/knowledge-creator/tests/test_pipeline.py -v
```

---

## Step 4: run.py 新オプション統合

### 変更ファイル: run.py

**変更1: argparse にオプション追加（110行目付近、既存の `--max-rounds` の後に追加）**

```python
    parser.add_argument("--max-rounds", type=int, default=1,
                        help="Max D->E->C loop iterations (default: 1, max: 10)")
    # ↓ ここから追加
    parser.add_argument("--clean-phase", type=str, default=None,
                        help="Clean artifacts for specified phases before run (e.g. 'D', 'BD')")
    parser.add_argument("--target", type=str, action="append", default=None,
                        help="Target file ID(s) to process (repeatable)")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompts")
    parser.add_argument("--regen", action="store_true",
                        help="Detect source changes and regenerate affected files")
```

**変更2: phases ループの前、`os.makedirs(ctx.log_dir, exist_ok=True)` の後に追加（160行目付近）**

```python
        os.makedirs(ctx.log_dir, exist_ok=True)
        phases = args.phase or "ABCDEM"

        # ↓ ここから追加
        # --clean-phase: remove artifacts before run
        if args.clean_phase:
            from steps.cleaner import clean_phase_artifacts
            clean_phase_artifacts(ctx, args.clean_phase,
                                  target_ids=args.target, yes=args.yes)

        # --regen: detect source changes and clean affected artifacts
        if args.regen:
            from steps.source_tracker import detect_and_clean_changed
            detect_and_clean_changed(ctx, yes=args.yes)
```

**変更3: Phase B の呼び出しに target_ids を渡す（176行目付近）**

```python
        # Before:
        if "B" in phases:
            print("\n🤖Phase B: Generate")
            print("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run()

        # After:
        if "B" in phases:
            print("\n🤖Phase B: Generate")
            print("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=args.target)

            if not args.dry_run:
                from steps.source_tracker import save_hashes
                save_hashes(ctx)
```

**変更4: Phase D の呼び出しで target を考慮（197行目付近）**

Phase D は既に `target_ids` パラメータを持っている。
現在は `pass_ids = c_result.get("pass_ids") if c_result else None` を渡しているが、
`--target` 指定時はそれでさらにフィルタする。

```python
        # Before:
            if "D" in phases:
                ...
                pass_ids = c_result.get("pass_ids") if c_result else None
                d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                    target_ids=pass_ids
                )

        # After:
            if "D" in phases:
                ...
                pass_ids = c_result.get("pass_ids") if c_result else None
                # Intersect with --target if specified
                if args.target and pass_ids is not None:
                    target_set = set(args.target)
                    effective_ids = [fid for fid in pass_ids if fid in target_set]
                elif args.target:
                    effective_ids = args.target
                else:
                    effective_ids = pass_ids
                d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                    target_ids=effective_ids
                )
```

### 完了条件

```bash
# 全テスト回帰
python -m pytest tools/knowledge-creator/tests/ -v
```

---

## Step 5: clean.py に --yes 追加

### 変更ファイル: clean.py

**変更1: argparse にオプション追加（82行目付近）**

```python
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")
```

**変更2: clean_version 実行前に確認プロンプト追加（117行目付近、`for version in versions:` の前）**

```python
    if not args.yes:
        answer = input(f"\nVersion {args.version} の全成果物を削除します。続行しますか？ [y/N]: ")
        if answer.lower() != "y":
            print("中止しました")
            sys.exit(0)
```

### 完了条件

手動確認:
- `python tools/knowledge-creator/clean.py --version 6` → プロンプト表示
- `python tools/knowledge-creator/clean.py --version 6 --yes` → プロンプトなしで実行

---

## Step 6: nc.sh 作成

### 実装ファイル: tools/knowledge-creator/nc.sh

```bash
#!/bin/bash
set -euo pipefail

# Detect repository root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TOOL_DIR="$REPO_ROOT/tools/knowledge-creator"
PYTHON="${PYTHON:-python}"

# Parse command and version
COMMAND="${1:-}"
VERSION="${2:-}"

if [ -z "$COMMAND" ] || [ -z "$VERSION" ]; then
    echo "Usage: ./nc.sh <gen|regen|fix> <version> [options]"
    echo ""
    echo "Commands:"
    echo "  gen     全件生成（clean後に全フェーズ実行）"
    echo "  regen   ソース変更への追随 / 特定ファイル再生成"
    echo "  fix     品質改善（再検証・修正）"
    echo ""
    echo "Options:"
    echo "  --resume          中断再開（genのみ、削除なし）"
    echo "  --target FILE_ID  対象ファイル指定（複数可）"
    echo "  --yes             確認プロンプトをスキップ"
    echo "  --dry-run         ドライラン"
    echo "  --max-rounds N    CDEループ回数（default: 1）"
    echo "  --concurrency N   並列数（default: 4）"
    echo "  --test FILE       テストファイル指定"
    exit 1
fi

shift 2

# Parse remaining arguments
RESUME=false
TARGET_ARGS=""
YES_FLAG=""
PASSTHROUGH_ARGS=""

while [ $# -gt 0 ]; do
    case "$1" in
        --resume)
            RESUME=true
            shift
            ;;
        --target)
            TARGET_ARGS="$TARGET_ARGS --target $2"
            shift 2
            ;;
        --yes)
            YES_FLAG="--yes"
            shift
            ;;
        *)
            PASSTHROUGH_ARGS="$PASSTHROUGH_ARGS $1"
            shift
            ;;
    esac
done

case "$COMMAND" in
    gen)
        if [ "$RESUME" = true ]; then
            # UC2: Resume interrupted generation (no clean)
            echo "🔄 中断再開モード"
            $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" $PASSTHROUGH_ARGS
        else
            # UC1: Full generation (clean first)
            echo "🚀 全件生成モード"
            $PYTHON "$TOOL_DIR/clean.py" --version "$VERSION" --repo "$REPO_ROOT" ${YES_FLAG:---yes}
            $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" $PASSTHROUGH_ARGS
        fi
        ;;
    regen)
        if [ -n "$TARGET_ARGS" ]; then
            # UC4: Regenerate specific files
            echo "🔄 特定ファイル再生成"
            $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" \
                --phase BCDEM --clean-phase BD $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        else
            # UC3: Detect source changes and regenerate
            echo "🔄 ソース変更検知 → 再生成"
            $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" \
                --regen ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        fi
        ;;
    fix)
        # UC5, UC6: Quality improvement
        echo "🔧 品質改善モード"
        $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" \
            --phase CDEM --clean-phase D $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        echo "Usage: ./nc.sh <gen|regen|fix> <version> [options]"
        exit 1
        ;;
esac
```

作成後に `chmod +x tools/knowledge-creator/nc.sh` を実行すること。

### テストファイル: tests/test_nc_sh.py

nc.sh が正しいコマンドを構築するかをテストする。
run.py / clean.py の実体を呼ばず、呼び出しコマンドをキャプチャするスタブを使う。

```python
"""Tests for nc.sh command routing.

Strategy: Replace python with a stub that prints the command it received,
then verify nc.sh routes to the correct command with correct arguments.
"""
import os
import subprocess
import pytest
import tempfile
import stat

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NC_SH = os.path.join(TOOL_DIR, "nc.sh")


@pytest.fixture
def stub_env(tmp_path):
    """Create a stub python that logs commands instead of executing them."""
    stub_script = tmp_path / "python"
    stub_script.write_text(
        '#!/bin/bash\n'
        'echo "CMD: $@"\n'
    )
    stub_script.chmod(stub_script.stat().st_mode | stat.S_IEXEC)

    env = os.environ.copy()
    env["PYTHON"] = str(stub_script)
    env["PATH"] = str(tmp_path) + ":" + env.get("PATH", "")
    return env


def _run_nc(args, env):
    """Run nc.sh with stub python and return stdout."""
    result = subprocess.run(
        ["bash", NC_SH] + args,
        capture_output=True, text=True, env=env
    )
    return result


class TestGenCommand:

    def test_gen_calls_clean_then_run(self, stub_env):
        result = _run_nc(["gen", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 2, f"Expected 2 commands, got: {lines}"
        assert "clean.py" in lines[0] and "--version 6" in lines[0]
        assert "run.py" in lines[1] and "--version 6" in lines[1]

    def test_gen_resume_skips_clean(self, stub_env):
        result = _run_nc(["gen", "6", "--resume"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1, f"Expected 1 command, got: {lines}"
        assert "run.py" in lines[0]
        assert "clean.py" not in lines[0]


class TestRegenCommand:

    def test_regen_without_target_uses_regen_flag(self, stub_env):
        result = _run_nc(["regen", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        assert "--regen" in lines[0]

    def test_regen_with_target_uses_phase_and_clean(self, stub_env):
        result = _run_nc(["regen", "6", "--target", "test-id"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        cmd = lines[0]
        assert "--phase BCDEM" in cmd
        assert "--clean-phase BD" in cmd
        assert "--target test-id" in cmd


class TestFixCommand:

    def test_fix_uses_phase_cdem_and_clean_d(self, stub_env):
        result = _run_nc(["fix", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        cmd = lines[0]
        assert "--phase CDEM" in cmd
        assert "--clean-phase D" in cmd

    def test_fix_with_target_passes_target(self, stub_env):
        result = _run_nc(["fix", "6", "--target", "test-id"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        assert "--target test-id" in lines[0]


class TestErrorHandling:

    def test_unknown_command_exits_nonzero(self, stub_env):
        result = _run_nc(["unknown", "6"], stub_env)
        assert result.returncode != 0

    def test_no_args_exits_nonzero(self, stub_env):
        result = _run_nc([], stub_env)
        assert result.returncode != 0
```

### 完了条件

```bash
python -m pytest tools/knowledge-creator/tests/test_nc_sh.py -v
# 全テスト GREEN
```

---

## Step 7: 全テスト回帰確認

```bash
cd /path/to/nabledge-dev
python -m pytest tools/knowledge-creator/tests/ -v
```

全テスト GREEN であればタスク完了。

---

## 重要な注意事項

### 言語ルール（CLAUDE.md より）
- コード・コメント・変数名: **英語**
- ユーザー向け print 文: **日本語**
- テストの docstring: 英語でも日本語でもよい（既存コードに合わせる）

### 既存テストの互換性
- `phase_b_generate.py` の `run()` シグネチャに `target_ids=None` を追加するが、デフォルト `None` なので既存の呼び出し元（`run.py`, `test_run_flow.py`, `test_pipeline.py`）は変更不要
- ただし `run.py` 内の Phase B 呼び出しは `args.target` を渡すように変更する

### conftest.py の活用
- テストで `ctx` fixture を使うと `tmp_path` ベースの一時リポジトリが作られる
- `mock_claude` fixture で claude CLI のモックが注入される
- 新規テストファイルでも `ctx`, `mock_claude` はそのまま使える（conftest.py で定義済み）

### ファイルパスの構造
```
最終成果物:  {ctx.knowledge_dir}/{output_path}
             = {repo}/.claude/skills/nabledge-6/knowledge/{type}/{category}/{id}.json

中間成果物:  {ctx.findings_dir}/{file_id}.json
             = {repo}/tools/knowledge-creator/.logs/v6/phase-d/findings/{file_id}.json

             {ctx.trace_dir}/{file_id}.json
             = {repo}/tools/knowledge-creator/.logs/v6/phase-b/traces/{file_id}.json

分類情報:    {ctx.classified_list_path}
             = {repo}/tools/knowledge-creator/.logs/v6/phase-a/classified.json
```
