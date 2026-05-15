# ベンチマーク設計

**Status**: Draft
**Date**: 2026-05-15

## 目的

検索改善の全コンポーネント（ヒアリング・意味検索・回答生成・検証・キーワード検索）を定量評価するベンチマーク基盤。

## スコープ

### 部品ベンチマーク（フェーズA）

各コンポーネントを個別に評価する。`simulate_*.py`で部品単位のベンチマークを実行し、`evaluate.py` + `report.py`で評価・レポート生成。改善は部品ベンチマークレベルで回す。

### E2Eベンチマーク（フェーズBで追加）

スキルワークフロー（qa.md）を通しで実行する。質問インタフェースは現行検索と新検索で共通のため、ベンチマーク側は1実装で検索側の切り替えだけで現行/新を比較できる。

- 現行検索のE2Eベースライン取得
- 新検索デプロイ後のE2E取得
- 現行以上になるまで改善（部品ベンチマーク→E2Eベンチマークの順で改善）

部品ベンチマークはE2E追加後も残す。改善の流れは部品→E2Eとする（E2Eレベルだと原因特定が困難なため）。

### LLM判定ライブラリ（別Issue）

deepevalによるLLM判定は別Issueとして対応。現時点は自前の`evaluate.py`（`claude -p`でLLM判定）でベンチマークする。

## 評価軸

search-design.mdの検索要件に基づき、2軸で評価する。

| 軸 | QA | Keyword | 判定方式 | 判定基準 |
|---|:---:|:---:|---|---|
| 回答精度 | ✓ | - | LLM判定 | must factが回答に含まれるか |
| ハルシネーション | ✓ | - | LLM判定 | 知識ベースにない主張が回答に含まれないか |

キーワード検索は検索精度（mustセクションがヒットするか）をルールベースで判定する。QAの2軸とは性質が異なるため、別カテゴリとして扱う。

**keyword-searchシナリオのfactフィールド**: keyword-search.jsonの `then.must` 内の `fact` フィールドは評価に使用しない。シナリオ作成者がmustセクション選定の根拠を記録する補助情報として保持する。評価はセクションIDの一致のみで行う。

## スコアリング

| 軸 | スコア | 計算式 |
|---|---|---|
| 回答精度 | 0.0〜1.0 | must_facts_present / must_facts_total |
| ハルシネーション | 0 or 1 | 検出なし=1、検出あり=0 |
| キーワード検索精度 | 0.0〜1.0 | must_found / must_total |

**ゼロ除算**: must_total = 0 のシナリオは該当軸のスコアを N/A（評価対象外）とし、集計から除外する。

**PASS閾値**: 集計レポートの「全PASS率」におけるPASS条件:
- 回答精度: スコア = 1.0（全must fact PRESENT確定）
- ハルシネーション: スコア = 1
- キーワード検索精度: スコア = 1.0（must全件一致）

**UNCERTAIN含むシナリオの集計**: 人間レビュー未完了のシナリオ（UNCERTAINを含む）は集計から除外し、除外件数を別欄で報告する。最終集計は人間レビュー完了後にのみ確定とする。

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

LLMプロンプト（`tools/benchmark/prompts/c-claim-judge.md`に配置）:
```
あなたはファクトチェックの判定者です。以下の「事実」が「回答」に含まれているかを判定してください。

## 事実
{fact}

## 回答
{answer}

## 参照セクション（事実の出典）
{section_content}

## 判定基準
- 事実の情報が回答に含まれていれば PRESENT（言い回しが違っても同じ情報ならPRESENT）
- 事実の情報が回答に含まれていなければ ABSENT
- 判定が困難な場合は UNCERTAIN

## 出力形式
判定: PRESENT / ABSENT / UNCERTAIN
理由: （1文で）
```

**ハルシネーション判定**:

回答テキスト中のNablarch固有の主張が、知識ベースの内容で裏付けられるかをLLMで判定する。

入力:
- answer: ワークフローの回答テキスト
- sections: シナリオのmust + acceptableセクションの本文（ゴールドスタンダード）

検索で取得されたセクションではなく、シナリオ定義のゴールドスタンダードを使用する。これにより検索精度とハルシネーション判定の独立性を確保する（検索が悪い→ハルシネーション判定も悪くなる連鎖を防止）。

