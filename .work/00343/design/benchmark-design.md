# ベンチマーク設計

**Date**: 2026-05-18

## 目的

検索改善の全コンポーネント（ヒアリング・意味検索・回答生成・検証・キーワード検索）を定量評価するベンチマーク基盤。

## スコープ

### 部品ベンチマーク

各コンポーネントを個別に評価する。`simulate_*.py` で部品単位のベンチマークを実行し、`evaluate.py` + `report.py` で評価・レポート生成。改善サイクルは部品ベンチマークレベルで回す。

### E2Eベンチマーク

スキルワークフロー（`qa.md`）を通しで実行する。ベンチマーク側は1実装で複数のスキルバージョンを比較できる。

- 現行スキルのE2Eベースライン取得
- 新スキルデプロイ後のE2E取得
- 現行以上になるまで改善（部品ベンチマーク → E2Eベンチマークの順で改善）

部品ベンチマークはE2E追加後も残す。改善の流れは部品 → E2Eとする（E2Eレベルだと原因特定が困難なため）。

### LLM判定ライブラリ（別Issue）

deepevalによるLLM判定は別Issueとして対応。現時点は自前の `evaluate.py` でベンチマークする。

## シナリオ設計

### フェーズ

シナリオはNablarch開発者が実際に直面する場面を3つのフェーズで分類する。

| フェーズ | usecase値 | 説明 | 例 |
|---|---|---|---|
| コードレビュー | `review` | 既存コードのレビュー時に実装の妥当性を確認する場面 | 「このRESTルーティング設定は正しいか？」 |
| 影響調査 | `impact` | 機能追加・移行・設計判断時に仕様を確認する場面 | 「セッションストアの選択肢と特徴は？」 |
| アプリ実装 | `qa` | 実装作業中に使い方・実装パターンを確認する場面 | 「CSVを1件ずつ読み込むにはどうする？」 |

### スコープ外シナリオ（out-of-scope）

知識ファイルにない機能・技術を尋ねたとき、スキルが推測せず正直に「情報がない」と答えられるかを検証する。影響調査・アプリ実装フェーズで「Nablarchにこの機能があるか？」と確認する場面が典型的なユースケース。

**評価方法**: 通常シナリオと同じ評価軸（回答精度・ハルシネーション）を使う。`must` の fact に「知識ファイルに該当情報がないと回答している」を設定する。

**シナリオID**: `oos-` プレフィックスを使用（例: `oos-impact-01`）。

**現在のout-of-scopeシナリオ**:

| ID | フェーズ | 質問概要 |
|---|---|---|
| `oos-impact-01` | impact | OAuth2/OpenID Connect認証の対応可否 |
| `oos-qa-01` | qa | WebSocketによるリアルタイム通知の実装方法 |

## 評価軸

| 軸 | QA | Keyword | 判定方式 | 判定基準 |
|---|:---:|:---:|---|---|
| 回答精度 | ✓ | - | LLM判定 | must factが回答に含まれるか |
| ハルシネーション | ✓ | - | LLM判定 | 知識ベースにない主張が回答に含まれないか |

キーワード検索はセクションIDの一致をルールベースで判定する。

## スコアリング

| 軸 | スコア | 計算式 |
|---|---|---|
| 回答精度 | 0.0〜1.0 | must_facts_present / must_facts_total |
| ハルシネーション | 0 or 1 | 検出なし=1、検出あり=0 |
| キーワード検索精度 | 0.0〜1.0 | must_found / must_total |

**PASS閾値**:
- 回答精度: スコア = 1.0（全must fact PRESENT確定）
- ハルシネーション: スコア = 1
- キーワード検索精度: スコア = 1.0（must全件一致）

**UNCERTAIN含むシナリオの集計**: 3 run中いずれかにUNCERTAINを含むシナリオは集計から除外し、除外件数を別欄で報告する。

## 判定方式

### QA: LLM判定

**回答精度（C-claim判定）**:

各must factについて、回答テキストにその情報が含まれているかをLLMで判定する。

入力:
- fact: シナリオのmust fact
- answer: ワークフローの回答テキスト
- section_content: factの参照先セクションの本文（判定の根拠として）

