# knowledge-creator ログ・レポート改善 実装タスク

## ゴール

`tools/knowledge-creator/` のログ管理・実行結果レポートを以下の3点で改善する。

1. **ログディレクトリに実行開始日時（run_id）を含める**: 複数回実行してもログが混在しない
2. **実行終了時に `report.json` を自動生成**: 毎回同一フォーマットで記録し、過去と比較可能にする
3. **CC の実行メトリクスを抽出・集計**: `claude -p --output-format json` の `usage`・`total_cost_usd`・`num_turns` を記録する

このドキュメントだけを見て実装を完了すること。

---

## ブランチ

```bash
git checkout main
git checkout -b 101-log-report-improvement
```

---

## 変更ファイル一覧

```
tools/knowledge-creator/
  run.py                          ← Context に run_id 追加、Report 生成ロジック追加
  nc.sh                           ← latest シンボリックリンク管理（gen --resume 対応）
  compare_reports.py              ← 新規: report.json 比較スクリプト
  steps/
    common.py                     ← run_claude() に cc_metrics 抽出を追加、aggregate_cc_metrics() 追加
    phase_b_generate.py           ← run() にメトリクス集計・return を追加
    phase_d_content_check.py      ← run() にメトリクス集計・返却キーを追加
    phase_e_fix.py                ← run() にメトリクス集計・返却キーを追加
  tests/
    conftest.py                   ← test_repo fixture の phase_a_dir パスを修正
    test_run_id.py                ← 新規: run_id・latest リンク・report.json のテスト
```

---

## ログディレクトリ構造（変更後）

```
tools/knowledge-creator/.logs/
└── v6/
    ├── latest -> 20250305T091500     ← シンボリックリンク（常に最新実行を指す）
    ├── 20250304T143022/              ← 1回目の実行
    │   ├── execution.log
    │   ├── report.json               ← 新規
    │   ├── phase-a/
    │   │   ├── sources.json
    │   │   └── classified.json
    │   ├── phase-b/
    │   │   ├── executions/           ← {file_id}_{timestamp}.json（cc_metrics 含む）
    │   │   └── traces/
    │   ├── phase-c/
    │   │   └── results.json
    │   ├── phase-d/
    │   │   ├── executions/
    │   │   └── findings/
    │   └── phase-e/
    │       └── executions/
    └── 20250305T091500/              ← 2回目の実行（独立）
        └── ...
```

---

## 実装詳細

### 1. `run.py` — Context に `run_id` を追加

#### 変更箇所: import 追加

ファイル冒頭の import 群に以下を追加する。

```python
from datetime import datetime, timezone
import json
```

#### 変更箇所: Context クラス

以下の変更を行う。

- `run_id: str = None` フィールドを追加
- `__post_init__` に `run_id` の自動生成を追加（既存の repo バリデーションは維持）
- `version_log_dir` プロパティを追加
- `log_dir` プロパティを `{version_log_dir}/{run_id}` を返すよう変更
- `report_path` プロパティを追加

```python
@dataclass
class Context:
    version: str
    repo: str
    concurrency: int
    test_file: str = None
    max_rounds: int = 1
    run_id: str = None          # 追加

    def __post_init__(self):
        if not os.path.isdir(self.repo):
            raise ValueError(f"Repository path does not exist: {self.repo}")
        if self.run_id is None:                                                 # 追加
            self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") # 追加

    @property
    def version_log_dir(self) -> str:
        """バージョン単位のログルート（latest リンクの親）"""                   # 追加
        return f"{self.repo}/tools/knowledge-creator/.logs/v{self.version}"    # 追加

    @property
    def log_dir(self) -> str:
        return f"{self.version_log_dir}/{self.run_id}"   # 変更（run_id を追加）

    @property
    def report_path(self) -> str:                        # 追加
        return f"{self.log_dir}/report.json"             # 追加

    # 以降のプロパティは変更なし（log_dir を使っているため自動的に新パスになる）
    @property
    def source_list_path(self) -> str:
        return f"{self.log_dir}/phase-a/sources.json"
    # ... （既存のまま）
```

#### 変更箇所: `main()` に `--run-id` 引数を追加

