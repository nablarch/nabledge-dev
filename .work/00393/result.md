# DeepEval 判定照合結果

**対象**: `tools/benchmark/results/20260616-1214-fullbench-classes-v6/` run-1〜run-3（34シナリオ×3run=102件）  
**照合日**: 2026-07-07  
**閾値**: answer_correctness ≥ 0.99 / answer_relevancy ≥ 0.95 / faithfulness ≥ 0.99

---

## 集計結果

### answer_correctness

| 区分 | 件数 | 率 |
|------|------|----|
| DeepEval=OK, 人手=OK（合意・正常） | 93 | — |
| DeepEval=NG, 人手=NG（合意・問題あり） | 5 | — |
| **DeepEval=NG, 人手=OK（false-positive / 誤検知）** | **4** | **44.4%** (4/9) |
| DeepEval=OK, 人手=NG（false-negative / 見逃し） | 0 | 0.0% (0/93) |

**false-positive率: 44.4%** — DeepEvalがNGとした9件のうち4件は人手評価ではOK。  
**false-negative率: 0.0%** — 見逃しなし。

**false-positive 主因**: DeepEvalが「回答が包括的すぎる」「形式が異なる」などの表面的差異をNGと判定したが、参照事実は実際に回答に含まれていた。

FP事例（根拠ファイル）:
- [run-1-qa-12.md](.work/00393/checks/run-1-qa-12.md) — DeepEvalが「包括的すぎる」として減点したが参照事実は全て含まれている
- [run-2-qa-17.md](.work/00393/checks/run-2-qa-17.md) — 型パラメータの説明は参照事実を充足
- [run-3-qa-12.md](.work/00393/checks/run-3-qa-12.md) — 同上（run-1と同一シナリオ）
- [run-3-review-09.md](.work/00393/checks/run-3-review-09.md) — 事実は含まれているが表現が異なる

---

### answer_relevancy

| 区分 | 件数 | 率 |
|------|------|----|
| DeepEval=OK, 人手=OK（合意・正常） | 79 | — |
| DeepEval=NG, 人手=NG（合意・問題あり） | 9 | — |
| **DeepEval=NG, 人手=OK（false-positive / 誤検知）** | **14** | **60.9%** (14/23) |
| DeepEval=OK, 人手=NG（false-negative / 見逃し） | 0 | 0.0% (0/79) |

**false-positive率: 60.9%** — DeepEvalがNGとした23件のうち14件は人手評価ではOK。  
**false-negative率: 0.0%** — 見逃しなし。

**false-positive 主因**: DeepEvalが回答末尾の `参照: xxx.json:sN` 形式の内部ナレッジ参照記法を「質問と無関係なコンテンツ」と解釈してスコアを閾値（0.95）以下に下げているが、人手評価では回答本体の内容は質問に直接関連しており、末尾の参照記法は出典メタデータとして許容範囲と判断。

FP事例（代表）:
- [run-1-impact-01.md](.work/00393/checks/run-1-impact-01.md) — DeepEvalは参照記法をスコア減点の根拠としてNGとしたが、人手では回答本体は質問に直接関連しOK
- [run-1-qa-01.md](.work/00393/checks/run-1-qa-01.md) — 同上（他12件も同様のパターン）

---

### faithfulness

| 区分 | 件数 | 率 |
|------|------|----|
| DeepEval=OK, 人手=OK（合意・正常） | 66 | — |
| DeepEval=NG, 人手=NG（合意・問題あり） | 9 | — |
| **DeepEval=NG, 人手=OK（false-positive / 誤検知）** | **26** | **74.3%** (26/35) |
| DeepEval=OK, 人手=NG（false-negative / 見逃し） | 1 | 1.5% (1/67) |

**false-positive率: 74.3%** — DeepEvalがNGとした35件のうち26件は人手評価ではOK。  
**false-negative率: 1.5%** — 見逃しはほぼなし。

**false-positive 主因**: DeepEvalが「回答がナレッジの一部を省略している」「コンストラクタの引数パターンが完全でない」などを矛盾と解釈しているが、人手評価では省略は矛盾ではなく、記述内容自体はナレッジと整合している。

FP事例（代表）:
- [run-1-impact-01.md](.work/00393/checks/run-1-impact-01.md) — `UniversalDao.Transaction` コンストラクタの説明が一部省略されているとDeepEvalが判定したが、記述内容はナレッジと矛盾なし
- 他25件（[全FPリスト](.work/00393/checks/)）

FN事例:
- [run-2-qa-11.md](.work/00393/checks/run-2-qa-11.md) — DeepEval=OKだが回答がナレッジに存在しない記述を含む

---

## サマリー

| 指標 | false-positive率 | false-negative率 | 評価 |
|------|------------------|------------------|------|
| answer_correctness | **44.4%** (4/9) | 0.0% (0/93) | 誤検知が多い・見逃しなし |
| answer_relevancy | **60.9%** (14/23) | 0.0% (0/79) | 誤検知が多い・見逃しなし |
| faithfulness | **74.3%** (26/35) | 1.5% (1/67) | 誤検知が非常に多い・見逃しは少ない |

## 解釈

**全指標で false-positive（誤検知）が高く、false-negative（見逃し）はほぼゼロ** という一貫した傾向がある。DeepEvalは「問題あり」方向に厳しすぎる判定をしており、実際には問題のない回答を誤ってNGとすることが多い。

**answer_relevancy の高 false-positive (60.9%)** は主に回答末尾の内部ナレッジ参照記法（`参照: xxx.json:sN`）に起因する。DeepEvalはこの記法を「質問と無関係なコンテンツ」と解釈してスコアを閾値（0.95）以下に下げるが、人手評価では回答本体の内容は質問に直接関連しており末尾の参照記法は出典メタデータとして許容範囲と判断した。

**faithfulness の高 false-positive (74.3%)** は、DeepEvalが「省略」を「矛盾」と過剰解釈することを示す。ナレッジの全情報を回答に含めることは求められておらず、含まれている情報がナレッジと矛盾しなければ faithful と判断すべきだが、DeepEvalはこの区別ができていない。

**answer_correctness の中程度 false-positive (44.4%)** は、参照事実が少数（1〜2件）のシナリオでDeepEvalが表現差異や補足情報の多さをNGと判定するケースに限定されており、影響範囲は小さい（9件中4件）。

## 確認ファイル

全102件の確認ファイル: [.work/00393/checks/](.work/00393/checks/)