出力: PASS / FAIL / UNCERTAIN + 検出箇所リスト

判定基準:
- 一般的なプログラミング知識（「Javaはオブジェクト指向」等）はハルシネーションではない
- Nablarch固有のAPI名・設定名・動作仕様の主張のみ検証対象
- セクション内容に裏付けがない主張をハルシネーションとする

LLMプロンプト（`tools/benchmark/prompts/hallucination-judge.md`に配置）:
```
あなたはハルシネーション検出の判定者です。以下の「回答」にNablarchフレームワークに関する捏造情報が含まれていないか確認してください。

## 回答
{answer}

## 知識セクション（シナリオ定義のゴールドスタンダード）
{sections}

## 判定基準
- 一般的なプログラミング知識はハルシネーションではない
- Nablarch固有の主張（API名、クラス名、設定方法、動作仕様）が知識セクションに裏付けられるか確認する
- 裏付けがない主張をハルシネーションとする

## 出力形式
判定: PASS（ハルシネーションなし） / FAIL（ハルシネーション検出） / UNCERTAIN
検出箇所: （FAILまたはUNCERTAINの場合、具体的な主張を引用）
理由: （1文で）
```

### 評価エンジンの抽象化

品質評価のLLM判定部分は、自前実装からライブラリ（deepeval）へ切り替え可能な設計とする。

**インタフェース**:

```
入力:
  - answer: 回答テキスト
  - scenario: シナリオ定義（must facts, gold standard sections）

出力:
  - accuracy_score: 0.0〜1.0
  - hallucination_score: 0 or 1
  - details: 判定詳細（fact別のPRESENT/ABSENT/UNCERTAIN等）
```

**実装の切り替え**:

| 実装 | 判定方式 | 状態 |
|---|---|---|
| v1: 自前（`evaluate.py`） | `claude -p`でC-claim・ハルシネーション判定 | 現行 |
| v2: deepeval（別Issue） | deepevalライブラリのメトリクス | 後日追加 |

切り替えはevaluate.pyの判定エンジン部分のみ。シナリオ形式、レポート形式、パフォーマンスメトリクスは共通のまま変わらない。

### キーワード検索: ルールベース判定

キーワード検索スクリプトの出力からセクションIDリストを取得し、must sectionsとの一致を確認する。

- mustセクション全てが含まれていれば PASS（スコア=1.0）
- 不足するmustセクションがあれば部分点（found/total）
- acceptableセクションは参考情報として記録するが、スコアには影響しない

### 人間最終判定フロー

LLM判定は知識ベースにマッチしないものをNGにする傾向がある。このバイアスを補正するため、人間が最終判定を行う。

1. LLM自動判定の結果を一覧表示
2. **必須レビュー**: UNCERTAIN判定 → 人間がPASS/FAILに確定
3. **必須レビュー**: ABSENT判定 → 人間が確認（LLMのfalse negative排除）
4. **必須レビュー**: FAIL（ハルシネーション検出）→ 人間が確認（LLMのfalse positive排除）
5. PRESENT / PASS判定 → 人間はスキップ可能（信頼度が高い）
6. 最終結果を記録

## 診断情報

評価軸のスコアとは独立に、問題の原因切り分けに使う診断情報をランナーが記録する。スコア対象外。

| 診断情報 | 内容 | 用途 |
|---|---|---|
| ヒアリング行動 | 質問したか、何を質問したか | ヒアリング設計の改善 |
| 検索セクションID | どのセクションが検索結果に含まれたか | 検索精度の改善 |
| 回答全文 | ワークフローの最終回答テキスト | 回答生成の改善 |
| 検証結果 | qa/verify.mdの出力（存在する場合） | 検証ステップの改善 |

## メトリクス

### 品質メトリクス（評価対象）

検索要件に直結する指標。スコアリングセクションで定義した計算式・PASS閾値で評価する。

| メトリクス | 計算式 | PASS閾値 |
|---|---|---|
| 回答精度 | must_facts_present / must_facts_total | 1.0 |
| ハルシネーション | 検出なし=1、検出あり=0 | 1 |
| キーワード検索精度 | must_found / must_total | 1.0 |

### パフォーマンスメトリクス（計測対象）

品質ゲートではなく、パフォーマンス監視・比較用。`claude -p --output-format json`の出力から全て取得できる。

