# E2Eベンチマーク実行手順

評価軸・スコアリング・ファイルフォーマットの定義は `.work/00343/design/benchmark-design.md` を参照。

## 前提

- スキルディレクトリ: `.claude/skills/nabledge-6`
- シナリオファイル: `tools/benchmark/scenarios/qa.json`

---

## ステップ 1: 1シナリオで動作確認

```bash
python3 -m tools.benchmark.scripts.run_e2e \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids pre-01
```

受入条件:
- 終了コード 0
- `tools/benchmark/results/YYYYMMDD-HHMMSS/pre-01/` に `workflow_details.json` / `answer.md` / `metrics.json` / `trace.json` / `evaluation.json` が揃う
- `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` が含まれる
- `pre-01/metrics.json` の `model_usage` が空でない

確認後、動作確認用ディレクトリを削除する:
```bash
rm -rf tools/benchmark/results/YYYYMMDD-HHMMSS
```

---

## ステップ 2: 全シナリオ実行（1 run）

```bash
python3 -m tools.benchmark.scripts.run_e2e \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6
```

完了後、出力ディレクトリをリネーム:
```bash
mkdir -p tools/benchmark/results/{run-label}
mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/{run-label}/run-N
```

`run-label` の例: `v1-new-search`（新スキル第1版）、`v2-new-search`（改善後）

受入条件:
- 終了コード 0
- `summary.json` の `total_scenarios` が期待値と一致

---

## ステップ 3: 1 runレポート作成

runの完了を待たず、完了したシナリオから順にレポートを作成してユーザーに確認を求める。

### 出力ファイル早見表

各シナリオの出力ファイルと用途:

| ファイル | 存在条件 | 用途 |
|---|---|---|
| `error.json` | エラー時のみ | エラー内容（`error`, `exception_type`） |
| `evaluation.json` | 正常完了時 | 自動スコア（claim_verdicts, hallucination）、選択ページ/セクション（diagnostics） |
| `workflow_details.json` | 正常完了時 | ステップ別WF詳細（step3: ページ/セクション選択理由、step4: 実際に読んだセクション、step8: 回答に使ったセクション） |
| `answer.md` | 正常完了時 | 最終回答テキスト |
| `trace.json` | 正常完了時 | claudeの生JSON出力（`result`フィールドにLLM出力全文） |
| `metrics.json` | 正常完了時 | 実行時間・ターン数・コスト |

**エラー時の調査**: `error.json` の `exception_type` でエラー種別確認。TimeoutExpiredの場合は単体再実行で回収する。

**正常完了後の調査**:
- スコア確認: `evaluation.json`（claim_verdicts / hallucination）
- 選択セクション確認: `evaluation.json["diagnostics"]["selected_sections"]` または `workflow_details.json["step3"]["selected_sections"]`
- 実際に読んだセクション: `workflow_details.json["step4"]["read_sections"]`
- 回答根拠セクション: `workflow_details.json["step8"]["answer_sections"]`
- LLMの行動全体: `trace.json["result"]`（中間思考・ツール呼び出し含む全文）

### 3a. 数値サマリー生成

以下の数値を集計する:

```
## 品質サマリー

| 軸 | PASS | FAIL | UNCERTAIN | PASS率 |
|---|---|---|---|---|
| 回答精度（must） | N | N | N | N% |
| ハルシネーション | N | N | N | N% |

## パフォーマンスサマリー

| メトリクス | 中央値 | 最大 | 合計コスト |
|---|---|---|---|
| 実行時間（総合） | Ns | Ns | - |
| ターン数 | N | N | - |
| コスト | - | - | $N |
```

### 3b. シナリオ別詳細表

全シナリオを以下の形式でリストアップする:

```
| シナリオID | 精度 | 幻覚 | sections | turns | 備考 |
|---|---|---|---|---|---|
| pre-01    | 2/2 PASS | PASS | 4 | 5 | |
| qa-02     | 0/2 FAIL | PASS | 2 | 14 | |
```

- `sections`: `workflow_details.json["step4"]["read_sections"]` の件数
- `turns`: `metrics.json["num_turns"]`

### 3c. 幻覚の裏取り（hallucination FAIL/UNCERTAIN シナリオのみ）

幻覚FAIL/UNCERTAIN判定されたclaimについて以下を確認する:

1. **知識ファイルに本当にないか**: `evaluation.json["hallucination"]["claims"]` で `supported: false` のclaimを特定し、`workflow_details.json["step4"]["read_sections"]` に記載のセクションIDの知識ファイルを読み、そのclaimの内容が実際に記載されていないことを確認する
2. **LLMがなぜ追加したか**: `trace.json["result"]` フィールド（LLMの出力全文）を読み、そのclaimが回答のどの文脈で出現したかを確認する。「Step6 verifyで一度検出したがStep7リトライ後も残ったか」「そもそも生成時から含まれていたか」を判断する

確認結果を3dの定性評価に含める。

### 3d. QAエキスパートによる定性評価（全シナリオ）

