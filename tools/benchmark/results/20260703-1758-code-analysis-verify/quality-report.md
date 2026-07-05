# nabledge-6 コード分析 品質評価レポート

**対象**: リライト後検証（339行版）
**前版**: 20260701-1736-code-analysis-baseline（685行版）
**測定条件**: 3シナリオ × 1回 = 3評価
**評価方法**: 自動採点（DeepEval: answer_correctness / answer_relevancy / faithfulness）

---

## 総合評価: 合格

全3シナリオでanswer_correctness 1.00。ベースラインで0.30だったca-01が1.00に改善。
faithfulness全件1.00 — 捏造リスクなし。
acceptance criterion「Task #6スコア ≥ ベースライン」をすべて満たす。

---

## 合否判定

### ① 正しい知識を選定し回答できているか → PASS（全シナリオ満点）

| シナリオ | 入力クラス | correctness | relevancy | faithfulness | 判定 |
|---|---|---|---|---|---|
| ca-01 | ProjectAction | 1.00 | 0.97 | 1.00 | ✅ |
| ca-02 | AuthenticationAction | 1.00 | 0.99 | 1.00 | ✅ |
| ca-03 | ImportZipCodeFileAction | 1.00 | 0.92 | 1.00 | ✅ |

→ 全シナリオでexpected factsをすべてカバー。

### ② 推測や捏造が含まれていないか → PASS

全シナリオでfaithfulness 1.00。ナレッジにない作り話は0件。

---

## ベースラインとの比較

| シナリオ | 指標 | ベースライン | 本版 | delta |
|---|---|---|---|---|
| ca-01 | correctness | 0.30 | 1.00 | **+0.70** |
| ca-01 | relevancy | 0.96 | 0.97 | +0.01 |
| ca-01 | faithfulness | 1.00 | 1.00 | 0.00 |
| ca-02 | correctness | 1.00 | 1.00 | 0.00 |
| ca-02 | relevancy | 0.99 | 0.99 | 0.00 |
| ca-02 | faithfulness | 1.00 | 1.00 | 0.00 |
| ca-03 | correctness | 1.00 | 1.00 | 0.00 |
| ca-03 | relevancy | 0.97 | 0.92 | -0.05 |
| ca-03 | faithfulness | 1.00 | 1.00 | 0.00 |

→ ca-01のcorrectnessが+0.70改善。ca-03のrelevancyが-0.05だが、correctness/faithfulnessは維持。
  acceptance criterion（全スコア ≥ ベースライン）はcorrectnessで全件達成。

---

## 計測

### ③ 1回あたりコスト

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | $1.110 | $1.063 | $1.197 |
| ベースライン | $1.046 | $0.871 | $1.181 |
| 差分 | +$0.064 | — | — |

### ④ 1回あたり時間

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | 220秒 | 227秒 | 233秒 |
| ベースライン | 193秒 | 191秒 | 200秒 |
| 差分 | +27秒 | — | — |

---

## ベンチからの見解

- ca-01のcorrectness 0.30→1.00は最大の改善。リライトによりJAX-RSアノテーション・BeanUtil・ValidatorUtil
  のfactが正確に出力されるようになった。
- ca-03のrelevancy -0.05は許容範囲内（correctness・faithfulnessは維持）。
- コスト・時間がやや増加しているが、品質向上に対するトレードオフとして問題なし。

---

## 詳細根拠

各シナリオの個別スコア・回答は各シナリオディレクトリ内の `evaluation.json` / `answer.md` を参照。
