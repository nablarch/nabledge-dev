# ベンチマーク設計書

`tools/benchmark/` の実装の設計。

---

## 概要

QAワークフロー（`workflows/qa.md`）を E2E で実行し、回答精度・関連性・ハルシネーションを自動評価する。キーワード検索スクリプトの単体評価も独立して実行できる。

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
│   └── e2e-prompt.md           — E2Eプロンプトテンプレート
├── tests/                       — ユニットテスト
├── results/                     — 実行結果（gitトラッキング対象、コミット任意）
└── HOW-TO-RUN.md               — 実行手順
```

---

## シナリオ定義

**設計意図**: シナリオは「入力・期待値・ヒアリング事前設定」を宣言的に定義し、ランナーと評価ロジックから分離する。期待値（`must`）は「回答に含まれるべき事実」と「その根拠セクション」をセットで持つことで、事実の有無をナレッジと照合して機械的に判定できる。

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
        "expected_hearing": "should_skip | must_ask | nice_to_ask",
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
| `when.expected_hearing` | ヒアリングの期待値（`should_skip`: スキップ予想、`must_ask`: ヒアリング必須、`nice_to_ask`: ヒアリングが望ましいが任意） |
| `when.hearing_answer` | ランナーがStep 1/2をスキップしてStep 3から開始するための事前設定値 |
| `then.must` | 回答に必ず含まれるべき事実のリスト（`section` はDeepEvalが `retrieval_context` を構築する際に参照するナレッジセクション） |
| `then.acceptable` | あってもよいセクションのリスト（評価には不使用） |

`must.section` が `null` または未設定のケース: アウトオブスコープシナリオ（ナレッジに情報がない質問）で使用。`retrieval_context` はセクションなしで空リストを渡す。

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

**設計意図**: `qa.md` をそのまま E2E 実行することで、実際のユーザー体験と同じ条件で品質を測る。2点の工夫がある。

1つ目は**ヒアリングのスキップ**。`qa.md` は Step 2 でユーザーに処理方式・目的を確認するが、ベンチマークは非対話型のため実行できない。そこでシナリオの `hearing_answer` を質問テキストに付記（`（処理方式: X）（目的: Y）`）してから渡すことで、`qa.md` が Step 1 で両軸を確定済みと判断し Step 3 へ直接進む。

2つ目は**AI判断の可視化**。通常の `qa.md` に加え `e2e-prompt.md` の追加指示を重ねることで、Step 3 のページ/セクション選定理由、Step 4 の実際に読んだセクション、Step 8 の使用/未使用セクションをすべて `Workflow Details` として出力させる。これによりAIがどのページを選び、なぜその回答になったかを追跡でき、閾値割れの根本原因調査が可能になる。ただし追加の出力指示により、実行時間・トークン量は通常使用時より増大する。

### 処理フロー

```
シナリオJSON読み込み
  ↓
各シナリオに対して:
  1. E2Eプロンプト構築（hearing_answer を質問テキストに付記 + e2e-prompt.md テンプレート）
  2. claude -p 実行（TIMEOUT=360秒）
  3. レスポンスのパース（`<<<WORKFLOW_DETAILS_JSON>>>` マーカーで分割）
  4. 結果ファイル保存
  5. evaluate_scenario() で評価
  6. evaluation.json 保存
  ↓
summary.json 保存
```

### claude -p の設定

| オプション | 値 | 理由 |
|---|---|---|
| `--model` | `sonnet` | 精度と速度のバランス |
| `--output-format` | `json` | メトリクスの取得 |
| `--no-session-persistence` | （フラグ） | セッション汚染の防止 |
| `--allowedTools` | `Bash(bash scripts/keyword-search.sh *) Bash(bash scripts/read-sections.sh *) Read` | スキルが使うツールのみ許可 |
| `cwd` | スキルディレクトリ | スクリプトの相対パスを解決するため |

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
| `summary.json` | 実行完了時 | 全シナリオのサマリー（`total_scenarios`, `skill_dir`, `scenarios_file`, `executed_at`, `scenarios`） |

---

## キーワード検索ランナー（`scripts/run_keyword_search.py`）

**設計意図**: LLMを介さず `keyword-search.sh` を直接実行し、リコール率（must セクションをどれだけ発見できたか）のみで評価する。QAと異なりヒアリング・回答生成・ハルシネーション検証がないため、シンプルなスクリプト呼び出しで完結する。

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

### 評価指標

**リコール率** = 発見した must セクション数 / must セクション総数  
must セクションがないシナリオのリコール率は 1.0。

---

## 評価ロジック（`scripts/evaluate.py`）

**設計意図**: 評価を3軸（回答精度・関連性・ハルシネーション）で行い、すべてDeepEvalの標準RAGメトリクスで自動判定する。スコアは0.0〜1.0の数値で返り、閾値を下回ったシナリオを改善対象として特定する。

### 評価の3軸

| 軸 | DeepEvalクラス | 定義 | スコア値域 |
|---|---|---|---|
| 回答精度（answer_correctness） | `GEval` | `actual_output` が `must.facts` に列挙された事実を網羅しているか | 0.0〜1.0 |
| 関連性（answer_relevancy） | `AnswerRelevancyMetric` | `actual_output` が `input`（質問）に対して関連した内容を回答しているか | 0.0〜1.0 |
| ハルシネーション（faithfulness） | `FaithfulnessMetric` | `actual_output` の主張が `retrieval_context`（検索セクション内容）で裏付けられているか | 0.0〜1.0 |

### LLMTestCase へのデータマッピング

| `LLMTestCase` フィールド | 取得元 |
|---|---|
| `input` | `scenario["when"]["input"]` |
| `actual_output` | `answer.md` の内容 |
| `expected_output` | `must.facts` を改行結合したテキスト（answer_correctness 用） |
| `retrieval_context` | `diagnostics.search_sections`（`path/to/file.json:sN` 形式）の各セクション内容リスト |

**注意**: `retrieval_context` の未解決参照は無視（スキップ）する。

### スコア計算

各指標はDeepEvalライブラリが非同期で計算し、`float`（0.0〜1.0）として返す。計算失敗時は `None`。

`evaluation.json["scores"]` の構造:

```json
{
  "answer_correctness": {"score": 0.9, "reason": "..."},
  "answer_relevancy":   {"score": 0.8, "reason": "..."},
  "faithfulness":       {"score": 1.0, "reason": "..."}
}
```

`reason` はDeepEvalが生成する判定根拠テキスト（調査・デバッグ用）。

---

## 評価フロー

```
ベンチマーク実行（全シナリオ）
  ↓