既存の `add_argument` 群の末尾に追加する。

```python
parser.add_argument("--run-id", type=str, default=None,
                    help="実行ID（省略時は現在時刻から自動生成、--resume 時は nc.sh が渡す）")
```

#### 変更箇所: `main()` の `for v in versions:` ループ内

`ctx = Context(...)` の行を以下に変更する（`run_id=args.run_id` を追加するだけ）。

```python
# 変更前
ctx = Context(
    version=v, repo=args.repo, concurrency=args.concurrency,
    test_file=args.test, max_rounds=args.max_rounds
)

# 変更後
ctx = Context(
    version=v, repo=args.repo, concurrency=args.concurrency,
    test_file=args.test, max_rounds=args.max_rounds,
    run_id=args.run_id  # 追加
)
```

#### 変更箇所: `main()` — `os.makedirs(ctx.log_dir, ...)` の直後に latest リンク更新を追加

```python
os.makedirs(ctx.log_dir, exist_ok=True)

# latest シンボリックリンクを更新（--run-id 未指定の新規実行のみ）
if args.run_id is None:
    latest_link = os.path.join(ctx.version_log_dir, "latest")
    try:
        if os.path.lexists(latest_link):
            os.remove(latest_link)
        os.symlink(ctx.run_id, latest_link)
    except OSError as e:
        logger.warning(f"latest リンクの更新に失敗しました（継続します）: {e}")
```

#### 変更箇所: `main()` — 実行開始時刻の記録とレポートデータ収集

`setup_logger(log_file_path=execution_log_path)` の直後、`phases = args.phase or "ABCDEM"` の前に追加する。

```python
# レポート用データ収集の初期化
started_at = datetime.now(timezone.utc).isoformat()
report = {
    "meta": {
        "run_id":      ctx.run_id,
        "version":     v,
        "started_at":  started_at,
        "phases":      args.phase or "ABCDEM",
        "max_rounds":  args.max_rounds,
        "concurrency": args.concurrency,
        "test_mode":   args.test is not None,
    },
    "phase_b":        None,
    "phase_c":        None,
    "phase_d_rounds": [],
    "phase_e_rounds": [],
    "totals":         None,
}
```

#### 変更箇所: `main()` — 各フェーズの呼び出し結果をレポートに格納

Phase B の呼び出し箇所を以下に変更する。

```python
# 変更前
PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=args.target)

# 変更後
b_result = PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=args.target)
if b_result:
    report["phase_b"] = b_result
```

Phase C の呼び出し箇所を以下に変更する。

```python
# 変更前
c_result = PhaseCStructureCheck(ctx).run()

# 変更後
c_result = PhaseCStructureCheck(ctx).run()
report["phase_c"] = {
    "total":     c_result.get("total", 0),
    "pass":      c_result.get("pass", 0),
    "fail":      c_result.get("error", 0),
    "pass_rate": round(c_result["pass"] / c_result["total"], 3)
                 if c_result.get("total", 0) > 0 else 0,
}
```

Phase D の呼び出し箇所を以下に変更する。

```python
# 変更前
d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(target_ids=effective_ids)

# 変更後
d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(target_ids=effective_ids)
findings_summary = _aggregate_findings(ctx)
d_round = {
    "round":      round_num,
    "total":      d_result.get("clean", 0) + len(d_result.get("issue_file_ids", [])),
    "clean":      d_result.get("clean", 0),
    "has_issues": len(d_result.get("issue_file_ids", [])),
    "clean_rate": round(
        d_result.get("clean", 0) /
        (d_result.get("clean", 0) + len(d_result.get("issue_file_ids", []))), 3
    ) if (d_result.get("clean", 0) + len(d_result.get("issue_file_ids", []))) > 0 else 0,
    "findings": findings_summary,
    "metrics":  d_result.get("metrics"),
}
report["phase_d_rounds"].append(d_round)
```

Phase E の呼び出し箇所を以下に変更する。