| メトリクス | 取得元フィールド | 説明 |
|---|---|---|
| 実行時間（総合） | `duration_ms` | プロンプト送信から結果受信まで |
| 実行時間（API） | `duration_api_ms` | API呼び出しの合計時間 |
| 入力トークン | `usage.input_tokens` | プロンプトの入力トークン数 |
| 出力トークン | `usage.output_tokens` | LLM応答の出力トークン数 |
| キャッシュ読取トークン | `usage.cache_read_input_tokens` | プロンプトキャッシュから読み取ったトークン数 |
| キャッシュ作成トークン | `usage.cache_creation_input_tokens` | プロンプトキャッシュに書き込んだトークン数 |
| コスト | `total_cost_usd` | API呼び出しの合計コスト（USD） |
| ターン数 | `num_turns` | LLMの応答ターン数 |
| イテレーション詳細 | `usage.iterations[]` | ターンごとのトークン内訳 |
| モデル別使用量 | `modelUsage` | モデルごとのトークン・コスト集計 |

部品ベンチマーク: 各`simulate_*.py`実行ごとにメトリクスを記録。コンポーネント単位の内訳が取れる。
E2Eベンチマーク: ワークフロー全体の合算メトリクスのみ（内訳は部品ベンチマークで把握）。

## モデル制約

| 用途 | モデル | 理由 |
|---|---|---|
| ワークフロー実行（ランナー） | sonnet | ユーザーが実際に使うモデルの上限がsonnet。opusで評価すると実環境と乖離する |
| 評価LLM（C-claim・ハルシネーション判定） | sonnet | 判定精度とコストのバランス |

## 実行フロー

### 部品ベンチマーク（フェーズA）

各コンポーネントを`simulate_*.py`で個別実行する。プロンプトを直接LLM呼び出しし、スキルワークフローは経由しない。

**QA部品ベンチマーク**:

| スクリプト | 対象 | 入力 | 出力 |
|---|---|---|---|
| `simulate_hearing.py` | ヒアリング分類 | シナリオのwhen.input | classification, processing_type |
| `simulate_semantic_search.py` | 意味検索 Stage1+2 | 質問 + hearing_answer | section_idリスト |
| `simulate_answer.py` | 回答生成 | 質問 + セクション本文 | 回答テキスト |
| `simulate_verify.py` | 根拠検証 | 回答 + セクション本文 | PASS/FAIL + claims |
| `simulate_answer_verify.py` | 回答+検証 | 質問 + セクション本文 | 回答 + 検証結果 |
| `run.py` | 部品チェーン | シナリオのwhen.input | hearing→search→answer結果 |

```
1. simulate_*.py でコンポーネント実行（model: sonnet）
   入力: シナリオから必要なフィールドを注入

2. 結果をファイルに保存

3. evaluate.py で評価
   a. 回答精度 → LLM判定（C-claim）
   b. ハルシネーション → LLM判定

4. report.py でレポート生成

5. 人間最終判定 → 確定スコア
```

**キーワード検索ベンチマーク**:

```
1. keyword-search.sh を実行
   入力: シナリオのwhen.input（キーワードリスト）

2. セクションIDリストを取得

3. mustセクションの一致確認 → 即時スコア

4. レポート生成
```

### E2Eベンチマーク（フェーズBで追加）

スキルワークフロー（qa.md）を`claude -p`で通し実行する。質問インタフェースは現行/新検索で共通のため、1実装で両方をベンチマークできる。

**実行方式**:

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
    cwd=skill_dir,  # .claude/skills/nabledge-6/
    timeout=180,
)
```

- `cwd`をスキルディレクトリに設定し、ワークフローと知識ファイルにアクセスできるようにする
- `--allowedTools`でワークフローが使うツールのみ許可（パーミッションプロンプト抑止）
- 部品ベンチマークでは`cwd="/tmp"`（スキルに依存しない）、E2Eでは`cwd=skill_dir`（スキルに依存する）

**プロンプト構成**:

```
以下のワークフロー（qa.md）に従って質問に回答してください。

## ワークフロー
{qa.mdの内容}

## 質問
{scenario.when.input}

## コンテキスト（ヒアリング結果）
処理方式: {scenario.when.hearing_answer.processing_type}
目的: {scenario.when.hearing_answer.goal}

