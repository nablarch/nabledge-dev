# 実験F — 条件5step 結果

**実験日**: 2026-06-10
**条件**: 5ステップ構成（両経路20件マージ、セクション絞り込み30枠）

## 実験設計

```
step1: index.md から関連ページを最大20件 → index_pages
step2: classes.md の各ページブロックから関連ページを最大20件 → classes_pages
step3: index_pages + classes_pages を dedup マージ（トリムなし）→ merged_pages
step4: merged_pages の各ページのセクションを high/partial/skip で選定、最大30枠 → selected_sections
step5: selected_sections から回答生成（qa.md 後段そのまま）
```

- 候補判定: 候補/skip の2値（条件20と同じ基準）
- 各経路上限: 20件
- セクション上限: 30枠

## 実験資産

- semantic-search.md: `.tmp/experiment-5step/workflows/semantic-search.md`
- skill_dir: `.tmp/experiment-5step/` (knowledge/scripts は nabledge-6 へ symlink)
- ランナー: `tools/benchmark/scripts/run_qa.py`（既存を --skill-dir 切り替えで利用）
- qa-05 結果ディレクトリ: 下表参照

## qa-05 × 10回 結果

| 試行 | ディレクトリ | merged総数 | adapter含有（関門1） | 関門3: adapter s2/s3 in selected | 関門4: Jackson2BodyConverter in answer | correctness | cache_read | input | output |
|------|------------|----------:|:--------------------:|:---------------------------------:|:--------------------------------------:|:-----------:|----------:|------:|-------:|
|  1 | 20260610-192604 |  6 | No  | No  | No  | 0.60 | 1,151,306 |  13 |  6,483 |
|  2 | 20260610-192842 |  8 | Yes | Yes | Yes | 1.00 |   289,573 |   7 |  7,431 |
|  3 | 20260610-193512 |  8 | No  | No  | No  | 0.70 |   443,805 |   7 | 11,456 |
|  4 | 20260610-193840 |  7 | No  | No  | No  | 0.60 |   274,714 |   7 |  7,859 |
|  5 | 20260610-195131 |  5 | No  | No  | No  | 0.60 |   809,125 |  13 |  6,596 |
|  6 | 20260610-200024 |  8 | Yes | Yes | Yes | 1.00 |   565,294 |  10 |  9,132 |
|  7 | 20260610-200328 |  5 | No  | No  | No  | 0.60 |   689,637 |   9 |  8,569 |
|  8 | 20260610-201250 |  8 | Yes | No  | No  | 0.60 | 1,508,647 |  17 | 10,449 |
|  9 | 20260610-201637 |  5 | No  | No  | No  | 0.60 |   334,430 |   6 |  6,729 |
| 10 | 20260610-201917 |  6 | No  | No  | No  | 0.60 |   336,809 |   6 |  7,144 |

**集計**:
- 関門1（adapter in merged_pages）: **3/10**
- 関門3（adapter s2/s3 in selected_sections）: **2/10**
- 関門4（Jackson2BodyConverter in answer）: **2/10**
- correctness 平均: **0.69** (n=10)

### 試行8 詳細（adapter in merged だが gate3=No）

adapter（adapters-jaxrs-adaptor.json）は merged_pages に入った（8/8ページ目）が、
セクション選定フェーズで adapter の s1〜s4 が全て excluded になった。
excluded_sections の記録には adapter エントリがなく、セクション総数が 30 枠未満（7件）だったにも関わらず
adapter セクションが読まれなかった可能性がある（Step 4 で全 merged_pages を処理したが adapter をスキップした）。

## 他シナリオ波及（各1回）

| シナリオ | 現行 correctness | 5step correctness | 5step pages | 5step sections | total tokens |
|---------|:----------------:|:-----------------:|:-----------:|:--------------:|-------------:|
| qa-02   | 1.00 | 1.00 | 5 | 10 | 741,022 |
| qa-11a  | 0.90 | 1.00 | 10 | 10 | 859,020 |
| review-07 | 1.00 | 1.00 | 3 | 5 | 847,163 |
| impact-03 | 1.00 | 1.00 | 3 | 4 | 1,106,230 |

現行 correctness は 条件M 回帰実行（20260610-152837）から取得。

## タイムアウト観察

10回中3回、4シナリオ中2件（qa-02/qa-11a 各2回）が 360秒でタイムアウト。
qa-02/qa-11a は 600秒タイムアウトに延長で成功。
条件5step で merged_pages が多いとき（10件超）、セクション読み取りが増加しタイムアウトリスクが上昇する可能性がある。