```python
# 変更前
PhaseEFix(ctx, dry_run=args.dry_run).run(target_ids=d_result["issue_file_ids"])

# 変更後
e_result = PhaseEFix(ctx, dry_run=args.dry_run).run(target_ids=d_result["issue_file_ids"])
if e_result:
    report["phase_e_rounds"].append({
        "round":   round_num,
        "fixed":   e_result.get("fixed", 0),
        "error":   e_result.get("error", 0),
        "metrics": e_result.get("metrics"),
    })
```

#### 変更箇所: `main()` — ループ終了後、Phase M 呼び出しの後に report.json を書き出す

最後の `logger.info(f"✨Completed version {v}")` の直前に追加する。

```python
finished_at = datetime.now(timezone.utc).isoformat()
report["meta"]["finished_at"] = finished_at
report["meta"]["duration_sec"] = int(
    (datetime.fromisoformat(finished_at) - datetime.fromisoformat(started_at)).total_seconds()
)
report["totals"] = _compute_totals(report)
_write_report(ctx, report)
logger.info(f"\n   📄 Report: {ctx.report_path}")
```

#### 追加: `main()` の定義の前に3つのヘルパー関数を追加

`def main():` の直前（ファイル末尾付近）に追加する。

```python
def _aggregate_findings(ctx) -> dict:
    """phase-d/findings/*.json を走査して findings サマリーを集計する。"""
    import glob
    findings_dir = ctx.findings_dir
    total = critical = minor = 0
    by_category = {}

    for path in glob.glob(os.path.join(findings_dir, "*.json")):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for finding in data.get("findings", []):
            total += 1
            sev = finding.get("severity", "")
            cat = finding.get("category", "unknown")
            if sev == "critical":
                critical += 1
            else:
                minor += 1
            by_category[cat] = by_category.get(cat, 0) + 1

    return {"total": total, "critical": critical, "minor": minor, "by_category": by_category}


def _compute_totals(report: dict) -> dict:
    """全フェーズのトークン・コストを合計する。"""
    tokens = {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}
    cost_usd = 0.0

    for phase_key in ["phase_b"]:
        phase = report.get(phase_key) or {}
        m = phase.get("metrics") or {}
        t = m.get("tokens") or {}
        for k in tokens:
            tokens[k] += t.get(k, 0)
        cost_usd += m.get("cost_usd") or 0.0

    for rounds_key in ["phase_d_rounds", "phase_e_rounds"]:
        for rnd in report.get(rounds_key) or []:
            m = rnd.get("metrics") or {}
            t = m.get("tokens") or {}
            for k in tokens:
                tokens[k] += t.get(k, 0)
            cost_usd += m.get("cost_usd") or 0.0

    return {"tokens": tokens, "cost_usd": round(cost_usd, 4)}


def _write_report(ctx, report: dict):
    """report.json を log_dir に書き出す。"""
    os.makedirs(ctx.log_dir, exist_ok=True)
    with open(ctx.report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
```

---

### 2. `nc.sh` — `gen --resume` 対応

現在の `gen --resume` ブロックは `--run-id` を渡していない。以下に変更する。

```bash
# 変更前
gen)
    if [ "$RESUME" = true ]; then
        echo "🔄 中断再開モード"
        $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" $PASSTHROUGH_ARGS
    else
        ...
    fi
    ;;

# 変更後
gen)
    if [ "$RESUME" = true ]; then
        echo "🔄 中断再開モード"
        LATEST_LINK="$REPO_ROOT/tools/knowledge-creator/.logs/v${VERSION}/latest"
        if [ ! -L "$LATEST_LINK" ]; then
            echo "Error: latest リンクが見つかりません。先に ./nc.sh gen $VERSION を実行してください。"
            exit 1
        fi
        EXISTING_RUN_ID=$(basename "$(readlink "$LATEST_LINK")")
        echo "   再開する run_id: $EXISTING_RUN_ID"
        $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" \
            --run-id "$EXISTING_RUN_ID" $PASSTHROUGH_ARGS
    else
        echo "🚀 全件生成モード"
        $PYTHON "$TOOL_DIR/clean.py" --version "$VERSION" --repo "$REPO_ROOT" ${YES_FLAG:---yes}
        $PYTHON "$TOOL_DIR/run.py" --version "$VERSION" --repo "$REPO_ROOT" $PASSTHROUGH_ARGS
    fi
    ;;
```

