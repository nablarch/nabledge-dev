# ベンチマーク設計書

`tools/benchmark/` の実装の設計。

---

## 概要

QAワークフロー（`workflows/qa.md`）を E2E で実行し、回答精度とハルシネーションを自動評価する。  
キーワード検索スクリプトの単体評価も独立して実行できる。

---

## ディレクトリ構成

```
tools/benchmark/
├── scenarios/
│   ├── qa.json                  — QAシナリオ定義
│   └── keyword-search.json      — キーワード検索シナリオ定義
├── scripts/
│   ├── run_qa.py               — QA E2Eランナー
│   ├── run_keyword_search.py   — キーワード検索ランナー
│   ├── evaluate.py             — 評価ロジック
│   └── report.py               — レポート生成
├── prompts/
│   ├── e2e-prompt.md           — E2Eプロンプトテンプレート
│   ├── c-claim-judge.md        — C-claimジャッジプロンプト
│   └── hallucination-judge.md  — ハルシネーションジャッジプロンプト
├── tests/                       — ユニットテスト
├── results/                     — 実行結果（gitトラッキング対象、コミット任意）
└── HOW-TO-RUN.md               — 実行手順
```

---

## シナリオ定義

### QAシナリオ（`scenarios/qa.json`）

スキーマバージョン: `1.1`

```json
{
  "scenarios": [
    {
      "id": "pre-01",
      "phase": "pre-benchmark",
      "given": {
        "usecase": "...",
        "category": "...",
        "description": "..."
      },
      "when": {
        "workflow": "qa",
        "input": "質問テキスト",
        "expected_hearing": "should_skip | should_ask",
        "hearing_answer": {
          "processing_type": "処理方式名 | null",
          "purpose": "目的名"
        }
      },
      "then": {
        "must": [
          {"fact": "回答に含まれるべき事実", "section": "path/to/file.json:sN"}
        ],
        "acceptable": [
          {"section": "path/to/file.json:sN"}
        ]
      }
    }
  ]
}
```

**フィールド説明**:

| フィールド | 説明 |
|---|---|
| `id` | シナリオID（例: `pre-01`, `qa-01`, `impact-01`） |
| `phase` | フェーズ（`pre-benchmark`, `benchmark`, `impact`） |
| `when.input` | ユーザーの質問テキスト |
| `when.expected_hearing` | ヒアリングが発生するか（`should_skip`: スキップ予想、`should_ask`: 発生予想） |
| `when.hearing_answer` | ランナーが Step 1/2 をスキップしてStep 3から開始するための事前設定値 |
| `then.must` | 回答に必ず含まれるべき事実のリスト（`section` はC-claimジャッジが参照するナレッジセクション） |
| `then.acceptable` | あってもよいセクションのリスト（評価には不使用） |

`must.section` が `null` または未設定のケース: アウトオブスコープシナリオ（ナレッジに情報がない質問）で使用。C-claimジャッジにはセクションなしで空文字を渡す。

### キーワード検索シナリオ（`scenarios/keyword-search.json`）

スキーマバージョン: `1.0`

```json
{
  "scenarios": [
    {
      "id": "review-01",
      "given": {"usecase": "...", "category": "...", "description": "..."},
      "when": {
        "workflow": "keyword-search",
        "input": ["キーワード1", "キーワード2"]
      },
      "then": {
        "must": [
          {"fact": "...", "section": "path/to/file.json:sN"}
        ],
        "acceptable": [
          {"section": "path/to/file.json:sN"}
        ]
      }
    }
  ]
}
```

`when.input` はキーワードの配列（または単一文字列）。評価はリコール率（must セクションの発見率）のみ。

---

## QA E2Eランナー（`scripts/run_qa.py`）

### 処理フロー

```
シナリオJSON読み込み
  ↓
各シナリオに対して:
  1. E2Eプロンプト構築（e2e-prompt.md テンプレート）
  2. claude -p 実行（TIMEOUT=360秒）
  3. レスポンスのパース（"### Workflow Details" で分割）
  4. 結果ファイル保存
  5. evaluate_scenario() で評価
  6. evaluation.json 保存
  ↓
summary.json 保存
```

