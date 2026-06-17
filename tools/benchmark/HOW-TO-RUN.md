# E2Eベンチマーク実行手順

評価軸・スコアリング・ファイルフォーマットの定義は `docs/benchmark-design.md` を参照。

この手順は **フェーズ > ステップ > アクション** の3層で構成される。
上から順に実行すること。各ステップは「実行 → レポート生成 → コミット」で閉じる。
情報がそろった時点でレポートを生成し、その都度コミット・プッシュする（最後にまとめて、ではない）。

## 前提

- スキルディレクトリ: `.claude/skills/nabledge-6`
- シナリオファイル: `tools/benchmark/scenarios/qa.json`
- DeepEval がインストール済みであること:
  ```bash
  pip install -r tools/benchmark/requirements.txt
  ```
- `{run-label}` は **`YYYYMMDD-HHMM-{識別}`** 形式（日時+識別）にする。日時は本ベンチ run-1 の実行時刻（`summary.json` の `executed_at`）を用いる。時刻HHMM を含めるのは、同日複数回取得を区別するため。識別は内容が分かる短い語（例: `baseline-current`, `fullbench-classes-v6`）。例: `20260616-1214-fullbench-classes-v6`。別ベンチは必ず別ラベルにする。

---

# フェーズ A: 動作確認

## ステップ A-1: 1シナリオで動作確認

### アクション A-1-1: 実行

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids pre-01
```

### アクション A-1-2: 受入確認

- 終了コード 0
- `tools/benchmark/results/YYYYMMDD-HHMMSS/pre-01/` に `workflow_details.json` / `answer.md` / `metrics.json` / `trace.json` / `evaluation.json` が揃う
- `summary.json` に `skill_dir`, `scenarios_file`, `executed_at` が含まれる
- `pre-01/metrics.json` の `model_usage` が空でない
- `pre-01/evaluation.json` の `scores` に `answer_correctness`, `answer_relevancy`, `faithfulness` が含まれる

### アクション A-1-3: 後始末

動作確認用ディレクトリは保存しない。削除する:
```bash
rm -rf tools/benchmark/results/YYYYMMDD-HHMMSS
```

---

# フェーズ B: 本実行（1 run ずつ、3 run 繰り返す）

このフェーズを **run-1, run-2, run-3 と 3 回繰り返す**。各 run でステップ B-1 〜 B-4 を完結させる。

## ステップ B-1: 全シナリオ実行

### アクション B-1-1: 実行

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6
```

### アクション B-1-2: リネーム（run-N は今回の回数に置換）

```bash
mkdir -p tools/benchmark/results/{run-label}
mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/{run-label}/run-N
```

### アクション B-1-3: 受入確認

- 終了コード 0
- `summary.json` の `total_scenarios` が期待値と一致

## ステップ B-2: タイムアウト・エラーの回収

### アクション B-2-1: エラー一覧確認

```bash
python3 -c "
import json
d = json.load(open('tools/benchmark/results/{run-label}/run-N/summary.json'))
for s in d['scenarios']:
    if s.get('status') == 'error':
        print(s['id'], '-', s.get('error', '')[:60])
"
```
エラーが無ければこのステップはスキップ。

### アクション B-2-2: 失敗シナリオを単体再実行（例: qa-11, oos-qa-01）

```bash
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids qa-11,oos-qa-01
```

### アクション B-2-3: 再実行結果を run-N へ上書き

```bash
RUNDIR=tools/benchmark/results/{run-label}/run-N
NEWDIR=tools/benchmark/results/YYYYMMDD-HHMMSS
for sid in qa-11 oos-qa-01; do
  rm -rf $RUNDIR/$sid
  cp -r $NEWDIR/$sid $RUNDIR/$sid
done
```

### アクション B-2-4: summary.json のエラーエントリを正常エントリで置換

```bash
python3 -c "
import json, pathlib
p = pathlib.Path('$RUNDIR/summary.json')
d = json.loads(p.read_text())
retry_ids = {'qa-11', 'oos-qa-01'}
d['scenarios'] = [s for s in d['scenarios'] if s['id'] not in retry_ids]
new_d = json.loads(pathlib.Path('$NEWDIR/summary.json').read_text())
d['scenarios'] += [s for s in new_d['scenarios'] if s['id'] in retry_ids]
d['total_scenarios'] = len(d['scenarios'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=2))
print('updated summary.json:', d['total_scenarios'], 'scenarios')
"
rm -rf $NEWDIR
```