---

### 3. `steps/common.py` — CC メトリクス抽出を追加

#### 変更箇所: `run_claude()` の execution log 保存部分

現在の保存処理を以下に置き換える。`response` 全体を保存していた箇所を、`cc_metrics` だけを抽出して保存するよう変更する。

```python
# 変更前（run_claude 内の execution log 保存箇所）
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
log_path = os.path.join(log_dir, f"{file_id}_{timestamp}.json")
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(response, f, ensure_ascii=False, indent=2)

# 変更後
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
log_path = os.path.join(log_dir, f"{file_id}_{timestamp}.json")
cc_metrics = {
    "duration_ms":     response.get("duration_ms"),
    "duration_api_ms": response.get("duration_api_ms"),
    "num_turns":       response.get("num_turns"),
    "total_cost_usd":  response.get("total_cost_usd"),
    "usage":           response.get("usage", {}),
}
log_data = {
    "file_id":    file_id,
    "timestamp":  timestamp,
    "subtype":    response.get("subtype"),
    "cc_metrics": cc_metrics,
}
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(log_data, f, ensure_ascii=False, indent=2)
```

#### 追加: `aggregate_cc_metrics()` 関数

`run_claude()` の後（ファイル末尾）に追加する。

```python
def aggregate_cc_metrics(executions_dir: str) -> dict:
    """executions ディレクトリの execution log を走査してメトリクスを集計する。

    executions_dir が存在しない場合や JSON ファイルがない場合は空の結果を返す。

    Returns:
        {
          "count": int,
          "tokens": {"input": int, "cache_creation": int, "cache_read": int, "output": int},
          "cost_usd": float,
          "avg_turns": float,        # ターンデータがある場合のみ含まれる
          "avg_duration_sec": float, # duration データがある場合のみ含まれる
          "p95_duration_sec": float, # duration データがある場合のみ含まれる
        }
    """
    import glob

    tokens = {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}
    cost_usd = 0.0
    turns = []
    durations = []
    count = 0

    for path in glob.glob(os.path.join(executions_dir, "*.json")):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        cc = data.get("cc_metrics", {})
        usage = cc.get("usage", {})
        tokens["input"]          += usage.get("input_tokens", 0)
        tokens["cache_creation"] += usage.get("cache_creation_input_tokens", 0)
        tokens["cache_read"]     += usage.get("cache_read_input_tokens", 0)
        tokens["output"]         += usage.get("output_tokens", 0)
        cost_usd                 += cc.get("total_cost_usd") or 0.0
        if cc.get("num_turns"):
            turns.append(cc["num_turns"])
        if cc.get("duration_ms"):
            durations.append(cc["duration_ms"] / 1000.0)
        count += 1

    result = {"count": count, "tokens": tokens, "cost_usd": round(cost_usd, 4)}
    if turns:
        result["avg_turns"] = round(sum(turns) / len(turns), 1)
    if durations:
        sorted_d = sorted(durations)
        result["avg_duration_sec"] = round(sum(sorted_d) / len(sorted_d), 1)
        p95_idx = max(0, int(len(sorted_d) * 0.95) - 1)
        result["p95_duration_sec"] = round(sorted_d[p95_idx], 1)

    return result
```

---

### 4. `steps/phase_b_generate.py` — `run()` にメトリクス集計・return を追加

#### 変更箇所: import 追加

```python
# 変更前
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

# 変更後
from .common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
```

#### 変更箇所: `run()` メソッドの末尾

現在 `run()` は `return` 文がない。以下のように末尾を変更する。

```python
# 変更前（run() 末尾）
ok_icon = "✅" if results['error'] == 0 else "⚠️"
self.logger.error(f"\n   {ok_icon} Generation: OK={results['ok']}, Skip={results['skip']}, Error={results['error']}")

# 変更後（logger.error → logger.info に修正、メトリクス集計・return を追加）
ok_icon = "✅" if results['error'] == 0 else "⚠️"
self.logger.info(f"\n   {ok_icon} Generation: OK={results['ok']}, Skip={results['skip']}, Error={results['error']}")
metrics = aggregate_cc_metrics(self.ctx.phase_b_executions_dir)
self.logger.info(
    f"   📊 Metrics: cost=${metrics['cost_usd']:.3f} "
    f"avg_turns={metrics.get('avg_turns', 'N/A')} "
    f"avg={metrics.get('avg_duration_sec', 'N/A')}s "
    f"p95={metrics.get('p95_duration_sec', 'N/A')}s"
)
results["metrics"] = metrics
return results
```

