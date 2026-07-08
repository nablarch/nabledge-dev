# nabledge-6 コード分析 品質評価レポート

**対象**: section-links 変更後（セクションタイトル付き詳細リンク）
**前版**: `20260701-1736-code-analysis-baseline/`
**測定条件**: 3シナリオ × 1回 = 3評価
**評価方法**: 自動採点（DeepEval: answer_correctness / answer_relevancy / faithfulness）

---

## 総合評価: PASS — 退行なし、ca-01 は大幅改善

全3シナリオで answer_correctness 1.00 を達成。
ベースラインで 0.30 だった ca-01（ProjectAction）が 1.00 に改善。
faithfulness は全件 1.00 を維持（推測・捏造ゼロ）。

---

## 合否判定

### ① 正しい知識を選定し回答できているか → PASS

| シナリオ | 入力クラス | correctness | relevancy | faithfulness | 判定 | ベースライン correctness |
|---|---|---|---|---|---|---|
| ca-01 | ProjectAction | 1.000 | 0.941 | 1.000 | ✅ | 0.300 ↑改善 |
| ca-02 | AuthenticationAction | 1.000 | 0.969 | 1.000 | ✅ | 1.000 = |
| ca-03 | ImportZipCodeFileAction | 1.000 | 0.973 | 1.000 | ✅ | 1.000 = |

→ 全シナリオで expected facts をカバー。退行なし。

### ② 推測や捏造が含まれていないか → PASS

全シナリオで faithfulness 1.00。ナレッジにない作り話は 0 件。

---

## 計測

### ③ 1回あたりコスト

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | $1.370 | $1.256 | $2.085 |
| ベースライン | $0.979 | $0.886 | $1.181 |

※ コスト増はセクションメタデータ収集（Step 3 拡張）による追加トークン消費によるもの。

### ④ 1回あたり時間

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | 279秒 | 317秒 | 332秒 |
| ベースライン | 193秒 | 191秒 | 199秒 |

---

## 結論

**REGRESSION DETECTED: なし**

correctness・faithfulness ともに退行なし。
ca-01 の correctness が 0.30 → 1.00 に改善（セクションリンクにより関連知識への到達精度が向上）。
コスト・時間はセクションメタデータ収集の追加処理分だけ増加しているが、品質上の問題はない。
