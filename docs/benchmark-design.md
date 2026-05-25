# ベンチマーク設計書

`tools/benchmark/` の実装の設計。

---

## 概要

QAワークフロー（`workflows/qa.md`）を E2E で実行し、回答精度とハルシネーションを自動評価する。キーワード検索スクリプトの単体評価も独立して実行できる。

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
| `when.hearing_answer` | ランナーがStep 1/2をスキップしてStep 3から開始するための事前設定値 |
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

**設計意図**: `qa.md` をそのまま E2E 実行することで、実際のユーザー体験と同じ条件で品質を測る。2点の工夫がある。

1つ目は**ヒアリングのスキップ**。`qa.md` は Step 2 でユーザーに処理方式・目的を確認するが、ベンチマークは非対話型のため実行できない。そこでシナリオの `hearing_answer` を質問テキストに付記（`（処理方式: X）（目的: Y）`）してから渡すことで、`qa.md` が Step 1 で両軸を確定済みと判断し Step 3 へ直接進む。

2つ目は**AI判断の可視化**。通常の `qa.md` に加え `e2e-prompt.md` の追加指示を重ねることで、Step 3 のページ/セクション選定理由、Step 4 の実際に読んだセクション、Step 8 の使用/未使用セクションをすべて `Workflow Details` として出力させる。これによりAIがどのページを選び、なぜその回答になったかを追跡でき、FAILの根本原因調査が可能になる。ただし追加の出力指示により、実行時間・トークン量は通常使用時より増大する。

### 処理フロー

```
シナリオJSON読み込み
  ↓
各シナリオに対して:
  1. E2Eプロンプト構築（hearing_answer を質問テキストに付記 + e2e-prompt.md テンプレート）
  2. claude -p 実行（TIMEOUT=360秒）
  3. レスポンスのパース（"### Workflow Details" で分割）
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
| `summary.json` | 実行完了時 | 全シナリオのサマリー（`total_scenarios`, `skill_dir`, `scenarios_file`, `executed_at`） |

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

**設計意図**: 評価を2軸に分ける。「回答精度」は期待する事実が回答に含まれているかを測り、「ハルシネーション」はナレッジに根拠のないNablarch固有クレームが混入していないかを測る。

LLM判定は全シナリオに対して実施するが、結果はAIによる詳細レポートと合わせてユーザーが確認し、FAILは人間が最終判断する。LLMジャッジは判定を求められると厳しく指摘する傾向があり、正しい回答をFAILと判定するケースがある。そのためLLM判定の結果をそのまま確定させるのではなく、ユーザーが承認したFAILのみを確定FAILとして扱う。

### 評価の2軸

| 軸 | 評価方法 | 判定値 |
|---|---|---|
| 回答精度（C-claim） | 各 `must.fact` がanswer.mdに含まれているかをLLMで判定 | `PRESENT` / `ABSENT` / `UNCERTAIN` |
| ハルシネーション | answer.mdのNablarch固有クレームがナレッジセクションで裏付けられるかをLLMで判定 | `PASS` / `FAIL` / `UNCERTAIN` |

### C-claimジャッジ

各 `must.fact` について `c-claim-judge.md` プロンプトに `{fact}`, `{answer}`, `{section_content}` を挿入してLLMで判定する。`must.section` が空の場合はセクション内容に空文字を渡す。

### ハルシネーションジャッジ

判定の根拠テキスト（`sections_text`）は2種類のコンテンツを合わせて構築する:
1. `must` と `acceptable` の全セクション内容
2. ランナーが選択した `step3.selected_pages` の全ページの全セクション — LLMが意味検索のStep 2でページ全体を読んでいるため、ページ全体を根拠として含める

`hallucination-judge.md` に `{answer}`, `{sections}` を挿入してLLMで判定する。

### スコア計算とUNCERTAIN扱い

**精度スコア**: `UNCERTAIN` が1件でも含まれると `None`（未確定）。それ以外は `PRESENT` 件数 / 総件数。  
**ハルシネーションスコア**: `PASS` → `1` / `FAIL` → `0` / `UNCERTAIN` → `None`。

`UNCERTAIN` スコアのシナリオは集計から除外し、人間レビュー対象としてマークする。承認されたFAILのみが確定FAILとなる。

---

## レポート生成（`scripts/report.py`）

**設計意図**: 3種類のレポートを用途に応じて出力する。シナリオ別レポートはFAILの原因調査用、サマリーレポートは全体品質の把握用、比較レポートは改善前後の変化確認用。

### シナリオ別レポート

各シナリオの評価結果を表形式で出力:
- 評価結果表（回答精度・ハルシネーションの自動判定・人間判定・スコア）
- 回答精度詳細（各factの判定と理由）
- 診断情報（ヒアリング状態・検索セクション）
- メトリクス（実行時間・トークン量・ツール呼び出し数）

### サマリーレポート

全シナリオを集計:
- 精度・ハルシネーション × 対象件数・確定件数・未確定・平均スコア・最低スコア・全PASS率
- パフォーマンスサマリー（実行時間・API時間・ターン数・トークン量・コスト の 平均/P50/P95/最大/合計）

`UNCERTAIN` を含むシナリオは「未確定」としてカウントし、平均・PASS率の計算から除外する。

### 比較レポート

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

## 実行手順

→ `tools/benchmark/HOW-TO-RUN.md` を参照。