出力: PRESENT / ABSENT / UNCERTAIN

判定基準:
- PRESENT: factの情報が回答に含まれている（表現の違いは許容）
- ABSENT: factの情報が回答に含まれていない
- UNCERTAIN: 判定が困難（人間レビュー必須）

**ハルシネーション判定**:

回答テキスト中のNablarch固有の主張が、知識ベースの内容で裏付けられるかをLLMで判定する。

入力:
- answer: ワークフローの回答テキスト
- sections: シナリオのmust + acceptableセクションの本文（ゴールドスタンダード）

検索で取得されたセクションではなく、シナリオ定義のゴールドスタンダードを使用する。これにより検索精度とハルシネーション判定の独立性を確保する。

出力: PASS / FAIL / UNCERTAIN + 検出箇所リスト

判定基準:
- 一般的なプログラミング知識はハルシネーションではない
- Nablarch固有のAPI名・設定名・動作仕様の主張のみ検証対象
- セクション内容に裏付けがない主張をハルシネーションとする

### 評価エンジンの抽象化

品質評価のLLM判定部分は、自前実装からライブラリ（deepeval）へ切り替え可能な設計とする（別Issue）。

### キーワード検索: ルールベース判定

キーワード検索スクリプトの出力からセクションIDリストを取得し、must sectionsとの一致を確認する。

## 診断情報

評価スコアとは独立に、問題の原因切り分けに使う情報をランナーが記録する。スコア対象外。

| 診断情報 | 内容 |
|---|---|
| ヒアリング行動 | 質問したか、何を質問したか |
| 検索セクションID | どのセクションが検索結果に含まれたか |
| 回答全文 | ワークフローの最終回答テキスト |
| 実行トレース | `claude -p` の全ターンログ（何ターン目に何をしたか、ツール呼び出し内容）|

`trace.json` は `claude -p --output-format json` の生出力全体を保存したもの。QAエキスパートが定性評価（回答の質・検索挙動・ハルシネーションの性質）を行う際に参照する。数値メトリクスだけでは見えない「なぜそのセクションを使ったか」「どの判断で回答が変わったか」を追跡できる。

## メトリクス

### 品質メトリクス（評価対象）

| メトリクス | 計算式 | PASS閾値 |
|---|---|---|
| 回答精度 | must_facts_present / must_facts_total | 1.0 |
| ハルシネーション | 検出なし=1、検出あり=0 | 1 |
| キーワード検索精度 | must_found / must_total | 1.0 |

### パフォーマンスメトリクス（計測対象）

品質ゲートではなく、パフォーマンス比較用。`claude -p --output-format json` の出力から全て取得できる。

| メトリクス | 取得元フィールド |
|---|---|
| 実行時間（総合） | `duration_ms` |
| 実行時間（API） | `duration_api_ms` |
| 入力トークン | `usage.input_tokens` |
| 出力トークン | `usage.output_tokens` |
| キャッシュ読取トークン | `usage.cache_read_input_tokens` |
| キャッシュ作成トークン | `usage.cache_creation_input_tokens` |
| コスト | `total_cost_usd` |
| ターン数 | `num_turns` |

## モデル制約

| 用途 | モデル |
|---|---|
| ワークフロー実行 | sonnet |
| 評価LLM（C-claim・ハルシネーション判定） | sonnet |

## E2Eベンチマーク実行

実行手順・レポート作成・定性評価の具体的な手順は `tools/benchmark/HOW-TO-RUN.md` を参照。

### シナリオファイルとhearing_answer

hearing_answerをプロンプトに注入するかどうかはシナリオファイルが制御する。`run_e2e.py` はシナリオに `hearing_answer`（非null）が設定されていれば注入し、なければ注入しない。スクリプト側にモード切り替えはない。

| ベンチマーク | シナリオファイル | hearing_answer |
|---|---|---|
| 現行スキルベースライン | `qa-current.json` | なし |
| 新スキルベンチマーク | `qa.json` | あり（全シナリオに設定済み） |

`qa-current.json` は `qa.json` と同じシナリオ定義で `hearing_answer` フィールドのみ除いたもの。

