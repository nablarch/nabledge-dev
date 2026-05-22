# E2Eベンチマーク実行手順

評価軸・スコアリング・ファイルフォーマットの定義は `.work/00343/design/benchmark-design.md` を参照。

## 前提

- スキルディレクトリ: `.claude/skills/nabledge-6`
- シナリオファイル: `tools/benchmark/scenarios/qa.json`

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

---

## 出力ファイル早見表

各シナリオの出力ファイルと用途:

| ファイル | 存在条件 | 用途 |
|---|---|---|
| `error.json` | エラー時のみ | エラー内容（`error`, `exception_type`） |
| `workflow_details.json` | 正常完了時 | WF全体の詳細。step3: ページ/セクション選択理由、step4: 実際に読んだセクション、step8: 回答に使ったセクション |
| `answer.md` | 正常完了時 | 最終回答テキスト |
| `evaluation.json` | 正常完了時 | 自動スコア（claim_verdicts, hallucination） |
| `metrics.json` | 正常完了時 | 実行時間・ターン数・コスト |
| `trace.json` | 正常完了時 | claudeの生JSON出力（`result`フィールドにLLM出力全文） |

**エラー時の調査**: `error.json` の `exception_type` でエラー種別確認。TimeoutExpiredの場合は単体再実行で回収する。

---

## ステップ 3: 妥当性評価（AIが判断 → ユーザーが承認 → FAILが確定）

**目的**: ベンチマークが正しく実行されたか、スコアが実態を反映しているかを確認する。FAILはここで確定する。改善に向けた根本原因の調査はこのステップでは行わない。

### 3a. 数値サマリー集計

全シナリオの `evaluation.json` を集計する:

| シナリオID | 精度 | 幻覚 | 読んだセクション数 | ターン数 |
|---|---|---|---|---|
| pre-01 | PASS | PASS | 4 | 5 |
| qa-02 | FAIL | PASS | 2 | 14 |

- 精度: `claim_verdicts` が全て PRESENT → PASS、1つでも ABSENT → FAIL、UNCERTAIN あり → UNCERTAIN
- 幻覚: `hallucination.verdict`
- セクション数: `workflow_details.json["step4"]["read_sections"]` の件数
- ターン数: `metrics.json["num_turns"]`

### 3b. FAIL/UNCERTAIN シナリオの妥当性評価

FAIL または UNCERTAIN が出たシナリオについて、`workflow_details.json` と `answer.md` を読み、以下を事実ベースで確認する:

1. **mustのfactは回答に含まれているか** — 精度FAIL/UNCERTAINの場合、まずmustのfact充足を確認する。mustが満たされていれば、FAIL/UNCERTAINはfactの問題である可能性が高い

2. **スキルは想定通りに動いたか** — 検索クエリは適切か、読んだセクションは質問に合っているか、回答はナレッジに基づいているか

3. **FAILの原因はどこにあるか** — 以下の分類で判定する:
   - **評価基準の問題**: factやclaimの記述が不正確・過剰・過度に単純化されており、正しい回答を誤判定している
   - **ナレッジ/RSTの問題**: ナレッジまたは元のRSTに誤りがあり、回答の方が正しい（ナレッジに問題があるならRSTまで遡って確認する）
   - **ナレッジ未収録の補足**: スキルが一般的な補足情報を追加したが、Nablarch固有のハルシネーションではない（mustが満たされているなら問題なし）
   - **スキルの挙動問題**: 検索ミス・回答生成ミス・Nablarch固有のハルシネーションなど、スキル側に原因がある

4. **FAILの妥当性** — 上記分類に基づき、このFAILは妥当か（実際の品質問題を反映しているか）を判定する

### 3c. レポート保存とユーザー確認

レポートを `tools/benchmark/results/{run-label}/run-N/report.md` に保存し、ユーザーに提示する。

ユーザーはAIの妥当性評価を確認し、各FAILを承認または否認する。**承認されたFAILのみが確定FAILとなる。**

承認後、次のrunへ進む（3 run完了まで繰り返す）。

---

## ステップ 4: 比較集計（3 run完了後）

**目的**: 3 runの数値を集計し、前回ラベルと比較する。判断は行わず集計のみ。

### 4a. 3 run集計

| 軸 | run-1 | run-2 | run-3 | 平均 |
|---|---|---|---|---|
| 精度 PASS率 | N% | N% | N% | N% |
| 幻覚 PASS率 | N% | N% | N% | N% |
| コスト合計 | $N | $N | $N | $N |

確定FAIL一覧（3 run中で1回以上 confirmed FAIL となったシナリオ）:

| シナリオID | FAIL回数/3 | 分類 |
|---|---|---|

### 4b. 前回ラベルとの比較

| 軸 | 前回 平均 | 今回 平均 | 差分 |
|---|---|---|---|
| 精度 PASS率 | N% | N% | ±Npp |
| 幻覚 PASS率 | N% | N% | ±Npp |

保存先: `tools/benchmark/results/{run-label}/report.md`

---

## ステップ 5: 確定FAILの根本原因調査（AIが調査 → ユーザーが対応要否を判定）

**目的**: 確定FAILについて原因を調査し、「揺らぎ（対処不要）」か「要改善」かをAIが提案する。ユーザーが対応要否を判定する。

### 5a. 各確定FAILの調査

`workflow_details.json` / `answer.md` / `evaluation.json` を読み、以下を調査する:

1. **再現性**: 3 run中何回発生したか（1回 → 揺らぎ候補、2〜3回 → 要調査）
2. **原因の特定**: ステップ3bの分類（評価基準の問題 / ナレッジ未収録 / スキルの挙動問題）を根拠付きで確定する
3. **改善可能性**: 原因に対して現実的な対処があるか

### 5b. 提案

各確定FAILについてAIが提案する:

| シナリオID | 原因分類 | 再現性 | 提案 | 根拠 |
|---|---|---|---|---|
| qa-12a | ナレッジ未収録 | 3/3 | 要改善: ナレッジ追加 | 全runでsupported:falseのclaimが同一 |
| impact-03 | スキルの挙動問題 | 1/3 | 揺らぎ扱い | run-2のみ発生、run-1/3ではPASS |

### 5c. ユーザー承認

ユーザーが各提案の対応要否を判定する。「要改善」と承認されたものが次イテレーションの改善対象となる。

---

## ステップ 6: コミット・プッシュ

```bash
git add tools/benchmark/results/{run-label}/
git commit -m "chore: save {run-label} E2E benchmark results ({N} runs)"
git push
```