---

### 5. `steps/phase_d_content_check.py` — `run()` にメトリクス集計・返却キーを追加

#### 変更箇所: import 追加

```python
# 変更前
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

# 変更後
from .common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
```

#### 変更箇所: `run()` メソッドの return 行

`d_result["clean"]` が `run.py` 側で必要なため、返却値に `"clean"` キーを追加し、メトリクスも追加する。

```python
# 変更前
status_icon = "✅" if len(issue_ids) == 0 else "⚠️"
self.logger.info(f"\n   {status_icon} Content Check: {clean} clean, {len(issue_ids)} with issues")
return {"issues_count": len(issue_ids), "issue_file_ids": issue_ids}

# 変更後
status_icon = "✅" if len(issue_ids) == 0 else "⚠️"
self.logger.info(f"\n   {status_icon} Content Check: {clean} clean, {len(issue_ids)} with issues")
metrics = aggregate_cc_metrics(self.ctx.phase_d_executions_dir)
self.logger.info(f"   📊 Metrics: cost=${metrics['cost_usd']:.3f} avg_turns={metrics.get('avg_turns', 'N/A')}")
return {
    "issues_count":   len(issue_ids),
    "issue_file_ids": issue_ids,
    "clean":          clean,      # 追加: run.py の report 生成で使用
    "metrics":        metrics,    # 追加
}
```

---

### 6. `steps/phase_e_fix.py` — `run()` にメトリクス集計・返却キーを追加

#### 変更箇所: import 追加

```python
# 変更前
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

# 変更後
from .common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
```

#### 変更箇所: `run()` メソッドの末尾

```python
# 変更前
self.logger.info(f"\n修正完了: {fixed}/{len(targets)}")
return {"fixed": fixed, "total": len(targets)}

# 変更後
self.logger.info(f"\n   ✅ 修正完了: {fixed}/{len(targets)}")
metrics = aggregate_cc_metrics(self.ctx.phase_e_executions_dir)
self.logger.info(f"   📊 Metrics: cost=${metrics['cost_usd']:.3f}")
return {
    "fixed":   fixed,
    "error":   len(targets) - fixed,  # 追加: run.py の report 生成で使用
    "total":   len(targets),
    "metrics": metrics,               # 追加
}
```

---

### 7. `tests/conftest.py` — `test_repo` fixture の修正

**⚠️ この修正を行わないと既存テストが全件失敗する。**

`test_repo` fixture は `classified.json` と traces ディレクトリを `.logs/v6/phase-a/` に直接作成している。`run_id` 追加後は `log_dir` が `.logs/v6/{run_id}/phase-a/` になるため、`ctx` fixture と同じ `run_id` を使って Context 経由でパスを取得するよう修正する。

修正方針: テスト用の固定 `run_id` として `"test"` を使う。`test_repo` fixture と `ctx` fixture が両方 `run_id="test"` を使うことで、両者の `classified_list_path` が一致する。

```python
# 変更前（test_repo fixture 内）
phase_a_dir = repo / "tools" / "knowledge-creator" / ".logs" / "v6" / "phase-a"
phase_a_dir.mkdir(parents=True)
classified = load_fixture("sample_classified.json")
with open(phase_a_dir / "classified.json", "w", encoding="utf-8") as f:
    json.dump(classified, f, ensure_ascii=False, indent=2)

# trace directory (required by Phase G for label index building)
trace_dir = repo / "tools" / "knowledge-creator" / ".logs" / "v6" / "phase-b" / "traces"
trace_dir.mkdir(parents=True, exist_ok=True)
```