### 構造化キャプチャマーカー

ワークフローは各ステージの出力を以下のマーカー形式で出力する。全マーカーの出力は必須。マーカーが欠落した場合はランナーエラー。

```
<<<BENCHMARK_HEARING>>>
{"status": "skipped" | "asked", "questions": ["質問1", "質問2"]}
<<<END_BENCHMARK_HEARING>>>

<<<BENCHMARK_SEARCH>>>
{"section_ids": ["path/to/file.json:s1", "path/to/file.json:s3"]}
<<<END_BENCHMARK_SEARCH>>>

<<<BENCHMARK_ANSWER>>>
{回答テキスト全文}
<<<END_BENCHMARK_ANSWER>>>
```

### CLIパターン（内部実装）

```python
result = subprocess.run(
    [
        "claude", "-p",
        "--model", "sonnet",
        "--output-format", "json",
        "--no-session-persistence",
        "--allowedTools", "Bash(keyword-search.sh *) Bash(read-sections.sh *) Read",
        prompt,
    ],
    capture_output=True, text=True,
    cwd=str(skill_dir),
    timeout=360,
)
```

必須ルール:
- 部品ベンチマーク: `cwd="/tmp"`
- E2Eベンチマーク: `cwd=skill_dir`
- `--bare` は使わない（OAuth/keychainを無効化するためCI以外では使えない）
- `--json-schema` は使わない（非bareモードでは動作しない）

## ディレクトリ構成

```
tools/benchmark/
  components/
    prompts/           ← スキルコンポーネントのプロンプト
    scripts/           ← keyword-search.sh, read-sections.sh
  prompts/             ← 評価用プロンプト（c-claim-judge.md, hallucination-judge.md）
  scenarios/
    qa.json            ← QAシナリオ（hearing_answerあり）— 新スキルベンチ用
    qa-current.json    ← QAシナリオ（hearing_answerなし）— 現行スキルベースライン用
    keyword-search.json
  scripts/
    run_e2e.py         ← E2Eベンチマーク実行
    evaluate.py        ← 評価（C-claim + ハルシネーション）
    report.py          ← レポート生成
    simulate_*.py      ← 部品ベンチマーク
    run.py             ← 部品チェーン実行
    generate_index.py  ← index.md生成
  tests/               ← スクリプトのユニットテスト
  results/
    {run-label}/       ← ベンチマーク実行結果（gitコミットして比較可能にする）
      run-1/
        {scenario-id}/
          hearing.json
          search.json
          answer.md
          metrics.json
          trace.json
          evaluation.json
      run-2/
      run-3/
      report.md        ← 3 run集計レポート
```

run-labelの例: `baseline-current`（現行スキル）、`v1-new-search`（新スキル第1版）

各 run は `run_e2e.py` を1回実行した結果。タイムスタンプディレクトリ（`results/YYYYMMDD-HHMMSS/`）として生成され、完了後に `results/{run-label}/run-{N}/` にリネームする。

## summary.json

各run完了時に生成。実行コンテキストを含む。

```json
{
  "run_label": "baseline-current",
  "skill_dir": ".claude/skills/nabledge-6",
  "scenarios_file": "tools/benchmark/scenarios/qa-current.json",
  "executed_at": "2026-05-18T17:13:00",
  "total_scenarios": 28,
  "scenarios": [
    {
      "id": "pre-01",
      "search_sections": 5,
      "hearing_status": "skipped"
    }
  ]
}
```

## metrics.json

`claude -p --output-format json` の出力から取得した全メトリクスを保存する。

```json
{
  "duration_ms": 45230,
  "duration_api_ms": 42100,
  "num_turns": 5,
  "total_cost_usd": 0.045,
  "usage": {
    "input_tokens": 12500,
    "output_tokens": 2500,
    "cache_read_input_tokens": 10000,
    "cache_creation_input_tokens": 2500
  },
  "model_usage": {
    "claude-sonnet-4-6": {
      "input_tokens": 12500,
      "output_tokens": 2500,
      "cost_usd": 0.045
    }
  }
}
```