### 実行コマンド

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  [--scenario-ids pre-01,qa-01]
```

### claude -p の設定

| オプション | 値 | 理由 |
|---|---|---|
| `--model` | `sonnet` | 精度と速度のバランス |
| `--output-format` | `json` | メトリクスの取得 |
| `--no-session-persistence` | （フラグ） | セッション汚染の防止 |
| `--allowedTools` | `Bash(bash scripts/keyword-search.sh *) Bash(bash scripts/read-sections.sh *) Read` | スキルが使うツールのみ許可 |
| `cwd` | スキルディレクトリ | スクリプトの相対パスを解決するため |

### E2Eプロンプト構築（`build_qa_prompt`）

`prompts/e2e-prompt.md` テンプレートの `{workflow}` と `{question}` を置換する。

`{question}` の構築:
- `hearing_answer` がある場合: `"質問（処理方式: X）（目的: Y）"` と付記
  - `processing_type` が null の場合は `（処理方式: X）` 部分を省略
- `hearing_answer` がない場合: 質問テキストそのまま

`e2e-prompt.md` の追加指示により、Step 1/2 をスキップして Step 3 から開始する（ヒアリング済みとして扱う）。また、各ステップの判断理由を `Workflow Details` セクションとしてレスポンス末尾に出力させる。

### レスポンスパース（`parse_qa_response`）

レスポンスを `"### Workflow Details"` で分割:
- 上部 → `answer`（最終回答テキスト）
- 下部の ` ```json...``` ` ブロック → `workflow_details`（各ステップの詳細JSON）

いずれかが欠如している場合は `MarkerError` を発生させる。

### 出力ファイル（シナリオごと）

| ファイル | 存在条件 | 内容 |
|---|---|---|
| `workflow_details.json` | 正常完了時 | step3: ページ/セクション選択理由、step4: 読んだセクションID、step8: 使用/未使用セクション |
| `answer.md` | 正常完了時 | 最終回答テキスト |
| `metrics.json` | 正常完了時 | 実行時間・ターン数・コスト・トークン量 |
| `trace.json` | 正常完了時 | claude -p の生JSON出力 |
| `evaluation.json` | 正常完了時 | 自動評価結果 |
| `error.json` | エラー時のみ | エラー内容（`error`, `exception_type`） |
| `raw_response.txt` | MarkerError時のみ | パース失敗したレスポンス全文 |

| ファイル | 内容 |
|---|---|
| `summary.json` | 全シナリオのサマリー（`total_scenarios`, `skill_dir`, `scenarios_file`, `executed_at`, per-scenario情報） |

---

## キーワード検索ランナー（`scripts/run_keyword_search.py`）

### 処理フロー

```
シナリオJSON読み込み
  ↓
各シナリオに対して:
  1. keyword-search.sh を subprocess で実行
  2. リコール評価（must セクションの発見率）
  3. 結果ファイル保存
  ↓
summary.json 保存
```

### 実行コマンド

```bash
python3 -m tools.benchmark.scripts.run_keyword_search \
  --scenarios tools/benchmark/scenarios/keyword-search.json \
  --skill-dir .claude/skills/nabledge-6 \
  [--scenario-ids review-01]