```python
# 変更後（test_repo fixture 内）
# Context 経由でパスを取得することで run_id の変更に追随する。
# run_id="test" を固定することで ctx fixture と同じパスになる。
from run import Context as _Context
_ctx = _Context(version="6", repo=str(repo), concurrency=1, run_id="test")

phase_a_dir = Path(_ctx.classified_list_path).parent
phase_a_dir.mkdir(parents=True, exist_ok=True)
classified = load_fixture("sample_classified.json")
with open(_ctx.classified_list_path, "w", encoding="utf-8") as f:
    json.dump(classified, f, ensure_ascii=False, indent=2)

# trace directory (required by Phase G for label index building)
trace_dir = Path(_ctx.trace_dir)
trace_dir.mkdir(parents=True, exist_ok=True)
```

合わせて `ctx` fixture も `run_id="test"` を指定する。

```python
# 変更前
@pytest.fixture
def ctx(test_repo):
    sys.path.insert(0, TOOL_DIR)
    from run import Context
    return Context(version="6", repo=test_repo, concurrency=1)

# 変更後
@pytest.fixture
def ctx(test_repo):
    sys.path.insert(0, TOOL_DIR)
    from run import Context
    return Context(version="6", repo=test_repo, concurrency=1, run_id="test")
```

---

### 8. `compare_reports.py` — 新規作成

`tools/knowledge-creator/compare_reports.py` として新規作成する。

```python
#!/usr/bin/env python3
"""report.json を2つ比較して改善効果を表示する。

Usage:
    python tools/knowledge-creator/compare_reports.py \\
        tools/knowledge-creator/.logs/v6/20250304T143022/report.json \\
        tools/knowledge-creator/.logs/v6/20250305T091500/report.json
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
```

---

## `report.json` の完成形サンプル

```json
{
  "meta": {
    "run_id": "20250304T143022",
    "version": "6",
    "started_at": "2025-03-04T14:30:22+00:00",
    "finished_at": "2025-03-04T15:12:45+00:00",
    "duration_sec": 2543,
    "phases": "ABCDEM",
    "max_rounds": 1,
    "concurrency": 4,
    "test_mode": false
  },
  "phase_b": {
    "ok": 91,
    "skip": 0,
    "error": 2,
    "metrics": {
      "count": 91,
      "tokens": {
        "input": 1234567,
        "cache_creation": 345678,
        "cache_read": 89012,
        "output": 234567
      },
      "cost_usd": 4.21,
      "avg_turns": 3.2,
      "avg_duration_sec": 19.6,
      "p95_duration_sec": 45.1
    }
  },
  "phase_c": {
    "total": 91,
    "pass": 88,
    "fail": 3,
    "pass_rate": 0.967
  },
  "phase_d_rounds": [
    {
      "round": 1,
      "total": 88,
      "clean": 72,
      "has_issues": 16,
      "clean_rate": 0.818,
      "findings": {
        "total": 38,
        "critical": 12,
        "minor": 26,
        "by_category": {
          "omission": 18,
          "fabrication": 6,
          "hints_missing": 10,
          "section_issue": 4
        }
      },
      "metrics": {
        "count": 88,
        "tokens": {"input": 567890, "cache_creation": 123456, "cache_read": 34567, "output": 89012},
        "cost_usd": 1.87,
        "avg_turns": 2.1
      }
    }
  ],
  "phase_e_rounds": [
    {
      "round": 1,
      "fixed": 14,
      "error": 2,
      "metrics": {
        "count": 16,
        "tokens": {"input": 234567, "cache_creation": 0, "cache_read": 67890, "output": 89012},
        "cost_usd": 0.98
      }
    }
  ],
  "totals": {
    "tokens": {
      "input": 2037024,
      "cache_creation": 469134,
      "cache_read": 191469,
      "output": 412591
    },
    "cost_usd": 7.06
  }
}
```

---

## テスト

`tests/test_run_id.py` を新規作成する。

