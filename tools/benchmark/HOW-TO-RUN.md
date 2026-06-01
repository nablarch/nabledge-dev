# E2Eベンチマーク実行手順

評価軸・スコアリング・ファイルフォーマットの定義は `docs/benchmark-design.md` を参照。

## 前提

- スキルディレクトリ: `.claude/skills/nabledge-6`
- シナリオファイル: `tools/benchmark/scenarios/qa.json`
- DeepEval がインストール済みであること:
  ```bash
  pip install -r tools/benchmark/requirements.txt
  ```

---

## ステップ 1: 1シナリオで動作確認

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids pre-01
```

受入条件:
- 終了コード 0
- `tools/benchmark/results/YYYYMMDD-HHMMSS/pre-01/` に `workflow_details.json` / `answer.md` / `metrics.json` / `trace.json` / `evaluation.json` が揃う
- `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` が含まれる
- `pre-01/metrics.json` の `model_usage` が空でない
- `pre-01/evaluation.json` の `scores` に `answer_correctness`, `answer_relevancy`, `faithfulness` が含まれる

確認後、動作確認用ディレクトリを削除する:
```bash
rm -rf tools/benchmark/results/YYYYMMDD-HHMMSS
```

---

## ステップ 2: 全シナリオ実行（1 run）

```bash
python3 -m tools.benchmark.scripts.run_qa \
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

### タイムアウトシナリオの再実行

タイムアウト（360s）や一時的なエラーで失敗したシナリオは、単体再実行して結果を上書きする。

```bash
# エラー一覧を確認
python3 -c "
import json
d = json.load(open('tools/benchmark/results/{run-label}/run-N/summary.json'))
for s in d['scenarios']:
    if s.get('status') == 'error':
        print(s['id'], '-', s.get('error', '')[:60])
"

# 失敗シナリオを単体再実行（例: qa-11a, oos-qa-01）
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids qa-11a,oos-qa-01
```

完了後、再実行結果をrun-Nディレクトリへ上書きコピー:
```bash
RUNDIR=tools/benchmark/results/{run-label}/run-N
NEWDIR=tools/benchmark/results/YYYYMMDD-HHMMSS
for sid in qa-11a oos-qa-01; do
  rm -rf $RUNDIR/$sid
  cp -r $NEWDIR/$sid $RUNDIR/$sid
done
rm -rf $NEWDIR
```

summary.jsonの`scenarios`エントリも更新する（エラーエントリを正常エントリで置き換え）:
```bash
python3 -c "
import json, pathlib
p = pathlib.Path('$RUNDIR/summary.json')
d = json.loads(p.read_text())
# remove error entries for retried scenarios
retry_ids = {'qa-11a', 'oos-qa-01'}
d['scenarios'] = [s for s in d['scenarios'] if s['id'] not in retry_ids]
# append new entries from new summary
new_d = json.loads(pathlib.Path('$NEWDIR/summary.json').read_text())
d['scenarios'] += [s for s in new_d['scenarios'] if s['id'] in retry_ids]
d['total_scenarios'] = len(d['scenarios'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
print('updated summary.json:', d['total_scenarios'], 'scenarios')
"
```

---

## 出力ファイル早見表

各シナリオの出力ファイルと用途:

| ファイル | 存在条件 | 用途 |
|---|---|---|
| `error.json` | エラー時のみ | エラー内容（`error`, `exception_type`） |
| `workflow_details.json` | 正常完了時 | WF全体の詳細。step3: ページ/セクション選択理由、step4: 実際に読んだセクション、step8: 回答に使ったセクション |
| `answer.md` | 正常完了時 | 最終回答テキスト |
| `evaluation.json` | 正常完了時 | DeepEval 3指標のスコアと判定根拠（answer_correctness / answer_relevancy / faithfulness） |
| `metrics.json` | 正常完了時 | 実行時間・ターン数・コスト |
| `trace.json` | 正常完了時 | claudeの生JSON出力（`result`フィールドにLLM出力全文） |

**エラー時の調査**: `error.json` の `exception_type` でエラー種別確認。TimeoutExpiredの場合は単体再実行で回収する。

---

## ステップ 3: スコア確認

**目的**: 閾値割れシナリオを一覧し、調査対象を特定する。

### 3a. レポート生成

```bash
python3 -m tools.benchmark.scripts.report \
  --run-dir tools/benchmark/results/{run-label}/run-N
```

出力: `tools/benchmark/results/{run-label}/run-N/report.md`

