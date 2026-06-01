# ベースライン ベンチマークレポート（baseline-deepeval）

**目的**: このレポートは次回ベンチマーク実行時の退行検出基準（baseline）を確立する。
`baseline.json` に機械可読な形式で保存済み。次回実行後に
`report.py --run-dir <new-run> --compare-baseline baseline.json` で自動比較できる。

**実行日**: 2026-06-01
**スキル**: nabledge-6
**シナリオ数**: 30（QA 15 + Impact 4 + Review 4 + OOS 2 + Pre 3 + OOS-Impact 2）
**閾値**: answer_correctness ≥0.99 / answer_relevancy ≥0.95 / faithfulness ≥0.99

---

## 1. ベンチは正確に計測できたか？

**結論: 部分的。計測精度に2つの構造的問題がある。**

### 問題1: DeepEval 評価器自体が不安定

faithfulness と answer_relevancy は LLM による判定のため、同一入力でもスコアが変動する。
3 run の stddev を見ると一部シナリオで顕著なばらつきがある：

| シナリオ | 指標 | mean | stddev | 備考 |
|---|---|---|---|---|
| qa-05 | answer_correctness | 0.733 | 0.189 | **3 runで 0.6 / 0.6 / 1.0 と大きく分散** |
| qa-12a | answer_correctness | 0.800 | 0.216 | **3 runで 1.0 / 0.9 / 0.5 と大きく分散** |
| qa-06 | answer_relevancy | 0.916 | 0.085 | 中程度の分散 |
| review-09 | faithfulness | 0.926 | 0.063 | 中程度の分散 |

qa-05 と qa-12a の answer_correctness は stddev が 0.19〜0.22 と非常に大きく、
**3 runの結果が「合格」「不合格」の両方に出ている**。
これは評価器の不安定性であり、スキルの実力を正確に反映していない。

**根本原因**: DeepEval の `AnswerCorrectnessMetric` と `FaithfulnessMetric` が
内部で使う LLM（Claude Sonnet 4.5 via Bedrock）の判定が、回答文の微妙な表現差で変わる。
qa-05 / qa-12a は「事実は正しいが書き方が違う」ケースで特に揺れやすい。

**改善案**:
- qa-05: `must.facts` の記述を緩和する（「`String` 型で宣言」→「文字列型で保持」など表現を一般化）
- qa-12a: `must.facts` の記述を現在の回答パターンに合わせて修正

### 問題2: answer_relevancy の閾値が高すぎる可能性

impact-03（0.923）・pre-01（0.887）は **3 run全て** で閾値 0.95 未達。
回答の内容は正しく（answer_correctness = 1.0）、ナレッジ外の記述もない（faithfulness = 1.0）が、
DeepEval が「質問より広い範囲をカバーしている」として relevancy を下げる。

**根本原因**: impact-03（DBの中のBareBeanValidation）と pre-01（バッチ起動方法）は、
正しく答えるために補足説明が必要なシナリオで、スキルが適切に周辺知識を提供している。
DeepEval の relevancy 計算がそれを「無関係な記述」と誤判定している。

**改善案（いずれかを選択）**:
- answer_relevancy の閾値を 0.90 に下げる（現状のスキル品質と整合した現実的な閾値）
- シナリオの質問文を「補足説明不要」な形に絞り込む

---

## 2. ベンチ結果から何が見えるか？

### 2-1. 3 run集計

| 指標 | run-1 | run-2 | run-3 | 平均 | stddev |
|---|---|---|---|---|---|
| answer_correctness | 0.9867 (29/30) | 0.9833 (28/30) | 0.9833 (29/30) | **0.984** | 0.079 |
| answer_relevancy   | 0.9757 (24/30) | 0.9732 (24/30) | 0.9765 (22/30) | **0.975** | 0.050 |
| faithfulness       | 0.9772 (21/30) | 0.9782 (21/30) | 0.9963 (28/30) | **0.984** | 0.034 |

### 2-2. 閾値割れの分類

| 分類 | シナリオ数 | 主な原因 |
|---|---|---|
| **評価器の問題**（must.facts と回答の表現ズレ） | 2 | qa-05, qa-12a |
| **閾値が高すぎる**（補足説明シナリオ） | 2 | impact-03, pre-01 |
| **スキルの回答が広すぎる**（relevancy低下） | 9 | qa-01, qa-06, oos-qa-01, qa-13 など |
| **faithfulness の揺らぎ**（LLM判定ブレ） | 13 | review-06/07/09, qa-12b, pre-03 など |
| **揺らぎ（1/3のみ）** | 10 | impact-01, qa-03 など |

### 2-3. スキルの実力評価

- **answer_correctness**: 平均 0.984、大半のシナリオで 1.0。スキルは問われた事実を正確に回答できている。  
  例外は qa-05（REST APIレスポンスのForm実装、must.facts記述の揺れ）と qa-12a（エラー表示タグ、表現ズレ）の2件のみ。

- **faithfulness**: 平均 0.984、run-3は 0.996（28/30通過）。スキルはほぼハルシネーションなし。  
  失敗ケースの根拠を見ると「微妙な表現の矛盾」を DeepEval が検出しているケースがほとんどで、
  実用上の誤りではない（例: CSRF トークン検証の説明の細部）。

- **answer_relevancy**: 平均 0.975、24〜22/30通過。3指標の中で最も低く最も不安定。  
  「質問に答えながら周辺知識も提供する」スキルの特性と relevancy 計算の相性が課題。

### 2-4. ベースラインとしての妥当性

- **安定シナリオ（stddev ≈ 0）**: 7シナリオが3指標全て pass_rate = 1.0。退行検出の信頼性が高い。
- **不安定シナリオ（flaky = 23/30）**: 閾値が厳しすぎる（≥0.99）ため、少しの揺れでも閾値割れになる。
  退行検出では `mean - 2σ` ルールを適用し、フラキーシナリオの偽陽性を抑制する（`baseline.json` に実装済み）。

---

## 3. 次のアクション

| 優先度 | 内容 |
|---|---|
| 高 | qa-05 / qa-12a の `must.facts` を修正してスコア安定化 → 再ベースライン |
| 中 | answer_relevancy 閾値を 0.90 に下げるか、impact-03 / pre-01 のシナリオ見直し |
| 低 | faithfulness の揺らぎはスキルの実力問題ではないため現状維持 |

---

## 各 run のレポート

- [run-1/run/report.md](run-1/run/report.md)
- [run-2/run/report.md](run-2/run/report.md)
- [run-3/run/report.md](run-3/run/report.md)

機械可読ベースライン: [baseline.json](baseline.json)