```python
"""Tests for run_id, latest symlink, and report.json generation."""
import json
import os
import sys
import pytest
from datetime import datetime, timezone
from pathlib import Path

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOL_DIR)

from run import Context, _aggregate_findings, _compute_totals, _write_report


class TestContext:
    def test_run_id_auto_generated(self, tmp_path):
        """run_id が未指定のとき自動生成される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        assert ctx.run_id is not None
        # フォーマット: YYYYMMDDTHHmmSS
        datetime.strptime(ctx.run_id, "%Y%m%dT%H%M%S")

    def test_run_id_explicit(self, tmp_path):
        """run_id を明示指定すると保持される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.run_id == "20250304T120000"

    def test_log_dir_contains_run_id(self, tmp_path):
        """log_dir に run_id が含まれる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert "20250304T120000" in ctx.log_dir

    def test_version_log_dir_is_parent_of_log_dir(self, tmp_path):
        """version_log_dir は log_dir の親ディレクトリ。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.log_dir.startswith(ctx.version_log_dir)
        assert ctx.log_dir != ctx.version_log_dir

    def test_report_path_inside_log_dir(self, tmp_path):
        """report_path は log_dir 内にある。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert ctx.report_path.startswith(ctx.log_dir)
        assert ctx.report_path.endswith("report.json")

    def test_sub_paths_use_run_id(self, tmp_path):
        """classified_list_path 等のサブパスも run_id を含む。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        assert "20250304T120000" in ctx.classified_list_path
        assert "20250304T120000" in ctx.findings_dir
        assert "20250304T120000" in ctx.phase_b_executions_dir


class TestLatestSymlink:
    def test_latest_created_on_new_run(self, tmp_path):
        """新規実行時に latest シンボリックリンクが作成される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.log_dir, exist_ok=True)

        latest_link = os.path.join(ctx.version_log_dir, "latest")
        if os.path.lexists(latest_link):
            os.remove(latest_link)
        os.symlink(ctx.run_id, latest_link)

        assert os.path.islink(latest_link)
        assert os.readlink(latest_link) == ctx.run_id

    def test_latest_updated_on_second_run(self, tmp_path):
        """2回目の実行で latest が新しい run_id に更新される。"""
        ctx1 = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T100000")
        os.makedirs(ctx1.log_dir, exist_ok=True)
        latest_link = os.path.join(ctx1.version_log_dir, "latest")
        os.symlink(ctx1.run_id, latest_link)

        ctx2 = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T110000")
        os.makedirs(ctx2.log_dir, exist_ok=True)
        if os.path.lexists(latest_link):
            os.remove(latest_link)
        os.symlink(ctx2.run_id, latest_link)

        assert os.readlink(latest_link) == "20250304T110000"

    def test_resume_reuses_run_id_from_latest(self, tmp_path):
        """--resume 時は latest リンクが指す run_id を再利用できる。"""
        original_run_id = "20250304T100000"
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id=original_run_id)
        os.makedirs(ctx.log_dir, exist_ok=True)
        latest_link = os.path.join(ctx.version_log_dir, "latest")
        os.symlink(original_run_id, latest_link)

        # nc.sh が行う操作をシミュレート: latest を読んで同じ run_id で Context を作る
        resumed_run_id = os.readlink(latest_link)
        ctx_resumed = Context(version="6", repo=str(tmp_path), concurrency=4, run_id=resumed_run_id)

        assert ctx_resumed.run_id == original_run_id
        assert ctx_resumed.log_dir == ctx.log_dir


class TestAggregateFindings:
    def test_empty_dir_returns_zero(self, tmp_path):
        """findings ディレクトリが空でもエラーにならず 0 を返す。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.findings_dir, exist_ok=True)
        result = _aggregate_findings(ctx)
        assert result == {"total": 0, "critical": 0, "minor": 0, "by_category": {}}

    def test_nonexistent_dir_returns_zero(self, tmp_path):
        """findings ディレクトリが存在しなくてもエラーにならない。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        # makedirs しない
        result = _aggregate_findings(ctx)
        assert result["total"] == 0

    def test_aggregate_multiple_findings(self, tmp_path):
        """複数の findings ファイルを正しく集計できる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4)
        os.makedirs(ctx.findings_dir, exist_ok=True)

        findings1 = {
            "file_id": "file-a", "status": "has_issues",
            "findings": [
                {"category": "omission",    "severity": "critical", "location": "x", "description": "y"},
                {"category": "omission",    "severity": "minor",    "location": "x", "description": "y"},
            ]
        }
        findings2 = {
            "file_id": "file-b", "status": "has_issues",
            "findings": [
                {"category": "fabrication", "severity": "critical", "location": "x", "description": "y"},
            ]
        }
        with open(os.path.join(ctx.findings_dir, "file-a.json"), 'w') as f:
            json.dump(findings1, f)
        with open(os.path.join(ctx.findings_dir, "file-b.json"), 'w') as f:
            json.dump(findings2, f)

        result = _aggregate_findings(ctx)
        assert result["total"] == 3
        assert result["critical"] == 2
        assert result["minor"] == 1
        assert result["by_category"]["omission"] == 2
        assert result["by_category"]["fabrication"] == 1


class TestComputeTotals:
    def test_all_none_returns_zero(self):
        """全フェーズが None でも合計 0 を返す。"""
        report = {"phase_b": None, "phase_d_rounds": [], "phase_e_rounds": []}
        totals = _compute_totals(report)
        assert totals["cost_usd"] == 0.0
        assert totals["tokens"]["input"] == 0

    def test_sums_all_phases(self):
        """Phase B + D + E のコスト・トークンを正しく合計する。"""
        report = {
            "phase_b": {
                "metrics": {
                    "cost_usd": 4.21,
                    "tokens": {"input": 100, "cache_creation": 10, "cache_read": 5, "output": 20}
                }
            },
            "phase_d_rounds": [{
                "metrics": {
                    "cost_usd": 1.87,
                    "tokens": {"input": 50, "cache_creation": 5, "cache_read": 3, "output": 10}
                }
            }],
            "phase_e_rounds": [{
                "metrics": {
                    "cost_usd": 0.98,
                    "tokens": {"input": 30, "cache_creation": 0, "cache_read": 2, "output": 8}
                }
            }],
        }
        totals = _compute_totals(report)
        assert totals["cost_usd"] == round(4.21 + 1.87 + 0.98, 4)
        assert totals["tokens"]["input"] == 180
        assert totals["tokens"]["cache_creation"] == 15


class TestWriteReport:
    def test_report_json_written(self, tmp_path):
        """report.json が log_dir に書き出される。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        os.makedirs(ctx.log_dir, exist_ok=True)

        report = {"meta": {"run_id": ctx.run_id}, "totals": {"cost_usd": 1.23}}
        _write_report(ctx, report)

        assert os.path.exists(ctx.report_path)
        with open(ctx.report_path) as f:
            loaded = json.load(f)
        assert loaded["meta"]["run_id"] == ctx.run_id
        assert loaded["totals"]["cost_usd"] == 1.23

    def test_report_overwrites_existing(self, tmp_path):
        """既存の report.json を上書きできる。"""
        ctx = Context(version="6", repo=str(tmp_path), concurrency=4, run_id="20250304T120000")
        os.makedirs(ctx.log_dir, exist_ok=True)

        _write_report(ctx, {"version": 1})
        _write_report(ctx, {"version": 2})

        with open(ctx.report_path) as f:
            loaded = json.load(f)
        assert loaded["version"] == 2
```

---

## テスト実行と検証

```bash
cd /path/to/nabledge-dev/tools/knowledge-creator

# 依存インストール
pip install -r requirements.txt --break-system-packages

# 新規テストのみ
python -m pytest tests/test_run_id.py -v

# 全テスト（既存テストを含め全パスすること）
python -m pytest tests/ -v
```

**成功条件**: 既存テストを含む全テストがパスすること。

---

## 注意事項

- `aggregate_cc_metrics()` は executions ディレクトリが存在しない場合でも空の結果を返す（`glob.glob()` は存在しないパスに対してエラーを出さない）
- `os.symlink()` は Windows 環境で管理者権限が必要な場合がある。`try/except OSError` で警告を出して継続するよう `run.py` に記載済み
- Phase B `run()` が dry_run モード時は `return` なしのまま（このタスクの対象外）。`run.py` 側で `if b_result:` でガードしているため問題なし
- `test_run_phases.py` は Phase クラスをすべてモック化しており `ctx.log_dir` の具体的なパスに依存していないため、今回の変更による影響はない