**目的**: 数値スコアでは見えない「LLMがどう考え・どう行動したか」を確認する。想定外の挙動・ハルシネーションの性質・検索の的外れを発見する。

**参照ファイル（シナリオごと）**:
- `workflow_details.json` — ステップ別WF詳細（選択ページ/セクション理由、実際に読んだセクション、回答根拠セクション）
- `answer.md` — 最終回答
- `evaluation.json` — 自動スコア（PASS/FAIL/UNCERTAIN）、選択セクション
- `trace.json` — LLMの行動全体（`result`フィールドに中間思考・ツール呼び出し含む全文）

QAエキスパート（別エージェント）に以下を渡して評価させる:

```
あなたはQAエンジニアです。Nablarchスキルのベンチマーク実行結果を定性評価してください。

## 評価観点
各シナリオについて workflow_details.json・answer.md・evaluation.json・trace.json を読み、
以下の観点でコメントしてください:

1. **行動の妥当性**: 検索クエリは適切か、何ターンで完了したか、無駄な行動はなかったか
2. **検索結果の質**: 選ばれたセクションIDはシナリオの質問に合っているか、関係ないセクションが混入していないか
3. **回答の質**: 質問への回答として的を射ているか、Nablarch固有の情報が正確か
4. **想定外の挙動**: スコアに関わらず、気になる動き・判断・回答があれば記録する
5. **FAILシナリオの原因分析**: なぜFAILしたか（検索ミス・回答生成ミス・評価基準の問題）

## 評価シナリオ一覧
{全シナリオのworkflow_details.json + answer.md + evaluation.json + trace.json}

## 出力形式

### 全体所見
（全シナリオを通じて気づいたパターン・傾向・懸念）

### シナリオ別コメント
| シナリオID | スコア | 定性コメント | 想定外/懸念 |
|---|---|---|---|
| pre-01 | 精度2/2 幻覚PASS | （コメント） | なし |
| qa-02  | 精度0/2 幻覚PASS | （コメント） | （あれば） |

### 要対応項目
（スコアに関わらず、次のイテレーションで対処すべき事項）
```

### 3e. レポートファイル保存

```bash
# 1 runレポートを保存
tools/benchmark/results/{run-label}/run-N/report.md
```

### 3f. ユーザー確認

レポートをプッシュしてユーザーに提示する。ユーザーの承認後に次 runへ進む。

---

## ステップ 4: 3 run完了後の集計レポート

3 run全て完了後に集計レポートを作成する。

### 4a. 3 run確認

```bash
for r in 1 2 3; do
  echo "run-$r: $(ls tools/benchmark/results/{run-label}/run-$r/ | wc -l) entries"
  cat tools/benchmark/results/{run-label}/run-$r/summary.json | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print('  total_scenarios:', d['total_scenarios'])"
done
```

### 4b. 集計レポート生成

外れ値除外（IQR×1.5ルール）後の平均・中央値・SDを計算する。

```
# ベンチマーク結果: {run-label} ({date})

## 品質サマリー（3 run集計）

| 軸 | 対象件数 | 確定件数 | 未確定 | 平均±SD | 中央値 | 最低 | 全PASS率 |
|---|---|---|---|---|---|---|---|
| 回答精度 | N | N | N | N ± N | N | N | N/N |
| ハルシネーション | N | N | N | N ± N | N | N | N/N |

## パフォーマンスサマリー（3 run集計、外れ値除外後）

| メトリクス | 平均±SD | 中央値 | P95 | 最大 | 外れ値除外件数 |
|---|---|---|---|---|---|
| 実行時間（総合） | Ns ± Ns | Ns | Ns | Ns | N |
| ターン数 | N ± N | N | N | N | N |
| コスト/シナリオ | $N ± $N | $N | $N | $N | N |

## シナリオ別詳細（3 run平均）

| シナリオID | 精度（平均） | 幻覚（平均） | 検索件数（中央値） | ターン数（中央値） |
|---|---|---|---|---|

## 人間レビュー対象

（UNCERTAIN / ABSENT / FAIL判定が1 run以上あったシナリオ一覧）
| シナリオID | 判定 | 対象ファイル |
|---|---|---|

## 定性評価総括

（3 runを通じた傾向・懸念・改善ポイント）
```

保存先: `tools/benchmark/results/{run-label}/report.md`

---

## ステップ 5: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/
git commit -m "feat: add {run-label} E2E benchmark results ({N} runs)"
git push
```

---

## 比較レポート（baseline-current vs 新スキル）

```
# ベンチマーク比較: {label-A} vs {label-B}

## 品質比較
| 軸 | {label-A} 平均±SD | {label-B} 平均±SD | 差分 | 判定 |
|---|---|---|---|---|

## パフォーマンス比較
| メトリクス | {label-A} | {label-B} | 変化率 |
|---|---|---|---|

## シナリオ別差分
（いずれかのSDを超える変化があったシナリオ）
```

差分がいずれかのSDを超える場合は「有意差あり」、そうでなければ「誤差範囲内」。
