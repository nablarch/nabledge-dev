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

## ステップ 4: 比較集計（3 run完了後）

**目的**: 3 runの数値を集計し、前回ラベルと比較する。

### 4a. 3 run集計

```bash
for r in run-1 run-2 run-3; do
  python3 -m tools.benchmark.scripts.report \
    --run-dir tools/benchmark/results/{run-label}/$r
done
```

| 軸 | run-1 | run-2 | run-3 | 平均 |
|---|---|---|---|---|
| answer_correctness 平均 | N.NN | N.NN | N.NN | N.NN |
| answer_relevancy 平均 | N.NN | N.NN | N.NN | N.NN |
| faithfulness 平均 | N.NN | N.NN | N.NN | N.NN |

閾値割れシナリオ一覧（3 run中で1回以上閾値未達となったシナリオ）:

| シナリオID | 発生回数/3 | 低下した指標 |
|---|---|---|

### 4b. 前回ラベルとの比較

```bash
python3 -m tools.benchmark.scripts.report \
  --run-dir tools/benchmark/results/{run-label}/run-1 \
  --compare tools/benchmark/results/{prev-label}/run-1
```

| 軸 | 前回 平均 | 今回 平均 | 差分 |
|---|---|---|---|
| answer_correctness | N.NN | N.NN | ±N.NN |
| answer_relevancy | N.NN | N.NN | ±N.NN |
| faithfulness | N.NN | N.NN | ±N.NN |

保存先: `tools/benchmark/results/{run-label}/report.md`

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
