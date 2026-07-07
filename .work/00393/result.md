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
| DeepEval=OK, 人手=OK（合意・正常） | 1 | — |
| DeepEval=NG, 人手=NG（合意・問題あり） | 22 | — |
| DeepEval=NG, 人手=OK（false-positive / 誤検知） | 1 | 4.3% (1/23) |
| **DeepEval=OK, 人手=NG（false-negative / 見逃し）** | **78** | **98.7%** (78/79) |

**false-positive率: 4.3%** — ほぼ誤検知なし。  
**false-negative率: 98.7%** — DeepEvalがOKとした79件のうち78件は人手評価ではNG。

**false-negative 主因**: nabledgeの回答末尾に `参照: xxx.json:sN` という内部JSON参照記法（例: `参照: libraries-universal-dao.json:s9`）が含まれており、これはユーザーには無意味な内部実装詳細の露出である。DeepEvalはこの不適切コンテンツを見逃している。

この問題は**全102件のほぼ全てで共通して発生**しており、answer_relevancyの閾値（0.95）をほとんどの場合でわずかに下回る（スコア0.91〜0.94程度）。DeepEvalの閾値は内部参照を検知できていない。

FP事例:
- [run-2-qa-01.md](.work/00393/checks/run-2-qa-01.md) — DeepEvalがNGとした（内部参照を検知）が、人手では回答本体の関連性が高いためOK

FN事例（代表）:
- [run-1-qa-02.md](.work/00393/checks/run-1-qa-02.md) — DeepEval=OK(1.0)だがJSONファイル参照記法が混入
- [run-1-pre-02.md](.work/00393/checks/run-1-pre-02.md) — 同上
- 他74件（[全FNリストはchecksディレクトリを参照](.work/00393/checks/)）

---

### faithfulness

| 区分 | 件数 | 率 |
|------|------|----|
| DeepEval=OK, 人手=OK（合意・正常） | 66 | — |
| DeepEval=NG, 人手=NG（合意・問題あり） | 8 | — |
| **DeepEval=NG, 人手=OK（false-positive / 誤検知）** | **27** | **77.1%** (27/35) |
| DeepEval=OK, 人手=NG（false-negative / 見逃し） | 1 | 1.5% (1/67) |

**false-positive率: 77.1%** — DeepEvalがNGとした35件のうち27件は人手評価ではOK。  
**false-negative率: 1.5%** — 見逃しはほぼなし。

**false-positive 主因**: DeepEvalが「回答がナレッジの一部を省略している」「コンストラクタの引数パターンが完全でない」などを矛盾と解釈しているが、人手評価では省略は矛盾ではなく、記述内容自体はナレッジと整合している。

FP事例（代表）:
- [run-1-impact-01.md](.work/00393/checks/run-1-impact-01.md) — `UniversalDao.Transaction` コンストラクタの説明が一部省略されているとDeepEvalが判定したが、記述内容はナレッジと矛盾なし
- [run-2-oos-qa-01.md](.work/00393/checks/run-2-oos-qa-01.md) — 他26件（[全FPリスト](.work/00393/checks/)）

FN事例:
- [run-2-qa-11.md](.work/00393/checks/run-2-qa-11.md) — DeepEval=OKだが回答がナレッジに存在しない記述を含む

---

## サマリー

| 指標 | false-positive率 | false-negative率 | 評価 |
|------|------------------|------------------|------|
| answer_correctness | **44.4%** (4/9) | 0.0% (0/93) | 誤検知が多い・見逃しなし |
| answer_relevancy | 4.3% (1/23) | **98.7%** (78/79) | 見逃しが極めて多い |
| faithfulness | **77.1%** (27/35) | 1.5% (1/67) | 誤検知が非常に多い・見逃しは少ない |

## 解釈

**answer_relevancy の大規模false-negative (98.7%)** は単一の系統的問題に起因する: nabledge回答末尾の内部JSON参照記法（`参照: xxx.json:sN`）がDeepEvalの関連性評価をすり抜けている。これはDeepEvalの評価観点がユーザー体験上の不適切コンテンツを直接検知できないことを示す。

**faithfulness の高false-positive (77.1%)** は、DeepEvalが「省略」を「矛盾」と過剰解釈することを示す。faithfulnessの判定には人手によるfact-checkが不可欠。

**answer_correctness の中程度false-positive (44.4%)** は、参照事実が少数（1〜2件）のシナリオでDeepEvalが表現差異や補足情報の多さをNGと判定するケースに限定されており、影響範囲は小さい（9件中4件）。

## 確認ファイル

全102件の確認ファイル: [.work/00393/checks/](.work/00393/checks/)
