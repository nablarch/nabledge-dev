# Code Analysis Benchmark 実行手順

このドキュメントは `code-analysis` ワークフローのベンチマーク実行方法を説明する。
QA ベンチマーク（`HOW-TO-RUN.md`）とは独立して実行できる。

---

## 前提

- **スキルディレクトリ**: `.claude/skills/nabledge-6`
- **シナリオファイル**: `tools/benchmark/scenarios/code-analysis.json`
- **プロジェクトルート**: リポジトリルート（`.claude/` を含むディレクトリ）
- DeepEval がインストール済みであること:
  ```bash
  pip install -r tools/benchmark/requirements.txt
  ```

---

## ステップ 1: ドライランで動作確認

`claude` を呼び出さず、シナリオファイルのロードと引数解析のみ確認する。

```bash
python3 -m tools.benchmark.scripts.run_code_analysis \
  --scenarios tools/benchmark/scenarios/code-analysis.json \
  --skill-dir .claude/skills/nabledge-6 \
  --dry-run
```

**期待結果**:
- 終了コード 0
- シナリオ一覧（`ca-01`, `ca-02`, `ca-03`）が標準エラーに出力される

---

## ステップ 2: 1 シナリオで動作確認

```bash
python3 -m tools.benchmark.scripts.run_code_analysis \
  --scenarios tools/benchmark/scenarios/code-analysis.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids ca-01
```

**期待結果**:
- 終了コード 0
- `tools/benchmark/results/YYYYMMDD-HHMMSS/ca-01/` に以下が作成される:
  - `answer.md` — 生成されたコード解析ドキュメント
  - `code_analysis_details.json` — step1/step2 の詳細（対象ファイル、依存クラス、参照セクション）
  - `metrics.json` — 実行時間・コスト
  - `trace.json` — claude の生JSON出力
  - `evaluation.json` — DeepEval 評価結果
- `summary.json` に `skill_dir`, `project_dir`, `scenarios_file`, `executed_at` が含まれる

動作確認後、不要なら削除する:
```bash
rm -rf tools/benchmark/results/YYYYMMDD-HHMMSS
```

---

## ステップ 3: 全シナリオ実行

`YYYYMMDD-HHMM` は実行日時に置き換えること（例: `20260701-1400`）。

```bash
python3 -m tools.benchmark.scripts.run_code_analysis \
  --scenarios tools/benchmark/scenarios/code-analysis.json \
  --skill-dir .claude/skills/nabledge-6 \
  --project-dir .lw/nab-official/v6 \
  --output-dir tools/benchmark/results/YYYYMMDD-HHMM-code-analysis-baseline
```

**オプション引数**:
- `--project-dir <path>`: `find-file.sh` が Java ファイルを探す起点ディレクトリ（シナリオが v6 クラスを使用するため `.lw/nab-official/v6` を指定する）
- `--output-dir <path>`: 結果の出力先ディレクトリ（省略時は `tools/benchmark/results/YYYYMMDD-HHMMSS`）
- `--scenario-ids ca-01,ca-03`: 特定シナリオのみ再実行

**シナリオスキーマ — `when.project_subdir`（任意）**:

`when` ブロックに `"project_subdir": "nablarch-example-rest"` のように指定すると、`claude` の実行ディレクトリ（cwd）を `{project_dir}/{project_subdir}` に絞り込む。同名クラスが複数サブプロジェクトに存在する場合（例: `ProjectAction.java` が `nablarch-example-rest` と `nablarch-example-web` の両方にある）に使用する。`project_subdir` を指定すると、スクリプトへの参照は自動的に絶対パスに切り替わるため、cwd がサブディレクトリになっても `find-file.sh` などが正しく解決される。

```json
{
  "when": {
    "workflow": "code-analysis",
    "input": "ProjectAction",
    "project_subdir": "nablarch-example-rest"
  }
}
```

---

## ステップ 4: 出力フォーマットの確認

生成された `answer.md` が正しい構造を持つか確認する。

```bash
python3 -m tools.benchmark.scripts.check_format_code_analysis \
  --content-file tools/benchmark/results/YYYYMMDD-HHMMSS/ca-01/answer.md
```

**期待結果 (正常)**:
```json
{
  "passed": true,
  "checks": {
    "no_unreplaced_placeholders": true,
    "all_sections_present": true,
    "has_class_diagram": true,
    "has_sequence_diagram": true
  },
  "details": {
    "no_unreplaced_placeholders": "OK",
    "all_sections_present": "OK",
    "has_class_diagram": "OK",
    "has_sequence_diagram": "OK"
  }
}
```

**フォーマット違反がある場合**: 終了コード 1 で `passed: false` が返る。
`details` フィールドで具体的な違反内容を確認できる。

---

## 出力ファイル構造