レポートには以下が含まれる:
- DeepEval 3指標のスコア一覧（閾値未達を閾値割れとして表示: answer_correctness/faithfulness ≥0.99、answer_relevancy ≥0.95）
- 各シナリオの判定根拠（reason）
- パフォーマンスサマリー

### 3b. 閾値割れシナリオの確認

閾値割れ（answer_correctness/faithfulness < 0.99、answer_relevancy < 0.95）が出たシナリオについて、`workflow_details.json` と `answer.md` を読み、原因を確認する:

- **answer_correctness が低い**: must.facts のどの事実が回答に含まれていないか → `evaluation.json["scores"]["answer_correctness"]["reason"]` を確認
- **answer_relevancy が低い**: 回答が質問から外れていないか → 検索セクションの選択が適切かを確認
- **faithfulness が低い**: 根拠なき主張が含まれているか → `evaluation.json["scores"]["faithfulness"]["reason"]` を確認

次のrunへ進む（3 run完了まで繰り返す）。

---

## ステップ 4: ベースライン確立（新ラベル初回 or 意図的なリセット時）

**目的**: 3 run の結果から機械可読な baseline.json を生成し、次回退行検出の基準を確立する。

### 4a. 各 run のレポート生成

```bash
for r in run-1 run-2 run-3; do
  python3 -m tools.benchmark.scripts.report \
    --run-dir tools/benchmark/results/{run-label}/$r/run
done
```

### 4b. baseline.json 生成

```bash
python3 -m tools.benchmark.scripts.report \
  --baseline-runs \
    tools/benchmark/results/{run-label}/run-1/run \
    tools/benchmark/results/{run-label}/run-2/run \
    tools/benchmark/results/{run-label}/run-3/run \
  --save-baseline tools/benchmark/results/{run-label}/baseline.json
```

出力: `tools/benchmark/results/{run-label}/baseline.json`

baseline.json には以下が含まれる:
- シナリオ×指標ごとの `mean`, `stddev`, `pass_rate`
- `pass_rate < 1.0` のシナリオに `flaky: true` フラグ
- グローバル平均・stddev
- 閾値設定

### 4c. 集計レポート作成

保存先: `tools/benchmark/results/{run-label}/report.md`

以下のテンプレートに従って記述する。実装を知らない読者が判断できる粒度で書くこと。

---

**テンプレート:**

```markdown
# ベンチマーク集計レポート: {run-label}

| 項目 | 値 |
|---|---|
| 実行日 | YYYY-MM-DD |
| スキル | nabledge-6 |
| シナリオ数 | N |

シナリオの内訳:

| カテゴリ | 件数 | 内容 |
|---|---|---|
| 質問回答 | x | 使い方・実装方法を問う標準シナリオ |
| 影響調査 | x | 設計変更がどこに影響するかを問うシナリオ |
| コードレビュー | x | 既存コードの問題点を指摘するシナリオ |
| 入門 | x | 基本的な使い方を確認する入門向けシナリオ |
| 対応範囲外 | x | Nablarchが非対応の機能への質問（スキルが正しく「対応範囲外」と断れるかを確認） |

---

## Q1. ベンチマークは想定通りに動作したか？

YES / NO（+ 1〜2文で根拠）

例: YES。30シナリオ全件が正常完了し、3 run分のスコアが取得できた。
例: NO。run-2 で qa-11a がタイムアウト（360s）。単体再実行で回収済み。

---

## Q2. スキルの検索・回答品質は良かったか？

### 3 run スコアサマリー

| 指標 | 意味 | 閾値 | run-1 | run-2 | run-3 | 平均 | 判定 |
|---|---|---|---|---|---|---|---|
| 回答正確性 | 聞かれた事実を正しく答えられたか | ≥0.99 | N.NN | N.NN | N.NN | N.NN | ○/△/× |
| 回答関連性 | 質問に対して的外れな回答をしていないか | ≥0.95 | N.NN | N.NN | N.NN | N.NN | ○/△/× |
| 忠実性     | ナレッジにない情報を作り話していないか | ≥0.99 | N.NN | N.NN | N.NN | N.NN | ○/△/× |

判定基準: 平均 ≥ 閾値 → ○、閾値 −0.05 以内 → △、閾値 −0.05 未満 → ×

### 全体評価（1〜2文）

良い点・悪い点を非技術者が理解できる言葉で述べる。
閾値は指標ごとに異なるため「閾値に届いていない」とまとめず、指標ごとに判定を述べること。
閾値割れの原因がスキルではなく評価基準にある場合は、その旨を明示すること（スキルの問題と評価基準の問題を混同しない）。

---

## Q3. 悪かった項目の根本原因と改善案

閾値割れが2回以上発生したシナリオのみ記載する（1回のみ＝偶発的なブレとして除外）。

### サマリー

原因分類ごとの件数と対応方針を示す。

| 原因分類 | 件数 | 意味 | 対応方針 |
|---|---|---|---|
| 評価基準の問題 | x | スキルの回答は正しいが、ベンチの期待値の書き方がズレている | 期待値を修正して再ベースライン取得 |
| スキルの挙動問題 | x | 検索ミス・回答の焦点ズレなど、スキル側に原因がある | スキル改善 |
| 評価器の揺らぎ | x | DeepEval の LLM 判定がブレており、スキルの実力とは無関係 | 対処不要（ベースラインの stddev で吸収） |

### 詳細

| シナリオID | 質問（要約） | 低下した指標 | 発生回数/3 | 原因分類 | 根本原因と改善案 |
|---|---|---|---|---|---|
| xxx | ... | 回答正確性 / 回答関連性 / 忠実性 | N/3 | 評価基準の問題 / スキルの挙動問題 / 評価器の揺らぎ | ... |

---

## Q4. このベースラインは退行検出に使えるか？

YES / NO（+ 根拠）

使えない場合は、何を修正してから再取得すべきかを書く。

参考指標:
- 全30シナリオ中、安定シナリオ（3 run全て閾値通過）が何件あるか → 多いほど検出精度が高い
- 評価基準の問題があるシナリオは修正してから再取得を推奨

---

## 次のアクション

| 優先度 | 内容 | 担当 |
|---|---|---|
| 高 | ... | |
| 中 | ... | |
```