DeepEval 3指標を自動計算（スコア + reason を evaluation.json に保存）
  ↓
report.py でレポート生成（閾値割れシナリオを一覧）
  ↓
3 run完了後、集計・比較・根本原因調査
```

詳細な実施手順は `tools/benchmark/HOW-TO-RUN.md` を参照。

---

## レポート生成（`scripts/report.py`）

**設計意図**: 3種類のレポートを用途に応じて出力する。シナリオ別レポートは閾値割れの原因調査用、サマリーレポートは全体品質の把握用、比較レポートは改善前後の変化確認用。

### シナリオ別レポート

各シナリオの評価結果を表形式で出力:
- DeepEval 3指標のスコアと判定根拠（reason）
- 診断情報（ヒアリング状態・検索セクション）
- メトリクス（実行時間・トークン量・ツール呼び出し数）

### サマリーレポート

全シナリオを集計:
- DeepEval 3指標 × 対象件数・平均スコア・最低スコア・閾値通過率
- パフォーマンスサマリー（実行時間・API時間・ターン数・トークン量・コスト の 平均/P50/P95/最大/合計）

### 比較レポート

2つの実行ラベルを比較:
- 品質比較（各指標の平均スコア・差分）
- パフォーマンス比較（実行時間・コスト・ターン数・変化率）
- シナリオ別差分（スコアが変化したシナリオのみ）

### レポート出力先

| レポート種別 | ファイル |
|---|---|
| フルレポート（1実行） | `{run-dir}/report.md` |
| 比較レポート | `{run-dir}/comparison-{label_b}.md` |
| 退行チェックレポート | `{run-dir}/regression-check.md` |
| 3run横断集約レポート | `{crossrun-dir}/crossrun-summary.md` |

---

## DeepEval RAGメトリクス

### 指標選定根拠

既存の評価軸（C-claimジャッジ・ハルシネーションジャッジ）はLLM-as-judgeによる独自指標であった。DeepEvalの3指標との相関分析（SC2）を実施した結果、`answer_correctness` ↔ `accuracy` が96.4%一致、`faithfulness` ↔ `hallucination` が88.5%一致することを確認した。この結果を受け、独自LLMジャッジをDeepEval標準指標に完全置き換えとした。

DeepEval採用の利点:
- **再現性**: 数値スコアで閾値による自動判定が可能（`UNCERTAIN` による人間確認ループが不要）
- **標準性**: RAG研究コミュニティの標準指標との比較が可能
- **補完**: `answer_relevancy` は旧指標では捉えられなかった「的外れな回答」を検出できる

### ジャッジLLM接続方式

- **方式**: DeepEval組み込みの `AmazonBedrockModel` を使用
- **モデル**: `jp.anthropic.claude-sonnet-4-6`（環境変数 `BEDROCK_MODEL_ID` で上書き可能）
- **リージョン**: `ap-northeast-1`（環境変数 `AWS_REGION` で上書き可能）
- **SSL**: `AWS_CA_BUNDLE` 環境変数で社内CA証明書を指定（`/usr/local/share/ca-certificates/ca.crt`）
- **認証**: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` 環境変数（既存Bedrock接続と共通）

### PASS/FAILしきい値

各指標の閾値はNabledgeの品質基準（ミッションクリティカルな金融系システム向け）から設定する:

| 指標 | 閾値 | 根拠 |
|------|------|------|
| answer_correctness | 0.99 | 実装に必要な事実の欠落は誤実装に直結する |
| answer_relevancy | 0.95 | 多少の冗長・脱線は許容するが大きな逸脱は不可 |
| faithfulness | 0.99 | ハルシネーション（根拠なし記述）は誤実装に直結する |

閾値を下回ったシナリオをレポートで一覧し、改善対象として扱う。

### 依存関係

`tools/benchmark/requirements.txt` に記載:

```
deepeval
aiobotocore
```

`setup.sh` の `tools/rbkc/requirements.txt` インストールブロックの直後に自動インストールされる。

---

## 実行手順

→ `tools/benchmark/HOW-TO-RUN.md` を参照。