```
tools/benchmark/results/
└── YYYYMMDD-HHMMSS/          ← run ディレクトリ（またはリネーム後のラベル）
    ├── summary.json          ← 全体サマリー
    ├── ca-01/
    │   ├── answer.md         ← 生成されたコード解析ドキュメント（正常完了時）
    │   ├── code_analysis_details.json  ← step1/step2 詳細（正常完了時）
    │   ├── metrics.json      ← 実行時間・ターン数・コスト（正常完了時）
    │   ├── trace.json        ← claude の生JSON出力（正常完了時 or MarkerError 時）
    │   ├── evaluation.json   ← DeepEval 評価結果（正常完了時）
    │   ├── error.json        ← エラー内容（エラー時のみ）
    │   └── raw_response.txt  ← LLM の生出力テキスト（MarkerError 時のみ）
    ├── ca-02/
    │   └── ...
    └── ca-03/
        └── ...
```

---

## 結果の読み方

### summary.json

```json
{
  "total_scenarios": 3,
  "skill_dir": ".claude/skills/nabledge-6",
  "project_dir": ".lw/nab-official/v6",
  "scenarios_file": "tools/benchmark/scenarios/code-analysis.json",
  "executed_at": "2026-07-01T10:00:00",
  "scenarios": [
    {"id": "ca-01", "status": "ok"},
    {"id": "ca-02", "status": "ok"},
    {"id": "ca-03", "status": "ok"}
  ]
}
```

- `status: "ok"` — 正常完了
- `status: "error"` — 失敗。`error.json` と `raw_response.txt` / `trace.json` で原因確認

### evaluation.json

`scores.answer_correctness` が各 `then.must[].fact` をドキュメントが網羅しているかを評価する。
コード解析ではソースコードから事実を導くため、QA ベンチマークと異なり `retrieval_context` は空（ソース自体が根拠）。

---

## ステップ 5: レポート作成

各ベンチラン完了後、QA ベンチと同様に 2 つのレポートファイルを手動で作成する。

### crossrun-summary.md

スコアの一覧表。`evaluation.json` の `scores` と `metrics` から転記する。

```markdown
# シナリオ別スコアサマリー（{ラベル}）

run数: 1 / シナリオ数: 3

## スコアサマリー

| 指標 | 平均 | ベースライン比（ベースラインのみ省略） |
|---|---|---|
| answer_correctness | X.XXX | ±X.XXX |
| answer_relevancy   | X.XXX | ±X.XXX |
| faithfulness       | X.XXX | ±X.XXX |

## シナリオ別スコア

| scenario | input | correctness | relevancy | faithfulness |
|---|---|---|---|---|
| ca-01 | {クラス名} | X.XXX | X.XXX | X.XXX |
| ca-02 | {クラス名} | X.XXX | X.XXX | X.XXX |
| ca-03 | {クラス名} | X.XXX | X.XXX | X.XXX |

## ベースラインとの差分（verify ランのみ）

| scenario | correctness Δ | relevancy Δ | faithfulness Δ |
|---|---|---|---|
...

## パフォーマンス集約

| メトリクス | 平均 | P50 | 最大 |
|---|---|---|---|
| 実行時間 | Xs | Xs | Xs |
| コスト   | $X.XXX | $X.XXX | $X.XXX |
```

### quality-report.md

ナラティブ形式の評価レポート。crossrun-summary.md をもとに所見を記述する。

```markdown
# nabledge-6 コード分析 品質評価レポート

**対象**: {ラベル}
**前版**: {ベースラインディレクトリ名 or "なし（これが基準版）"}
**測定条件**: 3シナリオ × 1回 = 3評価
...

## 総合評価: {合格 / 注意あり}

{1〜3行の概要}

## 合否判定

### ① 正しい知識を選定し回答できているか → {PASS / FAIL}
### ② 推測や捏造が含まれていないか → {PASS / FAIL}

## ベースラインとの比較（verify ランのみ）

## 計測

## ベンチからの見解
```

**作成後、results ディレクトリごとコミット・プッシュする。**

---

## テストの実行

ユニットテストを実行して実装の正常動作を確認する:

```bash
python3 -m pytest tools/benchmark/tests/test_run_code_analysis.py tools/benchmark/tests/test_check_format_code_analysis.py -v
```

---

## トラブルシューティング

| 症状 | 確認箇所 |
|------|---------|
| `<<<CODE_ANALYSIS_DETAILS_JSON>>> marker not found` | `raw_response.txt` で LLM 出力を確認。プロンプトが長すぎる or モデルが指示を無視している |
| `Invalid JSON in code analysis details` | `trace.json` → `result` フィールドを確認 |
| `find-file.sh: command not found` | `--project-dir` がリポジトリルートを指していない |
| 全シナリオが `ca-XX: ERROR — claude exited with code 1` | `--skill-dir` パスを確認。`workflows/code-analysis.md` が存在するか確認 |