## 出力要件
回答を出力した後、以下のマーカーで診断情報を出力してください。
{構造化キャプチャマーカーの指示}
```

ヒアリング結果をプロンプトに含めることで、ワークフローはヒアリングをスキップし検索から開始する。現行検索もヒアリング結果がない場合は質問文のみで検索するため、同条件で比較可能。

**実行フロー**:

```
1. claude -p でスキルワークフローを実行（model: sonnet）
   入力: シナリオのwhen.input + hearing_answer

2. JSON出力からメトリクスを取得
   duration_ms, num_turns, total_cost_usd, usage.*

3. 構造化キャプチャマーカーから診断情報をパース
   ヒアリング行動、検索セクションID、回答全文

4. evaluate.py で評価（部品と共通基盤）
   a. 回答精度 → LLM判定（C-claim）
   b. ハルシネーション → LLM判定

5. report.py でレポート生成（部品と共通基盤）

6. 人間最終判定 → 確定スコア
```

**現行 vs 新の比較**:

同じシナリオ・同じE2Eランナーで、検索側（スキルワークフロー）を切り替えるだけ。

| 実行 | cwd | ワークフロー | 目的 |
|---|---|---|---|
| ベースライン | 現行スキル | 現行qa.md | 現行の品質・パフォーマンス |
| 新検索 | 新スキル | 新qa.md | 新の品質・パフォーマンス |

レポートは`results/{run-label}/`に保存し、`run-label`で区別（例: `baseline-current`, `v1-new-search`）。比較は同じ`report.py`でrun-label間の差分を出力する。

### 構造化キャプチャ（E2Eベンチマーク用）

E2Eベンチマークでワークフローの診断情報を取得するために、ワークフローは各ステージの出力を構造化形式で返す。ワークフローは常に全マーカーを出力すること（必須）。マーカーが出力されない場合はランナーエラーとして扱い、シナリオを再実行する。

部品ベンチマークではファイル保存方式のため不要。

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

## レポート形式

### シナリオ別レポート

```markdown
## {scenario_id}: {given.description}

**入力**: {when.input}
**種別**: {部品 / E2E}
**ラベル**: {run-label}

### 品質評価

| 軸 | 自動判定 | 人間判定 | スコア |
|---|---|---|---|
| 回答精度 | 1 PRESENT, 1 UNCERTAIN | 要レビュー | - |
| ハルシネーション | PASS | - | 1 |

### 回答精度詳細
| # | fact | 判定 | 理由 |
|---|------|------|------|
| 1 | {fact1} | PRESENT | 回答に含まれている |
| 2 | {fact2} | UNCERTAIN | **要レビュー** |

### パフォーマンス
| メトリクス | 値 |
|---|---|
| 実行時間（総合） | 45,230 ms |
| 実行時間（API） | 42,100 ms |
| 入力トークン | 12,500 |
| 出力トークン | 2,500 |
| キャッシュ読取 | 10,000 |
| キャッシュ作成 | 2,500 |
| コスト | $0.045 |
| ターン数 | 5 |

### 診断情報
- ヒアリング: {skipped / asked — 質問内容}
- 検索セクション: {セクションIDリスト}
```

### 集計レポート

```markdown
# ベンチマーク結果: {run-label} ({date})

## 品質サマリー

| 軸 | 対象件数 | 確定件数 | 未確定 | 平均スコア | 最低スコア | 全PASS率 |
|---|---|---|---|---|---|---|
| 回答精度 | 15 | 13 | 2 | 0.92 | 0.50 | 12/13 |
| ハルシネーション | 15 | 14 | 1 | 0.93 | 0 | 13/14 |

※ 未確定 = 人間レビュー未完了（UNCERTAIN含む）。平均・PASS率は確定分のみで計算。

## パフォーマンスサマリー

| メトリクス | 平均 | P50 | P95 | 最大 | 合計 |
|---|---|---|---|---|---|
| 実行時間（総合） | 35s | 30s | 80s | 120s | — |
| 実行時間（API） | 32s | 28s | 75s | 110s | — |
| 入力トークン | 12,000 | 10,000 | 25,000 | 40,000 | 180,000 |
| 出力トークン | 2,500 | 2,000 | 5,000 | 8,000 | 37,500 |
| コスト | $0.04 | $0.03 | $0.08 | $0.12 | $0.60 |
| ターン数 | 4 | 3 | 8 | 12 | — |

