# nabledge-6 コード分析 品質評価レポート

**対象**: リライト後検証（339行版）
**前版**: 20260701-1736-code-analysis-baseline（685行版）
**測定条件**: 3シナリオ × 1回 = 3評価
**評価方法**: 自動採点（DeepEval: answer_correctness / answer_relevancy / faithfulness）

---

## 総合評価: 合格

全 3 シナリオで answer_correctness 1.00。ベースラインで 0.30 だった ca-01 が 1.00 に改善。
faithfulness 全件 1.00 — 捏造リスクなし。
acceptance criterion「Task #6 スコア ≥ ベースライン」を correctness・faithfulness で全件満たす。

---

## 合否判定

### ① 正しい知識を選定し回答できているか → PASS（全シナリオ満点）

| シナリオ | 入力クラス | correctness | relevancy | faithfulness | 判定 |
|---|---|---|---|---|---|
| ca-01 | ProjectAction | 1.000 | 0.974 | 1.000 | ✅ |
| ca-02 | AuthenticationAction | 1.000 | 0.989 | 1.000 | ✅ |
| ca-03 | ImportZipCodeFileAction | 1.000 | 0.918 | 1.000 | ✅ |

→ 全シナリオで expected facts をすべてカバー。

### ② 推測や捏造が含まれていないか → PASS

全シナリオで faithfulness 1.00。ナレッジにない作り話は 0 件。

---

## ベースラインとの比較

| シナリオ | 指標 | ベースライン | 本版 | Δ |
|---|---|---|---|---|
| ca-01 | correctness | 0.300 | 1.000 | **+0.700** |
| ca-01 | relevancy | 0.960 | 0.974 | +0.014 |
| ca-01 | faithfulness | 1.000 | 1.000 | 0.000 |
| ca-02 | correctness | 1.000 | 1.000 | 0.000 |
| ca-02 | relevancy | 0.988 | 0.989 | +0.001 |
| ca-02 | faithfulness | 1.000 | 1.000 | 0.000 |
| ca-03 | correctness | 1.000 | 1.000 | 0.000 |
| ca-03 | relevancy | 0.968 | 0.918 | -0.050 |
| ca-03 | faithfulness | 1.000 | 1.000 | 0.000 |

→ ca-01 の correctness が +0.700 改善。ca-03 の relevancy が -0.050 だが correctness・faithfulness は維持。

---

## 計測

### ③ 1回あたりコスト

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | $1.110 | $1.069 | $1.197 |
| ベースライン | $0.979 | $0.886 | $1.181 |
| 差分 | +$0.131 | — | — |

### ④ 1回あたり時間

| | 平均 | 中央値 | 最大 |
|---|---|---|---|
| 本版 | 220秒 | 226秒 | 232秒 |
| ベースライン | 193秒 | 191秒 | 199秒 |
| 差分 | +27秒 | — | — |

---

## ベンチからの見解

- ca-01 の correctness 0.30 → 1.00 が最大の改善。リライトにより JAX-RS アノテーション・BeanUtil・ValidatorUtil の fact が正確に出力されるようになった。
- ca-03 の relevancy -0.050 は許容範囲内（correctness・faithfulness は維持）。
- コスト・時間がやや増加しているが、品質向上に対するトレードオフとして問題なし。

---

## 詳細根拠

各シナリオの個別スコア・回答は各シナリオディレクトリ内の `evaluation.json` / `answer.md` を参照。