```

### 評価指標

**リコール率** = 発見した must セクション数 / must セクション総数  
must セクションがないシナリオのリコール率は 1.0。

---

## 評価ロジック（`scripts/evaluate.py`）

### 評価の2軸

| 軸 | 評価方法 | 判定値 |
|---|---|---|
| 回答精度（C-claim） | 各 `must.fact` がanswer.mdに含まれているかをLLMで判定 | `PRESENT` / `ABSENT` / `UNCERTAIN` |
| ハルシネーション | answer.mdのNablarch固有クレームがナレッジセクションで裏付けられるかをLLMで判定 | `PASS` / `FAIL` / `UNCERTAIN` |

### C-claimジャッジ（`build_claim_prompt`）

各 `must.fact` について:
1. `c-claim-judge.md` プロンプトテンプレートに `{fact}`, `{answer}`, `{section_content}` を挿入
2. `call_llm()` でSonnetを呼び出す
3. `{"verdict": "PRESENT"|"ABSENT"|"UNCERTAIN", "reason": "..."}` を返す

`must.section` が空の場合はセクション内容に空文字を渡す。

### ハルシネーションジャッジ（`build_hallucination_prompt`）

`sections_text` の構築:
1. `must` と `acceptable` の全セクションの個別コンテンツを追加（重複除去）
2. ランナーが選択した `step3.selected_pages` の全ページの全セクションを追加（重複除去）  
   ※ページ全体を含めるのは、LLMがStep 2でページ全体を読んでいるため

`hallucination-judge.md` プロンプトテンプレートに `{answer}`, `{sections}` を挿入し、`call_llm()` で判定。

返値: `{"verdict": "PASS"|"FAIL"|"UNCERTAIN", "claims": [...], "reason": "..."}`

### スコア計算

**精度スコア**:
- `UNCERTAIN` が1件でも含まれる → `None`（未確定）
- それ以外 → `PRESENT` 件数 / 総件数

**ハルシネーションスコア**:
- `PASS` → `1`
- `FAIL` → `0`
- `UNCERTAIN` → `None`

### 人間レビュー判定

以下の場合に `needs_human_review = true`:
- いずれかのC-claim判定が `UNCERTAIN` または `ABSENT`
- ハルシネーション判定が `FAIL` または `UNCERTAIN`

### LLM呼び出し（`call_llm`）

`claude -p` を `subprocess` で実行。JSONスキーマをプロンプト末尾に付与して構造化出力を強制する。  
モデル: Sonnet。`cwd=/tmp`（スキルディレクトリとは無関係）。

---

## レポート生成（`scripts/report.py`）

### シナリオ別レポート（`format_scenario_report`）

各シナリオの評価結果を表形式で出力:
- 評価結果表（回答精度・ハルシネーションの自動判定・人間判定・スコア）
- 回答精度詳細（各factの判定と理由）
- 診断情報（ヒアリング状態・検索セクション）
- メトリクス（実行時間・トークン量・ツール呼び出し数）

### サマリーレポート（`format_summary_report`）

全シナリオを集計:
- 精度・ハルシネーション × 対象件数・確定件数・未確定・平均スコア・最低スコア・全PASS率
- パフォーマンスサマリー（実行時間・API時間・ターン数・トークン量・コスト の 平均/P50/P95/最大/合計）

**集計ルール**: `UNCERTAIN` を含むシナリオは「未確定」としてカウントし、平均・PASS率の計算から除外する。

### 比較レポート（`format_comparison_report`）

2つの実行ラベルを比較:
- 品質比較（精度平均・ハルシネーションPASS率・差分）
- パフォーマンス比較（実行時間・コスト・ターン数・変化率）
- シナリオ別差分（精度スコアが変化したシナリオのみ）

### レポート出力先

| レポート種別 | ファイル |
|---|---|
| フルレポート（1実行） | `{run-dir}/report.md` |
| 比較レポート | `{run-dir}/comparison-{label_b}.md` |

---

## 実行手順（HOW-TO-RUN.md の要約）

### ステップ 1: 1シナリオで動作確認

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids pre-01
```

確認後、動作確認用ディレクトリを削除する。

### ステップ 2: 全シナリオ実行（1 run）

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6
```

完了後、出力ディレクトリを `results/{run-label}/run-N/` にリネームする。

### ステップ 3: 妥当性評価

FAIL/UNCERTAIN シナリオについて `workflow_details.json` と `answer.md` を読み、原因を分類する:
- **評価基準の問題**: factやclaimの記述が不正確
- **ナレッジ/RSTの問題**: ナレッジに誤りがあり回答の方が正しい
- **ナレッジ未収録の補足**: Nablarch固有でない一般的な補足情報
- **スキルの挙動問題**: 検索ミス・回答生成ミス・Nablarch固有のハルシネーション

AIが分類を提案 → ユーザーが承認した FAIL のみ確定FAILとなる。3 run繰り返す。

### ステップ 4: 比較集計（3 run完了後）

3 runの数値を集計し、前回ラベルと比較する。

### ステップ 5: 確定FAILの根本原因調査

確定FAILについて再現性・原因を調査し、「揺らぎ（対処不要）」か「要改善」かをAIが提案。ユーザーが対応要否を判定する。

### ステップ 6: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/
git commit -m "chore: save {run-label} E2E benchmark results ({N} runs)"
git push
```
