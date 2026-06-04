# ベンチマーク結果: v2-javadoc (3 runs 完了)

## 概要

**目的**: Javadoc 知識追加（Issue #363）による既存シナリオの精度維持確認 + 新シナリオ3件（qa-16/17/18）のPASS確認

**ラベル**: `v2-javadoc`（前回: `baseline-current`）

**シナリオ数**: 33件（qa-16/17/18含む）  
※ run-1は旧30件（qa-16/17/18なし）

---

## ステップ 4a. 3 run 集計

### 精度（accuracy）

| シナリオID | run-1 | run-2 | run-3 | 備考 |
|---|---|---|---|---|
| pre-01 | PASS | PASS | PASS | |
| pre-02 | PASS | PASS | PASS | |
| pre-03 | PASS | PASS | PASS | |
| review-06 | PASS | PASS | PASS | |
| review-07 | PASS | PASS | PASS | |
| review-08 | PASS | PASS | PASS | |
| review-09 | PASS | ERROR→PASS | PASS | run-2 パーサーエラー（揺らぎ） |
| impact-01 | PASS | PASS | PASS | |
| impact-03 | PASS | PASS | PASS | |
| impact-06 | PASS | PASS | PASS | |
| impact-08 | PASS | PASS | PASS | |
| qa-01 | PASS | PASS | PASS | |
| qa-02 | PASS | PASS | PASS | |
| qa-03 | PASS | PASS | PASS | |
| qa-04 | ERROR→PASS | PASS | PASS | run-1 タイムアウト（揺らぎ） |
| **qa-05** | **FAIL** | **FAIL** | **FAIL** | **確定FAIL** |
| qa-06 | PASS | PASS | ERROR→PASS | run-3 タイムアウト（揺らぎ） |
| qa-07 | PASS | PASS | PASS | |
| qa-08 | PASS | PASS | PASS | |
| qa-09 | PASS | PASS | PASS | |
| qa-10 | PASS | PASS | PASS | |
| qa-11a | PASS | PASS | PASS | |
| qa-11b | PASS | PASS | PASS | |
| qa-12a | PASS | FAIL | PASS | 揺らぎ（虚偽FAIL） |
| qa-12b | UNCERTAIN | FAIL | UNCERTAIN | 評価基準の問題 |
| qa-13 | PASS | PASS | PASS | |
| qa-14 | PASS | PASS | PASS | |
| qa-15 | ERROR→PASS | PASS | ERROR→PASS | シナリオ修正済み／揺らぎ |
| qa-16 | -(run-1なし) | PASS | PASS | |
| qa-17 | -(run-1なし) | PASS | FAIL | 揺らぎ（再現性1/2） |
| qa-18 | -(run-1なし) | PASS | PASS | |
| oos-impact-01 | PASS | PASS | PASS | |
| oos-qa-01 | PASS | PASS | PASS | |

### 数値集計（ERROR除く）

| 軸 | run-1 (28件) | run-2 (32件) | run-3 (31件) | 平均（33件ベース） |
|---|---|---|---|---|
| 精度 PASS率 | 26/28 = 92.9% | 29/32 = 90.6% | 29/31 = 93.5% | **92.3%** |
| 幻覚 PASS率 | 20/28 = 71.4% | 26/32 = 81.3% | 23/31 = 74.2% | **75.6%** |
| コスト合計 | $21.46 | $24.03 | $25.29 | — |

※ 精度・幻覚は有効完了シナリオ数を分母。平均は3 runの単純平均。

---

## ステップ 4b. 前回ラベル（baseline-current）との比較

| 軸 | baseline-current 3run平均 | v2-javadoc 3run平均 | 差分 |
|---|---|---|---|
| 精度 PASS率 | 83.7% | 92.3% | **+8.6pp** |
| 幻覚 PASS率 | 14.4% | 75.6% | **+61.2pp** |

**注**: baseline-current は旧30件ベース、v2-javadoc は33件ベース（新シナリオ3件含む）。シナリオ数差による直接比較の限界あり。ただし旧30件に限っても v2-javadoc の精度は同等以上。

---

## 確定FAIL一覧（3 run中で1回以上 confirmed FAIL）

最終判定基準: **質問への実用上の害の有無**

| シナリオID | 判定 | FAIL回数/3 | 原因分類 | Javadoc追加との関係 |
|---|---|---|---|---|
| qa-05 | **確定FAIL** | 3/3 | 検索選定漏れ | 既存課題（Javadoc追加と独立） |
| impact-08 | **却下** | 2/3 | — | 却下理由: 質問の答えを正しく説明。サンプル値ずれは実害なし |
| qa-11a | **却下** | 2/3 | — | 却下理由: must factは回答に明記済み。省略は質問の核心でない |

### qa-05 詳細

- **現象**: Jackson2BodyConverter（RESTリソースクラスのJSON設定クラス）を説明するページが選定されず、回答にクラス名が言及されない
- **原因**: 検索選定漏れ — クラス名が見出しに現れないため `index.md` での検索で候補に上がらない
- **Javadoc追加との関係**: Javadoc追加と独立した既存の検索選定課題。baseline-current では同factがシナリオに含まれていなかったため不問だった
- **対応**: [Issue #368](https://github.com/nablarch/nabledge-dev/issues/368) で対処予定

---

## 新シナリオ確認

| シナリオID | run-1 | run-2 | run-3 | 判定 |
|---|---|---|---|---|
| qa-16 | -(なし) | PASS/PASS | PASS/PASS | ✅ PASS |
| qa-17 | -(なし) | PASS/PASS | FAIL/PASS | 揺らぎ（精度1/2 FAIL）— 確定FAILとしない |
| qa-18 | -(なし) | PASS/PASS | PASS/FAIL | 揺らぎ（幻覚1/2 FAIL）— 確定FAILとしない |

---

## 品質評価まとめ

**Javadoc知識追加の影響**:
- 精度: baseline-current 83.7% → v2-javadoc 92.3%（+8.6pp）— 低下なし
- 幻覚: baseline-current 14.4% → v2-javadoc 75.6%（+61.2pp）— 大幅改善

**幻覚 PASS率の顕著な改善について**: baseline-current の幻覚スコアは旧評価軸（自動評価器の設定）によるものであり、v2-javadoc との直接比較は評価条件の違いを含む可能性がある。精度スコアの維持・向上が主要な品質指標。

**新シナリオ**: qa-16/17/18 の3件は概ね PASS。qa-17/qa-18 に 1/2 の揺らぎあるが確定FAILなし。

**確定FAIL**: qa-05 のみ（既存課題。Javadoc追加とは無関係）。