## ステップ B-3: run別レポート生成

### アクション B-3-1: レポート生成

```bash
python3 -m tools.benchmark.scripts.report \
  --run-dir tools/benchmark/results/{run-label}/run-N
```
出力: `tools/benchmark/results/{run-label}/run-N/report.md`

レポートには次が含まれる:
- DeepEval 3指標のスコア一覧（閾値: answer_correctness/faithfulness ≥0.99、answer_relevancy ≥0.95）
- 各シナリオの判定根拠（reason）
- パフォーマンスサマリー（cost/time の平均・p50・p95・最大）

> cost/time は平均でなく **p50・最大** を見ること（平均はばらつきを隠す）。

## ステップ B-4: この run をコミット

### アクション B-4-1: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/run-N
git commit -m "chore: save {run-label} run-N (benchmark + report)"
git push
```

**ここまでを run-1, run-2, run-3 で繰り返す。3 run 完了したらフェーズ C へ。**

---

# フェーズ C: 3 run 集約

3 run がそろった時点で、横断的な集約と人間向けの分析を行う。

## ステップ C-1: 3run横断集約レポート

### アクション C-1-1: 生成

```bash
python3 -m tools.benchmark.scripts.report \
  --crossrun-dir tools/benchmark/results/{run-label}
```
出力: `tools/benchmark/results/{run-label}/crossrun-summary.md`
（3run横断のスコア集約＋cost/time分布 P50/P95/最大）

### アクション C-1-2: コミット

```bash
git add tools/benchmark/results/{run-label}/crossrun-summary.md
git commit -m "chore: add {run-label} crossrun summary"
git push
```

## ステップ C-2: 閾値割れシナリオの裏付け調査

閾値割れが出たシナリオは、DeepEval の reason **だけ**で判定せず、必ず回答とナレッジを突き合わせて事実確認する。

### アクション C-2-1: 各閾値割れシナリオを照合

各シナリオについて:

1. `evaluation.json` の `reason` を読む（DeepEval が何を問題と判定したか）
2. `answer.md` を読む（スキルが実際に何を回答したか）
3. `workflow_details.json` の `step4`（読んだセクション）と `step8`（回答に使ったセクション）を確認
4. 該当ナレッジセクションを読む。**ページの `content`（導入文、セクション番号なし）も必ず確認する**（自動評価器はセクション単位で渡すため content を見落としやすい）
5. `diagnostics.selected_pages` のページは**全セクション**読む。Javadoc が含まれる場合はその JSON も全セクション読む

### アクション C-2-2: 3分類で判定

| 分類 | 判定基準 |
|---|---|
| 評価基準の問題 | スキルの回答はナレッジと一致しているが、DeepEval の判定根拠が誤っている |
| スキルの挙動問題 | スキルの回答がナレッジの記述と実際に異なる |
| 評価器の揺らぎ | run ごとに判定が変わり、ナレッジ照合では問題が確認できない |

判定は必ずナレッジ照合に基づく（reason だけで判定しない）。結果はステップ C-3 の集計レポート付録に記録する。

## ステップ C-3: 品質評価レポート作成（出荷審査の根拠）

横断集約（crossrun-summary.md）と run別レポートを素材に、品質評価レポートを作成する。

### アクション C-3-1: テンプレートを埋める

1. `tools/benchmark/templates/quality-report-template.md` を
   `tools/benchmark/results/{run-label}/quality-report.md` にコピー。
2. 素材を転記:
   - ①②の一次件数・③④の計測値 → crossrun-summary.md から
   - 退行（前版対比）→ 前版の crossrun-summary.md と対比
3. 確定判定（人手照合）:
   - 基準未満の各シナリオについて、answer.md とナレッジを突き合わせ、実害か採点の厳しさかを判定し「確定」欄に記入。
   - 自動採点のスコアだけで PASS/FAIL を決めない（誤審を除外した実害ベースで判定）。
4. ③④コストは合否を出さず、増減理由と見解を記入。

### アクション C-3-2: コミット

```bash
git add tools/benchmark/results/{run-label}/quality-report.md
git commit -m "docs: add quality report for {run-label}"
git push
```

---

# フェーズ D: ベースライン確立（新ラベル初回 or 意図的リセット時のみ）

退行検出の基準となる baseline.json を作る。既存ベースラインと比較するだけなら、このフェーズは飛ばしてフェーズ E へ。

## ステップ D-1: baseline.json 生成

### アクション D-1-1: 生成

```bash
python3 -m tools.benchmark.scripts.report \
  --baseline-runs \
    tools/benchmark/results/{run-label}/run-1 \
    tools/benchmark/results/{run-label}/run-2 \
    tools/benchmark/results/{run-label}/run-3 \
  --save-baseline tools/benchmark/results/{run-label}/baseline.json
