# Notes

## 2026-05-28

### T1: DeepEvalジャッジLLM接続方式確認

#### 調査結果

**1. DeepEvalのインストール**
- `uv pip install deepeval` 成功。`aiobotocore` も追加で必要（`uv pip install aiobotocore`）。
- `import deepeval` OK。

**2. ジャッジLLM接続方式**

採用: **案A（DeepEval組み込みの`AmazonBedrockModel`を使用）**

根拠:
- DeepEvalには`deepeval.models.AmazonBedrockModel`が組み込みで存在する。
- `AmazonBedrockModel(model='jp.anthropic.claude-sonnet-4-6', region='ap-northeast-1')` でインスタンス生成OK。
- 環境に`AWS_CA_BUNDLE=/usr/local/share/ca-certificates/ca.crt`が設定済みのため、SSLエラーを回避できる。
- 実際に`a_generate('Say hello in one word.')`が成功することを確認。
- `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_REGION`は環境変数として設定済み。

却下した案:
- 案B（claude CLIサブプロセスラップ）: DeepEvalの非同期呼び出し構造に合わせるのが複雑になる上、案Aで既に動作するため不要。
- 案C（自前実装）: DeepEvalの品質保証済みプロンプトを使えないため不要。

**3. 利用指標**

`AnswerCorrectnessMetric`/`AnswerSimilarityMetric`はDeepEval最新版に存在しない。
代わりに以下3指標を使用:
- `GEval`（Answer Correctness用: カスタム基準でfactの網羅性を評価）
- `AnswerRelevancyMetric`（Relevancy: 入力に対する回答の関連性）
- `FaithfulnessMetric`（Faithfulness: retrieval contextに対するハルシネーション検出）

## 2026-05-29

### T19: baseline-deepeval 3 run 結果

全30シナリオ × 3 run 完了（一部シナリオは偶発的エラーで再実行して回収）。

| run | answer_correctness | answer_relevancy | faithfulness | 閾値通過 |
|-----|-------------------|-----------------|--------------|---------|
| run-1 | 0.96 | 0.97 | 0.97 | 30/30 全指標 |
| run-2 | 0.99 | 0.96 | 0.97 | 30/30 全指標 |
| run-3 | 0.97 | 0.96 | 0.98 | 30/30 全指標 |

全指標で閾値（≥0.5）通過率100%、スコアも安定（0.96〜0.99）。
これを新ベースライン（`baseline-deepeval/`）として確定する。

→ 既存ベンチマークとの対応:
- `accuracy`（既存）↔ `GEval`（Answer Correctness）
- `hallucination`（既存）↔ `FaithfulnessMetric`

**4. LLMTestCaseへのマッピング**

既存データから`LLMTestCase`へのマッピング:
- `input` ← `scenario["when"]["input"]`（シナリオの質問）
- `actual_output` ← `answer.md`の内容
- `expected_output` ← `must.facts`を改行結合（Answer Correctness/GEval用）
- `retrieval_context` ← `diagnostics.search_sections`（section refリスト）の各セクション内容

**注意**: evaluation.jsonに`workflow_details.step3.selected_pages`は存在しない。
実際のretrieval contextは`diagnostics.search_sections`（section_id形式: `path/to/file.json:sN`）。
既存の`load_section_content()`関数でコンテンツを取得できる。

**5. T2以降のタスク修正が必要な点**

T4（evaluate.py）:
- `retrieval_context` の取得元は `diagnostics.search_sections` を使う（`workflow_details.step3.selected_pages`ではない）
- 3指標は `GEval`（answer_correctness）、`AnswerRelevancyMetric`（answer_relevancy）、`FaithfulnessMetric`（faithfulness）
- モデル設定: `AmazonBedrockModel(model=os.environ.get('BEDROCK_MODEL_ID', 'jp.anthropic.claude-sonnet-4-6'), region=os.environ.get('AWS_REGION', 'ap-northeast-1'))`

T2（requirements.txt）:
- `deepeval` と `aiobotocore` の両方を追加
