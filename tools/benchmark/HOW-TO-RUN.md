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

# 失敗シナリオを単体再実行（例: qa-11, oos-qa-01）
python3 -m tools.benchmark.scripts.run_qa \
  --scenarios tools/benchmark/scenarios/qa.json \
  --skill-dir .claude/skills/nabledge-6 \
  --scenario-ids qa-11,oos-qa-01
```

完了後、再実行結果をrun-Nディレクトリへ上書きコピー:
```bash
RUNDIR=tools/benchmark/results/{run-label}/run-N
NEWDIR=tools/benchmark/results/YYYYMMDD-HHMMSS
for sid in qa-11 oos-qa-01; do
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
retry_ids = {'qa-11', 'oos-qa-01'}
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

**エラー時の調査**:

`error.json` の `exception_type` でエラー種別を確認し、以下で対応を分ける:

- **出力が存在する場合**（`raw_response.txt` または `answer.md` あり）: スキルは回答を生成している。ステップ3bと同じ要領で `raw_response.txt` を読み、must のfact が満たされているかを確認して品質問題か否かを判定する
- **出力が存在しない場合**（スキルが回答を生成できなかった）: 単体再実行で回収する

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

### 3b. 閾値割れシナリオの裏付け調査

閾値割れが出たシナリオについて、DeepEval の判定根拠（reason）だけで原因を分類せず、
**必ず回答とナレッジを突き合わせて事実を確認する**。

**確認対象（必須）**:
- `evaluation.json` の `diagnostics.selected_pages` に列挙されたページの JSON ファイルを**全セクション**読む（`selected_sections` に挙がったセクションだけでなく、そのページの全内容を確認する）
- Javadoc ファイルが `selected_sections` に含まれている場合は、その Javadoc JSON を**全セクション**読む
- クレームに関連するクラス名や機能が `.claude/skills/nabledge-6/knowledge/javadoc/` に存在する場合は、そのファイルも確認する

**注意**: ページの `content`（導入文）はセクション番号がなく、`s1` 以降の named section とは別に存在する。自動評価器はセクション単位でナレッジを渡すため、ページ全体の `content` フィールドを見落としやすい。手動確認では必ずページの `content` も確認すること。

各シナリオについて以下を確認する:

1. `evaluation.json` の `reason` を読む（DeepEval が何を問題と判定したか）
2. `answer.md` を読む（スキルが実際に何を回答したか）
3. `workflow_details.json` の `step4`（読んだナレッジセクション）と `step8`（回答に使ったセクション）を確認する
4. 該当ナレッジセクションを読む（ナレッジに何が書かれているか）
5. 以下の3分類のどれかに判定する:

| 分類 | 判定基準 |
|---|---|
| **評価基準の問題** | スキルの回答はナレッジと一致しているが、DeepEval の判定根拠が誤っている |
| **スキルの挙動問題** | スキルの回答がナレッジの記述と実際に異なる |
| **評価器の揺らぎ** | 同じシナリオで run ごとに判定が変わり、ナレッジとの照合では問題が確認できない |

調査結果はレポートテンプレートの「付録: 閾値割れシナリオ調査結果」に記録する。

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
例: NO。run-2 で qa-11 がタイムアウト（360s）。単体再実行で回収済み。

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

詳細は付録を参照。

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

---

## 付録: 閾値割れシナリオ調査結果

3 run中1回以上閾値割れが発生した全シナリオの裏付け調査結果。
Q3 サマリーの根拠となる。回答とナレッジを実際に突き合わせた事実に基づく。

| シナリオID | 質問（要約） | 低下した指標 | 発生回数/3 | 最終判定 | DeepEvalの判定 | スキルの回答（該当箇所） | ナレッジの記述 | 根拠 |
|---|---|---|---|---|---|---|---|---|
| xxx | ... | 回答正確性 / 回答関連性 / 忠実性 | N/3 | 評価基準の問題 / スキルの挙動問題 / 評価器の揺らぎ | ... | ... | ... | ... |

---

記述の注意事項:
- Q2 の指標名には必ず「意味（非技術者向け）」を添える
- Q3 は「2回以上発生」のみ記載し、1回のみのブレは除外する
- Q4 は YES/NO で始め、理由を事実ベースで書く（「思われる」「可能性がある」は使わない）
- 付録は3 run通じて1回以上閾値割れが発生した全シナリオを対象とする（Q3 の「2回以上」フィルタを適用しない）
- 付録の最終判定は必ずナレッジとの照合に基づくこと（DeepEvalのreason だけで判定しない）

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
| qa-12 | faithfulness | 3/3 | ナレッジ未収録 | 要改善: ナレッジ追加 |
| impact-03 | answer_relevancy | 1/3 | 揺らぎ | 対処不要 |

---

## ステップ 6: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/
git commit -m "chore: save {run-label} E2E benchmark results ({N} runs)"
git push
```

---

## ベンチ後のレポート生成（必須・3種）

ベンチ実行後は必ず以下を実行し、3種のレポートを生成・コミットすること。

### (1) run別レポート
各 run について:
```bash
python3 -m tools.benchmark.scripts.report --run-dir <results>/<label>/run-N
```
→ run-N/report.md（シナリオ別スコア＋cost/time分布 p50/p95/max）

### (3) baseline差分レポート
比較対象 baseline の baseline.json を用意（無ければ --baseline-runs で生成）し:
```bash
python3 -m tools.benchmark.scripts.report \
  --run-dir <results>/<label>/run-N \
  --compare-baseline <baseline>/baseline.json || true
```
→ run-N/regression-check.md

### (2) 3run横断集約
現状 report.py 未対応（別タスクで追加予定）。暫定で REPORTS-INDEX.md に run別レポートの目次を作る。

### 注意
- レポートは必ずコミットする（summary.json だけで済ませない）。
- cost/time は平均でなく中央値(p50)・p95・最大を確認する（平均はばらつきを隠す）。