```
出力: `tools/benchmark/results/{run-label}/baseline.json`
内容: シナリオ×指標ごとの `mean`/`stddev`/`pass_rate`、`pass_rate<1.0` に `flaky:true`、グローバル平均・stddev、閾値設定。

### アクション D-1-2: コミット

```bash
git add tools/benchmark/results/{run-label}/baseline.json
git commit -m "chore: establish {run-label} baseline"
git push
```

---

# フェーズ E: 退行チェック（スキル改修後、既存ベースラインと比較）

スキルを変更した後、既存ベースラインと比較して退行を自動検出する。

## ステップ E-1: 退行チェック実行

### アクション E-1-1: 各 run を baseline と比較

```bash
for r in run-1 run-2 run-3; do
  python3 -m tools.benchmark.scripts.report \
    --run-dir tools/benchmark/results/{new-label}/$r \
    --compare-baseline tools/benchmark/results/{baseline-label}/baseline.json || true
done
```
出力: 各 `{new-label}/run-N/regression-check.md`
（`|| true`: REGRESSION DETECTED の exit 1 で止めないため）

判定ルール:
- スコアが `baseline_mean - 2σ` を下回る → `REGRESSION DETECTED`
- `flaky:true` シナリオの退行 → `CLEAN` 扱い（flaky_regressions に記録）
- ベースラインにない新規シナリオ → スキップ（new_scenarios に記録）

3 run 全て CLEAN なら退行なし。REGRESSION DETECTED はシナリオ・指標・delta を確認し、フェーズ C-2 と同じ要領でナレッジ照合して原因を判定する。

### アクション E-1-2: コミット

```bash
git add tools/benchmark/results/{new-label}/run-*/regression-check.md
git commit -m "chore: regression check {new-label} vs {baseline-label}"
git push
```

## ステップ E-2: 改善判断

### アクション E-2-1: 閾値割れシナリオを判断

`workflow_details.json` / `answer.md` / `evaluation.json` を読み、再現性・原因・改善可能性を判断する。

| シナリオID | 低下指標 | 再現性 | 原因分類 | 対応 |
|---|---|---|---|---|
| qa-12 | faithfulness | 3/3 | ナレッジ未収録 | 要改善: ナレッジ追加 |
| impact-03 | answer_relevancy | 1/3 | 揺らぎ | 対処不要 |

原因分類: 評価基準の問題 / ナレッジ未収録 / スキルの挙動問題。判定はナレッジ照合に基づく。

---

# 出力ファイル早見表

各シナリオの出力:

| ファイル | 存在条件 | 用途 |
|---|---|---|
| `error.json` | エラー時のみ | エラー内容（`error`, `exception_type`） |
| `workflow_details.json` | 正常完了時 | step3: ページ/セクション選択理由、step4: 読んだセクション、step8: 回答に使ったセクション |
| `answer.md` | 正常完了時 | 最終回答テキスト |
| `evaluation.json` | 正常完了時 | DeepEval 3指標のスコアと判定根拠 |
| `metrics.json` | 正常完了時 | 実行時間・ターン数・コスト |
| `trace.json` | 正常完了時 | claude の生JSON出力（`result` に LLM 出力全文） |

各ラベルディレクトリ直下のレポート:

| ファイル | 生成ステップ | 内容 |
|---|---|---|
| `run-N/report.md` | B-3 | run別スコア＋cost/time分布 |
| `crossrun-summary.md` | C-1 | 3run横断集約 |
| `quality-report.md` | C-3 | 出荷審査の根拠（合否①②＋計測③④＋退行） |
| `baseline.json` | D-1 | 退行検出の基準 |
| `run-N/regression-check.md` | E-1 | ベースライン差分 |

---

# 注意事項

- レポートは情報がそろった時点で生成し、その都度コミット・プッシュする（最後にまとめて、ではない）。
- cost/time は平均でなく p50・最大を見る（平均はばらつきを隠す）。
- レポートは固定名で出力される。同一ラベルで再実行すると同名レポートは上書きされる（再生成は意図通り）。別ベンチは別ラベルのディレクトリに出すこと。
- 閾値割れの最終判定は必ずナレッジ照合に基づく（DeepEval の reason だけで判定しない）。