## 人間レビュー対象
{UNCERTAIN / ABSENT / FAIL判定のリスト}
```

### 比較レポート（E2Eベンチマーク用）

2つのrun-labelの結果を比較する。品質指標の変化とパフォーマンスの変化を並べて表示。

```markdown
# ベンチマーク比較: {label-A} vs {label-B}

## 品質比較

| 軸 | {label-A} | {label-B} | 差分 |
|---|---|---|---|
| 回答精度（平均） | 0.85 | 0.92 | +0.07 |
| ハルシネーション（PASS率） | 12/15 | 14/15 | +2 |

## パフォーマンス比較

| メトリクス | {label-A} 平均 | {label-B} 平均 | 変化率 |
|---|---|---|---|
| 実行時間（総合） | 42s | 35s | -17% |
| コスト | $0.05 | $0.04 | -20% |
| ターン数 | 6 | 4 | -33% |

## シナリオ別差分
{品質スコアが変化したシナリオの一覧}
```

## CLI呼び出しパターン

ベンチマーク・シミュレーションのLLM呼び出しは `claude -p` を使用する。

```python
subprocess.run(
    [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--no-session-persistence",
        full_prompt,  # json_schemaはプロンプト末尾に追記
    ],
    capture_output=True,
    text=True,
    cwd="/tmp",
    timeout=120,
)
```

**必須ルール:**
- `cwd="/tmp"` を指定する。プロジェクトディレクトリから実行すると、Claude Codeのセッション管理と干渉して認証エラーになる
- `--bare` は使わない。`--bare` はOAuth/keychainを無効化し、`ANTHROPIC_API_KEY` 環境変数のみで認証する。CI以外では使えない
- `--json-schema` は使わない。非bareモードでは正しく動作しない（resultが空になる）。JSON Schemaはプロンプト末尾に出力形式指示として追記する
- レスポンスがmarkdownコードフェンスで囲まれる場合があるため、`extract_json_from_result()` でストリップしてからパースする

## ディレクトリ構成

```
tools/benchmark/
  components/
    prompts/
      hearing-classify.md          ← ヒアリング分類プロンプト
      hearing-extract.md           ← ヒアリング抽出プロンプト
      semantic-search-stage1.md    ← 意味検索Stage1プロンプト
      semantic-search-stage2.md    ← 意味検索Stage2プロンプト
      answer.md                    ← 回答生成プロンプト（トレース付）
      answer-generation.md         ← 回答生成プロンプト（run.py用）
      verify.md                    ← 根拠検証プロンプト
    scripts/
      keyword-search.sh           ← キーワード検索スクリプト
      read-sections.sh            ← セクション本文取得
  prompts/
    c-claim-judge.md               ← 回答精度LLM判定プロンプト
    hallucination-judge.md         ← ハルシネーション判定プロンプト
  scenarios/
    qa.json                        ← QAシナリオ定義（15件）
    keyword-search.json            ← キーワード検索シナリオ定義（12件）
  scripts/
    simulate_hearing.py            ← ヒアリング部品ベンチマーク
    simulate_semantic_search.py    ← 意味検索部品ベンチマーク
    simulate_answer.py             ← 回答生成部品ベンチマーク
    simulate_verify.py             ← 検証部品ベンチマーク
    simulate_answer_verify.py      ← 回答+検証部品ベンチマーク
    run.py                         ← 部品チェーン実行（hearing→search→answer）
    run_e2e.py                     ← E2Eベンチマーク実行（フェーズBで追加）
    evaluate.py                    ← 評価（ルールベース + LLM判定）
    report.py                      ← レポート生成（比較レポート含む）
    generate_index.py              ← index.md生成（ベンチマーク用）
  results/
    {run-label}/                   ← 実行結果（gitコミットして比較可能にする）
      {scenario-id}/
        hearing.json               ← 診断: ヒアリング結果
        search.json                ← 診断: 検索結果（セクションIDリスト）
        answer.md                  ← 診断: 回答テキスト
        metrics.json               ← パフォーマンスメトリクス
        evaluation.json            ← 自動判定結果
        final.json                 ← 人間確定後の最終結果
      report.md                    ← 集計レポート
```

### metrics.jsonスキーマ

`claude -p --output-format json`の出力から取得した全メトリクスを保存する。

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