---

記述の注意事項:
- Q2 の指標名には必ず「意味（非技術者向け）」を添える
- Q3 は「2回以上発生」のみ記載し、1回のみのブレは除外する
- Q4 は YES/NO で始め、理由を事実ベースで書く（「思われる」「可能性がある」は使わない）

---

## ステップ 4b（退行チェック）: スキル改修後の比較

**目的**: スキルを変更した後、既存ベースラインと比較して退行を自動検出する。

### 退行チェック実行

```bash
python3 -m tools.benchmark.scripts.report \
  --run-dir tools/benchmark/results/{new-label}/run-N/run \
  --compare-baseline tools/benchmark/results/{baseline-label}/baseline.json
```

出力: `tools/benchmark/results/{new-label}/run-N/run/regression-check.md`

判定ルール:
- シナリオのスコアが `baseline_mean - 2σ` を下回った場合 → `REGRESSION DETECTED`（exit code 1）
- `flaky: true` のシナリオで退行が出た場合 → `CLEAN` 扱い（flaky_regressions に記録）
- ベースラインにない新規シナリオ → スキップ（new_scenarios に記録）

3 run分を比較して全て CLEAN であれば退行なしと判断する。REGRESSION DETECTED が出た場合はシナリオ・指標・delta を確認して原因を調査する。

---

## ステップ 5: 閾値割れシナリオの改善判断

**目的**: 閾値割れシナリオについて原因を調査し、改善対象かどうかを判断する。

### 5a. 各閾値割れシナリオの調査

`workflow_details.json` / `answer.md` / `evaluation.json` を読み、以下を確認する:

1. **再現性**: 3 run中何回発生したか（1回 → 揺らぎ候補、2〜3回 → 要調査）
2. **原因の特定**: 以下の分類で判定する
   - **評価基準の問題**: must.facts の記述が不正確・過剰であり、正しい回答を誤判定している
   - **ナレッジ未収録**: スキルが参照すべき情報がナレッジに含まれていない
   - **スキルの挙動問題**: 検索ミス・回答生成ミスなど、スキル側に原因がある
3. **改善可能性**: 原因に対して現実的な対処があるか

### 5b. 改善判断

各閾値割れシナリオについて判断する:

| シナリオID | 低下指標 | 再現性 | 原因分類 | 対応 |
|---|---|---|---|---|
| qa-12a | faithfulness | 3/3 | ナレッジ未収録 | 要改善: ナレッジ追加 |
| impact-03 | answer_relevancy | 1/3 | 揺らぎ | 対処不要 |

---

## ステップ 6: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/
git commit -m "chore: save {run-label} E2E benchmark results ({N} runs)"
git push
```
